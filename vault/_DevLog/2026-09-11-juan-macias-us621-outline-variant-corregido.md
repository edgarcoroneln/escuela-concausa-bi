---
project: "FARO"
date: "2026-09-11"
author_human: "Juan Carlos Macías Mayen"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "Corrección puntual — hallazgo de Marina García sobre el fix de contraste anterior. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011"]
tags: [devlog, equipo-3, ux, accesibilidad, s7, us-621]
---

# DevLog — 2026-09-11 — `text-outline-variant` como texto, corregido (un caso real, uno descartado)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity]]

## Qué pasó

Marina García revisó el fix de contraste anterior (`text-outline` → `text-on-surface-variant`,
266 usos) y reportó 2 casos que se escaparon: `text-outline-variant` (`#c6c6cd`, token distinto,
más claro — 1.70:1 sobre blanco) usado directamente como texto en
`02_Panorama_Escuelas_Riesgo.html` y `04_Expediente_Escuela.html`. Verifiqué su medición
(exacta: 1.70:1 / 1.54:1 / 1.46:1) antes de tocar nada.

## Qué se corrigió y qué no

- **`02_Panorama_Escuelas_Riesgo.html`, línea 143:** "OPERATIVO EN LÍNEA" en
  `font-label-micro-mono` (10px) usaba `text-outline-variant` — caso real, corregido a
  `text-on-surface-variant`.
- **`04_Expediente_Escuela.html`, línea 258:** el segundo caso reportado **no es texto** — es el
  `stroke` de un patrón de cuadrícula decorativo en el SVG de fondo del mapa (`opacity-60`,
  `stroke-width 0.5`). Decorativo puro, exento de umbral de contraste bajo WCAG. No se tocó, para
  no oscurecer un fondo diseñado para ser apenas visible.
- **Barrido adicional, no pedido:** 6 usos más del mismo token en `Guia_Identidad_Visual.html` y
  `Como_Funciona_Preview.html` — fuera de los 7 mockups auditados, son separadores de puntuación
  ("/", "·"), no texto informativo. Anotados en `03_Visual_Identity.md` §6, sin corregir aún.

## Nota sobre orden de merge

Marina pidió que Edgar mergee su PR primero (choca con `dev/juan-macias` en
`Traceability_Matrix.md`, `03_Visual_Identity.md` y `_DevLog/_index.md`). Este commit **no
depende de ese orden** — es una corrección aislada sobre mis propios archivos, no toca las
secciones en disputa de forma que cambie la resolución acordada.
