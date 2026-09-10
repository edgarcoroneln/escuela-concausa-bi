---
id: DOC-FRONTEND-ARCH
title: "Frontend Architecture — FARO Web"
owner: "Manuel Alejandro Serranía Reinada"
status: draft
traces_up: ["REQ-002", "vault/01_Product/PRD"]
traces_down: ["US-206", "US-207", "US-305", "US-405"]
last_reviewed: "2026-08-07"
tags: [architecture, frontend, streamlit]
---

# Frontend Architecture — FARO Web

> Capa web integrada del proyecto. → [[vault/03_Architecture/_index]] · Decisión:
> [[vault/03_Architecture/ADRs/ADR-002-frontend-streamlit]] · Contrato de API: [[vault/03_Architecture/API_Specification]]

## 1. Objetivo
Una sola aplicación web (**Streamlit**, `src/frontend/`) que integra todo lo que ve el usuario final y
cubre el §3.5 del PRD de la materia: dashboards, panel de ML, chat del agente y autenticación por rol.

## 2. Componentes (`src/frontend/`)
| Archivo | Responsabilidad | Historia |
|---|---|---|
| `app.py` | Router, sesión y guardas por rol | US-206 |
| `auth.py` | Login/logout Google → JWT de la API; `require_role()` | US-405 |
| `pages/1_Dashboards.py` | Embebido de los 10 dashboards de Superset (guest token + RLS) | US-206 |
| `pages/2_Panel_ML.py` | Formulario de parámetros → inferencia de ML-01/02/03 | US-207 |
| `pages/3_Chat.py` | Widget de chat del agente RAG | US-305 |

## 3. Autenticación y roles
El front **no reimplementa** OAuth: redirige al `/auth/login` de la API (US-402), guarda el
access/refresh token en `st.session_state` y expone `require_role("analista")`. Roles del PRD:
`ciudadano` (dashboards + agente) y `analista` (además pipelines/export/ML avanzado).

## 4. Embebido de Superset (guest token + RLS)
El front pide a Superset un **guest token** por sesión con las reglas de **row-level security** del rol,
y renderiza cada dashboard por iframe firmado. Sin token válido no se muestra ningún tablero.

## 5. Panel de ML y chat
- **Panel ML:** el usuario ingresa parámetros de una escuela/municipio; el front hace `POST` a los
  endpoints de inferencia (US-412/US-415) y muestra la predicción de los 3 modelos.
- **Chat:** entrada de lenguaje natural → API del agente (US-304/US-323) → respuesta citada.

## 6. Despliegue
Contenedor propio (`Dockerfile` del front) desplegado en **GCP Cloud Run**, detrás de la URL pública.
Amplía el alcance de despliegue de C5 (US-522*/US-505); no introduce infraestructura nueva.

## 7. Trazabilidad
- Requisitos: REQ-002 (BI), REQ-004 (auth), REQ-006 (agente).
- Historias: US-206, US-207 (C2), US-405 (C4), US-305 (C3).
- Decisión: [[vault/03_Architecture/ADRs/ADR-002-frontend-streamlit]].
