---
id: DOC-USABILIDAD-DB0304
title: "Usability & Accessibility Test Plan — DB-03 / DB-04"
owner: "Marina García del Buey"
status: draft
traces_up: ["US-215a", "REQ-002"]
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
| 1.9 | En `KPI-17 · Detalle de la predicción`, hacer clic en el link a DB-06 | Abre DB-06 con Ciclo y **CCT** de esa escuela preseleccionados | ✅ estructura (2026-09-04) — verificado contra el tablero desplegado: `NATIVE_FILTER-US203-0`→`id_ciclo`, `-3`→`cct`. 🟡 (2026-09-04) — el link **existe y se renderiza** en `KPI-17 · Detalle de la predicción`; la estructura está verificada por API. Marina no llegó a probar el salto en esta pasada (los charts quedan al final del scroll). Pendiente de una segunda pasada | |
| 1.10 | En `KPI-18 · Recomendación prescriptiva`, hacer clic en el link a DB-09 | Abre DB-09 con Ciclo y CCT preseleccionados — es el camino a la narrativa de la demo (ranking prescriptivo) | ✅ estructura (2026-09-04) — `NATIVE_FILTER-US203-0`→`id_ciclo`, `-3`→`cct`. 🟡 (2026-09-04) — mismo caso que 1.9: el link se ve correcto en `KPI-18 · Recomendación prescriptiva` ("Ver su recomendación →", en azul) y la estructura está verificada por API, pero no se probó el salto | |

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
| 3.1 | Verificar contraste de texto (tarjetas, tablas, filtros) contra su fondo, en claro y oscuro | Contraste AA (≥ 4.5:1) en el texto principal | 🟡 (2026-09-04, Marina · Lighthouse) — **score 93**. Dos hallazgos: *"Background and foreground colors do not have a sufficient contrast ratio"* y *"`<html>` element does not have a `[lang]` attribute"*. Idéntico en claro y oscuro. El del `lang` es del shell de Superset, no de estos tableros (BUG-050) | |
| 3.2 | Recorrer los controles de Superset (filtros nativos, orden de columnas, links de drill-down) solo con teclado | Todos alcanzables y operables sin mouse | ✅ (2026-09-04, Marina) — se alcanzan todos los controles solo con Tab | |
| 3.3 | Verificar foco visible al tabular | El elemento con foco tiene indicador visual claro | ✅ (2026-09-04, Marina) — recuadro azul de foco siempre visible | |
| 3.4 | Activar el link de drill-down con **Enter** (no con clic) | Navega igual que con el mouse | ✅ (2026-09-04, Marina) — **el link se alcanza con Tab y se activa con Enter**. Era el caso con más riesgo de fallar, porque es un `<a href>` inyectado con `allow_render_html` y no un control nativo de Superset | |
| 3.5 | Revisar que `SIN_DATO` se distinga por texto y no solo por color | Un usuario con daltonismo distingue el hueco del cero | ✅ (2026-09-04, Marina) — `SIN_DATO` se distingue por texto, no por color: la celda dice `N/A` en el valor y `SIN_DATO` en la bandera | |

## Convención de resultados

`✅` verificado · `⚠️` verificado con salvedad · `❌` falla, con bug registrado · `⏳` pendiente

## Hallazgos de alcance (huecos del proyecto, no se rellenan por cuenta propia)

1. **No hay CI de accesibilidad.** [[vault/04_UX_Design/Accessibility]] declara
   *"verificados en CI (Lighthouse a11y)"* y *"Lighthouse Accessibility ≥ 0.9
   (bloqueante)"*. No existe ninguna referencia a Lighthouse en `.github/` ni en
   `vault/08_CICD_DevOps/`. Todo el §3 se verifica a mano. Mismo hueco que documentó
   Monserrat en US-215b: es del proyecto, no de esta historia.

2. **No hay paleta de colores documentada.** [[vault/04_UX_Design/UX_Guidelines]] está en
   `status: draft` con las tablas de tokens y componentes **vacías**, pese a llevar
   `source_of_truth: true`. Sin paleta declarada, el §3.1 se verifica contra lo que
   Superset trae por default, no contra un estándar del proyecto.

3. **El §3 no se puede cerrar sin sesión de navegador.** Se documenta como pendiente en
   vez de declararlo verificado: un plan de accesibilidad firmado sin haber tabulado por
   los controles no vale nada.

## Sesión de navegador — 2026-09-04 (Marina García, Chrome)

Primera pasada real con navegador. **De 22 casos, 19 quedan verificados y 3 pendientes.**

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
- **3.1** (contraste): medido con Lighthouse, score **93**. Queda como 🟡 en vez de ✅ porque
  hay dos hallazgos abiertos, registrados en **BUG-050**.

### Hallazgos registrados

| Bug | Qué | Dueño |
|---|---|---|
| **BUG-049** | Tarjetas alineadas al fondo con hueco vertical; tablas anchas exigen scroll horizontal para llegar a las columnas de link | C2 · Marina García |
| **BUG-050** | Lighthouse 93: contraste insuficiente y `<html>` sin `[lang]` | C5 (el `lang`) + C2 (la paleta) |

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
