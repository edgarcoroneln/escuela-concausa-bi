---
project: "FARO"
date: "2026-09-01"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — item 6 PROMPT-B: /version sella el commit de la imagen (GIT_SHA)"
touches: ["US-505", "REQ-005", "REQ-004"]
tags: [devlog, api, docker, observabilidad, deploy, carril-b]
---

# DevLog — 2026-09-01 — /version reporta el commit real de la imagen (item 6)

→ [[_DevLog/_index|Volver al índice]]

## Contexto

Item 6 de la remediación (PROMPT-B §6.6): `GET /api/v1/version` respondía siempre `commit: "dev"` → no
había forma de saber **qué imagen** está corriendo. El endpoint ([src/api/v1/health.py:22]) **ya leía**
`os.getenv("GIT_COMMIT", "dev")`; lo que faltaba era que **la imagen fijara** `GIT_COMMIT` desde un
`--build-arg GIT_SHA=...`. Carril seguro: no mueve números de Gold. **Local-first, sin deploy.**

Este PR está **apilado sobre el de item 5** (`carril-b/superset-validacion-local`, PR #178, aún sin
mergear) para no chocar en `_DevLog/_index.md`; su base pasará a `main` cuando #178 se integre.

## Qué se hizo

- **`docker/api.Dockerfile`**: `ARG GIT_SHA=dev` + `ENV GIT_COMMIT=${GIT_SHA}`, **después** de los
  `COPY` para no invalidar la capa de `pip install`. Sin build-arg queda `dev`.
- **`docker-compose.yml`** (servicio `api`): `build.args.GIT_SHA: ${GIT_SHA:-dev}` → `docker compose
  build` lee `GIT_SHA` del entorno.
- **`08_CICD_DevOps/scripts/build-and-push.sh`**: captura `GIT_SHA=$(git rev-parse HEAD)` y lo pasa como
  `--build-arg` (antes construía sin sellar → la imagen de **prod** también quedaba "dev"). Editar el
  script **no** lo ejecuta; sigue sin promoverse nada.
- **`.env.example`**: documenta `GIT_SHA` (interpolable por compose; no secreto; default `dev`).
- **`tests/test_api_contract.py`**: +2 pruebas — `/version` refleja `GIT_COMMIT` y cae a `dev` sin sellar.

## Validación (local, §6.6: build → run → curl)

- `docker build --build-arg GIT_SHA=5c56fac… -f docker/api.Dockerfile -t faro-api:item6-verify .` → OK.
- `docker run --rm … printenv GIT_COMMIT` → **`5c56fac…`** (ARG→ENV correcto).
- `docker run -d -p 127.0.0.1:18000:8080 …` + `curl :18000/api/v1/version` →
  **`{"api":"v1","commit":"5c56fac55c6ed910004977ba4235c07af6d4e377"}`**; `/health` → **200**.
- Contenedor e imagen de prueba eliminados tras validar.
- `pytest tests/test_api_contract.py -q` → **29 passed** (incl. las 3 de `/version`). El default `dev`
  queda cubierto por `ARG GIT_SHA=dev` + `test_version_default_dev_sin_sellar`.

## Hallazgos fuera de la lista

- **`build-and-push.sh` no pasaba `--build-arg`** (leído del script): la imagen que va a prod se
  construía igual de "dev", así que sellar solo compose habría dejado el problema real (identidad de la
  imagen en prod) sin resolver. Lo incluí en el **mismo defecto**.
- El `CMD` del Dockerfile usa forma shell (warning `JSONArgsRecommended`, línea 34) — **preexistente**,
  fuera del alcance de este item; **no lo toqué** (§9).

## Qué necesito del Carril A

- **Nada.** Carril seguro; no depende de datos de Gold ni del recálculo.

## Seguridad / alcance

- **No** se promovió nada a producción (verificado en local). Solo territorio mío: `src/api` (contrato),
  `docker/**`, `docker-compose.yml`, `.env.example`, `08_CICD_DevOps/scripts/`, `tests/test_api_*`.
- Sin credenciales ni contenido de `.env` en el código; `GIT_SHA` no es secreto.
