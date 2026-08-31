---
id: DOC-TRACE-MATRIX
title: "Matriz de Trazabilidad — FARO"
owner: "Edgar Edmundo Coronel Navarrete"
status: in_review
version: "1.0"
source_of_truth: true
traces_up: ["02_Requirements/Requirements_Detailed", "02_Requirements/User_Stories"]
last_reviewed: "2026-08-03"
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
| [[02_Requirements/Requirements_Detailed\|REQ-001]] · Data Engineering | AC-001.1…AC-001.7 (7) | [[02_Requirements/User_Stories\|18 US]]: US-101–106, US-111–114, US-121a/b–124a/b | [[14_Data_Sources/_index\|DS-01…DS-08]] (las 8) | — (produce `features_escuela`) | [[03_Architecture/Data_Model\|Data_Model]] | ⬜ · US-111: `dbt compile` ✅ · US-103/US-104: estrella Gold completa (dim_tiempo, dim_driver, dim_escuela, dim_municipio, fact_escuela_ciclo + features_escuela), 88 data tests propios en PASS · US-105: interpolación IDW de D6 (aire) real hacia cada escuela (ADR-006), `dbt run`+`dbt test` 53/53 PASS, D5 (agua) sigue en SIN_DATO — bloqueado por DS-06 · 9 sources · US-112: estrella Gold materializada + tests nativos unique/not_null/relationships/accepted_values ✅ · BUG-009 `fixed`: 11 vars de dbt con default permanente (DEC-011), `dbt parse` verde como test de regresión en el job `dbt-contract` de `ci.yml` · US-106: linaje completo fuente→dashboard documentado (`Data_Lineage_US106.md`, **draft**, freeze objetivo 6-sep-2026) · US-122b/US-123b DS-04: fuente alterna a SharePoint encontrada y verificada (`repodatos.atdt.gob.mx`), extractor real agrega subtipo/modalidad, 12 553 440 filas en Bronze · [[06_Quality_Testing/Automated/Great_Expectations_DS04_Sesnsp\|TEST-011 ✅]] (14/15, hallazgo real: 1 fila con conteo negativo) · US-124b: 28 pruebas `pytest` nuevas para extractores/suites GE de DS-04/DS-05, corren offline sin red (326 pruebas totales del repo en verde) · US-113: 9 cubos Gold / 10 dashboards · cobertura explícita · DEC-010 compatible · dbt/contratos ✅ | [[_DevLog/2026-08-07-diana-alvarez-data-model-us101\|2026-08-07]] · [[_DevLog/2026-08-14-luis-garcia-us121b-prueba-descarga\|2026-08-14]] · [[_DevLog/2026-08-16-deni-garrido-us111-bronze-silver-cierre|2026-08-16 · US-111]] · [[_DevLog/2026-08-18-luis-garcia-us122b-extractor-sinaica\|2026-08-18 · US-122b]] · [[_DevLog/2026-08-18-diana-alvarez-us103-merge-silver-us111\|2026-08-18 · US-103]] · [[_DevLog/2026-08-19-diana-alvarez-us104-features-escuela\|2026-08-19 · US-104]] · [[_DevLog/2026-08-19-diana-alvarez-us103-gold-estrella\|2026-08-19 · US-103]] · [[_DevLog/2026-08-19-diana-alvarez-us105-idw-calidad-aire\|2026-08-19 · US-105]] · [[_DevLog/2026-08-22-deni-garrido-us112-silver-gold\|2026-08-22 · US-112]] [[_DevLog/2026-08-23-diana-alvarez-us106-linaje-freeze\|2026-08-23 · US-106]] · [[_DevLog/2026-08-23-edgar-bug009-defaults-dbt\|2026-08-23 · BUG-009]] · [[_DevLog/2026-08-24-luis-garcia-us122b-us123b-sesnsp-fuente-alterna\|2026-08-24 · US-122b/US-123b]] · [[_DevLog/2026-08-24-luis-garcia-us124b-fixtures-ds04-ds05\|2026-08-24 · US-124b]] · [[_DevLog/2026-08-23-deni-garrido-us113-cierre-dec010-pipeline\|2026-08-23 · US-113 cierre]] | US-111 · PR #37 · US-103/US-104 · US-105 · US-112 · PR #72 · US-106 · BUG-009/DEC-011 · US-122b/US-123b · US-124b · US-113 · PR #81 (Draft) | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-002]] · Frontend BI | AC-002.1…AC-002.6 (6) | [[02_Requirements/User_Stories\|19 US]]: US-201–207, US-211a/b, US-212, US-213, US-214a/b, US-215a/b, US-221–224 | — (vía Gold) | ML-01/02/03 (consumidos en DB-06/09) | [[03_Architecture/Data_Model\|Data_Model]] (cubos) · [[03_Architecture/Frontend_Architecture\|FARO Web]] · [[04_UX_Design/Screen_Specs\|Screen_Specs]] (US-201) · [[04_UX_Design/Cube_Specs_DB03_DB04\|Cube_Specs DB-03/04]] (US-211a) · [[04_UX_Design/Superset_Setup_US202\|Superset Setup]] (US-202) · [[04_UX_Design/Cube_Specs_DB05_DB08\|Cube_Specs DB-05/08]] (US-211b) | `test_semantic_db03_db04` ✅ (US-211a, 28 casos: SIN_DATO≠0, ML por JOIN, grano) · `test_semantic_db01_db02` ✅ (US-203, 47 casos: filtros AC-002.2 en todos los datasets, componentes aditivos DEC-008, SIN_DATO≠0) · E2E Playwright ✅ (16/16 charts con datos; filtros ciclo/entidad/nivel aplican a todo el tablero; nombres oficiales INEGI de municipio vía `gold.geo_municipio`) · `test_semantic_db05_db08` ✅ (US-211b, 29 casos: formato largo/unpivot, SIN_DATO≠0, sin ML en v1, grano) · **BUG-011** ✅ fixed (`sync_semantic_layer.py` lee con `encoding="utf-8"` explícito — ya no requiere `PYTHONUTF8=1` en Windows; `ensure_chart()` compara `datasource_id` y ya no repunta charts homónimos de otro tablero) | [[_DevLog/2026-08-07-manuel-serrania-us-201\|2026-08-07]] · US-201 · [[_DevLog/2026-08-13-manuel-serrania-screenspecs-cubos\|2026-08-13]] · [[_DevLog/2026-08-14-marina-garcia-cubos-db03-db04\|2026-08-14]] · US-211a · [[_DevLog/2026-08-15-manuel-serrania-kpis-db03-ratificacion-join\|2026-08-15]] · [[_DevLog/2026-08-16-manuel-serrania-us202-superset\|2026-08-16]] · US-202 · [[_DevLog/2026-08-21-manuel-serrania-us203-tableros-db01-db02\|2026-08-21]] · US-203 · [[_DevLog/2026-08-21-marina-garcia-cierre-us211a\|2026-08-21]] · US-211a ✅ cerrada · [[_DevLog/2026-08-24-marina-garcia-us212-db03-db04\|2026-08-24]] · US-212 (DB-03/DB-04 sobre mock; pendiente validar con Gold real) · [[_DevLog/2026-08-22-handoff-us203-tableros-superset\|2026-08-22]] · US-203 depuración E2E · [[_DevLog/2026-08-22-handoff-us203-verificacion-e2e-playwright\|2026-08-22]] · verificación E2E + diagnóstico · [[_DevLog/2026-08-22-manuel-serrania-us203-filtros-nombres-reales\|2026-08-22]] · US-203 filtros AC-002.2 completos + nombres reales · [[_DevLog/2026-08-22-monserrat-miranda-us211b-cubos-db05-db08\|2026-08-22]] · US-211b | ⬜ | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-003]] · Modelos ML | AC-003.1…AC-003.6 (6) | [[02_Requirements/User_Stories\|10 US]]: US-301–303, US-311–313, US-321, US-322, US-324, US-325 (+apoyo US-412/415/416) | DS-01…08 (vía `features_escuela`) | [[15_ML_Models/_index\|ML-01, ML-02, ML-03]] | [[03_Architecture/Data_Model\|Data_Model]] · [[03_Architecture/API_Specification\|API_Spec]] | [[06_Quality_Testing/Automated/Particion_Temporal_ML01\|TEST-003 ✅]] (US-311, AC-003.3) · [[15_ML_Models/Indice_Riesgo_ML01\|TEST-004 ✅]] (US-311) · [[15_ML_Models/ML01_Entrenamiento\|TEST-005 ✅]] (ML-01 entrenado) · [[15_ML_Models/Publicacion_Gold\|TEST-006 ✅]] (US-313) · [[06_Quality_Testing/Automated/Evaluacion_Modelos\|TEST-007 ✅]] (US-312) | [[_DevLog/2026-08-08-hector-morales-fixture-particion-temporal\|2026-08-08]] · [[_DevLog/2026-08-11-hector-morales-indice-riesgo-ml01\|2026-08-11]] · [[_DevLog/2026-08-13-hector-morales-entrenamiento-ml01\|2026-08-13]] · [[_DevLog/2026-08-14-hector-morales-publicacion-gold\|2026-08-14]] · [[_DevLog/2026-08-18-hector-morales-evaluacion-us312\|2026-08-18]] · [[_DevLog/2026-08-23-diana-alvarez-dec010-grano-dual-predicciones\|2026-08-23 · DEC-010]] | DEC-010 | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-004]] · Backend/API/Auth | AC-004.1…AC-004.6 (6) | [[02_Requirements/User_Stories\|14 US]]: US-401–405, US-411–416, US-421–423 | — | ML-01/02/03 (expuestos vía API) | [[03_Architecture/API_Specification\|API_Spec]] · [[03_Architecture/Data_Model\|Data_Model]] · [[03_Architecture/ADRs/ADR-004-autenticacion-oauth2-jwt\|ADR-004]] (auth) | `test_api_contract` ✅ (US-401/US-411/US-412/US-413, 31) · `test_auth_jwt` ✅ (US-402, 15) · `test_rbac` ✅ (US-403, 11) | [[_DevLog/2026-08-11-christian-ruiz-us401-contrato-api\|2026-08-11]] · US-401 · [[_DevLog/2026-08-17-christian-ruiz-us402-oauth-jwt\|2026-08-17]] · US-402 · [[_DevLog/2026-08-20-karla-monter-us411-endpoints-gold\|2026-08-20]] · US-411 · [[_DevLog/2026-08-27-karla-monter-us413-admin-endpoints\|2026-08-27]] · US-413 | US-411 · PR #59 | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-005]] · Deploy GCP | AC-005.1…AC-005.5 (5) | [[02_Requirements/User_Stories\|13 US]]: US-501, US-502, US-504, US-505, US-522a/b/c, US-524a/b/c, US-525a/b/c | — | — | [[08_CICD_DevOps/Cloud_Run_Deploy\|Cloud Run Deploy ✅]] | ⬜ | [[_DevLog/2026-08-09-luis-tellez-us501-cloud-run-deploy\|2026-08-09]] · [[_DevLog/2026-08-15-luis-tellez-us502-docker-compose-ml-services\|2026-08-15]] · US-502 · [[_DevLog/2026-08-25-alejandro-velazquez-us522a\|2026-08-25]] | ⬜ | 🟡 En progreso |
| [[02_Requirements/Requirements_Detailed\|REQ-006]] · Agente | AC-006.1…AC-006.4 (4) | [[02_Requirements/User_Stories\|4 US]]: US-304a, US-304b, US-305, US-323 | — (vía Gold) | — (RAG sobre Gold) | [[03_Architecture/API_Specification\|API_Spec]] (`/agente`) · [[03_Architecture/Data_Model\|Data_Model]] | ⬜ | ⬜ | ⬜ | 📋 Planeado |
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
