---
project: "FARO"
date: "2026-09-12"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — inyección de VITE_API_ORIGIN en el build del front React (BUG-076), el gemelo del lado cliente de BUG-075. Sin tocar prod, credenciales ni api.js."
touches: ["BUG-076", "US-405", "ADR-012", "REQ-004"]
tags: [devlog, equipo-5, deploy, frontend, build, auth, ci-cd]
---

# DevLog — 2026-09-12 — BUG-076: el build del front no inyecta `VITE_API_ORIGIN`

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo|ADR-012]] ·
[[vault/07_Security/Threat_Model|Threat_Model]]

## Contexto

Preparando el runbook del redeploy del front React (bloqueante 3 del login e2e) encontré el **gemelo
del lado cliente de BUG-075**: aunque la API ya acepte el `redirect` del front (BUG-075) y las
credenciales de Google estén bien, el login e2e **seguiría fallando con 401** porque el build del
front nunca hornea `VITE_API_ORIGIN`.

El botón de login del React usa esa variable para construir una URL **absoluta** al origen de la API
(`frontend/src/lib/api.js:30` lee `import.meta.env.VITE_API_ORIGIN ?? ""`; `getAuthLoginUrl()` arma
`${API_ORIGIN}/api/v1/auth/login?redirect=...`). Esto es a propósito y está documentado en
`api.js:20-29`: el login **debe navegar directo al origen de la API, no por el proxy del front**,
porque la cookie anti-CSRF `faro_oauth_state` se fija en el origen que responde; si el login sale por
el `proxy_pass` de nginx, Google regresa al `/callback` del origen de la API, que **nunca fijó** esa
cookie → 401. Es exactamente el hallazgo que Christian dejó escrito en el `Threat_Model` v1.3 y en la
revisión del PR #304.

El problema: **nada inyecta `VITE_API_ORIGIN` en build-time**, así que la imagen se hornea con la
variable vacía. Verificado con evidencia dura en el repo:

- `docker/frontend-react.Dockerfile` no declaraba `ARG`/`ENV VITE_API_ORIGIN` (su comentario solo
  contemplaba `VITE_API_BASE_URL`, que sí debe quedar vacío).
- `vault/08_CICD_DevOps/scripts/build-and-push-frontend.sh` no pasaba `--build-arg`.
- No existe `frontend/.env.production` versionado (`git ls-files`) ni un `define` en
  `frontend/vite.config.js`.

Vite **congela** `import.meta.env.VITE_*` en tiempo de compilación; `docker build` no propaga el
entorno del host a la etapa de build sin un `ARG`/`ENV` explícito. Con la variable vacía,
`getAuthLoginUrl()` produce una **ruta relativa** que pasa por el proxy → cookie en el origen
equivocado → 401. Es el complemento exacto de BUG-075: BUG-075 hace que la API **acepte** el
`redirect` del front; BUG-076 hace que el front **mande** el login al origen correcto de la API.

`docker/**` y `vault/08_CICD_DevOps/**` son rutas críticas de `luis-tellez` en `ownership.yml`, así
que el fix es de mi alcance. Va en el mismo PR que BUG-075 (`dev/luis-tellez`, #338): son las dos
mitades de la misma configuración de redirect del login.

## Qué se hizo

Dos archivos tocados, ambos de mi alcance. **No se tocó `frontend/src/lib/api.js`** (alcance de C1 /
Diana): ya lee la variable correctamente; el hueco estaba en el build, no en el código.

1. **`docker/frontend-react.Dockerfile`** — se declara `ARG VITE_API_ORIGIN=""` + `ENV
   VITE_API_ORIGIN=$VITE_API_ORIGIN` antes de `RUN npm run build`. El default vacío **preserva el
   comportamiento de desarrollo** (donde el proxy de Vite cubre el login y las cookies locales no
   distinguen puerto). Se corrige además el comentario que —falso desde US-405— afirmaba que "no había
   nada que inyectar": ahora distingue `VITE_API_BASE_URL` (datos, se queda vacío, va por proxy) de
   `VITE_API_ORIGIN` (login, sí se hornea, va directo).
2. **`vault/08_CICD_DevOps/scripts/build-and-push-frontend.sh`** — se define `VITE_API_ORIGIN` con
   default al **origen de la API** (`https://faro-api-eanzfglvyq-uc.a.run.app`, sin barra final, el
   mismo valor que valida `FRONTEND_REDIRECT_URIS` del lado API en `deploy-cloud-run.sh`), overridable
   por entorno; se pasa como `--build-arg` al `docker build`; y se agrega un `echo` del valor efectivo
   al resumen previo al build, para que el operador no descubra un origen equivocado como un 401
   silencioso.

**Lo que NO se hizo, a propósito** (regla 7 / autorización del PO): no se reconstruyó ninguna imagen,
no se ejecutó `gcloud`, no se redesplegó nada, no se tocó producción ni `api.js` ni ninguna credencial.
El cambio solo surte efecto cuando alguien **reconstruya** la imagen del front con el script.

## Pruebas ejecutadas

```
bash -n vault/08_CICD_DevOps/scripts/build-and-push-frontend.sh   → sin errores de sintaxis
python vault/_Meta/scripts/vault_lint.py .                        → limpio
git ls-files frontend | grep -E '\.env|vite.config'               → no hay .env.production; sin define
```

No se probó el login e2e: requiere el redeploy con las credenciales reales de Google (bloqueante 2) y
el redeploy del front + API (bloqueante 3), ambos pendientes y de decisión de Luis. Esta sesión, junto
con BUG-075, deja **cerrada la configuración del redirect del login**; el e2e cierra con el redeploy.

## Ownership y reglas

- `docker/**` y `vault/08_CICD_DevOps/**` son alcance de `luis-tellez` — el dueño lo toca en su propia
  rama, así que `check_ownership.py` pasa sin excepción. **No se invoca `DEC-025`** (esa autorización
  es para que *otros* toquen mis rutas críticas; aquí no aplica).
- **Regla 7 (cambio de CI/CD):** requiere revisión humana explícita. La aporta la compuerta única del
  PM (`DEC-003`) sobre el PR; no se mergea en silencio.

## Bloqueantes

Ninguno para este cambio. Para el login e2e siguen abiertos, ambos de decisión de Luis (regla 7):

1. **`GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` reales** (bloqueante 2). Secretos: no por chat ni
   versionados.
2. **Redeploy del front React + API a Cloud Run** (bloqueante 3) y validación del recorrido completo
   hasta la sesión FARO en la URL pública.

## Próximos pasos

- Al reconstruir la imagen del front para prod, confirmar que el `echo` muestre el origen de la API
  correcto (el mismo de `FRONTEND_REDIRECT_URIS`).
- Correr el gate e2e del login una vez hechos los bloqueantes 2 y 3: el login real cierra cuando el
  front reconstruido navega directo al origen de la API y la sesión FARO se fija en el origen del front.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Archivos creados/modificados:** `docker/frontend-react.Dockerfile` (fix),
  `vault/08_CICD_DevOps/scripts/build-and-push-frontend.sh` (fix), este DevLog, su fila en
  `vault/_DevLog/_index.md`, y la fila `BUG-076` en `vault/06_Quality_Testing/Bug_Register.md`.
- **Decisiones autónomas del agente:** ninguna acción sobre producción ni GitHub-facing más allá de
  actualizar el PR autorizado por el PO. No se ejecutó `gcloud`, no se reconstruyó la imagen ni se
  tocaron credenciales ni `api.js`.
- **Correcciones manuales:** ninguna sobre este DevLog.

## Seguridad / calidad

- [x] Sin secretos hardcodeados (la URL del API es pública; viaja en la URL de consentimiento)
- [x] Ningún correo ni credencial versionados
- [x] No se tocó producción, ni se ejecutó `gcloud`, ni se reconstruyó la imagen
- [x] No se tocó `frontend/src/lib/api.js` (alcance de C1)
- [x] DevLog enlaza a los IDs afectados

→ [[vault/_DevLog/_index|Volver al índice]]
