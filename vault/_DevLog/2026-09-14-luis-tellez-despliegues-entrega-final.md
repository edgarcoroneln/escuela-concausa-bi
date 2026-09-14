---
project: "FARO"
date: "2026-09-14"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — despliegues de la entrega final: redeploy del front #360 a producción (mapas reales, fix de logout, orientación D3/D4, UX de Marina) y hotfix de la imagen de la API del chat (BUG-081 embedding equivocado, BUG-082 geojson faltante en about.py). Ambos verificados en vivo por Luis."
touches: ["BUG-081", "BUG-082", "US-505", "US-641", "US-304", "US-305", "US-601", "ADR-012", "REQ-004", "SEC-006"]
tags: [devlog, equipo-5, deploy, cloud-run, cloud-build, frontend, agente]
---

# DevLog — 2026-09-14 — Despliegues de la entrega final: redeploy del front #360 + hotfix de la imagen de la API (BUG-081, BUG-082)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo|ADR-012]] ·
[[vault/_DevLog/2026-09-13-luis-tellez-login-e2e-redeploy-api|DevLog del login e2e (13-sep)]]

## Contexto

Día de entrega. El código de la entrega ya estaba en `main`, pero **producción corría imágenes
anteriores**. Como Célula 5 (Frontend y deploy) me tocó alinear prod con `main` en dos frentes que
esta sesión cierra documentalmente: el **redeploy del front** (PR #360 de Diana) y un **hotfix de la
imagen de la API** del chat conversacional. Ambos quedaron **verificados en vivo por Luis**; este
DevLog documenta las operaciones de despliegue y el único cambio versionado que traen (`docker/api.Dockerfile`).

## Parte A — Redeploy del front #360 (operación; el código es de Diana, ya en `main`)

El **PR #360 de Diana** (merge `3233bbd8`, ya en `main`) trajo cuatro bloques —mapas reales dibujados
en el navegador con `d3-geo` sin dependencia externa (compatibles con el CSP del proxy), el fix del
botón «Cerrar sesión», la orientación de los drivers D3/D4 en las pantallas que la omitían, y la
auditoría UX de Marina— todos documentados por Diana en
[[vault/_DevLog/2026-09-14-diana-alvarez-menu-sesion-mapas-reales|su propio DevLog]]. El front vivo
era **anterior** a ese merge, así que nada de eso estaba desplegado.

Pasos de despliegue (mi frente), **pin-first**, con GO de Luis:

1. **Validación previa** que Diana no había corrido en su entorno: `vite build` (627 módulos, exit 0)
   y `oxlint` (7 avisos cosméticos, 0 errores). Código sano.
2. **Build de la imagen en Cloud Build** (patrón `cloudbuild-*-hf1`, para no empujar la imagen por el
   enlace local lento): `faro-frontend:main-f968c7a8`, SUCCESS en 38 s. El build hornea
   `VITE_API_ORIGIN` al origen absoluto de la API (BUG-076): Vite congela `import.meta.env.VITE_*` en
   build-time, y ese valor es el que usa el botón de login para que la cookie anti-CSRF caiga en el
   origen correcto. Un hash de bundle distinto al del build local es **esperado** (el build local no
   pasa ese build-arg).
3. **Deploy pin-first**: nueva revisión `faro-frontend-00017-daq` desplegada **al 0 %** con una
   `--tag` de preview. El deploy incremental (solo `--image`) **preserva** las 6 env vars, la cuenta
   de servicio y los recursos del servicio.
4. **Smoke técnico en la URL de preview** (0 % de tráfico): `HTTP 200`; el proxy `/api/` y `/auth/`
   responde idéntico a la API directa (`/api/v1/version` 200, `auth/me` 401 anónimo = arranque
   normal); CSP intacta con los mapas SVG; el bundle sirve el código #360 (el menú ya **no** muestra
   «Iniciar Sesión»); la landing renderiza en el navegador sin errores de CSP.
5. **Corte de tráfico al 100 %** a `faro-frontend-00017-daq` tras el GO de Luis, y reverificación en
   la URL canónica (la que ve el profesor): sirve el bundle #360, menú limpio, proxy vivo, landing OK.

**Resultado — verificado en vivo por Luis (2026-09-14):** login OK, mapas con datos en
Panorama / Selección de Caso / Expediente, «Enclave Georreferenciado» pinea las entidades, «Cerrar
sesión» funciona sin error, y el menú ya no muestra accesos sin ruta real. El front #360 queda
**cerrado (técnico + e2e)**.

Rollback en segundos a la revisión previa `faro-frontend-00015-yoj` (imagen `main-6c26a599`):
`gcloud run services update-traffic faro-frontend --region us-central1 --to-revisions REV=100` con
`REV` = esa revisión.

## Parte B — Hotfix de la imagen de la API del chat (BUG-081, BUG-082)

El chat conversacional (frente C5, 0.5 pts) respondía **«El contexto de FARO no está disponible
temporalmente»**, y la pantalla «Cómo funciona» del front reventaba. La causa estaba en la imagen de
la API, no en el código de `main`, y se corrige en `docker/api.Dockerfile` (mi alcance C5):

- **BUG-081 (high) — embedding equivocado horneado en la imagen.** La imagen horneaba el modelo de
  embeddings `all-MiniLM-L6-v2`, pero el código del agente (`src/agente/recuperacion.py`,
  `NOMBRE_MODELO_EMBEDDINGS`) y la colección de ChromaDB (`indexar_esquema.py`) usan
  `paraphrase-multilingual-MiniLM-L12-v2`. Como el runtime de la API es **OFFLINE**
  (`HF_HUB_OFFLINE`), solo puede cargar un modelo ya cacheado en la imagen; al pedir uno que no estaba,
  la carga fallaba → `ErrorRecuperacion` → el chat devolvía el mensaje de «contexto no disponible».
  **Fix:** hornear el modelo correcto (una sola línea del Dockerfile) + un comentario CRÍTICO que ata
  el nombre al default del código para que no vuelva a divergir.
- **BUG-082 (high) — assets geográficos fuera de `src/` no copiados a la imagen.** La sección «Cómo
  funciona / Modelo de datos» (US-601, `src/api/v1/about.py`) lee dos GeoJSON del disco
  (`superset/assets/geojson/municipios_scope.geojson` y `mexico_silueta.geojson`). Viven **fuera** de
  `src/`, así que el `COPY src/` no los incluía → `GET /api/v1/about/secciones/modelo-datos` daba
  `500` (FileNotFoundError) y la pantalla se rompía. **Fix:** `COPY superset/assets/geojson/` en el
  Dockerfile.

**Build y despliegue.** La imagen se reconstruyó en **Cloud Build** y se desplegó **solo al contenedor
`api`** con deploy pin-first, preservando el sidecar ChromaDB, `SEC-006` (`AUTH_LECTURA_PUBLICA=false`)
y las env vars/secretos: revisión `faro-api-00033-fim` (imagen `main-a8b8f252-hf1`, `/version` reporta
`a8b8f252`, el `src/` de la imagen es intacto respecto a `main`). Rollback a la revisión previa
`faro-api-00031-gom` con el mismo patrón `--to-revisions REV=100`.

**Rotación de credencial (operacional, con OK de Luis; nada de esto vive en el repo).** En el proceso
se detectó que la API key de Anthropic vigente estaba revocada (una prueba de autenticación real
devolvía 401). Luis cargó una versión nueva en **Secret Manager** y el contenedor `api` pasó a
apuntar a esa versión del secreto `anthropic-api-key` vía `--update-secrets`; el sidecar y `SEC-006`
se preservaron. El valor de la credencial **no** pasó por el chat ni queda en ningún archivo del
repositorio (política de secretos del vault).

**Resultado — verificado en vivo por Luis:** el chat responde de nuevo (un ranking de riesgo en
lenguaje natural devolvió 10 escuelas con datos) y el guardrail sigue bloqueando lo destructivo (una
orden de borrar una tabla se rechazó). La pantalla «Cómo funciona» carga. Quedan dos imperfecciones
que **no** son de deploy sino de calidad del agente (`src/agente`, alcance de C2): el redactor es
cauto en algunos conteos y algún Text-to-SQL falla en un driver; se dejan anotadas para C2, fuera del
freeze.

## Alcance y ownership

- **Único cambio de código versionado en este PR:** `docker/api.Dockerfile` (el hotfix de
  BUG-081/BUG-082). Es `docker/**`, verde de C5 (deploy); `DEC-025` además libera mis rutas críticas
  durante S7.
- **`.dockerignore` y `.gcloudignore` (raíz) — usados en el build, NO versionados en este PR.** Reducen
  lo que se sube al daemon de Docker y a Cloud Build (el repo pesa ~4.5 GB por entornos locales que
  ninguna imagen necesita) y documentan **no** excluir lo que copian los Dockerfiles (`src/`,
  `docker/`, `superset/assets/geojson`, `frontend/`). Se usaron para acotar el contexto de este build,
  pero son **archivos de raíz sin dueño en `ownership.yml`** —el mismo hueco ya resuelto para
  `.gitignore`/`.gitattributes`/`requirements.txt` (BUG-039)—, así que `check_ownership` los reprueba
  desde una rama C5 (verificado: rama y título ✅, los 4 archivos de este PR en alcance, solo esos dos
  quedan fuera). **Follow-up:** pedir al PM que los agregue a `comunes` y entonces incorporarlos.
- El **código del front #360 es de Diana** (ya en `main`, documentado en su DevLog); mi Parte A es una
  operación de despliegue, sin cambio de código.
- Ninguna credencial vive en el repositorio.

## Pendientes

- El **dump `bronze_real_2026-09-14`** (solo esquema bronze) quedó verificado y guardado en el bucket,
  **no cargado** el día de entrega (decisión de Luis): cargarlo sería un re-pipeline completo, no un
  swap, y el Gold vivo ya cumple. Se retoma después de la entrega.
- Las dos imperfecciones del redactor/Text-to-SQL del agente son calidad de `src/agente` (C2), no de
  deploy.
- **`.dockerignore`/`.gcloudignore`:** fuera de este PR por el hueco de ownership (archivos de raíz sin
  dueño); follow-up con el PM para agregarlos a `comunes`, mismo patrón que BUG-039. No afectan la
  imagen ya desplegada: solo aligeran futuros builds.
