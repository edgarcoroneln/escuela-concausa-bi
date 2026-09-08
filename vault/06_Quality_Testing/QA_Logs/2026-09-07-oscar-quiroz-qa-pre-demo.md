---
id: QALOG-2026-09-07-OSCAR-QUIROZ
title: "QA pre-demo — Oscar Quiroz — Corrección visual (10 dashboards)"
owner: "Oscar Antonio Quiroz Lázaro"
status: done
traces_up: ["vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo"]
traces_down: ["vault/06_Quality_Testing/Bug_Register"]
last_reviewed: "2026-09-07"
tags: [qa, qa-log, pre-demo, celula-2]
---

# QA pre-demo — Oscar Quiroz — Corrección visual

> → [[vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo]] · [[vault/06_Quality_Testing/QA_Logs/_index]]

## Tres reglas para escribir un caso

1. **Un caso es reproducible por alguien más.** "El tablero se ve mal" no es un caso; "DB-01,
   entidad = Jalisco, ciclo 2024-2025: el KPI-04 muestra 0 y `/api/v1/kpis` devuelve 7" sí lo es.
2. **"Obtenido" es lo que viste, no lo que concluiste.** El diagnóstico va en la columna de
   evidencia o en el bug, nunca en lugar del dato.
3. **Un caso que no corriste se marca `⏭️ no ejecutado` con el motivo.** Nunca se deja en blanco y
   nunca se marca ✅ sin haberlo visto. Un plan con huecos honestos vale más que uno completo y falso.

## Datos de la sesión

- **Responsable:** Oscar Antonio Quiroz Lázaro
- **Superficie asignada:** Corrección visual — gráficos, mapas, tarjetas vacías, valores de KPI, contraste (10 dashboards, `/Dashboards`)
- **URL probada:** https://faro-frontend-526490367142.us-central1.run.app/Dashboards
- **Fecha y hora de inicio / fin:** 2026-09-07, 20:39 CST / 22:30 CST
- **Sesión iniciada como:** oscar.qlazaro@gmail.com · rol `analista` (confirmado: dashboards cargan con datos reales sin restricción)
- **Navegador y sistema:** Google Chrome 152.0.7977.82, macOS

## Resultados

> Veredictos: **✅ pasa** · **❌ falla** (levanta bug) · **⚠️ pasa con reserva** (funciona pero se ve
> mal o es frágil) · **⏭️ no ejecutado** (con motivo).

| # | Caso | Esperado | Obtenido | Evidencia | Veredicto | Bug |
|---|---|---|---|---|---|---|
| 1 | DB-01 Panel Ejecutivo, fila de KPIs, ciclo 2024-2025, sin filtro de entidad | KPI-01 = 6,704,229 (cifra de referencia de Diana/plan); KPI-05 ≈ 0.62; ninguna tarjeta en No data/NaN | KPI-01 = 6,704,229 ✓ · KPI-02 = -2.9% · KPI-05 = 62% ✓ · "Escuelas en alcance" = 44,114 — las 4 tarjetas muestran número + subtítulo completos, sin cortes, en una sola fila | Captura 8:41pm, Chrome, tema oscuro | ✅ | — |
| 2 | DB-01, "Matrícula por ciclo" y "Ranking municipal por matrícula" | Gráfico de barras con valor sobre la barra, tabla ordenada por matrícula descendente | Barra 2024-2025 = 6,704,229 sobre la barra; tabla con 12 municipios, Iztapalapa arriba (259,942), orden correcto | Captura 8:43pm | ✅ | — |
| 3 | DB-01, "Escuelas por nivel (KPI-08)" — pastel, 3 categorías (Primaria/Secundaria/Preescolar) | Leyenda muestra las 3 categorías a la vez; etiquetas de rebanada legibles | Leyenda paginada, solo 1 de 3 visible (`◀ 1/3 ▶`); etiquetas de rebanada truncadas ("SECU...", "PR..." — ambiguo entre Primaria y Preescolar) | Captura 8:43pm | ❌ | `BUG-064` |
| 4 | DB-01, "Escuelas por sostenimiento (KPI-09)" — pastel, 2 categorías | Etiquetas de rebanada legibles | Etiquetas truncadas ("PRI...", "PÚB...") — menos ambiguo que el caso 3 por ser solo 2 categorías, mismo patrón de fondo | Captura 8:43pm | ❌ | `BUG-064` |
| 5 | DB-01, "Driver dominante (KPI-07)" — barras, 6 drivers | Eje X con el nombre de cada uno de los 6 drivers bajo su barra | Solo la primera barra muestra su categoría ("Agua"); las otras 5 barras (valores 419, 12,765, 2,086, 2,792, 26,046, 6) no muestran nombre de driver en el eje | Captura 8:43pm | ❌ | `BUG-064` |
| 6 | DB-02 Mapa de Riesgo, KPI-04 "Escuelas en riesgo" | Debe decir 7, no 0 (cifra de referencia DEC-019/Diana) | 7 ✓ | Captura 8:44pm | ✅ | — |
| 7 | DB-02, "% de escuelas en riesgo" junto a KPI-04 = 7 | Si dice 0.0%, confirmar que es un 0 verdadero y no un filtro roto (patrón BUG-054) | 0.0% — matemáticamente consistente: 7 escuelas sobre decenas de miles con predicción redondea a 0.0% a 1 decimal. Verificado, no es filtro roto | Captura 8:44pm | ✅ | — |
| 8 | DB-02, "Matrícula expuesta" vs DB-01 KPI-01 | Coherencia del mismo total nacional entre tableros distintos (chequeo de Diana) | 6,704,229 en ambos — idéntico | Captura 8:44pm | ✅ | — |
| 9 | DB-02, Coroplético (KPI-10) y puntos de riesgo | Mapas pintan, sin municipios en blanco sin explicación | Ambos mapas pintan con leyenda de rangos (coroplético) y clusters de puntos coherentes con las zonas de mayor riesgo | Captura 8:44pm | ✅ | — |
| 10 | DB-02, "Ranking municipal por escuelas en riesgo (KPI-04)" | Consistente con KPI-04 = 7 total | Toluca 0.6%, Naucalpan de Juárez 0.3%, resto en 0.0% — suma coherente con el total de 7 | Captura 8:44pm | ✅ | — |
| 11 | DB-03 Ficha de Escuela, fila de KPIs, sin filtro de CCT aplicado | KPI-15/02/17/05 deben reflejar una sola escuela (o mostrar un placeholder claro si no hay CCT elegido) | Las 4 tarjetas ("Matrícula/Variación/Completitud de la escuela") muestran exactamente los mismos agregados nacionales de DB-01/DB-02 (6,704,229 / -2.9% / 0.36 / 62%) bajo etiquetas que dicen "de la escuela"; "Perfil del plantel" lista varias escuelas, confirmando que no hay CCT aplicado | Captura 8:59-9:01pm | ❌ | `BUG-065` |
| 12 | DB-03, filtro "Escuela (CCT)": seleccionar `15DPR0920D` (CCT oficial del par de demostración) | El valor se selecciona una vez y "Apply filters" se habilita | `15DPR0920D` aparece **duplicado** en la lista del dropdown (2 entradas idénticas, ambas ✓); "Apply filters" queda deshabilitado sin importar el reintento | Captura 9:05pm y 9:07pm (persiste al reabrir el dropdown) | ❌ | `BUG-065` |
| 13 | DB-03, mismo filtro, con un CCT de control sin duplicar (`01DPR0540S`) | Aísla si el filtro está roto en general o solo para el CCT duplicado | "Apply filters" se habilitó normalmente; las 4 tarjetas cambiaron a valores de esa escuela (28 alumnos, -22.2%, 67%) y "Perfil del plantel" mostró una sola fila — el mecanismo de filtrado funciona, el defecto es específico de la entrada duplicada de `15DPR0920D` | Captura 9:10pm | ✅ (confirma causa acotada) | `BUG-065` (evidencia de aislamiento) |
| 14 | DB-03, KPI-17 "Índice de riesgo" filtrado a `01DPR0540S` | Si no hay predicción ML-01 para esa escuela, debe decir "No data"/SIN_DATO explícito, no 0 | "No data", con subtítulo "Vacío = sin dato disponible" — comportamiento esperado por diseño (regla SIN_DATO≠0), no bug | Captura 9:10pm | ✅ | — |
| 15 | DB-03, verificación del par de demostración (`15DPR0920D`/`15DPR2254O`, `índice_riesgo` esperado 0.4774 en ambos, per plan de Diana) | Confirmar la cifra de referencia | **No ejecutado** — bloqueado por el caso 12 (no se puede filtrar por `15DPR0920D`) | — | ⏭️ | `BUG-065` (bloquea esta verificación) |
| 16 | DB-04 Comparador de Municipio, fila de KPIs, sin filtro de municipio aplicado | Comportamiento de "comparador": sin selección, se asume la comparación sobre todo el universo | KPI-01 = 6,704,229, "Escuelas comparadas" = 44,114, KPI-02 = -2.9%, KPI-04 = 0.0% — idénticos al agregado nacional, bajo etiquetas "de los municipios seleccionados" | Captura 9:24pm | ✅ (confirmado correcto tras filtrar, ver caso 18) | — |
| 17 | DB-04, "KPI-03 · Riesgo promedio por municipio" y mini-gráficos D1/D2, sin filtrar | Eje Y con escala decimal (0, 0.2, 0.4... 1.0) para un índice 0-1 | Eje Y muestra "0, 0, 0, 1" — formato de número entero en un rango 0-1, hace parecer que casi todos los municipios tienen riesgo/driver ≈0 cuando está distribuido en todo el rango | Captura 9:25pm | ❌ | `BUG-066` |
| 18 | DB-04, mismo grupo de gráficos (KPI-03 y D1-D6) | Eje X con el nombre de cada municipio bajo su barra (o al menos una muestra representativa, no solo el primero alfabético) | Solo se ve "Abasolo" (o el municipio filtrado) como única etiqueta de eje X; con ~300 municipios sin filtrar, el resto no muestra nombre — mismo patrón que "Driver dominante" de DB-01 (`BUG-064`) pero recurrente en 7 gráficos de este tablero | Captura 9:25pm | ❌ | `BUG-066` |
| 19 | DB-04, filtro "Municipios a comparar": aislar si el filtro funciona | Seleccionar un municipio de control (`Zapopan`) y confirmar que "Apply filters" habilite y los gráficos cambien | Con `Zapopan` seleccionado, todos los gráficos SÍ cambiaron correctamente (una sola barra, eje X = "Zapopan") tras darle clic a "Apply filters" — el filtro funciona, **no es el mismo bug bloqueante que BUG-065** | Captura 9:28-9:30pm | ✅ (filtro funcional) | — |
| 20 | DB-04, botón "Apply filters" durante el caso 19 | El botón debe verse habilitado (azul) cuando hay un cambio pendiente por aplicar, y gris cuando no lo hay | **Corregido tras revisión en vivo (no en la captura estática):** el botón sí se pone azul al hacer un cambio pendiente — comportamiento correcto. La lectura inicial de "siempre gris" fue un error mío al interpretar la captura, no un defecto real. Retractado antes de anunciarlo | Captura 9:28-9:30pm + confirmación en vivo de Oscar | ✅ (comportamiento correcto, hallazgo descartado) | — |
| 21 | DB-04, D5 "Estrés hídrico" y D6 "Calidad del aire" filtrados a `Zapopan` | D5 sin dato es esperado (BUG-030); D6 en una zona metropolitana grande (Guadalajara) se esperaría cobertura SINAICA | Ambos gráficos aparecen completamente en blanco, sin ninguna barra ni indicación de SIN_DATO. D5 es consistente con la limitación ya conocida; **D6 en Zapopan llama la atención** — no se profundizó, queda como observación para verificar contra la cobertura real de estaciones SINAICA | Captura 9:30pm | ⚠️ (D5 esperado; D6 sin concluir) | — |
| 22 | DB-05 Análisis por driver, tab D1, tarjetas KPI (KPI-07, Escuelas por driver, % sin recomendación, Escuelas con recomendación) | Tarjetas con dato, sin No data/NaN | KPI-07 = 6.3%, Escuelas por driver = 2,792, % sin recomendación = 0.0% (con subtítulo "SIN_DATO explícito", correcto), Escuelas con recomendación = 44,108 — todo con dato real | Captura 9:46-9:47pm | ✅ | — |
| 23 | DB-05, mismas tarjetas — longitud de título | Título de la tarjeta no debería ocupar más espacio que el número | Títulos como "D1 · KPI-07 · % escuelas por driver dominante" se envuelven en 4-5 líneas, ocupando buena parte de la tarjeta. Mismo patrón que el `alto` de DB-01 que Edgar dejó **congelado** — no es un hallazgo nuevo, mismo tipo de limitación en otro tablero | Captura 9:46pm | ❌ (mismo patrón ya congelado, no reportar aparte) | — |
| 24 | DB-05, "D1 · % escuelas por driver dominante por ciclo" (`echarts_timeseries_line`) | Eje Y y etiqueta del punto de dato deben reflejar el valor real (6.3%, visible en KPI-07 del mismo tab) | Eje Y en "0,0,0,0,0"; la etiqueta del propio punto de dato también lee "0" (sin signo %). Tercer tablero con el mismo defecto de fondo que BUG-066 — aquí ni siquiera la etiqueta del dato individual respeta el formato, no solo el eje | Captura 9:47pm | ❌ | `BUG-066` (ampliado) |
| 25 | DB-05, tab D5 "Estrés hídrico" — KPI-07 y "Escuelas por driver dominante" | Con la fuente sin ingerir (nota del tab: "SIN_DATO explícito -- fuente aún no ingerida"), el 0% debe ser un 0 real, no un filtro roto | KPI-07 = 0.0%, "Escuelas por driver dominante" = 0 — consistente con la limitación ya documentada; ningún municipio puede tener D5 como dominante si la fuente no está cargada. Correcto, no es bug | Captura 9:52pm | ✅ | — |
| 26 | DB-05, tab D6 "Calidad del aire" — KPI-07 y "Escuelas por driver dominante" | Tarjetas con dato real (D6 sí tiene cobertura parcial, a diferencia de D5) | KPI-07 = 0.9%, "Escuelas por driver dominante" = 419 — **coincide exactamente con la barra "419" que ya vimos en "Driver dominante (KPI-07)" de DB-01** (caso 5). Buena confirmación de coherencia entre tableros | Captura 9:56pm | ✅ | — |
| 27 | DB-05, "D5 · % ... por ciclo" y "D6 · % ... por ciclo" (mismo chart que caso 24) | Mismo chequeo, en los tabs D5 y D6 | Mismo patrón: D5 con eje Y "1,1,1,0,0" (no monótono, valores repetidos) y punto en "0"; D6 con eje Y "0,0,0,0,0" y punto en "0" (debería ser 0.9%). Confirma que `BUG-066` afecta los 6 tabs por igual — no se necesita revisar D2-D4 para confirmarlo más | Captura 9:53pm y 9:56pm | ❌ | `BUG-066` (mismo patrón, sin ampliar más) |
| 28 | DB-06 Predicciones, fila de KPIs (KPI-01, KPI-02, KPI-12, % escuelas con predicción) | Tarjetas con dato real, sin No data/NaN | KPI-01 = 6,704,229 ✓ (coincide con DB-01), KPI-02 = -2.9% ✓, KPI-12 = -0.9%, % escuelas con predicción = 100% | Captura 9:59pm | ✅ | — |
| 29 | DB-06, "Matrícula observada por ciclo" (`echarts_timeseries_line`, métrica entera) | Eje Y con escala numérica normal | Eje Y correcto (0 a 7,000,000), punto de dato = 6,704,229 correcto. Confirma que el defecto de eje solo afecta métricas de fracción/porcentaje, no las enteras | Captura 9:59pm | ✅ | — |
| 30 | DB-06, "Variación proyectada (ML-01) por ciclo" (`echarts_timeseries_line`, métrica `variacion_proyectada_promedio`, `formato: porcentaje_1`) | Eje Y y punto de dato con formato porcentual correcto | **Correcto**: eje Y en 0.0%, -0.2%, -0.4%... -1.0%; punto de dato = -0.9% exacto. **Contraejemplo clave para BUG-066**: usa el mismo `formato: porcentaje_1` que `pct_escuelas_por_driver` (DB-05, caso 24, que sí falla) — confirma que la causa no es el string de formato en sí, acota la hipótesis para quien lo corrija | Captura 9:59pm | ✅ (pero cambia el diagnóstico de BUG-066) | `BUG-066` (acotado) |
| 31 | DB-06, "Distribución del riesgo proyectado" (pastel/donut) | Leyenda con todas las categorías visibles | Leyenda paginada, solo 1 categoría visible ("0.20 - 0.39") con `◀ 1/4 ▶` — mismo patrón de `BUG-064`, ahora confirmado en un segundo tablero | Captura 9:59pm | ❌ | `BUG-064` (ampliado) |
| 32 | DB-06, "Ranking municipal por riesgo" (tabla) | Consistente con KPI-04 = 7 escuelas en riesgo (verificado en DB-02, caso 6) | Toluca = 5, Naucalpan de Juárez = 2, resto en 0 — suma 7, exacto. Buena confirmación de coherencia entre tableros | Captura 9:59pm | ✅ | — |
| 33 | DB-07 Calidad de Cobertura, "Total de escuelas" y "Escuelas sin dato" | Total de escuelas debe coincidir con el total real en alcance (44,114, confirmado en DB-01/DB-04) | "Total de escuelas" = 264,684 = exactamente `44,114 × 6` — el grano del cubo (`cve_mun × nivel × id_driver × id_ciclo`) tiene una fila por cada uno de los 6 drivers y la métrica suma sin deduplicar. "Escuelas sin dato" = 100,747, mismo mecanismo. Verificado contra `metrics_db07.yaml` y el propio SQL de `cubo_completitud` | Captura 10:05pm | ❌ | `BUG-067` |
| 34 | DB-07, KPI-05 "Índice de completitud" y KPI-06 "% escuelas SIN_DATO" | Deben seguir siendo correctos pese a la inflación de conteos (son razones SUM/SUM sobre el mismo grano) | KPI-05 = 62% (coincide exacto con la cifra de referencia de Diana), KPI-06 = 38.1% — ambos correctos, la inflación se cancela en el cociente | Captura 10:05pm | ✅ | — |
| 35 | DB-07, "Mapa de vacíos municipal (KPI-06)" y "% SIN_DATO por driver" | Mapa pinta sin municipios en blanco sin explicación; gráfico de barras con las 6 categorías de driver | Mapa pinta correctamente con leyenda de 5 rangos; el gráfico de barras muestra las 6 categorías (D1-D6) con valores heterogéneos plausibles (14.8%-100%) — **con solo 6 categorías, el eje X sí muestra todos los nombres**, a diferencia de los gráficos con ~300 municipios. Buena evidencia de que el problema de eje X de BUG-066 es específico a muchas categorías | Captura 10:05-10:06pm | ✅ | — |
| 36 | DB-07, "Completitud detallada por municipio y driver" (tabla) | Datos reales, sin NaN | Valores reales de 73%-81% por municipio y driver (El Oro, Milpa Alta, Temascalcingo...) | Captura 10:06pm | ✅ | — |
| 37 | DB-08 Explorador de Cubo, "Escuelas en el explorador" | Total real (44,114), sin repetir el defecto de BUG-067 | 44,114 exacto — el subtítulo dice explícito "COUNT DISTINCT cct -- seguro bajo cualquier agrupación". Buen patrón de referencia, evitó proactivamente el defecto de grano multi-driver que sí tiene DB-07 | Captura 10:13pm | ✅ | — |
| 38 | DB-08, tabla dinámica "Explorador libre" y "Detalle por escuela × driver" | Datos reales, coherentes | Valores de driver plausibles (0.00-1.00), conteos de escuelas coherentes, filas D5/Agua presentes con el placeholder de BUG-030 (no una inconsistencia, D5 existe en la fila aunque nunca gane como dominante) | Captura 10:13pm | ✅ | — |
| 39 | DB-09 Recomendaciones, KPI-04 "Escuelas en riesgo" | Subtítulo debe decir "Índice ≥ 0.5 (DEC-019)", igual que DB-02/DB-04 | En producción muestra "Índice de riesgo >= 0.6 (R3)" — texto viejo. El YAML actual (`db09_recomendaciones.yaml`) **ya dice** "0.5 (DEC-019)" correctamente; este chart específico no se ha vuelto a sincronizar desde ese fix. No es bug de código, solo desincronización — se resuelve solo con el próximo sync (después del freeze) | Captura 10:15pm | ⚠️ (desincronización, no bug) | — |
| 40 | DB-09, KPI-04 = "No data", "% escuelas con recomendación" = 0%, "Recomendación de prioridad" = "No data" | Verificar si es el mismo BUG-063 (0 escuelas prioridad ALTA) o algo distinto | No se pudo confirmar con certeza la relación exacta — los tres tiles fallan juntos en el mismo dataset (`db09_cubo_recomendaciones`), consistente con BUG-063 pero sin evidencia suficiente para afirmarlo. Queda como duda abierta, no registrado como bug nuevo | Captura 10:15pm | ⚠️ (sin concluir) | — |
| 41 | DB-09, "Escuelas a intervenir (mayor riesgo)" (tabla, `metrica: indice_riesgo`, `order_desc: True`) | Escuelas con mayor índice de riesgo real deben aparecer primero | Las primeras ~6 filas muestran `N/A` (escuelas comunitarias sin predicción) **antes** que las filas con valor real (0.57, 0.52...) — Postgres ordena NULL primero en `ORDER BY DESC` sin `NULLS LAST` explícito | Captura 10:15pm | ❌ | `BUG-068` |
| 42 | DB-09, "Escuelas por driver dominante (KPI-07)" | Consistencia cruzada con el mismo chart de DB-01 | Mismos 6 valores exactos (419, 12,765, 2,086, 26,046, 2,792, 6) — coincide con DB-01. Mismo patrón de eje X con etiquetas parciales (BUG-066), ya documentado, no se amplía más | Captura 10:15pm | ✅ (dato) / conocido (eje) | — |
| 43 | DB-10 Monitor de Pipeline, "Fuentes con dato" | No puede exceder el total de 8 fuentes del catálogo (subtítulo propio del tile) | Muestra 11 — matemáticamente imposible frente a su propio universo declarado. Causa: `metrics_db10.yaml` (mío, US-223) tiene grano `[id_fuente, fecha_ingesta]`, y `SUM(es_ok)` cuenta cada fecha de ingesta por separado en vez de fuentes distintas. Mismo patrón que `BUG-067` | Captura 10:22pm | ❌ | `BUG-069` |
| 44 | DB-10, "Estado de las 8 fuentes" (tabla) | Las 8 fuentes reales, cobertura correcta | Lista exacta DS-01 a DS-08, las 8 con `cobertura_pipeline = OK`, filas ingeridas plausibles (12.5M SESNSP, 2.27M CONAPO... hasta 10 SINAICA) | Captura 10:22pm | ✅ | — |
| 45 | DB-10, KPI-13 "Filas ingeridas" y "Fuentes SIN_DATO" | Valores reales | KPI-13 = 16,325,303 (plausible, suma de las 8 fuentes reales); "Fuentes SIN_DATO" = 0, consistente con que las 8 fuentes reales están OK | Captura 10:22pm | ✅ | — |
| 46 | DB-10, "Última ingesta" | Ya documentado como limitación cosmética aceptada (no reportar de nuevo) | Muestra ".409ms" — mismo límite conocido de `big_number_total` con timestamps, aceptado desde el cierre de US-223 | Captura 10:22pm | ⚠️ (conocido, no bug) | — |

## Resumen

- **Casos ejecutados:** 46 — **los 10 dashboards completos** (D2-D4 de DB-05 omitidos deliberadamente, mismo patrón ya confirmado en D1/D5/D6)
- **✅ pasa:** 27 · **⚠️ con reserva:** 4 (caso 21 D6 sin concluir DB-04; caso 39 desincronización no-bug; caso 40 duda abierta sin concluir; caso 46 límite cosmético ya conocido) · **❌ falla:** 14 · **⏭️ no ejecutado:** 1 (bloqueado por BUG-065)
- **Bugs levantados:**
  - `BUG-064` — agrupa hallazgos de DB-01 y DB-06 (leyenda de pastel paginada/truncada, eje X de driver dominante sin etiquetas)
  - `BUG-065` — filtro "Escuela (CCT)" de DB-03 no aplica para `15DPR0920D` (entrada duplicada en el dropdown); bloquea la verificación del par de demostración de Diana. **Escalado a Edgar por Teams de inmediato**, antes de terminar esta bitácora
  - `BUG-066` — eje Y/etiquetas sin formato decimal-porcentual + eje X sin categorías en gráficos `echarts_timeseries_*` con muchas categorías. Confirmado en **3 tableros** (DB-01, DB-04, DB-05); **acotado** con un contraejemplo en DB-06 que usa el mismo formato y sí funciona
  - `BUG-067` — DB-07: "Total de escuelas"/"Escuelas sin dato" inflados ×6 por el grano del cubo (una fila por driver, sin deduplicar). **En mi propio archivo** (`metrics_db07.yaml`, US-222). Los KPI de porcentaje están correctos. *(Nota: este número ya había sido usado y retractado antes en esta misma sesión para un hallazgo distinto que resultó no ser un bug — el botón "Apply filters" de DB-04, que sí funciona bien. Como nunca se escribió en `Bug_Register.md`, el ID quedó libre y se reutiliza aquí para este hallazgo real, sin relación con el anterior.)*
  - `BUG-068` — DB-09: "Escuelas a intervenir (mayor riesgo)" ordena con NULLs primero (default de Postgres en `ORDER BY DESC` sin `NULLS LAST`); escuelas sin predicción aparecen antes que las de mayor riesgo real
  - `BUG-069` — DB-10: "Fuentes con dato" = 11 cuando el catálogo tiene 8 (grano `[id_fuente, fecha_ingesta]` sumado sin deduplicar). Mismo patrón que BUG-067, en mi propio archivo (US-223)
- **Clasificación para el miércoles** (del plan):
  - `BUG-064` → 🟠 se ve mal pero sobrevive
  - `BUG-065` → 🔴 rompe la demo (bloquea filtrar uno de los 2 CCT oficiales de la demostración, minuto 3:00-5:00 del guion)
  - `BUG-066` → 🟠 se ve mal pero sobrevive (mismo criterio que BUG-064)
  - `BUG-067` → 🟠 se ve mal pero sobrevive (número muy notorio, pero los KPI que importan — porcentajes — están correctos)
  - `BUG-068` → 🟠 se ve mal pero sobrevive (afecta el orden de una tabla de priorización, no rompe el tablero)
  - `BUG-069` → 🟠 se ve mal pero sobrevive (número imposible visible de inmediato, pero no bloquea el tablero)

## Lo que NO alcancé a probar

> Esta sección vale tanto como la tabla. Di qué quedó fuera y por qué, para que el PO sepa dónde no
> hay cobertura en vez de suponer que la hay.

- **DB-03, verificación de `índice_riesgo = 0.4774` para el par de demostración** (`15DPR0920D`/`15DPR2254O`) — bloqueado por `BUG-065`: no se puede filtrar por `15DPR0920D`. Pendiente de reintentar en cuanto se corrija el filtro.
- **DB-05, tabs D2, D3, D4** — decisión deliberada de no revisarlos: los 6 tabs comparten exactamente el mismo template de charts (documentado en `db05_analisis_driver.yaml`), y el defecto de `BUG-066` ya se confirmó en D1. Repetirlo en D2-D4 no aportaría información nueva.
- **Ventana angosta (proyector, ~1024px) y contraste en tema claro** — no se probaron de forma explícita y sistemática en ningún tablero. Todas las capturas de esta sesión se tomaron en ventana ancha y tema oscuro. El único dato indirecto que tengo es que el panel de filtros abierto (que angosta el área útil de forma similar a una ventana angosta) empeora visiblemente el truncado de leyendas ya reportado en `BUG-064`/`BUG-066` — pero no es lo mismo que una prueba real en proyector ni en tema claro. Queda sin cobertura.
- **DB-09, caso 40:** la relación exacta entre `BUG-063` y el patrón "No data"/0% de KPI-04, "% escuelas con recomendación" y "Recomendación de prioridad" en el mismo dataset (`db09_cubo_recomendaciones`) no se confirmó con certeza — anotado como duda abierta, no como bug.
- **DB-04, caso 21:** si "Calidad del aire" (D6) en blanco para Zapopan es un hueco real de cobertura SINAICA o solo la escala del mapa/filtro — no se profundizó.

## Hallazgos que no son bugs

> Cosas que sorprenden pero son comportamiento esperado, o dudas que conviene que alguien más lea.
> Si algo de aquí debería estar en las *«seis cosas que hay que saber»* del plan, dilo.

- **DB-09, "Recomendaciones de prioridad ALTA" en 0/No data** — ya conocido como `BUG-063` (causa registrada: el corte de prioridad está por encima del máximo real observado). No se reportó de nuevo, tal como indica el plan.
- **Contraste del tema de fábrica** — deuda ya medida y declarada en `DEC-016`. No se reportó de nuevo.
- **DB-01, scroll interno en los tiles de KPI** — la tarea de subir el `alto` sigue **congelada** por indicación explícita de Edgar hasta después del sync (posterior al 9-sep). Si el patrón de título largo/tarjeta apretada reaparece (visto también en DB-05), es la misma limitación ya declarada, no un hallazgo nuevo.
- **DB-05/DB-08, filas de driver D5 con el placeholder de `BUG-030`** — D5 nunca gana como dominante (0% en todo DB-05) pero sí aparece como fila en el explorador de DB-08 con su valor placeholder; son dos cosas distintas y ambas son comportamiento esperado, no contradictorias.
- **DB-09, KPI-04 con subtítulo "Índice >= 0.6 (R3)"** — el YAML actual ya dice "0.5 (DEC-019)"; el chart en producción simplemente no se ha vuelto a sincronizar. Se resuelve solo con el próximo sync (después del freeze), no requiere fix de código.
