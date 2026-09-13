---
project: "FARO"
date: "2026-09-13"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "Revisión del PR #355 con la objeción de Marina García, decisión de producto DEC-028
  y ajuste del guion de la demo."
touches: ["DEC-028", "US-305", "REQ-006", "REQ-007", "ADR-011"]
tags: [devlog, gobernanza, decision, agente, guion, s7]
---

# DevLog — 2026-09-13 — `DEC-028`: el Asistente FARO no muestra el SQL en la interfaz

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/10_Risk_Governance/Decision_Log|Decision Log]] ·
[[vault/01_Product/Guion_Demo_US006|Guion de la demo]]

## Qué se hizo

- **`DEC-028`** en `vault/10_Risk_Governance/Decision_Log.md`: el asistente de React deja de mostrar el
  SQL generado (PR #355). `sql_generado` sigue en el contrato de la API; no cambian el backend ni los
  guardarraíles.
- **Guion ajustado** (`vault/01_Product/Guion_Demo_US006.md`): el minuto 6:30–7:30 ya no promete
  «su SQL a la vista», la frase que se dice pasa a ser *«no opina: cada respuesta sale de una consulta de
  solo lectura a los datos del proyecto»*, y el bloque del agente lleva una nota que remite a la DEC.
- Fila nueva en la matriz de trazabilidad.

Sin cambios de código: todo lo de este registro es vault.

## Cómo se llegó a la decisión

1. **Lo que había en `main` no aplicaba al chat del producto.** El PR #351 ocultó el SQL sólo en el
   shell de Streamlit (`src/frontend/pages/3_Chat.py`), retirado como interfaz por `ADR-012`. El
   asistente de React (`AsistenteFaro.jsx`) seguía ofreciendo «Ver la consulta», y el bundle público
   del frontend de producción lo contenía el 13-sep, con la API ya en el `main` de ese día.
2. **El PR #355 quita la acción completa**: el botón «Ver la consulta» / «Ocultar la consulta», el
   bloque que mostraba el SQL y su estado. El SQL se sigue recibiendo y guardando por turno, pero no se
   renderiza. El build pasa y ninguna prueba del repositorio depende del botón.
3. **Marina García objetó el PR**, y sus cinco puntos se verificaron contra el árbol:
   - el gate de propiedad reprueba: `AsistenteFaro.jsx` es verde y crítico de Diana Alvarez;
   - `01_UX_Architecture.md` (aprobada) pide ocultar el SQL por defecto **pero dejarlo detrás de una
     acción discreta, cerrada de inicio**, para que el evaluador confirme que la respuesta sale de la
     base real — y `main` ya lo cumplía;
   - el guion usaba esa acción en el minuto 6:30–7:30, que presenta Diana;
   - el PR reescribió el comentario del componente que citaba la especificación;
   - el PR no trae DevLog.
4. **Decisión del PO:** retirar la acción de todos modos. El costo —perder la prueba visual de
   auditabilidad frente al evaluador— se asume a conciencia y queda escrito en `DEC-028` junto con la
   objeción. La auditabilidad se defiende con el rechazo en vivo y los guardarraíles de solo lectura.

## Omisiones conscientes

- **Revisión de Diana Alvarez** como dueña de `frontend/**`: el PR #355 se mergeó con bypass de admin.
- **DevLog de Andrés González** para el PR #355.
- **Firma de Marina García en la DEC**, que ella pidió: la DEC registra su objeción, pero la decisión es
  del PO.

## Pendientes, fuera de este registro

- **Luis Téllez (C5):** redesplegar el frontend desde `main`. Hasta entonces producción sigue mostrando
  «Ver la consulta».
- **Diana Alvarez:** ensayar el minuto 6:30 con la frase nueva.
- **Dueño de `01_UX_Architecture.md` (E3):** agregar una nota que apunte a `DEC-028`, después del freeze.

## Verificación

- `python vault/_Meta/scripts/vault_lint.py .` → Vault limpio.
- `check_ownership.py` para `edgarcoroneln` en `dev/edgar-coronel` → todos los archivos dentro del alcance.
