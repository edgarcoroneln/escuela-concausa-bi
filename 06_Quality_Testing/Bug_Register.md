---
id: DOC-BUGREG
title: "Bug Register"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
source_of_truth: true
tags: [qa, bugs]
---

# Bug Register — FARO

> Registro único de defectos. Detalle de cada uno con [[_Templates/Bug_template]].
> → [[06_Quality_Testing/_index]]

| BUG | Título | Severidad | Estado | US/REQ | Fix (PR) | Test regresión |
|---|---|---|---|---|---|---|
| BUG-001 | dag_anual.py: falta start_date | high | fixed | US-102 | fix/diana-varela-us102-dag-import-errors | manual (ver detalle) |
| BUG-002 | dag_censal_estatico.py: preset de cron no soportado | high | fixed | US-102 | fix/diana-varela-us102-dag-import-errors | manual (ver detalle) |
| BUG-003 | `sklearn` no instalado: `test_entrenar_ml01.py` y `test_entrenar_ml02.py` fallan con `ModuleNotFoundError` en colección de pytest | low | **not_a_bug** | US-311 / REQ-003 | ya resuelto en `main` desde 2026-08-13 (PR #28) — ver detalle | ambiente local desactualizado |
| BUG-004 | Imagen `apache/superset:latest` no incluye `psycopg2`: conexión a PostgreSQL falla con 422 al crear datasets virtuales | medium | open | US-202 | pendiente (**C5**, Edward Ruiz — US-522c) | — |
| BUG-005 | Scripts `.sh` se corrompen a CRLF en checkouts de Windows: `.gitattributes` no tiene regla `*.sh text eol=lf`, así que con `core.autocrlf=true` MLflow y Superset no arrancan (`$'
': command not found`; en MLflow el shebang `#!/bin/sh
` produce un engañoso `no such file or directory`) | high | fixed | US-502 / REQ-005 | PR #65 (Luis Téllez, **C5**) — agregado `*.sh text eol=lf` a `.gitattributes` | pendiente (validar en Windows) |
| BUG-006 | Healthcheck de `api` usa `curl -f` pero la imagen no incluye `curl` ni `wget` (solo `python`): el contenedor queda `unhealthy` de forma permanente aunque `/health` responda HTTP 200 | medium | fixed | US-502 / REQ-004 | PR #65 (Luis Téllez, **C5**) — removido healthcheck override de api, actualizado chromadb a /api/v2/heartbeat | pendiente (validar healthchecks) |
| BUG-007 | Healthcheck de `chromadb` apunta a `/api/v1/heartbeat`, que responde **HTTP 410 Gone** (endpoint retirado); la ruta viva es `/api/v2/heartbeat`. Además arrastra el mismo problema de `curl` de BUG-006 | medium | fixed | US-502 / REQ-006 | PR #65 (Luis Téllez, **C5**) — actualizado puerto MLflow en documentación (5000 → 5001) | validado |
| BUG-008 | `docker/api.Dockerfile` arranca `src.api.main:app` (el hola mundo de US-501, **3 rutas**) en vez de `src.api.app:app` (la app real del contrato v1, **18 rutas** bajo `/api/v1`): en el contenedor —y en la URL pública si usa este Dockerfile— **US-401, US-402 y US-411 son inalcanzables** | **high** | open | US-501 / US-411 / REQ-004 / REQ-005 | pendiente (**C5** + C4) | correr `uvicorn src.api.app:app` a mano fuera del contenedor | ver detalle |

## Convención

- Severidad: critical / high / medium / low
- Estado: open → in_progress → fixed → closed (o wont_fix)
- Todo `fixed` requiere test de regresión antes de `closed`.

---

## BUG-001 — dag_anual.py: falta start_date

- **Owner:** Diana Aracely Alvarez Varela
- **Severidad:** high
- **Estado:** fixed
- **traces_up:** US-102
- **found_on:** 2026-08-16

### Descripción
Airflow no podía importar `dag_anual.py`: el DAG no tenía definido `start_date`, parámetro requerido por Airflow para poder programarse.

### Pasos para reproducir
1. Levantar el stack con `docker compose up`.
2. Ejecutar `docker compose exec airflow-webserver airflow dags list-import-errors`.
3. `dag_anual.py` aparece con error de importación.

### Resultado actual vs esperado
- **Actual:** DAG no cargaba, error de importación en la UI de Airflow.
- **Esperado:** DAG carga sin errores y aparece programable en la UI.

### Entorno
- Docker Compose local, servicios airflow-webserver / airflow-scheduler / airflow-init (PR #34, US-502).

### Causa raíz
Faltaba el argumento `start_date` en la definición del DAG.

### Fix
- **PR:** fix/diana-varela-us102-dag-import-errors
- **Test de regresión:** manual — `docker compose exec airflow-webserver airflow dags list-import-errors` ya no reporta `dag_anual.py`; confirmado en la UI de Airflow "6/6 DAGs, 0 failed".

---

## BUG-002 — dag_censal_estatico.py: preset de cron no soportado

- **Owner:** Diana Aracely Alvarez Varela
- **Severidad:** high
- **Estado:** fixed
- **traces_up:** US-102
- **found_on:** 2026-08-16

### Descripción
Airflow no podía importar `dag_censal_estatico.py`: usaba un preset de `schedule` no soportado por el parser de cron de Airflow (`cron_descriptor.Exception.FormatException: Expression only has 1 parts. At least 5 part are required`).

### Pasos para reproducir
1. Levantar el stack con `docker compose up`.
2. Ejecutar `docker compose exec airflow-webserver airflow dags list-import-errors`.
3. `dag_censal_estatico.py` aparece con error de importación.

### Resultado actual vs esperado
- **Actual:** DAG no cargaba; traceback de `cron_descriptor` al parsear el preset.
- **Esperado:** DAG carga sin errores, con una expresión cron válida de 5 partes (o el preset correcto soportado por Airflow).

### Entorno
- Docker Compose local, servicios airflow-webserver / airflow-scheduler / airflow-init (PR #34, US-502).

### Causa raíz
El `schedule` usaba un preset no reconocido por el parser de cron de Airflow.

### Fix
- **PR:** fix/diana-varela-us102-dag-import-errors
- **Test de regresión:** manual — `docker compose exec airflow-webserver airflow dags list-import-errors` ya no reporta `dag_censal_estatico.py`; confirmado en la UI de Airflow "6/6 DAGs, 0 failed".

---

## BUG-003 — `sklearn` no instalado al correr pytest

| | |
|---|---|
| **Estado** | `not_a_bug` — el repositorio no tiene el defecto |
| **Reportado** | 2026-08-17 (commit `78ede8c`, US-202) |
| **Historia** | US-311 / REQ-003 |
| **Cerrado por** | Héctor Rafael Morales Marbán, 2026-08-17 |

### Diagnóstico

**No es un defecto del repositorio: es un ambiente local desactualizado.**

`scikit-learn>=1.5` ya está en `requirements.txt` desde el **13 de agosto**, cuatro días antes de
que se registrara este bug. Se agregó en el commit `5f0f04a` (PR #28) precisamente porque el CI
instala **sólo** `requirements.txt` y nunca los `requirements/celula-*.txt`, así que las pruebas de
`src/modelos/` fallaban en el runner.

### Evidencia

- `requirements.txt` contiene `scikit-learn>=1.5` (sección "Célula 3 - ML").
- El job **"Calidad de codigo y vault"** del CI hace `pip install -r requirements.txt` y luego
  `pytest tests/ -q`. Está **verde en `main`** en las corridas recientes: si faltara `sklearn`, la
  colección de pytest fallaría ahí primero.
- Cubre los **dos** archivos reportados: `entrenar_ml02.py` sólo necesita `sklearn` en imports de
  nivel superior (`shap` y `mlflow` son imports diferidos).

### Remediación para quien lo encuentre

No hay que tocar código, ni de la Célula 3 ni de nadie:

```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -q
```

Le pasa a cualquier ambiente virtual creado antes del 13 de agosto que no haya reinstalado
dependencias.

### Nota de alcance

Se preguntó si el fix correspondía a la Célula 3 por tocar `src/modelos/`. **No había fix de código
pendiente**, y la decisión de no tocar `src/modelos/` fuera del alcance propio fue la correcta.

## BUG-008 — El contenedor de la API corre el «hola mundo», no la app real

| | |
|---|---|
| **Severidad** | high — bloquea el ensayo E2E del 28–29 de agosto |
| **Estado** | `open` |
| **Detectado** | 2026-08-21, al ensayar el tramo ML → Gold → API |
| **Owner** | **Célula 5** (`docker/`), en coordinación con **Célula 4** (dueña de la app) |

### Qué pasa

`docker/api.Dockerfile` termina en:

```
CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT}
```

Pero hay **dos aplicaciones** en el repositorio:

| Módulo | Qué es | Rutas |
|---|---|---|
| `src/api/main.py` | el **«hola mundo»** de US-501 (Cloud Run): `/`, `/health`, `/info` | **3** |
| `src/api/app.py` | la app real — `create_app()`, *"FARO API — Contrato v1"*, router `api_v1_router` bajo `/api/v1` | **18** |

El contenedor arranca la primera.

### Evidencia

Levantando ambas y consultando su OpenAPI:

```
src.api.main:app  → 3 rutas   (/, /health, /info)
src.api.app:app   → 18 rutas  (/api/v1/escuelas, /api/v1/predicciones/{cct},
                               /api/v1/auth/*, /api/v1/agente/consulta, …)
```

Se reconstruyó la imagen con `docker compose up -d --build api` para descartar caché: el resultado
es idéntico. Es el `CMD`, no la imagen.

### Impacto

**Todo US-401 (contrato v1), US-402 (OAuth2/JWT) y US-411 (endpoints sobre Gold) es inalcanzable en
el contenedor.** Si el despliegue de Cloud Run usa este mismo Dockerfile, tampoco están en la URL
pública — y el **ensayo E2E del 28–29 evalúa exactamente esa URL** con criterio go/no-go.

### Corrección propuesta

Apuntar el `CMD` a `src.api.app:app` y verificar la URL pública antes del 28. Conviene además
decidir qué pasa con `src/api/main.py`: si se conserva como *health probe* mínimo o se retira, para
que no vuelva a confundirse cuál es la app.

Nota: la app real publica su OpenAPI en `/api/v1/openapi.json` y sus docs en `/api/v1/docs`, no en
la raíz. Cualquier verificación automatizada del ensayo debe apuntar ahí.

### Por qué no lo arregla quien lo reporta

`docker/` es de la Célula 5 y un cambio de despliegue requiere revisión explícita de su dueño
(regla 7 del vault).

## BUG-004 — Imagen `apache/superset:latest` no incluye `psycopg2`

- **Owner:** **Célula 5** (DevOps/Cloud) — Edward Ruiz (US-522c)
- **Severidad:** medium
- **Estado:** open
- **traces_up:** US-202
- **found_on:** 2026-08-17

### Descripción
La imagen oficial `apache/superset:latest` no trae el driver `psycopg2` para PostgreSQL. Sin él, Superset no puede conectarse a la base de datos PostgreSQL y la creación de datasets virtuales vía API falla con HTTP 422 ("Connection failed, please check your connection settings").

### Pasos para reproducir
1. `docker compose up -d db superset`
2. Abrir Superset en http://127.0.0.1:8088
3. Ir a Data → Databases → Add → PostgreSQL
4. Configurar la conexión (host: `db`, puerto: `5432`, usuario, contraseña, base de datos)
5. Probar conexión → falla con 422

### Resultado actual vs esperado
- **Actual:** 422 "Connection failed" al intentar conectar Superset con PostgreSQL.
- **Esperado:** Conexión exitosa; Superset puede crear datasets virtuales sobre la base de datos.

### Entorno
- Docker Compose local, servicio `superset` (`apache/superset:latest`)
- PostgreSQL en servicio `db` (`postgres:15-alpine`)

### Causa raíz
La imagen oficial no incluye `psycopg2-binary` en su venv (`/app/.venv/`). Superset intenta usar SQLAlchemy para conectarse a PostgreSQL pero falla al importar el driver.

### Fix temporal (workaround)
```bash
docker exec -u root faro-superset pip install --target /app/.venv/lib/python3.10/site-packages psycopg2-binary
```
> **Nota:** se pierde al reiniciar el contenedor.

### Fix permanente (pendiente)
- Crear un Dockerfile custom que extienda `apache/superset` e instale `psycopg2-binary`, O
- Agregar la instalación a `docker/superset-init.sh` ejecutando como root antes de iniciar Superset.

### Fix (PR)
- pendiente (**C5**, Edward Ruiz — US-522c)

### Test de regresión
- pendiente