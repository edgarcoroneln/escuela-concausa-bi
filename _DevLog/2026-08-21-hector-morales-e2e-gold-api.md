---
project: "FARO"
date: "2026-08-21"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "2h"
touches: ["US-313", "US-311", "US-411", "US-501", "REQ-003", "REQ-004", "REQ-005"]
tags: [devlog, celula-3, e2e, gold, api]
---

# DevLog — 2026-08-21 — Ensayo del tramo ML → Gold → API, previo al E2E del 28–29

→ [[_DevLog/_index|Volver al índice]]

## Por qué esta sesión

El PLAN_MAESTRO fija un **ensayo E2E en vivo el 28–29 de agosto** con criterio go/no-go sobre la URL
pública. Mi tramo es: ML-01 predice → se publica a Gold → la API lo sirve. Con los PR **#58**
(ML-02 integrado a Gold, Andrés) y **#59** (endpoints reales sobre Gold, Karla) ya existían todas
las piezas, así que se probó la cadena completa **con servicios levantados** por primera vez, en vez
de por partes.

## Lo que funciona

Con `docker compose up -d db` y `DATABASE_URL` apuntando a Postgres real:

```
ML-01 entrenado — MAE 0.0141 ± 0.0012
Predicciones construidas: 80 filas (ciclo 2023-2024)
gold.predicciones: 80 filas publicadas (upsert idempotente)
ML-02 entrenado — F1 macro 0.7945 ± 0.0241
gold.recomendaciones: 80 filas publicadas (upsert idempotente)
```

Verificado en la base: `gold.predicciones` 80 filas y `gold.recomendaciones` 80 filas.
**US-313 queda funcionalmente completa**: ambas tablas se publican, ya no sólo una.

También se revisó `src/api/repositorio_gold.py` (US-411, Karla Monter): lee el esquema publicado
correctamente — filtra `modelo = 'ML-01'`, hace `LEFT JOIN` por `cct` e `id_ciclo` y toma
`indice_riesgo` y `driver_dominante`. **No hace falta ajustar nada del lado de la Célula 3.**

## Dos hallazgos que bloquean el ensayo E2E

### 1. El contenedor de la API corre la app equivocada — **BUG-008**

`docker/api.Dockerfile` termina en:

```
CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT}
```

Pero `src/api/main.py` es el **"hola mundo" de US-501** (Cloud Run): expone exactamente `/`,
`/health` e `/info`. La aplicación real vive en **`src/api/app.py`** — `create_app()`, título
*"FARO API — Contrato v1"*, con el router `api_v1_router` montado bajo `/api/v1`.

Comprobado levantando ambas:

| Módulo | Rutas |
|---|---|
| `src.api.main:app` (lo que corre el contenedor) | **3** |
| `src.api.app:app` (la app real) | **18** |

Las 18 incluyen `/api/v1/escuelas`, `/api/v1/predicciones/{cct}`, `/api/v1/auth/*` y
`/api/v1/agente/consulta`. Se reconstruyó la imagen con `--build` para descartar caché: el
resultado es el mismo, es el `CMD`.

**Consecuencia:** todo US-401, US-402 y US-411 es inalcanzable en el contenedor, y —si el despliegue
usa este Dockerfile— **también en la URL pública de Cloud Run**. El ensayo del 28–29 evalúa
justamente esa URL.

Es de la **Célula 5** (`docker/`) en coordinación con la **Célula 4**, dueña de la app. Registrado como
**BUG-008** en [[06_Quality_Testing/Bug_Register]] con severidad `high`.

### 2. Las tablas base de Gold no están materializadas

Con la app real apuntando a Postgres, `/api/v1/escuelas` responde **500**:

```
psycopg2.errors.UndefinedTable: relation "gold.fact_escuela_ciclo" does not exist
```

El esquema `gold` contiene **sólo** `predicciones` y `recomendaciones` — las dos que publica la
Célula 3. Los modelos dbt de la Célula 1 (`fact_escuela_ciclo`, `dim_escuela`, `dim_municipio`,
`features_escuela`, cubos) existen como SQL pero **nadie ha corrido `dbt run` contra esta base con
datos**.

El endpoint de Karla está bien escrito: parte de `fact_escuela_ciclo` y enriquece con `LEFT JOIN` a
mis tablas. Sin la tabla base no hay de dónde partir.

## Estado del tramo, para el ensayo

| Paso | Estado |
|---|---|
| ML-01 entrena y predice | ✅ |
| ML-02 driver dominante + recomendación | ✅ |
| Publicación a `gold.predicciones` / `gold.recomendaciones` | ✅ 80 + 80, idempotente |
| Tablas base de Gold materializadas | ❌ falta `dbt run` con datos (C1) |
| API sirve los endpoints reales | ❌ el contenedor corre el hola mundo (C5/C4) |

**Mi tramo está listo; los dos eslabones que faltan son de otras células.** Faltan 7 días.

## Otro detalle de configuración

La app arma su DSN desde `POSTGRES_HOST`, que en `.env` vale `db` — el hostname **interno de la red
de Docker**. Correrla desde el host exige `POSTGRES_HOST=localhost`. Igual que con
`MLFLOW_TRACKING_URI`, conviene documentar el par host/contenedor en `.env.example`.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Archivos modificados:** `src/modelos/publicar_gold.py` (docstring)
- **Decisiones autónomas del agente:**
  - Probar la cadena con servicios reales en vez de asumir que las piezas encajan.
  - Reconstruir la imagen con `--build` antes de culpar al `CMD`, para descartar caché.
  - No tocar `docker/api.Dockerfile`: es de la Célula 5 y un cambio de despliegue requiere revisión
    de su dueño (regla 7 del vault).
- **Correcciones manuales:** al conectar ML-02, el PR #58 actualizó el docstring del módulo pero no
  el de `construir_recomendaciones()`, que seguía diciendo que ML-02 "aún no existe". Corregido, y
  se explicita que la función se mantiene genérica a propósito: sirve para publicar desde cualquier
  origen de driver, incluido un diagnóstico manual.
- **Prompt inicial:** validar el repositorio y ver cómo seguir avanzando.

## Seguridad / calidad

- [x] Sin secretos hardcodeados; la contraseña se leyó del `.env` local, nunca se imprimió
- [x] Suite completa **209 passed, 4 skipped** · `ruff` limpio · `vault_lint` ✅
- [x] Contenedores levantados sólo para verificar y bajados al terminar

## Pendiente

- **Célula 5 + Célula 4:** apuntar el `CMD` del Dockerfile a `src.api.app:app` y verificar la URL
  pública de Cloud Run antes del 28.
- **Célula 1:** materializar Gold con `dbt run`. Depende del extractor multi-ciclo del 911 que Diana
  está armando.
- **BLOCK-001** sigue abierto por el artifact root de MLflow.
