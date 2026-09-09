---
id: QALOG-PLANTILLA
title: "Plantilla de bitácora de QA"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
traces_up: ["vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo"]
traces_down: ["vault/06_Quality_Testing/Bug_Register"]
last_reviewed: "2026-09-07"
tags: [qa, plantilla, qa-log, pre-demo]
---

# Plantilla de bitácora de QA

> **Cópiala, no la edites.** Guárdala como
> `vault/06_Quality_Testing/QA_Logs/2026-09-07-{tu-identidad}-qa-pre-demo.md`, cambia el
> frontmatter, llena la tabla y **agrega tu fila al `_index.md` de esta carpeta** — sin eso no
> cuenta como archivado (`Definition_of_Filed`).
> → [[vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo]] · [[vault/06_Quality_Testing/QA_Logs/_index]]

## Tres reglas para escribir un caso

1. **Un caso es reproducible por alguien más.** "El tablero se ve mal" no es un caso; "DB-01,
   entidad = Jalisco, ciclo 2024-2025: el KPI-04 muestra 0 y `/api/v1/kpis` devuelve 7" sí lo es.
2. **"Obtenido" es lo que viste, no lo que concluiste.** El diagnóstico va en la columna de
   evidencia o en el bug, nunca en lugar del dato.
3. **Un caso que no corriste se marca `⏭️ no ejecutado` con el motivo.** Nunca se deja en blanco y
   nunca se marca ✅ sin haberlo visto. Un plan con huecos honestos vale más que uno completo y falso.

## Datos de la sesión

- **Responsable:**
- **Superficie asignada:**
- **URL probada:** https://faro-frontend-526490367142.us-central1.run.app/
- **Fecha y hora de inicio / fin:**
- **Sesión iniciada como:** (correo · rol `ciudadano` / `analista`)
- **Navegador y sistema:**

## Resultados

> Veredictos: **✅ pasa** · **❌ falla** (levanta bug) · **⚠️ pasa con reserva** (funciona pero se ve
> mal o es frágil) · **⏭️ no ejecutado** (con motivo).

| # | Caso | Esperado | Obtenido | Evidencia | Veredicto | Bug |
|---|---|---|---|---|---|---|
| 1 |  |  |  |  |  |  |
| 2 |  |  |  |  |  |  |
| 3 |  |  |  |  |  |  |

## Resumen

- **Casos ejecutados:** X de Y
- **✅ pasa:** · **⚠️ con reserva:** · **❌ falla:** · **⏭️ no ejecutado:**
- **Bugs levantados:** `BUG-0XX`, …
- **Clasificación para el miércoles** (del plan): 🔴 rompe la demo · 🟠 se ve mal pero sobrevive ·
  🟢 deuda declarada

## Lo que NO alcancé a probar

> Esta sección vale tanto como la tabla. Di qué quedó fuera y por qué, para que el PO sepa dónde no
> hay cobertura en vez de suponer que la hay.

## Hallazgos que no son bugs

> Cosas que sorprenden pero son comportamiento esperado, o dudas que conviene que alguien más lea.
> Si algo de aquí debería estar en las *«seis cosas que hay que saber»* del plan, dilo.
