---
id: MOC-ROOT
title: "FARO — Índice del Proyecto"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
version: "1.0"
source_of_truth: true
last_reviewed: "2026-09-10"
tags: [index, moc]
---

# FARO — Índice del Proyecto (MOC maestro)

> Punto de entrada único al vault. Desde aquí llegas a todo.
> **Nuestro Faro:** Que ninguna escuela pierda alumnos por una causa que pudimos anticipar y nombrar · **PM:** Edgar Edmundo Coronel Navarrete

> [!IMPORTANT] Recuperación activa — entrega lunes 14, primera hora
> La revisión del profesor del 9-sep no aceptó la entrega. `DEC-022` reabrió S7 hasta el domingo 13.
> Empieza por [[vault/13_Reports/Revision_Profesor_2026-09-09]] y
> [[vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09]].

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

## 🌐 URLs públicas (baseline; deben revalidarse para la entrega del 14)

> **Es lo primero que mira quien evalúa.** La rúbrica exige URL pública viva; sin ella el techo es 6.0.
> Las tres superficies se re-verificaron el **2026-09-08**, después del despliegue final
> documentado en el PR #294 y antes del *code freeze* definitivo.

| Servicio | URL | Acceso | Verificado 2026-09-08 |
|---|---|---|---|
| **FARO Web** · entrada principal | `https://faro-frontend-eanzfglvyq-uc.a.run.app` | **Login con Google obligatorio** | `/` → **200** · `/_stcore/health` → **200** |
| **API** · FastAPI | `https://faro-api-eanzfglvyq-uc.a.run.app` | **Login con Google obligatorio** desde `DEC-018` | `/api/v1/health` → **200** · `/api/v1/kpis` → **401 sin sesión** |
| **Superset** · los 10 tableros | `https://faro-superset-eanzfglvyq-uc.a.run.app` | **Login con Google obligatorio** | `/health` → **200** · botón de Google presente en `/login/` |

> Evidencia de cierre: [[vault/_DevLog/2026-09-08-luis-tellez-despliegue-agente-us305-frontend-main]]
> y [[vault/13_Reports/Cierre_Proyecto_2026-09-08]]. La API desplegada corresponde a la revisión
> `faro-api-00018-gjx`; FARO Web, a `faro-frontend-00009-way` construida desde `main`.

> **Corrección del 2026-09-06.** Esta tabla decía que la lectura de la API era **pública**, y dejó de
> serlo el 5-sep al cerrar `SEC-006`: `DEC-018` puso `AUTH_LECTURA_PUBLICA=false` y **toda ruta de
> datos exige sesión**. Sólo `/api/v1/health` responde sin token. Quien pruebe sin iniciar sesión verá
> **401 en todo** y creerá que está roto: no lo está, es la postura vigente. Se revierte en segundos
> con `AUTH_LECTURA_PUBLICA=true`, **sin rebuild**, si se decidiera reabrir la lectura para la demo.

**Rutas útiles de la API** — todas cuelgan de `/api/v1`, **no de la raíz**:

| Para ver | Ruta |
|---|---|
| Documentación interactiva (Swagger) | `/api/v1/docs` |
| Documentación alterna (ReDoc) | `/api/v1/redoc` |
| Contrato OpenAPI | `/api/v1/openapi.json` |
| KPIs del proyecto | `/api/v1/kpis` |
| Predicción de una escuela | `/api/v1/predicciones/{cct}` |

> **Dos avisos que evitan un 404 en vivo.** La raíz del dominio de la API devuelve 404 —la entrada
> de usuario es FARO Web— y `/docs` tampoco existe en la raíz de la API. La documentación está en
> `/api/v1/docs`, porque `src/api/app.py` monta el contrato bajo ese prefijo.
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

## 🎯 Salud del proyecto — recuperación S7
| Objetivo | Métrica | Meta | Actual |
|---|---|---|---|
| Historias cerradas | `done` / total | 99 / 99 al entregar | **91 / 99**; 3 en progreso y 5 frentes colectivos planeados |
| Superficies públicas | Healthcheck y prueba funcional en candidata | 3 / 3 | Baseline 8-sep: 3/3; candidata S7 pendiente |
| Cumplimiento del PRD interno | Criterios de éxito revalidados | 11 / 11 | **Reabierto**; siete REQ en progreso |
| Evaluación del profesor | Brechas observadas corregidas | 7 / 7 frentes | **0 / 7 aceptados aún**; valida QA el domingo |

> Dictamen vigente: [[vault/13_Reports/Revision_Profesor_2026-09-09]]. El cierre del 8-sep es histórico.
