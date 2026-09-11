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

- **Vector vigente (D1-D4):** `d1_pobreza`, `d2_inseguridad`, `d3_infraestructura` y
  `d4_conectividad`. Es exactamente `FEATURES_ML03` en `src/modelos/entrenar_ml03.py`.
- **Exclusiones deliberadas:** `cct`, municipio, ciclo y target de ML-01 no participan.
  `indice_completitud_drivers` tampoco participa del vector -- se retiró para mitigar
  `RISK-011` (ver §3) y se conserva sólo como atributo de auditoría de cobertura, nunca como
  feature de entrenamiento. D5/D6 tampoco: D5 no tuvo observaciones y D6 tuvo cobertura
  residual en el corte canónico. Su ausencia se conserva como auditoría, nunca se transforma
  en cero.
- **Preproceso:** `StandardScaler` y `KMeans` viven en el mismo pipeline. Cada scaler se ajusta
  sólo con ciclos anteriores a la ventana de validación.

## 3. Métrica obtenida y procedencia

- **Métrica principal:** coeficiente de **Silhouette** temporal.
- **Corte vigente (10-sep-2026, D1-D4):** `k=2`, **Silhouette = 0.4620526551** (`≈0.4621`), por
  encima de la referencia exploratoria de 0.30.
- **Protocolo:** se entrenó con 2022-2023 y 2023-2024; se validó con 2024-2025. Se comparó
  `k=2..6`, sin selección aleatoria ni búsqueda adicional de semillas/algoritmos.
- **Cobertura:** 114,200 observaciones elegibles y 21,846 excluidas de 136,046; la exclusión se
  debe a ausencias en el vector operativo, no a D5/D6 de manera directa.
- **Estabilidad:** ARI mínimo y promedio `1.0` entre las semillas 7, 21, 42, 84 y 2026 --
  reproducible con `evaluar_estabilidad_semillas()` (`src/modelos/entrenar_ml03.py`), probada en
  `tests/test_entrenar_ml03.py`.

La fuente numérica canónica de este corte es
[ML03_Comparacion_RISK011_20260910.json](ML03_Comparacion_RISK011_20260910.json) y
[[vault/15_ML_Models/Propuesta_Cierre_ML03_D1_D4]]. El corte anterior (`k=3`,
Silhouette `0.4644549058`, vector D1-D4 + `indice_completitud_drivers`, documentado en
[[vault/15_ML_Models/ML03_Entrenamiento_US321]] y
[ML03_Evidencia_20260908.json](ML03_Evidencia_20260908.json)) queda **superado**: su cluster 2
coincidía exactamente con las 1,648 observaciones elegibles con D6 disponible -- completitud
separaba disponibilidad de dato, no un perfil real de escuela (`RISK-011`). Esos dos documentos
se conservan como registro histórico del corte del 8-sep, no como el estado vigente. El
resultado histórico `0.1086` pertenece a un fixture/protocolo aún anterior y tampoco describe la
corrida actual.

### Cómo reproducir esta corrida

```bash
DATABASE_URL=postgresql://... python -m src.modelos.ejecutar_cierre_ml03 \
  --url "$DATABASE_URL" --estabilidad \
  --salida vault/15_ML_Models/ML03_Evidencia_<fecha>.json
```

`--estabilidad` agrega el bloque `estabilidad` (ARI entre semillas) al JSON de salida; se deja
opcional porque repite el entrenamiento una vez por semilla adicional. La comparación explícita
D1-D4 vs. D1-D4+completitud detrás de `ML03_Comparacion_RISK011_20260910.json` fue un análisis
puntual (dos corridas de `entrenar_y_evaluar` con `FEATURES_ML03` distinto, más
`evaluar_estabilidad_semillas` para el bloque de estabilidad) hecho para decidir el retiro de
completitud -- no es una bandera del CLI, porque ya no hay una variante candidata que comparar:
el código sólo entrena D1-D4.

## 4. Limitaciones conocidas
- Carece de una "verdad absoluta" al ser no supervisado; los clústeres resultantes requieren interpretación y etiquetado de negocio (ej. "Escuelas rurales sin conectividad", "Escuelas urbanas saturadas").
- Sólo hay una ventana temporal disponible; no es un test externo independiente. La estabilidad
  entre semillas sí está medida (ARI 1.0, ver §3); la estabilidad entre ciclos no.
- `RISK-011` tiene **mitigación técnica implementada** (se retiró `indice_completitud_drivers`
  del vector, eliminando el cluster equivalente a disponibilidad de D6), pero su **cierre formal
  sigue pendiente** de revisión técnica de Estefany Hernández Loredo y decisión de Edgar Coronel.
  Mientras `RISK-011` no se cierre formalmente en `vault/10_Risk_Governance/Risk_Register.md`, no
  se debe presentar el resultado como aprobado para producción.
- No existe aún una corrida MLflow aprobada para producción, productor Gold, endpoint C4 ni
  exposición real en la UI. El resultado analítico no equivale a modelo productivo.

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
