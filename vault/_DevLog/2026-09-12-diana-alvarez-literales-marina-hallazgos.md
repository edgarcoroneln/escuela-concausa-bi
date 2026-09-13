---
title: "Barrido de literales de Marina (§3.bis): 12 + 4 apariciones de '7 escuelas' quitadas, Hallazgos.jsx rotulado, Conclusion.jsx conectado a nombre real de municipio"
fecha: 2026-09-12
autor: Diana Aracely Alvarez Varela
herramienta: Claude Code / claude-sonnet-5
relacionado: [US-621, REQ-002, BUG-058, BUG-077]
---

## Contexto

Marina García del Buey (tech lead UX/UI) mandó una revisión directa a Diana Álvarez señalando
literales de "7 escuelas/siete historias" tecleados en 7 pantallas (regla §3.bis: el conteo de
escuelas en riesgo nunca va tecleado, sale del dato vivo -- mismo patrón que `BUG-058`), un error
de terminología en `MatrizDrivers.jsx` (usa "pistas" para referirse a escuelas, cuando el
glosario define "las 7 pistas" como matrícula + 6 drivers), y un hallazgo más serio en
`Hallazgos.jsx` (constantes tecleadas, sin llamada al API, sin rótulo de dato de ejemplo).

## Verificación previa a corregir

Los números de línea del reporte de Marina no coincidían con el árbol actual (probablemente
revisó una versión anterior a los commits de hoy) -- se ubicó cada literal por contenido, no por
línea, con `grep` sobre `pages/` y `components/`. Esto reveló **4 apariciones adicionales que
Marina no listó**, todas en `ComparacionTerritorial.jsx` (pantalla construida más tarde el mismo
día, probablemente después de su revisión): "Volver a los 7 casos", "más de una de las 7 escuelas
en riesgo", "Ninguno de los 7 casos" y el título de tarjeta "Las 7 escuelas por municipio y
nivel". Se corrigieron con el mismo criterio que el resto.

## Los 16 literales corregidos

Regla aplicada, la misma que propone Marina: donde el número solo describe la pantalla, se quita;
donde de verdad hace falta (subtítulo dinámico), sale del dato vivo ya cargado en esa pantalla
(no se agregó ninguna llamada nueva al API para esto).

- `Comparativa.jsx`: "las 7 escuelas en riesgo" → "las escuelas en riesgo".
- `ExpedienteEscuela.jsx` y `ComparacionTerritorial.jsx`: "Volver a los 7 casos" → "Volver a los
  casos" (2 apariciones).
- `Hallazgos.jsx`: "(2 de 7 casos)" → "entre los casos" (se quita el total tecleado, no el
  hallazgo en sí); título "Siete escuelas, siete historias" → "Cada escuela, su historia".
- `LosSieteCasos.jsx`: título "Nuestros 7 casos" → "Los casos que requieren atención"; subtítulo
  "Siete escuelas presentan una señal..." ahora usa `escuelas.length` (el mismo arreglo que ya
  carga la pantalla vía `getEscuelasEnRiesgo()`, sin llamada nueva), con una frase genérica de
  respaldo mientras carga.
- `MapaCasos.jsx`: subtítulo del header y título de la tabla, se quita el "7".
- `MatrizDrivers.jsx`: título "Las 7 pistas sobre la mesa" → **"Las seis pistas, caso por caso"**
  (propuesta literal de Marina) -- corrige el choque de terminología: en el glosario
  (`00_Storytelling_Scope §3.1`) "las 7 pistas" es matrícula + 6 drivers, y esta pantalla solo
  muestra los 6 drivers, así que el mismo término no puede significar "7 escuelas" aquí. Subtítulo
  y nota de `EnConstruccion` también pierden el "7".
- `VistaGeneral.jsx`: subtítulo del header y del mapa, se quita el "7".
- `ComparacionTerritorial.jsx` (las 4 apariciones no listadas por Marina, ver arriba).

## Hallazgos.jsx -- el que más preocupaba

Confirmado con lectura del código (no solo con `VITE_USE_MOCK=false`, como hizo Marina): `HALLAZGOS`
y `DISTRIBUCION` son arrays tecleados en el archivo, sin `useApiResource` ni llamada al API. Es la
única de las nueve pantallas que afirma sin avisar. Arreglo aplicado hoy, tal como propuso Marina
("eso lo arregla hoy y es honesto"): se agrega `<DemoBadge />` **incondicional** (no detrás de
`status === "demo"`, porque no hay `status` -- no hay fetch) bajo el subtítulo, mismo patrón que
`VistaGeneral.jsx` (bloques rotulados aunque se apague la bandera de mock). Conectarla de verdad
al API queda fuera de este commit -- no es parte del pedido de hoy y el rótulo ya la vuelve
honesta mientras tanto.

## Hallazgo adicional, fuera de la lista de Marina: `Conclusion.jsx`

Al auditar el mismo patrón ("¿el contrato ya no tiene esta limitación?") se encontró que
`Conclusion.jsx` (Pantalla 5) tenía el mismo gap que Marina señaló como desbloqueado hoy para
`MapaCasos.jsx`/`ComparacionTerritorial.jsx`, pero sin corregir: la tarjeta "Concentración por
municipio" pintaba `cve_mun` crudo con el subtítulo "cve_mun -- el contrato aún no expone el
nombre del municipio" -- ya no es cierto, `MunicipioOut` trae `nombre_municipio` desde el 11-sep
(US-621), confirmado real por `BUG-077` (317/317 municipios). Se agrega `getConclusionEscuelas()`
en `lib/api.js` (compone `getPanoramaEscuelas()` + `getMunicipiosPorClaves()`, mismo patrón que
`getComparacionTerritorial()`, una llamada por municipio único) y se conecta la tarjeta al nombre
real; en modo demo se agrupa por el nombre de municipio que ya trae el mock (no tiene `cve_mun`),
mismo patrón `esReal` que `ComparacionTerritorial.jsx`.

## Lo que NO se tocó (a propósito)

- Nombres técnicos, la ruta `/casos`, y todos los comentarios de código que mencionan "7
  escuelas"/"los 7 casos" -- quedan igual, como pidió Marina explícitamente.
- `Comparativa.jsx` y `MatrizDrivers.jsx` (la pantalla completa, no el header) siguen en
  "en construcción": son bloqueos técnicos reales y distintos (serie histórica de matrícula que no
  existe; endpoint de lote para drivers que no existe) -- no tienen relación con los campos que se
  desbloquearon hoy (lat/lon, nombre de municipio/entidad).
- El resto del contenido de `HALLAZGOS`/`DISTRIBUCION` (p. ej. "6 municipios y 5 entidades") no se
  tocó -- Marina no lo listó entre los 12 literales y conectar esa pantalla de verdad queda para
  después, según su propia recomendación.

## Verificación

Balance de paréntesis/llaves/corchetes (0/0/0) en los 10 archivos tocados, `git diff --check`
limpio y `vault_lint` limpio. Sin binding nativo de `oxlint`/`esbuild` en este entorno (mismo
motivo que el commit anterior) para correr el lint real -- pendiente que Diana lo confirme con
`npm run dev` desde su Mac, ahora sí con datos reales (`VITE_USE_MOCK` fuera).
