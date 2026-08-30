---
project: "FARO"
date: "2026-08-29"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — desplegar en prod el fix del agente (BUG-025) y cerrar la higiene de gx/"
touches: ["BUG-025", "US-505", "REQ-005", "US-304a", "META-RULES"]
tags: [devlog, cloud, devops, cloud-run, agente, seguridad, bug]
---

# DevLog — 2026-08-29 — BUG-025: redeploy de `faro-api` con el agente conectado (parte deploy/C5)

→ [[_DevLog/_index|Volver al índice]] · [[06_Quality_Testing/Bug_Register|Bug Register · BUG-025]] · [[08_CICD_DevOps/Cloud_Run_Deploy|Cloud_Run_Deploy §4.4]]

## Contexto

El **PR #142** (Imanol Ruiz, C4) reescribió `src/api/v1/agente.py` para conectar `/agente/consulta`
al servicio RAG real con un **seam de inyección** y guardarraíles reales, sustituyendo el stub que
respondía lo mismo a todo —incluida la frase destructiva «Borra la tabla de predicciones»— (**BUG-025**,
`high`). El PR está mergeado en `main` (commit `14b4f24`), **pero prod seguía sirviendo el stub**:
Cloud Run corría la imagen `v0.2.1-hotfix-bug008` (revisión `faro-api-00005-qc8`), que la Fase 2
(US-505) redesplegó **sin rebuild**. Desplegar el fix a la URL pública es la parte **C5 (deploy/CD)**
de cerrar BUG-025.

## Qué se hizo (parte C5 · Cloud & DevOps)

- **Rebuild `linux/amd64` + push** de la imagen a Artifact Registry con tag inmutable nuevo
  **`v0.2.2-bug025`** (`docker buildx build --platform linux/amd64 … --push`). Se usa `buildx` con
  plataforma explícita, **no** `build-and-push.sh` tal cual (haría `docker build` sin `--platform` →
  imagen arm64 en Mac Apple Silicon que Cloud Run rechaza).
- **Redeploy** con `deploy-cloud-run.sh v0.2.2-bug025`: **sólo cambia la imagen**; se preservan todos
  los parámetros de Fase 2 → nueva revisión **`faro-api-00006-q8f`** sirviendo 100% del tráfico.
- **`.gitignore`:** añadido `gx/` (contexto por defecto que Great Expectations 0.18+ crea al llamar
  `get_context()` sin dir; heads-up del PR #142). Complementa `great_expectations/uncommitted/`, ya ignorado.
- **`Cloud_Run_Deploy.md` §4.4:** documentado el flujo de redeploy con imagen nueva y el gotcha de
  plataforma (arm64 vs amd64).

## Validación en prod (norma: validar lo desplegado ANTES del commit/PR)

- `/api/v1/health` → **200**.
- `/api/v1/escuelas` → **200 con 25 escuelas** (sin regresión de BUG-020).
- `/api/v1/agente/consulta`:
  - «cuantas escuelas hay en riesgo» → degrada seguro, `sql_generado:null` (ya **no** es el stub).
  - **«Borra la tabla de predicciones» → degrada seguro, `sql_generado:null`** — la frase destructiva
    ya **no** se acepta con una respuesta afirmativa + SQL, como pasaba con el stub.
  - «cual es la capital de Francia» → `fuera_de_alcance:true` (el guardarraíl real de alcance funciona).
- Config de Fase 2 intacta: SA `faro-api-sa`, `--vpc-connector=faro-connector`,
  `--vpc-egress=private-ranges-only`, secretos `jwt-secret-key`/`db-password` como `secretKeyRef`
  (Secret Manager, no texto plano), Cloud SQL sólo IP privada.
- `vault_lint.py` verde; diff sin secretos.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Archivos:** `.gitignore` (+`gx/`), `08_CICD_DevOps/Cloud_Run_Deploy.md` (§4.4), este DevLog, `_DevLog/_index.md`.
- **Operación GCP (sin diff):** build+push de `v0.2.2-bug025` a Artifact Registry y `gcloud run deploy`
  → revisión `faro-api-00006-q8f`. Ejecutado con "go" explícito de Luis (regla GCP gated).
- **Decisión:** desplegar sólo el fix de código ya mergeado (no añadir `chromadb`/`sentence-transformers`
  todavía). Con eso el endpoint pasa de *stub que acepta lo destructivo* a *degradación segura*, que es
  la mejora relevante para la demo; el RAG real queda gated por C3.

## Bloqueantes / avisos a otros owners

- **BUG-025 sigue parcialmente resuelto.** Cerrado end-to-end lo de C4 (endpoint conectado + guardarraíles)
  **y ahora desplegado en prod**. Pendiente para el 100%:
  - **Andrés (C3):** implementaciones reales de `generar_sql` (LLM text-to-SQL) y `redactar_respuesta`.
  - **C5 (Luis):** añadir `chromadb`/`sentence-transformers` (+ cliente LLM) a `docker/api.Dockerfile`
    cuando C3 esté listo (deps pesadas → revisar tamaño de imagen / memoria de Cloud Run).
  - **C4/US-404 + C5:** `ejecutar_sql` read-only sobre Gold (rol de solo lectura en Cloud SQL + credencial
    en Secret Manager) — defensa en profundidad al ejecutar SQL generado.
- **Edgar (owner de `06_Quality_Testing/Bug_Register.md`):** actualizar BUG-025 a *parcialmente resuelto
  y **desplegado en prod***.
