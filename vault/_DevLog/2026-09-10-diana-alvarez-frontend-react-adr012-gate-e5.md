---
project: "FARO"
date: "2026-09-10"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — sincronización con main, ADR-012 (retiro de Streamlit), validación del docker build del frontend React, cierre de la decisión de auth con Luis y Christian en el gate E5, y dos huecos de gobernanza encontrados y corregidos antes de abrir el PR."
touches: ["US-641", "REQ-005", "REQ-002", "REQ-004", "ADR-010", "ADR-012", "BUG-063", "SEC-006"]
tags: [devlog, equipo-5, frontend, react, deploy, adr-012, gate-e5, ownership]
---

# DevLog — 2026-09-10 — ADR-012, docker build validado y cierre de auth con E5 (gate del jueves)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo|ADR-012]] ·
[[vault/08_CICD_DevOps/PLAN_TRABAJO_E5|Plan de trabajo E5]] · [[vault/08_CICD_DevOps/Arquitectura_Frontend_React|Arquitectura Frontend React]]

## Contexto

Combo #1 (React + Vite + Recharts + D3) ya se había decidido en sesión previa tras probar en código
real las 5 combinaciones candidatas. Esta sesión cierra lo que faltaba para presentarlo como evidencia
verificable en el gate E5 del jueves: `git merge origin/main`, validar que el Dockerfile del frontend
de verdad compila y sirve, y cerrar con Luis (E5) y Christian (seguridad, también E5) la decisión de
auth que el ADR había dejado como propuesta.

## Qué se hizo

**Sincronización.** `git merge origin/main` sin conflictos de contenido, pero con una colisión de
nombre de archivo: `docker/frontend.Dockerfile` ya existía en `main` (el Dockerfile del shell de
Streamlit, Luis, US-526) — el mío se renombró a `docker/frontend-react.Dockerfile` antes de mergear,
y se actualizaron las tres referencias (`build-and-push-frontend.sh`, los dos docs de E5).

**Docker build validado de verdad**, no solo "compila": `docker build` (17/17) + `docker run` +
`curl -sI` → `200 OK` de `nginx` sirviendo el `index.html` real. Fix necesario: `RUN npm ci` en el
Dockerfile no traía `--legacy-peer-deps` (mismo choque de peers que ya se había resuelto en local,
`react-simple-maps` vs. React 19).

**Auth — cerrada en el gate con Luis y Christian.** Luis revisó la propuesta contra el repo real y
confirmó el stack y los dos huecos de datos de `/municipios`, pero objetó el punto de auth: Bearer en
el navegador expone el token a JS (CIS v8 Control 16 de ~9 a ~7). Christian retiró su propia firma de
Bearer y propuso, en vez de BFF, **cookie `httpOnly` de un solo origen**: `nginx` hace `proxy_pass` de
`/api/*`, `/auth/exchange` deja `Set-Cookie` sin `Domain` (host-only, no choca con `BUG-059`),
`deps.py` gana fallback de cookie, y el frontend deja de tocar tokens — solo
`credentials: "same-origin"`. `ADR-010` (código de un solo uso) se conserva intacto. CORS deja de ser
bloqueante por diseño (un solo origen). Riesgo residual: CSRF, mitigado con `SameSite=Lax`, documentado
por Christian en `Threat_Model` como residual, no resuelto. `ADR-012` y los dos docs de E5 quedaron
actualizados con el diseño final antes de subir la rama.

**Dockerfile non-root** (pedido de Christian en la misma revisión): `docker/frontend-react.Dockerfile`
pasa de `nginx:1.27-alpine` (root) a `nginxinc/nginx-unprivileged:1.27-alpine`, con `chown` explícito
de `/usr/share/nginx/html` y `/etc/nginx` antes de bajar a `USER nginx`. Pendiente de reconfirmar el
build+run tras este cambio de imagen base (se pidió a Diana correrlo, resultado aún no llega a este
DevLog).

## Dos huecos de gobernanza encontrados antes de abrir el PR

**`DOC-FRONTEND-ARCH` duplicado.** `vault_lint.py` reprobó por ID duplicado:
`Arquitectura_Frontend_React.md` reusaba el ID del `Frontend_Architecture.md` de Manuel Serranía
(2026-08-07, ya en `main`, describe la arquitectura vieja de Streamlit). Por precedencia de merge
(`DEC-013`), el mío se renombra a `DOC-E5-ARQ-FRONTEND-REACT`. Ningún otro documento del vault
apuntaba al mío por ese ID, así que no hubo que corregir referencias ajenas.

**`ownership.yml` de Diana no se había actualizado con la reapertura S7.** `check_ownership.py`
reprobó el PR: 78 archivos fuera de alcance. El `rol` de Diana ya decía *"Líder S7 · Frontend e
integración"* desde `DEC-022`, pero el `verde` se había quedado en el de Célula 1 (pre-reapertura) —
sin `frontend/**`, `docker/**` ni `vault/08_CICD_DevOps/**`, las mismas rutas que Luis Téllez sí tiene
desde la reorganización. Se agregaron esas cuatro rutas al `verde` de `diana-alvarez` con nota inline
explicando el hueco (mismo patrón que los huecos ya documentados en ese archivo por Christian y por la
propia Diana en sesiones anteriores). **Toca una ruta crítica de Edgar Coronel (`vault/_Meta/**`) — el
PR pide su revisión explícita, regla 7.**

## Pruebas ejecutadas

```
python3 vault/_Meta/scripts/vault_lint.py .
  → 1 ID duplicado (DOC-FRONTEND-ARCH) antes del fix; "Vault limpio" después.

python3 vault/_Meta/scripts/check_ownership.py --autor DianaVarela96 --rama dev/diana-alvarez --base origin/main
  → 78 archivos fuera de alcance antes del fix a ownership.yml; "Identidad, rama y alcance correctos" después.

pytest tests/ -q
  → No se pudo correr en este entorno: faltan dependencias de Python (fastapi y otras) no instaladas
    en la sandbox de edición. Ningún archivo Python se tocó en esta sesión (solo docs, YAML, Dockerfile
    y frontend/), así que no debería haber impacto — pendiente de que Diana lo confirme en su propio
    entorno antes de marcar la casilla del PR.
```

## Siguiente acción recomendada

Diana confirma el `docker build`/`docker run` tras el cambio a `nginx-unprivileged` (verificar
`whoami` → `nginx`, no `root`), corre `pytest tests/ -q` en su entorno real, pide a Edgar la revisión
del cambio a `ownership.yml`, y abre el PR contra `main` con el título y cuerpo ya preparados.
