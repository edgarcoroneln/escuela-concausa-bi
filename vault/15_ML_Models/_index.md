---
id: MOC-MLMODELS
title: "ML Models — Índice"
owner: "Andrés González Habib"
status: active
source_of_truth: true
tags: [index, moc, ml]
---

# 15_ML_Models — Modelos de Machine Learning

> El PRD exige **3 modelos de tipos distintos**: regresión/series, clasificación y no supervisado.
> Todos expuestos vía API.

## Los 3 modelos

| ID | Modelo | Tipo | Predice | Métrica | Estado |
|---|---|---|---|---|---|
| ML-01 | Regresión de matrícula | Supervisado · regresión | Variación de matrícula por escuela | MAE / RMSE | entrenado · cumple umbrales en fixture |
| ML-02 | Clasificación de driver | Supervisado · multiclase | Cuál de los 6 drivers explica el riesgo | F1 macro | en progreso |
| ML-03 | Clustering de escuelas | No supervisado | Grupos de perfil similar | Silhouette | entrenado · umbral no alcanzado en fixture |

**ML-02 es el corazón prescriptivo del proyecto**: permite que dos escuelas con el mismo riesgo
reciban recomendaciones distintas.

## Reglas de modelado no negociables

1. **Partición temporal, nunca aleatoria.** Una partición aleatoria produce fuga de información.
2. **Backtesting obligatorio.** Reportar la métrica real, no la de entrenamiento.
3. **Explicabilidad con SHAP** en ML-02. Sin explicabilidad no hay recomendación defendible.
4. **Cobertura parcial explícita.** Las features con `SIN_DATO` no se imputan con cero.
5. **Todo modelo se registra en MLflow** con parámetros, métricas y artefacto versionado.

## Documentos

| Artefacto | Descripción |
|---|---|
| [[vault/15_ML_Models/ML_Strategy]] | Estrategia de modelado, partición temporal, backtesting, schema de features, umbrales (US-301) |
| [[vault/15_ML_Models/Indice_Riesgo_ML01]] | Conversión de la variación de matrícula predicha por ML-01 al `indice_riesgo` ∈ [0,1] que consumen la API, los cubos y los tableros (US-311) |
| [[vault/15_ML_Models/ML01_Entrenamiento]] | Entrenamiento de ML-01, backtesting walk-forward, resultados y registro en MLflow (US-311) |
| [[vault/15_ML_Models/ML02_Clasificacion_Driver]] | ML-02 temporal: target proxy, contrato del target real, recomendaciones y SHAP (US-302) |
| [[vault/15_ML_Models/Agente_Guardrails_US304a]] | Guardarraíles y orquestación inyectable del agente: alcance, SQL de solo lectura y límite de filas (US-304a) |
| [[vault/15_ML_Models/Agente_Recuperacion_US304b]] | Capa RAG del agente, integrando ChromaDB y sentence-transformers para inyectar el esquema de Gold en el prompt (US-304b) |
| [[vault/15_ML_Models/Agente_Evaluacion_US323]] | Set de evaluación objetiva de 20 preguntas (válidas, fuera de alcance, inseguras) y pruebas automatizadas asociadas (US-323) |
| [[vault/15_ML_Models/Widget_Chat_US305]] | Widget Streamlit: cliente HTTP/JWT, historial, errores de autorización, rechazo visible y SQL auditable (US-305) |
| [[vault/15_ML_Models/Preguntas_Coordinacion_C3]] | Preguntas puntuales para desbloquear ML-02, MLflow/API y agente con C1, C4, C5 y compañeros de C3 |
| [[vault/15_ML_Models/Guia_Ejecucion_C3]] | Guía corta para instalar dependencias mínimas y correr pruebas/ML-02 localmente |
| [[vault/15_ML_Models/PR_Draft_Trabajo_Independiente_C3]] | Borrador de PR listo para pegar en GitHub con pruebas, alcance y bloqueantes |
| [[vault/15_ML_Models/Publicacion_Gold]] | Job batch que publica `gold.predicciones` y `gold.recomendaciones` con upsert idempotente (US-313) |
| [[vault/15_ML_Models/Target_Hibrido]] | Target híbrido de dos niveles: agregación a `municipio × nivel` para el objetivo, driver dominante a nivel escuela (DEC-007, mitiga RISK-007) |
| [[vault/15_ML_Models/ML01_Model_Card]] | Ficha de Modelo de ML-01: propósito, features de entrada, métricas obtenidas (MAE/RMSE), limitaciones y contexto de NO uso (US-324) |
| [[vault/15_ML_Models/ML02_Model_Card]] | Ficha de Modelo de ML-02: clasificación multiclase, driver dominante, F1/SHAP, coberturas y contexto de NO uso (US-324) |
| [[vault/15_ML_Models/ML03_Model_Card]] | Ficha de Modelo de ML-03: agrupamiento no supervisado (clustering), características usadas, silhouette score y fronteras (US-324) |
| [[vault/15_ML_Models/EDA_Features_US322]] | Diagnóstico reproducible, correlaciones y selección de variables sin fuga para ML-03 (US-322) |
| [[vault/15_ML_Models/Cobertura_Parcial_US325]] | Auditoría de `SIN_DATO`, completitud y concentración territorial por entidad y municipio (US-325) |
| [[vault/15_ML_Models/ML03_Entrenamiento_US321]] | KMeans temporal, selección de `k` por Silhouette y perfiles auditables; política provisional sin imputación (US-321) |
| [[vault/15_ML_Models/Plan_Cierre_Estefany_US321_US322_US325]] | Propuesta post-PR #197 y prompt maestro para llevar US-321/322/325 de fixtures a evidencia reproducible sobre Gold real |
