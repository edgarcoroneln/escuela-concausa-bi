---
id: DOC-RISKREG
title: "Risk Register"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
source_of_truth: true
tags: [risk, register]
---

# Risk Register — FARO

> → [[vault/10_Risk_Governance/_index]]

| RISK | Descripción | Prob. (1-5) | Impacto (1-5) | Respuesta | Mitigación | Disparador | Dueño | Estado | US relacionada | Fecha objetivo |
|---|---|---:|---:|---|---|---|---|---|---|---|
| RISK-001 | Sin URL pública viva al evaluar: techo de 6.0 | 3 | 5 | mitigar | Deploy temprano y healthcheck verificable en S1 | US-501 no tiene evidencia el 9 ago | Luis Téllez Domínguez | cerrado | US-501 | 2026-08-09 (URL viva) |
| RISK-002 | Una o más fuentes resultan inservibles | 4 | 4 | mitigar | 6/8 fuentes probadas con extractor real (DS-04/05 por Luis, PR #47; DS-01/02/03/07 vía DAG); **faltan DS-06 CONAGUA y DS-08 CONAPO** (Emilio, US-121a/122a en `planned`) | descarga, esquema o llave fallan | Diana Aracely Alvarez Varela | mitigando | US-121a, US-121b, US-122b | 2026-08-16 (fin S2) |
| RISK-003 | Participación concentrada o contribución no auditable | 3 | 3 | mitigar | PR, reviews y DevLogs; sin ranking de commits | persona sin evidencia durante 7 días | Edgar Edmundo Coronel Navarrete | abierto | US-004 | Continuo |
| RISK-004 | Retraso de Gold bloquea BI, ML y API | 4 | 5 | mitigar | Contratos, mocks y fixtures; escalamiento a 24 h | US-103/104 se desvía del gate S3 | Diana Aracely Alvarez Varela | cerrado | US-103, US-104, US-105 | 2026-08-19 (Gold entregado: dim/fact + features, PR #48/#52) |
| RISK-005 | Sobre-alcance geográfico o funcional | 3 | 4 | evitar | Respetar `SCOPE_ENTIDADES` y congelar alcance | nueva entidad/feature sin decisión registrada | Edgar Edmundo Coronel Navarrete | mitigando | — | Continuo |
| RISK-006 | El vault pierde trazabilidad con 21 contribuidores | 3 | 4 | mitigar | linter, steward, matriz y generador validado — **las cuatro operativas desde 2026-09-05**: el steward existía sólo en el plan hasta que US-005 creó [[vault/_Meta/Vault_Steward]] con lista de verificación y turnos; los hallazgos de S5 están en ese documento | link roto, ID duplicado o artefacto huérfano | Edgar Edmundo Coronel Navarrete | mitigando | US-004 | Continuo |
| RISK-007 | Formato 911 solo tiene el ciclo 2024-2025: sin ≥2 ciclos no hay `target_variacion_matricula` que predecir (ML sin objetivo real) | 4 | 5 | mitigar | **Target híbrido de dos niveles (DEC-007):** target real multi-año a nivel `municipio × nivel` con la serie SNIEE de la SEP (misma fuente DS-01, agregada) + features y driver dominante a nivel escuela con el 911 2024-2025. **En paralelo:** perseguir el 2º ciclo crudo del 911 (2023-2024/2022-2023) para subir la granularidad del target a escuela. **Contingencia:** índice compuesto de riesgo desde los 6 drivers marcado `SIN_DATO_REAL` | Ni la serie SNIEE ni un 2º ciclo confirmados antes del gate ML (S4) | Edgar Edmundo Coronel Navarrete | mitigando | US-104, US-311, US-313 | 2026-08-30 (gate S4) |
| RISK-008 | `coneval_periodo_medicion = 2020` es un placeholder sin confirmar contra la fuente: ninguna tabla `coneval_*` trae año o período, así que el valor se decidió a mano en el ensayo E2E (PR #70). Si el año es incorrecto, `silver.rezago_municipio` etiqueta mal el período de medición del rezago social y el error se propaga a D1 y a todo lo que consume ese driver — **sin romper ningún build**. Sin confirmar tampoco cuál de las dos tablas es la buena: se eligió `coneval_v2` sobre `coneval_test` por inspección, no por confirmación del dueño | 3 | 4 | mitigar | **Deuda técnica aceptada explícitamente por el PM en DEC-011**, no cerrada en silencio: el valor está marcado como placeholder en el propio `dbt_project.yml`, en la sección Fix de BUG-009 y en el checklist de freeze de [[vault/03_Architecture/Data_Lineage_US106]]. Cierra cuando Deni confirme contra CONEVAL (a) el año de medición y (b) que `coneval_v2` es la tabla correcta. Si no alcanza, el freeze se declara con la deuda a la vista | Llega el 6-sep (freeze) sin confirmación de la dueña de DS-07 | Deni Garrido Fragoso | abierto | US-111, DS-07, BUG-009, DEC-011 | 2026-09-06 (freeze) |

## Escala
Probabilidad e impacto usan escala 1 (mínimo) a 5 (máximo). Severidad = `Prob. × Impacto`.
Respuesta: evitar / mitigar / transferir / aceptar. Estado: abierto → mitigando → cerrado → aceptado.
Los riesgos de seguridad enlazan a [[vault/07_Security/Threat_Model]].
