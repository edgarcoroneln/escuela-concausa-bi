"""Modelos Pydantic del contrato de la API FARO (US-401).

Fuente de verdad: `03_Architecture/API_Specification.md` §4. Estos modelos se mantienen
**1:1** con ese documento y con `03_Architecture/Data_Model.md`. Cambiar aquí una forma
obliga a actualizar el contrato y avisar a las Células 2 y 3 (regla de oro del §6).

Nota de alcance: este módulo define **solo el contrato** (request/response). La autenticación
real (OAuth2/JWT — US-402) y el RBAC (US-403) se implementan en sus historias; aquí los roles
viven en el enum `Rol` para que el contrato sea completo.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, StrictFloat, StrictInt, StrictStr

# --------------------------------------------------------------------------- #
# Infraestructura del contrato
# --------------------------------------------------------------------------- #


class Rol(str, Enum):
    """Los 2 roles del PRD (RBAC de US-403)."""

    ciudadano = "ciudadano"
    analista = "analista"


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Sobre de paginación por *offset*. Ver §1 del contrato."""

    items: list[T]
    total: StrictInt
    page: StrictInt = Field(ge=1)
    size: StrictInt = Field(ge=1, le=100)


# --------------------------------------------------------------------------- #
# Salud / versión / auth
# --------------------------------------------------------------------------- #


class HealthOut(BaseModel):
    status: str = "ok"


class VersionOut(BaseModel):
    api: str = "v1"
    commit: StrictStr


class TokenPair(BaseModel):
    access_token: StrictStr
    refresh_token: StrictStr
    token_type: str = "bearer"
    expires_in: StrictInt = 900  # 15 min


class RefreshIn(BaseModel):
    refresh_token: StrictStr


class UserOut(BaseModel):
    sub: StrictStr
    email: StrictStr
    role: Rol


# --------------------------------------------------------------------------- #
# Lectura sobre Gold
# --------------------------------------------------------------------------- #


class EscuelaOut(BaseModel):
    cct: StrictStr = Field(min_length=10, max_length=10)
    nombre: StrictStr
    nivel: StrictStr
    cve_mun: StrictStr = Field(min_length=5, max_length=5)
    matricula_total: StrictInt = Field(ge=0)
    # indice_riesgo/driver_dominante vienen de gold.predicciones/gold.recomendaciones por
    # LEFT JOIN (Data_Model.md §4.1) -- None => SIN_DATO explícito, nunca inventado. Confirmado
    # por Christian Ruiz (Tech Lead C4) el 2026-08-20, avisado a C2/C3.
    indice_riesgo: StrictFloat | None = Field(None, ge=0, le=1)
    driver_dominante: StrictStr | None = None  # "D1".."D6"
    tiene_prediccion: bool  # True si hay fila en gold.predicciones (modelo ML-01) para este cct


class EscuelaDetalleOut(EscuelaOut):
    sostenimiento: StrictStr
    latitud: float | None = None
    longitud: float | None = None
    indice_completitud_drivers: StrictFloat = Field(ge=0, le=1)
    # None => SIN_DATO explícito (regla de cobertura parcial del CLAUDE.md §4)
    d1: float | None = None
    d2: float | None = None
    d3: float | None = None
    d4: float | None = None
    d5: float | None = None
    d6: float | None = None
    # DEC-008 (Edgar, 2026-08-20): indice_riesgo de gold.predicciones puede repartirse a nivel
    # grupo en vez de ser una predicción directa por cct. None mientras tiene_prediccion=False
    # (todavía no existe la columna en gold.predicciones -- pendiente de Diana/Héctor).
    es_estimado_por_grupo: bool | None = None


class MunicipioOut(BaseModel):
    cve_mun: StrictStr = Field(min_length=5, max_length=5)
    nombre_municipio: StrictStr
    poblacion: StrictInt = Field(ge=0)
    indice_rezago_social: float | None = None
    pobreza_pct: float | None = None


class KpisOut(BaseModel):
    matricula_total: StrictInt
    variacion_matricula: StrictFloat
    escuelas_en_riesgo: StrictInt
    indice_completitud_drivers: StrictFloat = Field(ge=0, le=1)


# --------------------------------------------------------------------------- #
# Predicciones (inferencia ML)
# --------------------------------------------------------------------------- #


class PrediccionOut(BaseModel):
    cct: StrictStr = Field(min_length=10, max_length=10)
    id_ciclo: StrictStr
    indice_riesgo: StrictFloat = Field(ge=0, le=1)  # ML-01
    driver_dominante: StrictStr  # ML-02
    recomendacion: StrictStr
    # ML-03 (US-321, Estefany Hernández) aún no existe: sin productor, `cluster` es None.
    # Mismo criterio SIN_DATO que EscuelaOut.indice_riesgo (Christian Ruiz, 2026-08-20) -- nunca
    # se inventa un entero. BUG-010. Al aterrizar ML-03, vuelve a StrictInt obligatorio con
    # aviso a C2/C3 (regla de oro del contrato, API_Specification.md).
    cluster: StrictInt | None = None  # ML-03
    mlflow_run_id: StrictStr


class PrediccionBatchIn(BaseModel):
    ccts: list[StrictStr] = Field(min_length=1, max_length=1000)
    id_ciclo: StrictStr


class ExplicacionSHAPOut(BaseModel):
    cct: StrictStr
    driver_dominante: StrictStr
    contribuciones: dict[str, float]  # driver -> valor SHAP


# --------------------------------------------------------------------------- #
# Agente conversacional
# --------------------------------------------------------------------------- #


class AgenteConsultaIn(BaseModel):
    pregunta: StrictStr = Field(min_length=3, max_length=500)


class AgenteRespuestaOut(BaseModel):
    respuesta: StrictStr
    sql_generado: StrictStr | None = None  # auditable
    fuera_de_alcance: bool = False


# --------------------------------------------------------------------------- #
# Administración (solo analista)
# --------------------------------------------------------------------------- #


class PipelineRunIn(BaseModel):
    dag: StrictStr
    ciclo: StrictStr


class PipelineRunOut(BaseModel):
    run_id: StrictStr
    estado: str = "accepted"


class MetricsOut(BaseModel):
    frescura_por_fuente: dict[str, datetime]
    # None => SIN_DATO explícito: no hay checkpoints de Great Expectations persistidos todavía
    # para leer un resultado real (US-413, 2026-08-27, avisado a C2/C3 y a Luis García/C1).
    suites_ge_en_verde: bool | None = None


# --------------------------------------------------------------------------- #
# Contrato de errores (§5) — estructura uniforme, sin fuga de detalles internos
# --------------------------------------------------------------------------- #


class ErrorOut(BaseModel):
    error: str  # código estable: "not_found", "forbidden", "validation_error"...
    message: str  # mensaje humano, seguro para el cliente
    request_id: str  # correlación para soporte (el detalle real vive en logs)
