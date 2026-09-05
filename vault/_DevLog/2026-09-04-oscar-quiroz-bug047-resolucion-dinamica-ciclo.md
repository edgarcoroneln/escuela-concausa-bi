---
author_human: "Oscar Antonio Quiroz Lázaro"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "sesión: diagnóstico y mejora del fix de BUG-047 (filtro de ciclo sin default)"
touches: ["US-203", "US-204", "US-211a", "US-211b", "US-222", "REQ-002", "BUG-047"]
tags: [devlog]
---

# DevLog — 2026-09-04 — BUG-047: resolución dinámica del ciclo por defecto (mejora aditiva)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register]]

## Qué pedí

Edgar reportó por Teams (mismo aviso enviado a Manuel) revisar los tiles de "total" que sumen
matrícula o escuelas en mis tableros y confirmar si respetan el filtro de ciclo vigente, por el
mismo patrón que Karla encontró en la API (BUG-044). Pedí verificar contra datos reales, no solo
contra el YAML, antes de tocar nada. Cuando Manuel afirmó dos veces por Teams que ya lo había
corregido, pedí verificarlo también contra el repo antes de darlo por cerrado. Al confirmar que
ninguna de las dos afirmaciones tenía evidencia real **en ese momento**, pedí explicar el alcance
del defecto en términos simples y, ya con eso claro, autoricé aplicar el fix completo (código
compartido + verificación en los tableros afectados), con la condición de documentar evidencia
antes/después y flaggear explícitamente cualquier archivo fuera de mi propiedad directa.

## Qué hizo la IA

- Confirmó en vivo que DB-07 tenía el defecto: `total_escuelas` mostraba 25,578 (suma de los 3
  ciclos materializados) en vez de 8,382 (ciclo 2024-2025), consultando Postgres y la metadata
  real de Superset (`defaultDataMask: None` en el filtro "Ciclo escolar").
- Verificó dos veces las afirmaciones de Manuel ("ya quedó, le pusimos 2024-2025 como default") y
  ambas resultaron sin respaldo en ese momento: sin commits nuevos en `dev/manuel-serrania`, sin
  PRs abiertos en el repo, sin cambio en el `defaultDataMask` real de Superset.
- Diagnosticó la causa raíz de forma independiente: `metrics_db01_db02.yaml`,
  `metrics_db03_db04.yaml`, `metrics_db05_db08.yaml`, `metrics_db06_db09.yaml` y
  `metrics_db07.yaml` ya declaraban `default: ultimo_ciclo` en su contrato semántico, pero
  `_filtros_nativos()` (`superset/sync_semantic_layer.py`) nunca leía ese campo.
- Registró el hallazgo como bug nuevo (`BUG-050`) y construyó el fix completo (resolución
  dinámica del valor vía `/api/v1/chart/data`, nunca hardcodeada) antes de volver a sincronizar
  con `main`.
- **Al sincronizar (109 commits nuevos), encontró que el defecto ya estaba registrado y resuelto**
  como **BUG-047** (`dev/manuel-serrania`, Manuel Serranía): mecanismo `valor_por_defecto`
  estático, ya mergeado a `main`, con su propia suite `tests/test_filtro_ciclo_por_defecto.py`
  (Marina García, US-214a). El fix real llegó a `main` después de las dos verificaciones de esta
  sesión, no antes — las verificaciones fueron correctas en su momento, no una falsa alarma.
- **Retractó el número duplicado** (`BUG-050` → consolidado en `BUG-047`) por DEC-013 ("un
  defecto, un ID"), mismo criterio que usó Héctor Morales con BUG-041→043 el 3-sep.
- En vez de descartar el trabajo de Manuel/Marina, fusionó ambos mecanismos en
  `_filtros_nativos()`: `default: ultimo_ciclo` (dinámico, resuelto contra los datos reales,
  prioritario) con `valor_por_defecto` (estático, de ellos) como respaldo si la resolución
  dinámica no está disponible. Preservó la firma original de la función
  (`cfg_dashboard, datasets_uuids, ...`) agregando `token`/`datasets_by_name` como parámetros
  opcionales al final — los 5 tests de `test_filtro_ciclo_por_defecto.py` siguen pasando sin
  tocarlos.
- Agregó `default: ultimo_ciclo` a los 9 dashboards que ya declaraban esa intención en su propio
  `metrics_*.yaml` (los 7 que Manuel ya cubrió con `valor_por_defecto` más DB-03/DB-04 de Marina),
  sin quitar ninguna línea de `valor_por_defecto` existente.
- Escribió `tests/test_filtros_nativos_default_dinamico.py` (5 casos): resolución dinámica
  correcta, ausencia de cambio sin `default:`, que el valor sigue a los datos si el ciclo avanza,
  que un fallo de red no rompe el sync ni pierde el respaldo estático, y una guardia paramétrica
  sobre los 10 YAML de tablero.
- Corrió el sync completo y verificó, dataset por dataset, el número antes/después en los 9
  datasets con métrica de conteo absoluto.
- Retomó la captura real de DB-07 en `Manual_Usuario_Dashboards.md` (v1.3) con el fix visible: el
  filtro arranca en "2024-2025" (una sola opción), "Total de escuelas" = 8,382.

## Qué revisé yo

- No acepté la afirmación de Manuel dos veces seguidas sin evidencia — verifiqué contra `git
  fetch`, diff de ramas, lista de PRs abiertos vía API de GitHub, y la metadata real de Superset
  en ambas ocasiones. Esa verificación fue correcta: el fix no estaba ahí en ese momento.
- Al encontrar el fix ya mergeado como BUG-047 durante la sincronización, no lo ignoré ni lo
  descarté — leí su implementación completa, su comentario ("hay que actualizar este valor a
  mano cada ciclo") y su suite de pruebas antes de decidir cómo reconciliar.
- Elegí fusionar los dos mecanismos en vez de que uno reemplazara al otro, preservando el trabajo
  y las pruebas de Manuel/Marina intactas.
- Corregí mi propio registro duplicado (`BUG-050`) en cuanto lo detecté, siguiendo el
  precedente ya establecido en el proyecto (BUG-041→043).
- Verifiqué el resultado en los 9 datasets afectados con consultas reales, no solo confié en que
  el sync terminara sin errores.
- Corrí la suite completa (872 passed) y `vault_lint` antes de dar el fix por terminado.

## Qué falta / bloqueos

- **De mi lado, ninguno.** El fix está aplicado, verificado y con pruebas de regresión, sobre el
  trabajo ya existente de Manuel y Marina, no en su lugar.
- Manuel y Marina pueden revisar la mejora dinámica si quieren, aunque el número que ya
  documentaron (`"2024-2025"`) no cambia con este fix — solo deja de requerir mantenimiento
  manual en el próximo ciclo.

## IDs tocados

US-203, US-204, US-211a, US-211b, US-222, REQ-002, BUG-047 (BUG-050 retractado por DEC-013)
