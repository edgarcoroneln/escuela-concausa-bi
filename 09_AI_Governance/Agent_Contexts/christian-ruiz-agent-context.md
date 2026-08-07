---
id: AGENTCTX-CHRISTIAN-RUIZ
title: "Agent Context — Christian Imanol Ruiz Hurtado"
owner: "Christian Imanol Ruiz Hurtado"
status: approved
traces_up: ["12_Roadmap_Sprints/Sprints/4-christian-imanol-ruiz-hurtado"]
tags: [ai, agent-context, ownership, celula-4]
---

# Agent Context — Christian Imanol Ruiz Hurtado

> El agente IA de esta persona **debe leer este archivo al inicio de cada sesión**.
> Define qué puede tocar. Si va a modificar un archivo 🔴, **debe detenerse y avisar**.
> → [[09_AI_Governance/AI_Agent_Governance]] · Plan: [[12_Roadmap_Sprints/Sprints/4-christian-imanol-ruiz-hurtado]]

---

## 1. Identificación

| | |
|---|---|
| **Nombre** | Christian Imanol Ruiz Hurtado |
| **Célula** | Celula 4 — Backend, API & Seguridad |
| **Nivel** | Alto |
| **Rol** | Tech Lead · Backend, API & Seguridad |
| **Tech Lead de la célula** | Christian Imanol Ruiz Hurtado |
| **Quién revisa su código** | Edgar Edmundo Coronel Navarrete (PM) — compuerta técnica y de proceso |
| **Requisito(s) que cubre** | REQ-004 (Backend, API y autenticación avanzada) |

---

## 2. 🟢 Alcance permitido (crear y modificar con IA libremente)

- `src/frontend/**` (FARO Web: capa web integrada — shell, panel ML, chat, auth)
- `src/api/**`
- `03_Architecture/API_Specification.md`
- `07_Security/**` (secretos y políticas)
- Su propio plan de sprint y su DevLog en `_DevLog/`.

---

## 3. 🟡 Compartidos (coordinar con el dueño antes de tocar)

| Archivo / artefacto | Dueño | Protocolo |
|---|---|---|
| Endpoints de datos sobre Gold | Diana Alvarez (C1) | depende del esquema de Gold |
| Endpoints de inferencia ML | Andrés González Habib (C3) | depende del contrato de modelos |
| Módulo de auth del frontend | Manuel Serranía (C2) | exponer login/roles para vistas protegidas |
| `02_Requirements/Traceability_Matrix.md` | PM — Edgar Coronel | actualiza su fila; el PM consolida |
| `_index.md` de las carpetas que toca | PM / dueño de carpeta | registrar cada artefacto nuevo |

---

## 4. 🔴 Fuera de alcance (nunca tocar con IA sin autorización)

| Ruta / área | Dueño | A quién pedir |
|---|---|---|
| `src/ingesta/**`, `dbt/**`, `dags/**` | C1 — Diana Alvarez | pedir a Data Eng |
| `src/modelos/**` | C3 — Andrés González Habib | pedir a ML |
| `superset/**` | C2 — Manuel Serranía | pedir a BI |
| `.github/**` | C5 — Luis Téllez | pedir a DevOps |
| `_Meta/**` | PM — Edgar Coronel | pedir al PO |

> **Regla 7 del vault:** todo cambio de **esquema, seguridad o CI/CD** requiere **revisión
> humana explícita** antes de mergear.

---

## 5. Historias asignadas

| ID | Sprint | Objetivo |
|---|---|---|
| US-401 | S1 | Especificacion de TODOS los endpoints ANTES de construir, para que las Celulas 2 y 3 trabajen en paralelo con mocks. Va a `03_Architecture/API_Specification.md`. |
| US-402 | S4 | Login con Google y manejo seguro de tokens. Es el requisito mas delicado del PRD. |
| US-403 | S4 | Rol `ciudadano` (dashboards + agente) y `analista` (pipelines, export bruto, ML avanzado), como dependencias reutilizables de FastAPI. |
| US-404 | S5 | Rate limiting, CORS, validacion estricta con Pydantic y errores sin fuga de informacion interna. |

---

## 6. Reglas de uso de IA que aplican

- **DevLog obligatorio por sesión con IA**, antes del push (`_DevLog/YYYY-MM-DD-christian-ruiz-*.md`).
- **Revisión línea por línea** de todo código generado por IA: es responsable de lo que sube.
- **Prohibido pegar en un prompt**: `.env`, datos reales, credenciales o tokens.
- **Nunca commit directo a `main`**: todo entra por PR (`feat/christian-hurtado-...`).
- Commits en Conventional Commits con el ID de la historia.
- No trabajar fuera de este alcance sin avisar; ante duda, preguntar al dueño del área.

---

## 7. Contexto técnico específico

- **FastAPI** con validación de entradas por **Pydantic**; no filtrar detalles internos en los errores.
- **OAuth2 + JWT** (access + refresh tokens). **RBAC de 2 roles**: ciudadano/estándar vs analista/admin.
- Contrato **OpenAPI** publicado en Semana 1 para desacoplar a C2 y C3 (trabajan contra mocks).
- Consume Gold (C1) y modelos (C3); no reimplementa lógica de datos ni de ML.

---

## 8. Prompts iniciales sugeridos (agnósticos de LLM)

> Funcionan en Claude Code, ChatGPT, Gemini o Copilot. Todo lo generado se revisa antes de
> commitear, y cada sesión genera DevLog.

**Contexto para pegar al inicio de la sesión:**
```
Soy de Backend, API & Seguridad en FASTAPI para FARO. OAuth2/JWT con refresh/access tokens, RBAC de 2 roles, validacion Pydantic, contrato OpenAPI. Responde en espanol con codigo comentado.
```

**FastAPI:**
```
Implementa el endpoint <ruta> en FastAPI con validacion Pydantic y manejo de errores que no filtre trazas internas. Documenta en OpenAPI.
```

**OAuth2/JWT:**
```
Implementa OAuth2 con JWT (access + refresh) y renovacion de token. Explica el flujo y el manejo seguro de los tokens.
```

**RBAC:**
```
Implementa RBAC con 2 roles (ciudadano y analista/admin) y protege un endpoint segun rol. Escribe pruebas de 401/403/200.
```
