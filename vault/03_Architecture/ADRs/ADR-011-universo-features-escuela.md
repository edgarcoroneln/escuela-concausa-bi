---
id: ADR-011
title: "ADR-011 — Universo canónico de features y hecho central"
owner: "Deni Garrido Fragoso"
status: accepted
traces_up: ["REQ-001", "REQ-002", "REQ-003"]
traces_down: ["US-104", "US-112", "US-113", "US-311", "US-313", "vault/03_Architecture/Data_Model"]
supersedes: []
tags: [architecture, adr, gold, ml, celula-1, celula-3]
date: "2026-09-05"
---

# ADR-011 — Universo canónico de features y hecho central

## Contexto

`gold.fact_escuela_ciclo` ya restringe los hechos observados a los CCT de
`gold.dim_escuela` (DS-02) y toma de ahí `cve_mun`. En cambio,
`gold.features_escuela` usaba el CCT y `cve_mun` de `silver.matricula` (DS-01).
Con los datos reales había 1,168 CCT×ciclo en features, recomendaciones y predicciones que no
existían en el hecho central: las salidas ML no podían aparecer en los cubos que parten de él.

La excepción DS-01 estaba documentada como simplificación, pero viola la relación 1:1 entre
features y hecho central declarada en `Data_Model.md`. No existe un ADR previo que la formalice,
por lo cual esta decisión no supersede un identificador: sustituye esa excepción documentada.

## Decisión

`gold.features_escuela` y `gold.fact_escuela_ciclo` tendrán el mismo universo de llaves
`(cct, id_ciclo)`. Ambos usarán `gold.dim_escuela` como autoridad de pertenencia a Gold y de
`cve_mun`; DS-01 aporta la matrícula y el target, pero no incorpora CCT sin catálogo DS-02.

## Alternativas consideradas

| Opción | Pros | Contras |
|---|---|---|
| Alinear features con `dim_escuela` (aceptada) | Garantiza que ML, hechos y cubos representan el mismo universo y municipio canónico | Excluye temporalmente CCT que DS-02 aún no cataloga |
| Mantener features desde DS-01 | Maximiza las filas disponibles para entrenamiento | Publica salidas que no pueden consumirse en Gold ni en los tableros |
| Ampliar `dim_escuela` desde DS-01 | Conservaría los CCT de matrícula | Inventaría atributos de catálogo y cambia la autoridad de DS-02 sin validación de la fuente |

## Consecuencias

- C1 regenera features y el hecho central con paridad obligatoria por `(cct, id_ciclo)` y
  `cve_mun` canónico.
- C3 no cambia su código ni el esquema de sus tablas; sus salidas se republican desde el universo
  alineado mediante un vaciado controlado de datos, no mediante `DROP TABLE`.
- La brecha de catálogo DS-02 permanece visible: debe corregirse en la fuente/carga si se requiere
  incorporar esos CCT en una corrida futura.
- Cambiar de nuevo el universo o la autoridad de `cve_mun` requiere ADR y revisión C1/C3.

## Trazabilidad

- Requisitos: REQ-001, REQ-002, REQ-003.
- Impacta: `gold.features_escuela`, `gold.fact_escuela_ciclo`, `gold.predicciones`,
  `gold.recomendaciones`, cubos Gold y [[vault/03_Architecture/Data_Model]].
