---
project: "FARO"
date: "2026-09-11"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — botón de login (US-405, ADR-012) sobre el PR #321 ya mergeado, corrección de las 4 pantallas de Vista general pedida por Edgar en esa misma revisión, y un hallazgo de infraestructura en docker-compose.yml encontrado al probar el login."
touches: ["US-405", "ADR-012", "REQ-002"]
tags: [devlog, equipo-5, frontend, react, auth, ownership]
---

# DevLog — 2026-09-11 — Botón de login (US-405) y fix de variables de auth en docker-compose

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo|ADR-012]] ·
[[vault/08_CICD_DevOps/Arquitectura_Frontend_React|Arquitectura_Frontend_React]]

## Contexto

`ADR-012` (Diana Álvarez / Luis Téllez, `accepted`) dejó explícitamente pendiente de E5 el botón/UI
de login: "`Topbar.jsx` hoy no tiene ningún estado de sesión". `frontend/src/lib/api.js` traía desde
el PR #302 (revisión de Edgar) un comentario detallado de por qué se había retirado `getAuthLoginUrl()`
en vez de dejarlo mal armado, con el contrato exacto a seguir cuando se implementara. El PR #321 (Fase
2 de identidad visual) se mergeó hoy (`75e072f`) con dos pendientes de Edgar en esa misma revisión: (1)
construir el botón de login, y (2) rotular con `DemoBadge` los 4 bloques de "Vista general" que seguían
en mock sin ningún aviso en pantalla.

## Qué se hizo

**Corrección inmediata pedida por Edgar (antes del merge del #321).** `VistaGeneral.jsx`: los 4
bloques que seguían en `mock.js` sin rótulo (KPIs de arriba —incluye `escuelas_en_riesgo`—, mapa,
"Matrícula por ciclo", "Distribución por nivel educativo") ya llevan `DemoBadge`, mismo patrón que "El
diferenciador". Commit `c5e4442`, ya mergeado en `main` junto con el resto del #321.

**Botón de login (US-405, ADR-012).** `frontend/src/lib/api.js`: `getAuthLoginUrl()` reconstruido tal
como especificaba el comentario que Edgar dejó en el PR #302 — URL absoluta al origen del API
(`API_ORIGIN`, variable nueva `VITE_API_ORIGIN`, deliberadamente separada de `VITE_API_BASE_URL` para
no romper el proxy same-origin), con `redirect=window.location.origin`. `postAuthExchange(code)` nuevo:
`POST /api/v1/auth/exchange?sesion=cookie`, ruta relativa (sí va por el proxy), nunca toca JWT en JS —
la respuesta es `SesionOut`. `frontend/src/lib/session.jsx` (nuevo): `SessionProvider` — al montar, si
la URL trae `?code_faro=`, lo canjea y limpia el parámetro con `history.replaceState`; siempre pregunta
`getAuthMe()` (un 401 es "no autenticado", no un error). Vive en `App.jsx` (layout raíz) para correr sin
importar en qué ruta caiga la vuelta de Google. `Topbar.jsx` consume la sesión: botón "Iniciar sesión"
si no hay sesión, avatar con iniciales reales + "Cerrar sesión" si la hay.

**Hallazgo de infraestructura, encontrado al probar el botón en vivo.** El flujo fallaba con
`internal_error` (400 real, mal etiquetado — ver más abajo) y después seguía fallando tras corregir el
`.env` local y reiniciar el contenedor. Causa real: el bloque `environment:` del servicio `api` en
`docker-compose.yml` nunca pasaba `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`,
`FRONTEND_REDIRECT_URIS` ni `JWT_SECRET_KEY` al contenedor — y el `.env` de la raíz tampoco se copia ni
se monta dentro de él (`docker/api.Dockerfile` solo copia `src/`). Ningún valor de `.env` local llegaba
nunca al proceso, sin importar cuántas veces se reiniciara o recreara el contenedor con la variable
equivocada. Corregido agregando las 6 variables al bloque `environment:`, con los mismos defaults
inseguros que ya usa `src/api/config.py` para desarrollo local. Verificado con `docker compose up -d
api` + prueba en vivo: el flujo llegó correctamente hasta la pantalla de consentimiento de Google
(`accounts.google.com`, `Error 400: invalid_request — Missing required parameter: client_id`, esperado
porque las credenciales reales de Google siguen vacías a propósito en local).

**Bug secundario encontrado, no corregido aquí (fuera de alcance de E5).** `src/api/app.py`, el mapa
`_ERROR_POR_STATUS` no tiene entrada para `400` — cualquier `HTTPException(400, ...)` (como el rechazo
de `_validar_redirect` en `/auth/login`) cae al mensaje genérico `"internal_error"` en vez de reportar
el 400 real con su detalle. Reportado a Christian (dueño probable de ese hardening, US-404).

## Pruebas ejecutadas

```
Verificación manual en navegador (npm run dev + docker compose up -d api, Diana):
  - Botón "Iniciar sesión" visible en Topbar sin sesión activa.
  - Click → construye https://localhost:8000/api/v1/auth/login?redirect=http://localhost:5173
    → backend valida contra FRONTEND_REDIRECT_URIS → redirige a accounts.google.com con los
    parámetros correctos (client_id vacío en local, error esperado de Google, no del frontend).
  - VistaGeneral.jsx: los 4 bloques en mock muestran su DemoBadge correctamente.
```

No se corrió en este entorno (bash de edición, no el de Diana): `npm run dev` / `docker compose` —
corridos y confirmados por Diana vía capturas de navegador y terminal. `vault_lint.py` corrido en este
entorno: limpio.

## Bloqueantes

Ninguno para este cambio en sí. Dos hallazgos que sí bloquean el login real antes del viernes,
reportados a Christian/Luis por tocar ownership de CI/CD (regla 7):

1. El mismo hueco de `docker-compose.yml` existe en producción: `vault/08_CICD_DevOps/scripts/deploy-cloud-run.sh`
   no incluye `FRONTEND_REDIRECT_URIS` en su `--set-env-vars` — aunque se configure el valor correcto,
   hoy nunca llegaría al Cloud Run real.
2. `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` reales siguen pendientes de Célula 5 — sin ellos el login
   no puede completarse de punta a punta en ningún entorno.

## Próximos pasos

Abrir PR desde `dev/diana-alvarez` (ya sincronizada con `main` tras el merge del #321) para este
commit; coordinar con Christian la URL real de producción del frontend en cuanto exista, para validar
`FRONTEND_REDIRECT_URIS`; solicitar revisión de Luis por tocar `docker-compose.yml` (regla 7).
