---
project: "FARO"
date: "2026-09-05"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — cierre de SEC-006: flip AUTH_LECTURA_PUBLICA=false en Cloud Run y verificación e2e en vivo"
touches: ["SEC-006", "US-403", "US-404", "US-402", "REQ-004", "REQ-005"]
tags: [devlog, celula-5, security, cloud-run, rbac, sec006, flip, env-var, e2e]
---

# DevLog — 2026-09-05 — SEC-006 cerrado: la lectura de la API ya exige sesión

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/07_Security/Security_Audit_Log|SEC-006]] ·
[[vault/07_Security/Security_Review_US402_US403_US404|Revisión de seguridad US-402/403/404]] ·
[[vault/_DevLog/2026-09-04-luis-tellez-redeploy-bug046-e2e|Login e2e en vivo (BUG-046)]]

## Contexto

`SEC-006` (Security Audit Log, `low`, `accepted_risk` desde 2026-09-02): `AUTH_LECTURA_PUBLICA=true` en
el entorno desplegado — la lectura de la API no exigía sesión. Se aceptó **como decisión de demo**, con una
condición de cierre explícita: *"se apaga por configuración cuando el login e2e esté validado — C5"*.

Esa condición ya se cumplía: el **login e2e quedó validado en vivo** con el cierre de `BUG-046`
(`/auth/login` 302→Google con `state` JWT de un solo uso, canje de código, `/auth/me` 401 sin token,
RBAC `analista`/`ciudadano` sobre `/admin/*` — AC-004.4/AC-004.5). Faltaba únicamente **ejecutar el flip**,
que es acción de C5 (interruptor de configuración, contemplado en [[vault/03_Architecture/ADRs/ADR-004-autenticacion-oauth2-jwt|ADR-004]]).

## Qué se hizo

Un único cambio de **variable de entorno** en Cloud Run, sin reconstruir imagen:

```
gcloud run services update faro-api --region us-central1 --update-env-vars AUTH_LECTURA_PUBLICA=false
```

- `--update-env-vars` hace *merge*: preservó `ANALISTA_EMAILS`, `GOOGLE_*`, los secretos de Secret Manager,
  la service account y la conexión VPC. **No se tocó ningún secreto ni se imprimió ninguna lista de correos.**
- Nueva revisión **`faro-api-00012-pq5`** al 100 % del tráfico (la anterior, `faro-api-00011-hr5`, queda como
  punto de rollback inmediato).
- **No hubo rebuild**: `/api/v1/version` sigue devolviendo la misma imagen `33fcbbb`. Es cambio de
  configuración, **reversible en segundos** con el mismo comando y `=true`.
- El arranque pasó `assert_production_ready()` (JWT_SECRET_KEY válido desde Secret Manager); el flip no
  afecta esa comprobación.

## Cómo lo probé (verificación en vivo, sin token)

`BASE=https://faro-api-eanzfglvyq-uc.a.run.app`. Se sondearon **todos** los endpoints del contrato
(`/api/v1/openapi.json`) sin credencial, comparando contra el baseline previo al flip:

| Endpoint (sin token) | Antes | Ahora |
|---|---|---|
| `GET /api/v1/kpis` | 200 | **401** |
| `GET /api/v1/escuelas` · `/escuelas/{cct}` | 200 | **401** |
| `GET /api/v1/municipios` · `/municipios/{cve_mun}` | 200 | **401** |
| `GET /api/v1/predicciones/{cct}` · `/explicacion` | 200 | **401** |
| `POST /api/v1/predicciones/batch` | 200 | **401** |
| `POST /api/v1/agente/consulta` | 200 | **401** |
| `GET /api/v1/version` · `/health` | 200 | **200** (públicos, por diseño) |
| `GET /api/v1/auth/login` | 302 | **302** (inicia OAuth, público) |
| `GET /api/v1/admin/metrics` · `/admin/export` · `POST /admin/pipeline/run` | 401 | **401** (sin cambio) |

### Matriz de acceso resultante

| Nivel | Endpoints | Quién entra |
|---|---|---|
| **Público** | `health`, `version`, `docs` (`/api/v1/docs`), `auth/login` | Cualquiera, sin login |
| **Lectura** | `kpis`, `escuelas`, `municipios`, `predicciones/*`, `agente/consulta` | Cualquier usuario autenticado — rol `ciudadano` **o** `analista` (`require_lectura` ya exige sesión) |
| **Admin** | `admin/metrics`, `admin/export`, `admin/pipeline/run` | Solo rol `analista` (lista `ANALISTA_EMAILS`, efímera: PO + C5). Un `ciudadano` autenticado recibe 403 |

El rol se resuelve por correo al iniciar sesión con Google: en la lista de analistas → `analista`; cualquier
otra cuenta → `ciudadano`. No hay auto-registro de analistas.

## Alcance del cambio — lo que este flip **no** hace

- **No redesplegó código.** La imagen sigue en `33fcbbb`. El pendiente *"C5 redespliega la API antes del 9"*
  (Traceability, REQ-004/US-412) sigue **abierto**: el `SIN_DATO` de `/explicacion` (`BUG-055`, C4) y los demás
  fixes de código de hoy **no** entran con este flip; requieren rebuild aparte. Este DevLog cubre solo el
  interruptor de lectura.
- **No toca el par de demostración.** El par prescriptivo vigente lo elige C2 con datos de producción
  (Traceability, REQ-002/003, acción abierta de Marina García); es ajeno a este cambio.

## Rollback

Un comando, ~30 s, sin rebuild:

```
gcloud run services update faro-api --region us-central1 --update-env-vars AUTH_LECTURA_PUBLICA=true
```

> Nota de demo (decisión ya tomada, no se reabre): con la lectura cerrada, la "URL pública viva" se
> sostiene con `/api/v1/version`, `/api/v1/health`, `/api/v1/docs` (Swagger) y el login OAuth + Superset con
> SSO. El interruptor queda a un comando por si en la demo se prefiere mostrar datos sin fricción.

## Seguridad / calidad

- [x] Único cambio = **una variable de entorno** (`AUTH_LECTURA_PUBLICA=false`); sin cambios de código
- [x] Sin rebuild: imagen intacta (`/version` = `33fcbbb`), reversible por configuración
- [x] `--update-env-vars` preserva secretos, `ANALISTA_EMAILS`, SA y VPC; **no se imprimió ni versionó ningún correo**
- [x] Verificado en vivo, sin token: lectura y predicciones/agente pasan de 200 a **401**; `admin/*` sin cambio; públicos intactos
- [x] Punto de rollback disponible (revisión previa `faro-api-00011-hr5`) + comando de reverso documentado
- [x] Sin credenciales / tokens / `.env` en repo, plan ni DevLog

## Avisos a otros owners

- **Christian Ruiz (C4, dueño de `vault/07_Security/**`):** `SEC-006 → resolved` en el Security Audit Log.
  La acción de apagado era de C5 por diseño (ADR-004); pido tu **revisión de regla 7** sobre el cierre del hallazgo.
- **Edgar (PO):** cambio de seguridad → **lo mergeas tú** (regla 7). No bloquea el freeze: es env-var, no código.
- **C4/C5:** recordatorio de que el **redeploy de código** de la API (para `BUG-055` y lo de hoy) sigue
  pendiente y es independiente de este flip.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog.
- **Modificados:** `vault/07_Security/Security_Audit_Log.md` (SEC-006 → `resolved` + verificado),
  `vault/_DevLog/_index.md` (fila de este DevLog), `vault/02_Requirements/Traceability_Matrix.md`
  (evidencia incremental del cierre de SEC-006).
- **Sin cambios de código.** Único cambio de infraestructura: la variable `AUTH_LECTURA_PUBLICA` en Cloud Run,
  reversible en segundos.
