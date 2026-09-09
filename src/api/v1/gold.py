"""Lectura sobre Gold: `/escuelas`, `/municipios`, `/kpis` (§3.3).

Solo lectura (todos los `GET`). Fuera de `SCOPE_ENTIDADES` → lista vacía o 404, nunca datos
de otra entidad. Las tres rutas consultan `gold.*` real a través de `RepositorioGold`
(`src/api/repositorio_gold.py`, US-411) inyectada por `Depends(get_repositorio_gold)` — así la
suite rápida del contrato puede sustituirla por un fake en memoria sin tocar Postgres (Decisión 2
de US-411, acordada con Christian Ruiz el 2026-08-20).

`indice_riesgo`/`driver_dominante` en `/escuelas` se traen por `LEFT JOIN` a
`gold.predicciones`/`gold.recomendaciones` (Data_Model.md §4.1) — `None` es `SIN_DATO` explícito,
nunca inventado. `gold.recomendaciones` sigue vacía hoy (depende de ML-02, US-302, sin entregar),
así que `driver_dominante` da `None` en toda escuela por ahora; es el comportamiento correcto, no
un bug. Decisión de contrato confirmada por Christian Ruiz (Tech Lead C4) el 2026-08-20 (incluye
`tiene_prediccion` y, en el detalle, `es_estimado_por_grupo` de DEC-008 — ver `schemas.py`).
"""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.repositorio_gold import RepositorioGold, get_repositorio_gold
from src.api.schemas import (
    EscuelaDetalleOut,
    EscuelaOut,
    KpisOut,
    MunicipioOut,
    Page,
)

router = APIRouter(tags=["Gold"])

# Mismos nombres que ESCUELAS_ORDENABLES/MUNICIPIOS_ORDENABLES de repositorio_gold.py, como
# `Literal` para que un `order_by` fuera de la whitelist responda 422 por validación de Pydantic
# -- nunca llega a construir SQL (Decisión 3 de US-411, avisada a C2/C3, ver API_Specification.md).
OrdenEscuela = Literal["cct", "nombre", "matricula_total", "indice_riesgo"]
OrdenMunicipio = Literal["cve_mun", "nombre_municipio", "poblacion", "indice_rezago_social", "pobreza_pct"]
Direccion = Literal["asc", "desc"]


@router.get("/escuelas", response_model=Page[EscuelaOut])
def listar_escuelas(
    cve_ent: str | None = Query(None, min_length=2, max_length=2),
    cve_mun: str | None = Query(None, min_length=5, max_length=5),
    nivel: str | None = Query(None),
    ciclo: str | None = Query(None),
    order_by: OrdenEscuela | None = Query(None),
    order: Direccion = Query("asc"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    repo: RepositorioGold = Depends(get_repositorio_gold),
) -> Page[EscuelaOut]:
    """Lista escuelas de Gold con filtros, ordenamiento opcionales y paginación (rol mínimo:
    ciudadano). `SIN_DATO` en el campo de orden siempre queda al final (ver `repositorio_gold.py`).
    """
    filas, total = repo.listar_escuelas(
        cve_ent=cve_ent,
        cve_mun=cve_mun,
        nivel=nivel,
        ciclo=ciclo,
        order_by=order_by,
        order=order,
        page=page,
        size=size,
    )
    items = [EscuelaOut(**fila) for fila in filas]
    return Page[EscuelaOut](items=items, total=total, page=page, size=size)


@router.get("/escuelas/{cct}", response_model=EscuelaDetalleOut)
def obtener_escuela(
    cct: str, repo: RepositorioGold = Depends(get_repositorio_gold)
) -> EscuelaDetalleOut:
    """Detalle de una escuela por CCT, con los 6 drivers (None => SIN_DATO)."""
    fila = repo.obtener_escuela(cct)
    if fila is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="CCT inexistente o fuera de alcance.")
    # es_estimado_por_grupo (DEC-008) todavía no existe como columna en gold.predicciones
    # (pendiente Diana/Héctor) -- None explícito, no se inventa ni se asume False.
    return EscuelaDetalleOut(**fila, es_estimado_por_grupo=None)


@router.get("/municipios", response_model=Page[MunicipioOut])
def listar_municipios(
    cve_ent: str | None = Query(None, min_length=2, max_length=2),
    ciclo: str | None = Query(None),
    order_by: OrdenMunicipio | None = Query(None),
    order: Direccion = Query("asc"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    repo: RepositorioGold = Depends(get_repositorio_gold),
) -> Page[MunicipioOut]:
    """Lista municipios de Gold con filtros, ordenamiento opcionales y paginación (rol mínimo:
    ciudadano).

    `ciclo` no filtra `dim_municipio` (no tiene esa columna, Data_Model.md §4.2 — el municipio
    no varía por ciclo escolar); se acepta en la firma por paridad con el contrato (§3.3) y
    se ignora, igual que hacía el stub de mock_data. `SIN_DATO` en el campo de orden siempre
    queda al final (ver `repositorio_gold.py`).
    """
    filas, total = repo.listar_municipios(
        cve_ent=cve_ent, order_by=order_by, order=order, page=page, size=size
    )
    items = [MunicipioOut(**fila) for fila in filas]
    return Page[MunicipioOut](items=items, total=total, page=page, size=size)


@router.get("/municipios/{cve_mun}", response_model=MunicipioOut)
def obtener_municipio(
    cve_mun: str, repo: RepositorioGold = Depends(get_repositorio_gold)
) -> MunicipioOut:
    """Detalle de un municipio por clave INEGI de 5 dígitos."""
    fila = repo.obtener_municipio(cve_mun)
    if fila is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Municipio inexistente o fuera de alcance.")
    return MunicipioOut(**fila)


@router.get("/kpis", response_model=KpisOut)
def obtener_kpis(
    cve_ent: str | None = Query(None, min_length=2, max_length=2),
    cve_mun: str | None = Query(None, min_length=5, max_length=5),
    ciclo: str | None = Query(None),
    repo: RepositorioGold = Depends(get_repositorio_gold),
) -> KpisOut:
    """KPIs agregados del tablero (rol mínimo: ciudadano).

    Fórmulas tomadas literalmente de `vault/04_UX_Design/Screen_Specs.md` (KPI-02 variación ponderada,
    KPI-04 escuelas en riesgo vía JOIN a `gold.predicciones` con la línea de alerta de 0.50
    (`DEC-019`, distinta del ancla 0.60 de la sigmoide -- ver `repositorio_gold.LINEA_DE_ALERTA`), KPI-05
    completitud promedio) — no son agregaciones inventadas para este endpoint.
    """
    datos = repo.obtener_kpis(cve_ent=cve_ent, cve_mun=cve_mun, ciclo=ciclo)
    return KpisOut(**datos)
