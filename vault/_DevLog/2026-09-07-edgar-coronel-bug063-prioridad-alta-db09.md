---
project: "FARO"
date: "2026-09-07"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "revisión del PR #279 de C3: se responde la pregunta que escaló Héctor Morales y se registra BUG-063"
tags: [devlog, pm, bug-063, dec-019, db09, revision-pr, demo]
---

# DevLog — 2026-09-07 — BUG-063: la prioridad ALTA de DB-09 es inalcanzable por construcción

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register]] ·
[[vault/10_Risk_Governance/Decision_Log]] · [[vault/01_Product/Guion_Demo_US006]]

## Qué se hizo

Revisión del **PR #279** (Héctor Morales, C3 implementa `DEC-019`) y respuesta a la pregunta que
ese PR escala al PO.

El PR es correcto y entra sin reservas: renombra `RIESGO_UMBRAL` a `ANCLA_SIGMOIDE`, conserva el
alias, documenta la separación entre **ancla de calibración** (0.60) y **línea de alerta** (0.50), y
**no mueve un solo número** — `prioridad_de_riesgo()` cambia una constante por otra del mismo valor.
Su prueba `test_la_linea_de_alerta_equivale_al_menos_34_por_ciento` ata el *argumento de negocio* de
`DEC-019` a un fallo visible: si alguien recalibra la sigmoide creyendo que el ancla y la línea son
lo mismo, la equivalencia `0.50 ↦ −3.4 %` deja de ser cierta y la prueba lo dice.

## La pregunta que escaló, y por qué tenía más consecuencia de la que apuntó

Héctor documentó que **no** bajó el corte de `prioridad_de_riesgo` a 0.50, porque reescribiría la
columna `prioridad` de las 45 276 filas ya publicadas y `DEC-019` dice explícitamente que no cambia
un solo valor publicado. Hizo bien en no decidirlo solo.

Persiguiendo esa pregunta apareció lo que no estaba registrado: con el corte en **0.60** y un máximo
real de **0.5717**, **ninguna escuela es `ALTA`**. Y `db09_recomendaciones.yaml:51` expone una
tarjeta llamada literalmente **«Recomendaciones de prioridad ALTA»**, más un gráfico desglosado por
esa columna. En el tablero del diferenciador, la tarjeta que dice a qué escuelas entrar primero
muestra **cero**.

Es **`BUG-058` otra vez, en otra columna**: un corte de negocio por encima del techo del fenómeno.
`DEC-019` arregló el conteo del KPI-04 y no tocó `prioridad`.

**Por qué `BUG-054` no lo cazó:** ese bug corrigió la comparación de mayúsculas y se verificó contra
un fixture de ~55 filas donde sí había *«alta 2, media 29, baja 24»*. El fix es correcto; lo que
cambió es el universo — en 45 276 filas, ese 2 es 0. Es el mismo modo de falla que ya nos costó
antes: **una verificación sobre fixture que no se repite contra el dato real.**

## Decisión

**No se corrige antes del 9-sep.** Tres salidas evaluadas:

1. No mostrar DB-09 el miércoles — el guion no lo pide por nombre.
2. Alinear `prioridad` a la línea de alerta y republicar — coherente, pero reescribe 45 276 filas a
   dos días de la entrega y contradice `DEC-019`.
3. Dejarlo y **decirlo antes de que lo pregunten**, igual que con `escuelas_en_riesgo`.

**Se elige la (3).** Es la línea que el guion ya usa, no mueve el suelo bajo los números que se van a
mostrar, y convierte un hallazgo en una demostración de criterio en vez de en una sorpresa.

El fix de fondo —decidir si `prioridad` sigue el ancla de la sigmoide o la línea de alerta, que
desde `DEC-019` son dos cosas distintas— queda para después del 9, con C3 y el PO.

## Lo que queda pendiente

- **La línea del guion.** `Guion_Demo_US006.md` todavía no dice nada de la prioridad ALTA. Hay que
  agregarla a *«lo que decimos antes de que lo pregunten»*, junto con la corrección de
  `/explicacion` (ver abajo). Va en un cambio aparte.
- **`/explicacion` quedó desalineado con el guion.** Tras el `ALTER` de C5 (PR #280) las seis
  columnas `shap_d1..shap_d6` existen pero están en `NULL`, así que en producción el endpoint
  devuelve `SIN_DATO` hasta que C3 repueble el Gold con `publicar_gold.py`. El guion, editado el
  2026-09-06, afirma lo contrario: *«ya devuelve SHAP real… si sale la pregunta, se enseña»*.
  `BUG-053` sigue correctamente en `fixed` —el código sí lee las columnas reales— pero el dato no
  está. **Error del PO al redactar esa línea; pendiente de corregir antes del ensayo.**
- **La guarda propuesta en `BUG-063`**: una prueba que contraste el corte de la categoría más alta
  contra el máximo observado en el Gold publicado. Habría cazado `BUG-058` y éste.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** este DevLog; `BUG-063`.
- **Modificados:** `vault/_DevLog/_index.md`, `vault/02_Requirements/Traceability_Matrix.md`.
- **Verificado por el agente antes de escribir:** que `publicar_gold.py:197` compara contra
  `ANCLA_SIGMOIDE`; que la métrica `recomendaciones_prioridad_alta` ya usa `upper(prioridad)`
  (`metrics_db06_db09.yaml:217`, fix de `BUG-054`), así que el 0 no viene de ahí; que la tarjeta
  existe con ese nombre en `db09_recomendaciones.yaml:51`; y que el PR #279 no cambia comportamiento
  (`RIESGO_UMBRAL == ANCLA_SIGMOIDE == 0.60`), con 1064 pruebas en verde sobre el árbol fusionado.
- **Correcciones manuales:** pendientes de revisión humana.
