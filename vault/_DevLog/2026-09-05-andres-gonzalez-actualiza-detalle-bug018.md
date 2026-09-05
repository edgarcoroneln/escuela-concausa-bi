---
id: DEVLOG-2026-09-05-ANDRES-GONZALEZ-BUG018
project: "FARO"
date: "2026-09-05"
owner: "Andrés González Habib"
status: filed
author_human: "Andrés González Habib"
agent: "GitHub Copilot"
model: "GitHub Copilot"
session_duration: "15m"
touches: ["BUG-018", "US-302", "REQ-003", "US-305"]
traces_up: ["BUG-018", "US-302", "REQ-003"]
traces_down: ["src/modelos/entrenar_ml02.py"]
tags: [devlog, celula-3, bug-register, ml-02]
---

# DevLog — 2026-09-05 — Actualiza el detalle de BUG-018

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo
- Se actualizó la sección detallada de `BUG-018`, que todavía decía que el parche estaba pendiente.
- Se verificó en `src/modelos/entrenar_ml02.py` que `drivers_utilizables()` se aplica a cada ventana
  de entrenamiento y que predicción y SHAP reutilizan `feature_names_in_`.
- Se confirmó que el bloqueo para cerrar el E2E de `US-305` sigue en C5: la imagen API no instala las
  dependencias RAG y no hay un commit relacionado pendiente en `dev/luis-tellez`.

## Sesión de IA
- **Agente / modelo:** GitHub Copilot
- **Archivos creados/modificados:** `vault/06_Quality_Testing/Bug_Register.md`, este DevLog y
  `vault/_DevLog/_index.md`.
- **Decisiones autónomas del agente:** ninguna; la corrección sigue la revisión del PR #230 hecha por
  Edgar Coronel y se verificó contra el código.
- **Correcciones manuales:** ninguna.
- **Prompt inicial:** revisión recibida de Edgar Coronel sobre el PR #230.

## Seguridad / calidad
- [x] Sin secretos hardcodeados
- [x] Cambio documental verificado contra el código
- [x] DevLog enlaza a los IDs afectados

## Bloqueantes
- C5 debe incluir las dependencias RAG en la imagen API, configurar los servicios requeridos y
  redesplegar antes de ejecutar la sonda pública de `US-305`.

## Próximos pasos
- Pedir a Edgar que escale hoy con Luis Téllez el bloqueo de C5, antes del freeze.
