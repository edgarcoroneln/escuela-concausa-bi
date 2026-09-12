---
project: "FARO"
date: "2026-09-13"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "Seguimiento corto — registro de BUG-078/079/080 en la matriz de trazabilidad. El cierre operativo y su DevLog ya se mergearon en PR #344; esta entrada solo completa la trazabilidad, que vive en un archivo aparte."
touches: ["BUG-079", "BUG-078", "BUG-080", "US-405", "US-641", "US-505", "ADR-012", "REQ-004", "REQ-005"]
tags: [devlog, equipo-5, trazabilidad, documentacion, seguimiento]
---

# DevLog — 2026-09-13 — Registro de BUG-078/079/080 en la matriz de trazabilidad

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/_DevLog/2026-09-13-luis-tellez-login-e2e-redeploy-api|DevLog de cierre del login e2e]] ·
[[vault/02_Requirements/Traceability_Matrix|Matriz de trazabilidad]]

## Contexto

El **login e2e en producción ya quedó cerrado y verificado en vivo** (`BUG-079`), junto con dos
endurecimientos de los scripts de deploy (`BUG-078`, `BUG-080`). Todo eso se documentó y mergeó a
`main` en **PR #344** (DevLog de cierre + altas en `Bug_Register` + `_index`). Lo único que faltaba
para cerrar la regla de trazabilidad era **reflejar esos tres defectos en la matriz**, que es un
archivo distinto y que en el momento del merge de #344 todavía no los tenía.

Como #344 ya estaba mergeado cuando se preparó este registro, la actualización de la matriz **no
podía sumarse a ese PR** y va en este PR de seguimiento.

## Qué se hizo

- Se añadió una sección **«Evidencia incremental — 2026-09-13 · login e2e cerrado en prod y
  endurecimiento de scripts de deploy»** al final de
  [[vault/02_Requirements/Traceability_Matrix|Traceability_Matrix.md]], calcando el formato de las
  secciones incrementales existentes (encabezado + tabla de 5 columnas).
- Tres filas, una por defecto, con su REQ/US, evidencia verificada y estado:
  - `BUG-079` (critical) → `REQ-004`/`REQ-005`, `US-405`/`ADR-012`: causa raíz (la imagen
    `agente-457715a` era anterior a la sesión por cookie de `ADR-012`), fix operacional por redeploy
    de la API desde `main` (rev `faro-api-00020-nwg`), **verificado en vivo por Luis**. 🟢
  - `BUG-078` (medium, `fixed`) → `US-641`: `--cpu-throttling` en
    `deploy-cloud-run-frontend.sh`. 🟢
  - `BUG-080` (medium, `fixed`) → `US-505`: `--platform linux/amd64` en `build-and-push.sh`. 🟢
- Se marcó el cierre documental de #344 como **ya mergeado** en las celdas de estado (antes decía
  "pendiente por el PO").

## Verificación

- `python3 vault/_Meta/scripts/vault_lint.py .` → **Vault limpio**.
- `check_ownership.py` → exit 0. `Traceability_Matrix.md` está en `comunes` (cada autor mantiene su
  fila y el PM consolida); sigue anotado como crítico de Edgar solo a título informativo, por lo que
  su revisión ya la exige el propio PR.
- Sin pipes literales dentro de las celdas (escapados o reformulados) para no romper el gate de 5
  columnas del tablero PM.

## Trazabilidad y pendientes

- **No** hay cambio de código en este PR: solo documentación de trazabilidad.
- Recordatorio abierto, ajeno a mi frente: **`BUG-077`** (`GET /api/v1/municipios` → 500 por
  `nombre_entidad` nulo en ~97 % de `dim_municipio`). Dueños: Diana Álvarez (C1, confirmar cobertura
  en prod) y Christian Ruiz (C4, degradar el campo a `SIN_DATO`). Escalado por separado antes del
  freeze de hoy 20:00.
