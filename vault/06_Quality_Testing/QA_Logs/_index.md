---
id: MOC-06-QALOGS
title: "QA Logs"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
tags: [moc, qa, logs]
---

# QA Logs

> Bitácoras fechadas de ejecución de QA (una por sesión de testing).
> Nombre: `YYYY-MM-DD-{qa}-{alcance}.md`. → [[vault/06_Quality_Testing/_index]]

| Fecha | Alcance | Responsable | Resultado | Bugs |
|---|---|---|---|---|
| [[vault/06_Quality_Testing/QA_Logs/2026-09-08-edgar-coronel-qa-sin-sesion-playwright]] | Barrido con **Playwright contra producción** de la superficie **sin sesión**: **13 de 15**. Confirma de forma independiente que **Dashboards y Chat renderizan sin exigir login** (`BUG-071`), con el agravante de que el embebido usa credenciales admin propias y deja los 10 tableros en blanco sin avisar. Contrato 401 de `DEC-018` verificado en 3 rutas, sin fuga de detalle. Incluye la **corrección de un falso positivo propio** sobre el login de Superset. Script reproducible en `tests/qa_barrido_sin_sesion.py` | Edgar Coronel |
| — | **Plantilla** — cópiala para tu bitácora | [[vault/06_Quality_Testing/QA_Logs/PLANTILLA-qa-log\|PLANTILLA-qa-log]] | — | — |
| 2026-09-07 | Corrección visual — 10 dashboards | [[vault/06_Quality_Testing/QA_Logs/2026-09-07-oscar-quiroz-qa-pre-demo\|Oscar Quiroz]] | 46 casos: 27 ✅ · 14 ❌ · 4 ⚠️ · 1 ⏭️ | `BUG-064`, `BUG-065` 🔴, `BUG-066`, `BUG-067`, `BUG-068`, `BUG-069` |
