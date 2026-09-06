---
id: DOC-EDA-FEATURES-US322
title: "US-322 — EDA y selección de variables para ML-03"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
traces_up: ["US-322", "REQ-003", "vault/15_ML_Models/ML_Strategy"]
traces_down: ["US-321"]
tags: [ml, eda, features, celula-3]
---

# US-322 — EDA y selección de variables para ML-03

> Implementación reproducible: `src/modelos/analizar_features.py`.

## Alcance

El diagnóstico valida el contrato de `gold.features_escuela` sobre el fixture sintético y reporta:

- Nulos, cardinalidad y correlación de los seis drivers y `indice_completitud_drivers`.
- Matriz de correlaciones de las features; el target no se mezcla con las variables de clustering.
- Llaves y target excluidos del vector: `cct`, `cve_mun`, `id_ciclo` y
  `target_variacion_matricula`.
- Coherencia obligatoria entre valores ausentes y la bandera `SIN_DATO`.

## Selección inicial para ML-03

Las candidatas son los seis drivers, `indice_completitud_drivers` y los indicadores de disponibilidad
de D5/D6. La imputación se ajustará solamente con cada conjunto de entrenamiento; nunca se usará
cero para cubrir una ausencia.

`cve_mun` se conserva exclusivamente para auditar cobertura y perfilar resultados. No representa
una característica socioeconómica y meterla como número en KMeans introduciría una distancia
artificial entre claves administrativas.

## Limitación conocida

El fixture tiene 400 observaciones sintéticas de 80 escuelas y 5 ciclos. Sirve para verificar el
pipeline, no para declarar perfiles de negocio o resultados sobre escuelas reales.

## Criterio de salida

US-321 puede consumir estas variables después de revisar correlaciones y cobertura. La preparación
del pipeline puede avanzar, pero la imputación definitiva permanece pendiente de ratificar el
fallback para municipios sin suficientes observaciones.

Desde el PR #197, Bronze DS-01/DS-02 ya es reproducible y tiene suites de Great Expectations. Para
cerrar la limitación conocida todavía se debe reconstruir Gold y ejecutar este diagnóstico sobre
`gold.features_escuela`; ver
[[vault/15_ML_Models/Plan_Cierre_Estefany_US321_US322_US325]].

## Ejecución reproducible desde Gold

## Evidencia real — 2026-09-05

Se restauró el dump local `gold_bug048_final2_2026-09-05.sql` en la base aislada
`faro_gold_bug048_review_20260905_02`. El archivo no se versiona. Su SHA-256 es
`B8A3FC50A636A2943EB0BC25CBE495ED49914429A76838346E7EBCF6AAA5B32A`.

El ejecutor produjo únicamente agregados: 136,046 observaciones, 46,547 escuelas, 3 ciclos
(`2022-2023` a `2024-2025`) y cero duplicados en `cct × id_ciclo`. `cve_mun` estuvo disponible
para el diagnóstico municipal. Las llaves `cct`, `cve_mun`, `id_ciclo` y el target no entraron al
vector de clustering.

| Feature | Nulos | % nulos | Correlación con target |
|---|---:|---:|---:|
| `d1_pobreza` | 0 | 0.00% | -0.0133 |
| `d2_inseguridad` | 0 | 0.00% | 0.0158 |
| `d3_infraestructura` | 21,769 | 16.00% | 0.0133 |
| `d4_conectividad` | 21,654 | 15.92% | 0.0126 |
| `d5_agua` | 136,046 | 100.00% | no calculable |
| `d6_aire` | 134,272 | 98.70% | -0.0613 |
| `indice_completitud_drivers` | 0 | 0.00% | -0.0826 |

Reproducción: `src.modelos.ejecutar_cierre_ml03` con `DATABASE_URL` apuntando a la base aislada y
`--salida` en una ruta temporal. La evidencia confirma que D5 no puede participar en una selección
estadística sobre este corte; no se imputó ni se convirtió `SIN_DATO` en cero. El estado permanece
`in_review` hasta la revisión de Andrés y Edgar.

`python -m src.modelos.ejecutar_cierre_ml03` lee `gold.features_escuela` desde `DATABASE_URL` y
emite EDA y correlaciones agregadas sin incluir CCT individuales ni mezclar el target con el vector
de clustering. La ejecución real quedó verificada sobre dos dumps Gold equivalentes (`final1` y
`final2`) en bases locales aisladas; ambos produjeron las mismas cifras agregadas.

## Efecto de D5 y D6 en US-322

D5 y D6 no invalidan el EDA ni la selección de variables de US-322, pero sí cambian la interpretación
de la disponibilidad estadística:

- D5 (`d5_agua`) está 100% en `SIN_DATO`, por lo que no tiene varianza observable ni correlación
  calculable en este corte. Se conserva como señal de cobertura, no como feature imputada.
- D6 (`d6_aire`) tiene 98.70% de ausencia. Su correlación y cualquier patrón asociado deben leerse
  como evidencia parcial, nunca como perfil nacional completo.
- La ausencia total de D5 y la cobertura residual de D6 bloquean `casos_completos` para US-321;
  no bloquean el cierre analítico de US-322 ni obligan a imputar valores.

## Criterios de cierre de US-322

- [x] Contrato Gold validado sobre datos reales: grano, ciclos y duplicados.
- [x] EDA de nulos, cardinalidad y correlaciones documentado.
- [x] Llaves administrativas y target excluidos del vector de clustering.
- [x] `SIN_DATO` conservado explícitamente, sin convertirlo en cero.
- [x] Evidencia reproducible y agregada, sin CCT individuales en el artefacto.
- [ ] Revisión técnica de Andrés González Habib.
- [ ] Aprobación de Edgar Coronel y actualización final del estado a `done`.

US-322 puede cerrarse de forma independiente de US-321. El estado del documento permanece
`in_review` hasta completar las dos revisiones humanas exigidas por el flujo del vault.
