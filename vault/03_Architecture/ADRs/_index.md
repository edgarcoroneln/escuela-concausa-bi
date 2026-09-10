---
id: MOC-ADR
title: "ADRs"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
tags: [moc, adr, architecture]
---

# Architecture Decision Records (ADRs)

> Cada decisión técnica relevante se registra como un ADR inmutable. Plantilla: [[vault/_Templates/ADR_template]].
> → [[vault/03_Architecture/_index]]

| ADR | Título | Estado | Fecha |
|---|---|---|---|
| [[vault/03_Architecture/ADRs/ADR-001-example]] | Ejemplo de decisión | accepted | 2026-08-01 |
| [[vault/03_Architecture/ADRs/ADR-002-frontend-streamlit]] | Frontend integrado en Streamlit sobre Superset + API | accepted | 2026-08-07 |
| [[vault/03_Architecture/ADRs/ADR-003-ml-estrategia-modelado]] | Estrategia de modelado ML: partición temporal, backtesting y cobertura parcial | accepted | 2026-08-09 |
| [[vault/03_Architecture/ADRs/ADR-004-autenticacion-oauth2-jwt]] | Autenticación: OAuth2 con Google + JWT propio (access/refresh) | proposed | 2026-08-17 |
| [[vault/03_Architecture/ADRs/ADR-005-dim-driver-mapeo]] | Mapeo de D3/D4 en dim_driver: infraestructura y conectividad desde CEMABE | accepted | 2026-08-17 |
| [[vault/03_Architecture/ADRs/ADR-006-idw-calidad-aire-agua]] | Interpolación IDW de D5/D6 (agua/aire) hacia cada escuela | accepted | 2026-08-19 |
| [[vault/03_Architecture/ADRs/ADR-007-unidad-target-variacion-matricula]] | Unidad de `target_variacion_matricula`: fracción, no diferencia absoluta | accepted | 2026-08-29 |
| [[vault/03_Architecture/ADRs/ADR-008-contenerizacion-airflow-sqlalchemy]] | Contenerización propia de Airflow con SQLAlchemy fijado en 1.4.x | accepted | 2026-08-25 |
| [[vault/03_Architecture/ADRs/ADR-009-monitoreo-mlflow-webhook]] | Monitoreo de runs de MLflow con alertas por webhook genérico | proposed | 2026-08-31 |
| [[vault/03_Architecture/ADRs/ADR-010-puente-oauth-frontend]] | Puente OAuth → frontend: código de un solo uso, nunca tokens en la URL | proposed | 2026-09-03 |
