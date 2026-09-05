---
id: MOC-META
title: "_Meta — Reglas y salud del vault"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
tags: [moc, meta]
---

# _Meta — Reglas del vault

> Cómo funciona el vault: convenciones, trazabilidad e higiene.
> → [[vault/00_Start_Here/PROJECT_INDEX|Índice del Proyecto]]

| Documento | Propósito |
|---|---|
| [[vault/_Meta/Vault_Rules]] | Reglas no negociables del vault |
| `ownership.yml` | **Fuente única** de identidad, rama fija y permisos de los 21 integrantes |
| [[vault/_Meta/Naming_Conventions]] | IDs, nombres de archivo, ramas y commits |
| [[vault/_Meta/Traceability_Model]] | Cómo se conecta todo (frontmatter + matriz) |
| [[vault/_Meta/Definition_of_Filed]] | Cuándo algo "nuevo reportado" se considera archivado |
| [[vault/_Meta/Link_Hygiene]] | Evitar links rotos y huérfanos |
| [[vault/_Meta/Vault_Steward]] | Rol rotativo de higiene del vault: lista de verificación y turnos por sprint |
| [[vault/_Meta/Adoption_Guide]] | Cómo adoptar el vault en un proyecto nuevo |
| `scripts/vault_lint.py` | Check automatizable de higiene (links, frontmatter, IDs) |
| `scripts/generate_pm_dashboard.py` | Genera el snapshot y HTML PM desde fuentes canónicas |
| `scripts/validate_pm_dashboard.py` | `TEST-002`: valida IDs, cobertura, estados y vistas del tablero |
| `scripts/collect_github_activity.py` | Recopila PR/CI agregado en Actions; no modifica estados de US |
| `scripts/check_ownership.py` | `TEST-014`: verifica identidad, rama fija y alcance del autor del PR |
* [[US-521b-guia-ambiente-local]] - Guía de ambiente local reproducible
