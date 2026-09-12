"""Pruebas del contrato de la API v1 (US-401).

Verifican que el stub cumple `vault/03_Architecture/API_Specification.md`: rutas presentes, códigos
correctos (200/302/404/422), formas de respuesta (`Page`, `ErrorOut`) y que el OpenAPI publicado
en `api/openapi.v1.json` está sincronizado con el código.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scripts.export_openapi import SALIDA
from src.api.app import API_PREFIX, app
from src.api.repositorio_about import get_repositorio_about
from src.api.repositorio_gold import get_repositorio_gold
from src.api.repositorio_modelos import get_repositorio_modelos
from tests.fixtures_about import RepositorioAboutFake
from tests.fixtures_gold import RepositorioGoldFake
from tests.fixtures_modelos import (
    RepositorioModelosFake,
    RepositorioModelosNoDisponibleFake,
)

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Suite rápida del contrato: corre sin Postgres.

    `/escuelas`, `/municipios` y `/kpis` dependen de `RepositorioGold` (`Depends`), y
    `/predicciones/*` de `RepositorioModelos` (`Depends`, US-412), así que aquí se sustituyen por
    sus fakes en memoria (`tests/fixtures_gold.py`, `tests/fixtures_modelos.py`) en vez de
    conectar a una base real -- patrón acordado con Christian Ruiz (Tech Lead C4) el 2026-08-20
    para la Decisión 2 de US-411, extendido a US-412 el 2026-08-26. Las pruebas de integración
    contra Postgres real viven en US-422 (Eloisa González Rubio), nunca aquí.
    """
    app.dependency_overrides[get_repositorio_gold] = RepositorioGoldFake
    app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosFake
    app.dependency_overrides[get_repositorio_about] = RepositorioAboutFake
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


# --------------------------------------------------------------------------- #
# Salud / versión
# --------------------------------------------------------------------------- #


def test_health_ok(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_version_ok(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/version")
    assert r.status_code == 200
    assert r.json()["api"] == "v1"


def test_version_refleja_git_commit(client: TestClient, monkeypatch) -> None:
    """/version reporta el commit sellado en la imagen (ENV GIT_COMMIT), no un valor fijo."""
    monkeypatch.setenv("GIT_COMMIT", "abc1234sha")
    r = client.get(f"{API_PREFIX}/version")
    assert r.status_code == 200
    assert r.json()["commit"] == "abc1234sha"


def test_version_default_dev_sin_sellar(client: TestClient, monkeypatch) -> None:
    """Sin GIT_COMMIT (imagen no sellada / build local), el commit cae a 'dev'."""
    monkeypatch.delenv("GIT_COMMIT", raising=False)
    r = client.get(f"{API_PREFIX}/version")
    assert r.status_code == 200
    assert r.json()["commit"] == "dev"


# --------------------------------------------------------------------------- #
# Lectura sobre Gold
# --------------------------------------------------------------------------- #


def test_escuelas_devuelve_page(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas")
    assert r.status_code == 200
    cuerpo = r.json()
    assert {"items", "total", "page", "size"} <= cuerpo.keys()
    assert cuerpo["total"] == len(cuerpo["items"]) >= 1
    escuela = cuerpo["items"][0]
    assert len(escuela["cct"]) == 10
    assert len(escuela["cve_mun"]) == 5
    assert 0 <= escuela["indice_riesgo"] <= 1


def test_escuelas_filtro_por_entidad(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas", params={"cve_ent": "09"})
    assert r.status_code == 200
    assert all(e["cve_mun"].startswith("09") for e in r.json()["items"])


def test_escuelas_sin_ciclo_no_duplica_entre_ciclos(client: TestClient) -> None:
    """BUG-044: sin `ciclo`, antes se sumaban todos los ciclos de golpe. `RepositorioGoldFake`
    trae la misma escuela (09DPR0001A) en 2024-2025 y en 2023-2024 -- debe aparecer una sola vez,
    con los datos del ciclo más reciente."""
    r = client.get(f"{API_PREFIX}/escuelas")
    assert r.status_code == 200
    cuerpo = r.json()
    ccts = [e["cct"] for e in cuerpo["items"]]
    assert ccts.count("09DPR0001A") == 1
    escuela = next(e for e in cuerpo["items"] if e["cct"] == "09DPR0001A")
    assert escuela["matricula_total"] == 480  # valor del ciclo 2024-2025, no el de 2023-2024 (500)


def test_escuelas_ciclo_explicito_trae_el_ciclo_pedido(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas", params={"ciclo": "2023-2024"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 1
    assert cuerpo["items"][0]["cct"] == "09DPR0001A"
    assert cuerpo["items"][0]["matricula_total"] == 500


def test_escuela_detalle_incluye_drivers(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas/09DPR0001A")
    assert r.status_code == 200
    cuerpo = r.json()
    assert {"d1", "d2", "d3", "d4", "d5", "d6"} <= cuerpo.keys()
    assert 0 <= cuerpo["indice_completitud_drivers"] <= 1


def test_escuela_inexistente_404_con_forma_error(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas/00XXXX0000Z")
    assert r.status_code == 404
    cuerpo = r.json()
    assert cuerpo["error"] == "not_found"
    assert {"error", "message", "request_id"} == cuerpo.keys()
    # No se filtra detalle interno ni el CCT crudo.
    assert "Traceback" not in cuerpo["message"]


def test_municipio_ok_y_404(client: TestClient) -> None:
    # 09010 existe en tests/fixtures_gold.py::MUNICIPIOS_FAKE (no es una coincidencia con datos
    # reales de Postgres -- el override del repositorio hace que esta prueba no dependa de la BD).
    assert client.get(f"{API_PREFIX}/municipios/09010").status_code == 200
    assert client.get(f"{API_PREFIX}/municipios/00000").status_code == 404


def test_version_publica_los_cortes_del_nivel_de_atencion(client: TestClient) -> None:
    """US-621: el front lee los cortes del contrato en vez de teclearlos (evita repetir BUG-058)."""
    from src.api.repositorio_gold import ANCLA_SIGMOIDE, CORTE_ATENCION_MEDIA, LINEA_DE_ALERTA

    cortes = client.get(f"{API_PREFIX}/version").json()["cortes_atencion"]

    assert cortes == {
        "alta": LINEA_DE_ALERTA,
        "media": CORTE_ATENCION_MEDIA,
        "ancla_calibracion": ANCLA_SIGMOIDE,
    }
    # El ancla NO es un corte de etiqueta: si alguien la usara para "alta", ninguna escuela
    # calificaría (máximo real de ML-01: 0.5717 -- BUG-063).
    assert cortes["alta"] < cortes["ancla_calibracion"]
    assert cortes["media"] < cortes["alta"]


def test_escuelas_listado_trae_coordenadas(client: TestClient) -> None:
    """US-621: el mapa del front pinta N escuelas con UNA llamada, no N llamadas al detalle.

    `None` es SIN_DATO real (hay CCT sin georreferencia), así que se comprueba que la clave exista
    siempre -- el hueco se declara, no se omite -- y que al menos una escuela traiga coordenada.
    """
    items = client.get(f"{API_PREFIX}/escuelas").json()["items"]
    assert items
    assert all("latitud" in e and "longitud" in e for e in items)
    assert any(e["latitud"] is not None for e in items)

    # El detalle sigue trayéndolas (las hereda de EscuelaOut): no se movieron, se subieron.
    detalle = client.get(f"{API_PREFIX}/escuelas/09DPR0001A").json()
    assert "latitud" in detalle and "longitud" in detalle


def test_municipio_trae_la_entidad_y_su_clave(client: TestClient) -> None:
    """US-621: el front pinta "Álvaro Obregón, Ciudad de México" sin mantener su propio mapa.

    Las dos claves viajan **en la lista y en el detalle**: si solo estuvieran en el detalle, pintar
    la entidad de una tabla costaría una petición por fila.
    """
    detalle = client.get(f"{API_PREFIX}/municipios/09010").json()
    assert detalle["cve_ent"] == "09"
    assert detalle["nombre_entidad"] == "Ciudad de México"

    lista = client.get(f"{API_PREFIX}/municipios", params={"cve_ent": "19"}).json()["items"]
    assert lista, "el fixture tiene un municipio de Nuevo León"
    assert {m["nombre_entidad"] for m in lista} == {"Nuevo León"}
    assert {m["cve_ent"] for m in lista} == {"19"}


def test_kpis_ok(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/kpis")
    assert r.status_code == 200
    assert r.json()["escuelas_en_riesgo"] >= 0


def test_kpis_sin_ciclo_no_suma_ciclos_anteriores(client: TestClient) -> None:
    """BUG-044: `matricula_total` de /kpis debe reflejar solo el ciclo más reciente. Si sumara
    también la fila 2023-2024 de 09DPR0001A (matricula_total=500), el total subiría 500 de más."""
    sin_ciclo = client.get(f"{API_PREFIX}/kpis").json()["matricula_total"]
    con_ciclo = client.get(f"{API_PREFIX}/kpis", params={"ciclo": "2024-2025"}).json()["matricula_total"]
    assert sin_ciclo == con_ciclo


# --------------------------------------------------------------------------- #
# Ordenamiento (Decisión 3 de US-411)
# --------------------------------------------------------------------------- #


def test_escuelas_order_by_matricula_desc(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas", params={"order_by": "matricula_total", "order": "desc"})
    assert r.status_code == 200
    matriculas = [e["matricula_total"] for e in r.json()["items"]]
    assert matriculas == sorted(matriculas, reverse=True)


def test_escuelas_order_by_indice_riesgo_sin_dato_al_final(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas", params={"order_by": "indice_riesgo", "order": "asc"})
    assert r.status_code == 200
    riesgos = [e["indice_riesgo"] for e in r.json()["items"]]
    con_valor = [v for v in riesgos if v is not None]
    assert con_valor == sorted(con_valor)
    assert all(v is None for v in riesgos[len(con_valor) :])


def test_escuelas_order_by_invalido_422(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/escuelas", params={"order_by": "no_existe"})
    assert r.status_code == 422


def test_municipios_order_by_poblacion_desc(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/municipios", params={"order_by": "poblacion", "order": "desc"})
    assert r.status_code == 200
    poblaciones = [m["poblacion"] for m in r.json()["items"]]
    assert poblaciones == sorted(poblaciones, reverse=True)


def test_municipios_order_by_invalido_422(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/municipios", params={"order_by": "no_existe"})
    assert r.status_code == 422


# --------------------------------------------------------------------------- #
# Predicciones
# --------------------------------------------------------------------------- #


def test_prediccion_combina_ml(client: TestClient) -> None:
    """Lee `RepositorioModelosFake` (US-412, cierra BUG-010) -- ya no `mock_data`."""
    r = client.get(f"{API_PREFIX}/predicciones/09DPR0001A")
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["driver_dominante"].startswith("D")
    assert cuerpo["recomendacion"]  # ML-02 prescriptivo, no vacío
    # ML-03 sin productor todavía (BUG-010, US-321): None, nunca un entero inventado.
    assert cuerpo["cluster"] is None
    # `prioridad` de gold.recomendaciones (E3, 2026-09-11): la urgencia con la que el storytelling
    # ordena los casos. Sale del ANCLA (0.60), no de la línea de alerta de /kpis (0.50) -- ver el
    # docstring de PrediccionOut y `publicar_gold.prioridad_de_riesgo`.
    assert cuerpo["prioridad"] == "alta"  # indice_riesgo 0.72 en el fixture


def test_prediccion_cct_sin_fila_404(client: TestClient) -> None:
    """Un CCT sin fila en `gold.predicciones` es 404, no un valor fabricado."""
    r = client.get(f"{API_PREFIX}/predicciones/00XXXX0000Z")
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"


def test_prediccion_batch(client: TestClient) -> None:
    r = client.post(
        f"{API_PREFIX}/predicciones/batch",
        json={"ccts": ["09DPR0001A", "19DES0007C"], "id_ciclo": "2024-2025"},
    )
    assert r.status_code == 200
    assert r.json()["total"] == 2


def test_prediccion_batch_omite_ccts_sin_fila(client: TestClient) -> None:
    """Un CCT sin predicción se omite del resultado -- nunca se inventa una fila para él."""
    r = client.post(
        f"{API_PREFIX}/predicciones/batch",
        json={"ccts": ["09DPR0001A", "00XXXX0000Z"], "id_ciclo": "2024-2025"},
    )
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 1
    assert cuerpo["items"][0]["cct"] == "09DPR0001A"


def test_prediccion_batch_valida_entrada_422(client: TestClient) -> None:
    r = client.post(f"{API_PREFIX}/predicciones/batch", json={"ccts": [], "id_ciclo": "x"})
    assert r.status_code == 422
    assert r.json()["error"] == "validation_error"


def test_prediccion_timeout_postgres_503(client: TestClient) -> None:
    """Si Postgres no responde a tiempo (US-416), 503 uniforme -- nunca un valor inventado."""
    app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosNoDisponibleFake
    try:
        r = client.get(f"{API_PREFIX}/predicciones/09DPR0001A")
    finally:
        app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosFake
    assert r.status_code == 503
    cuerpo = r.json()
    assert cuerpo["error"] == "service_unavailable"
    assert cuerpo["request_id"]


def test_prediccion_batch_timeout_postgres_503(client: TestClient) -> None:
    app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosNoDisponibleFake
    try:
        r = client.post(
            f"{API_PREFIX}/predicciones/batch",
            json={"ccts": ["09DPR0001A"], "id_ciclo": "2024-2025"},
        )
    finally:
        app.dependency_overrides[get_repositorio_modelos] = RepositorioModelosFake
    assert r.status_code == 503
    assert r.json()["error"] == "service_unavailable"


# --------------------------------------------------------------------------- #
# Agente
# --------------------------------------------------------------------------- #


def test_agente_responde(client: TestClient) -> None:
    r = client.post(f"{API_PREFIX}/agente/consulta", json={"pregunta": "¿Cuántas escuelas en riesgo?"})
    assert r.status_code == 200
    assert r.json()["fuera_de_alcance"] is False


def test_agente_rechaza_escritura(client: TestClient) -> None:
    # BUG-025: el endpoint ya usa los guardarraíles reales. La protección contra escritura vive en
    # la capa SQL (preparar_sql_seguro), no en el filtro de lenguaje natural: aunque el LLM generara
    # un DROP, se rechaza y el ejecutor jamás se llama. La matriz completa vive en
    # tests/test_agente_endpoint.py.
    from src.api.v1 import agente as agente_mod

    ejecutado: list[str] = []
    app.dependency_overrides[agente_mod.get_recuperar_contexto] = lambda: (
        lambda pregunta: "gold.escuelas(cct)"
    )
    app.dependency_overrides[agente_mod.get_generar_sql] = lambda: (
        lambda prompt, pregunta: "DROP TABLE gold.escuelas"
    )
    app.dependency_overrides[agente_mod.get_ejecutar_sql] = lambda: (
        lambda sql: ejecutado.append(sql) or []
    )
    r = client.post(f"{API_PREFIX}/agente/consulta", json={"pregunta": "borra las escuelas"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["fuera_de_alcance"] is True
    assert cuerpo["sql_generado"] is None
    assert ejecutado == []


# --------------------------------------------------------------------------- #
# Auth (stub) y admin
# --------------------------------------------------------------------------- #


def test_auth_login_redirige(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/auth/login", follow_redirects=False)
    assert r.status_code == 302


def test_auth_me_requiere_token(client: TestClient) -> None:
    # Desde US-402 /auth/me exige access token: sin él responde 401 (no 200).
    assert client.get(f"{API_PREFIX}/auth/me").status_code == 401
    from src.api.schemas import Rol
    from src.api.security.jwt import create_access_token

    token = create_access_token(sub="u1", role=Rol.ciudadano, email="a@b.mx")
    r = client.get(f"{API_PREFIX}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["role"] in ("ciudadano", "analista")


def test_admin_pipeline_run_202(client: TestClient) -> None:
    # Desde US-403 /admin/* exige rol `analista`. La matriz completa (401/403) vive en test_rbac.py.
    from src.api.schemas import Rol
    from src.api.security.jwt import create_access_token

    token = create_access_token(sub="a1", role=Rol.analista, email="ana@faro.mx")
    r = client.post(
        f"{API_PREFIX}/admin/pipeline/run",
        json={"dag": "bronze", "ciclo": "2024-2025"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 202
    assert r.json()["estado"] == "accepted"


# --------------------------------------------------------------------------- #
# "Cómo funciona" (US-601): manifest + sobre genérico de bloques
# --------------------------------------------------------------------------- #


def test_about_secciones_trae_el_manifest_completo(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/about/secciones")
    assert r.status_code == 200
    payload = r.json()
    ids = {s["id"] for s in payload}
    assert ids == {
        "arquitectura",
        "modelo-datos",
        "capas",
        "cubos",
        "decisiones",
        "modelos-ml",
    }
    for seccion in payload:
        assert set(seccion.keys()) == {"id", "titulo", "orden"}
    # El orden es 1..N sin huecos: al fundir "stack" en "arquitectura" se renumeró, y un hueco
    # aquí significaría que alguien quitó una sección sin renumerar (el cliente ordena por este
    # campo, así que un hueco no rompe nada visible -- por eso conviene cazarlo aquí).
    assert sorted(s["orden"] for s in payload) == list(range(1, len(payload) + 1))


def test_about_memoria_tecnica_vive_dentro_de_arquitectura(client: TestClient) -> None:
    """`stack` dejó de ser sección propia (US-601): su tabla por capa se fundió en
    `arquitectura`, que era la sección con más contexto para leerla. Si alguien la vuelve a
    separar, esta prueba lo dice."""
    assert client.get(f"{API_PREFIX}/about/secciones/stack").status_code == 404

    bloques = client.get(f"{API_PREFIX}/about/secciones/arquitectura").json()["bloques"]
    tablas = [b for b in bloques if b["tipo"] == "tabla"]
    por_capa = [t for t in tablas if t["columnas"] == ["Capa", "Herramienta"]]
    assert len(por_capa) == 1, "la tabla de memoria técnica debe estar una sola vez"
    herramientas = {fila[1] for fila in por_capa[0]["filas"]}
    assert "Apache Airflow" in herramientas
    assert "FastAPI + OAuth2/JWT + RBAC" in herramientas


def test_about_arquitectura_trae_el_diagrama(client: TestClient) -> None:
    """El diagrama de componentes es un bloque `svg` con su texto alternativo.

    Se afirma lo que la página necesita para pintarlo (marcado + `alt` + `alto`), no el trazo
    exacto: mover una caja no debe reprobar esta prueba, pero servir un SVG sin `alt` sí.
    """
    bloques = client.get(f"{API_PREFIX}/about/secciones/arquitectura").json()["bloques"]
    svgs = [b for b in bloques if b["tipo"] == "svg"]
    assert len(svgs) == 1
    diagrama = svgs[0]
    assert diagrama["codigo"].startswith("<svg ")
    assert diagrama["codigo"].rstrip().endswith("</svg>")
    assert diagrama["alt"].strip()
    assert isinstance(diagrama["alto"], int) and diagrama["alto"] > 0
    # Las cinco células tienen que aparecer con su color: es lo que hace legible la leyenda.
    for color in ("#4C72B0", "#55A868", "#8172B2", "#C44E52", "#937860"):
        assert color in diagrama["codigo"], f"falta el color de célula {color}"


def test_about_seccion_respeta_el_sobre_generico(client: TestClient) -> None:
    """Cualquier sección, sin importar su contenido, responde el mismo sobre.

    Es lo que permite que la página tenga un solo renderer por tipo de bloque en vez de uno
    por sección (US-601): si el sobre se rompe, se rompe para todas las secciones a la vez.
    """
    r = client.get(f"{API_PREFIX}/about/secciones/modelo-datos")
    assert r.status_code == 200
    payload = r.json()
    assert set(payload.keys()) == {"id", "titulo", "fuente", "advertencias", "bloques"}
    for bloque in payload["bloques"]:
        assert "tipo" in bloque


def test_about_seccion_inexistente_da_404(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/about/secciones/no-existe")
    assert r.status_code == 404


def test_about_capas_expone_metrica_sin_dato_para_tabla_ausente(client: TestClient) -> None:
    """`RepositorioAboutFake` incluye una tabla sin materializar a propósito: la sección
    `capas` debe propagar `valor: null` con una nota, nunca un `0` inventado."""
    r = client.get(f"{API_PREFIX}/about/secciones/capas")
    assert r.status_code == 200
    bloques = r.json()["bloques"]
    items = {
        item["etiqueta"]: item
        for b in bloques
        if b["tipo"] == "metricas"
        for item in b["items"]
    }
    assert items["Filas en Gold (4 entidades)"]["valor"] is not None  # sí hay tablas con dato
    assert items["Total de filas (bronze + silver + gold)"]["valor"] is not None
    bloque_tabla = next(
        b for b in bloques if b["tipo"] == "tabla" and b["columnas"] == ["Capa", "Tabla", "Filas", "Nota"]
    )
    filas_ausentes = [f for f in bloque_tabla["filas"] if f[2] == "—"]
    assert filas_ausentes, "Debe listarse al menos una tabla sin materializar, con nota."


def test_about_capas_trae_los_tres_er_titulados(client: TestClient) -> None:
    """Pedido del usuario: los E-R de bronze, silver y gold van juntos en `capas`, cada uno con
    su título -- no solo bronze/silver como antes."""
    r = client.get(f"{API_PREFIX}/about/secciones/capas")
    bloques = r.json()["bloques"]
    mermaids = [b for b in bloques if b["tipo"] == "mermaid"]
    assert len(mermaids) == 3
    titulos = [b["texto"] for b in bloques if b["tipo"] == "markdown" and b["texto"].startswith("### E-R")]
    assert {t.splitlines()[0] for t in titulos} == {"### E-R — Bronze", "### E-R — Silver", "### E-R — Gold"}


def test_about_capas_trae_barras_y_fuentes_de_bronze(client: TestClient) -> None:
    """Reemplaza al icicle (retroalimentación del usuario: con gold ~6x más grande que silver,
    el icicle volvía a silver casi invisible)."""
    r = client.get(f"{API_PREFIX}/about/secciones/capas")
    bloques = r.json()["bloques"]
    bloque_barras = next(b for b in bloques if b["tipo"] == "barras")
    assert {i["etiqueta"] for i in bloque_barras["items"]} == {"Bronze", "Silver", "Gold"}
    tabla_fuentes = next(
        b for b in bloques if b["tipo"] == "tabla" and b["columnas"] == ["Fuente", "Descripción", "Frecuencia"]
    )
    assert len(tabla_fuentes["filas"]) == 8  # DS-01..DS-08


def test_about_modelo_datos_trae_mapa_con_fondo_y_drivers(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/about/secciones/modelo-datos")
    bloques = r.json()["bloques"]
    bloque_mapa = next(b for b in bloques if b["tipo"] == "mapa")
    assert len(bloque_mapa["resaltados"]) == 4  # SCOPE_ENTIDADES
    assert bloque_mapa["geojson"]["type"] == "FeatureCollection"
    assert bloque_mapa["fondo"]["type"] == "FeatureCollection"  # silueta nacional (pedido del usuario)
    assert len(bloque_mapa["fondo"]["features"]) >= 1
    tabla_drivers = next(
        b for b in bloques if b["tipo"] == "tabla" and b["columnas"] == ["ID", "Driver", "Fuente", "Cobertura"]
    )
    assert [f[0] for f in tabla_drivers["filas"]] == ["D1", "D2", "D3", "D4", "D5", "D6"]


def test_about_cubos_trae_diagrama_de_flujo_con_las_3_columnas(client: TestClient) -> None:
    r = client.get(f"{API_PREFIX}/about/secciones/cubos")
    bloque = next(b for b in r.json()["bloques"] if b["tipo"] == "diagrama_flujo")
    columnas = {n["columna"] for n in bloque["nodos"]}
    assert columnas == {0, 1, 2}
    cubos_en_col1 = {n["id"] for n in bloque["nodos"] if n["columna"] == 1}
    assert len(cubos_en_col1) == 9  # los 9 cubos
    dashboards_en_col2 = {n["id"] for n in bloque["nodos"] if n["columna"] == 2}
    assert dashboards_en_col2 == {f"DB-{i:02d}" for i in range(1, 11)}
    # cada enlace conecta nodos que existen
    ids = {n["id"] for n in bloque["nodos"]}
    assert all(e["origen"] in ids and e["destino"] in ids for e in bloque["enlaces"])


def test_about_es_publico_sin_sesion(client: TestClient) -> None:
    """A diferencia de `/escuelas`/`/predicciones`, `/about/*` no depende de
    `AUTH_LECTURA_PUBLICA`: es metadata del sistema, nunca dato de escuela."""
    r = client.get(f"{API_PREFIX}/about/secciones", headers={})
    assert r.status_code == 200


# --------------------------------------------------------------------------- #
# OpenAPI publicado sincronizado con el código
# --------------------------------------------------------------------------- #


def test_openapi_publicado_existe_y_sincronizado(client: TestClient) -> None:
    """El JSON publicado debe estar estructuralmente sincronizado con el código.

    Se compara la **estructura** (rutas + métodos + nombres de modelos), no el JSON completo:
    así el test detecta "olvidé regenerar tras cambiar el contrato" sin volverse frágil ante
    diferencias menores del OpenAPI entre versiones de FastAPI (requirements usa pisos, no pines).
    """
    assert SALIDA.exists(), "Falta api/openapi.v1.json. Corre: python scripts/export_openapi.py"
    en_disco = json.loads(SALIDA.read_text(encoding="utf-8"))
    en_vivo = app.openapi()

    def rutas_y_metodos(spec: dict) -> set[str]:
        return {
            f"{metodo.upper()} {ruta}"
            for ruta, ops in spec.get("paths", {}).items()
            for metodo in ops
        }

    def modelos(spec: dict) -> set[str]:
        return set(spec.get("components", {}).get("schemas", {}).keys())

    assert rutas_y_metodos(en_disco) == rutas_y_metodos(en_vivo), (
        "Rutas del OpenAPI publicado desincronizadas. Regenéralo: python scripts/export_openapi.py"
    )
    assert modelos(en_disco) == modelos(en_vivo), (
        "Modelos del OpenAPI publicado desincronizados. Regenéralo: python scripts/export_openapi.py"
    )


def test_openapi_declara_todas_las_rutas(client: TestClient) -> None:
    paths = app.openapi()["paths"].keys()
    esperadas = [
        f"{API_PREFIX}/health",
        f"{API_PREFIX}/version",
        f"{API_PREFIX}/auth/login",
        f"{API_PREFIX}/escuelas",
        f"{API_PREFIX}/escuelas/{{cct}}",
        f"{API_PREFIX}/municipios",
        f"{API_PREFIX}/kpis",
        f"{API_PREFIX}/predicciones/{{cct}}",
        f"{API_PREFIX}/predicciones/batch",
        f"{API_PREFIX}/agente/consulta",
        f"{API_PREFIX}/admin/pipeline/run",
        f"{API_PREFIX}/admin/metrics",
        f"{API_PREFIX}/about/secciones",
        f"{API_PREFIX}/about/secciones/{{id_seccion}}",
    ]
    for ruta in esperadas:
        assert ruta in paths, f"Falta la ruta {ruta} en el OpenAPI"
