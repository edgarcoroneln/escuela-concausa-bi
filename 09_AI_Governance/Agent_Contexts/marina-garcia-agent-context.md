---
id: AGENTCTX-MARINA-GARCIA
title: "Agent Context — Marina García del Buey"
owner: "Marina García del Buey"
status: approved
traces_up: ["12_Roadmap_Sprints/Sprints/2-marina-garcia-del-buey"]
tags: [ai, agent-context, ownership, celula-2]
---

# Agent Context — Marina García del Buey

> El agente IA de esta persona **debe leer este archivo al inicio de cada sesión**.
> Define qué puede tocar. Si va a modificar un archivo 🔴, **debe detenerse y avisar**.
> → [[09_AI_Governance/AI_Agent_Governance]] · Plan: [[12_Roadmap_Sprints/Sprints/2-marina-garcia-del-buey]]

---

## 1. Identificación

| | |
|---|---|
| **Nombre** | Marina García del Buey |
| **Célula** | Celula 2 — Analytics & Business Intelligence |
| **Nivel** | Medio |
| **Rol** | Analista BI · Dashboards ejecutivos |
| **Tech Lead de la célula** | Manuel Alejandro Serranía Reinada |
| **Quién revisa su código** | Manuel Alejandro Serranía Reinada (Tech Lead, compuerta técnica) → Edgar Coronel (PM, compuerta de proceso) |
| **Requisito(s) que cubre** | REQ-002 (Frontend BI interactivo) |

---

## 2. 🟢 Alcance permitido (crear y modificar con IA libremente)

- `src/frontend/**` (FARO Web: capa web integrada — shell, panel ML, chat, auth)
- `superset/**` (dashboards y capa semántica)
- documentación/manual de los 10 dashboards
- Su propio plan de sprint y su DevLog en `_DevLog/`.

---

## 3. 🟡 Compartidos (coordinar con el dueño antes de tocar)

| Archivo / artefacto | Dueño | Protocolo |
|---|---|---|
| Cubos de Gold | Diana Alvarez (C1) | consumir el contrato; pedir cambios de grano |
| Tabla de predicciones | Andrés González Habib (C3) | acordar formato de salida |
| Contrato de datos de la API | Christian Ruiz (C4) | alinear campos que consumen los dashboards |
| `02_Requirements/Traceability_Matrix.md` | PM — Edgar Coronel | actualiza su fila; el PM consolida |
| `_index.md` de las carpetas que toca | PM / dueño de carpeta | registrar cada artefacto nuevo |

---

## 4. 🔴 Fuera de alcance (nunca tocar con IA sin autorización)

| Ruta / área | Dueño | A quién pedir |
|---|---|---|
| `src/ingesta/**`, `dbt/**`, `dags/**` | C1 — Diana Alvarez | pedir a Data Eng |
| `src/api/**` | C4 — Christian Ruiz | pedir a Backend |
| `src/modelos/**` | C3 — Andrés González Habib | pedir a ML |
| `.github/**` | C5 — Luis Téllez | pedir a DevOps |
| `_Meta/**` | PM — Edgar Coronel | pedir al PO |
| `07_Security/**` | C4 — Christian Ruiz | pedir a Seguridad |

> **Regla 7 del vault:** todo cambio de **esquema, seguridad o CI/CD** requiere **revisión
> humana explícita** antes de mergear.

---

## 5. Historias asignadas

| ID | Sprint | Objetivo |
|---|---|---|
| US-211a | S3 | Cubos y capa semantica que alimentan DB-03 (ficha de escuela) y DB-04 (comparador de municipios): metricas, jerarquias y granos. |
| US-212 | S4 | Drill-down individual por CCT y benchmark lado a lado entre municipios. |
| US-214a | S5 | Filtros globales (ciclo, entidad, nivel) y drill-down cruzado aplicados a DB-03 y DB-04. |
| US-215a | S5 | Pruebas de usabilidad y accesibilidad sobre DB-03 y DB-04. |

---

## 6. Reglas de uso de IA que aplican

- **DevLog obligatorio por sesión con IA**, antes del push (`_DevLog/YYYY-MM-DD-marina-garcia-*.md`).
- **Revisión línea por línea** de todo código generado por IA: es responsable de lo que sube.
- **Prohibido pegar en un prompt**: `.env`, datos reales, credenciales o tokens.
- **Nunca commit directo a `main`**: todo entra por PR (`feat/marina-buey-...`).
- Commits en Conventional Commits con el ID de la historia.
- No trabajar fuera de este alcance sin avisar; ante duda, preguntar al dueño del área.

---

## 7. Contexto técnico específico

- **10 dashboards** DB-01…DB-10 en **Apache Superset** (NO Power BI), sobre Gold acotado a 4 entidades.
- Filtros por **ciclo, entidad y nivel educativo** que apliquen al conjunto de tableros.
- DB-07 mapea `indice_completitud_drivers` y los territorios `SIN_DATO`.
- Llaves de cruce: **CCT** y **clave INEGI de 5 dígitos**. Nunca mostrar cero donde hay `SIN_DATO`.

---

## 8. Prompts iniciales sugeridos (agnósticos de LLM)

> Funcionan en Claude Code, ChatGPT, Gemini o Copilot. Todo lo generado se revisa antes de
> commitear, y cada sesión genera DevLog.

**Contexto para pegar al inicio de la sesión:**
```
Soy de Analytics & BI en FARO. Construyo dashboards en Apache Superset (NO Power BI) sobre la capa Gold. Filtros por ciclo, entidad y nivel. Responde en espanol y explica tus decisiones de visualizacion.
```

**Dashboard Superset:**
```
Diseña el dashboard <DB-xx> en Superset: KPIs, graficos e interactividad. Filtros por ciclo, entidad y nivel. Explica el mapeo a los cubos de Gold.
```

**Mapa:**
```
Propon como visualizar el mapa de riesgo territorial (coropletico municipal + puntos de escuela) evitando mostrar cero donde hay SIN_DATO.
```

**KPIs:**
```
Define el catalogo de KPIs de matricula y riesgo, con su formula y el grano del cubo que los alimenta.
```
