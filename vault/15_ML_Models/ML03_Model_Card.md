---
id: DOC-ML03-CARD
title: "Ficha de Modelo: ML-03 (Clustering de Escuelas)"
owner: "Carlos Guillermo Mayorga Tapia"
status: in_review
source_of_truth: false
traces_up: ["US-324", "US-321", "US-631", "REQ-003"]
tags: [ml, ml-03, clustering, no-supervisado, model-card]
---

# Ficha de Modelo: ML-03 (Clustering de Escuelas)

> → [[vault/15_ML_Models/_index|Volver a _index]]

## 1. Propósito
El objetivo de **ML-03** es un agrupamiento no supervisado (clustering) para encontrar perfiles similares de escuelas. Se utiliza para identificar bolsas de escuelas con problemáticas comunes independientemente de su región geográfica o su índice de riesgo directo de ML-01. (Ver: [[vault/15_ML_Models/ML_Strategy]]).

## 2. Features de entrada

- **Vector de la variante candidata (D1-D4):** `d1_pobreza`, `d2_inseguridad`,
  `d3_infraestructura` y `d4_conectividad`. Es exactamente `FEATURES_ML03` en
  `src/modelos/entrenar_ml03.py`; todavía no es el vector canónico de `main`.
- **Exclusiones deliberadas:** `cct`, municipio, ciclo y target de ML-01 no participan.
  `indice_completitud_drivers` tampoco participa del vector -- la candidata propone retirarlo
  para responder a `RISK-011` (ver §3) y conservarlo sólo como atributo de auditoría de cobertura, nunca como
  feature de entrenamiento. D5/D6 tampoco: D5 no tuvo observaciones y D6 tuvo cobertura
  residual en la evidencia histórica. Su ausencia se conserva como auditoría, nunca se transforma
  en cero.
- **Preproceso:** `StandardScaler` y `KMeans` viven en el mismo pipeline. Cada scaler se ajusta
  sólo con ciclos anteriores a la ventana de validación.

## 3. Métrica obtenida y procedencia

- **Métrica principal:** coeficiente de **Silhouette** temporal.
- **Evidencia candidata (10-sep-2026, D1-D4):** `k=2`, **Silhouette = 0.4620526551**
  (`≈0.4621`), por encima de la referencia exploratoria de 0.30. Está pendiente de revisión
  técnica; no es una selección canónica.
- **Protocolo:** se entrenó con 2022-2023 y 2023-2024; se validó con 2024-2025. Se comparó
  `k=2..6`, sin selección aleatoria ni búsqueda adicional de semillas/algoritmos.
- **Cobertura:** 114,200 observaciones elegibles y 21,846 excluidas de 136,046; la exclusión se
  debe a ausencias en el vector operativo, no a D5/D6 de manera directa.
- **Estabilidad de inicialización:** ARI mínimo y promedio `1.0` entre las semillas 7, 21, 42, 84
  y 2026 -- reproducible con `evaluar_estabilidad_semillas()`
  (`src/modelos/entrenar_ml03.py`) y probado en `tests/test_entrenar_ml03.py`. No valida
  estabilidad temporal, territorial ni resultados de negocio.

La fuente numérica histórica canónica sigue siendo [[vault/15_ML_Models/ML03_Entrenamiento_US321]]
y [ML03_Evidencia_20260908.json](ML03_Evidencia_20260908.json). La comparación D1-D4 está en
[ML03_Comparacion_RISK011_20260910.json](ML03_Comparacion_RISK011_20260910.json) y se conserva
como evidencia candidata para revisión. El corte histórico (`k=3`, Silhouette `0.4644549058`,
vector D1-D4 + `indice_completitud_drivers`) permanece como registro histórico: su cluster 2
coincidía con las 1,648 observaciones elegibles con D6 disponible, por lo que no debe leerse como
un perfil sustantivo de escuela (`RISK-011`). Esta observación no convierte a D1-D4 en canónico.
El resultado histórico `0.1086` pertenece a un fixture/protocolo aún anterior y tampoco describe
la evidencia candidata.

### Cómo reproducir esta corrida

```bash
DATABASE_URL=postgresql://... python -m src.modelos.ejecutar_cierre_ml03 \
  --url "$DATABASE_URL" --estabilidad \
  --salida vault/15_ML_Models/ML03_Evidencia_<fecha>.json
```

`--estabilidad` agrega el bloque `estabilidad` (ARI entre semillas) al JSON de salida; se deja
opcional porque repite el entrenamiento una vez por semilla adicional. La comparación explícita
D1-D4 vs. D1-D4+completitud fue un análisis puntual para la revisión de RISK-011. Debe repetirse
sólo sobre el dump canónico y con el protocolo de la compuerta; no aprueba el vector ni permite
promoción por sí misma.

## 4. Limitaciones conocidas
- Carece de una "verdad absoluta" al ser no supervisado; los clústeres resultantes requieren interpretación y etiquetado de negocio (ej. "Escuelas rurales sin conectividad", "Escuelas urbanas saturadas").
- Sólo hay una ventana temporal disponible; no es un test externo independiente. La estabilidad
  entre semillas sí está medida (ARI 1.0, ver §3); la estabilidad entre ciclos no.
- La variante candidata retira `indice_completitud_drivers` del vector para responder a
  `RISK-011`, pero su mitigación no está aceptada ni el riesgo cerrado. Requiere revisión técnica
  de Estefany Hernández Loredo y decisión de Edgar Coronel.
- El registro MLflow no se pudo recuperar independientemente: `mlflow_run_id` es `null` y el
  registro está pendiente. Tampoco existe productor Gold, endpoint C4 ni exposición real en la
  UI. El resultado analítico no equivale a modelo productivo.

## 5. Contextos de no uso
- **NO usar para estimar series de tiempo** (ej. proyectar matrículas a futuro). Para eso existe ML-01.
- **NO usar para clasificar directamente el riesgo de un alumno**. Los clústeres agrupan condiciones estructurales, no el destino final de un estudiante individual.
- **NO recomendar intervenciones ni asignar prioridad/riesgo** a partir del número de cluster.
- **NO mostrar un cluster de cobertura como hallazgo de negocio** mientras `RISK-011` permanezca
  abierto.

## 6. Estado de integración

ML-03 tiene evidencia reproducible y una explicación para S7, pero permanece sin promoción:
`mlflow_run_id` es nulo para este corte y el Panel debe conservar `SIN_DATO`. La integración
posterior requiere un productor C3 aprobado, esquema Gold de C1 y lectura de C4, cada uno en su
propio PR y con revisión humana. La explicación de demostración está en
[[vault/15_ML_Models/ML03_Explicacion_US631]].
