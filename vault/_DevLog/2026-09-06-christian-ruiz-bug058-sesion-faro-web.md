---
project: "FARO"
date: "2026-09-06"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — P0 del PO: la sesión de FARO Web no sobrevivía a la demo"
touches: ["BUG-058", "US-405", "US-207", "US-305", "REQ-004"]
tags: [devlog, celula-4, frontend, sesion, oauth2, refresh, bug058]
---

# DevLog — 2026-09-06 — La sesión de FARO Web no sobrevivía a la demo (BUG-058)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register|BUG-058]] ·
[[vault/03_Architecture/ADRs/ADR-010-puente-oauth-frontend|ADR-010]]

## Contexto

El PO reportó tres defectos en `src/frontend/auth.py` y los llamó P0 con razón: *"este es el que
puede tumbar la demo, no el que se ve peor"*. Verifiqué los tres antes de tocar nada. **Los tres
son ciertos**, y hay un cuarto por la misma causa.

## Qué se hizo

### 1. El que tumbaba la demo: el token moría a media presentación

`auth.py` guardaba el `refresh_token` y **nunca lo usaba**. Cero llamadas a `/auth/refresh` en todo
el front. El access token dura **15 minutos** (`src/api/config.py:33`) y la demo dura más: iniciar
sesión en la preparación significaba llegar a la sala sin sesión.

`token_de_acceso()` refresca con **120 s de margen**, usando el `expires_in` que la API ya devolvía
y el front tiraba a la basura. Sin ese dato no hay forma de saber cuándo refrescar — por eso el
arreglo empieza por guardarlo.

Dos decisiones sobre los errores, y son opuestas a propósito:

- **La API rechaza el refresh** (expirado, revocado) → se **cierra la sesión**. Mejor mostrar
  "Inicia sesión" que dejar a la persona con un token muerto que da 401 en cada página.
- **La API no responde** (corte de red) → **no se toca la sesión**. Puede ser pasajero y el access
  token actual quizá siga sirviendo. Tirar la sesión por un timeout sería peor que el problema.

### 2. Las páginas internas no tenían encabezado de sesión

`logout_button()` vivía solo en `app.py:25`. Quien entraba directo a Dashboards, Panel de ML o Chat
no veía con quién estaba dentro ni podía cerrar sesión.

`encabezado()` unifica el bloque: **una línea por página**. `app.py` también lo usa, así que el
comportamiento es el mismo en las cuatro y no hay dos copias que se separen.

**No cambia quién entra.** Solo muestra el estado; cada página sigue decidiendo si exige rol. El
Panel de ML sigue de lectura pública, como está decidido.

### 3. El token que nunca viajó (defecto de contrato, mío)

`2_Panel_ML.py:142` mandaba `(user or {}).get("access_token")`. Pero `/auth/me` devuelve
`sub`/`email`/`name`/`role` y **nunca** el token: era `None` **siempre**. Hoy no se nota porque la
lectura es pública; el día que deje de serlo, la página daría 401 con sesión iniciada.

`3_Chat.py:34` leía `st.session_state["access_token"]` directo — el mismo problema por otra puerta:
devuelve el token guardado aunque ya haya expirado. Las dos ahora piden `token_de_acceso()`.

## Lo que NO se pudo arreglar, y por qué

El PO pidió que **la sesión sobreviva a recargar y a abrir en otra pestaña**. No se logró, y
prefiero que quede escrito antes de que alguien lo descubra el día 9.

`st.session_state` vive en la sesión del websocket de Streamlit: recargar crea una sesión nueva y
el estado se pierde. Las tres salidas posibles:

| Opción | Por qué no |
|---|---|
| **Cookie puesta por la API** | La API está en `faro-api-…run.app` y el front en `faro-frontend-…run.app`. **`run.app` está en la Public Suffix List**, así que el navegador **rechaza** una cookie de `.run.app`. No es cuestión de esfuerzo: es imposible |
| **Componente de terceros para cookies** | Funciona, pero es una dependencia nueva en el camino del login **el día del freeze**. Si falla en Cloud Run, no hay demo |
| **Token en la URL** | Lo prohíbe ADR-010, y con razón: queda en el historial, en los logs del proxy y en el `Referer` |

Streamlit 1.62 sí tiene `st.context.cookies`, pero es **solo lectura**: puede leer cookies, no
ponerlas. No sirve sin componente.

**Lo que sí se consiguió** es que recargar deje de parecer un error: el encabezado muestra "Inicia
sesión" y, como Google ya dio el consentimiento, es un clic y ~2 segundos. Es degradación limpia,
no persistencia. Queda como follow-up post-freeze.

Nota de alcance sobre el reporte: abrir una página en pestaña propia es un caso de prueba, no el de
la demo — navegando por el menú lateral la sesión se conserva. El de recargar sí es realista.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Modificados:** `src/frontend/auth.py`, `src/frontend/app.py`,
  `src/frontend/pages/{1_Dashboards,2_Panel_ML,3_Chat}.py`, `tests/test_frontend_auth.py`,
  `vault/06_Quality_Testing/Bug_Register.md`, `vault/_DevLog/_index.md`.
- **Creados:** este DevLog.

## Seguridad / calidad

- [x] `tests/test_frontend_auth.py` 12 → **20 casos**
- [x] **Las 3 pruebas del refresco reprueban con el código anterior** — comprobado desactivándolo
- [x] Suite de frontend completa (los 3 archivos) → **23 passed**
- [x] `ruff check .` sobre todo el repo → limpio
- [x] Ningún cambio en quién puede entrar: no se tocó `require_role` ni las guardas de las páginas

## Bloqueantes / avisos a otros owners

- **Marina García (C2):** toqué **una línea** de `2_Panel_ML.py` (el origen del token) porque el
  arreglo real vive en `auth.py` y partirlo habría dejado la página a medias. El resto de la página
  no cambia. Si prefieres llevarlo tú, revierto esa línea y te paso la firma.
- **Manuel Serranía (C2):** `encabezado()` se suma al contrato de `auth.py` que acordamos. Las
  firmas viejas (`current_user`, `login_button`, `logout_button`, `require_role`) **no cambian**.
- **Luis Téllez (C5):** el front desplegado necesita `FARO_API_BASE_URL` y `FARO_FRONTEND_URL`
  apuntando a las URLs reales, y esta última debe estar en `FRONTEND_REDIRECT_URIS` de la API o
  `/auth/login` responde 400.
- **La API sigue en `33fcbbb`.** Nada de esto —ni BUG-053, ni BUG-055, ni esto— está en producción.

## Próximos pasos

1. Redeploy de la API y del front (C5).
2. Login e2e real, ahora con la sesión sobreviviendo los 15 minutos.
3. Persistencia entre recargas: follow-up post-freeze, requiere componente de cookies.
