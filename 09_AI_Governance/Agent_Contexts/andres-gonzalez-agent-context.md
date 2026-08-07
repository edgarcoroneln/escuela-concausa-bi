---
id: AGENTCTX-ANDRES-GONZALEZ
title: "Agent Context — Andrés González Habib"
owner: "Andrés González Habib"
status: approved
traces_up: ["12_Roadmap_Sprints/Sprints/3-andres-gonzalez-habib"]
tags: [ai, agent-context, ownership, celula-3]
---

# Agent Context — Andrés González Habib

> El agente IA de esta persona **debe leer este archivo al inicio de cada sesión**.
> Define qué puede tocar. Si va a modificar un archivo 🔴, **debe detenerse y avisar**.
> → [[09_AI_Governance/AI_Agent_Governance]] · Plan: [[12_Roadmap_Sprints/Sprints/3-andres-gonzalez-habib]]

---

## 1. Identificación

| | |
|---|---|
| **Nombre** | Andrés González Habib |
| **Célula** | Celula 3 — Machine Learning & AI Agent |
| **Nivel** | Alto |
| **Rol** | Tech Lead · Machine Learning & Agente IA |
| **Tech Lead de la célula** | Andrés González Habib |
| **Quién revisa su código** | Edgar Edmundo Coronel Navarrete (PM) — compuerta técnica y de proceso |
| **Requisito(s) que cubre** | REQ-003 (3 modelos de ML) y REQ-006 (agente conversacional) |

---

## 2. 🟢 Alcance permitido (crear y modificar con IA libremente)

- `src/frontend/**` (FARO Web: capa web integrada — shell, panel ML, chat, auth)
- `src/modelos/**`
- `src/agente/**`
- `15_ML_Models/**`
- `notebooks/**`
- Su propio plan de sprint y su DevLog en `_DevLog/`.

---

## 3. 🟡 Compartidos (coordinar con el dueño antes de tocar)

| Archivo / artefacto | Dueño | Protocolo |
|---|---|---|
| `gold.features_escuela` | Diana Alvarez (C1) | contrato de features versionado (US-104) |
| Endpoints de inferencia ML | Christian Ruiz (C4) | acordar contrato de request/response |
| Tabla de predicciones → Gold | Diana Alvarez (C1) | acordar reincorporación a Gold |
| `02_Requirements/Traceability_Matrix.md` | PM — Edgar Coronel | actualiza su fila; el PM consolida |
| `_index.md` de las carpetas que toca | PM / dueño de carpeta | registrar cada artefacto nuevo |

---

## 4. 🔴 Fuera de alcance (nunca tocar con IA sin autorización)

| Ruta / área | Dueño | A quién pedir |
|---|---|---|
| `src/ingesta/**`, `dbt/**`, `dags/**` | C1 — Diana Alvarez | pedir a Data Eng |
| `src/api/**` | C4 — Christian Ruiz | pedir a Backend |
| `superset/**` | C2 — Manuel Serranía | pedir a BI |
| `.github/**` | C5 — Luis Téllez | pedir a DevOps |
| `_Meta/**` | PM — Edgar Coronel | pedir al PO |
| `07_Security/**` | C4 — Christian Ruiz | pedir a Seguridad |

> **Regla 7 del vault:** todo cambio de **esquema, seguridad o CI/CD** requiere **revisión
> humana explícita** antes de mergear.

---

## 5. Historias asignadas

| ID | Sprint | Objetivo |
|---|---|---|
| US-301 | S3 | Los 3 modelos, particion temporal (nunca aleatoria), protocolo de backtesting y manejo de cobertura parcial en features. Documentar como ADR. |
| US-302 | S4 | Multiclase: cual de los 6 drivers explica el riesgo de cada escuela. Con SHAP para explicabilidad. Es el corazon prescriptivo del proyecto. |
| US-303 | S4 | Versionado, metricas, artefactos y contrato de inferencia batch y en tiempo real. |
| US-304a | S5 | Diseno del agente conversacional, prompt del sistema y guardarraines de seguridad: rechazar consultas fuera de alcance y nunca ejecutar DELETE/UPDATE/DROP. La capa de recuperacion (indexado y contexto) la construye Carlos en US-304b. |

---

## 6. Reglas de uso de IA que aplican

- **DevLog obligatorio por sesión con IA**, antes del push (`_DevLog/YYYY-MM-DD-andres-gonzalez-*.md`).
- **Revisión línea por línea** de todo código generado por IA: es responsable de lo que sube.
- **Prohibido pegar en un prompt**: `.env`, datos reales, credenciales o tokens.
- **Nunca commit directo a `main`**: todo entra por PR (`feat/andres-habib-...`).
- Commits en Conventional Commits con el ID de la historia.
- No trabajar fuera de este alcance sin avisar; ante duda, preguntar al dueño del área.

---

## 7. Contexto técnico específico

- 3 modelos: **ML-01** regresión (MAE/RMSE), **ML-02** clasificación multiclase de driver dominante con **SHAP**, **ML-03** clustering (Silhouette).
- **Validación con partición temporal, nunca aleatoria** (evitar fuga de información).
- Registro y versionado en **MLflow**; features desde `gold.features_escuela`.
- Agente **RAG/Text-to-SQL** (ChromaDB + sentence-transformers). **Nunca** ejecutar DELETE/UPDATE/DROP.

---

## 8. Prompts iniciales sugeridos (agnósticos de LLM)

> Funcionan en Claude Code, ChatGPT, Gemini o Copilot. Todo lo generado se revisa antes de
> commitear, y cada sesión genera DevLog.

**Contexto para pegar al inicio de la sesión:**
```
Soy de Machine Learning & Agente en FARO. 3 modelos (regresion, clasificacion multiclase de driver con SHAP, clustering), validacion temporal (nunca aleatoria), MLflow, y agente RAG/Text-to-SQL. Responde en espanol con codigo comentado.
```

**Modelo supervisado:**
```
Entrena <ML-01 regresion / ML-02 clasificacion> con particion temporal (nunca aleatoria). Reporta la metrica y, para ML-02, explicabilidad con SHAP.
```

**Clustering:**
```
Implementa el clustering de escuelas (ML-03): selecciona k, valida con Silhouette y perfila cada grupo en lenguaje de negocio.
```

**Agente RAG:**
```
Diseña la capa de recuperacion del agente: indexar el esquema de Gold en ChromaDB con embeddings y construir la consulta de contexto. Nunca DELETE/UPDATE/DROP.
```
