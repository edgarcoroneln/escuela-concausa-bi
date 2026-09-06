---
id: DOC-USABILIDAD-DB0508
title: "Usability & Accessibility Test Plan — DB-05 / DB-08"
owner: "Monserrat Xcaret Miranda Olivas"
status: approved
traces_up: ["US-215b", "REQ-002", "DEC-016"]
traces_down: ["BUG-038", "BUG-051", "BUG-056"]
last_reviewed: "2026-09-05"
tags: [qa, usability, accessibility, db05, db08]
---

# Usability & Accessibility Test Plan — DB-05 / DB-08

> Guion de pruebas de usabilidad y accesibilidad para DB-05 (Análisis por driver, 6 tabs) y DB-08
> (Explorador del cubo), incluyendo el link cruzado entre ambos (US-214b).
> → [[vault/06_Quality_Testing/_index]]

## Alcance

**Cubre:**
- DB-05 · Análisis por driver — los 6 tabs (D1-D6) y su tabla "Municipios · driver dominante y
  cobertura", incluyendo la columna `link_db08` nueva (US-214b).
- DB-08 · Explorador del cubo — filtros globales, tabla dinámica libre y tabla de detalle.
- El viaje completo DB-05 → DB-08 vía el link (RISON `native_filters`, US-214b).

**No cubre — corresponde a otra historia:**
- El shell de FARO Web (React/Streamlit, US-206/US-207, dueño Manuel Serranía): ARIA de sus
  componentes propios, `prefers-reduced-motion`, layout responsivo del shell.
- El código fuente interno de Superset (controles nativos, dropdowns de filtro): se prueba su
  comportamiento visible, no se audita su implementación — es un tercero, no algo que el equipo
  pueda corregir.

El checklist de accesibilidad de §3 se **adapta** de [[vault/04_UX_Design/Accessibility]], no se copia
íntegro: de sus 6 ítems, se excluyen "Roles/labels ARIA en controles" (fuera de alcance — controles
de Superset, no propios) y "Respeta `prefers-reduced-motion`" (shell de FARO Web).

## Matriz de alcance

| Dashboard | Navegador | Responsable |
|---|---|---|
| DB-05 · Análisis por driver (6 tabs) | Chrome | Monserrat Xcaret Miranda Olivas |
| DB-08 · Explorador del cubo | Chrome | Monserrat Xcaret Miranda Olivas |

## Guion por sección

### §1 — Usabilidad DB-05

| Caso | Pasos | Esperado | Resultado (✅/⚠️/❌/⏳) | Bug |
|---|---|---|---|---|
| 1.1 | Abrir DB-05, confirmar que carga en el tab D1 | El dashboard abre sin error, tab D1 activo por default | ✅ (2026-09-04) — re-probado tras el fix de BUG-038: abre en D1 con `aria-selected: true` y **los 6 tabs visibles** en la barra. La salvedad de 2026-08-30 ("hoy es el único tab visible") queda resuelta | |
| 1.2 | Cambiar entre los 6 tabs (D1 → D6) | Cada tab muestra sus propios KPI tiles y tabla, filtrados por su `id_driver` | ✅ (2026-09-04) — **antes ❌ por BUG-038**. Verificado en navegador real contra Superset 6.1.0: los 6 tabs se dibujan y al cambiar a D4 su panel queda `aria-hidden: false` con **6 charts** y su propia nota ("CEMABE (DS-03) · medido a nivel escuela"). Los valores son propios de cada tab, no heredados: D1 → 52.7 % / 18 escuelas; D4 → 30.9 % / 17. Antes del fix D2-D6 eran inalcanzables | BUG-038 ✅ |
| 1.3 | Aplicar los filtros globales (Ciclo, Entidad, Nivel) | Los tiles y la tabla recalculan según el filtro aplicado | ✅ (2026-09-04) — **antes ❌ por BUG-038**. Con `nombre_entidad = 'Jalisco'` el panel muestra el valor y los charts **sí recalculan**: KPI-07 pasa de 52.7 % a 0.0 % y "Escuelas por driver dominante" de 18 a 0. **Contrastado contra la base**, no sólo contra la pantalla: `gold.cubo_driver` da para Jalisco/D1/2024-2025 `escuelas_driver = 0` sobre `total_escuelas = 7`, y el cuarto tile muestra exactamente 7. Sin filtro, los 18 del tablero son la suma real (0+0+10+8) de las 4 entidades | BUG-038 ✅ |
| 1.4 | En la tabla "Municipios · driver dominante y cobertura" de cualquier tab, localizar la columna del link | La columna se ve como texto de link (no HTML crudo), rotulada "Ver detalle del municipio →", **y legible en los dos temas** (DEC-016) | ✅ (2026-08-30) el render · **⚠️→✅ el contraste (2026-09-05)**. Reportado por Marina García al cerrar US-215a: el `<a>` no traía estilo propio y heredaba el acento de Superset. **Medido en DB-05, no inferido** — antes: `#2893b3` sobre `#f5f5f5` = **3.26:1 REPRUEBA** en claro, 5.91:1 pasa en oscuro, sin subrayado. Corregido con `color:inherit` + `text-decoration:underline` → después: **19.26:1 claro / 21:1 oscuro**, subrayado presente. Por DEC-016 **este sí era defecto**: el `<a>` lo escribe FARO. Guarda: `test_el_link_db08_no_depende_del_color_del_tema`, validada reintroduciendo cada defecto por separado. **Por qué no se vio el 4-sep**: se midió el tema oscuro —donde pasa— y la tabla del link queda **debajo del pliegue**, fuera del viewport recorrido; los 30 links sólo aparecen en el DOM tras hacer scroll | |
| 1.5 | Hacer clic en el link de una fila | Abre DB-08 en pestaña nueva, con Municipio y Driver de esa fila pre-seleccionados | ✅ (2026-08-30) — confirmado con 2 filas distintas (municipio 09003→19039), el chart "Valor promedio del driver" de DB-08 cambió de valor entre una y otra (0.10 → 0.90), evidencia de que el filtro sí llegó aplicado | |
| 1.6 | Revisar legibilidad de números grandes en los KPI tiles | Formato consistente (separador de miles, decimales según `formato` de la métrica) | ✅ (2026-08-30) — contraste correcto en dark y light mode. Hallazgo aparte (no de formato numérico): el mensaje "sin datos" es inconsistente entre tiles y está en inglés — documentado como punto 5 de UX pendiente en `db08_explorador_cubo.yaml`, no se resuelve hoy (limitación de Superset) | |

### §2 — Usabilidad DB-08

| Caso | Pasos | Esperado | Resultado (✅/⚠️/❌/⏳) | Bug |
|---|---|---|---|---|
| 2.1 | Llegar a DB-08 directo (sin pasar por el link) | **Ciclo llega preseleccionado en `2024-2025`** (comportamiento correcto desde BUG-047); Entidad, Nivel, Municipio y Driver llegan vacíos | ✅ (2026-09-04) — verificado por API sobre `native_filter_configuration`: `-0` Ciclo → `defaultDataMask` con `['2024-2025']`; `-1` Entidad, `-2` Nivel, `-3` Municipio y `-4` Driver sin `defaultDataMask`. **Esperado reescrito hoy**: decía "los 5 aparecen vacíos/default", redacción anterior a BUG-047 que habría marcado falla falsa | |
| 2.2 | Llegar a DB-08 vía el link de DB-05 | Municipio y Driver llegan preseleccionados con el valor exacto de la fila de origen | ✅ (2026-08-30) — ver 1.5 · **Regresión revisada (2026-09-04)**: los IDs de filtro se generan **por posición**, y BUG-047 añadió `valor_por_defecto` a `id_ciclo`. Contrastado el RISON de `link_db08` contra el tablero desplegado: sigue apuntando a `-3` (`cve_mun`) y `-4` (`id_driver`), que son los índices reales. Sin regresión | |
| 2.3 | Cambiar filas/columnas de la tabla dinámica libre | El pivote recalcula sin error, respeta `rowTotals`/`colTotals` en `false` | ✅ (2026-09-04) — verificado por API sobre el chart 95: `viz_type: pivot_table_v2`, `groupbyRows` `[nombre_entidad, nombre_municipio, nivel]`, `groupbyColumns` `[id_driver, nombre_driver]`, `rowTotals: False`, `colTotals: False`; `/api/v1/chart/data` responde **180 filas, `status: ok`** | |
| 2.4 | Revisar la tabla de detalle sin agregar | Muestra `SIN_DATO` explícito donde no hay dato de un driver, nunca `0` silencioso (R2) | ✅ (2026-09-04) — verificado **en datos** sobre `gold.cubo_pivot`: **309 filas** marcadas `SIN_DATO` (D3 12, D4 12, D5 145, D6 140) y **ninguna** trae valor. Prueba discriminante: conviven con **60 ceros legítimos** en filas `OK` (D1 15, D2 15, D3 2, D4 43, D6 2) — el cero real existe y no se confunde con el hueco | |

### §3 — Accesibilidad (DB-05 y DB-08)

Adaptado de [[vault/04_UX_Design/Accessibility]] §Checklist, acotado a lo verificable en un dashboard de
Superset embebido (ver exclusiones en §Alcance).

| Caso | Pasos | Esperado | Resultado (✅/⚠️/❌/⏳) | Bug |
|---|---|---|---|---|
| 3.1 | Verificar contraste de texto (tiles, tablas, filtros) contra su fondo | Contraste AA (≥ 4.5:1 texto normal) sobre color y fondo **efectivos**, en los **dos temas** (DEC-016) | ⚠️ **medido por separado en cada tablero (2026-09-05)**. **DB-05** — claro 31/34 · oscuro 30/32. **DB-08** — claro **1085/1209**, oscuro **1208/1209**. **Todo lo que reprueba es color heredado de Superset, ninguno lo estiliza FARO** → por DEC-016 son limitación conocida y no bloquean: `Published` (2.16 claro), `Edit dashboard` (3.07 claro / 3.41 oscuro) y, en DB-08, **122 celdas `pvtVal` del pivote** con el acento `#2893b3` sobre blanco a **3.55:1**. Verificado que el YAML de DB-08 **no declara ningún color ni formato condicional** —sólo estructura— así que el color lo pone Superset en línea. La etiqueta del tab activo de DB-05 sigue en 3.55/4.07 → **BUG-051**, reclasificado por DEC-016 como limitación que **ya no bloquea** US-215b. **En oscuro el pivote sí pasa**: el problema es exclusivo del tema claro | BUG-051 · BUG-056 |
| 3.2 | Navegar los controles propios de Superset (filtros nativos, tabs, orden de columnas de tabla) solo con teclado (Tab/Enter/flechas) | Todos los controles son alcanzables y operables sin mouse | ✅ **en los dos tableros (2026-09-05)**. **DB-05** (4-sep): 48 enfocables, 6/6 tabs y 3/3 filtros en el orden de tabulación; activación `Tab`+`Enter` **verificada a mano por Monserrat Xcaret Miranda Olivas**. **DB-08** (5-sep): **1056 enfocables y 5/5 filtros globales alcanzables** (Ciclo, Entidad, Nivel, Municipio, Driver) — el tablero **no tiene tabs**, así que el esperado de DB-05 no aplica aquí. **Activación verificada a mano por Monserrat Xcaret Miranda Olivas** (2026-09-05): `Tab` hasta el filtro *Ciclo escolar* + `Enter` **sí abre el desplegable**. La comprobación humana era necesaria por el artefacto ya documentado — el navegador automatizado no entrega `Enter` ni clic a los componentes React de Superset aunque sí mueva el foco, así que habría reportado un **falso negativo**, igual que en DB-05 el 4-sep. Salvedad heredada: las flechas ← → no navegan entre tabs (patrón ARIA incompleto de Superset) | |
| 3.3 | Verificar foco visible al tabular por los controles | El elemento con foco tiene un indicador visual claro | ✅ **en los dos tableros**. DB-05 (4-sep) y **DB-08 (5-sep)**: tabulando con `Tab` real el elemento activo cumple `:focus-visible` y pinta el mismo anillo `box-shadow: rgb(37,128,155) 0 0 0 2px`. `outline-style` es `none`: el indicador es la sombra, no el outline — quien audite mirando sólo `outline` concluiría falsamente que no hay foco visible. Un `.focus()` programático **no** dispara `:focus-visible` y no sirve para este caso |

## Convención de resultados

✅ pasa · ⚠️ pasa con observación · ❌ falla (→ crear `BUG-###`) · ⏳ pendiente

## Hallazgos de alcance (huecos del proyecto, no se rellenan por cuenta propia)

> **Los dos hallazgos de abajo se re-verificaron el 2026-09-05 y los dos habían envejecido.** Se
> corrigen declarando la corrección en vez de borrarla. La lección va con el mismo espíritu con el
> que Marina García corrigió el suyo en el PR #249: **un hallazgo que no se re-verifica envejece
> igual que un bloqueo**, y este plan citaba dos documentos que ya habían cambiado.

- **Sin CI de accesibilidad — el hueco sigue, la cita estaba vieja.** Este plan afirmaba que
  [[vault/04_UX_Design/Accessibility]] declaraba *"Lighthouse Accessibility ≥ 0.9 (bloqueante)"*.
  **Ya no lo declara**: desde el 3-sep su sección se titula *"Meta objetivo (no bloqueante — sin CI
  que lo mida)"* y marca la meta como aspiracional. Lo que **sí** se sostiene, reverificado hoy: no
  hay una sola referencia a Lighthouse en `.github/` ni en `vault/08_CICD_DevOps/`, así que el §3 se
  sigue verificando a mano y este plan no puede heredar un gate que no existe.
- **Sin paleta propia — dejó de ser un hueco y pasó a ser una decisión.** Este plan lo anotaba como
  insumo faltante que impedía un caso de "colorblind-safe". **DEC-016** (5-sep) lo resolvió en
  sentido contrario: FARO **no declara paleta propia** de forma deliberada —los 10 tableros heredan
  el tema de Superset 6.1— porque adoptar identidad visual a tres días de la demo significaría
  re-teñir 103 charts sin ninguna prueba detrás. Con esa regla, el contraste heredado se registra
  como limitación conocida (BUG-051, BUG-056) y el caso de daltonismo queda fuera de alcance por
  decisión, no por falta de insumo.

## Cierre

**Tercera pasada — 2026-09-05.** Cierra dos huecos de la pasada anterior: el §3 se había medido
**sólo en DB-05** pese a declarar los dos tableros, y el `<a>` de drill-down tenía un defecto de
contraste que el barrido del 4-sep no alcanzó.

| | Casos |
|---|---|
| **Ejecutados** | **13 de 13**, ahora con §3 medido en **ambos** tableros |
| ✅ pasan | **12** — 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4, 3.2 y 3.3, **los dos tableros** |
| ⚠️ pasan con observación | 1 — 3.1 (contraste heredado: BUG-051 · BUG-056) |
| ❌ fallan | **0** |

### Lo que cambió respecto a la pasada del 4-sep

- **El `<a>` de `link_db08` era un defecto real y está corregido.** Lo reportó Marina García tras
  encontrar el mismo patrón en DB-03/DB-04. Medido en DB-05 —no heredado de su informe—:
  **3.26 : 1 en claro** antes, **19.26 : 1** después; oscuro 5.91 → 21. Por DEC-016 este **sí**
  bloqueaba: el ancla la escribe FARO.
- **Dos razones por las que el barrido anterior no lo cazó**, ambas anotadas para que no se repitan:
  se midió primero el tema oscuro —donde el defecto no aparece— y la tabla que contiene el link
  está **debajo del pliegue**, así que sus 30 anclas ni siquiera estaban en el DOM.
- **§3 medido en DB-08** por primera vez. Los números no son comparables con los de DB-05 y por eso
  se reportan por separado: DB-08 tiene **1209 nodos de texto** contra 34, **5 filtros y ningún
  tab**. Confirmó además que el §3 anterior describía DB-05: citaba "6/6 tabs y 3/3 filtros".
- **BUG-056** nace de esta pasada: 122 celdas del pivote de DB-08 a 3.55 : 1 en claro. Se verificó
  contra el YAML que **FARO no declara ese color**, así que por DEC-016 es limitación conocida y no
  bloquea — pero pesa más que el chrome, porque son los valores del explorador.
- **BUG-051 dejó de bloquear** por DEC-016, sin trabajo de por medio.

### El §3.2 volvió a cerrarse con comprobación humana, y volvió a hacer falta

El navegador automatizado no entrega `Enter` ni clic a los componentes React de Superset —sí mueve
el foco—, así que habría reportado un **falso negativo** por segunda vez. Se dejó sin marcar hasta
que la autora verificó a mano que `Tab` + `Enter` abre el desplegable del filtro *Ciclo escolar*.
Es el mismo patrón que en DB-05 el 4-sep: cuando el instrumento no puede distinguir un defecto de
su propia limitación, el caso no se marca — se comprueba.

- **Bugs abiertos:** [[vault/06_Quality_Testing/Bug_Register]] — **BUG-051** y **BUG-056**, los dos
  limitación conocida por DEC-016. **BUG-038** cerrado en la pasada anterior.
