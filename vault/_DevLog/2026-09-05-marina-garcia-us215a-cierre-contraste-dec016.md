---
project: "FARO"
date: "2026-09-05"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sesión: cierre de US-215a bajo DEC-016 y corrección del número de producción"
touches: ["US-215a", "US-207", "US-214a", "REQ-002", "BUG-050", "BUG-048", "BUG-052", "DEC-015", "DEC-016"]
tags: [devlog, accesibilidad, superset, bi, celula-2]
---

# DevLog — 2026-09-05 — US-215a cierra 22/22, y medir por elemento destapó un defecto propio

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB03_DB04]]

## Contexto

Edgar mergeó el PR #234 con `UX_Guidelines.md` en `approved` y **DEC-016**, la regla que
faltaba para poder cerrar el caso 3.1. Su lectura era que 3.1 cerraba como limitación
conocida y US-215a quedaba 22/22.

**La regla tiene dos mitades y solo se citó la primera.** La segunda dice que un elemento
que **sí escribe FARO** y no llega al umbral **es defecto y bloquea**. Cerrar sin medir eso
habría sido saltarse la mitad que sí me tocaba.

## 1. Por qué el score de Lighthouse no alcanzaba

El 93 dice que *hay* contraste insuficiente, pero no **en qué elemento** — y DEC-016 decide
justamente por elemento. Así que se midió con `getComputedStyle`, elemento por elemento,
sobre color y fondo **efectivos** (subiendo el árbol hasta el primer fondo opaco), en DB-03
y DB-04, en los dos temas.

| Tablero | Tema | Peor elemento escrito por FARO | Veredicto |
|---|---|---|---|
| DB-03 | claro | 19.26 : 1 | pasa |
| DB-03 | oscuro | 21 : 1 | pasa |
| DB-04 | claro | 19.26 : 1 | pasa |
| DB-04 | oscuro | 18.42 : 1 | pasa |

**Reprueban exactamente dos elementos, los dos del shell de Superset:** `Published` a
**2.16 : 1** y `Edit dashboard` a **3.07 : 1** en claro y **3.41 : 1** en oscuro. Son
heredados, así que por DEC-016 son limitación conocida y no bloquean. Esa medición se
adjuntó a **BUG-050**, que es lo que la propia regla exige y lo que el bug no tenía.

## 2. El defecto que el score escondía

Los cuatro `<a href>` de drill-down de DB-03 y DB-04 no traían estilo propio, así que
tomaban el azul de acento de Superset `#2893B3`.

- En tema **oscuro**: 5.91 : 1 — pasa.
- En tema **claro**, sobre el `#F5F5F5` de la celda de tabla: **3.26 : 1** — reprueba.

El 4-sep se revisó en oscuro, que es exactamente donde no falla.

**No se arregla eligiendo otro azul, y eso es aritmética, no gusto.** Pasar 4.5 : 1 contra
`#F5F5F5` exige luminancia ≤ 0.164; contra `#000000` exige ≥ 0.175. **Los rangos no se
cruzan**: ningún color único sirve para los dos temas.

La salida fue heredar el color del texto de la celda —que ya pasa en ambos— y marcar el link
con **subrayado** en vez de con tono. Queda en **19.26 : 1** claro y **21 : 1** oscuro, y de
paso cumple WCAG 1.4.1: el color deja de ser el único medio para reconocer que es un link.

Verificado en el navegador después del sync, no solo en el SQL.

### Guarda

`test_el_link_no_depende_del_color_del_tema`, 4 casos parametrizados sobre los links de
DB-03 y DB-04. Validada **reintroduciendo sus dos defectos** por separado: quitar
`color:inherit` y quitar el subrayado. Las dos reprueban cuando deben.

## 3. Corrección del número de producción

Edgar no ratificó mis números de producción y tenía razón. Yo había escrito en el PR
*"verificado contra la API real, local y producción"* juntando ambos en un renglón, y eso
indujo la lectura de que el par era citable en la demo.

```
prod  15DJN0049A  ->  0.129 / D3  (infraestructura)   local: 0.7423 / D1 (pobreza)
prod  09DSN0042A  ->  0.0976 / D2                     local: 0.6692 / D2
prod  /kpis       ->  escuelas_en_riesgo = 0 · completitud 0.1966
```

Reverificado hoy: producción sigue igual. Es **BUG-048**, el Gold viejo en Cloud SQL. El
contraste de drivers se sostiene **en local**; los valores no se sostienen en producción.
Corregido en `Panel_ML_US207.md` §2.1 y §7 —los dos ambientes ahora se reportan por separado
a propósito— y en el DevLog del panel de ML. **No cambia la entrega; cambia lo que podemos
afirmar frente al profesor**, que es como lo dejó asentado DEC-015.

## 4. Gate visual de BUG-049

Capturados los 7 tableros para la revisión de Manuel, en tema claro. El agrupado coincide
con lo reportado: DB-01 9→3 · DB-02 7→3 · DB-03 11→5 · DB-04 13→5 · DB-06 8→3 · DB-07 7→3 ·
DB-09 7→3, y **ninguna fila desborda de 12**.

DB-05 aparece con 42 filas para 36 charts: son las 6 filas `ROW-MD-D1…D6` de encabezado
markdown, una por tab de driver. **No es defecto.**

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Creados:** este DevLog
- **Modificados:** `superset/semantic/db03_cubo_escuela_360.sql`,
  `superset/semantic/db04_cubo_comparador_municipio.sql`,
  `tests/test_drill_down_db03_db04.py`,
  `vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB03_DB04.md`,
  `vault/06_Quality_Testing/Bug_Register.md`, `vault/04_UX_Design/Panel_ML_US207.md`,
  `vault/_DevLog/2026-09-05-marina-garcia-us207-panel-ml-bug049.md`,
  `vault/02_Requirements/Traceability_Matrix.md`, `vault/_DevLog/_index.md`
- **Decisiones autónomas:** medir por elemento en vez de aceptar el score agregado; tratar el
  `<a href>` como elemento propio de FARO —lo escribe FARO, luego FARO responde por él— en
  vez de clasificarlo como heredado, que habría cerrado el caso sin arreglar nada.
- **Corrección propia:** reporté que Edgar se había saltado el `DEC-014`. **Era falso**: leí
  el `Decision_Log` contra `main` cuando su rama todavía no mergeaba. DEC-014 existe desde el
  3-sep. Se rectificó antes de mandarle nada.

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] 4 casos nuevos, la guarda validada reintroduciendo sus dos defectos
- [x] Contraste medido en el navegador sobre valores efectivos, en claro y oscuro
- [x] `vault_lint.py` ✅ · **978 pruebas** en verde (la única roja es BUG-052, ajena)

## Hallazgos para otros

- **Monserrat Miranda:** `superset/semantic/db05_cubo_driver.sql:70` tiene el mismo link sin
  estilo (`Ver detalle del municipio →`). Cae en US-215b / BUG-051. No se toca desde aquí; el
  arreglo es el de §2 y ya tiene prueba en el repo.
- **Manuel Serranía:** **BUG-052 reproducido hoy** — 1 de 3 corridas aisladas falló, y falló
  una prueba **distinta** a la que había fallado en la corrida completa. Es el síntoma que el
  propio bug describe. El patrón de arreglo ya está en el repo.
- **Equipo:** quien reconstruya la imagen de Superset con el `superset_config.py` nuevo de
  Luis va a mover la metadata de SQLite a Postgres, que está vacía: **pierde los 9 tableros
  hasta volver a correr `sync_semantic_layer.py`**. Conviene saberlo antes del 9-sep.
- **DB-09:** la tarjeta *"% escuelas con recomendación"* muestra **"No data"**. No es de
  layout ni de esta historia, pero se vería mal en la demo.

## Próximos pasos

- Que Manuel revise las 7 capturas y cierre el gate visual de BUG-049.
- BUG-050 sigue `open` como deuda declarada, ya con su medición.

---

## Adenda — un hallazgo mío que envejeció (misma fecha)

Edgar señaló al revisar el **PR #247** que el hallazgo 1 de
[[vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB03_DB04]] acusaba a
[[vault/04_UX_Design/Accessibility]] de prometer *"verificados en CI (Lighthouse a11y)"* y
*"≥ 0.9 (bloqueante)"*.

**Ya no lo promete.** Su sección de meta se titula *"no bloqueante — sin CI que lo mida"* y
declara la meta aspiracional hasta que exista el gate. Y lo incómodo: **esa corrección la
hice yo misma el 3-sep**, con una nota en ese documento. Mi plan de pruebas siguió citando la
versión anterior dos días.

La otra mitad del hallazgo se reverificó hoy y sí se sostiene: no hay una sola referencia a
Lighthouse en `.github/` ni en `vault/08_CICD_DevOps/`, así que el §3 se sigue verificando a
mano. El hallazgo se reescribió para decir eso y nada más.

Es la misma lección de esta semana en otra forma: **un hallazgo que no se re-verifica
envejece igual que un bloqueo.** Ya me había pasado con "US-207 está bloqueada por Manuel".

### Lo que no se tocó, y por qué

La fila de **BUG-050** arrastra desde el PR #229 la frase *"requiere primero que alguien
llene la paleta de `UX_Guidelines.md` (C2 · Manuel Serranía)"*, que **DEC-016 dejó sin
sentido** —no se adoptó paleta propia— y que además nombra al dueño equivocado: el registro
es de Edgar Coronel. Verificado que sigue ahí. **La limpia él**, lo pidió explícitamente.
