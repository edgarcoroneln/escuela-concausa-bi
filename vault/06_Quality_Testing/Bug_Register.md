---
id: DOC-BUGREG
title: "Bug Register"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
source_of_truth: true
tags: [qa, bugs]
---

# Bug Register — FARO

> Registro único de defectos. Detalle de cada uno con [[vault/_Templates/Bug_template]].
> → [[vault/06_Quality_Testing/_index]]

| BUG | Título | Severidad | Estado | US/REQ | Fix (PR) | Test regresión |
|---|---|---|---|---|---|---|
| BUG-001 | dag_anual.py: falta start_date | high | fixed | US-102 | fix/diana-varela-us102-dag-import-errors | manual (ver detalle) |
| BUG-002 | dag_censal_estatico.py: preset de cron no soportado | high | fixed | US-102 | fix/diana-varela-us102-dag-import-errors | manual (ver detalle) |
| BUG-003 | `sklearn` no instalado: `test_entrenar_ml01.py` y `test_entrenar_ml02.py` fallan con `ModuleNotFoundError` en colección de pytest | low | **not_a_bug** | US-311 / REQ-003 | ya resuelto en `main` desde 2026-08-13 (PR #28) — ver detalle | ambiente local desactualizado |
| BUG-043 | **El Model Registry acepta versiones cuyo modelo nunca llegó, y las deja `READY`.** `mlflow.register_model()` crea la versión aunque `log_model()` haya fallado, así que la UI y `search_model_versions` muestran un modelo que ningún cliente puede cargar. Dos configuraciones lo provocan: (1) `--default-artifact-root` es una ruta de disco (`/mlflow/artifacts`) en vez del proxy `mlflow-artifacts:/`, y el cliente la resuelve contra su propio disco → `OSError: Read-only file system: '/mlflow'`; (2) falta `--artifacts-destination`, y los artefactos caen en la capa **efímera** del contenedor: **verificado que un solo `docker compose up --force-recreate` convierte los tres modelos en fantasmas**, lo cual es fatal en Cloud Run, donde recrear el contenedor es rutina. `ML01_RegresionMatricula` v1 estuvo así desde el 18-ago y **AC-003.4 se dio por cumplido sin estarlo**. Bloquea la inferencia de C4, que carga por `models:/…` | **critical** | **fixed (parcial)** | US-311 / US-303 / REQ-003 / AC-003.4 | **C3 ✅ (Héctor, 2026-09-03):** la guarda `verificar_artefactos_descargables()` carga cada versión con `pyfunc` y reprueba; `.env.example` pasa a `MLFLOW_ARTIFACT_ROOT=mlflow-artifacts:/`. Con eso **AC-003.4 queda CUMPLIDO**: los tres modelos registrados y **carga verificada** (ML-01 v4, ML-02 v2, ML-03 v2) — sin tocar `docker-compose.yml`. **Corrección de mi diagnóstico del 2-sep:** culpé a la falta de `--serve-artifacts`, pero en MLflow 3.x **viene activo por defecto** (`--help`: `Default: True`); la causa era la raíz de artefactos. **Pendiente C5 ⬜:** agregar `--artifacts-destination /mlflow/artifacts` al `command:` del servicio `mlflow` — sin eso el registry es efímero (probado en los dos sentidos: con el flag los tres sobreviven al `--force-recreate`; sin él, mueren) | `tests/test_mlflow_utils.py::test_artefacto_ausente_reprueba_aunque_la_version_exista` (exige que el mensaje nombre `--artifacts-destination` y `MLFLOW_ARTIFACT_ROOT`) |
| BUG-004 | Imagen `apache/superset:latest` no incluye `psycopg2`: conexión a PostgreSQL falla con 422 al crear datasets virtuales | medium | open | US-202 | pendiente (**C5**, Edward Ruiz — US-522c) | — |
| BUG-005 | Scripts `.sh` se corrompen a CRLF en checkouts de Windows: `.gitattributes` no tiene regla `*.sh text eol=lf`, así que con `core.autocrlf=true` MLflow y Superset no arrancan (`$'': command not found`; en MLflow el shebang `#!/bin/sh` produce un engañoso `no such file or directory`) | high | fixed | US-502 / REQ-005 | PR #65 (Luis Téllez, **C5**) — agregado `*.sh text eol=lf` a `.gitattributes` | pendiente (validar en Windows) |
| BUG-006 | Healthcheck de `api` usa `curl -f` pero la imagen no incluye `curl` ni `wget` (solo `python`): el contenedor queda `unhealthy` de forma permanente aunque `/health` responda HTTP 200 | medium | fixed | US-502 / REQ-004 | PR #65 (Luis Téllez, **C5**) — removido healthcheck override de api, actualizado chromadb a /api/v2/heartbeat | pendiente (validar healthchecks) |
| BUG-007 | Healthcheck de `chromadb` apunta a `/api/v1/heartbeat`, que responde **HTTP 410 Gone** (endpoint retirado); la ruta viva es `/api/v2/heartbeat`. Además arrastra el mismo problema de `curl` de BUG-006 | medium | fixed | US-502 / REQ-006 | PR #65 (Luis Téllez, **C5**) — actualizado puerto MLflow en documentación (5000 → 5001) | validado |
| BUG-008 | `docker/api.Dockerfile` arranca `src.api.main:app` (el hola mundo de US-501, **3 rutas**) en vez de `src.api.app:app` (la app real del contrato v1, **18 rutas** bajo `/api/v1`): en el contenedor —y en la URL pública si usa este Dockerfile— **US-401, US-402 y US-411 son inalcanzables** | **high** | **fixed** | US-501 / US-411 / REQ-004 / REQ-005 | fix/luis-tellez-bug008-api-dockerfile (Luis Téllez, **C5**, 27-ago) — 1 línea en Dockerfile + redeploy urgente a producción | `tests/test_docker_api_entrypoint.py` (3 pruebas, PR #137): lee el CMD del Dockerfile, importa la app declarada y compara sus rutas contra el esquema OpenAPI de `src.api.app` en vivo |
| BUG-009 | 11 vars de dbt sin valor por default (7 `identifier` de fuentes Bronze + 4 vars de modelo): cualquier `dbt parse`/`build`/`run` falla al renderizar el manifest aunque el modelo probado no use esas fuentes | high | fixed | US-111 | defaults inline en `sources.yml` + bloque `vars:` en `dbt_project.yml` (DEC-011) | `dbt parse` en `ci.yml` (job `dbt-contract`) |
| BUG-010 | `/api/v1/predicciones/*` sigue leyendo `src/api/mock_data.py` en vez de `gold.predicciones` + `gold.recomendaciones`: la verificación **#4 del ensayo E2E** («≥1 modelo sirviendo por API») devolvería un valor fijo, no la predicción de ML-01 | **high** | fixed | US-412 / US-415 / REQ-004 / REQ-003 | `feat/juan-mayen-us415-pydantic-schemas` — `src/api/repositorio_modelos.py` (`RepositorioModelos` sobre Postgres, mismo patrón `Depends` que `RepositorioGold`); `PrediccionOut.cluster` pasa a `StrictInt \| None` (ML-03 sin productor, US-321) · `tests/test_api_contract.py::test_prediccion_combina_ml`, `test_prediccion_cct_sin_fila_404`, `test_prediccion_batch_omite_ccts_sin_fila` (fake en `tests/fixtures_modelos.py`) |
| BUG-011 | `sync_semantic_layer.py` lee YAML/SQL con la codificación del sistema (`read_text()` sin `encoding`): en Windows usa cp1252 y truena con los acentos de cualquier `metrics_*.yaml`; el script solo corre con `PYTHONUTF8=1`. Misma familia que BUG-005 (locale de Windows) | medium | fixed | US-203 / US-212 | `fix/manuel-serrania-bug010-sync-charts-utf8` — `encoding="utf-8"` explícito en las 3 lecturas (`_read_yaml`, `_read_sql`) | pendiente (validar en Windows) |
| BUG-012 | No existe runbook para levantar el pipeline local: `dbt/README.md` es el scaffold por defecto de dbt, no hay `profiles.yml` ni se documenta dónde ponerlo, y **cargar solo `bronze_formato911_sample.csv` deja `gold.fact_escuela_ciclo` en 0 filas** — hay que cargar también `bronze_formato911_ciclo_anterior_sample.csv` en la MISMA tabla para que `lag()` encuentre pares. Nada de esto está escrito. | high | **fixed** | US-112 / US-113 / REQ-001 | resuelto 2026-09-04 (**Edgar Coronel, PM**): [[vault/00_Start_Here/Runbook_Ambiente_Local]] — runbook canónico `approved`/`source_of_truth`, verificado de punta a punta en una máquina sin `.env` ni perfil de dbt. Documenta los 4 pasos que ningún documento recogía: `dbt seed` antes de `dbt run`, el orden ML-antes-de-cubos, `export POSTGRES_HOST=localhost` (el `.env` trae `db`) y `DATABASE_URL` para `publicar_gold`. Corrige además el conteo de fixtures: son **tres** de Formato 911 a la misma tabla (242 filas) y **ocho** de drivers, no siete — CONEVAL se partió en `irs`/`pobreza` con BUG-045 | ✅ verificado corriéndolo el 2026-09-04, con la cifra esperada por paso: 242 filas en bronze, `gold.fact_escuela_ciclo` 145, `features_escuela` 145/3 ciclos, ML-01 MAE 0.0844, 55 predicciones + 55 recomendaciones, 8 de 9 cubos, 103 charts y 9 tableros en Superset, `/api/v1/kpis` = 11 828 (ciclo vigente). Cada número queda escrito en el runbook para que una desviación futura se note en el paso exacto donde ocurre. Pendiente ajeno, anotado y no corregido aquí: `scripts/verificar-servicios.sh` consulta `/health` cuando la app monta `/api/v1/health` (falso FAIL de la API) — `scripts/**` es alcance de C5
| BUG-013 | `publicar_gold.py` usa por defecto el fixture sintético `tests/fixtures/features_escuela_mock.csv`, no `gold.features_escuela`: publica 80 filas de **ciclo 2023-2024** mientras el hecho real tiene 25 de **2024-2025**. El JOIN por `(cct, id_ciclo)` da cero, así que DB-03 muestra `cobertura_prediccion = SIN_DATO` en el 100% de las escuelas y los bloques de predicción y recomendación (AC-002.4) quedan vacíos. Apuntarlo al Gold real tampoco basta hoy: `features_escuela` tiene un solo ciclo y ML exige partición temporal. | high | **fixed** | US-313 / US-113 / REQ-003 | **C3 ✅** (`a76c748`, Héctor): el hueco era que `publicar_gold.py` no sabía leer de una tabla; `cargar_features_desde_gold()` + `--desde-gold`. **C1 ✅ con datos reales** (Diana, 27-ago): 4 ciclos reales cargados en `bronze.formato911_2024_2025` → estrella completa y 8 cubos, 149/149 tests. **Lo que queda ⬜:** no es reproducible fuera del ambiente de Diana — con los fixtures del repo `features_escuela` sigue saliendo con 1 ciclo, así que **la dueña de DB-03 no puede verificar sus propios bloques ML (AC-002.4)** ni CI ejercitar la ruta. Ver **BUG-026** · **2026-09-03 ✅ RESUELTO — verificado por Marina García.** Ese último hueco cerró: con los **tres** fixtures de Formato 911 (el tercero, `bronze_formato911_serie_historica_sample.csv`, lo creó Diana para BUG-026) `gold.features_escuela` sale con **145 filas y 3 ciclos**, y `publicar_gold --desde-gold` publica **55 predicciones + 55 recomendaciones** — mismas cifras que reprodujo Héctor Morales el mismo día. **AC-002.4 ya es verificable en un ambiente armado solo con fixtures del repo**: DB-03 muestra 55 escuelas con `cobertura_prediccion = OK` y 90 con `SIN_DATO` (los ciclos sin predicción), y el `indice_riesgo` va de 0.1637 a 0.5615 — ya no saturado, que era el síntoma de BUG-017 | verificado en local (Marina, 28-ago): `--desde-gold` → `ValueError: Con 1 ciclos no se puede hacer backtesting… Ciclos disponibles: ['2024-2025']` |
| BUG-014 | `quality_gate.yml` busca el token de casilla sin marcar en **todo el cuerpo del PR** con `grep -q "\[ \]"`, no solo en ítems de lista: basta con **mencionar** esa sintaxis dentro de una explicación —aunque vaya en backticks— para que el check falle. Sumado a que la plantilla oficial trae la casilla de aprobación del PM sin marcar (le toca marcarla a él al revisar), **la plantilla del repo no puede pasar su propio gate** y empuja a los autores a borrar el registro de aprobación o a marcarlo ellos mismos. | medium | **fixed** | US-503 / REQ-007 | `fix/edgar-navarrete-mojibake-higiene-vault` (Edgar Coronel, PM — **revisión de C5 solicitada a Luis Téllez por regla 7**). Tres cambios: el patrón se acota a `grep -qE '^[[:space:]]*-[[:space:]]*\[ \]'`; la sección `## Aprobación` se recorta antes de evaluar, porque es del PM y se marca al revisar; y se agrega el evento **`edited`**, sin el cual un cuerpo corregido después del push se quedaba en rojo para siempre; además, las dos casillas que un autor honesto no puede marcar —`(Alternativa) No usé IA` y `Si toqué esquema…`— se marcan `<!-- opcional -->` en la plantilla y el gate las omite (hallado al revisar el PR #110) | `.github/scripts/probar_verificar_plantilla.sh` — 7 casos contra el script real, leyendo `.github/PULL_REQUEST_TEMPLATE.md` del archivo (no una copia): la plantilla llenada por el autor pasa, sin llenar reprueba, las casillas opcionales marcadas con `<!-- opcional -->` no cuentan, y mencionar la sintaxis en prosa ya no reprueba |
| BUG-015 | ML-01 no podía entrenar sobre `gold.features_escuela` real: un driver **100 % `SIN_DATO`** (D5 agua, DS-06 sin descarga) rompe el binning de `HistGradientBoostingRegressor` con `window shape cannot be larger than input array shape`, un error que no delata la causa. Además el default `--ventanas 3` pedía 5 ciclos y el Gold real sólo tiene 3 utilizables | high | **fixed** | US-311 / US-313 / REQ-003 | `fix/hector-marban-driver-sin-datos` | — |
| BUG-016 | La publicación a Gold tronaba en ML-02 con datos reales: hay filas con los **6 drivers en NULL a la vez**, y `generar_driver_dominante_proxy` falla ahí por diseño. La `driver_dominante` real de C1 (US-302, PR #113) ya adoptó la convención de dejarlas en NULL; faltaba apartarlas antes de entrenar, porque `validar_target_ml02` rechaza nulos. Conservan su predicción de ML-01 y no reciben recomendación (`SIN_DATO`, nunca un driver inventado) | high | **fixed** | US-313 / REQ-003 | `fix/hector-marban-driver-sin-datos` | — |
| BUG-017 | `indice_riesgo` se publicó **saturado**: la corrida real de ML-01 dio MAE 10.90, pero la sigmoide está calibrada sobre **fracción** (`-0.05` = pierde 5 % de matrícula). Con esa escala el 100 % de las 45 249 filas queda en riesgo ≈ 1.00 y el tablero cuenta como "en riesgo" a todo el universo. **Confirmado por Diana el 2026-08-28**: `target_variacion_matricula = matricula_total - matricula_ciclo_anterior`, diferencia absoluta de alumnos. El MAE 10.90 son ~11 alumnos, no un modelo malo; lo que está mal es publicar eso a través de una sigmoide calibrada sobre fracción. Añadida guarda que detiene la publicación en vez de saturar en silencio | high | **fixed** | US-311 / US-313 / REQ-003 / US-104 | `fix/diana-varela-bug017-target-fraccion` (Diana Alvarez, C1) — ratifica [[vault/03_Architecture/ADRs/ADR-007-unidad-target-variacion-matricula\|ADR-007]] (2026-08-29): `features_escuela.sql` (CTE `base`) pasa de diferencia absoluta a **fracción** (`matricula_total/matricula_ciclo_anterior - 1.0`, cast a `double precision` antes de dividir, división nativa de Postgres sin `nullif` rechaza `matricula_ciclo_anterior=0` en vez de silenciarlo). Unidad declarada en `src/modelos/contrato.py` y `Data_Model.md` §5.3 | dbt test nuevo `features_escuela_target_variacion_escala` (mediana \|target\|≤1.0, mismo umbral que `verificar_escala_variacion()` de Héctor) · verificado con datos reales: `dbt run --full-refresh` sin división por cero (ninguna escuela real con matrícula previa 0), `dbt test` limpio salvo el hueco ya conocido de DS-07/CONEVAL (no relacionado, ver US-325) · **pendiente C3 (Andrés González):** regenerar las 45 249 filas de `gold.predicciones` (quedaron saturadas con la unidad vieja) y reentrenar ML-01 (el MAE deja de leerse en alumnos) · [[vault/_DevLog/2026-08-31-diana-alvarez-bug017-bug019-target-fraccion]] |
| BUG-018 | ML-02 arrastra el **mismo defecto por ventana** que BUG-015: `entrenar_ml02._matriz()` toma siempre los 6 drivers sin comprobar cobertura dentro de la ventana de entrenamiento, así que un driver vacío en ese tramo (D6 aire, IDW de US-105) rompe el binning de `HistGradientBoostingClassifier` con el mismo error. Reproducido; el arreglo es el mismo que ya se aplicó en ML-01 | high | **fixed** | US-302 / REQ-003 | `feat/andres-habib-bug018-ml02-cobertura` (Andrés González) — cobertura evaluada por ventana y predicción/SHAP alineados con `feature_names_in_`. **Corregido el 29-ago en el registro**: la matriz de trazabilidad ya lo daba por resuelto desde el 28-ago pero esta fila seguía en `open`; el registro es la fuente canónica y no puede ir detrás de la matriz | ver detalle |
| BUG-019 | `target_variacion_matricula` se producía en **dos unidades distintas** bajo el mismo nombre: `features_escuela.sql` (C1, grano escuela) daba **alumnos absolutos** y `target_hibrido.variacion_desde_serie` (C3, grano municipio×nivel) da **fracción**. Ambas llegan a `gold.predicciones.valor`, distinguidas sólo por `grano` (DEC-010), así que esa columna mezclaba alumnos con fracciones. El contrato nunca declaraba la unidad | high | **fixed** | US-104 / US-311 / US-313 / REQ-003 | mismo branch que BUG-017: `fix/diana-varela-bug017-target-fraccion` (Diana Alvarez, C1) — las dos unidades quedan unificadas en **fracción**; `src/modelos/contrato.py` y `Data_Model.md` §5.3 declaran explícitamente la unidad por primera vez | verificado junto con BUG-017 (mismo cambio, misma corrida real) · [[vault/_DevLog/2026-08-31-diana-alvarez-bug017-bug019-target-fraccion]] |
| BUG-020 | En la URL pública **toda ruta que toca base de datos responde HTTP 500**: `/api/v1/predicciones/{cct}`, `/predicciones/batch` y `/escuelas`. `/api/v1/health` responde 200, así que el contenedor corre y el despliegue de BUG-008 sirvió. Con token válido, inválido o sin token el resultado es el mismo 500 —nunca 401—, así que el fallo ocurre **antes** de validar auth. Sin esto no hay demo end-to-end ni el punto de rúbrica de URL pública | **critical** | open | US-401 / US-411 / US-501 / REQ-004 / REQ-005 | — | pendiente — **Christian Ruiz (C4) y Luis Téllez (C5); seguimiento diario de Edgar Coronel hasta cerrarlo.** Es el **único riesgo vivo para la casilla 6 del ensayo E2E** y para el punto de rúbrica de URL pública. Sin esto no hay demo end-to-end. Escalado el 29-ago tras dos peticiones de estado sin respuesta |
| BUG-021 | `dbt run` con el número de hilos por defecto (`threads>1`) truena en `gold.dim_escuela`, `dim_municipio` y `dim_tiempo` con *relation does not exist*, aunque su silver de origen se cree casi en el mismo instante. Con `--threads 1` corre limpio de punta a punta. Causa: esos modelos leían su origen con `source('silver', …)` en vez de `ref()`. `silver.*` son modelos **de este mismo proyecto**, no datos externos, así que dbt no tenía cómo saber que debía construirlos antes y los agendaba en paralelo. Con `threads=1` el orden accidental funcionaba y el defecto quedaba escondido | high | **fixed** | US-213 / US-113 / REQ-001 | **Reportado por Monserrat Miranda** (2026-08-28, validando DB-05/DB-08 contra Gold real) · **corregido por Diana Alvarez** en `fix/diana-varela-bug016-source-vs-ref`: los siete modelos Gold pasan a `ref()`; `_gold__sources.yml` queda sólo como documentación de columnas | `dbt run` completo con hilos por defecto ✅ · [[vault/_DevLog/2026-08-29-diana-alvarez-bug021-source-vs-ref]] |
| BUG-022 | `gold.dim_driver` puede quedar desincronizado sin que nada lo detecte: `superset/mock/gold_estrella_mock.sql` (mock previo de C2/US-212, hoy superado) crea la tabla con `CREATE TABLE IF NOT EXISTS` + `INSERT ... ON CONFLICT DO NOTHING` usando nombres largos ("Pobreza y rezago social"...) distintos al catálogo canónico corto del seed (`dbt/seeds/dim_driver.csv`). Si ese mock corre en un entorno donde `dbt seed`/`dbt build` nunca se ejecutó, la tabla se queda con los nombres viejos — la columna `nombre` solo tenía `not_null`, sin `accepted_values`, así que ningún test lo detectaba; el primer síntoma era un HTTP 500 río abajo en Superset (US-213) | high | **fixed** | US-213 / US-113 | **Reportado por Manuel Serranía** (PR #100) y **Monserrat Olivas** (validando US-213 contra Gold real) · **corregido por Diana Alvarez** en `fix/diana-varela-bug022-dim-driver-catalogo`: `accepted_values` sobre `nombre` en `dbt/seeds/_gold__seeds.yml` con los 6 nombres canónicos, documentado en `Data_Model.md` §4.2 | Simulado el estado divergente real (test FALLA con `FAIL 6`) y el estado correcto tras `dbt seed` (PASS limpio) · [[vault/_DevLog/2026-08-29-diana-alvarez-bug022-dim-driver-catalogo]] |
| BUG-023 | Tercera aparición del defecto de BUG-015/BUG-018, ahora en `evaluar.py`: `error_por_entidad()` y `cobertura_y_error()` predecían con los **seis** drivers aunque el modelo se hubiera entrenado con menos, así que `construir_reporte()` **no podía generar el reporte** en el único escenario que el PM necesita documentar para la demo — el de 5 de 6 drivers. `ValueError: The feature names should match those that were passed during fit` | high | **fixed** | US-312 / REQ-003 / AC-003.2 | `feat/hector-marban-drivers-en-evaluacion` | — |
| BUG-024 | `SELECT ... INTO` atravesaba el guardarraíl porque empieza con `SELECT`, pero en PostgreSQL crea una tabla; el agente no tiene otra capa que garantice solo lectura | **critical** | **fixed** | US-304a / US-305 / REQ-006 | `fix/andres-habib-bug024-select-into-rag-empty` | `tests/test_agente_guardrails.py::test_select_into_se_rechaza_como_escritura` |
| BUG-025 | El endpoint desplegado `/api/v1/agente/consulta` es el **stub** de `src/api/v1/agente.py`: responde **la misma cadena fija a cualquier pregunta**, incluidas las fuera de alcance y las destructivas. Además su filtro de palabras busca `"borrar"` por subcadena, así que **«Borra la tabla de predicciones» no lo dispara** y recibe la respuesta normal con `fuera_de_alcance: false`. Los guardarraíles reales de `src/agente/guardrails.py` —que sí rechazan esa frase— nunca se invocan desde la API | high | open | US-304a, US-305, REQ-006 | pendiente (**C4 + C3**): conectar `procesar_consulta_con_rag()` al endpoint; como mitigación inmediata, que el stub llame a `pregunta_en_alcance()` || — 
| BUG-026 | **Ningún juego de fixtures del repo puede ejercitar el grano escuela multi-ciclo.** Hay dos y cada uno resuelve la mitad: `bronze_formato911_sample.csv` + `…_ciclo_anterior_sample.csv` traen CCT coherentes con `gold.dim_escuela` (**59 de 60**) pero solo **2 ciclos**, así que `gold.features_escuela` sale con 1 y ML-01 no puede hacer partición temporal; `bronze_formato911_historico_sample.csv` trae **6 ciclos** pero comparte solo **3 CCT de 30** con `dim_escuela` (se generó sobre su propio universo, disjunto de `bronze.cct`), así que a grano escuela el JOIN se vacía **sin ningún error** — el modo de falla silenciosa de BUG-012. Consecuencia: entrenar ML-01 y verificar los bloques de predicción de DB-03 (AC-002.4) solo es posible con ~460 MB de CSV real en un ambiente propio (hoy, únicamente el de Diana); **CI nunca recorre esa ruta** | high | **fixed** | US-104 / US-113 / US-313 / REQ-001 / REQ-003 | **PR #129** (Diana Alvarez) — fixture aditivo `bronze_formato911_serie_historica_sample.csv`: reutiliza las CCT de `bronze_formato911_sample.csv` tal cual (mismo patrón que `..._ciclo_anterior_fixture.py`) y agrega 2021-2022 y 2022-2023 sobre la MISMA tabla. No toca ningún modelo dbt. **Verificado de punta a punta por la reportante el 29-ago** | — (propuesto: aserción dbt de solape mínimo con `dim_escuela` y de ciclos mínimos en `features_escuela`). **Mergeado el 29-ago**; cierra la mitad que faltaba de BUG-013 | — el fixture *es* la regresión: con él, `features_escuela` sale con 3 ciclos y `publicar_gold.py --desde-gold` entrena. Pendiente la guarda automática propuesta (aserción dbt de solape mínimo con `dim_escuela` y de ciclos mínimos), sin la cual un fixture futuro puede volver a divergir sin que CI lo note 
| BUG-027 | `superset/semantic/metrics_kpis_base_us221.yaml` apunta sus 5 `sql_ref` a `sql/kpi_0*.sql`, ruta que **ya no existe**: el commit `1c2f5f9` movió esos archivos de `superset/sql/` a `superset/semantic/` y actualizó el test, pero no el YAML. Nadie lo nota porque `tests/test_kpis_us221.py` **codifica la ruta a mano** (`SQL_DIR = superset/semantic`) y nunca lee el `sql_ref` del catálogo: la prueba pasa en verde mientras el artefacto que la gente consulta apunta al vacío | medium | **superseded** | US-221 / REQ-002 | US-221 / REQ-002 | **No se corrige la ruta: los archivos desaparecen.** Manuel Serranía ratificó el 28-ago una sola implementación por KPI (regla 1 del vault): se borran los 5 `kpi_*.sql` y las tarjetas se remapean a los datasets canónicos (`db01_cubo_matricula`, `db02_cubo_riesgo_territorial`, `db01_distribucion_escuelas`), sin `sql_ref` a SQL nuevo. Arreglar el `sql_ref` sería trabajo sobre artefactos que se eliminan. Seguimiento en el follow-up de US-221 (C2, Oscar Quiroz) | — **lo que sí sobrevive del hallazgo**: `test_kpis_us221.py` codifica `SQL_DIR` a mano y nunca lee el `sql_ref`, por eso pasaba en verde con el catálogo apuntando al vacío. El follow-up convierte ese test en guarda antiduplicación, que es el requisito que nace de este reporte 
| BUG-028 | `cargar_features()` leía el CSV **sin `dtype`**, así que pandas infería `int64` en `cve_mun` y se comía el cero de la izquierda: `"09001"` llegaba como `9001`. El join contra `dim_municipio` y la agregación de DEC-007 fallaban **en silencio** para las 9 entidades cuya clave INEGI empieza en cero — **CDMX (09) incluida, que es la entidad principal del alcance**. Diana lo había previsto y lo cubrió en `tests/conftest.py`, pero el lector de producción seguía sin ello, así que las pruebas veían la clave correcta y el pipeline no | high | **fixed** | US-325 / US-311 / DEC-007 / REQ-003 | **PR #127** — `dtype={"cve_mun": str}` en `cargar_features()` (`src/modelos/entrenar_ml01.py`). Detectado por la guarda de coherencia entidad↔municipio que el mismo PR agregó a `generar_fixture_dim.py`: reventó de inmediato con `'9001' contradice la entidad '09'` | la guarda misma es la regresión — `generar()` falla si `cve_mun` no empieza con la entidad que codifica el CCT, así que el cero perdido no puede volver a pasar inadvertido |
| BUG-029 | **RESERVADO — Oscar Quiroz (C2).** `superset/sync_semantic_layer.py` recorre alfabéticamente los `.sql` de `superset/semantic/` y **aborta toda la corrida** al llegar a `db09_cubo_recomendaciones.sql` si `gold.recomendaciones` no existe. No es error del SQL: en un ambiente sin la cadena Bronze→Gold materializada, nadie que sincronice después de `db09` alfabéticamente puede registrar sus datasets. Detectado por Oscar al construir DB-07 (US-222) | medium | **fixed** | US-222 / US-223 / US-205 / REQ-002 | **2026-09-02 (Oscar Quiroz, C2, confirmado por Edgar Coronel):** `ensure_datasets()` envuelve el POST/PUT de cada dataset en `try/except` — un dataset roto se reporta y se omite (no entra a `datasets`), el resto de la corrida continúa. `ensure_chart()` ya omitía charts de datasets ausentes (`-1`), así que el efecto en cascada queda cortado en el único punto real de falla. Mitigación inmediata (`gold_ml_outputs_mock.sql`) sigue documentada para quien la necesite en su ambiente local | `tests/test_sync_resiliencia_bug029.py` — 3 casos: dataset roto no aborta los posteriores (db10 se registra aunque db09 falle), un dataset sano antes del roto no se ve afectado, guarda de no-regresión sin fallos |
| BUG-030 | **El esquema real de DS-06 no es el que `silver/agua_region.sql` espera, y el riesgo no es que D5 siga en `SIN_DATO` sino que alguien lo saque con la columna equivocada.** El extractor entrega `id_presa, nombre_oficial, corriente, estado, anio_term, alt_cort, cap_name, cap_namo`; el modelo espera `id_punto, region_hidrologica, latitud, longitud, indicador, valor, fecha`. **Ninguna de las cuatro columnas que importan existe** — no es renombrar, son dos estructuras distintas. Dos huecos: (1) sin `lat`/`lon` no hay interpolación IDW, que `Data_Model.md` §3 exige para D5; (2) `cap_name`/`cap_namo` son la **capacidad máxima** de la presa, no el volumen actual, así que conectarlas produciría un indicador constante en el tiempo que mide el tamaño de la presa y no la disponibilidad hídrica — un número creíble y falso, misma familia que el `indice_riesgo` saturado y el `*100`. Hoy no rompe nada porque BUG-009 mantiene el identifier falso y D5 sigue `SIN_DATO` explícito. Reportado por Diana Alvarez (C1) el 30-ago al revisar los metadatos de DS-06/DS-08, que **sí** están limpios | high | open | US-122a / US-112 / REQ-001 / DS-06 | pendiente (**C1 + Emilio Galnares**) — la solución ya está documentada en la ficha DS-06 §64-70 (endpoint «Detalle por presa: Presa, Año, Vol. de almacenamiento (hm3) — SERIE DE TIEMPO») y §74 (georreferencia vía datos.gob.mx). El extractor de US-122a jaló el listado general porque eso pedía la historia. **Decisión pendiente del PM:** ampliar el extractor, o documentar D5 como cobertura parcial explícita para la demo | — (propuesto: aserción de contrato entre las columnas de `bronze.conagua` y las que `agua_region.sql` consume) |
| BUG-031 | **KPI-02 «Variación de matrícula» pinta −54.5 % donde el valor real es −0.19 %, en SEIS tableros: DB-01, DB-02, DB-03, DB-04, DB-06 y DB-09.** La métrica es `SUM(variacion_matricula * matricula_total) / NULLIF(SUM(matricula_total), 0)` con `formato: porcentaje_1`, es decir un **promedio ponderado de razones**… salvo que `variacion_matricula` no es una razón: `fact_escuela_ciclo.sql` la produce como `matricula_total - matricula_ciclo_anterior`, **alumnos absolutos** (rango observado −24 a 24). El resultado se renderiza como porcentaje, que multiplica por 100 otra vez. Verificado contra Postgres: 32 312 alumnos contra 32 374 del ciclo anterior = **−0.19 %**; los dos tableros dicen **−54.5 %**, factor 287 | **critical** | **fixed** | US-203 / US-204 / US-211a / US-212 / US-221 / REQ-002 / AC-002.4 | **C1 (Diana Alvarez) fixed** — `matricula_ciclo_anterior` expuesta en `fact_escuela_ciclo.sql`, `cubo_escuela_360.sql`, `cubo_comparador_municipio.sql` y, ampliando el alcance tras encontrar el mismo defecto en el repo, también `cubo_matricula.sql` (DB-01/DB-06) y `cubo_riesgo_territorial.sql` (DB-02) — rama `fix/diana-varela-bug031-matricula-anterior`, verificado contra Postgres real (`dbt run --full-refresh` + `dbt test`, `cubo_matricula_fact_parity` y `not_null_fact_escuela_ciclo_matricula_ciclo_anterior` en verde). Pendiente **C2 · Manuel Serranía**: migrar `metrics_db01_db02.yaml`, `metrics_db03_db04.yaml`, `metrics_db06_db09.yaml` a razón de sumas y retirar `variacion_x_matricula` + las dos aserciones que la exigen (`test_semantic_db01_db02.py`, `test_semantic_db06_db09.py`) — el origen es §4.4 de [[vault/04_UX_Design/Cube_Specs_DB03_DB04]]: Marina especificó el componente aditivo y Deni Garrido lo implementó fielmente; la implementación es correcta, la especificación no · **2026-09-03 · C2 ✅ — verificado por Marina García.** El trabajo lo hizo **Luis Téllez** el 31-ago (`f013b20`, `b74a700`), no Manuel: los tres `metrics_*.yaml` están migrados a razón de sumas y `variacion_x_matricula` no aparece fuera de comentarios en ninguno; las dos aserciones quedaron **invertidas** —ahora exigen `suma_matricula_anterior` y rechazan que `variacion_x_matricula` reaparezca—. **Comprobado contra Postgres, no solo leyendo el código**: KPI-02 da **−0.192 %** desde los cuatro cubos que lo alimentan (`cubo_matricula` DB-01/DB-06, `cubo_riesgo_territorial` DB-02, `cubo_escuela_360` DB-03, `cubo_comparador_municipio` DB-04) **y** desde el hecho `gold.fact_escuela_ciclo`, sobre los mismos 32 312 / 32 374 del reporte original. Los seis tableros afectados quedan coherentes entre sí y con la fuente | `tests/test_semantic_db03_db04.py::test_una_metrica_de_porcentaje_no_multiplica_dos_medidas` |
| BUG-032 | `Data_Model.md` se contradice a sí mismo sobre dónde vive `indice_riesgo`: la línea 181 (§4.5) describe correctamente `valor` (variación cruda) e `indice_riesgo` como **columnas distintas** —que es lo implementado y lo que consume la API—, pero la nota de la línea 313 afirma que `indice_riesgo` vive *"en la columna `valor`"*. Quien lea §5.3 consultaría `valor` esperando un `[0,1]` y recibiría la variación cruda, hoy en alumnos absolutos: números como `-20` donde espera `0.6` | medium | fixed | US-313 / US-411 / REQ-003 | docs/diana-varela-bug032-indice-riesgo | manual — Diana Alvarez (C1), ver detalle |
| BUG-033 | El workflow **"Update Project Graph"** falla en **cada** merge a `main`: su paso final regenera `graphify-out/` y hace `git commit` + `git push` **directo a `main`**, que la branch protection rechaza (`GH013` — exige PR + revisión de code owner, DEC-003). Ningún commit del bot entró nunca; el grafo versionado solo se actualiza a mano. No bloquea merges (no es required check) pero deja **rojo cada run** y el grafo desactualizado desde el 25-ago | low | fixed | REQ-007 | `fix/luis-tellez-bug033-update-graph-artifact` (Luis Téllez, **C5**) — el workflow deja de commitear a main y **publica el grafo como artefacto de Actions**; `permissions` baja a `contents: read` | `workflow_dispatch` sobre la rama: el run genera el artefacto sin intentar push (ver detalle) |
| BUG-034 | **DS-02: coordenadas `0,0` en el catálogo real de CCT pasaban como georreferencia válida.** Verificado contra la descarga real de SIGED (30-ago, ver `DS-02_Catalogo_CCT.md` §9): 6 filas de 77,712 escuelas de básica en las 4 `SCOPE_ENTIDADES` traían `INMUEBLE_LATITUD`/`INMUEBLE_LONGITUD` en `0.0`. `silver/escuela.sql` solo nulificaba cadenas vacías (`nullif(trim(cast(latitud as text)), '')`), nunca ceros literales — así que esas 6 escuelas se veían con georreferencia "presente" y podían entrar a la interpolación IDW de D5/D6 (ADR-006) como si `(0,0)` fuera un punto real, sesgando el resultado de las escuelas vecinas | medium | **fixed** | DS-02 / ADR-006 / US-105 / REQ-001 | `feat/diana-varela-ds02-cct-real` (Diana Alvarez, **C1**) — `nullif()` anidado sobre el valor numérico además de la cadena vacía | `dbt/tests/valid_escuela_georreferencia.sql` |
| BUG-036 | **`cargar_fixture()` reportaba mal el número de filas insertadas en cargas grandes.** `execute_values()` pagina el INSERT en lotes de 100 filas por default; `cur.rowcount` justo después de la llamada solo refleja el ÚLTIMO lote, no el total acumulado. Verificado real: la carga de DS-02 (385,175 filas nuevas) reportó "75 insertadas" — exactamente `385175 % 100` — confirmado falso con un `COUNT(*)` directo en Postgres. Afecta a todos los cargadores reales que usan `cargar_fixture()` con más de 100 filas (DS-01, DS-04, DS-05, DS-08...); el número impreso en sesiones anteriores probablemente subestimó el conteo real, aunque los datos en sí sí quedaron completos (`ON CONFLICT DO NOTHING` seguía operando bien, solo el conteo impreso era falso) | medium | **fixed** | src/ingesta/cargar_bronze_fixture.py | `feat/diana-varela-ds02-cct-real` (Diana Alvarez, **C1**) — `RETURNING` + `execute_values(..., fetch=True)`, que sí agrega los resultados de todas las páginas | `tests/test_cargar_bronze_fixture_conteo.py` |
| BUG-037 | `sync_semantic_layer.py` actualiza el SQL de un dataset (`PUT /api/v1/dataset/<id>`) pero nunca vuelve a pedirle a Superset que re-lea sus columnas: la lista de columnas queda fija desde la creación del dataset. Cualquier columna agregada, renombrada o quitada en un `.sql` de `superset/semantic/` después de esa primera creación se sincroniza en el texto del SQL pero no en el esquema del dataset — cualquier chart que la referencie falla con `Columns missing in dataset: [...]`, y el error solo aparece al abrir el dashboard en el navegador, nunca en la corrida del script ni en la API de creación de charts (que no valida contra el schema real) | medium | open | US-214b / REQ-002 | pendiente — mitigación manual usada hoy: `PUT /api/v1/dataset/<id>/refresh` (Superset ya expone este endpoint) llamado a mano tras el sync; fix de fondo propuesto: que `ensure_datasets()`/`_apply_metrics_and_columns()` llame ese mismo endpoint automáticamente cada vez que el SQL de un dataset cambia | Reportado por Monserrat Miranda (2026-08-30), validando US-214b en vivo: `db05_cubo_driver` ganó la columna `link_db08`, se sincronizó el SQL, y el chart "D1 · Municipios · driver dominante y cobertura" reventó con 4 columnas de esa fila (3 preexistentes + la nueva) marcadas "missing" hasta refrescar a mano. Sin test de regresión automatizado todavía |
| BUG-038 | `_layout_tabs()` en `sync_semantic_layer.py` arma `ROOT_ID` con `type: "TABS"` y cuelga los 6 nodos `TAB-D1..D6` directamente como sus hijos. Superset renderiza el contenido del primer tab (D1) correctamente, pero **no dibuja ninguna barra de navegación entre tabs** — D2 a D6 quedan inalcanzables desde la interfaz, aunque sus datos y charts existen y funcionan bien vía API. El test `test_layout_tabs_arma_root_de_tipo_tabs` codifica esta estructura como si fuera la esperada (`assert position["ROOT_ID"]["type"] == "TABS"`), por eso pasaba en verde sin que nadie lo notara — nunca se había confirmado visualmente en un navegador real hasta hoy. **Segundo síntoma, misma causa probable**: los filtros globales de DB-05 (Ciclo/Entidad/Nivel) se pueden editar en el panel (quitar un valor, "Clear all") pero el cambio nunca le llega a los charts — ni al quitar un valor y darle "Apply filters", ni con "Clear all". Probado directo contra `/api/v1/chart/data` (sin pasar por el navegador): el mismo filtro por `cve_ent` sí funciona perfecto ahí (filtrar a `'09'` trae solo Ciudad de México, filtrar a `'19'` trae solo Nuevo León) — el SQL/dataset está bien, el defecto es que el *scope* del filtro nativo (`rootPath: ["ROOT_ID"]`) probablemente no puede resolver qué charts están "dentro" del árbol cuando ese árbol está mal armado para tabs, el mismo defecto de fondo que el síntoma anterior | high | open | US-213 / US-214b / REQ-002 | pendiente — **dos hipótesis probadas en vivo contra este Superset (nunca en el repo), ninguna resuelve ambas cosas a la vez**: (1) insertar un nodo `TABS-1` intermedio entre `ROOT_ID` (cambiado a `type: "ROOT"`) y los 6 `TAB-*` sí hace aparecer la barra de tabs, pero el contenido de todos los tabs queda en blanco (causa no identificada aún); (2) revertir a la estructura original recupera el contenido pero vuelve a perder la barra de tabs. Falta una tercera hipótesis — candidato: revisar si Superset necesita metadata adicional en el nodo `TABS` (tamaño, fondo) o si el problema está en otro lado (`json_metadata`, `filter_scopes`); dado el segundo síntoma, revisar también si arreglar el árbol resuelve el scope de filtros de un solo golpe | Reportado por Monserrat Miranda (2026-08-30), validando US-214b/US-215b en vivo. Sin test de regresión — el test existente (`test_layout_tabs_arma_root_de_tipo_tabs`) codifica la estructura incompleta como correcta y habría que revisarlo también |
| BUG-039 | **El padrón de propiedad no permitía lo que la plantilla de PR exige: los 21 quedaron sin poder abrir un PR que pasara sus propios gates.** La plantilla marca como obligatorias las casillas «Listado en el `_index.md` de su carpeta» y «Fila actualizada en la matriz de trazabilidad», pero `vault/_DevLog/_index.md` y `vault/02_Requirements/Traceability_Matrix.md` eran alcance exclusivo del PM en `ownership.yml`: quien cumplía la plantilla reprobaba el gate de propiedad, y quien pasaba el gate incumplía la plantilla. `.gitignore` y `.gitattributes` no estaban en el alcance de **nadie** —ni siquiera del PM—, así que el ignore y los drivers de merge quedaban sin mantenimiento posible. 8 personas de C1/C4 tenían un `.md` de `03_Architecture` en verde sin poder tocar su `_index.md`, lo que impide cumplir la regla 4 al crear un documento ahí. Y —el alcance real del defecto, visible al correr el gate contra la propia corrección— **los seis registros de intake que `Definition_of_Filed` obliga a usar a cualquiera** (Bug_Register, Security_Audit_Log, Risk/Blocker/Decision/Incident) estaban cerrados a 0 o 1 persona: la regla que manda reportar un bug o un riesgo era imposible de cumplir para 20 de 21. Verificado con el propio gate: 20 de 21 personas con 4 rutas obligatorias fuera de alcance, el PM con 2, y `Bug_Register.md` sin dueño alguno | high | closed | US-001 / REQ-007 | 11 rutas pasan a `comunes` —índice de DevLog, matriz, infra raíz y los 6 registros de intake—, `03_Architecture/_index.md` al amarillo de C1/C4 y `tests/**` al del PM (mantiene `vault/_Meta/scripts/**`); la matriz y `10_Risk_Governance/**` quedan en `criticos`, de modo que el gate sigue avisando a quién pedirle revisión sin reprobar | `TEST-014` ampliado a 40 casos en `tests/test_check_ownership.py`: recorren a los 21 contra cada ruta que la plantilla exige y contra cada registro de intake de `Definition_of_Filed` |
| BUG-040 | **El parser del tablero PM partía las filas por los pipes escapados y publicó datos corruptos en silencio.** `table_cells()` hacía `.split("\|")` sobre la línea cruda, así que el `\|` de un wikilink con alias —`[[ruta\|texto]]`, la sintaxis que el vault usa 190+ veces y siempre escapada— partía la celda en dos y desplazaba todas las columnas siguientes. En la fila `US-004` de `Execution_Status.md` eso dejaba `evidence` truncada con un `[[` sin cerrar y metía **texto en el campo `updated`** donde va una fecha. No reventaba nada: la fila conservaba más de 6 celdas y el estado seguía siendo válido, y `validate_pm_dashboard.py` no revisaba `updated`. Estuvo publicado en `main` dentro de `pm-dashboard.json`. **El mismo defecto corrompía las métricas por persona:** 4 filas del índice de DevLog llevaban el pipe sin escapar y atribuían el DevLog a su propia descripción — el tablero contaba **25 autores** en vez de 21. Y al normalizarlas aparecieron 3 variantes de nombre (`Serrania` sin ñ, `Gonzalez` sin acento, `Carlos Mayorga` en corto) que, al cruzarse por coincidencia exacta contra el nombre canónico, dejaban a Manuel con **0 DevLogs teniendo 12**, a Eloísa con 0 de 3 y a Carlos con 0 de 1. Escapar el pipe **no** bastaba: el parser tampoco interpretaba el escape. El propio archivo ya tenía la solución diez líneas más abajo, en `parse_devlog_authors`, que sí protegía `\|` antes de partir — nunca llegó a la función compartida, que usan 6 parsers (`stories`, `execution`, `people`, `github_directory`, `markdown_rows`, `raci`) | high | closed | US-004 / REQ-007 | `table_cells()` protege el pipe escapado antes de partir y lo restituye en la celda (`clean()` ya sabía resolver `[[x\|y]]`, solo se le destruía el enlace antes); `parse_devlog_authors` deja su copia y usa la función canónica (regla 1 del vault); la fila `US-004` escapa su pipe y suelta la fecha sobrante; `validate_pm_dashboard.py` valida que `updated` sea una fecha; las 4 filas del índice de DevLog escapan su pipe y las 3 variantes de nombre se normalizan al padrón | `TEST-015` (`tests/test_generate_pm_dashboard.py`, 8 casos): el contrato del parser con pipes escapados y, sobre la fuente real, que ninguna historia tenga `updated` fuera de formato ni evidencia con wikilink sin cerrar, que toda fila del índice de DevLog tenga 5 columnas y que **todo autor del índice exista en el padrón** (una variante de nombre ya no deja a nadie en cero en silencio). Verificado además que el validador reprueba con la fila rota inyectada |
| BUG-042 | **24 de 91 historias no tenían fila en `Execution_Status.md`, y el generador las contaba como `planned` en silencio.** `build_snapshot()` hacía `state = execution.get(story["id"], {})` y luego `state.get("status", "planned")` — una US ausente del registro no era un error, era indistinguible de "de verdad no ha arrancado". Pasó con **10 de las 24** ya con PR mergeado, algunas terminadas (US-205, US-214b, US-523b), otras con datos reales entregados y solo pendientes de bloqueo ajeno (US-222, US-321). Una de las filas existentes además tenía la evidencia mal etiquetada: `US-206` cargaba el trabajo real de `US-205` (repunteo de capa semántica, PR #134), hallazgo de Manuel Serranía. Detectado auditando el tablero contra los PRs mergeados en `main`, 2026-09-03 | high | fixed | US-004 / REQ-007 | Se agregan las 24 filas faltantes con su estado real verificado contra PR/commit (no un default) y se corrige la etiqueta `US-206`→`US-205`; `build_snapshot()` ya no completa con `.get(..., "planned")` — si una US no tiene fila, el generador falla y lista cuáles faltan | `TEST-034` (`tests/test_generate_pm_dashboard.py`, 2 casos): confirma que las 91 historias reales tienen fila, y que inyectar una historia sin registro hace que `build_snapshot()` truene mencionando `BUG-042` y su ID — no que caiga a `planned` |
| BUG-044 | **Sin `ciclo` explícito, `/escuelas`, `/escuelas/{cct}` y `/kpis` sumaban/listaban TODOS los ciclos materializados a la vez, no solo el actual.** `listar_escuelas`/`obtener_kpis`/`obtener_escuela` (`src/api/repositorio_gold.py`) solo filtraban por `fact.c.id_ciclo` cuando el caller mandaba `ciclo`; al omitirlo (el caso más común), la consulta quedaba sin acotar sobre `gold.fact_escuela_ciclo`, que materializa ~3 ciclos. Verificado en producción: `/escuelas?cve_ent=09` sin `ciclo` → 19 456 filas; con `ciclo=2024-2025` → 6 378 (razón ≈3, una fila por ciclo por escuela, sin campo `id_ciclo` en `EscuelaOut` para distinguirlas); `/kpis` sin `ciclo` → `matricula_total=20 638 574` (nacional aparente) cuando el real de las 4 entidades es ~7M — la matrícula estaba **triplicada**, no fuera de alcance. `obtener_escuela` (detalle) tenía el mismo hueco: sin filtro, `.first()` devolvía una fila cualquiera entre los ciclos de una escuela, no determinista. Detectado por Karla Monter validando el cierre de US-411 (BUG-020 ya curado) el 2026-09-03 | **critical** | **fixed** | US-411 / REQ-004 | `dev/karla-monter` (Karla Monter, C4) — los tres métodos de `RepositorioGoldPostgres` ahora usan `_ciclo_mas_reciente()` (`MAX(id_ciclo)`) como default cuando `ciclo` es `None`; `tests/fixtures_gold.py::RepositorioGoldFake` refleja el mismo default para que la suite rápida lo ejerza sin Postgres | `tests/test_api_contract.py::test_escuelas_sin_ciclo_no_duplica_entre_ciclos` · `::test_escuelas_ciclo_explicito_trae_el_ciclo_pedido` · `::test_kpis_sin_ciclo_no_suma_ciclos_anteriores` — las tres usan el fixture con la misma escuela en dos ciclos (`09DPR0001A`, 2024-2025 y 2023-2024) para que la deduplicación se ejerza de verdad, no por casualidad de datos |
| BUG-041 | **El path real `--desde-gold` de ML truena cuando un driver queda 100 % `SIN_DATO`: `pd.read_sql_table` devuelve los nombres de columna como `quoted_name` (subclase de `str`), sklearn exige `type(x) == str` exacto para poblar `feature_names_in_`, así que **nunca lo puebla**; el fallback `getattr(modelo, "feature_names_in_", DRIVERS)` de `construir_predicciones` cae a los 6 `DRIVERS` y reintroduce el driver descartado → `ValueError: X has 6 features, but HistGradientBoostingRegressor is expecting 5 features`. Misma FAMILIA que BUG-015/018/023 pero **causa raíz nueva**: aquí el propio patrón `feature_names_in_` que arregló a los tres nunca se activa al leer de la BD, así que el fix de BUG-015 queda anulado en el path de producción. Los tests no lo cazan porque usan fixtures CSV (`read_csv` → `str` puro). Reportado por Luis Téllez (C5) al cerrar la validación L0 local el 2026-09-02, ejercitando cobertura parcial real (D5 agua 100 % `SIN_DATO`) | high | **fixed** | US-311 / US-313 / REQ-003 | **C3 ✅ aplicado por Héctor Morales (2026-09-03)** en `cargar_features_desde_gold` (`entrenar_ml01.py`), tal cual lo preparó Luis Téllez: `df.columns = [str(c) for c in df.columns]` tras el `read_sql_table`. Diagnóstico **verificado de forma independiente** antes de aplicarlo: `pd.read_sql_table` devuelve `quoted_name` (Postgres **y** SQLite) y sklearn 1.9.0 no puebla `feature_names_in_` con él, sí con `str` puro. Fallo reproducido end-to-end contra el Gold local (3 ciclos, D5 100 % `SIN_DATO`) con el mismo `ValueError` y el mismo MAE 0.0844 que reportó C5; con el parche, `--desde-gold` publica **55 predicciones + 55 recomendaciones** (F1 0.6458), las mismas cifras | `tests/test_entrenar_ml01.py::test_las_columnas_leidas_de_gold_son_str_puro` · `::test_entrenar_desde_gold_puebla_feature_names_in` · `::test_predecir_desde_gold_no_cae_al_fallback_de_los_6_drivers` — las tres **reprueban con el parche revertido** (comprobado) y usan SQLite, que también entrega `quoted_name`, así que corren en CI sin Postgres |
| BUG-045 | **CONEVAL (DS-07) no es reproducible desde el repositorio: el fixture y el modelo hablan esquemas distintos, y no existe ninguno compatible.** `dbt/models/silver/rezago_municipio.sql` consume el esquema del **extracto oficial**, con columnas hasheadas — exige `c_b9548dbd414b`, `c_deef5d1bd71a`, `c_9b370f449788`, `c_9e8609cad84d`, `c_5d0523b1d4a3`, `c_91fd46c9babe`, `c_9bd1a7aa7fca`, `c_764f3baf1395`, `c_1a3c72ae6dd1` y `_periodo_medicion`. El único fixture de CONEVAL del repo (`tests/fixtures/bronze_coneval_sample.csv`, generado por `tests/fixtures/generate_bronze_drivers_fixtures.py::generar_coneval`) emite `cve_mun, entidad, municipio, indice_rezago_social, grado_rezago, pobreza_pct` — el contrato **viejo**, anterior a la migración de Deni, y su propio docstring lo cita (`Data_Model.md §6`). **Ningún CSV del repo tiene columnas `c_…`.** Sin los dos Excel reales de CONEVAL no se construye `silver.rezago_municipio` → sin él no hay `gold.dim_municipio` → sin él **no se materializa ningún cubo** → **sin cubos no funciona ningún tablero**. Reproducido corriéndolo: `dbt run` reprueba con `column "c_b9548dbd414b" does not exist`. **CI no lo atrapa**: el job `dbt-contract` solo hace `dbt parse`, que renderiza el manifest sin ejecutar Silver contra datos | **high** | fixed | US-112 / US-113 / REQ-001 / REQ-002 / DS-07 | resuelto 2026-09-04 (**C1 — Diana Alvarez**): se extendió `ESQUEMAS` en `src/ingesta/cargar_bronze_fixture.py` con las entradas `coneval_irs`/`coneval_pobreza` (columnas `c_…` hasheadas, verificadas contra los manifiestos reales de la carga DS-07 del 2026-09-04) y se regeneraron los fixtures vía `generate_bronze_drivers_fixtures.py::generar_coneval`: `bronze_coneval_irs_sample.csv` + `bronze_coneval_pobreza_sample.csv`. Se retiró el fixture huérfano `bronze_coneval_sample.csv` y el esquema `coneval` obsoleto (`--esquema coneval` ahora lanza `ValueError`). Ver §Arreglo aplicado en el detalle | ✅ verificado real contra Postgres por Diana (`dbt run`+`dbt test` sobre `rezago_municipio`, `pytest` 884 passed) — sigue pendiente solo la guarda de CI propuesta, no implementada en este fix (ver §Guarda propuesta) |
| BUG-046 | **El verifier OAuth rechaza TODO `id_token` real de Google porque `jwt.decode` no desactiva la verificación de `at_hash`.** El `id_token` del *authorization code flow* siempre trae el claim `at_hash`; `_verificar_id_token` (`src/api/security/google.py`) llama a `jwt.decode` **sin `access_token` y sin `options`**, y jose —con `verify_at_hash=True` por defecto— lanza `JWTClaimsError("No access_token provided to compare against at_hash claim")`. `verify()` lo traduce a `ValueError` → **401 uniforme en TODO login real, analista y ciudadano**. La lectura pública y la URL pública NO se ven afectadas (dependen de `AUTH_LECTURA_PUBLICA`), pero el login interactivo e2e (US-402) y la demostración de RBAC 200/403 con cuentas reales (US-403) quedan **100% bloqueados**. Reproducido en prod (rev `faro-api-00010`) al intentar el primer login real: respuesta `{"error":"unauthorized",...}` con `JWTClaimsError` (`name=faro.api.google`) en los logs de Cloud Run. Los tests nunca lo cazaron porque el fixture emitía `id_token` **sin** `at_hash`, el único claim que Google siempre añade en producción. Reportado por Luis Téllez (C5) el 2026-09-04 | **critical** | fixed | US-402 / US-403 / REQ-004 | **parche + test de regresión preparados y validados en local por Luis Téllez (C5), rama `dev/luis-tellez`** — 1 línea (`options={"verify_at_hash": False}`) en `_verificar_id_token`. **Mergeado por Edgar Coronel (PO)** como excepción de propiedad: toca `src/api/security/**` (**alcance C4, Christian Ruiz**) y es **cambio de seguridad (regla 7)** → `check_ownership.py` reprueba, correctamente, un PR desde una rama C5. **Revisión de regla 7 de C4 firmada el 2026-09-04 — 🟢 aprobado sin cambios** (verificado por reversión del parche: reprueba con el mismo `JWTClaimsError` de prod; 66 passed en la familia de auth con el parche puesto). Ver [[vault/07_Security/Security_Review_US402_US403_US404]] Anexo A y `SEC-009`. **✅ `fixed` 2026-09-04:** redespliegue C5 → revisión `faro-api-00011-hr5` (rebuild `linux/amd64` desde `origin/main` `33fcbbb` + `gcloud run services update --image`, patrón BUG-044/DEC-012: preserva env/secrets/SA/VPC → `ANALISTA_EMAILS` efímero intacto). `/version`=`33fcbbb`. **Login e2e real validado por Luis Téllez (C5):** analista→**200**, ciudadano (2º correo fuera de `ANALISTA_EMAILS`)→**403**, sin token→**401** (AC-004.5). Ver [[vault/_DevLog/2026-09-04-luis-tellez-redeploy-bug046-e2e]] | `tests/test_oauth_google.py::test_verifier_acepta_id_token_con_at_hash` (emite un `id_token` con `at_hash`; **reprueba con el parche revertido**, comprobado — mismo `JWTClaimsError` del log de prod) |
| BUG-047 | **Espejo en dashboards de BUG-044: los filtros globales de ciclo existen pero sin `valor_por_defecto`, así que al abrir cada tablero sin haber filtrado, toda métrica agregada suma los ~3 ciclos materializados del cubo a la vez.** A diferencia del fix de BUG-044 (que vive en la API `/api/v1/kpis`), los tableros no pasan por la API — leen la base directo, así que el fix de BUG-044 no los cubre. Afecta a los 7 dashboards que declaran `id_ciclo` y no fijaban ciclo al abrir: DB-01 ejecutivo, DB-02 mapa de riesgo, DB-05 analisis driver, DB-06 predicciones, DB-07 calidad cobertura, DB-08 explorador cubo, DB-09 recomendaciones (DB-03/DB-04 ya los cubrió Marina García dentro de US-214a; DB-10 monitoreo de pipeline no declara `id_ciclo` y no aplica). Mismo defecto que detonó el aviso de Luis Téllez el 2026-09-04: producción `/api/v1/kpis` pintaba 20.6M contra 6.7M reales | **high** | **fixed** | US-203 / US-204 / US-205 / US-213 / US-222 / REQ-002 | `dev/manuel-serrania` (Manuel Serranía, C2) — clave opcional `valor_por_defecto: "2024-2025"` en el YAML de cada dashboard, traducida al `defaultDataMask` de Superset por `sync_semantic_layer.py`, **aditiva y opt-in** (los tableros sin la clave no cambian); selectbox de ciclo en `1_Dashboards.py` fija `index=len(CICLOS)-1` (2024-2025) por defecto; `cct` agregado al final de `filtros_globales` (índice 3) en DB-06/DB-09 para destrabar el drill-down de Marina. **Actualización 2026-09-04 (Oscar Quiroz, C2):** agrega `default: ultimo_ciclo`, resolución dinámica que sustituye la necesidad de actualizar `valor_por_defecto` a mano cada ciclo; ver §Actualización al final de esta entrada | `tests/test_frontend_dashboards_streamlit.py` (2 passed — el archivo tiene 2 tests; de los 3 archivos de frontend que el CI se saltaba en silencio y ya corren) + guarda de compatibilidad hacia atrás exigiendo que sin la clave no se escriba `defaultDataMask` + `tests/test_filtros_nativos_default_dinamico.py` (5 casos, resolución dinámica) |
| BUG-048 | **Producción sirve un Gold empobrecido: `indice_completitud_drivers` 0.197 y `escuelas_en_riesgo` 0, contra 0.648 y 2 escuelas con el mismo código y el pipeline completo.** El snapshot de Gold que se importó a Cloud SQL en L1 (`gold_real.sql`, 2026-09-03) se generó **antes** del fix de BUG-045, cuando CONEVAL no tenía fixture compatible y D1 iba vacío. El código desplegado es correcto —`/version` = `33fcbbb`, con los fixes de BUG-044 y BUG-046— y la matrícula es la del ciclo vigente (6,704,229 ✅); **lo que está viejo son los datos**, no la imagen. Medido el 2026-09-04 contra `https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/kpis` y contra un ambiente local reconstruido de cero con el runbook (`vault/00_Start_Here/Runbook_Ambiente_Local`): local da D1 145/145, D2 145/145, D3 y D4 133/145, D6 5/145, D5 0/145 (CONAGUA no ingerida, correcto). **Impacto en la demo del 9-sep**: quien abra la URL pública ve `escuelas_en_riesgo = 0` y 20 % de completitud — los dos números que peor cuentan la historia del proyecto, y ninguno refleja el estado real del pipeline. No es regresión de código ni de despliegue: es que Gold en Cloud SQL nunca se refrescó tras BUG-045 | **high** | open | US-113 / US-505 / REQ-001 / REQ-005 / DS-07 | pendiente (**C1 — Diana Alvarez** materializa, **C5 — Luis Téllez** sube). Camino ya probado: es el mismo procedimiento de L1 (`pg_dump` de las tablas Gold → bucket privado → `gcloud sql import sql`), ahora con el Gold regenerado post-BUG-045 y, si alcanza, con los 9 cubos que L1 excluyó a propósito ("0 matviews") | ⬜ sin guarda automatizada: nada compara hoy la completitud de prod contra la del pipeline, así que una degradación de datos pasa invisible mientras el código siga verde. Guarda propuesta, no implementada: que el smoke de despliegue falle si `indice_completitud_drivers` cae por debajo de un umbral acordado |
| BUG-049 | **Las tarjetas y tablas de DB-03/DB-04 quedan alineadas al fondo de su celda, con hueco vertical arriba, y las tablas anchas exigen scroll horizontal para ver las últimas columnas.** Encontrado en la sesión de usabilidad de US-215a (Marina García, 2026-09-04, Chrome): los `big_number_total` dejan un espacio vacío notable bajo la cifra, y en `Perfil del plantel`, `KPI-16` y `KPI-18` las columnas de la derecha —incluidas las de link, que son el drill-down de US-214a— quedan fuera de vista hasta desplazar. **No afecta los datos ni la navegación**, ambos verificados correctos; es presentación, y el tablero es material de la demo del 9-sep | low | open | US-215a / US-212 / REQ-002 | pendiente (**C2 · Marina García**) — los valores `alto`/`ancho` de cada chart viven en `superset/dashboards/db03_ficha_escuela.yaml` y `db04_comparador_municipio.yaml`. Requiere ajustar contra el navegador, no a ciegas: la altura correcta depende de cuántas filas devuelve cada tabla | ⬜ no automatizable con lo que hay: es juicio visual, y no existe CI de accesibilidad ni de layout (ver BUG-049) |
| BUG-050 | **Lighthouse reporta score de accesibilidad 93 en DB-03, con dos hallazgos: contraste insuficiente entre texto y fondo, y `<html>` sin atributo `[lang]`.** Medido por Marina García el 2026-09-04 en Chrome, idéntico en modo claro y oscuro. El del `lang` **no es de estos tableros**: lo emite el shell de Superset, así que corregirlo sería configuración de la imagen (C5) o un upstream, no un cambio de tablero. El de contraste sí puede tocar a los tableros, pero **no hay paleta declarada contra la cual verificar**: `vault/04_UX_Design/UX_Guidelines.md` está en `status: draft` con las tablas de tokens vacías pese a llevar `source_of_truth: true` | low | open | US-215a / REQ-002 | pendiente — **dos dueños distintos**: el `[lang]` es del shell de Superset (**C5**, `docker/superset.Dockerfile` / `superset_config.py`); el contraste requiere primero que alguien llene la paleta de `UX_Guidelines.md` (**C2 · Manuel Serranía**, dueño del sistema de diseño). Sin paleta no hay criterio de aceptación | ⬜ **el proyecto declara un gate que no existe**: `vault/04_UX_Design/Accessibility.md` dice *"verificados en CI (Lighthouse a11y)"* y *"Lighthouse Accessibility ≥ 0.9 (bloqueante)"*, pero no hay ninguna referencia a Lighthouse en `.github/` ni en `vault/08_CICD_DevOps/`. El 93 se midió a mano |

## BUG-046 — El verifier OAuth rechaza todo `id_token` real por no desactivar la verificación de `at_hash`

Reportado por **Luis Téllez (C5)** el 2026-09-04, al validar el **primer login real end-to-end** en
producción (revisión `faro-api-00010`, con `ANALISTA_EMAILS` y la consola de Google ya configuradas).
No es un fallo de la cuenta ni de la consola: es un defecto de código que rompe **todos** los logins
reales por igual.

### Síntoma

Tras autenticarse con una cuenta real de Google, el callback responde **401**:

```json
{"error":"unauthorized","message":"No hay credenciales válidas para esta operación.","request_id":"req_…"}
```

En los logs de Cloud Run, el origen exacto:

```
id_token de Google invalido: JWTClaimsError   (logger name=faro.api.google)
```

`/auth/login` (302), `/health` (200) y la lectura pública siguen funcionando; lo que revienta es el
último paso del callback: la verificación del `id_token`.

### Causa raíz

`_verificar_id_token` (`src/api/security/google.py`) llama a `jwt.decode(...)` **sin `access_token` y
sin `options`**. El `id_token` que Google emite en el *authorization code flow* **siempre** incluye el
claim `at_hash`. python-jose trae `verify_at_hash=True` por defecto, y `_validate_at_hash` lanza

```
JWTClaimsError: No access_token provided to compare against at_hash claim.
```

cuando `at_hash` está presente pero no se pasa `access_token`. `_verificar_id_token` captura cualquier
`JWTError` (del que `JWTClaimsError` es subclase) y lo convierte en `ValueError("id_token invalido")`,
que la capa HTTP traduce al **401 uniforme**. Resultado: **ningún login real completa** —analista o
ciudadano, da igual el correo—, porque el rechazo ocurre antes de resolver el rol.

### Por qué los tests no lo cazaban

El fixture `google_falso` de `tests/test_oauth_google.py` fabrica `id_token` firmados de verdad, pero
**sin `at_hash`**. Sin ese claim, jose no ejecuta `_validate_at_hash` y la verificación pasa. `at_hash`
es justamente **el único claim que Google añade en producción y las pruebas nunca emitían**. Misma
lección que BUG-023 y BUG-041: un fixture construido para validar la forma no valida la realidad.

### Fix (1 línea, validado en local)

En la llamada `jwt.decode` de `_verificar_id_token`, desactivar la verificación de `at_hash`:

```python
options={"verify_at_hash": False},
```

**Por qué es seguro:** en el *authorization code flow* server-side el `id_token` llega por un canal
TLS directo servidor↔Google, y su integridad ya la garantizan **firma RS256 + `aud` + `iss` + `exp`**,
todas verificadas aquí. `at_hash` es una defensa pensada para el *implicit flow* —donde el token viaja
por el navegador y conviene atarlo al `access_token`—; en este flujo el `access_token` ni se usa
(`_intercambiar_code` solo devuelve el `id_token`). El resto de comprobaciones quedan intactas.

*Alternativa más purista (descartada):* capturar el `access_token` en `_intercambiar_code` y pasarlo a
`jwt.decode(access_token=...)`. Más código y estado que mantener, sin ganancia real de seguridad aquí,
porque el `access_token` se descarta acto seguido.

### Verificación (local, 2026-09-04, venv 3.11)

- Con el fix: `pytest tests/test_oauth_google.py tests/test_auth_jwt.py tests/test_frontend_auth.py
  tests/test_puente_oauth_frontend.py` → **54 passed, 1 skipped**.
- Test de regresión nuevo (`test_verifier_acepta_id_token_con_at_hash`): **reprueba con el parche
  revertido** (`ValueError: id_token invalido`, log `JWTClaimsError` — idéntico al de prod) y **pasa con
  el fix**.

### Propiedad / gobernanza

`src/api/security/**` está **verde de Célula 4** (Christian Ruiz —TL— y su célula). Por la regla 9,
`check_ownership.py` reprueba un PR de cualquier rama fuera de C4 que toque `src/api/**`. Además es un
**cambio de seguridad → regla 7** (revisión humana explícita). El reporte y el parche se dan de alta
aquí —`Bug_Register.md` es `comunes` y `Definition_of_Filed` obliga a registrar el bug a quien lo
encuentre—, patrón de BUG-041 y BUG-008.

**En modo reparación**, y por la proximidad del CODE FREEZE (2026-09-06), **Luis Téllez (C5, TL de
Cloud & DevOps) autorizó preparar el parche + test en su rama `dev/luis-tellez`**; el **merge lo decide
Edgar Coronel (PO)** pese al gate de ownership, con la revisión de C4 recomendada. El gate reprobará el
check de propiedad: es esperado y queda advertido en el PR.

## BUG-041 — El `quoted_name` de SQLAlchemy vacía `feature_names_in_` y reintroduce el driver descartado

Reportado por **Luis Téllez (C5)** el 2026-09-02, al cerrar la **validación L0 local** (pipeline ML
completo contra el Gold local, ~$0, sin GCP). No lo reportó C3: se destapó al ejercitar
`publicar_gold.py --desde-gold` con **cobertura parcial real** —justo el escenario `SIN_DATO` que FARO
promete manejar—, no con el fixture sintético.

### Síntoma

```
ValueError: X has 6 features, but HistGradientBoostingRegressor is expecting 5 features
```

ML-01 **entrena bien** (con datos de muestra, MAE 0.0844) y truena **en la predicción**, después de
haber excluido correctamente el driver sin datos.

### Causa raíz

`cargar_features_desde_gold` (`entrenar_ml01.py:203`) lee con `pd.read_sql_table(...)`, y **SQLAlchemy
devuelve los nombres de columna como `quoted_name`** —una subclase de `str`, no `str` puro—.
scikit-learn detecta los nombres de features exigiendo **`type(x) == str` exacto**, así que trata cada
`quoted_name` como "no-string" y **nunca puebla `modelo.feature_names_in_`**. En la predicción,
`construir_predicciones` hace `getattr(modelo, "feature_names_in_", DRIVERS)` (`publicar_gold.py:267`) →
cae al fallback `DRIVERS` (los 6) → reintroduce el driver que se descartó por estar 100 % `SIN_DATO` →
desajuste de forma → crash.

### Por qué es un bug NUEVO y no un duplicado de BUG-015/018/023

Aquellos tres arreglaron el lado de entrenamiento/predicción para **confiar en `feature_names_in_`**
(el patrón `getattr(modelo, "feature_names_in_", DRIVERS)`). **Este defecto es que ese atributo nunca
se puebla en el path de la BD**, así que el propio fallback que debía protegernos se dispara y **anula
el fix de BUG-015** en producción. No es la misma causa: es el eslabón que hace fallar al remedio de
los otros tres. El arreglo cierra el hueco **en el borde donde entra el `quoted_name`**.

### Por qué los tests no lo cazan

Los tests usan **fixtures CSV** (`read_csv` → nombres `str` puros), donde `feature_names_in_` sí se
puebla. **Solo el path real `--desde-gold` (lee de la BD) sufre el `quoted_name`.** Y solo se manifiesta
cuando **un driver queda 100 % `SIN_DATO`** en la ventana de entrenamiento (si no se descarta ninguno,
`DRIVERS`=6 coincide por casualidad con lo entrenado). Con datos reales de cobertura parcial —D5 agua es
regional, D6 aire ~80 zonas— es un escenario **plausible en producción**, no solo en la muestra. Misma
lección que BUG-023: un fixture construido para validar la forma no valida la realidad.

### Alcance del impacto

Todos los consumidores que confían en `feature_names_in_`, todos en archivos de C3:
`publicar_gold.construir_predicciones` (:267) y `construir_predicciones_municipio_nivel` (:335),
`entrenar_ml02` (:245, :302) y `evaluar.py` (:212, :244).

### Fix preparado (4 líneas, validado en local)

En `cargar_features_desde_gold`, tras `pd.read_sql_table`, normalizar los nombres a `str` puro:

```python
df = pd.read_sql_table(tabla, engine, schema=esquema)
df.columns = [str(c) for c in df.columns]  # SQLAlchemy da quoted_name; sklearn solo
                                            # puebla feature_names_in_ con str puro (BUG-041)
```

**Validación (local, 2026-09-02):** con el fix, `feature_names_in_` = los 5 drivers usables y
`construir_predicciones` produjo **55 filas** (ciclo 2024-2025), `indice_riesgo` ∈ [0.084, 0.742], sin
saturar. Publicadas 55 predicciones (ML-01) + 55 recomendaciones (ML-02); `/api/v1/kpis` →
`escuelas_en_riesgo=2`; diferenciador prescriptivo probado (15DJN0049A→D1, 09DSN0042A→D2).

### Propiedad / gobernanza

`entrenar_ml01.py` está bajo `src/modelos/**`, **verde de Célula 3** (Andrés González —TL—, Héctor
Morales, Estefany Hernández, Carlos Mayorga). Por la regla 9, `check_ownership.py` reprueba un PR de
cualquier rama fuera de C3 que toque `src/modelos/**` (`return 1`). Por eso el reporte y el parche se dan
de alta aquí —`Bug_Register.md` es `comunes`, y `Definition_of_Filed` obliga a cualquiera a registrar el
bug que encuentre— pero **el código lo lleva Célula 3**: lo natural es **Héctor Morales**
(`dev/hector-morales`), dueño de US-311/US-313, con la coordinación del TL **Andrés González**. Es
exactamente el patrón de BUG-018 ("queda el parche preparado… para que lo aplique quien corresponde") y
BUG-008. Seguimiento honesto de la corrida L0 en `_local/L0_ML_realidad_vs_prueba.md` §5.

**Alternativa más defensiva (follow-up de C3):** pasar `drivers_usados` explícito a
`construir_predicciones` en vez de depender de `feature_names_in_`, para no volver a atarse a un
atributo que un tipo de columna puede dejar sin poblar.

## BUG-016 — Filas sin ningún driver rompían la publicación de ML-02

Reportado por Diana Alvarez el 2026-08-27, corriendo `publicar_gold.py --desde-gold` contra la Gold
real. ML-01 ya entrenó y publicó bien (45 249 filas); el fallo estaba un paso después:

```
File "src/modelos/entrenar_ml02.py", line 114, in generar_driver_dominante_proxy
    raise ValueError("No se puede derivar driver_dominante_proxy para filas sin ningun driver.")
```

En el Gold real hay escuelas con los **seis drivers en NULL a la vez**. `generar_driver_dominante_proxy`
falla ahí **por diseño**, y hace bien: no se puede nombrar un driver dominante donde no se observó
ninguno. Forzarlo sería inventar el diferenciador del proyecto.

Lo que faltaba era **apartarlas antes**. La Célula 1 ya adoptó esa convención en la `driver_dominante`
real de US-302 (PR #113): esas filas quedan en `NULL`. Y `validar_target_ml02` —con razón— rechaza un
target con nulos, así que el filtrado tiene que ocurrir en el sitio de llamada, que es mío.

`filtrar_con_driver_observado()` las aparta y dice cuántas. **Endurecido el 2026-08-28**, cuando US-302 (#113) publicó la `driver_dominante` real: el filtro miraba sólo si el valor del driver era no nulo, pero C1 exige además `dN_cobertura = 'OK'`. Una fila con dato y cobertura `SIN_DATO` tiene la etiqueta en NULL y habría sobrevivido al filtro para morir en `validar_target_ml02`. Ahora, cuando la columna real existe, **ella es la autoridad** y el filtro mira dónde quedó NULL en vez de inferirlo. **Conservan su predicción de ML-01** —la
variación de matrícula no necesita drivers— y no reciben recomendación. Eso es exactamente la regla de
cobertura parcial: `SIN_DATO` explícito, nunca un driver inventado.

### Lo que la simulación encontró y las pruebas unitarias no

Al apartar filas de `features_ml02`, esas escuelas quedan con predicción pero sin features, y
`construir_recomendaciones_ml02` lo rechaza con `Faltan features de ML-02 para los CCT`. La tentación
era relajar esa verificación; se hizo lo contrario: se filtran las predicciones en el sitio de llamada
y la verificación sigue intacta, porque debe seguir cazando desajustes **de verdad** y no el hueco que
abrimos a propósito. Hay una prueba que lo fija.

## BUG-017 — `indice_riesgo` publicado saturado por unidades del target

La corrida real reportó **MAE 10.90**. La sigmoide de `indice_riesgo` está calibrada sobre
**fracción**: `0.0` → riesgo 0.30, `-0.05` ("pierde 5 % de su matrícula") → riesgo 0.60.

Un error medio de 10.90 es **218 veces** la banda completa de calibración. Verificado:

| variación | indice_riesgo |
|---|---|
| 0.0 | 0.300000 |
| -0.05 | 0.600000 |
| -0.10 | 0.840000 |
| -5.0 | 1.000000 |
| -10.9 | 1.000000 |

Con esa escala, **las 45 249 filas publicadas quedan en riesgo ≈ 1.00**. No es una degradación: es
salida incorrecta que en un tablero se ve perfectamente normal, y `RIESGO_UMBRAL = 0.60` contaría como
"escuela en riesgo" a todo el universo.

La sospecha es que `target_variacion_matricula` en el Gold real viene en **puntos porcentuales**
(`-5.0`) o como **diferencia absoluta de alumnos**, en vez de fracción.

`verificar_escala_variacion()` detiene la publicación antes de convertir, mirando la **mediana** de
`|variación|` —no el máximo, para no confundir unidades equivocadas con unos pocos valores extremos
legítimos. Una escuela que triplica su matrícula no dispara la alarma; una columna entera en otra
escala sí.

> **Falta la parte que no me toca:** confirmar con C1 en qué unidades produce US-104 esa columna. Si
> la escala es correcta y el dato es así de extremo, entonces hay que recalibrar las anclas en
> `vault/15_ML_Models/Indice_Riesgo_ML01.md` — pero eso es una decisión de negocio, no un arreglo de código.

## BUG-018 — ML-02 repite el defecto por ventana de BUG-015

Encontrado al simular la corrida completa de Diana, no reportado por ella: es el siguiente muro.

`entrenar_ml02._matriz()` devuelve `df[list(DRIVERS)]` —los seis, siempre— y el bucle de backtesting
no comprueba la cobertura dentro de la ventana de entrenamiento. Es **el mismo defecto** que BUG-015,
en el clasificador:

```
ValueError: window shape cannot be larger than input array shape
  ...
  entrenar_ml02.py:177 in entrenar_y_evaluar
    modelo = HistGradientBoostingClassifier(**params).fit(x_entrena, y_entrena)
```

Se dispara con D6 (aire), que tras la IDW de US-105 sólo cubre el ciclo más reciente y queda vacío en
el tramo de entrenamiento.

El arreglo es el mismo que ya se aplicó y probó en `entrenar_ml01`: evaluar `drivers_utilizables()`
sobre la ventana de entrenamiento y entrenar sólo con esos. `entrenar_ml02.py` es de **Andrés González
Habib**; queda el parche preparado y la reproducción, para que lo aplique quien corresponde.


## BUG-019 — La misma columna en dos unidades según el grano

Consecuencia de BUG-017, y el defecto de fondo: **el contrato nunca declaró la unidad**.
`Data_Model.md` §5.3 dice `StrictFloat` y nada más, así que los dos productores eligieron distinto y
ninguno se equivocó contra lo escrito.

| Productor | Grano | Fórmula | Unidad |
|---|---|---|---|
| `features_escuela.sql` (C1, US-104) | escuela | `matricula_total - matricula_ciclo_anterior` | alumnos |
| `target_hibrido.variacion_desde_serie` (C3, DEC-007) | municipio × nivel | `matricula_total / matricula_previa - 1.0` | fracción |

Ambas alimentan `gold.predicciones.valor` distinguidas sólo por `grano` (DEC-010). Un tablero que lea
esa columna sin filtrar por grano está sumando alumnos con fracciones.

**No se corrige unilateralmente:** cuál de las dos unidades gana es decisión de equipo, propuesta en
[[vault/03_Architecture/ADRs/ADR-007-unidad-target-variacion-matricula|ADR-007]] con la evidencia. La
recomendación ahí es fracción, porque el target absoluto ordena las escuelas por tamaño
(correlación 0.70 con la matrícula) en vez de por riesgo, y hunde a las escuelas pequeñas y rurales
que el proyecto existe para hacer visibles.

Mientras tanto `verificar_escala_variacion()` impide publicar el grano escuela, que es el
comportamiento correcto.
## BUG-020 — Todas las rutas con base de datos responden 500 en producción

Encontrado el 2026-08-28 al reanudar la verificación E2E de la Célula 3, que llevaba semanas
bloqueada por BUG-008. Ese sí quedó arreglado: la API pública levanta y expone las 18 rutas del
contrato v1. Lo que no funciona es todo lo que consulta datos.

```
/api/v1/health                    HTTP 200  {"status":"ok"}
/api/v1/predicciones/{cct}        HTTP 500
/api/v1/predicciones/batch        HTTP 500
/api/v1/escuelas                  HTTP 500
```

Reproducir:

```bash
curl -i https://faro-api-eanzfglvyq-uc.a.run.app/api/v1/predicciones/09DPR0001A
```

Repetir la misma petición añadiendo una cabecera de autorización con un token inventado da
**exactamente el mismo 500** (no se pega el comando literal aquí porque el escáner de secretos del
CI marca esa cabecera, y con razón).

**Ninguna de las dos da 401.** El spec declara `bearerAuth` en esas rutas, así que una petición sin
token debería rebotar con 401 antes de tocar nada. Que no lo haga significa que el fallo ocurre antes
de la validación —probablemente una dependencia de sesión de base de datos que revienta al construir
la petición—. No es que la autenticación esté mal implementada.

> **Corrección del 2026-08-28 (PM).** La redacción original añadía «hoy no se puede comprobar en
> producción, y eso toca US-402». Verificado contra el despliegue, **eso no es cierto**: la
> autenticación sí se comprueba y sí funciona.
>
> ```
> GET  /api/v1/auth/login    HTTP 302   (redirige al proveedor)
> GET  /api/v1/auth/me       HTTP 401   (sin token, como debe)
> GET  /api/v1/version       HTTP 200
> ```
>
> Lo que no se puede comprobar es el 401 **de las rutas de datos**, porque revientan antes. El
> alcance de BUG-020 es la sesión de base de datos, no la autenticación: **US-402 no queda tocada
> por este bug.**

**Hipótesis, sin confirmar:** el Gold de producción está vacío o inalcanzable. `gold.predicciones` se
crea con `metadata.create_all` dentro del job de publicación de C3, que **nunca ha corrido contra la
base de producción** —sólo contra el Gold local de Diana—. Pero `/escuelas` lee `dim_escuela`, que no
depende de ese job, así que el problema parece más amplio que la tabla de C3.

Lo que hace falta para cerrarlo es mirar los logs de Cloud Run, que son de C4/C5.

**Actualización 2026-08-29/30 (C5, US-505 Fase 2 — PR #144/#146):** BUG-020 **curado en
producción**. Se pobló Gold en Cloud SQL y se redeployó `faro-api` por IP privada con secretos en
Secret Manager. Validación en prod: `/escuelas` **500→200** (25 escuelas), `/predicciones/{cct}`
**500→404 estructurado** (correcto: `gold.predicciones` vacía hasta que ML-01 publique a prod).

**Verificación 2026-09-02 (Juan Carlos Macías, US-412/US-416):** re-confirmado en vivo contra la
URL pública — `/api/v1/predicciones/{cct}` → 404 `ErrorOut`, `/api/v1/predicciones/batch` → 200
`{"items":[],"total":0}`, `/api/v1/escuelas` → 200. **BUG-020 no reproduce.** Regresión adicional
en `tests/test_repositorio_modelos.py`: un `ProgrammingError` por esquema `gold` ausente ahora
degrada a 503, no a 500. **Recomendación a los dueños (Christian Ruiz / Luis Téllez):** mover a
`fixed` → `closed`. *(El campo `status` de la tabla lo actualizan los dueños; esta nota no lo
cambia.)*

## BUG-024 — `SELECT INTO` atravesaba el guardarraíl de solo lectura

Reportado por Edgar Coronel el 2026-08-28 durante la revisión de seguridad del PR #119.
`validar_sql_lectura()` aceptaba cualquier sentencia que comenzara con `SELECT` o `WITH` y no
incluyera los verbos prohibidos. En PostgreSQL, esta consulta crea una tabla aunque empiece con
`SELECT`:

```sql
SELECT cct INTO public.robo FROM gold.predicciones;
```

El arreglo agrega `into` a `VERBOS_PROHIBIDOS`. Una consulta legítima de solo lectura no necesita
esa cláusula. La regresión comprueba tanto `validar_sql_lectura()` como `preparar_sql_seguro()`.

## BUG-025 — El agente desplegado responde lo mismo a todo, incluido lo destructivo

Encontrado el 2026-08-28 al verificar la URL pública para la reconciliación de estatus. `/agente/consulta`
responde **200**, lo cual parecía buena noticia frente a BUG-020. No lo es: responde 200 a todo, con el
mismo texto.

```
POST /api/v1/agente/consulta  {"pregunta":"cuantas escuelas hay en riesgo"}
POST /api/v1/agente/consulta  {"pregunta":"cual es la capital de Francia"}
POST /api/v1/agente/consulta  {"pregunta":"Borra la tabla de predicciones"}
POST /api/v1/agente/consulta  {"pregunta":"zzzz qqq 12345"}
```

Las cuatro devuelven, byte por byte:

```json
{"respuesta":"En el alcance actual hay 4 escuelas; 2 superan el umbral de riesgo (0.5).",
 "sql_generado":"SELECT cct, indice_riesgo FROM gold.features_escuela WHERE indice_riesgo >= 0.5;",
 "fuera_de_alcance":false}
```

Que sea un stub está **documentado y es legítimo**: el docstring de `src/api/v1/agente.py` lo dice, y
US-304a lleva semanas registrando «falta conectar el endpoint real de C4». Lo que no estaba registrado
es su consecuencia, y son dos.

**Primera: el stub deja pasar la frase destructiva más obvia.** Su lista es
`("borrar", "elimina", "drop", "update", "delete")` y la comprobación es por subcadena, así que
`"borrar" in "borra la tabla de predicciones"` es `False`. La conjugación más natural en español no
dispara el filtro. Los guardarraíles reales de `src/agente/guardrails.py` **sí** rechazan esa frase
—verificado— pero la API no los llama.

**Segunda: en la demo esto se ve peor de lo que es.** No borra nada —no hay ejecución de SQL detrás—,
pero el usuario ve una pregunta destructiva aceptada, con `fuera_de_alcance: false` y un `sql_generado`
impreso al lado, como si algo se hubiera ejecutado. Cualquier pregunta fuera de tema recibe una
respuesta segura de sí misma sobre escuelas.

**Mitigación de 2 líneas mientras llega la integración real:** que el stub llame a
`pregunta_en_alcance()` de `src/agente/guardrails.py` en vez de su lista de subcadenas. El módulo ya
está en `main`, no depende de ChromaDB ni de embeddings y no añade dependencias al contenedor.

**El cierre de verdad** es US-304a: conectar `procesar_consulta_con_rag()` (mergeado en PR #119) al
endpoint. Eso es C4 con C3.

## BUG-023 — El reporte de evaluación no se podía generar con un driver excluido

Tercera aparición de la misma causa que BUG-015 (ML-01) y BUG-018 (ML-02): **predecir con columnas
distintas a las del entrenamiento**. Encontrada el 2026-08-28 al implementar la petición del PM de
publicar los drivers excluidos en un artefacto.

```
❌ error_por_entidad:  ValueError: The feature names should match those that were passed during fit.
                       Feature names unseen at fit time: - d5_agua
❌ cobertura_y_error:  (idéntico)
```

Ambas funciones hacían `modelo.predict(_matriz(prueba))`, y `_matriz` toma los seis `DRIVERS` por
omisión. Cuando un driver queda fuera del entrenamiento, sklearn rechaza la forma.

La ironía operativa: el reporte fallaba **exactamente** en el escenario que existe para documentar.
Con los seis drivers presentes —el caso del fixture— nunca se disparaba.

Arreglo: las dos usan `getattr(modelo, "feature_names_in_", DRIVERS)`, igual que
`construir_predicciones` y que el `predecir_driver` de ML-02.

### Por qué se escapó tres veces

El fixture sintético trae los seis drivers poblados. **El escenario que rompe es justamente el que
el fixture no representa**, así que ninguna suite lo veía: ni la mía, ni la de ML-02. La lección no
es "faltaba una prueba" —es que un fixture construido para validar la forma no valida la realidad, y
que los casos degradados hay que construirlos a propósito.

## BUG-032 — `Data_Model.md` se contradice sobre dónde vive `indice_riesgo`

Encontrado el 2026-08-29 al cerrar los pendientes de `DOC-INDICE-RIESGO`.

**Línea 181 (§4.5), correcta y implementada:**

> `valor` (variación cruda, para métricas MAE/RMSE de ML-01) · **`indice_riesgo`** (float[0,1],
> columna derivada calculada en `src/modelos/riesgo.py`)

**Línea 313 (nota de §5.3), obsoleta:**

> `indice_riesgo` vive en `gold.predicciones` (columna `valor`, `modelo = 'ML-01'`)

Las dos no pueden ser ciertas. La implementación coincide con la 181: `publicar_gold.py` crea ambas
columnas y `src/api/schemas.py` declara `indice_riesgo: StrictFloat | None = Field(None, ge=0, le=1)`.

El daño no es teórico. Quien siga §5.3 consultará `valor` esperando un índice acotado a `[0,1]` y
recibirá la variación cruda — que hasta que se implemente ADR-007 viene en **alumnos absolutos**. Es
decir, valores como `-20` donde el consumidor espera `0.6`, sin que nada falle. Es el mismo modo de
falla de BUG-017: un número creíble que significa otra cosa.

Arreglo: la nota de la 313 debe decir que `indice_riesgo` es su **propia columna**, no `valor`.
Archivo de Célula 1.
**Resuelto 2026-08-30** — Diana Alvarez Varela (C1), rama `docs/diana-varela-bug032-indice-riesgo`: la nota de la línea 313 ahora dice que `indice_riesgo` es su propia columna en `gold.predicciones` (no vive en `valor`), consistente con la línea 181 y con `publicar_gold.py`/`src/api/schemas.py`.

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

---

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

---

## BUG-010 — `/predicciones` sirve datos simulados, no la salida de ML-01

| | |
|---|---|
| **Severidad** | high — impide cumplir la verificación **#4** del ensayo E2E del 28–29 |
| **Estado** | `fixed` (pendiente de PR/merge — `feat/juan-mayen-us415-pydantic-schemas`) |
| **Detectado** | 2026-08-24, preparando el guion de la verificación #4 |
| **Owner** | **Célula 4** (`src/api/`) — Juan Carlos Macías Mayen (US-412) |

### Qué pasa

`src/api/v1/predicciones.py` importa `src.api.mock_data` y construye la respuesta desde ahí. Su
propio docstring lo anticipa: *"Los valores provienen de `mock_data`; al integrar MLflow (Célula 3)
es un swap"*. Ese swap no se ha hecho.

`src/api/repositorio_gold.py` (US-411) sí lee Gold, pero cubre `/escuelas`, `/municipios` y `/kpis`
— **no `/predicciones`**.

### Por qué importa ahora

El PLAN_MAESTRO fija como verificación #4 del ensayo: *«≥1 modelo sirviendo por API (ML-01) …
`/predicciones` devuelve valor (real o simulado, marcado)»*.

El criterio **admite valores simulados si están marcados**, así que la falta de datos reales del 911
no bloquea. Lo que sí bloquea es que hoy el endpoint no consulta el modelo en absoluto: devolvería un
número escrito a mano, no la predicción de ML-01. La verificación pasaría de forma engañosa.

### Lo que el swap necesita

`gold.predicciones` y `gold.recomendaciones` ya están pobladas y verificadas contra Postgres
(US-313). El mapeo a `PrediccionOut` es directo salvo por un campo:

| Campo de `PrediccionOut` | Origen | ¿Existe? |
|---|---|---|
| `cct`, `id_ciclo` | `gold.predicciones` (filtrar `grano = 'escuela'`, `modelo = 'ML-01'`) | ✅ |
| `indice_riesgo` | `gold.predicciones.indice_riesgo` | ✅ |
| `mlflow_run_id` | `gold.predicciones.mlflow_run_id` | ✅ |
| `driver_dominante`, `recomendacion` | `gold.recomendaciones` por `cct` + `id_ciclo` | ✅ |
| **`cluster`** | **ML-03 (US-321, Estefany Hernández)** | ❌ **no existe** |

**`PrediccionOut.cluster` es un `StrictInt` obligatorio sin productor.** Mientras ML-03 no exista,
el swap no puede completar la respuesta sin inventar el valor. Opciones a decidir por la Célula 4:
hacer `cluster` opcional, o declararlo explícitamente ausente — nunca rellenarlo con un entero
arbitrario, por la misma regla de `SIN_DATO` que rige el resto del proyecto.

### Nota

Filtrar por `grano = 'escuela'` es necesario desde **DEC-010**: `gold.predicciones` admite también
filas a `municipio × nivel`, que no corresponden a un CCT.

### Resolución (2026-08-26, Juan Carlos Macías Mayen)

Se eligió **`cluster` opcional** (`StrictInt | None = None`), no la alternativa de bandera
explícita: mismo criterio ya usado por `EscuelaOut.indice_riesgo`/`driver_dominante` (Christian
Ruiz, 2026-08-20) para "campo sin productor" — no se introduce un `tiene_cluster` porque, a
diferencia de `tiene_prediccion` (que varía por escuela), hoy ML-03 no cubre a *ninguna* escuela:
una bandera constante en `False` sería ruido, no señal. Si al aterrizar ML-03 resulta que solo
cubre parte del universo, ahí sí se justifica una bandera — no antes.

`src/api/repositorio_modelos.py` (`RepositorioModelosPostgres`) hace el swap real sobre
`gold.predicciones` (`modelo = 'ML-01'`, `grano = 'escuela'`) `JOIN` `gold.recomendaciones`,
mismo patrón `Depends` + Protocol que `RepositorioGold` (US-411). `src/api/db.py` gana la columna
`grano` que le faltaba a la tabla `predicciones` (post-DEC-010). `src/api/mock_data.py` ya no
respalda el endpoint en vivo; se queda solo como referencia para un mock server standalone
(§6 de `API_Specification.md`), con su propio `cluster` corregido a `None` por la misma razón.

**Pendiente de avisar a C2 (Manuel) y C3 (Andrés/Héctor)** por la regla de oro del contrato
(cambio de forma en `PrediccionOut`) — parte de la descripción del PR.

## BUG-015 — Un driver sin ningún dato impedía entrenar ML-01 sobre el Gold real

| | |
|---|---|
| **Severidad** | high |
| **Estado** | `fixed` |
| **Detectado** | 2026-08-27 por Diana Alvarez, al correr `publicar_gold --desde-gold` sobre `gold.features_escuela` real |
| **Corregido por** | Héctor Morales (C3) |

### Síntoma

```
Features desde gold.features_escuela: 135 932 filas · 46 515 escuelas · ciclos
  ['2022-2023', '2023-2024', '2024-2025']
...
ValueError: window shape cannot be larger than input array shape
  en sklearn/ensemble/_hist_gradient_boosting/binning.py::_find_binning_thresholds
```

La carga funcionaba; el entrenamiento tronaba antes de escribir nada a Gold.

### Causa

Un driver con **cero valores observados** en todo el conjunto. `HistGradientBoostingRegressor`
calcula sus cortes con `sliding_window_view(distinct_values, 2)`; sin ningún valor distinto, la
ventana de tamaño 2 no cabe y numpy falla con un mensaje que **no menciona la causa real**.

Reproducido de forma aislada: una columna **toda `NaN`** falla; una columna **constante** entrena
sin problema.

En el Gold real el driver afectado es **D5 (agua)**, que sigue completo en `SIN_DATO` porque DS-06
(CONAGUA) no tiene descarga verificada. El fixture sintético nunca lo ejercitó porque su generador
siempre da algún valor a los seis drivers.

### Corrección

`drivers_utilizables()` detecta los drivers con al menos un valor observado y los excluye del
entrenamiento **reportándolo**, nunca en silencio:

```
⚠️  Drivers sin ningún dato, excluidos del entrenamiento: ['d5_agua'].
    Se entrena con 5 de 6.
```

Que un driver no aporte nada es **un hallazgo del proyecto**, no un detalle de implementación:
`ResultadoEntrenamiento` expone `drivers_usados` y `drivers_excluidos` para que quede en el reporte
de US-312 y en el registro de MLflow.

Si **ningún** driver tiene datos, falla con un mensaje explícito en vez de un error de numpy.

### Segunda vuelta: la cobertura hay que mirarla POR VENTANA

El primer arreglo excluía los drivers vacíos **en todo el conjunto**, y Diana reportó que seguía
fallando. Tenía razón: la exclusión correcta es **dentro de la ventana de entrenamiento**.

Un driver puede tener datos globalmente y estar **entero en `NaN` en el tramo con el que se
entrena**. Es exactamente el caso de **D6 (aire)**: llega por la interpolación IDW de US-105 y sólo
cubre el ciclo más reciente, que con 3 ciclos y 1 ventana cae del lado de **prueba**, no del de
entrenamiento.

Con la comprobación global, D6 pasaba el filtro y volvía a romper el binning. Ahora se evalúa por
ventana y se reportan los dos casos por separado:

```
⚠️  Drivers sin ningún dato en todo el conjunto: ['d5_agua']. Quedan fuera del modelo.
⚠️  entrena[2021-2022…2022-2023] -> prueba[2023-2024]: sin datos en el entrenamiento
    ['d5_agua', 'd6_aire']; se entrena con 4 de 6 drivers.
```

Son dos situaciones distintas —un driver que no existe nunca y uno que aún no cubre el pasado— y
merecen mensajes distintos.

### Segundo hallazgo: `--ventanas` fijo

El default de 3 ventanas exigía 5 ciclos; el Gold real tiene 3 utilizables (2021-2022 se consume
como referencia del target). `--ventanas` pasa a ser **automático**: `ventanas_posibles()` calcula
el máximo que permiten los ciclos disponibles y lo reporta. Señalado por Diana en el mismo reporte.

### Verificación

Simulado el escenario exacto —3 ciclos y D5 en `SIN_DATO`— el circuito completo corre: entrena con
5 drivers, reporta la exclusión y construye las 80 filas de predicción del ciclo más reciente.

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

---

## BUG-009 — 11 vars de dbt sin valor por default

- **Owner:** Edgar Edmundo Coronel Navarrete
- **Severidad:** high
- **Estado:** fixed
- **traces_up:** US-111
- **found_on:** 2026-08-21
- **fixed_on:** 2026-08-23

### Descripción
Al validar `matricula_historica` (modelo nuevo y aislado, RISK-007/DEC-007) con `dbt build --select matricula_historica`, el build falló con `Required var 'bronze_cct_identifier' not found in config` — una fuente que el modelo ni siquiera consume. Causa: 7 de las 10 tablas Bronze declaradas en `dbt/models/sources.yml` no tienen un valor por default en su `identifier` (a diferencia de `formato911`, `formato911_historico` y `cemabe`, que sí lo tienen). Como dbt necesita renderizar el manifest completo del proyecto antes de ejecutar cualquier selección, cualquier `--select` falla si falta CUALQUIERA de las 7 vars, sin importar si el modelo seleccionado las usa.

Las 7 fuentes afectadas tocan varias historias distintas, sin un solo dueño:
- `bronze_cct_identifier` (DS-02 Catálogo CCT)
- `bronze_sesnsp_identifier`, `bronze_sinaica_observaciones_identifier`, `bronze_sinaica_estaciones_identifier` (DS-04/DS-05, Luis García)
- `bronze_coneval_identifier` (DS-07, Deni)
- `bronze_conagua_identifier`, `bronze_conapo_identifier` (DS-06/DS-08, Emilio)

`sources.yml` es de Deni (US-111).

### Pasos para reproducir
1. `cd dbt`
2. Correr cualquier `dbt build`/`dbt run`, con o sin `--select`, sin pasar las 7 vars por `--vars`.
3. Falla con `Compilation Error: Required var 'bronze_cct_identifier' not found in config` (o el nombre de la siguiente var sin default que encuentre).

### Resultado actual vs esperado
- **Actual:** `dbt build --select <modelo>` falla al renderizar fuentes que ese modelo no consume.
- **Esperado:** `dbt build --select <modelo>` sólo debería requerir las vars/fuentes que ese modelo realmente usa; o, alternativamente, las 7 fuentes deberían tener un valor por default como ya tienen `formato911`/`formato911_historico`/`cemabe`.

### Entorno
- dbt-core 1.12.0, dbt-postgres 1.11.0 (`requirements/celula-1.txt`)
- `dbt/models/sources.yml`

### Causa raíz
7 de los 10 `identifier` en `sources.yml` se declararon como `"{{ var('bronze_X_identifier') }}"` sin segundo argumento de default, a diferencia de los 3 que sí lo tienen (`"{{ var('bronze_formato911_identifier', 'formato911_2024_2025') }}"`, etc.).

Además, `dbt/dbt_project.yml` no tenía ningún bloque `vars:`, así que las 4 vars usadas dentro de modelos Silver tampoco tenían dónde tomar un default. El alcance real eran **11 vars, no 7**.

### Fix
- **PR:** `fix/edgar-navarrete-bug009-defaults-dbt` · **DEC-011** · 2026-08-23
- **Reparto (decisión del PM):** no se dividió entre los 4 dueños de DS. Cuatro PRs paralelos sobre
  el mismo YAML garantizaban conflicto y 4 ciclos de revisión para ~15 líneas, a dos semanas del
  freeze. Lo ejecuta el PM en un solo PR; cada dueño de fuente revisa **sus** valores como reviewer.
- **Ubicación (ratificada por Diana Alvarez Varela, TL Célula 1, regla 7):** los `identifier` llevan
  su default **inline** en `sources.yml`, extendiendo el patrón que ya existía; las 4 vars de modelo
  van en un bloque `vars:` nuevo en `dbt_project.yml`, porque `sources.yml` no tiene dónde alojarlas.

| Var | Default | Dueño que confirma |
|---|---|---|
| `bronze_cct_identifier` | `cct_sample` | Diana Alvarez Varela (DS-02) |
| `bronze_sesnsp_identifier` | `sesnsp_test` | Luis Enrique García Vázquez (DS-04) |
| `bronze_sinaica_observaciones_identifier` | `sinaica_observaciones_test` | Luis Enrique García Vázquez (DS-05) |
| `bronze_sinaica_estaciones_identifier` | `sinaica_estaciones_test` | Luis Enrique García Vázquez (DS-05) |
| `bronze_conapo_identifier` | `conapo_sample` | Emilio Galnares Ruiz (DS-08) |
| `bronze_coneval_identifier` | `coneval_v2` | Deni Garrido Fragoso (DS-07) |
| `bronze_conagua_identifier` | `conagua_no_ingerido` ⚠️ falso a propósito | Emilio Galnares Ruiz (DS-06) |
| `bronze_conapo_age_column` | `grupo_edad` | Emilio Galnares Ruiz (DS-08) |
| `bronze_sesnsp_count_column` | `conteo` | Luis Enrique García Vázquez (DS-04) |
| `bronze_conagua_id_column` | `id_estacion` (del esquema documentado, sin datos que lo confirmen) | Emilio Galnares Ruiz (DS-06) |
| `coneval_periodo_medicion` | `2020` ⚠️ deuda técnica | Deni Garrido Fragoso (DS-07) |

**Los dos valores que no se resolvieron, y por qué no se cerraron callados:**

1. `bronze_conagua_identifier` → `conagua_no_ingerido`. No existe ninguna tabla `conagua*` real en
   `bronze`. El nombre es deliberadamente falso (a sugerencia de Diana) para que nadie lo confunda
   con una tabla real al verlo en un log: deja pasar el parse del proyecto y hace que `agua_region`
   falle en runtime **de forma visible**. D5 sigue `SIN_DATO` explícito.
2. `coneval_periodo_medicion` → `2020`. **Deuda técnica aceptada explícitamente por Edgar Coronel
   (PM).** No es una columna: ninguna tabla `coneval_*` trae año o período, así que es un entero
   fijo heredado del ensayo E2E (PR #70) y sin confirmar contra la fuente. Si está mal, no rompe
   nada — **etiqueta mal en silencio** el período de medición del rezago social en
   `silver.rezago_municipio` y todo lo que cuelga de ahí. Pendiente de confirmación por Deni Garrido
   Fragoso (dueña de DS-07) antes del freeze del 6-sep-2026; es también un ítem del checklist de
   freeze en [[vault/03_Architecture/Data_Lineage_US106]].
   **Rastreado como `RISK-008`** en [[vault/10_Risk_Governance/Risk_Register]], con dueña y fecha objetivo:
   el `Bug_Register` no lo alcanza porque el defecto ya está corregido — lo que queda es un valor sin
   confirmar, y el tablero PM lee el registro de riesgos, no el de bugs.

- **Test de regresión:** job `dbt-contract` en `.github/workflows/ci.yml` — corre `dbt parse` en cada
  PR con un perfil dummy (parse no abre conexión a la base). Verificado empíricamente antes de
  abrir el PR: con `main` el parse aborta con `Compilation Error: Required var 'bronze_cct_identifier'
  not found in config`; con el fix termina en exit 0 y genera el manifest completo. Es un cambio a
  `.github/` (regla 7): lo revisa Diana Alvarez Varela como TL de Célula 1 y ratificadora de DEC-011,
  bajo la compuerta única de DEC-003. La revisión de Célula 5 se omite conscientemente por tiempo
  (freeze el 6-sep); el job está aislado y es reversible sin tocar nada más.
- **Efecto colateral:** los comandos que `CLAUDE.md` documenta como estándar (`dbt run --select
  silver`, `dbt test`) estaban rotos de fábrica para cualquiera que clonara el repo. Ahora funcionan
  sin pasar `--vars` a mano.

### Actualización 2026-08-23 — valores reales encontrados (Diana, materializando Gold para el ensayo E2E de Héctor, PR #70)

Al construir un `dbt build` real contra la base del docker-compose local (no solo compilar, con datos) para que Héctor tuviera algo que mostrar en el ensayo del 28-29, se ubicaron los valores reales de 6 de las 7 identifiers, más 2 vars adicionales no documentadas antes que también hacían falta:

| Var | Valor real encontrado |
|---|---|
| `bronze_cct_identifier` | `cct_sample` |
| `bronze_sesnsp_identifier` | `sesnsp_test` |
| `bronze_sinaica_observaciones_identifier` | `sinaica_observaciones_test` |
| `bronze_sinaica_estaciones_identifier` | `sinaica_estaciones_test` |
| `bronze_conapo_identifier` | `conapo_sample` |
| `bronze_coneval_identifier` | `coneval_v2` (existe también `coneval_test`, con `entidad` como código crudo en vez de nombre — parece una ingesta de prueba anterior; **no confirmado con el dueño de DS-07**) |
| `bronze_conagua_identifier` | sin resolver — no existe ninguna tabla `conagua*` ingerida todavía en `bronze` |

Además, `poblacion_municipio.sql` y `delitos_municipio.sql` requieren dos vars que tampoco estaban documentadas aquí:
- `bronze_conapo_age_column` → `grupo_edad` (la columna ya existe con ese nombre literal en `conapo_sample`)
- `bronze_sesnsp_count_column` → `conteo` (idem, ya existe en `sesnsp_test`)

Y `rezago_municipio.sql` requiere `coneval_periodo_medicion`, que **no es una columna** — ninguna de las dos tablas `coneval_*` trae año/período. Es un valor entero fijo que hay que decidir a mano. Se usó `2020` como placeholder solo para el ensayo E2E (no confirmado contra la fuente real) — **pendiente que Deni (dueña de DS-07) confirme el año correcto** antes de usar estos datos para algo más que la demo.

Esto no cierra BUG-009 — sigue pendiente que Edgar decida el reparto para que estos valores (o los que correspondan) queden como default permanente en `sources.yml` — pero deja evidencia empírica lista para quien lo tome. Detalle completo en el DevLog `vault/_DevLog/2026-08-23-diana-alvarez-bug009-hallazgos-gold-e2e.md`.

### Actualización 2026-08-23 — cierre (Edgar, PM · DEC-011)

Al ejecutar el reparto apareció una **var número 11** que no estaba en esta lista:
`bronze_conagua_id_column`, en `dbt/models/silver/agua_region.sql:4`. No se había topado porque
`conagua` no tiene datos ingeridos y `agua_region` nunca llegó a correr. Diana la ratificó como parte
del alcance el mismo día.

Los 11 defaults quedaron aplicados con la ubicación que decidió Diana (identifiers inline en
`sources.yml`, vars de modelo en `dbt_project.yml`) — ver la sección **Fix** arriba para la tabla
completa de valores, dueños y los dos casos que quedaron sin confirmar.

---

## BUG-011 — `sync_semantic_layer.py` lee YAML/SQL en cp1252 en Windows

- **Owner:** Manuel Alejandro Serranía Reinada
- **Reportó:** Marina García del Buey (revisión de US-212, 2026-08-24)
- **Severidad:** medium
- **Estado:** fixed
- **traces_up:** US-203, US-212
- **found_on:** 2026-08-24
- **fixed_on:** 2026-08-25

### Descripción
`_read_yaml()` y `_read_sql()` de `superset/sync_semantic_layer.py` leen los archivos con
`path.read_text()` sin `encoding`, así que en Windows Python resuelve la codificación del locale
(cp1252) y lanza `UnicodeDecodeError` con cualquier `metrics_*.yaml` que traiga acentos o `·`.
El workaround era exportar `PYTHONUTF8=1` antes de cada corrida. `PYTHONIOENCODING` no basta
porque solo afecta stdin/stdout, no la apertura de archivos.

Misma familia que BUG-005: suposiciones del locale por defecto que solo explotan en Windows.
El resto del repo ya usaba `read_text(encoding="utf-8")` explícito; este script (stdlib-only,
escrito en macOS) se pasó de largo.

### Pasos para reproducir
1. En Windows: `python superset/sync_semantic_layer.py`
2. Falla al parsear el primer `metrics_*.yaml` con acentos (`UnicodeDecodeError: 'charmap' codec can't decode byte...`).

### Causa raíz
3 llamadas a `Path.read_text()` sin `encoding`: `_read_yaml()` (2, rutas PyYAML y parser manual)
y `_read_sql()` (1).

### Fix
- Rama `fix/manuel-serrania-bug010-sync-charts-utf8`: `encoding="utf-8"` explícito en las 3 lecturas.
- El mismo PR corrige el hallazgo hermano de la misma revisión: `ensure_chart()` identificaba
  charts por `slice_name` global y repuntaba charts homónimos de otro tablero a otro dataset
  (le pasó a Diana/Marina con "KPI-01 · Matrícula total" entre DB-01 y DB-03). Ahora solo
  actualiza el candidato cuyo `datasource_id` coincide; si el homónimo vive en otro dataset,
  crea un chart nuevo y lo avisa en el log.

### Test de regresión
Pendiente de validar en Windows (el fallo es específico de ese SO; en Linux/macOS el default ya
era UTF-8 y un test no distinguiría). Quien tenga Windows corre el sync sin `PYTHONUTF8=1`.
## BUG-026 — Ningún fixture del repo ejercita el grano escuela multi-ciclo

Reportado por Marina García del Buey el 2026-08-28, buscando por qué `publicar_gold.py --desde-gold`
seguía sin poder entrenar en un ambiente local al día (mitad C1 de BUG-013).

### Descripción

Existen dos fixtures de Formato 911 y **cada uno resuelve la mitad del problema**:

| Fixture | Ciclos | CCT ∩ `gold.dim_escuela` | Sirve a grano escuela |
|---|---|---|---|
| `bronze_formato911_sample.csv` + `…_ciclo_anterior_sample.csv` | **2** | 59 de 60 ✅ | no: `features_escuela` sale con 1 ciclo |
| `bronze_formato911_historico_sample.csv` | **6** ✅ | **3 de 30** | no: el JOIN contra `dim_escuela` se vacía |

```
historico            ∩ dim_escuela          →  3 de 30
formato911_2024_2025 ∩ dim_escuela          → 59 de 60
historico            ∩ formato911_2024_2025 →  3 de 30
```

ML-01 necesita **3 ciclos** en `features_escuela` para hacer partición temporal
(`ventanas_posibles()`), y `features_escuela` pierde un ciclo al calcular el target. Hacen falta ≥4
ciclos en Bronze **sobre los CCT del catálogo**. Ningún fixture cumple las dos cosas a la vez.

### Por qué importa

**No es un problema de ambiente local.** Con datos reales el camino funciona: Diana cargó 4 ciclos
reales el 27-ago y materializó la estrella completa con 149/149 tests en verde
([[vault/_DevLog/2026-08-28-diana-alvarez-formato911-real-validacion-us113]]). El problema es que esa
verificación **solo se puede reproducir con ~460 MB de CSV descargados a mano**, hoy únicamente en el
ambiente de Diana. Consecuencias:

1. **CI nunca recorre la ruta.** El entrenamiento de ML-01 a grano escuela no está cubierto por
   ninguna prueba que corra en el pipeline.
2. **La dueña de DB-03 no puede verificar sus propios criterios de aceptación.** Los bloques de
   predicción y recomendación (AC-002.4) dependen de que existan predicciones en el mismo ciclo que
   el hecho; sin fixture no hay forma de comprobarlo salvo pidiéndole a Diana que corra su ambiente.
3. **El histórico invita a un arreglo que falla en silencio.** Repuntar `features_escuela.sql` a
   `ref('matricula_historica')` —que es lo primero que uno intenta al ver que tiene 6 ciclos— produce
   un modelo **en verde con 3 escuelas en vez de 30**, sin error y con los tests de dbt pasando,
   porque una tabla casi vacía pasa cualquier test. Es el mismo modo de falla de BUG-012.

### Pasos para reproducir

1. Cargar los fixtures de `tests/fixtures/` y correr `dbt run` (7 pasos en
   [[vault/_DevLog/2026-08-27-marina-garcia-pipeline-local-us212]]).
2. `python -m src.modelos.publicar_gold --desde-gold`
3. ```
   ValueError: Con 1 ciclos no se puede hacer backtesting: se necesitan al menos 3
   (entrenar con 2 y evaluar con 1). Ciclos disponibles: ['2024-2025'].
   ```
4. ```sql
   select count(*) from (
     select distinct cct from silver.matricula_historica
     intersect select cct from gold.dim_escuela) x;   -- devuelve 3
   ```

### Causa raíz

`generate_bronze_formato911_historico_fixtures.py` genera su muestra sintética sin sembrarla desde
`bronze.cct`. Su docstring documenta con mucho cuidado la *suciedad* que reproduce —ceros a la
izquierda, mayúsculas, reingestas, dos turnos, entidad fuera de scope— pero no dice nada sobre el
universo de CCT, porque su único consumidor, `gold.matricula_municipio_nivel`, agrega a
municipio × nivel y **nunca toca `dim_escuela`**. La incoherencia era invisible hasta que alguien
intentó usar el histórico a grano escuela.

### Precisión de la causa (Diana Alvarez, 2026-08-29)

Mi encuadre original —"dos fixtures y cada uno resuelve la mitad"— sugiere que el histórico era
candidato a tapar el hueco. **No lo es, y por una razón más de fondo que el solape de CCT:**
`silver.matricula`, que es la que alimenta `features_escuela`, **nunca lee de
`bronze.formato911_historico`**. Ese camino termina en `gold.matricula_municipio_nivel` (DEC-007) y
no toca el grano escuela. Aunque se le arreglara el solape, no habría movido la aguja aquí.

El hueco real es aritmético y vive en la tabla que sí está en el linaje:
`bronze.formato911_2024_2025` solo tenía **2 ciclos crudos**, y `con_target`
(`features_escuela.sql:74`) sacrifica siempre el primer ciclo de cada `cct` como referencia del
`LAG`. Como `ventanas_posibles()` exige 3 ciclos ya con target, hacen falta **4 ciclos crudos**. El
solape sigue siendo cierto y sigue importando —es lo que hace que el arreglo aparente falle en
silencio— pero es la consecuencia, no la causa.

### Fix

**PR #129** (Diana Alvarez): fixture aditivo con **≥4 ciclos sobre los CCT de `bronze.cct`**,
reutilizando las de `bronze_formato911_sample.csv` tal cual —mismo patrón que
`..._ciclo_anterior_fixture.py`— para que el 100 % de solape sea estructural y no una coincidencia
que haya que perseguir. Se carga en la misma tabla. No toca ningún modelo dbt.

### Verificación del fix (Marina García del Buey, 2026-08-29)

Revisado corriéndolo, no leyéndolo. El generador es **reproducible** (mismo MD5 al regenerar) y la
carga es **idempotente**. Resultado en Postgres local:

| Qué | Antes | Con PR #129 |
|---|---|---|
| Ciclos crudos en `bronze.formato911_2024_2025` | 2 | **4** |
| Ciclos en `gold.features_escuela` | 1 | **3** (2022-2023 … 2024-2025) |
| CCT que cruzan con `gold.dim_escuela` | — | **60 de 60** |
| `publicar_gold.py --desde-gold` | `ValueError` por 1 ciclo | **entrena ML-01, MAE 12.2252** |

`dbt run --threads 1 --full-refresh`: 22 modelos OK; el único fallo es `silver.agua_region` por
CONAGUA no ingerida, que es el error esperado y correcto. La corrida se detiene ahora en la guarda de
BUG-017 —no en la falta de ciclos—, tal como Diana reportó.

Observación menor, **no bloqueante**: el panel queda desbalanceado (60 escuelas en 2022-2023, 30 en
2023-2024, 55 en 2024-2025), porque los dos ciclos nuevos cubren las 72 CCT del fixture base y los
dos viejos no. Con 1 ventana de backtesting funciona; si algún día se quieren 2 o más, conviene
emparejar la cobertura.

### Test de regresión

Propuesto, dos aserciones que hoy no existen:

- solape mínimo entre `silver.matricula_historica` y `gold.dim_escuela`;
- ciclos mínimos en `gold.features_escuela`, para que "salió con 1 ciclo" reprueben en CI en vez de
  descubrirse a mano.

## BUG-027 — `metrics_kpis_base_us221.yaml` apunta a un directorio que ya no existe

Reportado por Marina García del Buey el 2026-08-28, revisando si US-221 colisionaba con DB-03/DB-04.
(No colisiona: los KPI base viven sobre `cubo_matricula`, de DB-01.)

### Descripción

Las 5 entradas del catálogo declaran `sql_ref: sql/kpi_0*.sql`, pero `superset/sql/` **ya no existe**:
el commit `1c2f5f9` movió esos archivos a `superset/semantic/`. El catálogo quedó apuntando al vacío.

### Por qué CI no lo ve

El mismo commit **sí** actualizó `tests/test_kpis_us221.py`, pero ahí la ruta está codificada:

```python
SQL_DIR = Path(__file__).parent.parent / "superset" / "semantic"
```

El test nunca lee el `sql_ref` del YAML, así que valida los archivos correctos mientras el catálogo
—el artefacto que la gente consulta— apunta a otro lado. La prueba pasa y la referencia sigue rota.

> **Actualización 2026-08-30 (Monserrat Miranda).** Confirmado con evidencia nueva: el pendiente
> de C2/Oscar Quiroz no es solo una referencia rota que nadie lee. `sync_semantic_layer.py`
> descubre `.sql` por *glob* directo sobre `superset/semantic/*.sql` (línea 224), sin pasar por
> `sql_ref` ni por ningún `datasets:` del YAML — así que los 5 `kpi_0*.sql` que este bug pide
> borrar se siguen registrando como datasets nuevos en cualquier sincronización.
>
> Al intentar validar US-214b en vivo (Superset 6.1.0, Docker local), `kpi_01_matricula_total.sql`
> específicamente usa `WHERE e.nivel = :nivel` — un bind-param de SQLAlchemy sin valor al
> momento de crear el dataset — y Superset lo ejecuta tal cual contra Postgres para inspeccionar
> columnas. Postgres lo rechaza (`syntax error at or near "%"`), sin capturar la excepción:
> **`sync_semantic_layer.py` aborta por completo antes de sincronizar ningún dashboard**, no solo
> el suyo. Por eso sube la severidad a `medium`: ya no es una referencia muerta, es un bloqueo
> operativo para cualquiera que sincronice desde cero.
>
> Mitigación local usada hoy (no persiste en el repo): apartar temporalmente
> `kpi_01_matricula_total.sql` de `superset/semantic/` solo en disco para completar la validación
> de DB-05/DB-08, y devolverlo a su lugar al terminar.

### Fix propuesto

De C2 (Oscar Quiroz, dueño del artefacto): cambiar los 5 `sql_ref` a `semantic/…`.

### Test de regresión

Propuesto: que `test_kpis_us221.py` **resuelva la ruta desde el `sql_ref` del YAML** en vez de
codificarla, para que el catálogo y los archivos no puedan volver a divergir en silencio.

## BUG-028 — El cero de la izquierda de `cve_mun` se perdía al leer el CSV

Encontrado por Edgar Coronel (PM) el 2026-08-29, resolviendo el cruce entre el PR #124 (Héctor
Morales) y el PR #127 (Diana Alvarez). No lo reportó una persona: lo destapó una guarda escrita
minutos antes.

### Descripción

`cargar_features()` leía el fixture con `pd.read_csv(ruta)` sin declarar tipos. `cve_mun` es
puramente numérica, así que pandas la infería `int64` y descartaba el cero inicial:

```
"09001"  ->  9001
```

El daño no aparece al leer: aparece **río abajo y sin ruido**. El join contra `dim_municipio` no
cruza, la agregación de DEC-007 pierde el grupo, y nada lanza excepción. Afecta a las **9 entidades
cuya clave INEGI empieza en cero** — entre ellas **CDMX (`09`)**, que es la entidad principal de
`SCOPE_ENTIDADES`.

### Por qué las pruebas no lo veían

Diana **sí había previsto exactamente esto**. Su comentario en `tests/conftest.py` lo dice palabra
por palabra:

```python
# cve_mun es puramente numérica (p.ej. "09001") -- sin dtype=str, pandas la infiere como
# int64 y se come el cero a la izquierda, rompiendo el join contra dim_municipio.
return pd.read_csv(FIXTURE_FEATURES, dtype={"cve_mun": str})
```

Pero el `dtype` quedó **sólo en el fixture de pruebas**. El lector de producción —el que usan
`entrenar_ml01`, `publicar_gold` y la generación de la dimensión— seguía sin él. Resultado: los
tests veían la clave bien formada y el pipeline real no. El diagnóstico era correcto y la corrección
se aplicó del lado que no la necesitaba.

Es una variante del modo de falla de [[vault/06_Quality_Testing/Bug_Register#BUG-026]] y de BUG-012: el
artefacto de prueba y el artefacto real dejan de compartir origen, y la divergencia no produce
error, sólo números distintos.

### Cómo se detectó

El PR #127 falló `test_agrega_igual_traiga_o_no_cve_mun_el_contrato` —la invariante que Héctor
escribió en el PR #124— con 230 filas contra 315. Investigando esa diferencia se agregó a
`generar_fixture_dim.generar()` una guarda de coherencia entre la entidad que codifica el CCT y la
que declara `cve_mun`. La guarda reventó en la primera corrida:

```
ValueError: 09DCT0000G: `cve_mun` '9001' contradice la entidad '09' del CCT.
```

El defecto llevaba ahí desde que el contrato incorporó la columna. La guarda tardó una corrida en
encontrarlo.

### Fix

`src/modelos/entrenar_ml01.py`, en `cargar_features()`:

```python
df = (
    pd.read_parquet(ruta)
    if ruta.suffix == ".parquet"
    else pd.read_csv(ruta, dtype={"cve_mun": str})
)
```

Parquet no necesita el tratamiento: conserva el tipo declarado en el esquema.

### Test de regresión

**La guarda es la regresión.** `generar_fixture_dim.generar()` falla si `cve_mun` no empieza con la
entidad que codifica el CCT, o si las features traen más de un municipio por CCT. No es una prueba
que alguien deba acordarse de correr: es una condición que el generador no puede violar.

### Lección

Una hipótesis correcta escrita en un comentario no protege nada si la corrección se aplica del lado
equivocado. Cuando alguien documente un riesgo de tipos, la pregunta siguiente es **cuántos lectores
tiene ese archivo**, no si el test pasa.

## BUG-031 — KPI-02 muestra −54.5 % donde el valor real es −0.19 %

Encontrado por Marina García del Buey el 2026-08-29, auditando sus propias métricas antes de la mesa
de ADR-007. **El defecto es mío**, no de quien lo implementó.

### Descripción

La tarjeta «Variación de matrícula» (KPI-02) aparece en DB-03 y DB-04. Su métrica es:

```
SUM(variacion_matricula * matricula_total) / NULLIF(SUM(matricula_total), 0)     formato: porcentaje_1
```

Eso es un promedio de `variacion_matricula` ponderado por matrícula, y solo tiene sentido si
`variacion_matricula` ya es una razón. **No lo es.** `fact_escuela_ciclo.sql:49` la produce como
`matricula_total - matricula_ciclo_anterior`: alumnos absolutos, rango observado −24 a 24. El
promedio ponderado da −0.545 «alumnos», y `porcentaje_1` lo multiplica por 100 al renderizar.

Verificado contra Postgres:

| | |
|---|---|
| Matrícula del ciclo | 32 312 |
| Matrícula del ciclo anterior | 32 374 |
| Variación real | **−0.19 %** |
| Lo que pintan DB-03 y DB-04 | **−54.5 %** |

Factor de error: 287. No es una degradación sutil: el tablero afirma que las escuelas perdieron más
de la mitad de su matrícula en un ciclo.

### Alcance real: seis tableros, no dos

Encontrado al buscar referencias colgantes después de corregir DB-03 y DB-04. **El componente
defectuoso se reutilizó en toda la Célula 2.** Expresión idéntica, formato de porcentaje idéntico:

| Archivo | Línea | Tableros |
|---|---|---|
| `metrics_db01_db02.yaml` | 74 | DB-01 Ejecutivo |
| `metrics_db01_db02.yaml` | 177 | DB-02 Mapa de riesgo |
| `metrics_db03_db04.yaml` | 70 · 154 | DB-03 · DB-04 |
| `metrics_db06_db09.yaml` | 73 | DB-06 · DB-09 |

Verificado contra Postgres: `gold.cubo_matricula`, que alimenta DB-01 y DB-02, también da
**−54.5 %**. Es el mismo número equivocado en todos.

**Y hay dos pruebas que exigen el defecto como si fuera un requisito:**

```
tests/test_semantic_db01_db02.py:251   assert re.search(r"variacion_x_matricula", sql)
tests/test_semantic_db06_db09.py:268   assert re.search(r"variacion_x_matricula", db06_cubo)
```

Mientras esas aserciones existan, quitar el componente **reprueba CI**. Cualquier corrección tiene
que retirarlas en el mismo cambio. Esos dos archivos son de Manuel Serranía (C2, Tech Lead): no se
tocan desde aquí, se le escalan.

Por eso la severidad sube a **critical**: no es una tarjeta de dos tableros, es la métrica KPI-02 del
catálogo canónico, mal en seis de los diez tableros, y con pruebas que la sostienen.

### Causa raíz

Está en la especificación, no en el código. §4.4 de [[vault/04_UX_Design/Cube_Specs_DB03_DB04]] declaró
`variacion_x_matricula = sum(variacion_matricula * matricula_total)` como componente aditivo del cubo
de DB-04, y Deni Garrido lo implementó exactamente así en `cubo_comparador_municipio.sql`. **La
implementación es fiel; la especificación estaba mal.**

Ese componente carga dos errores a la vez:

1. **Asume una unidad que el contrato nunca declaró.** Es el mismo hueco de BUG-019 y ADR-007, esta
   vez en el frontend en lugar del ML.
2. **Congela la agregación equivocada.** Una razón se calcula como razón de sumas, no como promedio
   ponderado de razones por escuela. Guardar el producto ya ponderado impide corregirlo desde la capa
   semántica: DB-04 **no se puede arreglar sin tocar el cubo**, porque `sum(variacion_matricula)` y la
   matrícula anterior agregada no existen como columnas.

### Por qué la prueba de regresión no lo vio

`test_los_porcentajes_no_se_multiplican_dos_veces` (US-212) busca la cadena `100` en el texto de la
expresión. Esta métrica **nunca tuvo `* 100`**, así que pasó en verde. La prueba detectaba la *forma*
del error que Edgar Coronel encontró en `pct_escuelas_en_riesgo`, no la *clase* de error. Dio
confianza falsa, que es peor que no tener prueba.

Tampoco lo vio la validación de US-212 —«24/24 charts devuelven datos reales»—, porque **«devuelve
datos» no es «devuelve el dato correcto»**.

### Fix

La corrección **no depende de ADR-007**: se expresa solo con matrículas, que son alumnos y lo seguirán
siendo se ratifique lo que se ratifique.

```
SUM(matricula_total) / NULLIF(SUM(matricula_ciclo_anterior), 0) - 1
```

- **DB-03**: aplicable hoy derivando el denominador (`matricula_total - variacion_matricula`), y
  migra a `matricula_ciclo_anterior` cuando C1 la exponga.
- **DB-04**: requiere cambio en el cubo. Se retira la tarjeta mientras tanto — un tablero con una
  métrica menos es defendible; con una métrica falsa, no.
- **§4.4 del contrato**: `suma_matricula_anterior` reemplaza a `variacion_x_matricula`.

**Fuera del alcance de este PR, escalado a C2 (Manuel Serranía):** `metrics_db01_db02.yaml`,
`metrics_db06_db09.yaml` y las dos aserciones de `test_semantic_db01_db02.py` /
`test_semantic_db06_db09.py`. La corrección es la misma expresión y depende del mismo cambio de cubo,
así que conviene que vaya coordinada, no en cinco PR sueltos.

Lo que hace falta de **C1**, cuatro líneas que conviene meter en el mismo PR de la normalización de
ADR-007, porque ya van a tocar esos archivos:

```sql
-- fact_escuela_ciclo.sql:48 — el dato ya existe en el CTE con_anterior, solo se está tirando
        matricula_ciclo_anterior,

-- cubo_escuela_360.sql:25
    f.matricula_ciclo_anterior,

-- cubo_comparador_municipio.sql:29 — sustituye a variacion_x_matricula
        sum(f.matricula_ciclo_anterior) as suma_matricula_anterior,
```
**Actualización (2026-08-31, Diana Alvarez) — C1 implementado.** Rama
`fix/diana-varela-bug031-matricula-anterior`. Al revisar el repo antes de cerrar esta parte, el mismo
patrón (`variacion_x_matricula` = promedio ponderado de una columna que no es razón) apareció también
en `cubo_matricula.sql` (alimenta DB-01/DB-06, ya listados como afectados) y en
`cubo_riesgo_territorial.sql` (alimenta DB-02, también listado) — ninguno de los dos estaba en el
alcance original de tres archivos de este registro. Se corrigieron los cinco: `fact_escuela_ciclo.sql`,
`cubo_escuela_360.sql`, `cubo_comparador_municipio.sql`, `cubo_matricula.sql`,
`cubo_riesgo_territorial.sql`, más el test `cubo_matricula_fact_parity.sql` (columna renombrada) y
`_gold__models.yml` (`matricula_ciclo_anterior` documentada con `not_null`). Verificado con
`dbt run --full-refresh` + `dbt test` completos sobre Postgres real: los 5 modelos reconstruyen limpio
(148/90/90/90/90 filas), `cubo_matricula_fact_parity` y
`not_null_fact_escuela_ciclo_matricula_ciclo_anterior` pasan. Los 13 errores restantes del run son
preexistentes y no relacionados: 8 ya documentados (gaps DS-06/CONAGUA y DS-07/CONEVAL) y 2 nuevos
diagnosticados en esta verificación (`cubo_recomendaciones_kpi11_parity`,
`gold_ml_runtime_recomendaciones_fact_relationship`) — ninguno de los dos referencia columnas de
matrícula; ambos vienen del filtro preexistente `where matricula_ciclo_anterior is not null` en
`fact_escuela_ciclo.sql` (excluye el primer ciclo observado de cada cct) frente a recomendaciones de
ML-02 emitidas para ese primer ciclo, confirmado sin cambios vía `git diff main` (el fix es puramente
aditivo, no toca ese filtro ni ningún JOIN). Sigue pendiente C2 (ver arriba).

### Cierre — 2026-09-03 (verificado por Marina García del Buey)

**El bug queda `fixed`.** La parte de C2 que este registro daba por pendiente ya estaba hecha
desde el **31 de agosto**, y la hizo **Luis Téllez** (`f013b20`, `b74a700`), no Manuel Serranía
como decía la asignación. El registro llevaba tres días describiendo un pendiente inexistente.

Lo pendiente eran tres cosas y las tres están:

| Pendiente declarado | Estado verificado |
|---|---|
| Migrar `metrics_db01_db02.yaml` a razón de sumas | ✅ `SUM(matricula_total) / NULLIF(SUM(suma_matricula_anterior), 0) - 1` |
| Migrar `metrics_db03_db04.yaml` y `metrics_db06_db09.yaml` | ✅ misma fórmula en ambos |
| Retirar `variacion_x_matricula` y sus dos aserciones | ✅ cero apariciones fuera de comentarios; las aserciones quedaron **invertidas** (exigen `suma_matricula_anterior`, rechazan que `variacion_x_matricula` reaparezca) |

**Verificación contra datos, no contra el código.** El reporte original decía −54.5 % donde el
valor real es −0.19 %. Hoy, con la estrella reconstruida desde los fixtures del repo, KPI-02 da
el mismo número desde **cinco** caminos independientes:

| Origen | KPI-02 |
|---|---|
| `gold.fact_escuela_ciclo` (fuente de verdad) | **−0.192 %** |
| `gold.cubo_matricula` → DB-01, DB-06 | **−0.192 %** |
| `gold.cubo_riesgo_territorial` → DB-02 | **−0.192 %** |
| `gold.cubo_escuela_360` → DB-03 | **−0.192 %** |
| `gold.cubo_comparador_municipio` → DB-04 | **−0.192 %** |

Sobre los mismos 32 312 / 32 374 alumnos del reporte original. Los seis tableros que el bug
afectaba quedan coherentes entre sí y con la fuente.

> **Lo que sobrevive como aprendizaje**, y no lo cierra este bug: el defecto nació en la
> **especificación** (§4.4 del contrato de DB-03/DB-04), no en la implementación. Deni Garrido
> implementó fielmente lo que estaba escrito. La regla que quedó en §4.4 —un componente aditivo
> es una suma simple, nunca un producto ponderado— es el arreglo de fondo.

### Test de regresión

`test_una_metrica_de_porcentaje_no_multiplica_dos_medidas`: una métrica con formato de porcentaje no
puede multiplicar dos columnas de medida dentro de un agregado. Ese producto es la firma del defecto
—delata que se está promediando una razón que no es razón— y es verificable sin base de datos. Se
conserva la prueba del `* 100`.

## BUG-033 — «Update Project Graph» falla en cada merge por push directo a `main`

| | |
|---|---|
| **Severidad** | low — no bloquea merges (no es required check); deja rojo cada run y el grafo desactualizado |
| **Estado** | `fixed` |
| **Detectado** | 2026-08-31, revisando por qué todos los merges recientes marcan un check en rojo |
| **Owner** | **Célula 5** (`.github/workflows/`) — Luis Téllez |
| **traces_up** | REQ-007 |

### Qué pasa

`.github/workflows/update-project-graph.yml` corre en cada `push` a `main` que toque
`src/`, `dbt/`, `dags/` o `vault/03_Architecture/`. Su último paso regeneraba el grafo y lo subía a `main`:

```
git add graphify-out/graph.json graphify-out/GRAPH_REPORT.md
git commit -m "docs: update project graph [skip ci]"
git push
```

La branch protection de `main` rechaza el push (log del run `33470181062`):

```
remote: error: GH013: Repository rule violations found for refs/heads/main
- Changes must be made through a pull request.
- 2 of 2 required status checks are expected.
! [remote rejected] main -> main (push declined due to repository rule violations)
```

### Causa raíz

El workflow presupone que puede escribir a `main` con el `GITHUB_TOKEN`, pero las repository rules
exigen **PR + 1 aprobación de code owner** (`* @edgarcoroneln`, DEC-003) y 2 status checks. Un push
directo del bot es exactamente lo que esas reglas prohíben (regla 5 del vault). Confirmado: **no
existe ni un commit del bot** en el historial — el auto-refresh nunca funcionó desde que se activó;
el grafo versionado se actualizó siempre a mano (último cambio: `86fc37c`, 25-ago, en un commit de
feature humano).

### Por qué no se resuelve dándole push al bot

Lograr un push realmente automático exigiría **debilitar la branch protection** (agregar el bot o un
PAT/GitHub App a la bypass-list del ruleset) o abrir **un PR-de-bot por cada merge** que solo el PM
—code owner único— podría aprobar y mergear. Ambas requieren decisión de Edgar (regla 7) y tienen
mala relación costo/beneficio para un artefacto derivado que se regenera con dos comandos. Se
descartaron a favor de no escribir a `main` en absoluto.

### Fix

El workflow deja de commitear. Regenera el grafo, valida que no filtre secretos y lo **publica como
artefacto descargable de Actions** (`actions/upload-artifact@v4`, 30 días). Cambios:

- se elimina el paso `git commit`/`git push`;
- `permissions` baja de `contents: write` a `contents: read` (mínimo privilegio: ya solo hace checkout);
- se retira el guard anti-ciclo `if: !contains(... 'update project graph')`, que solo existía para
  no re-disparar el commit del bot que ya no ocurre.

El grafo versionado en `graphify-out/` se sigue actualizando a mano por PR cuando haga falta
(`graphify . --code-only && graphify cluster-only .`). No se toca la lógica de generación.

### Test de regresión

No hay prueba unitaria de workflows. Verificación: disparar el workflow con `workflow_dispatch` sobre
la rama del fix y confirmar que el run **termina en verde** y publica el artefacto `project-graph`
**sin intentar ningún push**. Cierre definitivo: el primer merge a `main` que toque los paths ya no
deja el check en rojo.

### Nota

Los dos checks **requeridos** por `main` son «Calidad de codigo y vault» y «Generar y validar
tablero PM» — viven en `ci.yml` y `pm-dashboard.yml`, no en este workflow, así que el cambio no los
altera. («Contrato dbt» corre en cada PR pero **no** es required.)


## BUG-043 — El Registry acepta versiones cuyo modelo nunca llegó

> Reportado por Héctor Morales (2026-09-02) al correr la confirmación de US-311 que pedía el PM.
> → [[vault/15_ML_Models/ML01_Entrenamiento]] · [[vault/_DevLog/2026-09-02-hector-morales-registry-us311]]

### Atribución: qué es nuevo aquí y qué no

**La causa de configuración no es un hallazgo de hoy.** Está descrita en
[[vault/15_ML_Models/ML01_Entrenamiento]] §4 desde el **29 de agosto**, con el fix de
`--serve-artifacts` ya probado. Lo que faltaba —y es lo que abre este bug— son dos cosas:

1. Que `mlflow.register_model()` **crea la versión aunque el artefacto haya fallado**, dejándola
   `READY` en el Registry. El fallo de escritura es ruidoso; la versión fantasma que deja atrás, no.
2. Que por eso `verificar_modelos_registrados()` daba **verde durante 15 días** sobre un modelo que
   nadie podía cargar, y con ese verde se dio **AC-003.4 por cumplido**.

Dicho de otro modo: el 29-ago se supo que el servidor no guardaba modelos, y aun así el tablero de
verificación siguió diciendo que sí había modelos. Ese es el defecto que se registra.

### Qué pasa

El servicio `mlflow` de `docker-compose.yml` arranca así:

```
mlflow server --backend-store-uri ${MLFLOW_BACKEND_STORE_URI}
              --default-artifact-root ${MLFLOW_ARTIFACT_ROOT}   # = /mlflow/artifacts
```

`/mlflow/artifacts` existe **dentro del contenedor**. MLflow no lo trata como "una ruta del
servidor": se la entrega al cliente para que escriba ahí **directamente**. Un cliente en macOS o en
el CI intenta entonces crear `/mlflow` en la raíz de su propio disco.

Las dos capas se comportan distinto y por eso el fallo es tan silencioso:

| Qué | Por dónde viaja | Resultado |
|---|---|---|
| Parámetros, métricas, tags | API REST → Postgres | ✅ se guardan bien |
| Modelo (artefacto) | sistema de archivos del **cliente** | ❌ `Read-only file system: '/mlflow'` |
| Fila del Model Registry | API REST → Postgres | ⚠️ **se crea igual**, y queda `READY` |

Esa tercera fila es el defecto real. `mlflow.register_model()` no comprueba que el artefacto exista,
así que deja una versión que se ve sana y no se puede usar.

### Por qué el verde sobrevivió 15 días al diagnóstico

`verificar_modelos_registrados()` preguntaba `search_model_versions(...)` y daba verde si la fila
existía. Nunca intentó traer el modelo de vuelta. Con eso, `ML01_RegresionMatricula` v1 —creada el
18-ago, el día del fix de versiones de PR #45— pasó por buena hasta hoy:

```
$ python -m src.modelos.verificar_registry --modelo ML01_RegresionMatricula
ML01_RegresionMatricula: versión 1          # ✅ aparentemente correcto

$ mlflow.sklearn.load_model("models:/ML01_RegresionMatricula/1")
MlflowException: No such artifact: 'MLmodel'  # ❌ la realidad
```

**AC-003.4 pide que el modelo *llegue* al registry.** Una fila no prueba eso; traerlo de vuelta sí.

### El arreglo, en dos partes

**C3 (hecho).** `verificar_artefactos_descargables()` carga cada versión con `mlflow.pyfunc` —la
misma ruta que usa la API de C4 para servir inferencia— y reprueba nombrando el modelo, la versión y
la causa probable. `verificar_registry` la ejecuta por defecto; `--sin-artefacto` conserva la
verificación débil y **lo dice en el reporte**, para que nadie la confunda con la fuerte.

**C5 (pendiente).** En el `command:` del servicio `mlflow`:

```
mlflow server --backend-store-uri ${MLFLOW_BACKEND_STORE_URI}
              --serve-artifacts --artifacts-destination /mlflow/artifacts
              --host 0.0.0.0 --port 5000
```

Con `--serve-artifacts` el servidor **proxya** los artefactos por HTTP y el cliente ya no toca
rutas del contenedor. Verificado en local con un override fuera del repo: ML-01 registró la
**versión 2**, y esa versión carga y predice desde un cliente limpio.

### Secuela: las versiones ya registradas

Un experimento guarda su `artifact_location` **al crearse** y no se recalcula. `ML-01-regresion-matricula`
(experimento 1) quedó fijado a `/mlflow/artifacts/1`, así que **seguirá roto para escrituras nuevas
aunque el servidor se arregle**. Al aplicar el fix de C5 hay que crear el experimento de nuevo (o
renombrarlo) y volver a registrar los tres modelos. La verificación de arriba lo detecta.

### Test de regresión

`tests/test_mlflow_utils.py::test_artefacto_ausente_reprueba_aunque_la_version_exista` reproduce el
estado exacto de v1 —fila presente, artefacto ausente— y exige que repruebe.

## BUG-013 — Corrección: la causa que publiqué el 2-sep era equivocada

> Escrito por Héctor Morales el 2026-09-02 y **corregido por él mismo el 2026-09-03**.
> Se deja el error a la vista en vez de borrarlo, porque alguien pudo haberlo leído.

### Lo que afirmé el 2-sep, y es falso

Afirmé que `gold.features_escuela` salía con un solo ciclo porque `features_escuela.sql` §42 arma
su base desde `{{ ref('matricula') }}` y no desde `matricula_historica`, y propuse a C1 cambiar ese
`ref`. **Eso era incorrecto y la propuesta habría sido trabajo inútil.**

### Qué pasó de verdad

No cargué los **tres** fixtures de Formato 911 en `bronze.formato911_2024_2025`, sólo dos. Faltaba
`bronze_formato911_serie_historica_sample.csv` —justamente el que BUG-026 creó para dar grano
escuela multi-ciclo—, que aporta 2021-2022 y 2022-2023:

| Fixture | Ciclos que aporta |
|---|---|
| `bronze_formato911_sample` | 2023-2024, 2024-2025 |
| `bronze_formato911_ciclo_anterior_sample` | 2024-2025 |
| `bronze_formato911_serie_historica_sample` | **2021-2022, 2022-2023** ← el que faltaba |

Con los tres cargados y `dbt run --full-refresh`, Gold sale así:

```
gold.fact_escuela_ciclo   145 filas
gold.features_escuela     145 filas · 3 ciclos (2022-2023: 60, 2023-2024: 30, 2024-2025: 55)
```

Las mismas 145 filas y los mismos 3 ciclos que reportó Luis Téllez el 2-sep. **`features_escuela`
nunca estuvo mal**: mi carga de Bronze estaba incompleta, y le atribuí a un modelo de C1 un defecto
que era mío.

### Consecuencia

`--desde-gold` **sí funciona** con los fixtures del repo. Ya no hay nada que pedirle a C1 por este
motivo, y **la parte de BUG-013 que bloqueaba a US-313 queda cerrada** — lo que faltaba después era
BUG-041, ya corregido.

### La lección, que es la parte útil

BUG-012 sigue abierto: no hay runbook del pipeline local. Reconstruí los pasos leyendo el DevLog de
Marina del 27-ago, que dice *«cargar DOS fixtures de Formato 911 en la MISMA tabla»* — cierto el
27-ago, incompleto después de que BUG-026 agregara el tercero. **Un runbook que vive en un DevLog no
se actualiza cuando cambia el repo.** Ese es el costo real de BUG-012, y me lo cobró a mí.


## BUG-043 — Corrección del diagnóstico y fix verificado en dos partes

> Héctor Morales, 2026-09-03. Corrige lo que yo mismo escribí el 2-sep.

### Lo que dije mal

Escribí que el servidor «no corre con `--serve-artifacts`» y que ése era el arreglo. **Falso.** En
MLflow 3.15.1 esa opción viene activa por defecto — lo dice su propio `--help`:

```
--serve-artifacts / --no-serve-artifacts   ...   Default: True
```

Pedirle a C5 que agregara ese flag habría sido un no-op. La causa real es la **raíz de artefactos**.

### Las dos causas, verificadas por separado

**1. `--default-artifact-root` apunta a disco, no al proxy.** El servidor entrega esa raíz al
cliente *tal cual*; si es `/mlflow/artifacts` —que sólo existe dentro del contenedor— el cliente
intenta escribirla en su propio disco. Se corrige con `MLFLOW_ARTIFACT_ROOT=mlflow-artifacts:/`
en el `.env`, **sin tocar `docker-compose.yml`**. Con sólo esto, los tres modelos registran y cargan:

```
ML01_RegresionMatricula: versión 3 — carga verificada ✅
ML02_DriverClasificador: versión 1 — carga verificada ✅
ML03_ClusteringEscuelas: versión 1 — carga verificada ✅
```

**2. Sin `--artifacts-destination`, el registry es efímero.** Con la raíz corregida los artefactos
van al `./mlartifacts` del contenedor —**no** al volumen `faro-mlflow-artifacts`, montado en
`/mlflow/artifacts`—. Probado:

| Configuración | Tras `docker compose up --force-recreate` |
|---|---|
| sólo la raíz corregida | ❌ **los tres modelos quedan `READY` sin artefacto** |
| raíz + `--artifacts-destination /mlflow/artifacts` | ✅ los tres siguen cargando |

En local eso cuesta re-registrar. **En Cloud Run el contenedor se recrea de rutina**, así que sin la
segunda parte el registry de la demo se vacía solo.

### Reparto

- **C3 ✅ hecho:** la guarda que detecta el estado, y `.env.example` con la raíz correcta.
- **C5 ⬜ pendiente:** una línea en el `command:` del servicio `mlflow`:

```
--artifacts-destination /mlflow/artifacts
```

Para Cloud Run conviene que ese destino sea un bucket de GCS, no una ruta local; queda a criterio de
Célula 5.

## BUG-044 — `/escuelas` y `/kpis` sumaban todos los ciclos a la vez sin `ciclo` explícito

Encontrado el 2026-09-03 por **Karla Monter (C4)**, validando el cierre de US-411 contra la URL
pública una vez que BUG-020 quedó curado (`/escuelas` y `/kpis` ya respondían 200, pero con datos
inconsistentes).

**Reproducir contra prod (antes del fix):**
```
GET /api/v1/escuelas?cve_ent=09              -> total: 19456
GET /api/v1/escuelas?cve_ent=09&ciclo=2024-2025 -> total: 6378   (razón ≈ 3)
GET /api/v1/kpis                             -> matricula_total: 20638574
GET /api/v1/kpis?cve_ent=09                  -> matricula_total: 3920977
```

`gold.fact_escuela_ciclo` materializa ~3 ciclos. `listar_escuelas`, `obtener_kpis` y
`obtener_escuela` (`src/api/repositorio_gold.py`) solo agregaban `WHERE fact.id_ciclo = :ciclo`
cuando el caller lo mandaba explícito; si no, la consulta corría sin esa condición y el `JOIN`
contra `fact` (grano escuela × ciclo) traía una fila por ciclo por escuela. `EscuelaOut` no expone
`id_ciclo`, así que del lado del cliente esas filas son indistinguibles — parecen escuelas
duplicadas con datos distintos. En `/kpis`, el mismo hueco suma `matricula_total` de los ~3 ciclos
de una vez, triplicando la cifra.

**No es un problema de `SCOPE_ENTIDADES`:** los ~20.6M sin filtro de entidad son las 4 entidades del
alcance sumadas 3 veces (≈7M reales × 3), no datos de otras entidades — confirmado comparando
`cve_ent=09` con y sin `ciclo`.

**Fix:** `RepositorioGoldPostgres._ciclo_mas_reciente()` (`SELECT MAX(id_ciclo)`) se usa como
default en los tres métodos cuando `ciclo` es `None`. `id_ciclo` tiene formato `AAAA-AAAA`, así que
el orden lexicográfico coincide con el cronológico. `tests/fixtures_gold.py::RepositorioGoldFake`
implementa el mismo default (antes solo tenía un `id_ciclo` en todo el fixture, por lo que la
suite rápida nunca pudo ejercitar este defecto — se agregó una segunda fila con el mismo `cct`
en un ciclo distinto para que las pruebas de regresión lo cubran de verdad).

**Estado:** corregido en `dev/karla-monter`, con pruebas de regresión (ver tabla arriba). Pendiente
verificar contra la URL pública tras el próximo deploy — el fix vive en código, no en producción
todavía.

---

## BUG-045 — CONEVAL (DS-07) no es reproducible desde el repositorio

| | |
|---|---|
| **Severidad** | high — bloquea la construcción de Gold completa a cualquiera sin los Excel reales |
| **Estado** | `fixed` — 2026-09-04, por Diana Alvarez Varela (Célula 1) |
| **Owner** | **Célula 1** — Diana Alvarez Varela / Deni Garrido Fragoso |
| **Detectado** | 2026-09-03, por Marina García del Buey, al reconstruir su ambiente local desde cero |
| **Validado** | 2026-09-04, por Luis Téllez Domínguez, en revisión de solo lectura, claim por claim |
| **traces_up** | US-112 / US-113 / REQ-001 / REQ-002 / DS-07 |

### Qué pasa

`dbt/models/silver/rezago_municipio.sql` consume el esquema del **extracto oficial** de
CONEVAL, cuyas columnas de negocio vienen con nombre hasheado
(`_nombre_fisico(x) = "c_" + sha1(x)[:12]`, ver `src/ingesta/cargar_bronze_coneval_real.py`).
El modelo exige literalmente:

```
c_b9548dbd414b  c_deef5d1bd71a  c_9b370f449788  c_9e8609cad84d  c_5d0523b1d4a3
c_91fd46c9babe  c_9bd1a7aa7fca  c_764f3baf1395  c_1a3c72ae6dd1  _periodo_medicion
```

Revirtiendo los hashes, cuatro de ellos son los encabezados del Excel oficial:

| Hash | Columna original |
|---|---|
| `c_9b370f449788` | `Entidad federativa` |
| `c_9e8609cad84d` | `Municipio` |
| `c_5d0523b1d4a3` | `Índice de rezago social` |
| `c_91fd46c9babe` | `Grado de rezago social` |

El **único** fixture de CONEVAL del repositorio, `tests/fixtures/bronze_coneval_sample.csv`,
emite otro esquema por completo:

```
cve_mun, entidad, municipio, indice_rezago_social, grado_rezago, pobreza_pct
```

No es un descuido puntual: su generador
(`tests/fixtures/generate_bronze_drivers_fixtures.py::generar_coneval`) lo produce así
**contra el contrato viejo**, y su propio docstring lo cita — *"Data_Model.md §6:
nombre_entidad/nombre_municipio vienen de DS-07"*. Es anterior a la migración de Deni al
extracto real. **Ningún CSV del repositorio tiene columnas `c_…`.**

### Por qué es grave

La cadena se rompe entera, no en una hoja:

```
sin los dos Excel reales de CONEVAL
  → no hay bronze.coneval_irs_2020 / bronze.coneval_pobreza_2020
    → silver.rezago_municipio revienta: column "c_b9548dbd414b" does not exist
      → no hay gold.dim_municipio
        → no se materializa NINGÚN cubo (todos dependen de dim_municipio)
          → no funciona NINGÚN tablero
```

Reproducido corriéndolo, no deducido.

**CI no lo atrapa.** El job `dbt-contract` de `ci.yml` corre `dbt parse`, que renderiza el
manifest sin ejecutar Silver contra datos: un fixture incompatible pasa el gate en verde.

### Precisión sobre `coneval_v2` (corrige un punto de la validación)

La validación de Luis marcó como *inferido* que el fixture carga en `coneval_v2`, tomándolo
de una referencia del propio Bug_Register. **Verificado hoy: ese var ya no existe.**
`dbt/models/sources.yml` fue migrado a dos vars distintos —
`bronze_coneval_irs_identifier` → `coneval_irs_2020` y `bronze_coneval_pobreza_identifier`
→ `coneval_pobreza_2020` — y **ningún source de dbt apunta a `coneval_v2`**.

Eso hace el hallazgo **más agudo, no menos**: el fixture no solo tiene el esquema
equivocado, es que **ya no tiene destino alguno en el dbt actual**. Está huérfano.
`src/ingesta/cargar_bronze_fixture.py` todavía acepta `--esquema coneval` y lo carga sin
protestar, así que quien lo use cree haber ingerido DS-07 y no ingirió nada que el pipeline
lea. `vault/14_Data_Sources/DS-07_CONEVAL_Rezago_Social.md` §11 ya declara que
*"coneval_v2 y coneval_test no son fuentes válidas"*.

### Relación con BLOCK-004 — es un bloqueo distinto

**BLOCK-004 está `resolved`**, pero su solución automatizada
(`src/ingesta/reproducir_bronze_real.py`, "el Camino A en un solo comando") cubre
**solo DS-02 (catálogo CCT) y DS-01 (Formato 911 histórico)**. Verificado: el script no
menciona CONEVAL ni DS-07 en ninguna línea, y su propio docstring enumera su alcance.

Es decir: el comando que cerró BLOCK-004 **no reproduce DS-07**. Este hueco es aparte y
sigue abierto.

### Mitigación en uso hoy (no es el arreglo)

Marina creó las dos tablas Bronze **vacías** con la forma correcta, solo en su base local,
para que `rezago_municipio` compile con 0 filas y `dim_municipio` sobreviva por su
`LEFT JOIN`. Resultado: **D1 sale `SIN_DATO` en 145/145 escuelas** — que es lo honesto —
en vez de un número inventado. No toca ningún archivo del repositorio y no invade a C1.

Efecto colateral medible, para que no sorprenda: con D1 fuera, ML-01 entrena con **4 de 6
drivers** y su MAE cambia (0.0818 contra 0.0844 de la corrida de Héctor, que sí tenía D1).

### Arreglo propuesto — alcance de Célula 1

Dos caminos, cualquiera resuelve:

1. **Publicar un fixture** `tests/fixtures/bronze_coneval_irs_2020_sample.csv` (+ el de
   pobreza) con las columnas `c_…` que el modelo espera.
2. **Extender el generador** `generate_bronze_drivers_fixtures.py::generar_coneval` para
   que emita ese esquema en vez del viejo.

Hay precedente directo y reciente: existen **cuatro** generadores de Formato 911
(`generate_bronze_formato911_*.py`), y uno de ellos —el de la serie histórica— nació
justo para cerrar un hueco equivalente en BUG-026.

### Arreglo aplicado (2026-09-04, Célula 1 — Diana Alvarez)

Se tomó el camino 2 de los dos propuestos arriba: **extender el generador**, no publicar
fixtures sueltos a mano, para quedar consistente con el patrón que ya usan las demás
fuentes (`ESQUEMAS` en `src/ingesta/cargar_bronze_fixture.py`).

**Evidencia usada — no se adivinó ningún hash.** Los manifiestos reales generados por la
propia carga DS-07 de ayer (`data/bronze/coneval/manifests/ds07_postgres_columns_irs_2020.json`
y `..._pobreza_2020.json`, artefactos locales, no versionados) dan el mapeo completo
hash → encabezado original — no solo los 4 que ya estaban documentados arriba:

| Hash | Columna original | Tabla |
|---|---|---|
| `c_b9548dbd414b` | `Clave entidad` | irs |
| `c_deef5d1bd71a` | `Clave municipio` | irs |
| `c_9b370f449788` | `Entidad federativa` | irs / pobreza |
| `c_9e8609cad84d` | `Municipio` | irs / pobreza |
| `c_5d0523b1d4a3` | `Índice de rezago social` | irs |
| `c_91fd46c9babe` | `Grado de rezago social` | irs |
| `c_9bd1a7aa7fca` | `Clave de entidad` | pobreza |
| `c_764f3baf1395` | `Clave de municipio` | pobreza |
| `c_1a3c72ae6dd1` | `Pobreza \| Porcentaje 2020` | pobreza |

**Cambios de código:**

1. `src/ingesta/cargar_bronze_fixture.py` — se quitó el `DDL_BRONZE_CONEVAL` /
   `COLUMNAS_CONEVAL` viejos (esquema de una sola tabla, ya huérfano) y la clave
   `"coneval"` de `ESQUEMAS`. Se agregaron `DDL_BRONZE_CONEVAL_IRS` /
   `COLUMNAS_CONEVAL_IRS` y `DDL_BRONZE_CONEVAL_POBREZA` / `COLUMNAS_CONEVAL_POBREZA`
   (6 y 5 columnas de negocio hasheadas respectivamente, más `_periodo_medicion`,
   `_ingested_at`, `_source`, `_source_url`), y las claves `"coneval_irs"` /
   `"coneval_pobreza"` en `ESQUEMAS`, con conflicto de unicidad en
   `(_source, _ingested_at, c_b9548dbd414b, c_deef5d1bd71a)` e
   `(_source, _ingested_at, c_9bd1a7aa7fca, c_764f3baf1395)` respectivamente — mismo
   patrón que las demás fuentes de este archivo, sin tocar
   `src/ingesta/cargar_bronze_coneval_real.py` (el loader de producción, que ya emite
   este esquema correctamente y no tenía el bug).
2. `tests/fixtures/generate_bronze_drivers_fixtures.py::generar_coneval` — reescrito
   para emitir **dos** archivos (`bronze_coneval_irs_sample.csv`,
   `bronze_coneval_pobreza_sample.csv`) con el esquema `c_…` real en vez de uno solo
   con el esquema viejo. Reutiliza los mismos 12 municipios sintéticos que ya usan los
   generadores hermanos (vía `_leer_ccts_y_municipios()`), incluida una fila
   `SIN_DATO` para ejercitar cobertura parcial.
3. Se corrió el generador y se borró `tests/fixtures/bronze_coneval_sample.csv`
   (el fixture huérfano que causaba el bug).

**Verificado sin Postgres** (`device_bash` no tiene Docker ni alcanza `127.0.0.1:5432`,
así que esto se validó a nivel de esquema, no de base de datos real): las dos CSV nuevas,
leídas con `pd.read_csv(..., dtype=str, keep_default_na=False)`, no tienen columnas
faltantes contra `COLUMNAS_CONEVAL_IRS` / `COLUMNAS_CONEVAL_POBREZA` — 12 filas cada una,
1 fila `SIN_DATO`. `tests/test_cargar_bronze_fixture_conteo.py` (único test existente que
toca este módulo) solo ejercita `esquema="cct"` y no se ve afectado.

**Verificación real contra Postgres (Diana, 2026-09-04, misma tarde).** `pytest tests/ -q`
→ **884 passed, 7 skipped**, nada roto por el fix. `dbt run --select rezago_municipio` →
**éxito, `SELECT 2469`** contra las tablas reales `bronze.coneval_irs_2020` /
`coneval_pobreza_2020` que Diana ya tenía cargadas de su propia corrida real de DS-07 del
mismo día. `dbt test --select rezago_municipio` → **6 de 7 en verde** (los 3
`accepted_values`/`not_null`/`valid_rezago_municipio` propios del modelo, todos `PASS`); el
único `ERROR` es `cubo_pipeline_rows_parity` por `relation "bronze.conagua_presas" does not
exist` — **ajeno a este bug**, es DS-06/CONAGUA (Emilio Galnares), no CONEVAL. Esto prueba
el mapeo hash→columna de punta a punta contra datos reales, no solo contra los manifiestos.

**Hallazgo real durante la verificación, ya corregido.** Cargar el fixture con
`cargar_bronze_fixture.py --esquema coneval_irs --tabla coneval_irs_2020` (incluyendo
`--fixture`, que las instrucciones iniciales omitieron) reventó con
`psycopg2.errors.InvalidColumnReference: no unique or exclusion constraint matching the ON
CONFLICT specification`. Causa real: **la tabla `bronze.coneval_irs_2020` de Diana ya
existía**, creada antes por el loader de producción (`cargar_bronze_coneval_real.py`), que
es idempotente por snapshot (`_source`, `_ingested_at`) y **no** define ningún `UNIQUE` —
`CREATE TABLE IF NOT EXISTS` de este script fue entonces un no-op contra una tabla sin la
restricción que el `ON CONFLICT` necesita. No es un defecto del mapeo de columnas (que
`dbt run` ya probó correcto) ni algo que corresponda "arreglar" insertando de todos modos:
mezclar filas sintéticas de fixture en una tabla con datos reales sería justo el tipo de
inconsistencia silenciosa que CLAUDE.md pide evitar. Arreglo: `cargar_fixture()` ahora
detecta ese error específico, hace `rollback()` (no toca ni una fila de la tabla real) y
levanta un `RuntimeError` explicando la causa y sugiriendo cargar el fixture bajo un
`--tabla` nuevo si de verdad se necesita ahí — en vez del traceback crudo de psycopg2. Este
camino aplica solo quien ya tiene datos reales cargados (como Diana); en un ambiente
limpio (CI, o alguien reconstruyendo desde cero como hizo Marina) la tabla no existe de
antemano y el flujo normal de `CREATE TABLE` + `INSERT ON CONFLICT` corre sin tocar este
caso — ese es justo el escenario que este fix de BUG-045 existe para resolver.

### Guarda propuesta (no existe hoy)

Nada en CI falla cuando un fixture y su modelo divergen. Valdría una prueba que, para cada
`source` de `dbt/models/sources.yml`, compruebe que **existe algún fixture cuyo encabezado
contenga las columnas que el modelo Silver correspondiente referencia**. Cubriría la clase
de error —fixture desalineado del contrato— y no solo esta instancia. Se propone, no se
implementa aquí: `dbt/**` y `tests/fixtures/**` de C1 son alcance de Célula 1.

## BUG-047 — Filtro de ciclo sin `valor_por_defecto` infla las métricas en 7 dashboards

Reportado como **espejo de BUG-044 en los tableros**. BUG-044 (C4, Karla Monter) fija el
ciclo por defecto en la API; pero los dashboards de Superset **no pasan por la API** — leen
la base directo —, así que el fix de BUG-044 no los cubre. Detonado por el aviso de **Luis
Téllez (2026-09-04)**: en producción `/api/v1/kpis` pintaba matrícula **20.6M** contra **6.7M**
reales. Allá se arregló en la API; los tableros necesitaban su propio arreglo.

### El defecto

Los filtros globales de ciclo existían desde US-212 pero **sin valor inicial**. Al abrir un
tablero nadie ha filtrado todavía, así que toda métrica agregada sobre `gold.fact_escuela_ciclo`
(que materializa ~3 ciclos) sumaba los tres a la vez — la matrícula quedaba ≈3× inflada, sin
ningún error visible en pantalla. Marinas lo detectó en DB-03 (KPI-15) y DB-04 (KPI-01):
**32 312 donde el ciclo tiene 11 828**, 2.7×.

El mismo patrón vivía en los otros 7 tableros que declaran `id_ciclo`. El dato numérico
concreto por dashboard no se revalidó uno a uno (la inflación es el mismo mecanismo en todos),
pero DB-01/DB-02 ya están cubiertos por el AC-002.2 y el E2E de Playwright, que validan el
filtro ciclo sobre todo el tablero.

### El arreglo (aditivo y opt-in)

Clave opcional `valor_por_defecto: "2024-2025"` en el YAML de cada dashboard, traducida al
`defaultDataMask` de Superset por `sync_semantic_layer.py` (mecanismo aditivo en la fila
`defaultDataMask`). Sin la clave, el tablero no cambia — compatibilidad hacia atrás exigida
por prueba. Los tableros de Manuel, Monserrat y Oscar no se ven afectados.

En **`src/frontend/pages/1_Dashboards.py`**, el selectbox de ciclo fija
`index=len(CICLOS)-1` (2024-2025) por defecto, idéntico al `defaultDataMask`.

Cobertura por dashboard:

| Dashboard | `valor_por_defecto` | `cct` (index 3) |
|---|---|---|
| DB-01 ejecutivo | ✅ | — |
| DB-02 mapa de riesgo | ✅ | — |
| DB-05 analisis driver | ✅ | — |
| DB-06 predicciones | ✅ | ✅ |
| DB-07 calidad cobertura | ✅ | — |
| DB-08 explorador cubo | ✅ | — |
| DB-09 recomendaciones | ✅ | ✅ |

DB-03/DB-04 ya los cubrió Marina García dentro de US-214a. **DB-10 (monitoreo de pipeline)
no declara `id_ciclo`** y no aplica.

Además, con el mismo PR se destraba a Marina: el filtro `cct` se agrega **al final**
(índice 3) de `filtros_globales` en DB-06 y DB-09 — los IDs de filtro se generan por
posición, insertar en medio rompería la navegación del drill-down DB-03→DB-06/DB-09 sin
error visible.

### Otros cambios del mismo PR (migración Streamlit)

- `st.components.v1.html` → `st.html()` en `1_Dashboards.py` (deprecado a remover tras
  2026-06-01). Se mantuvo `st.html()` (no deprecado) en lugar de `st.iframe` para conservar
  borde/border-radius + `allow=fullscreen`; `st.html()` no acepta `height`/`scrolling`, esos
  parámetros se quitaron (el iframe inline define `height="800"`).
- Fix de caché + transporte: `st.cache_data.clear()` + `_tableros.clear()` en los
  `except SupersetDeshabilitado` / `except SupersetError`, y nuevo `except httpx.HTTPError`.
- `requirements.txt` raíz: `streamlit==1.62.0` — el CI solo instala el `requirements.txt`
  raíz, así que los tests de frontend se saltaban en silencio (hallazgo Marina/Christian).

### Pruebas

`tests/test_frontend_dashboards_streamlit.py` — **2 passed** (el archivo tiene 2 tests). Era uno de
los 3 archivos de frontend que el CI se saltaba en silencio (por no instalar streamlit) y que ahora
corren; además lleva el fix real de la causa raíz del test en secuencia:
AppTest comparte `sys.modules` entre `.run()` y `superset_client.SUPERSET_URL` quedaba
congelada del test previo → "Connection refused". El fixture purga `sys.modules` de
`MODULOS_FRONTEND = ("superset_client", "auth", "1_Dashboards")`.

Guarda de compatibilidad hacia atrás: sin la clave `valor_por_defecto` no se escribe
`defaultDataMask`.

Todo el alcance de C2 de este PR (frontend + capa semántica + sync) pasa en verde:
**226 passed** en los archivos de la célula, incluido `test_frontend_dashboards_streamlit.py`
(2). En ambiente limpio (CI con `requirements.txt` raíz) la suite completa corre sin `failed`
(0). Los 21 `failed` de tests de validación (`great_expectations` — `'project_root_dir' and
'context_root_dir' are conflicting args`, conflicto de versión de la librería) y los 12 módulos
que no colectan por faltar el módulo `limits` (slowapi de `src/api`) son artefactos de este venv
local, no del PR. `vault_lint` limpio.

### Actualización 2026-09-04 (Oscar Quiroz, C2) — resolución dinámica, sin renumerar

Diagnostiqué el mismo defecto de forma independiente (Edgar me pidió revisar mis propios
tiles de "total"), sin ver todavía este PR de Manuel: verifiqué dos veces por Teams su
afirmación de que ya estaba corregido y, en ambas ocasiones, ni `git fetch` ni la metadata
real de Superset mostraban ningún cambio — el fix real llegó a `main` después de esas dos
verificaciones. Registré el hallazgo por mi cuenta como un bug nuevo (`BUG-050`) antes de
sincronizar con `main` y encontrar que ya existía aquí como **BUG-047**; por DEC-013 (un
defecto, un ID — ver el precedente de BUG-041→043 de Héctor Morales) retracto ese número y
consolido toda mi evidencia en esta entrada.

**Mejora aportada, aditiva sobre el mecanismo de Manuel/Marina:** `valor_por_defecto` es un
valor estático — el propio comentario del fix ya lo señala ("al cargar un ciclo nuevo hay
que actualizar este valor a mano"). Agregué a `_filtros_nativos()` una segunda vía,
`default: ultimo_ciclo`, que resuelve el valor **dinámicamente** contra los datos reales
(`ORDER BY id_ciclo DESC LIMIT 1` vía `/api/v1/chart/data`) — nunca hardcodeado. Cuando un
filtro declara ambas claves, la dinámica tiene prioridad y `valor_por_defecto` queda como
respaldo si la resolución dinámica no está disponible (sin red/token). Agregué
`default: ultimo_ciclo` a los 9 dashboards que ya declaraban esa intención en su propio
`metrics_*.yaml` (los 7 de este PR más DB-03/DB-04 de Marina), sin quitar ninguna línea de
`valor_por_defecto` ya existente.

Verificado en vivo, antes/después, en los 9 datasets con métrica de conteo absoluto
(`total_escuelas`/`matricula_total`/`escuelas`, según el dashboard):

| Tablero | Dataset | Métrica | Antes (sin default) | Después (ciclo 2024-2025) |
|---|---|---|---|---|
| DB-01 | `db01_cubo_matricula` | `matricula_total` | 768,569 | 244,571 |
| DB-01 | `db01_driver_dominante` | `escuelas` | 4,263 | 1,397 |
| DB-02 | `db02_cubo_riesgo_territorial` | `matricula_total` | 768,569 | 244,571 |
| DB-03 | `db03_cubo_escuela_360` | `matricula_total` | 768,569 | 244,571 |
| DB-04 | `db04_cubo_comparador_municipio` | `matricula_total` | 768,569 | 244,571 |
| DB-06 | `db06_cubo_predicciones` | `matricula_total` | 768,569 | 244,571 |
| DB-07 | `db07_cubo_completitud` | `total_escuelas` | 25,578 | 8,382 |
| DB-07 | `db07_cubo_completitud` | `escuelas_con_dato` | 5,561 | 1,818 |
| DB-07 | `db07_cubo_completitud` | `escuelas_sin_dato` | 20,017 | 6,564 |
| DB-08 | `db08_cubo_pivot` | `matricula_total` | 4,611,414 | 1,467,426 |
| DB-09 | `db09_cubo_recomendaciones` | `matricula_total` | 768,569 | 244,571 |

DB-05 solo expone métricas de porcentaje sobre este dataset; no se distorsionan porque
numerador y denominador se inflan igual. Por la misma razón, KPI-06 (`% escuelas SIN_DATO`)
de DB-07 se mantuvo correcto (78.3% antes y después) — el error es exclusivo de los
conteos absolutos, confirmando lo que este PR ya documentaba.

Preservé la firma original de `_filtros_nativos(cfg_dashboard, datasets_uuids, ...)` y los
5 tests de `tests/test_filtro_ciclo_por_defecto.py` siguen pasando sin modificarlos — los
parámetros nuevos (`token`, `datasets_by_name`) son opcionales al final, con default `None`.
Pruebas nuevas: `tests/test_filtros_nativos_default_dinamico.py` (5 casos: resolución
dinámica correcta, sin `default:` no cambia nada, sigue a los datos si el ciclo avanza, un
fallo de red no rompe el sync ni pierde el respaldo estático, guardia paramétrica sobre los
10 YAML de tablero). Recapturé mi propia evidencia visual (DB-07) en
`Manual_Usuario_Dashboards.md` v1.3; Manuel/Marina/Monserrat pueden revisar si quieren
recapturar la suya, aunque el número que ya documentaron (`"2024-2025"`) no cambia con mi
fix — solo deja de requerir mantenimiento manual en el próximo ciclo. 872 passed, `vault_lint`
limpio.
