---
id: DEVLOG-2026-09-05-HECTOR-MORALES-VALIDACION
project: "FARO"
date: "2026-09-05"
owner: "Héctor Rafael Morales Marbán"
status: filed
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "validación integral, retractación de un diagnóstico y verificación de la URL pública"
touches: ["US-313", "US-311", "BUG-048", "BUG-020", "BUG-053", "SEC-006", "REQ-003", "REQ-004"]
traces_up: ["US-313", "US-311"]
tags: [devlog, celula-3, ml, validacion, correccion, produccion]
---

# DevLog — 2026-09-05 — Validación integral, un diagnóstico mío retirado, y la URL pública en 401

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/_DevLog/2026-09-04-hector-morales-ambiente-real-us313|Mi sesión de ayer]] ·
[[vault/_DevLog/2026-09-05-andres-gonzalez-bug048-rerun-ml|Rerun de Andrés]]

## 1. Retractación: `cubo_pipeline` no era un bug de C1

Ayer reporté que `cubo_pipeline` fallaba con
`UNION types timestamp without time zone and text cannot be matched` y **lo atribuí a un defecto del
modelo de C1**, distinto del que Oscar había visto. Estuvo a punto de irse en una nota al equipo.

Es falso. Verifiqué el tipo antes de mandarla: `bronze.conagua_presas._ingested_at` es **`text`** en
mi base local, y el modelo espera `timestamp`. Es un artefacto de **mi** tabla —la que conservé del
estado previo de mi ambiente—, no del código: Oscar lo tiene materializado con 10 filas y el dump de
Andrés trae `cubo_pipeline` real con 11.

Es el segundo diagnóstico que emito contra un modelo de C1 y resulta ser mío; el primero fue el de
`features_escuela` el 2-sep. El patrón que comparten: **atribuí a código ajeno el estado de mi
propio ambiente.** Lo dejo escrito en vez de borrarlo porque la conclusión de ayer se publicó.

## 2. Mi corrida quedó superseded, y mis hallazgos confirmados por otra vía

Andrés González (TL de C3) corrió el rerun definitivo el mismo día, con el dump de Diana que
incorpora **CONAPO real**, y **reprodujo mis tres hallazgos sin haber visto mi trabajo**:

| Mi medición (4-sep) | La suya |
|---|---|
| MAE **0.1592** con pérdida cuadrática | MAE **0.159148**, "mejora prácticamente nula" vs baseline 0.159223 |
| 0 escuelas en riesgo, modelo aplastado | idem — "todas las predicciones positivas" |
| **1,168** huérfanas fuera de `fact_escuela_ciclo` | **1,168**, el mismo número exacto |

Adoptó `loss="absolute_error"` en `entrenar_ml01.py` — la misma familia de arreglo que yo iba a
proponer (winsorizar), resuelta por la vía más limpia: MAE **0.141458**, **11.04 %** mejor que el
baseline temporal, sin tocar las anclas de riesgo.

**Y decidió lo contrario que yo en las huérfanas:** las conserva a petición de Luis Téllez, *"no se
borraron filas para forzar el gate"*. Yo iba a filtrarlas contra el hecho para poner dos pruebas de
dbt en verde. **Su decisión es la correcta y la mía habría escondido el desfase**: el gate en rojo
es información, no ruido. Que no lo hiciera solo el viernes fue lo que evitó el error.

**Consecuencia para mi ambiente:** mis 45,276 predicciones locales traen la pérdida cuadrática vieja
y SESNSP/CONAPO de fixture. Las vigentes son las de Andrés. No re-publico encima: el entregable a C5
ya salió (`gold_bug048_final2_2026-09-05.sql`) y duplicar la corrida sólo agregaría una tercera
versión de la verdad a un día del freeze.

## 3. Verificación de la URL pública — `BUG-020` resuelto de hecho, y un 401 nuevo

Adelanté la verificación que el plan pone para el domingo. Medido hoy contra
`https://faro-api-eanzfglvyq-uc.a.run.app`:

| Ruta | Código |
|---|---|
| `/api/v1/health` · `/version` · `/docs` | **200** |
| `/api/v1/kpis` · `/escuelas` · `/municipios` · `/predicciones/{cct}` | **401** |

**`BUG-020` está resuelto de hecho:** ninguna ruta responde ya 500, y su fila del `Bug_Register`
sigue diciendo `pendiente` — está desactualizada.

Pero **toda ruta de datos responde 401 a un visitante anónimo**. Edgar sí obtuvo valores de `/kpis`
esta mañana al cerrar `BUG-048`, así que la condición cambió después; C5 desplegó hoy varias guardas
de SSO y `SEC-006` (flip de lectura pública) estaba explícitamente "a decisión C5+PO" en el DevLog
de Luis del 4-sep. **No afirmo la causa: reporto la medición y la hora.** Importa porque el punto de
rúbrica es una URL pública funcionando y porque el ensayo del martes la usa.

`/version` sigue devolviendo `33fcbbb`, por detrás de `main`, como ya anotó Edgar.

**Respondido al sincronizar, antes de abrir el PR:** el 401 **es intencional**. C5 cerró `SEC-006`
apagando `AUTH_LECTURA_PUBLICA` en Cloud Run (revisión `faro-api-00012-pq5`, cambio de variable de
entorno, sin rebuild — por eso `/version` no se movió). Era la condición de cierre que esperaba a que
el login e2e quedara validado con `BUG-046`. Mi medición no descubrió un defecto: **confirma el flip
desde fuera**, de forma independiente y sin conocerlo. Queda una consecuencia real para el 9: quien
abra la URL pública sin sesión ya no ve KPIs ni predicciones, y el guion de la demo tiene que
contemplar el login.

## 4. Lo único mío que sigue vivo

De las dos sesiones, el hallazgo que **nadie más documentó** es la duplicación ×2 de Bronze
(`_ingested_at` dentro de la llave UNIQUE de `formato911_historico`; `cct_siged_202608` sin ningún
índice) y que [[vault/14_Data_Sources/DS-01_Formato_911]] §11 afirme una idempotencia que no existe.
Sigue en pie y es de C1.

## Verificación

`pytest tests/ -q` **970 passed, 8 skipped** · `ruff check src/ tests/` limpio · `vault_lint.py`
limpio · `git status` limpio · rama sincronizada con `origin/main` (0/0) tras merge de 154 commits ·
`curl` a las 7 rutas de producción listadas arriba.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Archivos modificados:** este DevLog, el del 4-sep, su índice, `Publicacion_Gold.md` y mi fila de
  la matriz de trazabilidad.
- **🔴 Fuera de alcance, no tocado:** `vault/12_Roadmap_Sprints/Execution_Status.md` (del PM) —
  su fila de `US-311` sigue en `in_progress` citando el MAE 0.0141 del 25-ago, desactualizada desde
  el cierre de `BLOCK-001`; se pide al PM que la actualice. `vault/06_Quality_Testing/Bug_Register.md`
  tampoco: la duplicación de Bronze se reporta a su dueña en vez de darla de alta yo.
- **Decisiones autónomas del agente:** verificar el tipo de la columna antes de mandar la nota, lo
  que evitó reportar un bug inexistente contra C1; no re-publicar sobre el entregable de Andrés.

## Pendientes

1. **C1 — Diana Alvarez:** duplicación ×2 de DS-01/DS-02 y la afirmación de §11.
2. **C4/C5 — el 401** de las rutas de datos en producción, y la fila de `BUG-020` desactualizada.
3. **PM — Edgar Coronel:** fila de `US-311` en `Execution_Status.md`.
