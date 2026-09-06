---
project: "FARO"
date: "2026-09-06"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "firma de DEC-019, registro de RISK-010 y verificación de la cadena del umbral"
tags: [devlog, pm, dec-019, risk-010, bug-058, umbral, freeze]
---

# DevLog — 2026-09-06 — `DEC-019` firmada, y la mitad de la cadena que no tiene dueño

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/10_Risk_Governance/Decision_Log]] ·
[[vault/10_Risk_Governance/Risk_Register]]

## 1. `DEC-019` — el número que hacía dos trabajos

Marina García pidió la firma con urgencia y tenía razón en lo esencial: **`DEC-019` no existía en
`main` y ya lo citaban ramas**, contra `DEC-013`. Dijo cuatro; **verifiqué y son cinco**:
`marina-garcia`, `christian-ruiz`, `andres-gonzalez`, `estefany-hernandez` y `luis-tellez`.

El contenido lo eligió C2 y no lo reabrí. Lo que sí hice fue entender **por qué es correcto**, y es
más interesante que "bajar un umbral": **0.60 estaba haciendo dos trabajos incompatibles.** Es la
equivalencia de negocio que calibra la sigmoide —perder 5 % de matrícula— y **además** era el corte
con el que los tableros contaban. Como corte de alerta es **inalcanzable por construcción**: el
máximo que ML-01 predice sobre 45 276 escuelas es **0.5717**. El KPI daba 0 porque el corte estaba
**por encima del techo del fenómeno**.

El criterio de C2 para 0.50 es de negocio, no de conveniencia: ≈ −3.4 %, **justo por debajo del
3.7 % de deserción real en secundaria**. La alerta enciende antes de que la escuela alcance la norma
nacional. Y no baja más porque a 0.40 serían 11 775 escuelas (26 %) y a 0.35, 24 951 (55 %) — a esa
escala deja de ser alerta y es un censo. Con 0.50 son **7 de 45 276**.

## 2. Me equivoqué al decir que faltaba la mitad de la cadena

Escribí en `DEC-019` —y se lo dije al PO— que `src/api/repositorio_gold.py` y
`src/frontend/prediccion_client.py` *"siguen en 0.60 y no los tiene nadie en ninguna rama"*. **Era
falso.** El error fue de método, y es **el mismo que Marina García ya me señaló con `latitud`**:
busqué por el **nombre viejo** de la constante (`UMBRAL_RIESGO`) y las dos células la habían
**renombrado**.

Buscando por el valor y no por el nombre, la realidad es la contraria y mucho mejor:

| Capa | Quién | Commit / PR |
|---|---|---|
| **dbt** (5 archivos) | Diana Alvarez | `ad3d2fd`, empujado, **sin PR** |
| **API** (`repositorio_gold`, `mock_data`, `v1/gold`) | Christian Ruiz | `0f4b37c`, empujado, **sin PR** |
| **Frontend** (`prediccion_client`, `2_Panel_ML`) | Marina García | **PR #268 abierto**, 4/4 verde |
| **`DEC-019`** (registro) | Edgar Coronel | esta rama, **sin PR** |

**Las tres capas están escritas, y las tres separan el ancla de la línea con el mismo nombre**
—`ANCLA_SIGMOIDE` / `LINEA_DE_ALERTA`—. C1, C2 y C4 se coordinaron en la nomenclatura **sin que el
PO lo pidiera**, que es exactamente lo que uno quiere ver el día del freeze.

**Lo que falta no es código: son tres PRs y un orden.**

## 2.bis El riesgo real es el orden, y hay una asimetría de costo

Si entra una sola capa, **dos superficies del mismo sistema se contradicen**: los tableros dirían 7
y `/api/v1/kpis` diría 0 sobre el mismo dato. Peor que dejar todo en 0.60.

Y las capas no cuestan lo mismo:

- **API y frontend filtran en tiempo de consulta** → cambian con un **redespliegue**.
- **Los cubos de dbt materializan `escuelas_en_riesgo`** → exigen **regenerar Gold y reimportar a
  Cloud SQL**, que es de C5 y es el eslabón largo.

`RISK-010` sigue abierto porque la **duplicación persiste**: `LINEA_DE_ALERTA` queda definida dos
veces, en `repositorio_gold.py` y en `prediccion_client.py`, sin prueba que las ate.

## 3. El dato de Marina sobre C1 ya está vencido

Reportó que `origin/dev/diana-alvarez` estaba *"a cero commits de main y los cinco archivos de dbt
siguen en 0.6"*. **Era cierto cuando lo escribió y dejó de serlo:** Diana empujó a las **17:57 de
hoy** el commit `ad3d2fd fix(gold): baja linea de alerta de riesgo de 0.6 a 0.5`, y los cinco
archivos están en **0.5**. La rama va 3 commits adelante.

**Lo que falta no es el trabajo: es el PR.** No hay ninguno abierto desde esa rama. El empujón que
Marina pedía sigue siendo necesario, pero es de otra naturaleza — y la rama va **173 commits detrás
de `main`**, así que hay que sincronizar antes.

## 4. `RISK-010`

Registrado con probabilidad 4 e impacto 4, dueño el PO, objetivo **post-demo**. La propuesta de una
sola fuente —`var` de dbt más una constante importada en Python, con una prueba que falle si dos
sitios discrepan— es de **Christian Ruiz** y la respalda Marina. **Hoy no se hace**: tocar cuatro
células el día del freeze cambia lo que la demo enseña.

Con la salvedad que importa: **`riesgo.py::RIESGO_UMBRAL` se queda en 0.60**, porque ahí el número
significa el ancla de la sigmoide y no la alerta. Unificar sin esa distinción rompería la
calibración.

## Verificado

`pytest tests/ -q` → **1022 passed, 4 skipped** · `ruff` limpio · `dbt parse` exit 0 ·
`vault_lint.py` limpio · `TEST-002` válido · gate de propiedad en verde ·
`test_riesgo.py::test_reproduce_el_ancla_del_umbral_de_negocio` existe y sigue verde —confirma que
`DEC-019` no toca la calibración— · 5 ramas citando `DEC-019` contadas una por una ·
`repositorio_gold.py` y `prediccion_client.py` revisados en las 21 ramas

## IDs tocados

`DEC-019`, `RISK-010`, `DEC-006`, `BUG-058`, `US-113`, `KPI-04`, `REQ-001`, `REQ-002`, `REQ-003`

## Pendiente ajeno, anotado y no corregido

El **par de demostración** sigue sin elegirse y es criterio de aceptación de mi propio guion. Es de
C2 y Marina lo tiene anotado; se lo recuerdo hoy, no el lunes.

## Próximos pasos

- Diana sincroniza (va 173 detrás) y abre PR — es el primer eslabón.
- Alguien tiene que tomar el lado API + frontend del umbral, **hoy**, o se declara que el KPI-04 se
  queda en 0.60 en todas las superficies y `DEC-019` entra sólo como decisión.
- Marina elige el par de demostración con datos de producción.
