---
id: DEVLOG-20260908-ESTEFANY-CORRIDA-ML03
title: "Handoff — corrida temporal ML-03 y cobertura indirecta"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
date: "2026-09-08"
author_human: "Estefany Lucero Hernández Loredo"
agent: "Codex"
touches: ["US-321", "US-325", "REQ-003", "RISK-011"]
traces_up: ["vault/15_ML_Models/ML03_Entrenamiento_US321", "vault/_DevLog/2026-09-08-handoff-estefany-hernandez-sync"]
tags: [devlog, handoff, ml03, validacion-temporal, cobertura]
---

## Handoff — 2026-09-08 — Codex

- **Current objective:** ejecutar y documentar la fase final de evidencia ML-03 y enviarla a aprobación de Edgar mediante PR; preservar la indicación de no tocar Gold publicado.
- **Current branch:** `dev/estefany-hernandez`.
- **Latest graph status:** reporte del 2026-08-25, última modificación versionada 86fc37c; no regenerado.
- **Relevant Graphify queries:** CLI no disponible; búsqueda dirigida de entrenar_ml03/ejecutar_cierre_ml03 en graph.json sin nodos coincidentes. Se consultaron el reporte y los archivos canónicos ya identificados por el plan.
- **Files changed:** ficha canónica ML03_Entrenamiento_US321, JSON agregado de evidencia, plan de cierre, índice ML, fila incremental de trazabilidad, alta de RISK-011 y este DevLog con su índice. Se incluye el handoff local de sincronización previo. Sin cambios a código productivo, Gold, API, Superset ni reglas del vault.
- **IDs touched:** US-321, US-325, REQ-003, RISK-011. US-322/325 conservan el cierre oficial del PO; US-321 no se marca done.
- **Decisions made:** código de 7e514b849648ce7f5aa645495118d70d99dc58a6; dump final1 con SHA-256 canónico; tabla local verificada contra todas las filas COPY; conexión localhost con default_transaction_read_only=on. D1-D4 + completitud, StandardScaler/KMeans, semilla 42, n_init=20, k=2..6, orden id_ciclo/cct, dos hilos y 256 MiB para distancias. Una ventana 2022-2023/2023-2024 → 2024-2025. Resultado: k=3, Silhouette 0.4644549058; 114,200 elegibles y 21,846 excluidas. Refit descriptivo auditado: las 1,648 filas elegibles con D6 observado coinciden con cluster 2. Se propone aceptar la evidencia y mantener producción SIN_DATO hasta revisión de RISK-011.
- **Open questions:** Andrés debe revisar utilidad del tercer grupo y suficiencia temporal; Edgar debe decidir aceptación de evidencia, alcance de una siguiente comparación y cierre/deuda. MLflow run_id, persistencia Gold, lectura C4 y comparación Panel/DB-03 siguen pendientes.
- **Risks:** RISK-011 (cobertura indirecta), exclusión territorial desigual y una sola ventana usada también para seleccionar k. No se afirma generalización independiente ni mejora controlada frente a 0.1086 histórico. Python local 3.12.14 frente a CI 3.11; se documentan versiones. No hay publicación ni registro de modelo.
- **Tests executed:** corrida real completada en 112.282 s; auditoría complementaria a k fijo reproduce conteos y cruce D6/completitud. `python -m pytest tests/ -q`: 1044 passed, 8 skipped, 13 warnings, 57.67 s. `python -m ruff check . --output-format concise`: PASS. `python vault/_Meta/scripts/validate_pm_dashboard.py .`: PASS con PYTHONUTF8=1. Linter de vault, verificación de diff y alcance se ejecutan sobre la documentación final antes del push y se registran abajo.
- **Next recommended action:** revisar el PR con Edgar y Andrés. Aceptar primero la evidencia; decidir RISK-011 antes de registrar MLflow o coordinar los dos cables. La reproducción segura y los agregados están en la ficha canónica y su JSON. No reaplicar los scripts contra producción.

### Incidencias operativas de esta sesión

- Docker/psql no están en PATH; PostgreSQL local ya responde y la base aislada existente conserva el dump canónico. No fue necesario iniciar ni instalar servicios, ni restaurar/modificar tablas.
- Primer intento: el entrenamiento terminó, pero el exportador local falló al pedir `cve_ent` como columna; el contrato deriva entidad del CCT. Se corrigió sólo el script ignorado de auditoría y se repitió el protocolo completo sin cambiar parámetros. Sólo la segunda ejecución produjo el informe completo.
- `validate_pm_dashboard.py` falló al imprimir el emoji en consola cp1252, después de validar; se repitió con `PYTHONUTF8=1` y pasó. No se editó el validador.
- Scripts y logs de ejecución en `_local/`, ignorado por Git. No se publican filas individuales, dumps, credenciales ni modelos binarios. La autenticación GitHub CLI no está disponible; el PR se crea desde la sesión de navegador existente.

→ [[vault/_DevLog/_index|Volver al índice]]

### Validación de la documentación final

- vault_lint.py: Vault limpio, 7 avisos preexistentes.
- git diff --check: sin errores de whitespace.
- tests/test_generate_pm_dashboard.py: 12 passed; TEST-002 válido después de actualizar registros.
- Integridad del JSON: conteos y selección de k consistentes; solo lectura, sin publicación, sin run_id, sin CCT individuales. Bloque Python de reproducción compila.
- Ruff: todos los checks pasan. El JSON agregado ocupa 12,349 bytes.
- check_ownership.py: identidad, rama y los 9 archivos dentro de alcance; matriz y registro de riesgos requieren revisión de Edgar.
