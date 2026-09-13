"""Fake de `RepositorioGold` para la suite rápida del contrato (US-411, Decisión 2).

Implementa `src.api.repositorio_gold.RepositorioGold` en memoria, 100% datos sintéticos. Se
inyecta en `tests/test_api_contract.py` vía `app.dependency_overrides[get_repositorio_gold]`, así
que `/escuelas`, `/municipios` y `/kpis` corren **sin** Postgres — CI queda verde en cualquier
máquina.

Deliberadamente NO usa SQLite (acordado con Christian Ruiz, Tech Lead C4, 2026-08-20): SQLite no
modela el esquema `gold` igual que Postgres y daría falsos verdes. La suite de integración contra
Postgres real es US-422 (Eloisa González Rubio), con un Postgres efímero como *service* de CI.
"""
from __future__ import annotations

from copy import deepcopy

# --------------------------------------------------------------------------- #
# Datos sintéticos (mismas escuelas/municipios de ejemplo que src/api/mock_data.py,
# con los campos que hoy solo existen en Gold: cve_ent, id_ciclo, tiene_prediccion,
# matricula_ciclo_anterior — denominador directo de KPI-02, BUG-031/P-09).
# --------------------------------------------------------------------------- #

ESCUELAS_FAKE: list[dict] = [
    {
        "cct": "09DPR0001A",
        "nombre": "Primaria Benito Juárez",
        "nivel": "PRIMARIA",
        "cve_ent": "09",
        "cve_mun": "09010",  # Álvaro Obregón, CDMX
        "id_ciclo": "2024-2025",
        "matricula_total": 480,
        "matricula_ciclo_anterior": 500,  # la variacion son alumnos absolutos = total - anterior, como gold.fact_escuela_ciclo
        "variacion_matricula_alumnos": -20,
        "indice_riesgo": 0.72,
        "driver_dominante": "D2",
        "tiene_prediccion": True,
        "sostenimiento": "PUBLICO",
        "latitud": 19.3578,
        "longitud": -99.2036,
        "indice_completitud_drivers": 1.0,
        "d1": 0.41, "d2": 0.83, "d3": 0.22, "d4": 0.35, "d5": 0.18, "d6": 0.55,
    },
    {
        "cct": "15DPR0100B",
        "nombre": "Primaria Sor Juana Inés",
        "nivel": "PRIMARIA",
        "cve_ent": "15",
        "cve_mun": "15057",  # Naucalpan, Edomex
        "id_ciclo": "2024-2025",
        "matricula_total": 610,
        "matricula_ciclo_anterior": 598,
        "variacion_matricula_alumnos": 12,
        "indice_riesgo": 0.55,
        "driver_dominante": "D1",
        "tiene_prediccion": True,
        "sostenimiento": "PUBLICO",
        "latitud": 19.4785,
        "longitud": -99.2396,
        "indice_completitud_drivers": 0.83,
        "d1": 0.77, "d2": 0.40, "d3": 0.31, "d4": 0.44, "d5": None, "d6": 0.29,
    },
    {
        "cct": "19DES0007C",
        "nombre": "Secundaria Técnica 7",
        "nivel": "SECUNDARIA",
        "cve_ent": "19",
        "cve_mun": "19039",  # Monterrey, Nuevo León
        "id_ciclo": "2024-2025",
        "matricula_total": 320,
        "matricula_ciclo_anterior": 298,
        "variacion_matricula_alumnos": 22,
        "indice_riesgo": 0.31,
        "driver_dominante": "D4",
        "tiene_prediccion": True,
        "sostenimiento": "PUBLICO",
        "latitud": 25.6866,
        "longitud": -100.3161,
        "indice_completitud_drivers": 1.0,
        "d1": 0.20, "d2": 0.25, "d3": 0.18, "d4": 0.68, "d5": 0.30, "d6": 0.22,
    },
    {
        "cct": "14DPR0250D",
        "nombre": "Primaria Miguel Hidalgo",
        "nivel": "PRIMARIA",
        "cve_ent": "14",
        "cve_mun": "14039",  # Guadalajara, Jalisco
        "id_ciclo": "2024-2025",
        "matricula_total": 540,
        "matricula_ciclo_anterior": 551,
        "variacion_matricula_alumnos": -11,
        "indice_riesgo": 0.48,
        "driver_dominante": "D5",
        "tiene_prediccion": True,
        "sostenimiento": "PUBLICO",
        "latitud": 20.6767,
        "longitud": -103.3475,
        "indice_completitud_drivers": 0.67,
        "d1": 0.35, "d2": 0.30, "d3": 0.28, "d4": 0.40, "d5": 0.71, "d6": None,
    },
    {
        # Sin fila en gold.predicciones todavía -- ejercita SIN_DATO explícito
        # (tiene_prediccion=False, indice_riesgo/driver_dominante=None), no un caso inventado.
        "cct": "09DPR0002B",
        "nombre": "Primaria Sin Predicción",
        "nivel": "PRIMARIA",
        "cve_ent": "09",
        "cve_mun": "09010",
        "id_ciclo": "2024-2025",
        "matricula_total": 200,
        "matricula_ciclo_anterior": 200,
        "variacion_matricula_alumnos": 0,
        "indice_riesgo": None,
        "driver_dominante": None,
        "tiene_prediccion": False,
        "sostenimiento": "PUBLICO",
        "latitud": None,
        "longitud": None,
        "indice_completitud_drivers": 0.5,
        "d1": 0.2, "d2": None, "d3": 0.3, "d4": None, "d5": None, "d6": None,
    },
    {
        # Ciclo ANTERIOR de la misma escuela que la primera fila (mismo cct, otro id_ciclo) --
        # ejercita BUG-044: sin `ciclo` explícito, el default debe quedarse con el más reciente
        # (2024-2025) y nunca sumar/listar esta fila también.
        "cct": "09DPR0001A",
        "nombre": "Primaria Benito Juárez",
        "nivel": "PRIMARIA",
        "cve_ent": "09",
        "cve_mun": "09010",
        "id_ciclo": "2023-2024",
        "matricula_total": 500,
        "matricula_ciclo_anterior": 510,
        "variacion_matricula_alumnos": -10,
        "indice_riesgo": 0.65,
        "driver_dominante": "D2",
        "tiene_prediccion": True,
        "sostenimiento": "PUBLICO",
        "latitud": 19.3578,
        "longitud": -99.2036,
        "indice_completitud_drivers": 1.0,
        "d1": 0.41, "d2": 0.83, "d3": 0.22, "d4": 0.35, "d5": 0.18, "d6": 0.55,
    },
]

MUNICIPIOS_FAKE: list[dict] = [
    {
        "cve_mun": "09010",
        "cve_ent": "09",
        "nombre_entidad": "Ciudad de México",
        "nombre_municipio": "Álvaro Obregón",
        "poblacion": 759137,
        "indice_rezago_social": -1.12,
        "pobreza_pct": 22.4,
    },
    {
        "cve_mun": "15057",
        "cve_ent": "15",
        "nombre_entidad": "México",
        "nombre_municipio": "Naucalpan de Juárez",
        "poblacion": 834434,
        "indice_rezago_social": -0.98,
        "pobreza_pct": 33.1,
    },
    {
        "cve_mun": "19039",
        "cve_ent": "19",
        "nombre_entidad": "Nuevo León",
        "nombre_municipio": "Monterrey",
        "poblacion": 1142994,
        "indice_rezago_social": -1.45,
        "pobreza_pct": 17.9,
    },
    {
        "cve_mun": "14039",
        "cve_ent": "14",
        "nombre_entidad": "Jalisco",
        "nombre_municipio": "Guadalajara",
        "poblacion": 1385629,
        "indice_rezago_social": -1.30,
        "pobreza_pct": 20.6,
    },
]

_CAMPOS_ESCUELA_OUT = (
    "cct", "nombre", "nivel", "cve_mun",
    "matricula_total", "indice_riesgo", "driver_dominante", "tiene_prediccion",
    # US-621 (2026-09-11): el listado ya trae coordenadas para el mapa del frontend.
    "latitud", "longitud",
    # US-621 (2026-09-12): los seis drivers y la comparacion con el ciclo anterior, para que la
    # matriz de drivers y el mapa se llenen con UNA peticion en vez de una por escuela.
    "d1", "d2", "d3", "d4", "d5", "d6", "indice_completitud_drivers",
    "matricula_ciclo_anterior", "variacion_matricula_alumnos",
)


class RepositorioGoldFake:
    """Mismo contrato que `RepositorioGoldPostgres`, resuelto en memoria sobre las listas de
    arriba. Cada instancia parte de una copia propia para que las pruebas no puedan mutar el
    fixture compartido entre sí."""

    def __init__(self) -> None:
        self._escuelas = deepcopy(ESCUELAS_FAKE)
        self._municipios = deepcopy(MUNICIPIOS_FAKE)

    def _ciclo_mas_reciente(self) -> str | None:
        """Mismo default que `RepositorioGoldPostgres._ciclo_mas_reciente` (BUG-044): el `id_ciclo`
        más alto entre las escuelas del fixture, formato `AAAA-AAAA` (orden lexicográfico ==
        cronológico)."""
        ciclos = {e["id_ciclo"] for e in self._escuelas}
        return max(ciclos) if ciclos else None

    def _filtrar_escuelas(
        self,
        *,
        cve_ent: str | None = None,
        cve_mun: str | None = None,
        nivel: str | None = None,
        ciclo: str | None = None,
    ) -> list[dict]:
        ciclo = ciclo or self._ciclo_mas_reciente()
        return [
            e
            for e in self._escuelas
            if (not cve_ent or e["cve_ent"] == cve_ent)
            and (not cve_mun or e["cve_mun"] == cve_mun)
            and (not nivel or e["nivel"].upper() == nivel.upper())
            and (not ciclo or e["id_ciclo"] == ciclo)
        ]

    @staticmethod
    def _ordenar(filas: list[dict], order_by: str | None, order: str) -> list[dict]:
        """Mismo criterio que `RepositorioGoldPostgres._aplicar_orden`: `SIN_DATO` (`None`)
        siempre al final, sin importar `asc`/`desc`."""
        if not order_by:
            return filas
        con_valor = [f for f in filas if f.get(order_by) is not None]
        sin_valor = [f for f in filas if f.get(order_by) is None]
        con_valor.sort(key=lambda f: f[order_by], reverse=(order == "desc"))
        return con_valor + sin_valor

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
        filtradas = self._filtrar_escuelas(cve_ent=cve_ent, cve_mun=cve_mun, nivel=nivel, ciclo=ciclo)
        total = len(filtradas)
        ordenadas = self._ordenar(filtradas, order_by, order)
        inicio = (page - 1) * size
        pagina = ordenadas[inicio : inicio + size]
        items = [{campo: e[campo] for campo in _CAMPOS_ESCUELA_OUT} for e in pagina]
        return items, total

    def obtener_escuela(self, cct: str) -> dict | None:
        """Detalle en el ciclo más reciente (BUG-044): una escuela puede tener fila en más de un
        `id_ciclo`; nunca se devuelve "la primera que aparezca en la lista"."""
        candidatas = [e for e in self._escuelas if e["cct"] == cct]
        if not candidatas:
            return None
        return dict(max(candidatas, key=lambda e: e["id_ciclo"]))

    def listar_municipios(
        self, *, cve_ent: str | None, order_by: str | None, order: str, page: int, size: int
    ) -> tuple[list[dict], int]:
        filtrados = [m for m in self._municipios if not cve_ent or m["cve_ent"] == cve_ent]
        total = len(filtrados)
        ordenados = self._ordenar(filtrados, order_by, order)
        inicio = (page - 1) * size
        pagina = ordenados[inicio : inicio + size]
        return [dict(m) for m in pagina], total

    def obtener_municipio(self, cve_mun: str) -> dict | None:
        for m in self._municipios:
            if m["cve_mun"] == cve_mun:
                return dict(m)
        return None

    def obtener_kpis(
        self, *, cve_ent: str | None, cve_mun: str | None, ciclo: str | None
    ) -> dict:
        escuelas = self._filtrar_escuelas(cve_ent=cve_ent, cve_mun=cve_mun, ciclo=ciclo)
        matricula_total = sum(e["matricula_total"] for e in escuelas)
        # KPI-02 como RAZÓN DE SUMAS, idéntico a RepositorioGoldPostgres.obtener_kpis
        # (BUG-031/P-09): SUM(matricula_total) / NULLIF(SUM(matricula_ciclo_anterior), 0) - 1.
        # NO el promedio ponderado SUM(variacion * matricula) / SUM(matricula), que era la
        # fórmula defectuosa: pintaba -54.5 % donde el valor real era -0.19 %. El NULLIF se
        # refleja aquí como el guard sobre suma_anterior (0 -> variacion 0.0, como el `or 0.0`
        # del repo real).
        suma_anterior = sum(e["matricula_ciclo_anterior"] for e in escuelas)
        variacion = (matricula_total / suma_anterior - 1) if suma_anterior else 0.0
        en_riesgo = sum(
            1
            for e in escuelas
            if e["tiene_prediccion"] and (e["indice_riesgo"] or 0.0) >= 0.6
        )
        completitud = (
            sum(e["indice_completitud_drivers"] for e in escuelas) / len(escuelas)
            if escuelas
            else 0.0
        )
        return {
            "matricula_total": matricula_total,
            "variacion_matricula": variacion,
            "escuelas_en_riesgo": en_riesgo,
            "indice_completitud_drivers": completitud,
        }
