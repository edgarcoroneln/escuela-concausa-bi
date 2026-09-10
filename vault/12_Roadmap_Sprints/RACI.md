---
id: DOC-RACI
title: "RACI de entregables — FARO"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["vault/12_Roadmap_Sprints/PLAN_MAESTRO", "vault/02_Requirements/User_Stories"]
traces_down: ["vault/13_Reports/PM_Dashboard_Spec"]
last_reviewed: "2026-09-10"
tags: [roadmap, raci, governance, dashboard]
---

# RACI de entregables — FARO

> Responsabilidades a nivel de entregable. La asignación de cada historia permanece en
> [[vault/02_Requirements/User_Stories]]. → [[vault/12_Roadmap_Sprints/_index]]

## Claves

- **R:** Responsible — ejecuta.
- **A:** Accountable — responde por la aceptación final.
- **C:** Consulted — participa antes de decidir.
- **I:** Informed — recibe el resultado.

| Entregable S7 | R | A | C | I | Fecha gate |
|---|---|---|---|---|---|
| Componentes, datos y memoria técnica | Equipo 1 | Héctor Rafael Morales Marbán | Equipos 3, 5 y 6 | PO · equipo | 2026-09-10 18:00 |
| Chat IA natural y auditable | Equipo 2 | Andrés González Habib | Equipos 5 y 6 | PO · equipo | 2026-09-11 18:00 |
| UX/UI, visualizaciones y storytelling | Equipo 3 | Marina García del Buey | Equipos 1, 5 y 6 | PO · equipo | 2026-09-11 18:00 |
| ML-03 y explicación de los tres modelos | Equipo 4 | Estefany Lucero Hernández Loredo | Equipos 1, 5 y 6 | PO · equipo | 2026-09-11 18:00 |
| Frontend integrado y candidata desplegada | Equipo 5 | Diana Aracely Alvarez Varela | Equipos 1–4 y 6 | PO · equipo | 2026-09-12 18:00 |
| Estrategia, ejecución y dictamen QA | Equipo 6 | Edward Ulysses Ruiz Bustillos | Líderes de Equipos 1–5 | PO · equipo | 2026-09-13 18:00 |
| Go/no-go, freeze y entrega | Edgar Edmundo Coronel Navarrete | Edgar Edmundo Coronel Navarrete | Edward + líderes | Equipo · profesor | 2026-09-13 20:00 / 2026-09-14 primera hora |

## Regla de escalamiento

Un entregable bloqueado por más de 24 horas se registra en
[[vault/10_Risk_Governance/Blocker_Register]]. Una decisión que cambie alcance, seguridad, esquema o CI/CD
requiere aprobación humana y registro en [[vault/10_Risk_Governance/Decision_Log]] o un ADR.
