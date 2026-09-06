---
project: "FARO"
date: "2026-09-06"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — diagnóstico del KPI-04 «escuelas en riesgo» = 0 en el Mapa de Riesgo; se registra BUG-058 con dos salidas (recalibrar el umbral de alerta para la demo / ampliar el universo a media superior como ruta estratégica) para que C2 decida. C5 solo aporta la medición del universo de producción; no ejecuta el cambio."
touches: ["BUG-058", "DEC-006", "US-215a", "US-204", "US-113", "DS-03", "REQ-002", "REQ-001", "REQ-003"]
tags: [devlog, celula-5, riesgo, umbral, kpi-04, mapa-riesgo, dec-006, media-superior, diagnostico]
---

# DevLog — 2026-09-06 — El KPI-04 «escuelas en riesgo» da 0, y no es un defecto: es el umbral de alerta

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/_DevLog/2026-09-05-luis-tellez-parche-desfase-docs-c2-bug048|Parche de desfase docs C2 (universo 45 276)]] ·
[[vault/_DevLog/2026-09-05-edgar-coronel-bug048-cerrado-par-demo-roto|Cierre BUG-048 (el −4.53 % del PO)]]

## Contexto — qué se vio en la demo del Mapa de Riesgo

En el tablero **Mapa de Riesgo** (DB-02), el KPI **«escuelas en riesgo»** muestra **0 (0 %)**. A
primera vista parece un dato vacío o un pipeline roto. No lo es: es **matemáticamente correcto y
esperado**, y la causa está en la **calibración del umbral de alerta**, no en el código ni en el
modelo.

El umbral hoy es `indice_riesgo >= 0.60`, que por la sigmoide de **`DEC-006`** significa **"perder
≥ 5 % de matrícula"**. El problema tiene **doble evidencia**, y por eso no es un ajuste cosmético:

1. **Empírica.** La mayor caída **NETA** que ML-01 predice sobre el **Gold real de producción** es
   **4.53 %** (máx `indice_riesgo` = **0.5717**; medido al cerrar BUG-048, ratificado por el PO en su
   DevLog *"caída máxima −4.53 % contra el umbral de −5 %… ése es el número correcto"*). Con el techo
   del fenómeno **por debajo** de la línea de alerta, el conteo es **0 por construcción**: ninguna
   escuela puede cruzar un umbral que el modelo nunca alcanza.
2. **De negocio.** La **deserción escolar** real en México es **0.6 % en primaria** y **3.7 % en
   secundaria** (ciclo 2023-2024, educación básica). Un umbral de alerta puesto en **5 %** describe
   una **crisis consumada**, no el punto donde una alerta **temprana** —el propósito del tablero—
   debería encender. La línea está calibrada para un fenómeno más violento que el que ocurre en el
   nivel educativo que hoy observa FARO.

**Conclusión:** el modelo está bien, la sigmoide está bien, el dato está bien. Lo que está
**descalibrado para el propósito de alerta** es **dónde ponemos la línea**. Y esa línea, hoy pegada
al ancla de negocio de la sigmoide (`DEC-006`), es **separable** de ella: se puede mover el corte del
KPI **sin tocar** cómo se calcula el índice.

## Dos salidas — para que C2 pondere (no las ejecuta C5)

### Salida B1 — recalibrar el umbral de alerta (para la demo del 9-sep)

Bajar **solo la línea de alerta del KPI** a un corte que sí exista en los datos, p. ej.
**`indice_riesgo` en 0.45–0.50** (≈ perder **2.6–3.4 %**), **sin recalibrar la sigmoide**:

- Los valores `indice_riesgo` **no cambian** (la sigmoide y sus anclas quedan intactas).
- **No se re-publica Gold ni se re-entrena** ningún modelo.
- Es **reversible** en una línea de configuración.
- El diferenciador (driver dominante por escuela) **no se toca**: sigue explicando *por qué* cada
  escuela está donde está.

Es la salida **recomendada para la entrega**, porque hace que el KPI **cuente algo** sin alterar la
integridad del índice ni la narrativa de C2.

### Salida D — ampliar el universo a media superior (ruta estratégica)

La observación que motivó registrar esto: la **deserción en media superior (prepa) es 11.3 % anual**
— **muy por encima del 5 %**. Si el universo incluyera ese nivel, el umbral de `DEC-006` **aplicaría
tal cual, sin moverlo**: habría escuelas cruzando los 5 % de forma legítima. Es la salida más
**honesta** (deja el umbral intacto y verdadero), pero también la más **cara y arriesgada**, y **hoy
no es viable dentro del CODE FREEZE**:

- **El pipeline excluye media superior por diseño**, no por un filtro flojo:
  `dbt/models/silver/matricula_historica.sql` filtra a `PREESCOLAR / PRIMARIA / SECUNDARIA`, y
  `NIVELES_BASICA` en `src/ingesta/validacion_cct.py` y `src/ingesta/cargar_bronze_cct_real.py`
  acota la carga a esos tres niveles.
- **Salvedad decisiva — CEMABE (DS-03) no cubre media superior.** CEMABE alimenta **D3
  (infraestructura)** y **D4 (conectividad)**, los **únicos dos drivers a nivel escuela**. Si
  entraran prepas, D3/D4 llegarían como **`SIN_DATO` estructural** justo en el nivel de mayor riesgo,
  **debilitando la tesis del "sensor multidimensional"** precisamente donde más debería lucir.
- Es trabajo de **C1 (ingesta) + C3 (modelo)**, **no de C5**, y excede el CODE FREEZE del 6-sep.

Por eso **B1 y D no compiten**: B1 resuelve la demo; D queda como **historia futura** (extender el
sensor a EMS, resolviendo antes la cobertura de D3/D4). Se registra ahora para **no perder la idea**.

## Qué aporta C5 y qué NO — medición del universo (prod)

C5 **solo aporta la medición** del universo completo de producción (45 276 escuelas, Gold post
BUG-048), que C2 no puede recalcular desde su muestra local:

| Corte de `indice_riesgo` | ≈ % de pérdida | Escuelas | % del universo |
|---|---|---|---|
| **≥ 0.60** (umbral actual) | 5.0 % | **0** | 0 % |
| ≥ 0.50 | 3.4 % | 7 | 0.015 % |
| ≥ 0.45 | 2.6 % | ≈ p95 (~2 000) | ~5 % |
| ≥ 0.40 | 1.8 % | 11 775 | 26.0 % |
| ≥ 0.35 | 0.9 % | 24 951 | 55.1 % |

El **"punto dulce"** de una alerta *temprana* razonable cae en **0.45–0.50**; **cuál exactamente es
decisión de C2**, no de C5.

## Ownership — por qué C5 solo registra (regla 9)

- **`Bug_Register.md`, este DevLog y `_index` son comunes** → C5 puede escribirlos. Es lo único que
  se toca en este PR.
- **La decisión del umbral es de C2** (Marina García del Buey, con Manuel Serranía —TL— y firma del
  PO), con **Christian Ruiz (C4)** por el filtro `indice_riesgo >= 0.6` en
  `src/api/repositorio_gold.py`. Se asienta como **DEC-019** (revisión de `DEC-006`) — **la abre y
  firma C2/PO**, no C5. El código del corte vive en scope **C2** (`prediccion_client.py`,
  `2_Panel_ML.py`) y **C4** (`repositorio_gold.py`, `gold.py`); C3 posee la sigmoide
  (`src/modelos/riesgo.py`), que **B1 no toca**.
- **La salida D (media superior)** es historia futura de **C1 + C3**; su US la abre el **PO**
  (`vault/02_Requirements` es scope de Edgar), no C5. Dejo un borrador de esa US como handoff en
  `_local/` para que Luis se lo pase al PO — **no puede vivir en este PR** por ownership.

**C5 no ejecuta ni el cambio de umbral ni la ampliación.** Diagnostica, mide y registra.

## Avisos a otros owners

- **C2 (Marina García del Buey / Manuel Serranía):** el KPI-04 = 0 es correcto pero **poco útil para
  alertar**. Con la tabla de arriba pueden decidir el nuevo corte (B1) y firmar **DEC-019**. La
  narrativa de C2 y `DEC-006` **no se tocan** aquí.
- **C4 (Christian Ruiz):** cuando C2 fije el umbral, el cambio muerde en el filtro
  `indice_riesgo >= 0.6` de `src/api/repositorio_gold.py` (dos sitios, KPI-04) y en el rótulo del
  cliente.
- **C3 (modelos):** B1 **no requiere** re-entrenar ni re-anclar la sigmoide; solo la salida D (EMS)
  implicaría trabajo de modelo, y va después del freeze.
- **PO (Edgar Coronel):** BUG-058 pide **una decisión** (DEC-019), no un fix de código; y propone
  abrir la **US de media superior** como roadmap. Ambas son tuyas / de C2 por ownership.

## Seguridad / alcance

- [x] **Sin código** (`src/**`), sin `dbt/**`, sin `superset/**`, sin infra ni env-vars.
- [x] Solo archivos **comunes**: `Bug_Register.md`, este DevLog y `_index.md`.
- [x] **No se movió `DEC-006`** ni la narrativa de C2; el BUG *recomienda* la revisión (DEC-019),
      que firma C2/PO.
- [x] Medición del universo tomada **read-only** en el cierre de BUG-048 (ya documentada); aquí no se
      corrió nada nuevo contra producción.
- [x] Cero secretos / cero correos: personas por nombre y rol.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog; fila **BUG-058** en `Bug_Register.md`; fila en `_index.md`.
- **Modificados:** ninguno de código.
- **Handoff pendiente (Luis):** borrador de la US de media superior en `_local/` para el PO/C1/C3.
