---
id: DEVLOG-2026-09-06-HECTOR-MORALES-DEC019
project: "FARO"
date: "2026-09-06"
owner: "Héctor Rafael Morales Marbán"
status: filed
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sincronización, validación del plan y la parte de C3 de DEC-019"
touches: ["DEC-019", "RISK-010", "BUG-058", "US-311", "US-313", "REQ-003"]
traces_up: ["US-311", "US-313"]
tags: [devlog, celula-3, ml, dec-019, riesgo]
---

# DevLog — 2026-09-06 — La parte de C3 de `DEC-019`, y 179 archivos que no eran del repositorio

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/_DevLog/2026-09-05-hector-morales-validacion-y-retractacion|Mi sesión de ayer]] ·
[[vault/_DevLog/2026-09-06-christian-ruiz-dec019-linea-de-alerta|La parte de C4]] ·
[[vault/_DevLog/2026-09-06-marina-garcia-p0-panel-ml-ficha-busqueda|La parte de C2]]

## 1. C3 era la única capa que no había implementado `DEC-019`

`DEC-019` se firmó hoy y separa dos números que eran uno solo: el **ancla de la sigmoide** (`0.60`,
calibración de `DEC-006`) y la **línea de alerta** (`0.50`, con la que los tableros *cuentan*
escuelas). C4 ya renombró (`repositorio_gold.py`), C2 también (`prediccion_client.py`) y C1 ya corrió
el cambio en dbt (PR #273).

C3 no. Y `RISK-010` nombra mis archivos línea por línea. Lo que encontré al abrirlos:

| Archivo | Afirmaba | Estado |
|---|---|---|
| `riesgo.py:13` | *"los tableros cuentan escuelas en riesgo con `indice_riesgo >= 0.6`"* | **falso desde hoy** |
| `riesgo.py:25` | *"`0.60` \| justo el umbral de 'escuela en riesgo' de los tableros"* | **falso** |
| `riesgo.py:60` | *"Umbral con el que los tableros cuentan escuelas en riesgo"* | **falso** |
| `publicar_gold.py:180` | *"`0.60` es el umbral de 'escuela en riesgo' que usan los tableros"* | **falso** |

Importa más de lo que parece porque **`publicar_gold.py` cita `DOC-INDICE-RIESGO` —mi documento— como
la autoridad de esa afirmación**. La fuente canónica de una decisión tomada hoy estaba muda, mientras
tres células ya la habían implementado leyendo de ella.

## 2. Qué cambié — y qué deliberadamente no

**Sí:** `RIESGO_UMBRAL` pasa a llamarse **`ANCLA_SIGMOIDE`**, el mismo nombre que ya usan C4 y C2, con
el nombre viejo conservado como alias para no romper importaciones. Los cuatro docstrings falsos
quedan corregidos y apuntan a `repositorio_gold.py::LINEA_DE_ALERTA` para el corte. `§4.4` nuevo en
[[vault/15_ML_Models/Indice_Riesgo_ML01]].

**El valor no se mueve: `ANCLA_SIGMOIDE` sigue en `0.60`.** `DEC-019` cambia el criterio de alerta,
no la calibración. Moverla a 0.50 recalibraría la sigmoide y reinterpretaría **todo** lo publicado.

**No definí `LINEA_DE_ALERTA` en `riesgo.py`, y es lo que más me tentó hacer.** Parecería lo natural
—es el módulo que define el índice—, pero `RISK-010` está abierto precisamente porque `0.50` ya está
escrito **dos veces** sin una prueba que las ate. Una tercera definición agrava el riesgo que estoy
tratando de no empeorar. La fuente única es trabajo post-freeze.

## 3. Un hallazgo que no esperaba: el `0.50` sale de mi propio documento

`DEC-019` justifica el `0.50` diciendo que equivale a proyectar **−3.4 %**, justo debajo del 3.7 % de
deserción real en secundaria. Ese número no lo calculó la decisión: **ya estaba en `§4.1` de
`Indice_Riesgo_ML01.md`** desde agosto, como nota al margen del ancla `0.30`.

Lo reverifiqué corriéndolo: `variacion_equivalente(0.50) = −0.03382`. Coincide. Lo dejo escrito
porque significa que el ancla `0.30` —la decisión que sigue abierta— **no es cosmética**: mueve el
punto medio de la escala y, con él, lo que la línea de alerta significa en lenguaje de negocio.

## 4. Lo que dejé abierto en vez de decidirlo

`publicar_gold.py::prioridad_de_riesgo()` marca `ALTA` a partir del **ancla** (`0.60`), no de la
línea (`0.50`). **Lo dejé sin cambiar a propósito.** Moverlo reescribiría la columna `prioridad` de
las 45,276 filas ya publicadas en `gold.recomendaciones`, y `DEC-019` dice explícitamente que no
cambia un solo valor publicado.

¿Debe `prioridad` seguir la línea de alerta? Es un juicio de negocio para **Edgar (PO)** y **Andrés
(TL de C3)**, no una decisión de implementación, y menos en día de freeze. Queda escrito en el
docstring y en `§4.4` del documento para que no se pierda.

## 5. 179 archivos que no eran del repositorio

La suite reprobó **20 pruebas** y `vault_lint` reportó **36 problemas bloqueantes**. Ninguno era mío.

Tras el merge de 434 commits aparecieron **179 archivos sin rastrear** con el patrón `<nombre> 2.<ext>`
—`mock_data 2.py`, `Execution_Status 2.md`, `ownership 2.yml`—: copias de conflicto de **iCloud**,
que sincroniza `~/Desktop`, donde vive mi clon. `pytest`, `ruff` y `vault_lint` los recogían como
archivos reales.

Verifiqué que **los 179 tenían un original rastreado** antes de tocarlos, y los moví a cuarentena
fuera del repositorio en vez de borrarlos. Con eso: **1042 passed, 8 skipped, 0 failed**.

> [!warning] Esto le puede pasar a cualquiera con el clon bajo iCloud
> Un `git add .` a ciegas el día del freeze habría metido **179 archivos basura** al PR, incluidos
> duplicados de `ownership.yml` y `Execution_Status.md`. El plan de sprint ya dice *"NUNCA uses
> `git add .` a ciegas"* (§6.3) y hoy quedó claro por qué. **No agregué un patrón a `.gitignore`**
> aunque está en `comunes`: `* 2.*` es lo bastante ancho para ocultar un archivo legítimo, y
> cambiar infraestructura compartida el día del freeze sin pedirlo no me toca. Lo reporto.

## Verificación

`pytest tests/ -q` → **1042 passed, 8 skipped** · `ruff check src/ tests/` → *All checks passed* ·
`vault_lint.py` → ✅ Vault limpio · `git status` sólo mis 4 archivos · rama sincronizada con
`origin/main` (0/0).

**Las dos guardas nuevas están falsificadas:** puse `ANCLA_SIGMOIDE = 0.50` y reprobaron las dos
(`test_dec019_no_recalibra_la_sigmoide` y `test_la_linea_de_alerta_equivale_al_menos_34_por_ciento`);
restaurado el valor, pasan. Existen para cazar exactamente a quien "actualice" el ancla a 0.50
creyendo que `DEC-019` pedía eso.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Archivos modificados:** `src/modelos/riesgo.py`, `src/modelos/publicar_gold.py`,
  `tests/test_riesgo.py`, `vault/15_ML_Models/Indice_Riesgo_ML01.md`, este DevLog, su índice y mi
  fila de la matriz.
- **🔴 Fuera de alcance, no tocado:** `vault/12_Roadmap_Sprints/Execution_Status.md` (del PM) —
  la fila de `US-313` sigue pidiendo *"aprobar `Publicacion_Gold` (sigue en `status: in_review`)"* y
  ese documento está en **`approved`** desde el 5-sep. `vault/10_Risk_Governance/Risk_Register.md`
  — `RISK-010` puede tachar la parte de C3, pero es del PO. `.gitignore` — ver §5.
- **Decisiones autónomas del agente:** no definir `LINEA_DE_ALERTA` en `riesgo.py` para no agravar
  `RISK-010`; no mover `prioridad_de_riesgo()` para no reescribir datos publicados en freeze;
  poner los 179 duplicados en cuarentena en vez de borrarlos, verificando antes que cada uno
  tuviera original rastreado.

## Pendientes

1. **PO — Edgar Coronel:** fila de `US-313` en `Execution_Status.md` (su único pendiente ya no
   existe) y la parte de C3 de `RISK-010`, que hoy queda cubierta.
2. **PO + TL de C3 — Edgar y Andrés:** ¿`prioridad` sigue la línea de alerta? (§4).
3. **Todos, informativo:** los duplicados de iCloud (§5).
