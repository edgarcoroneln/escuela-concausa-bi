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
| BUG-005 | Scripts `.sh` se corrompen a CRLF en checkouts de Windows: `.gitattributes` no tiene regla `*.sh text eol=lf`, así que con `core.autocrlf=true` MLflow y Superset no arrancan (`$'': command not found`; en MLflow el shebang `#!/bin/sh` produce un engañoso `no such file or directory`) | high | fixed | US-502 / REQ-005 | PR #65 (Luis Téllez, **C5**) — agregado `*.sh text eol=lf` a `.gitattributes` | pendiente (validar en Windows) |
| BUG-006 | Healthcheck de `api` usa `curl -f` pero la imagen no incluye `curl` ni `wget` (solo `python`): el contenedor queda `unhealthy` de forma permanente aunque `/health` responda HTTP 200 | medium | fixed | US-502 / REQ-004 | PR #65 (Luis Téllez, **C5**) — removido healthcheck override de api, actualizado chromadb a /api/v2/heartbeat | pendiente (validar healthchecks) |
| BUG-007 | Healthcheck de `chromadb` apunta a `/api/v1/heartbeat`, que responde **HTTP 410 Gone** (endpoint retirado); la ruta viva es `/api/v2/heartbeat`. Además arrastra el mismo problema de `curl` de BUG-006 | medium | fixed | US-502 / REQ-006 | PR #65 (Luis Téllez, **C5**) — actualizado puerto MLflow en documentación (5000 → 5001) | validado |
| BUG-008 | `docker/api.Dockerfile` arranca `src.api.main:app` (el hola mundo de US-501, **3 rutas**) en vez de `src.api.app:app` (la app real del contrato v1, **18 rutas** bajo `/api/v1`): en el contenedor —y en la URL pública si usa este Dockerfile— **US-401, US-402 y US-411 son inalcanzables** | **high** | **fixed** | US-501 / US-411 / REQ-004 / REQ-005 | fix/luis-tellez-bug008-api-dockerfile (Luis Téllez, **C5**, 27-ago) — 1 línea en Dockerfile + redeploy urgente a producción | `tests/test_docker_api_entrypoint.py` (3 pruebas, PR #137): lee el CMD del Dockerfile, importa la app declarada y compara sus rutas contra el esquema OpenAPI de `src.api.app` en vivo |
| BUG-009 | 11 vars de dbt sin valor por default (7 `identifier` de fuentes Bronze + 4 vars de modelo): cualquier `dbt parse`/`build`/`run` falla al renderizar el manifest aunque el modelo probado no use esas fuentes | high | fixed | US-111 | defaults inline en `sources.yml` + bloque `vars:` en `dbt_project.yml` (DEC-011) | `dbt parse` en `ci.yml` (job `dbt-contract`) |
| BUG-010 | `/api/v1/predicciones/*` sigue leyendo `src/api/mock_data.py` en vez de `gold.predicciones` + `gold.recomendaciones`: la verificación **#4 del ensayo E2E** («≥1 modelo sirviendo por API») devolvería un valor fijo, no la predicción de ML-01 | **high** | fixed | US-412 / US-415 / REQ-004 / REQ-003 | `feat/juan-mayen-us415-pydantic-schemas` — `src/api/repositorio_modelos.py` (`RepositorioModelos` sobre Postgres, mismo patrón `Depends` que `RepositorioGold`); `PrediccionOut.cluster` pasa a `StrictInt \| None` (ML-03 sin productor, US-321) · `tests/test_api_contract.py::test_prediccion_combina_ml`, `test_prediccion_cct_sin_fila_404`, `test_prediccion_batch_omite_ccts_sin_fila` (fake en `tests/fixtures_modelos.py`) |
| BUG-011 | `sync_semantic_layer.py` lee YAML/SQL con la codificación del sistema (`read_text()` sin `encoding`): en Windows usa cp1252 y truena con los acentos de cualquier `metrics_*.yaml`; el script solo corre con `PYTHONUTF8=1`. Misma familia que BUG-005 (locale de Windows) | medium | fixed | US-203 / US-212 | `fix/manuel-serrania-bug010-sync-charts-utf8` — `encoding="utf-8"` explícito en las 3 lecturas (`_read_yaml`, `_read_sql`) | pendiente (validar en Windows) |
| BUG-012 | No existe runbook para levantar el pipeline local: `dbt/README.md` es el scaffold por defecto de dbt, no hay `profiles.yml` ni se documenta dónde ponerlo, y **cargar solo `bronze_formato911_sample.csv` deja `gold.fact_escuela_ciclo` en 0 filas** — hay que cargar también `bronze_formato911_ciclo_anterior_sample.csv` en la MISMA tabla para que `lag()` encuentre pares. Nada de esto está escrito. | high | open | US-112 / US-113 / REQ-001 | pendiente (**C1**) — pasos verificados en `_DevLog/2026-08-27-marina-garcia-pipeline-local-us212.md` | pendiente — **asignado a Edgar Coronel (PM) el 29-ago tras 3 días sin dueño en C1.** Los 7 pasos verificados de Marina en `_DevLog/2026-08-27-marina-garcia-pipeline-local-us212.md` se convierten en `dbt/README.md`. Con BUG-026 cerrado el pipeline ya es reproducible desde fixtures, así que el runbook por fin puede escribirse completo y verificarse |
| BUG-013 | `publicar_gold.py` usa por defecto el fixture sintético `tests/fixtures/features_escuela_mock.csv`, no `gold.features_escuela`: publica 80 filas de **ciclo 2023-2024** mientras el hecho real tiene 25 de **2024-2025**. El JOIN por `(cct, id_ciclo)` da cero, así que DB-03 muestra `cobertura_prediccion = SIN_DATO` en el 100% de las escuelas y los bloques de predicción y recomendación (AC-002.4) quedan vacíos. Apuntarlo al Gold real tampoco basta hoy: `features_escuela` tiene un solo ciclo y ML exige partición temporal. | high | **parcial** | US-313 / US-113 / REQ-003 | **C3 ✅** (`a76c748`, Héctor): el hueco era que `publicar_gold.py` no sabía leer de una tabla; `cargar_features_desde_gold()` + `--desde-gold`. **C1 ✅ con datos reales** (Diana, 27-ago): 4 ciclos reales cargados en `bronze.formato911_2024_2025` → estrella completa y 8 cubos, 149/149 tests. **Lo que queda ⬜:** no es reproducible fuera del ambiente de Diana — con los fixtures del repo `features_escuela` sigue saliendo con 1 ciclo, así que **la dueña de DB-03 no puede verificar sus propios bloques ML (AC-002.4)** ni CI ejercitar la ruta. Ver **BUG-026** | verificado en local (Marina, 28-ago): `--desde-gold` → `ValueError: Con 1 ciclos no se puede hacer backtesting… Ciclos disponibles: ['2024-2025']` |
| BUG-014 | `quality_gate.yml` busca el token de casilla sin marcar en **todo el cuerpo del PR** con `grep -q "\[ \]"`, no solo en ítems de lista: basta con **mencionar** esa sintaxis dentro de una explicación —aunque vaya en backticks— para que el check falle. Sumado a que la plantilla oficial trae la casilla de aprobación del PM sin marcar (le toca marcarla a él al revisar), **la plantilla del repo no puede pasar su propio gate** y empuja a los autores a borrar el registro de aprobación o a marcarlo ellos mismos. | medium | **fixed** | US-503 / REQ-007 | `fix/edgar-navarrete-mojibake-higiene-vault` (Edgar Coronel, PM — **revisión de C5 solicitada a Luis Téllez por regla 7**). Tres cambios: el patrón se acota a `grep -qE '^[[:space:]]*-[[:space:]]*\[ \]'`; la sección `## Aprobación` se recorta antes de evaluar, porque es del PM y se marca al revisar; y se agrega el evento **`edited`**, sin el cual un cuerpo corregido después del push se quedaba en rojo para siempre; además, las dos casillas que un autor honesto no puede marcar —`(Alternativa) No usé IA` y `Si toqué esquema…`— se marcan `<!-- opcional -->` en la plantilla y el gate las omite (hallado al revisar el PR #110) | `.github/scripts/probar_verificar_plantilla.sh` — 7 casos contra el script real, leyendo `.github/PULL_REQUEST_TEMPLATE.md` del archivo (no una copia): la plantilla llenada por el autor pasa, sin llenar reprueba, las casillas opcionales marcadas con `<!-- opcional -->` no cuentan, y mencionar la sintaxis en prosa ya no reprueba |
| BUG-015 | ML-01 no podía entrenar sobre `gold.features_escuela` real: un driver **100 % `SIN_DATO`** (D5 agua, DS-06 sin descarga) rompe el binning de `HistGradientBoostingRegressor` con `window shape cannot be larger than input array shape`, un error que no delata la causa. Además el default `--ventanas 3` pedía 5 ciclos y el Gold real sólo tiene 3 utilizables | high | **fixed** | US-311 / US-313 / REQ-003 | `fix/hector-marban-driver-sin-datos` | — |
| BUG-016 | La publicación a Gold tronaba en ML-02 con datos reales: hay filas con los **6 drivers en NULL a la vez**, y `generar_driver_dominante_proxy` falla ahí por diseño. La `driver_dominante` real de C1 (US-302, PR #113) ya adoptó la convención de dejarlas en NULL; faltaba apartarlas antes de entrenar, porque `validar_target_ml02` rechaza nulos. Conservan su predicción de ML-01 y no reciben recomendación (`SIN_DATO`, nunca un driver inventado) | high | **fixed** | US-313 / REQ-003 | `fix/hector-marban-driver-sin-datos` | — |
| BUG-017 | `indice_riesgo` se publicó **saturado**: la corrida real de ML-01 dio MAE 10.90, pero la sigmoide está calibrada sobre **fracción** (`-0.05` = pierde 5 % de matrícula). Con esa escala el 100 % de las 45 249 filas queda en riesgo ≈ 1.00 y el tablero cuenta como "en riesgo" a todo el universo. **Confirmado por Diana el 2026-08-28**: `target_variacion_matricula = matricula_total - matricula_ciclo_anterior`, diferencia absoluta de alumnos. El MAE 10.90 son ~11 alumnos, no un modelo malo; lo que está mal es publicar eso a través de una sigmoide calibrada sobre fracción. Añadida guarda que detiene la publicación en vez de saturar en silencio; **falta confirmar las unidades en Gold con C1** | high | open | US-311 / US-313 / REQ-003 / US-104 | — | pendiente — **convoca y cierra: Edgar Coronel (PM).** No es defecto de código sino de decisión pendiente: se resuelve al ratificar [[03_Architecture/ADRs/ADR-007-unidad-target-variacion-matricula\|ADR-007]]. Héctor ya puso la guarda que detiene la publicación en vez de saturar en silencio, así que hoy estamos protegidos. Mesa: Andrés González, Christian Ruiz, Diana Alvarez y Marina García |
| BUG-018 | ML-02 arrastra el **mismo defecto por ventana** que BUG-015: `entrenar_ml02._matriz()` toma siempre los 6 drivers sin comprobar cobertura dentro de la ventana de entrenamiento, así que un driver vacío en ese tramo (D6 aire, IDW de US-105) rompe el binning de `HistGradientBoostingClassifier` con el mismo error. Reproducido; el arreglo es el mismo que ya se aplicó en ML-01 | high | open | **fixed** | `feat/andres-habib-bug018-ml02-cobertura` (Andrés González) — cobertura evaluada por ventana y predicción/SHAP alineados con `feature_names_in_`. **Corregido el 29-ago en el registro**: la matriz de trazabilidad ya lo daba por resuelto desde el 28-ago pero esta fila seguía en `open`; el registro es la fuente canónica y no puede ir detrás de la matriz | ver detalle |
| BUG-019 | `target_variacion_matricula` se produce en **dos unidades distintas** bajo el mismo nombre: `features_escuela.sql` (C1, grano escuela) da **alumnos absolutos** y `target_hibrido.variacion_desde_serie` (C3, grano municipio×nivel) da **fracción**. Ambas llegan a `gold.predicciones.valor`, distinguidas sólo por `grano` (DEC-010), así que esa columna hoy mezcla alumnos con fracciones. El contrato nunca declaró la unidad | high | open | US-104 / US-311 / US-313 / REQ-003 | — | pendiente — **misma mesa que BUG-017**, convoca Edgar Coronel (PM). Las dos unidades bajo el mismo nombre se unifican al ratificar ADR-007. DEC-006 («riesgo ≥ 0.6 ↔ pérdida de ~5 %») ya presupone fracción, así que ratificar no abre una decisión nueva: la alternativa A obligaría a **reabrir DEC-006** |
| BUG-020 | En la URL pública **toda ruta que toca base de datos responde HTTP 500**: `/api/v1/predicciones/{cct}`, `/predicciones/batch` y `/escuelas`. `/api/v1/health` responde 200, así que el contenedor corre y el despliegue de BUG-008 sirvió. Con token válido, inválido o sin token el resultado es el mismo 500 —nunca 401—, así que el fallo ocurre **antes** de validar auth. Sin esto no hay demo end-to-end ni el punto de rúbrica de URL pública | **critical** | open | US-401 / US-411 / US-501 / REQ-004 / REQ-005 | — | pendiente — **Christian Ruiz (C4) y Luis Téllez (C5); seguimiento diario de Edgar Coronel hasta cerrarlo.** Es el **único riesgo vivo para la casilla 6 del ensayo E2E** y para el punto de rúbrica de URL pública. Sin esto no hay demo end-to-end. Escalado el 29-ago tras dos peticiones de estado sin respuesta | `08_CICD_DevOps/scripts/smoke-test-bug020.sh` — 4 etapas que distinguen contenedor caído, sesión de DB ausente, Gold vacío y auth. **Línea base del 30-ago, 02:15**: etapa 1 ✅ (health 200), etapa 2 ❌ (`/escuelas` 500), etapa 4 ❌ (500 **sin token**, nunca 401 → el fallo ocurre antes de validar auth). Reejecutar tras la Fase 2 
| BUG-021 | `dbt run` con el número de hilos por defecto (`threads>1`) truena en `gold.dim_escuela`, `dim_municipio` y `dim_tiempo` con *relation does not exist*, aunque su silver de origen se cree casi en el mismo instante. Con `--threads 1` corre limpio de punta a punta. Causa: esos modelos leían su origen con `source('silver', …)` en vez de `ref()`. `silver.*` son modelos **de este mismo proyecto**, no datos externos, así que dbt no tenía cómo saber que debía construirlos antes y los agendaba en paralelo. Con `threads=1` el orden accidental funcionaba y el defecto quedaba escondido | high | **fixed** | US-213 / US-113 / REQ-001 | **Reportado por Monserrat Miranda** (2026-08-28, validando DB-05/DB-08 contra Gold real) · **corregido por Diana Alvarez** en `fix/diana-varela-bug016-source-vs-ref`: los siete modelos Gold pasan a `ref()`; `_gold__sources.yml` queda sólo como documentación de columnas | `dbt run` completo con hilos por defecto ✅ · [[_DevLog/2026-08-29-diana-alvarez-bug021-source-vs-ref]] |
| BUG-022 | `gold.dim_driver` puede quedar desincronizado sin que nada lo detecte: `superset/mock/gold_estrella_mock.sql` (mock previo de C2/US-212, hoy superado) crea la tabla con `CREATE TABLE IF NOT EXISTS` + `INSERT ... ON CONFLICT DO NOTHING` usando nombres largos ("Pobreza y rezago social"...) distintos al catálogo canónico corto del seed (`dbt/seeds/dim_driver.csv`). Si ese mock corre en un entorno donde `dbt seed`/`dbt build` nunca se ejecutó, la tabla se queda con los nombres viejos — la columna `nombre` solo tenía `not_null`, sin `accepted_values`, así que ningún test lo detectaba; el primer síntoma era un HTTP 500 río abajo en Superset (US-213) | high | **fixed** | US-213 / US-113 | **Reportado por Manuel Serranía** (PR #100) y **Monserrat Olivas** (validando US-213 contra Gold real) · **corregido por Diana Alvarez** en `fix/diana-varela-bug022-dim-driver-catalogo`: `accepted_values` sobre `nombre` en `dbt/seeds/_gold__seeds.yml` con los 6 nombres canónicos, documentado en `Data_Model.md` §4.2 | Simulado el estado divergente real (test FALLA con `FAIL 6`) y el estado correcto tras `dbt seed` (PASS limpio) · [[_DevLog/2026-08-29-diana-alvarez-bug022-dim-driver-catalogo]] |
| BUG-023 | Tercera aparición del defecto de BUG-015/BUG-018, ahora en `evaluar.py`: `error_por_entidad()` y `cobertura_y_error()` predecían con los **seis** drivers aunque el modelo se hubiera entrenado con menos, así que `construir_reporte()` **no podía generar el reporte** en el único escenario que el PM necesita documentar para la demo — el de 5 de 6 drivers. `ValueError: The feature names should match those that were passed during fit` | high | **fixed** | US-312 / REQ-003 / AC-003.2 | `feat/hector-marban-drivers-en-evaluacion` | — |
| BUG-024 | `SELECT ... INTO` atravesaba el guardarraíl porque empieza con `SELECT`, pero en PostgreSQL crea una tabla; el agente no tiene otra capa que garantice solo lectura | **critical** | **fixed** | US-304a / US-305 / REQ-006 | `fix/andres-habib-bug024-select-into-rag-empty` | `tests/test_agente_guardrails.py::test_select_into_se_rechaza_como_escritura` |
| BUG-025 | El endpoint desplegado `/api/v1/agente/consulta` es el **stub** de `src/api/v1/agente.py`: responde **la misma cadena fija a cualquier pregunta**, incluidas las fuera de alcance y las destructivas. Además su filtro de palabras busca `"borrar"` por subcadena, así que **«Borra la tabla de predicciones» no lo dispara** y recibe la respuesta normal con `fuera_de_alcance: false`. Los guardarraíles reales de `src/agente/guardrails.py` —que sí rechazan esa frase— nunca se invocan desde la API | high | open | US-304a, US-305, REQ-006 | pendiente (**C4 + C3**): conectar `procesar_consulta_con_rag()` al endpoint; como mitigación inmediata, que el stub llame a `pregunta_en_alcance()` || — 
| BUG-026 | **Ningún juego de fixtures del repo puede ejercitar el grano escuela multi-ciclo.** Hay dos y cada uno resuelve la mitad: `bronze_formato911_sample.csv` + `…_ciclo_anterior_sample.csv` traen CCT coherentes con `gold.dim_escuela` (**59 de 60**) pero solo **2 ciclos**, así que `gold.features_escuela` sale con 1 y ML-01 no puede hacer partición temporal; `bronze_formato911_historico_sample.csv` trae **6 ciclos** pero comparte solo **3 CCT de 30** con `dim_escuela` (se generó sobre su propio universo, disjunto de `bronze.cct`), así que a grano escuela el JOIN se vacía **sin ningún error** — el modo de falla silenciosa de BUG-012. Consecuencia: entrenar ML-01 y verificar los bloques de predicción de DB-03 (AC-002.4) solo es posible con ~460 MB de CSV real en un ambiente propio (hoy, únicamente el de Diana); **CI nunca recorre esa ruta** | high | **fixed** | US-104 / US-113 / US-313 / REQ-001 / REQ-003 | **PR #129** (Diana Alvarez) — fixture aditivo `bronze_formato911_serie_historica_sample.csv`: reutiliza las CCT de `bronze_formato911_sample.csv` tal cual (mismo patrón que `..._ciclo_anterior_fixture.py`) y agrega 2021-2022 y 2022-2023 sobre la MISMA tabla. No toca ningún modelo dbt. **Verificado de punta a punta por la reportante el 29-ago** | — (propuesto: aserción dbt de solape mínimo con `dim_escuela` y de ciclos mínimos en `features_escuela`). **Mergeado el 29-ago**; cierra la mitad que faltaba de BUG-013 | — el fixture *es* la regresión: con él, `features_escuela` sale con 3 ciclos y `publicar_gold.py --desde-gold` entrena. Pendiente la guarda automática propuesta (aserción dbt de solape mínimo con `dim_escuela` y de ciclos mínimos), sin la cual un fixture futuro puede volver a divergir sin que CI lo note 
| BUG-027 | `superset/semantic/metrics_kpis_base_us221.yaml` apunta sus 5 `sql_ref` a `sql/kpi_0*.sql`, ruta que **ya no existe**: el commit `1c2f5f9` movió esos archivos de `superset/sql/` a `superset/semantic/` y actualizó el test, pero no el YAML. Nadie lo nota porque `tests/test_kpis_us221.py` **codifica la ruta a mano** (`SQL_DIR = superset/semantic`) y nunca lee el `sql_ref` del catálogo: la prueba pasa en verde mientras el artefacto que la gente consulta apunta al vacío | low | **superseded** | US-221 / REQ-002 | US-221 / REQ-002 | **No se corrige la ruta: los archivos desaparecen.** Manuel Serranía ratificó el 28-ago una sola implementación por KPI (regla 1 del vault): se borran los 5 `kpi_*.sql` y las tarjetas se remapean a los datasets canónicos (`db01_cubo_matricula`, `db02_cubo_riesgo_territorial`, `db01_distribucion_escuelas`), sin `sql_ref` a SQL nuevo. Arreglar el `sql_ref` sería trabajo sobre artefactos que se eliminan. Seguimiento en el follow-up de US-221 (C2, Oscar Quiroz) | — **lo que sí sobrevive del hallazgo**: `test_kpis_us221.py` codifica `SQL_DIR` a mano y nunca lee el `sql_ref`, por eso pasaba en verde con el catálogo apuntando al vacío. El follow-up convierte ese test en guarda antiduplicación, que es el requisito que nace de este reporte 
| BUG-028 | `cargar_features()` leía el CSV **sin `dtype`**, así que pandas infería `int64` en `cve_mun` y se comía el cero de la izquierda: `"09001"` llegaba como `9001`. El join contra `dim_municipio` y la agregación de DEC-007 fallaban **en silencio** para las 9 entidades cuya clave INEGI empieza en cero — **CDMX (09) incluida, que es la entidad principal del alcance**. Diana lo había previsto y lo cubrió en `tests/conftest.py`, pero el lector de producción seguía sin ello, así que las pruebas veían la clave correcta y el pipeline no | high | **fixed** | US-325 / US-311 / DEC-007 / REQ-003 | **PR #127** — `dtype={"cve_mun": str}` en `cargar_features()` (`src/modelos/entrenar_ml01.py`). Detectado por la guarda de coherencia entidad↔municipio que el mismo PR agregó a `generar_fixture_dim.py`: reventó de inmediato con `'9001' contradice la entidad '09'` | la guarda misma es la regresión — `generar()` falla si `cve_mun` no empieza con la entidad que codifica el CCT, así que el cero perdido no puede volver a pasar inadvertido |
| BUG-029 | **RESERVADO — Oscar Quiroz (C2).** `superset/sync_semantic_layer.py` recorre alfabéticamente los `.sql` de `superset/semantic/` y **aborta toda la corrida** al llegar a `db09_cubo_recomendaciones.sql` si `gold.recomendaciones` no existe. No es error del SQL: en un ambiente sin la cadena Bronze→Gold materializada, nadie que sincronice después de `db09` alfabéticamente puede registrar sus datasets. Detectado por Oscar al construir DB-07 (US-222) | medium | open | US-222 / US-205 / REQ-002 | pendiente (**C2**) — mitigación inmediata: cargar `superset/mock/gold_ml_outputs_mock.sql`, mismo patrón de US-203/204/211b/212; solución de fondo: la resiliencia del sync que Manuel agrega en US-205, para que un dataset con tabla ausente no tumbe la corrida completa | — (propuesto: que el sync reporte y continúe en vez de abortar) |
| BUG-030 | **El esquema real de DS-06 no es el que `silver/agua_region.sql` espera, y el riesgo no es que D5 siga en `SIN_DATO` sino que alguien lo saque con la columna equivocada.** El extractor entrega `id_presa, nombre_oficial, corriente, estado, anio_term, alt_cort, cap_name, cap_namo`; el modelo espera `id_punto, region_hidrologica, latitud, longitud, indicador, valor, fecha`. **Ninguna de las cuatro columnas que importan existe** — no es renombrar, son dos estructuras distintas. Dos huecos: (1) sin `lat`/`lon` no hay interpolación IDW, que `Data_Model.md` §3 exige para D5; (2) `cap_name`/`cap_namo` son la **capacidad máxima** de la presa, no el volumen actual, así que conectarlas produciría un indicador constante en el tiempo que mide el tamaño de la presa y no la disponibilidad hídrica — un número creíble y falso, misma familia que el `indice_riesgo` saturado y el `*100`. Hoy no rompe nada porque BUG-009 mantiene el identifier falso y D5 sigue `SIN_DATO` explícito. Reportado por Diana Alvarez (C1) el 30-ago al revisar los metadatos de DS-06/DS-08, que **sí** están limpios | high | open | US-122a / US-112 / REQ-001 / DS-06 | pendiente (**C1 + Emilio Galnares**) — la solución ya está documentada en la ficha DS-06 §64-70 (endpoint «Detalle por presa: Presa, Año, Vol. de almacenamiento (hm3) — SERIE DE TIEMPO») y §74 (georreferencia vía datos.gob.mx). El extractor de US-122a jaló el listado general porque eso pedía la historia. **Decisión pendiente del PM:** ampliar el extractor, o documentar D5 como cobertura parcial explícita para la demo | — (propuesto: aserción de contrato entre las columnas de `bronze.conagua` y las que `agua_region.sql` consume) |

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
> `15_ML_Models/Indice_Riesgo_ML01.md` — pero eso es una decisión de negocio, no un arreglo de código.

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
[[03_Architecture/ADRs/ADR-007-unidad-target-variacion-matricula|ADR-007]] con la evidencia. La
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
   freeze en [[03_Architecture/Data_Lineage_US106]].
   **Rastreado como `RISK-008`** en [[10_Risk_Governance/Risk_Register]], con dueña y fecha objetivo:
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

Esto no cierra BUG-009 — sigue pendiente que Edgar decida el reparto para que estos valores (o los que correspondan) queden como default permanente en `sources.yml` — pero deja evidencia empírica lista para quien lo tome. Detalle completo en el DevLog `_DevLog/2026-08-23-diana-alvarez-bug009-hallazgos-gold-e2e.md`.

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
([[_DevLog/2026-08-28-diana-alvarez-formato911-real-validacion-us113]]). El problema es que esa
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
   [[_DevLog/2026-08-27-marina-garcia-pipeline-local-us212]]).
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

Es una variante del modo de falla de [[06_Quality_Testing/Bug_Register#BUG-026]] y de BUG-012: el
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
