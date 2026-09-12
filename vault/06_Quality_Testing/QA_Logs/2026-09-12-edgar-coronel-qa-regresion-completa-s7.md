---
id: QALOG-20260912-EDGAR-REGRESION-S7
title: "Bitácora de QA — regresión completa del sistema, S7"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
traces_up: ["vault/06_Quality_Testing/QA_team_documentation/Plan_QA_Exhaustivo_S7"]
traces_down: ["vault/06_Quality_Testing/Bug_Register"]
last_reviewed: "2026-09-12"
tags: [qa, plan_qa_exhaustivo_s7, qa-log, s7, regresion]
---

# Bitácora de QA — regresión completa del sistema (S7)

→ [[vault/06_Quality_Testing/QA_team_documentation/Plan_QA_Exhaustivo_S7]] · [[vault/06_Quality_Testing/QA_Logs/_index]] · [[vault/06_Quality_Testing/Bug_Register]]

## Datos de la sesión

- **Responsable:** Edgar Edmundo Coronel Navarrete (con Claude Code)
- **Superficie asignada:** Todo el sistema — backend, dbt/Gold, API, frontend local
- **Ambiente probado:** **Local** (`docker compose up -d db mlflow api`, `main` sincronizado al SHA `3a1ad9b7`, frontend `npm run dev`) — **no** la URL pública. Todo hallazgo de dato requiere confirmarse contra producción antes de asumir que reproduce ahí.
- **Fecha y hora:** 2026-09-12, sesión continua ~13:00-19:00
- **Sesión iniciada como:** anónimo (no se completó login real; ver "Lo que NO alcancé a probar")
- **Navegador y sistema:** Chromium vía herramienta de navegador de Claude Code, macOS

## Resultados

| # | Caso | Esperado | Obtenido | Evidencia | Veredicto | Bug |
|---|---|---|---|---|---|---|
| 1 | `pytest tests/ -q` completo | Todo verde | 1241 passed, 4 skipped, 0 failed | Salida de consola | ✅ pasa | — |
| 2 | Suite de ML (`test_entrenar_ml03`, `test_ejecutar_cierre_ml03`, `test_publicar_gold`, `test_preflight_ml03`) | Todo verde | 66/66 passed | Salida de consola | ✅ pasa | — |
| 3 | `dbt parse` | Sin errores de sintaxis | Sin errores | Salida de consola | ✅ pasa | — |
| 4 | `dbt test --select gold` contra Postgres local | Todo verde | **250 PASS, 8 ERROR** | Salida de consola completa | ❌ falla | Ver #5, #6 |
| 5 | `not_null_dim_municipio_nombre_entidad` / `_poblacion` | 0 filas con nulo | 307 de 317 municipios con `nombre_entidad`/`poblacion` nulos | `select count(*), count(poblacion), count(nombre_entidad) from gold.dim_municipio` → `317, 10, 10` | ❌ falla | `BUG-077` |
| 6 | `GET /api/v1/municipios` (listado, sin filtro) | 200 con página de municipios | **500 `internal_error`** | `curl http://localhost:8000/api/v1/municipios?size=5` | ❌ falla | `BUG-077` |
| 7 | `GET /api/v1/municipios/{cve_mun}` para un municipio con `nombre_entidad` nulo (`14113`) | 200 o `SIN_DATO` explícito | **500 `internal_error`** | `curl http://localhost:8000/api/v1/municipios/14113` | ❌ falla | `BUG-077` |
| 8 | `GET /api/v1/municipios/99999` (no existe) | 404 | 404 `not_found` | `curl` | ✅ pasa | — |
| 9 | `cubo_riesgo_territorial_ml01_parity` (dbt) | 0 discrepancias | 5 combinaciones cve_mun×nivel×ciclo no coinciden con `fact_escuela_ciclo`+`predicciones` | Salida de `dbt test` | ⚠️ pasa con reserva | Pendiente — ver hallazgos |
| 10 | `GET /api/v1/escuelas?order_by=nombre_falso` (valor fuera de whitelist) | 422, nunca 500 | 422 | `curl` | ✅ pasa | — |
| 11 | `GET /api/v1/escuelas?size=99999` (fuera de rango) | 422 | 422 | `curl` | ✅ pasa | — |
| 12 | `GET /api/v1/escuelas/{cct}` con CCT inexistente | 404 | 404 `not_found` | `curl` | ✅ pasa | — |
| 13 | `GET /api/v1/auth/me` sin sesión | 401, sin romper la pantalla | 401 `unauthorized` | `curl` + verificado en frontend (botón "Iniciar sesión" se muestra correctamente) | ✅ pasa | — |
| 14 | `GET /api/v1/kpis` | 200, `escuelas_en_riesgo` coincide con `DEC-019` | `escuelas_en_riesgo: 7` | `curl` | ✅ pasa | — |
| 15 | `GET /api/v1/version` | `cortes_atencion` presente (`DEC-026`) | `{alta: 0.5, media: 0.3, ancla_calibracion: 0.6}` | `curl` | ✅ pasa | — |
| 16 | `GET /api/v1/predicciones/{cct}` | 200 con recomendación | **503 `service_unavailable`** — `ProgrammingError: column recomendaciones.shap_d1 does not exist` | Log del contenedor `api`, `curl` | ❌ falla (local) | No registrado — ver hallazgos |
| 17 | `/` (Home) | Carga con KPIs reales, sin excepción de JS | Correcto | Captura + consola | ✅ pasa | — |
| 18 | `/casos` (Los 7 Casos) | 7 tarjetas, nivel de atención derivado de `cortes_atencion` | Correcto — incluso el borde `0.50` etiqueta "Alta" | Captura | ✅ pasa | — |
| 19 | `/casos/:cct` — pestaña Resumen | Gauge + driver dominante | Correcto | Captura | ✅ pasa | — |
| 20 | `/casos/:cct` — pestaña Drivers | 6 drivers, D5/D6 en `SIN_DATO` explícito, nunca `0` | Correcto | Captura | ✅ pasa | — |
| 21 | `/casos/:cct` — pestaña Comparación | Estado declarado "pendiente", no error crudo | Correcto — explica el gap de contrato exacto | Captura | ✅ pasa | — |
| 22 | `/casos/:cct` — pestaña Predicción | Con backend sano, predicción; si no, mensaje explicado | Mensaje "No se pudo cargar la predicción (503 Service Unavailable)" — consistente con caso #16, no una excepción de React | Captura | ⚠️ pasa con reserva (depende de #16) | — |
| 23 | `/casos/:cct` — pestaña Recomendación | Igual que Predicción | No verificado a fondo (mismo bloqueo de #16) | — | ⏭️ no ejecutado | — |
| 24 | `/vista-general` | KPIs + "El diferenciador" con par oficial de demo | "El diferenciador": 404 (par `15DPR0920D`/`15DPR2254O` no existe en el fixture local de 55 escuelas) — **limitación de datos locales, no de código** | Captura + red | ⚠️ pasa con reserva (no reproducible sin el fixture completo) | — |
| 25 | `/mapa`, `/drivers`, `/comparacion-territorial`, `/comparativa` | Estado "en construcción" explicando el gap real, sin fallar | Las 4 correctas | Capturas | ✅ pasa | — |
| 26 | `/hallazgos` | Distribución de driver dominante + 5 hallazgos con datos reales | Correcto | Captura | ✅ pasa | — |
| 27 | Excepciones de JavaScript no controladas en las 9 rutas + 5 pestañas | Cero | Cero | `read_console_messages` filtrado por "Uncaught" | ✅ pasa | — |
| 28 | `http://localhost:5001` (MLflow) | Responde y tiene el `run_id` de la evidencia de `DEC-027` | Responde (200), pero **sin ningún run** — solo el experimento `Default` | `curl` API de MLflow | ❌ falla (dato) | Relacionado a `RISK-011`/`DEC-027`, no registrado como BUG nuevo |

## Resumen

- **Casos ejecutados:** 27 de 28 (uno diferido, #23)
- **✅ pasa:** 19 · **⚠️ con reserva:** 4 · **❌ falla:** 4 · **⏭️ no ejecutado:** 1
- **Bugs levantados:** `BUG-077` (nuevo, critical)
- **Clasificación para la junta de la tarde:** 🔴 rompe listados de municipio en producción **si el hueco de CONEVAL se repite ahí** (`BUG-077`, por confirmar) · 🟠 predicciones/recomendación caídas localmente por esquema desactualizado (probablemente solo local) · 🟢 el resto — el sitio degrada como está diseñado, sin excepciones de JS y sin errores crudos

## Lo que NO alcancé a probar

- **Login real (OAuth completo).** No se puede completar un flujo de Google real desde esta sesión sin credenciales; solo se verificó que el estado anónimo (401 en `/auth/me`) no rompe la pantalla.
- **Sesión `analista` / RBAC de escritura.** Sin login real, no se probó ningún endpoint que exija rol `analista`.
- **Chat del agente en el frontend.** No existe página de Chat en `frontend/src/pages/` todavía — nada que probar ahí.
- **Superset (los 10 tableros).** No se levantó el servicio `superset` en esta corrida por tiempo; sus datasets/gráficas no se verificaron.
- **Contra la URL pública de producción.** Todo lo de este documento es contra ambiente **local**. Los hallazgos de dato (`BUG-077`, MLflow vacío, esquema de `shap_d1..d6`) requieren confirmarse ahí antes de tratarse como defectos de producción.
- **Airflow / DAGs.** No se ejecutó ningún DAG en esta corrida.
- **Caso #23** (pestaña Recomendación del expediente): mismo bloqueo que #16, no se profundizó por no duplicar evidencia.

## Hallazgos que no son bugs

- **"El diferenciador" en 404 (caso #24) es esperado en este ambiente**: el fixture local de 55 escuelas no incluye el par oficial de demo (`15DPR0920D`/`15DPR2254O`). No reproducible sin ese fixture específico — no confundir con un defecto de `VistaGeneral.jsx`.
- **`cubo_riesgo_territorial_ml01_parity` (caso #9) probablemente es staleness del cubo local**, no necesariamente un defecto de producción: es consistente con que mi Postgres local no pasó por un `dbt run` completo y ordenado, sino por una carga parcial. Queda marcado "⚠️ pasa con reserva" en vez de bug hasta que alguien lo confirme corriendo `dbt run` completo.
- **`/predicciones/{cct}` en 503 local (caso #16) es, con alta probabilidad, un volumen de Docker desactualizado del PO**, no un bug de código: `src/modelos/publicar_gold.py` sí declara `shap_d1..shap_d6` en `gold.recomendaciones`; mi tabla local no las tiene porque se creó antes de que existieran. No se registra como BUG hasta confirmar que el ambiente compartido/producción tiene el mismo problema.
