---
id: PLAN-MAESTRO
title: "Plan Maestro del Proyecto FARO"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
version: "1.3"
source_of_truth: true
traces_up: ["01_Product/PRD"]
last_reviewed: "2026-08-06"
delivery_date: "2026-09-09"
delivery_label: "Demo en vivo y entrega final"
delivery_timezone: "America/Mexico_City"
tags: [roadmap, plan, sprints]
---

# FARO — Escuela como Sensor Social
## Plan Maestro de Proyecto · Inteligencia de Negocios · MTIIA Anáhuac

> **Repositorio sugerido:** `escuela-concausa-bi`
> **Equipo:** 21 integrantes en 5 células + PO
> **Ventana:** lunes 3 de agosto → **demo en vivo miércoles 9 de septiembre de 2026**
> **Profesor:** Dr. José Gustavo Fuentes

---

## 1. Qué construimos

Una **plataforma de datos end-to-end** que usa la escuela como unidad de observación multidimensional
del territorio. En vez de estudiar educación de forma aislada, cruzamos matrícula escolar con pobreza,
inseguridad, agua y calidad del aire para responder dos preguntas:

1. **¿Qué escuelas van a perder matrícula el próximo ciclo?**
2. **¿Cuál de los seis drivers lo explica en cada caso?**

El diferenciador frente a cualquier dashboard educativo: dos escuelas con el mismo nivel de riesgo
reciben **recomendaciones distintas**, según el driver que domina en cada una. Eso convierte el
proyecto de descriptivo a **prescriptivo**.

**Valor social:** dirigir la intervención correcta a cada escuela (transporte, comedor, conectividad,
agua o seguridad) en lugar de aplicar la misma beca a todas.

**Privacidad por diseño:** la estadística del Formato 911 tiene como unidad de observación la escuela
y no capta datos individualizados de alumnos ni maestros. Todo el proyecto opera a nivel agregado.

---

## 2. Fuentes de datos — confirmadas y verificadas

| ID | Fuente | Qué aporta | Frecuencia | Formato | Cobertura |
|---|---|---|---|---|---|
| `DS-01` | SEP · Formato 911 (SIGED / datos.gob.mx) | Matricula, docentes y grupos por CCT | **Anual (ciclo escolar)** | CSV/XLSX | Nacional |
| `DS-02` | SEP · Catalogo CCT | Identidad y georreferencia de cada escuela | **Continua** | CSV | Nacional |
| `DS-03` | SEP · CEMABE | Infraestructura por escuela: agua, drenaje, electricidad, sanitarios, internet | **Censo 2013** | CSV | Nacional |
| `DS-04` | SESNSP · Incidencia delictiva municipal | Delitos y victimas por municipio | **MENSUAL (dia 20)** | CSV | Nacional |
| `DS-05` | SINAICA / INECC · Calidad del aire | Contaminantes por estacion | **HORARIA (API JSON)** | API REST | ~80 zonas urbanas |
| `DS-06` | CONAGUA · SINA | Disponibilidad hidrica y presas | **DIARIA** | CSV/API | Regional |
| `DS-07` | CONEVAL · Rezago social y pobreza municipal | Contexto socioeconomico | **Bienal/quinquenal** | XLSX | Nacional |
| `DS-08` | CONAPO · Proyecciones de poblacion | Denominador para tasas y normalizacion | **Anual** | CSV | Nacional |

- **`DS-01`** — Serie desde 1990-91. Unidad de observacion = ESCUELA, no alumnos. Es el hecho central.
- **`DS-02`** — LLAVE PRIMARIA del proyecto. Une todas las fuentes.
- **`DS-03`** — Joya escondida: datos A NIVEL ESCUELA. Alimenta los drivers D3 y D4.
- **`DS-04`** — Ingesta continua #1.
- **`DS-05`** — Ingesta continua #2. COBERTURA PARCIAL - ver estrategia de cobertura.
- **`DS-06`** — Ingesta continua #3.
- **`DS-07`** — Dimension de contexto y validación.
- **`DS-08`** — Permite comparar municipios de distinto tamano.

**Cumplimiento del PRD:** son **7 fuentes distintas** (el mínimo exigido es 5), de las cuales **3 son de
ingesta genuinamente continua** (SINAICA horaria, CONAGUA diaria, SESNSP mensual). Esto es lo que hace
demostrable el requisito más caro de la rúbrica.

> **Tarea crítica de la Semana 1:** cada fuente debe pasar la **prueba de descarga real** — bajar el
> archivo, abrirlo, contar registros. No basta con leer la página del portal. Si una fuente falla, se
> sustituye en la semana 1, no en la 5.


---

## 2.bis Alcance del proyecto — decisión de diseño

**Bronze y Silver: nacionales.** **Gold, modelos y dashboards: 4 entidades** vía parámetro de configuración.

```python
SCOPE_ENTIDADES = ["09", "15", "19", "14"]   # CDMX · Edomex · Nuevo León · Jalisco
```

El sistema es nacional por diseño; se acota por **cobertura de datos**, no por capacidad. Ampliar a 32
entidades es cambiar una línea de configuración — y eso se demuestra en vivo ante el profesor.

### Estrategia de cobertura parcial

No todas las fuentes cubren todo el país. En lugar de ocultarlo, **lo convertimos en un hallazgo**:

- **SINAICA** solo tiene estaciones en ~80 zonas urbanas. Se interpola por distancia (IDW) dentro de un
  radio válido y **fuera de ese radio se marca `SIN_DATO` explícito** — nunca cero ni nulo silencioso.
- Cada cubo expone una **bandera de cobertura**, de modo que al filtrar un municipio sin dato el tablero
  dice *"sin información disponible para cruzar"* en vez de mostrar un hueco engañoso.
- Se calcula un **`indice_completitud_drivers`** por escuela y municipio. El tablero **DB-07** mapea los
  vacíos de información del país: *qué territorios son invisibles para la política pública porque nadie
  mide ahí*. Esa es, en sí misma, una conclusión de valor social.

### Los 6 drivers — compensando la cobertura parcial

Para no depender de fuentes incompletas, cuatro de los seis drivers tienen **cobertura nacional y a nivel
escuela**, gracias al CEMABE:

| ID | Driver | Fuente | Cobertura | Estado |
|---|---|---|---|---|
| `D1` | Pobreza y rezago social | CONEVAL + CONAPO | Nacional | Completa |
| `D2` | Inseguridad del entorno | SESNSP | Nacional | Completa |
| `D3` | Infraestructura escolar | CEMABE (agua, drenaje, luz, sanitarios) | Nacional · nivel escuela | Completa |
| `D4` | Conectividad digital | CEMABE (internet/computadoras) | Nacional · nivel escuela | Completa |
| `D5` | Estres hidrico regional | CONAGUA SINA | Regional | Parcial |
| `D6` | Calidad del aire | SINAICA | ~80 zonas urbanas | Parcial · con IDW e indice de confianza |

> El hallazgo que refuerza el proyecto: **CEMABE tiene infraestructura por escuela** (agua, drenaje,
> electricidad, sanitarios, internet). Eso da dos drivers sólidos y nacionales — D3 y D4 — que compensan
> con creces la cobertura parcial de aire y agua, y refuerzan la tesis de "la escuela como sensor".

---

## 2.ter Portafolio de dashboards

La rúbrica asigna 2.5 puntos al frontend BI. Se construyen **10 tableros** en Apache Superset:

| ID | Dashboard | Contenido |
|---|---|---|
| `DB-01` | **Ejecutivo / Home** | KPIs globales, tendencia de matrícula, escuelas en riesgo, alertas |
| `DB-02` | **Mapa de riesgo territorial** | Coropletico municipal + puntos de escuela, color por indice de riesgo |
| `DB-03` | **Ficha de escuela** | Drill-down individual: perfil, drivers, predicción y recomendacion |
| `DB-04` | **Comparador de municipios** | Benchmark lado a lado entre municipios de las 4 entidades |
| `DB-05` | **Análisis por driver** | Un tab por driver (D1-D6) con distribucion y correlacion con matrícula |
| `DB-06` | **Predicciones y escenarios** | Salida de los 3 modelos + panel interactivo de simulacion |
| `DB-07` | **Calidad y cobertura de datos** | Completitud por driver, Data Docs de Great Expectations, mapa de vacios |
| `DB-08` | **Explorador del cubo (pivot)** | Tabla dinámica libre sobre los cubos de Gold |
| `DB-09` | **Recomendaciones prescriptivas** | Que intervencion toca a cada escuela segun su driver dominante |
| `DB-10` | **Monitor del pipeline** | Estado de los DAGs, frescura de cada fuente, ultima ingesta exitosa |

---

## 3. Arquitectura de la solución

```
FUENTES (7)          BRONZE              SILVER              GOLD
─────────────        ─────────────       ─────────────       ─────────────────────
SEP Formato 911  ┐   Parquet crudo       Tipado             ⭐ ESQUEMA ESTRELLA
Catálogo CCT     │   particiónado    →   Deduplicado    →   fact_escuela_ciclo
SESNSP (mensual) │   por fecha           CCT homologado      dim_escuela
SINAICA (horaria)├→  _ingested_at        Municipio INEGI     dim_municipio
CONAGUA (diaria) │   _source             Validado con GE     dim_tiempo · dim_driver
CONEVAL          │                                           ─────────────────────
CONAPO           ┘                                           CUBOS materializados
                                                             features_escuela (ML)
        ▲                                                    predicciónes
        │                                                            │
   AIRFLOW (orquestación · ingesta continua)                        ▼
                                                    ┌────────────────────────────┐
                                                    │ 3 MODELOS ML → MLflow      │
                                                    │ M1 Regresión · matrícula   │
                                                    │ M2 Clasificación · driver  │
                                                    │ M3 Clustering · perfiles   │
                                                    └────────────┬───────────────┘
                                                                 ▼
                                          FastAPI (inferencia + datos) + OAuth2/JWT + RBAC
                                                                 │
                                    ┌────────────────────────────┼──────────────────┐
                                    ▼                            ▼                  ▼
                          Superset (dashboards)          Agente RAG          Roles: ciudadano
                                                     (preguntas, no SQL)            analista

               TODO DOCKERIZADO · DESPLEGADO EN GCP CLOUD RUN · URL PÚBLICA VIVA
                        (sin URL pública funcionando, la nota máxima es 6.0)
```

### Capa GOLD — el corazón del proyecto

La rúbrica premia que Gold quede impecable. Debe contener:

- **`fact_escuela_ciclo`** — hecho central: una fila por escuela × ciclo escolar, con matrícula,
  variación, y las métricas de los 6 drivers.
- **`dim_escuela`** (CCT, nivel, sostenimiento, georreferencia), **`dim_municipio`** (clave INEGI,
  población, rezago), **`dim_tiempo`** (ciclo escolar), **`dim_driver`** (catálogo de los 6 drivers).
- **Cubos materializados** — agregaciones pre-calculadas para que Superset responda rápido.
- **`features_escuela`** — tabla de features versionada, contrato cerrado con la Célula 3.
- **`predicciónes`** — salida batch de los 3 modelos, reincorporada a Gold.

---

## 4. Equipo — 21 integrantes

Asignación por nivel: las historias de **mayor complejidad técnica y de diseño** van a perfil Alto;
las de **complejidad intermedia con autonomía** a perfil Medio; las **acotadas y bien definidas** a
perfil Bajo. Quien no tenía nivel especificado se consideró Bajo.

| Integrante | Nivel | Célula | Rol | Plan individual |
|---|---|---|---|---|
| Edgar Edmundo Coronel Navarrete | **Medio** | PO | Líder de Proyecto / Product Owner | [`0-edgar-edmundo-coronel-navarrete.md`](Sprints/0-edgar-edmundo-coronel-navarrete.md) |
| Diana Aracely Alvarez Varela | **Alto** | Célula 1 | Tech Lead · Data Engineering | [`1-diana-aracely-alvarez-varela.md`](Sprints/1-diana-aracely-alvarez-varela.md) |
| Deni Garrido Fragoso | **Medio** | Célula 1 | Ingeniera de datos · Transformaciones dbt | [`1-deni-garrido-fragoso.md`](Sprints/1-deni-garrido-fragoso.md) |
| Luis Enrique García Vázquez | **Bajo** | Célula 1 | Ingeniero de datos jr · Extracción de fuentes | [`1-luis-enrique-garcia-vazquez.md`](Sprints/1-luis-enrique-garcia-vazquez.md) |
| Emilio Galnares Ruiz | **Bajo** | Célula 1 | Ingeniero de datos jr · Calidad de datos | [`1-emilio-galnares-ruiz.md`](Sprints/1-emilio-galnares-ruiz.md) |
| Manuel Alejandro Serranía Reinada | **Alto** | Célula 2 | Tech Lead · Analytics & BI | [`2-manuel-alejandro-serrania-reinada.md`](Sprints/2-manuel-alejandro-serrania-reinada.md) |
| Marina García del Buey | **Medio** | Célula 2 | Analista BI · Dashboards ejecutivos | [`2-marina-garcia-del-buey.md`](Sprints/2-marina-garcia-del-buey.md) |
| Monserrat Xcaret Miranda Olivas | **Medio** | Célula 2 | Analista BI · Modelado semántico y cubos | [`2-monserrat-xcaret-miranda-olivas.md`](Sprints/2-monserrat-xcaret-miranda-olivas.md) |
| Eloisa González Rubio | **Bajo** | Célula 4 | Desarrolladora jr · Pruebas de API | [`4-eloisa-gonzalez-rubio.md`](Sprints/4-eloisa-gonzalez-rubio.md) |
| Andrés González Habib | **Alto** | Célula 3 | Tech Lead · Machine Learning & Agente IA | [`3-andres-gonzalez-habib.md`](Sprints/3-andres-gonzalez-habib.md) |
| Héctor Rafael Morales Marbán | **Medio** | Célula 3 | Científico de datos · Modelos supervisados | [`3-hector-rafael-morales-marban.md`](Sprints/3-hector-rafael-morales-marban.md) |
| Estefany Lucero Hernández Loredo | **Bajo** | Célula 3 | Analista ML jr · Clustering y features | [`3-estefany-lucero-hernandez-loredo.md`](Sprints/3-estefany-lucero-hernandez-loredo.md) |
| Carlos Guillermo Mayorga Tapia | **Bajo** | Célula 3 | Analista ML jr · Agente RAG y evaluación | [`3-carlos-guillermo-mayorga-tapia.md`](Sprints/3-carlos-guillermo-mayorga-tapia.md) |
| Christian Imanol Ruiz Hurtado | **Alto** | Célula 4 | Tech Lead · Backend, API & Seguridad | [`4-christian-imanol-ruiz-hurtado.md`](Sprints/4-christian-imanol-ruiz-hurtado.md) |
| Karla Alejandra Monter Benitez | **Medio** | Célula 4 | Desarrolladora backend · Endpoints y RBAC | [`4-karla-alejandra-monter-benitez.md`](Sprints/4-karla-alejandra-monter-benitez.md) |
| Juan Carlos Macías Mayen | **Medio** | Célula 4 | Desarrollador backend · Inferencia ML y contratos de API | [`4-juan-carlos-macias-mayen.md`](Sprints/4-juan-carlos-macias-mayen.md) |
| Oscar Antonio Quiroz Lázaro | **Bajo** | Célula 2 | Analista BI jr · Gráficos, mapas y KPIs | [`2-oscar-antonio-quiroz-lazaro.md`](Sprints/2-oscar-antonio-quiroz-lazaro.md) |
| Luis Téllez Domínguez | **Medio** | Célula 5 | Tech Lead · Cloud & DevOps | [`5-luis-tellez-dominguez.md`](Sprints/5-luis-tellez-dominguez.md) |
| Edgar Ulises Jiménez López | **Bajo** | Célula 5 | DevOps jr · Contenedores | [`5-edgar-ulises-jimenez-lopez.md`](Sprints/5-edgar-ulises-jimenez-lopez.md) |
| Alejandro Velázquez Mendoza | **Bajo** | Célula 5 | DevOps jr · Ambientes y despliegue | [`5-alejandro-velazquez-mendoza.md`](Sprints/5-alejandro-velazquez-mendoza.md) |
| Edward Ulysses Ruiz Bustillos | **Bajo** | Célula 5 | DevOps jr · Monitoreo y documentación | [`5-edward-ulysses-ruiz-bustillos.md`](Sprints/5-edward-ulysses-ruiz-bustillos.md) |

**Distribución:** 4 Alto · 8 Medio · 9 Bajo

---

## 5. Calendario por sprint

### S1 · Lun 3 - Dom 9 ago
**Foco: Cimientos, fuentes y despliegue temprano**

| ID | Célula | Historia | Responsable |
|---|---|---|---|
| `US-001` | PO | Crear el repositorio nuevo y adaptar el vault | Edgar Edmundo Coronel Navarrete |
| `US-002` | PO | Cargar el PRD del profesor con criterios de aceptacion | Edgar Edmundo Coronel Navarrete |
| `US-003` | PO | Registrar a los 21 integrantes y crear sus Agent Contexts | Edgar Edmundo Coronel Navarrete |
| `US-101` | Célula 1 | Disenar el modelo de datos medallon completo | Diana Aracely Alvarez Varela |
| `US-121a` | Célula 1 | Prueba de descarga real de DS-06 (CONAGUA) y DS-08 (CONAPO) | Emilio Galnares Ruiz |
| `US-121b` | Célula 1 | Prueba de descarga real de DS-04 (SESNSP) y DS-05 (SINAICA) | Luis Enrique García Vázquez |
| `US-201` | Célula 2 | Disenar el portafolio de 10 dashboards y el catalogo de KPIs | Manuel Alejandro Serranía Reinada |
| `US-401` | Célula 4 | Definir y publicar el contrato de la API (OpenAPI) | Christian Imanol Ruiz Hurtado |
| `US-501` | Célula 5 | Desplegar el 'hola mundo' en GCP con URL publica | Luis Téllez Domínguez |
| `US-521a` | Célula 5 | Guia de ambiente local: API y Postgres | Alejandro Velázquez Mendoza |
| `US-521b` | Célula 5 | Guia de ambiente local: Airflow y jobs de ML | Edgar Ulises Jiménez López |
| `US-521c` | Célula 5 | Guia de ambiente local: Superset y agente | Edward Ulysses Ruiz Bustillos |

### S2 · Lun 10 - Dom 16 ago
**Foco: Ingesta continua y capa Bronze**

| ID | Célula | Historia | Responsable |
|---|---|---|---|
| `US-004` | PO | Sembrar y mantener la Traceability_Matrix | Edgar Edmundo Coronel Navarrete |
| `US-102` | Célula 1 | Construir el DAG maestro de orquestación en Airflow | Diana Aracely Alvarez Varela |
| `US-111` | Célula 1 | Implementar transformaciones Bronze -> Silver con dbt | Deni Garrido Fragoso |
| `US-122a` | Célula 1 | Extractores de DS-06 y DS-08 | Emilio Galnares Ruiz |
| `US-122b` | Célula 1 | Extractores de DS-04 y DS-05 | Luis Enrique García Vázquez |
| `US-502` | Célula 5 | Disenar el docker-compose completo del ecosistema | Luis Téllez Domínguez |
| `US-503` | Célula 5 | Configurar el pipeline de CI en GitHub Actions | Luis Téllez Domínguez |

### S3 · Lun 17 - Dom 23 ago
**Foco: Silver, Gold, Great Expectations y cubos**

| ID | Célula | Historia | Responsable |
|---|---|---|---|
| `US-103` | Célula 1 | Modelar la capa GOLD como esquema estrella | Diana Aracely Alvarez Varela |
| `US-104` | Célula 1 | Definir e implementar la tabla de features para ML | Diana Aracely Alvarez Varela |
| `US-105` | Célula 1 | Implementar la estrategia de cobertura parcial e indice de confianza | Diana Aracely Alvarez Varela |
| `US-112` | Célula 1 | Implementar transformaciones Silver -> Gold con dbt | Deni Garrido Fragoso |
| `US-113` | Célula 1 | Construir los cubos de agregacion | Deni Garrido Fragoso |
| `US-123a` | Célula 1 | Validaciones Great Expectations para DS-06 y DS-08 | Emilio Galnares Ruiz |
| `US-123b` | Célula 1 | Validaciones Great Expectations para DS-04 y DS-05 | Luis Enrique García Vázquez |
| `US-202` | Célula 2 | Configurar Superset: conexion, datasets y capa semantica | Manuel Alejandro Serranía Reinada |
| `US-211a` | Célula 2 | Modelar métricas y jerarquías para DB-03 y DB-04 | Marina García del Buey |
| `US-211b` | Célula 2 | Modelar métricas y jerarquías para DB-05 y DB-08 | Monserrat Xcaret Miranda Olivas |
| `US-221` | Célula 2 | Construir los graficos base de KPIs | Oscar Antonio Quiroz Lázaro |
| `US-301` | Célula 3 | Disenar la estrategia de modelado y el protocolo de validación | Andrés González Habib |
| `US-411` | Célula 4 | Implementar los endpoints de datos sobre Gold | Karla Alejandra Monter Benitez |
| `US-421` | Célula 4 | Implementar el esqueleto de FastAPI y healthcheck | Eloisa González Rubio |
| `US-522a` | Célula 5 | Contenerizar la API y Postgres | Alejandro Velázquez Mendoza |
| `US-522b` | Célula 5 | Contenerizar Airflow y los jobs de ML | Edgar Ulises Jiménez López |
| `US-522c` | Célula 5 | Contenerizar Superset y el agente | Edward Ulysses Ruiz Bustillos |
| `US-523a` | Célula 5 | Configurar branch protection y quality gates | Alejandro Velázquez Mendoza |
| `US-523b` | Célula 5 | Configurar el pipeline de CI para jobs y DAGs | Edgar Ulises Jiménez López |
| `US-523c` | Célula 5 | Documentar la arquitectura de despliegue | Edward Ulysses Ruiz Bustillos |

### S4 · Lun 24 - Dom 30 ago
**Foco: Modelos ML, FastAPI, Auth y Dashboards**

| ID | Célula | Historia | Responsable |
|---|---|---|---|
| `US-005` | PO | Coordinar la rotacion del Vault Steward | Edgar Edmundo Coronel Navarrete |
| `US-124a` | Célula 1 | Fixtures de prueba de DS-06 y DS-08 | Emilio Galnares Ruiz |
| `US-124b` | Célula 1 | Fixtures de prueba de DS-04 y DS-05 | Luis Enrique García Vázquez |
| `US-203` | Célula 2 | Construir DB-01 Ejecutivo y DB-02 Mapa de riesgo territorial | Manuel Alejandro Serranía Reinada |
| `US-204` | Célula 2 | Construir DB-06 Predicciones y DB-09 Recomendaciones prescriptivas | Manuel Alejandro Serranía Reinada |
| `US-212` | Célula 2 | Construir DB-03 Ficha de escuela y DB-04 Comparador de municipios | Marina García del Buey |
| `US-213` | Célula 2 | Construir DB-05 Análisis por driver y DB-08 Explorador del cubo | Monserrat Xcaret Miranda Olivas |
| `US-222` | Célula 2 | Construir DB-07 Calidad y cobertura de datos | Oscar Antonio Quiroz Lázaro |
| `US-302` | Célula 3 | Entrenar el Modelo 2 - Clasificacion de driver dominante | Andrés González Habib |
| `US-303` | Célula 3 | Registrar los 3 modelos en MLflow y exponerlos via API | Andrés González Habib |
| `US-311` | Célula 3 | Entrenar el Modelo 1 - Regresion de matrícula | Héctor Rafael Morales Marbán |
| `US-321` | Célula 3 | Entrenar el Modelo 3 - Clustering de escuelas | Estefany Lucero Hernández Loredo |
| `US-322` | Célula 3 | Análisis exploratorio y seleccion de variables | Estefany Lucero Hernández Loredo |
| `US-325` | Célula 3 | Analizar el sesgo por cobertura parcial en las features | Estefany Lucero Hernández Loredo |
| `US-402` | Célula 4 | Implementar OAuth2 + JWT con refresh/access tokens | Christian Imanol Ruiz Hurtado |
| `US-403` | Célula 4 | Implementar RBAC con los 2 roles del PRD | Christian Imanol Ruiz Hurtado |
| `US-412` | Célula 4 | Implementar los endpoints de inferencia ML | Juan Carlos Macías Mayen |
| `US-415` | Célula 4 | Implementar el contrato de datos entre API y modelos | Juan Carlos Macías Mayen |
| `US-422` | Célula 4 | Escribir pruebas unitarias y de integracion de la API | Eloisa González Rubio |
| `US-504` | Célula 5 | Aprovisionar Cloud SQL, Artifact Registry y secretos | Luis Téllez Domínguez |
| `US-206` | Célula 2 | FARO Web: shell y embebido de los 10 dashboards | Manuel Alejandro Serranía Reinada |
| `US-405` | Célula 4 | FARO Web: login/logout y vistas por rol | Christian Imanol Ruiz Hurtado |

### S5 · Lun 31 ago - Dom 6 sep
**Foco: Agente RAG, integracion y CODE FREEZE**

| ID | Célula | Historia | Responsable |
|---|---|---|---|
| `US-106` | Célula 1 | Congelar esquema y documentar linaje completo | Diana Aracely Alvarez Varela |
| `US-114` | Célula 1 | Optimizar consultas y crear indices | Deni Garrido Fragoso |
| `US-205` | Célula 2 | Integrar y armonizar los 10 dashboards | Manuel Alejandro Serranía Reinada |
| `US-214a` | Célula 2 | Filtros dinámicos y drill-down en DB-03 y DB-04 | Marina García del Buey |
| `US-214b` | Célula 2 | Filtros dinámicos y drill-down en DB-05 y DB-08 | Monserrat Xcaret Miranda Olivas |
| `US-215a` | Célula 2 | Pruebas de usabilidad de DB-03 y DB-04 | Marina García del Buey |
| `US-215b` | Célula 2 | Pruebas de usabilidad de DB-05 y DB-08 | Monserrat Xcaret Miranda Olivas |
| `US-223` | Célula 2 | Construir DB-10 Monitor del pipeline | Oscar Antonio Quiroz Lázaro |
| `US-224` | Célula 2 | Documentar el manual de usuario de los dashboards | Oscar Antonio Quiroz Lázaro |
| `US-304a` | Célula 3 | Disenar el agente conversacional: prompt y guardarraíles | Andrés González Habib |
| `US-304b` | Célula 3 | Construir la capa de recuperación del agente | Carlos Guillermo Mayorga Tapia |
| `US-312` | Célula 3 | Evaluar modelos y documentar métricas | Héctor Rafael Morales Marbán |
| `US-313` | Célula 3 | Integrar predicciónes y recomendaciones a Gold | Héctor Rafael Morales Marbán |
| `US-323` | Célula 3 | Construir el set de evaluación del agente | Carlos Guillermo Mayorga Tapia |
| `US-324` | Célula 3 | Documentar las fichas de modelo (model cards) | Carlos Guillermo Mayorga Tapia |
| `US-404` | Célula 4 | Hardening de la API | Christian Imanol Ruiz Hurtado |
| `US-413` | Célula 4 | Endpoints administrativos protegidos | Karla Alejandra Monter Benitez |
| `US-414` | Célula 4 | Documentar la API en OpenAPI y publicar la coleccion | Karla Alejandra Monter Benitez |
| `US-416` | Célula 4 | Implementar cache y manejo de errores de inferencia | Juan Carlos Macías Mayen |
| `US-423` | Célula 4 | Pruebas de seguridad de la autenticacion | Eloisa González Rubio |
| `US-524a` | Célula 5 | Monitoreo y logs de API y Postgres | Alejandro Velázquez Mendoza |
| `US-524b` | Célula 5 | Monitoreo de DAGs y jobs de entrenamiento | Edgar Ulises Jiménez López |
| `US-524c` | Célula 5 | Monitoreo de Superset y del agente | Edward Ulysses Ruiz Bustillos |
| `US-207` | Célula 2 | FARO Web: panel de ML interactivo | Marina García del Buey |
| `US-305` | Célula 3 | FARO Web: widget de chat del agente | Andrés González Habib |

### S6 · Lun 7 - Mar 8 sep
**Foco: Pruebas finales, seguridad, GCP y ensayo**

| ID | Célula | Historia | Responsable |
|---|---|---|---|
| `US-006` | PO | Preparar y ensayar el pitch de la demo en vivo | Edgar Edmundo Coronel Navarrete |
| `US-505` | Célula 5 | Despliegue final productivo y verificacion | Luis Téllez Domínguez |
| `US-525a` | Célula 5 | Runbook de rollback de API y base de datos | Alejandro Velázquez Mendoza |
| `US-525b` | Célula 5 | Runbook de rollback de Airflow y modelos | Edgar Ulises Jiménez López |
| `US-525c` | Célula 5 | Runbook de rollback de Superset y agente | Edward Ulysses Ruiz Bustillos |


### Standups

- **Semanas 1-3 (semanal, jueves):** 6, 13 y 20 de agosto - 19:00 hrs, 45 min.
- **Semanas 4-6 (3 por semana, L-Mi-V):** 24, 26, 28 ago · 31 ago, 2, 4 sep · 7 y 8 sep - 19:00 hrs, 30 min.
- **Formato:** cada celula responde 3 preguntas (que cerre, que sigue, que me bloquea). El PO actualiza la
  Traceability_Matrix al cierre de cada standup.

### Hitos que no se mueven

| Fecha | Hito |
|---|---|
| **Dom 9 ago** | URL pública "hola mundo" viva en GCP + las 7 fuentes probadas |
| **Dom 16 ago** | Ingesta continua automatizada corriendo → Bronze poblado |
| **Dom 23 ago** | Medallón completo + Great Expectations en verde + cubos |
| **Dom 30 ago** | 3 modelos entrenados + API con OAuth2/RBAC + dashboard funcional |
| **Dom 6 sep** | **CODE FREEZE** — agente integrado, todo end-to-end en la URL pública |
| **Mar 8 sep** | Dry-run completo de la demo |
| **Mié 9 sep** | **DEMO EN VIVO AL PROFESOR** |

---

## 6. Mapa de dependencias entre células

```
Célula 5 (Cloud/DevOps) ──── habilita a TODAS ────► ambiente, CI, despliegue
        │
        ▼
Célula 1 (Data Eng) ──► GOLD ──┬──► Célula 2 (BI)        dashboards
                               ├──► Célula 3 (ML)        features → modelos
                               └──► Célula 4 (Backend)   endpoints de datos
                                            │
Célula 3 ──► modelos en MLflow ─────────────┤
                                            ▼
                                    Célula 4 (API) ──► Célula 2 (panel de predicción)
                                                   └─► Célula 3 (agente consulta API)
```

**Ruta crítica:** Célula 5 → Célula 1 → Célula 3 → Célula 4 → Célula 2.
Un retraso en la Célula 1 (Gold) bloquea a tres células a la vez. Es el punto de mayor atención del PO.

**Regla de desacople:** la Célula 4 publica el **contrato de la API (OpenAPI) en la Semana 1**, antes de
construir nada. Así las Células 2 y 3 trabajan contra mocks sin esperar. Sin esta regla, 21 personas se
bloquean mutuamente.

---

## 7. Reglas de trabajo — resumen ejecutivo

1. **Prohibido commit directo a `main`.** Todo entra por PR revisado con la plantilla completa.
2. **Ramas:** `feat/ fix/ chore/ docs/ sec/` + `{nombre}-{descripción}`.
3. **Commits:** Conventional Commits con el ID de la historia — `feat(gold): cubo de matrícula (US-113)`.
4. **CI obligatorio en verde:** lint + pruebas + `vault_lint.py`. Si el linter falla, no se mergea.
5. **DevLog obligatorio** por cada sesión con IA, antes del push.
6. **Todo código de IA se revisa línea por línea.** Eres responsable de lo que subes.
7. **Nada de datos reales, `.env` ni llaves en el repositorio.** Fixtures ≤500 filas para pruebas.
8. **Definition of Filed:** ID + carpeta + frontmatter + `_index` + fila en la matriz de trazabilidad.
9. **README actualizado** cuando cambie la instalación o el uso.
10. **No apruebas tu propio PR.**

---

## 8. Cobertura del PRD — verificación

| Requisito del PRD | Peso | Dónde se cumple |
|---|---|---|
| ≥5 fuentes con ingesta continua automatizada | 2.5 | Célula 1 · 7 fuentes, 3 continuas, DAGs Airflow |
| Arquitectura en capas + auditoría de calidad | (incl.) | Medallón + Great Expectations |
| Dashboard BI dinámico e interactivo | 2.5 | Célula 2 · Superset con mapas, filtros, drill-down |
| 3 modelos ML distintos integrados vía API | 1.5 | Célula 3 · Regresión + Clasificación + Clustering |
| Backend con OAuth2/JWT y RBAC de 2 roles | 1.5 | Célula 4 · FastAPI + Google OAuth + roles |
| Despliegue en GCP dockerizado con URL pública | 1.0 | Célula 5 · Cloud Run + Cloud SQL |
| Agente conversacional sobre los datos | 0.5 | Célula 3 · RAG / Text-to-SQL |
| Trabajo en equipo, Git y documentación | 0.5 | PO + vault + commits repartidos entre los 21 |
| **Total** | **10.0** | |

---

## 9. Riesgos principales

| ID | Riesgo | Mitigación |
|---|---|---|
| `RISK-001` | Sin URL pública viva al evaluar → techo 6.0 | Deploy en Semana 1, no al final |
| `RISK-002` | Una fuente resulta inservible | Prueba de descarga real en Semana 1 |
| `RISK-003` | Commits concentrados en pocas personas | Rama por persona, PR obligatorio, revisión del PO en cada standup |
| `RISK-004` | Célula 1 se atrasa y bloquea a 3 células | Contrato de features cerrado en S3; mocks mientras tanto |
| `RISK-005` | Sobre-alcance con 32 estados | **Recorte a 3-5 estados** para que el ciclo completo funcione |
| `RISK-006` | El vault se degrada con 21 personas | `vault_lint.py` en CI + Vault Steward rotativo por sprint |

> **Decisión recomendada de alcance:** arrancar con **3 estados** (por ejemplo Estado de México, Oaxaca y
> Chiapas — contrastan urbano/rural y marginación). Es preferible un pipeline completo y prescriptivo
> sobre 3 estados que uno a medias sobre 32.

---

*Plan maestro · Proyecto FARO · Maestría MTIIA · Universidad Anáhuac*
