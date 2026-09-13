"""Humo del contrato **contra un despliegue real** (US-621, `BUG-077`, `BUG-079`).

**Por qué existe.** El código en `main` no cambia producción: hay que reconstruir y redesplegar la
imagen. `BUG-079` costó días de login roto justamente por eso —la imagen desplegada era anterior al
PR que arreglaba el problema— y `BUG-077` es del mismo tipo: se arregla en el contrato, pero hasta el
redespliegue el endpoint sigue en 500. Esta prueba contesta una sola pregunta, la que no contesta el
CI: **¿lo que está arriba es lo que mergeamos?**

**No corre en el CI ni en local por accidente.** Se salta el módulo completo salvo que se pida
explícitamente con `FARO_SMOKE=1`, porque sale a la red y depende de un despliegue que no controla.

Uso:

    # solo lo público (salud, versión y los cortes del nivel de atención)
    FARO_SMOKE=1 pytest tests/test_smoke_contrato_prod.py -v

    # además las rutas de lectura, con la sesión de un navegador ya autenticado
    FARO_SMOKE=1 FARO_SMOKE_COOKIE="<valor de faro_sesion>" pytest tests/test_smoke_contrato_prod.py -v

`FARO_SMOKE_BASE_URL` apunta a otro despliegue (default: la API de producción).

**La credencial se lee del entorno y nunca se imprime.** No se escribe en el repositorio, no aparece
en los mensajes de error de estas pruebas y no se registra en ningún log: `vault/07_Security/Secrets_Policy.md`.
Para obtener la cookie: iniciar sesión en el front y copiarla desde las herramientas de desarrollo.
"""
from __future__ import annotations

import os
from typing import Any

import httpx
import pytest

BASE_URL = os.environ.get(
    "FARO_SMOKE_BASE_URL", "https://faro-api-eanzfglvyq-uc.a.run.app"
).rstrip("/")
PREFIJO = "/api/v1"
COOKIE_SESION = "faro_sesion"
TIMEOUT_S = 20.0

pytestmark = pytest.mark.skipif(
    os.environ.get("FARO_SMOKE") != "1",
    reason="humo contra un despliegue real: se pide con FARO_SMOKE=1",
)


def _cookies() -> dict[str, str]:
    """Sesión del navegador, si se proporcionó. El valor nunca se imprime."""
    valor = os.environ.get("FARO_SMOKE_COOKIE", "").strip()
    return {COOKIE_SESION: valor} if valor else {}


def _requiere_sesion() -> None:
    if not _cookies():
        pytest.skip("necesita FARO_SMOKE_COOKIE (rutas de lectura protegidas por SEC-006)")


def _get(ruta: str) -> httpx.Response:
    with httpx.Client(timeout=TIMEOUT_S, cookies=_cookies()) as cliente:
        return cliente.get(f"{BASE_URL}{PREFIJO}{ruta}")


def _json_ok(ruta: str) -> Any:
    r = _get(ruta)
    # El cuerpo NO se incluye en el mensaje: en una ruta autenticada puede traer datos reales.
    assert r.status_code == 200, f"{ruta} respondió {r.status_code}, se esperaba 200"
    return r.json()


# --------------------------------------------------------------------------- #
# Público: contesta "qué imagen está desplegada" sin necesitar sesión
# --------------------------------------------------------------------------- #


def test_salud() -> None:
    assert _json_ok("/health")["status"] == "ok"


def test_version_trae_los_cortes_del_nivel_de_atencion() -> None:
    """Si faltan, la imagen desplegada es anterior al PR de los cortes: no hace falta más prueba."""
    from src.api.repositorio_gold import ANCLA_SIGMOIDE, CORTE_ATENCION_MEDIA, LINEA_DE_ALERTA

    cuerpo = _json_ok("/version")
    cortes = cuerpo.get("cortes_atencion")

    assert cortes is not None, (
        "la imagen desplegada no publica `cortes_atencion`: es anterior a este contrato "
        f"(commit desplegado: {cuerpo.get('commit')})"
    )
    assert cortes == {
        "alta": LINEA_DE_ALERTA,
        "media": CORTE_ATENCION_MEDIA,
        "ancla_calibracion": ANCLA_SIGMOIDE,
    }


# --------------------------------------------------------------------------- #
# Lectura: necesita la sesión del navegador (SEC-006)
# --------------------------------------------------------------------------- #


def test_municipios_no_responde_500_con_los_huecos_de_cobertura() -> None:
    """`BUG-077`: 307 de 317 municipios tienen la entidad en NULL. Antes tumbaba la página completa."""
    _requiere_sesion()
    items = _json_ok("/municipios?size=100")["items"]

    assert items, "la página no trajo municipios"
    for municipio in items:
        # Las claves existen siempre; el valor puede ser `null` (SIN_DATO) y eso está bien.
        assert "nombre_entidad" in municipio, municipio.get("cve_mun")
        assert "cve_ent" in municipio, municipio.get("cve_mun")
        assert "poblacion" in municipio, municipio.get("cve_mun")

    sin_entidad = [m for m in items if m["nombre_entidad"] is None]
    print(
        f"\n  municipios en la página: {len(items)} · sin nombre_entidad (SIN_DATO): {len(sin_entidad)}"
    )


def test_un_municipio_concreto_tampoco_revienta() -> None:
    """El detalle de un municipio con el hueco: el otro síntoma que reportó QA."""
    _requiere_sesion()
    items = _json_ok("/municipios?size=100")["items"]
    sin_entidad = [m for m in items if m["nombre_entidad"] is None]
    if not sin_entidad:
        pytest.skip("este despliegue no tiene municipios sin entidad: nada que reproducir")

    detalle = _json_ok(f"/municipios/{sin_entidad[0]['cve_mun']}")
    assert detalle["nombre_entidad"] is None


def test_escuelas_trae_drivers_coordenadas_y_comparacion_de_ciclo() -> None:
    """US-621: lo que el frontend necesita para el mapa y la matriz, en UNA petición."""
    _requiere_sesion()
    items = _json_ok("/escuelas?size=50")["items"]

    assert items, "la página no trajo escuelas"
    esperados = (
        [f"d{i}" for i in range(1, 7)]
        + ["indice_completitud_drivers", "latitud", "longitud"]
        + ["matricula_ciclo_anterior", "variacion_matricula_alumnos"]
    )
    faltantes = sorted({campo for e in items for campo in esperados if campo not in e})

    assert not faltantes, (
        f"la imagen desplegada no expone {faltantes}: es anterior a este contrato — "
        "hay que reconstruir y redesplegar la imagen de la API"
    )

    con_coordenada = sum(1 for e in items if e["latitud"] is not None)
    con_anterior = sum(1 for e in items if e["matricula_ciclo_anterior"] is not None)
    print(
        f"\n  escuelas en la página: {len(items)} · con coordenada: {con_coordenada}"
        f" · con ciclo anterior: {con_anterior}"
    )


def test_una_escuela_concreta_conserva_el_detalle() -> None:
    """Los campos subieron al listado, no se movieron: el detalle sigue trayéndolos."""
    _requiere_sesion()
    items = _json_ok("/escuelas?size=1")["items"]
    if not items:
        pytest.skip("el despliegue no devolvió escuelas")

    detalle = _json_ok(f"/escuelas/{items[0]['cct']}")
    for campo in ("sostenimiento", "d1", "indice_completitud_drivers", "matricula_ciclo_anterior"):
        assert campo in detalle, campo
