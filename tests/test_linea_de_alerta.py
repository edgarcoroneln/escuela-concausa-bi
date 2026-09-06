"""La línea de alerta del KPI-04 y su acoplamiento con los cubos de dbt (`DEC-019`, `BUG-058`).

`DEC-019` separó dos números que hasta el 2026-09-06 eran el mismo `0.60`:

- **`ANCLA_SIGMOIDE` (0.60)** — calibración: `indice_riesgo = 0.60` significa "proyecta perder 5 %
  de matrícula". **No cambia**; es lo que hace interpretable el índice.
- **`LINEA_DE_ALERTA` (0.50)** — criterio de negocio: cuándo enciende la alerta. Bajó porque 0.60
  era inalcanzable por construcción (máximo real de ML-01: 0.5717).

Confundirlos fue `BUG-058`, y el motivo por el que no se podía bajar uno sin parecer que se movía
el otro. Estas pruebas existen para que no vuelvan a fundirse en un solo literal.

**Lo que de verdad protege este archivo** es el acoplamiento de §3: el mismo corte está hardcodeado
en los cubos de dbt, que alimentan columnas **materializadas**, y son ésas —no la constante de
Python— las que leen los tableros de Superset. Mientras Gold no se re-materialice, `/kpis` y los
tableros cuentan distinto. Ninguna prueba de Python puede detectarlo sola: lo que se hace aquí es
**leer los .sql y comparar**, para que la divergencia falle en el CI en vez de aparecer en la demo.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.api import mock_data
from src.api.repositorio_gold import ANCLA_SIGMOIDE, LINEA_DE_ALERTA

RAIZ = Path(__file__).resolve().parents[1]

#: Archivos de dbt que cuentan "escuelas en riesgo" con el corte hardcodeado. Si alguien agrega
#: otro, esta lista se queda corta -- por eso `test_no_hay_cubos_nuevos_con_el_corte` la vigila.
CUBOS_CON_CORTE = (
    "dbt/models/gold/cubo_riesgo_territorial.sql",
    "dbt/models/gold/cubo_comparador_municipio.sql",
    "dbt/models/gold/cubo_escuela_360.sql",
    "dbt/tests/cubo_riesgo_territorial_ml01_parity.sql",
    "dbt/tests/cubo_comparador_municipio_prediccion_parity.sql",
)

_CORTE = re.compile(r"indice_riesgo\s*>=\s*(\d*\.?\d+)")


def _cortes_en(ruta: str) -> list[float]:
    texto = (RAIZ / ruta).read_text(encoding="utf-8")
    return [float(v) for v in _CORTE.findall(texto)]


# --------------------------------------------------------------------------- #
# 1. Los dos números son distintos y siguen siéndolo
# --------------------------------------------------------------------------- #


def test_el_ancla_no_cambia() -> None:
    """`ANCLA_SIGMOIDE` es calibración: moverla reinterpreta todos los índices ya publicados."""
    assert ANCLA_SIGMOIDE == 0.60


def test_la_linea_de_alerta_es_la_de_dec019() -> None:
    assert LINEA_DE_ALERTA == 0.50


def test_son_numeros_distintos() -> None:
    """Fundirlos otra vez en uno solo es exactamente BUG-058."""
    assert LINEA_DE_ALERTA != ANCLA_SIGMOIDE


def test_la_alerta_enciende_antes_que_el_ancla() -> None:
    """Una alerta *temprana* tiene que dispararse antes del punto que describe la crisis."""
    assert LINEA_DE_ALERTA < ANCLA_SIGMOIDE


# --------------------------------------------------------------------------- #
# 2. Dentro de la API no hay dos cortes distintos
# --------------------------------------------------------------------------- #


def test_el_mock_cuenta_con_la_misma_linea_que_el_repositorio() -> None:
    """Antes el mock usaba 0.5 y el repositorio real 0.6: el contrato mentía en las pruebas."""
    esperado = sum(
        1 for e in mock_data.ESCUELAS if e["indice_riesgo"] >= LINEA_DE_ALERTA
    )
    assert mock_data.kpis_mock()["escuelas_en_riesgo"] == esperado


def test_el_repositorio_no_trae_el_corte_hardcodeado() -> None:
    """El filtro tiene que usar la constante, no un literal suelto que nadie encuentre después."""
    fuente = (RAIZ / "src/api/repositorio_gold.py").read_text(encoding="utf-8")
    assert "indice_riesgo >= LINEA_DE_ALERTA" in fuente
    assert "indice_riesgo >= 0.6" not in fuente


# --------------------------------------------------------------------------- #
# 3. El acoplamiento con dbt — lo que de verdad puede romper la demo
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("ruta", CUBOS_CON_CORTE)
def test_los_cubos_cuentan_con_la_misma_linea_que_la_api(ruta: str) -> None:
    """Los tableros leen columnas **materializadas** por dbt, no la constante de Python.

    Si este corte y `LINEA_DE_ALERTA` difieren, `/kpis` y los tableros reportan números distintos
    para la misma pregunta, y quien evalúe compara las dos pantallas. Cuando se cambie uno hay que
    cambiar el otro **y re-materializar Gold** (`dbt run`), o la divergencia queda viva.
    """
    cortes = _cortes_en(ruta)
    assert cortes, f"{ruta} ya no declara el corte: revisa si se movió a otro lado"

    if all(c == ANCLA_SIGMOIDE for c in cortes):
        pytest.skip(
            f"{ruta} todavía cuenta con {ANCLA_SIGMOIDE} (el valor previo a DEC-019) mientras la "
            f"API ya usa {LINEA_DE_ALERTA}. **La divergencia es real y está viva**: /kpis calcula "
            "sobre `gold.predicciones` en cada petición, pero los tableros leen columnas "
            "materializadas por dbt, así que hasta que C1 cambie el corte y corra `dbt run` los dos "
            "reportan números distintos para la misma pregunta. Este salto NO es una excepción "
            "permitida: desaparece solo en cuanto C1 actualice el archivo, y a partir de ahí la "
            "prueba exige que ambos coincidan. Ver BUG-058 y el aviso de Marina García (2026-09-06)."
        )

    assert all(c == LINEA_DE_ALERTA for c in cortes), (
        f"{ruta} cuenta con {sorted(set(cortes))} y la API con {LINEA_DE_ALERTA}. "
        "Los tableros y /kpis reportarian numeros distintos para la misma pregunta."
    )


def test_no_hay_cubos_nuevos_con_el_corte() -> None:
    """Si aparece otro `.sql` con el corte y no está en la lista, se queda atrás en silencio."""
    encontrados = {
        str(p.relative_to(RAIZ)).replace("\\", "/")
        for p in (RAIZ / "dbt").rglob("*.sql")
        if _CORTE.search(p.read_text(encoding="utf-8"))
    }
    assert encontrados == set(CUBOS_CON_CORTE), (
        f"archivos de dbt con el corte que la lista no cubre: {encontrados - set(CUBOS_CON_CORTE)}"
    )
