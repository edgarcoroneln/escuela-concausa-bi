---
project: "FARO"
date: "2026-09-13"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — cierre del login e2e en prod (BUG-079: la imagen de API desplegada era anterior a la sesión por cookie de ADR-012) mediante redeploy de la API desde `main`, más dos endurecimientos de scripts de deploy (BUG-078 cpu-throttling, BUG-080 --platform amd64). Verificado en vivo por Luis."
touches: ["BUG-079", "BUG-078", "BUG-080", "US-405", "ADR-012", "ADR-010", "REQ-004", "REQ-005", "SEC-006", "BUG-075", "BUG-076"]
tags: [devlog, equipo-5, deploy, auth, login, ci-cd, cloud-run]
---

# DevLog — 2026-09-13 — Login e2e cerrado en prod: la imagen de la API era anterior a la sesión por cookie (BUG-079)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo|ADR-012]] ·
[[vault/07_Security/Threat_Model|Threat_Model]]

## Contexto

El **login e2e en producción era el último bloqueante del camino crítico** de la entrega: con
`SEC-006` activo (`AUTH_LECTURA_PUBLICA=false`) todas las pantallas de datos responden `401` hasta
que hay sesión. Los dos gemelos previos ya estaban resueltos y desplegados: `BUG-075`
(`FRONTEND_REDIRECT_URIS` al Cloud Run) y `BUG-076` (`VITE_API_ORIGIN` horneado en el build del
front). Al probar el flujo completo en vivo, Luis reportó el síntoma: **pasaba el login de Google y
regresaba al portal sin sesión** — siempre el botón «Iniciar sesión», las cifras con «No se pudieron
cargar las cifras del API (401)», nunca su nombre arriba.

## Diagnóstico — BUG-079 (critical)

El front estaba **bien**; el desalineado era la API. La imagen de la API en prod era
`agente-457715a` (del 8-sep), **anterior al PR #304 / ADR-012** que introdujo la sesión por cookie:

- No contenía `src/api/security/cookies.py` (no existía `sembrar_sesion`).
- Su `POST /auth/exchange` **ignoraba** `?sesion=cookie` y solo devolvía `TokenPair` JSON.
- Su `get_current_user` leía **solo** el encabezado `Bearer`, nunca la cookie `faro_sesion`.

Consecuencia: aunque el front canjeara el `code_faro`, la API **nunca sembraba** la cookie de sesión,
así que `GET /auth/me` devolvía `401` permanente → el `SessionProvider` marcaba `anonimo`. Front
(`react-d10ce60`) y API (`457715a`) estaban **desalineados**.

Verificación de que el front no tenía culpa (inspección del bundle desplegado):

- `VITE_API_ORIGIN` horneado al origen real de la API (login navega directo → la cookie anti-CSRF
  `faro_oauth_state` cae en el origen de la API, no en el del front — el diseño Camino B, BUG-059).
- `POST /api/v1/auth/exchange?sesion=cookie` **relativo** (por el `proxy_pass` de nginx → la cookie
  `faro_sesion` cae en el origen del front, mismo-origen).
- `SessionProvider` detecta `?code_faro=`, canjea, limpia la URL con `history.replaceState` y llama
  `getAuthMe()`. Todo correcto.

## Fix — redeploy de la API desde `main` (operacional, sin cambio de código)

`main` (`6896255`) **sí** trae la sesión por cookie (`cookies.py`, el modo `sesion=cookie` en
`/exchange`, y `get_current_user` que lee la cookie — el propio `require_lectura` cita ADR-012 y el
frontend React en su docstring) y **sí** trae las dependencias del agente en `docker/api.Dockerfile`.
Pasos ejecutados:

1. **Build + push** de la imagen desde `main`: `faro-api:agente-6896255` (`--platform linux/amd64`,
   `GIT_SHA` horneado). Las capas pesadas (torch, sentence-transformers, modelo) venían en caché.
2. **Deploy pin-first** para verificar antes de exponer: clavé el tráfico a la revisión sana
   (`faro-api-00019-2xs`), desplegué la imagen **solo al contenedor `api`**
   (`--container=api --image=...`) → nueva revisión `faro-api-00020-nwg` **al 0%**. El swap de un solo
   contenedor **preserva el sidecar ChromaDB** (`faro-chroma-sidecar:agente-9a654d4`), `SEC-006` y las
   18 env vars/secretos (no pasé banderas de entorno).
3. **Verificación en la URL de preview** (0% de tráfico): `/version=6896255`, `/health=200`,
   `SEC-006 /kpis=401`, `exchange?sesion=cookie` con code inválido → **`401` limpio** (no `500`),
   revisión `Ready=True` con `ContainerHealthy=True` (incluye el sidecar).
4. **Corte de tráfico** al 100% a `00020-nwg` (`--to-latest`) y reverificación en la URL de prod.

### Confirmación del contrato de acceso (código de `6896255`)

`/kpis`, `/escuelas`, `/predicciones`, `/agente` cuelgan de `require_lectura`, que con
`AUTH_LECTURA_PUBLICA=false` exige **cualquier** usuario autenticado (no distingue rol) y **lee la
cookie `faro_sesion`**. No hay whitelist de login en la API: cualquier cuenta de Google entra como
mínimo `ciudadano`, y `ciudadano` ya ve las cifras de la home. Solo `/admin/*` pide `analista`.

### Resultado — login e2e CERRADO

**Luis verificó en vivo (2026-09-13): tras el login de Google aparece su nombre arriba y las cifras
de la home cargan.** La cadena Camino B completa (state cookie en la API → `code_faro` → exchange modo
cookie → `faro_sesion` en el front → `/auth/me` `200`) funciona en producción.

Rollback disponible en segundos: `gcloud run services update-traffic faro-api
--to-revisions=faro-api-00019-2xs=100`.

## Dos endurecimientos de scripts de deploy encontrados en el camino

- **BUG-078** — `deploy-cloud-run-frontend.sh` heredaba el `--no-cpu-throttling` del Streamlit previo
  y Cloud Run rechaza `256Mi` con la CPU siempre asignada (`Total memory < 512 Mi is not supported
  with cpu always allocated`). Fix: fijar `--cpu-throttling` (nginx es request-driven). De paso,
  reescribí el comentario del encabezado, que aún describía el modelo CORS/`VITE_API_BASE_URL`
  anterior a Camino B.
- **BUG-080** — `build-and-push.sh` no fija `--platform linux/amd64`. En un host arm64 (Docker Desktop
  en Mac Apple Silicon) eso construye una imagen arm64 que Cloud Run (amd64) no puede ejecutar. Tuve
  que añadir el flag a mano para reconstruir la API esta sesión; lo dejo en el script para que sea
  correcto por defecto (en CI/hosts amd64 es no-op).

## Alcance y pendientes

- **Único cambio versionado:** los dos scripts de deploy (`vault/08_CICD_DevOps/scripts/`, mi alcance
  verde). El fix del login fue **operacional** (redeploy de una imagen ya mergeada en `main`), sin
  tocar código de producción ni credenciales.
- **Recordatorio (fuera de mi alcance):** actualizar `vault/02_Requirements/Traceability_Matrix.md`
  (crítico de Edgar) con `BUG-078/079/080`.
- **Escalado pendiente:** `BUG-077` (`GET /api/v1/municipios` → `500` por `nombre_entidad` nulo en
  ~97% de municipios; dueños Diana C1 dbt + Christian C4 API), ya registrado por QA el 12-sep.
