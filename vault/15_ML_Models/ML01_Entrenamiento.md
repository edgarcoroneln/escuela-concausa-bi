---
id: DOC-ML01-ENTRENAMIENTO
title: "ML-01 — Entrenamiento, backtesting y resultados"
owner: "Héctor Rafael Morales Marbán"
status: in_review
traces_up: ["vault/02_Requirements/User_Stories", "vault/03_Architecture/ADRs/ADR-003-ml-estrategia-modelado", "vault/15_ML_Models/ML_Strategy"]
traces_down: ["US-311", "US-312", "US-313"]
tags: [ml, celula-3, ml-01, entrenamiento]
---

# ML-01 — Entrenamiento, backtesting y resultados

> Entregable central de [[vault/02_Requirements/User_Stories|US-311]]: modelo entrenado, MAE/RMSE con
> backtesting temporal y registro en MLflow (AC-003.2, AC-003.3, AC-003.4).
> → [[vault/15_ML_Models/_index]] · [[vault/15_ML_Models/ML_Strategy]] · [[vault/15_ML_Models/Indice_Riesgo_ML01]]

> [!warning] Los resultados de abajo son sobre **datos sintéticos**
> El entrenamiento corre hoy contra `tests/fixtures/features_escuela_mock.csv`. Las métricas
> validan que **el pipeline funciona**; no son resultados de negocio. Cuando la Célula 1 publique
> `gold.features_escuela` (US-104, vence el **23 de agosto**) se re-ejecuta con `--features` y este
> documento se actualiza con las cifras reales.

## 1. El modelo

| | |
|---|---|
| Estimador | `HistGradientBoostingRegressor` (scikit-learn 1.9.0) |
| Pérdida | `absolute_error` — robusta a outliers del target real |
| Objetivo | `target_variacion_matricula` — variación de matrícula al siguiente ciclo |
| Entradas | los 6 drivers normalizados de `gold.features_escuela` |
| Métrica | MAE / RMSE (AC-003.2) |
| Registry MLflow | `ML01_RegresionMatricula` |
| Código | `src/modelos/entrenar_ml01.py` |

### Por qué `HistGradientBoostingRegressor`

**Maneja `NaN` de forma nativa.** Un driver `SIN_DATO` llega al modelo como ausencia real y **nunca
se imputa a cero**, conforme a la regla 4 de [[vault/15_ML_Models/_index]]. El estimador aprende a qué
lado del árbol mandar las ausencias: no tener dato de calidad del aire es información sobre la
escuela, no un cero.

Esto difiere de la imputación por mediana municipal que propone
[[vault/03_Architecture/ADRs/ADR-003-ml-estrategia-modelado|ADR-003]] §"cobertura parcial". Ambas rutas
son defendibles; ésta preserva la señal de ausencia sin agregar features indicadoras. **Punto a
ratificar con Andrés** antes de cerrar US-311.

## 2. Protocolo de evaluación

Backtesting **walk-forward** con ventana de entrenamiento creciente, conforme a ADR-003. Antes de
cada `fit()` se invoca `verificar_sin_fuga()`: la regla "partición temporal, nunca aleatoria"
(AC-003.3) no se asume, se comprueba en ejecución.

Cada ventana se compara contra `DummyRegressor(strategy="mean")`. **Una métrica sin baseline no
dice nada**: un MAE de 0.015 puede ser excelente o ridículo según la escala del objetivo.

> ADR-003 fija 4 ventanas. El fixture sólo tiene 5 ciclos, así que hoy corren 3. Con los ciclos
> reales del Formato 911 se sube a 4 sin tocar código (`--ventanas 4`).

## 3. Resultados (datos sintéticos, 400 filas · 80 escuelas · 5 ciclos)

| Ventana | MAE | RMSE | MAE baseline | Mejora |
|---|---|---|---|---|
| entrena 2019-2021 → prueba 2021-2022 | 0.0145 | 0.0186 | 0.0294 | **50.8 %** |
| entrena 2019-2022 → prueba 2022-2023 | 0.0145 | 0.0183 | 0.0283 | **48.8 %** |
| entrena 2019-2023 → prueba 2023-2024 | 0.0160 | 0.0192 | 0.0295 | **45.9 %** |

**MAE 0.0150 ± 0.0007 · RMSE 0.0187 ± 0.0004** (1.50 y 1.87 puntos porcentuales,
respectivamente; promedio ± desviación de las ventanas, ADR-003). Ambos cumplen los umbrales
provisionales de 3 y 5 puntos porcentuales.

El modelo reduce el error entre 46 % y 51 % frente al baseline en las tres ventanas. La degradación
progresiva (51 % → 46 %) es esperable: las ventanas tardías predicen ciclos más lejanos del inicio
de la serie.

### Resultados sobre Gold real · BUG-048 · 2026-09-05

Se reentrenó con partición temporal sobre el dump post-BUG-045 de Diana Alvarez: 136,046 filas,
46,547 escuelas y tres ciclos (`2022-2023`…`2024-2025`). D5 quedó excluido de forma explícita por
ausencia total; los otros cinco drivers entraron al modelo.

La pérdida cuadrática vigente no aportaba frente al baseline: MAE 0.159148 contra 0.159223 y
predicciones exclusivamente positivas, por lo que ninguna escuela superaba el umbral de riesgo.
Con `loss="absolute_error"`, en la misma ventana temporal y sin ajustar el umbral, el dump
definitivo con CONAPO real produce:

| Métrica | Resultado |
|---|---:|
| MAE | 0.141458 |
| RMSE | 0.436326 |
| MAE baseline | 0.159223 |
| Mejora sobre baseline | 11.04 % |
| Riesgo mínimo / mediana / máximo | 0.0292 / 0.3533 / 0.5717 |
| Escuelas con `indice_riesgo >= 0.6` | 0 (0 %) |

No se movieron las anclas de negocio ni se optimizó un porcentaje objetivo. El cambio se aceptó
porque mejora el holdout temporal frente al baseline. El 0 % definitivo es consistente con la
calibración ratificada: la mayor caída predicha es 4.53 %, menor que el umbral de 5 %. La publicación
local produjo 45,276 predicciones y 45,276 recomendaciones para 2024-2025; ML-02 obtuvo F1 macro
0.8333 y cinco drivers dominantes.

### Error por entidad (ventana de producción)

Insumo directo de US-312. Como `features_escuela` no trae `cve_ent`, la entidad se deriva de los
dos primeros caracteres del CCT.

| Entidad | Escuelas | MAE |
|---|---|---|
| 14 · Jalisco | 20 | 0.0183 |
| 19 · Nuevo León | 20 | 0.0171 |
| 09 · CDMX | 20 | 0.0167 |
| 15 · Edomex | 20 | 0.0118 |

## 4. Registro en MLflow

Una corrida **padre** con las métricas agregadas y una corrida **hija por ventana**, con sus ciclos
de entrenamiento y prueba como parámetros. El `run_id` del padre es el que va a
`gold.predicciones.mlflow_run_id` (US-313).

```bash
python -m src.modelos.entrenar_ml01 --tracking-uri sqlite:///mlflow.db --registrar-modelo
```

> [!bug] BLOCK-001 sigue abierto — verificado el 2026-08-19
> **Primera causa, ya resuelta:** el servidor corría MLflow 2.8.0 contra el cliente 3.15.1 de la
> Célula 3. Luis Téllez lo alineó a **3.15.1** en el PR #45.
>
> **Segunda causa, vigente:** el servicio arranca con `--default-artifact-root /mlflow/artifacts`
> —una ruta **dentro del contenedor**— y **sin `--serve-artifacts`**. El experimento queda con
> `artifact_location: /mlflow/artifacts/1`, así que un cliente que entrena **desde el host** intenta
> escribir esa ruta en su propia máquina y falla con
> `OSError: [Errno 30] Read-only file system: '/mlflow'`. Las métricas se registran; el modelo no.
> ~~El servidor compartido sigue bloqueado, pero **AC-003.4 ya se verificó localmente** el 29 de
> agosto: ML-01, ML-02 y ML-03 quedaron registrados como versión 1 en un backend SQLite temporal y
> el verificador conjunto confirmó los tres nombres canónicos.~~
>
> **Corregido el 2026-09-02 (BUG-043).** Esa afirmación era engañosa y hay que decirlo con claridad:
> lo que se verificó el 29-ago fue un **SQLite temporal**, no el servidor que se demuestra. Contra el
> servidor real, `ML01_RegresionMatricula` **v1 era un fantasma** — fila `READY` en el Registry,
> artefacto inexistente, `load_model()` respondiendo `No such artifact: 'MLmodel'`. **AC-003.4 no
> estaba cumplido**, y el verificador lo daba por bueno porque sólo preguntaba si la fila existía.
>
> La causa de configuración ya estaba descrita aquí desde el 29-ago; lo que faltaba era ver que
> `mlflow.register_model()` **crea la versión aunque el artefacto haya fallado**, y que por eso un
> verificador que sólo mira el Registry nunca lo iba a detectar. Ahora
> `verificar_artefactos_descargables()` carga cada versión con `pyfunc` y reprueba.
>
> **Fix probado** (pendiente de aplicar por la Célula 5): levantando el mismo `faro-mlflow:3.15.1`
> con `--serve-artifacts` y `--artifacts-destination ${MLFLOW_ARTIFACT_ROOT}`, el experimento queda
> con `artifact_location: mlflow-artifacts:/2`, el modelo llega al registry como
> `ML01_RegresionMatricula` v1 y se recupera con
> `mlflow.sklearn.load_model("models:/ML01_RegresionMatricula/1")` para predecir.
>
> Nota: el experimento actual ya tiene la ruta mala grabada en Postgres; con el cambio los
> experimentos **nuevos** salen bien pero el existente conserva su `artifact_location`.
>
> Mitigación en el código: `mlflow_utils.verificar_compatibilidad()` detecta el desajuste de
> versiones antes de entrenar. No cubre este segundo caso, que sólo se ve al escribir el artefacto.

> **MLflow 3.x deprecó el file store.** `file:./mlruns` ya no funciona y lanza excepción; el URI
> debe apuntar a una base de datos (`sqlite:///mlflow.db` en local, Postgres en producción).
> Además, `mlflow.db` **no está en `.gitignore`**, que sí cubre `airflow.db` y `superset.db`.
> Reportado a la Célula 5.

Verificado a mano: 4 corridas (1 padre + 3 ventanas), métricas y parámetros presentes.

**Estado del registry al 2026-09-02** (corrida de confirmación pedida por el PM, US-311):

| Versión | Experimento | Carga con `load_model()` |
|---|---|---|
| v1 (18-ago) | `ML-01-regresion-matricula` | ❌ fantasma: `No such artifact: 'MLmodel'` |
| v2 (2-sep) | `ML-01-regresion-matricula-v2` | ✅ carga y predice — servidor con `--serve-artifacts` |

Las métricas no cambian entre ambas (MAE 0.0141 ± 0.0012, RMSE 0.0177 ± 0.0008): lo que cambia es
que el modelo **existe** y se puede recuperar. Mientras C5 no aplique el fix a `docker-compose.yml`,
el servidor que se va a demostrar sigue produciendo versiones fantasma; ver **BUG-043**.

## 5. Del modelo al tablero

ML-01 predice una **variación con signo**. La conversión al `indice_riesgo` ∈ [0,1] que consumen la
API, los cubos y FARO Web está en [[vault/15_ML_Models/Indice_Riesgo_ML01]] y es **capa de presentación**:
no cambia el modelo, no cambia la métrica reportada y no se entrena contra ella.

| Variación | `indice_riesgo` |
|---|---|
| −0.10 | 0.840 |
| −0.05 | 0.600 |
| 0.00 | 0.300 |
| +0.05 | 0.109 |

## 6. Pruebas

`tests/test_entrenar_ml01.py` — 15 casos (`TEST-005`). Sólo ejercitan la parte pura: el CI no
levanta MLflow ni escribe artefactos. Las que importan:

- `test_ninguna_ventana_tiene_fuga_temporal` — AC-003.3 en cada ventana.
- `test_le_gana_al_baseline_en_todas_las_ventanas` — si no supera predecir la media, no hay modelo.
- `test_no_imputa_los_sin_dato` — compara el conteo de nulos que recibe el estimador contra el
  origen; un `fillna(0)` en el pipeline hace fallar la prueba.
- `test_falla_si_la_tabla_no_cumple_el_contrato` — si la Célula 1 publica una tabla sin las columnas
  acordadas, se detecta al cargar y no en medio del entrenamiento.

## 7. Lo que falta para cerrar US-311

1. **Re-ejecutar contra `gold.features_escuela` real** (US-104, Diana, vence 23 ago) y actualizar §3.
2. **Ratificar con Andrés** el manejo de cobertura parcial: `NaN` nativo (esta implementación) frente
   a imputación por mediana + indicador (ADR-003).
3. **Subir a 4 ventanas** cuando haya ciclos suficientes.
