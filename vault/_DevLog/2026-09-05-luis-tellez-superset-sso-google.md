---
project: "FARO"
date: "2026-09-05"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — Google SSO obligatorio en Superset (OAuth2/OIDC vía Flask-AppBuilder), como interruptor de entorno sobre el Bloque 0 ya mergeado (PR #233)"
touches: ["US-502", "REQ-005", "REQ-002"]
tags: [devlog, celula-5, superset, sso, oauth, seguridad, cloud-run, fase-2, bi]
---

# DevLog — 2026-09-05 — Google SSO obligatorio en Superset (Fase 2)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Deploy a Cloud Run]]

## Contexto

Con el **Bloque 0** ya en `main` (PR #233: `superset_config.py` propio + gunicorn + entrypoint
self-contained), la imagen de Superset es desplegable a Cloud Run. Faltaba definir **cómo se autentica**.
El plan previo (`_local/plan_F2_superset_gcp.md` §4) contemplaba login admin + un rol público de solo
lectura tras la compuerta del PO. **Decisión revisada de Luis (2026-09-05): Superset se autentica con
Google SSO**, con tres condiciones de seguridad:

1. **Client OAuth DEDICADO a Superset** (separado del OAuth del API/C4).
2. **Acceso por lista blanca de correos** (fail-closed: lista vacía ⇒ nadie entra), con subconjunto Admin.
3. **SSO obligatorio, sin acceso anónimo** ⇒ el rol público queda apagado y **se elimina la dependencia
   del PO** para exponer BI.

Alcance **C5** (`docker/**`); **no toca** `superset/dashboards/**` ni `superset/semantic/**` (C2). El SSO de
Superset es **independiente** del OAuth del API.

## Qué se hizo

- **`docker/superset_config.py` (mod).** Bloque §6 nuevo, **interruptor de entorno** (mismo criterio que el
  resto del archivo):
  - Si están `SUPERSET_GOOGLE_CLIENT_ID` y `SUPERSET_GOOGLE_CLIENT_SECRET` → `AUTH_TYPE = AUTH_OAUTH`,
    proveedor **Google** vía OIDC discovery (`server_metadata_url`, authlib deriva
    authorize/token/userinfo/jwks), scope `openid email profile`.
  - `CUSTOM_SECURITY_MANAGER = FaroSsoSecurityManager(SupersetSecurityManager)`: en `oauth_user_info`
    exige `email_verified` **y** correo ∈ `SUPERSET_SSO_ALLOWED_EMAILS` (si no, devuelve `{}` ⇒ rechazo);
    asigna `role_keys` = `faro_admin` (si ∈ `SUPERSET_SSO_ADMIN_EMAILS`) o `faro_viewer` (resto).
  - `AUTH_ROLES_MAPPING` (`faro_admin`→Admin, `faro_viewer`→rol de lectura) + `AUTH_ROLES_SYNC_AT_LOGIN`
    ⇒ promover/expulsar admins por correo **sin tocar la BD**, en cada login.
  - Si **no** están esas credenciales → `AUTH_TYPE = AUTH_DB` (login nativo): piso seguro para local y
    **rollback sin cambiar código** (basta quitar las env-vars del deploy).
- **`docker/superset.Dockerfile` (mod).** Se añade **`authlib`** al `uv pip install`. La imagen
  `apache/superset:latest` **no lo trae** y `AUTH_OAUTH` lo importa en el arranque del SecurityManager;
  sin él, el contenedor muere con `ModuleNotFoundError: No module named 'authlib'`.

## Cómo lo probé

Smoke local del contenedor de **producción** (gunicorn), Postgres desechable dedicado, puerto 8091,
credenciales SSO *dummy* para forzar `AUTH_OAUTH`:

- **Build** `--platform linux/amd64` → `authlib==1.8.0` + `joserfc==1.7.5` instalados en el venv `/app/.venv`.
- **SSO ON:** `/health` **200** en ~12 s, contenedor estable, **sin** `ModuleNotFoundError` de authlib en logs.
- **`/login/`:** ofrece el botón **`fa-google`** y tiene **cero** campos usuario/contraseña (no es el
  formulario nativo de `AUTH_DB`).
- **Config cargada dentro del contenedor:** `AUTH_TYPE=4` (OAUTH), `provider=google`,
  `SecurityManager=FaroSsoSecurityManager`.
- **Fallback SSO OFF** (sin credenciales): `AUTH_TYPE=1` (AUTH_DB) ⇒ rollback intacto.

Verificado que el smoke **no** afecta a `faro-eval-bug048` (contenedor del dump de C1/C3) ni al stack de
`docker-compose` local; la infra de smoke se desmonta al final.

**Verificación manual sugerida (Luis), reproducible en local:**

```bash
docker build --platform linux/amd64 -f docker/superset.Dockerfile -t faro-superset:test .
# levantar pg desechable + superset en modo production con SSO dummy (ENVIRONMENT=production, PORT=8088,
#   DATABASE_* → pg local, SUPERSET_GOOGLE_CLIENT_ID/SECRET dummy, SUPERSET_SSO_ALLOWED_EMAILS=test@x)
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8091/health     # espera 200
curl -s -L http://localhost:8091/login/ | grep -c fa-google               # espera 1 (botón Google)
```

## Seguridad / calidad

- [x] **Cero secretos en el repo:** `SUPERSET_GOOGLE_CLIENT_ID/SECRET` salen de env (Secret Manager en
  prod). El código solo lee `os.environ`.
- [x] **Fail-closed:** lista blanca vacía ⇒ nadie entra (mismo patrón que `ANALISTA_EMAILS` en la API).
- [x] **Solo correos verificados** por Google (`email_verified`) pasan la puerta.
- [x] **Sin exposición anónima:** SSO obligatorio; el rol público (`SUPERSET_PUBLIC_READONLY`) queda en su
  default `false`.
- [x] **Rollback sin código:** quitar las env-vars del deploy revierte a `AUTH_DB`.
- [x] Alcance **C5** respetado: solo `docker/**`; **no** se tocan `superset/dashboards/**` ni
  `superset/semantic/**` (C2).
- [x] **Gate de ruff verde:** `ruff check` limpio con la versión de CI (**0.16.6**) y con *latest*. Las
  constantes `AUTH_DB`/`AUTH_OAUTH` se importan en el bloque superior del archivo (evita I001 de forma
  robusta ante cualquier versión de ruff, ya que `docker/**` no está exonerado en `ruff.toml`); el import
  de `superset.security` queda diferido dentro del `if _SSO_ENABLED:` por el ciclo de imports de Superset.

## Avisos a otros owners

- **Edgar (PO):** PR de **seguridad** C5 — requiere revisión humana (regla 7) y tu merge. No toca `main` de
  datos ni territorio C2. Con SSO obligatorio, **ya no hay que decidir exposición pública anónima de BI**.
- **Christian (C4):** este SSO es un **Client de Google DEDICADO a Superset**, independiente del OAuth del
  API. No comparte `client_id`/redirect con `/api/v1/auth/callback`.

## Pendiente de despliegue (Bloque 1, con OK paso a paso de Luis)

- **Huevo-gallina de redirect URI:** el Client de Google debe autorizar
  `https://<url-superset-cloudrun>/oauth-authorized/google`, y esa URL solo se conoce tras el primer deploy.
  Secuencia: deploy con SSO OFF (arranca en `AUTH_DB`, plataforma viva) → obtener URL → **Luis** crea el
  Client dedicado + registra el redirect en la consola de Google → cargar `CLIENT_ID/SECRET` (Secret
  Manager) + `SSO_ALLOWED_EMAILS`/`_ADMIN_EMAILS` (env, efímeras) → redeploy → SSO vivo.

## Follow-ups C5 (no incluidos en este PR)

- **BUG-050 (low):** `BABEL_DEFAULT_LOCALE` para poblar `<html lang>`. Confirmado que **no** entró en #233;
  va en **PR aparte** (no se mezcla con un cambio de seguridad) tras validar en el smoke que puebla `lang`
  sin cambiar el idioma de la UI.

## Endurecimiento post-merge #235 — guarda *fail-loud* del SSO en prod

En su revisión de **regla 7** sobre el #235 ya mergeado, el PO (Edgar) detectó una **asimetría**:
`SECRET_KEY` revienta en prod si falta, pero las credenciales SSO caían **en silencio** a `AUTH_DB`.
"SSO obligatorio" con respaldo silencioso es indistinguible de "el secreto no se inyectó" — el día de la
demo se vería como una caja usuario/contraseña donde debería decir "Entrar con Google".

**Fix (PR de seguimiento, aparte de BUG-050 por ser cambio de seguridad):** guarda *fail-loud* en
`docker/superset_config.py`, con el mismo criterio que `SECRET_KEY`, y con salida de rollback **explícita**:

```python
_SSO_ROLLBACK = os.environ.get("SUPERSET_SSO_ROLLBACK", "").lower() in ("1", "true", "yes", "on")
if _IS_PROD and not _SSO_ENABLED and not _SSO_ROLLBACK:
    raise RuntimeError("SSO obligatorio en producción: faltan CLIENT_ID/SECRET; "
                       "si es rollback deliberado, declara SUPERSET_SSO_ROLLBACK=true.")
```

- En **prod** sin credenciales SSO ⇒ el arranque **revienta** (y el log dice por qué), salvo que se
  declare **explícitamente** `SUPERSET_SSO_ROLLBACK=true` (rollback deliberado a `AUTH_DB`).
- En **local** la guarda no aplica (dev intacto).

**Smoke** (imagen amd64 = la de Cloud Run, importando el módulo dentro del contenedor):

| Escenario | AUTH_TYPE | Resultado |
|---|---|---|
| prod · sin SSO · sin rollback | — | `RuntimeError` (no arranca) ✅ |
| prod · sin SSO · `SUPERSET_SSO_ROLLBACK=true` | 1 (AUTH_DB) | arranca ✅ |
| prod · con credenciales SSO | 4 (AUTH_OAUTH) | arranca ✅ |
| local · sin SSO | 1 (AUTH_DB) | arranca ✅ |

Ruff 0.16.6 (versión de CI) + latest + AST + `vault_lint`, todo verde.

**Consecuencia operativa (Bloque 1):** el bootstrap "deploy SSO-OFF para obtener la URL" ahora exige
`SUPERSET_SSO_ROLLBACK=true`; o se despliega **directo con SSO ON** (recomendado: crear el Client dedicado
primero y registrar el redirect `…/oauth-authorized/google` cuando ya exista la URL de Cloud Run).

## Despliegue a Cloud Run (Bloque 1) + fixes de runtime del SSO (2026-09-05)

Con el código SSO ya mergeado se **desplegó Superset a Cloud Run con Google SSO obligatorio y URL
pública viva**. Aparecieron **dos bugs que solo se manifiestan en runtime** (no en el smoke local) y se
resolvieron en la misma sesión, con OK paso a paso de Luis (regla 7).

### Cadena de revisiones

| Rev | Cambio | Estado |
|---|---|---|
| `00001-hb9` | Bootstrap SSO-OFF (blindado con IAM + `SUPERSET_SSO_ROLLBACK=true`) para obtener la URL | vivo, vacío |
| `00002-967` | SSO-ON + `allUsers→run.invoker` (público). Client dedicado + redirect `…/oauth-authorized/google` (los creó Luis) | SSO vivo |
| `00003-fvb` | **Fix runtime 1** (userinfo) — imagen nueva `00d3c14` | login funciona |
| `00004-s82` | **Fix runtime 2** (correo del admin → cuenta de servicio, defensivo) | e2e OK |

Config del servicio: SA dedicado `faro-superset-sa` (roles mínimos), `--vpc-connector faro-connector
--vpc-egress private-ranges-only`, metadata en base `superset`/`superset_app`, secrets desde Secret
Manager, `min=max=1`, 2 vCPU/2Gi. La exposición pública (`allUsers`) es el **diseño final acordado** (el
SSO reemplaza el blindaje IAM), no un estado temporal.

### Fix runtime 1 — `oauth_user_info` resuelve el userinfo vía OIDC discovery (commit `00d3c14`)

- **Síntoma:** tras autenticar con Google, Superset rebotaba al login.
- **Causa:** con `server_metadata_url` (OIDC discovery), `oauth_remotes["google"].get("userinfo")` trata
  `"userinfo"` como **URL relativa** → authlib revienta con *"Invalid URL 'userinfo': No scheme
  supplied"* → el callback falla → rebote.
- **Fix (1 línea):** `remote.userinfo()`, que resuelve el `userinfo_endpoint` publicado en el discovery.
- **Validado en vivo:** el PO (Edgar) entró correctamente. Es el **único cambio de código** de estos
  fixes ⇒ va en el PR.

### Fix runtime 2 — colisión del correo del admin de servicio con el SSO

- **Síntoma:** con el fix 1 ya desplegado, **una** persona seguía rebotando al login mientras el resto
  entraba (fallaba también en incógnito limpio, en Chrome y Safari).
- **Causa (probada en logs + `describe`):** `SUPERSET_ADMIN_EMAIL` se había fijado a un **correo personal
  que también estaba en la lista blanca SSO**. El admin de servicio (`username="admin"`) ocupaba ese
  email. FAB (`auth_user_oauth`) empareja **solo por `username`** (= el correo del usuario SSO); no lo
  encuentra, e intenta `add_user(...)` con ese email → choca con el del admin (`duplicate key ...
  ab_user_email_key`) → rebota. Los demás entran porque su correo no es el del admin.
- **Reparación (con OK de Luis, regla 7):**
  1. **Job one-shot in-VPC** (`faro-superset-fixadmin`, misma imagen, vía **ORM** de Superset —no SQL
     crudo—) cambió el email del usuario `admin` de ese correo personal → `admin@faro.local`,
     liberándolo. Evidencia del log: `ADMIN_ANTES admin <correo-personal>` →
     `ADMIN_ACTUALIZADO admin admin@faro.local`; el listado de usuarios confirmó que **nunca** existió el
     usuario SSO de esa persona (el INSERT siempre falló por la colisión). Job **borrado** tras usarse.
  2. **`SUPERSET_ADMIN_EMAIL` → `admin@faro.local`** en el deploy (rev `00004-s82`, sin rebuild), para
     que un eventual re-bootstrap no vuelva a robar un correo personal.
  3. **Guard preventivo** en `docker/superset_config.py` (fail-loud, mismo criterio que `SECRET_KEY`/SSO):
     si `SUPERSET_ADMIN_EMAIL` está en `SUPERSET_SSO_ALLOWED_EMAILS` con SSO activo, el arranque revienta
     con un mensaje que explica la colisión. Cierra el bug en el código; no dispara con la config actual
     y entra en la próxima imagen (Bloque 2).
- **Verificación e2e (Luis, en vivo):** la persona afectada ya entra por Google; `/health` 200 en
  `00004-s82`, botón "Sign in with Google" presente, **cero** campos de contraseña (SSO obligatorio
  intacto).

### Aprendizaje

El admin de servicio de Superset **no debe usar el correo de una persona real** que también entra por
SSO: FAB empareja por `username`, no por `email`, y la unicidad del `email` provoca una colisión
silenciosa que se percibe como "el login rebota". El guard preventivo lo vuelve imposible de
reintroducir por configuración.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog.
- **Modificados (código SSO + guardas):** `docker/superset_config.py` (bloque §6 SSO; guarda fail-loud del
  SSO; fix `userinfo` `00d3c14`; guarda de colisión admin/SSO), `docker/superset.Dockerfile` (authlib),
  `vault/_DevLog/_index.md` (fila de este DevLog).
- **Infra GCP (sin código):** deploy de Cloud Run `faro-superset` revs `00001`→`00004`; Job efímero de
  reparación `faro-superset-fixadmin` (creado y **borrado** tras usarse); env `SUPERSET_ADMIN_EMAIL`.
- **Sin cambios de código de aplicación** (`src/`) ni de dashboards/semántica (C2).
