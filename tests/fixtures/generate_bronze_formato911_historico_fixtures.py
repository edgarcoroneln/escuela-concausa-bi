"""Genera tests/fixtures/bronze_formato911_historico_sample.csv -- muestra sintetica y
anonimizada (<=500 filas, _Meta/Vault_Rules.md / CLAUDE.md Section3) de bronze.formato911_historico
(DS-01, distribucion HISTORICA multi-ciclo -- ver src/ingesta/extractor_formato911_historico.py),
para poder correr y probar localmente el modelo Silver/Gold nuevos que mitigan RISK-007/DEC-007
mientras la descarga real de los 6 ciclos completos no se ejecuta en este entorno.

Grano: cct x ciclo x turno. Cubre los 6 ciclos reales verificados (2019-2020 .. 2024-2025), con
la "suciedad" real que ya confirmamos con datos reales (ver DevLog 2026-08-21) y que Silver debe
resolver:

  - entidad/municipio CON cero a la izquierda en los ciclos legacy (confirmado real en 2019-2020
    y 2021-2022) vs SIN cero a la izquierda en 2024-2025 (confirmado real). Para 2020-2021,
    2022-2023 y 2023-2024 -- que NO se compararon columna por columna con datos reales -- este
    fixture asume el mismo patron que su vecino mas cercano solo para tener algo sintetico con
    que probar; no es un hecho verificado, es una eleccion de fixture (ver docstring del
    extractor: la deteccion real de columnas se hace en tiempo de ejecucion, no aqui).
  - nivel en MAYUSCULAS en los ciclos legacy (confirmado real 2019-2020/2021-2022) vs Capitalizado
    en 2024-2025 (confirmado real) -- ejercita el UPPER(TRIM(nivel)) que Silver debe aplicar para
    hacer match con gold.dim_escuela.nivel.
  - un mismo cct con 2 turnos en el mismo ciclo (bronze.formato911_historico es UNIQUE en
    cct+ciclo+turno, no solo cct+ciclo).
  - una reingesta del mismo (cct, ciclo, turno) con _ingested_at mas reciente y matricula
    corregida -- Silver debe quedarse con la mas reciente.
  - una entidad fuera de SCOPE_ENTIDADES (Oaxaca, "20") -- Bronze/Silver son nacionales, el
    filtro va en Gold (Data_Model.md Section7).

La matricula varia por ciclo (algunos grupos municipio x nivel crecen, otros decrecen) para que
el futuro modelo Gold tenga variacion real que agregar -- nunca la misma cifra en los 6 ciclos.

Uso:
    python tests/fixtures/generate_bronze_formato911_historico_fixtures.py
"""
import csv
import os

FIXTURES_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(FIXTURES_DIR, "bronze_formato911_historico_sample.csv")

SOURCE_NAME = "DS-01_FORMATO911_HISTORICO"

# URLs reales verificadas a mano por Diana (ver DevLog 2026-08-21 / extractor_formato911_historico.py)
SOURCE_URL_POR_CICLO = {
    "2019-2020": "https://repodatos.atdt.gob.mx/s_educacion_publica/f911/BASICA_2019-2020.csv",
    "2020-2021": "https://repodatos.atdt.gob.mx/s_educacion_publica/f911/BASICA_2020-2021.csv",
    "2021-2022": "https://repodatos.atdt.gob.mx/s_educacion_publica/f911/BASICA_2021-2022.csv",
    "2022-2023": "https://repodatos.atdt.gob.mx/s_educacion_publica/f911/BASICA_2022-2023.csv",
    "2023-2024": "https://repodatos.atdt.gob.mx/s_educacion_publica/f911/ESTANDAR_BASICA_I2324.csv",
    "2024-2025": (
        "https://repodatos.atdt.gob.mx/api_update/secretaria_educacion/"
        "registro_alumnado_personal_docente_educacion_basica_media_superior_formato_911/"
        "educacion_basica_2024_2025.csv"
    ),
}

# Formato "legacy" (confirmado real en 2019-2020 y 2021-2022): entidad/municipio con cero a la
# izquierda, nivel en MAYUSCULAS. Formato "nuevo" (confirmado real solo en 2024-2025): sin cero a
# la izquierda, nivel Capitalizado. 2020-2021/2022-2023 se asumen legacy y 2023-2024 se asume
# nuevo solo para el fixture -- NO es un hecho verificado (ver docstring arriba).
FORMATO_POR_CICLO = {
    "2019-2020": "legacy",
    "2020-2021": "legacy",
    "2021-2022": "legacy",
    "2022-2023": "legacy",
    "2023-2024": "nuevo",
    "2024-2025": "nuevo",
}

CICLOS = list(SOURCE_URL_POR_CICLO.keys())

# entidad -> municipio (un solo municipio por entidad para mantener el fixture chico)
ENTIDAD_MUNICIPIO = {
    "09": "003",  # CDMX (SCOPE)
    "15": "033",  # Edomex (SCOPE)
    "19": "039",  # Nuevo Leon (SCOPE)
    "14": "039",  # Jalisco (SCOPE)
    "20": "067",  # Oaxaca (fuera de SCOPE_ENTIDADES; Bronze/Silver son nacionales igual)
}

NIVELES = ["PREESCOLAR", "PRIMARIA", "SECUNDARIA"]
TIPO_POR_NIVEL = {"PREESCOLAR": "JN", "PRIMARIA": "PR", "SECUNDARIA": "SN"}

COLUMNAS = [
    "cct", "ciclo", "turno", "entidad", "municipio", "nivel", "matricula_total",
    "_ingested_at", "_source", "_source_url",
]

INGESTED_AT_BASE = "2026-08-21T20:00:00+00:00"
INGESTED_AT_REINGESTA = "2026-08-22T09:00:00+00:00"


def _formatear_entidad_municipio(entidad: str, municipio: str, formato: str) -> tuple:
    if formato == "legacy":
        return entidad, municipio
    # "nuevo": sin cero a la izquierda -- tal cual se confirmo real en 2024-2025
    return str(int(entidad)), str(int(municipio))


def _formatear_nivel(nivel: str, formato: str) -> str:
    if formato == "legacy":
        return nivel
    return nivel.capitalize()


def generar():
    rows = []
    folio = 0

    for entidad, municipio in ENTIDAD_MUNICIPIO.items():
        for nivel in NIVELES:
            # 2 ccts por grupo municipio x nivel, para que la futura agregacion Gold promedie
            # mas de una escuela (no solo el caso trivial de 1 escuela = 1 grupo).
            for n_escuela in range(2):
                folio += 1
                tipo = TIPO_POR_NIVEL[nivel]
                cct = f"{entidad}D{tipo}{folio:04d}A"
                # matricula base + tendencia propia del cct (algunos crecen, otros decrecen) --
                # nunca la misma cifra en los 6 ciclos.
                base = 80 + (folio * 7) % 200
                tendencia = (folio % 5) - 2  # -2..+2 alumnos por ciclo

                for i, ciclo in enumerate(CICLOS):
                    formato = FORMATO_POR_CICLO[ciclo]
                    entidad_fmt, municipio_fmt = _formatear_entidad_municipio(
                        entidad, municipio, formato
                    )
                    nivel_fmt = _formatear_nivel(nivel, formato)
                    matricula = max(base + tendencia * i, 1)

                    rows.append({
                        "cct": cct,
                        "ciclo": ciclo,
                        "turno": "1",
                        "entidad": entidad_fmt,
                        "municipio": municipio_fmt,
                        "nivel": nivel_fmt,
                        "matricula_total": matricula,
                        "_ingested_at": INGESTED_AT_BASE,
                        "_source": SOURCE_NAME,
                        "_source_url": SOURCE_URL_POR_CICLO[ciclo],
                    })

    # Caso 1: un cct reporta 2 turnos en el mismo ciclo (matutino/vespertino) -- ejercita la
    # UNIQUE de bronze en (cct, ciclo, turno), no solo (cct, ciclo).
    fila_turno_2 = dict(rows[0])
    fila_turno_2["turno"] = "2"
    fila_turno_2["matricula_total"] = 35
    rows.append(fila_turno_2)

    # Caso 2: reingesta del mismo (cct, ciclo, turno) con _ingested_at mas reciente y matricula
    # corregida -- Silver debe quedarse con esta version, no con la primera.
    reingesta = dict(rows[0])
    reingesta["matricula_total"] = reingesta["matricula_total"] + 4
    reingesta["_ingested_at"] = INGESTED_AT_REINGESTA
    rows.append(reingesta)

    with open(OUTPUT_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        w.writeheader()
        w.writerows(rows)

    return OUTPUT_PATH, len(rows)


if __name__ == "__main__":
    path, n = generar()
    print(f"Fixture generado: {path} ({n} filas)")