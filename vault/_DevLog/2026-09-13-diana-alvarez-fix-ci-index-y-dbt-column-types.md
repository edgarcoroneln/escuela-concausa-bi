---
title: "CI en rojo corregido: pipe sin escapar en _index.md + tipo INTEGER real en el seed dim_entidad (BUG-077)"
fecha: 2026-09-13
autor: Diana Aracely Alvarez Varela
herramienta: Claude Code / claude-sonnet-5
relacionado: [BUG-077, US-621, REQ-002]
---

## Contexto

El workflow "Calidad de código y vault" quedó en rojo (2 failed, 1243 passed) y llegó una
revisión real de alguien que corrió `dbt run --select dim_municipio` contra Postgres de
verdad. Dos hallazgos distintos, ambos reales, ninguno falso positivo.

## 1. Pytest: fila de `_index.md` con columnas desalineadas (error mío)

`test_toda_fila_del_indice_de_devlog_tiene_5_columnas` y
`test_todo_autor_del_indice_existe_en_el_padron` fallaban porque la fila que agregué hoy
(`fix-contorno-dominante-panorama`) escribió el wikilink sin
escapar el pipe interno: `[[ruta|fecha]]` en vez de `[[ruta\|fecha]]`. `table_cells()`
(`generate_pm_dashboard.py`) parte la fila por *todo* pipe no escapado -- exactamente el bug
que ya documenta su propio docstring (BUG-040, misma causa en `Execution_Status.md`) -- así
que el link se cortó en dos celdas, desplazó las 5 columnas reales a 6, y el texto del
resumen terminó leyéndose como "autor". Las otras 369 filas del archivo sí llevan el pipe
escapado; solo esa de hoy no. Corregido con el mismo patrón. Verificado con
`pytest tests/test_generate_pm_dashboard.py -k "..."` -- 2 passed.

## 2. dbt real: seed `dim_entidad` sin `+column_types` (hallazgo de revisión del PR)

`dbt_project.yml` configura `+schema: gold` para `dim_driver` en `seeds: faro:`, pero nunca
se agregó una entrada para `dim_entidad` (agregado ayer para BUG-077). Sin `+column_types`,
dbt infiere el tipo de `cve_ent` del CSV ("09", "15", "19", "14") como `INTEGER` -- pierde el
cero a la izquierda ("09" -> 9) -- y `dim_municipio.sql` compara ese valor contra
`substring(cve_mun, 1, 2)`, que es texto. El JOIN nunca llega a evaluarse: Postgres rechaza
la comparación de plano con `operator does not exist: integer = text`, el modelo no se
construye. **Los números 17/17 y 317/317 reportados ayer no pueden venir de este código tal
cual estaba** -- se corrigió agregando `dim_entidad: +schema: gold, +column_types: {cve_ent:
varchar(2)}`, mismo patrón que ya usa `dim_driver` (que no lo necesitaba porque "D1".."D6" no
son numéricos).

Actualizado `Bug_Register.md` (BUG-077) con la corrección explícita, sin borrar la nota
anterior -- para que quede claro que esos números necesitan volver a correrse de verdad.

## Pendiente

Correr `dbt seed --select dim_entidad --full-refresh && dbt run --select dim_municipio &&
dbt test --select dim_municipio` de verdad contra Postgres local (no disponible en este
entorno de ejecución) y pegar la salida real en el PR antes de que se vuelva a revisar.

## Verificación

`pytest tests/test_generate_pm_dashboard.py -k "..."` -- 2 passed (confirmado en este
entorno). `python3 -c "import yaml; yaml.safe_load(...)"` sobre `dbt_project.yml` -- OK.
`vault_lint.py` -- limpio, sin huérfanos nuevos. `git diff --check` -- limpio.
