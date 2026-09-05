---
id: MOC-ROOT
title: "FARO — Índice del Proyecto"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
version: "1.0"
source_of_truth: true
last_reviewed: "2026-08-01"
tags: [index, moc]
---

# FARO — Índice del Proyecto (MOC maestro)

> Punto de entrada único al vault. Desde aquí llegas a todo.
> **Nuestro Faro:** Que ninguna escuela pierda alumnos por una causa que pudimos anticipar y nombrar · **PM:** Edgar Edmundo Coronel Navarrete

## 🚀 Empieza aquí
- [[vault/00_Start_Here/Developer_Onboarding]] — configurar entorno y flujo
- [[vault/00_Start_Here/How_To_Navigate]] — cómo se organiza y enlaza el vault
- [[vault/00_Start_Here/Glossary]] — términos del dominio
- [[CLAUDE]] — contexto del proyecto para agentes de IA (Claude Code)
- [[AGENTS]] — protocolo de trabajo y de handoff entre LLMs: cómo pasar el contexto de un asistente a otro para que sobreviva a los límites de tokens y a los cambios de asistente
- [[GEMINI]] — apuntador de contexto para Gemini CLI (redirige a AGENTS.md)
- `.cursorrules` — apuntador equivalente para **Cursor** (redirige a AGENTS.md; sin frontmatter porque no es `.md` del vault)
- `.github/copilot-instructions.md` — apuntador equivalente para **GitHub Copilot** (redirige a AGENTS.md; sin frontmatter porque no es `.md` del vault)
- [[vault/00_Start_Here/Vault_Changelog]] — cambios del vault

## 🌐 URLs públicas (demo del 9 de septiembre)

> **Es lo primero que mira quien evalúa.** La rúbrica exige URL pública viva; sin ella el techo es 6.0.
> Las dos rutas de abajo se verificaron respondiendo el 2026-09-05.

| Servicio | URL | Acceso | Verificado |
|---|---|---|---|
| **API** · FastAPI | `https://faro-api-eanzfglvyq-uc.a.run.app` | Lectura **pública** | `/api/v1/health` → 200 |
| **Superset** · los 10 tableros | `https://faro-superset-eanzfglvyq-uc.a.run.app` | **Login con Google obligatorio** | `/health` → 200 · botón de Google presente en `/login/` |

**Rutas útiles de la API** — todas cuelgan de `/api/v1`, **no de la raíz**:

| Para ver | Ruta |
|---|---|
| Documentación interactiva (Swagger) | `/api/v1/docs` |
| Documentación alterna (ReDoc) | `/api/v1/redoc` |
| Contrato OpenAPI | `/api/v1/openapi.json` |
| KPIs del proyecto | `/api/v1/kpis` |
| Predicción de una escuela | `/api/v1/predicciones/{cct}` |

> **Dos avisos que evitan un 404 en vivo.** La raíz de ambos dominios **no sirve nada**: `/` devuelve
> 404 en la API y FARO Web aún no está desplegado. Y `/docs` **tampoco existe** en la raíz — la
> documentación está en `/api/v1/docs`, porque `src/api/app.py` monta todo bajo ese prefijo.
>
> Superset **no admite acceso anónimo**: quien vaya a abrirlo debe tener su correo en la lista blanca
> del SSO antes de la demo (`SUPERSET_SSO_ALLOWED_EMAILS`). Si no está, el login con Google funciona
> y aun así lo rechaza. Detalle en [[vault/08_CICD_DevOps/Cloud_Run_Deploy]] §5.1 y en
> [[vault/_DevLog/2026-09-05-luis-tellez-superset-sso-google]].

## 🧭 Ciclo de vida (carpetas)
| # | Carpeta | Contenido |
|---|---|---|
| 01 | [[vault/01_Product/_index]] | Visión, PRD, OKRs, personas |
| 02 | [[vault/02_Requirements/_index]] | Requisitos general/detallado + **Matriz de trazabilidad** |
| 03 | [[vault/03_Architecture/_index]] | System design, data model, API, ADRs |
| 04 | [[vault/04_UX_Design/_index]] | Design system, pantallas, accesibilidad |
| 05 | [[vault/05_Engineering/_index]] | Workflow, DoD, PR, estándares |
| 06 | [[vault/06_Quality_Testing/_index]] | Pruebas automáticas + físicas + bugs |
| 07 | [[vault/07_Security/_index]] | Ciberseguridad y cumplimiento |
| 08 | [[vault/08_CICD_DevOps/_index]] | Pipeline, gates, deploy, release |
| 09 | [[vault/09_AI_Governance/_index]] | Gobernanza de agentes IA |
| 10 | [[vault/10_Risk_Governance/_index]] | Riesgos, decisiones, incidentes |
| 11 | [[vault/11_Operations/_index]] | Runbooks, monitoreo, SLOs |
| 12 | [[vault/12_Roadmap_Sprints/_index]] | Roadmap y sprints |
| 13 | [[vault/13_Reports/_index]] | Dashboards y auditorías |

## 🛠 Soporte
- [[vault/_Templates/_index]] — plantillas
- [[vault/_DevLog/_index]] — bitácora única
- [[vault/_Meta/_index]] — reglas del vault y trazabilidad

## 🎯 Salud del proyecto (rellenar)
| Objetivo | Métrica | Meta | Actual |
|---|---|---|---|
