---
id: DOC-CLAUDE
title: "CLAUDE.md — Contexto del proyecto para agentes de IA"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
version: "1.0"
source_of_truth: true
traces_up: ["vault/00_Start_Here/PROJECT_INDEX"]
tags: [ai-governance, context, meta]
---

# CLAUDE.md — Contexto del proyecto para agentes de IA

> Este archivo lo lee Claude Code automáticamente al abrir el repositorio.
> **Léelo completo antes de generar cualquier código o documento.**

---

## 1. Qué es este proyecto

**Proyecto final de la materia de Inteligencia de Negocios** — Maestría MTIIA, Universidad Anáhuac.
Profesor: **Dr. José Gustavo Fuentes** (doctor en matemáticas, experto en IA/BI, cursos en MIT).

Construimos **"Escuela como Sensor Social"**: una plataforma de datos end-to-end que usa la escuela como
unidad de observación multidimensional del territorio. Cruzamos matrícula escolar con pobreza,
inseguridad, infraestructura, conectividad, agua y aire para responder dos preguntas:

1. ¿Qué escuelas van a perder matrícula el próximo ciclo?
2. ¿Cuál de los seis drivers lo explica **en cada caso**?

**El diferenciador:** dos escuelas con el mismo riesgo reciben **recomendaciones distintas** según el
driver dominante. El proyecto es **prescriptivo**, no solo descriptivo.

**Privacidad por diseño:** el Formato 911 observa la ESCUELA, nunca al alumno. Todo es agregado.

- **Nueva entrega:** lunes 14 de septiembre de 2026, a primera hora
- **Equipo:** 21 personas en 6 equipos de recuperación; Edgar conserva el rol PO y apoya QA
- **Ventana activa:** jueves 10 a domingo 13 · revisión diaria 18:00 · **CODE FREEZE domingo 20:00**

> La revisión del profesor del 9-sep no aceptó satisfactoriamente la entrega. `DEC-022` reabre el
> desarrollo. Contexto vigente: `vault/13_Reports/Revision_Profesor_2026-09-09.md` y
> `vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09.md`.

---

## 2. Regla de oro del repositorio

> **Este repositorio se rige por el vault.** Antes de crear cualquier archivo, consulta
> `vault/_Meta/Vault_Rules.md`, `vault/_Meta/Naming_Conventions.md` y `vault/_Meta/Definition_of_Filed.md`.
> Si un artefacto no cumple "Definition of Filed", **no está terminado**.

Las 9 reglas no negociables:

1. Un tema, un archivo canónico. Prohibido duplicar.
2. Todo artefacto lleva frontmatter con `id`, `owner`, `status` y (si aplica) `traces_up` / `traces_down`.
3. Todo artefacto tiene un ID único. Los IDs nunca se reciclan.
4. Nada vive en una carpeta sin estar en su `_index.md`.
5. Cambios al código pasan por PR. **Nunca push directo a `main`.**
6. **Toda sesión con IA genera una entrada de DevLog antes del push.**
7. Cambios de seguridad, esquema o CI/CD requieren revisión humana explícita.
8. **Una rama fija por persona: `dev/{identidad}`.** Permanente, se sincroniza con `merge`, nunca se borra.
9. **Cada quien toca solo su alcance**, definido en `vault/_Meta/ownership.yml`. El CI lo hace cumplir.

---

## 3. Instrucciones específicas para ti (el agente)

### Siempre
- Escribe en **español** (código y comentarios técnicos pueden ir en inglés).
- Usa los prefijos de ID correctos: `REQ-` `US-` `AC-` `ADR-` `TASK-` `TEST-` `BUG-` `SEC-` `RISK-` `INC-` `DEC-` `DS-` `ML-`
- Al terminar una tarea, **recuerda al usuario** que debe: actualizar el `_index.md`, la
  `vault/02_Requirements/Traceability_Matrix.md` y escribir su DevLog.
- Commits en formato Conventional Commits **con el ID de la historia**:
  `feat(gold): cubo de matrícula por municipio (US-113)`
- **Una sola rama por persona:** `dev/{primer-nombre}-{apellido-paterno}`, permanente. La rama dice
  quién; el commit dice qué. El padrón de las 21 identidades está en `vault/_Meta/ownership.yml`.
- **Sincroniza antes de trabajar y antes de abrir el PR:** `git fetch origin && git merge origin/main`.
- Título del PR: `[Nombre Apellido] - Descripción concisa (ID) - [sync|CI|DoF|DevLog]`

### Nunca
- **Nunca hagas commit directo a `main`.**
- **Nunca abras una rama por historia, por sprint o por tema.** Solo existe `dev/{identidad}`.
- **Nunca uses `rebase` ni `--force`** sobre una rama `dev/*`: es permanente y su historia sostiene
  las revisiones de los PRs anteriores.
- **Nunca toques archivos fuera del alcance de la persona con la que trabajas.** Ante duda, pregunta
  al dueño del área.
- **Nunca pongas credenciales, tokens ni contenido de `.env` en el código.** Ver `vault/07_Security/Secrets_Policy.md`.
- **Nunca subas datos reales pesados.** `data/raw/` está en `.gitignore`. Los fixtures van en
  `tests/fixtures/`, máximo 500 filas, anonimizados.
- Nunca inventes rutas de fuentes de datos. Si no sabes la URL exacta, dilo y pide confirmación.
- Nunca generes código que ejecute `DELETE`, `UPDATE` o `DROP` desde el agente conversacional.

### Al generar código
- Python 3.11, PEP 8, docstrings, type hints.
- Todo script de ingesta debe ser **idempotente** y escribir metadatos `_ingested_at`, `_source`, `_source_url`.
- Todo endpoint debe validar entradas con Pydantic y no filtrar detalles internos en los errores.
- Todo modelo ML se valida con **partición temporal, nunca aleatoria** (evitar fuga de información).

---

## 4. Arquitectura

```
8 FUENTES → BRONZE (Parquet crudo) → SILVER (limpio, validado) → GOLD (esquema estrella)
                    ↑ Airflow                    ↑ dbt + Great Expectations
                                                                      ↓
                            3 MODELOS ML (MLflow) → FastAPI (OAuth2/JWT + RBAC)
                                                          ↓
                          Superset (10 dashboards)  ·  Agente RAG (Text-to-SQL)
                                                          ↓
                    TODO DOCKERIZADO · GCP CLOUD RUN · URL PÚBLICA VIVA
```

**Sin URL pública funcionando al evaluar, la nota máxima es 6.0.** Por eso el deploy "hola mundo" va en
la Semana 1, no al final.

### Alcance (parámetro de configuración)

```python
SCOPE_ENTIDADES = ["09", "15", "19", "14"]   # CDMX · Edomex · Nuevo León · Jalisco
```

**Bronze y Silver son nacionales. Gold, modelos y dashboards se acotan a 4 entidades.**
El sistema es nacional por diseño; se acota por cobertura de datos, no por capacidad.

### Los 6 drivers

| ID | Driver | Fuente | Cobertura |
|---|---|---|---|
| D1 | Pobreza y rezago social | CONEVAL + CONAPO | Nacional |
| D2 | Inseguridad del entorno | SESNSP | Nacional |
| D3 | Infraestructura escolar | CEMABE | Nacional · nivel escuela |
| D4 | Conectividad digital | CEMABE | Nacional · nivel escuela |
| D5 | Estrés hídrico | CONAGUA SINA | Regional |
| D6 | Calidad del aire | SINAICA | ~80 zonas urbanas |

**Regla de cobertura parcial:** donde no hay dato, se marca `SIN_DATO` explícito. **Nunca cero, nunca
nulo silencioso.** Cada cubo expone bandera de cobertura y se calcula `indice_completitud_drivers`.

### Las 8 fuentes

| ID | Fuente | Frecuencia |
|---|---|---|
| DS-01 | SEP Formato 911 (SIGED / datos.gob.mx) | Anual |
| DS-02 | SEP Catálogo CCT | Continua |
| DS-03 | SEP CEMABE | Censo 2013 |
| DS-04 | SESNSP incidencia delictiva | **Mensual** |
| DS-05 | SINAICA calidad del aire (API) | **Horaria** |
| DS-06 | CONAGUA SINA | **Diaria** |
| DS-07 | CONEVAL rezago social | Bienal |
| DS-08 | CONAPO proyecciones | Anual |

---

## 5. Stack técnico

| Capa | Herramienta |
|---|---|
| Orquestación | Apache Airflow |
| Transformación | dbt-core |
| Calidad de datos | Great Expectations + Pydantic |
| Almacén | PostgreSQL (Cloud SQL en prod) |
| ML | scikit-learn, XGBoost + MLflow |
| API | FastAPI + OAuth2/JWT + RBAC |
| Agente | ChromaDB + sentence-transformers |
| BI | **Apache Superset** (NO Power BI) |
| Contenedores | Docker + docker-compose |
| Nube | **GCP** (Cloud Run + Cloud SQL + Artifact Registry) |

---

## 6. Equipo — 6 frentes de recuperación S7

| Equipo | Área | Líder | Integrantes |
|---|---|---|---|
| 1 | Componentes y memoria técnica | Héctor Morales | Manuel Serranía · Carlos Mayorga |
| 2 | Chat IA natural | Andrés González | Karla Monter · Alejandro Velázquez |
| 3 | UX/UI y storytelling | Marina García | Oscar Quiroz · Juan Macías · Monserrat Miranda |
| 4 | ML-03 y explicación ML | Estefany Hernández | Deni Garrido · Luis García |
| 5 | Frontend y deploy | Diana Alvarez | Luis Téllez · Christian Ruiz |
| 6 | QA integral | Edward Ruiz | Emilio Galnares · Edgar Jiménez · Eloisa González · Edgar Coronel (comodín) |

Cada integrante tiene su plan en `vault/12_Roadmap_Sprints/Sprints/` y su alcance de IA en
`vault/09_AI_Governance/Agent_Contexts/`.

**Antes de trabajar con alguien, revisa su Agent Context.** No trabajes fuera del alcance definido.

---

## 7. Rúbrica — dónde viven los 10 puntos

| Módulo | Puntos |
|---|---|
| Data Engineering & pipelines multi-fuente | 2.5 |
| Frontend BI interactivo | 2.5 |
| 3 modelos de ML integrados vía API | 1.5 |
| Backend, API & Auth avanzada (OAuth2 + RBAC) | 1.5 |
| Despliegue GCP + Docker con URL pública | 1.0 |
| Agente conversacional | 0.5 |
| Trabajo en equipo, Git & documentación | 0.5 |

---

## 8. Comandos frecuentes

```bash
# Ambiente
source .venv/bin/activate
docker compose up -d

# Calidad del vault (DEBE dar verde antes de cada PR)
python vault/_Meta/scripts/vault_lint.py .

# Pruebas
pytest tests/ -q

# dbt
dbt run --select silver
dbt test
```

---

*Última actualización: 10 de septiembre de 2026 · Sprint de recuperación · MTIIA Anáhuac*
