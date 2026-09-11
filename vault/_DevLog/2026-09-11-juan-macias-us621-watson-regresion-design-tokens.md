---
project: "FARO"
date: "2026-09-11"
author_human: "Juan Carlos Macías Mayen"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "Corrección puntual, misma sesión — hallazgo reportado por revisión de par. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011"]
tags: [devlog, equipo-3, ux, identidad-visual, s7, us-621]
---

# DevLog — 2026-09-11 — Regresión de "Watson" en Design_Tokens_Stitch.md corregida

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity]]

## Qué pasó

Un revisor detectó que `mockups/Design_Tokens_Stitch.md` volvió a decir "Watson" en 4 lugares
("Telemetry Float (Watson AI Node)", "Watson AI predictive recommendations", "Floating Watson AI
Intelligence Node", badge `WATSON.AI // ONLINE`) — la corrección de la ronda anterior (5
menciones a **Asistente FARO**) se perdió porque el archivo se regeneró completo al copiar de
nuevo el `DESIGN.md` crudo de Stitch en la última integración (el grep de verificación de esa
ronda solo cubrió `*/code.html`, no el `.md` de tokens — hueco real en el proceso de revisión, no
solo en el archivo).

## Qué se corrigió

- Las 4 menciones a "Watson" → **Asistente FARO**, mismo criterio que `ADR-011` §6.
- **Tachadas en línea** (no solo con nota al encabezado) las secciones "Calibrated Risk Tiers"
  (semáforo rojo/ámbar/verde, `#E11D48`/`#D97706`/`#059669`) y "Systematic Risk Drivers" (6
  colores por driver) — la nota de encabezado ya explicaba que estaban superadas, pero un
  copiar-pegar treinta líneas abajo no la ve. Cada bloque tachado indica qué lo sustituye.
- Limpiados 2 espacios finales que `git diff --check` marcaba en `06_Explorador.html`.

## Verificación

- `grep -ci watson Design_Tokens_Stitch.md` → 0.
- `git diff --check` sobre `vault/04_UX_Design/FARO_Storytelling_UX/` → limpio.
- `vault_lint.py` limpio (mismo hallazgo bloqueante preexistente de otra tarea, ajeno).

## Pendiente

El resto de los 7 puntos de la revisión (información inventada en Panorama, Selección,
Expediente, Conclusión y Explorador; `mockups/_index.md`; actualizar matriz/DevLog/PR) sigue
abierto — se aborda en una entrada aparte.
