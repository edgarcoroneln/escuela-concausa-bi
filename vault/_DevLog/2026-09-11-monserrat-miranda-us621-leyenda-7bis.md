---
project: "FARO"
date: "2026-09-11"
author_human: "Monserrat Xcaret Miranda Olivas"
agent: "Claude Code"
model: "claude-sonnet-5 / claude-opus-5"
session_duration: "1 sesión — §7.bis (leyenda de gráficas), revisión de §5.bis contra las reglas de forma, y la leyenda aplicada a los seis ejemplos. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011", "US-601"]
tags: [devlog, equipo-3, ux, dataviz, storytelling, s7, us-621]
---

# DevLog — 2026-09-11 — Leyenda de las gráficas (§7.bis) y revisión de "Cómo funciona" (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]]

## Qué se hizo

- **§7.bis del documento**: qué declara toda leyenda (qué se ve, unidad, `SIN_DATO`, ciclo y
  recorte) y la leyenda resuelta para las cinco gráficas de la historia más el panel de
  explicación del modelo — alcance **por gráfica**, no por pantalla, como precisó Marina.
  Colocada como sección propia (no dentro de §1), respondiendo a su segunda precisión.
- **§8.4**: revisión de "Cómo funciona" (§5.bis del plan, Equipo 1) contra las reglas de forma de
  este documento — cinco puntos, ninguno un defecto de ellos, todos decisiones a tomar a propósito
  (criterio 28 sin acotar, cifras fijas con datos que podrían quedar viejas, `SIN_DATO` de
  estructura, fondo forzado de los iframes D3, y la oportunidad del bloque `mapa`).
- **§8.3 actualizada**: las tres piezas que decía "pendientes, aún no llegan a `main`" ya estaban
  mergeadas (PR #312); se corrigió antes de que quedara desactualizado otra vez.
- **Los seis ejemplos regenerados** con la leyenda de la §7.bis.2 integrada: un bloque fijo y
  visible (nunca tooltip), con el mismo texto que el documento.

## Cómo se resolvió el layout, y por qué importa dejarlo escrito

El primer intento posicionó la leyenda en una posición fija adivinada, y chocó con contenido que
ya vivía cerca del borde inferior en cuatro de los seis ejemplos (P2, P5, P6, y por poco P3). La
causa: **adivinar cuánto espacio ocupa un bloque de texto es frágil** en cuanto el texto cambia.

Se corrigió midiendo el bloque ya renderizado (`Text.get_window_extent` de matplotlib) y colocando
todo lo demás **por encima de esa medición real**, no de un número fijo. `pie()` ahora devuelve la
fracción de figura donde termina su propio bloque; cada pantalla dibuja su leyenda de la §7.bis
**primero** y usa ese valor para todo lo que antes tenía una posición fija cerca del borde. Esto
hace que el layout no se rompa si el texto de una leyenda crece (por ejemplo, si el nombre de una
escuela es más largo, o si cambia la redacción de alguna declaración).

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-sonnet-5 (esta sesión), continuando trabajo de
  claude-opus-5 en la misma rama.
- **Archivos modificados:** `02_Data_Visualization_Spec.md` (§7.bis, §8.3, §8.4) ·
  `ejemplos_graficas/generar_ejemplos.py` (leyenda medida, no adivinada) · los 12 PNG/SVG
  regenerados · este DevLog.
- **Decisiones de Marina, aplicadas:** §7.bis como sección propia del documento canónico (no un
  archivo aparte, regla 1 del vault); alcance por gráfica y no por pantalla.
- **Decisiones autónomas del agente:** medir el bloque de leyenda en vez de calcular su altura a
  mano; un solo color de texto para la leyenda (visualmente plana, ya que Juan define el
  tratamiento visual en §7.5 y no vale la pena arriesgar una segunda pasada de color antes de eso).
- **Sincronía:** `git merge origin/main` trajo el PR #312 de Marina (§7.bis/§4.ter/§5.bis/§10.quater
  ya en `main`) y trabajo nuevo de Juan Macías (7 mockups + identidad) y de Edgar Coronel — ninguno
  tocó `02_Data_Visualization_Spec.md`, sin conflictos.

## Seguridad / calidad

- [x] Sin secretos.
- [x] `ruff check` limpio sobre `ejemplos_graficas/`.
- [x] `vault_lint` limpio sobre una copia con lo versionado más lo nuevo.
- [ ] Suite completa de `pytest`: no aplica, sin cambios de código productivo.
- [x] DevLog enlaza a los IDs afectados.

## Bloqueantes

- Ninguno.

## Próximos pasos

- Pasar `02_Data_Visualization_Spec.md` a `status: approved` — lo aprueba Marina (gate final de
  UX/UI, §7 del plan).
- Confirmar con Juan que sus mockups ya recogen la leyenda de la §7.bis.2 (llegaron en el mismo
  merge; revisión pendiente, fuera del alcance de esta sesión).
- Entregar los ejemplos regenerados a Juan si hace falta reemplazar una versión anterior.
