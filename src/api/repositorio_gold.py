"""Repositorio de datos de Gold para `/escuelas`, `/municipios` y `/kpis` (US-411).

Aísla el acceso a datos detrás de una interfaz (`RepositorioGold`) para que los endpoints de
`src/api/v1/gold.py` dependan de una abstracción (`Depends(get_repositorio_gold)`), no de una
conexión directa a Postgres. Así la suite rápida del contrato (`tests/test_api_contract.py`)
puede sustituirla con un fake en memoria vía `app.dependency_overrides`, sin necesitar una base
de datos real — patrón acordado con Christian Ruiz (Tech Lead C4) el 2026-08-20 para la Decisión 2
de US-411. La suite de integración contra Postgres real es US-422 (Eloisa González Rubio), con un
Postgres efímero como *service* de CI (Luis Téllez, Célula 5); esta interfaz nunca corre contra la
Postgres local de nadie en CI.

Los métodos devuelven `dict`s con las llaves exactas de los *Out schemas* (`src/api/schemas.py`),
para que el router los construya igual sin importar qué implementación esté detrás.
"""
from __future__ import annotations

import time
from typing import Protocol

from sqlalchemy import Numeric, cast, func, select
from sqlalchemy.engine import Engine

from src.api.db import get_engine, get_tablas

# TTL del cache de `_ciclo_mas_reciente()` (BUG-044, revisión de Christian Ruiz 2026-09-05): el
# set de ciclos materializados solo cambia cuando corre dbt (cadencia de días), así que 5 minutos
# de margen no arriesga servir un ciclo obsoleto por mucho tiempo, y evita un `SELECT MAX(id_ciclo)`
# extra en cada petición a /escuelas, /kpis y /escuelas/{cct}.
_CICLO_CACHE_TTL_SEGUNDOS = 300

# Whitelist de `order_by` (Decisión 3 de US-411, avisada a C2/C3, ver API_Specification.md §3.3).
# Fuente de verdad para el Literal de FastAPI en `src/api/v1/gold.py` -- un valor fuera de aquí
# nunca llega a construir SQL (ni siquiera necesita whitelist propia en la Postgres real).
ESCUELAS_ORDENABLES = ("cct", "nombre", "matricula_total", "indice_riesgo")
MUNICIPIOS_ORDENABLES = ("cve_mun", "nombre_municipio", "poblacion", "indice_rezago_social", "pobreza_pct")


class RepositorioGold(Protocol):
    """Lecturas sobre Gold que necesitan `/escuelas`, `/municipios` y `/kpis`."""

    def listar_escuelas(
        self,
        *,
        cve_ent: str | None,
        cve_mun: str | None,
        nivel: str | None,
        ciclo: str | None,
        order_by: str | None,
        order: str,
        page: int,
        size: int,
    ) -> tuple[list[dict], int]:
        """`(items, total)` de escuelas que cumplen los filtros, ordenadas y ya paginadas.

        `order_by` es una de `ESCUELAS_ORDENABLES` (whitelist validada por FastAPI antes de
        llegar aquí, ver `src/api/v1/gold.py`); `SIN_DATO` (`None`) siempre queda al final.

        Si `ciclo` viene `None`, se usa el ciclo más reciente materializado en
        `fact_escuela_ciclo` -- **nunca** todos los ciclos a la vez (BUG-044). Ese default es
        **global** (el máximo de toda la tabla), no por `cve_ent`/`cve_mun`: una entidad sin
        filas todavía para ese ciclo da lista vacía, no su propio último ciclo disponible. Ver
        `RepositorioGoldPostgres._ciclo_mas_reciente` para el porqué.
        """
        ...

    def obtener_escuela(self, cct: str) -> dict | None:
        """Detalle de una escuela (con los 6 drivers) o `None` si no existe/no aplica alcance."""
        ...

    def listar_municipios(
        self, *, cve_ent: str | None, order_by: str | None, order: str, page: int, size: int
    ) -> tuple[list[dict], int]:
        """`(items, total)` de municipios que cumplen los filtros, ordenados y ya paginados."""
        ...

    def obtener_municipio(self, cve_mun: str) -> dict | None:
        """Detalle de un municipio por clave INEGI o `None` si no existe."""
        ...

    def obtener_kpis(
        self, *, cve_ent: str | None, cve_mun: str | None, ciclo: str | None
    ) -> dict:
        """Agregados del tablero (KPI-02/04/05 de `Screen_Specs.md`).

        Si `ciclo` viene `None`, se usa el ciclo más reciente materializado -- nunca la suma de
        todos los ciclos a la vez (BUG-044). Ese default es **global**, no por `cve_ent`/`cve_mun`
        -- ver `RepositorioGoldPostgres._ciclo_mas_reciente`.
        """
        ...


class RepositorioGoldPostgres:
    """Implementación real sobre `gold.*` vía SQLAlchemy Core (mismo estilo que
    `src/modelos/publicar_gold.py`, ver `src/api/db.py`)."""

    # Cache del ciclo más reciente compartido entre instancias (BUG-044): `get_repositorio_gold()`
    # crea una instancia nueva por petición (`Depends`), así que un cache de instancia no serviría
    # de nada -- tiene que vivir a nivel de clase para sobrevivir entre requests del mismo proceso.
    _ciclo_cache: tuple[str | None, float] | None = None

    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine or get_engine()
        (
            _,
            self._dim_escuela,
            self._dim_municipio,
            self._fact,
            self._predicciones,
            self._recomendaciones,
        ) = get_tablas()

    def _seleccion_escuela(self, *, detalle: bool):
        """`SELECT` común de `/escuelas`: grano `fact_escuela_ciclo x dim_escuela`, con
        `indice_riesgo`/`driver_dominante` por `LEFT JOIN` (Data_Model.md §4.1, confirmado por
        Christian Ruiz el 2026-08-20). Solo incluye escuelas con hecho observado (`fact` es el
        ancla, igual que `/kpis`).
        """
        dim_escuela, fact = self._dim_escuela, self._fact
        predicciones, recomendaciones = self._predicciones, self._recomendaciones

        columnas = [
            fact.c.cct,
            dim_escuela.c.nombre,
            dim_escuela.c.nivel,
            fact.c.cve_mun,
            fact.c.matricula_total,
            predicciones.c.indice_riesgo,
            recomendaciones.c.driver_dominante,
            (predicciones.c.cct.is_not(None)).label("tiene_prediccion"),
        ]
        if detalle:
            columnas += [
                dim_escuela.c.sostenimiento,
                dim_escuela.c.latitud,
                dim_escuela.c.longitud,
                fact.c.indice_completitud_drivers,
                fact.c.d1,
                fact.c.d2,
                fact.c.d3,
                fact.c.d4,
                fact.c.d5,
                fact.c.d6,
            ]

        return select(*columnas).select_from(
            fact.join(dim_escuela, fact.c.cct == dim_escuela.c.cct)
            .join(
                predicciones,
                (fact.c.cct == predicciones.c.cct)
                & (fact.c.id_ciclo == predicciones.c.id_ciclo)
                & (predicciones.c.modelo == "ML-01"),
                isouter=True,
            )
            .join(
                recomendaciones,
                (fact.c.cct == recomendaciones.c.cct)
                & (fact.c.id_ciclo == recomendaciones.c.id_ciclo),
                isouter=True,
            )
        )

    def _columna_orden_escuela(self, order_by: str):
        return {
            "cct": self._fact.c.cct,
            "nombre": self._dim_escuela.c.nombre,
            "matricula_total": self._fact.c.matricula_total,
            "indice_riesgo": self._predicciones.c.indice_riesgo,
        }[order_by]

    def _columna_orden_municipio(self, order_by: str):
        dim_municipio = self._dim_municipio
        return {
            "cve_mun": dim_municipio.c.cve_mun,
            "nombre_municipio": dim_municipio.c.nombre_municipio,
            "poblacion": dim_municipio.c.poblacion,
            "indice_rezago_social": dim_municipio.c.indice_rezago_social,
            "pobreza_pct": dim_municipio.c.pobreza_pct,
        }[order_by]

    @staticmethod
    def _aplicar_orden(consulta, columna, order: str):
        """`NULLS LAST` en ambas direcciones -- `SIN_DATO` nunca se ordena como si fuera cero
        (misma regla de cobertura parcial del CLAUDE.md §4), avisado a C2/C3 en el contrato."""
        criterio = columna.desc() if order == "desc" else columna.asc()
        return consulta.order_by(criterio.nulls_last())

    def _ciclo_mas_reciente(self) -> str | None:
        """`id_ciclo` más alto materializado en TODO `fact_escuela_ciclo` (formato `AAAA-AAAA`,
        orden lexicográfico == orden cronológico). Sirve como default cuando el caller omite
        `ciclo`: antes de BUG-044, omitirlo dejaba `fact` sin filtrar y listaba/sumaba **todos**
        los ciclos a la vez (escuelas triplicadas, `matricula_total` de `/kpis` triplicado en
        producción). Cacheado `_CICLO_CACHE_TTL_SEGUNDOS` (revisión de Christian Ruiz,
        2026-09-05): el set de ciclos solo cambia cuando corre dbt, así que recalcularlo en cada
        petición era un `SELECT MAX` gratuito de más.

        **El ciclo resuelto es GLOBAL, no por entidad/municipio/filtro** (aclarado a petición de
        Christian Ruiz, para que esto no se lea como un bug en dos semanas): es el máximo de TODO
        `fact_escuela_ciclo`, calculado una sola vez y aplicado igual sin importar qué `cve_ent`,
        `cve_mun` o `nivel` pida el caller. Si una entidad todavía no tiene filas para ese ciclo
        global -- por ejemplo, si CDMX ya recibió el ciclo 2025-2026 pero Jalisco todavía no --
        filtrar por ese `cve_ent` da **lista vacía**, no el último ciclo *disponible para esa
        entidad*. Es intencional: la alternativa (resolver el ciclo por entidad) mostraría
        matrículas de ciclos distintos una al lado de otra en el mismo tablero sin ninguna marca
        que lo distinga -- exactamente el tipo de número "creíble y falso" que el proyecto evita
        en otras partes (ver BUG-017, BUG-030). Todas las entidades avanzan de ciclo juntas o la
        comparación entre ellas deja de tener sentido."""
        ahora = time.monotonic()
        if self._ciclo_cache is not None:
            valor, marca = self._ciclo_cache
            if ahora - marca < _CICLO_CACHE_TTL_SEGUNDOS:
                return valor
        with self._engine.connect() as conexion:
            valor = conexion.execute(select(func.max(self._fact.c.id_ciclo))).scalar_one_or_none()
        RepositorioGoldPostgres._ciclo_cache = (valor, ahora)
        return valor

    def listar_escuelas(
        self,
        *,
        cve_ent: str | None,
        cve_mun: str | None,
        nivel: str | None,
        ciclo: str | None,
        order_by: str | None,
        order: str,
        page: int,
        size: int,
    ) -> tuple[list[dict], int]:
        dim_escuela, fact = self._dim_escuela, self._fact
        ciclo = ciclo or self._ciclo_mas_reciente()
        consulta = self._seleccion_escuela(detalle=False)
        if cve_ent:
            consulta = consulta.where(dim_escuela.c.cve_ent == cve_ent)
        if cve_mun:
            consulta = consulta.where(fact.c.cve_mun == cve_mun)
        if nivel:
            consulta = consulta.where(func.upper(dim_escuela.c.nivel) == nivel.upper())
        if ciclo:
            consulta = consulta.where(fact.c.id_ciclo == ciclo)
        if order_by:
            consulta = self._aplicar_orden(consulta, self._columna_orden_escuela(order_by), order)

        with self._engine.connect() as conexion:
            total = conexion.execute(
                select(func.count()).select_from(consulta.subquery())
            ).scalar_one()
            filas = conexion.execute(
                consulta.limit(size).offset((page - 1) * size)
            ).mappings().all()

        return [dict(fila) for fila in filas], total

    def obtener_escuela(self, cct: str) -> dict | None:
        """Detalle de una escuela en el ciclo más reciente materializado (BUG-044): sin acotar
        `id_ciclo`, `.first()` devolvía una fila cualquiera entre los ciclos de la misma escuela,
        no determinista."""
        ciclo = self._ciclo_mas_reciente()
        consulta = self._seleccion_escuela(detalle=True).where(self._fact.c.cct == cct)
        if ciclo:
            consulta = consulta.where(self._fact.c.id_ciclo == ciclo)
        with self._engine.connect() as conexion:
            fila = conexion.execute(consulta).mappings().first()
        return dict(fila) if fila is not None else None

    def listar_municipios(
        self, *, cve_ent: str | None, order_by: str | None, order: str, page: int, size: int
    ) -> tuple[list[dict], int]:
        dim_municipio = self._dim_municipio
        consulta = select(dim_municipio)
        if cve_ent:
            consulta = consulta.where(dim_municipio.c.cve_ent == cve_ent)
        if order_by:
            consulta = self._aplicar_orden(consulta, self._columna_orden_municipio(order_by), order)

        with self._engine.connect() as conexion:
            total = conexion.execute(
                select(func.count()).select_from(consulta.subquery())
            ).scalar_one()
            filas = conexion.execute(
                consulta.limit(size).offset((page - 1) * size)
            ).mappings().all()

        return [self._municipio_dict(fila) for fila in filas], total

    def obtener_municipio(self, cve_mun: str) -> dict | None:
        dim_municipio = self._dim_municipio
        with self._engine.connect() as conexion:
            fila = conexion.execute(
                select(dim_municipio).where(dim_municipio.c.cve_mun == cve_mun)
            ).mappings().first()
        return self._municipio_dict(fila) if fila is not None else None

    @staticmethod
    def _municipio_dict(fila) -> dict:
        """`gold.dim_municipio.poblacion` es `numeric` en Postgres (llega como `Decimal` por
        SQLAlchemy); `MunicipioOut.poblacion` es `StrictInt | None` — se normaliza aquí, en la
        frontera con la BD, en vez de relajar el contrato. El NULL es legítimo (SIN_DATO, P-03):
        con el universo INEGI de municipios, los que no tienen fila CONAPO llegan sin población;
        se preserva el `None` explícito en vez de coaccionar `int(None)` (que rompía con 500)."""
        datos = dict(fila)
        poblacion = datos["poblacion"]
        datos["poblacion"] = int(poblacion) if poblacion is not None else None
        return datos

    def obtener_kpis(
        self, *, cve_ent: str | None, cve_mun: str | None, ciclo: str | None
    ) -> dict:
        """Fórmulas tomadas literalmente de `vault/04_UX_Design/Screen_Specs.md` (KPI-02 variación
        como razón de sumas con la columna directa `matricula_ciclo_anterior` — BUG-031/P-09;
        KPI-04 escuelas en riesgo vía JOIN a `gold.predicciones` con umbral 0.6 ratificado;
        KPI-05 completitud promedio). El `cast(..., Numeric)` evita la división entera de dos
        columnas integer en Postgres (SUM(int)/SUM(int) truncaría a -1)."""
        fact, dim_municipio, predicciones = self._fact, self._dim_municipio, self._predicciones
        ciclo = ciclo or self._ciclo_mas_reciente()

        consulta = (
            select(
                func.coalesce(func.sum(fact.c.matricula_total), 0).label("matricula_total"),
                (
                    cast(func.sum(fact.c.matricula_total), Numeric)
                    / func.nullif(func.sum(fact.c.matricula_ciclo_anterior), 0)
                    - 1
                ).label("variacion_matricula"),
                func.count(predicciones.c.cct)
                .filter(predicciones.c.indice_riesgo >= 0.6)
                .label("escuelas_en_riesgo"),
                func.coalesce(func.avg(fact.c.indice_completitud_drivers), 0).label(
                    "indice_completitud_drivers"
                ),
            )
            .select_from(
                fact.join(dim_municipio, fact.c.cve_mun == dim_municipio.c.cve_mun).join(
                    predicciones,
                    (fact.c.cct == predicciones.c.cct)
                    & (fact.c.id_ciclo == predicciones.c.id_ciclo)
                    & (predicciones.c.modelo == "ML-01"),
                    isouter=True,
                )
            )
        )
        if cve_ent:
            consulta = consulta.where(dim_municipio.c.cve_ent == cve_ent)
        if cve_mun:
            consulta = consulta.where(fact.c.cve_mun == cve_mun)
        if ciclo:
            consulta = consulta.where(fact.c.id_ciclo == ciclo)

        with self._engine.connect() as conexion:
            fila = conexion.execute(consulta).mappings().one()

        return {
            "matricula_total": int(fila["matricula_total"]),
            "variacion_matricula": float(fila["variacion_matricula"] or 0.0),
            "escuelas_en_riesgo": int(fila["escuelas_en_riesgo"]),
            "indice_completitud_drivers": float(fila["indice_completitud_drivers"]),
        }


def get_repositorio_gold() -> RepositorioGold:
    """Dependencia de FastAPI (`Depends(get_repositorio_gold)`). Las pruebas rápidas la
    sustituyen con `app.dependency_overrides[get_repositorio_gold] = ...` (ver
    `tests/fixtures_gold.py`) — nunca con SQLite: no maneja el esquema `gold` igual que Postgres
    y daría falsos verdes."""
    return RepositorioGoldPostgres()
