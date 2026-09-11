---
project: "FARO"
date: "2026-09-11"
author_human: "Juan Carlos Macías Mayen"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — auditoría del frente, corrección de datos inventados en 4 mockups, decisión de convivencia claro/oscuro, frontmatter del anexo de tokens y alta de mockups/_index.md, tras revisión de Marina García del Buey. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011", "DEC-024"]
tags: [devlog, equipo-3, ux, identidad-visual, s7, us-621]
---

# DevLog — 2026-09-11 — Retiro del PDF, datos inventados corregidos, anexo de tokens formalizado (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]]

## Contexto

Auditoría del frente (Equipo 3) a petición de Juan: reveló que `01_UX_Architecture.md` de Oscar
Quiroz no está en `main` (vive en `dev/oscar-quiroz`, sin PR abierto — mismo patrón que le pasó
antes a Marina) y que el criterio de cierre de `US-621` tenía 3 de 4 entregables reales, no 4.
Aparte de esa auditoría, Marina revisó el PR #310 (ya mergeado) y encontró información mostrada
como si fuera dato de producción sin serlo, en 4 de los 7 mockups.

## Qué se hizo

- **Propuesta de retirar `FARO_UX_UI_Guide.pdf`** del criterio de cierre — aceptada por Marina con
  un ajuste: el archivo que sustituye al PDF no es `Design_Tokens_Stitch.md` suelto (no puede ser
  guía, es anexo — su frontmatter era el YAML crudo de Stitch, sin `id`/`owner`/`status`), sino
  `03_Visual_Identity.md` como guía de identidad de referencia, con `Design_Tokens_Stitch.md` como
  su anexo técnico. Registrado en `PLAN_TRABAJO.md` §7.ter (Marina) y reflejado en
  `03_Visual_Identity.md` §8 y en el `_index.md` del paquete.
- **`Design_Tokens_Stitch.md` recibió frontmatter propio** (`DOC-FARO-UX-TOKENS`, owner Juan,
  status `draft`, trazas a `US-621`/`03_Visual_Identity`) — el YAML crudo de Stitch se movió a un
  bloque `yaml` dentro del cuerpo, ya no ocupa el frontmatter del archivo.
- **`mockups/_index.md` creado** — no existía, regla 4 del vault. Lista los 7 HTML + 7 PNG +
  material de soporte (guía de identidad, anexo de tokens, borrador de "Cómo funciona"). Enlazado
  desde el `_index.md` del paquete.
- **Datos inventados corregidos en 4 archivos**, siguiendo la lista literal de Marina (patrón de
  Monserrat en `LEER_PRIMERO.md`: números en vivo nunca se tecléan, van como `N`/`k`/`[entidad]`):
  - `02_Panorama_Escuelas_Riesgo.html`: "7 PLANTEL(ES) PRIORITARIO(S)" → "N PLANTELES EN RIESGO";
    "5/2 DE 7 ESCUELAS" → "k DE N ESCUELAS"; el texto de la alerta JS con "7 escuelas
    prioritarias" → "N escuelas en riesgo en [entidad]"; y un hallazgo propio no listado por
    Marina: la fórmula del pie de página tenía `N=7` tecleado en el cálculo, corregido a `N`.
  - `03_Seleccion_Caso.html`: "7 escuelas identificadas con nivel prioritario" → "N escuelas con
    nivel de atención alta"; se quitó por completo "Cluster Prioritario: Edomex Norte-Valle
    Central" (el nombre de la agrupación está inventado — ML-03 daría un cluster, no ese nombre).
  - `05_Conclusion_Top3.html`: las 4 apariciones de "N=7 PLANTELES" → "N PLANTELES".
  - `06_Explorador.html`: "(5 registros prioritarios)" → "(k registros con nivel de atención
    alta)"; "5 de 4,112 planteles" → "k de M planteles".
- **Decisión de convivencia claro/oscuro documentada** en `03_Visual_Identity.md` (nueva nota tras
  la de Watson): esta identidad nunca usa un lienzo oscuro de página — el slate `#0F172A` es solo
  acento en componentes puntuales (botones, nav seleccionado, nodo del Asistente FARO). Los 3
  bloques D3 de "Cómo funciona" (forzados a `color-scheme: light`) no chocan porque el lienzo de
  toda la experiencia ya es claro.
- **Sincronía:** el commit de Marina (`974d16e`, retiro del PDF) tampoco tenía PR abierto — se
  fusionó directo desde `dev/marina-garcia` (branch en sync 1:1 con `main` más ese commit, sin
  riesgo de arrastrar trabajo ajeno). Conflicto menor en `_index.md` del paquete (ambos
  editábamos la misma fila) resuelto a favor de su versión.

## Pendiente

- `01_UX_Architecture.md` de Oscar Quiroz — sigue sin PR, bloquea el criterio de cierre #1.
  Reportado, no es competencia de este frente resolverlo.
- Auditoría formal de contraste WCAG 2.1 AA (§6 de `03_Visual_Identity.md`).
- La leyenda de cada gráfica (`PLAN_TRABAJO.md` §7.bis, alcance: P2/P3/P4/P5/P6) es entrega de
  Monserrat Miranda dentro de `02_Data_Visualization_Spec.md`; Juan le da tratamiento visual
  cuando ella la escriba.
