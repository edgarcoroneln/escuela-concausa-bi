"""Pruebas del extractor de DS-01 Formato 911 -- distribución HISTÓRICA multi-ciclo
(`src/ingesta/extractor_formato911_historico.py`), mitigación de RISK-007/DEC-007.

Lo que más importa proteger aquí, con datos sintéticos que reproducen la ESTRUCTURA real
verificada a mano (ver docstring del módulo bajo prueba y DevLog 2026-08-21), no con
suposiciones:

- La detección de la columna llave de escuela nunca debe "adivinar": si el archivo no trae
  ninguna de las dos variantes ya confirmadas (`clave_cct` / `clavecct`), debe fallar
  explícito, no seguir con un nombre inventado.
- La validación de columnas fijas (`entidad`, `municipio`, `nivel`, `periodo`, `insc_t`,
  `turno`) debe fallar explícito si falta alguna, no rellenar en silencio.
- `matricula_total` (de `insc_t`) debe coercer a nulo lo que no sea numérico, nunca tronar
  ni inventar un cero.
- Un mismo cct con más de un turno en el mismo ciclo debe preservar TODAS sus filas -- el
  grano de bronze es cct x ciclo x turno (ver `matricula_historica.sql`, que sí agrega).
- `extraer_formato911_historico` debe rechazar cualquier ciclo sin URL verificada ANTES de
  intentar descargar nada -- ni siquiera los ciclos válidos de la misma llamada.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.ingesta.extractor_formato911_historico import (
    COLUMNAS_FIJAS_REQUERIDAS,
    SOURCE_NAME,
    VARIANTES_COLUMNA_CCT,
    _detectar_columna_cct,
    _parsear_ciclo,
    _validar_columnas_fijas,
    extraer_formato911_historico,
)

# --------------------------------------------------------------------------- _detectar_columna_cct


def test_detecta_columna_cct_formato_nuevo() -> None:
    """2024-2025 trae `clave_cct` (verificado real, ver docstring del módulo)."""
    assert _detectar_columna_cct(["clave_cct", "entidad", "municipio"]) == "clave_cct"


def test_detecta_columna_cct_formato_legado() -> None:
    """2019-2020 y 2021-2022 traen `clavecct` (verificado real, ver docstring del módulo)."""
    assert _detectar_columna_cct(["clavecct", "entidad", "municipio"]) == "clavecct"


def test_prefiere_clave_cct_si_ambas_variantes_estan_presentes() -> None:
    """Caso límite no observado en los 3 ciclos comparados a mano, pero el orden de
    `VARIANTES_COLUMNA_CCT` decide de forma determinista -- se documenta con una prueba en
    vez de dejarlo implícito."""
    assert VARIANTES_COLUMNA_CCT[0] == "clave_cct"
    assert _detectar_columna_cct(["clavecct", "clave_cct"]) == "clave_cct"


def test_columna_cct_desconocida_falla_explicito_en_vez_de_adivinar() -> None:
    """Un tercer formato no verificado (ej. 2020-2021/2022-2023/2023-2024, nunca comparados
    columna por columna) debe frenar el pipeline, no inventar un nombre."""
    with pytest.raises(ValueError, match=SOURCE_NAME):
        _detectar_columna_cct(["llave_escuela", "entidad", "municipio"])


# --------------------------------------------------------------------------- _validar_columnas_fijas


def test_columnas_fijas_completas_no_truena() -> None:
    _validar_columnas_fijas(list(COLUMNAS_FIJAS_REQUERIDAS) + ["clave_cct", "otra_columna"])


def test_columnas_fijas_faltantes_reporta_exactamente_cuales() -> None:
    columnas_incompletas = ["clave_cct", "entidad", "municipio"]  # faltan nivel/periodo/insc_t/turno
    with pytest.raises(ValueError) as exc_info:
        _validar_columnas_fijas(columnas_incompletas)
    for faltante in ["nivel", "periodo", "insc_t", "turno"]:
        assert faltante in str(exc_info.value)


# --------------------------------------------------------------------------- _parsear_ciclo


def _escribir_csv(tmp_path, nombre_columna_cct: str, filas: list[dict]) -> str:
    """Arma un CSV sintético con la estructura real (columna cct variable + columnas fijas
    verificadas), en el orden en que de verdad llega el archivo (cct primero, como en los 3
    encabezados comparados a mano)."""
    columnas = [nombre_columna_cct] + list(COLUMNAS_FIJAS_REQUERIDAS)
    df = pd.DataFrame(filas, columns=columnas)
    ruta = tmp_path / "formato911_historico_sintetico.csv"
    df.to_csv(ruta, index=False)
    return str(ruta)


def test_parsear_ciclo_formato_nuevo_clave_cct(tmp_path) -> None:
    ruta = _escribir_csv(
        tmp_path,
        "clave_cct",
        [
            {
                "clave_cct": "09DPR0001A", "entidad": "9", "municipio": "10",
                "nivel": "Primaria", "periodo": "2024-2025", "insc_t": "120", "turno": "1",
            },
        ],
    )
    url = "https://ejemplo.test/x.csv"
    resultado = _parsear_ciclo(ruta, "2024-2025", url)

    assert list(resultado.columns) == [
        "cct", "ciclo", "turno", "entidad", "municipio", "nivel", "matricula_total",
        "_ingested_at", "_source", "_source_url",
    ]
    fila = resultado.iloc[0]
    assert fila["cct"] == "09DPR0001A"
    assert fila["ciclo"] == "2024-2025"
    assert fila["turno"] == "1"
    assert fila["matricula_total"] == 120
    assert fila["_source"] == SOURCE_NAME
    assert fila["_source_url"] == url


def test_parsear_ciclo_formato_legado_clavecct(tmp_path) -> None:
    """Mismo resultado canónico con el nombre de columna legado (`clavecct`, sin guion bajo) --
    la variante de nombre no debe filtrarse al esquema de salida."""
    ruta = _escribir_csv(
        tmp_path,
        "clavecct",
        [
            {
                "clavecct": "09DPR0001A", "entidad": "09", "municipio": "010",
                "nivel": "PRIMARIA", "periodo": "2019-2020", "insc_t": "85", "turno": "1",
            },
        ],
    )
    resultado = _parsear_ciclo(ruta, "2019-2020", "https://ejemplo.test/legado.csv")

    assert "clavecct" not in resultado.columns
    assert resultado.iloc[0]["cct"] == "09DPR0001A"
    assert resultado.iloc[0]["matricula_total"] == 85


def test_insc_t_no_numerico_se_coerce_a_nulo_no_truena(tmp_path) -> None:
    """`insc_t` corrupto o vacío no debe tronar el parseo ni inventarse un 0 -- debe quedar
    nulo, igual que ya se exige para D5/D6 en el resto del proyecto (SIN_DATO explícito,
    nunca cero silencioso)."""
    ruta = _escribir_csv(
        tmp_path,
        "clave_cct",
        [
            {
                "clave_cct": "09DPR0002B", "entidad": "9", "municipio": "10",
                "nivel": "Primaria", "periodo": "2024-2025", "insc_t": "N/D", "turno": "1",
            },
        ],
    )
    resultado = _parsear_ciclo(ruta, "2024-2025", "https://ejemplo.test/x.csv")
    assert pd.isna(resultado.iloc[0]["matricula_total"])


def test_mismo_cct_dos_turnos_preserva_ambas_filas(tmp_path) -> None:
    """Grano de bronze: cct x ciclo x turno. Un cct con matrícula distinta por turno (caso real
    confirmado con datos de 2024-2025, ver DevLog) no debe colapsarse aquí -- la suma pasa en
    silver.matricula_historica, no en el extractor."""
    ruta = _escribir_csv(
        tmp_path,
        "clave_cct",
        [
            {
                "clave_cct": "01DES0001O", "entidad": "1", "municipio": "1",
                "nivel": "Secundaria", "periodo": "2024-2025", "insc_t": "541", "turno": "1",
            },
            {
                "clave_cct": "01DES0001O", "entidad": "1", "municipio": "1",
                "nivel": "Secundaria", "periodo": "2024-2025", "insc_t": "63", "turno": "2",
            },
        ],
    )
    resultado = _parsear_ciclo(ruta, "2024-2025", "https://ejemplo.test/x.csv")

    assert len(resultado) == 2
    matriculas_por_turno = dict(zip(resultado["turno"], resultado["matricula_total"]))
    assert matriculas_por_turno == {"1": 541, "2": 63}


def test_parsear_ciclo_falla_si_falta_columna_fija(tmp_path) -> None:
    """`_parsear_ciclo` debe propagar el mismo error explícito de `_validar_columnas_fijas`,
    no seguir adelante con una columna faltante."""
    ruta = tmp_path / "sin_turno.csv"
    pd.DataFrame([{
        "clave_cct": "09DPR0001A", "entidad": "9", "municipio": "10",
        "nivel": "Primaria", "periodo": "2024-2025", "insc_t": "120",
        # falta "turno" a propósito
    }]).to_csv(ruta, index=False)

    with pytest.raises(ValueError, match="turno"):
        _parsear_ciclo(str(ruta), "2024-2025", "https://ejemplo.test/x.csv")


# --------------------------------------------------------------------------- extraer_formato911_historico


def test_ciclo_sin_url_verificada_falla_antes_de_descargar_nada(monkeypatch) -> None:
    """Ni siquiera debe intentar la descarga del ciclo válido si otro ciclo de la misma
    llamada no tiene URL verificada -- todo o nada, nunca una descarga a medias."""

    def _requests_get_no_deberia_llamarse(*args, **kwargs):
        raise AssertionError(
            "extraer_formato911_historico() llamó a requests.get() antes de validar los "
            "ciclos -- no debería descargar nada si algún ciclo pedido no tiene URL verificada."
        )

    monkeypatch.setattr("requests.get", _requests_get_no_deberia_llamarse)

    with pytest.raises(ValueError, match="2018-2019"):
        extraer_formato911_historico(["2024-2025", "2018-2019"])