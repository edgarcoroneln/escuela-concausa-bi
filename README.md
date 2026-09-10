# FARO — Project Vault (SDLC-with-AI Standard)

> Vault estándar para gestionar **todo el ciclo de vida de desarrollo de software asistido por IA**,
> con trazabilidad total entre requerimientos, código, pruebas, seguridad y releases.
>
> **Cómo empezar:** abre [[vault/00_Start_Here/PROJECT_INDEX]].

---

## Qué es este vault

Un sistema de documentación viva (compatible con Obsidian y con cualquier editor Markdown) que
garantiza que **nada quede huérfano**: cada requisito, decisión, bug, hallazgo de seguridad y
sesión de IA tiene un **ID**, un **dueño**, un **lugar** y **enlaces** hacia lo que lo origina y
lo que lo implementa.

Está diseñado para equipos que trabajan con agentes de IA (Claude Code, Codex, Gemini, etc.) y
necesitan **auditar qué hizo la IA**, **cumplir un PRD** y **pasar quality gates** antes de release.

## Principios (ver [[vault/_Meta/Vault_Rules]])

1. **Todo tiene ID y dueño** — `REQ-`, `US-`, `ADR-`, `RISK-`, `SEC-`, `TEST-`, `BUG-`, `TASK-`.
2. **Una sola fuente de verdad por tema** — sin copias duplicadas.
3. **Trazabilidad bidireccional** — `traces_up` / `traces_down` en el frontmatter.
4. **Definition of Filed** — nada está "reportado" hasta tener ID + carpeta + enlace + índice actualizado.
5. **Enforcement > convención** — las reglas se vuelven CI, plantillas de PR y branch protection.

## Mapa del ciclo de vida

| Fase | Carpeta |
|---|---|
| Producto / visión | `vault/01_Product` |
| Requerimientos (general + detallado) + **trazabilidad** | `vault/02_Requirements` |
| Arquitectura + decisiones (ADR) | `vault/03_Architecture` |
| UX / Diseño | `vault/04_UX_Design` |
| Ingeniería (git, DoD, PR, estándares) | `vault/05_Engineering` |
| **Pruebas** (automáticas + físicas/manuales) | `vault/06_Quality_Testing` |
| **Ciberseguridad** | `vault/07_Security` |
| CI/CD & DevOps | `vault/08_CICD_DevOps` |
| **Gobernanza de IA** | `vault/09_AI_Governance` |
| Riesgos / decisiones / incidentes | `vault/10_Risk_Governance` |
| Operación / runbooks / SLOs | `vault/11_Operations` |
| Roadmap & Sprints | `vault/12_Roadmap_Sprints` |
| Reportes ejecutivos & auditorías | `vault/13_Reports` |

Carpetas de soporte: `vault/_Templates` (plantillas), `vault/_DevLog` (bitácora única), `vault/_Meta` (reglas del vault).

## 🚀 Despliegue

### URL de Producción

**Aplicación principal (FARO Web):**
[https://faro-frontend-eanzfglvyq-uc.a.run.app](https://faro-frontend-eanzfglvyq-uc.a.run.app)

**Business Intelligence (Superset):**
[https://faro-superset-eanzfglvyq-uc.a.run.app](https://faro-superset-eanzfglvyq-uc.a.run.app)

**API:** [https://faro-api-eanzfglvyq-uc.a.run.app](https://faro-api-eanzfglvyq-uc.a.run.app)

Las tres superficies se verificaron con HTTP 200 el 8 de septiembre de 2026. FARO Web, los
tableros y las rutas de datos requieren sesión de Google; el healthcheck y la documentación de la
API son públicos.

**Endpoints disponibles** (todos bajo el prefijo `/api/v1/`):
- `GET /api/v1/health` — Health check
- `GET /api/v1/version` — Versión de la API (`api`, `commit`)
- `GET /api/v1/kpis` — KPIs del tablero
- `GET /api/v1/escuelas` · `GET /api/v1/escuelas/{cct}` — Escuelas
- `GET /api/v1/municipios` · `GET /api/v1/municipios/{cve_mun}` — Municipios
- `GET /api/v1/predicciones/{cct}` — Predicción de matrícula de una escuela
- `GET /api/v1/docs` — Documentación interactiva (Swagger UI) con el catálogo completo

**Infraestructura:**
- Platform: Google Cloud Run
- Región: us-central1 (Iowa, USA)
- Proyecto: faro-escuela-sensor
- Organización: luis-g-roses-org
- Límite de instancias: 1 (ambiente de prueba)

**Deploy manual:**
```bash
# Build y push
./vault/08_CICD_DevOps/scripts/build-and-push.sh v0.1.0-s1

# Deploy a Cloud Run
./vault/08_CICD_DevOps/scripts/deploy-cloud-run.sh v0.1.0-s1
```

Ver procedimiento completo: [[vault/08_CICD_DevOps/Cloud_Run_Deploy]]

---

## Cómo adoptar este vault en tu proyecto

Ver [[vault/_Meta/Adoption_Guide]] — reemplaza los placeholders `{{...}}`, asigna dueños y crea tu primer PRD.

---

**Placeholders a reemplazar globalmente:** `FARO`, `Edgar Edmundo Coronel Navarrete`, `https://github.com/edgarcoroneln/escuela-concausa-bi`,
`Python 3.11 · Airflow · dbt · Postgres · Superset · MLflow · FastAPI · Docker · GCP`, `2026-08-01`, `Edgar Edmundo Coronel Navarrete`.
