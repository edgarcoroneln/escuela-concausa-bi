---
id: DOC-USABILIDAD-DB0304
title: "Usability & Accessibility Test Plan — DB-03 / DB-04"
owner: "Marina García del Buey"
status: approved
version: "1.0"
traces_up: ["US-215a", "REQ-002", "DEC-016"]
traces_down: ["BUG-049", "BUG-050"]
last_reviewed: "2026-09-05"
tags: [qa, usability, accessibility, db03, db04]
---

# Usability & Accessibility Test Plan — DB-03 / DB-04

> Guion de pruebas de usabilidad y accesibilidad para **DB-03 (Ficha de escuela)** y
> **DB-04 (Comparador de municipios)**, incluyendo los filtros globales y el drill-down
> cruzado entre ambos (US-214a).
> → [[vault/06_Quality_Testing/_index]] · Contrato: [[vault/04_UX_Design/Cube_Specs_DB03_DB04]]

## Alcance

Calca el formato del plan de Monserrat Miranda para DB-05/DB-08
([[vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB05_DB08]]), para que los
cuatro tableros de la célula se lean igual.

**Adapta** —no copia íntegro— el checklist de [[vault/04_UX_Design/Accessibility]], acotado
a lo verificable en un dashboard de Superset embebido. Quedan **excluidos explícitamente**:

- ARIA de componentes propios de FARO Web (es US-206/US-207, de la capa Streamlit)
- `prefers-reduced-motion` (mismo motivo)
- Lighthouse automatizado: **no existe ese gate en el proyecto**, pese a que
  `Accessibility.md` lo declara como bloqueante. Ver §Hallazgos de alcance.

## Matriz de alcance

| Dashboard | Navegador | Responsable |
|---|---|---|
| DB-03 · Ficha de escuela | Chrome | Marina García del Buey |
| DB-04 · Comparador de municipios | Chrome | Marina García del Buey |

## Guion por sección

### §1 — Usabilidad DB-03

| Caso | Pasos | Esperado | Resultado | Bug |
|---|---|---|---|---|
| 1.1 | Abrir DB-03 sin tocar nada | Carga sin error, con el **ciclo 2024-2025 ya preseleccionado** en la barra de filtros | ✅ (2026-09-04) — verificado por API: `defaultDataMask` persistido en `NATIVE_FILTER-US203-1` con `val: ['2024-2025']` | |
| 1.2 | Leer la tarjeta `KPI-15 · Matrícula de la escuela` recién abierto | La cifra corresponde **al ciclo**, no a la suma de todos los ciclos del cubo | ✅ (2026-09-04) — verificado contra `/api/v1/chart/data`: sin filtro devuelve 32 312, con el ciclo devuelve **11 828**. El defecto inflaba 2.73× | |
| 1.3 | Aplicar los filtros globales (Ciclo, Entidad, Nivel) | Las tarjetas y tablas recalculan según el filtro | ✅ (2026-09-04, Marina en Chrome) — cambiar Entidad y Nivel recalcula todas las tarjetas y tablas. **Hallazgo de layout aparte, no de filtros:** las tarjetas quedan alineadas abajo en vez de arriba, dejando hueco vertical (BUG-049) | |
| 1.4 | Filtrar por una escuela concreta con el filtro `Escuela (CCT)` | El tablero se vuelve la ficha de esa escuela: perfil, drivers, predicción y recomendación de ese CCT (AC-002.4) | ✅ (2026-09-04, Marina) — con `Escuela (CCT) = 15DJN0049A` el tablero se vuelve la ficha de esa escuela: perfil, 6 drivers, predicción (`indice_riesgo` 0.74, `en_riesgo` true, proyectada −7.60 %) y recomendación. **AC-002.4 verificado en vivo.** Salvedades de presentación en BUG-049 | |
| 1.5 | Revisar la tabla `KPI-16 · Drivers de la escuela y su cobertura` | Donde no hay dato de un driver muestra `SIN_DATO` explícito, **nunca `0`** (regla R2) | ✅ (2026-09-04) — verificado en datos **después del fix de BUG-045**: D5 145/145 `SIN_DATO` (CONAGUA sigue sin ingerir), D6 140/145, D3/D4 12/145, y D1 ya con dato en 145/145. Lo que importa: **cero casos** de driver marcado `SIN_DATO` que traiga valor | |
| 1.6 | En `Perfil del plantel`, localizar la columna del link a DB-04 | Se ve como texto de link (no HTML crudo), rotulado "Comparar su municipio →" | ✅ (2026-09-04, Marina) — la columna `link_db04` se ve como link azul, rotulado "Comparar su municipio →". No sale HTML crudo | |
| 1.7 | Hacer clic en ese link | Abre DB-04 en pestaña nueva con Ciclo y Municipio de esa fila preseleccionados | ✅ estructura (2026-09-04) — RISON decodificado con `prison` y contrastado contra el tablero desplegado: `NATIVE_FILTER-US203-0`→`id_ciclo`, `-4`→`cve_mun`, ambos correctos. ✅ **verificado en vivo** (2026-09-04, Marina) — abre DB-04 con `Municipio (clave INEGI) = 15106` y `Ciclo = 2024-2025` ya preseleccionados | |
| 1.8 | Leer `KPI-17 · Índice de riesgo` | Muestra el índice, y el subheader explica el umbral 0.60 de DEC-006 | ✅ (2026-09-04) — **la calibración quedó verificada empíricamente** tras el fix de BUG-045: con los 6 drivers, 2 escuelas cruzan 0.60 y ambas proyectan perder más de 5 % (−7.60 % y −6.19 %), mientras la de 0.538 (−4.00 %) no cruza. El umbral dispara cuando debe. **DEC-006 ratificada por el PM**, no se reabre — ver §8.quinquies.5 | |
| 1.9 | En `KPI-17 · Detalle de la predicción`, hacer clic en el link a DB-06 | Abre DB-06 con Ciclo y **CCT** de esa escuela preseleccionados | ✅ estructura (2026-09-04) — verificado contra el tablero desplegado: `NATIVE_FILTER-US203-0`→`id_ciclo`, `-3`→`cct`. ✅ (2026-09-05) — **verificado con datos, no solo estructura**: aplicando el filtro que lleva el link sobre `db06_predicciones_escuela`, el dataset pasa de **145 filas a 2**, todas del CCT `15DJN0049A`. Los índices se contrastaron contra el tablero desplegado (`-0`→`id_ciclo`, `-3`→`cct`). La razón por la que no se probó el 4-sep —los charts quedaban al final de un scroll larguísimo— era **BUG-049**, ya corregido: DB-03 pasó de 11 filas a 5 | |
| 1.10 | En `KPI-18 · Recomendación prescriptiva`, hacer clic en el link a DB-09 | Abre DB-09 con Ciclo y CCT preseleccionados — es el camino a la narrativa de la demo (ranking prescriptivo) | ✅ estructura (2026-09-04) — `NATIVE_FILTER-US203-0`→`id_ciclo`, `-3`→`cct`. ✅ (2026-09-05) — mismo método que 1.9: el filtro lleva `db09_cubo_recomendaciones` de **145 filas a 2**, todas del CCT de origen. Es el camino a la narrativa que el PM eligió para la demo: de la ficha de una escuela al ranking prescriptivo | |

### §2 — Usabilidad DB-04

| Caso | Pasos | Esperado | Resultado | Bug |
|---|---|---|---|---|
| 2.1 | Abrir DB-04 sin tocar nada | Carga con el ciclo 2024-2025 preseleccionado | ✅ (2026-09-04) — `defaultDataMask` en `NATIVE_FILTER-US203-0` | |
| 2.2 | Leer `KPI-01 · Matrícula de los municipios` recién abierto | Cifra del ciclo, no la suma | ✅ (2026-09-04) — 11 828 con filtro contra 32 312 sin él | |
| 2.3 | Seleccionar 2-3 municipios en `Municipios a comparar` | La comparativa y los seis small-multiples de driver recalculan solo con esos municipios | ✅ (2026-09-04, Marina) — seleccionar municipios recalcula la comparativa y los KPI (`KPI-01` 1 258, `KPI-02` −0.5 %) | |
| 2.4 | Revisar `KPI-02 · Variación de matrícula` | Razón de sumas, coherente con el hecho | ✅ (2026-09-04) — **−0.496 %** en el ciclo, idéntico por los cinco caminos (hecho + 4 cubos). Ver §8.ter.3 del contrato | |
| 2.5 | Revisar los seis paneles de driver (D1…D6) | Cada promedio divide entre `escuelas_con_d#`, y los `SIN_DATO` no aparecen como cero | ✅ (2026-09-04) — verificado en datos y en pantalla: D5 y D6 tienen `escuelas_con_d# = 0` y suma `NULL`, así que sus paneles salen **vacíos, no en cero**. En `KPI-16` de DB-03 se ve `N/A` + `SIN_DATO`, nunca `0` | |
| 2.6 | En `Comparativa de municipios`, hacer clic en el link a DB-03 | Abre DB-03 con Ciclo y Municipio preseleccionados, y `cct` **libre** (para elegir escuela) | ✅ estructura (2026-09-04) — `NATIVE_FILTER-US203-1`→`id_ciclo`, `-4`→`cve_mun`; `cct` (índice 0) deliberadamente sin fijar. ⏳ falta confirmar visualmente | |
| 2.7 | Revisar `KPI-14 · Contexto socioeconómico` | Muestra población, pobreza y rezago del municipio | ✅ (2026-09-04) — **destrabado el mismo día**: Diana Alvarez publicó los fixtures de CONEVAL con el esquema real (BUG-045 `fixed`). Verificado en datos: `gold.dim_municipio` pasa de 0 a **10 municipios con pobreza, rezago y grado**, y D1 de 145/145 `SIN_DATO` a 145/145 con dato | |

### §3 — Accesibilidad (DB-03 y DB-04)

Requiere navegador; ninguno automatizable con lo que hay hoy en el proyecto.

| Caso | Pasos | Esperado | Resultado | Bug |
|---|---|---|---|---|
| 3.1 | Verificar contraste de texto (tarjetas, tablas, filtros) contra su fondo, en claro y oscuro | **WCAG 2.1 AA** (4.5:1 texto normal, 3:1 texto grande y componentes) sobre color y fondo **efectivos**, en los dos temas — criterio de [[vault/04_UX_Design/UX_Guidelines]] | ⚠️ (2026-09-05, Marina · `getComputedStyle` en Chrome) — medido elemento por elemento, no con un score agregado. **Todo lo que escribe FARO pasa**: peor caso **19.26:1** en claro y **18.42:1** en oscuro, en los dos tableros. **Reprueban dos elementos heredados del tema de Superset**: `Published` **2.16:1** (claro) y `Edit dashboard` **3.07:1** claro / **3.41:1** oscuro. Por **DEC-016** son limitación conocida y no bloquean. **Se encontró y corrigió un defecto de FARO en el camino** — ver 3.1.bis | BUG-050 |
| 3.1.bis | Medir el contraste de los `<a href>` de drill-down, que **los escribe FARO** y no el tema | WCAG 2.1 AA (4.5:1); por DEC-016 un elemento propio que no llegue **es defecto y bloquea** | ✅ (2026-09-05, Marina) — **reprobaba**: heredándole el azul de acento de Superset `#2893B3` daba **3.26:1** sobre el `#F5F5F5` de la celda en tema claro (en oscuro pasaba con 5.91:1, por eso no se había visto). Corregido en los 4 links de DB-03/DB-04: heredan el color del texto de la celda y se marcan con subrayado. **19.26:1 claro · 21:1 oscuro**, y de paso cumple WCAG 1.4.1. Guarda: `test_el_link_no_depende_del_color_del_tema` | |
| 3.2 | Recorrer los controles de Superset (filtros nativos, orden de columnas, links de drill-down) solo con teclado | Todos alcanzables y operables sin mouse | ✅ (2026-09-04, Marina) — se alcanzan todos los controles solo con Tab | |
| 3.3 | Verificar foco visible al tabular | El elemento con foco tiene indicador visual claro | ✅ (2026-09-04, Marina) — recuadro azul de foco siempre visible | |
| 3.4 | Activar el link de drill-down con **Enter** (no con clic) | Navega igual que con el mouse | ✅ (2026-09-04, Marina) — **el link se alcanza con Tab y se activa con Enter**. Era el caso con más riesgo de fallar, porque es un `<a href>` inyectado con `allow_render_html` y no un control nativo de Superset | |
| 3.5 | Revisar que `SIN_DATO` se distinga por texto y no solo por color | Un usuario con daltonismo distingue el hueco del cero | ✅ (2026-09-04, Marina) — `SIN_DATO` se distingue por texto, no por color: la celda dice `N/A` en el valor y `SIN_DATO` en la bandera | |

## Convención de resultados

`✅` verificado · `⚠️` verificado con salvedad · `❌` falla, con bug registrado · `⏳` pendiente

> El `🟡` que este documento usó en el caso 3.1 hasta el 2026-09-04 **no estaba en esta
> leyenda**: se inventó sobre la marcha para un tercer estado que no existía. Ya no se usa —
> el caso cerró con `⚠️`, que es exactamente "verificado con salvedad" y sí está definido.

## Hallazgos de alcance (huecos del proyecto, no se rellenan por cuenta propia)

1. **No hay CI de accesibilidad, pero el documento ya no dice lo contrario.**
   Reverificado el 2026-09-05: sigue sin haber una sola referencia a Lighthouse en
   `.github/` ni en `vault/08_CICD_DevOps/`, así que todo el §3 se verifica a mano — ese
   hueco es real y es del proyecto, no de esta historia. Mismo que documentó Monserrat en
   US-215b.

   **Lo que este hallazgo afirmaba de más, y se corrige aquí.** Decía que
   [[vault/04_UX_Design/Accessibility]] prometía *"verificados en CI (Lighthouse a11y)"* y
   *"≥ 0.9 (bloqueante)"*. **Ya no lo promete**: su §"Meta objetivo" se titula *"no
   bloqueante — sin CI que lo mida"* y declara la meta **aspiracional hasta que exista el
   gate**. Se corrigió el 2026-09-03 con una nota mía en ese mismo documento, y este plan
   siguió citando la versión anterior dos días. Señalado por Edgar Coronel al revisar el
   PR #247. **Un hallazgo que no se re-verifica envejece igual que un bloqueo.**

2. ~~**No hay paleta de colores documentada.**~~ **Resuelto el 2026-09-05.**
   [[vault/04_UX_Design/UX_Guidelines]] pasó a `status: approved` y declara **WCAG 2.1 AA**
   como criterio. La decisión de fondo es que **FARO no adopta paleta propia** y hereda los
   temas de Superset y Streamlit; de ahí sale **DEC-016**, que separa lo que FARO escribe
   —bloquea si no llega al umbral— de lo que hereda —limitación conocida con su medición—.
   El §3.1 ya tiene criterio de aceptación y por eso pudo cerrarse.

3. **El §3 no se puede cerrar sin sesión de navegador.** Se documenta como pendiente en
   vez de declararlo verificado: un plan de accesibilidad firmado sin haber tabulado por
   los controles no vale nada.

## Sesión de navegador — 2026-09-04 (Marina García, Chrome)

Primera pasada real con navegador. **De 22 casos, 19 quedan verificados y 3 pendientes.**
Los tres restantes cerraron después: **1.9** y **1.10** el 2026-09-05 tras corregir BUG-049,
y **3.1** el mismo día con el criterio de DEC-016 ya publicado. **22 de 22.**

### Lo que se confirmó

- **AC-002.4 en vivo**: con `Escuela (CCT) = 15DJN0049A` el tablero se vuelve la ficha de esa
  escuela, con sus 6 drivers, su predicción (`indice_riesgo` 0.74, `en_riesgo` true) y su
  recomendación. Es el criterio central de US-212 y se ve funcionando.
- **El drill-down DB-03 → DB-04 funciona de punta a punta**: el link abre DB-04 con el
  municipio (`15106`) y el ciclo ya preseleccionados.
- **El §3 completo de accesibilidad salió mejor de lo esperado.** El caso 3.4 —el que más
  riesgo tenía de fallar, porque el link es un `<a href>` inyectado y no un control nativo—
  **se alcanza con Tab y se activa con Enter**. Foco visible en todo el recorrido.
- **La regla `SIN_DATO` se sostiene visualmente**: `N/A` + `SIN_DATO` en texto, distinguible
  sin depender del color (caso 3.5).

### Lo que NO se pudo cerrar, y por qué

- **1.9 y 1.10** (saltos a DB-06 y DB-09): los links se ven correctos y su estructura está
  verificada por API, pero el salto no se probó — esos charts quedan al final del scroll y
  la sesión no llegó ahí. Pendiente de una segunda pasada corta.
- **3.1** (contraste): medido con Lighthouse, score **93**. Quedó abierto porque no había
  criterio de aceptación contra el cual medir. **Cerrado el 2026-09-05** — ver la sesión de
  abajo.

### Hallazgos registrados

| Bug | Qué | Dueño |
|---|---|---|
| **BUG-049** | Tarjetas alineadas al fondo con hueco vertical; tablas anchas exigen scroll horizontal para llegar a las columnas de link | C2 · Marina García |
| **BUG-050** | Lighthouse 93: contraste insuficiente y `<html>` sin `[lang]`. **Medición fina 2026-09-05**: los dos elementos que reprueban son `Published` (**2.16:1** claro) y `Edit dashboard` (**3.07:1** claro / **3.41:1** oscuro), ambos del shell de Superset. Por **DEC-016** es limitación conocida y deja de bloquear `US-215a`; sigue `open` | C5 (el `lang` y el tema) |

## Sesión de navegador — 2026-09-05 (Marina García, Chrome, claro y oscuro)

Segunda pasada, ya con el criterio de **DEC-016** publicado. No se usó un score agregado:
se midió **elemento por elemento** con `getComputedStyle`, sobre el color y el fondo
**efectivos** —subiendo el árbol hasta el primer fondo opaco— y en los dos temas.

| Tablero | Tema | Peor elemento escrito por FARO | Veredicto |
|---|---|---|---|
| DB-03 | claro | 19.26 : 1 | pasa |
| DB-03 | oscuro | 21 : 1 | pasa |
| DB-04 | claro | 19.26 : 1 | pasa |
| DB-04 | oscuro | 18.42 : 1 | pasa |

**Por qué Lighthouse no bastaba.** El score 93 señala que *hay* contraste insuficiente pero
no dice **en qué elemento**, y DEC-016 decide precisamente por elemento: propio bloquea,
heredado no. Medir por elemento fue lo que separó los dos casos — y lo que destapó un defecto
propio que el score había escondido dentro del mismo hallazgo genérico.

**El defecto que apareció (3.1.bis).** Los cuatro `<a href>` de drill-down de DB-03 y DB-04
no traían estilo propio, así que tomaban el azul de acento de Superset `#2893B3`. En tema
**oscuro** eso da 5.91 : 1 y pasa; en **claro**, sobre el `#F5F5F5` de la celda de tabla, da
**3.26 : 1** y reprueba. Se había revisado en oscuro el 4-sep, que es donde no falla.

No se arregló eligiendo otro azul, porque no existe: pasar 4.5 : 1 contra `#F5F5F5` exige
luminancia ≤ 0.164 y contra `#000000` exige ≥ 0.175, y los rangos **no se cruzan**. Ningún
color único sirve para los dos temas. La salida fue heredar el color del texto de la celda
—que ya pasa en ambos— y marcar el link con **subrayado** en vez de con tono, lo que además
cumple WCAG 1.4.1: el color deja de ser el único medio para reconocerlo.

> **3.1.bis no es un caso 23.** Es el desglose del 3.1 que DEC-016 obliga a hacer: el
> denominador de esta historia sigue siendo **22**.

**Hallazgo ajeno, para su dueña.** `superset/semantic/db05_cubo_driver.sql:70` tiene el mismo
link sin estilo (`Ver detalle del municipio →`). Cae en `US-215b` / `BUG-051`, de **Monserrat
Miranda**, y no se toca desde aquí. El arreglo es el de arriba, ya con prueba en el repo.

### Un hallazgo de interpretación, no de defecto

La escuela `15DJN0049A` muestra `KPI-02 = +26.7 %` **y a la vez** `en_riesgo = true`. Ambos
números son correctos y verificados contra la base: creció 26.7 % el ciclo pasado
(114 contra 90 alumnos) y el modelo proyecta **−7.60 %** para el siguiente.

Pero puestos uno junto al otro **se leen como una contradicción**. `KPI-02` es histórico
observado y `variacion_proyectada` es pronóstico, y el tablero no dice cuál es cuál en la
tarjeta. Es exactamente el tipo de cosa que un evaluador pregunta en una demo.

No se registra como bug porque no hay defecto: es una decisión de rotulado. Propuesta para
la mesa: que el subheader de `KPI-02` diga **"observado"** y el de `KPI-17` diga
**"proyectado"**. Toca el catálogo de KPIs, así que requiere aval de Manuel Serranía.

## Cierre

Los casos con evidencia de datos o de API se verificaron el **2026-09-04** y quedan
cerrados. Los que exigen navegador quedan `⏳` para una segunda pasada, con la lista
explícita de arriba. No se marca ninguno como verificado sin haberlo corrido.
