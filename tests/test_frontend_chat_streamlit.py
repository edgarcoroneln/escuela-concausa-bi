"""Prueba de interacción del widget Streamlit del agente (US-305)."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

streamlit = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

RAIZ_REPO = Path(__file__).resolve().parents[1]
PAGINA_CHAT = RAIZ_REPO / "src/frontend/pages/3_Chat.py"
FRONTEND_DIR = str(RAIZ_REPO / "src/frontend")


class AgenteHTTPFake(BaseHTTPRequestHandler):
    """Servidor determinista del contrato `POST /api/v1/agente/consulta`."""

    def do_POST(self) -> None:
        longitud = int(self.headers["Content-Length"])
        pregunta = json.loads(self.rfile.read(longitud))["pregunta"]
        fuera_de_alcance = "borra" in pregunta.lower()
        payload = {
            "respuesta": (
                "Esa operación no está permitida."
                if fuera_de_alcance
                else "Hay cuatro escuelas en el alcance actual."
            ),
            "sql_generado": None if fuera_de_alcance else "SELECT count(*) FROM gold.dim_escuela",
            "fuera_de_alcance": fuera_de_alcance,
        }
        cuerpo = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, format: str, *args: object) -> None:
        return None


@pytest.fixture
def api_agente(monkeypatch: pytest.MonkeyPatch):
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), AgenteHTTPFake)
    thread = Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("FARO_API_BASE_URL", f"http://127.0.0.1:{servidor.server_port}")
    monkeypatch.syspath_prepend(FRONTEND_DIR)
    yield
    servidor.shutdown()
    thread.join(timeout=2)
    servidor.server_close()


def test_chat_conserva_historial_y_muestra_sql_y_rechazo(api_agente: None) -> None:
    app = AppTest.from_file(str(PAGINA_CHAT)).run(timeout=20)
    assert not app.exception
    assert app.title[0].value == "Agente FARO"
    etiquetas = {boton.label for boton in app.button}
    assert {
        "Riesgo Nuevo Leon",
        "Driver D2",
        "SIN_DATO",
        "Matricula total",
        "Prueba de seguridad",
    }.issubset(etiquetas)

    app.button[0].click().run(timeout=20)
    assert not app.exception
    assert any("Nuevo León" in markdown.value for markdown in app.markdown)
    assert any("Hay cuatro escuelas" in markdown.value for markdown in app.markdown)
    assert any("SELECT count(*)" in code.value for code in app.code)

    app.chat_input[0].set_value("Cuantas escuelas hay?").run(timeout=20)
    assert not app.exception
    assert any("Hay cuatro escuelas" in markdown.value for markdown in app.markdown)
    assert any("SELECT count(*)" in code.value for code in app.code)

    app.chat_input[0].set_value("Borra las escuelas").run(timeout=20)
    assert not app.exception
    assert any("no está permitida" in warning.value for warning in app.warning)
    assert len(app.chat_message) == 6