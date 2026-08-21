---
id: DEVLOG-2026-08-21-LUIS-US123B
title: "DevLog — US-123b Great Expectations para DS-05 (SINAICA) + recordatorio a Diana"
author: "Luis Enrique García Vázquez"
session_date: "2026-08-21"
ai_tool: "Claude Code (Sonnet 5)"
traces_up: ["US-123b", "US-121b", "REQ-001"]
affected_ids: ["US-123b", "TEST-010", "REQ-001", "DS-05", "DS-04"]
tags: [devlog, ai-assisted, sprint-3, great-expectations, sinaica, data-quality]
---

# DevLog — US-123b: Great Expectations para DS-05 (SINAICA)

## Contexto

Volví a la sesión sin respuesta nueva de Diana en el PR #31 (3 días desde mi respuesta del
18-ago). Le mandé un recordatorio breve y arranqué `US-123b` (Great Expectations) para DS-05, que
ya no tiene bloqueos. De paso encontré (y corregí a nivel de reporte, no de archivo, porque no son
míos) dos imprecisiones en `Execution_Status.md` y `Risk_Register.md` del PM: marcaban `US-122b`
como "done" y `US-123b` como "in progress" citando el PR #47, que en realidad nunca tocó Great
Expectations.

## Qué se pidió a la IA

> "Publica un recordatorio breve a Diana en el PR #31 sobre DS-04 y comencemos a trabajar en la
> US-123b configurando Great Expectations para los datos de DS-05 (SINAICA)."

## Qué hizo la IA (y qué se revisó)

### Recordatorio a Diana (PR #31)

Publicó un comentario corto (no repite todo el contexto anterior, solo recuerda que sigue
pendiente y que el sprint cierra el domingo). **Revisión mía:** confirmé que el tono fuera breve y
no repetitivo antes de autorizarlo.

### Suite de Great Expectations (`src/ingesta/validacion_sinaica.py`)

`requirements.txt` fija `great-expectations>=0.18` sin techo, así que la instalación real resolvió
la **1.21.0** (API declarativa moderna: `ExpectationSuite` + `gx.expectations.*`, no la API
`validator` de las guías de 0.1x). La IA exploró la API real contra datos reales antes de escribir
el script final (no copió una guía desactualizada):

- Confirmó que `gx.get_context(mode="file", project_root_dir=".")` crea una carpeta `gx/` nueva
  por defecto en GE 1.x — **no** la `great_expectations/` que ya existe en el repo (con
  `.gitignore` propio que ya excluye `uncommitted/`). Corrigió a `context_root_dir="great_expectations"`
  para no duplicar convención.
- Probó en vivo el flujo completo (datasource pandas → asset → batch definition → suite →
  `batch.validate()` → `context.build_data_docs()`) contra los Parquet reales que generó
  `extractor_sinaica.py` antes de darlo por bueno.
- Diseñó las expectativas para que sean **idempotentes** (`add_or_update_pandas`,
  `add_or_update` de suites, y `get_asset`/`get_batch_definition` con fallback a `add_*` si no
  existen) — se puede correr el script muchas veces sin acumular datasources/suites duplicados.

**Revisión mía:** revisé los rangos físicos por contaminante (O3/CO/NO2/SO2/PM2.5/PM10) contra lo
documentado en `DS-05_SINAICA_Calidad_Aire.md` antes de aceptarlos, y decidí explícitamente **no**
usar `mostly=` para esconder el hallazgo de georreferencia (ver abajo) — quería que la suite
reportara el problema real, no que "pasara" artificialmente.

## Hallazgo real (no una falla de la suite)

Al correr la suite contra datos reales (no un fixture sintético), `sinaica_estaciones` falla de
forma reproducible: **24 de 384 estaciones (≈6.3%)** traen `latitud`/`longitud` inutilizables — 3
con nulo genuino y 21 con el placeholder literal `"0.0"` que usa SINAICA en vez de un `SIN_DATO`
explícito. `sinaica_observaciones` pasa las 12 expectativas sin fallos en la muestra probada.

Esto es relevante para `US-105` (interpolación IDW de D6, ya construida por Diana el 19-ago): si
su código no filtra estas ~24 estaciones antes de interpolar, va a jalar coordenadas `(0,0)`
(frente a la costa de África) hacia el cálculo de escuelas cercanas. Lo dejé documentado en
`DS-05_SINAICA_Calidad_Aire.md` sección 10 y en `TEST-010`; no le avisé todavía a Diana por otro
canal — queda como pendiente de esta sesión.

## Decisiones tomadas (no delegadas a la IA)

1. Acepté que Bronze se valide **sin tipar** `latitud`/`longitud`/`municipioId` (siguen como texto
   en esta suite) porque el tipado real ya vive en el modelo Silver de Deni — decidí no duplicar
   esa responsabilidad en Bronze.
2. Decidí dejar que la expectativa de georreferencia **falle de verdad** en vez de suavizarla con
   `mostly=`, porque el objetivo de la historia es encontrar problemas reales, no maquillar la
   suite en verde.
3. Asigné el ID `TEST-010` después de verificar en `06_Quality_Testing/Automated/_index.md` que
   `TEST-008` y `TEST-009` ya estaban tomados por otras historias (no asumí el siguiente número sin
   revisar).

## Archivos modificados

- `src/ingesta/validacion_sinaica.py` — suite real de Great Expectations (nuevo).
- `06_Quality_Testing/Automated/Great_Expectations_DS05_Sinaica.md` — `TEST-010` (nuevo).
- `06_Quality_Testing/Automated/_index.md` — registro de `TEST-010`.
- `14_Data_Sources/DS-05_SINAICA_Calidad_Aire.md` — nuevo riesgo (georreferencia).
- `12_Roadmap_Sprints/Sprints/1-luis-enrique-garcia-vazquez.md` — tabla de seguimiento.
- `02_Requirements/Traceability_Matrix.md` — fila `REQ-001`, columnas Test y DevLog.
- `_DevLog/2026-08-21-luis-garcia-us123b-great-expectations-ds05.md` (este archivo).
- `_DevLog/_index.md` — nueva fila.

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] No se suben datos reales pesados (Parquet de prueba y `great_expectations/uncommitted/`
  quedan fuera de git)
- [x] `ruff check` limpio, `py_compile` limpio
- [x] DevLog enlaza a los IDs afectados (`US-123b`, `TEST-010`, `REQ-001`, `DS-05`, `DS-04`)

## Bloqueantes

- DS-04 sigue sin respuesta de Diana (recordatorio enviado hoy en PR #31).
- La suite de DS-04 no puede escribirse hasta que exista un extractor real que produzca Bronze
  para esa fuente.

## Próximos pasos

- Avisar a Diana del hallazgo de georreferencia (impacta su IDW de `US-105`).
- Conectar `validacion_sinaica.py` a un DAG/CI en vez de correrlo manualmente.
- Cuando DS-04 se destrabe: extractor real + suite GE para SESNSP, cerrando `US-122b`/`US-123b`
  por completo.
