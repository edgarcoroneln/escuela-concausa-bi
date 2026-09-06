---
id: DOC-VAULT-STEWARD
title: "Vault Steward — rol rotativo y turnos"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["US-005", "REQ-007", "vault/_Meta/Vault_Rules"]
traces_down: ["vault/10_Risk_Governance/Risk_Register"]
last_reviewed: "2026-09-05"
tags: [meta, gobernanza, higiene, steward]
---

# Vault Steward — rol rotativo y turnos

> Un responsable por sprint que corre el linter, revisa la matriz y caza documentos huérfanos.
> → [[vault/_Meta/_index|Volver a _Meta]] · [[vault/_Meta/Vault_Rules]] · [[vault/_Meta/Link_Hygiene]]

## Por qué existe

`RISK-006` —*el vault pierde trazabilidad con 21 contribuidores*— se mitiga con cuatro cosas:
**linter, steward, matriz y generador validado**. Tres estaban construidas desde S1. La cuarta, el
steward, sólo existía como palabra en el plan.

**No operó en S1–S4.** Esto no se descubre por auditoría: se descubre por el costo, y el costo es
medible. Todo lo de abajo apareció en una sola semana, y lo habría cazado alguien corriendo una
lista de verificación una vez por sprint:

| Lo que se degradó | Cómo se manifestó |
|---|---|
| `ownership.yml` sin cobertura | El mismo hueco parchado **seis veces** en tres días: `Accessibility.md` (Marina), `Data_Lineage_US106.md` (Diana), `requirements.txt` (Manuel), `US-521b-guia-ambiente-local.md` (Edgar Jiménez), `UX_Guidelines.md` (el PM sobre su propio documento) y `guia-ambiente-local/` (aún sin dueño). Cada vez, alguien no pudo tocar **su propio entregable** |
| Secreto versionado | `guia-ambiente-local/configuracion.env` sigue en git contra `Secrets_Policy`. Sin credenciales dentro —verificado—, pero el patrón `*.env` no des-trackea lo ya versionado |
| Registro mal formado | La fila de `BUG-018` tenía `**fixed**` en la columna de US y `open` en la de estado: **contaba como bug abierto** en cualquier conteo, con el arreglo mergeado desde el 28-ago |
| Regla 1 rota | Tres documentos de ambiente local solapados: `vault/_Meta/US-521b-guia-ambiente-local.md`, `guia-ambiente-local/VERIFICACION.md` y `Runbook_Ambiente_Local.md` con `source_of_truth: true` |
| Colisión de IDs | `BUG-049` registrado por dos personas el mismo día para defectos distintos, con `DEC-013` ya escrita justo para evitarlo. **Resuelto**: Monserrat Miranda renumeró el suyo a `BUG-051` por su cuenta y entró con el PR #228 |
| Tablero desinformando | El bloque §Estado del proyecto de la matriz llevaba cifras de agosto —*"0 REQ Done"*— tres semanas después de dejar de ser ciertas |

Ninguno es culpa de quien lo escribió. Son **higiene**, y la higiene sin dueño no ocurre.

## Qué hace el Steward

Un turno son **treinta minutos al cierre del sprint**. No es revisar PRs ni aprobar trabajo ajeno:
es correr una lista y **reportar**, no arreglar en silencio lo que es de otro.

### Lista de verificación

```bash
python vault/_Meta/scripts/vault_lint.py .
python vault/_Meta/scripts/validate_pm_dashboard.py
```

1. **Linter y TEST-002 en verde.** Si algo truena, se reporta al dueño del artefacto; el Steward no
   edita fuera de su alcance de `ownership.yml`.
2. **Cobertura de `ownership.yml`.** Todo archivo tocado en el sprint cae en el verde, amarillo o
   comunes de alguien. Un archivo sin dueño es un PR que alguien no va a poder abrir.
3. **IDs únicos y sin recicle.** `BUG-`, `DEC-`, `RISK-`, `ADR-`, `INC-`, `BLOCK-`: el máximo escrito
   en `main` es el que reserva (`DEC-013`). Un ID en dos registros es una colisión que hay que
   resolver antes de que se ramifique.
4. **Registros bien formados.** Las filas de `Bug_Register` y `Blocker_Register` tienen el estado en
   la columna de estado. Una columna corrida convierte un bug cerrado en uno abierto.
5. **Regla 1.** Ningún tema con dos documentos canónicos. Dos `source_of_truth: true` sobre lo mismo
   es un conflicto, no una redundancia.
6. **Huérfanos.** Todo artefacto está en el `_index.md` de su carpeta (regla 4).
7. **Estado del proyecto al día.** El bloque §Estado del proyecto de
   [[vault/02_Requirements/Traceability_Matrix]] se **transcribe a mano** desde
   `vault/13_Reports/data/pm-dashboard.json`. El turno lo compara contra el snapshot y lo corrige si
   se desfasó — se desfasa solo, con cada merge. **Follow-up post-freeze**: que el generador lo
   escriba entre marcadores y esta comparación deje de existir. Hoy no se hace porque cada refresco
   automático tocaría la matriz, donde todo el equipo agrega evidencia al final del archivo.
8. **Secretos.** Ningún `.env` ni credencial versionada — `git ls-files | grep -iE '\.env$'`.

### Qué entrega

Una entrada de DevLog con el resultado de los ocho puntos y **a quién le tocó cada hallazgo**. Si
todo salió limpio, se dice en una línea: un turno sin hallazgos también es información.

## Turnos

| Sprint | Fechas | Steward | Estado |
|---|---|---|---|
| S1 | 3–9 ago | — | ⚠️ No operó |
| S2 | 10–16 ago | — | ⚠️ No operó |
| S3 | 17–23 ago | — | ⚠️ No operó |
| S4 | 24–30 ago | — | ⚠️ No operó |
| S5 | 31 ago – 6 sep | Edgar Coronel (PO) | 🔵 En curso — hallazgos de esta semana en la tabla de arriba |
| S6 | 7–8 sep | Diana Alvarez (C1) | ⬜ Pendiente · corre la lista **antes** del ensayo de `US-006` |

**Criterio de asignación:** el turno de S6 va a quien tenga su alcance cerrado, para que la higiene
no compita con una entrega. Diana cerró sus 6 historias al 100 %.

**Después del proyecto**, la rotación sigue el orden de células —C1 → C2 → C3 → C4 → C5 → PO— y el
Tech Lead de cada célula nombra a quien le toca.

## Lo que el Steward no es

- **No es un revisor de PRs.** La compuerta de aprobación es del PM y no cambia.
- **No arregla lo ajeno.** Reporta al dueño. La única excepción son los arreglos mecánicos que el
  PM ya autoriza —resolver conflictos, sincronizar ramas—, y esos son del PM, no del rol.
- **No es un auditor de personas.** La lista mira artefactos, nunca desempeño.
