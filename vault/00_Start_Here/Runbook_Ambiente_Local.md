---
id: DOC-RUNBOOK-LOCAL
title: "Runbook — Levantar el ambiente local de FARO"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
version: "1.0"
traces_up: ["BUG-012", "US-502", "REQ-005"]
traces_down: ["vault/04_UX_Design/Superset_Setup_US202", "vault/08_CICD_DevOps/Guia_Local_API_Postgres"]
last_reviewed: "2026-09-04"
tags: [runbook, local, docker, dbt, superset, onboarding, bug-012]
---

# Runbook — Levantar el ambiente local de FARO

> **Cierra BUG-012.** Antes de este documento, los pasos vivían dispersos entre `.env.example`, un
> DevLog personal, `superset/README.md` y dos scripts sin documentar. Héctor Morales reconstruyó el
> pipeline leyendo el DevLog de Marina del 27-ago —correcto entonces, incompleto después— y publicó
> un diagnóstico falso contra un modelo ajeno: *"un runbook que vive en un DevLog no se actualiza
> cuando cambia el repo"*.
> → [[vault/00_Start_Here/_index]] · [[vault/00_Start_Here/Developer_Onboarding]]

**Verificado de punta a punta el 2026-09-04** en macOS 15 / Docker 29.6.2 / Python 3.11.16, desde
una máquina sin `.env` y sin perfil de dbt. Cada paso trae la cifra que debe salir: si tu número no
coincide, algo se rompió ahí y no más adelante.

---

## 0. Prerrequisitos

| Requisito | Verificación |
|---|---|
| Docker Desktop **corriendo** | `docker ps` responde sin error |
| Python 3.11 con el venv del repo | `.venv/bin/python --version` |
| ~3 GB libres de disco | Las imágenes de `api` y `superset` |

Si el venv no existe: `python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

**No corras `setup_proyecto.sh`.** No es un launcher: es un scaffolder de un solo uso que
*sobrescribe* `.env.example`, `.gitignore`, `ci.yml` y `CODEOWNERS` con versiones de agosto.

---

## 1. Configuración (una sola vez)

### 1.1 `.env`

```bash
cp .env.example .env
python3 scripts/generate-keys.py
```

El script imprime 9 valores. Pégalos en `.env` sustituyendo los placeholders `GENERAR_CON_SCRIPT_*`,
y reemplaza también las dos apariciones del literal `CAMBIAR_POR_PASSWORD_POSTGRES` (líneas 20 y 30)
por el `POSTGRES_PASSWORD` que acabas de generar.

Anota `SUPERSET_ADMIN_USERNAME` y `SUPERSET_ADMIN_PASSWORD`: son tus credenciales de Superset.

`.env` está en `.gitignore` (patrón `*.env`). **Nunca lo subas.**

### 1.2 Perfil de dbt

`dbt/dbt_project.yml` declara `profile: 'faro'` y el perfil vive **fuera del repo** porque lleva
contraseña. Crea `~/.dbt/profiles.yml`:

```yaml
faro:
  target: local
  outputs:
    local:
      type: postgres
      host: localhost          # NO 'db': dbt corre en el host, fuera de la red de Compose
      port: 5432
      user: postgres
      password: "{{ env_var('POSTGRES_PASSWORD') }}"
      dbname: escuela_concausa_db
      schema: public           # los modelos van a silver/gold vía macros/generate_schema_name.sql
      threads: 4
```

---

## 2. Levantar los contenedores

```bash
docker compose up -d db api superset
docker compose ps            # esperar db, api y superset en 'healthy' (~45 s la primera vez)
```

`airflow`, `mlflow` y `chromadb` **no son dependencia de nada de lo anterior**: se omiten salvo que
los necesites (`docker compose up -d mlflow` → :5001, `airflow-webserver` → :8080, `chromadb` → :8001).

| Servicio | URL | Notas |
|---|---|---|
| Postgres | `localhost:5432` | db `escuela_concausa_db`, user `postgres`. Ligado a 127.0.0.1 |
| API | `http://localhost:8000/api/v1/docs` | Swagger. **Todo cuelga de `/api/v1`**, no de la raíz |
| Superset | `http://localhost:8088` | Usuario/clave = `SUPERSET_ADMIN_*` de tu `.env` |

Comprobación rápida: `curl -s localhost:8000/api/v1/health` → `{"status":"ok"}`.

---

## 3. Poblar la base

Los tres `export` de abajo son obligatorios y son justo lo que BUG-012 nunca documentó:

```bash
source .venv/bin/activate
set -a; source .env; set +a
export POSTGRES_HOST=localhost   # el .env trae 'db' (red de Compose); los scripts corren en el host
export DATABASE_URL="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB"
```

### 3.1 Bronze — Formato 911: los **tres** fixtures a la **misma** tabla

```bash
for f in bronze_formato911_sample bronze_formato911_ciclo_anterior_sample bronze_formato911_serie_historica_sample; do
  python -m src.ingesta.cargar_bronze_fixture --fixture tests/fixtures/$f.csv \
      --tabla formato911_2024_2025 --esquema formato911
done
python -m src.ingesta.cargar_bronze_fixture \
  --fixture tests/fixtures/bronze_formato911_historico_sample.csv \
  --tabla formato911_historico --esquema formato911_historico
```

**Esperado: 73 + 25 + 144 = 242 filas** en `bronze.formato911_2024_2025`, más 182 en el histórico.

⚠️ Con menos de los tres, `gold.fact_escuela_ciclo` sale en **0 filas sin ningún mensaje de error**
—el hecho filtra `where matricula_ciclo_anterior is not null`—. Es el error que más ha costado al
equipo y la razón por la que este runbook existe.

### 3.2 Bronze — los 8 fixtures de drivers

Los nombres de `--tabla` son los `identifier` por default de `dbt/models/sources.yml`; usarlos evita
tener que pasarle `--vars` a dbt.

| Fixture (`tests/fixtures/`) | `--tabla` | `--esquema` | Filas |
|---|---|---|---|
| `bronze_cct_sample.csv` | `cct_siged_202608` | `cct` | 72 |
| `bronze_cemabe_sample.csv` | `cemabe_2013` | `cemabe` | 72 |
| `bronze_coneval_irs_sample.csv` | `coneval_irs_2020` | `coneval_irs` | 12 |
| `bronze_coneval_pobreza_sample.csv` | `coneval_pobreza_2020` | `coneval_pobreza` | 12 |
| `bronze_sesnsp_sample.csv` | `sesnsp_test` | `sesnsp` | 72 |
| `bronze_conapo_sample.csv` | `conapo_sample` | `conapo` | 36 |
| `bronze_sinaica_estaciones_sample.csv` | `sinaica_estaciones_test` | `sinaica_estaciones` | 4 |
| `bronze_sinaica_observaciones_sample.csv` | `sinaica_observaciones_test` | `sinaica_observaciones` | 10 |

CONEVAL son **dos** archivos desde el 2026-09-04 (BUG-045 partió el esquema viejo en `irs` +
`pobreza`). Toda la documentación anterior dice "siete fixtures de drivers": hoy son ocho.

### 3.3 Geometrías, dbt, ML y cubos — **el orden no es negociable**

```bash
python superset/cargar_geojson_municipios.py            # → 317 geometrías
cd dbt && dbt seed                                      # → gold.dim_driver
dbt run --full-refresh                                  # → 15 modelos OK, 9 ERROR (esperado)
cd .. && python -m src.modelos.publicar_gold --desde-gold
cd dbt && dbt run --select "gold.cubo_*"                # → 8 de 9
cd .. && python superset/sync_semantic_layer.py --validar-datos
```

Las cuatro reglas de orden, cada una con su consecuencia si se rompe:

1. **Geometrías antes que dbt.** Si no, `gold.geo_municipio` queda como stub y el coroplético de
   DB-02 (KPI-10) truena.
2. **`dbt seed` antes que `dbt run`.** Sin `gold.dim_driver` fallan 6 cubos.
3. **`--full-refresh` obligatorio.** Sin él "la tabla vacía se queda vacía".
4. **ML antes que los cubos.** `dbt run --full-refresh` deja 9 errores *a propósito*: 8 cubos que
   piden `gold.predicciones` (que aún no existe) y `silver.agua_region`. Después de
   `publicar_gold --desde-gold`, la segunda pasada de cubos los levanta. Invertir el orden hace
   fallar los 9 sin remedio.

**Cifras esperadas:**

| Paso | Resultado |
|---|---|
| `dbt run --full-refresh` | `gold.fact_escuela_ciclo` **145**, `gold.features_escuela` **145 filas / 3 ciclos** |
| `publicar_gold --desde-gold` | ML-01 MAE **0.0844**, **55** predicciones · ML-02 F1 macro **0.6458**, **55** recomendaciones |
| `dbt run --select "gold.cubo_*"` | **8 de 9** cubos |
| `sync_semantic_layer.py` | **103 charts**, **9 tableros** |

---

## 4. Verificar

```bash
curl -s localhost:8000/api/v1/kpis
```

Debe devolver **`matricula_total: 11828`** — el ciclo vigente. Si sale **32 312** estás viendo la
suma de los 3 ciclos: sería BUG-044/BUG-047 revividos.

```sql
-- SQL Lab de Superset (menú SQL → SQL Lab), o docker compose exec db psql -U postgres -d escuela_concausa_db
select count(*), count(distinct id_ciclo) from gold.features_escuela;  -- 145, 3
select count(*) from gold.predicciones;                                -- 55
```

En el navegador: **9 tableros** en Superset (DB-01 a DB-09), Swagger en `/api/v1/docs` con "Try it
out" — la lectura es pública (`AUTH_LECTURA_PUBLICA=true`), no necesitas token para `/kpis`,
`/escuelas`, `/municipios`.

Para explorar la base sin instalar nada: **SQL Lab** de Superset ya queda conectado a Postgres por
el sync; ahí ves `bronze.*`, `silver.*` y `gold.*`.

---

## 5. Techos conocidos con solo fixtures

Todo lo de abajo es **comportamiento correcto**, no una falla de tu ambiente:

- **DB-10 y `gold.cubo_pipeline` no se materializan.** Requieren `bronze.conagua_presas`, que solo
  carga `cargar_bronze_conagua_real.py --parquet` con el parquet real de CONAGUA. Verás 9 tableros,
  no 10, y `dbt test` reporta un ERROR esperado en `cubo_pipeline_rows_parity`.
- **`silver.agua_region` falla** (`bronze.conagua_no_ingerido` no existe) → el driver **D5 sale
  `SIN_DATO` en las 145 filas**. Es la regla de cobertura parcial del proyecto funcionando: nunca
  cero silencioso. `publicar_gold` lo avisa y entrena con 5 de 6 drivers.
- **El login con Google no funciona local**: `GOOGLE_CLIENT_ID`/`SECRET` van vacíos por diseño. La
  lectura pública cubre todo lo demás.
- **`indice_completitud_drivers ≈ 0.65`**, no 1.0 — consecuencia directa de D5 sin datos.

### Nota sobre `escuelas_en_riesgo`

Con el pipeline completo **post-BUG-045** este ambiente devuelve **2 escuelas** en riesgo
(máx. `indice_riesgo` 0.7423, peor variación proyectada −7.60 %) y 12 más en la banda 0.40–0.60.

Las corridas del 3-sep reportaban **0** con máximo 0.5615. La diferencia no es azar —ML-01 fija
`random_state: 0`— sino **datos**: aquel día CONEVAL no tenía fixture compatible y D1 iba vacío. Hoy
D1 tiene dato en 145 de 145. Quien cite el "0" de aquellas corridas está citando un ambiente con un
driver menos.

---

## 6. Operación diaria

```bash
docker compose ps                    # estado
docker compose logs -f api           # logs de un servicio
docker compose restart superset      # charts colgados en "Waiting on ..." (caché en memoria)
docker compose stop                  # apagar sin perder datos
docker compose down -v               # ⚠️ BORRA el volumen: hay que repetir la sección 3 completa
```

Recargar datos **no** requiere reconstruir: los cargadores de fixtures son idempotentes
(`ON CONFLICT DO NOTHING`) y `publicar_gold` hace upsert.

---

## 7. Problemas conocidos

| Síntoma | Causa | Solución |
|---|---|---|
| `could not translate host name "db"` | Falta `export POSTGRES_HOST=localhost` | Es el error #1 del equipo. Va antes de **cualquier** script del host |
| `gold.fact_escuela_ciclo` en 0 filas, sin error | Faltó alguno de los 3 fixtures de Formato 911 | Cargar los tres (§3.1) y repetir `dbt run --full-refresh` |
| 6 cubos fallan | Faltó `dbt seed` | Correr `dbt seed` y repetir |
| Los 9 cubos fallan | Se corrieron los cubos antes de `publicar_gold` | Respetar el orden de §3.3 |
| `publicar_gold` no conecta | Falta `DATABASE_URL` | No se deriva del `.env`; hay que exportarla |
| Charts en "Waiting on ..." | Caché en memoria de Superset tras el sync | `docker compose restart superset` |
| `Columns missing in dataset` | **BUG-037**, abierto | `PUT /api/v1/dataset/<id>/refresh` |
| `scripts/verificar-servicios.sh` reporta FAIL de la API | El script consulta `/health`; la app monta `/api/v1/health` | Pendiente de C5. Usa `curl localhost:8000/api/v1/health` |

---

## Ver también

- [[vault/04_UX_Design/Superset_Setup_US202]] — detalle de Superset (su §"docker exec faro-superset"
  quedó obsoleto: los `container_name` fijos se eliminaron el 29-ago; usa `docker compose exec superset`)
- [[vault/08_CICD_DevOps/Guia_Local_API_Postgres]] — guía de C4, anterior a este runbook
- `superset/README.md` §"Cadena local completa" — el paso 3 (mock de ML) quedó superado por
  `publicar_gold --desde-gold`
