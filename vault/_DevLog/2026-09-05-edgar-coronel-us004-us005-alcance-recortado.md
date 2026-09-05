---
project: "FARO"
date: "2026-09-05"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "cierre de la cola de PRs, alcance recortado y cierre de US-004/US-005"
tags: [devlog, pm, us-004, us-005, dec-014, descoped, steward, tablero]
---

# DevLog — 2026-09-05 — Alcance recortado asentado y cierre de US-004 / US-005

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/_Meta/Vault_Steward]] ·
[[vault/02_Requirements/Traceability_Matrix]] · [[vault/10_Risk_Governance/Decision_Log]]

## Qué se pidió

Revisar los PRs abiertos del día, actualizar el tablero de control marcando el alcance recortado, y
cerrar las dos historias propias que seguían abiertas: `US-004` y `US-005`.

## 1. El recorte que el tablero no sabía

El 3-sep corté tres historias —`US-413` y `US-414` con Karla Monter, `US-525a` con Alejandro
Velázquez— al reasignar sus semanas. Las tres decisiones vivieron **sólo en el DevLog de quien las
recibió**. Ninguna llegó a `Execution_Status`, así que el tablero las contó como trabajo pendiente
durante dos días y el porcentaje del proyecto salía castigado por trabajo que ya no existía.

**La opción fácil era marcarlas `done`, y es la incorrecta.** Es exactamente el modo de falla que nos
costó reabrir `US-206`: una historia marcada como entregada que no lo estaba. Un recorte no es una
entrega, y el porcentaje que ve el evaluador no puede sugerir lo contrario.

Se introdujo un estado terminal nuevo, **`descoped`** (`DEC-014`), que hace lo correcto en las dos
direcciones: **sale del denominador** porque no es trabajo pendiente, y **nunca cuenta como `done`**
porque no se entregó. Exige la decisión y la fecha del corte escritas en la evidencia.

| | Antes | Después |
|---|---|---|
| Alcance | 91 historias | **88** (91 en catálogo − 3 recortadas) |
| Avance | 73.5 % | **76.4 %** |
| Historias recortadas | invisibles, contadas como pendientes | bloque propio con su decisión |

**Cambios de código, los dos en `vault/_Meta/scripts/`:** el generador saca las recortadas del
alcance antes de contar nada —así ni células, ni rúbrica, ni readiness las tocan— y las reporta
aparte; el validador exige que cada recortada traiga su justificación, que no aparezca a la vez en
alcance y fuera, y sobre todo que **alcance + recortadas = 91**. Esa última guarda es la que importa:
el `91` estaba escrito a mano en el validador, y ahora vigila el catálogo completo, de modo que una
historia no puede desaparecer del tablero en silencio por la puerta que acabo de abrir.

## 2. `US-004` — el tablero de control estaba desinformando

El único ítem abierto de esta historia era el acuerdo de
[[vault/13_Reports/US_Validation_Followup_2026-08-28]]: *"resolver los acuerdos de la tabla,
regenerar el tablero y cerrar TEST-002"*.

**Cola de validación del 28-ago, 20 historias:** 8 cerraron (`US-121a`, `US-122a`, `US-123a`,
`US-124a`, `US-213`, `US-221`, `US-411`, `US-412`) y 12 están en revisión con PR mergeado.
**Ninguna quedó en `in_progress` ni en `planned`.** `TEST-002` en verde sobre el snapshot regenerado.

Y al ir a verificarlo apareció lo de fondo: el bloque **§Estado del proyecto** de la propia matriz
—el "tablero de control del proyecto" que esta historia promete— llevaba cifras de planeación de
agosto. Decía *"REQ Done: 0 / 7"* y *"REQ pendientes de ejecución: 7 / 7"* tres semanas después de
que dejaran de ser ciertas. **Un tablero de control desactualizado desinforma más que uno ausente**,
porque parece dato.

Sustituido por cifras **derivadas** de `Execution_Status` vía el generador, con la regla escrita de
que no se capturan a mano. Hoy dice lo que es: 50 de 88, 76.4 %, **7.84 de 10 puntos asegurados**, y
los dos gates en rojo —tres modelos registrados, y el ensayo de la demo que no ha arrancado.

**La parte de "mantener" no se declara terminada.** Se entrega el artefacto y se traspasa el
mantenimiento al rol rotativo de `US-005`, que es donde debe vivir: una historia del PO no puede ser
el mecanismo permanente de higiene de un vault con 21 contribuidores.

## 3. `US-005` — el rol que `RISK-006` daba por existente

`RISK-006` se mitiga con cuatro cosas: **linter, steward, matriz y generador validado**. Tres estaban
construidas desde S1. **La cuarta era una palabra en el plan.**

Se creó [[vault/_Meta/Vault_Steward]] con el rol, una lista de verificación de ocho puntos y los
turnos. Y se registra sin adornos que **la rotación no operó en S1–S4** — con el costo documentado,
porque el costo es medible y todo apareció en una sola semana:

- El hueco de `ownership.yml` parchado **cinco veces** en dos días. Cada vez, alguien no pudo tocar
  **su propio entregable**: Marina, Diana, Manuel, Edgar Jiménez, y `guia-ambiente-local/` que sigue
  sin dueño.
- `guia-ambiente-local/configuracion.env` versionado en git contra `Secrets_Policy` — verificado sin
  credenciales dentro, pero el patrón `*.env` no des-trackea lo ya versionado.
- La fila de `BUG-018` con `**fixed**` en la columna de US y `open` en la de estado: **contaba como
  bug abierto** con el arreglo mergeado desde el 28-ago. Lo cazó Monserrat, lo corrigió Andrés.
- Tres documentos de ambiente local solapados contra la regla 1, uno de ellos con
  `source_of_truth: true`.
- `BUG-049` registrado por **dos personas el mismo día** para defectos distintos, con `DEC-013`
  escrita justo para evitarlo.

Ninguno es culpa de quien lo escribió. Son higiene, y la higiene sin dueño no ocurre.

**Turnos:** S5 el PO; **S6 Diana Alvarez**, elegida por tener su alcance cerrado al 100 % — el turno
no debe competir con una entrega.

## 4. Reporte de estado publicado

Semáforo por persona, secuencia de PRs y bloqueos, con la regla del color escrita: verde es sin
pendientes, ámbar es todo entregado esperando revisión, rojo es algo en curso o sin empezar.

Dos cosas salen al ponerlo junto y no se veían por separado: las **20 historias en revisión** son el
bloque más barato que queda —ya están entregadas—, y el **silencio de PR** es una señal que el
tablero no daba: Edward Ruiz lleva 14 días sin PR mergeado con dos historias sin empezar.

## Verificado

`generate_pm_dashboard.py` → 88 US · `validate_pm_dashboard.py` (**TEST-002**) en verde ·
`vault_lint.py` limpio · `pytest tests/ -q` → **923 passed, 4 skipped, 0 failed** · cola de
validación del 28-ago contrastada historia por historia contra el snapshot regenerado · el 404 de la
raíz de la URL pública y la ausencia de `frontend.Dockerfile` comprobados directamente.

## IDs tocados

`US-004`, `US-005`, `US-413`, `US-414`, `US-525a`, `DEC-014`, `RISK-006`, `REQ-007`, `TEST-002`

## Hallazgo abierto, sin dueño

**FARO Web está construido y no está desplegado, y ninguna historia cubre desplegarlo.** `US-206`
cerró con el embebido real de los diez tableros (PR #193), pero la raíz de la URL pública devuelve
`404`, no existe `docker/frontend.Dockerfile` y no hay servicio de frontend en `docker-compose.yml`.
Se decidió contenerizarlo y **la historia nunca se dio de alta**: no existe `US-526` en el catálogo.
Mientras siga así, `US-207` (Marina), `US-405` (Christian) y la prueba end-to-end del chat de Andrés
no tienen dónde vivir. Es de Célula 5 y es la decisión que más pesa de aquí al domingo.

## Próximos pasos

- Decidir FARO Web: darla de alta con dueño y fecha, o declarar que la demo corre sobre Superset y la
  API por separado. Hoy, no el lunes.
- `US-006` (ensayo de la demo) sigue sin arrancar y es la única historia mía que no depende de nadie.
- Diana corre la lista del Steward en S6, antes del ensayo.
