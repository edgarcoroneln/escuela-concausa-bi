---
id: DOC-EVALUACION-MODELOS
title: "Evaluación comparativa de modelos y análisis de error"
owner: "Héctor Rafael Morales Marbán"
status: in_review
traces_up: ["vault/02_Requirements/Requirements_Detailed", "vault/15_ML_Models/ML_Strategy"]
traces_down: ["US-312"]
tags: [qa, ml, celula-3, metricas]
---

# Evaluación comparativa de modelos y análisis de error

> **Documento generado por `src/modelos/evaluar.py`. No editar a mano.**
> Regenerar con `python -m src.modelos.evaluar`. Así las cifras del vault no se desincronizan de
> las que produce el pipeline, que es lo que exige AC-003.2 al pedir métricas *reproducibles*.
> → [[vault/06_Quality_Testing/Automated/_index]] · [[vault/15_ML_Models/ML01_Entrenamiento]] · [[vault/15_ML_Models/ML_Strategy]]

> [!warning] Métricas sobre datos sintéticos
> Se evalúa contra `tests/fixtures/features_escuela_mock.csv`. Las cifras validan que el pipeline
> de evaluación funciona; **no son resultados de negocio**. Se regeneran cuando la Célula 1
> publique `gold.features_escuela` (US-104).

## 1. Tabla comparativa

| modelo | tipo | metrica | valor | desviacion | baseline | mejora | ventanas |
|---|---|---|---|---|---|---|---|
| ML-01 | regresión | MAE | 0.0150 | 0.0007 | 0.0291 | 0.4851 | 3 |
| ML-02 | clasificación | F1 macro | 0.7731 | 0.0434 | 0.0534 | 13.8908 | 3 |
| ML-03 | no supervisado | Silhouette (k=2) | 0.1086 | 0.0454 | nan | nan | 3 |

Los tres optimizan cosas distintas —error absoluto, F1 y separación de grupos—, así que **sus
métricas no se comparan entre sí**. Entre ML-01 y ML-02 lo comparable es `mejora`: cuánto aporta
cada uno sobre su propio baseline; el que no lo supera no aporta nada, por buena que se vea su cifra.

**ML-03 no tiene baseline y por eso `mejora` va vacía**, no en cero. Es no supervisado: su
Silhouette mide qué tan separados quedan los grupos, no cuánto le gana a un modelo tonto. Ponerle un
cero lo haría parecer un modelo que no aporta, que es una afirmación distinta a "no aplica".

ML-02 se entrena hoy contra `driver_dominante`. Si es el proxy determinista, su F1 mide la capacidad
de recuperar una etiqueta derivada de los propios drivers, **no de predecir un driver observado**;
la cifra se vuelve significativa cuando Gold publique la etiqueta real.

## 2. Curva de error por ventana

| ventana | modelo | ciclo_prueba | metrica | valor | baseline | mejora | n_entrena |
|---|---|---|---|---|---|---|---|
| 1 | ML-01 | 2021-2022 | MAE | 0.0145 | 0.0294 | 0.5085 | 160 |
| 2 | ML-01 | 2022-2023 | MAE | 0.0145 | 0.0283 | 0.4881 | 240 |
| 3 | ML-01 | 2023-2024 | MAE | 0.0160 | 0.0295 | 0.4588 | 320 |
| 1 | ML-02 | 2021-2022 | F1 macro | 0.7475 | 0.0612 | 11.2094 | 160 |
| 2 | ML-02 | 2022-2023 | F1 macro | 0.7376 | 0.0556 | 12.2763 | 240 |
| 3 | ML-02 | 2023-2024 | F1 macro | 0.8342 | 0.0435 | 18.1867 | 320 |
| 1 | ML-03 | 2021-2022 | Silhouette | 0.0610 | nan | nan | 44 |
| 2 | ML-03 | 2022-2023 | Silhouette | 0.0950 | nan | nan | 63 |
| 3 | ML-03 | 2023-2024 | Silhouette | 0.1697 | nan | nan | 80 |

Es la "curva" de la historia en forma de datos: permite ver si el modelo se degrada conforme
predice ciclos más lejanos del inicio de la serie. Se emite como tabla y no como imagen porque un
diff de PR muestra exactamente qué métrica cambió; un PNG sólo se ve distinto. `--figuras` las
renderiza en local para la demo, sin versionarlas.

## 3. Error por entidad (ML-01, ventana de producción)

| entidad | escuelas | mae | desviacion_vs_global |
|---|---|---|---|
| 14 | 20 | 0.0183 | 0.1444 |
| 19 | 20 | 0.0171 | 0.0714 |
| 09 | 20 | 0.0167 | 0.0470 |
| 15 | 20 | 0.0118 | -0.2627 |

`desviacion_vs_global` es la diferencia relativa contra el MAE global de la ventana. La entidad con
peor desempeño es **14**, con MAE 0.0183
(+14.4% respecto al global).

Importa porque un error global aceptable puede esconder una entidad en la que el modelo funciona
mal, y las recomendaciones prescriptivas se emiten escuela por escuela.

## 4. Error contra cobertura de drivers

| tramo | escuelas | mae |
|---|---|---|
| ≤ 3 de 6 drivers | 3 | 0.0244 |
| 4-5 de 6 | 22 | 0.0130 |
| 6 de 6 | 55 | 0.0167 |

Responde la pregunta que el proyecto se hace explícitamente: **¿predecimos peor donde hay menos
datos?** Si el error crece al bajar la completitud, el sistema es menos confiable justo en las
zonas con cobertura parcial —y eso debe declararse junto a la predicción, no esconderse.

## 5. Drivers que entraron al modelo

| driver | ML-01 | ML-02 |
|---|---|---|
| d1_pobreza | entró | entró |
| d2_inseguridad | entró | entró |
| d3_infraestructura | entró | entró |
| d4_conectividad | entró | entró |
| d5_agua | entró | entró |
| d6_aire | entró | entró |

Los seis drivers tienen datos suficientes: **ningún driver quedó fuera**.

> [!important] Esta tabla describe **la corrida que generó este reporte**, no el estado de las
> fuentes en producción
> Hoy se genera contra `tests/fixtures/features_escuela_mock.csv`, que trae los seis drivers
> poblados a propósito. Que aquí digan "entró" **no significa que la fuente esté llegando**.
>
> Contra el Gold real la tabla será distinta, y ya se sabe en qué: `features_escuela.sql` fija
> `d5_agua = NULL` y `d5_cobertura = 'SIN_DATO'` de forma explícita, y ningún modelo Gold consume
> `silver.agua_region`. **Mientras ese enlace no se conecte, ML-01 entrenará con 5 de 6 drivers y
> D5 (agua) será el que quede fuera.** Regenerar este reporte contra `gold.features_escuela` (US-104)
> es lo que convierte esa afirmación en cifra publicada.

Un driver excluido **no es un ajuste técnico**: es una fuente que no está llegando. Aparece aquí, y
no sólo en la consola de quien entrena, porque es una cifra que el proyecto tiene que poder citar —
decir "el modelo entrena con 5 de 6 drivers" obliga a decir también cuál falta y por qué.

Los `SIN_DATO` de un driver que sí entró no se imputan: llegan al modelo como ausencia real
(`HistGradientBoosting` los maneja de forma nativa). Lo que se excluye es únicamente el driver que
no tiene **ningún** valor con el que aprender.

### 5.1 Exclusiones por ventana

Ninguna ventana de entrenamiento se quedó sin un driver: **todos tuvieron datos en todos los tramos** de esta corrida.

La cobertura se evalúa dentro de cada ventana de entrenamiento, no sobre el conjunto completo. La
distinción importa y tiene dueños distintos: un driver ausente en **todas** las ventanas es un hueco
de fuente que alguien debe ir a buscar; uno ausente sólo en las **más viejas** —porque su serie
apenas empieza— se resuelve solo conforme se carguen más ciclos.

## 6. Umbrales de aceptación

`vault/15_ML_Models/ML_Strategy` §5 fija: ML-01 MAE < 0.03 (3 puntos porcentuales) y
RMSE < 0.05 (5 puntos porcentuales); ML-02 F1 macro ≥
0.6; ML-03 Silhouette ≥ 0.3.

| modelo | metrica | valor | umbral | cumple |
|---|---|---|---|---|
| ML-01 | MAE | 0.0150 | < 0.03 | ✅ sí |
| ML-01 | RMSE | 0.0187 | < 0.05 | ✅ sí |
| ML-02 | F1 macro | 0.7731 | ≥ 0.6 | ✅ sí |
| ML-03 | Silhouette | 0.1086 | ≥ 0.3 | ❌ **no** |

> [!warning] Umbral no alcanzado: ML-03 (Silhouette = 0.1086)
> Está evaluado y reporta su métrica —que es lo que exige AC-003.2— pero **no llega al umbral de aceptación** de `ML_Strategy` §5. Reportarlo es parte del entregable: un modelo que no alcanza su umbral sobre el fixture sintético no puede presentarse como si lo hiciera, y la cifra tiene que volver a mirarse contra los datos reales de US-104.

ML-01 usa la misma unidad proporcional de `target_variacion_matricula`: `0.0141` equivale a un
error medio de 1.41 puntos porcentuales. No se convierte a alumnos porque el contrato de features
no incluye la matrícula base necesaria para hacerlo de forma reproducible. Los umbrales son
provisionales hasta ejecutar la evaluación contra los datos reales de US-104.

## 7. Cobertura de la evaluación

| Modelo | Estado |
|---|---|
| ML-01 · regresión | ✅ evaluado |
| ML-02 · clasificación | ✅ evaluado (target `driver_dominante`) |
| ML-03 · clustering | ✅ evaluado — `k=2`, Silhouette 0.1086 |

**Los tres modelos reportan su métrica**, que es lo que AC-003.2 exige. ML-03 entrena sobre 107 de 400 filas: 293 quedan fuera por la política `casos_completos`, porque KMeans no admite ausencias y **no se imputan** — la misma regla de cobertura parcial que rige el resto del pipeline. Esa exclusión es parte del resultado, no una limpieza previa: los grupos describen a las escuelas con datos completos, no al universo.
