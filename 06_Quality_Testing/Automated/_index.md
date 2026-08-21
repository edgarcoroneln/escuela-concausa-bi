---
id: MOC-06-AUTO
title: "Automated Testing"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
tags: [moc, qa, automation]
---

# Pruebas Automáticas

> Unit, integración y E2E. Cada caso usa [[_Templates/Test_Case_template]].
> → [[06_Quality_Testing/_index]]

## Suites
| Suite | Nivel | Ruta en repo | Comando | Corre en |
|---|---|---|---|---|
| Partición temporal y fixture ML-01 | unit | `tests/test_particion_temporal.py` | `pytest tests/ -q` | CI |
| | integración | | | CI |
| | e2e | | | nightly |

## Registro de casos (TEST-###)
| TEST | Valida (REQ/US) | Tipo | Estado |
|---|---|---|---|
| TEST-001 | REQ-001 | unit | draft |
| TEST-002 | US-004 · REQ-007 | integración | implemented |
| [[06_Quality_Testing/Automated/Particion_Temporal_ML01\|TEST-003]] | US-311 · REQ-003 · AC-003.3 | unit | implemented |
| [[15_ML_Models/Indice_Riesgo_ML01\|TEST-004]] | US-311 · REQ-003 · US-401 (contrato API) | unit | implemented |
| [[15_ML_Models/ML01_Entrenamiento\|TEST-005]] | US-311 · REQ-003 · AC-003.2/003.3 | unit | implemented |
| [[15_ML_Models/Publicacion_Gold\|TEST-006]] | US-313 · REQ-003 · DEC-005 | integración | implemented |
| [[06_Quality_Testing/Automated/Evaluacion_Modelos\|TEST-007]] | US-312 · REQ-003 · AC-003.2 | unit | implemented |
| TEST-008 | US-104 · US-311 · REQ-001/003 | contrato | implemented |
| [[15_ML_Models/Target_Hibrido\|TEST-009]] | US-311 · US-313 · DEC-007 · RISK-007 | unit | implemented |
| [[06_Quality_Testing/Automated/Great_Expectations_DS05_Sinaica\|TEST-010]] | US-123b · REQ-001 | data quality | implemented |

`TEST-002` ejecuta `python3 _Meta/scripts/validate_pm_dashboard.py .` y verifica 87 US únicas,
21 personas, usuarios GitHub no duplicados, cobertura exacta de US por integrante, conteos de PR
válidos, ocho fuentes, rúbrica de 10 puntos, estados válidos, evidencia para Done y las once vistas
requeridas, incluidas **Equipo** y el plan seleccionable por célula/persona. También exige la fecha
canónica y los elementos visibles de la cuenta regresiva de entrega. Es determinista y no usa red.

`TEST-003` valida el fixture simulado de `gold.features_escuela` contra su contrato y, sobre todo,
que la partición de ML-01 sea **temporal y nunca aleatoria** (AC-003.3): incluye un caso que baraja
el fixture y exige que la verificación de fuga lo rechace. Determinista y sin red.

`TEST-004` (`tests/test_riesgo.py`, 16 casos) valida la conversión de la variación de matrícula
predicha por ML-01 al `indice_riesgo` ∈ [0,1]. Incluye un caso que construye un `PrediccionOut`
real de la Célula 4: si alguien recalibra la sigmoide fuera de rango, el CI lo detiene antes de que
falle la API. Su especificación vive en [[15_ML_Models/Indice_Riesgo_ML01]].

`TEST-007` (`tests/test_evaluar.py`, 13 casos) respalda
[[06_Quality_Testing/Automated/Evaluacion_Modelos]], que **se genera desde el código** con
`python -m src.modelos.evaluar` y no se edita a mano. La prueba clave verifica que el reporte sea
determinista: así las cifras publicadas en el vault no pueden divergir de las que produce el
pipeline, que es lo que AC-003.2 exige al pedir métricas reproducibles.

`TEST-008` (`tests/test_contrato_features.py`, 4 casos) vigila el contrato
`gold.features_escuela` entre la Célula 1 y la Célula 3: compara el modelo dbt de US-104 contra el
espejo Pydantic `src/modelos/contrato.py`. El `Data_Model` §5.3 exige avisar antes de cambiar
columnas; esta prueba lo hace cumplir, de modo que un renombre falle en el CI y no al entrenar
ML-01. Lee los archivos de dbt como texto, sin `yaml` ni `dbt`, para no depender de paquetes que
el CI no instala.

`TEST-009` (`tests/test_target_hibrido.py`, 18 casos) cubre la agregación del target híbrido de
DEC-007. La prueba central es `test_no_cuenta_la_ausencia_como_cero`: al promediar los drivers de un
municipio, una escuela sin dato queda fuera del cálculo en vez de arrastrar el promedio hacia cero.
Un `fillna(0)` antes del promedio hace fallar la prueba.

`TEST-010` (`src/ingesta/validacion_sinaica.py`) es la primera suite de Great Expectations real del
proyecto (GE 1.21, API declarativa). Valida Bronze de DS-05 SINAICA y ya encontró un hallazgo real:
~6.3% de las estaciones traen coordenadas inutilizables (nulo genuino o el placeholder `"0.0"` de
SINAICA), relevante para la interpolación IDW de `US-105`. Ver
[[06_Quality_Testing/Automated/Great_Expectations_DS05_Sinaica]] para el detalle y cómo reproducir.

## Convenciones
- Nombrar tests por comportamiento, no por implementación.
- Tests deterministas; sin dependencias de red reales (usar mocks/emuladores).
- Todo bug corregido añade su test de regresión.
