---
id: DOC-ML01-CARD
title: "Ficha de Modelo: ML-01 (Regresión de Matrícula)"
owner: "Carlos Guillermo Mayorga Tapia"
status: in_review
source_of_truth: false
traces_up: ["US-324"]
tags: [ml, ml-01, regresion, model-card]
---

# Ficha de Modelo: ML-01 (Regresión de Matrícula)

> → [[vault/15_ML_Models/_index|Volver a _index]]

## 1. Propósito
El objetivo de **ML-01** es realizar una regresión supervisada para predecir el **riesgo de pérdida o variación de matrícula** por escuela (o por clúster municipio × nivel). Su salida no acotada es transformada posteriormente en un **índice de riesgo** acotado al intervalo `[0,1]`. Este es el primer nivel del target híbrido. (Ver: [[vault/15_ML_Models/Target_Hibrido]] y [[vault/15_ML_Models/ML_Strategy]]).

## 2. Features de Entrada
- ML-01 utiliza exclusivamente los **seis drivers normalizados** como entrada del estimador (`D1` a `D6` provenientes de `gold.features_escuela`).
- No utiliza features de escuelas sin datos consistentes (cobertura parcial respetada, sin imputar ceros a lo ciego).

## 3. Métrica Obtenida
- **Resultados actuales (sobre Gold real)**: Tras resolver el bloqueo por el error interno de `scikit-learn` (BUG-015), el modelo fue entrenado y evaluado exitosamente sobre datos reales (5 de septiembre).
- **Desempeño**: El modelo obtuvo un **MAE de 0.141458** y un **RMSE de 0.436326**, logrando superar al baseline (MAE de 0.159223) con una **mejora del 11.04 %**.
- **El umbral de aceptación sigue incumplido, y se declara**: `src/modelos/evaluar.py::UMBRALES` fija `ML-01_mae: 0.03`. La corrida real da **0.141458**, es decir **4.7× por encima del umbral**. Se reporta tal cual, con el mismo criterio que se aplicó al Silhouette de ML-03 en `US-312`: **un modelo que no alcanza su umbral no se presenta como si lo hiciera.** Lo que sí se puede afirmar, y no era cierto con pérdida cuadrática, es que le gana al baseline temporal por 11.04 %.
- (Ver detalle de entrenamiento: [[vault/15_ML_Models/ML01_Entrenamiento]]; declaración canónica del umbral incumplido: [[vault/15_ML_Models/Publicacion_Gold]] §9).

## 4. Limitaciones Conocidas
- Es sensible a datos históricos fuertemente ruidosos (outliers) generados por cierres temporales o errores en los censos anteriores.
- Al generar una predicción continua no acotada, requiere de una transformación posprocesamiento estricta para convertirse en un índice probabilístico consumible.

## 5. Contextos de NO Uso
- **NO usar a nivel individual (alumno)**. La granularidad de entrenamiento es la escuela o agregación por municipio × nivel. FARO no predice la deserción de alumnos individuales.
- **NO usar para estimaciones financieras** ni decisiones de presupuesto directo sin considerar los intervalos de confianza (MAE/RMSE), dado que es un modelo estadístico de variación, no un censo demográfico futuro.
- **Artefactos que lo consumen**: La salida de este modelo es consumida en el cubo `DB-06 Predicciones`.
