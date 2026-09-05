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

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog.
- **Modificados:** `docker/superset_config.py`, `docker/superset.Dockerfile`, `vault/_DevLog/_index.md`
  (fila de este DevLog).
- **Sin cambios de código de aplicación** (`src/`) ni de dashboards/semántica (C2).
