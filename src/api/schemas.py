"""Modelos Pydantic del contrato de la API FARO (US-401).

Fuente de verdad: `vault/03_Architecture/API_Specification.md` §4. Estos modelos se mantienen
**1:1** con ese documento y con `vault/03_Architecture/Data_Model.md`. Cambiar aquí una forma
obliga a actualizar el contrato y avisar a las Células 2 y 3 (regla de oro del §6).

Nota de alcance: este módulo define **solo el contrato** (request/response). La autenticación
real (OAuth2/JWT — US-402) y el RBAC (US-403) se implementan en sus historias; aquí los roles
viven en el enum `Rol` para que el contrato sea completo.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Generic, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictFloat,
    StrictInt,
    StrictStr,
    StringConstraints,
    field_validator,
)

# --------------------------------------------------------------------------- #
# Infraestructura del contrato
# --------------------------------------------------------------------------- #


class EntradaEstricta(BaseModel):
    """Base para los modelos de **entrada** (request bodies). Validación estricta (US-404):

    `extra="forbid"` => un campo desconocido en el cuerpo se rechaza con 422 (`validation_error`),
    en vez de ignorarse en silencio. Endurece la superficie de la API contra typos y payloads
    inesperados. Solo se aplica a la entrada; las salidas siguen siendo permisivas.
    """

    model_config = ConfigDict(extra="forbid")


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


class RefreshIn(EntradaEstricta):
    refresh_token: StrictStr


class ExchangeIn(EntradaEstricta):
    """Canje del codigo de un solo uso por la sesion (US-405). Ver ADR-010."""

    code: StrictStr = Field(min_length=16, max_length=256)


class UserOut(BaseModel):
    sub: StrictStr
    email: StrictStr
    role: Rol
    # Nombre para mostrar, del claim `name` del id_token de Google (scope `profile`). Puede venir
    # vacio: no todo perfil lo expone y no queremos que la sesion dependa de un dato opcional del
    # proveedor. El front cae a `email` cuando esta vacio (acordado con C2, US-405).
    name: StrictStr = ""


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
    # SIN_DATO explícito (P-03/US-103): con `gold.dim_municipio` = universo INEGI (317 municipios
    # de las 4 entidades), la población entra por LEFT JOIN a CONAPO; donde no hay fila queda NULL,
    # nunca 0 ni municipio borrado. Se expone como null, igual que rezago/pobreza, en vez de romper.
    poblacion: StrictInt | None = Field(default=None, ge=0)
    indice_rezago_social: float | None = None
    pobreza_pct: float | None = None


class KpisOut(BaseModel):
    matricula_total: StrictInt
    # KPI-02 es una razón de sumas en [-1, 1]: -1 es la cota matemática (matrícula_total=0) y
    # +1 duplicar la matrícula agregada de todo un filtro (irreal). Field(ge=-1, le=1) es la
    # guardia de BUG-031: si la fórmula volviera a devolver alumnos absolutos (p. ej. -54.5),
    # Pydantic rechaza con 500 en vez de pintar -5450% en el tablero.
    variacion_matricula: StrictFloat = Field(ge=-1, le=1)
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


class PrediccionBatchIn(EntradaEstricta):
    ccts: list[StrictStr] = Field(min_length=1, max_length=1000)
    id_ciclo: StrictStr


class ExplicacionSHAPOut(BaseModel):
    """Contribución de cada driver al riesgo de una escuela.

    `contribuciones` admite `None` **a propósito**: es el `SIN_DATO` explícito de la regla de
    cobertura parcial del proyecto. Un driver sin dato NO es un driver que contribuyó cero -- D5
    (estrés hídrico) es regional y D6 (aire) cubre ~80 zonas urbanas, así que el hueco es el caso
    normal, no la excepción. Devolver `0.0` ahí sería afirmar "este driver no influyó", que es una
    afirmación falsa y además incoherente con `indice_completitud_drivers` y con los cubos, que sí
    marcan `SIN_DATO`.
    """

    cct: StrictStr
    driver_dominante: StrictStr
    # driver -> valor SHAP; `None` = SIN_DATO, nunca 0.0 de relleno
    contribuciones: dict[str, float | None]


# --------------------------------------------------------------------------- #
# Agente conversacional
# --------------------------------------------------------------------------- #


#: Un CCT es la clave de 10 caracteres de la escuela. **No se valida su estructura**
#: (`\d{2}[A-Z]{3}\d{4}[A-Z]`) sino solo longitud y alfabeto: rechazar un CCT real por una
#: variante de formato rompería el chat, mientras que lo que hay que impedir aquí —espacios,
#: saltos de línea, comillas, cualquier cosa que altere la estructura del prompt— ya lo impide
#: este patrón. La existencia del CCT la decide Gold, no el contrato.
CCT = Annotated[str, StringConstraints(pattern=r"^[0-9A-Z]{10}$")]

#: Cotas del contexto. Existen para acotar el tamaño del prompt y la superficie de abuso, no por
#: gusto: cada valor entra **literalmente** en el prompt del sistema (`src/agente/prompt.py`).
MAX_CCTS_CONTEXTO = 200
MAX_FILTROS_CONTEXTO = 10
MAX_LARGO_FILTRO = 100
MAX_LARGO_RESUMEN = 300

#: Cotas del historial de turnos (rediseño del chat, 2026-09-10). Igual criterio que el
#: contexto estructurado de arriba: cada turno entra literal al prompt, así que se acota en
#: cantidad y en tamaño por turno para no desplazar las instrucciones de seguridad ni disparar
#: costo/latencia sin límite.
MAX_TURNOS_HISTORIAL = 10
MAX_LARGO_TURNO = 500


class ContextoConversacionalIn(EntradaEstricta):
    """Contexto estructurado del turno anterior del chat (US-305).

    Existe para que *"¿cuáles son las recomendaciones para **esas** escuelas?"* pueda resolverse
    sin que el LLM invente CCTs. C3 lo consume en `construir_prompt_sistema()`.

    **Este objeto es entrada del cliente, no estado de confianza.** Quien llame a la API puede
    escribir aquí lo que quiera —el endpoint es público bajo `require_lectura`—, así que se trata
    como hostil:

    - `extra="forbid"` (heredado): un `sql`, `sql_generado` o `rol` en el cuerpo se rechaza con 422
      en vez de ignorarse. **El frontend no puede colar SQL por esta puerta.**
    - Los CCT se validan por forma, así que no pueden transportar saltos de línea ni comillas.
    - `resumen` es el único campo de texto libre y por eso es el más peligroso: entra literal al
      prompt, donde un salto de línea permitiría falsificar la estructura del bloque de contexto.
      Se rechazan los caracteres de control.
    - Todo está acotado en tamaño: un contexto no puede empujar el prompt hasta desplazar las
      instrucciones de seguridad.

    Nada de esto sustituye a los guardarraíles de C3 (`preparar_sql_seguro`, solo `SELECT`/`WITH`
    sobre Gold, `LIMIT 1000`). Es la capa de antes: lo que nunca debió llegar al LLM.
    """

    ciclo: StrictStr | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{4}$",
        description="Ciclo del turno anterior, p. ej. `2024-2025`.",
    )
    ccts: list[CCT] = Field(
        default_factory=list,
        max_length=MAX_CCTS_CONTEXTO,
        description="CCTs que el turno anterior identificó. La API no verifica que existan.",
    )
    filtros: dict[str, StrictStr] = Field(
        default_factory=dict,
        description="Filtros del turno anterior (entidad, nivel...). Solo texto plano.",
    )
    resumen: StrictStr | None = Field(
        default=None,
        max_length=MAX_LARGO_RESUMEN,
        description="Resumen del turno anterior. **Dato no confiable**: entra literal al prompt.",
    )

    @field_validator("resumen")
    @classmethod
    def _resumen_sin_caracteres_de_control(cls, v: str | None) -> str | None:
        """Un salto de línea aquí permitiría falsificar la estructura del bloque de contexto."""
        if v is not None and not v.isprintable():
            raise ValueError("el resumen no puede contener saltos de línea ni caracteres de control")
        return v

    @field_validator("filtros")
    @classmethod
    def _filtros_acotados(cls, v: dict[str, str]) -> dict[str, str]:
        if len(v) > MAX_FILTROS_CONTEXTO:
            raise ValueError(f"como máximo {MAX_FILTROS_CONTEXTO} filtros")
        for clave, valor in v.items():
            if len(clave) > MAX_LARGO_FILTRO or len(valor) > MAX_LARGO_FILTRO:
                raise ValueError(f"clave y valor de un filtro: máximo {MAX_LARGO_FILTRO} caracteres")
            if not f"{clave}{valor}".isprintable():
                raise ValueError("los filtros no pueden contener caracteres de control")
        return v


class HistorialTurnoIn(EntradaEstricta):
    """Un turno previo del chat (pregunta del usuario + respuesta del agente).

    Existe para que el agente sostenga una conversación real en vez de tratar cada pregunta
    como independiente (rediseño del chat, 2026-09-10). A diferencia de `ContextoConversacionalIn`
    (un resumen estructurado del turno anterior para resolver referencias como "esas escuelas"),
    `historial` es la transcripción literal de los turnos previos, tal como el widget de chat la
    guarda en `st.session_state`.

    **Mismo criterio de entrada hostil que `ContextoConversacionalIn`**: quien llama al endpoint
    público puede escribir aquí lo que quiera, así que se acota en tamaño y se rechazan
    caracteres de control (evita que un turno inyecte saltos de línea para falsificar la
    estructura del bloque de historial dentro del prompt).
    """

    pregunta: StrictStr = Field(min_length=1, max_length=MAX_LARGO_TURNO)
    respuesta: StrictStr = Field(min_length=1, max_length=MAX_LARGO_TURNO)

    @field_validator("pregunta", "respuesta")
    @classmethod
    def _sin_caracteres_de_control(cls, v: str) -> str:
        """Un salto de línea aquí permitiría falsificar la estructura del bloque de historial."""
        if not v.isprintable():
            raise ValueError("el turno no puede contener saltos de línea ni caracteres de control")
        return v


class AgenteConsultaIn(EntradaEstricta):
    pregunta: StrictStr = Field(min_length=3, max_length=500)
    #: Opcional y **retrocompatible**: un cuerpo sin `contexto` se comporta igual que antes.
    contexto: ContextoConversacionalIn | None = None
    #: Opcional y **retrocompatible**: un cuerpo sin `historial` se comporta igual que antes.
    #: Turnos previos del chat, en orden cronológico (el más antiguo primero).
    historial: list[HistorialTurnoIn] = Field(default_factory=list, max_length=MAX_TURNOS_HISTORIAL)


class AgenteRespuestaOut(BaseModel):
    respuesta: StrictStr
    sql_generado: StrictStr | None = None  # auditable
    fuera_de_alcance: bool = False


# --------------------------------------------------------------------------- #
# Administración (solo analista)
# --------------------------------------------------------------------------- #


class PipelineRunIn(EntradaEstricta):
    dag: StrictStr
    ciclo: StrictStr


class PipelineRunOut(BaseModel):
    run_id: StrictStr
    estado: str = "accepted"


class MetricsOut(BaseModel):
    frescura_por_fuente: dict[str, datetime]
    suites_ge_en_verde: bool


# --------------------------------------------------------------------------- #
# Contrato de errores (§5) — estructura uniforme, sin fuga de detalles internos
# --------------------------------------------------------------------------- #


class ErrorOut(BaseModel):
    error: str  # código estable: "not_found", "forbidden", "validation_error"...
    message: str  # mensaje humano, seguro para el cliente
    request_id: str  # correlación para soporte (el detalle real vive en logs)
