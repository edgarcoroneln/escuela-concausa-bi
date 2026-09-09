---
project: "FARO"
date: "2026-09-04"
author_human: "Estefany Lucero Hernández Loredo"
agent: "Codex"
model: "GPT-5.6"
session_duration: "~1h"
touches: ["US-321", "US-322", "US-325", "REQ-003"]
tags: [devlog, ml, ml-03, eda, cobertura, gold]
---

# DevLog — 2026-09-04 — Inicio de ejecución del cierre ML-03

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

- Se verificó el protocolo del vault, el alcance de Estefany, el handoff más reciente y el plan de
  cierre aprobado.
- Se comprobó que el ambiente local no tiene Docker ni `.env`; por ello no se reconstruyó Bronze →
  Silver → Gold y no se atribuyó evidencia real a las historias.
- Se reparó el entorno virtual local, que no podía importar NumPy/Pydantic, sin versionar archivos.
- Se creó `src/modelos/ejecutar_cierre_ml03.py`: lee Gold, genera evidencia agregada de US-322/325,
  ejecuta ML-03 bajo `casos_completos` y deja MLflow como acción explícita posterior a validar.
- Se añadieron pruebas para ausencia de identificadores individuales, bloqueo sin casos completos y
  ejecución sin registro automático.

## 🤖 Sesión de IA

- **Agente / modelo:** Codex / GPT-5.6.
- **Archivos creados/modificados:** ejecutor ML, prueba acotada, fichas de US-321/322/325, plan de
  cierre, índice de DevLog y esta entrada.
- **Decisiones autónomas del agente:** no modificar ingestión/dbt; no registrar MLflow por defecto;
  conservar como bloqueo la ausencia total bajo `casos_completos`; no cambiar historias a `done`.
- **Correcciones manuales:** pendientes de revisión línea por línea de Estefany y aprobación de
  Edgar Coronel en el PR.

## Seguridad / calidad

- [x] El reporte contiene sólo agregados; no exporta CCT individuales ni datos reales al repo.
- [x] No se modificaron contratos Gold, ingestión, dbt, CI/CD ni archivos rojos.
- [x] La prueba en `tests/**` es acotada y se declarará como área compartida en el PR.
- [x] `pytest tests/ -q`: 911 passed, 7 skipped, 13 warnings; sin fallos.
- [x] Pruebas enfocadas: 27 passed; tres corresponden al ejecutor nuevo.
- [x] `ruff check .`: sin hallazgos.
- [x] `validate_pm_dashboard.py .`: TEST-002 válido con consola UTF-8.
- [x] `vault_lint.py`: Vault limpio; conserva 7 avisos de huérfanos preexistentes.
- [ ] Corrida Gold real y MLflow: bloqueadas por ausencia de Docker/configuración local.

## Bloqueantes

- Infraestructura local: Docker no está instalado/disponible y falta `.env`; no existe Gold local.
- Política ML: `casos_completos` puede excluir todas las filas si D5 permanece 100 % `SIN_DATO`.
  Cualquier fallback o cambio de algoritmo requiere decisión de Andrés y Edgar.

## Próximos pasos

1. Ejecutar el runbook en un host con Docker y materializar `gold.features_escuela`.
2. Correr `python -m src.modelos.ejecutar_cierre_ml03` y revisar los agregados.
3. Si ML-03 queda bloqueado o bajo 0.30, decidir política/uso con Andrés y Edgar.
4. Solicitar aprobación de Edgar Coronel antes del merge; no autoaprobar ni cerrar historias.
