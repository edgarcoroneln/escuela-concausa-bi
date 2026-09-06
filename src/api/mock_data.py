"""Datos de ejemplo para el stub del contrato (US-401).

100% sintéticos y deterministas. Sirven para que las Células 2 (BI) y 3 (ML/Agente)
construyan y prueben **contra el mock** antes de que exista la API real (§6 del contrato).
Los CCT son ficticios (10 chars) y las claves de municipio siguen el patrón INEGI de 5
dígitos (2 de entidad + 3 de municipio) dentro de `SCOPE_ENTIDADES` = {09, 15, 19, 14}.

Cuando llegue la capa Gold real (Célula 1), estas listas se sustituyen por consultas;
las *formas* no cambian, así que la integración es un *swap*.
"""
from __future__ import annotations

from datetime import datetime, timezone

# La linea de alerta vive en el repositorio real (una sola fuente en la capa API); el mock la
# importa para no volver a divergir -- antes contaba con 0.5 mientras el repositorio usaba 0.6.
from src.api.repositorio_gold import LINEA_DE_ALERTA

# --------------------------------------------------------------------------- #
# Escuelas (una por entidad del alcance)
# --------------------------------------------------------------------------- #

ESCUELAS: list[dict] = [
    {
        "cct": "09DPR0001A",
        "nombre": "Primaria Benito Juárez",
        "nivel": "PRIMARIA",
        "cve_mun": "09010",  # Álvaro Obregón, CDMX
        "matricula_total": 480,
        "indice_riesgo": 0.72,
        "driver_dominante": "D2",  # inseguridad del entorno
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
        "cve_mun": "15057",  # Naucalpan, Edomex
        "matricula_total": 610,
        "indice_riesgo": 0.55,
        "driver_dominante": "D1",  # pobreza y rezago
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
        "cve_mun": "19039",  # Monterrey, Nuevo León
        "matricula_total": 320,
        "indice_riesgo": 0.31,
        "driver_dominante": "D4",  # conectividad digital
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
        "cve_mun": "14039",  # Guadalajara, Jalisco
        "matricula_total": 540,
        "indice_riesgo": 0.48,
        "driver_dominante": "D5",  # estrés hídrico
        "sostenimiento": "PUBLICO",
        "latitud": 20.6767,
        "longitud": -103.3475,
        "indice_completitud_drivers": 0.67,
        "d1": 0.35, "d2": 0.30, "d3": 0.28, "d4": 0.40, "d5": 0.71, "d6": None,
    },
]

# --------------------------------------------------------------------------- #
# Municipios
# --------------------------------------------------------------------------- #

MUNICIPIOS: list[dict] = [
    {
        "cve_mun": "09010",
        "nombre_municipio": "Álvaro Obregón",
        "poblacion": 759137,
        "indice_rezago_social": -1.12,
        "pobreza_pct": 22.4,
    },
    {
        "cve_mun": "15057",
        "nombre_municipio": "Naucalpan de Juárez",
        "poblacion": 834434,
        "indice_rezago_social": -0.98,
        "pobreza_pct": 33.1,
    },
    {
        "cve_mun": "19039",
        "nombre_municipio": "Monterrey",
        "poblacion": 1142994,
        "indice_rezago_social": -1.45,
        "pobreza_pct": 17.9,
    },
    {
        "cve_mun": "14039",
        "nombre_municipio": "Guadalajara",
        "poblacion": 1385629,
        "indice_rezago_social": -1.30,
        "pobreza_pct": 20.6,
    },
]

# --------------------------------------------------------------------------- #
# Recomendaciones por driver dominante (ML-02) — el diferenciador prescriptivo
# --------------------------------------------------------------------------- #

RECOMENDACION_POR_DRIVER: dict[str, str] = {
    "D1": "Priorizar programas de becas y apoyo alimentario en la zona.",
    "D2": "Coordinar con seguridad pública rutas escolares seguras y entornos protegidos.",
    "D3": "Gestionar rehabilitación de infraestructura escolar prioritaria.",
    "D4": "Ampliar conectividad y dotación de equipo de cómputo.",
    "D5": "Asegurar suministro de agua y planes de contingencia hídrica.",
    "D6": "Activar protocolos por contingencia de calidad del aire.",
}

CICLO_DEFAULT = "2024-2025"


def prediccion_de_escuela(escuela: dict, id_ciclo: str = CICLO_DEFAULT) -> dict:
    """Deriva un `PrediccionOut` de ejemplo a partir de una escuela del mock.

    Ya no respalda `/predicciones/*` (US-412 lee `gold.predicciones` real vía
    `RepositorioModelos`, cierra BUG-010); queda como referencia para un mock server standalone
    (§6 de `API_Specification.md`). `cluster` es `None`: inventar un entero aquí es justo lo que
    BUG-010 señaló como engañoso, aunque sea en el mock -- ML-03 (US-321) sigue sin productor.
    """
    driver = escuela["driver_dominante"]
    return {
        "cct": escuela["cct"],
        "id_ciclo": id_ciclo,
        "indice_riesgo": escuela["indice_riesgo"],
        "driver_dominante": driver,
        "recomendacion": RECOMENDACION_POR_DRIVER.get(driver, "Sin recomendación."),
        "cluster": None,  # ML-03 sin productor (BUG-010, US-321)
        "mlflow_run_id": "mock-run-0000000000000000",
    }


def kpis_mock() -> dict:
    """KPIs agregados de ejemplo sobre las escuelas del mock."""
    matricula = sum(e["matricula_total"] for e in ESCUELAS)
    # Mismo corte que el repositorio real: si divergen, el contrato miente en las pruebas.
    en_riesgo = sum(1 for e in ESCUELAS if e["indice_riesgo"] >= LINEA_DE_ALERTA)
    completitud = sum(e["indice_completitud_drivers"] for e in ESCUELAS) / len(ESCUELAS)
    return {
        "matricula_total": matricula,
        "variacion_matricula": -0.043,
        "escuelas_en_riesgo": en_riesgo,
        "indice_completitud_drivers": round(completitud, 3),
    }


def metrics_mock() -> dict:
    """Métricas internas de ejemplo (solo analista)."""
    ts = datetime(2026, 8, 11, 12, 0, tzinfo=timezone.utc)
    return {
        "frescura_por_fuente": {
            "DS-04_SESNSP": ts,
            "DS-05_SINAICA": ts,
            "DS-06_CONAGUA": ts,
        },
        "suites_ge_en_verde": True,
    }
