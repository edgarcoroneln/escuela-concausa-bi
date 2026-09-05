---
id: DOC-PUBLICACION-GOLD
title: "Publicación de predicciones y recomendaciones a Gold"
owner: "Héctor Rafael Morales Marbán"
status: in_review
traces_up: ["vault/02_Requirements/User_Stories", "vault/03_Architecture/Data_Model", "vault/15_ML_Models/Indice_Riesgo_ML01"]
traces_down: ["US-313"]
tags: [ml, celula-3, gold, batch]
---

# Publicación de predicciones y recomendaciones a Gold

> Job batch de [[vault/02_Requirements/User_Stories|US-313]]: escribe `gold.predicciones` y
> `gold.recomendaciones`, las tablas que alimentan **DB-06** y **DB-09** y los endpoints de
> inferencia de la Célula 4.
> → [[vault/15_ML_Models/_index]] · [[vault/15_ML_Models/ML01_Entrenamiento]] · [[vault/03_Architecture/Data_Model]]

## 1. Contrato

Conforme a [[vault/03_Architecture/Data_Model]] §4.5 tras **DEC-005/006**, que resolvió la ambigüedad que
señalamos en [[vault/15_ML_Models/Indice_Riesgo_ML01]] §4: la tabla guarda **las dos cosas**.

| `gold.predicciones` | Tipo | Notas |
|---|---|---|
| `grano` | enum | `escuela` \| `municipio_nivel` — discriminador (DEC-010) |
| `cct` | str \| NULL | poblado **sólo** si `grano = escuela` |
| `cve_mun` + `nivel` | str \| NULL | poblados **sólo** si `grano = municipio_nivel` |
| `id_ciclo`, `modelo` | — | parte de la llave en ambos granos |
| `valor` | float | **variación cruda**; conserva la unidad para MAE/RMSE |
| `indice_riesgo` | float [0,1] | derivado, calculado en `src/modelos/riesgo.py` |
| `probabilidad` | float \| NULL | ML-01 es regresión: siempre `NULL`, nunca 0 |
| `mlflow_run_id` | str | corrida que produjo el modelo |
| `generado_at` | timestamptz | |

| `gold.recomendaciones` | Tipo | Notas |
|---|---|---|
| `cct`, `id_ciclo` | — | llave primaria compuesta |
| `driver_dominante` | str | `D1`…`D6`; **salida de ML-02** |
| `recomendacion` | str | del catálogo prescriptivo (§4) |
| `prioridad` | enum | `alta` / `media` / `baja` (§5) |
| `shap_d1`…`shap_d6` | float \| NULL | contribuciones batch de ML-02; `NULL` = `SIN_DATO`, nunca cero de relleno |

## 2. Grano dual (DEC-010)

ML-01 puede predecir a `municipio × nivel` (DEC-007, mitigación de RISK-007) mientras las features y
el driver dominante viven a nivel escuela. **Repartir el valor del grupo a cada escuela le
atribuiría un dato que no se midió ahí** — el mismo tipo de dato inventado que las reglas de
`SIN_DATO` prohíben en el resto del esquema. Por eso la fila **declara su grano** en vez de
repartirse.

`gold.recomendaciones` **no cambia**: se mantiene siempre a grano escuela, porque el carácter
prescriptivo no se agrega.

### Cómo se hace cumplir

La restricción del `Data_Model` §4.5 —*exactamente uno de `cct` o (`cve_mun`+`nivel`), nunca ambos,
nunca ninguno*— se aplica en **tres capas**:

1. **Pydantic**: un `model_validator` en `PrediccionGold` rechaza la fila antes de escribirla.
2. **La base de datos**: el `CHECK ck_predicciones_llave_segun_grano` la rechaza aunque alguien
   escriba por SQL directo, sin pasar por el job.
3. **Unicidad**: no hay llave primaria única posible, porque una PK no admite nulos y las dos llaves
   se excluyen. Se usan **dos índices únicos parciales**, uno por grano.

El UPSERT elige su objetivo de conflicto según el grano del lote, y **rechaza lotes que mezclen
granos**: con dos índices, un lote mixto haría ambiguo contra cuál resolver el conflicto.

### Verificado contra Postgres

Además de las pruebas con SQLite, se comprobó contra el Postgres del `docker-compose`:

| Comprobación | Resultado |
|---|---|
| Ambos granos conviven | 80 filas `escuela` + 46 `municipio_nivel` |
| Idempotencia por grano | repetir ambas escrituras deja 80 + 46, no 160 + 92 |
| Índices parciales creados | `ux_predicciones_escuela` y `ux_predicciones_municipio_nivel`, con su `WHERE` |
| `CHECK` rechaza las dos llaves | ✅ |
| `CHECK` rechaza ninguna llave | ✅ |
| `CHECK` rechaza un `grano` inventado | ✅ |
| Índice parcial rechaza duplicados del mismo grano | ✅ |

Las tres primeras filas de rechazo se probaron por **SQL directo**, sin pasar por el job: es
justamente lo que el `CHECK` protege.

> El `indice_riesgo` se calcula en ambos granos, pero sus anclas se fijaron sobre la variación de
> **una escuela concreta**. A nivel `municipio × nivel` es una lectura agregada, **no una alerta por
> plantel**; el `Data_Model` §4.5 lo advierte igual.

## 3. Idempotencia

El job se corre N veces con el mismo resultado. Escribe con **UPSERT** (`ON CONFLICT DO UPDATE`)
sobre la llave natural: **no borra particiones ni trunca tablas**. Tras reentrenar, la corrida
siguiente actualiza `valor`, `indice_riesgo` y `mlflow_run_id` en su sitio.

Verificado contra Postgres real (el `docker-compose.yml` del equipo): dos corridas seguidas dejan
**80 filas / 80 escuelas**, no 160.

## 4. Catálogo prescriptivo

Es el corazón del proyecto: dos escuelas con el mismo riesgo reciben recomendaciones distintas
según su driver dominante.

| Driver | Recomendación |
|---|---|
| D1 · Pobreza | Priorizar programas de becas y apoyo alimentario en la zona. |
| D2 · Inseguridad | Coordinar con seguridad pública rutas escolares seguras y entornos protegidos. |
| D3 · Infraestructura | Gestionar rehabilitación de infraestructura escolar prioritaria. |
| D4 · Conectividad | Ampliar conectividad y dotación de equipo de cómputo. |
| D5 · Agua | Asegurar suministro de agua y planes de contingencia hídrica. |
| D6 · Aire | Activar protocolos por contingencia de calidad del aire. |

El catálogo canónico vive en `src/modelos/recomendaciones.py`. Célula 4 todavía conserva una copia
en `src/api/mock_data.py` (US-401); `test_catalogo_coincide_con_el_de_la_api` falla si divergen.
Cuando C4 retire sus datos simulados, debe importar el catálogo canónico de Célula 3.

## 5. Prioridad

Derivada del `indice_riesgo` reutilizando las **anclas ya ratificadas** de
[[vault/15_ML_Models/Indice_Riesgo_ML01]] — no se introducen umbrales nuevos:

| Prioridad | Condición | Origen del umbral |
|---|---|---|
| `alta` | `indice_riesgo >= 0.60` | umbral de "escuela en riesgo" ratificado por Manuel Serranía (PR #27) |
| `media` | `>= 0.30` | ancla de matrícula estable |
| `baja` | `< 0.30` | |

## 6. Integración con ML-02

`driver_dominante` es salida de **ML-02 (US-302, Andrés González Habib)**. El CLI entrena ML-01 y
ML-02, alinea sus salidas uno-a-uno por `cct` e `id_ciclo`, construye las recomendaciones y publica
ambas tablas. Si falta una fila de features para ML-02, el job falla en vez de inventar un driver.

`--solo-predicciones` conserva la posibilidad explícita de omitir ML-02 cuando se necesite aislar
ML-01 durante diagnóstico.

`--con-shap` calcula las contribuciones con `TreeExplainer` durante el batch y las persiste junto a
cada recomendación. El modo normal deja las seis columnas en `NULL`; no calcula SHAP por request ni
convierte drivers excluidos por cobertura en `0.0`. Si la tabla ya existe, el publicador agrega las
columnas faltantes de forma idempotente antes del UPSERT.

## 7. Uso

### Contra `gold.features_escuela` real (cierra BUG-013)

```bash
docker compose up -d db
export DATABASE_URL="postgresql+psycopg2://postgres:<PASSWORD>@localhost:5432/escuela_concausa_db"
python -m src.modelos.publicar_gold --desde-gold
```

`--desde-gold` lee la tabla materializada por la Célula 1 en vez del fixture. Es lo que resuelve el
`JOIN` en cero de **DB-03**: publicando desde el fixture, las predicciones salen de un ciclo que el
hecho real no tiene, así que `cobertura_prediccion` queda en `SIN_DATO` para el 100 % de las
escuelas.

Requiere que `gold.features_escuela` esté materializada (`dbt run`). Si no lo está, el job **falla
con un mensaje que lo dice**, en vez de publicar silenciosamente desde el fixture.

### Contra el fixture sintético (desarrollo)

```bash
python -m src.modelos.publicar_gold --features tests/fixtures/features_escuela_mock.csv
```

Imprime un aviso explícito de que los datos son sintéticos.

## 8. Pruebas

`tests/test_publicar_gold.py` — 32 casos (`TEST-006`), sobre **SQLite en archivo temporal**: el CI
no necesita Postgres y el UPSERT se ejercita de verdad, no se simula. El código es dialecto-aware,
así que es la misma ruta que corre contra Postgres.

Las que importan:

- `test_es_idempotente` y `test_el_upsert_actualiza_en_vez_de_duplicar` — el requisito central.
- `test_probabilidad_es_nula_en_una_regresion` — `NULL` explícito, nunca 0.
- `test_conserva_la_variacion_cruda_y_el_riesgo` — DEC-005 en ejecución.
- `test_catalogo_coincide_con_el_de_la_api` — vigila la duplicación con la Célula 4.
- `test_rechaza_drivers_fuera_del_catalogo` — un `D9` no se publica en silencio.
- `test_conecta_ml02_con_recomendaciones_del_mismo_ciclo` — alinea ML-01 y ML-02 por llave.
- `test_igual_riesgo_y_distinto_driver_producen_recomendaciones_distintas` — verifica AC-003.6.
- `test_recomendaciones_persisten_shap_nullable` — diferencia contribución cero de `SIN_DATO`.
- `test_migra_recomendaciones_legacy_con_columnas_shap` — actualiza una tabla existente sin borrar datos.
- `test_predice_a_municipio_nivel_sin_repartir_a_escuelas` — DEC-010: la fila declara su grano.
- `test_los_dos_granos_conviven_sin_colisionar` — cada uno usa su índice parcial.
- `test_escribir_rechaza_un_lote_con_granos_mezclados` — objetivo de conflicto inequívoco.
- `test_la_base_rechaza_una_fila_con_las_dos_llaves` — el `CHECK` protege incluso al SQL directo.

## 9. Pendientes

1. **Re-ejecutar con `gold.features_escuela` real** y la etiqueta supervisada confirmada por C1.
2. ~~Verificar el grano dual contra Postgres~~ — **hecho** (ver §3).
3. **Forma exacta del contrato de la API**: DEC-010 la deja pendiente de confirmar con Christian
   Ruiz, dueño de `PrediccionOut`. Hoy el esquema de `PrediccionOut` asume grano escuela.
2. **Resolver la duplicación del catálogo** con la Célula 4.
3. `vault/03_Architecture/Data_Model.md` **línea 255** conserva la redacción vieja — dice que
   `indice_riesgo` vive en la columna `valor`, lo que contradice el §4.5 tras DEC-005. Es de la
   Célula 1.
