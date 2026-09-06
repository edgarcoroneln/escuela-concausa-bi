---
id: DOC-COBERTURA-PARCIAL-US325
title: "US-325 — Sesgo por cobertura parcial en features"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
traces_up: ["US-325", "REQ-003", "vault/03_Architecture/ADRs/ADR-003-ml-estrategia-modelado"]
traces_down: ["US-321"]
tags: [ml, cobertura, sesgo, celula-3]
---

# US-325 — Sesgo por cobertura parcial en features

> Implementación reproducible: `src/modelos/analizar_features.py`.

## Qué se mide

El análisis entrega, por driver, el número y porcentaje de observaciones `SIN_DATO`, más las escuelas
afectadas. También desglosa cobertura y `indice_completitud_drivers` por entidad, derivada de los dos
primeros caracteres del CCT.

## Regla de interpretación

Una menor cobertura no equivale a un valor cero ni a menor riesgo. Cualquier diferencia sistemática
entre entidades debe reportarse antes de interpretar clusters como perfiles de intervención.

## Diagnóstico municipal preparado

El módulo valida `cve_mun` como clave INEGI de cinco dígitos, conserva ceros iniciales y comprueba
que pertenezca a la misma entidad que el CCT. No infiere el municipio desde la escuela. Produce
cobertura y completitud por municipio, además de la brecha entre los municipios con menor y mayor
porcentaje de `SIN_DATO` para cada entidad y driver.

La implementación queda desacoplada del cambio de esquema de Célula 1: funciona cuando la columna
está presente y falla con un mensaje explícito cuando todavía no ha sido publicada. Célula 1
entrega esa columna y su fixture desde su propio alcance, sin que este cambio copie trabajo ajeno.

No se asigna automáticamente una etiqueta de “sesgo”: todavía no existe un umbral aprobado. El
reporte cuantifica la concentración para que la interpretación sea auditable.

## Criterio de salida

La implementación queda lista para revisión con el fixture sintético. Para declarar US-325 `done`
se requiere integrar el contrato de Célula 1, reconstruir `gold.features_escuela` y ejecutar el
diagnóstico sobre Gold real. D5 seguirá identificado como cobertura parcial mientras falte el
crosswalk `region_hidrologica → cve_mun`.

El PR #197 ya resolvió la reproducción de Bronze DS-01/DS-02 y sus suites de calidad; el pendiente
es ahora una corrida Bronze → Silver → Gold y la evidencia agregada de cobertura real. Secuencia y
criterios: [[vault/15_ML_Models/Plan_Cierre_Estefany_US321_US322_US325]].

## Ejecución reproducible desde Gold

## Evidencia real — 2026-09-05

El dump `gold_bug048_final2_2026-09-05.sql` se restauró en la base local aislada
`faro_gold_bug048_review_20260905_02`; no se copia al repositorio. El corte tiene 136,046
observaciones, 46,547 escuelas, 3 ciclos y `cve_mun` disponible.

| Driver | Observaciones sin dato | % sin dato | Escuelas afectadas |
|---|---:|---:|---:|
| D1 · pobreza | 0 | 0.00% | 0 |
| D2 · inseguridad | 0 | 0.00% | 0 |
| D3 · infraestructura | 21,769 | 16.00% | 8,022 |
| D4 · conectividad | 21,654 | 15.92% | 7,984 |
| D5 · agua | 136,046 | 100.00% | 46,547 |
| D6 · aire | 134,272 | 98.70% | 45,952 |

El hallazgo principal es que D5 está completamente ausente y D6 tiene cobertura residual. Esto
impide interpretar clusters como perfiles completos del territorio y bloquea `casos_completos` de
ML-03. La sección municipal sí está disponible para continuar el análisis de concentración; no se
declara un umbral de sesgo ni se cambia el estado a `done` sin revisión humana.

`python -m src.modelos.ejecutar_cierre_ml03` produce agregados por driver, entidad y municipio,
incluida la dispersión municipal, sin exportar CCT individuales ni convertir `SIN_DATO` en cero.
Cuando `cve_mun` falta o contiene nulos, el reporte marca la sección municipal como bloqueada.

La prueba real permanece pendiente porque el ambiente usado el 4-sep-2026 no tenía Docker ni una
base Gold configurada; no se inventan cifras de cobertura ni se propone `status: done`.
