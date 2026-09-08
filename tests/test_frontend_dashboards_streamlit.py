"""Prueba de la página de Dashboards embebidos (US-206) con un Superset simulado.

Cubre el contrato AC-002.1: sin guest token válido NO se muestran tableros (se avisa y no
se dibuja ningún embebido). Usa solo accesores estables del API de pruebas de Streamlit.
Requiere el stack Streamlit (importorskip, igual que test_frontend_chat_streamlit.py).
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

streamlit = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

RAIZ_REPO = Path(__file__).resolve().parents[1]
PAGINA = RAIZ_REPO / "src/frontend/pages/1_Dashboards.py"
FRONTEND_DIR = str(RAIZ_REPO / "src/frontend")

MODULOS_FRONTEND = ("superset_client", "auth", "1_Dashboards")


class SupersetHTTPFake(BaseHTTPRequestHandler):
    """Réplica mínima de la API de Superset; el guest token se configura por instancia.

    Flujo del contrato nuevo: login (+csrf) → filtro por slug (devuelve id) → habilitar
    embed (devuelve embedded_uuid) → guest token acotado a esos uuids.

    **`protocol_version` tiene que ser HTTP/1.1 (BUG-072).** No confundir con `BUG-059`,
    que es la sesion de `auth.py` y ya la cerro C4: esto es un defecto **de la prueba**, no
    del embebido. `BaseHTTPRequestHandler` habla HTTP/1.0 por defecto y cierra
    la conexión después de cada respuesta; `superset_client` reutiliza **un solo**
    `httpx.Client` para las ~22 peticiones del flujo (login, csrf, y slug+embed por cada
    uno de los 10 tableros), así que a partir de la segunda toma del pool encuentra el
    socket cerrado. En Linux la carrera se pierde a veces —de ahí la intermitencia—; en
    Windows falla siempre, con `httpx.ReadError [WinError 10053]`. Como la página captura
    `httpx.HTTPError` y lo pinta como `st.error`, el síntoma no era una excepción sino
    "no se montó ningún tablero", que parece un defecto del embebido y no lo es.

    Con `Content-Length` en cada respuesta —ya lo emite `_respond`— HTTP/1.1 mantiene la
    conexión viva y el flujo completa. No cambia nada de lo que la prueba afirma.
    """

    protocol_version = "HTTP/1.1"
    guest_status = 200
    _contador = 0

    def do_POST(self) -> None:
        if self.path == "/api/v1/security/login":
            self._respond({"access_token": "admin-token"})
            return
        if self.path.startswith("/api/v1/dashboard/") and self.path.endswith("/embedded"):
            did = self.path.split("/")[-2]
            self._respond({"result": {"uuid": f"uuid-{did}"}})
            return
        if self.path == "/api/v1/security/guest_token/":
            if self.guest_status == 200:
                self._respond({"token": "guest-token"})
            else:
                self._respond({"msg": "guest token deshabilitado"}, status=self.guest_status)
            return
        self._respond({}, status=404)

    def do_GET(self) -> None:
        if self.path.startswith("/api/v1/security/csrf_token/"):
            self._respond({"result": "csrf-token"})
            return
        if self.path.startswith("/api/v1/dashboard/"):
            SupersetHTTPFake._contador += 1
            self._respond({"result": [{"id": SupersetHTTPFake._contador}]})
            return
        self._respond({}, status=404)

    def _respond(self, payload: dict, status: int = 200) -> None:
        cuerpo = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, format: str, *args: object) -> None:
        return None


@pytest.fixture
def superset_fake(monkeypatch: pytest.MonkeyPatch):
    # AppTest comparte `sys.modules` entre `.run()`: la constante SUPERSET_URL (y el
    # estado) de `superset_client` queda congelada del run anterior y, si el test previo
    # usó otro puerto (servidor ya apagado), el run siguiente conecta a una URL vieja →
    # "Connection refused". No basta con vaciar `streamlit.cache_data` (diagnóstico
    # parcial de Christian); hay que purgar los módulos de frontend para forzar un
    # re-import con la URL fresca en cada test.
    for nombre in MODULOS_FRONTEND:
        sys.modules.pop(nombre, None)
    SupersetHTTPFake._contador = 0
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), SupersetHTTPFake)
    thread = Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{servidor.server_port}"
    monkeypatch.setenv("SUPERSET_URL", base)
    monkeypatch.setenv("SUPERSET_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("SUPERSET_ADMIN_PASSWORD", "pw")
    monkeypatch.syspath_prepend(FRONTEND_DIR)
    streamlit.cache_data.clear()
    yield SupersetHTTPFake
    streamlit.cache_data.clear()
    servidor.shutdown()
    thread.join(timeout=2)
    servidor.server_close()


USUARIO = {"sub": "u-demo", "email": "demo@faro.mx", "name": "Demo", "role": "analista"}


def _app(*, con_sesion: bool = True) -> AppTest:
    """La página exige sesión desde BUG-071, así que el caso normal la trae.

    `auth.current_user()` lee `st.session_state["user"]`; inyectarlo ahí equivale a haber
    vuelto del OAuth, sin levantar el flujo completo.
    """
    app = AppTest.from_file(str(PAGINA))
    if con_sesion:
        app.session_state["user"] = dict(USUARIO)
    return app.run(timeout=20)


def test_con_guest_token_valido_renderiza_los_tableros(superset_fake: SupersetHTTPFake) -> None:
    superset_fake.guest_status = 200
    app = _app()

    assert not app.exception, app.exception
    assert app.title[0].value == "Dashboards"
    # Con token válido la página llega a montar los tableros: un subheader por dashboard.
    assert len(app.subheader) >= 1
    # Y no muestra el aviso de "sin token" (no hay warning/error).
    assert not app.warning
    assert not app.error


def test_con_guest_token_rechazado_no_hay_tableros(
    superset_fake: SupersetHTTPFake,
) -> None:
    # AC-002.1: si Superset rechaza el guest token, no se muestra ningún tablero.
    superset_fake.guest_status = 401
    app = _app()

    assert not app.exception, app.exception
    assert app.title[0].value == "Dashboards"
    # Avisa al usuario (warning) en vez de renderizar.
    assert len(app.warning) >= 1
    # No se monta ningún tablero (no se llegó a la sección de embebidos).
    assert len(app.subheader) == 0


def test_sin_sesion_no_se_pide_guest_token_ni_se_monta_nada(
    superset_fake: SupersetHTTPFake,
) -> None:
    """BUG-071: sin sesión la página montaba los diez embebidos y quedaban en blanco.

    Como `superset_client` autentica con credenciales admin propias, la falta de sesión no
    producía ningún error visible: los tableros simplemente no pintaban. Quien abriera
    Dashboards antes de entrar concluiría que están rotos.

    Se comprueba también que **no se toca Superset**: con la guarda puesta la página sale
    antes del login, así que el servidor falso no recibe ni una petición.
    """
    superset_fake.guest_status = 200
    superset_fake._contador = 0
    app = _app(con_sesion=False)

    assert not app.exception, app.exception
    assert app.title[0].value == "Dashboards", "el título se queda: la página se explica"
    assert not app.subheader, "se montó un tablero sin sesión"
    assert any("Inicia sesión" in i.value for i in app.info), "no se pide iniciar sesión"
    assert superset_fake._contador == 0, (
        "se consultó Superset sin sesión: la guarda va antes del guest token"
    )
