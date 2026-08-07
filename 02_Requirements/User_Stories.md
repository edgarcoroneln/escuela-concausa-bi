---
id: US-CATALOG
title: "Catálogo de User Stories — FARO"
owner: "Edgar Edmundo Coronel Navarrete"
status: in_review
version: "1.1"
source_of_truth: true
traces_up: ["02_Requirements/Requirements_Detailed"]
tags: [requirements, user-stories, catalogo]
---

# Catálogo de User Stories — FARO

> **Catálogo único** de todas las historias del proyecto (no hay un archivo por historia).
> Fuente: los 21 planes individuales de [[12_Roadmap_Sprints/Sprints/_index]].
> Cada `US-###` mapea al `REQ-###` que satisface (ver [[02_Requirements/Requirements_Detailed]]).
> → [[02_Requirements/_index]]

**91 historias únicas · 91 asignaciones** (1 responsable por historia). Las historias que antes
compartían ID entre varias personas se **partieron con sufijo de letra** (a/b/c), dando a cada quien un
alcance distinto y verificable. Sprints S1–S6 (3 ago → 8 sep 2026).

---

## Célula 0 · PO — Dirección de Proyecto

| ID | Historia | Responsable | Nivel | Sprint | REQ |
|---|---|---|---|---|---|
| US-001 | Crear el repositorio nuevo y adaptar el vault | Edgar Edmundo Coronel Navarrete | Medio | S1 | REQ-007 |
| US-002 | Cargar el PRD del profesor con criterios de aceptación | Edgar Edmundo Coronel Navarrete | Medio | S1 | REQ-007 |
| US-003 | Registrar a los 21 integrantes y crear sus Agent Contexts | Edgar Edmundo Coronel Navarrete | Medio | S1 | REQ-007 |
| US-004 | Sembrar y mantener la Traceability_Matrix | Edgar Edmundo Coronel Navarrete | Medio | S2 | REQ-007 |
| US-005 | Coordinar la rotación del Vault Steward | Edgar Edmundo Coronel Navarrete | Medio | S4 | REQ-007 |
| US-006 | Preparar y ensayar el pitch de la demo en vivo | Edgar Edmundo Coronel Navarrete | Medio | S6 | REQ-007 |

---

## Célula 1 · Data Engineering & Quality

> US-121…124 partidas **por fuente**: Emilio (DS-06, DS-08) vs Luis Enrique (DS-04, DS-05).

| ID | Historia | Responsable | Nivel | Sprint | REQ |
|---|---|---|---|---|---|
| US-101 | Diseñar el modelo de datos medallón completo | Diana Aracely Alvarez Varela | Alto | S1 | REQ-001 |
| US-102 | Construir el DAG maestro de orquestación en Airflow | Diana Aracely Alvarez Varela | Alto | S2 | REQ-001 |
| US-103 | Modelar la capa GOLD como esquema estrella | Diana Aracely Alvarez Varela | Alto | S3 | REQ-001 |
| US-104 | Definir e implementar la tabla de features para ML | Diana Aracely Alvarez Varela | Alto | S3 | REQ-001 |
| US-105 | Implementar la estrategia de cobertura parcial e índice de confianza | Diana Aracely Alvarez Varela | Alto | S3 | REQ-001 |
| US-106 | Congelar esquema y documentar linaje completo | Diana Aracely Alvarez Varela | Alto | S5 | REQ-001 |
| US-111 | Implementar transformaciones Bronze → Silver con dbt | Deni Garrido Fragoso | Medio | S2 | REQ-001 |
| US-112 | Implementar transformaciones Silver → Gold con dbt | Deni Garrido Fragoso | Medio | S3 | REQ-001 |
| US-113 | Construir los cubos de agregación | Deni Garrido Fragoso | Medio | S3 | REQ-001 |
| US-114 | Optimizar consultas y crear índices | Deni Garrido Fragoso | Medio | S5 | REQ-001 |
| US-121a | Prueba de descarga real de DS-06 (CONAGUA) y DS-08 (CONAPO) | Emilio Galnares Ruiz | Bajo | S1 | REQ-001 |
| US-122a | Escribir los extractores de DS-06 y DS-08 | Emilio Galnares Ruiz | Bajo | S2 | REQ-001 |
| US-123a | Validaciones Great Expectations de DS-06 y DS-08 | Emilio Galnares Ruiz | Bajo | S3 | REQ-001 |
| US-124a | Fixtures de prueba anonimizados de DS-06 y DS-08 | Emilio Galnares Ruiz | Bajo | S4 | REQ-001 |
| US-121b | Prueba de descarga real de DS-04 (SESNSP) y DS-05 (SINAICA) | Luis Enrique García Vázquez | Bajo | S1 | REQ-001 |
| US-122b | Escribir los extractores de DS-04 y DS-05 | Luis Enrique García Vázquez | Bajo | S2 | REQ-001 |
| US-123b | Validaciones Great Expectations de DS-04 y DS-05 | Luis Enrique García Vázquez | Bajo | S3 | REQ-001 |
| US-124b | Fixtures de prueba anonimizados de DS-04 y DS-05 | Luis Enrique García Vázquez | Bajo | S4 | REQ-001 |

---

## Célula 2 · Analytics & Business Intelligence

> US-211/214/215 partidas **por dashboard**: Marina (DB-03, DB-04) vs Monserrat (DB-05, DB-08).
> US-212 (DB-03/04) queda solo para Marina; US-213 (DB-05/08) solo para Monserrat.

| ID | Historia | Responsable | Nivel | Sprint | REQ |
|---|---|---|---|---|---|
| US-201 | Diseñar el portafolio de 10 dashboards y el catálogo de KPIs | Manuel Alejandro Serranía Reinada | Alto | S1 | REQ-002 |
| US-202 | Configurar Superset: conexión, datasets y capa semántica | Manuel Alejandro Serranía Reinada | Alto | S3 | REQ-002 |
| US-203 | Construir DB-01 Ejecutivo y DB-02 Mapa de riesgo territorial | Manuel Alejandro Serranía Reinada | Alto | S4 | REQ-002 |
| US-204 | Construir DB-06 Predicciones y DB-09 Recomendaciones prescriptivas | Manuel Alejandro Serranía Reinada | Alto | S4 | REQ-002 |
| US-205 | Integrar y armonizar los 10 dashboards | Manuel Alejandro Serranía Reinada | Alto | S5 | REQ-002 |
| US-211a | Modelar métricas y jerarquías de los cubos de DB-03 y DB-04 | Marina García del Buey | Medio | S3 | REQ-002 |
| US-212 | Construir DB-03 Ficha de escuela y DB-04 Comparador de municipios | Marina García del Buey | Medio | S4 | REQ-002 |
| US-214a | Filtros dinámicos y drill-down en DB-03 y DB-04 | Marina García del Buey | Medio | S5 | REQ-002 |
| US-215a | Pruebas de usabilidad y accesibilidad de DB-03 y DB-04 | Marina García del Buey | Medio | S5 | REQ-002 |
| US-211b | Modelar métricas y jerarquías de los cubos de DB-05 y DB-08 | Monserrat Xcaret Miranda Olivas | Medio | S3 | REQ-002 |
| US-213 | Construir DB-05 Análisis por driver y DB-08 Explorador del cubo | Monserrat Xcaret Miranda Olivas | Medio | S4 | REQ-002 |
| US-214b | Filtros dinámicos y drill-down en DB-05 y DB-08 | Monserrat Xcaret Miranda Olivas | Medio | S5 | REQ-002 |
| US-215b | Pruebas de usabilidad y accesibilidad de DB-05 y DB-08 | Monserrat Xcaret Miranda Olivas | Medio | S5 | REQ-002 |
| US-221 | Construir los gráficos base de KPIs | Oscar Antonio Quiroz Lázaro | Bajo | S3 | REQ-002 |
| US-222 | Construir DB-07 Calidad y cobertura de datos | Oscar Antonio Quiroz Lázaro | Bajo | S4 | REQ-002 |
| US-223 | Construir DB-10 Monitor del pipeline | Oscar Antonio Quiroz Lázaro | Bajo | S5 | REQ-002 |
| US-224 | Documentar el manual de usuario de los dashboards | Oscar Antonio Quiroz Lázaro | Bajo | S5 | REQ-002 |
| US-206 | Construir FARO Web: shell, navegación y embebido de los 10 dashboards | Manuel Alejandro Serranía Reinada | Alto | S4 | REQ-002 |
| US-207 | Construir FARO Web: panel de ML interactivo (parámetros → inferencia de los 3 modelos) | Marina García del Buey | Medio | S5 | REQ-002 |

---

## Célula 3 · Machine Learning & Agente IA

> US-304 partida en diseño (Andrés) + recuperación (Carlos). Célula rebalanceada a 3 historias por
> perfil Bajo: Estefany (clustering, features, sesgo) y Carlos (recuperación, evaluación, model cards).

| ID | Historia | Responsable | Nivel | Sprint | REQ |
|---|---|---|---|---|---|
| US-301 | Diseñar la estrategia de modelado y el protocolo de validación | Andrés González Habib | Alto | S3 | REQ-003 |
| US-302 | Entrenar el Modelo 2 — Clasificación de driver dominante | Andrés González Habib | Alto | S4 | REQ-003 |
| US-303 | Registrar los 3 modelos en MLflow y exponerlos vía API | Andrés González Habib | Alto | S4 | REQ-003 |
| US-304a | Diseño del agente: prompt del sistema y guardarraíles de seguridad | Andrés González Habib | Alto | S5 | REQ-006 |
| US-311 | Entrenar el Modelo 1 — Regresión de matrícula | Héctor Rafael Morales Marbán | Medio | S4 | REQ-003 |
| US-312 | Evaluar modelos y documentar métricas | Héctor Rafael Morales Marbán | Medio | S5 | REQ-003 |
| US-313 | Integrar predicciones y recomendaciones a Gold | Héctor Rafael Morales Marbán | Medio | S5 | REQ-003 |
| US-321 | Entrenar el Modelo 3 — Clustering de escuelas | Estefany Lucero Hernández Loredo | Bajo | S4 | REQ-003 |
| US-322 | Análisis exploratorio y selección de variables | Estefany Lucero Hernández Loredo | Bajo | S4 | REQ-003 |
| US-325 | Analizar el sesgo por cobertura parcial en las features | Estefany Lucero Hernández Loredo | Bajo | S4 | REQ-003 |
| US-304b | Construir la capa de recuperación del agente (RAG: ChromaDB + embeddings) | Carlos Guillermo Mayorga Tapia | Bajo | S5 | REQ-006 |
| US-323 | Construir el set de evaluación del agente | Carlos Guillermo Mayorga Tapia | Bajo | S5 | REQ-006 |
| US-324 | Documentar las fichas de modelo (model cards) de ML-01, ML-02 y ML-03 | Carlos Guillermo Mayorga Tapia | Bajo | S5 | REQ-003 |
| US-305 | Integrar FARO Web: widget de chat del agente (RAG) | Andrés González Habib | Alto | S5 | REQ-006 |

---

## Célula 4 · Backend, API & Seguridad

| ID | Historia | Responsable | Nivel | Sprint | REQ |
|---|---|---|---|---|---|
| US-401 | Definir y publicar el contrato de la API (OpenAPI) | Christian Imanol Ruiz Hurtado | Alto | S1 | REQ-004 |
| US-402 | Implementar OAuth2 + JWT con refresh/access tokens | Christian Imanol Ruiz Hurtado | Alto | S4 | REQ-004 |
| US-403 | Implementar RBAC con los 2 roles del PRD | Christian Imanol Ruiz Hurtado | Alto | S4 | REQ-004 |
| US-404 | Hardening de la API | Christian Imanol Ruiz Hurtado | Alto | S5 | REQ-004 |
| US-411 | Implementar los endpoints de datos sobre Gold | Karla Alejandra Monter Benitez | Medio | S3 | REQ-004 |
| US-412 | Implementar los endpoints de inferencia ML | Juan Carlos Macías Mayen | Medio | S4 | REQ-004 ᵃ |
| US-413 | Endpoints administrativos protegidos | Karla Alejandra Monter Benitez | Medio | S5 | REQ-004 |
| US-414 | Documentar la API en OpenAPI y publicar la colección | Karla Alejandra Monter Benitez | Medio | S5 | REQ-004 |
| US-415 | Implementar el contrato de datos entre API y modelos | Juan Carlos Macías Mayen | Medio | S4 | REQ-004 ᵃ |
| US-416 | Implementar cache y manejo de errores de inferencia | Juan Carlos Macías Mayen | Medio | S5 | REQ-004 ᵃ |
| US-421 | Implementar el esqueleto de FastAPI y healthcheck | Eloisa González Rubio | Bajo | S3 | REQ-004 |
| US-422 | Escribir pruebas unitarias y de integración de la API | Eloisa González Rubio | Bajo | S4 | REQ-004 |
| US-423 | Pruebas de seguridad de la autenticación | Eloisa González Rubio | Bajo | S5 | REQ-004 |
| US-405 | Construir FARO Web: login/logout y vistas protegidas por rol | Christian Imanol Ruiz Hurtado | Alto | S4 | REQ-004 |

ᵃ El endpoint ML (US-412, US-415, US-416) vive en la Célula 4 (REQ-004) pero **también sostiene** el
requisito de "3 modelos integrados vía API" (REQ-003).

---

## Célula 5 · Cloud Infrastructure & DevOps

> US-521…525 partidas **por servicio**: Alejandro (API + Postgres), Edgar Ulises (Airflow + jobs ML),
> Edward (Superset + agente).

| ID | Historia | Responsable | Nivel | Sprint | REQ |
|---|---|---|---|---|---|
| US-501 | Desplegar el 'hola mundo' en GCP con URL pública | Luis Téllez Domínguez | Medio | S1 | REQ-005 |
| US-502 | Diseñar el docker-compose completo del ecosistema | Luis Téllez Domínguez | Medio | S2 | REQ-005 |
| US-503 | Configurar el pipeline de CI en GitHub Actions | Luis Téllez Domínguez | Medio | S2 | REQ-007 ᵇ |
| US-504 | Aprovisionar Cloud SQL, Artifact Registry y secretos | Luis Téllez Domínguez | Medio | S4 | REQ-005 |
| US-505 | Despliegue final productivo y verificación | Luis Téllez Domínguez | Medio | S6 | REQ-005 |
| US-521a | Guía de ambiente local reproducible — API y Postgres | Alejandro Velázquez Mendoza | Bajo | S1 | REQ-007 ᵇ |
| US-522a | Contenerizar API (FastAPI) y Postgres | Alejandro Velázquez Mendoza | Bajo | S3 | REQ-005 |
| US-523a | Branch protection y required reviews en GitHub | Alejandro Velázquez Mendoza | Bajo | S3 | REQ-007 ᵇ |
| US-524a | Monitoreo, logs y alertas de API y Postgres | Alejandro Velázquez Mendoza | Bajo | S5 | REQ-005 |
| US-525a | Runbook de rollback de API y Postgres | Alejandro Velázquez Mendoza | Bajo | S6 | REQ-005 |
| US-521b | Guía de ambiente local reproducible — Airflow y jobs ML | Edgar Ulises Jiménez López | Bajo | S1 | REQ-007 ᵇ |
| US-522b | Contenerizar Airflow y los jobs de ML | Edgar Ulises Jiménez López | Bajo | S3 | REQ-005 |
| US-523b | Quality gate de CI: lint y pruebas | Edgar Ulises Jiménez López | Bajo | S3 | REQ-007 ᵇ |
| US-524b | Monitoreo, logs y alertas de Airflow y jobs ML | Edgar Ulises Jiménez López | Bajo | S5 | REQ-005 |
| US-525b | Runbook de rollback de Airflow y jobs ML | Edgar Ulises Jiménez López | Bajo | S6 | REQ-005 |
| US-521c | Guía de ambiente local reproducible — Superset y agente | Edward Ulysses Ruiz Bustillos | Bajo | S1 | REQ-007 ᵇ |
| US-522c | Contenerizar Superset y el agente | Edward Ulysses Ruiz Bustillos | Bajo | S3 | REQ-005 |
| US-523c | Quality gate de vault_lint y plantilla de PR | Edward Ulysses Ruiz Bustillos | Bajo | S3 | REQ-007 ᵇ |
| US-524c | Monitoreo, logs y alertas de Superset y agente | Edward Ulysses Ruiz Bustillos | Bajo | S5 | REQ-005 |
| US-525c | Runbook de rollback de Superset y agente | Edward Ulysses Ruiz Bustillos | Bajo | S6 | REQ-005 |

ᵇ Historias ejecutadas por la Célula 5 pero cuyo **valor de rúbrica** cae en gobernanza / Git /
documentación (REQ-007): CI, branch protection, quality gates y guía de ambiente local.

---

## Resumen A · Historias por sprint

| Sprint | Fechas | # historias |
|---|---|---|
| S1 | Lun 3 – Dom 9 ago | 12 |
| S2 | Lun 10 – Dom 16 ago | 7 |
| S3 | Lun 17 – Dom 23 ago | 20 |
| S4 | Lun 24 – Dom 30 ago | 22 |
| S5 | Lun 31 ago – Dom 6 sep | 25 |
| S6 | Lun 7 – Mar 8 sep | 5 |
| **Total** | | **91** |

---

## Resumen B · Historias por REQ (cobertura de la rúbrica)

| REQ | Módulo de rúbrica | Puntos | # historias | Cubierto |
|---|---|---|---|---|
| REQ-001 | Data Engineering y pipelines multi-fuente | 2.5 | 18 | ✅ |
| REQ-002 | Frontend BI interactivo | 2.5 | 19 | ✅ |
| REQ-003 | Tres modelos de ML integrados vía API | 1.5 | 10 (+3 de apoyo ᵃ) | ✅ |
| REQ-004 | Backend, API y autenticación avanzada | 1.5 | 14 | ✅ |
| REQ-005 | Despliegue en GCP dockerizado con URL pública | 1.0 | 13 | ✅ |
| REQ-006 | Agente conversacional | 0.5 | 4 | ✅ |
| REQ-007 | Trabajo en equipo, Git y documentación | 0.5 | 13 | ✅ |
| **Total** | | **10.0** | **91** | **7/7** |

**Ningún REQ quedó sin historias.** Los 7 módulos de la rúbrica tienen cobertura.

---

## Resumen C · Historias por persona (IDs)

> Tras la partición y el rebalanceo de la Célula 3: **87 historias únicas = 87 asignaciones**
> (1 responsable por historia).

| Persona | Célula | Nivel | # | IDs |
|---|---|---|---|---|
| Edgar Edmundo Coronel Navarrete | PO | Medio | 6 | US-001…US-006 |
| Diana Aracely Alvarez Varela | C1 | Alto | 6 | US-101…US-106 |
| Deni Garrido Fragoso | C1 | Medio | 4 | US-111, US-112, US-113, US-114 |
| Emilio Galnares Ruiz | C1 | Bajo | 4 | US-121a, US-122a, US-123a, US-124a |
| Luis Enrique García Vázquez | C1 | Bajo | 4 | US-121b, US-122b, US-123b, US-124b |
| Manuel Alejandro Serranía Reinada | C2 | Alto | 6 | US-201…US-205, US-206 |
| Marina García del Buey | C2 | Medio | 5 | US-211a, US-212, US-214a, US-215a, US-207 |
| Monserrat Xcaret Miranda Olivas | C2 | Medio | 4 | US-211b, US-213, US-214b, US-215b |
| Eloisa González Rubio | C4 | Bajo | 3 | US-421, US-422, US-423 |
| Andrés González Habib | C3 | Alto | 5 | US-301, US-302, US-303, US-304a, US-305 |
| Héctor Rafael Morales Marbán | C3 | Medio | 3 | US-311, US-312, US-313 |
| Estefany Lucero Hernández Loredo | C3 | Bajo | 3 | US-321, US-322, US-325 |
| Carlos Guillermo Mayorga Tapia | C3 | Bajo | 3 | US-304b, US-323, US-324 |
| Karla Alejandra Monter Benitez | C4 | Medio | 3 | US-411, US-413, US-414 |
| Christian Imanol Ruiz Hurtado | C4 | Alto | 5 | US-401, US-402, US-403, US-404, US-405 |
| Juan Carlos Macías Mayen | C4 | Medio | 3 | US-412, US-415, US-416 |
| Oscar Antonio Quiroz Lázaro | C2 | Bajo | 4 | US-221, US-222, US-223, US-224 |
| Luis Téllez Domínguez | C5 | Medio | 5 | US-501…US-505 |
| Alejandro Velázquez Mendoza | C5 | Bajo | 5 | US-521a, US-522a, US-523a, US-524a, US-525a |
| Edgar Ulises Jiménez López | C5 | Bajo | 5 | US-521b, US-522b, US-523b, US-524b, US-525b |
| Edward Ulysses Ruiz Bustillos | C5 | Bajo | 5 | US-521c, US-522c, US-523c, US-524c, US-525c |
| **Total** | | | **91** | |

> **Célula 3 rebalanceada:** al partir US-304 (diseño → Andrés / recuperación → Carlos) y añadir
> US-325 (Estefany) y US-324 (Carlos), Estefany y Carlos quedan con **3 historias cada uno**, en línea
> con el resto de perfiles Bajo, sin quitarle alcance real a Andrés.
