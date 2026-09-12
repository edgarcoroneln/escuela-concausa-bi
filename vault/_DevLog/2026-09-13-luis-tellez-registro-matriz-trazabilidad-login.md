---
project: "FARO"
date: "2026-09-13"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "Seguimiento — registro de BUG-078/079/080 en la matriz de trazabilidad (el cierre operativo y su DevLog ya se mergearon en PR #344). Incluye la resolución de un falso positivo de GitLeaks con un cambio mínimo de config del escáner en .github/ (regla 7, revisa el PO)."
touches: ["BUG-079", "BUG-078", "BUG-080", "US-405", "US-641", "US-505", "ADR-012", "REQ-004", "REQ-005"]
tags: [devlog, equipo-5, trazabilidad, documentacion, seguimiento, ci, seguridad]
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
- **GitLeaks (paso G5) verificado en local** con el binario `gitleaks 8.30.1`, reproduciendo el rango
  del PR (`c82d29a..HEAD`): con la config por defecto reporta **1 fuga** (el falso positivo, ver abajo);
  con `--config .github/gitleaks.toml` y con `GITLEAKS_CONFIG=.github/gitleaks.toml` reporta
  **`no leaks found` (exit 0)**.

## Resolución del gate de secretos (GitLeaks) — regla 7

El intento previo de registrar la matriz reprobó el gate **«Calidad de codigo y vault»**: la regla
`generic-api-key` marcó como secreto el **identificador de revisión de Cloud Run**
`faro-api-00019-2xs`, que aparece dentro de un comando de rollback documentado en la matriz. **No es
un secreto** — es el nombre público de una revisión de despliegue —, pero el patrón «palabra clave …
signo igual … valor de alta entropía» lo dispara.

- **Por qué no bastó reformular la línea:** GitLeaks escanea **todo el rango del PR** (los commits que
  la rama tiene por encima de `main`), no solo el último commit. La línea marcada quedó en el commit
  histórico `6f6b167`; reformularla en un commit posterior (`5b6e280`) no lo saca del rango, así que
  el gate seguía en rojo.
- **Por qué no se reescribe la historia:** en `dev/*` el force-push está **prohibido** por regla de
  oro del repo (la rama es permanente y sostiene las revisiones de PRs anteriores). No es una opción.
- **Fix mínimo y quirúrgico (dentro de mi alcance `.github/**`):** se añade
  [`.github/gitleaks.toml`](../../.github/gitleaks.toml) que **extiende y conserva todas las reglas por
  defecto** (`useDefault = true`) y solo **exime ese único commit histórico** (`commits = [...]`); y una
  línea `GITLEAKS_CONFIG: .github/gitleaks.toml` en el paso G5 de
  [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml). El escáner queda **intacto en el resto
  del repositorio y en commits futuros**; solo se documenta el falso positivo puntual.
- **Regla 7:** es un cambio de config del escáner de seguridad y del CI. `.github/**` está en mi verde,
  pero también anotado como crítico → la revisión del PO/Edgar la exige el propio PR. Cambio autorizado
  por Luis Téllez para desbloquear el registro de la matriz.

## Trazabilidad y pendientes

- El único cambio de código/config de este PR es la config mínima de GitLeaks descrita arriba
  (`.github/gitleaks.toml` + una línea en `.github/workflows/ci.yml`); el resto es documentación de
  trazabilidad.
- Recordatorio abierto, ajeno a mi frente: **`BUG-077`** (`GET /api/v1/municipios` → 500 por
  `nombre_entidad` nulo en ~97 % de `dim_municipio`). Dueños: Diana Álvarez (C1, confirmar cobertura
  en prod) y Christian Ruiz (C4, degradar el campo a `SIN_DATO`). Escalado por separado antes del
  freeze de hoy 20:00.
