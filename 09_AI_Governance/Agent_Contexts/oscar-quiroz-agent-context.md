---
id: AGENTCTX-OSCAR-QUIROZ
title: "Agent Context — Oscar Antonio Quiroz Lázaro"
owner: "Oscar Antonio Quiroz Lázaro"
status: approved
traces_up: ["12_Roadmap_Sprints/Sprints/2-oscar-antonio-quiroz-lazaro"]
tags: [ai, agent-context, ownership, celula-2]
---

# Agent Context — Oscar Antonio Quiroz Lázaro

> El agente IA de esta persona **debe leer este archivo al inicio de cada sesión**.
> Define qué puede tocar. Si va a modificar un archivo 🔴, **debe detenerse y avisar**.
> → [[09_AI_Governance/AI_Agent_Governance]] · Plan: [[12_Roadmap_Sprints/Sprints/2-oscar-antonio-quiroz-lazaro]]

---

## 1. Identificación

| | |
|---|---|
| **Nombre** | Oscar Antonio Quiroz Lázaro |
| **Célula** | Celula 2 — Analytics & Business Intelligence |
| **Nivel** | Bajo |
| **Rol** | Analista BI jr · Graficos, mapas y KPIs |
| **Tech Lead de la célula** | Manuel Alejandro Serranía Reinada |
| **Quién revisa su código** | Manuel Alejandro Serranía Reinada (Tech Lead, compuerta técnica) → Edgar Coronel (PM, compuerta de proceso) |
| **Requisito(s) que cubre** | REQ-002 (Frontend BI interactivo) |

---

## 2. 🟢 Alcance permitido (crear y modificar con IA libremente)

- `superset/**` (dashboards y capa semántica)
- `04_UX_Design/**` (diseño de pantallas y accesibilidad de dashboards)
- documentación/manual de los 10 dashboards
- Su propio plan de sprint y su DevLog en `_DevLog/`.

---

## 3. 🟡 Compartidos (coordinar con el dueño antes de tocar)

| Archivo / artefacto | Dueño | Protocolo |
|---|---|---|
| Cubos de Gold | Diana Alvarez (C1) | consumir el contrato; pedir cambios de grano |
| Tabla de predicciones | Andrés González Habib (C3) | acordar formato de salida |
| Contrato de datos de la API | Karla Monter (C4) | alinear campos que consumen los dashboards |
| `02_Requirements/Traceability_Matrix.md` | PM — Edgar Coronel | actualiza su fila; el PM consolida |
| `_index.md` de las carpetas que toca | PM / dueño de carpeta | registrar cada artefacto nuevo |

---

## 4. 🔴 Fuera de alcance (nunca tocar con IA sin autorización)

| Ruta / área | Dueño | A quién pedir |
|---|---|---|
| `src/ingesta/**`, `dbt/**`, `dags/**` | C1 — Diana Alvarez | pedir a Data Eng |
| `src/api/**` | C4 — Karla Monter | pedir a Backend |
| `src/modelos/**` | C3 — Andrés González Habib | pedir a ML |
| `.github/**` | C5 — Luis Téllez | pedir a DevOps |
| `_Meta/**` | PM — Edgar Coronel | pedir al PO |
| `07_Security/**` | C4 — Karla Monter | pedir a Seguridad |

> **Regla 7 del vault:** todo cambio de **esquema, seguridad o CI/CD** requiere **revisión
> humana explícita** antes de mergear.

---

## 5. Historias asignadas

| ID | Sprint | Objetivo |
|---|---|---|
| US-221 | S3 | Series de matricula, distribucion por nivel educativo y tarjetas de KPI reutilizables. |
| US-222 | S4 | Tablero de completitud por driver y mapa de vacios. Convierte una limitacion en un hallazgo de valor. |
| US-223 | S5 | Estado de DAGs, frescura por fuente y ultima ingesta exitosa. |
| US-224 | S5 | Guia con capturas para el pitch y el README. |

---

## 6. Reglas de uso de IA que aplican

- **DevLog obligatorio por sesión con IA**, antes del push (`_DevLog/YYYY-MM-DD-oscar-quiroz-*.md`).
- **Revisión línea por línea** de todo código generado por IA: es responsable de lo que sube.
- **Prohibido pegar en un prompt**: `.env`, datos reales, credenciales o tokens.
- **Nunca commit directo a `main`**: todo entra por PR (`feat/oscar-lazaro-...`).
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
