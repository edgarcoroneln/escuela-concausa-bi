---
id: MOC-06
title: "06_Quality_Testing"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
tags: [moc, qa, testing]
---

# 06_Quality_Testing

> Estrategia y evidencia de pruebas: automáticas, físicas/manuales y bugs.
> → [[vault/00_Start_Here/PROJECT_INDEX]]

| Documento | Contenido |
|---|---|
| [[vault/06_Quality_Testing/Test_Strategy]] | Pirámide de pruebas, cobertura, responsabilidades |
| [[vault/06_Quality_Testing/Automated/_index]] | Unit, integración, E2E |
| [[vault/06_Quality_Testing/Physical_Manual/_index]] | Pruebas en dispositivo real / manuales |
| [[vault/06_Quality_Testing/QA_Logs/_index]] | Bitácoras de ejecución de QA |
| [[vault/06_Quality_Testing/Bug_Register]] | Registro de defectos `BUG-###` |
| [[vault/06_Quality_Testing/Guion_E2E_Verificacion_4]] | Guion de la verificación #4 del ensayo E2E: ML-01 sirviendo por API (C3) |
| [[vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB05_DB08]] | Plan de pruebas de usabilidad/accesibilidad de DB-05/DB-08 (US-215b) |
| [[vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB03_DB04]] | Plan de pruebas de usabilidad/accesibilidad de DB-03/DB-04, incluido el drill-down cruzado (US-215a) |
| [[vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo]] | Recorrido de **la aplicación desplegada** con Playwright, repartido entre cinco personas sin traslape: API (Eloisa), sesión y RBAC (Karla), los 10 tableros (Monserrat), corrección visual (Oscar) y coherencia del dato de punta a punta (Diana). Trae el prompt sugerido, dónde registrar resultados y a quién se asigna cada bug |
| [[vault/06_Quality_Testing/Plan_Correccion_Defectos_Pre_Demo]] | Los **8 defectos abiertos** ordenados por **impacto sobre la demo**, no por severidad: qué minuto del guion rompe cada uno, quién lo tiene, en qué orden se atacan y **con qué prueba se declara cerrado**. Incluye la mitigación de sala para `BUG-070` y el plan B del bloque 3:00–5:00 si `BUG-065` no alcanza |
| [[vault/06_Quality_Testing/Reporte_QA_Regresion_S7_2026-09-12]] | **Reporte para la junta del 12-sep.** Regresión local completa de S7: encuentra `BUG-077` (critical) — `/municipios` responde 500 para el 97% de municipios porque `nombre_entidad` es obligatorio en el contrato pero nulo en 307/317 filas de `dim_municipio`, y la guarda de dbt que ya existía para esto nunca corre en CI. Ordenado por impacto sobre el freeze, con plan de remediación y dueño por acción |
| [[vault/06_Quality_Testing/QA_team_documentation/Plan_QA_Exhaustivo_S7]] | Complementa la estrategia operativa de Edward Ruiz (`QA_team_documentation/Reporte_Auditoria_QA_UX.md`, pendiente de mergear): inventario exhaustivo de las 9 pantallas del frontend con checklist verificable pantalla por pantalla, verificación local de ML, reparto de apoyo por frente, y hallazgos de la corrida del 12-sep (backend 1241/1241 verde, MLflow local vacío, esquema local de `gold.recomendaciones` desactualizado) |
