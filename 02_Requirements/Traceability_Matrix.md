---
id: DOC-TRACE-MATRIX
title: "Matriz de Trazabilidad — FARO"
owner: "Edgar Edmundo Coronel Navarrete"
status: in_review
version: "1.0"
source_of_truth: true
traces_up: ["02_Requirements/Requirements_Detailed", "02_Requirements/User_Stories"]
last_reviewed: "2026-08-28"
tags: [requirements, traceability, matrix]
---

# ⭐ Matriz de Trazabilidad — FARO

> **Vista única del estado del proyecto** (historia **US-004**, PM). Cierra el ciclo:
> REQ → AC → US → Fuentes → Modelos → Arquitectura → Test → DevLog → Release.
> → [[02_Requirements/_index]] · [[02_Requirements/Requirements_Detailed]] · [[02_Requirements/User_Stories]]

## Cómo se mantiene

- **El PM la actualiza en cada standup** (semanas 1–3 los jueves; semanas 4–6 L-Mi-V).
- Las columnas **Test**, **DevLog** y **Release** nacen **vacías (⬜)** y se llenan conforme avanza la
  ejecución.
- **Regla dura:** una fila con **Test o DevLog en ⬜ NO está Done.** La planeación puede estar completa,
  pero el REQ solo pasa a 🟢 cuando tiene prueba verde, DevLog y quedó en un release.
- Nuevo `REQ-###` → fila nueva. Cambios de alcance → PR con aviso al dueño del REQ.

---

## Matriz

| REQ | Criterios AC | User Stories | Fuentes DS | Modelos ML | Arquitectura | Test | DevLog | Release | Estado |
|---|---|---|---|---|---|---|---|---|---|
| [[02_Requirements/Requirements_Detailed\|REQ-001]] · Data Engineering | AC-001.1…AC-001.7 (7) | [[02_Requirements/User_Stories\|18 US]]: US-101–106, US-111–114, US-121a/b–124a/b | [[14_Data_Sources/_index\|DS-01…DS-08]] (las 8) | — (produce `features_escuela`) | [[03_Architecture/Data_Model\|Data_Model]] | ⬜ · US-111: `dbt compile` ✅ · US-103/US-104: estrella Gold completa (dim_tiempo, dim_driver, dim_escuela, dim_municipio, fact_escuela_ciclo + features_escuela), 88 data tests propios en PASS · US-105: interpolación IDW de D6 (aire) real hacia cada escuela (ADR-006), `dbt run`+`dbt test` 53/53 PASS, D5 (agua) sigue en SIN_DATO — bloqueado por DS-06 · 9 sources · US-112: estrella Gold materializada + tests nativos unique/not_null/relationships/accepted_values ✅ · BUG-009 `fixed`: 11 vars de dbt con default permanente (DEC-011), `dbt parse` verde como test de regresión en el job `dbt-contract` de `ci.yml` · US-106: linaje completo fuente→dashboard documentado (`Data_Lineage_US106.md`, **draft**, freeze objetivo 6-sep-2026) · US-122b/US-123b DS-04: fuente alterna a SharePoint encontrada y verificada (`repodatos.atdt.gob.mx`), extractor real agrega subtipo/modalidad, 12 553 440 filas en Bronze · [[06_Quality_Testing/Automated/Great_Expectations_DS04_Sesnsp\|TEST-011 ✅]] (14/15, hallazgo real: 1 fila con conteo negativo) · US-124b: 28 pruebas `pytest` nuevas para extractores/suites GE de DS-04/DS-05, corren offline sin red (326 pruebas totales del repo en verde) · US-113: 9 cubos Gold / 10 dashboards · cobertura explícita · DEC-010 compatible · dbt/contratos ✅ · DS-01: 4 ciclos reales cargados (2021-2022…2024-2025) vía cargador real nuevo (`cargar_bronze_formato911_real.py`), estrella + 8 cubos Gold validados contra Postgres real, 149/149 tests dbt — evidencia del gate que US-113 tenía pendiente de Diana Alvarez (TL C1) | [[_DevLog/2026-08-07-diana-alvarez-data-model-us101\|2026-08-07]] · [[_DevLog/2026-08-14-luis-garcia-us121b-prueba-descarga\|2026-08-14]] · [[_DevLog/2026-08-16-deni-garrido-us111-bronze-silver-cierre|2026-08-16 · US-111]] · [[_DevLog/2026-08-18-luis-garcia-us122b-extractor-sinaica\|2026-08-18 · US-122b]] · [[_DevLog/2026-08-18-diana-alvarez-us103-merge-silver-us111\|2026-08-18 · US-103]] · [[_DevLog/2026-08-19-diana-alvarez-us104-features-escuela\|2026-08-19 · US-104]] · [[_DevLog/2026-08-19-diana-alvarez-us103-gold-estrella\|2026-08-19 · US-103]] · [[_DevLog/2026-08-19-diana-alvarez-us105-idw-calidad-aire\|2026-08-19 · US-105]] · [[_DevLog/2026-08-22-deni-garrido-us112-silver-gold\|2026-08-22 · US-112]] [[_DevLog/2026-08-23-diana-alvarez-us106-linaje-freeze\|2026-08-23 · US-106]] · [[_DevLog/2026-08-23-edgar-bug009-defaults-dbt\|2026-08-23 · BUG-009]] · [[_DevLog/2026-08-24-luis-garcia-us122b-us123b-sesnsp-fuente-alterna\|2026-08-24 · US-122b/US-123b]] · [[_DevLog/2026-08-24-luis-garcia-us124b-fixtures-ds04-ds05\|2026-08-24 · US-124b]] · [[_DevLog/2026-08-23-deni-garrido-us113-cierre-dec010-pipeline\|2026-08-23 · US-113 cierre]] · [[_DevLog/2026-08-28-diana-alvarez-formato911-real-validacion-us113\|2026-08-28 · DS-01/US-113]] | US-111 · PR #37 · US-103/US-104 · US-105 · US-112 · PR #72 · US-106 · BUG-009/DEC-011 · US-122b/US-123b · US-124b · US-113 · PR #81 (Draft) · DS-01 · PR #105 (Open) | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-002]] · Frontend BI | AC-002.1…AC-002.6 (6) | [[02_Requirements/User_Stories\|19 US]]: US-201–207, US-211a/b, US-212, US-213, US-214a/b, US-215a/b, US-221–224 | — (vía Gold) | ML-01/02/03 (consumidos en DB-06/09) | [[03_Architecture/Data_Model\|Data_Model]] (cubos) · [[03_Architecture/Frontend_Architecture\|FARO Web]] · [[04_UX_Design/Screen_Specs\|Screen_Specs]] (US-201) · [[04_UX_Design/Cube_Specs_DB03_DB04\|Cube_Specs DB-03/04]] (US-211a) · [[04_UX_Design/Superset_Setup_US202\|Superset Setup]] (US-202) · [[04_UX_Design/Cube_Specs_DB05_DB08\|Cube_Specs DB-05/08]] (US-211b) · [[04_UX_Design/US221_KPIs_Base|US221_KPIs_Base]] (US-221) · [[04_UX_Design/Cube_Specs_DB07\|Cube_Specs DB-07]] (US-222) | `test_semantic_db03_db04` ✅ (US-211a, 27 casos: SIN_DATO≠0, grano, repunteo a cubos US-205) · `test_semantic_db01_db02` ✅ (US-203, 47 casos: filtros AC-002.2 en todos los datasets, componentes aditivos DEC-008, SIN_DATO≠0) · E2E Playwright ✅ (16/16 charts con datos; filtros ciclo/entidad/nivel aplican a todo el tablero; nombres oficiales INEGI de municipio vía `gold.geo_municipio`) · `test_semantic_db05_db08` ✅ (US-211b/US-205/US-213, 53 casos: repunteo a gold.cubo_driver/cubo_pivot, re-escala DB-05 a KPI-07, dashboards DB-05/08 alineados a los nombres reescalados, SIN_DATO≠0, formato largo) · `test_semantic_repunteo_cubos` ✅ (US-205, 34 casos: los 15 datasets virtuales —13 US-205 + 2 DB-07/US-222— no leen gold.fact_*, fuentes en allowlist C1, toda expresión de métrica usa solo columnas expuestas por el dataset) · **BUG-011** ✅ fixed (`sync_semantic_layer.py` lee con `encoding="utf-8"` explícito — ya no requiere `PYTHONUTF8=1` en Windows; `ensure_chart()` compara `datasource_id` y ya no repunta charts homónimos de otro tablero) · `test_kpis_us221` ✅ (US-221, 6 casos: KPI-01/02/03/04/08 vs fixtures, SIN_DATO≠0, umbral 0.6, SCOPE_ENTIDADES) · `test_semantic_db06_db09` ✅ (US-204, 48 casos: grano escuela DEC-010, SIN_DATO≠0, ML por LEFT JOIN con llave completa + modelo='ML-01', umbral 0.6, componentes aditivos, repunteo a cubos US-205) · `test_db07_calidad_cobertura` ✅ (US-222, 7 casos: KPI-05/06 SUM/SUM, SIN_DATO≠0, grano sin duplicados en mapa, geometría, coherencia agregado vs detalle) · `test_semantic_db05_db08` ampliado ✅ (US-213, 51 casos totales: +21 nuevas — layout de tabs vía `_layout_tabs()`, dashboard db05 declarativo de 6 tabs D1-D6 con adhoc_filters por driver y nota MARKDOWN de fuente, dashboard db08 con guarda de doble conteo del pivote) · DB-05 (36 charts, 6 tabs) y DB-08 (5 charts, pivote libre) sincronizados y validados contra Gold real (dbt, no mock) ✅ · hallazgo de `gold.dim_driver` (Célula 1): condición de carrera en `dbt run` corregida como **BUG-021**; esquema desincronizado corregido por Diana como **BUG-022** (fix en `main`; fila del registro restaurada en este PR) | [[_DevLog/2026-08-07-manuel-serrania-us-201\|2026-08-07]] · US-201 · [[_DevLog/2026-08-13-manuel-serrania-screenspecs-cubos\|2026-08-13]] · [[_DevLog/2026-08-14-marina-garcia-cubos-db03-db04\|2026-08-14]] · US-211a · [[_DevLog/2026-08-15-manuel-serrania-kpis-db03-ratificacion-join\|2026-08-15]] · [[_DevLog/2026-08-16-manuel-serrania-us202-superset\|2026-08-16]] · US-202 · [[_DevLog/2026-08-21-manuel-serrania-us203-tableros-db01-db02\|2026-08-21]] · US-203 · [[_DevLog/2026-08-21-marina-garcia-cierre-us211a\|2026-08-21]] · US-211a ✅ cerrada · [[_DevLog/2026-08-24-marina-garcia-us212-db03-db04\|2026-08-24]] · US-212 (DB-03/DB-04 sobre mock; pendiente validar con Gold real) · [[_DevLog/2026-08-27-marina-garcia-pipeline-local-us212\|2026-08-27]] · US-212 revalidada sobre Gold real (24/24 charts; bloques ML pendientes por BUG-013) · [[_DevLog/2026-08-22-handoff-us203-tableros-superset\|2026-08-22]] · US-203 depuración E2E · [[_DevLog/2026-08-22-handoff-us203-verificacion-e2e-playwright\|2026-08-22]] · verificación E2E + diagnóstico · [[_DevLog/2026-08-22-manuel-serrania-us203-filtros-nombres-reales\|2026-08-22]] · US-203 filtros AC-002.2 completos + nombres reales · [[_DevLog/2026-08-22-monserrat-miranda-us211b-cubos-db05-db08\|2026-08-22]] · US-211b · [[_DevLog/2026-08-26-oscar-quiroz-us221-kpis-base\|2026-08-26]] · US-221 · [[_DevLog/2026-08-27-manuel-serrania-us204-db06-db09\|2026-08-27]] · US-204 (DB-06/DB-09, validación en vivo 15/15 OK + AC-002.2; hallazgo preexistente `dim_driver` que bloquea DB-05/08 escalado a C1) · [[_DevLog/2026-08-28-monserrat-miranda-us213-db05-db08-dashboards\|2026-08-28]] · US-213 (DB-05 6 tabs + DB-08 explorador, tabs/markdown en `sync_semantic_layer.py` aprobados por Manuel, validado contra Gold real; BUG-021/BUG-022 con Diana — threads ya corregido, fila de BUG-022 restaurada en Bug_Register.md) | ⬜ | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-003]] · Modelos ML | AC-003.1…AC-003.6 (6) | [[02_Requirements/User_Stories\|10 US]]: US-301–303, US-311–313, US-321, US-322, US-324, US-325 (+apoyo US-412/415/416) | DS-01…08 (vía `features_escuela`) | [[15_ML_Models/_index\|ML-01, ML-02, ML-03]] | [[03_Architecture/Data_Model\|Data_Model]] · [[03_Architecture/API_Specification\|API_Spec]] | [[06_Quality_Testing/Automated/Particion_Temporal_ML01\|TEST-003 ✅]] (US-311, AC-003.3) · [[15_ML_Models/Indice_Riesgo_ML01\|TEST-004 ✅]] (US-311) · [[15_ML_Models/ML01_Entrenamiento\|TEST-005 ✅]] (ML-01 entrenado) · [[15_ML_Models/Publicacion_Gold\|TEST-006 ✅]] (US-313) · [[06_Quality_Testing/Automated/Evaluacion_Modelos\|TEST-007 ✅]] (US-312) | [[_DevLog/2026-08-08-hector-morales-fixture-particion-temporal\|2026-08-08]] · [[_DevLog/2026-08-11-hector-morales-indice-riesgo-ml01\|2026-08-11]] · [[_DevLog/2026-08-13-hector-morales-entrenamiento-ml01\|2026-08-13]] · [[_DevLog/2026-08-14-hector-morales-publicacion-gold\|2026-08-14]] · [[_DevLog/2026-08-18-hector-morales-evaluacion-us312\|2026-08-18]] · [[_DevLog/2026-08-23-diana-alvarez-dec010-grano-dual-predicciones\|2026-08-23 · DEC-010]] · [[_DevLog/2026-08-27-carlos-mayorga-us324\|2026-08-27 · US-324]] · [[_DevLog/2026-08-29-diana-alvarez-us325-cve-mun-features-escuela\|2026-08-29 · US-325]] | DEC-010 | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-004]] · Backend/API/Auth | AC-004.1…AC-004.6 (6) | [[02_Requirements/User_Stories\|14 US]]: US-401–405, US-411–416, US-421–423 | — | ML-01/02/03 (expuestos vía API) | [[03_Architecture/API_Specification\|API_Spec]] · [[03_Architecture/Data_Model\|Data_Model]] · [[03_Architecture/ADRs/ADR-004-autenticacion-oauth2-jwt\|ADR-004]] (auth) | `test_api_contract` ✅ (US-401/US-411/US-412/US-416, 27) · `test_auth_jwt` ✅ (US-402, 15) · `test_schemas_ml` ✅ (US-415, 11) · `test_cache_predicciones` ✅ (US-416, 8) | [[_DevLog/2026-08-11-christian-ruiz-us401-contrato-api\|2026-08-11]] · US-401 · [[_DevLog/2026-08-17-christian-ruiz-us402-oauth-jwt\|2026-08-17]] · US-402 · [[_DevLog/2026-08-20-karla-monter-us411-endpoints-gold\|2026-08-20]] · US-411 · [[_DevLog/2026-08-26-juan-macias-us415-contrato-modelos\|2026-08-26]] · US-415 · [[_DevLog/2026-08-26-juan-macias-us412-repositorio-modelos-bug010\|2026-08-26]] · US-412/BUG-010 · [[_DevLog/2026-08-27-juan-macias-us416-cache-timeouts\|2026-08-27]] · US-416 | PR #95 (US-412/415) | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-005]] · Deploy GCP | AC-005.1…AC-005.5 (5) | [[02_Requirements/User_Stories\|13 US]]: US-501, US-502, US-504, US-505, US-522a/b/c, US-524a/b/c, US-525a/b/c | — | — | [[08_CICD_DevOps/Cloud_Run_Deploy\|Cloud Run Deploy ✅]] | ⬜ | [[_DevLog/2026-08-09-luis-tellez-us501-cloud-run-deploy\|2026-08-09]] · [[_DevLog/2026-08-15-luis-tellez-us502-docker-compose-ml-services\|2026-08-15]] · US-502 · [[_DevLog/2026-08-25-alejandro-velazquez-us522a\|2026-08-25]] · [[_DevLog/2026-08-29-luis-tellez-us502-compose-sin-container-name\|2026-08-29 · US-502]] · [[_DevLog/2026-08-29-luis-tellez-us504-provision-gcp-fase1\|2026-08-29 · US-504]] · [[_DevLog/2026-08-29-luis-tellez-us505-fase2-gold-cloudsql-redeploy\|2026-08-29 · US-505 · BUG-020 prod ✅]] · [[_DevLog/2026-08-29-luis-tellez-security-docs-cis-usids-genkeys\|2026-08-29 · docs seguridad CIS/US IDs]] | ⬜ | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-006]] · Agente | AC-006.1…AC-006.4 (4) | [[02_Requirements/User_Stories\|4 US]]: US-304a, US-304b, US-305, US-323 | — (vía Gold) | — (RAG sobre Gold) | [[03_Architecture/API_Specification\|API_Spec]] (`/agente`) · [[03_Architecture/Data_Model\|Data_Model]] | `test_agente_recuperacion` ✅ (US-304b, 3) · `test_agente_evaluacion` ✅ (US-323, 2) | [[_DevLog/2026-08-26-andres-gonzalez-plan-registry-guardrails\|2026-08-26]] · [[_DevLog/2026-08-26-andres-gonzalez-us305-apptest\|2026-08-26]] · [[_DevLog/2026-08-27-andres-gonzalez-us305-jwt-client\|2026-08-27]] · [[_DevLog/2026-08-27-carlos-mayorga-us304b-us323\|2026-08-27]] | ⬜ | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-007]] · Equipo/Git/Docs | AC-007.1…AC-007.5 (5) | [[02_Requirements/User_Stories\|13 US]]: US-001–006, US-503, US-521a/b/c, US-523a/b/c | — | — | [[AGENTS\|AGENTS.md]] · [[_Meta/Vault_Rules\|vault]] · [[13_Reports/PM_Dashboard_Spec\|Tablero PM]] | [[06_Quality_Testing/Automated/_index\|TEST-002 ✅]] | [[_DevLog/2026-08-05-edgar-tablero-control-pm-v2\|2026-08-05]] · [[_DevLog/2026-08-06-edgar-directorio-github-codeowners\|2026-08-06]] · [[_DevLog/2026-08-12-alejandro-velazquez-mendoza\|2026-08-12]] · [[_DevLog/2026-08-15-luis-tellez-us503-ci-pipeline\|2026-08-15]] · US-503 · [[_DevLog/2026-08-25-alejandro-velazquez-us522a\|2026-08-25]] | ⬜ | 🟡 En progreso |

## Evidencia incremental — 2026-08-26

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-003` | `US-302`, `US-303` | ML-02/MLflow/Gold/guardarraíles: 71 pruebas enfocadas ✅ · Registry local MLflow 3.15.1: `ML02_DriverClasificador` v1 ✅ | [[_DevLog/2026-08-26-andres-gonzalez-plan-registry-guardrails]] | 🟡 En progreso |
| `REQ-006` | `US-304a`, `US-305` | Guardarraíles y prompt ✅ · cliente HTTP: 8 pruebas ✅ · flujo Streamlit persistente: historial, SQL y rechazo ✅ · Ruff ✅ | [[_DevLog/2026-08-26-andres-gonzalez-plan-registry-guardrails]] · [[_DevLog/2026-08-26-andres-gonzalez-us305-apptest]] | 🟡 En progreso |

## Evidencia incremental — 2026-08-27

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-006` | `US-305` | Cliente y widget preparados para propagar `Authorization: Bearer` desde la sesión: 9 pruebas enfocadas ✅ · Ruff ✅ | [[_DevLog/2026-08-27-andres-gonzalez-us305-jwt-client]] | 🟡 En progreso |
| `REQ-003` | `US-311`, `US-313` | BUG-015: la cobertura de drivers se evalúa **por ventana** de entrenamiento, no global — un driver con datos sólo en el ciclo reciente (D6, IDW de US-105) quedaba vacío en el tramo de entrenamiento y rompía el binning ✅ · `--ventanas` se calcula desde los ciclos disponibles ✅ · 3 pruebas de regresión nuevas · suite 481 ✅ · Ruff y `vault_lint` ✅ | [[_DevLog/2026-08-27-hector-morales-bug015-segunda-vuelta]] | 🟡 En progreso |
| `REQ-003` | `US-311`, `US-313` | Primera corrida real de ML-01 sobre `gold.features_escuela`: 45 249 predicciones ✅ · filas sin ningún driver apartadas de ML-02 conservando su predicción (BUG-016) ✅ · guarda de escala que detiene un `indice_riesgo` saturado (BUG-017) ✅ · BUG-018 reproducido en ML-02 y documentado ⬜ · 11 pruebas nuevas · suite 492 ✅ | [[_DevLog/2026-08-27-hector-morales-bug016-018-gold-real]] | 🟡 En progreso |
| `REQ-003` | `US-104`, `US-311`, `US-313` | Unidad de `target_variacion_matricula` confirmada como diferencia absoluta de alumnos · **BUG-019**: la misma columna se produce en dos unidades según el grano y ambas llegan a `gold.predicciones.valor` ⬜ · **ADR-007** propuesto con evidencia cuantificada (correlación 0.70 entre variación absoluta y tamaño de escuela) ⬜ · guarda de escala vigente · suite 497 ✅ | [[_DevLog/2026-08-28-hector-morales-adr007-unidad-target]] | 🟡 En progreso |
| `REQ-006` | `US-304b`, `US-323` | Capa RAG implementada e indexador ChromaDB creado ✅ · Set de evaluación de 20 preguntas con clasificación probado ✅ | [[_DevLog/2026-08-27-carlos-mayorga-us304b-us323]] | 🟡 En progreso |

## Evidencia incremental — 2026-08-27 · avance independiente C3

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-003` | `US-302`, `US-303` | Target ML-02 validado antes de entrenar: 13 pruebas ✅ · verificación y CLI del Registry: 14 pruebas ✅ | [[_DevLog/2026-08-27-andres-gonzalez-avance-independiente-c3]] | 🟡 En progreso |
| `REQ-006` | `US-304a`, `US-305` | Orquestación segura inyectable: 19 pruebas con guardarraíles ✅ · cliente JWT distingue 401/403: 11 pruebas y 1 omitida ✅ | [[_DevLog/2026-08-27-andres-gonzalez-avance-independiente-c3]] | 🟡 En progreso |

## Evidencia incremental — 2026-08-28

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-001` | `US-121a`, `US-122a`, `US-123a`, `US-124a` | DS-06 (CONAGUA) destrabado: endpoint POST real confirmado (`mapa.php`, 180 presas con volumen NAME/NAMO), reemplaza el placeholder `SOURCE_URL="PENDIENTE-CONFIRMAR"` en `extractor_conagua.py` · DS-08 (CONAPO) procesado desde archivo local (sin URL de descarga estable), clave municipal corregida a 5 dígitos en `extractor_conapo.py` · Great Expectations: `suite_ds06_conagua` 7/7 ✅ (180 filas) y `suite_ds08_conapo` 7/7 ✅ (252,450 filas) · Fixtures CI: `bronze_ds06_conagua_sample.csv` (180 filas) y `bronze_ds08_conapo_sample.csv` (500 filas) | [[_DevLog/2026-08-28-emilio-galnares-us121a-ds06-ds08]] | 🟡 En progreso |
| `REQ-003` | `US-302` | BUG-018 corregido: cobertura evaluada por ventana y predicción/SHAP alineados con `feature_names_in_` ✅ · ML-02 16 pruebas ✅ · Ruff ✅ | [[_DevLog/2026-08-28-andres-gonzalez-bug018-ml02-cobertura]] | 🟡 En progreso |
| `REQ-003` | `US-303` | Verificador del Registry rechaza versiones nulas o no numéricas con error accionable ✅ · suite enfocada 15 pruebas ✅ | [[_DevLog/2026-08-28-andres-gonzalez-us303-version-registry]] | 🟡 En progreso |

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-003` | `US-302` | `driver_dominante` real en `gold.features_escuela` (Célula 1): CTE argmax + desempate D1>D2>D3>D4>D5>D6 · 5 pruebas dbt nuevas ✅ · prueba de paridad SQL vs proxy Python ✅ · contrato y fixture actualizados · `dbt build --target dev` 173 pass · `pytest tests/ -q` 467 pass | [[_DevLog/2026-08-28-diana-alvarez-driver-dominante-us302]] | 🟡 En progreso |
| `REQ-006` | `US-304a`, `US-304b`, `US-305`, `US-323` | RAG endurecido e integrado con guardarraíles ✅ · indexación idempotente y observable ✅ · 20 casos recorren el flujo completo simulado ✅ · 32 pruebas enfocadas | [[_DevLog/2026-08-28-andres-gonzalez-integracion-rag-evaluacion]] | 🟡 En progreso |
| `REQ-006` | `US-304a`, `US-305` | BUG-024: `SELECT INTO` rechazado antes del ejecutor ✅ · sin coincidencias RAG diferenciado de caída operativa ✅ · 32 pruebas enfocadas · suite local 526 pass, 0 skips ✅ | [[_DevLog/2026-08-28-andres-gonzalez-bug024-rag-empty]] | 🟡 En progreso |

## Evidencia incremental — 2026-08-28 · higiene del vault y CI

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-007` | `US-503`, `US-004` | Guardia anti-mojibake en `vault_lint.py`, dentro del check requerido: 11 casos de validación ✅ · **BUG-014** cerrado con regresión versionada, `.github/scripts/probar_verificar_plantilla.sh` — 7 casos contra la plantilla real ✅ · `pytest tests/ -q` 467 ✅ | [[_DevLog/2026-08-28-edgar-mojibake-higiene-vault]] | 🟡 En progreso |

---
---

## Leyenda de estado

- 📋 **Planeado** — cobertura de planeación completa (AC, US y arquitectura definidos); **ejecución no
  iniciada** (Test/DevLog/Release en ⬜).
- 🟡 **En progreso** — hay commits/PRs abiertos pero aún sin Test o DevLog completo.
- 🟢 **Done** — Test verde + DevLog + quedó en un Release.
- 🔴 **No iniciado** · ⚫ **Archivado/deprecado**.
- ⚠️ marca un **hueco de planeación** en alguna columna (ver abajo).

---

## Estado del proyecto

| Métrica | Valor |
|---|---|
| REQ totales | 7 |
| REQ con **planeación completa** (AC + US + arquitectura) | **6 / 7** |
| REQ con hueco de planeación | **1 / 7** (REQ-005: falta `System_Design.md`) |
| REQ **pendientes de ejecución** (sin Release completo) | **7 / 7** |
| REQ con Test | 1 / 7 |
| REQ con DevLog | 1 / 7 |
| REQ **Done** | 0 / 7 |
| Historias mapeadas | 91 / 91 (cobertura 7/7 módulos) |

> **Lectura:** la **planeación** está prácticamente cerrada (6 de 7 REQ con cobertura completa); la
> **ejecución** arrancó en REQ-007, pero aún hay 0 REQ Done. El único hueco es la **arquitectura de despliegue de
> REQ-005**, que se resolverá al escribir `03_Architecture/System_Design.md`.

## Evidencia incremental — 2026-08-28 · etiqueta real y verificación E2E

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-003` | `US-302`, `US-313` | Filtro de ML-02 usa `driver_dominante` real como autoridad cuando existe: cierra el hueco de inferir cobertura por valor (BUG-016) ✅ · cadena ML-01 → filtro → ML-02 verificada con target real, F1 0.633 ✅ · 2 pruebas nuevas · suite 500 ✅ | [[_DevLog/2026-08-28-hector-morales-filtro-etiqueta-real]] | 🟡 En progreso |
| `REQ-004` | `US-401`, `US-411` | **BUG-020**: en la URL pública toda ruta con base de datos responde HTTP 500 (`/predicciones`, `/predicciones/batch`, `/escuelas`); `/health` responde 200 y nunca se devuelve 401, así que el fallo precede a la validación de auth ⬜ | [[_DevLog/2026-08-28-hector-morales-filtro-etiqueta-real]] | 🔴 Bloqueante |

## Evidencia incremental — 2026-08-28 · drivers en el artefacto publicado

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-003` | `US-311`, `US-312` | Drivers usados/excluidos publicados en `Evaluacion_Modelos.md` §5 y §5.1 y registrados en MLflow (`cobertura_drivers`, `drivers_sin_datos` por ventana) ✅ · **BUG-023**: el reporte no podía generarse con un driver excluido porque predecía con los 6 ✅ · §5 acota la tabla a la corrida que la generó y declara el estado real de D5 en Gold ✅ · registro MLflow con pruebas (doble inyectado, corre sin `mlflow` en CI) ✅ · 9 pruebas nuevas · suite 510 ✅ | [[_DevLog/2026-08-28-hector-morales-drivers-en-evaluacion]] | 🟡 En progreso |

## Evidencia incremental — 2026-08-28 · `cve_mun` en el contrato

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-003` | `US-325`, `US-311`, `US-313` | `agregar_a_municipio_nivel()` soporta `cve_mun` en el contrato sin colisión de sufijos y detecta el faltante con el indicador del merge ✅ · espejo `FeaturesEscuela` acepta el contrato antes y después del cambio (`extra=forbid`) ✅ · 4 pruebas nuevas verificadas contra regresión · suite 521 ✅ | [[_DevLog/2026-08-28-hector-morales-cve-mun-contrato]] | 🟡 En progreso |
## Evidencia incremental — 2026-08-28 · reconciliación integral de estatus

| REQ | Historias | Evidencia / decisión de estado | Próxima validación | Estado |
|---|---|---|---|---|
| `REQ-001` | `US-113`, `US-121a`–`US-124a` | US-113: PR #81 + PR #105, estrella y 8 cubos sobre 4 ciclos reales, 149/149 ✅ · BUG-021/PR #115 corrige orden dbt ✅ · PR #107 abierto para DS-06/DS-08 | Deni/Diana validan DB-10 o el PM aprueba excepción; Diana revisa PR #107 | 🟡 En revisión |
| `REQ-002` | `US-204`, `US-213`, `US-221` | PR #100 mergeado: DB-06/DB-09, 50 pruebas y 15/15 charts ✅ · PR #114 DB-05/08 abierto · PR #106 gráficos KPI abierto | Manuel valida datos ML reales y revisa #106/#114 | 🟡 En revisión |
| `REQ-003` | `US-302`, `US-313`, `US-323`, `US-324` | PR #113/#116/#117 estabilizan ML-02 ✅ · US-323 pasa a `done` con PR #108 y documento `approved` ✅ · US-324 en revisión por fichas PR #110 | Andrés valida Gold/Registry/SHAP; Héctor/Diana ejecutan publicación real; dueños de modelos revisan fichas | 🟡 En revisión |
| `REQ-004` | `US-403`, `US-411`, `US-412`, `US-415`, `US-416` | US-415 pasa a `done` con PR #95 ✅ (contrato Pydantic, sin superficie desplegada) · US-403 PR #97 y US-416 PR #101 pasan a revisión · **BUG-020 mantiene abiertas US-411 y US-412**: ambas entregan rutas HTTP que responden 500 en producción, y el criterio adoptado el 28-ago las trata igual · autenticación verificada viva (`/auth/login` 302, `/auth/me` 401), así que US-402 no queda tocada por BUG-020 | Christian ratifica seguridad/cache; Christian+Luis corrigen BUG-020; Karla valida endpoints | 🔴 Bloqueante |
| `REQ-005` | `US-522a/b/c`, `US-524a` | BUG-008 corregido por PR #99 ✅ · PR #87 Airflow y PR #102 monitoreo abiertos · Superset ya instala `psycopg2` en su venv · E2E Compose validado en LOCAL (rama `feat/luis-tellez-compose-sin-container-name`): 8 servicios verdes + Gold poblado, `container_name` eliminado para soportar worktrees; **BUG-020 curado en LOCAL** (prod sigue sin DB) · **US-504 Fase 1 GCP aprovisionada** (VPC privada + connector, Cloud SQL IP privada + backups/PITR, Secret Manager, SA de mínimo privilegio, audit logs) vía `provision-gcp-fase1.sh` → base para curar BUG-020 en prod (Fase 2) | C5 ejecuta E2E Compose, cierra BUG-004 y revisa #87/#102 | 🟡 En revisión |
| `REQ-006` | `US-304a`, `US-304b`, `US-305`, `US-323` | RAG y evaluación PR #108 ✅ · US-323 `done` · guardarraíles/widget/JWT mergeados · rama de integración RAG aún sin merge | Andrés/Carlos integran y ejecutan E2E; Christian entrega login y corrige BUG-020 | 🟡 En revisión |
| `REQ-007` | `US-004`, `US-521c`, `US-523a` | Reconciliación de 91 US ejecutada · US-523a pasa a `done` por PR #93/documento `approved` ✅ · US-521c conserva DevLog no filed | Edward regulariza DevLog; Edgar cierra acuerdos del reporte y regenera tablero | 🟡 En revisión |

## Evidencia incremental — 2026-08-28 · revisión de `main` y cobertura de fixtures (C2)

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-001` · `REQ-003` | `US-104`, `US-113`, `US-313` | **BUG-026** resuelto por **PR #129** (Diana Alvarez) ✅ · causa precisada por ella: `silver.matricula` nunca lee de `bronze.formato911_historico`, así que el hueco es aritmético en la tabla que sí está en el linaje — `con_target` sacrifica el primer ciclo, luego hacen falta 4 crudos para los 3 que exige `ventanas_posibles()` · **verificado corriéndolo**: `features_escuela` 1→3 ciclos, 60/60 CCT cruzan el catálogo, `--desde-gold` entrena ML-01 (MAE 12.2252) y se detiene en la guarda de BUG-017, no por falta de ciclos · generador reproducible (MD5) y carga idempotente | [[_DevLog/2026-08-29-marina-garcia-correcciones-y-revision-pr129]] | ✅ Desbloquea `US-212` |
| `REQ-003` | `US-311`, `US-313` | **BUG-013** replanteado a `parcial`: mitad C3 ✅ (`--desde-gold`, Héctor) y mitad C1 ✅ con datos reales (4 ciclos, Diana, 149/149); lo que queda es reproducibilidad y pasa a BUG-026 · registrado además que el error de sklearn abierto en el DevLog de Diana **ya es BUG-015** ⚠️ **corregido el 29-ago**: el fix no es `4f22bd8` (primer intento, cobertura global, no sirvió) sino **`f906a7d`** (cobertura por ventana) — `d6_aire` tenía datos globalmente pero estaba vacío en el tramo de entrenamiento; cadena verificada por Héctor sobre `main` con target real, F1 0.633 y 78/80 predicciones con recomendación ✅ | [[_DevLog/2026-08-28-marina-garcia-revision-main-bugs]] | 🟡 En progreso |
| `REQ-002` | `US-212`, `US-221` | `test_semantic_db03_db04` ✅ 29/29 sobre `main` de hoy · ningún archivo canónico de DB-03/DB-04 tocado en 123 commits · **cero colisiones de nombre** entre US-221 y DB-03/DB-04 · **BUG-027** → **superseded** por decisión de convención de Manuel Serranía (follow-up de US-221): se borran los `kpi_*.sql` y las tarjetas se remapean a los datasets canónicos, así que corregir los `sql_ref` sería trabajo sobre archivos que desaparecen. **Sobrevive el hallazgo de por qué CI no lo veía** —`test_kpis_us221` codifica `SQL_DIR` a mano y nunca lee `sql_ref`—: de ahí nace la guarda antiduplicación pedida a Oscar ✅ | [[_DevLog/2026-08-28-marina-garcia-revision-main-bugs]] | 🟡 En progreso |
| `REQ-002` · `REQ-003` | `US-212`, `US-104` | **BUG-017 / ADR-007** afectan directamente a DB-03/DB-04: con el target en alumnos absolutos y la sigmoide calibrada sobre fracción, `en_riesgo` (DEC-006, umbral 0.6) marcaría el 100 % de las escuelas y `pct_escuelas_en_riesgo` diría 100 % ⬜ · **incorporada como ratificadora** por PR #128 (Héctor Morales), junto con el costo asimétrico señalado ✅ · argumento que aporta Héctor y conviene registrar: **DEC-006 ya dice "`indice_riesgo` ≥ 0.6 ↔ pérdida de ~5 % de matrícula"**, y ese "~5 %" es una fracción — el umbral de DB-03/DB-04 ya presupone la unidad que ADR-007 propone, así que la alternativa A no es una opción nueva sino una reapertura de DEC-006 | [[_DevLog/2026-08-29-marina-garcia-correcciones-y-revision-pr129]] | ⬜ Mesa convocada por el PM |

## Evidencia incremental — 2026-08-29 · BUG-031, unidad de KPI-02 (C2)

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-002` | `US-211a`, `US-212` | **BUG-031**: KPI-02 pintaba −54.5 % contra un valor real de −0.19 %, verificado en Postgres (32 312 alumnos contra 32 374) ⬜ · origen en §4.4 del contrato, no en la implementación de US-113 · DB-03 corregido a razón de sumas y verificado corriéndolo ✅ · tarjeta de DB-04 retirada hasta que C1 exponga `suma_matricula_anterior` ⬜ · §4.4 reescrito con la regla de que un componente aditivo es una suma simple, nunca un producto ponderado ✅ | [[_DevLog/2026-08-29-marina-garcia-bug031-kpi02-unidad]] | 🟡 Parcial: falta el cubo (C1) |
| `REQ-002` | `US-212` | `test_una_metrica_de_porcentaje_no_multiplica_dos_medidas` ✅ — verificado reintroduciendo el defecto a propósito: falla con él y pasa sin él · cubre la **clase** de error, no la forma: la prueba anterior buscaba `* 100` y esta expresión nunca lo tuvo · 28 passed, ninguna prueba previa perdida (`--collect-only` comparado contra `main`) | [[_DevLog/2026-08-29-marina-garcia-bug031-kpi02-unidad]] | ✅ |

→ Seguimiento de junta: [[13_Reports/US_Validation_Followup_2026-08-28]]

## Evidencia incremental — 2026-08-29 · EDA y cobertura territorial ML-03

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-003` | `US-322`, `US-325` | EDA reproducible y auditoría de `SIN_DATO` por driver, entidad y municipio; `cve_mun` excluida del vector de clustering; validación de clave INEGI y cero inicial; 17 pruebas enfocadas ✅ · suite 544 ✅ · Ruff ✅ · Vault limpio ✅ | [[_DevLog/2026-08-29-estefany-hernandez-us322-us325-territorial]] | 🟡 En revisión; US-325 espera ejecución sobre Gold real |

## Evidencia incremental — 2026-08-29 · ML-03 clustering temporal

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-003` | `US-321` | Pipeline KMeans + StandardScaler; selección de `k` por Silhouette walk-forward; perfiles de negocio; target y llaves excluidos; política provisional `casos_completos` sin imputar cero · 6 pruebas enfocadas ✅ · suite 533 ✅ | [[_DevLog/2026-08-29-estefany-hernandez-us321-clustering]] | 🟡 En revisión; espera fallback ratificado y corrida real |
| `REQ-003` | `US-303`, `US-321` | ML-03 integrado al helper compartido y preparado para crear la versión canónica `ML03_ClusteringEscuelas` en Registry, sin promoción productiva · 7 pruebas enfocadas ✅ | [[_DevLog/2026-08-29-andres-gonzalez-us303-registro-ml03]] | 🟡 En progreso; E2E local completado, falta servidor compartido |
| `REQ-003` | `US-303` | E2E local MLflow 3.15.1: `ML01_RegresionMatricula`, `ML02_DriverClasificador` y `ML03_ClusteringEscuelas` registrados y verificados como versión 1 ✅ | [[_DevLog/2026-08-29-andres-gonzalez-e2e-registry-tres-modelos]] | 🟡 En progreso; falta servidor compartido y API C4 |

## Evidencia incremental — 2026-08-29 · ML-03 en la evaluación

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-003` | `US-312`, `US-321` | **AC-003.2 cubierto**: los tres modelos reportan métrica en `Evaluacion_Modelos.md` ✅ · ML-03 sin baseline fingido (`NaN`, no `0`) ✅ · §6 contrasta cada métrica contra su umbral y **afirma** si cumple — ML-03 no llega (0.1086 vs ≥0.30) ⚠️ · guarda de sincronía extendida a ML-03 ✅ · 6 pruebas nuevas · suite 595 ✅ | [[_DevLog/2026-08-29-hector-morales-ml03-en-evaluacion]] | 🟡 En progreso |

## Evidencia incremental — 2026-08-29 · ratificación de ADR-007

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-003` | `US-311`, `US-313` | **ADR-007 `accepted`** (29-ago) con la tabla de lo que falta para que surta efecto ✅ · `DOC-INDICE-RIESGO` reducido a una sola decisión abierta —el ancla `0.30`— tras cerrar el umbral (`DEC-006`) y la doble columna `valor`/`indice_riesgo` ✅ · **BUG-032** registrado: `Data_Model` §5.3 contradice a §4.5 ⬜ · suite 643 ✅ | [[_DevLog/2026-08-29-hector-morales-adr007-ratificado]] | 🟡 En progreso |

## Evidencia incremental — 2026-08-30 · cierre de BUG-020 y del stub del agente

| REQ | Historias | Evidencia de prueba | DevLog | Estado |
|---|---|---|---|---|
| `REQ-004` · `REQ-005` | `US-411`, `US-412`, `US-504`, `US-505` | **BUG-020 `fixed`** ✅ — PR #141 (VPC privada, Cloud SQL, Secret Manager) + PR #144 (Gold poblado y redeploy con conector VPC). **Verificado en vivo por el PM contra la URL pública**, no contra el reporte: `/escuelas`, `/municipios` y `/kpis` pasan de **500 a 200**; `/predicciones/{cct}` pasa de **500 a 404 estructurado** ✅ · se cumple el criterio de **DEC-012** para US-411 y US-412 · rectificado el alcance del bug: la autenticación siempre funcionó (`/auth/login` 302, `/auth/me` 401), **US-402 nunca estuvo tocada** ✅ | [[_DevLog/2026-08-29-luis-tellez-us505-fase2-gold-cloudsql-redeploy]] · [[_DevLog/2026-08-30-edgar-reconciliacion-post-adr007]] | 🟡 En progreso |
| `REQ-006` | `US-304a`, `US-304b`, `US-305` | **BUG-024 `fixed`** (PR #121): `SELECT … INTO` ya rebota en el validador de solo lectura ✅ · **BUG-025 `fixed`** (PR #142): `/agente/consulta` deja de ser stub y usa los guardarraíles reales — verificado en vivo, «cuál es la capital de Francia» devuelve `fuera_de_alcance: true` ✅ · **BUG-033 abierto**: ChromaDB no está desplegado, así que toda pregunta en alcance devuelve «contexto no disponible» ⬜ — bloquea el punto de rúbrica del agente | [[_DevLog/2026-08-30-edgar-reconciliacion-post-adr007]] | 🔴 Bloqueante |
| `REQ-007` | `US-004` | **DEC-012** asentada: una historia cuyo entregable es una ruta HTTP no cierra mientras esa ruta no responda en el despliegue ✅ · **DEC-013** asentada: un ID solo queda reservado cuando está en su registro canónico en `main` ✅ · corregida la fila `US-004` de [[12_Roadmap_Sprints/Execution_Status]], que tenía 8 columnas por un pipe sin escapar dentro de un wikilink y una celda de fecha duplicada ✅ · tablero PM regenerado | [[_DevLog/2026-08-30-edgar-reconciliacion-post-adr007]] | 🟡 En progreso |
