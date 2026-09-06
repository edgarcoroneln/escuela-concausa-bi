---
id: DOC-ML02-CLASIFICACION-DRIVER
title: "ML-02 — Clasificación de driver dominante"
owner: "Andrés González Habib"
status: in_review
version: "0.4"
traces_up: ["US-302", "REQ-003", "vault/15_ML_Models/ML_Strategy"]
traces_down: ["src/modelos/entrenar_ml02.py", "tests/test_entrenar_ml02.py"]
tags: [ml, ml-02, clasificacion, shap, celula-3]
---

# ML-02 — Clasificación de driver dominante

> → [[vault/15_ML_Models/_index]] · [[vault/15_ML_Models/ML_Strategy]]

## Objetivo

ML-02 identifica cuál de los seis drivers (`D1`…`D6`) explica mejor el riesgo de una escuela y devuelve
una recomendación prescriptiva alineada con el contrato de la API.

## Estado actual

El pipeline ejecutable vive en `src/modelos/entrenar_ml02.py`:

- carga `tests/fixtures/features_escuela_mock.csv` o una tabla compatible con `gold.features_escuela`;
- reutiliza backtesting temporal (`generar_backtesting` + `verificar_sin_fuga`);
- entrena `HistGradientBoostingClassifier`, que tolera `NaN` para preservar `SIN_DATO`;
- reporta `F1 macro`, `accuracy`, `precision macro` y baseline `most_frequent`;
- produce `driver_dominante` (`D1`…`D6`) y `recomendacion` para integración posterior con API;
- publica las recomendaciones en Gold, alineadas por `cct` e `id_ciclo` con las predicciones de ML-01;
- devuelve explicaciones SHAP por escuela con el contrato `cct`, `driver_dominante` y
	`contribuciones` (`D1`…`D6`);
- puede registrar el modelo de producción en MLflow con el nombre canónico `ML02_DriverClasificador`
	y exige confirmación de la versión creada en el Registry.
- valida antes de entrenar que el target real o proxy no tenga nulos, use solo `D1`…`D6` y contenga
	al menos dos clases.
- evalúa la cobertura dentro de cada ventana y excluye los drivers completamente vacíos antes de
	entrenar; predicción y SHAP reutilizan las columnas reales de `modelo.feature_names_in_`.

## Target operativo

Desde el 28 de agosto, `gold.features_escuela` publica `driver_dominante` mediante el argmax de los
drivers con cobertura `OK`, desempate determinista D1→D6 y `NULL` si ninguno es elegible. El pipeline
la prefiere y conserva `driver_dominante_proxy` como fallback para fixtures o fuentes anteriores.

La etiqueta sigue siendo derivada de los mismos drivers, no un ground truth observado de forma
independiente. Por ello, F1 mide la capacidad de reproducir esa regla operativa y no evidencia causal.

## Explicabilidad

`calcular_shap_batch()` calcula contribuciones mediante `TreeExplainer` y `explicar_driver()` las
transforma al contrato acordado para Célula 4. El benchmark local calculó 100 filas en 0.67 s;
`KernelExplainer` no es viable para las 45 mil escuelas del ciclo vigente.

El job `publicar_gold --con-shap` persiste `shap_d1`…`shap_d6` como columnas nullable de
`gold.recomendaciones`. Un driver excluido por falta de cobertura queda en `NULL`, nunca en `0.0`:
cero significa contribución nula, mientras `NULL` significa que no pudo calcularse. La migración de
la tabla existente es idempotente. SHAP vive en `requirements/celula-3.txt`, fuera del camino
crítico del CI base, y se calcula en batch; la API sólo lee los valores persistidos.

## Validación

El 26 de agosto se validó el flujo completo de registro contra un backend SQLite temporal de MLflow
3.15.1: el entrenamiento creó una corrida y registró `ML02_DriverClasificador` versión `1`. Esto
confirma el código cliente y el Registry local; el identificador de corrida es efímero y cambia en
cada ejecución. Aún falta repetir la prueba contra el servidor Docker compartido para cerrar la
validación end-to-end de infraestructura.

Pruebas agregadas en `tests/test_entrenar_ml02.py`:

- derivación de `driver_dominante_proxy` sin convertir `SIN_DATO` en cero;
- rechazo de filas sin ningún driver observado;
- backtesting temporal sin fuga;
- métricas acotadas en `[0,1]`;
- salida con `cct`, `id_ciclo`, `driver_dominante` y `recomendacion`.
- contrato de explicación SHAP con contribuciones `D1`…`D6`;
- publicación de una recomendación por escuela y ciclo en Gold;
- dos escuelas con igual riesgo y distinto driver reciben recomendaciones distintas;
- nombre MLflow canónico de ML-02.
- preferencia del target real y rechazo temprano de etiquetas nulas, desconocidas o monoclase.
- paridad entre la etiqueta de Gold y el proxy Python.
- regresión de BUG-018: un driver vacío en el entrenamiento de una ventana no rompe sklearn y queda
	registrado como excluido; la predicción usa las mismas columnas con las que se entrenó el modelo.

## Pendientes para cerrar US-302

- Correr y registrar métricas sobre `gold.features_escuela` real después de fusionar BUG-018.
- Validar el Registry contra el servidor Docker compartido cuando el entorno local tenga las
	variables de Compose configuradas; el Registry local con MLflow 3.15.1 ya fue verificado.
- Conectar la explicación SHAP completa al endpoint `/predicciones/{cct}/explicacion` de Célula 4.
