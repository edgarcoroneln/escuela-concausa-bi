---
project: "FARO"
date: "2026-09-04"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — redespliegue del fix de BUG-046 a producción (rev 00011-hr5) y validación e2e del login real (AC-004.5)"
touches: ["BUG-046", "US-402", "US-403", "US-505", "REQ-004", "REQ-005", "AC-004.5"]
tags: [devlog, celula-5, deploy, cloud-run, oauth2, rbac, bug046, e2e, modo-reparacion]
---

# DevLog — 2026-09-04 — Redespliegue de BUG-046 y login e2e real (AC-004.5)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register|BUG-046]] ·
[[vault/_DevLog/2026-09-04-luis-tellez-bug046-oauth-at-hash|DevLog del fix]] ·
[[vault/_DevLog/2026-09-04-christian-ruiz-revision-bug046-at-hash|Revisión de regla 7 (C4)]]

## Contexto

El fix de `BUG-046` (una línea, `options={"verify_at_hash": False}` en `_verificar_id_token`) ya estaba
en `main`: lo diagnostiqué y validé en local (PR #217), Edgar Coronel (PO) lo mergeó como excepción de
propiedad —toca `src/api/security/**`, alcance C4— y Christian Ruiz (C4) firmó la **revisión de regla 7,
🟢 aprobado sin cambios**, verificándolo de forma independiente (reversión del parche → reprueba con el
mismo `JWTClaimsError` de prod; 66 passed con el parche puesto). En su DevLog dejó dicho explícitamente
que **C5 podía redesplegar sin esperarlo**.

Faltaba lo que ningún check automático prueba: **llevar el parche a producción y ejercitar un login real
de Google end-to-end**. Hasta este redespliegue, prod seguía en la revisión `faro-api-00010-4kn`
(imagen `38be8f2`, sin el fix) → todo login real devolvía 401.

## Qué se hizo

- **Sincronicé `dev/luis-tellez` con `origin/main`** (`git merge`, sin rebase) para construir desde el
  último estado — trajo, entre otras cosas, la propia revisión de regla 7 de C4.
- **Rebuild `linux/amd64` desde contexto limpio de `origin/main` (`33fcbbb`).** `git archive origin/main`
  → `docker buildx build --platform linux/amd64 --build-arg GIT_SHA=33fcbbb… -f docker/api.Dockerfile
  --push` a Artifact Registry (`faro-api:33fcbbb…`). El `--platform` es obligatorio (sin él la imagen
  sale arm64 y no arranca en Cloud Run — aprendizaje de L1/BUG-044); el `--build-arg GIT_SHA` sella
  `/version` con el commit real.
- **`gcloud run services update faro-api --image …:33fcbbb…` (NO deploy completo).** `update --image`
  cambia solo la imagen y **preserva** env vars, secrets, service account (`faro-api-sa`) y VPC connector
  de la revisión anterior → **no re-inyecté `ANALISTA_EMAILS`** (los 2 correos siguen efímeros, solo en
  la revisión, nunca en el repo) ni toqué OAuth/RBAC. → nueva revisión **`faro-api-00011-hr5`** al
  **100 %** del tráfico.

## Cómo lo probé (verificación manual + login e2e real)

`BASE=https://faro-api-eanzfglvyq-uc.a.run.app`

Smoke read-only (yo):

```
/api/v1/version                    → {"commit":"33fcbbba634c…"}   # nueva imagen sellada (era 38be8f2)
/api/v1/health                     → 200
/api/v1/auth/login                 → 302 (→ Google, cadena OAuth intacta)
/api/v1/admin/metrics (sin token)  → 401 (RBAC)
/api/v1/kpis                       → 200 (lectura pública viva)
```

**Login real e2e (Luis Téllez, en su navegador) — cierra AC-004.5:**

| Caso | Esperado | Resultado |
|---|---|---|
| Sin token | 401 | ✅ |
| Analista (correo en `ANALISTA_EMAILS`) | 200 | ✅ |
| Ciudadano (2º correo, fuera de la lista) | 403 | ✅ |

El login real completó por primera vez en producción (el callback devolvió el `TokenPair`), lo que
confirma el fix de `at_hash` **end-to-end**: sin él, el callback moría en 401 antes de emitir token. Con
el token de analista, `/admin/metrics` → 200; con el del segundo correo, → 403. Esta era la única prueba
que faltaba y el mayor riesgo abierto que señalaba C4.

## SEC-007 (aviso de C4)

Christian pidió revisar si en los logs de la nueva revisión aparecía `No se pudo preparar el almacen de
codigos` (degradación del almacén de códigos OAuth a memoria). Búsqueda en los logs de Cloud Run de
`faro-api` (últimas 3 h, término `almacen`): **sin coincidencias**, consistente con un login e2e que sí
usó el almacén de códigos (canje del código opaco de un solo uso). Búsqueda acotada, no exhaustiva.

## Seguridad / calidad

- [x] Imagen sellada con el commit real (`/version`=`33fcbbb`), no `dev`
- [x] `--image` preservó env/secrets/SA/VPC → `ANALISTA_EMAILS` (2) intacto y efímero, sin re-inyección
- [x] Correos de analista **nunca** escritos a repo, plan, memoria ni logs (solo en la revisión y la consola OAuth)
- [x] RBAC verificado end-to-end con cuentas reales: 401 / 200 / 403 (AC-004.5)
- [x] Regla 7 satisfecha antes del redespliegue (revisión firmada de C4, 🟢)
- [x] Rollback disponible: `gcloud run services update-traffic faro-api --region us-central1 --to-revisions faro-api-00010-4kn=100`

## Avisos a otros owners

- **Edgar (PO):** `BUG-046` pasa a `fixed` en `Bug_Register.md` — el redespliegue y el login e2e real
  eran su condición de cierre y ambos ya se cumplieron. La excepción de propiedad quedó ratificada por
  la revisión de regla 7 de C4.
- **Christian (C4):** `SEC-007` sin señal en la nueva revisión; `SEC-009` (propagar el `access_token`
  para *verificar* `at_hash` en vez de desactivarlo) sigue como follow-up low tuyo, no bloqueante para
  la entrega.
- **C5 + PO:** el flip de `AUTH_LECTURA_PUBLICA=false` (`SEC-006`) queda a decisión de producto ahora
  que el login e2e está validado; la recomendación registrada es mantener la lectura pública viva para
  el día D y demostrar RBAC con las cuentas de test, sin cerrar la URL pública.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog.
- **Modificados:** `vault/06_Quality_Testing/Bug_Register.md` (BUG-046 → `fixed` + nota de cierre),
  `vault/_DevLog/_index.md` (fila de este DevLog).
- **Sin cambios de código.** El único cambio en infraestructura fue la nueva revisión de Cloud Run
  (reversible por redespliegue de la anterior).
