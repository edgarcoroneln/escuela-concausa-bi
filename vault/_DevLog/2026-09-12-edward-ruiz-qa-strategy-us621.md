---
project: "FARO"
date: "2026-09-12"
author_human: "Edward Ulysses Ruiz Bustillos"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "Recreado por el PM (Edgar Coronel) sobre dev/edward-ruiz: el PR original (#320) se abrió desde feat/documentacion-qa, una rama por tema prohibida por la regla 8 del vault, y el título no seguía el formato estándar. El contenido de la estrategia es de Edward; el DevLog y la fila de matriz que faltaban en el PR original se completan aquí."
touches: ["US-621", "REQ-004", "REQ-005"]
tags: [devlog, qa, estrategia, celula-6]
---

# DevLog — 2026-09-12 — Estrategia operativa de QA para S7 (US-621)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/QA_team_documentation/Reporte_Auditoria_QA_UX|Reporte_Auditoria_QA_UX]]

## Qué se agrega

`vault/06_Quality_Testing/QA_team_documentation/Reporte_Auditoria_QA_UX.md`: estrategia operativa
del equipo de QA (3 personas) para la recuperación S7. Define el modelo de trabajo "Owner Checks"
(QA orquesta, cada dueño de área entrega evidencia, QA valida sobre el producto real), la matriz de
tres perspectivas de auditoría (Data & Lógica, Funcional E2E, UX & Storytelling), y las reglas de
veredicto Go / GO WITH RISKS / NO-GO.

## Corrección de proceso sobre el PR original (#320)

El PR se abrió desde `feat/documentacion-qa` en vez de `dev/edward-ruiz` (regla 8: una rama fija por
persona, nunca por tema) y el título no seguía `[Nombre Apellido] - Descripción (ID) -
[sync|CI|DoF|DevLog]`. `check_ownership.py` lo reprobó por ambos motivos. Edward confirmó que no
puede operar su equipo en este momento, así que el PM resincronizó `dev/edward-ruiz` con `main` y
trasladó el mismo archivo, sin modificar su contenido.

El PR original también marcaba en su checklist que la matriz de trazabilidad estaba actualizada y
que existía un DevLog — ninguno de los dos se había commiteado. Se agregan aquí ambos para que el
PR cumpla Definition of Filed de verdad, no solo en el checklist.

## Pendiente, fuera de este documento

El PO plantea, aparte de esta estrategia organizativa, si el plan de QA de S7 debe incluir una
suite de pruebas automatizadas (Playwright) exhaustiva de navegación, botones y respuestas de todo
el frontend — hoy no existe ninguna en el repositorio (`frontend/package.json` no declara ningún
test runner). Se responde y se recomienda por separado a Edward, no se resuelve en este PR.
