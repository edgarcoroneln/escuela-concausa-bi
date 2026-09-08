"""Prueba de la página de Dashboards embebidos (US-206) con un Superset simulado.

Cubre el contrato AC-002.1: sin guest token válido NO se muestran tableros (se avisa y no
se dibujan los filtros). Usa solo accesores estables del API de pruebas de Streamlit.
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
    """Réplica mínima de la API de Superset; el guest token se configura por instancia."""

    guest_status = 200

    def do_POST(self) -> None:
        if self.path == "/api/v1/security/login":
            self._respond({"access_token": "admin-token"})
            return
        if self.path == "/api/v1/security/guest_token/":
            if self.guest_status == 200:
                self._respond({"token": "guest-token"})
            else:
                self._respond({"msg": "guest token deshabilitado"}, status=self.guest_status)
            return
        self._respond({}, status=404)

    def do_GET(self) -> None:
        if self.path.startswith("/api/v1/dashboard/"):
            self._respond(
                {"result": [{"uuid": "uuid-00000000-0000-0000-0000-000000000001"}]}
            )
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


def test_con_guest_token_valido_dibuja_los_filtros(superset_fake: SupersetHTTPFake) -> None:
    superset_fake.guest_status = 200
    app = AppTest.from_file(str(PAGINA)).run(timeout=20)

    assert not app.exception, app.exception
    assert app.title[0].value == "Dashboards"
    # Con token válido la página llega a dibujar los filtros globales AC-002.2.
    assert len(app.sidebar.selectbox) >= 2
    # Y no muestra el aviso de "sin token" (no hay warning/error).
    assert not app.warning
    assert not app.error


def test_con_guest_token_rechazado_no_hay_tableros_ni_filtros(
    superset_fake: SupersetHTTPFake,
) -> None:
    # AC-002.1: si Superset rechaza el guest token, no se muestra ningún tablero.
    superset_fake.guest_status = 401
    app = AppTest.from_file(str(PAGINA)).run(timeout=20)

    assert not app.exception, app.exception
    assert app.title[0].value == "Dashboards"
    # Avisa al usuario (warning) en vez de renderizar.
    assert len(app.warning) >= 1
    # No se dibujan los filtros, señal de que no se llegó a la sección de iframes.
    assert len(app.sidebar.selectbox) == 0
