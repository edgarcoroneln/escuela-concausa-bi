---
project: "FARO"
date: "2026-09-13"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1h"
touches: ["DEC-026", "BUG-063", "RISK-010", "DEC-019", "US-313", "REQ-003"]
tags: [devlog, ml, celula-3, gold, dec-026]
---

# DevLog — 2026-09-13 — `DEC-026`: el corte de `prioridad` baja a la línea de alerta

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

La **mitad de código** de `DEC-026`. Recordatorio de Imanol: la decisión se firmó el 12-sep y
`publicar_gold.py:197` seguía con `>= ANCLA_SIGMOIDE` en `main`, en mi rama y en la de Estefany —
verificado blob por blob, tenía razón.

**La otra mitad —republicar Gold— no se hizo y no la puedo hacer.** Ver §3.

## 1. El cambio

`prioridad_de_riesgo()` marcaba `ALTA` sólo desde `ANCLA_SIGMOIDE` (0.60), y el máximo que ML-01
predice sobre el Gold de producción es **0.5717**: ninguna de las 45,276 escuelas calificaba, y la
tarjeta *«Recomendaciones de prioridad ALTA»* de DB-09 leía **0** — en el tablero del diferenciador
(`BUG-063`). El corte estaba **por encima del techo del fenómeno**, no era un defecto del modelo.

Ahora usa `LINEA_DE_ALERTA` (0.50). **El ancla no se mueve**: sigue en 0.60 calibrando la sigmoide
(`DEC-006`). Cambia la categoría de negocio, no la calibración.

## 2. Dónde vive la constante, y por qué cambié de postura

`LINEA_DE_ALERTA` no existía en `src/modelos/**`. Vivía dos veces: `src/api/repositorio_gold.py:55`
(C4) y `src/frontend/prediccion_client.py:43` (C2). Tres opciones:

| Opción | Por qué no / sí |
|---|---|
| Importarla del API | Invierte la dependencia: los modelos no deben depender de la capa que los expone |
| Escribir una tercera copia | Agrava `RISK-010`, que existe precisamente por eso |
| **Hacerla canónica en `riesgo.py`** | ✅ Es donde vive la semántica del riesgo, y es mi verde |

**Esto invierte una decisión mía del 6-sep.** Ese día escribí en `riesgo.py` que el módulo **no**
debía definir la línea de alerta, con este argumento: `0.50` ya estaba escrito dos veces y una
tercera copia agravaría `RISK-010`. El argumento era correcto **mientras la capa de modelos no
necesitara el número**. `DEC-026` cambió eso. Dejé la nota vieja reescrita en el docstring
explicando el cambio de postura, en vez de borrarla como si nunca hubiera existido.

**No cierra `RISK-010`**: las copias de C4 y C2 siguen ahí, y retirarlas es de sus dueños. Lo que sí
hace es dar el lugar al que deben apuntar y **atarlas con una prueba** — el riesgo decía
literalmente *«no hay prueba que los ate»*, y ésa era la mitad que faltaba.

## 3. Lo que NO se hizo: republicar Gold

`prioridad` es columna **almacenada**, no derivada en consulta. Sin volver a correr `publicar_gold`
contra el Gold vigente, **la base conserva el corte viejo por más que el código diga otra cosa** —
o sea que la tarjeta de DB-09 seguirá en 0 hasta que alguien republique.

**No puedo hacerlo desde aquí, y no es una excusa de proceso:**

- Mi base tiene `mlflow_run_id = local-sin-mlflow`: es **una corrida personal mía**, no la de
  producción (`bug048-20260905-temporal-robusto`). Republicar desde aquí **sobrescribiría las
  45,276 filas con mis números**.
- Su máximo de `indice_riesgo` es **0.3744**, no 0.5717. Sobre mis datos, el corte en 0.50 **tampoco
  produciría ninguna fila `alta`**: el arreglo ni siquiera se notaría.

Hace falta que Edgar responda **cuál Gold es el autoritativo y quién puede correr el job contra
él**. Con eso, republicar es un solo comando.

## 4. Las dos guardas, y por qué la de `BUG-063` no consulta la base

**`tests/test_prioridad_alcanzable.py`** — lo que `DEC-026` pedía: que reprucbe si el corte de la
categoría más alta queda por encima del techo del fenómeno.

`DEC-026` proponía contrastarlo contra *«el máximo observado en el Gold publicado»*. **Consultar la
base conectada habría sido un error**: sobre mi Gold (máximo 0.3744) la prueba saldría roja y
dejaría el CI en rojo para todo el equipo sin que nada esté mal en el código. Se afirma la
propiedad con el techo **declarado como dato** —`MAXIMO_OBSERVADO_EN_GOLD = 0.5717`, con su
procedencia y una nota de que si el modelo se recalibra hay que actualizarlo con la corrida nueva,
no subirlo para que la prueba pase.

**`tests/test_linea_de_alerta_unica.py`** — ata las copias de C4 y C2 a la canónica, nombrando al
dueño en el mensaje de error. Es la prueba que `RISK-010` pedía. Ya pasó una vez con este número
exacto: `BUG-060` documenta que el camino mock del KPI-04 contaba con 0.50 y el real con 0.60, y
**cada camino se probaba contra sí mismo**, así que la divergencia era invisible.

**Las dos se falsificaron**, que es lo único que prueba que una guarda sirve:

| Defecto reintroducido | Resultado |
|---|---|
| Corte de vuelta en `ANCLA_SIGMOIDE` | 3 fallos en `test_prioridad_alcanzable` |
| Canónica movida a 0.55 | 3 fallos en `test_linea_de_alerta_unica` |

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Modificados:** `src/modelos/riesgo.py` (constante canónica + docstring),
  `src/modelos/publicar_gold.py` (corte y docstring), `tests/test_publicar_gold.py`
- **Creados:** `tests/test_prioridad_alcanzable.py`, `tests/test_linea_de_alerta_unica.py`
- **Decisiones autónomas del agente:** hacer canónica la constante en `riesgo.py` en vez de
  importarla del API; declarar el techo como dato en vez de consultarlo de la base.
- **Correcciones manuales:** ninguna. **Una prueba existente reprobó y era correcto que lo
  hiciera**: `test_prioridad_usa_los_umbrales_ya_ratificados` afirmaba que 0.59 → `MEDIA`, que era
  el comportamiento viejo. Se actualizó a `DEC-026` conservando lo que protege, y se le añadió que
  el ancla y la línea siguen siendo dos cortes distintos.
- **Prompt inicial:** recordatorio de Imanol sobre `DEC-026` sin ejecutar.

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] `pytest tests/ -q` → **1314 passed, 10 skipped** (eran 1303; +11)
- [x] `ruff check src/ tests/` limpio · los 3 doctests de `prioridad_de_riesgo` pasan
- [x] **No se tocó ninguna base de datos**
- [x] DevLog enlaza a los IDs afectados

## Bloqueantes

- **Republicar Gold**: falta que Edgar defina cuál Gold es el autoritativo y quién corre el job.
  Hasta entonces la tarjeta de DB-09 sigue en 0 aunque el código ya esté bien.
- **Asignación ambigua**: `DEC-026` dice en la misma frase que el cambio *«es alcance de Estefany
  Hernández Loredo»* y que está *«asignado por `BUG-063` a Héctor Morales»*. Se hizo desde C3 con
  `src/modelos/**` en verde; si Estefany ya lo tenía en curso, hay trabajo duplicado que conviene
  cortar hoy.
- **`prioridad` en las filas ya publicadas** conserva el corte viejo hasta la republicación.

## Próximos pasos

- Que Edgar responda las dos preguntas de arriba; con eso, republicar es un comando.
- Que C4 y C2 decidan si retiran sus copias de `LINEA_DE_ALERTA` e importan la canónica. La prueba
  ya las ata, así que retirarlas es seguro.
