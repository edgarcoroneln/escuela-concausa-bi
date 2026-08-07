---
id: ADR-002
title: "ADR-002 — Frontend integrado en Streamlit sobre Superset + API"
owner: "Edgar Edmundo Coronel Navarrete"
status: accepted
traces_up: ["REQ-002", "REQ-004", "REQ-006"]
supersedes: []
tags: [architecture, adr, frontend]
date: "2026-08-07"
---

# ADR-002 — Frontend integrado en Streamlit sobre Superset + API

## Contexto
El §3.5 del PRD de la materia ([[01_Product/PRD_General_Materia]]) exige, además de dashboards, tres
piezas de interfaz: un **panel de ML interactivo** (parámetros → predicción de los 3 modelos), un
**widget de chat** del agente y un **módulo de auth** (login/logout + vistas protegidas por rol).
Superset por sí solo no hospeda con naturalidad esas tres piezas.

## Decisión
Construir **FARO Web**, una app **Streamlit** en `src/frontend/` que:
- Embebe los 10 dashboards de Superset por **guest token con row-level security** por rol.
- Hospeda el **panel de ML interactivo** (form → API de inferencia US-412/US-415).
- Hospeda el **widget de chat** del agente RAG (US-304/US-323).
- Implementa **login/logout** delegando en el OAuth2/JWT de la API (US-402/US-403) y protege vistas
  por rol `ciudadano`/`analista`.

## Alternativas consideradas
| Opción | Pros | Contras |
|---|---|---|
| **Streamlit (elegida)** | Rápido, 100% Python, en los ejemplos del profesor | Menos control de UX fino |
| Next.js/React | Máximo control de UX | Más trabajo; requiere dominio de React |
| Todo dentro de Superset | Sin capa nueva | Panel ML y chat forzados; auth por rol limitado |

## Consecuencias
- **Positivas:** cubre el §3.5 en un solo lugar; reutiliza la API y Superset existentes; alineado con
  GCP/Docker.
- **Negativas / trade-offs:** agrega carga a C2/C4/C3; el guest token requiere coordinación con
  Superset (C2) y el despliegue (C5).

## Trazabilidad
- Requisitos: REQ-002, REQ-004, REQ-006 · Historias: US-206, US-207 (C2), US-405 (C4), US-305 (C3)
- Diseño: [[03_Architecture/Frontend_Architecture]]
