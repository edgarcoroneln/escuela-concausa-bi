"""TEST-015 — El parser de tablas del tablero PM respeta los pipes escapados.

BUG-040: `table_cells` partía la fila cruda por **todos** los pipes, incluido el de un
wikilink con alias (`[[ruta\\|texto]]`). Ese pipe no separa columnas: es sintaxis de
Obsidian, y el vault la escribe escapada 190+ veces. Al partir ahí, las columnas se
desplazaban y el campo `updated` recibía texto en vez de una fecha — sin que nada fallara,
porque la fila seguía teniendo suficientes celdas. El tablero publicó basura durante días.

Estas pruebas fijan el contrato: una celda con un pipe escapado sigue siendo UNA celda.
"""

import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "vault" / "_Meta" / "scripts"))

from generate_pm_dashboard import parse_execution, table_cells

FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")


# ── El contrato del parser ───────────────────────────────────────────────────


def test_un_pipe_escapado_no_abre_columna():
    fila = r"| US-999 | done | 2026-01-01 | — | [[vault/x/Doc\|alias]] y algo | 2026-01-02 |"
    celdas = table_cells(fila)
    assert len(celdas) == 6
    assert celdas[5] == "2026-01-02", "la fecha se desplazó de columna"


def test_el_alias_se_resuelve_a_su_texto():
    celdas = table_cells(r"| a | [[vault/x/Doc\|texto visible]] |")
    assert celdas[1] == "texto visible"


def test_varios_pipes_escapados_en_la_misma_celda():
    fila = r"| US-999 | done | 2026-01-01 | — | [[a\|uno]] · [[b\|dos]] · [[c\|tres]] | 2026-01-02 |"
    celdas = table_cells(fila)
    assert len(celdas) == 6
    assert celdas[5] == "2026-01-02"


def test_una_fila_sin_alias_no_cambia_de_comportamiento():
    fila = "| US-998 | done | 2026-01-01 | — | [[vault/x/Doc]] evidencia | 2026-01-02 |"
    celdas = table_cells(fila)
    assert len(celdas) == 6
    assert celdas[5] == "2026-01-02"


def test_los_pipes_reales_siguen_separando():
    assert len(table_cells("| a | b | c |")) == 3


# ── El archivo real, que es lo que se publica ────────────────────────────────


@pytest.fixture(scope="module")
def ejecucion():
    return parse_execution(RAIZ)


def test_toda_historia_tiene_una_fecha_en_updated(ejecucion):
    """El síntoma exacto de BUG-040, medido sobre la fuente canónica."""
    malas = {k: v["updated"][:40] for k, v in ejecucion.items() if not FECHA.fullmatch(v["updated"])}
    assert not malas, f"'updated' no es fecha en: {malas}"


def test_la_evidencia_no_queda_truncada(ejecucion):
    """Una celda cortada a la mitad deja un wikilink sin cerrar."""
    rotas = [k for k, v in ejecucion.items() if v["evidence"].count("[[") != v["evidence"].count("]]")]
    assert not rotas, f"evidencia con wikilink sin cerrar en: {rotas}"


def test_us004_conserva_su_evidencia_completa(ejecucion):
    r"""La fila que destapó el defecto: su texto llega hasta el final.

    La guarda vigila que el parser cruce los pipes escapados sin cortar la celda, no
    un contenido congelado: US-004 es una historia continua y su fila se actualiza en
    cada reconciliación. Fijar aquí la fecha del 29-ago hacía que la prueba reprobara
    ante una actualización legítima (pasó el 2026-09-05 al cerrar el entregable), y una
    guarda que falla cuando el cambio es correcto acaba relajándose. Se comprueba la
    ESTRUCTURA: que la última columna llegó -- prueba de que la fila no se truncó -- y
    que el wikilink con `\|` que destapó BUG-040 sigue del otro lado del corte.
    """
    fila = ejecucion["US-004"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", fila["updated"]), fila["updated"]
    # El alias del wikilink con `\|` sobrevive resuelto a su texto visible: si el pipe
    # escapado hubiera cortado la celda, este fragmento y todo lo que sigue faltarían.
    assert "plan de corrección del vault" in fila["evidence"]
    assert fila["evidence"].endswith("hasta el cierre del proyecto")


# ── El índice de DevLog alimenta las métricas por persona ────────────────────
#
# `build_engagement` cruza el conteo de DevLogs con el nombre canónico por coincidencia
# EXACTA. Una fila con el pipe sin escapar corre la columna y atribuye el DevLog a la
# descripción; una variante de nombre —sin acento, o el nombre corto— deja a esa persona
# con cero DevLogs aunque los haya escrito. Ambas cosas pasaron: el tablero contaba 25
# "autores" y mostraba a tres personas sin documentación.

sys.path.insert(0, str(RAIZ / "vault" / "_Meta" / "scripts"))
from check_ownership import leer_ownership
from generate_pm_dashboard import parse_devlog_authors


@pytest.fixture(scope="module")
def nombres_canonicos():
    datos = leer_ownership(str(RAIZ / "vault" / "_Meta" / "ownership.yml"))
    return {p["nombre"] for p in datos["personas"].values()}


def test_toda_fila_del_indice_de_devlog_tiene_5_columnas():
    ruta = RAIZ / "vault" / "_DevLog" / "_index.md"
    malas = []
    for numero, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        if linea.startswith("| [[vault/_DevLog/") and len(table_cells(linea)) != 5:
            malas.append(numero)
    assert not malas, f"filas con columnas desalineadas: {malas}"


def test_todo_autor_del_indice_existe_en_el_padron(nombres_canonicos):
    """Una variante de nombre no rompe nada: silenciosamente deja a alguien en cero."""
    autores = set(parse_devlog_authors(RAIZ))
    fuera = autores - nombres_canonicos
    assert not fuera, (
        f"autores que no coinciden con ningún nombre canónico: {sorted(fuera)}. "
        "Sus DevLogs no se le cuentan a nadie."
    )


# ── BUG-042 — una US sin fila en Execution_Status.md ya no cae a "planned" ───
#
# `state.get("status", "planned")` asumía que ausencia de fila == planificada. Pasó con
# 24 historias reales (algunas con PR ya mergeado) contadas como "planned" sin que nada
# fallara, durante días. El generador ahora exige la fila explícita.

from generate_pm_dashboard import build_snapshot


def test_las_91_historias_reales_tienen_fila(ejecucion):
    """El estado actual del archivo: cobertura completa, sin default silencioso."""
    from generate_pm_dashboard import parse_stories

    faltantes = [s["id"] for s in parse_stories(RAIZ) if s["id"] not in ejecucion]
    assert not faltantes, f"sin fila en Execution_Status.md: {faltantes}"


def test_una_historia_sin_fila_truena_en_vez_de_asumir_planned(monkeypatch):
    """El síntoma exacto de BUG-042, forzado: una US fuera del registro debe reventar."""
    import generate_pm_dashboard as gpd

    reales = gpd.parse_stories(RAIZ)
    con_huerfana = [*reales, {**reales[0], "id": "US-999z"}]
    monkeypatch.setattr(gpd, "parse_stories", lambda root: con_huerfana)

    with pytest.raises(ValueError, match=r"BUG-042.*US-999z"):
        build_snapshot(RAIZ)
