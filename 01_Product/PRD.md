---
id: PRD
title: "PRD — FARO · Escuela como Sensor Social"
owner: "Edgar Edmundo Coronel Navarrete"
status: in_review
version: "1.0"
source_of_truth: true
traces_up: [PRD-GENERAL]
last_reviewed: "2026-08-02"
tags: [product, prd, faro, concausa]
---

# PRD — FARO · Escuela como Sensor Social

> Documento **fuente de verdad de CÓMO** resolvemos el requerimiento externo de la materia
> ([[01_Product/PRD_General_Materia]], `PRD-GENERAL`, que define **QUÉ** nos piden).
> Todo `REQ-###` en [[02_Requirements/Requirements_Detailed]] traza a una sección de aquí.
> Este documento es **autosuficiente**: quien lo lea completo entiende el proyecto sin abrir otro archivo.

---

## 1. Resumen ejecutivo

**Escuela como Sensor Social** es una plataforma de datos end-to-end que usa la escuela como
**unidad de observación multidimensional del territorio**. Cruza la matrícula escolar con seis
dimensiones del entorno (pobreza, inseguridad, infraestructura, conectividad, agua y aire) para
responder dos preguntas: *¿qué escuelas van a perder matrícula el próximo ciclo?* y *¿cuál es la
causa concurrente que lo explica en cada caso?*. El resultado es **prescriptivo**: dos escuelas con
el mismo riesgo reciben recomendaciones distintas según su driver dominante. Todo el sistema se
entrega dockerizado, desplegado en GCP con URL pública viva, con privacidad por diseño (se observa la
escuela, nunca al alumno).

---

## 2. Problema y contexto

La deserción escolar hoy se atiende con **la misma intervención para todas las escuelas, sin
distinguir su causa**. Se aplica un programa genérico —típicamente apoyo alimentario o becas— por
igual, como si el motivo del abandono fuera siempre el mismo.

No lo es. **Un niño que abandona la escuela por falta de transporte no se retiene con apoyo
alimentario.** Otro que deja de asistir porque el entorno es inseguro no se retiene mejorando la
conectividad. Cuando la intervención no coincide con la causa, se gasta presupuesto sin mover el
resultado. El problema no es la falta de programas: es la **falta de diagnóstico causal a nivel de
cada escuela**.

---

## 3. Nuestra tesis

La escuela es el **punto físico donde convergen** las seis condiciones del territorio: pobreza,
inseguridad, infraestructura, conectividad, agua y aire. Usarla como **unidad de observación
multidimensional** permite hacer dos cosas a la vez:

1. **Predecir** la caída de matrícula del próximo ciclo, y
2. **Explicar su causa concurrente** — de ahí **"concausa"**: no una causa única y abstracta, sino
   el driver que concurre y domina *en esa escuela concreta*.

Observar el territorio a través de la escuela convierte un problema social difuso en una señal
medible, atribuible y accionable.

---

## 4. Nuestro Faro

> **"Que ninguna escuela pierda alumnos por una causa que pudimos anticipar y nombrar."**

Es la métrica estrella del proyecto. "Anticipar" es la parte predictiva (ML-01); "nombrar" es la
parte prescriptiva (ML-02, el driver dominante). Ver [[01_Product/OKRs_NorthStar]].

---

## 5. Diferenciador

El proyecto es **PRESCRIPTIVO, no descriptivo**. No se limita a mostrar dónde está el riesgo: dice
**qué hacer distinto en cada escuela**.

> Dos escuelas con **el mismo nivel de riesgo** reciben **recomendaciones DISTINTAS** según su driver
> dominante.

Ese salto —de "esta escuela está en riesgo" a "esta escuela está en riesgo *por inseguridad*, actúa
sobre el entorno; esta otra *por conectividad*, actúa sobre infraestructura digital"— es el corazón
del valor y lo que separa este proyecto de un tablero descriptivo convencional.

---

## 6. Privacidad por diseño

El **Formato 911 observa la ESCUELA, nunca al alumno**. La unidad mínima de dato es el plantel
(CCT), no la persona. **Todo es agregado.** No se recolecta, almacena ni infiere información
individual de estudiantes. La privacidad no es un control añadido al final: es una propiedad del
diseño del modelo de datos. Ver [[07_Security/_index]].

---

## 7. Las 8 fuentes de datos

| ID | Fuente | Frecuencia | Cobertura | Rol en el proyecto |
|---|---|---|---|---|
| DS-01 | SEP Formato 911 | Anual | Nacional | **Hecho central**: matrícula por CCT |
| DS-02 | Catálogo CCT | Continua | Nacional | **Llave primaria** del proyecto (integra todo) |
| DS-03 | CEMABE | Censo (2013) | Nacional · nivel escuela | Infraestructura por escuela → alimenta **D3 y D4** |
| DS-04 | SESNSP incidencia delictiva | Mensual | Nacional | Ingesta continua → D2 |
| DS-05 | SINAICA calidad del aire (API) | Horaria | Parcial (~80 zonas) | Ingesta continua → D6 |
| DS-06 | CONAGUA SINA | Diaria | Regional | Ingesta continua → D5 |
| DS-07 | CONEVAL rezago social | Bienal | Nacional | Contexto socioeconómico → D1 |
| DS-08 | CONAPO proyecciones | Anual | Nacional | **Denominador** para calcular tasas |

Las fuentes de alta frecuencia (DS-04 mensual, DS-05 horaria, DS-06 diaria) satisfacen el requisito
de **ingesta continua automatizada** de la materia. DS-02 (CCT) es la llave que permite unir todas
las demás a nivel escuela/municipio.

---

## 8. Los 6 drivers y la estrategia de cobertura parcial

| ID | Driver | Fuente | Cobertura |
|---|---|---|---|
| D1 | Pobreza y rezago social | CONEVAL (+CONAPO) | Nacional |
| D2 | Inseguridad del entorno | SESNSP | Nacional |
| D3 | Infraestructura escolar | CEMABE | Nacional · nivel escuela |
| D4 | Conectividad digital | CEMABE | Nacional · nivel escuela |
| D5 | Estrés hídrico | CONAGUA SINA | Regional |
| D6 | Calidad del aire | SINAICA | Parcial (~80 zonas urbanas) |

**Estrategia de cobertura parcial.** Donde no hay dato para un driver, se marca **`SIN_DATO`
explícito — NUNCA cero, NUNCA nulo silencioso**. Un cero afirmaría "no hay problema"; un nulo lo
ocultaría. `SIN_DATO` dice la verdad: "no observado".

Cada cubo expone su **bandera de cobertura** y se calcula `indice_completitud_drivers` (qué fracción
de los 6 drivers está efectivamente observada en cada escuela). El tablero **DB-07** mapea
geográficamente esos vacíos: **la limitación de datos se convierte en un hallazgo de valor social**
—dónde el Estado no está mirando el territorio— en lugar de esconderse.

---

## 9. Alcance (in / out)

**Bronze y Silver son NACIONALES. Gold, modelos y dashboards se acotan a 4 entidades:**

```python
SCOPE_ENTIDADES = ["09", "15", "19", "14"]   # CDMX · Edomex · Nuevo León · Jalisco
```

El sistema es **nacional por diseño**; se acota por **cobertura de datos, no por capacidad**. Ampliar
a las 32 entidades es **cambiar una sola línea de configuración**, no rediseñar el pipeline.

| En alcance | Fuera de alcance |
|---|---|
| Bronze/Silver nacionales sobre las 8 fuentes | Datos individuales de alumnos (privacidad por diseño) |
| Gold + ML + dashboards en 4 entidades (`SCOPE_ENTIDADES`) | Intervención/ejecución de políticas públicas |
| Predicción de variación de matrícula por escuela | Pronóstico a >1 ciclo escolar |
| Atribución de driver dominante (prescripción) | Causalidad estructural formal (usamos importancia de features, no inferencia causal) |
| URL pública viva en GCP | Multi-tenant / SLA de producción real |

---

## 10. Arquitectura medallón

```
8 FUENTES → BRONZE → SILVER → GOLD → (ML + BI + Agente) → GCP Cloud Run (URL pública)
```

- **Bronze** — Parquet crudo + metadatos obligatorios `_ingested_at`, `_source`, `_source_url`.
  Idempotente. Nacional.
- **Silver** — tipado, **CCT homologado** (la llave DS-02 unifica todas las fuentes), validado con
  **Great Expectations** (nulos, duplicados, límites físicos, tipos). Nacional.
- **Gold** — **esquema estrella**, acotado a `SCOPE_ENTIDADES`:
  - Hecho: `fact_escuela_ciclo`
  - Dimensiones: `dim_escuela`, `dim_municipio`, `dim_tiempo`, `dim_driver`
  - Derivados: **cubos** de agregación · `features_escuela` · `predicciones` · `recomendaciones`

Detalle en [[03_Architecture/Data_Model]] y [[03_Architecture/API_Specification]].

---

## 11. Los 3 modelos de ML

| ID | Modelo | Tipo | Salida | Métrica |
|---|---|---|---|---|
| ML-01 | Variación de matrícula por escuela | Regresión | Δ matrícula próximo ciclo | MAE / RMSE |
| ML-02 | **Driver dominante** | Clasificación multiclase | Cuál de D1–D6 domina, con **SHAP** | F1 macro / accuracy |
| ML-03 | Perfiles de escuela | Clustering (no supervisado) | Segmentación de planteles | Silhouette |

**ML-02 es el corazón prescriptivo del proyecto**: la clasificación multiclase con explicabilidad
SHAP es lo que permite pasar de "está en riesgo" a "está en riesgo por *este* driver", y de ahí a la
recomendación diferenciada.

**Validación con partición TEMPORAL, nunca aleatoria** — se entrena con ciclos pasados y se valida en
el ciclo siguiente, para evitar fuga de información temporal. Registro y versionado con **MLflow**.

---

## 12. Los 10 dashboards (Superset)

| ID | Dashboard | Historia que lo construye |
|---|---|---|
| DB-01 | Ejecutivo | US-203 |
| DB-02 | Mapa de riesgo territorial | US-203 |
| DB-03 | Ficha de escuela (drill-down por CCT) | US-212 |
| DB-04 | Comparador de municipios | US-212 |
| DB-05 | Análisis por driver | US-213 |
| DB-06 | Predicciones | US-204 |
| DB-07 | **Calidad y cobertura de datos** (`indice_completitud_drivers` y `SIN_DATO`) | US-222 |
| DB-08 | Explorador del cubo | US-213 |
| DB-09 | Recomendaciones prescriptivas | US-204 |
| DB-10 | Monitor del pipeline | US-223 |

> **Catálogo canónico (regla 1).** Estos nombres se homologaron con `02_Requirements/User_Stories.md`
> y las fichas de sprint de la Célula 2 (reporte de Sprint 1), que era la versión vigente en ejecución.
> **Pendiente de ratificación final de Manuel (TL C2)**; si ajusta algún nombre, se corrige en este mismo PR.

### 12.1 Capa web integrada (FARO Web)

Los 10 dashboards se integran en **FARO Web**, una app **Streamlit** (`src/frontend/`) que además hospeda el **panel de ML interactivo**, el **widget de chat del agente** y el **login/logout con vistas protegidas por rol**. Los dashboards se embeben por **guest token con row-level security**. Cubre el §3.5 del PRD de la materia. Historias: US-206, US-207 (C2), US-405 (C4), US-305 (C3). Ver [[03_Architecture/Frontend_Architecture]] y [[03_Architecture/ADRs/ADR-002-frontend-streamlit]].

---

## 13. Criterios de éxito (medibles)

| # | Criterio | Meta |
|---|---|---|
| 1 | Fuentes integradas con ingesta continua | ≥ 5 de las 8 (incluyendo ≥1 horaria/diaria) |
| 2 | Cobertura Gold | 4 entidades (`SCOPE_ENTIDADES`) completas |
| 3 | ML-01 predicción de matrícula | MAE/RMSE reportado con validación temporal |
| 4 | ML-02 driver dominante | F1 macro reportado + explicación SHAP por escuela |
| 5 | ML-03 clustering | Silhouette reportado + perfiles interpretables |
| 6 | Prescripción diferenciada | 2 escuelas mismo riesgo → recomendaciones distintas demostrables |
| 7 | Calidad de datos | Suite Great Expectations en verde; `SIN_DATO` sin nulos silenciosos |
| 8 | Backend | API con OAuth2/JWT + RBAC (≥2 roles) funcional |
| 9 | Despliegue | **URL pública viva en GCP** al momento de evaluar |
| 10 | Agente conversacional | Responde preguntas de negocio sobre los datos consolidados |
| 11 | Trazabilidad | Todo `REQ-###` traza a una sección de este PRD |

> Recordatorio de la rúbrica externa ([[01_Product/PRD_General_Materia]]): **sin URL pública
> funcional al evaluar, la nota máxima es 6.0/10.**

---

## 14. Fuera de alcance (expectativas acotadas)

- **No** se hace inferencia causal formal: ML-02 atribuye el driver por importancia de features
  (SHAP), no demuestra causalidad estructural. La palabra "concausa" es descriptiva del enfoque, no
  una afirmación econométrica.
- **No** se ejecutan ni financian intervenciones: el proyecto **recomienda**, no interviene.
- **No** se manejan datos a nivel de alumno bajo ninguna circunstancia.
- **No** se garantiza SLA de producción, multi-tenant, ni pronóstico a más de un ciclo escolar.
- **No** se incluyen las 32 entidades en Gold en esta entrega (es un cambio de configuración, no un
  compromiso de esta versión).

---

## 15. Requisitos no funcionales (NFR)

| NFR | Meta | Gate que lo verifica |
|---|---|---|
| Rendimiento | Respuesta de API y dashboards aceptable en demo en vivo | [[08_CICD_DevOps/CI_Quality_Gates]] |
| Seguridad | OAuth2/JWT + RBAC; sin secretos en el repo | [[07_Security/_index]] |
| Accesibilidad | Dashboards legibles, contraste y etiquetas claras | — |
| Disponibilidad / SLO | URL pública estable durante la ventana de evaluación | [[11_Operations/Monitoring_SLOs]] |
| Privacidad | Dato mínimo = escuela (CCT); cero PII de alumnos | [[07_Security/_index]] |

---

## 16. Referencias

- Requerimiento externo (QUÉ): [[01_Product/PRD_General_Materia]] (`PRD-GENERAL`)
- Faro y OKRs: [[01_Product/OKRs_NorthStar]]
- Personas y casos de uso: [[01_Product/Personas]]
- Modelo de datos y APIs: [[03_Architecture/Data_Model]] · [[03_Architecture/API_Specification]]
- Riesgos: [[10_Risk_Governance/Risk_Register]]
- Roadmap y fases: [[12_Roadmap_Sprints/Roadmap]]
