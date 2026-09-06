---
id: DEVLOG-20260905-ESTEFANY-ENTORNO-PR231
title: "Handoff — entorno local y PR 231"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
date: "2026-09-05"
author_human: "Estefany Lucero Hernández Loredo"
agent: "Codex"
touches: ["US-321", "US-322", "US-325"]
traces_up: ["US-321", "US-322", "US-325", "vault/15_ML_Models/Plan_Cierre_Estefany_US321_US322_US325"]
tags: [devlog, handoff, ml, entorno]
---

## Handoff — 2026-09-05 — Codex

- **Current objective:** actualizar la rama, configurar entorno local y preparar PR #231 para Edgar; no declarar cierre sin evidencia.
- **Current branch:** `dev/estefany-hernandez`.
- **Latest graph status:** reporte disponible del 2026-08-25, anterior a HEAD; no regenerado.
- **Relevant Graphify queries:** CLI no disponible; consulta del reporte y fuentes canónicas del plan y DEVLOG de C3 post-BUG-048.
- **Files changed:** plan canónico de cierre, matriz e índice DevLog y este handoff. `.env` creado sólo localmente, excluido de Git.
- **IDs touched:** US-321, US-322, US-325, REQ-003.
- **Decisions made:** merge de origin/main (25d76e3), sin rebase ni rama nueva. Claves locales aleatorias sin imprimirlas. PostgreSQL local funciona; no alterar imputación, esquema ni estados finales. Actualizar PR existente #231 en vez de duplicarlo.
- **Open questions:** Gold definitivo autorizado de C1/C3; política D5 y criterio de cierre ML-03 a ratificar por Andrés/Edgar.
- **Risks:** Gold no existe localmente; D5 totalmente ausente según evidencia de C3 puede dejar cero casos completos. Silhouette histórico 0.1086 < 0.30. DEC-015 no cierra US-321. GitHub CLI sin autenticación; navegador sí tiene sesión y PR con revisión de Edgar pendiente.
- **Tests executed:** Docker version/Compose responden; compose config --quiet correcto; compose up -d db correcto; SQLAlchemy conecta y to_regclass confirma ausencia de gold.features_escuela. pytest tests/ -q: 973 passed, 8 skipped, 13 warnings. Ruff limpio; validate_pm_dashboard.py válido. vault_lint.py se ejecuta antes del push y su resultado se reporta en PR.
- **Next recommended action:** publicar esta actualización de PR, comprobar CI y revisión de Edgar; obtener/reconstruir Gold conforme al runbook y ejecutar evidencia US-322/325 antes de decidir el entrenamiento US-321.

→ [[vault/_DevLog/_index|Volver al índice]]

### Corrección detectada por CI

### Verificación adicional — 2026-09-05

- `dev/estefany-hernandez` permanece limpia y alineada con `origin/dev/estefany-hernandez`; la
  comparación local `origin/main...HEAD` devuelve `0 4` (sin commits pendientes de integrar desde
  `main` y cuatro commits propios por delante).
- El `.venv` local ejecuta Python 3.12.14. Pasaron `973 passed, 8 skipped, 13 warnings` con
  `& ./.venv/Scripts/python.exe -m pytest tests/ -q`; Ruff quedó limpio para el ejecutor y sus
  pruebas; `& ./.venv/Scripts/python.exe vault/_Meta/scripts/vault_lint.py .` reportó `Vault limpio`.
- `DATABASE_URL` está configurada sin imprimir su valor y PostgreSQL responde a `select 1`, pero
  no existen `gold.features_escuela`, `gold.fact_escuela_ciclo` ni tablas en `bronze`, `silver` o
  `gold`. El `.venv` no contiene `dbt` y Docker no está disponible en el `PATH` actual.
- No se ejecutó `ejecutar_cierre_ml03` contra Gold porque el contrato no está materializado. Las
  pruebas con fixture siguen siendo válidas como regresión, pero no constituyen evidencia real de
  US-321, US-322 ni US-325.
- No se pudo consultar el estado visual del PR #231 en esta sesión; queda pendiente verificar CI y
  aprobación de Edgar desde GitHub.

**Siguiente acción concreta:** Diana/Andrés deben entregar un Gold autorizado post-BUG-048 o
habilitar el runbook completo de C1 (Bronze → Silver → Gold), con commit y checksum. Después ejecutar
`src.modelos.ejecutar_cierre_ml03` y revisar los agregados con Andrés y Edgar antes de cambiar estados.

### Resultado posterior al dump Gold — 2026-09-05

- Se verificó el dump `gold_bug048_final2_2026-09-05.sql` (69,873,466 bytes; SHA-256
  `B8A3FC50A636A2943EB0BC25CBE495ED49914429A76838346E7EBCF6AAA5B32A`) y se restauró sólo en la
  base local aislada `faro_gold_bug048_review_20260905_02`; el archivo no se versiona.
- La evidencia agregada reporta 136,046 filas, 46,547 escuelas, 3 ciclos, cero duplicados por
  `cct × id_ciclo` y cobertura municipal disponible. US-322 y US-325 quedaron documentadas con
  cifras reales; US-321 sigue abierta porque `casos_completos` queda bloqueado por D5 100% y D6
  98.70% en `SIN_DATO`.
- No se entrenó ML-03 ni se registró MLflow. Queda pendiente la ratificación de la política de
  ausencia por Andrés y Edgar.

### Comparación con `gold_bug048_final1_2026-09-05 1.sql` — 2026-09-05

- Dump PostgreSQL 15.19, 304,702,498 bytes, SHA-256
  `07ECF29DEEE250732C38B252CA48794CCE413B5F295197E68804C337AC89D0BE`.
- Restaurado en `faro_gold_bug048_final1_review_20260905`; contiene 19 tablas Gold y conserva
  136,046 filas de `gold.features_escuela`, 132,566 hechos, 46,547 escuelas y 3 ciclos.
- El diagnóstico y ML-03 producen exactamente el mismo resultado agregado que `final2`: cero
  duplicados, cobertura municipal disponible, D5 100% sin dato, D6 98.70% sin dato y ML-03
  bloqueado por `casos_completos` sin entrenamiento ni registro MLflow.

El primer push detectó dos fallos en tests/test_generate_pm_dashboard.py: el separador del wikilink de la nueva fila del índice requería escape. Corregido sin cambiar pruebas ni reglas; se repite validación tras la documentación final. La descripción del PR conserva los marcadores opcionales de la plantilla para no exigir casillas no aplicables.
