---
project: "FARO"
date: "2026-09-05"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — carga de los 10 tableros (capa semántica + charts) a la Superset de prod, como apoyo de C5, con la versión de `main` y sin tocar código de C2"
touches: ["US-502", "REQ-002", "REQ-005"]
tags: [devlog, celula-5, superset, cloud-run, dashboards, bi, fase-2, despliegue]
---

# DevLog — 2026-09-05 — Carga de los 10 tableros en Superset de prod (Bloque 2)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Deploy a Cloud Run]]

## Contexto

La Superset de prod estaba **viva y vacía a propósito**: `docker/superset-init.sh` (C5) solo migra la
metadata, crea el admin de servicio y arranca gunicorn — **nunca carga tableros**. La carga (datasets +
charts + 10 dashboards) es el **"Bloque 2"** del `superset/README.md`, contenido de **C2** (US-202/203/205,
Manuel Serranía / Marina García) vía `superset/sync_semantic_layer.py`. Ese paso estaba **bloqueado** por
el `gold` vacío (un cubo faltante tumba el `sync` completo); con **BUG-048** cerrado, el `gold` de prod ya
tiene los 8 cubos ⇒ bloqueo levantado.

**Decisión de Luis (2026-09-05):** ejecutar la carga **nosotros (C5) como apoyo**, con la versión de `main`,
por pasos y con OK explícito, **sin modificar código de C2** (`superset/**`) — solo correr su `sync` tal cual.
Motivo: la rúbrica exige la URL pública con BI visible (REQ-002) y el freeze es mañana (6-sep).

## Qué se hizo (operación de despliegue — sin código)

1. **Respaldo de Cloud SQL** (red de seguridad, no destructivo): `gcloud sql backups create
   --instance=faro-postgres` → backup **`1788655421739`** (cubre metadata `superset` y analítica `faro`).
2. **Conexión de datos creada a mano en la UI** con nombre EXACTO **`faro_escuela_concausa_db`** →
   `faro`/schema `gold` en Cloud SQL. Esto **evita el hardcode a `db` sin tocar el código de C2**:
   `ensure_database` reutiliza la conexión por nombre si ya existe (línea 173-175), así que no llega a la
   rama que cablea `superset_db_host = "db"`. Par de credenciales **`faro_app` / secreto `db-password`** — el
   **mismo** que usa `faro-api` para leer el `gold` (verificado en su config: `POSTGRES_USER=faro_app`,
   `POSTGRES_PASSWORD=<secreto:db-password>`). `superset_app`/`superset-db-password` son de la **metadata**
   de Superset (base `superset`), **no** para leer el `gold`.
3. **Corrida del `sync` de `main` contra prod** (`SUPERSET_URL` de prod, admin de servicio `admin` por
   `POST /api/v1/security/login` `provider:"db"` — funciona con SSO activo —, **sin** `--validar-datos`):
   conexión reutilizada (id=1), **16 datasets**, sus métricas, **108 charts** y los **10 dashboards**
   (DB-01…DB-10, `published:True` — línea 1314), `✔ Sincronización terminada`.
4. **Afinado del rol de lectura** (el "Bloque 2" que el `sync` NO automatiza): los usuarios del whitelist
   entran por SSO como rol **Gamma** (`faro_viewer`) y Gamma **no tenía `datasource access`** a los 16
   datasets ⇒ solo los Admin (Luis, Edgar) veían los tableros. Desde la UI (Admin) se dio al rol **Gamma**
   el permiso **`all datasource access on all_datasource_access`**. Persiste en la metadata (Cloud SQL),
   no en la imagen ni env-vars; `AUTH_ROLES_SYNC_AT_LOGIN=True` re-sincroniza el rol pero no borra el
   permiso del rol.

## Cómo se probó (Luis, en vivo, en la URL pública)

- **Los 10 tableros** aparecen en el menú Dashboards y **pintan con datos reales** (DB-01 Ejecutivo:
  matrícula ≈ **6,704,229**, completitud ≈ 0.62, ranking municipal; DB-03 Ficha; DB-09 Recomendaciones).
- **Diferenciador** visible (dos escuelas, distinto driver dominante).
- **Visibilidad para no-admins:** antes del afinado del rol, un usuario del whitelist no veía nada; tras
  agregar `all_datasource_access` a Gamma y re-entrar, **ve los 10 tableros con datos**. Confirmado por Luis.

## Diagnósticos / aprendizajes (para C2 y para el runbook)

- **La conexión debe crearse a mano** con el nombre exacto: `ensure_database` cablea el host a `db`
  (servicio Docker local); en prod eso registra una conexión a un host inexistente y los charts salen
  vacíos. Crearla por la UI y dejar que el `sync` la reutilice por nombre lo resuelve sin tocar código.
- **Password en el SQLAlchemy URI crudo** rompe si trae `@ : / # % &` (el parser lo corta →
  `password authentication failed`). Usar los **campos separados** de Superset (codifica el password).
- **El guard de arranque del `sync`** (`main()`, 1368-1373) exige `SUPERSET_ADMIN_PASSWORD` y
  `POSTGRES_PASSWORD` presentes **aunque** reutilice la conexión; hay que exportar las `POSTGRES_*`. El
  script **no** abre conexión directa a Postgres desde la laptop (todo va por la API de Superset; la
  consulta al `gold` la hace Superset por el VPC connector) — solo valida presencia y arma strings.
- **El rol viewer necesita `datasource access`**: el `sync` crea datasets/charts/dashboards pero **no**
  toca permisos de rol. El afinado del rol de lectura (`superset/README.md` §3) es manual.

## Seguridad / calidad

- [x] **No se tocó código de C2** (`superset/**`): solo se ejecutó su `sync` tal cual. Alcance C5 (operación
  de despliegue) respetado.
- [x] **No se tocaron env-vars de seguridad** del servicio (SSO, whitelist, `SUPERSET_SSO_ROLLBACK`,
  `SUPERSET_PUBLIC_READONLY`): intactos. La lectura sigue tras **SSO obligatorio + lista blanca**.
- [x] **Cero secretos en repo/chat/DevLog:** los valores (`db-password`, `superset-admin-password`) los
  inyectó Luis desde Secret Manager en su terminal; el agente nunca los leyó ni los imprimió.
- [x] **Reversible:** re-correr el `sync` es idempotente; el permiso del rol se quita desde la UI; backup
  `1788655421739` como punto de restauración.
- [x] **Sin redeploy:** no cambió la imagen (`faro-superset:00d3c14`, rev `00005-4dl`) — es carga de datos
  en la metadata + un permiso de rol.

## Avisos a otros owners

- **C2 (Manuel / Marina):** los **10 tableros de `main` ya están en la Superset de prod** como apoyo de C5.
  Si ajustan los YAML de `superset/dashboards/**` o `superset/semantic/**`, basta **re-correr el `sync`**
  (idempotente) con `SUPERSET_URL` de prod. **Follow-up de C2/PO:** endurecer el rol de lectura
  (`faro_invitado` de solo lectura estricta, o `datasource access` acotado a los 16 datasets del alcance en
  vez de `all_datasource_access`) — `superset/README.md` §3.
- **C2 / Diana (datos):** el **coroplético de DB-02** (KPI-10) necesita `gold.geo_municipio` materializado
  (orden P-03: geo → dbt Gold → sync). Si ese mapa sale vacío pero los demás pintan, es dato, no la carga.
- **Caché:** en prod sin Redis puede aparecer el cuelgue "Waiting on faro_escuela_concausa_db…"; el
  workaround es reiniciar el servicio (rev nueva, sin perder metadata). Redis/Memorystore es follow-up C5.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog.
- **Modificados:** `vault/_DevLog/_index.md` (fila de este DevLog).
- **Infra GCP (sin código):** backup de Cloud SQL `1788655421739`; carga de 16 datasets + 108 charts + 10
  dashboards en la metadata de `faro-superset` (vía su `sync`); permiso `all_datasource_access` al rol Gamma.
- **Sin cambios de código** de aplicación (`src/`), de `docker/**` (C5) ni de `superset/**` (C2).
