---
project: "FARO"
date: "2026-09-12"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — cierre de las dos preguntas abiertas del frente: DEC-026 y el mapa. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011", "DEC-026", "DEC-023", "DEC-019", "DEC-006", "BUG-063", "BUG-058", "US-651"]
tags: [devlog, equipo-3, ux, s7, us-621, dec-026]
---

# DevLog — 2026-09-12 — `DEC-026`, los cortes por contrato y el mapa resuelto (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec]]

## Contexto

Las dos preguntas que este frente dejó abiertas ayer se resolvieron el mismo día, y ninguna se
resolvió aquí: `BUG-063` lo cerró el PO como **`DEC-026`**, y el estatus del mapa lo cerró Diana
Álvarez desde el Equipo 5. Esta sesión las **registra**, que es lo que faltaba.

## 1. Los cortes dejan de teclearse (`GET /api/v1/version`)

Del trabajo de `DEC-026` salió un endpoint que no pedimos con ese nombre y que resuelve mejor lo que
sí pedimos: **`GET /api/v1/version` → `cortes_atencion`**, con `alta`, `media` y `ancla_calibracion`.

Tres cosas lo hacen la respuesta correcta y no un parche:

1. **Es público y sin token.** El front tiene los cortes **antes** del login y puede etiquetar lo que
   ya tenga en pantalla.
2. **Resuelve un problema de capas, no de comodidad.** `LINEA_DE_ALERTA` vive en
   `src/api/repositorio_gold.py` y la matrícula estable en `src/modelos/riesgo.py`. El front
   necesitaba las dos y no puede importar de ninguna. Tecleálas era el camino obvio, y es
   exactamente `BUG-058`.
3. **`ancla_calibracion` no es un corte de presentación.** Viaja para que el glosario explique la
   diferencia con DB-09 **sin teclear el `0.60`**.

Con esto se cierra la última coordinación abierta de la §11 del plan, *"importar, no reteclear los
cortes"*. La tabla de la §3.quater se reescribe **contra el contrato** en vez de contra dos rutas de
código: las celdas dejan de decir `0.50` y `0.30` y pasan a decir de dónde se leen.

## 2. `DEC-026`, y la trampa que trae

`DEC-026` baja el corte `alta` de `publicar_gold.prioridad_de_riesgo()` de `0.60` a `0.50` y
republica Gold. `ANCLA_SIGMOIDE` **no se toca**: sigue en `0.60` como calibración de la sigmoide
(`DEC-006`). Cambia la categoría, no el modelo.

**La regla de no consumir `prioridad` no caduca con el merge, y esto es lo importante de esta
sesión.** `prioridad` es una **columna almacenada**: cambiar el código no reescribe una sola de las
45 276 filas ya publicadas. Entre el merge y la republicación, la API devuelve **los valores viejos
con el código nuevo**, que es la peor combinación posible — todo parece arreglado y el dato dice lo
contrario. Quien vea el PR mergeado y cablee el chip a `prioridad` ese día, reproduce el bug entero.

Por eso la regla se levanta con una **condición verificable y no con una fecha**: cuando alguien
compruebe **contra producción**, no contra el código, que existe al menos una fila `alta` en
`gold.recomendaciones` y que su conteo coincide con `escuelas_en_riesgo` de `/kpis`. Queda escrito en
la §10.quinquies y entra al smoke de `US-651`.

## 3. El mapa: resuelto, y degradado a propósito

Diana Álvarez eligió la opción (a) con un matiz mejor que la pregunta: **el mapa se queda como
contexto de ubicación, no como ranking de riesgo**, porque la comparación por índice ya la resuelve
la lista de tarjetas. Es la lectura que la mitad viva del argumento original exigía —base **estatal,
no municipal**, siete escuelas en **dos municipios**— y evita que el mapa pretenda distinguir lo que
no puede.

Leyenda acordada, textual: *"Ubicación aproximada de las escuelas en riesgo — no reemplaza la
comparación por índice, ver lista."*

Tres condiciones verificables, registradas para QA:

1. El mapa **no** puede ser la única forma de leer el riesgo (`ADR-011` §4).
2. Las escuelas sin georreferencia **se omiten**; un marcador en el `(0, 0)` inventa una ubicación.
3. La palabra *aproximada* es literal y se queda: la base es estatal, el punto ubica y no
   georreferencia una dirección.

Queda como **§10.septies** del plan, y las dos filas de `02_Data_Visualization_Spec` (§3.3 y §8.1)
pasan de *recorte* a *pieza con lectura declarada*, con nota fechada, por la misma vía de la
corrección de ayer y con la autoría intacta.

## Qué NO se hizo

- **Nada de la ejecución de `DEC-026`.** El cambio de `publicar_gold.py` y la republicación de Gold
  son de C3 (Héctor Morales, Estefany Hernández, con Andrés González como TL). La prueba guarda que
  el propio `BUG-063` propone la escribe su autor.
- **No se retiró la advertencia del glosario de §3.quater.** Se marca como *en vías de desaparecer*,
  no como desaparecida, porque la divergencia con DB-09 vive hasta la republicación.

## Estado de `US-621`

Puntos 1 y 2 del criterio de cierre: cumplidos. **Punto 3: sin pendientes de contenido de este
frente** — el mapa y las rutas ya están resueltos y documentados; falta que E5 declare el handoff
aceptado. **Punto 4: el único abierto**, `US-651` sigue `planned`.
