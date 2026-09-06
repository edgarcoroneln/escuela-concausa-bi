---
project: "FARO"
date: "2026-09-06"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — parte de C4 de DEC-019: separar el ancla de la línea de alerta en la API"
touches: ["DEC-019", "DEC-006", "BUG-058", "US-215a", "US-204", "REQ-002"]
tags: [devlog, celula-4, api, kpi, umbral, dec019, bug058]
---

# DevLog — 2026-09-06 — Parte de C4 de `DEC-019`: la línea de alerta del KPI-04

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register|BUG-058]] ·
[[vault/03_Architecture/API_Specification|API_Spec §3.3]]

## Contexto

`BUG-058` (Marina García, C2): el KPI-04 «escuelas en riesgo» daba **0 por construcción**. El corte
`indice_riesgo >= 0.6` (`DEC-006`, = perder 5 % de matrícula) queda por encima del techo del
fenómeno en educación básica — el máximo que ML-01 predice sobre el Gold real de producción es
**0.5717** (perder 4.53 %).

`DEC-019` separa dos números que hasta hoy eran el mismo `0.60`:

- **Ancla de calibración (0.60)** — qué *significa* el índice. **No cambia**: moverla reinterpreta
  todos los índices ya publicados.
- **Línea de alerta (0.50)** — cuándo *enciende* la alerta. Criterio de negocio.

El `0.50` sale de la medición de Marina: equivale a perder 3.4 %, justo por debajo del 3.7 % de
deserción real en secundaria, así que la alerta enciende **antes** de que la escuela alcance la
norma nacional — que es lo que significa "temprana". Bajar más diluye: 0.40 marcaría el 26 % del
universo y 0.35 el 55 %. Con 0.50 son **7 escuelas de 45,276**: una lista accionable.

El filtro de `src/api/repositorio_gold.py` es alcance C4, así que esta es mi parte.

## Qué se hizo

- **`repositorio_gold.py`** — `ANCLA_SIGMOIDE = 0.60` y `LINEA_DE_ALERTA = 0.50` declaradas con su
  porqué; el filtro usa la constante en vez del literal. El ancla se declara **aunque la API no la
  use en ningún cálculo**, para que quede a la vista que son dos números distintos.
- **`v1/gold.py`** y el docstring de `obtener_kpis` — decían "umbral 0.6 ratificado", que ya no
  describe el sistema.
- **`mock_data.py`** — contaba con `>= 0.5` mientras el repositorio real usaba `0.6`. **Esa
  incoherencia ya existía y nadie la había notado**: el contrato mentía en las pruebas. Ahora
  importa la constante.

## El hallazgo: mi cambio no puede ir solo, y lo demuestro con una prueba

Escribí `tests/test_linea_de_alerta.py` para fijar la separación de los dos números, y le añadí una
tercera sección que **lee los `.sql` de dbt y compara el corte con el de la API**. Al correrla,
reprobó las cinco:

```
dbt/models/gold/cubo_riesgo_territorial.sql cuenta con [0.6] y la API con 0.5
```

Es decir: el mismo corte está hardcodeado en **cinco archivos de dbt** —tres cubos y dos pruebas de
paridad— donde alimenta columnas **materializadas**. Y son ésas, no la constante de Python, las que
leen los tableros de Superset.

**Consecuencia:** `/kpis` calcula sobre `gold.predicciones` en cada petición, así que con mi cambio
reporta 7; los tableros leen la columna materializada y siguen reportando 0. **Hasta que C1
re-materialice Gold, las dos pantallas dicen cosas distintas para la misma pregunta.** Marina lo
había advertido en su mensaje; esta prueba lo vuelve verificable en vez de una advertencia.

La prueba **se salta con un motivo explícito** mientras dbt siga en 0.6, y **se activa sola** en
cuanto C1 cambie el archivo: a partir de ahí exige que ambos coincidan. No es una excepción
permanente; es un acoplamiento declarado.

Mismo criterio que usó Marina al **no** tocar la anotación de umbral de la capa semántica: cambiar
el metadato antes que el dato lo vuelve mentira.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** `tests/test_linea_de_alerta.py` (12 casos), este DevLog.
- **Modificados:** `src/api/repositorio_gold.py`, `src/api/v1/gold.py`, `src/api/mock_data.py`,
  `vault/_DevLog/_index.md`.

## Seguridad / calidad

- [x] 12 casos nuevos; 7 verdes y 5 saltados **por la divergencia real de dbt**, con el motivo escrito
- [x] `ruff check .` sobre todo el repo → limpio
- [x] Suite completa: mismas 4 fallas que `main` en esta máquina (deps de C1/C3 ausentes del venv)
- [x] `test_no_hay_cubos_nuevos_con_el_corte` vigila que no aparezca un sexto archivo sin registrar

## Bloqueantes / avisos a otros owners

- **⚠️ No mergear esto antes de que `DEC-019` esté firmada por el PO.** El número lo decide producto,
  no C4; yo ejecuto el filtro. Al momento de escribir esto, `DEC-019` **no está** en el
  `Decision_Log`.
- **C1 (dbt) — el acoplamiento:** hay que cambiar el corte en `cubo_riesgo_territorial.sql`,
  `cubo_comparador_municipio.sql`, `cubo_escuela_360.sql` y las dos pruebas de paridad, **y correr
  `dbt run`**. No hay `var` de dbt para esto: son cinco literales. Mientras no ocurra, `/kpis` y los
  tableros cuentan distinto.
- **Marina García (C2):** tu medición es la que sostiene el 0.50; mi parte solo la ejecuta. Las
  constantes están duplicadas entre `src/api/repositorio_gold.py` y `src/frontend/prediccion_client.py`
  porque la dependencia va del front a la API y no al revés — la prueba nueva las compara para que
  no se separen.
- **Follow-up post-freeze:** que el corte salga de **una sola fuente** (una `var` de dbt alimentada
  desde la misma constante) en vez de estar escrito en ocho sitios de cuatro células.

## Próximos pasos

1. Firma de `DEC-019` por el PO.
2. C1 cambia los cinco `.sql` y corre `dbt run` — antes o a la vez que el despliegue de la API.
3. Redeploy (sigue pendiente desde hace días; la API en producción está en `33fcbbb`).
