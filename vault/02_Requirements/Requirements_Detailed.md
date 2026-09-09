---
id: DOC-REQ-DET
title: "Requisitos Detallados"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
version: "1.0"
source_of_truth: true
traces_up: ["vault/01_Product/PRD_General_Materia", "vault/01_Product/PRD"]
last_reviewed: "2026-09-08"
tags: [requirements, detailed, rubrica]
---

# Requisitos Detallados — FARO

> Un `REQ-###` por cada uno de los **7 módulos de la rúbrica** del profesor
> ([[vault/01_Product/PRD_General_Materia]] = QUÉ nos piden). Cada REQ indica **cómo lo resuelve FARO**
> ([[vault/01_Product/PRD]] = CÓMO). Cada criterio de aceptación `AC-###` es **verificable** (cumplido/no
> cumplido, sin discusión).
> → [[vault/02_Requirements/_index]] · [[vault/02_Requirements/Traceability_Matrix]]

---

### REQ-001 — Data Engineering y pipelines multi-fuente
- **Módulo de rúbrica:** 1 · **Peso:** 2.5 pts · **Tipo:** funcional · **Prioridad:** Must
- **Qué pide el profesor:** integración continua y automatizada de ≥5 fuentes distintas, arquitectura
  de almacenamiento en capas (tipo Medallón) limpia y funcional, con auditoría/validación de calidad
  explícita.
- **Cómo lo resuelve FARO:** ingiere las **8 fuentes DS-01 a DS-08**; **3 son de ingesta genuinamente
  continua** (DS-04 SESNSP mensual, DS-05 SINAICA horaria vía API, DS-06 CONAGUA diaria). Arquitectura
  **Bronze → Silver → Gold**: Bronze/Silver nacionales, Gold acotado a `SCOPE_ENTIDADES = ["09","15","19","14"]`.
  Llave primaria **DS-02 (CCT)** homologa todas las fuentes. Calidad con **Great Expectations**;
  cobertura parcial marcada como **`SIN_DATO`** (nunca cero, nunca nulo) e `indice_completitud_drivers`.
- **Criterios de aceptación:**
  - **AC-001.1** — Se ingieren ≥5 de las 8 fuentes DS-01…DS-08; el pipeline lista cada fuente con su
    conteo de registros tras una corrida.
  - **AC-001.2** — Al menos 3 fuentes se ejecutan de forma programada/automatizada (no manual):
    DS-04 mensual, DS-05 horaria, DS-06 diaria, orquestadas en Airflow (DAG visible).
  - **AC-001.3** — Cada tabla Bronze contiene los metadatos `_ingested_at`, `_source` y `_source_url`.
  - **AC-001.4** — Existen las tres capas Bronze, Silver y Gold; Gold es un esquema estrella con
    `fact_escuela_ciclo` + `dim_escuela`, `dim_municipio`, `dim_tiempo`, `dim_driver`.
  - **AC-001.5** — La suite de Great Expectations corre en Silver y pasa en verde (nulos, duplicados,
    tipos, límites físicos); su reporte (Data Docs) es accesible.
  - **AC-001.6** — Donde falta dato para un driver, el valor es `SIN_DATO` explícito; no hay ceros ni
    nulos silenciosos, y cada cubo expone su bandera de cobertura.
  - **AC-001.7** — Los scripts de ingesta son idempotentes: re-ejecutar no duplica filas.
- **User Stories:** US-101, US-102, US-103, US-104, US-105, US-111, US-112, US-113, US-121, US-122, US-123
- **Estado:** done — cierre técnico y administrativo; deuda residual declarada en [[vault/13_Reports/Cierre_Proyecto_2026-09-08]].

---

### REQ-002 — Frontend BI interactivo
- **Módulo de rúbrica:** 2 · **Peso:** 2.5 pts · **Tipo:** funcional · **Prioridad:** Must
- **Qué pide el profesor:** el §3.5 del PRD no pide sólo un dashboard: enumera **cinco componentes**
  del *Frontend & Business Intelligence Interactivo*, y **los cinco cargan sobre estos 2.5 puntos**.
  La redacción anterior de este requisito sólo describía el primero y el segundo, así que dos
  entregables reales del proyecto —el panel de ML y el chat— no tenían criterio de aceptación aquí
  aunque `US-207` y `US-305` ya trazaban a `REQ-002`. Ampliado el **2026-09-07**:

  | # | Componente que pide §3.5 | Dónde vive en FARO |
  |---|---|---|
  | 1 | KPIs globales en tiempo real | `AC-002.5` · KPI-01…KPI-18 en Superset y `/api/v1/kpis` |
  | 2 | Gráficos interactivos (series, distribución, **mapas si aplica**) | `AC-002.2`…`AC-002.4`, `AC-002.6` |
  | 3 | **Panel de Machine Learning** — *"el usuario ingresa parámetros y recibe predicciones de los 3 modelos"* | **`AC-002.7`** · `US-207` |
  | 4 | **Widget del Agente Conversacional** — *"ventana de chat flotante o dedicada"* | **`AC-002.8`** · `US-305` |
  | 5 | Módulo de Gestión de Usuarios/Auth — login, logout y vistas por rol | **`AC-002.9`** · `US-405` |

  **El §3.2 lo refuerza desde el otro lado:** los modelos deben estar *"expuestos vía API… integrándose
  en el Frontend/BI"*. El panel de ML **es** esa integración, así que sirve de evidencia a `REQ-002` y
  a `REQ-003` a la vez — no se cuenta dos veces en la rúbrica, pero se demuestra una sola vez.
- **Cómo lo resuelve FARO:** **10 dashboards DB-01 a DB-10 en Apache Superset** (no Power BI) sobre la
  capa Gold acotada a las 4 entidades, incluyendo el mapa de riesgo (DB-02), la ficha de escuela
  (DB-03), recomendaciones prescriptivas (DB-09) y el mapa de vacíos de datos (DB-07). **Más FARO Web**
  (`https://faro-frontend-eanzfglvyq-uc.a.run.app`, `US-526`), el shell de Streamlit que hospeda los
  tableros embebidos, el panel de ML y el chat del agente bajo una sola URL con sesión de Google.
- **Criterios de aceptación:**
  - **AC-002.1** — Existen los 10 dashboards DB-01…DB-10 desplegados en Superset y accesibles desde la
    URL pública.
  - **AC-002.2** — Hay filtros por **ciclo escolar, entidad y nivel educativo** y aplican al conjunto
    de dashboards, no a uno solo.
  - **AC-002.3** — DB-02 muestra un mapa (coroplético municipal + puntos de escuela) coloreado por
    índice de riesgo.
  - **AC-002.4** — DB-03 permite drill-down a una escuela por CCT y muestra su perfil, drivers,
    predicción y recomendación.
  - **AC-002.5** — Los dashboards muestran KPIs globales y al menos una serie de tiempo de matrícula.
  - **AC-002.6** — DB-07 visualiza `indice_completitud_drivers` y los territorios `SIN_DATO`.
  - **AC-002.7** — **Panel de ML interactivo**: el usuario elige una escuela por CCT —con búsqueda por
    filtros, no tecleando la clave— y recibe **predicción, driver dominante y recomendación** sin salir
    de la página. **Brecha declarada contra la letra del §3.5**, que pide *"los 3 modelos"*: el panel
    sirve **ML-01** (riesgo) y **ML-02** (driver dominante y recomendación) con datos reales; **ML-03
    no se sirve** porque su corrida quedó `bloqueada` con la política `casos_completos` —**D5 al 100 %
    `SIN_DATO` y D6 al 98.7 %**—, y entregar un clustering entrenado sobre dos columnas vacías sería
    inventar un resultado. Está registrado, medido y se dice en la demo antes de que lo pregunten;
    **no se maquilla como cumplido**. Ver `US-321`, `US-324` y el guion de `US-006`.
  - **AC-002.8** — **Widget del agente conversacional**: página de chat dedicada dentro de FARO Web que
    consulta `/api/v1/agente/consulta` con la sesión del usuario, **muestra el SQL generado** —la
    respuesta es auditable, no una opinión— y **rechaza** las preguntas fuera de alcance y las
    destructivas con los guardarraíles reales. Ver `US-305`, `US-304a/b`, `US-323` y `REQ-006`, donde
    vive el peso propio del agente.
  - **AC-002.9** — **Gestión de usuarios y vistas por rol**: login y logout con Google en las cuatro
    páginas de FARO Web, sesión que **sobrevive a la recarga** y refresco automático del access token
    antes de que expire (`BUG-059`), con **403 demostrable en vivo** para una cuenta `ciudadano` sobre
    una ruta de `analista`. Ver `US-405`, `US-403` y `AC-004.5`.
- **User Stories:** US-201, US-202, US-203, US-204, US-205, US-207, US-211, US-212, US-213, US-214, US-221, US-222, US-223, US-305, US-405, US-526
- **Estado:** done — cierre administrativo con salvedades visuales y sin ML-03 en el panel; ver [[vault/13_Reports/Cierre_Proyecto_2026-09-08]].

---

### REQ-003 — Tres modelos de ML integrados vía API
- **Módulo de rúbrica:** 3 · **Peso:** 1.5 pts · **Tipo:** funcional · **Prioridad:** Must
- **Qué pide el profesor:** ≥3 modelos de ML distintos, bien justificados, entrenados e integrados a
  la API/Frontend para inferencias en tiempo real o batch.
- **Cómo lo resuelve FARO:** **ML-01** regresión (variación de matrícula por escuela, MAE/RMSE),
  **ML-02** clasificación multiclase del **driver dominante** con explicabilidad **SHAP** (corazón
  prescriptivo), **ML-03** clustering de perfiles de escuela (Silhouette). Registro en **MLflow** y
  **validación con partición temporal, nunca aleatoria**.
- **Criterios de aceptación:**
  - **AC-003.1** — Existen 3 modelos distintos: uno de regresión (ML-01), uno de clasificación
    multiclase (ML-02) y uno de clustering (ML-03).
  - **AC-003.2** — Cada modelo reporta su métrica: ML-01 MAE/RMSE, ML-02 F1 macro/accuracy, ML-03
    Silhouette, documentadas y reproducibles.
  - **AC-003.3** — La validación de ML-01 y ML-02 usa partición **temporal** (entrena en ciclos
    previos, valida en el siguiente); no hay split aleatorio.
  - **AC-003.4** — Los 3 modelos están registrados en MLflow con versión.
  - **AC-003.5** — Cada modelo se consume por un endpoint de la API que devuelve predicción dado un
    CCT o un conjunto de features.
  - **AC-003.6** — ML-02 devuelve, además de la clase, la atribución del driver dominante (SHAP) por
    escuela, y dos escuelas con igual riesgo pero distinto driver reciben recomendaciones distintas.
- **User Stories:** US-301, US-302, US-303, US-311, US-312, US-313, US-321, US-322
- **Estado:** done — cierre administrativo; cumplimiento externo parcial porque ML-03 no fue promovido a Gold/API/UI. La brecha se conserva en [[vault/13_Reports/Cierre_Proyecto_2026-09-08]].

---

### REQ-004 — Backend, API y autenticación avanzada
- **Módulo de rúbrica:** 4 · **Peso:** 1.5 pts · **Tipo:** funcional · **Prioridad:** Must
- **Qué pide el profesor:** API robusta y parametrizada con autenticación avanzada (OAuth2/JWT) y
  autorización por roles (RBAC) con al menos 2 roles, funcionando en vistas protegidas.
- **Cómo lo resuelve FARO:** **FastAPI** con **OAuth2/JWT** (access + refresh tokens) y **RBAC de 2
  roles**: *ciudadano/estándar* (solo dashboards públicos y agente) y *analista/admin* (ejecuta
  pipelines, endpoints ML avanzados y exportación). Contrato OpenAPI publicado en Semana 1; validación
  de entradas con Pydantic sin filtrar detalles internos en errores.
- **Criterios de aceptación:**
  - **AC-004.1** — La API expone un contrato OpenAPI navegable (`/docs`).
  - **AC-004.2** — El login emite **access token y refresh token** JWT; un access token expirado se
    renueva con el refresh token.
  - **AC-004.3** — Existen exactamente ≥2 roles (estándar y analista/admin) y están documentados.
  - **AC-004.4** — Un endpoint protegido rechaza (401/403) a un usuario sin token o con rol
    insuficiente, y responde 200 al rol autorizado.
  - **AC-004.5** — El rol estándar NO puede ejecutar pipelines ni exportar datos en bruto; el rol
    analista/admin SÍ.
  - **AC-004.6** — Las entradas se validan con Pydantic; un payload inválido devuelve 422 sin exponer
    trazas internas.
- **User Stories:** US-401, US-402, US-403, US-404, US-411, US-412, US-413, US-421, US-422, US-423
- **Estado:** done — autenticación, autorización y contrato verificados; riesgos residuales aceptados en [[vault/13_Reports/Cierre_Proyecto_2026-09-08]].

---

### REQ-005 — Despliegue en GCP dockerizado con URL pública
- **Módulo de rúbrica:** 5 · **Peso:** 1.0 pt · **Tipo:** no-funcional · **Prioridad:** Must
- **Qué pide el profesor:** todos los servicios en contenedores Docker, desplegados en AWS o GCP en
  una URL pública totalmente funcional. Sin URL pública funcional al evaluar, la nota máxima es 6.0.
- **Cómo lo resuelve FARO:** todo el ecosistema (Frontend/Superset, Backend/FastAPI, DB, ML/Agente,
  Pipeline) **dockerizado** con docker-compose y desplegado en **GCP Cloud Run + Cloud SQL + Artifact
  Registry**. Deploy "hola mundo" en Semana 1 para asegurar la URL desde el inicio.
- **Criterios de aceptación:**
  - **AC-005.1** — Existe una **URL pública** accesible que sirve la plataforma sin túneles ni
    localhost.
  - **AC-005.2** — Todos los servicios corren en contenedores Docker (existen sus imágenes /
    `docker-compose.yml`).
  - **AC-005.3** — El despliegue está en **GCP** (Cloud Run para servicios, Cloud SQL para la base,
    Artifact Registry para imágenes).
  - **AC-005.4** — La URL pública está viva y estable durante la ventana de evaluación (demo 9-sep).
  - **AC-005.5** — Los secretos no están en el repo; se inyectan por configuración/gestor de secretos.
- **User Stories:** US-501, US-502, US-503, US-504, US-505, US-521, US-522, US-523, US-524, US-525
- **Estado:** done — despliegue final verificado; deuda operativa aceptada en [[vault/13_Reports/Cierre_Proyecto_2026-09-08]].

---

### REQ-006 — Agente conversacional
- **Módulo de rúbrica:** 6 · **Peso:** 0.5 pts · **Tipo:** funcional · **Prioridad:** Should
- **Qué pide el profesor:** agente funcional integrado en la UI que responde preguntas de negocio
  usando los datos consolidados, mediante lenguaje natural.
- **Cómo lo resuelve FARO:** agente **RAG / Text-to-SQL** (ChromaDB + sentence-transformers) integrado
  como widget en la interfaz, que responde sobre la capa Gold y las métricas calculadas, con un set de
  evaluación propio. Nunca ejecuta `DELETE`/`UPDATE`/`DROP`.
- **Criterios de aceptación:**
  - **AC-006.1** — Hay un widget de chat accesible dentro de la UI web.
  - **AC-006.2** — El agente responde preguntas de negocio sobre los datos (p. ej. "¿qué municipio tuvo
    mayor riesgo el ciclo pasado?", "dame la predicción de la escuela X") usando los datos del sistema,
    no respuestas genéricas desconectadas.
  - **AC-006.3** — Existe un set de evaluación con preguntas esperadas y el agente acierta en un umbral
    documentado.
  - **AC-006.4** — El agente no ejecuta sentencias de escritura/borrado (`DELETE`/`UPDATE`/`DROP`).
- **User Stories:** US-304, US-323
- **Estado:** done — agente desplegado y funcional en modo single-turn; residual documentado en [[vault/13_Reports/Cierre_Proyecto_2026-09-08]].

---

### REQ-007 — Trabajo en equipo, Git y documentación
- **Módulo de rúbrica:** 7 · **Peso:** 0.5 pts · **Tipo:** no-funcional · **Prioridad:** Must
- **Qué pide el profesor:** commits distribuidos equitativamente entre los integrantes, README
  impecable, diagramas claros y entrega organizada.
- **Cómo lo resuelve FARO:** gobernanza por **vault** (Vault_Rules, Naming_Conventions, Definition of
  Filed), un **plan individual por cada uno de los 21 integrantes**, PR obligatorio (nada de push a
  `main`), Conventional Commits con ID de historia, **DevLog por sesión de IA** y `vault_lint.py` como
  gate.
- **Criterios de aceptación:**
  - **AC-007.1** — Los 21 integrantes tienen commits en el repositorio (contribución distribuida, no
    concentrada en pocas personas).
  - **AC-007.2** — Existe un README con instrucciones de ejecución local y arquitectura.
  - **AC-007.3** — Existe un diagrama de arquitectura que muestra el flujo Fuentes → Almacenamiento →
    API → ML → BI/Agente.
  - **AC-007.4** — Todo cambio entró por PR (0 commits directos a `main`); los commits siguen
    Conventional Commits con el ID de la historia.
  - **AC-007.5** — Cada sesión con IA tiene su entrada de DevLog y `vault_lint.py` corre en verde.
- **User Stories:** US-001, US-002, US-003, US-004, US-005, US-006
- **Estado:** in_progress — sólo falta ejecutar la demo/entrega (`US-006`) el 9-sep; el resto queda cerrado por `DEC-021`.

---

## Resumen

| REQ | Módulo de rúbrica | Puntos | # AC |
|---|---|---|---|
| REQ-001 | Data Engineering y pipelines multi-fuente | 2.5 | 7 |
| REQ-002 | Frontend BI interactivo | 2.5 | 9 |
| REQ-003 | Tres modelos de ML integrados vía API | 1.5 | 6 |
| REQ-004 | Backend, API y autenticación avanzada | 1.5 | 6 |
| REQ-005 | Despliegue en GCP dockerizado con URL pública | 1.0 | 5 |
| REQ-006 | Agente conversacional | 0.5 | 4 |
| REQ-007 | Trabajo en equipo, Git y documentación | 0.5 | 5 |
| **Total** | **7 módulos** | **10.0** | **42** |
