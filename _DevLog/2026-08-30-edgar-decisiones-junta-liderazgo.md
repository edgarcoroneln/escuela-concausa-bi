---
project: "FARO"
date: "2026-08-30"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "Sonnet 5"
session_duration: "larga — aplicación de las cuatro decisiones de la junta de liderazgo"
touches: ["US-004", "US-104", "US-204", "US-206", "US-212", "US-303", "US-304a", "US-305", "US-311", "US-313", "US-403", "US-411", "US-412", "US-504", "ADR-007", "DEC-012", "DEC-013", "DEC-014", "BLOCK-002", "BUG-017", "BUG-018", "BUG-019", "BUG-020", "BUG-025", "PLAN-QA-S6"]
tags: [devlog, pm, decisiones, gobernanza, adr]
---

# DevLog — 2026-08-30 — Las cuatro decisiones de la junta de liderazgo

→ [[_DevLog/_index|Volver al índice]] · [[10_Risk_Governance/Decision_Log]] ·
[[03_Architecture/ADRs/ADR-007-unidad-target-variacion-matricula]]

## Qué se decidió

**DEC-012 · ADR-007 ratificado en fracción**, sin cambios a la sigmoide ni al umbral 0.6. Lo
importante es que **no fue una decisión nueva**: `DEC-006` ya había fijado el 13 de agosto que
«riesgo ≥ 0.6 ↔ pérdida de ~5 %», y ese «~5 %» ya era una fracción. Se alineó el código con algo
que el equipo ya había acordado y que la unidad vigente contradecía en silencio.

La mesa amplió el alcance en cuatro cláusulas, todas aportadas por Célula 2, y las cuatro mejoran el
ADR original:

- **R-1** — cubre también `fact_escuela_ciclo.variacion_matricula`, que tenía el mismo defecto y la
  leen **cuatro tableros**. Ratificar sólo el target dejaba el ML coherente y el frontend roto.
- **R-2** — la unidad se declara en el contrato, no en el acuerdo. Ésta es la causa raíz: mientras
  viva en la memoria de una junta, el siguiente productor vuelve a elegir por su cuenta.
- **R-3** — convención de nombres: `_pct`/`_frac`, o numerador y denominador por separado.
- **R-4** — tres cosas con dueño y fecha, no sólo con firma.

**DEC-013 · DB-05 adopta la salida B.** El argumento que la definió no fue el costo sino la
naturaleza del cambio: la salida A no era «dejar los charts quietos», era una **reversión** que
obligaba a re-exponer `valor_promedio` y a reintroducir el KPI-19 que US-205 excluyó a propósito. La
magnitud por driver no se pierde — vive en DB-08. DB-05 queda como tablero de decisión y DB-08 como
tablero de exploración, que es una separación más limpia que la que había.

**DEC-014 · DS-07 por tres vías en paralelo.** El diagnóstico cambió la decisión: DS-07 lleva cinco
semanas en cero **no por postergación sino porque nunca se convirtió en tarea con fecha**. El sprint
de Deni tiene US-111 a US-114 y ningún `US-1XXa` para DS-07, a diferencia de DS-06, que sí tuvo
US-121a–124a asignadas a Emilio. Eso no es un problema de la persona, es un hueco de planeación mío.

Por eso no se dejó en una sola persona ni en una sola opción: Deni intenta la descarga con fecha
compromiso, C1 implementa la cobertura parcial en paralelo como red de seguridad, y el bloqueo se
registró hoy como **BLOCK-002** sin esperar a nadie.

## BUG-020 cerrado, y verificado en vivo

No lo di por bueno porque alguien lo dijera. Corrí el guion de prueba contra la URL pública:

```
Etapa 1 ✅ /api/v1/health → 200
Etapa 2 ✅ /api/v1/escuelas → 200 (hay sesión de base de datos)
Etapa 3 ✅ devuelve datos reales (25 CCT)
Etapa 4 ✅ ruta protegida responde 404 para CCT inexistente
exit code: 0
```

La línea base de hace unas horas daba `exit code 2`. **Desbloquea cinco historias** —US-411, US-412,
US-403, US-305, US-304a— y recupera el punto de rúbrica de URL pública viva.

Christian cerró además **BUG-025** en el PR #142: el endpoint del agente deja de ser el stub.

## De nueve bugs abiertos a cuatro

`BUG-017`, `BUG-019`, `BUG-020` y `BUG-025` pasan a `fixed`. Quedan `BUG-004`, `BUG-012`, `BUG-029`
y `BUG-030`, ninguno crítico.

**Corregí también `BUG-018`, que llevaba dos días marcado `open` estando resuelto.** La causa fue un
error mío: al editar la tabla por posición de columna, el índice estaba corrido y el estado se
escribió en la celda equivocada. Lo detecté porque el conteo de abiertos no cuadraba con lo que
sabía. Vale registrarlo: **editar una tabla markdown por índice de columna es frágil**, y la próxima
vez conviene reconstruir la fila completa en vez de parchear una celda.

## El camino crítico cambió de dueño

Ya no es BUG-020. Ahora es **el reentrenamiento de ML-01** (Héctor, R-4). De él cuelgan US-311,
US-313, US-212 de Marina y US-204 de Manuel. Por eso R-4 lo exige con fecha: Marina verifica DB-03
**contra predicciones nuevas publicadas**, no contra el ADR firmado.

## Uso de IA

Claude Code aplicó las cuatro decisiones a los artefactos canónicos, verificó BUG-020 en vivo contra
la URL pública antes de marcarlo `fixed`, y regeneró el plan de QA y el reporte al equipo. Revisé la
redacción del ADR y de las tres decisiones antes de commitear, porque el texto de una decisión
ratificada es lo que se lee dentro de un mes.

## Pendiente

- Fecha del reentrenamiento de ML-01 (R-4) — Héctor.
- Dueño de BUG-019 — standup de hoy.
- Fecha compromiso de Deni para DS-07 y arranque de la vía 2 con Diana.
- Congelamiento de desarrollo el miércoles 2-sep.
