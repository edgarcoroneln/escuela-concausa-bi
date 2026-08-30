---
id: PLAN-EXEC-STATUS
title: "Estado de ejecución — FARO"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
source_of_truth: true
traces_up: ["02_Requirements/User_Stories", "12_Roadmap_Sprints/PLAN_MAESTRO"]
traces_down: ["13_Reports/PM_Dashboard_Spec", "02_Requirements/Traceability_Matrix"]
last_reviewed: "2026-08-28"
tags: [roadmap, execution, status, dashboard]
---

# Estado de ejecución — FARO

> Registro canónico de los campos **operativos** de cada historia. El catálogo, responsable, célula,
> sprint y REQ viven únicamente en [[02_Requirements/User_Stories]]. El tablero une ambos documentos.
> → [[12_Roadmap_Sprints/_index]] · [[13_Reports/PM_Dashboard_Spec]]

## Reglas

- Toda `US-###` ausente de la tabla se interpreta como `planned`; así no se duplica el catálogo.
- Estados válidos: `planned` → `in_progress` → `in_review` → `blocked` → `done`.
- `blocked` exige `bloqueo_desde` y un `BLOCK-###` en [[10_Risk_Governance/Blocker_Register]].
- `done` exige evidencia de PR/commit, prueba, DevLog y trazabilidad conforme a
  [[05_Engineering/Definition_of_Done]].
- **Historias cuyo entregable es una ruta HTTP de la API no cierran mientras esa ruta no responda
  en el despliegue que se va a demostrar.** El código correcto y las pruebas en verde son condición
  necesaria, no suficiente: la rúbrica evalúa la URL pública viva. Una historia cuyo entregable es
  un contrato, un esquema o una biblioteca sí cierra con evidencia de código, porque no tiene
  superficie desplegada que verificar. Criterio adoptado el 28-ago para resolver la asimetría entre
  US-411 y US-412 (ver [[13_Reports/US_Validation_Followup_2026-08-28]]).
- **Alcance del criterio anterior: aplica a rutas HTTP de la API, no a tableros de Superset.** Un
  tablero cierra con evidencia de código más capa de datos validada, y no queda condicionado a que
  Célula 5 lo despliegue. Precisión añadida el 29-ago a petición de Marina García, cuya pregunta
  expuso que la redacción original admitía dos lecturas y la diferencia valía medio sprint.
- El porcentaje del tablero se deriva del estado; nunca se captura manualmente.
- El PO actualiza este registro al cierre de cada standup.

## Historias con estado distinto de `planned`

| US | Estado | Inicio | Bloqueo desde | Evidencia | Actualizado |
|---|---|---|---|---|---|
| US-001 | done | 2026-08-01 | — | [[_DevLog/2026-08-03-handoff-cierre-planeacion]] · PR #3/#5 | 2026-08-10 |
| US-002 | done | 2026-08-01 | — | [[01_Product/PRD_General_Materia]] · [[02_Requirements/Requirements_Detailed]] | 2026-08-10 |
| US-003 | done | 2026-08-02 | — | [[09_AI_Governance/Agent_Contexts/_index]] · PR #3/#5 | 2026-08-10 |
| US-004 | in_review | 2026-08-03 | — | [[02_Requirements/Traceability_Matrix]] · [[13_Reports/PM_Dashboard_Spec]] · PR #112 · [[13_Reports/US_Validation_Followup_2026-08-28]]. Reconciliación del **29-ago**: 14 PRs mergeados en el día, 11 historias actualizadas, BUG-026 cerrado, BUG-027 `superseded`, BUG-028 registrado y [[13_Reports/Vault_Correcciones_2026-08-29|plan de corrección del vault]] abierto con 5 hallazgos. Historia continua hasta el cierre del proyecto | 2026-08-29 | 2026-08-28 |
| US-101 | done | 2026-08-02 | — | [[03_Architecture/Data_Model]] · [[_DevLog/2026-08-07-diana-alvarez-data-model-us101]] · PR #9 · PR #30 (columna indice_riesgo) | 2026-08-17 |
| US-102 | done | 2026-08-11 | — | [[_DevLog/2026-08-16-diana-alvarez-us102-fix-import-errors]] · PR #29 (DAGs de Airflow para las 8 fuentes) · PR #38 (fix de importación en dags) | 2026-08-17 |
| US-103 | done | 2026-08-15 | — | [[_DevLog/2026-08-19-diana-alvarez-us103-gold-estrella]] · PR #48 (esquema estrella Gold: dim_escuela, dim_municipio, fact_escuela_ciclo; 170 tests) | 2026-08-19 |
| US-104 | done | 2026-08-15 | — | [[_DevLog/2026-08-19-diana-alvarez-us104-features-escuela]] · PR #48 (gold.features_escuela con drivers D1-D4 reales); **target definido por DEC-007** (híbrido: variación `municipio × nivel` con serie SNIEE + features escuela con 911) — resuelve RISK-007 | 2026-08-19 |
| US-105 | done | 2026-08-18 | — | [[_DevLog/2026-08-19-diana-alvarez-us105-idw-calidad-aire]] · PR #52 (interpolación IDW de D6 calidad del aire + cobertura parcial e índice de confianza) | 2026-08-19 |
| US-106 | in_progress | 2026-08-23 | — | [[_DevLog/2026-08-23-diana-alvarez-us106-linaje-freeze]] · PR #77 ([[03_Architecture/Data_Lineage_US106]]: linaje nodo por nodo de fuente → dashboard) · PR #80 (Diana la declara al 80%). **El freeze sigue sin declararse**: el documento continúa en `status: draft`. Su dependencia US-113 pasó a `in_review` con PR #81, no a `done`, y **RISK-008** (`coneval_periodo_medicion`) sigue sin confirmar. Cierra cuando ambas cosas se resuelvan y Diana cambie el documento a `approved` | 2026-08-26 |
| US-111 | done | 2026-08-12 | — | [[_DevLog/2026-08-16-deni-garrido-us111-bronze-silver-cierre]] · PR #37 (transformaciones Bronze → Silver con dbt) · PR #67 (alineación del `ciclo` canónico) · PR #82 (**BUG-009**: 11 vars de dbt con default permanente, DEC-011) | 2026-08-25 |
| US-112 | done | 2026-08-14 | — | [[_DevLog/2026-08-22-deni-garrido-us112-silver-gold]] · PR #72 (estrella Gold materializada + tests nativos unique/not_null/relationships/accepted_values) · PR #67 (ciclo canónico en Silver). El DevLog condicionaba el cierre a que PR #72 dejara de estar abierto; se mergeó el 22-ago | 2026-08-25 |
| US-113 | in_review | 2026-08-15 | — | [[_DevLog/2026-08-23-deni-garrido-us113-cierre-dec010-pipeline]] · PR #81 (9 cubos y contratos) · [[_DevLog/2026-08-28-diana-alvarez-formato911-real-validacion-us113]] / PR #105 (estrella + **8 cubos** contra 4 ciclos reales, 149/149) · PR #115 / BUG-021 (dependencias `ref()` corregidas). Falta materializar/validar DB-10 `cubo_pipeline`, dependiente de DS-06, o que el PM apruebe una excepción explícita de alcance; después Deni confirma el cierre | 2026-08-28 |
| US-121a | done | 2026-08-28 | — | PR #107 **mergeado**: prueba de descarga real de DS-06 (endpoint `mapa.php`, 180 presas con volumen NAME/NAMO — reemplaza el `SOURCE_URL="PENDIENTE-CONFIRMAR"`) y de DS-08 CONAPO. [[_DevLog/2026-08-28-emilio-galnares-us121a-ds06-ds08]] | 2026-08-29 |
| US-122a | done | 2026-08-28 | — | PR #107 **mergeado**: `extractor_conagua.py` (POST automatizado, sin descarga manual) y `extractor_conapo.py` (252,450 registros, clave municipal corregida a 5 dígitos). [[_DevLog/2026-08-28-emilio-galnares-us121a-ds06-ds08]] | 2026-08-29 |
| US-123a | done | 2026-08-28 | — | PR #107 **mergeado**: Great Expectations `suite_ds06_conagua` 7/7 ✅ y `suite_ds08_conapo` 7/7 ✅, integradas a la suite compartida del equipo | 2026-08-29 |
| US-124a | done | 2026-08-28 | — | PR #107 **mergeado**: fixtures `bronze_ds06_conagua_sample.csv` (180 filas) y `bronze_ds08_conapo_sample.csv` (500), dentro del tope de 500 del plan §8 · `test_extractor_ds06` y `test_validacion_ds06` | 2026-08-29 |
| US-121b | done | 2026-08-13 | — | [[_DevLog/2026-08-14-luis-garcia-us121b-prueba-descarga]] · PR #31 (prueba de descarga real DS-04/DS-05) | 2026-08-17 |
| US-122b | done | 2026-08-14 | — | [[_DevLog/2026-08-18-luis-garcia-us122b-extractor-sinaica]] · [[_DevLog/2026-08-24-luis-garcia-us122b-us123b-sesnsp-fuente-alterna]] · PR #31 · PR #47 (extractor real de DS-05 SINAICA contra la API en vivo) · PR #85 (fuente alterna de DS-04 en `repodatos.atdt.gob.mx` verificada; el extractor agrega subtipo y modalidad, 12 553 440 filas) | 2026-08-26 |
| US-123b | done | 2026-08-18 | — | [[_DevLog/2026-08-21-luis-garcia-us123b-great-expectations-ds05]] · [[_DevLog/2026-08-24-luis-garcia-us122b-us123b-sesnsp-fuente-alterna]] · PR #47 · PR #63 (suite GE de DS-05) · **PR #85** (suite GE de DS-04, TEST-011 14/15 con hallazgo real: una fila con conteo negativo). Las dos mitades entregadas; Luis la declara 100% | 2026-08-26 |
| US-124b | done | 2026-08-24 | — | [[_DevLog/2026-08-24-luis-garcia-us124b-fixtures-ds04-ds05]] · **PR #85** (28 pruebas `pytest` nuevas para extractores y suites GE de DS-04/DS-05, corren offline sin red; 326 pruebas del repo en verde) | 2026-08-26 |
| US-201 | done | 2026-08-07 | — | [[04_UX_Design/Screen_Specs]] · [[_DevLog/2026-08-07-manuel-serrania-us-201]] · PR #10 · PR #27/#36 (KPIs 15-18, JOIN a predicciones) · PR #78 (alta de KPI-19/KPI-20 en el catálogo canónico) | 2026-08-25 |
| US-202 | done | 2026-08-15 | — | [[_DevLog/2026-08-16-manuel-serrania-us202-superset]] · PR #39 (Superset: conexión, datasets y capa semántica) | 2026-08-17 |
| US-203 | done | 2026-08-21 | — | [[_DevLog/2026-08-21-manuel-serrania-us203-tableros-db01-db02]] · [[_DevLog/2026-08-22-manuel-serrania-us203-filtros-nombres-reales]] · PR #71 (DB-01 Ejecutivo y DB-02 Mapa de riesgo, filtros AC-002.2 completos y nombres INEGI reales vía `gold.geo_municipio`; 47 casos y E2E Playwright 16/16 charts) · PR #88 (**BUG-011**: `sync_semantic_layer.py` leía en cp1252 y repuntaba charts homónimos de otro tablero) | 2026-08-26 |
| US-204 | in_review | 2026-08-27 | — | PR #100 (DB-06 y DB-09, 15/15 charts). **Desbloqueada parcialmente:** ADR-007 fija la unidad, pero DB-06 y DB-09 leen `gold.predicciones`, así que dependen del reentrenamiento de ML-01 y de la implementación de BUG-019 — **cuyo dueño se asigna en el standup del 30-ago** | 2026-08-30 |
| US-206 | done | 2026-08-07 | — | PR #134 **mergeado**: repunteo de la capa semántica a `gold.cubo_*`. **DEC-013 adopta la salida B** del choque con DB-05: los 18 charts se remapean y `valor_promedio_driver` sale del catálogo. La magnitud por driver no se pierde — vive en DB-08 (`valor_driver`, KPI-20). **DB-05 queda como tablero de decisión y DB-08 como tablero de exploración.** 53/53 en la suite DB-05/DB-08 | 2026-08-30 |
| US-207 | in_progress | 2026-08-07 | — | [[_DevLog/2026-08-07-edgar-andamiaje-faro-web]] · [[03_Architecture/Frontend_Architecture]] (solo andamiaje) | 2026-08-10 |
| US-211a | done | 2026-08-15 | — | [[_DevLog/2026-08-21-marina-garcia-cierre-us211a]] · PR #32 · PR #39 (métricas y jerarquías de cubos DB-03/DB-04, 28 casos `test_semantic_db03_db04`); grano de DB-04 registrado en **DEC-008** | 2026-08-21 |
| US-211b | done | 2026-08-22 | — | [[_DevLog/2026-08-22-monserrat-miranda-us211b-cubos-db05-db08]] · [[_DevLog/2026-08-22-monserrat-miranda-us211b-fix-revision-manuel]] · PR #73 (contrato semántico de DB-05/DB-08 en formato largo, 29 casos `test_semantic_db05_db08`) · PR #78 (alta de KPI-19/KPI-20, cierra §8.3); revisado y aprobado por Manuel Serranía; grano registrado en **DEC-009** | 2026-08-25 |
| US-212 | in_review | 2026-08-24 | — | [[_DevLog/2026-08-24-marina-garcia-us212-db03-db04]] · PR #84 · PR #103 · PR #126. **Al 95 % y desbloqueada el 30-ago:** BUG-026 cerrado por el PR #129 y **ADR-007 ratificado (DEC-012) confirmando fracción**, así que el umbral 0.6 de DEC-006 sigue válido y Marina no toca nada. Falta únicamente verificar los bloques de predicción de DB-03 (AC-002.4) **contra predicciones nuevas publicadas**, no contra el ADR firmado — depende del reentrenamiento de ML-01 (R-4, Héctor). **Valida: Marina García** | 2026-08-30 |
| US-213 | done | 2026-08-28 | — | PR #114 **mergeado**: DB-05 (36 charts, 6 tabs D1-D6) y DB-08 (explorador, 5 charts) sobre `gold.cubo_driver`/`cubo_pivot`. `_layout_tabs()` aditivo en `sync_semantic_layer.py`, aprobado por Manuel Serranía (dueño de la convención US-202). **Validado contra Gold real levantando el pipeline dbt completo, no el mock**: 41 charts nuevos con datos, 61 charts previos sin regresión · 51 pruebas · BUG-021 y BUG-022 escalados y corregidos. [[_DevLog/2026-08-28-monserrat-miranda-us213-db05-db08-dashboards]] | 2026-08-29 |
| US-221 | done | 2026-08-28 | — | PR #106 **mergeado** (`7754b90`): gráficos base reutilizables de KPIs. Corregido el 29-ago tras el reporte de Manuel Serranía, que detectó que esta fila seguía diciendo «PR #106 abierto». **Follow-up aparte** (no reabre la historia): Manuel ratificó una sola implementación por KPI — se borran los 5 `kpi_*.sql` y las tarjetas se remapean a datasets canónicos, con guarda antiduplicación en `test_kpis_us221.py`. Ese follow-up **absorbe BUG-027**, que queda `superseded` | 2026-08-29 |
| US-301 | done | 2026-08-09 | — | [[03_Architecture/ADRs/ADR-003-ml-estrategia-modelado]] · [[_DevLog/2026-08-09-andres-gonzalez-us301-estrategia-modelado]] · PR #12 | 2026-08-10 |
| US-302 | in_review | 2026-08-16 | — | PR #58 (ML-02 + SHAP + Gold) · PR #113 (`driver_dominante` supervisado real) · PR #116 (BUG-018 por ventana) · PR #117 (etiqueta real como autoridad); suite integrada 500 pass y F1 0.633. Falta correr métricas sobre Gold real actual, validar Registry Docker, conectar SHAP al endpoint y aprobar [[15_ML_Models/ML02_Clasificacion_Driver]] | 2026-08-28 |
| US-303 | in_review | 2026-08-16 | — | PR #123 **mergeado**: validación de versiones del registry con error accionable y prueba de regresión. PR #133 **mergeado**: ML-03 integrado al helper compartido `registrar_sklearn`, con lo que los tres modelos se registran por el mismo camino y la validación los cubre a todos. **Registrar una versión no implica promoverla a producción.** Falta el E2E contra MLflow real, la verificación conjunta ML-01/02/03 y la exposición vía la API de C4, que depende de BUG-020 | 2026-08-29 |
| US-304a | in_review | 2026-08-16 | — | PR #92/#104/#108/#119 · **PR #142 mergeado (Christian Ruiz): BUG-025 cerrado** — `/api/v1/agente/consulta` deja de ser el stub y conecta con el servicio RAG real, así que los guardarraíles por fin se invocan desde la API desplegada. Falta aprobar el documento del prompt | 2026-08-30 |
| US-304b | in_review | 2026-08-16 | — | [[_DevLog/2026-08-27-carlos-mayorga-us304b-us323]] · PR #108 mergeado · [[15_ML_Models/Agente_Recuperacion_US304b]] en `approved` · **PR #119 mergeado**: carga diferida del modelo, errores tipados e indexación idempotente con IDs deterministas. Falta verificar la recuperación dentro del contenedor antes de cerrar | 2026-08-28 |
| US-305 | in_review | 2026-08-26 | — | PR #92/#94/#98/#104/#119. **Desbloqueada el 30-ago:** BUG-020 cerrado y verificado en vivo (4/4 etapas del smoke test) y BUG-025 cerrado por el PR #142. Falta el E2E widget → API → RAG con login real sobre la URL pública, que ya responde | 2026-08-30 |
| US-311 | in_progress | 2026-08-08 | — | **Desbloqueada el 30-ago** por DEC-012: el `indice_riesgo` deja de saturar porque la unidad del target coincide con la calibración de la sigmoide. **Pendiente con dueño y fecha (R-4 del ADR): reentrenar ML-01 — Héctor Morales.** C2 verifica DB-03 con predicciones publicadas, no con la firma | 2026-08-30 |
| US-312 | done | 2026-08-18 | — | PR #42 (reporte comparativo, TEST-007) · PR #118 (drivers excluidos a MLflow, BUG-023) · **PR #135 mergeado**: ML-03 entra a la evaluación y cierra **AC-003.2**, que exigía que cada modelo reporte su métrica y llevaba días esperando a que ML-03 existiera. ML-03 **no finge mejora sobre baseline**: es no supervisado, su Silhouette mide separación de grupos y poner `0` habría afirmado en falso que el modelo no aporta. **PR #136 mergeado** (Andrés): el índice distingue entre *modelo entrenado* y *modelo que supera su umbral* — ML-03 entrena con Silhouette 0.1086 contra un umbral de 0.3, y el artefacto lo dice en vez de esconderlo. [[_DevLog/2026-08-29-hector-morales-ml03-en-evaluacion]] · [[_DevLog/2026-08-29-andres-gonzalez-estado-indice-modelos]] | 2026-08-30 |
| US-313 | in_review | 2026-08-14 | — | PR #41 · #83 · #96 · #111 · #117. **Desbloqueada el 30-ago:** ADR-007 ratificado en fracción (DEC-012). La guarda de escala que detenía la publicación **queda como control permanente, no medida temporal** (R-4). Falta ejecutar `--desde-gold` sobre Gold real con la unidad ya definida y publicar predicciones nuevas | 2026-08-30 |
| US-323 | done | 2026-08-27 | — | [[_DevLog/2026-08-27-carlos-mayorga-us304b-us323]] · PR #108 mergeado · [[15_ML_Models/Agente_Evaluacion_US323]] en `approved` · set de 20 preguntas y pruebas automatizadas de alcance/SQL inseguro | 2026-08-28 |
| US-324 | in_review | 2026-08-27 | — | [[_DevLog/2026-08-27-carlos-mayorga-us324]] · PR #110 mergeado: fichas ML-01/02/03. Falta revisión de los dueños de cada modelo y corregir la ficha ML-03 para no afirmar implementación mientras US-321 sigue pendiente | 2026-08-28 |
| US-401 | done | 2026-08-03 | — | [[03_Architecture/API_Specification]] · `api/openapi.v1.json` · [[_DevLog/2026-08-11-christian-ruiz-us401-contrato-api]] · PR #19 (18 pruebas de contrato) | 2026-08-11 |
| US-402 | done | 2026-08-15 | — | [[_DevLog/2026-08-17-christian-ruiz-us402-oauth-jwt]] · [[03_Architecture/ADRs/ADR-004-autenticacion-oauth2-jwt]] · PR #43 (OAuth2 + JWT access/refresh, `test_auth_jwt` 15 casos) | 2026-08-18 |
| US-403 | in_review | 2026-08-15 | — | [[_DevLog/2026-08-26-christian-ruiz-us403-rbac]] · PR #97. **Desbloqueada el 30-ago: BUG-020 cerrado**, así que el E2E de 401/403 ya se puede ejecutar sobre la URL pública. Falta definir `ANALISTA_EMAILS` y registrar la revisión de seguridad | 2026-08-30 |
| US-404 | in_progress | 2026-08-15 | — | PR #43 (hardening inicial de la API, avance); vence en S4 | 2026-08-18 |
| US-405 | in_progress | 2026-08-07 | — | [[_DevLog/2026-08-07-edgar-andamiaje-faro-web]] · [[03_Architecture/Frontend_Architecture]] (solo andamiaje) | 2026-08-10 |
| US-411 | in_review | 2026-08-20 | — | [[_DevLog/2026-08-20-karla-monter-us411-endpoints-gold]] · PR #59/#95/#99. **Desbloqueada el 30-ago: BUG-020 cerrado.** `/api/v1/escuelas` responde **200 con datos reales** sobre la URL pública. Falta ratificar `/series` fuera de alcance y confirmar el cierre | 2026-08-30 |
| US-412 | in_review | 2026-08-26 | — | [[_DevLog/2026-08-26-juan-macias-us412-repositorio-modelos-bug010]] · PR #95. **Desbloqueada el 30-ago: BUG-020 cerrado.** Estuvo reabierta por el criterio de ruta HTTP, no por defecto del código — que siempre estuvo correcto. La ruta ya responde en el despliegue; falta confirmar el cierre | 2026-08-30 |
| US-415 | done | 2026-08-26 | — | [[_DevLog/2026-08-26-juan-macias-us415-contrato-modelos]] · PR #95 mergeado: contrato Pydantic API↔ML, reutiliza `FeaturesEscuela`, valida alineación CCT/ciclo y agrega 11 pruebas; Juan la declara terminada en su plan | 2026-08-28 |
| US-416 | in_review | 2026-08-27 | — | [[_DevLog/2026-08-27-juan-macias-us416-cache-timeouts]] · PR #101 mergeado: cache TTL por fila, cache negativo, timeout SQL y error 503; suite 390 pass. Falta que el TL C4 ratifique el diseño y acepte que la prueba con Postgres real corresponde a US-422 | 2026-08-28 |
| US-421 | done | 2026-08-09 | — | **Entregada por otros, no por su dueña.** Las dos mitades existen en `main` desde antes de que Eloisa González arrancara: el esqueleto FastAPI en `src/api/main.py` (**Luis Téllez**, `0bfeb2e`, 09-ago, US-501) y el healthcheck con el contrato navegable en `src/api/v1/health.py` + `src/api/app.py` (**Christian Ruiz**, `1648259`, PR #19, 11-ago, US-401) — `/health`, `/version` y `/api/v1/docs`, que es AC-004.1. Cubierta por `test_health_ok` y `test_version_ok` en `tests/test_api_contract.py`, ambas en verde. Eloisa la verificó de punta a punta y lo dejó en dos DevLogs (PR #91) sin código propio, porque no quedaba código por escribir. **Es un traslape de planeación del PM**, no una historia sin entregar: se le asignó una historia que otras dos ya habían cubierto. Se reasigna a **US-422**, arrancando por la prueba que detecta **BUG-008**. Nota: dentro del contenedor `/health` lo sirve hoy `src.api.main:app`, no el contrato v1 — eso es BUG-008, y se registra en US-522a | 2026-08-26 |
| US-501 | done | 2026-08-09 | — | [[08_CICD_DevOps/Cloud_Run_Deploy]] · [[_DevLog/2026-08-09-luis-tellez-us501-cloud-run-deploy]] · PR #13 (URL pública viva) | 2026-08-10 |
| US-502 | done | 2026-08-13 | — | [[_DevLog/2026-08-15-luis-tellez-us502-docker-compose-ml-services]] · PR #34 (MLflow/Superset/ChromaDB con hardening) · PR #35 (docker-compose del ecosistema) | 2026-08-17 |
| US-503 | done | 2026-08-14 | — | [[_DevLog/2026-08-15-luis-tellez-us503-ci-pipeline]] · PR #35 (pipeline CI completo con GitLeaks y pip-audit) | 2026-08-17 |
| US-504 | in_review | 2026-08-16 | — | **PR #141 mergeado**: Fase 1 del provisionamiento GCP — VPC privada, Cloud SQL **sin IP pública**, Secret Manager y service account de mínimo privilegio, todo idempotente. **Fase 2 ejecutada el 30-ago: cierra BUG-020.** Verificado en vivo con `smoke-test-bug020.sh`: 4/4 etapas, exit code 0. Faltan Fase 3 (VM Airflow + IAP) y Fase 4 (Load Balancer + Cloud Armor), fuera del alcance de la demo | 2026-08-30 |
| US-505 | in_progress | 2026-08-16 | — | PR #34 (avance temprano de rollback/observabilidad); vence en S6 | 2026-08-17 |
| US-521a | done | 2026-08-12 | — | [[_DevLog/2026-08-12-alejandro-velazquez-mendoza]] · PR #25 (docker-compose + guía local API/Postgres) | 2026-08-17 |
| US-521b | in_progress | 2026-08-09 | — | [[_Meta/US-521b-guia-ambiente-local]] · [[_DevLog/2026-08-09-edgar-jimenez-setup]] · PR #14 · PR #29 (env DAGs); **verificar si el docker-compose de Airflow/ML ya queda cubierto por el compose del ecosistema (PR #35)** | 2026-08-17 |
| US-521c | in_review | 2026-08-12 | — | PR #23 mergeado: inventario y ambiente local. Existe `_DevLog/2026-08-11-Edward-Setup-Local`, pero no tiene extensión `.md`, ID ni estado válido y el linter no lo evalúa; Edward debe archivarlo correctamente, actualizar el índice y repetir la guía | 2026-08-28 |
| US-522a | in_review | 2026-08-12 | — | [[_DevLog/2026-08-25-alejandro-velazquez-us522a]] · PR #90 · PR #99 / [[_DevLog/2026-08-27-luis-tellez-bug008-api-dockerfile]]: contenedor corregido para arrancar la app real y OpenAPI de 18+ rutas validado en Cloud Run. Falta un E2E local Compose API↔Postgres; BUG-020 de producción se sigue por separado | 2026-08-28 |
| US-522b | in_review | 2026-08-25 | — | PR #87 abierto: contenerización de Airflow y corrección de SQLAlchemy. Pendiente resolver checks/revisión y merge | 2026-08-28 |
| US-522c | in_review | 2026-08-18 | — | PR #49 (contenedor Superset) · PR #71 corrige instalación persistente de `psycopg2` dentro de `/app/.venv` y ya existe evidencia de sync real. Falta que Edward escriba DevLog válido y que C5 actualice BUG-004 de `open` a `fixed` tras una verificación final | 2026-08-28 |
| US-523a | done | 2026-08-12 | — | [[_DevLog/2026-08-25-alejandro-velazquez-us522a]] · PR #90 · [[_DevLog/2026-08-26-edgar-reconciliacion-y-branch-protection]] / PR #93: documento corregido contra el ruleset real, tres discrepancias resueltas, [[05_Engineering/Branch_Protection]] en `approved` y TEST-002/vault en verde | 2026-08-28 |
| US-523c | done | 2026-08-22 | — | [[08_CICD_DevOps/US-523c-quality-gate]] (`status: done`) · PR #69 (workflow `quality_gate.yml` + plantilla de PR). Operando en todos los PRs desde el 22-ago. Deuda conocida: el workflow no se dispara en `edited`, así que corregir el cuerpo de un PR no vuelve a correr el check | 2026-08-25 |
| US-524a | in_review | 2026-08-28 | — | PR #102 abierto: logs estructurados, healthcheck y monitoreo de API/Postgres; la rama contiene correcciones de revisión y DevLog. Pendiente checks, revisión de C5 y merge | 2026-08-28 |

## Interpretación actual — 2026-08-28

- **32 `done`:** se agregan US-323, US-412, US-415 y US-523a, todas con PR mergeado, evidencia,
  DevLog y artefacto/pruebas trazables.
- **23 `in_review`:** incluyen las entregas mergeadas que aún necesitan una validación final y los
  PR abiertos #87, #102, #106, #107 y #114.
- **12 `in_progress`:** conservan trabajo funcional o dependencias todavía no terminadas; un PR
  parcial no las convierte automáticamente en `in_review`.
- **24 `planned`:** historias sin evidencia suficiente de inicio en las fuentes disponibles.

El detalle accionable —responsable, PR, gate de cierre, validador y controles para registrar
decisiones en junta— vive en [[13_Reports/US_Validation_Followup_2026-08-28]]. El HTML asociado es
una bitácora local de reunión; **no sustituye** esta fuente canónica.

Para US de documentación/diseño, la prueba de Definition of Done la cubren la revisión del Tech Lead,
`vault_lint` y TEST-002. Para código, datos, seguridad o despliegue se conserva además el gate técnico
específico descrito en la fila de la historia.
