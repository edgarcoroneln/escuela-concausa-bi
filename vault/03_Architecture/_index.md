---
id: MOC-03
title: "03_Architecture"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
tags: [moc, architecture]
---

# 03_Architecture

> Diseño técnico y decisiones. → [[vault/00_Start_Here/PROJECT_INDEX]]

| Documento | Contenido |
|---|---|
| [[vault/03_Architecture/System_Design]] | Arquitectura de alto nivel |
| [[vault/03_Architecture/Data_Model]] | **Arquitectura medallón completa** (Bronze/Silver/Gold), esquema estrella, contratos Pydantic + Great Expectations, diccionario de datos y linaje. Implementa REQ-001 (US-101). |
| [[vault/03_Architecture/API_Specification]] | **Contrato de la API** (OpenAPI): OAuth2/JWT + RBAC, catálogo de endpoints, modelos Pydantic y cómo mockear. Desbloquea a C2 y C3. Implementa REQ-004 (US-401). |
| [[vault/03_Architecture/Frontend_Architecture]] | **FARO Web** (Streamlit): capa web integrada que embebe Superset y hospeda panel ML, chat y auth. Implementa REQ-002/004/006 (US-206, US-207, US-305, US-405). |
| [[vault/03_Architecture/Technical_Guide]] | Stack y decisiones técnicas |
| [[vault/03_Architecture/ADRs/_index]] | Architecture Decision Records |
