---
project: "FARO"
date: "2026-09-06"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — regresión del shell tras un redeploy limpio (Dashboards y Panel ML rotos) diagnosticada y corregida con una imagen combinada; se versiona el Dockerfile del frontend y se documenta la deuda de reproducibilidad de C2"
touches: ["US-526", "BUG-059", "REQ-002", "REQ-005", "AC-002.1"]
tags: [devlog, celula-5, frontend, streamlit, cloud-run, dashboards, embebido, reproducibilidad, despliegue]
---

# DevLog — 2026-09-06 — Imagen combinada del frontend: regresión del shell corregida y Dockerfile versionado

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/_DevLog/2026-09-06-luis-tellez-superset-charts-timeseries-guest|Charts timeseries]] · [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Deploy a Cloud Run]]

## Contexto

El shell FARO Web (US-526, Streamlit) une en una sola URL pública: login OAuth (US-405), **dashboards de
Superset embebidos** (US-206), Panel ML (US-207) y chat (US-305). El CÓDIGO del shell (`src/frontend/`) es
de **C2 (Manuel/Marina)**; C5 solo lo conteneriza y despliega, igual que la API.

El redeploy anterior del frontend (**rev `faro-frontend-00004-nkt`**) bajó el fix de sesión **BUG-059**
(`auth.py`, ya en `main` vía PR #267: refresca el token con margen de 120 s para que la sesión sobreviva la
demo). Se construyó **desde `origin/main` limpio** para traer ese fix. Tras el deploy, en producción
**dejaron de verse los Dashboards y el Panel ML dejó de responder** — una regresión.

## Causa raíz (confirmada con evidencia)

Las correcciones de embebido de C2 (`superset_client.py` reescrito al contrato guest-token + `1_Dashboards.py`
al Embedded SDK de Superset) **nunca se commitearon a `main`**: vivían **sin commitear** en el working tree y
estaban horneadas en la imagen que sí funcionaba (`00003-594`) vía `COPY src/frontend/`. Al reconstruir desde
`origin/main` para traer BUG-059, se trajo el **`superset_client.py` viejo de `main`** (188 líneas, "uuid
regular + guest_token en la URL, no autentica") ⇒ los tableros no montan. Verificado con datos:

- `origin/main:src/frontend/superset_client.py` = **188 líneas**, 0 marcadores del contrato de embebido.
- `origin/main:src/frontend/pages/1_Dashboards.py` = **88 líneas**, sin `@superset-ui/embedded-sdk`.
- La versión correcta (embebido) = **265 líneas** de `superset_client.py`, solo en el working tree.

El Panel ML de `main` usa `token_de_acceso()` (correcto); su "no responde" fue por **sesión perdida en el
cold-start** del deploy (SEC-006 exige token, `AUTH_LECTURA_PUBLICA=false`), no por un defecto de código.

## Qué se hizo (operación de despliegue — imagen combinada)

Decisión de Luis: **"imagen combinada primero"** — no dejar prod rota; construir y probar en LOCAL una imagen
que una BUG-059 (de `main`) con el embebido (del working tree), y desplegar una sola vez ya probada.

1. **Fusión, base = `main`:** worktree efímero sobre `origin/main` (`b2be5c5`) + se portaron **solo**
   `superset_client.py` y `1_Dashboards.py` del embebido; `1_Dashboards.py` con el único ajuste
   `current_user()` → `encabezado()` (unifica el bloque de sesión BUG-059 con las otras páginas; seguro:
   `encabezado()` sin sesión emite `st.sidebar.info` + `login_button`, no `warning`/`error`). `auth.py`,
   `app.py`, `2_Panel_ML.py`, `3_Chat.py` = `main` (BUG-059) intactos.
2. **Pruebas:** **45 pruebas de frontend en verde** (contenedor `python:3.11`, streamlit 1.62.0 + httpx 0.28.1).
   Verificación local de Luis (login + sesión + Panel ML). Los Dashboards **no se validan en local** a
   propósito: `superset_client._embedded_uuid()` reescribe `allowed_domains` en cada montaje, así que apuntar
   el front local a Superset de prod **sobrescribiría** la config de prod (y localhost no está en CORS) ⇒ el
   contenedor local corre **sin** `SUPERSET_*` (Dashboards "no disponible" a propósito) y los Dashboards se
   validan en PROD.
3. **Deploy (autorizado por Luis):** rebuild `--platform linux/amd64` (Cloud Run exige amd64) → imagen
   `faro-frontend:embed-combo-b2be5c5` (digest `sha256:26b2789576d3659c8074a40e8d63653f8a7b386008ddece505a015b02e214c6b`,
   sello `GIT_COMMIT=b2be5c5`) → **rev `faro-frontend-00005-6vs`**, 100 % de tráfico. Env-vars y secreto de
   Superset **preservados** (merge, no reemplazo).
4. **Se versiona el Dockerfile del frontend (este PR):** `docker/frontend.Dockerfile` y
   `docker/frontend-requirements.txt` estaban **untracked** (solo en el working tree local) ⇒ la imagen no era
   reproducible desde git por el lado de C5. Con este DevLog se suben al repo (alcance C5, `docker/**`).

## Cómo se probó

- **Local:** 45/45 pruebas de frontend verdes; home y `/_stcore/health` 200; login + sesión + Panel ML
  verificados por Luis.
- **Smoke en PROD (rev 00005-6vs):** `/_stcore/health` 200, home 200, `/auth/login?redirect=<front>` **302**
  (allowlist OK), sello de imagen `embed-combo-b2be5c5`, 6 env-vars + secreto de Superset intactos.
- **En vivo, por Luis:** confirma que **Dashboards montan y Panel ML responde** en producción ("ya funciona").

## Diagnósticos / aprendizajes

- **Un redeploy "limpio desde `main`" no es seguro mientras código en producción viva sin commitear.** La
  imagen que servía Dashboards dependía de `COPY src/frontend/` sobre un working tree con cambios no
  versionados; reconstruir desde `main` los perdió. La reproducibilidad exige que **todo lo que corre en prod
  esté en `main`**.
- **Los dos conjuntos de sesión no se mezclan a ciegas:** `main` = `encabezado()` + `token_de_acceso()`
  (BUG-059, token en `st.session_state["access_token"]`, refresco a 120 s); working tree previo =
  `current_user()` + `st.session_state.get(...)`. `superset_client.py` es **autónomo** (no importa `auth`) ⇒
  portable limpio; `1_Dashboards.py` sí toca `auth`, por eso el ajuste `current_user()`→`encabezado()`.

## Seguridad / calidad

- [x] **Este PR NO toca código de C2** (`src/frontend/**`) ni de C4/C2 ya mergeado (BUG-059): sube solo
  `docker/**` (alcance C5) + este DevLog + su fila de índice (comunes). El gate de propiedad pasa.
- [x] **No se tocaron env-vars de seguridad:** `AUTH_LECTURA_PUBLICA=false` (SEC-006), SSO/whitelist de
  Superset, CORS y redirect URIs intactos. Los correos de login siguen **efímeros** solo en la revisión de
  Cloud Run, nunca en archivo.
- [x] **Cero secretos** en repo/chat/DevLog: el `superset-admin-password` se leyó de Secret Manager en la
  terminal y **nunca** se imprimió ni se escribió a archivo.
- [x] **Reversible:** `gcloud run services update-traffic faro-frontend --region us-central1 --to-revisions faro-frontend-00003-594=100`.

## Avisos a otros owners

- **C2 (Manuel / Marina) — bloquea la reproducibilidad, no la demo (prod ya funciona):** el embebido corre hoy
  en prod horneado desde el working tree; para que un rebuild desde `main` no vuelva a regresar los Dashboards,
  **hay que commitear a `main` desde la rama de C2**: `src/frontend/superset_client.py` (265 líneas, contrato
  guest-token), `src/frontend/pages/1_Dashboards.py` (Embedded SDK, con `encabezado()` — la versión desplegada),
  y los dos tests actualizados (`tests/test_frontend_superset_client.py`,
  `tests/test_frontend_dashboards_streamlit.py`). Los archivos exactos quedan en el handoff
  `_local/handoff_embedding_c2_2026-09-06/`. **C5 no puede llevarlos** (`src/frontend/**` es alcance de C2; el
  gate de propiedad reprueba sin bypass posible).
- **PO (Edgar):** merge de este DevLog + Dockerfile del frontend (solo `docker/**` + comunes). Cierra la parte
  C5 de la deuda de reproducibilidad; la parte C2 (arriba) va por la rama de Manuel.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog; `docker/frontend.Dockerfile` y `docker/frontend-requirements.txt` se versionan
  (existían untracked); handoff `_local/handoff_embedding_c2_2026-09-06/` (fuera del repo, para C2).
- **Modificados:** `vault/_DevLog/_index.md` (fila de este DevLog).
- **Infra GCP (sin cambio de imagen de seguridad):** rev `faro-frontend-00005-6vs` con imagen
  `faro-frontend:embed-combo-b2be5c5`; env-vars y secreto de Superset preservados.
- **Sin cambios de código** de aplicación (`src/`) en este PR.
