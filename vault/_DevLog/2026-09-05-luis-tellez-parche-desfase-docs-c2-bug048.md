---
project: "FARO"
date: "2026-09-05"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — parche de desfase documental en dos docs de C2 tras cerrar BUG-048, con la cifra del universo completo de producción que C2 no podía medir; autorizado por la dueña (Marina García del Buey) y el PO (Edgar Coronel)"
touches: ["BUG-048", "DEC-006", "SEC-006", "BUG-057", "DEC-018", "US-207", "US-113", "REQ-002", "REQ-005"]
tags: [devlog, celula-5, documentacion, desfase, bug048, sec006, cube-specs, panel-ml]
---

# DevLog — 2026-09-05 — Parche de desfase documental en dos docs de C2 (post BUG-048 / SEC-006)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/_DevLog/2026-09-05-luis-tellez-bug048-refresco-gold-prod|BUG-048 (refresco de Gold)]] ·
[[vault/_DevLog/2026-09-05-luis-tellez-sec006-flip-auth-lectura-publica|SEC-006 (flip de lectura)]]

## Contexto — por qué C5 toca dos docs de C2

No es un defecto de código: es **desfase documental**. Dos artefactos de Célula 2 describen un
estado que **ya cambió** por trabajo de C5 desplegado en producción:

1. **`vault/04_UX_Design/Cube_Specs_DB03_DB04.md`** (§8.quinquies) — sus cifras de riesgo salen de
   una **muestra de 55 escuelas** (y de 145 *fixtures* sintéticos en el .3.bis). El propio apartado
   deja **una pregunta abierta**: *"no sabemos qué dará `escuelas_en_riesgo` en producción después
   del refresco de Gold (BUG-048/BLOCK-005)… puede seguir en cero o no"*, y marca en su tabla *"el
   conteo real del país: No, hasta que se refresque Gold"*.
2. **`vault/04_UX_Design/Panel_ML_US207.md`** (§3.1) — dice que la lectura *"responde sin token
   mientras `AUTH_LECTURA_PUBLICA=true`"*; esa bandera está en **`false`** en producción desde el
   cierre de **SEC-006** (postura del PO, **DEC-018**; **BUG-057**).

**Por qué lo mide y lo escribe C5 y no C2 (Marina):** la dueña, **Marina García del Buey**, sólo
tiene una **muestra** local; el **universo completo (45 276 escuelas)** vive en el `gold` de
**producción** (Cloud SQL `faro-postgres`, territorio C5, instancia de sólo IP privada). Marina no
puede recalcular la distribución del universo desde su muestra. C5 sí lo midió al cerrar BUG-048.

## Autorización de propiedad (regla 9 — ownership)

`vault/04_UX_Design/**` es **scope C2** (Manuel Serranía / Marina García del Buey). Esta edición se
hace **con OK explícito de la dueña (Marina García del Buey) y del PO (Edgar Coronel)**, presentes
junto a Luis Téllez, que **validaron el contenido concreto** antes de escribirlo. `check_ownership`
marcará los dos `.md` de `04_UX_Design/` **fuera del alcance de C5** — es lo **esperado**; el PO
mergea el PR **a conciencia**, con esta autorización registrada aquí. El DevLog, el `_index` y el
`Bug_Register` (si se tocara) son **comunes**.

## Qué se cambió (aditivo, sin reescribir ni mover DEC-006)

Se siguió el **mismo patrón aditivo** que el propio documento usa para sus correcciones (.3.bis, la
corrección de Edgar): **no se borró nada**; se agregaron bloques nuevos.

- **`Cube_Specs_DB03_DB04.md`**
  - Nota en **§8.quinquies.1** apuntando a la medición vigente (la cita histórica "0.401" se
    conserva como histórica).
  - Nuevo **§8.quinquies.3.ter** con la medición del **universo completo de producción** (ciclo
    2024-2025), que **responde la pregunta abierta** del .3.bis:

    | Estadístico | `indice_riesgo` (universo 45 276) |
    |---|---|
    | Mínimo | 0.0292 |
    | Promedio | 0.3510 |
    | Mediana | 0.3533 |
    | p90 | 0.4425 |
    | p95 | 0.4526 |
    | **Máximo** | **0.5717** |

    Conteo por umbral: **≥ 0.60 → 0 (0 %)**; ≥ 0.50 → 7 (0.015 %); ≥ 0.40 → 11 775 (26.0 %);
    ≥ 0.35 → 24 951 (55.1 %). `indice_completitud_drivers`: **0.197 → 0.619**.
  - **Tesis intacta:** `escuelas_en_riesgo = 0` sigue siendo la afirmación **verdadera** (máx real
    0.5717 < 0.60 = perder ≥ 5 %), y **ahora el cero es confiable** (Gold refrescado, ya no el
    empobrecido con D1 vacío). **No contradice el .3.bis** (que probó con *fixtures* que la sigmoide
    dispara a −7.60 %); lo completa. **No mueve DEC-006** — la recomendación de §8.quinquies.4
    (ordenar/ranking por driver dominante, no contar) queda igual.

- **`Panel_ML_US207.md` §3.1** — nota de actualización: en producción `AUTH_LECTURA_PUBLICA=false`
  desde SEC-006 (postura del PO, DEC-018; BUG-057), la lectura **exige sesión**, y —tal como el
  párrafo anticipaba— **no hubo cambio de código** (el cliente ya pasa el `access_token`); reversible
  en segundos si se reabriera la lectura anónima.

## Cómo se midió el universo (read-only, mínimo privilegio, revertido)

Cloud SQL `faro-postgres` es de **sólo IP privada**: no se alcanza `psql` desde la laptop. Las
consultas de **sólo lectura** se extrajeron con `gcloud sql export csv --query="SELECT…"` al bucket
privado `gs://faro-escuela-sensor-sql-import`, **mismo patrón server-side** que el import de BUG-048.
Para escribir el CSV, la SA de la instancia necesitaba `objectCreator` (sólo tenía `objectViewer`):
se pidió **OK explícito de Luis** (regla 7 — cambio de seguridad), se otorgó **temporalmente**, se
corrieron los `SELECT` y **se revirtió** (verificado por parseo del IAM: sólo queda el
`objectViewer` preexistente). Cero mutaciones de datos; cero secretos y cero correos en repo/chat.

## Seguridad / alcance

- [x] **Sin código** (`src/**`), sin `docker/**`, sin `superset/**`, sin infra ni env-vars nuevas.
- [x] **Sólo lectura** contra producción; el grant IAM temporal quedó **revertido**.
- [x] Dos `.md` de **C2** editados **con OK de la dueña (Marina) + PO** — registrado aquí;
      `check_ownership` los marcará fuera de scope de C5 (esperado, el PO mergea a conciencia).
- [x] **No se movió DEC-006** ni la narrativa de C2: sólo se **añadieron cifras** y una nota de auth.
- [x] Cero secretos / cero correos: personas por nombre y rol.

## Avisos a otros owners

- **C2 (Marina García del Buey / Manuel Serranía):** sus dos docs quedan al día con producción sin
  perder su narrativa. La **decisión sobre DEC-006 sigue siendo de C2**; C5 sólo aportó la cifra del
  universo que su muestra no podía dar. Si ajustan el .ter, es su artefacto.
- **PO (Edgar Coronel):** este parche responde la pregunta que el §8.quinquies dejó abierta y que tu
  propio DevLog de cierre de BUG-048 retomó (par de demo por reelegir con datos de prod — eso es C2).

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog.
- **Modificados:** `vault/04_UX_Design/Cube_Specs_DB03_DB04.md` (§8.quinquies.1 + nuevo
  §8.quinquies.3.ter), `vault/04_UX_Design/Panel_ML_US207.md` (§3.1), `vault/_DevLog/_index.md`.
- **Sin cambios** de código, `docker/**`, `superset/**`, infra GCP ni env-vars.
