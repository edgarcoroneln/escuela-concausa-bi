---
project: "FARO"
date: "2026-09-05"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — Bloque 0 de Fase 2 (Superset→GCP): imagen de Superset lista para producción (config propia + gunicorn + entrypoint self-contained)"
touches: ["US-502", "REQ-005", "REQ-002"]
tags: [devlog, celula-5, superset, cloud-run, fase-2, bi, deploy]
---

# DevLog — 2026-09-05 — Superset apto para producción (Bloque 0, Fase 2)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Deploy a Cloud Run]]

## Contexto

La rúbrica pide "Frontend BI interactivo (2.5 pts)" con **Superset (10 dashboards) en URL pública**
(CLAUDE.md §4). Hoy Superset solo corre en `docker-compose` local con el **servidor de desarrollo**
(`superset run --reload`) y **sin `superset_config.py` propio** (la imagen oficial arma la metadata desde
`DATABASE_*`). Eso no es desplegable a Cloud Run tal cual: falta un servidor de producción ligado a
`$PORT`, la config de proxy/TLS del borde de Cloud Run y una `SECRET_KEY` estable inyectable desde Secret
Manager.

Este es el **Bloque 0** del plan de Fase 2 (`_local/plan_F2_superset_gcp.md`): **solo código/infra**, sin
tocar GCP y **sin depender de Fase 1** (los datos/cubos llegan en el Bloque 2). Pertenece al alcance **C5**
(`docker/**`); **no toca** `superset/dashboards/**` ni `superset/semantic/**` (territorio C2).

## Qué se hizo

- **`docker/superset_config.py` (nuevo).** Override mínimo de los defaults de Superset, sirve para local y
  prod con las mismas `DATABASE_*`:
  - `SQLALCHEMY_DATABASE_URI` armada explícitamente desde `DATABASE_*` con `quote_plus` en el password
    (soporta caracteres especiales); `pool_pre_ping` + `pool_recycle=300` (Cloud SQL corta conexiones
    ociosas).
  - `SECRET_KEY` desde `SUPERSET_SECRET_KEY`; **obligatoria en prod** (`RuntimeError` si falta) y con
    fallback explícitamente inseguro solo para desarrollo local.
  - Caché en **filesystem** bajo `/tmp` (sin Redis en la ventana de demo; con una sola instancia en Cloud
    Run es consistente). Migrar a Redis/Memorystore queda como follow-up post-demo.
  - `ENABLE_PROXY_FIX=True` (respeta `X-Forwarded-Proto/Host` de Cloud Run → URLs `https://`) y
    `TALISMAN_ENABLED=False` (forzar HTTPS en la app tras un borde que ya da HTTPS crea bucle de
    redirección); `WTF_CSRF_ENABLED=True` (default seguro).
  - **Rol público de solo lectura pre-cableado APAGADO** tras el flag de entorno
    `SUPERSET_PUBLIC_READONLY` (default `false`). Encender la lectura anónima lo decide **Edgar (PO)** y
    será un cambio de env-var, no de código (mismo patrón que `AUTH_LECTURA_PUBLICA` en la API).
- **`docker/superset-init.sh` (mod).** El arranque bifurca por `ENVIRONMENT`: en `production`/`prod` lanza
  **gunicorn** (`gthread`, `--bind 0.0.0.0:$PORT`, workers/threads/timeout configurables por env,
  `--keep-alive 65`); fuera de prod conserva `superset run --reload` (el flujo de `docker-compose` no
  cambia). `db upgrade` / `create-admin` / `superset init` siguen idempotentes.
- **`docker/superset.Dockerfile` (mod).** Copia `superset_config.py` a `/app/pythonpath/` + fija
  `SUPERSET_CONFIG_PATH`; copia el `superset-init.sh` **dentro de la imagen** (Cloud Run no monta
  volúmenes) y define `CMD`. El contenido del script es idéntico al que `docker-compose` monta por volumen.

## Cómo lo probé

- **Smoke del contenedor de producción (sesión previa, 2026-09-04):** `docker build --platform
  linux/amd64` (exit 0) + `docker run` contra un Postgres local → `/health` **200** y **login admin por
  API 200**. El `--platform linux/amd64` es obligatorio (lección BUG-044: sin él sale arm64 y Cloud Run no
  arranca).
- **En esta sesión (verificación estática, pre-commit):** `bash -n docker/superset-init.sh` **OK**;
  `python -c "ast.parse(...)"` sobre `superset_config.py` **OK**; escaneo de secretos hardcodeados sobre
  los 3 archivos → **limpio** (todo sale de variables de entorno).

**Verificación manual sugerida (Luis), reproducible en local:**

```bash
docker build --platform linux/amd64 -f docker/superset.Dockerfile -t faro-superset:test .
# arrancar apuntando a un pg local (ENVIRONMENT=production para ejercitar la rama gunicorn):
#   docker run --rm -e ENVIRONMENT=production -e SUPERSET_SECRET_KEY=... -e DATABASE_* ... -p 8088:8088 faro-superset:test
curl -sf http://localhost:8088/health    # espera 200
```

## Seguridad / calidad

- [x] **Cero secretos en el repo:** `SECRET_KEY`, password de metadata y admin salen de env (Secret
  Manager en prod, `.env` en local). Escaneo de secretos limpio en los 3 archivos.
- [x] `SECRET_KEY` **obligatoria en prod** (falla el arranque si falta) → no hay clave por defecto en
  producción.
- [x] Exposición anónima **apagada por defecto** (`SUPERSET_PUBLIC_READONLY=false`); encenderla es
  compuerta del PO, cambio de env-var.
- [x] TLS delegado al borde de Cloud Run (`ENABLE_PROXY_FIX`) sin bucle de redirección
  (`TALISMAN_ENABLED=False`); CSRF activo.
- [x] Alcance **C5** respetado: solo `docker/**`; **no** se tocan `superset/dashboards/**` ni
  `superset/semantic/**` (C2).
- [x] Reversible: es imagen/config; el `docker-compose` local no cambia de comportamiento (rama `local`).

## Avisos a otros owners

- **Edgar (PO):** PR de infra C5 para merge. No toca `main` de datos ni territorio C2. El deploy real a
  Cloud Run (Bloque 1) va aparte, con tu visto bueno y el mío paso a paso.
- **Manuel / Marina / Monserrat (C2):** este PR **no** modifica dashboards ni la capa semántica. Aviso de
  coordinación: cuando se ejecute el bootstrap de Superset (Bloque 2) usaré la versión de
  `superset/sync_semantic_layer.py` de `main` **tras** mergear #232 y #228 (ambos lo tocan).
- **Diana (C1):** el Bloque 0 **no** depende del dump de BUG-048. La carga de tableros (Bloque 2) sí
  necesita el Gold con los **8 cubos** en Cloud SQL; seguimos esperando el dump con cobertura de drivers.

## Follow-ups C5 identificados (no incluidos en este PR)

- **BUG-050 (pata C5, low):** el `<html>` sin atributo `[lang]` lo emite el shell de Superset → candidata
  `BABEL_DEFAULT_LOCALE` en `superset_config.py`. **No se incluye aún** porque requiere validar en el smoke
  del contenedor que realmente puebla `lang` **sin** cambiar el idioma de la UI; entra en un commit
  posterior del mismo PR una vez verificado. (La otra pata de BUG-050 —contraste de color— es C2.)

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** `docker/superset_config.py`, este DevLog.
- **Modificados:** `docker/superset-init.sh`, `docker/superset.Dockerfile`, `vault/_DevLog/_index.md`
  (fila de este DevLog).
- **Sin cambios de código de aplicación** (`src/`) ni de dashboards/semántica (C2).
