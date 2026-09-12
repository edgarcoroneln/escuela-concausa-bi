---
project: "FARO"
date: "2026-09-11"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — corrección del plan tras un cambio de contrato posterior a la aprobación. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011", "ADR-012", "DEC-019", "DEC-006", "BUG-063", "BUG-058", "US-651", "US-601"]
tags: [devlog, equipo-3, ux, s7, us-621, contrato]
---

# DevLog — 2026-09-11 — `prioridad` ya viaja en el contrato: corrección del plan (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]] ·
[[vault/03_Architecture/API_Specification]]

## Contexto

El gate de UX/UI del 2026-09-11 aprobó los cuatro entregables de la §7 y cerró los puntos 1 y 2 del
criterio de cierre. **Después de ese gate**, `ec1b43b` (Christian Imanol Ruiz, PR #332) entró a `main`
y movió el contrato de lectura en tres puntos, uno de los cuales toca directamente este frente.

No se revisó por gusto: se revisó porque el plan afirma cosas sobre el contrato, y cuando el contrato
se mueve esas afirmaciones dejan de ser opiniones y pasan a ser errores.

## Qué cambió en el contrato

Verificado sobre `origin/main`, no sobre el mensaje de su autor:

| Campo | Dónde | Efecto en este frente |
|---|---|---|
| `prioridad` | `PrediccionOut` (`GET /predicciones/{cct}`, `POST /predicciones/batch`) | **Riesgo.** Ver abajo |
| `latitud` / `longitud` | subidas de `EscuelaDetalleOut` a `EscuelaOut` | Útil. Quita 7 llamadas para 7 marcadores |
| `cve_ent` / `nombre_entidad` | `MunicipioOut` | Útil. Quita un diccionario tecleado en el front |

## El hallazgo

`ADR-011` §5 resolvió que el front **no consume** `gold.recomendaciones.prioridad` y deriva el nivel
de atención de `indice_riesgo`. Hasta ayer esa regla se sostenía sola: **el campo no existía**, así
que no había nada que desobedecer. Tres lugares del plan lo decían con esas palabras —§0 fila 5,
§10.ter y `P-01`: *"el contrato v1 no expone `prioridad`"*—. Hoy eso es **falso**.

**Por qué importa y no es cosmético.** La §3 fija el guardarraíl *"lo que no está en la §10 no se
dibuja"*, y el Equipo 5 lee la §10 como el mapa de lo construible. Un mapa que afirma que un campo no
existe, frente a un contrato que sí lo entrega, se resuelve solo y a favor de lo que se leyó después.

**Y el modo de fallo es concreto.** Los tres valores del campo —`alta`, `media`, `baja`— se llaman
**igual** que los tres niveles de atención de la §3.quater. Quien lea el contrato sin leer el plan los
va a conectar. Y entonces: `publicar_gold.prioridad_de_riesgo()` asigna `ALTA` sólo con
`riesgo >= ANCLA_SIGMOIDE` (0.60), y el máximo que ML-01 predice sobre el Gold publicado es
**0.5717**, así que **ninguna de las 45 276 filas es `alta`** (`BUG-063`). El expediente diría
**«media»** para las siete escuelas de las que trata toda la historia, en la pantalla que acaba de
decir que están en riesgo. Es `BUG-058` otra vez, en otra columna y esta vez en la cara del usuario.

## Qué se hizo

1. **Nueva §10.quinquies.** Es ahora la sección que sostiene la regla de no consumir `prioridad`,
   con el número que la justifica (0.5717 contra 0.60, cero de 45 276). Antes la regla vivía sólo
   como una frase en la §3.quater, cuando no tenía que competir con un campo real.
2. **Nueva §10.sexies.** Documenta los dos campos que sí sirven, y deja escrito que `None` en
   coordenadas significa **omitir** la escuela del mapa, nunca dibujarla en el `(0, 0)`.
3. **Corregidas las tres afirmaciones falsas** —§0 fila 5, §10.ter, `P-01`— de *"no se expone"* a
   *"se expone y no se consume"*.
4. **Actualizada la tabla de mapeo de la §10** con `latitud`/`longitud` en el listado y con la nota
   de `prioridad` en la fila de predicciones.
5. **Adenda al §14** dejando por escrito que el contrato se movió después de aprobar, qué no cambia
   (ninguna pantalla, ningún criterio de la §9) y qué queda escalado.

## Lo que no se hizo, a propósito

- **No se tocó `BUG-063`.** Realinear el corte de `prioridad` a la línea de alerta reescribe las
  45 276 filas publicadas y `DEC-019` prohíbe mover un solo valor publicado. Es decisión del PO con
  el TL de C3, escalada el 2026-09-11. Su efecto visible está en **DB-09 de Superset**, que `DEC-023`
  conserva como evidencia analítica: la tarjeta *"Recomendaciones de prioridad ALTA"* lee 0.
- **No se cambió `API_Specification`.** Su §3.4 describe `prioridad` como *"la urgencia con la que el
  storytelling ordena los casos"*, que es falso —el storytelling ordena por `indice_riesgo`
  descendente— pero el archivo es de otro alcance. Se pidió la corrección a su autor.
- **No se decidió el estatus del mapa.** `02_Data_Visualization_Spec` lo descarta en §3.3 y §8.1
  porque *"ningún endpoint expone geometría"*; esa **mitad** de la razón dejó de sostenerse —el front
  trae `d3-geo` y una base versionada en `frontend/src/data/geo/mexico-states.json`, y
  `Arquitectura_Frontend_React` §5 ya compromete `MapaRiesgo.jsx` y una ruta `/mapa`—. La otra mitad
  sigue en pie: *dónde* no responde *qué situación*, y la base disponible es **estatal, no
  municipal**. La decisión pertenece al handoff con el Equipo 5, no a este documento.

## Corrección en documento ajeno, con aviso

`02_Data_Visualization_Spec.md` §8.1 repetía la misma afirmación falsa —que `prioridad` *"no aparece
en `PrediccionOut`"*— en su tabla de recortes explícitos, que es **la lista que el Equipo 5 lee como
"lo que no se dibuja"**. Dejarla falsa en un documento y corregirla en otro es exactamente la regla 1
del vault al revés.

Se corrigieron **dos celdas** con autorización de la líder del frente, más una **nota de corrección
fechada y firmada** bajo la tabla que dice qué se cambió, por qué y qué **no** se tocó:

- Fila de `prioridad`: de *"no aparece"* a *"ya aparece y sigue sin consumirse"*, con el número
  (cero de 45 276 contra un máximo de 0.5717). La columna *"si se aprueba"* deja de pedir que el
  contrato la exponga —ya lo hace— y pide lo único que falta: realinear el corte.
- Fila del *mapa de ubicación*: se marca la premisa técnica como parcialmente caída y **se declara
  explícitamente que la decisión no se toma ahí**, sino en el handoff con el Equipo 5.

No se tocó ninguna forma, ningún criterio ni ninguna otra fila, y la autoría del documento sigue
siendo de **Monserrat Xcaret Miranda Olivas**. Avisado a la autora el mismo día.

## Verificación

- `vault_lint.py` limpio.
- Suite completa sobre `main` sincronizado: **1216 passed, 4 skipped**, sin fallas.
- `prioridad` en `PrediccionOut` y los cortes de `prioridad_de_riesgo()` leídos de `origin/main`, no
  del mensaje que los anunció.

## Pendiente

- `BUG-063`: decisión del PO sobre el corte, y qué se hace con la tarjeta de DB-09 antes del freeze.
- Corrección de una línea en `API_Specification` §3.4 (su autor).
- Handoff con el Equipo 5: reconciliación de rutas **y** el estatus del mapa.
- `US-651` sigue `planned` sin desglose.
