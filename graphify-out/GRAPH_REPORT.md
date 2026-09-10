# Graph Report - us113-candidate  (2026-08-25)

## Corpus Check
- 299 files · ~135,311 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2267 nodes · 3115 edges · 312 communities (244 shown, 68 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `81027f82`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- vault_lint.py
- generate_pm_dashboard.py
- CLAUDE.md — Contexto del proyecto para agentes de IA
- Data Model — Arquitectura Medallón FARO
- PRD — FARO · Escuela como Sensor Social
- 3. Catálogo de endpoints
- README.md
- Branching Strategy — Modelo de ramas
- DS-01 · SEP Formato 911
- DS-02 · SEP Catálogo CCT
- DS-03 · SEP CEMABE (Censo de Escuelas, Maestros y Alumnos de Educación Básica y Especial)
- DS-04 · SESNSP Incidencia Delictiva Municipal
- DS-05 · SINAICA Calidad del Aire
- DS-06 · CONAGUA SINA (Sistema Nacional de Información del Agua)
- DS-07 · CONEVAL Rezago Social y Pobreza Municipal
- DS-08 · CONAPO Proyecciones de Población
- Catálogo de User Stories — FARO
- Secrets Policy — Manejo de credenciales y secretos
- Requisitos Detallados — FARO
- PULL_REQUEST_TEMPLATE.md
- Por tipo
- Developer Onboarding — FARO
- PR Checklist — FARO
- ADR-001 — Ejemplo: elección de base de datos
- Engineering Workflow — FARO
- Security Model — FARO
- AI Agent Governance — FARO
- AI Collaboration Guide — FARO
- Naming Conventions — IDs, archivos, ramas y commits
- Traceability Model — Cómo se conecta todo
- ⭐ Matriz de Trazabilidad — FARO
- System Design — FARO
- Coding Standards — FARO
- Environment Setup — FARO
- Compliance — FARO
- 🔒 Threat Model & Security Policy — Proyecto FARO
- api_list
- How To Navigate — Modelo del vault
- Technical Guide — FARO
- Branch Protection — FARO
- CI Quality Gates — FARO
- Deployment Guide — FARO
- Release Checklist — FARO
- Rollback Runbook — FARO
- Glossary — FARO
- OKRs & Nuestro Faro — FARO
- Security Review Checklist — FARO
- Prompt Library — FARO
- 14_Data_Sources — Fuentes de datos
- 15_ML_Models — Modelos de Machine Learning
- Definition of Filed — Intake de "cosas nuevas reportadas"
- Link Hygiene — Evitar links rotos y huérfanos
- Personas — FARO
- Requisitos Generales — FARO
- Security Audit Log — FARO
- Environments — FARO
- main
- 00_Start_Here/_index.md
- Vault_Changelog.md
- 01_Product/_index.md
- PRD_General_Materia.md
- 02_Requirements/_index.md
- ADRs/_index.md
- 03_Architecture/_index.md
- 05_Engineering/_index.md
- 07_Security/_index.md
- 08_CICD_DevOps/_index.md
- AI_Usage_Log.md
- 09_AI_Governance/_index.md
- GEMINI.md
- copilot-instructions.md
- Guía de ambiente local reproducible
- entrenar_ml02.py
- sync_semantic_layer.py
- test_semantic_db03_db04.py
- entrenar_ml01.py
- test_evaluar.py
- test_api_contract.py
- test_target_hibrido.py
- test_particion_temporal.py
- test_extractor_formato911_historico.py
- test_riesgo.py
- test_mlflow_utils.py
- v1/auth.py
- RepositorioGoldPostgres
- get_settings
- test_semantic_db01_db02.py
- test_agente_guardrails.py
- predicciones.py
- test_publicar_gold.py
- schemas.py
- evaluar.py
- escribir
- contrato.py
- Política de Credenciales — FARO
- ⚠️ ADVERTENCIAS DE SEGURIDAD — Desarrollo Local
- validacion_sinaica.py
- extractor_sinaica.py
- leer
- test_semantic_db05_db08.py
- parametrize
- PrediccionGold
- RepositorioGold
- test_auth_jwt.py
- agregar_a_municipio_nivel
- main.py
- BaseModel
- ResultadoEntrenamiento
- test_ml_strategy.py
- Estrategia de Modelado ML — FARO
- Publicación de predicciones y recomendaciones a Gold
- test_contrato_features.py
- Guía de ejecución local — Célula 3
- Borrador de PR — trabajo independiente Célula 3
- frontend/app.py
- `superset/` — capa semántica de Superset (convención US-202)
- ML-01 — Entrenamiento, backtesting y resultados
- config.py
- Rol
- prioridad_de_riesgo
- ADR-003 — Estrategia de modelado ML: partición temporal, backtesting y cobertura parcial
- Deploy a Cloud Run — FARO API
- Target híbrido de dos niveles para ML-01 (DEC-007)
- dag_anual.py
- api/app.py
- test_agente_prompt.py
- publicar_gold.py
- construir_predicciones_municipio_nivel
- generar_geojson_municipios.py
- FixtureRequest
- leer
- Frontend Architecture — FARO Web
- v1/__init__.py
- health.py
- generate_bronze_drivers_fixtures.py
- Linaje de datos completo — fuente → dashboard (US-106)
- Agente FARO — Guardarraíles de seguridad
- Índice de riesgo de ML-01 — de variación de matrícula a [0,1]
- ML-02 — Clasificación de driver dominante
- Preguntas de coordinación — Célula 3
- ADR-002 — Frontend integrado en Streamlit sobre Superset + API
- ADR-004 — Autenticación: OAuth2 con Google + JWT propio (access/refresh)
- ADR-005 — Mapeo de D3/D4 en dim_driver: infraestructura y conectividad desde CEMABE
- ADR-006 — Interpolación IDW de D5/D6 (agua/aire) hacia cada escuela
- Guía de Ambiente Local: API + Postgres
- extractor_conagua.py
- extractor_sesnsp.py
- FARO — Project Vault (SDLC-with-AI Standard)
- cargar_bronze_fixture.py
- generate_bronze_cct_conapo_fixtures.py
- 10. Troubleshooting
- 2. Configuración Inicial de GCP (Una sola vez)
- extractor_coneval.py
- extractor_cemabe.py
- walk_forward_splits
- mock_data.py
- `superset/semantic/` — capa semántica de DB-03 y DB-04
- features
- FARO — Índice del Proyecto (MOC maestro)
- build_authorization_url
- generate-keys.py
- verify-docker-compose.sh
- generate_bronze_formato911_historico_fixtures.py
- 5. Verificación del Deploy
- 9. Costos
- FARO Web (frontend Streamlit)
- cargar
- generate_bronze_sinaica_fixtures.py
- 3. Build y Push de Imagen Docker
- 4. Deploy a Cloud Run
- 6. Configuración de Seguridad
- 7. Actualización del Servicio
- dbt/README.md
- verificar-servicios.sh
- gold_ml_outputs_mock.sql
- generate_bronze_formato911_ciclo_anterior_fixture.py
- build-and-push.sh
- deploy-cloud-run.sh
- US-523c-quality-gate.md
- chromadb-entrypoint.sh
- mlflow-entrypoint.sh
- superset-init.sh
- VERIFICACION.md
- requirements/README.md
- agente/__init__.py
- api/__init__.py
- security/__init__.py
- 1_Dashboards.py
- 2_Panel_ML.py
- 3_Chat.py
- generate_bronze_formato911_fixture.py
- generate_mock_features.py
- test_el_umbral_de_riesgo_es_el_ratificado
- test_sin_prediccion_no_es_en_riesgo
- test_db01_cubo_agrupa_al_grano_declarado
- test_db02_cubo_agrupa_al_mismo_grano_que_db04
- test_los_componentes_son_aditivos_no_promedios
- test_variacion_es_ponderada_por_matricula
- test_los_filtros_globales_tienen_columna
- test_toda_razon_protege_la_division
- test_el_porcentaje_en_riesgo_usa_las_escuelas_puntuadas
- test_los_kpis_ratificados_estan_trazados
- test_cada_dataset_declara_su_sql_real
- test_todo_chart_apunta_a_dataset_y_metrica_declarados
- test_los_filtros_nativos_cubren_columnas_reales
- test_el_mock_es_identificable
- test_el_mock_es_idempotente
- test_el_mock_no_destruye_nada
- test_el_mock_solo_toca_tablas_de_salida_ml
- test_el_mock_respeta_el_umbral_r3
- sync
- test_el_layout_genera_estructura_v2
- test_los_formatos_d3_cubren_los_formatos_del_yaml
- test_los_porcentajes_se_formatean_como_porcentaje
- test_db05_no_guarda_promedio_ya_calculado
- test_db05_agrupa_al_grano_declarado
- test_el_yaml_declara_los_tres_filtros_globales
- test_toda_razon_protege_la_division
- test_pct_sin_dato_reusa_kpi06
- test_db05_publica_el_denominador_real_del_driver

## God Nodes (most connected - your core abstractions)
1. `build_snapshot()` - 25 edges
2. `entrenar_y_evaluar()` - 21 edges
3. `indice_riesgo()` - 21 edges
4. `get_settings()` - 20 edges
5. `entrenar_y_evaluar()` - 19 edges
6. `ParticionTemporal` - 19 edges
7. `escribir()` - 19 edges
8. `construir_reporte()` - 17 edges
9. `_metadatos()` - 17 edges
10. `ensure_dashboard()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `test_recomendacion_falla_con_driver_desconocido()` --calls--> `recomendacion_para_driver()`  [INFERRED]
  tests/test_entrenar_ml02.py → src/modelos/recomendaciones.py
- `test_pregunta_de_faro_esta_en_alcance()` --calls--> `pregunta_en_alcance()`  [EXTRACTED]
  tests/test_agente_guardrails.py → src/agente/guardrails.py
- `test_pregunta_fuera_de_dominio_se_rechaza()` --calls--> `pregunta_en_alcance()`  [EXTRACTED]
  tests/test_agente_guardrails.py → src/agente/guardrails.py
- `test_cte_que_solo_lee_gold_se_permite()` --calls--> `validar_sql_lectura()`  [EXTRACTED]
  tests/test_agente_guardrails.py → src/agente/guardrails.py
- `test_join_por_coma_se_rechaza()` --calls--> `validar_sql_lectura()`  [EXTRACTED]
  tests/test_agente_guardrails.py → src/agente/guardrails.py

## Import Cycles
- None detected.

## Communities (312 total, 68 thin omitted)

### Community 0 - "vault_lint.py"
Cohesion: 0.43
Nodes (7): find_md(), main(), _norm(), Normaliza separadores a / para comparaciones multiplataforma (Windows/Unix)., Quita bloques y spans de código para no leer links de ejemplo., stem(), strip_code()

### Community 1 - "generate_pm_dashboard.py"
Cohesion: 0.12
Nodes (47): date, build_engagement(), build_history(), build_pending(), build_performance(), build_prd_compliance(), build_snapshot(), clean() (+39 more)

### Community 2 - "CLAUDE.md — Contexto del proyecto para agentes de IA"
Cohesion: 0.06
Nodes (28): 1.bis Apuntadores por herramienta, 1. Orden de lectura obligatorio al iniciar sesión, 2. Consulta el grafo antes de leer archivos, 3. Reglas de trabajo (resumen — el detalle está en Vault_Rules), 4. LLM Handoff Protocol, 5. Si eres el siguiente agente, AGENTS.md — Protocolo para cualquier asistente de IA, 1. Qué es este proyecto (+20 more)

### Community 3 - "Data Model — Arquitectura Medallón FARO"
Cohesion: 0.08
Nodes (25): 1. Principios de diseño, 2. BRONZE — landing crudo, 3. SILVER — limpio y conformado, 4.1 `gold.fact_escuela_ciclo` — hecho central, 4.2 Dimensiones, 4.3 Cubos materializados (para los 10 dashboards), 4.4 `gold.features_escuela` — contrato con la Célula 3, 4.5 Salida de modelos (+17 more)

### Community 4 - "PRD — FARO · Escuela como Sensor Social"
Cohesion: 0.11
Nodes (18): 10. Arquitectura medallón, 11. Los 3 modelos de ML, 12.1 Capa web integrada (FARO Web), 12. Los 10 dashboards (Superset), 13. Criterios de éxito (medibles), 14. Fuera de alcance (expectativas acotadas), 15. Requisitos no funcionales (NFR), 16. Referencias (+10 more)

### Community 5 - "3. Catálogo de endpoints"
Cohesion: 0.08
Nodes (22): 1. Principios, 2.1 Flujo OAuth2 con Google + JWT, 2.2 Matriz RBAC (los 2 roles del PRD), 2.3 Códigos: 401 vs 403, 2. Autenticación y autorización, 3.1 Salud y versión (públicos), 3.2 Autenticación `/auth/*`, 3.3 Lectura sobre Gold (+14 more)

### Community 6 - "README.md"
Cohesion: 0.29
Nodes (3): Adoption Guide — Cómo adoptar este vault en un proyecto, Checklist de "vault listo", Paso a paso

### Community 7 - "Branching Strategy — Modelo de ramas"
Cohesion: 0.13
Nodes (14): Aprobación de Pull Requests — compuerta única (PM), Aprobación obligatoria — Edgar Edmundo Coronel Navarrete (PM / PO), Branching Strategy — Modelo de ramas, Convención de commits, Convención de nombres, Flujo completo, Modelo: rama por unidad de trabajo, Principio rector (+6 more)

### Community 8 - "DS-01 · SEP Formato 911"
Cohesion: 0.15
Nodes (12): 10. Riesgos conocidos, 1. Identificación, 2. Acceso, 3. Frecuencia real de actualización, 4. Cobertura geográfica y temporal, 5. Esquema esperado (confirmar en prueba de descarga), 6. Llave de unión, 7. Driver que alimenta (+4 more)

### Community 9 - "DS-02 · SEP Catálogo CCT"
Cohesion: 0.17
Nodes (11): 10. Riesgos conocidos, 1. Identificación, 2. Acceso, 3. Frecuencia real de actualización, 4. Cobertura geográfica y temporal, 5. Esquema esperado (confirmar en prueba de descarga), 6. Llave de unión, 7. Driver que alimenta (+3 more)

### Community 10 - "DS-03 · SEP CEMABE (Censo de Escuelas, Maestros y Alumnos de Educación Básica y Especial)"
Cohesion: 0.17
Nodes (11): 10. Riesgos conocidos, 1. Identificación, 2. Acceso, 3. Frecuencia real de actualización, 4. Cobertura geográfica y temporal, 5. Esquema esperado (confirmar en prueba de descarga), 6. Llave de unión, 7. Driver que alimenta (+3 more)

### Community 11 - "DS-04 · SESNSP Incidencia Delictiva Municipal"
Cohesion: 0.17
Nodes (11): 10. Riesgos conocidos, 1. Identificación, 2. Acceso, 3. Frecuencia real de actualización, 4. Cobertura geográfica y temporal, 5. Esquema esperado (confirmar en prueba de descarga), 6. Llave de unión, 7. Driver que alimenta (+3 more)

### Community 12 - "DS-05 · SINAICA Calidad del Aire"
Cohesion: 0.17
Nodes (11): 10. Riesgos conocidos, 1. Identificación, 2. Acceso, 3. Frecuencia real de actualización, 4. Cobertura geográfica y temporal, 5. Esquema real (confirmado en prueba de descarga, 2026-08-14), 6. Llave de unión, 7. Driver que alimenta (+3 more)

### Community 13 - "DS-06 · CONAGUA SINA (Sistema Nacional de Información del Agua)"
Cohesion: 0.17
Nodes (11): 10. Riesgos conocidos, 1. Identificación, 2. Acceso, 3. Frecuencia real de actualización, 4. Cobertura geográfica y temporal, 5. Esquema esperado (confirmar en prueba de descarga), 6. Llave de unión, 7. Driver que alimenta (+3 more)

### Community 14 - "DS-07 · CONEVAL Rezago Social y Pobreza Municipal"
Cohesion: 0.17
Nodes (11): 10. Riesgos conocidos, 1. Identificación, 2. Acceso, 3. Frecuencia real de actualización, 4. Cobertura geográfica y temporal, 5. Esquema esperado (confirmar en prueba de descarga), 6. Llave de unión, 7. Driver que alimenta (+3 more)

### Community 15 - "DS-08 · CONAPO Proyecciones de Población"
Cohesion: 0.17
Nodes (11): 10. Riesgos conocidos, 1. Identificación, 2. Acceso, 3. Frecuencia real de actualización, 4. Cobertura geográfica y temporal, 5. Esquema esperado (confirmar en prueba de descarga), 6. Llave de unión, 7. Driver que alimenta (+3 more)

### Community 16 - "Catálogo de User Stories — FARO"
Cohesion: 0.18
Nodes (10): Catálogo de User Stories — FARO, Célula 0 · PO — Dirección de Proyecto, Célula 1 · Data Engineering & Quality, Célula 2 · Analytics & Business Intelligence, Célula 3 · Machine Learning & Agente IA, Célula 4 · Backend, API & Seguridad, Célula 5 · Cloud Infrastructure & DevOps, Resumen A · Historias por sprint (+2 more)

### Community 17 - "Secrets Policy — Manejo de credenciales y secretos"
Cohesion: 0.18
Nodes (10): Cómo se manejan, En CI (GitHub Actions), Local (desarrollo), Producción (GCP), Qué se considera secreto, Regla absoluta, Reglas para el trabajo con IA, Secrets Policy — Manejo de credenciales y secretos (+2 more)

### Community 18 - "Requisitos Detallados — FARO"
Cohesion: 0.20
Nodes (9): REQ-001 — Data Engineering y pipelines multi-fuente, REQ-002 — Frontend BI interactivo, REQ-003 — Tres modelos de ML integrados vía API, REQ-004 — Backend, API y autenticación avanzada, REQ-005 — Despliegue en GCP dockerizado con URL pública, REQ-006 — Agente conversacional, REQ-007 — Trabajo en equipo, Git y documentación, Requisitos Detallados — FARO (+1 more)

### Community 19 - "PULL_REQUEST_TEMPLATE.md"
Cohesion: 0.20
Nodes (9): Aprobación — compuerta única (PM · DEC-003), Avance entregado, Calidad, ¿Cómo lo probaste?, Definition of Filed, IDs relacionados, ¿Qué cambia y por qué?, Seguridad (+1 more)

### Community 20 - "Por tipo"
Cohesion: 0.22
Nodes (8): CI/CD / Infra, Componente (frontend), Definition of Done — FARO, Endpoint (backend), No bloquea (MVP), Por tipo, Schema / datos, Universales (toda tarea)

### Community 21 - "Developer Onboarding — FARO"
Cohesion: 0.22
Nodes (8): 1. Requisitos, 2. Setup, 3. Tu primer día, 4. Directorio del equipo, 5. Flujo de trabajo (resumen), 6. Integrantes que completaron onboarding, Developer Onboarding — FARO, Pendientes para la sesión del 2026-08-06

### Community 22 - "PR Checklist — FARO"
Cohesion: 0.25
Nodes (7): Calidad / Trazabilidad, Colaboración IA (primero), Código, PR Checklist — FARO, Pruebas, 🚫 Rechazo automático, Seguridad

### Community 23 - "ADR-001 — Ejemplo: elección de base de datos"
Cohesion: 0.29
Nodes (6): ADR-001 — Ejemplo: elección de base de datos, Alternativas consideradas, Consecuencias, Contexto, Decisión, Trazabilidad

### Community 24 - "Engineering Workflow — FARO"
Cohesion: 0.29
Nodes (6): Archivos "hot-spot", Conflictos, Engineering Workflow — FARO, Flujo paso a paso, Reglas de oro, Trazabilidad en el commit

### Community 25 - "Security Model — FARO"
Cohesion: 0.29
Nodes (6): Acceso a producción, Autenticación, Autorización, Datos, Reglas de datos (si aplica, p.ej. Firestore/DB rules), Security Model — FARO

### Community 26 - "AI Agent Governance — FARO"
Cohesion: 0.29
Nodes (6): AI Agent Governance — FARO, Checklist antes de activar un agente nuevo, Kill-switch (proceso), Ownership de archivos por colaborador, Principios de gobernanza, Reglas no negociables

### Community 27 - "AI Collaboration Guide — FARO"
Cohesion: 0.29
Nodes (6): AI Collaboration Guide — FARO, Al terminar (obligatorio), Antes de cada sesión, Durante, Qué NO debe hacer un agente, Skills útiles (Claude Code)

### Community 28 - "Naming Conventions — IDs, archivos, ramas y commits"
Cohesion: 0.29
Nodes (6): Commits — Conventional Commits, Naming Conventions — IDs, archivos, ramas y commits, Nombres de archivo, Nombres de personas, Prefijos de ID (globales, únicos, secuenciales), Ramas Git

### Community 29 - "Traceability Model — Cómo se conecta todo"
Cohesion: 0.29
Nodes (6): Backlinks (Obsidian), Cómo se mantiene sin fricción, Frontmatter de trazabilidad (estándar), La cadena de trazabilidad, La matriz viva, Traceability Model — Cómo se conecta todo

### Community 30 - "⭐ Matriz de Trazabilidad — FARO"
Cohesion: 0.33
Nodes (5): Cómo se mantiene, Estado del proyecto, Leyenda de estado, Matriz, ⭐ Matriz de Trazabilidad — FARO

### Community 31 - "System Design — FARO"
Cohesion: 0.33
Nodes (5): Componentes, Decisiones clave, Diagrama de alto nivel, Requisitos no funcionales que impactan el diseño, System Design — FARO

### Community 32 - "Coding Standards — FARO"
Cohesion: 0.33
Nodes (5): Coding Standards — FARO, Comentarios, Estilo, Manejo de errores y logging, Reglas mínimas de lint (bloqueantes en CI)

### Community 33 - "Environment Setup — FARO"
Cohesion: 0.33
Nodes (5): Comandos comunes, Environment Setup — FARO, Instalación, Requisitos, Variables de entorno

### Community 34 - "Compliance — FARO"
Cohesion: 0.33
Nodes (5): Atribuciones requeridas, Checklist legal pre-release, Compliance — FARO, Licencias de terceros / APIs, Privacidad de datos

### Community 35 - "🔒 Threat Model & Security Policy — Proyecto FARO"
Cohesion: 0.06
Nodes (33): 1. Network-based, 2. Credential-based, 3. Application-based, 4. Data-based, Activos Críticos, Actores de Amenaza, Altas (5), Bajas (2) (+25 more)

### Community 36 - "api_list"
Cohesion: 0.60
Nodes (5): api(), api_list(), main(), next_page(), Recorre la paginación REST para no truncar el conteo por persona.

### Community 37 - "How To Navigate — Modelo del vault"
Cohesion: 0.40
Nodes (4): How To Navigate — Modelo del vault, Idea central, Para encontrar…, Reglas de navegación

### Community 38 - "Technical Guide — FARO"
Cohesion: 0.40
Nodes (4): Convenciones de código, Entornos, Stack, Technical Guide — FARO

### Community 39 - "Branch Protection — FARO"
Cohesion: 0.40
Nodes (4): Branch Protection — FARO, CODEOWNERS (opcional pero recomendado), Reglas obligatorias en `main`, Verificación

### Community 40 - "CI Quality Gates — FARO"
Cohesion: 0.40
Nodes (4): CI Quality Gates — FARO, Esqueleto de pipeline (`.github/workflows/ci.yml`), Gates, Trazabilidad NFR → Gate

### Community 41 - "Deployment Guide — FARO"
Cohesion: 0.40
Nodes (4): Deployment Guide — FARO, Estrategia, Pasos (referencia), Post-deploy

### Community 42 - "Release Checklist — FARO"
Cohesion: 0.40
Nodes (4): Post-release, Pre-release, Release, Release Checklist — FARO

### Community 43 - "Rollback Runbook — FARO"
Cohesion: 0.40
Nodes (4): Criterios para revertir, Kill-switch, Procedimiento, Rollback Runbook — FARO

### Community 44 - "Glossary — FARO"
Cohesion: 0.50
Nodes (3): Glossary — FARO, Términos del dominio (rellenar), Términos del vault

### Community 45 - "OKRs & Nuestro Faro — FARO"
Cohesion: 0.50
Nodes (3): Nuestro Faro (métrica estrella), OKRs del ciclo, OKRs & Nuestro Faro — FARO

### Community 46 - "Security Review Checklist — FARO"
Cohesion: 0.50
Nodes (3): Checklist, Resultado, Security Review Checklist — FARO

### Community 47 - "Prompt Library — FARO"
Cohesion: 0.50
Nodes (3): Plantilla de prompt de tarea, Prompt Library — FARO, Prompts por fase

### Community 48 - "14_Data_Sources — Fuentes de datos"
Cohesion: 0.50
Nodes (3): 14_Data_Sources — Fuentes de datos, Las 8 fuentes del proyecto, Prueba de descarga real — obligatoria (Semana 1)

### Community 49 - "15_ML_Models — Modelos de Machine Learning"
Cohesion: 0.40
Nodes (4): 15_ML_Models — Modelos de Machine Learning, Documentos, Los 3 modelos, Reglas de modelado no negociables

### Community 50 - "Definition of Filed — Intake de "cosas nuevas reportadas""
Cohesion: 0.50
Nodes (3): Checklist de "Filed" ✅, Definition of Filed — Intake de "cosas nuevas reportadas", Flujo de intake por tipo

### Community 51 - "Link Hygiene — Evitar links rotos y huérfanos"
Cohesion: 0.50
Nodes (3): Check automatizado, Link Hygiene — Evitar links rotos y huérfanos, Reglas

### Community 71 - "Guía de ambiente local reproducible"
Cohesion: 0.29
Nodes (5): _Meta — Reglas del vault, 1. Mapeo de puertos, 2. Variables de entorno, 3. Verificación del entorno, Guía de ambiente local reproducible

### Community 72 - "entrenar_ml02.py"
Cohesion: 0.07
Nodes (44): HistGradientBoostingClassifier, RuntimeError, Series, calcular_shap_kernel(), cargar_features_ml02(), columna_target_disponible(), entrenar_y_evaluar(), explicar_driver() (+36 more)

### Community 73 - "sync_semantic_layer.py"
Cohesion: 0.07
Nodes (51): _apply_metrics_and_columns(), _coerce(), _detalle_dataset(), ensure_chart(), ensure_dashboard(), ensure_database(), ensure_datasets(), _export_chart() (+43 more)

### Community 74 - "test_semantic_db03_db04.py"
Cohesion: 0.05
Nodes (47): db03(), db04(), leer(), metricas(), fixture, FixtureRequest, parametrize, Path (+39 more)

### Community 75 - "entrenar_ml01.py"
Cohesion: 0.06
Nodes (42): ndarray, _entidades_de(), entrenar_y_evaluar(), _error_por_entidad(), _matriz(), MetricasVentana, DataFrame, Entrenamiento y backtesting de ML-01 — regresión de variación de matrícula… (+34 more)

### Community 76 - "test_evaluar.py"
Cohesion: 0.07
Nodes (47): cobertura_y_error(), construir_reporte(), curva_por_ventana(), error_por_entidad(), FilaComparativa, _md(), DataFrame, Tabla comparativa de los modelos evaluados. ML-01 y ML-02 optimizan cosas… (+39 more)

### Community 77 - "test_api_contract.py"
Cohesion: 0.07
Nodes (37): exportar(), Path, Exporta el OpenAPI del contrato v1 a `api/openapi.v1.json` (US-401). Este JSON…, Genera el OpenAPI y lo escribe con formato estable (claves ordenadas, UTF-8)., Fake de `RepositorioGold` para la suite rápida del contrato (US-411, Decisión…, Mismo contrato que `RepositorioGoldPostgres`, resuelto en memoria sobre las…, Mismo criterio que `RepositorioGoldPostgres._aplicar_orden`: `SIN_DATO`…, RepositorioGoldFake (+29 more)

### Community 78 - "test_target_hibrido.py"
Cohesion: 0.07
Nodes (41): nivel_de_cct(), Deriva el nivel educativo de los caracteres 3–5 del CCT. >>>…, cargar_dimension(), DataFrame, Path, Adjunta el objetivo multi-año de la serie SNIEE al grano agregado. El target…, Lee `gold.dim_escuela` (o su fixture) con las columnas que la agregación…, unir_target() (+33 more)

### Community 79 - "test_particion_temporal.py"
Cohesion: 0.08
Nodes (39): columna_cobertura(), Devuelve el nombre de la bandera de cobertura de un driver. >>>…, ciclos_ordenados(), dividir_por_ciclo(), generar_backtesting(), DataFrame, Partición temporal y backtesting para ML-01 (US-311). Regla no negociable del…, Genera ventanas de backtesting *walk-forward* (ventana de entrenamiento… (+31 more)

### Community 80 - "test_extractor_formato911_historico.py"
Cohesion: 0.10
Nodes (33): _detectar_columna_cct(), extraer_formato911_historico(), _parsear_ciclo(), DataFrame, Extractor de DS-01 Formato 911 -- distribucion HISTORICA multi-ciclo…, Lee el CSV real de un ciclo (ruta local a un archivo ya descargado) y devuelve…, Descarga y parsea los ciclos indicados (todos por default) de la distribucion…, Devuelve el nombre real de la columna llave de escuela en este archivo. Falla… (+25 more)

### Community 81 - "test_riesgo.py"
Cohesion: 0.10
Nodes (32): CalibracionRiesgo, indice_riesgo(), T, Traducción de la predicción de ML-01 al `indice_riesgo` ∈ [0,1] (US-311). ##…, Convierte la variación de matrícula predicha por ML-01 en `indice_riesgo` ∈…, Inversa de `indice_riesgo`: qué variación produce un riesgo dado. Sirve para…, Calibración de la sigmoide, definida por dos anclas de negocio. Args:…, variacion_equivalente() (+24 more)

### Community 82 - "test_mlflow_utils.py"
Cohesion: 0.10
Nodes (29): Any, Utilidades comunes de registro MLflow para Célula 3 (US-303)., Falla temprano y con un mensaje accionable si cliente y servidor no son…, Configuracion para registrar un modelo en MLflow., Falla si el modelo no usa el nombre acordado en `ML_Strategy` §7., Registra un modelo compatible con scikit-learn en MLflow. El import de MLflow…, Consulta la versión del servidor MLflow. `None` si no es un servidor HTTP o no…, Versión de MLflow instalada localmente. `None` si no está instalado. (+21 more)

### Community 83 - "v1/auth.py"
Cohesion: 0.11
Nodes (27): HTTPAuthorizationCredentials, RefreshIn, TokenPair, UserOut, get_current_user(), get_google_verifier(), Dependencias FastAPI de seguridad (US-402). - `get_current_user` — extrae y…, Valida el access token del encabezado `Authorization` y devuelve el usuario.… (+19 more)

### Community 84 - "RepositorioGoldPostgres"
Cohesion: 0.10
Nodes (18): get_engine(), get_tablas(), _metadatos(), Engine, MetaData, Table, Conexión a Postgres para las lecturas reales sobre Gold (US-411). Define el…, `(metadata, dim_escuela, dim_municipio, fact_escuela_ciclo, predicciones,… (+10 more)

### Community 85 - "get_settings"
Cohesion: 0.15
Nodes (26): Exception, get_settings(), Settings cacheados (una sola lectura del entorno por proceso)., AuthError, create_access_token(), create_refresh_token(), _decode(), _encode() (+18 more)

### Community 86 - "test_semantic_db01_db02.py"
Cohesion: 0.08
Nodes (15): Pruebas del contrato semántico de DB-01 y DB-02 (US-203). Mismas reglas que…, En driver dominante, COALESCE solo puede etiquetar la categoría vacía., KPI-07 lee la salida prescriptiva de ML-02; LEFT porque el modelo va llegando., La capa de puntos no agrega: cada CCT es un marcador (Screen_Specs §2)., Contrato visual §4: la fila superior son tiles KPI (big_number_total)., Contrato §2: coroplético municipal + puntos de escuela georreferenciados., Deja un municipio completo sin predicciones para probar cobertura SIN_DATO., Los ajustes finos viven en el YAML (`params_extra`), no en código. (+7 more)

### Community 87 - "test_agente_guardrails.py"
Cohesion: 0.14
Nodes (23): aplicar_limit(), pregunta_en_alcance(), preparar_sql_seguro(), Guardarrailes de seguridad para el agente conversacional (US-304a). Este modulo…, Garantiza un `LIMIT` maximo para respuestas auditables y acotadas., Valida y normaliza SQL de solo lectura. Raises: ValueError: si la consulta…, Resultado de aplicar una regla de seguridad., Valida si una pregunta pertenece al dominio de FARO. La regla es… (+15 more)

### Community 88 - "predicciones.py"
Cohesion: 0.14
Nodes (21): prediccion_de_escuela(), Deriva un `PrediccionOut` de ejemplo a partir de una escuela del mock., ExplicacionSHAPOut, Page, PrediccionBatchIn, PrediccionOut, Sobre de paginación por *offset*. Ver §1 del contrato., paginate() (+13 more)

### Community 89 - "test_publicar_gold.py"
Cohesion: 0.15
Nodes (21): construir_recomendaciones(), Genera las filas de `gold.recomendaciones` a partir del driver dominante. El…, DataFrame, Pruebas de la publicación a Gold (US-313, TEST-006). Usan SQLite en un archivo…, DEC-005: `valor` guarda la unidad original y `indice_riesgo` la versión acotada., ML-01 no produce probabilidad: NULL explícito, nunca 0., Sin ML-02 no hay driver; no se inventa uno para las escuelas restantes., Anti-deriva: si la Célula 4 cambia su catálogo, esto falla y se reconcilia. El… (+13 more)

### Community 90 - "schemas.py"
Cohesion: 0.16
Nodes (20): Direccion, OrdenEscuela, OrdenMunicipio, EscuelaDetalleOut, EscuelaOut, KpisOut, MunicipioOut, Modelos Pydantic del contrato de la API FARO (US-401). Fuente de verdad:… (+12 more)

### Community 91 - "evaluar.py"
Cohesion: 0.12
Nodes (20): entidad_de_cct(), Extrae la clave INEGI de entidad (2 dígitos) que prefija al CCT.…, cargar_features(), Path, Lee la tabla de features desde CSV o Parquet. Raises: FileNotFoundError: si la…, main(), Path, Evaluación comparativa de los modelos y análisis de error (US-312). Cierra… (+12 more)

### Community 92 - "escribir"
Cohesion: 0.14
Nodes (22): escribir(), _metadatos(), _objetivo_de_conflicto(), DataFrame, MetaData, Table, Define las dos tablas de Gold. `esquema=None` para motores sin esquemas…, Elige el índice único contra el que hace UPSERT este lote. Con grano dual… (+14 more)

### Community 93 - "contrato.py"
Cohesion: 0.14
Nodes (18): Cobertura, FeaturesEscuela, BaseModel, Enum, str, Espejo local del contrato `gold.features_escuela` (US-311). El contrato…, Ausencia explícita de dato: nunca 0, nunca nulo silencioso., Una fila por CCT × ciclo. Grano y columnas fijados por el contrato §5.3. (+10 more)

### Community 94 - "Política de Credenciales — FARO"
Cohesion: 0.11
Nodes (18): Almacenamiento de Credenciales, Auditoría y Cumplimiento, Desarrollo Local, Desarrollo Local, Frecuencia Recomendada, Generación de Credenciales, Nivel de Seguridad, Política de Credenciales — FARO (+10 more)

### Community 95 - "⚠️ ADVERTENCIAS DE SEGURIDAD — Desarrollo Local"
Cohesion: 0.11
Nodes (17): ✅ Aceptable SOLO para desarrollo porque:, Actual (Desarrollo Local), ⚠️ ADVERTENCIAS DE SEGURIDAD — Desarrollo Local, Airflow (puerto 8080), ChromaDB (puerto 8001), 🌐 Configuración de Red, 🔐 Credenciales en Desarrollo, 🏢 En Producción (Sprint 4): (+9 more)

### Community 96 - "validacion_sinaica.py"
Cohesion: 0.20
Nodes (17): _archivo_mas_reciente(), _contexto(), _expectativas_estaciones(), _expectativas_observaciones(), _obtener_o_crear_asset(), _obtener_o_crear_batch_definition(), DataFrame, Validaciones de calidad (Great Expectations) para DS-05 SINAICA — capa Bronze.… (+9 more)

### Community 97 - "extractor_sinaica.py"
Cohesion: 0.18
Nodes (15): DAG horario — orquesta la extracción de fuentes con periodicidad horaria (DS-05…, _estaciones_activas(), _extraer_dato_horario(), extraer_sinaica(), extraer_sinaica_estaciones(), extraer_sinaica_observaciones(), _guardar_parquet(), DataFrame (+7 more)

### Community 98 - "leer"
Cohesion: 0.21
Nodes (17): dashboards(), datasets_por_nombre(), db01_cubo(), db01_dist(), db01_driver(), db02_cubo(), db02_puntos(), leer() (+9 more)

### Community 99 - "test_semantic_db05_db08.py"
Cohesion: 0.12
Nodes (9): Pruebas del contrato semántico de los cubos de DB-05 y DB-08 (US-211b). Mismas…, DB-08 está al grano de detalle (cct × driver × ciclo): no debe agregar., KPI-19 (DB-05) y KPI-20 (DB-08) están libres en el catálogo: se registran como…, Sólo `cubo_driver` necesita el cambio de grano estilo DEC-008 (Cube_Specs…, El formato `porcentaje_*` (d3 `%`) ya multiplica por 100 al mostrar (convención…, test_cubo_driver_declara_grano_canonico_y_cambio_solicitado(), test_db08_no_agrega_al_grano_del_hecho(), test_kpi19_y_kpi20_estan_propuestos() (+1 more)

### Community 100 - "parametrize"
Cohesion: 0.17
Nodes (16): FixtureRequest, parametrize, A diferencia de DB-03/DB-04, v1 de estos cubos analiza el driver observado, no…, Formato largo: cada uno de los 6 drivers debe aparecer como literal (Cube_Specs…, 6 bloques (uno por driver) requieren al menos 5 `UNION ALL`., Ciclo, entidad y nivel deben existir en ambos cubos (AC-002.2)., Sin agrupar/filtrar por id_driver, las métricas del formato largo se inflan x6., Prohibido `COALESCE(d#, 0)`: la ausencia de dato no es un cero (Data_Model §1). (+8 more)

### Community 101 - "PrediccionGold"
Cohesion: 0.16
Nodes (14): model_validator, PrediccionGold, BaseModel, Exactamente una llave poblada según el grano — nunca ambas, nunca ninguna. Es…, Contrato ejecutable de una fila de `gold.recomendaciones` (§4.5)., Contrato ejecutable de una fila de `gold.predicciones` (§4.5, grano dual…, RecomendacionGold, _fila_base() (+6 more)

### Community 102 - "RepositorioGold"
Cohesion: 0.13
Nodes (10): get_repositorio_gold(), Protocol, Dependencia de FastAPI (`Depends(get_repositorio_gold)`). Las pruebas rápidas…, Lecturas sobre Gold que necesitan `/escuelas`, `/municipios` y `/kpis`., `(items, total)` de escuelas que cumplen los filtros, ordenadas y ya paginadas.…, Detalle de una escuela (con los 6 drivers) o `None` si no existe/no aplica…, `(items, total)` de municipios que cumplen los filtros, ordenados y ya…, Detalle de un municipio por clave INEGI o `None` si no existe. (+2 more)

### Community 103 - "test_auth_jwt.py"
Cohesion: 0.21
Nodes (13): GoogleIdentity, Identidad mínima que necesitamos de Google para emitir nuestros JWT., client(), fixture, TestClient, Pruebas del núcleo de autenticación OAuth2/JWT (US-402). Todo offline y sin…, test_callback_con_verificador_falso_emite_tokens(), test_login_redirige_a_google() (+5 more)

### Community 104 - "agregar_a_municipio_nivel"
Cohesion: 0.14
Nodes (14): agregar_a_municipio_nivel(), Agrega las features de escuela al grano `municipio × nivel × ciclo` de DEC-007.…, Qué pasó al agregar. Sirve para no publicar un dataset sin saber qué se perdió., Fracción de escuelas que sí encontraron su municipio y nivel., ResumenAgregacion, agregado(), engine(), modelo() (+6 more)

### Community 105 - "main.py"
Cohesion: 0.21
Nodes (13): on_event, health(), info(), get, FARO API - FastAPI Application Endpoint inicial para Sprint 1: Hello World +…, Evento de inicio de la aplicación, Evento de apagado de la aplicación, Endpoint raíz - Hello World from FARO Returns: dict: Mensaje de bienvenida con… (+5 more)

### Community 106 - "BaseModel"
Cohesion: 0.21
Nodes (13): MetricsOut, PipelineRunIn, PipelineRunOut, BaseModel, export(), metrics(), pipeline_run(), get (+5 more)

### Community 107 - "ResultadoEntrenamiento"
Cohesion: 0.15
Nodes (9): _imprimir_reporte(), main(), Resultado completo del backtesting más el modelo de producción., La ventana más reciente: entrena con todo el pasado y evalúa el último ciclo., Registra el backtesting en MLflow: una corrida padre y una hija por ventana.…, Reporte legible en consola: es la evidencia que va al PR y al DevLog., Punto de entrada: entrena, evalúa, reporta y registra en MLflow., registrar_en_mlflow() (+1 more)

### Community 108 - "test_ml_strategy.py"
Cohesion: 0.14
Nodes (13): df(), fixture, Tests de no-fuga temporal y schema del fixture mock (TEST-ML-001, TEST-ML-002,…, TEST-ML-003: el fixture tiene todas las columnas del schema esperado de…, TEST-ML-002: no hay nulos en ninguna columna., TEST-ML-002: drivers imputados (dato_disponible=0) nunca tienen valor 0.0 (cero…, TEST-ML-001: ningún ciclo del conjunto de test aparece en el conjunto de train…, Solo las 4 entidades del scope están en el fixture (09 CDMX, 15 Edomex, 19 NL,… (+5 more)

### Community 109 - "Estrategia de Modelado ML — FARO"
Cohesion: 0.15
Nodes (12): 1. Los 3 modelos, 2. Fuente de datos, 3. Partición temporal, 4. Manejo de cobertura parcial (D5 y D6), 5. Umbrales de aceptación (provisionales), 6. Explicabilidad — ML-02, 7. Registro en MLflow, 8. Tests requeridos (US-301) (+4 more)

### Community 110 - "Publicación de predicciones y recomendaciones a Gold"
Cohesion: 0.15
Nodes (12): 1. Contrato, 2. Grano dual (DEC-010), 3. Idempotencia, 4. Catálogo prescriptivo, 5. Prioridad, 6. Integración con ML-02, 7. Uso, 8. Pruebas (+4 more)

### Community 111 - "test_contrato_features.py"
Cohesion: 0.21
Nodes (12): skipif, _columnas_declaradas(), Guarda del contrato `gold.features_escuela` entre Célula 1 y Célula 3…, Columnas que la Célula 1 declara para `features_escuela` en su `schema.yml`. Se…, Toda columna declarada por la C1 debe existir en `FeaturesEscuela`., Cada campo del espejo debe aparecer en el SQL que construye la tabla. Detecta…, La regla de cobertura parcial exige valor + bandera para los seis drivers., Regla 4 de `15_ML_Models/_index`: nunca cero, nunca nulo silencioso. (+4 more)

### Community 112 - "Guía de ejecución local — Célula 3"
Cohesion: 0.17
Nodes (11): Ambiente usado en esta rama, Correr pruebas enfocadas, Ejecutar ML-02 con MLflow, Ejecutar ML-02 contra fixture sintético, Guía de ejecución local — Célula 3, Instalar dependencias mínimas, Limitaciones conocidas, Objetivo (+3 more)

### Community 113 - "Borrador de PR — trabajo independiente Célula 3"
Cohesion: 0.17
Nodes (11): Aprobación — compuerta única (PM · DEC-003), Avance entregado, Borrador de PR — trabajo independiente Célula 3, Calidad, ¿Cómo lo probaste?, Definition of Filed, IDs relacionados, ¿Qué cambia y por qué? (+3 more)

### Community 114 - "frontend/app.py"
Cohesion: 0.26
Nodes (10): main(), FARO Web — app Streamlit integrada (andamiaje). Router + sesión + guardas por…, current_user(), login_button(), logout_button(), Autenticación del frontend delegando en la API (andamiaje). El front NO…, Devuelve el usuario en sesión o None. TODO(US-405): validar el JWT contra la…, TODO(US-405): iniciar el flujo OAuth2 (Google) contra /auth/login de la API. (+2 more)

### Community 115 - "`superset/` — capa semántica de Superset (convención US-202)"
Cohesion: 0.17
Nodes (11): Cadena local completa (US-203), Estructura de carpetas, Estructura del YAML, Naming de archivos y de métricas, Notas del GeoJSON (`assets/geojson/municipios_scope.geojson`), Notas del mock (`mock/gold_ml_outputs_mock.sql`), Reglas no negociables (heredadas de Screen_Specs y Data_Model), Responsables (+3 more)

### Community 116 - "ML-01 — Entrenamiento, backtesting y resultados"
Cohesion: 0.18
Nodes (10): 1. El modelo, 2. Protocolo de evaluación, 3. Resultados (datos sintéticos, 400 filas · 80 escuelas · 5 ciclos), 4. Registro en MLflow, 5. Del modelo al tablero, 6. Pruebas, 7. Lo que falta para cerrar US-311, Error por entidad (ventana de producción) (+2 more)

### Community 117 - "config.py"
Cohesion: 0.18
Nodes (6): BaseSettings, Configuración tipada de la API FARO (US-402). Lee variables de entorno…, Parámetros de la API. Los nombres mapean a variables de entorno en MAYÚSCULAS., True si el secreto es el de desarrollo o es demasiado corto para HS256., Falla rápido si se intenta correr en producción con un secreto inseguro. Evita…, Settings

### Community 118 - "Rol"
Cohesion: 0.20
Nodes (10): Enum, str, Los 2 roles del PRD (RBAC de US-403)., Rol, Política de asignación de rol (US-402/US-403). ⚠️ **PROVISIONAL.** La política…, Devuelve el rol para un correo según la política provisional de mínimo…, resolve_role(), MonkeyPatch (+2 more)

### Community 119 - "prioridad_de_riesgo"
Cohesion: 0.20
Nodes (11): Grano, Prioridad, prioridad_de_riesgo(), Enum, str, Traduce el `indice_riesgo` a urgencia de intervención. **No inventa umbrales…, Urgencia de la intervención, derivada del `indice_riesgo`., Discriminador de grano de `gold.predicciones` (DEC-010). ML-01 puede predecir a… (+3 more)

### Community 120 - "ADR-003 — Estrategia de modelado ML: partición temporal, backtesting y cobertura parcial"
Cohesion: 0.20
Nodes (9): ADR-003 — Estrategia de modelado ML: partición temporal, backtesting y cobertura parcial, Alternativas consideradas, Consecuencias, Contexto, Decisión, Protocolo de backtesting por modelo, Protocolo de cobertura parcial (drivers D5 y D6), Protocolo de partición temporal (+1 more)

### Community 121 - "Deploy a Cloud Run — FARO API"
Cohesion: 0.20
Nodes (10): 11. Recursos y Referencias, 12. Próximos Pasos (Sprints futuros), 1. Requisitos Previos, 8.1 Cloud Logging, 8.2 Cloud Monitoring, 8.3 Uptime checks (Sprint 2), 8. Monitoreo y Observabilidad, Configuración de GCP (+2 more)

### Community 122 - "Target híbrido de dos niveles para ML-01 (DEC-007)"
Cohesion: 0.20
Nodes (9): 1. Qué separa DEC-007, 2. El hueco que había que resolver, 3. Cómo se agregan los drivers, 4. Lo que la agregación reporta, 5. Estado, 6. Pruebas, 7. Pendiente, Ensayo sobre el fixture (+1 more)

### Community 123 - "dag_anual.py"
Cohesion: 0.20
Nodes (7): DAG anual — orquesta la extracción de fuentes con periodicidad anual (DS-01…, extraer_conapo(), Descarga las Proyecciones de la Población de México (CONAPO) y las guarda en…, # TODO: reemplazar por el parseo real del CSV de CONAPO, extraer_formato911(), Descarga la Estadística Educativa - Formato 911 (SEP/SIGED) y la guarda en…, # TODO: reemplazar por el parseo real del CSV/XLSX de Formato 911

### Community 124 - "api/app.py"
Cohesion: 0.29
Nodes (8): FastAPI, JSONResponse, create_app(), _lifespan(), Fábrica de la app del **contrato v1** de FARO (US-401). Esta app es la…, Construye la app del contrato v1 con sus routers y manejadores de error…, _respuesta_error(), ErrorOut

### Community 125 - "test_agente_prompt.py"
Cohesion: 0.24
Nodes (5): construir_prompt_sistema(), Prompt de sistema del agente FARO (US-304a)., Construye el prompt final con contexto RAG opcional. US-304b aportara el…, Pruebas del prompt de sistema del agente (US-304a)., test_construir_prompt_agrega_contexto_recuperado()

### Community 126 - "publicar_gold.py"
Cohesion: 0.24
Nodes (9): construir_recomendaciones_ml02(), main(), _motor(), Engine, Publicación de predicciones y recomendaciones a Gold (US-313). Job batch que…, Conecta las clases de ML-02 con las recomendaciones del mismo ciclo de ML-01., Crea el motor desde `--url`, `DATABASE_URL` o el `docker-compose.yml` local., Entrena ML-01, construye las filas de Gold y las publica. (+1 more)

### Community 127 - "construir_predicciones_municipio_nivel"
Cohesion: 0.20
Nodes (10): construir_predicciones(), construir_predicciones_municipio_nivel(), datetime, Genera las filas de `gold.predicciones` para ML-01. Predice sobre el ciclo más…, Genera filas de `gold.predicciones` con `grano = municipio_nivel` (DEC-010 +…, DEC-010: la fila declara su grano en vez de atribuir el valor a cada escuela…, test_cada_grano_es_idempotente_por_separado(), test_falla_si_el_agregado_no_trae_las_llaves() (+2 more)

### Community 128 - "generar_geojson_municipios.py"
Cohesion: 0.38
Nodes (9): descargar(), _douglas_peucker(), generar(), main(), _perp_dist(), Path, Distancia del punto p al segmento ab (proyección, grados)., _simplificar() (+1 more)

### Community 129 - "FixtureRequest"
Cohesion: 0.27
Nodes (10): FixtureRequest, parametrize, `fact_escuela_ciclo` solo tiene hechos observados (Data_Model §4.1)., Con INNER JOIN, una escuela sin predicción desaparecería del mapa sin…, (cct, id_ciclo) + modelo='ML-01': sin llave completa se mezclan ciclos; sin…, Una escuela/municipio sin predicción no tiene riesgo 0: tiene SIN_DATO., test_el_join_usa_llave_completa_y_filtro_de_modelo(), test_el_riesgo_no_se_rellena_con_cero() (+2 more)

### Community 130 - "leer"
Cohesion: 0.27
Nodes (10): db05(), db08(), leer(), metricas(), fixture, Path, Carga el YAML de métricas. `pyyaml` no está en requirements.txt: si falta, se…, Lee un artefacto de la capa semántica; falla con un mensaje útil si no está. (+2 more)

### Community 131 - "Frontend Architecture — FARO Web"
Cohesion: 0.22
Nodes (8): 1. Objetivo, 2. Componentes (`src/frontend/`), 3. Autenticación y roles, 4. Embebido de Superset (guest token + RLS), 5. Panel de ML y chat, 6. Despliegue, 7. Trazabilidad, Frontend Architecture — FARO Web

### Community 132 - "v1/__init__.py"
Cohesion: 0.28
Nodes (7): AgenteConsultaIn, AgenteRespuestaOut, consulta(), post, Agente conversacional `/agente/*` (§3.5). Responde en lenguaje natural sobre…, Consulta en lenguaje natural sobre Gold (rol mínimo: ciudadano)., Router agregado de la v1 del contrato FARO. Reúne todos los subrouters de §3…

### Community 133 - "health.py"
Cohesion: 0.31
Nodes (8): HealthOut, VersionOut, health(), get, Salud y versión (endpoints públicos, §3.1 del contrato)., Liveness del contrato v1 (público, sin token)., Versión de la API y commit desplegado (público, sin token)., version()

### Community 134 - "generate_bronze_drivers_fixtures.py"
Cohesion: 0.22
Nodes (7): generar_cemabe(), generar_coneval(), generar_sesnsp(), Genera fixtures Bronze (<=500 filas, anonimizados) para cemabe, coneval y…, DS-04 SESNSP: incidencia delictiva municipal, serie mensual. 3 meses x tipo de…, DS-03 CEMABE: infraestructura escolar a nivel CCT. Incluye un caso SIN_DATO…, DS-07 CONEVAL: rezago social y pobreza a nivel municipio. `entidad`/`municipio`…

### Community 135 - "Linaje de datos completo — fuente → dashboard (US-106)"
Cohesion: 0.25
Nodes (7): 1. Estado de este documento, 2. Cómo leer el diagrama, 3. Qué está materializado hoy (23-ago-2026) vs. qué falta, 4. Checklist para el freeze del 6 de septiembre, 5. Qué significa "congelar" el esquema, 6. Ver también, Linaje de datos completo — fuente → dashboard (US-106)

### Community 136 - "Agente FARO — Guardarraíles de seguridad"
Cohesion: 0.25
Nodes (7): Agente FARO — Guardarraíles de seguridad, Contrato esperado, Objetivo, Pendientes para cerrar US-304a, Prompt de sistema, Reglas implementadas, Validación

### Community 137 - "Índice de riesgo de ML-01 — de variación de matrícula a [0,1]"
Cohesion: 0.25
Nodes (7): 1. El hueco que cierra, 2. La definición, 3. Por qué una sigmoide, 4. Lo que hay que ratificar, 5. Pruebas, Valores de referencia, Índice de riesgo de ML-01 — de variación de matrícula a [0,1]

### Community 138 - "ML-02 — Clasificación de driver dominante"
Cohesion: 0.25
Nodes (7): Estado actual, Explicabilidad, ML-02 — Clasificación de driver dominante, Objetivo, Pendientes para cerrar US-302, Target provisional, Validación

### Community 139 - "Preguntas de coordinación — Célula 3"
Cohesion: 0.25
Nodes (7): Para Carlos / US-304b y US-323, Para Diana Alvarez / Célula 1 — `gold.features_escuela`, Para Edgar / PM, Para Estefany / ML-03, Para Juan Carlos / Christian / Célula 4 — API de inferencia, Para Luis / Edgar Ulises / Célula 5 — MLflow y jobs ML, Preguntas de coordinación — Célula 3

### Community 140 - "ADR-002 — Frontend integrado en Streamlit sobre Superset + API"
Cohesion: 0.29
Nodes (6): ADR-002 — Frontend integrado en Streamlit sobre Superset + API, Alternativas consideradas, Consecuencias, Contexto, Decisión, Trazabilidad

### Community 141 - "ADR-004 — Autenticación: OAuth2 con Google + JWT propio (access/refresh)"
Cohesion: 0.29
Nodes (6): ADR-004 — Autenticación: OAuth2 con Google + JWT propio (access/refresh), Alternativas consideradas, Consecuencias, Contexto, Decisión, Riesgos de seguridad y mitigaciones

### Community 142 - "ADR-005 — Mapeo de D3/D4 en dim_driver: infraestructura y conectividad desde CEMABE"
Cohesion: 0.29
Nodes (6): ADR-005 — Mapeo de D3/D4 en dim_driver: infraestructura y conectividad desde CEMABE, Alternativas consideradas, Consecuencias, Contexto, Decisión, Trazabilidad

### Community 143 - "ADR-006 — Interpolación IDW de D5/D6 (agua/aire) hacia cada escuela"
Cohesion: 0.29
Nodes (6): ADR-006 — Interpolación IDW de D5/D6 (agua/aire) hacia cada escuela, Alternativas consideradas, Consecuencias, Contexto, Decisión, Trazabilidad

### Community 144 - "Guía de Ambiente Local: API + Postgres"
Cohesion: 0.29
Nodes (6): 1. Requisitos Previos, 2. Iniciar el Ambiente Local, 3. Conexión a la Base de Datos (Para DBeaver/pgAdmin), 4. Acceso a la API, 5. Detener el Ambiente, Guía de Ambiente Local: API + Postgres

### Community 145 - "extractor_conagua.py"
Cohesion: 0.29
Nodes (5): DAG diario — orquesta la extracción de fuentes con periodicidad diaria (DS-06…, extraer_conagua(), Extractor de CONAGUA SINA (DS-06) — Disponibilidad hídrica, periodicidad…, Descarga la lectura diaria más reciente de CONAGUA SINA y la guarda en Bronze.…, # TODO: reemplazar por el parseo real del formato de CONAGUA (CSV o API,…

### Community 146 - "extractor_sesnsp.py"
Cohesion: 0.29
Nodes (5): DAG mensual — orquesta la extracción de fuentes con periodicidad mensual (DS-04…, extraer_sesnsp(), Extractor de SESNSP (DS-04) — Incidencia delictiva municipal, periodicidad…, Descarga la incidencia delictiva municipal más reciente de SESNSP y la guarda…, # TODO: reemplazar por el parseo real del CSV de SESNSP

### Community 147 - "FARO — Project Vault (SDLC-with-AI Standard)"
Cohesion: 0.29
Nodes (7): Cómo adoptar este vault en tu proyecto, 🚀 Despliegue, FARO — Project Vault (SDLC-with-AI Standard), Mapa del ciclo de vida, Principios (ver [[_Meta/Vault_Rules]]), Qué es este vault, URL de Producción

### Community 148 - "cargar_bronze_fixture.py"
Cohesion: 0.38
Nodes (6): cargar_fixture(), cargar_fixture_formato911(), _dsn(), Carga un fixture de Bronze (CSV en tests/fixtures/, <=500 filas, anonimizado) a…, Carga el CSV de fixture a bronze.<tabla>, usando el DDL/columnas/llave de…, Compatibilidad hacia atrás: equivalente a cargar_fixture(...,…

### Community 149 - "generate_bronze_cct_conapo_fixtures.py"
Cohesion: 0.29
Nodes (5): generar_cct(), generar_conapo(), Genera fixtures Bronze (<=500 filas, anonimizados) para bronze.cct (DS-02) y…, DS-02 Catálogo CCT: identidad y georreferencia por escuela. Una fila SIN_DATO…, DS-08 CONAPO: proyecciones de población por municipio y grupo de edad. 3 grupos…

### Community 150 - "10. Troubleshooting"
Cohesion: 0.33
Nodes (6): 10. Troubleshooting, Cold start lento (>3 segundos), Error: "API not enabled", Error: "Container manifest type not supported", Error: "Permission denied", Servicio no responde

### Community 151 - "2. Configuración Inicial de GCP (Una sola vez)"
Cohesion: 0.33
Nodes (6): 2.1 Autenticación, 2.2 Configurar proyecto, 2.3 Habilitar APIs necesarias, 2.4 Crear Artifact Registry, 2.5 Configurar Docker para Artifact Registry, 2. Configuración Inicial de GCP (Una sola vez)

### Community 152 - "extractor_coneval.py"
Cohesion: 0.33
Nodes (4): DAG bienal — orquesta la extracción de fuentes con cadencia real…, extraer_coneval(), Descarga el Índice de Rezago Social / Medición de Pobreza municipal (CONEVAL) y…, # TODO: reemplazar por el parseo real del XLSX de CONEVAL (encabezados en…

### Community 153 - "extractor_cemabe.py"
Cohesion: 0.33
Nodes (4): DAG censal estático — orquesta la extracción de la fuente censal única, sin…, extraer_cemabe(), Descarga el Censo de Escuelas, Maestros y Alumnos de Educación Básica y…, # TODO: reemplazar por el parseo real del CSV de CEMABE

### Community 154 - "walk_forward_splits"
Cohesion: 0.33
Nodes (5): Index, DataFrame, Utilidad de partición temporal walk-forward para modelos de series de tiempo…, Genera índices de train/test con walk-forward de 1 ciclo. Garantiza que no haya…, walk_forward_splits()

### Community 155 - "mock_data.py"
Cohesion: 0.33
Nodes (5): kpis_mock(), metrics_mock(), Datos de ejemplo para el stub del contrato (US-401). 100% sintéticos y…, KPIs agregados de ejemplo sobre las escuelas del mock., Métricas internas de ejemplo (solo analista).

### Community 156 - "`superset/semantic/` — capa semántica de DB-03 y DB-04"
Cohesion: 0.33
Nodes (5): Cómo se validan, Para qué sirve cada cosa, Pendientes de coordinación, Reglas que estos archivos respetan, `superset/semantic/` — capa semántica de DB-03 y DB-04

### Community 157 - "features"
Cohesion: 0.33
Nodes (5): features(), DataFrame, fixture, Configuración compartida de pytest. Pone la raíz del repositorio en `sys.path`…, Fixture simulado de `gold.features_escuela` (datos 100% sintéticos).

### Community 158 - "FARO — Índice del Proyecto (MOC maestro)"
Cohesion: 0.40
Nodes (5): 🧭 Ciclo de vida (carpetas), 🚀 Empieza aquí, FARO — Índice del Proyecto (MOC maestro), 🎯 Salud del proyecto (rellenar), 🛠 Soporte

### Community 159 - "build_authorization_url"
Cohesion: 0.40
Nodes (5): RedirectResponse, build_authorization_url(), Construye la URL de consentimiento de Google (OpenID Connect:…, login(), Inicia OAuth2 con Google redirigiendo a la pantalla de consentimiento. Nota de…

### Community 160 - "generate-keys.py"
Cohesion: 0.40
Nodes (4): generate_secure_password(), generate_unique_username(), Genera password seguro con letras y números (sin símbolos), Genera username único por servicio

### Community 161 - "verify-docker-compose.sh"
Cohesion: 0.70
Nodes (4): check_container(), check_http(), check_port(), verify-docker-compose.sh script

### Community 162 - "generate_bronze_formato911_historico_fixtures.py"
Cohesion: 0.60
Nodes (4): _formatear_entidad_municipio(), _formatear_nivel(), generar(), Genera tests/fixtures/bronze_formato911_historico_sample.csv -- muestra…

### Community 163 - "5. Verificación del Deploy"
Cohesion: 0.50
Nodes (4): 5.1 Obtener la URL del servicio, 5.2 Probar endpoints, 5.3 Verificar logs, 5. Verificación del Deploy

### Community 164 - "9. Costos"
Cohesion: 0.50
Nodes (4): 9.1 Free Tier de Cloud Run (mensual), 9.2 Estimación de costos para FARO (Sprint 1), 9.3 Proyección futura (Sprint 4-6), 9. Costos

### Community 165 - "FARO Web (frontend Streamlit)"
Cohesion: 0.50
Nodes (3): Correr en local (cuando esté implementado), Estructura (andamiaje), FARO Web (frontend Streamlit)

### Community 166 - "cargar"
Cohesion: 0.67
Nodes (3): cargar(), _dsn(), Path

### Community 168 - "3. Build y Push de Imagen Docker"
Cohesion: 0.67
Nodes (3): 3.1 Usando el script automatizado (Recomendado), 3.2 Comandos manuales (si el script falla), 3. Build y Push de Imagen Docker

### Community 169 - "4. Deploy a Cloud Run"
Cohesion: 0.67
Nodes (3): 4.1 Usando el script automatizado (Recomendado), 4.2 Comando manual, 4. Deploy a Cloud Run

### Community 170 - "6. Configuración de Seguridad"
Cohesion: 0.67
Nodes (3): 6.1 Límite de instancias (Ya configurado), 6.2 Alertas de presupuesto (Recomendado), 6. Configuración de Seguridad

### Community 171 - "7. Actualización del Servicio"
Cohesion: 0.67
Nodes (3): 7.1 Flujo completo de actualización, 7.2 Rollback a versión anterior, 7. Actualización del Servicio

## Knowledge Gaps
- **576 isolated node(s):** `build-and-push.sh script`, `deploy-cloud-run.sh script`, `chromadb-entrypoint.sh script`, `mlflow-entrypoint.sh script`, `superset-init.sh script` (+571 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **68 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `indice_riesgo()` connect `test_riesgo.py` to `ResultadoEntrenamiento`, `entrenar_ml01.py`, `publicar_gold.py`, `construir_predicciones_municipio_nivel`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `GoogleNotConfigured` connect `v1/auth.py` to `entrenar_ml02.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `Rol` connect `Rol` to `test_auth_jwt.py`, `test_api_contract.py`, `v1/auth.py`, `get_settings`, `schemas.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **What connects `build-and-push.sh script`, `deploy-cloud-run.sh script`, `chromadb-entrypoint.sh script` to the rest of the system?**
  _576 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `generate_pm_dashboard.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11702127659574468 - nodes in this community are weakly interconnected._
- **Should `CLAUDE.md — Contexto del proyecto para agentes de IA` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
- **Should `Data Model — Arquitectura Medallón FARO` be split into smaller, more focused modules?**
  _Cohesion score 0.07692307692307693 - nodes in this community are weakly interconnected._