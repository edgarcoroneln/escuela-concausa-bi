# `superset/` — capa semántica de Superset (convención US-202)

> Convención canónica de la capa semántica de FARO. La fija **Manuel Alejandro Serranía Reinada**
> (Tech Lead C2, **US-202** — REQ-002) y la deben seguir todas las historias que modelan cubos o
> construyen tableros: US-211a, US-211b, US-212, US-213, US-214a/b, US-215a/b.
> Catálogo canónico de KPIs: [[vault/04_UX_Design/Screen_Specs]] · Contrato de cada cubo: `vault/04_UX_Design/Cube_Specs_*.md`.

## Estructura de carpetas

- **Una subcarpeta por contrato de cubos**, con el nombre del dashboard o familia que alimenta:
  - `semantic/` → SQL de datasets virtuales + YAML de métricas, **repunteados a los cubos físicos
    C1 (`gold.cubo_*`, US-205)**:
    - DB-01/DB-02 (`Screen_Specs` §2/§4, US-203 · Manuel).
    - DB-03/DB-04 (contrato `DOC-CUBESPEC-DB0304`, US-211a · Marina).
    - DB-05/DB-08 (contrato `DOC-CUBESPEC-DB0508`, US-211b + re-escala US-205 · Manuel).
    - DB-06/DB-09 (contrato `DOC-CUBESPEC-DB0609`, US-204 · Manuel).
    - DB-07 (contrato `DOC-CUBESPEC-DB07`, US-222 · Oscar).
    - `kpi_0*.sql` + `metrics_kpis_base_us221.yaml` (catálogo canónico, US-201/US-221).
  - `dashboards/` → definición declarativa de tableros (`*.yaml`): charts, layout y filtros nativos.
  - `mock/` → salidas de ML simuladas para desarrollo local mientras llega C3 (US-311/313).
  - `assets/geojson/` → geometrías municipales del alcance (INEGI, filtradas y simplificadas).

## Naming de archivos y de métricas

- **Archivos por cubo:** `<tablero>_<cubo>.sql` (p.ej. `db03_cubo_escuela_360.sql`) — dataset virtual
  de Superset que, desde **US-205**, **consume** el cubo físico `gold.cubo_*` ya materializado por
  la Célula 1 (US-113); ya no es el SQL de referencia para materializar nada.
- **Métricas por contrato:** `metrics_<cubos>.yaml` (p.ej. `metrics_db03_db04.yaml`).
- **Nombres de métricas: `snake_case`** y **idénticos a la fórmula del KPI canónico** de
  [[vault/04_UX_Design/Screen_Specs]] (p.ej. `variacion_ponderada_pct` es el nombre del KPI-02). Cada métrica
  declara `kpi: KPI-xx`; si no hay KPI canónico aún, se marca `kpis_propuestos` y se alinea cuando el
  catálogo lo publique. **El catálogo de KPIs es la única fuente de nombres de métricas.**

## Estructura del YAML

| Sección | Contenido |
|---|---|
| `version` / `owner` / `story` / `traces_up` | Metadatos del artefacto (Definition of Filed) |
| `filtros_globales` | Ciclo, entidad y nivel (AC-002.2); acotado a `SCOPE_ENTIDADES` |
| `datasets[].grano` / `llave_primaria` | Grano y llave del cubo |
| `datasets[].banderas_cobertura` | Todas las banderas de cobertura del cubo |
| `datasets[].jerarquias` | Rutas de drill-down (territorio, tiempo, oferta) |
| `datasets[].metricas` | Nombre, etiqueta, expresión, formato y `kpi` al que sustenta |
| `drill_down` | Navegación cruzada entre tableros (US-214a) |

## Reglas no negociables (heredadas de Screen_Specs, Data_Model y US-205)

1. **Los datasets virtuales leen `gold.cubo_*` (US-205), nunca `gold.fact_*`.** La agregación y las
   salidas de ML ya las resolvieron los cubos C1 (DEC-009/010); la capa semántica hace passthrough +
   enrich. Guarda: `tests/test_semantic_repunteo_cubos.py`.
2. **Las salidas de ML (`indice_riesgo`, `driver_dominante`, `recomendacion`, `prioridad`) llegan
   resueltas por C1.** Solo `db09` vuelve a unir `gold.predicciones` (LEFT JOIN, llave
   `cct-id_ciclo`, `modelo='ML-01'`) para el ranking de urgencia (AC-010.0).
3. **`SIN_DATO` explícito: nunca cero, nunca nulo silencioso.** Prohibido `COALESCE(<driver>, 0)`.
   Cada métrica viaja con su bandera de cobertura y muestra "sin dato disponible".
4. **Línea de alerta `>= 0.5`** (DEC-019); el ancla de calibración de la sigmoide
   se mantiene en `0.60` (≈ perder ~5% de matrícula, DEC-006).
5. **Razones como componentes aditivos:** numerador y denominador por separado
   (`suma_*` / `escuelas_con_*`), para que se reagreguen bien con cualquier combinación de filtros.
6. Toda división se protege con `NULLIF(denominador, 0)`.

## Validación

- Validación **estática** por contrato (todo el `semantic/`):
  `pytest tests/test_semantic_db01_db02.py tests/test_semantic_db03_db04.py
  tests/test_semantic_db05_db08.py tests/test_semantic_db06_db09.py
  tests/test_semantic_repunteo_cubos.py -q`.
- Validación **contra datos** (local, requiere C1 materializado): `python superset/sync_semantic_layer.py --validar-datos`
  consulta cada chart contra Postgres y reporta filas o error SQL.

## Cadena local completa (US-203)

Con Docker arriba (`docker compose up -d db superset`) y `.env` cargado:

```bash
source .venv/bin/activate
# 1) Bronze: fixtures sintéticos a bronze.* (idempotente)
#    ver src/ingesta/cargar_bronze_fixture.py
# 2) Silver + Gold con dbt (los datasets virtuales CONSUMEN gold.cubo_* de C1, US-205):
#    dbt run --select ... --vars '{...}'   (vars de identificadores de fuentes)
# 3) Mock de ML-01/ML-02 (MIENTRAS C3 no entrega; marcado MOCK-US203):
docker exec -i faro-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
    < superset/mock/gold_ml_outputs_mock.sql
# 4) Geometrías municipales (una sola vez; asset versionado en el repo):
set -a; source .env; set +a
python superset/cargar_geojson_municipios.py
# 5) Sincronizar datasets + métricas + charts + tableros:
python superset/sync_semantic_layer.py --validar-datos
```

Tableros resultantes: `http://127.0.0.1:8088/superset/dashboard/db01-ejecutivo/` y
`http://127.0.0.1:8088/superset/dashboard/db02-mapa-riesgo/`.

### Workaround: charts colgados en "Waiting on faro_escuela_concausa_db"

Síntoma observado (US-203, 2026-08-22): un tablero carga y el otro se queda con todos los charts
en "Waiting on ..." indefinidamente, sin errores en consola ni peticiones `POST /api/v1/chart/data`
en la red del navegador; las SQL corren en milisegundos directo contra Postgres.

- **Causa probable:** caché de metadatos/resultados en memoria de Superset (esta imagen no tiene
  Redis ni backend de resultados externo) que quedó en mal estado tras una corrida del sync.
- **Workaround:** reiniciar solo el contenedor de BI — `docker restart faro-superset` — esperar el
  healthcheck (`docker ps` → *healthy*, ~30 s) y recargar con hard-refresh (Ctrl/Cmd+Shift+R).
  Verificado: tras el restart ambos tableros cargan completos en ~2 s.
- Si reaparece, reportarlo en `vault/06_Quality_Testing/Bug_Register.md` citando este README.
- Fix definitivo (C5, backlog): backend de caché/resultados externo (Redis) o al menos
  `DATA_CACHE_CONFIG` persistente en `superset_config.py`.

### Notas del mock (`mock/gold_ml_outputs_mock.sql`)

- Solo desarrollo local: valores determinísticos por hash del CCT, `mlflow_run_id = 'MOCK-US203'`.
- Idempotente (`ON CONFLICT DO NOTHING`) y sin DDL destructivo; único cambio de esquema permitido:
  `ADD COLUMN IF NOT EXISTS` para completar DEC-005 si la tabla local quedó mínima.
- Deja un municipio completo sin predicciones a propósito: ejercita `cobertura_riesgo = 'SIN_DATO'`.
- Se descarta cuando C3 publique las salidas reales en `gold.predicciones` / `gold.recomendaciones`.

### Notas del GeoJSON (`assets/geojson/municipios_scope.geojson`)

- Fuente: espejo comunitario del Marco Geoestadístico INEGI (CONABIO 2023, MIT) — datos públicos.
- Filtrado a `SCOPE_ENTIDADES` (09, 14, 15, 19), simplificado (Douglas-Peucker ~200 m) hasta ~600 KB.
- Regenerable: `python superset/generar_geojson_municipios.py --descargar <dir>` + `--generar <dir>`.
- La llave de cada feature es `cve_mun` (CVEGEO de 5 dígitos) = `gold.dim_municipio.cve_mun`.

## Promoción a producción (pendiente · C5 con autorización del PM)

> Este README documenta **qué haría falta** para promover Superset; **el deploy no lo ejecuta este PR
> ni ningún agente.** Promoverlo es tarea de C5 (Cloud & DevOps) y requiere autorización explícita del
> PM (CLAUDE.md §2.7). El endurecimiento HTTP (TLS, rate-limit en login, WAF/Cloud Armor, rotación) vive
> en `docker/README-SECURITY.md` y ya lo resume la advertencia de `docker/superset-init.sh`.

### 1. Metadata DB — ya es PostgreSQL; apuntarla a Cloud SQL

- **La metadata de Superset NO es SQLite.** El servicio `superset` de `docker-compose.yml` fija
  `DATABASE_DIALECT=postgresql` + `DATABASE_DB=superset`; la imagen oficial arma su
  `SQLALCHEMY_DATABASE_URI` con esos `DATABASE_*`, así que en local la metadata vive en la base
  `superset` del **mismo contenedor `db`**. El volumen `superset-data` solo guarda `superset_home`
  (caché/archivos), **no** la metadata.
- Para prod: los mismos `DATABASE_*` deben apuntar a una **base `superset` en Cloud SQL** (vía Cloud SQL
  Auth Proxy o IP privada), preferentemente **separada** de la base analítica (`escuela_concausa_db`)
  para acotar el radio de impacto. Host/usuario/password desde **Secret Manager**, nunca en la imagen.
- `superset-init.sh` ya corre `superset db upgrade` al arrancar: crea/migra el esquema de metadata en
  Cloud SQL en el primer boot. Cloud Run es **stateless** → esto es válido justamente porque la metadata
  persiste en Cloud SQL, no en el volumen efímero.

### 2. SECRET_KEY — Secret Manager y cuidado al rotar

- `SUPERSET_SECRET_KEY` hoy sale de `.env` (`scripts/generate-keys.py`, ≥32 chars). En prod: valor
  fuerte y **estable** inyectado desde **Secret Manager** como variable de entorno del servicio.
- **Cuidado al rotar:** la SECRET_KEY firma las sesiones **y cifra las contraseñas de las conexiones a
  bases** guardadas en la metadata. Rotarla **invalida las sesiones activas** y, si hay conexiones
  guardadas, hay que re-cifrarlas con `superset re-encrypt-secrets` **en la misma promoción**, o esas
  conexiones dejan de abrir. Tratar la rotación como paso operativo, no como cambio de env "en caliente".

### 3. Rol invitado de solo lectura (demo pública)

- La demo se enseña sin login (misma postura que `AUTH_LECTURA_PUBLICA=true` en la API, aunque Superset
  tiene su **propio** auth, independiente del RBAC de FastAPI). Para eso, dar de alta un rol
  **`faro_invitado`** (o usar el rol `Public`) con permisos **mínimos de solo lectura**:
  - `can read` sobre `Dashboard`, `Chart` y `Dataset`, con acceso **solo** a los datasets del alcance.
  - **Sin** SQL Lab, **sin** "Upload CSV/Excel", **sin** acceso a *Database connections* ni a *Security*.
  - Acceso explícito a DB-01…DB-10; nada más.
- Marcar los tableros como *published*; si se usa el rol `Public`, activar `PUBLIC_ROLE_LIKE` con cuidado
  (otorga permisos a **todo** anónimo). **La decisión de hacer públicos los tableros es del PO** (misma
  compuerta que la allowlist / `ANALISTA_EMAILS`).

### Prerequisitos de datos y de servidor (antes del primer deploy)

- **Orden de build P-03:** cargar geometrías **antes** de construir Gold. Si dbt corre primero,
  `gold.geo_municipio` queda como *stub* y el coroplético de DB-02 (KPI-10) truena. Secuencia:
  `cargar_geojson_municipios.py` → `dbt run` (Gold) → `sync_semantic_layer.py`.
- **Cubos C1 materializados (US-205):** los datasets virtuales leen `gold.cubo_*` (incl. `cubo_pivot` y
  `cubo_escuela_360`). Un cubo faltante hace fallar el `sync` **completo**: importa todos los
  `semantic/*.sql` en bloque y un solo 500 aborta todo.
- **Servidor de prod:** arrancar con **gunicorn** (la imagen oficial trae `run-server.sh`), no con
  `superset run --reload` (servidor de desarrollo, el que usa `superset-init.sh` hoy).
- **Caché:** backend de resultados externo (**Redis** / `DATA_CACHE_CONFIG`) — ver el workaround de
  "Waiting on…" arriba; en prod evita el cuelgue de charts.

### Checklist de promoción (C5)

- [ ] Cloud SQL con base `superset` (metadata) + `DATABASE_*` desde Secret Manager
- [ ] `SUPERSET_SECRET_KEY` estable desde Secret Manager (plan de rotación con `re-encrypt-secrets`)
- [ ] Rol `faro_invitado` / `Public` de solo lectura con acceso solo a DB-01…DB-10 (aprueba PO)
- [ ] geo → dbt Gold → sync en ese orden (P-03); cubos `gold.cubo_*` materializados
- [ ] gunicorn (no `superset run`) + Redis para caché de resultados
- [ ] `CORS_ORIGINS` y dominio público configurados; TLS/rate-limit/WAF por `docker/README-SECURITY.md`

## Responsables

- **Convención (US-202):** Manuel Alejandro Serranía Reinada (Tech Lead C2).
- **Contenido por historia:** el owner de cada US-211a/b…215a/b y US-221/222 declara sus datasets/métricas
  siguiendo esta convención y alineando nombres con el catálogo de KPIs.
