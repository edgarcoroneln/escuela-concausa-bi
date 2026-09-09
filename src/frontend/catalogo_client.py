"""Cliente HTTP del catálogo de escuelas y municipios para el panel de ML (US-207).

Consume `/api/v1/escuelas`, `/api/v1/escuelas/{cct}` y `/api/v1/municipios` para que el
panel pueda **decir de qué escuela habla** y para llegar a un CCT **sin teclearlo**.

Mismo patrón que `prediccion_client.py` y `agente_client.py`: `api_base_url` como primer
posicional, el verbo HTTP como **seam inyectable** (`get`), `access_token` opcional, y
salida en dataclasses congeladas. Así las pruebas ejercitan el cliente completo sin red.

**Vive aparte de la página a propósito.** `tests/test_frontend_panel_ml_streamlit.py`
comprueba por AST que `2_Panel_ML.py` no importa `httpx` ni construye rutas de la API: el
contrato con la API se declara en un solo lugar, no repartido entre la página y el cliente.

**Tres huecos de la API que se resuelven aquí, no en la página** (verificado contra el
contrato el 2026-09-06):

1. **No existe `/entidades` ni `/niveles`.** Se declaran abajo como constantes. Los niveles
   van en MAYÚSCULAS porque así están en Gold; el filtro de la API es case-insensitive,
   pero el dato canónico no.
2. **Ni `EscuelaOut` ni `EscuelaDetalleOut` traen `cve_ent` ni `nombre_municipio`.** La
   entidad se deriva de `cve_mun[:2]` y el nombre del municipio sale de `/municipios`.
3. **`size` topa en 100 y hay 317 municipios.** Por eso `listar_municipios` pide por
   entidad y no el catálogo completo: la cascada nunca necesita más de una entidad a la vez.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

#: Las 4 entidades del alcance (`SCOPE_ENTIDADES` del CLAUDE.md §4). La API **no** sirve
#: este catálogo, así que se declara aquí. El nombre es presentación; la clave es el dato.
ENTIDADES: dict[str, str] = {
    "09": "Ciudad de México",
    "15": "Estado de México",
    "19": "Nuevo León",
    "14": "Jalisco",
}

#: Niveles realmente presentes en Gold. `dbt/models/silver/matricula_historica.sql` filtra
#: a estos tres y `NIVELES_BASICA` en `src/ingesta/validacion_cct.py` los fija: media
#: superior **no entra por diseño**, así que ofrecerla daría siempre cero resultados.
NIVELES: tuple[str, ...] = ("PREESCOLAR", "PRIMARIA", "SECUNDARIA")

#: Tope de la API (`size: int = Query(50, ge=1, le=100)`). Pedir más devuelve 422, no
#: recorta en silencio.
TAMANO_MAXIMO = 100


class RecursoNoEncontrado(LookupError):
    """El CCT o la clave de municipio no existe en el ciclo servido."""


@dataclass(frozen=True)
class EscuelaListada:
    """Una fila del listado de búsqueda (`EscuelaOut`)."""

    cct: str
    nombre: str
    nivel: str
    cve_mun: str
    matricula_total: int
    indice_riesgo: float | None
    driver_dominante: str | None
    tiene_prediccion: bool

    @property
    def cve_ent(self) -> str:
        """La entidad no viaja en la respuesta; se deriva de la clave del municipio."""
        return self.cve_mun[:2]


@dataclass(frozen=True)
class FichaEscuela:
    """Detalle de una escuela (`EscuelaDetalleOut`): quién es, no cuánto riesgo tiene.

    `indice_riesgo` y `driver_dominante` también vienen aquí, pero el panel los toma de
    `/api/v1/predicciones/{cct}`, que es el contrato de ML. Se conservan para poder
    **detectar la divergencia** entre ambas fuentes en vez de pintar dos números de ciclos
    distintos uno al lado del otro.
    """

    cct: str
    nombre: str
    nivel: str
    cve_mun: str
    matricula_total: int
    sostenimiento: str
    indice_completitud_drivers: float
    drivers: dict[str, float | None]
    tiene_prediccion: bool
    indice_riesgo: float | None
    latitud: float | None
    longitud: float | None

    @property
    def cve_ent(self) -> str:
        return self.cve_mun[:2]

    @property
    def nombre_entidad(self) -> str:
        return ENTIDADES.get(self.cve_ent, self.cve_ent)

    @property
    def drivers_observados(self) -> int:
        """Cuántos de los 6 drivers tienen dato. `None` es `SIN_DATO`, nunca cero."""
        return sum(1 for v in self.drivers.values() if v is not None)


def _encabezados(access_token: str | None) -> dict[str, str] | None:
    """Misma línea que el resto de los clientes: sin token, sin cabecera."""
    return {"Authorization": f"Bearer {access_token}"} if access_token else None


def _pedir(get: Callable[..., Any], url: str, params: dict, access_token: str | None) -> Any:
    """Una llamada GET con el manejo de errores común a las tres funciones públicas.

    Distingue las mismas tres situaciones que `prediccion_client`: el recurso no existe
    (404), la API no responde, y la API responde algo fuera de contrato.
    """
    try:
        response = get(url, params=params, headers=_encabezados(access_token), timeout=15.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        codigo = exc.response.status_code
        if codigo == 404:
            raise RecursoNoEncontrado("El recurso solicitado no existe.") from exc
        if codigo == 401:
            raise ConnectionError(
                "La API exige sesión para leer el catálogo; inicia sesión y vuelve a intentar."
            ) from exc
        if codigo == 429:
            raise ConnectionError(
                "Demasiadas consultas seguidas; espera un momento antes de reintentar."
            ) from exc
        raise ConnectionError("La API rechazó la consulta al catálogo.") from exc
    except httpx.HTTPError as exc:
        raise ConnectionError("La API del catálogo no está disponible.") from exc


def listar_escuelas(
    api_base_url: str,
    *,
    cve_ent: str | None = None,
    cve_mun: str | None = None,
    nivel: str | None = None,
    ciclo: str | None = None,
    tamano: int = TAMANO_MAXIMO,
    get: Callable[..., Any] = httpx.get,
    access_token: str | None = None,
) -> tuple[list[EscuelaListada], int]:
    """Escuelas que cumplen los filtros, ordenadas por riesgo descendente.

    Devuelve `(items, total)`: `total` es el conteo **antes** de paginar, así que sirve
    para avisar cuando la búsqueda trae más de lo que cabe en una página.

    **Se ordena siempre.** Sin `order_by` el orden de la API no es determinista, y paginar
    sobre un orden inestable repite y pierde filas. Se ordena por `indice_riesgo`
    descendente porque el panel quiere el ranking prescriptivo arriba, y la API pone los
    `None` al final en ambas direcciones (`nulls_last`), así que las escuelas sin
    predicción no se cuelan al principio.
    """
    if tamano > TAMANO_MAXIMO:
        raise ValueError(f"La API no acepta más de {TAMANO_MAXIMO} resultados por página.")

    params: dict[str, Any] = {
        "order_by": "indice_riesgo",
        "order": "desc",
        "size": tamano,
        "page": 1,
    }
    for clave, valor in (("cve_ent", cve_ent), ("cve_mun", cve_mun), ("nivel", nivel), ("ciclo", ciclo)):
        if valor:
            params[clave] = valor

    payload = _pedir(get, f"{api_base_url.rstrip('/')}/api/v1/escuelas", params, access_token)

    try:
        items = [
            EscuelaListada(
                cct=str(fila["cct"]),
                nombre=str(fila["nombre"]),
                nivel=str(fila["nivel"]),
                cve_mun=str(fila["cve_mun"]),
                matricula_total=int(fila["matricula_total"]),
                indice_riesgo=None if fila.get("indice_riesgo") is None else float(fila["indice_riesgo"]),
                driver_dominante=fila.get("driver_dominante"),
                tiene_prediccion=bool(fila["tiene_prediccion"]),
            )
            for fila in payload["items"]
        ]
        return items, int(payload["total"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("La API devolvió un listado de escuelas fuera de contrato.") from exc


def obtener_ficha(
    api_base_url: str,
    cct: str,
    get: Callable[..., Any] = httpx.get,
    access_token: str | None = None,
) -> FichaEscuela:
    """Detalle de una escuela: quién es, para poder decirlo antes del índice de riesgo."""
    clave = cct.strip().upper()
    if len(clave) != 10:
        raise ValueError("El CCT debe tener exactamente 10 caracteres.")

    payload = _pedir(
        get, f"{api_base_url.rstrip('/')}/api/v1/escuelas/{clave}", {}, access_token
    )

    try:
        return FichaEscuela(
            cct=str(payload["cct"]),
            nombre=str(payload["nombre"]),
            nivel=str(payload["nivel"]),
            cve_mun=str(payload["cve_mun"]),
            matricula_total=int(payload["matricula_total"]),
            sostenimiento=str(payload["sostenimiento"]),
            indice_completitud_drivers=float(payload["indice_completitud_drivers"]),
            drivers={d: payload.get(d) for d in ("d1", "d2", "d3", "d4", "d5", "d6")},
            tiene_prediccion=bool(payload["tiene_prediccion"]),
            indice_riesgo=None if payload.get("indice_riesgo") is None else float(payload["indice_riesgo"]),
            latitud=payload.get("latitud"),
            longitud=payload.get("longitud"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("La API devolvió una ficha de escuela fuera de contrato.") from exc


def listar_municipios(
    api_base_url: str,
    cve_ent: str,
    get: Callable[..., Any] = httpx.get,
    access_token: str | None = None,
) -> dict[str, str]:
    """Mapa `cve_mun -> nombre_municipio` de una entidad, **paginando hasta completarla**.

    **Hay que paginar, no basta una página.** `size` topa en 100 y **dos de las cuatro
    entidades del alcance lo exceden**: Jalisco (14) y Estado de México (15) tienen 125
    municipios cada una. Pedir solo la primera página deja fuera ~25 municipios por
    entidad, y como la API ordena por nombre, los que faltan son siempre los del final del
    alfabeto — el fallo es silencioso: la ficha muestra la clave INEGI cruda en vez del
    nombre, que es justo el problema que el panel debía resolver.

    Se detectó al mirar la página renderizada, no el código: `15106` (Tepotzotlán) salía
    como número.
    """
    base = f"{api_base_url.rstrip('/')}/api/v1/municipios"
    mapa: dict[str, str] = {}
    pagina = 1

    while True:
        payload = _pedir(
            get,
            base,
            {
                "cve_ent": cve_ent,
                "size": TAMANO_MAXIMO,
                "page": pagina,
                "order_by": "nombre_municipio",
            },
            access_token,
        )
        try:
            items = payload["items"]
            total = int(payload["total"])
            mapa.update({str(m["cve_mun"]): str(m["nombre_municipio"]) for m in items})
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("La API devolvió un listado de municipios fuera de contrato.") from exc

        # Se corta por página vacía además de por `total` para no depender de un solo
        # criterio: si `total` viniera mal, un `items` vacío igual detiene el bucle.
        if not items or len(mapa) >= total:
            return mapa
        pagina += 1
