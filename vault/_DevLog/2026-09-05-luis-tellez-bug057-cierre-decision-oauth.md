---
project: "FARO"
date: "2026-09-05"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — cierre documental de BUG-057 por decisión confirmada (OAuth en las dos capas), sin cambio técnico, con smoke de verificación en vivo"
touches: ["BUG-057", "SEC-006", "US-403", "US-411", "REQ-004", "REQ-005"]
tags: [devlog, celula-5, seguridad, rbac, oauth, decision, bug057, cloud-run]
---

# DevLog — 2026-09-05 — Cierre de BUG-057 por decisión confirmada (OAuth en las dos capas)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register|BUG-057]] ·
[[vault/_DevLog/2026-09-05-luis-tellez-sec006-flip-auth-lectura-publica|SEC-006 (flip de lectura)]]

## Contexto

**BUG-057** lo levantó el PM (Edgar Coronel) el 2026-09-05 al medir que la URL pública dejó de servir
datos de forma anónima: `/api/v1/kpis`, `/api/v1/escuelas` y `/api/v1/predicciones/{cct}` pasaron a
**401** minutos después de haber dado 200. **No es un defecto de código** —el propio registro lo dice:
`require_lectura` (`src/api/security/rbac.py:61`) se comporta como está especificado—: fue el efecto del
flip **`AUTH_LECTURA_PUBLICA=false`** que yo ejecuté en Cloud Run como **cierre de SEC-006**, el paso que
`src/api/config.py:72` anticipa textualmente (*"cuando C5 entregue credenciales, se pone
`AUTH_LECTURA_PUBLICA=false`"*). El registro dejó el bug como **decisión del PO**: (a) sostener la postura
—las dos superficies con login— o (b) reabrir la lectura durante la demo.

**Decisión (Luis Téllez, C5, confirmada hoy):** postura **(a)**. Sostenemos **OAuth/login obligatorio en
las dos capas** (API + Superset) para **incrementar la seguridad** y **demostrar RBAC real** en la demo.
Este DevLog documenta el **cierre documental** del bug —no hubo cambio técnico: el estado ya estaba en
producción desde SEC-006—.

## Qué se hizo (documental, sin código ni infra)

- **`vault/06_Quality_Testing/Bug_Register.md`** (artefacto **común**): BUG-057 pasa de `open` a **`closed`**
  (convención del register: `open → in_progress → fixed → closed`; no es `fixed` porque no hubo cambio de
  código, es cierre **por decisión confirmada**). Se reescribieron las columnas de resolución y verificación
  para registrar la postura (a), la evidencia en vivo y el acceso del evaluador.
- **Este DevLog** (regla 6).

## El hallazgo que resuelve el acceso del evaluador (sin tocar env de la API)

Se verificó en el código cómo la API asigna rol y quién puede entrar:

- `resolve_role` (`src/api/security/roles.py`) asigna **`ciudadano` por defecto** a cualquier correo, y
  `analista` **solo** si el correo está en `ANALISTA_EMAILS`.
- **La API NO tiene lista blanca de login por persona:** cualquier cuenta Google que complete el OAuth
  obtiene **≥ ciudadano** y puede leer (con `AUTH_LECTURA_PUBLICA=false`). La única "lista" del flujo es
  `redirect_uri` (anti-*open-redirect*: URLs, no personas).

**Consecuencia (decisión de la sesión):** el **profesor entra a la API como `ciudadano`** —lectura +
tableros vía datos + agente— **sin ningún cambio de variable de entorno** (no hay que darlo de alta en
`ANALISTA_EMAILS`; eso solo daría rol admin/analista, que no necesita para evaluar).

La **única compuerta por persona** de todo el sistema es **Superset**, cuya whitelist
`SUPERSET_SSO_ALLOWED_EMAILS` es **fail-closed** (solo entran los correos listados). El correo del profesor
**ya está** en esa lista (rev `faro-superset-00006-68n`, alta hecha en otra sesión).

## Verificación en vivo (smoke, 2026-09-05)

Sondeo HTTP sin credenciales contra la URL pública (solo lectura, sin gcloud):

| Ruta | Código | Lectura |
|---|---|---|
| `/api/v1/health` | **200** `{"status":"ok"}` | público ✓ |
| `/api/v1/version` | **200** `commit 33fcbbb…` | imagen intacta (flip fue env-var, no rebuild) ✓ |
| `/api/v1/docs` + `/api/v1/openapi.json` | **200** | Swagger público ✓ |
| `/api/v1/kpis`, `/api/v1/escuelas`, `/api/v1/predicciones/09DBN0007I` | **401** | lectura exige sesión ✓ (SEC-006) |
| Superset `/health` | **200** | vivo tras SSO ✓ |

> Corrección de método: en un primer sondeo probé `/health`, `/version`, `/docs` en la **raíz** (dieron 404
> con el JSON de error propio de FARO — la app está viva pero monta todo bajo `/api/v1/`, como ya anotaba
> BUG-012). Los públicos reales están bajo `/api/v1/`.

## Por qué la postura (a) no arriesga el punto de rúbrica

- La rúbrica evalúa **URL pública viva**. **`RISK-001` está `cerrado`** (2026-08-09) y **DEC-012** acota
  ese criterio a las **rutas HTTP de la API**, no a servir el `gold` sin login.
- Los endpoints públicos (`/api/v1/health`, `/version`, `/docs`, `/openapi.json`) siguen respondiendo
  **200 anónimos** → la URL pública **está viva**.
- OAuth + RBAC en **las dos** capas **suma** en dos módulos de la rúbrica: Backend/API & Auth (1.5) y
  Deploy GCP (1.0), además de demostrar el diferenciador con control de acceso real.

## Checklist pre-demo (Luis, manual)

1. **Superset:** confirmar que el correo del profesor sigue en `SUPERSET_SSO_ALLOWED_EMAILS` (whitelist
   fail-closed; ya agregado). Si la *consent screen* de Google sigue en modo **Testing**, además darlo de
   alta como **test user** en la consola Google — si no, Google lo bloquea **antes** de la whitelist.
2. **API:** nada que hacer — el profesor entra como `ciudadano` sin cambio de env. (Si por algún motivo se
   quisiera reabrir la lectura anónima durante la ventana de demo, es reversible en segundos:
   `AUTH_LECTURA_PUBLICA=true`, sin tocar código — postura (b), descartada.)

## Seguridad / alcance

- [x] **Sin cambio técnico:** el estado (`AUTH_LECTURA_PUBLICA=false`) ya estaba en prod desde SEC-006
  (rev `faro-api-00012-pq5`, imagen `33fcbbb`). Este cierre es **documental**.
- [x] **Bug_Register es artefacto común** (ownership) — editarlo no invade alcance de otra célula.
- [x] **No se tocó código** (`src/**`), ni `docker/**` (C5), ni `superset/**` (C2), ni env-vars del servicio.
- [x] **Cero secretos / cero correos** en repo, chat o DevLog: se refiere al profesor por su rol, nunca por
  su correo; el smoke no expone listas.

## Avisos a otros owners

- **PO (Edgar Coronel):** BUG-057 —que tú levantaste— queda **`closed` por decisión confirmada (postura a)**:
  OAuth en las dos capas, deliberado, cierre de SEC-006. El evaluador entra a la API como **ciudadano** (sin
  cambio de env) y ya está en la whitelist de Superset. Handoff con el detalle en
  `_local/aviso_edgar_bug057_2026-09-05.md`.
- **C4 (Christian Ruiz):** la postura ratifica el comportamiento de `require_lectura` que documentaste en
  US-416; no hay cambio en `src/api/**`.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog; `_local/aviso_edgar_bug057_2026-09-05.md` (aviso al PO, fuera del repo).
- **Modificados:** `vault/06_Quality_Testing/Bug_Register.md` (BUG-057 → `closed`); `vault/_DevLog/_index.md`
  (fila de este DevLog).
- **Sin cambios** de código, `docker/**`, `superset/**`, infra GCP ni env-vars.
