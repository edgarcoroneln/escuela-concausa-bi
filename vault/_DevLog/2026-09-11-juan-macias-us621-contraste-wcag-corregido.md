---
project: "FARO"
date: "2026-09-11"
author_human: "Juan Carlos Macías Mayen"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — atención a los 3 puntos de la revisión de Marina García (gate de UX/UI) que le tocaban a Juan. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011"]
tags: [devlog, equipo-3, ux, identidad-visual, accesibilidad, s7, us-621]
---

# DevLog — 2026-09-11 — Contraste WCAG corregido, tamaño mínimo y foco definidos (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity]]

## Contexto

Marina García del Buey cerró el gate de UX/UI (los 4 entregables, `approved`) y dejó 3 puntos
para Juan + 1 para Oscar. **Su trabajo (flip a `approved`, auditoría completa de 14 pares, fila
de "Cómo funciona") vive sin PR en `dev/marina-garcia`** — a petición suya, no lo va a abrir hasta
tener también estos ajustes, para no meter un PR que necesite otra ronda inmediata. Esta entrada
cubre solo lo que hizo Juan sobre `main`, verificado de forma independiente.

## Qué se hizo

- **Verifiqué los 2 hallazgos de contraste de Marina con la fórmula real de WCAG 2.1** (cálculo
  propio de luminancia relativa, no confié en la cifra sin comprobarla): confirmé exacto
  4.10:1 (blanco/Beacon Action), 5.93:1 (blanco/hover), 4.46:1 (`text-outline`/blanco) y 9.39:1
  (`on-surface-variant`/blanco).
- **`text-outline` → `text-on-surface-variant`** en los 7 mockups, **266 usos como texto**
  (`text-outline-variant`, token distinto, no se tocó — verificado con `grep` antes y después,
  cero colisiones). El conteo real de Marina eran 268 con esa variante incluida por accidente.
- **Botón Beacon Action**: el fondo de reposo (`#0284C7`) fallaba con texto blanco a 4.10:1.
  Corregido intercambiando reposo/hover con su propio hover (`#0369A1`, 5.93:1) — sin inventar
  color nuevo. Aplicado en `03_Visual_Identity.md` §3 y en el anexo `Design_Tokens_Stitch.md`.
- **Tamaño mínimo de texto y foco visible**, agregados a §6 (antes "no definidos"): piso de 10px
  (`label-micro-mono`), anillo de foco de 2px en `#38BDF8` con offset de 2px, un solo tratamiento
  para todo control interactivo.
- **Orden de tabulación** se deja explícito en §6 como fuera de alcance de este documento —
  corresponde a Oscar Quiroz en `01_UX_Architecture.md` §8, no a identidad visual.
- §6 reescrita para reflejar el estado real: 2 hallazgos corregidos y verificados hoy, auditoría
  completa de 14 pares pendiente de que Marina abra su PR.

## Pendiente

- Auditoría formal de 14 pares (Marina, `dev/marina-garcia`, sin PR).
- Orden de tabulación (Oscar, `01_UX_Architecture.md` §8).
- Reconciliar cuando Marina abra su PR: su versión de §6/§7 y `mockups/_index.md` (fila "S" de
  "Cómo funciona", flip a `approved`) probablemente diverge de esta, dado que ambos editamos
  `03_Visual_Identity.md` en paralelo sin PR intermedio.
