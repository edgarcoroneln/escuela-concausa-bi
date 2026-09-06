---
project: "FARO"
date: "2026-09-05"
author_human: "Monserrat Xcaret Miranda Olivas"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sesión: el único tablero con tabs nunca recibió la corrección de BUG-049"
touches: ["US-213", "US-214b", "US-202", "REQ-002", "US-215b", "DEC-016", "BUG-051", "BUG-049", "BUG-038", "BUG-037"]
tags: [devlog, superset, bi, layout, accesibilidad, celula-2]
---

# DevLog — 2026-09-05 — El `ancho` que nadie leía en el único tablero con tabs

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/Cube_Specs_DB05_DB08]]

## Contexto

El hallazgo no salió de una prueba ni de un barrido: salió de **comparar los dos tableros propios
entre sí**. DB-08 se leía en horizontal como los de las demás células; DB-05, del mismo autor y bajo
la misma convención, era una tira vertical de un chart por pantalla. Dos tableros de la misma
persona no deberían verse distinto sin una razón, y la razón resultó ser un defecto conocido que se
había dado por cubierto donde no lo estaba.

**No se levanta bug.** Es la misma vía que usó Marina García con el link de contraste el 5-sep:
corregir dentro de la propia historia y dejar la evidencia en el DevLog y en el contrato. US-213 es
la historia que construyó DB-05 y sus 6 tabs; su lectura es parte de lo que esa historia entrega.

## 1. Es BUG-049, un mes después, en la única ruta que no se tocó

`_agrupar_en_filas()` existe desde BUG-049 justo para esto: empaquetar charts consecutivos hasta
llenar los 12 de la grilla, para que el `ancho` declarado en el YAML signifique algo. La corrección
se aplicó a `_layout_grilla()` —el camino plano— y **no** a `_layout_tabs()`, que seguía metiendo
cada chart en su propia fila.

Lo revelador es que el motivo del hueco quedó escrito, y era falso en las dos mitades. El docstring
de la propia guarda de BUG-049 decía:

> *"`_layout_grilla()` la usan 8 tableros […]; DB-05 y DB-08 van por `_layout_tabs()`, que no se
> toca."*

| Afirmación | Realidad |
|---|---|
| DB-08 va por `_layout_tabs()` | **No.** No declara `tabs:` — va por el camino plano, y por eso siempre agrupó bien |
| El defecto queda acotado a dos tableros que no se tocan | **DB-05 es el único tablero con tabs**, así que quedó solo, sin nadie con quien compararse dentro de su propia ruta |

Creer que el defecto vivía en dos tableros "que no se tocan" es lo que lo dejó vivo un mes en uno.
La comparación de la que salió el hallazgo —DB-05 contra DB-08— es justamente la que ese docstring
daba por innecesaria.

**El YAML nunca estuvo mal.** Los 6 tabs ya declaraban `3,3,3,3` y `6,6`, el mismo patrón que
DB-03. El `ancho` estaba bien escrito desde el principio; simplemente no lo leía nadie.

## 2. La medida antes de tocar nada

| | Antes | Después |
|---|---|---|
| Filas de DB-05 | **42** (36 charts + 6 notas) | **24** |
| Filas por tab | 7 | 4 |
| Tabla municipal: ancho necesario / visible | 999 px / **504 px** | 1093 px / **1086 px** |
| Desborde horizontal de la tabla | **495 px** | **7 px** |
| Links `link_db08` visibles sin scroll | ninguno | los 30 |

Esa última fila es la que convierte el defecto en algo más que estético: la columna que se ocultaba
era `link_db08`, **el drill-down a DB-08 que entrega US-214b**. Estaba publicado, medido y con su
guarda de contraste desde ayer, y no se podía ver sin descubrir que había scroll horizontal dentro
de la tabla. Es la misma consecuencia práctica que BUG-049 describe para las columnas de US-214a.

## 3. Por qué la tabla pasó a fila completa, y por qué eso se decidió midiendo

Con el arreglo del builder y los anchos originales, cada tab queda en 3 filas —nota, 4 tarjetas,
línea + tabla— que es el patrón exacto de DB-03. Se abrió así en el navegador y **la tabla seguía
sin caber**: 8 columnas en media fila desbordaban 495 px.

Así que la serie de tiempo y la tabla pasan a `ancho: 12` en los 6 tabs. No es preferencia
estética: es la única configuración en la que el entregable de US-214b se ve. `ancho: 12` ya está
en el vocabulario de los tableros de las otras células (DB-03, DB-04 y DB-09 lo usan), así que
"hacer match" no se rompe.

Cada tab queda en 4 filas: nota · 4 tarjetas · serie de tiempo · tabla.

## 4. Guardas — y las que no bastaban

Siete casos nuevos en `tests/test_layout_filas_bug049.py` para el camino con tabs, y uno en
`tests/test_semantic_db05_db08.py` que lee el **YAML real** y rechaza cualquier fila con un solo
chart angosto.

**Validadas reintroduciendo el defecto**, no sólo en verde: con `_layout_tabs()` devuelto a un
chart por fila, fallan 3 de las 7 sintéticas y la del YAML real. Las otras 4 pasan con el defecto
puesto —y está bien: comprueban invariantes que el defecto no violaba (no perder charts, no
desbordar la grilla, la nota sola arriba). Anotarlo importa: **una guarda que pasa con el defecto
puesto no es guarda de ese defecto**, y conviene saber cuáles son cuáles antes de confiar en el
conteo.

La separación entre ambas es deliberada: las sintéticas prueban el **algoritmo** con un patrón
fijo; la del YAML vigila **DB-05 tal como está declarado hoy**. Si mañana cambian los anchos del
tablero, la guarda del algoritmo no debe volverse roja por eso.

También se corrigió el docstring que originó el hueco, **declarando la corrección en vez de
borrarla** — misma práctica que con los hallazgos envejecidos de la sesión anterior.

## 5. Re-medir accesibilidad, porque cambiar el layout cambia lo que se mide

Un cambio de layout **invalida el barrido de contraste anterior**, y no por sutileza: el barrido del
4-sep midió **34 nodos** en DB-05 porque la tabla municipal estaba debajo del pliegue y Superset la
renderiza perezosamente. Al pasar el tablero a horizontal, esa tabla entra en la pantalla —y con
ella 30 anclas y 60 celdas que **nunca se habían medido**. Dar por bueno el 31/34 anterior sería
repetir el error que este mismo plan documentó hace un día.

Remedido en los **dos temas**, sobre color y fondo efectivos:

| Tema | Cumplen AA | Reprueban |
|---|---|---|
| Claro | **280 / 292** | 12 |
| Oscuro | **281 / 292** | 11 |

**Ninguno de los que reprueban lo escribe FARO.** Son chrome de Superset: `Published`,
`Edit dashboard`, los placeholders `N options` / `Apply filters` en `rgba(…,0.25)`, la etiqueta del
tab activo (**BUG-051**, ya reclasificado por DEC-016) y **seis insignias de conteo de filtro**
—blanco sobre `#2893b3`, 3.55:1— que el barrido angosto no alcanzaba a ver. Por DEC-016 son
limitación conocida y no bloquean.

Lo que sí escribe FARO **pasa, y ahora está comprobado en vez de supuesto**:

| Elemento propio | Claro | Oscuro |
|---|---|---|
| Los 30 `link_db08` | **15.39 : 1** ✅ | **13.40 : 1** ✅ |
| 60 celdas de la tabla municipal | ✅ ninguna bajo AA | ✅ ninguna bajo AA |
| Subrayado del link (WCAG 1.4.1) | `underline` | `underline` |

> **Matiz sobre la medición de ayer.** El fix del link se anotó como 19.26 : 1 en claro asumiendo
> `#000000`. El color heredado real es `rgba(0,0,0,0.88)` sobre `#f5f5f5`, que da **15.39 : 1**. La
> conclusión no cambia —pasa AA holgadamente en ambos temas— pero el número correcto es éste, y se
> corrige aquí porque ahora se midió el ancla real, ya visible, en vez de inferirla.

## 6. Poner las tarjetas en fila no era terminar: había que alinearlas

Agrupar los charts los puso lado a lado, pero **el contenido seguía mal**: los cuatro números
caían a alturas distintas y el primero se salía de su tarjeta. Medido:

| Tarjeta | Alto del título | Posición del número |
|---|---|---|
| KPI-07 · % escuelas por driver dominante | **83 px** (3 líneas) | **103 px** |
| Escuelas por driver dominante | 58 px (2 líneas) | 154 px |
| % escuelas sin recomendación | 58 px + subtítulo | **78 px** |
| Escuelas con recomendación | 58 px (2 líneas) | 154 px |

Dos causas, ninguna de ellas el alto de la fila: **el título de KPI-07 era el único que envolvía a
tres líneas**, y **sólo dos de las cuatro tarjetas tenían subtítulo**, que corre el número hacia
arriba. Resultado: cuatro alturas distintas —103, 154, 78, 154— y 76 px de dispersión.

### El intento equivocado, y por qué se descartó

Lo primero que se probó fue **subir `alto` de 38 a 52**. Falló por partida doble: Superset escala la
cifra al contenedor, así que los números salieron **desproporcionados frente a los demás tableros**
—que usan 38—, y encima no arreglaba la alineación, porque la causa era el título. Se revirtió.

Lo que sí funciona es **reducir lo que tiene que caber**, no agrandar la caja:

- El título de KPI-07 se acorta a `Dx · KPI-07 · % driver dominante`, que envuelve a dos líneas
  como los otros tres. **Los otros tres nombres no se tocan.**
- Las cuatro tarjetas llevan subtítulo, para que compartan estructura.

Resultado medido, y comparado contra DB-03 como referencia de "hacer match":

| | DB-05 (después) | DB-03 (referencia) |
|---|---|---|
| Alto de tarjeta | 304 px | 304 px |
| Tamaño de la cifra | 51 px | 51 px |
| Posición del número | **78 px en las cuatro** | 78 px |
| Dispersión entre tarjetas | **0 px** | — |

> El componente `big_number_total` pide 277 px y recibe 210, así que deja una barra de scroll
> interna. **No es de este cambio: DB-03 tiene exactamente el mismo 277/210** en sus cuatro
> tarjetas. Es cómo se comporta ese chart con `alto: 38` y subtítulo, y forma parte de "verse igual
> que los demás".

## 7. El defecto que el rename destapó — y que rompía cualquier tablero en silencio

Acortar el título **rompió DB-05 al abrirlo**: tarjetas vacías, contenido intercambiado, con el
sync en verde y sin un solo error en la consola. La causa no era el rename sino algo que llevaba
ahí desde siempre, en `_position_con_uuid()`:

```python
por_indice = [u for _, u in sorted(charts_con_uuid)]   # uuid ordenados por id
for child in position.values():                        # nodos en orden de declaración
    if child.get("type") == "CHART":
        child["meta"]["uuid"] = por_indice[i]; i += 1
```

Emparejaba **por posición**: uuid ordenados por id contra nodos en orden de declaración. Sólo
acierta si los ids ascienden en el mismo orden en que los charts aparecen en el YAML.

Y eso deja de cumplirse **en cuanto alguien renombra un chart**: `ensure_chart()` identifica por
`slice_name`, así que un nombre nuevo **crea** un chart nuevo con un id alto. El de KPI-07 va
primero en cada tab, así que pasó a tener el id mayor (110-115) declarado en primer lugar, y cada
nodo recibió el uuid de otro.

El arreglo quita el supuesto de orden: el uuid se busca **por `meta.chartId`**, que el nodo ya
declara. **Cuando los ids sí ascienden, el resultado es idéntico** — hay una guarda que lo exige,
y pasa con las dos implementaciones, que es la prueba de que no cambia nada para los otros nueve
tableros.

Vale decir lo incómodo: **este defecto no lo introduje, pero sí lo activé**, y durante unos minutos
DB-05 estuvo roto. Es la clase de trampa que no se ve hasta que alguien hace lo más natural del
mundo —cambiar el nombre de un chart— a un día del freeze.

## 8. Riesgo del cambio, a un día del freeze

`sync_semantic_layer.py` es herramienta compartida de los 10 tableros y su dueño de convención es
Manuel Serranía (US-202), así que tocarla merece justificarse:

- **El camino plano no se toca.** `_layout_grilla()` queda idéntico; los 9 tableros que lo usan no
  cambian una línea de su `position_json`.
- **El cambio sólo puede afectar a tableros con `tabs:`, y sólo hay uno.** Verificado leyendo los
  10 YAML: DB-05 es el único.
- **Reusa código ya probado en producción.** No introduce una regla de agrupación nueva: llama a la
  misma `_agrupar_en_filas()` que los otros nueve tableros usan desde BUG-049.
- El árbol de BUG-038 se conserva: ninguna de sus guardas asumía un chart por fila, y las 12 siguen
  en verde sin tocarlas.
- **El cambio de `_position_con_uuid()` (§7) sí es de comportamiento compartido**, y por eso lleva
  una guarda que exige que el caso normal —ids ascendentes— dé el mismo resultado que antes.
  Verificado además abriendo DB-03 después del cambio: tarjetas y métricas intactas.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Modificados:** `superset/sync_semantic_layer.py`,
  `superset/dashboards/db05_analisis_driver.yaml`, `tests/test_layout_filas_bug049.py`,
  `tests/test_semantic_db05_db08.py`, `vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB05_DB08.md`, este DevLog,
  `vault/_DevLog/_index.md`, `vault/02_Requirements/Traceability_Matrix.md`
- **Decisiones autónomas:** medir el desborde real de la tabla en el DOM antes de elegir su ancho,
  en vez de decidirlo por parecido con DB-03; separar la guarda del algoritmo de la guarda del
  YAML real para que no envejezcan juntas; y arreglar el emparejamiento de `uuid` por `chartId` en
  vez de renunciar a acortar el título.
- **Dos correcciones propias registradas.** (1) Dar por buena la agrupación sin mirar el contenido
  de las tarjetas: quedaban desalineadas y el primer número se salía, y sólo se vio cuando la
  autora lo señaló sobre una captura. (2) Subir `alto` a 52 como primer intento — agrandó la cifra
  respecto de los demás tableros y no arreglaba la causa, que era el título; revertido (§6).
- **Corrección propia registrada:** la primera versión de esta sesión levantó el hallazgo como
  **BUG-058**. Se descartó: el número estaba libre —verificado contra el working tree y las 15
  ramas remotas, todas topan en BUG-057— pero **la clasificación era la equivocada**. Se corrige
  dentro de US-213, como hizo Marina con el link de contraste.
- **Verificación que no se pudo hacer con el navegador automatizado:** el clic sintético no cambia
  de tab en los componentes React de Superset (ya conocido desde BUG-038). Los 6 tabs se
  verificaron contra el `position_json` publicado por la API, que es lo que el frontend monta.

## Seguridad / calidad

- [x] `pytest tests/ -q` → **993 passed, 8 skipped, 0 failed**
- [x] `ruff check .` → limpio · `vault_lint.py` → Vault limpio
- [x] Guardas nuevas validadas reintroduciendo el defecto (y anotado cuáles no lo cazan)
- [x] Verificado en vivo: DB-05 re-sincronizado, los 6 tabs con 4 filas, ninguna excede la grilla
      de 12, los 36 charts intactos
- [x] **Contraste remedido en los dos temas tras el cambio de layout** (§5): claro 280/292 ·
      oscuro 281/292; lo propio de FARO pasa, lo que reprueba es chrome heredado (DEC-016)
- [x] Tarjetas medidas contra **DB-03** como referencia: mismo alto (304), misma cifra (51 px) y
      los cuatro números a la misma altura (dispersión 0)
- [x] Guardas del `uuid` validadas reintroduciendo la implementación vieja: 2 fallan con ella y el
      caso de ids ascendentes pasa con **ambas** (prueba de que no cambia nada para los otros 9)
- [x] Sin secretos hardcodeados · no se tecleó ninguna credencial en el navegador

## Bloqueantes

Ninguno. **BUG-037 no mordió**: el cambio no altera la lista de columnas de ningún dataset, sólo el
`position_json`, así que no hizo falta el `PUT /api/v1/dataset/<id>/refresh` del runbook.

## Hallazgos para otros

- **Manuel Serranía (C2):** el arreglo toca `sync_semantic_layer.py`, del que eres dueño de
  convención (US-202). Es aditivo, no toca el camino plano y reusa `_agrupar_en_filas()` tal cual;
  aun así conviene tu revisión por ser herramienta de los 10 tableros. Nota aparte: si algún
  tablero futuro declara `tabs:`, ya hereda la agrupación sin trabajo extra.
- **Marina García (C2):** tu corrección de BUG-049 era correcta y su `_agrupar_en_filas()` se reusó
  tal cual — lo que falló fue el **alcance declarado** en el docstring de su guarda, que daba por
  cubiertos dos tableros (DB-05 y DB-08) que en realidad no lo estaban ni lo necesitaban por igual.
  Queda corregido ahí mismo, declarando la corrección.
- **Toda la Célula 2:** una guarda cuyo docstring afirma **qué tableros cubre** debe verificarse
  contra los YAML, no contra la memoria de quien la escribe. Ésta se equivocó en las dos mitades y
  por eso el defecto sobrevivió a su propia corrección.
- **Oscar Quiroz / PM:** la captura de DB-05 del [[vault/04_UX_Design/Manual_Usuario_Dashboards]]
  es del layout viejo (vertical, 36 charts apilados). Conviene recapturarla antes del 9-sep — el
  tablero se lee muy distinto ahora.
- **Luis Téllez (C5):** al correr el bootstrap de Superset a producción, DB-05 toma el layout nuevo
  automáticamente (el `position_json` se reescribe entero en cada sync). No hay paso manual.

## Próximos pasos

1. PR con Manuel Serranía como reviewer, por tocar herramienta compartida.
2. Sugerir a Oscar Quiroz recapturar DB-05 para el manual.
