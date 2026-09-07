---
project: "FARO"
date: "2026-09-06"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "el par de demostración entra al guion, la excepción de freeze queda asentada y se registra el sesgo de escala del driver dominante"
tags: [devlog, pm, us-006, dec-020, bug-062, demo, guion, freeze]
---

# DevLog — 2026-09-06 — El par de demostración, DEC-020 y el sesgo de D6

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/01_Product/Guion_Demo_US006]] ·
[[vault/10_Risk_Governance/Decision_Log]] · [[vault/06_Quality_Testing/Bug_Register]]

## Qué se hizo

Tres cosas que venían de una entrega de Marina García del Buey (C2) y una revisión propia del guion.

### 1 · El par de demostración entra al guion (US-006)

`15DPR0920D` y `15DPR2254O`, las dos primarias en Ecatepec de Morelos, con `indice_riesgo`
**idéntico al cuarto decimal (0.4774)** y driver dominante distinto — D4 conectividad contra D2
inseguridad. Se acepta el par tal como lo propuso C2 y por su razón: el bloque tiene que **aislar
una sola variable**, y con mismo municipio, mismo nivel y mismo riesgo no queda ninguna otra
explicación disponible para la diferencia de recomendación.

Se descartó la alternativa por encima de la línea de alerta (`15EES1468A` / `15EPR0628Y`, Toluca)
porque son de distinto nivel y distinto riesgo: dos variables extra a las que atribuir la
diferencia, justo lo que el bloque quiere descartar.

### 2 · Tres lugares del guion contradecían a `main`

El primero lo reportó C2: la celda del minuto 5:00–6:30 anunciaba `escuelas_en_riesgo` = 0, y con
`DEC-019` son **7 de 45 276**. Los otros dos los encontró esta revisión y **no estaban en el
reporte**:

- *Lo que decimos antes de que lo pregunten*, punto 1, repetía el mismo 0 con el argumento viejo
  del −4.53 % contra el umbral de −5 %.
- El punto 2 seguía declarando `/explicacion` sin SHAP citando `BUG-053`, que está **`fixed`**
  desde el 2026-09-05 (Christian Ruiz): el endpoint lee `gold.recomendaciones.shap_d1..shap_d6` a
  través de `RepositorioModelos`. El guion pedía disculpas por algo que ya funciona.

Se agregó además la respuesta a la pregunta que el par nuevo abre y que nadie había escrito: **el
par está en 0.4774, debajo de la línea de alerta de 0.50**. No es contradicción —la línea es
*triage*, la recomendación es prescriptiva y se deriva del driver, exista o no alerta— pero esa
frase tiene que estar preparada, no improvisada en la sala.

### 3 · `DEC-020` — la excepción de freeze, y un ID reciclado

La excepción acotada al CODE FREEZE se anunció al equipo como *DEC-019*. Ese ID ya lo ocupaba la
línea de alerta del KPI-04, que entró antes a `main`. Se asienta como **`DEC-020`** en vez de
reciclar el número (regla 3; mismo criterio de `DEC-013`), y se deja dicho que la ambigüedad ya se
había propagado a un documento de C2 — corregirlo en silencio habría dejado dos cosas con el mismo
nombre en dos ramas.

### 4 · `BUG-062` — el driver dominante premia al driver con cobertura más angosta

C2 reportó que D6 está sobre-representado en la cola alta de riesgo: dominante en 419 de 45 276
escuelas (0.93 %) pero en 12 de las 40 de mayor riesgo, en municipios rurales donde SINAICA no
debería alcanzar. Su hipótesis era **imputación**.

Se revisó `dbt/models/gold/features_escuela.sql` y **la hipótesis no se sostiene**: el filtro
`distancia_km <= 15` deja fuera del CTE a la escuela sin estación cercana, y el ensamblado la marca
`coalesce(d6.d6_cobertura, 'SIN_DATO')`. La regla de `SIN_DATO` se respeta.

Lo que sí hay es otra cosa: **cada driver se reescala min-max sobre su propio conjunto cubierto**.
D1 y D2 sobre poblaciones casi nacionales; D6 sobre el ~1.3 % dentro del radio de 15 km. El min-max
estira siempre su entrada hasta llenar el `[0,1]`, así que en ese subconjunto los valores de D6
salen inflados frente a los D1/D2 de las mismas escuelas y ganan el argmax con más frecuencia de la
que su severidad justifica. La etiqueta es en parte un artefacto de **amplitud de cobertura**.

Queda `open`, `medium`, **sin corregir antes del 9-sep**: rematerializar cambia todas las
predicciones publicadas, el par de demostración recién elegido y el conteo de 7 que sostiene
`DEC-019`. Mismo criterio con el que se difirió `BUG-037`.

## Decisiones

- Se acepta el par de Ecatepec sobre la alternativa de Toluca. **Criterio: control de variables por
  encima de "que cruce la línea".**
- `BUG-062` no se corrige antes de la demo y se responde con una frase preparada, no con un fix.
- La excepción de freeze se reasienta con ID nuevo en vez de reciclar `DEC-019`.

## Lo que queda pendiente

- **Verificación en vivo del par**: elegido contra el Gold rematerializado, **no** contra producción
  con sesión. Lo corre C2 en el ensayo del lunes 7 y otra vez la mañana del 9. Es criterio de
  checklist, no de este PR.
- `BUG-062` sin dueño confirmado: propuesto C1 (Diana Alvarez, dueña de `dbt/**`) con C3 (Andrés
  González Habib) por la especificación del argmax. **Después del 9.**
- Cierre de estado en `Execution_Status`: `US-526` sigue en `planned` con la URL viva, y `US-207` /
  `US-405` siguen abajo de donde están realmente. Va en el siguiente paso, no en este PR.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** este DevLog; `DEC-020`; `BUG-062`.
- **Modificados:** `vault/01_Product/Guion_Demo_US006.md` (5 ediciones: las 3 de C2 más 2 que su
  reporte no cubría), `vault/_DevLog/_index.md`.
- **Verificado por el agente antes de escribir:** el filtro de 15 km y la normalización min-max por
  cobertura en `features_escuela.sql`; el estado `fixed` de `BUG-053` en el registro; que `DEC-019`
  en `main` es la línea de alerta y no la excepción de freeze; que `_export_chart()` manda
  `"query_context": None` (`sync_semantic_layer.py:1074`), que es lo que sostiene la caída del P2.
- **Correcciones manuales:** pendientes de revisión humana.
