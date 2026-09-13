---
title: "Retiro de las 6 vistas heredadas y de VistaGeneral.jsx (decisión de Marina García del Buey): El diferenciador rescatado en Conclusión, arquitectura final de 7 pantallas"
fecha: 2026-09-12
autor: Diana Aracely Alvarez Varela
herramienta: Claude Code / claude-sonnet-5
relacionado: [US-641, US-621, ADR-011]
---

## Contexto

Marina García del Buey respondió a la pregunta de arquitectura pendiente sobre `VistaGeneral.jsx`
y las 6 rutas "Heredadas" del Sidebar (mensaje completo citado en el DevLog de checklist/pendientes
del mismo día). Decisión, textual: **las 6 heredadas se retiran y la sección "Vistas heredadas"
desaparece por completo** -- la arquitectura final del producto son las 7 pantallas del spec de
Equipo 3, no 7 + una sección secundaria con versiones duplicadas de lo mismo. Antes de apagar
`VistaGeneral.jsx` había que rescatar "El diferenciador", que **no es una comparación de 2 ciclos de
matrícula** (esa es una pieza distinta de la misma pantalla) sino el par de CCTs reales elegido por
Marina el 6-sep (`15DPR0920D`/`15DPR2254O`, mismo municipio, mismo índice de riesgo, distinto driver
dominante y distinta recomendación) -- la prueba concreta de la tesis del proyecto.

## Qué se retiró

- **Páginas borradas** (6): `VistaGeneral.jsx`, `Hallazgos.jsx`, `MatrizDrivers.jsx`, `MapaCasos.jsx`,
  `Comparativa.jsx`, `ComparacionTerritorial.jsx`.
- **Rutas borradas de `main.jsx`**: `/vista-general`, `/hallazgos`, `/drivers`, `/mapa`,
  `/comparativa`, `/comparacion-territorial`. Comentario desactualizado del router ("las 9 pantallas
  del storytelling de 'los 7 casos'", señalado hoy por Diana) corregido de paso: la arquitectura son
  7 pantallas + `/explorador`.
- **Sidebar/navFases**: se quita la sección "Vistas heredadas" completa (`SectionLabel` + `nav`), el
  export `HEREDADAS` de `lib/navFases.js`, y el comentario "Las 5 vistas heredadas..." que ya estaba
  desactualizado (eran 6 desde que `/hallazgos` se volvió heredada al construirse `/conclusion`) --
  por indicación explícita de Marina, no se corrigió el número: se borró junto con la sección.
- **`lib/api.js`**: se quita `getComparacionTerritorial()` (solo la usaba la pantalla retirada);
  `getMunicipiosPorClaves()` se queda, la sigue usando `getConclusionEscuelas()`.
- **Componentes huérfanos borrados** (verificado uno por uno que ninguna pantalla viva los importa):
  `KpiCard.jsx`, `BarChartCard.jsx`, `DonutChartCard.jsx`, `MapaRiesgo.jsx`, `EnConstruccion.jsx`.

Motivo por ruta, tal como lo documentó Marina (no reinterpretado): `/vista-general` la cubre
Panorama; `/hallazgos` la cubre Conclusión; `/drivers` lo cubre el bloque "Comparativa de los 6
drivers" de Panorama; `/mapa` lo cubre el bloque de ubicación de Panorama, y además una pantalla
dedicada a "¿dónde están ocurriendo los casos?" contradice la propia decisión de que el mapa es
contexto de ubicación, no ranking; `/comparativa` y `/comparacion-territorial` eran recorte
declarado de la especificación (§8.1: sin serie histórica de matrícula por escuela y sin promedio
estatal en el API), no una conexión pendiente.

**Confirmado antes de borrar cada componente**: `KpiCard`/`BarChartCard`/`DonutChartCard`/
`MapaRiesgo` solo los importaba `VistaGeneral.jsx` (y `MapaRiesgo` también `MapaCasos.jsx`, ambas
retiradas); `EnConstruccion` solo lo importaban `Comparativa.jsx`/`MatrizDrivers.jsx`. `DriverMatrix`
NO se tocó -- lo sigue usando `Panorama.jsx`. Verificado también que `Panorama.jsx` ya cubre lo que
parecía que se perdía con `VistaGeneral.jsx` (KPIs, mapa de las 4 entidades, variación de matrícula
vs. ciclo anterior vía `kpisMockParaComparacion2Ciclos`/`KpisOut`) -- no hay funcionalidad real
perdida fuera de "El diferenciador", que se rescató.

## El diferenciador, rescatado en Conclusión

Movido tal cual de `VistaGeneral.jsx` a `Conclusion.jsx` (constantes, funciones y bloque JSX con sus
3 estados de carga/error/demo, usando el mismo `DifferentiatorChart.jsx` ya existente) -- **no en
Panorama**, por indicación explícita de Marina: es la evidencia de cierre de la conclusión ("mismo
riesgo, distinto problema, distinta acción"), no el enunciado de apertura de la investigación. Se
colocó después de la tarjeta "Concentración por municipio" y antes de la nota obligatoria de cierre
de la pantalla.

**Nota de QA de Marina, sin resolver aquí a propósito:** al probarlo contra su API local, el bloque
devolvió 404 -- probablemente porque su base local tiene pocos datos y no incluye esos 2 CCTs
específicos. El código ya maneja ese caso con su propio estado de error (no revienta la pantalla),
pero **falta confirmar contra la base con datos completos, antes del freeze**, que `15DPR0920D` y
`15DPR2254O` sí existen ahí -- pendiente de Diana/quien tenga acceso a esa base.

## Los 4 literales que Marina pensaba pendientes: ya estaban resueltos

Marina calculó que, tras retirar las 6 heredadas, quedarían 4 literales de "7" sin corregir en
`LosSieteCasos.jsx` y `ExpedienteEscuela.jsx` (líneas de su reporte original, previas al barrido de
hoy). Verificado por contenido, no por línea: **ya no queda ninguno** -- el barrido de literales de
Marina de esta misma tarde (`vault/_DevLog/2026-09-12-diana-alvarez-literales-marina-hallazgos.md`)
ya los había corregido a todos, en ambos archivos. No hizo falta tocar nada aquí.

## Verificación

Balance de paréntesis/llaves/corchetes (0/0/0) en los 18 archivos `.js`/`.jsx` tocados (creados,
modificados o borrados), `git diff --check` y `vault_lint.py` limpios. Sin Docker ni bindings
nativos de `oxlint`/`esbuild` en este entorno -- pendiente que Diana confirme con `npm run dev` que
Conclusión se ve bien con el bloque nuevo (Marina pidió específicamente esta confirmación: "que el
diferenciador quepa sin romper la lectura de la pantalla; si desbalancea, avísame y buscamos otro
lugar").
