"""Pruebas del cableado condicional del LLM del agente en la app (BUG-025 / P-13).

El *fix* de P-13 conecta las dos etapas LLM (text-to-SQL y redactor) al seam de inyección del
agente, pero SOLO cuando hay `ANTHROPIC_API_KEY`. Sin la clave, el seam conserva sus defaults
seguros ("no configurado"): ni el CI ni el entorno local llaman a Anthropic y el agente degrada.

Estas pruebas verifican ese gobierno por configuración a nivel de `create_app`, sin ejecutar el LLM
real (solo se comprueba QUÉ callable queda cableado, nunca se invoca). El mismo patrón que el
cableado del ejecutor read-only en `test_ejecutor_gold.py::test_wiring_condicional_del_override`.
"""
from __future__ import annotations

import src.api.app as appmod
from src.api.config import Settings
from src.api.v1.agente import get_generar_sql, get_redactar_respuesta


def test_con_api_key_cablea_las_dos_etapas_llm(monkeypatch) -> None:
    """Con ANTHROPIC_API_KEY, la app sobreescribe get_generar_sql y get_redactar_respuesta."""
    from src.agente.llm import generar_sql_con_llm, redactar_respuesta_con_llm

    monkeypatch.setattr(
        appmod,
        "get_settings",
        lambda: Settings(anthropic_api_key="sk-ant-de-prueba", cors_origins=""),
    )
    app_con = appmod.create_app()

    assert get_generar_sql in app_con.dependency_overrides
    assert get_redactar_respuesta in app_con.dependency_overrides
    # Se cablean las funciones reales del adaptador. Resolver el override devuelve la referencia:
    # NO invoca al LLM (cero llamadas a la API de Anthropic en la prueba).
    assert app_con.dependency_overrides[get_generar_sql]() is generar_sql_con_llm
    assert app_con.dependency_overrides[get_redactar_respuesta]() is redactar_respuesta_con_llm


def test_sin_api_key_no_cablea_el_llm(monkeypatch) -> None:
    """Sin la clave, el seam queda con sus defaults seguros (el agente degrada, no llama al LLM)."""
    monkeypatch.setattr(
        appmod, "get_settings", lambda: Settings(anthropic_api_key="", cors_origins="")
    )
    app_sin = appmod.create_app()

    assert get_generar_sql not in app_sin.dependency_overrides
    assert get_redactar_respuesta not in app_sin.dependency_overrides
