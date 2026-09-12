---
id: DOC-ML03-PREFLIGHT-US631
title: "US-631 — Preflight de integración segura de ML-03"
owner: "Estefany Lucero Hernández Loredo"
status: draft
source_of_truth: false
traces_up: ["US-631", "REQ-003", "RISK-011", "DOC-ML03-RISK011-GATE"]
traces_down: ["vault/15_ML_Models/ML03_RISK011_Gate", "src/modelos/preflight_ml03.py"]
tags: [ml, ml-03, preflight, cobertura, risk-011, sprint-7]
---

# US-631 — Preflight de integración segura de ML-03

> Este documento ejecuta la compuerta canónica [[vault/15_ML_Models/ML03_RISK011_Gate]]. No cambia
> la decisión sobre RISK-011 ni sustituye la evidencia histórica del 8-sep-2026.

## Diagnóstico consolidado

ML-03 no está bloqueado por D5/D6 para el vector candidato D1-D4. Está bloqueado por una cadena de
gobernanza e integración: la variante debe quedar sincronizada y revisada, MLflow debe tener una
verdad recuperable, y después debe existir la ruta Gold → API → Panel → QA.

| Hecho verificable | Consecuencia para US-631 |
|---|---|
| D5 usa metadata de 180 presas (`cap_name`/`cap_namo`) sin ubicación ni serie de volumen utilizable por escuela; BUG-030 sigue abierto. | D5 no puede incorporarse al estimador ni rellenarse. Requiere fuente/contrato de Datos antes de cualquier reentrenamiento de seis drivers. |
| D6 procede de estaciones SINAICA y sólo se acepta dentro del radio IDW de 15 km; gran parte del territorio carece de estación. | D6 debe seguir como `SIN_DATO` fuera del radio. Aumentar el radio sólo para elevar cobertura invalida ADR-006. |
| El corte histórico tiene 136,046 filas: 114,200 elegibles y 21,846 excluidas. | La exclusión que importa para D1-D4 debe reportarse por ciclo, entidad y driver antes de decidir operación. |
| La completitud convirtió disponibilidad de D6 en un cluster. | `indice_completitud_drivers` queda como auditoría y nunca como feature de KMeans en la variante D1-D4. |

## Estrategia de ML que sí es defendible

1. Usar exclusivamente D1-D4 en el estimador y `casos_completos` sólo para esas cuatro features.
2. Mantener D5/D6 y completitud como auditoría visible; nunca imputarlos a cero ni crear un cluster
   para ausencias.
3. Ejecutar el preflight con `generar_preflight()` contra el corte Gold aislado. Publicar sólo sus
   agregados: elegibilidad por ciclo/entidad y causas por driver.
4. Tras revisión del preflight, ejecutar exactamente `k=2..6` con una sola ventana temporal y
   reportar perfiles y `cluster × d6_cobertura`.
5. Medir ARI únicamente entre las cinco semillas fijadas y describirlo como estabilidad de
   inicialización, nunca como validación externa.

## Exclusiones obligatorias

| Elemento | Tratamiento | Motivo |
|---|---|---|
| `cct`, `cve_mun`, `id_ciclo`, `target_variacion_matricula` | Excluir del vector | Llaves, geografía y target introducen fuga o identidad. |
| `indice_completitud_drivers` | Auditoría, no feature | Evita repetir el sesgo de cobertura que originó RISK-011. |
| D5 | `SIN_DATO` explícito y fuera del vector | No existe contrato espacial/temporal de agua defendible. |
| D6 fuera de 15 km o sin lectura válida | `SIN_DATO` explícito y fuera del vector | La ausencia geográfica es real; no se corrige ampliando el radio. |
| Filas sin alguno de D1-D4 | Excluir y contabilizar | No se imputa hasta una decisión humana respaldada por evidencia temporal. |
| ARI o Silhouette | Métricas técnicas, no causalidad ni prioridad | No prueban eficacia de una intervención. |

## Plan de cierre por responsable

| Orden | Responsable | Entregable verificable | Criterio de salida |
|---|---|---|---|
| 1 | Estefany / E4 | Preflight agregado y revisión de #317 | SHA sincronizado, CI verde, vector y documentación sin contradicciones. |
| 2 | Estefany / E4 | Verificación MLflow | Experimento, parámetros D1-D4, métrica, artefacto descargable y carga exitosa; si falla, `run_id: null`. |
| 3 | Edgar | Decisión RISK-011 | Acepta la mitigación o conserva ML-03 como deuda; no se cierra por narrativa. |
| 4 | Diana / C1 | `gold.ml03_asignaciones` idempotente | Grano `cct × id_ciclo`, unicidad, `cluster >= 0`, versión y `run_id` trazables. |
| 5 | C4 | Lectura API desde Gold | Entero sólo para asignación válida; `null` para ausencia. |
| 6 | C2 + QA | Prueba E2E en candidata | Misma escuela/ciclo/versión en Gold, API y Panel; una elegible y una excluida. |

## Qué debe hacer Datos antes de aumentar cobertura

- **D5:** Emilio/C1 deben extraer volumen fechado y georreferenciado, definir el indicador de estrés
  hídrico y documentar su grano. La capacidad máxima de presa no sirve como proxy temporal.
- **D6:** Luis/C1 pueden ampliar cobertura únicamente incorporando estaciones y lecturas PM2.5
  válidas dentro del radio ya aprobado, con fecha compatible con cada ciclo. No se amplía el radio
  ni se asigna el valor municipal a escuelas lejanas.
- Cualquier nueva cobertura requiere reconstrucción aislada, comparación antes/después, reevaluación
  de ML-01/ML-02/ML-03 y revisión de regresión de recomendaciones, API y panel.

## Alcance de este PR de preflight

El código nuevo no descarga datos, no toca `src/ingesta`, `dbt`, `dags`, Gold, API ni frontend. Su
salida no contiene CCT y no registra MLflow. Su propósito es impedir que una falta real de datos se
convierta en imputación silenciosa o en un cierre documental prematuro.

→ [[vault/15_ML_Models/_index|Volver al índice]]
