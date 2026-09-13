---
id: DOC-DEVLOG-2026-09-12-COMPARATIVA-100
title: "Comparativa de diseño P0-P6, sugerencias visuales y checklist de cierre del frontend"
author_human: "Diana Aracely Alvarez Varela"
author_agent: "Claude Code / claude-sonnet-5"
date: 2026-09-12
status: draft
tags: [US-641, US-621, REQ-002, DEC-023, DEC-024, ADR-011]
---

# Comparativa de diseño P0-P6, sugerencias visuales y checklist de cierre del frontend

A pedido de Diana (12-sep, tras aprobar el mapa interactivo del Login): continuación de la
auditoría del mismo día, esta vez desde una lente de **experiencia de diseño** -- no de
correctitud de dato, que ya se cerró en la auditoría anterior (ver DevLog "auditoría mockups vs
código"). Compara el storytelling visual completo que entregó el equipo de UX/UI (Juan Macías,
Marina García, Monserrat Miranda, Oscar Quiroz) contra lo que hoy renderiza cada pantalla, y
propone cómo llenar los espacios que hoy se ven más vacíos que el mockup -- sin reabrir ninguna
decisión ya tomada (sin narrativa de "sensores"/vigilancia, sin semáforo de color, sin datos
inventados).

## 0. Hallazgo transversal, antes de ir pantalla por pantalla

Se releyó el HTML real de los 6 mockups de escritorio (`vault/04_UX_Design/FARO_Storytelling_UX/
mockups/01_Entrada.html` a `06_Explorador.html`) para no comparar de memoria. Resultado: buena
parte de la "densidad visual" que se siente al ver el mockup **no viene de iconos ni de fotos**
(cero `<img>` en las 6 pantallas, cero librería de iconos usada de forma consistente) sino de dos
cosas puntuales:

1. **Gradientes y grids de 12 columnas** en el layout (Tailwind `grid-cols-12`, varios
   `gradient-to-*`) -- esto sí es una técnica de maquetación neutra, replicable sin tocar tono ni
   dato.
2. **Un gráfico decorativo de "radar/mapa de vigilancia"**, repetido en P1, P2, P3 y P4: una
   cuadrícula punteada de fondo, un pin o círculo concéntrico, y texto superpuesto con
   coordenadas y conteos **inventados** -- `GEO_COORD: 19.2826° N, 99.6557° W`, `Radio de
   Vigilancia: 1,500m`, `PERÍMETRO 250M`, `TOLUCA (5)` / `NAUCALPAN (2)` (municipios y conteos que
   no salen de ningún dato real), y en el expediente decorativo el mismo CCT de ejemplo
   (`15DJN1794N`) que ya le devolvió a Diana un "No encontrado" esta semana por no existir en el
   set real ni en el mock de demo.

Ese segundo punto **no es solo la narrativa institucional ya rechazada por tono** (aunque el
texto "Radio de Vigilancia" es exactamente esa narrativa) -- es además una infracción del propio
principio que este proyecto exige en todos lados: nunca mostrar un dato sin respaldo real,
`SIN_DATO` explícito en vez de inventar. La razón honesta de por qué las pantallas reales se
sienten "más vacías" en esos huecos no es que falte trabajo de diseño: es que ese hueco específico,
en el mockup, se llena con un dato falso. La alternativa ya existe y ya se construyó hoy mismo: el
mapa del Login (D3 + geojson real de los 32 estados, sin coordenadas inventadas) es el patrón a
repetir -- densidad visual real, no fabricada. Las secciones 1 y 2 de abajo parten de esta
distinción en cada pantalla.

## 1. Comparativa pantalla por pantalla (lente de experiencia de diseño)

### P0 -- Login
Ya resuelto hoy mismo (ver DevLog "Pantalla Login P0" y su segunda/tercera vuelta): panel
dividido, mapa real interactivo de las 4 entidades, tono llano. Es, de las 7 pantallas, la que
más cerca queda del mockup en densidad visual **sin** usar el gráfico de radar inventado --
sirve de referencia para el resto.

### P1 -- Entrada (`Home.jsx`)
El mockup arma la mitad derecha del hero con el radar decorativo descrito arriba
("Capa 01: Territorio Operativo"). `Home.jsx` en cambio deja esa mitad vacía: el hero de hoy es
una sola columna de texto sobre fondo degradado, sin ningún elemento a la derecha. Las 4
`FEATURES` (con emoji) y las 3 tarjetas "01 · Detección / 02 · Síntesis / 03 · Acción" ya cubren
bien la franja inferior -- el hueco real está solo en el hero.

### P2 -- Panorama (`Panorama.jsx`)
El mockup reserva una tarjeta lateral completa para el mismo mini-mapa de radar con
"Convergencia urbana" y "Brecha de telemetría" (datos inventados). La pantalla real hoy es una
sola columna: mensaje agregado, `DriverMatrix` y el CTA -- funcionalmente completa (ya con la
variación de matrícula agregada de la auditoría de hoy), pero visualmente es un solo bloque
angosto en una pantalla ancha; el espacio lateral que el mockup llenaba con el radar, aquí
simplemente no existe todavía.

### P3 -- Los 7 casos (`LosSieteCasos.jsx`)
Esta es de las mejor resueltas: grid de tarjetas (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`),
gauge por escuela, insignia de driver dominante -- visualmente ya es una cuadrícula, no una
lista. Dos huecos puntuales: el botón "Comparar los 7 casos" no tiene acción (no navega ni hace
nada -- posible cabo suelto, ver checklist §4), y el mockup individual de cada tarjeta reserva
espacio para el mismo bloque "GEO_LOCK / PERÍMETRO 250M" con lat/lon inventada que aquí,
correctamente, no se dibujó.

### P4 -- Expediente (`ExpedienteEscuela.jsx`)
La pantalla con más profundidad funcional (5 tabs, todos conectados salvo "Comparación", que
está bloqueado por contrato) pero la que más se aleja del mockup en densidad visual: el mockup
dedica una tarjeta entera al mapa de radar con "GEO_COORD" y "Radio de Vigilancia: 1,500m"
fabricados (el mismo CCT `15DJN1794N` que confundió a Diana). Sin ese bloque, el tab "Resumen"
de hoy queda con una tabla angosta a la izquierda y el gauge a la derecha, dejando visible el
mismo tipo de hueco lateral que P2.

### P5 -- Conclusión (`Conclusion.jsx`)
El mockup de esta pantalla ya no usa el radar decorativo (0 `<svg>`, 0 gradientes) -- su densidad
viene de tipografía y tarjetas en grid de 3/6 columnas. La versión real ya tiene ese mismo
espíritu: barras de Top 2-3 con icono de driver, "Concentración por municipio" en chips. Es la
pantalla que menos se aleja del mockup en este sentido; el único hueco es que "Concentración por
municipio" hoy muestra el código (`Municipio 15104`) en vez del nombre -- ver §4, ya no está
bloqueado por el contrato.

### P6 -- Explorador (`Explorador.jsx`)
Mockup también sin radar decorativo, apoyado en grid de tarjetas. La versión real ya iguala esa
estructura (filtros + grid `sm:grid-cols-2 lg:grid-cols-3`) y de hecho añade algo que el mockup
no tenía: un pop-up de bienvenida a la pantalla. El hueco aquí no es de densidad sino de
alcance: las 4 páginas heredadas ("Vistas heredadas" del Sidebar) siguen sin reconciliarse contra
este Explorador -- ver checklist §4.

## 2. Sugerencias de imágenes / iconos / grids para llenar los espacios vacíos

Ninguna sugerencia de esta sección propone imágenes fotográficas ni un banco de iconos nuevo --
el producto no ha usado fotografía en ningún punto y agregar una ahora sería inconsistente. Todo
lo de abajo reutiliza herramientas que **ya existen en el código** (D3 + geojson real, los emoji
de `driverIcons`, los tokens `--faro-entity-*`) o técnicas de maquetación neutras (grids,
gradiente de fondo), nunca un dato inventado.

- **P1 (Home), hueco del hero:** en vez del radar decorativo, un mapa D3 de las 4 entidades igual
  al del Login pero en miniatura y sin interacción (o con el mismo hover), del lado derecho del
  hero. Reutiliza el componente que ya se construyó hoy -- cero trabajo nuevo de diseño, solo
  extraer `MapaEntidadesLogin` a `components/` para importarlo en ambos lados.
- **P2 (Panorama), columna lateral vacía:** el mismo mini-mapa de entidades (ahora sí interactivo
  tendría sentido: al pasar el cursor por una entidad, atenuar las filas de `DriverMatrix` que no
  son de esa entidad -- ver también la sugerencia de efecto en §3). Si no hay tiempo para eso en
  esta entrega, aunque sea el mapa estático ya cierra el hueco.
- **P3/P4, bloque de mapa por escuela:** ahora que se confirmó que `EscuelaOut`/
  `EscuelaDetalleOut` ya traen `latitud`/`longitud` reales (agregado 11-sep para exactamente
  este uso, ver §4), un mini-mapa de un solo punto real sobre el geojson de la entidad de esa
  escuela es factible y, a diferencia del mockup, sería un dato real -- no una coordenada inventada.
  Esto es más trabajo que las demás sugerencias de esta lista (nuevo componente), por eso se anota
  también en el checklist de §4 como pieza a planear, no a improvisar hoy.
- **Iconos de driver en `DriverMatrix` (P2):** las cabeceras de columna hoy son solo texto
  (`driverNombres`, partido en dos líneas). Agregar el emoji de `driverIcons` (🏘️🚨🏗️📶💧🌫️) antes de
  cada nombre de columna -- el mismo set que ya usan las insignias de P3/P4/P5/P6 -- da
  identidad visual sin inventar nada y hace la matriz más escaneable.
- **Chips de entidad con color propio:** los tokens `--faro-entity-cdmx/edomex/nl/jalisco`
  llevaban desde la fase de diseño sin usarse en ningún componente (se les dio su primer uso hoy
  en el Login). Vale la pena extenderlos a cualquier chip de entidad que aparezca en Explorador o
  en un futuro filtro por entidad, para que el color de cada entidad sea consistente en toda la
  app, no solo en el Login.
- **P5, "Concentración por municipio":** una vez resuelto el nombre real del municipio (§4), cada
  chip puede llevar el color de su entidad (mismo token) en vez de ser todos del mismo gris --
  ayuda a leer de un vistazo si la concentración es de una sola entidad o de varias.

## 3. Sugerencias de efectos y transiciones

Hoy la única transición que existe en todo el frontend es `.lift` (`index.css`, hover con
`transform`+`shadow` de 0.15s) sobre las tarjetas de P3/P6. `RiskGauge` y `DriverBars` dibujan su
valor final de inmediato, sin animación de entrada; no hay ningún fade-in al cambiar de pantalla.
Estas cuatro son honestas de construir sobre lo que ya existe, sin depender de ninguna librería
nueva (todo es CSS o D3, que el proyecto ya usa):

- **Relleno animado de `RiskGauge` y `DriverBars`:** que el arco/las barras crezcan desde 0 hasta
  su valor real en ~500-600ms al montarse (con `transition` de `stroke-dashoffset`/`width`, CSS
  puro) -- hace que P3, P4 y P6 se sientan vivos la primera vez que se ven, sin tocar el dato que
  muestran.
- **Aparición escalonada de las tarjetas en grid** (P3, P6): un `fade-in` + leve desplazamiento
  vertical con `animation-delay` creciente por índice de tarjeta (10-12 tarjetas como máximo, así
  que el costo de mantenimiento es mínimo) -- el mismo efecto que ya insinúa el `.lift` en hover,
  pero al cargar.
- **Extender el hover del mapa del Login** (ya construido hoy) a cualquier futuro mapa de
  entidades (P1/P2 en la sugerencia anterior): reusar exactamente el mismo patrón de
  `fill-opacity` + transición de 180ms, para que el lenguaje de "esto es interactivo" sea el
  mismo en toda la app.
- **Transición de tab en el Expediente (P4):** hoy el cambio entre "Resumen/Drivers/Predicción/…"
  es instantáneo; un fade cruzado corto (150-200ms) entre el contenido saliente y el entrante
  evitaría el salto visual, sobre todo en "Drivers" donde el contenido cambia de tamaño.

## 4. Checklist para dar el frontend por "100%" y presentarlo al equipo

Divido en lo que ya se puede cerrar sin pedirle nada a nadie más, y lo que sí necesita una
respuesta de otra persona del equipo antes de tocarlo.

**Ya accionable por Equipo 5, sin depender de nadie más:**

- Mapa interactivo del Login -- cerrado hoy.
- Icono de driver en las cabeceras de `DriverMatrix` (P2) -- cosmético, sin dependencia de API.
- Fondo de mapa decorativo (sin datos) en el hero de P1 y la columna lateral de P2, reutilizando
  `MapaEntidadesLogin` -- extraerlo a `components/` primero.
- Animaciones de relleno en `RiskGauge`/`DriverBars` y aparición escalonada de tarjetas -- CSS/D3
  puro, sin tocar ningún endpoint.
- Revisar y, si de verdad no lleva a ningún lado, quitar o conectar el botón "Comparar los 7
  casos" de P3 (hoy no tiene `onClick`).
- **Municipio y entidad por nombre real, ya no bloqueado:** al releer `src/api/schemas.py` se
  confirmó que `MunicipioOut` ya expone `nombre_municipio`/`nombre_entidad` desde el 11-sep
  ("US-621, pedido de Diana para el frontend de React") y que `getMunicipio(cveMun)` ya existe en
  `lib/api.js`, pero **nunca se ha usado desde ninguna pantalla** -- ni siquiera se probó. Esto
  deja stale (viejo) el motivo que citan `MapaCasos.jsx` y `ComparacionTerritorial.jsx` para
  seguir "en construcción" ("el contrato aún no expone el nombre de municipio/entidad" -- eso ya
  no es cierto) y también resuelve de una vez la nota de P5 ("cve_mun -- el contrato aún no
  expone el nombre del municipio"). Antes de dar esto por buena hay que probar `getMunicipio` de
  verdad contra el API real (no solo confiar en el schema) y decidir el patrón de llamada: la
  Conclusión (P5) agrupa por `cve_mun` con pocos municipios distintos entre las 7 escuelas -- una
  llamada por municipio único (no por escuela) alcanza.
- `EscuelaOut`/`EscuelaDetalleOut` ya traen `latitud`/`longitud` reales desde el 11-sep (mismo
  motivo, US-621) -- esto es lo que de verdad desbloquea `MapaCasos.jsx`, ya con nombre de
  municipio/entidad disponible también. Vale la pena replantear si esa pantalla se reconstruye
  como tal o si sus 7 puntos se integran al Explorador (P6), que es donde el spec de
  `01_UX_Architecture.md` ya consolidó las 4 páginas heredadas.

**Necesita respuesta de alguien más antes de poder cerrarse (con a quién preguntar):**

- **Serie histórica de matrícula por escuela** (bloqueador real de `Comparativa.jsx`, no
  stale -- confirmado por Christian el 12-sep: `/series` nunca existió). Preguntar a **Christian
  Imanol Ruiz Hurtado** (Tech Lead C4, dueño del contrato del API) si vale la pena un endpoint
  nuevo o si se resuelve con los mismos 2 ciclos derivados que ya se usan en `VistaGeneral.jsx`.
- **Los 6 drivers (d1..d6) de las 7 escuelas en una sola llamada**, para poder construir
  `MatrizDrivers.jsx` sin pagar 7 llamadas individuales. Ya existe `postPrediccionesBatch()` en
  `lib/api.js` apuntando a `/api/v1/predicciones/batch`, pero ese endpoint devuelve
  `driver_dominante` + `recomendacion`, no los 6 valores crudos -- y nunca se ha probado desde
  ninguna pantalla (comentario sin código real detrás). Preguntar a **Christian Ruiz** o a
  **Edgar Edmundo Coronel Navarrete** (revisor habitual de los PRs de contrato) si el batch puede
  extender su respuesta con `d1..d6`, o si el patrón correcto es aceptar las 7 llamadas.
- **Panel de explicación SHAP en P4** (tab "Predicción" hoy solo muestra índice/driver/cluster,
  sin desglose de por qué el modelo llegó a ese resultado): sigue bloqueado porque
  `gold.recomendaciones.shap_d1..d6` está en NULL en producción. Preguntar a **Estefany Lucero
  Hernández Loredo** o a **Héctor Rafael Morales Marbán** (ML) en qué ciclo se espera que ese
  campo empiece a poblarse.
- **Decisión pendiente sobre `VistaGeneral.jsx`** (vista heredada, no la narrativa guiada): las
  KPI cards y el mapa de esa pantalla siguen esperando una decisión de diseño con **Marina García
del Buey** sobre si se quedan, se recortan o se reemplazan por el Explorador -- sin eso, no se
  puede decir si esa pantalla forma parte del "100%" o si se retira del todo.
- **Reconciliación final de rutas heredadas** (`/mapa`, `/drivers`, `/comparacion-territorial`,
  `/comparativa` vs. el Explorador único que pide `01_UX_Architecture.md`): con `MapaCasos.jsx` ya
  desbloqueado por dato (arriba) y `Comparativa.jsx`/`MatrizDrivers.jsx` todavía esperando
  respuesta de Christian/Edgar, conviene una decisión de una sola vez sobre si las 4 se retiran del
  Sidebar cuando el Explorador las cubra, o si se quedan como vistas alternas -- **Oscar Quiroz**
  es el autor del documento de arquitectura que define el Explorador como destino único, buen
  primer punto de contacto.
- **PR #313 de Andrés González<**, sigue esperando revisión de Diana -- no es un hueco de diseño,
  pero cierra un pendiente de proceso antes de decir el frontend "cerrado" para esta entrega.
- **Auditoría de contraste WCAG 2.1 AA** de `03_Visual_Identity.md`: el gate de Marina del 11-sep
  aprobó el diseño con este hueco declarado a propósito (pertenece a `US-651`, no a esta entrega)
  -- no bloquea el 100% de esta fase, pero sí conviene decirlo explícito en la presentación al
  equipo para que nadie lo lea como un olvido.

## Verificación de este documento

Balance de llaves/paréntesis del `Login.jsx` verificado con un script de Python antes de
commitear (el proyecto no tiene `esbuild`/`@babel/core` instalados en este entorno -- `npm i` de
Diana con `node_modules` completo lo verificará mejor con el propio `vite` al correr
`npm run dev`). Todo lo citado de los 6 mockups (`GEO_COORD`, `Radio de Vigilancia`,
`TOLUCA (5)`/`NAUCALPAN (2)`, `15DJN1794N`, `GEO_LOCK`) se confirmó leyendo el HTML real de
`vault/04_UX_Design/FARO_Storytelling_UX/mockups/`, no de memoria. El estado de
`MunicipioOut`/`EscuelaOut` se confirmó releyendo `src/api/schemas.py` línea por línea (no se
confía en el comentario de las pantallas "en construcción", que quedó desactualizado). No se
tocó ningún archivo de código en esta entrega salvo `Login.jsx` (documentado aparte en el commit
`c33956a`).
