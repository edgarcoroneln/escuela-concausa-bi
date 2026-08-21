---
id: TEST-010
title: "Great Expectations — DS-05 SINAICA (Bronze)"
owner: "Luis Enrique García Vázquez"
status: implemented
traces_up: ["02_Requirements/User_Stories", "02_Requirements/Requirements_Detailed"]
tags: [qa, testing, great-expectations, celula-1, bronze, sinaica]
---

# TEST-010 — Great Expectations DS-05 SINAICA (Bronze)

> Valida las dos tablas Bronze que produce `extractor_sinaica.py` (`US-122b`) para
> [[02_Requirements/User_Stories|US-123b]]. DS-04 (SESNSP) queda **fuera** de esta suite —
> sigue bloqueada, ver [[14_Data_Sources/DS-04_SESNSP_Incidencia_Delictiva]].
> → [[06_Quality_Testing/Automated/_index]] · [[14_Data_Sources/DS-05_SINAICA_Calidad_Aire]]

## Qué valida

| Ruta en repo | Comando | Corre en |
|---|---|---|
| `src/ingesta/validacion_sinaica.py` | `python -m src.ingesta.validacion_sinaica` | manual (aún no en CI/DAG) |

Usa Great Expectations 1.21 (API Fluent/declarativa: `ExpectationSuite` + `gx.expectations.*`,
no la API `validator` de las versiones 0.1x). Corre sobre el Parquet **más reciente** de cada
tabla en `data/bronze/sinaica/` y publica Data Docs (HTML) en
`great_expectations/uncommitted/data_docs/local_site/index.html` (no se versiona — ver
`great_expectations/.gitignore`, ya excluye `uncommitted/`).

### `sinaica_estaciones` (catálogo de estaciones)
- **Llave:** `id` no nulo y único.
- **Tipos:** `id` entero.
- **Nulos:** `nombre`, `latitud`, `longitud`.
- **Calidad de georreferencia:** `latitud`/`longitud` no deben ser el placeholder literal
  `"0.0"`/`"0"`/`""` que usa SINAICA para "sin coordenada" en vez de un nulo explícito.

### `sinaica_observaciones` (lecturas horarias)
- **Nulos:** `id_estacion`, `parametro`, `fecha`, `hora`, `valor`.
- **Tipos:** `hora` entero, `valor` flotante.
- **Rangos físicos:** `hora` ∈ [0,23]; `valor` ≥ 0 en general, y además un rango específico por
  contaminante (`O3` ≤ 0.5 ppm, `CO` ≤ 50 ppm, `NO2`/`SO2` ≤ 1 ppm, `PM2.5` ≤ 1000 µg/m³, `PM10`
  ≤ 1200 µg/m³ — generosos a propósito, para atrapar errores de captura, no para hacer cumplir el
  límite normativo NOM).
- **Catálogo válido:** `parametro` ∈ {O3, CO, NO2, SO2, PM2.5, PM10}; `val` ∈ {0,1}.
- **Duplicados / llave:** `(id_estacion, parametro, fecha, hora)` debe ser único dentro de un
  mismo archivo Bronze.

## Nota de diseño: por qué Bronze no está "tipado"

`latitud`, `longitud` y `municipioId` siguen siendo texto en esta suite a propósito. El medallón
es bronze (crudo) → silver (tipado/validado) → gold; el `cast(... as double precision)` real ya
vive en `dbt/models/silver/aire_estacion.sql`. Esta suite valida lo que Bronze **debe** garantizar
tal cual llega de la fuente: nulos, llave, duplicados y anomalías de captura — no reemplaza el
tipado de Silver.

## Hallazgo real (no es un bug de la suite)

Al correr la suite contra datos reales (2026-08-21), `sinaica_estaciones` **falla** dos
expectativas de forma consistente y reproducible:

| Columna | Nulos genuinos | Placeholder `"0.0"` literal | Total sin georreferencia usable |
|---|---:|---:|---:|
| `latitud` | 3 | 21 | 24 / 384 (≈6.3%) |
| `longitud` | 3 | 21 | 24 / 384 (≈6.3%) |

SINAICA mezcla dos formas distintas de "sin dato" (nulo real y el literal `"0.0"`) en vez de una
sola marca explícita — exactamente el problema que la regla `SIN_DATO` del proyecto (CLAUDE.md
§4) existe para atrapar. **Esto es información nueva para `US-105` (interpolación IDW de D6, ya
implementada por Diana):** si el código de IDW no filtra estas ~24 estaciones antes de
interpolar, va a jalar coordenadas `(0,0)` (frente a la costa de África) hacia el cálculo. Vale la
pena confirmarlo con Diana.

`sinaica_observaciones` pasa las 12 expectativas sin fallos en la muestra probada (45 registros,
3 estaciones, 3 parámetros).

## Cómo reproducir

```bash
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt

$env:PYTHONPATH = "src"
.venv\Scripts\python.exe -c "from ingesta.extractor_sinaica import extraer_sinaica; extraer_sinaica()"
.venv\Scripts\python.exe -m src.ingesta.validacion_sinaica
# Data Docs en great_expectations/uncommitted/data_docs/local_site/index.html
```

## Pendientes

- Conectar la suite a `dags/dag_horario.py` (o a un DAG de calidad aparte) para que corra en cada
  extracción, no solo manualmente.
- Suite equivalente para DS-04 (SESNSP) — bloqueada hasta que se resuelva el acceso (ver PR #31).
- Publicar Data Docs en CI (hoy son solo locales, `great_expectations/uncommitted/` no se versiona).
