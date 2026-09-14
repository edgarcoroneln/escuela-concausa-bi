---
title: "Menú/sesión, auditoría de Marina y mapas reales sin dependencia externa (Ficha Operativa, Selección de Caso, Panorama)"
fecha: 2026-09-14
autor: Diana Aracely Alvarez Varela
herramienta: Claude Code / claude-sonnet-5
relacionado: [US-641, US-621, REQ-002]
---

## Contexto

Sesión con IA sobre `dev/diana-alvarez` pidiendo, en orden: aplicar los hallazgos
críticos/altos/medios de la auditoría UX/UI de Marina García (12 puntos, ya
discutidos en devlogs previos), corregir el menú lateral y un bug real de sesión,
y reemplazar el mapa roto en producción por una alternativa sin dependencia
externa.

## Hallazgo que definió el diseño del mapa

`docker/nginx-frontend.conf.template` (parche `faro_nginx_proxy_US641.patch`,
Luis Téllez, US-641) fija `img-src 'self' data:` y `connect-src 'self'` en el
CSP del proxy. Eso bloquea **cualquier** servicio externo de mapas/tiles
independientemente de si el servicio responde o no -- explica por qué el
iframe original de OpenStreetMap se rompía en producción, y descarta dos de
tres alternativas propuestas sin coordinar el CSP con Luis (C5/DevOps, dueño
de ese archivo). Diana eligió la tercera: un mapa dibujado en el propio SVG
con D3 + `d3-geo`, usando el geojson real de 32 estados que ya usan
`MapaEntidades.jsx`/`SiluetaEntidad.jsx` -- cero dependencia externa, cero
llamada de red nueva.

## Qué se corrigió (menú y sesión)

- `frontend/src/lib/navFases.js`: quita "Iniciar Sesión" (sin ruta real),
  "Expediente de Escuela" (renumera 05→04, 06→05) y "Guía de Identidad"
  (pendiente de implementar) del menú lateral.
- `frontend/src/lib/api.js`: `request()` hacía `await res.json()` en todo
  response "ok" sin distinguir 204 sin cuerpo -- causa real de "el botón de
  Cerrar sesión no funciona" (`POST /auth/logout` responde 204, verificado
  contra `src/api/v1/auth.py`/`src/api/security/cookies.py`, correctos del
  lado backend). Corregido con rama explícita para 204 y `JSON.parse` solo
  si hay cuerpo.
- `frontend/src/pages/Panorama.jsx`: quita el detalle de hex "(colores del
  contorno)" de la leyenda de "dominantes de riesgo".

## Qué se construyó (mapas)

`frontend/src/components/MapaPin.jsx` (nuevo): mapa de la república completa
(mismo geojson, `geoMercator`+`fitSize`) con la(s) entidad(es) resaltadas en
su color de marca y un pin real por punto -- mismo trazo `location_on` de
Material Symbols que ya usa `IconLocationOn` en `Icons.jsx`, no una forma
inventada. API final: `puntos: [{lat, lon, entidadId, color, etiqueta}]`; con
un solo punto recentra la proyección en él, con dos o más conserva el
centrado natural del país.

- **Selección de Caso** (`LosSieteCasos.jsx`): usa `MapaPin` con el punto
  real de la escuela activa (`latitud`/`longitud`), quitó la barra oscura de
  "Lat/Lon" (redundante con el propio mapa).
- **Ficha Operativa** (`ExpedienteEscuela.jsx`): a petición explícita de
  Diana, se revirtió a `SiluetaEntidad.jsx` (silueta de una sola entidad) en
  vez de `MapaPin` -- el mapa nacional queda solo para Selección de Caso.
  Bug de datos aparte, ya corregido: en modo demo `municipioMock.cve_ent` es
  `null` a propósito (para no simular dato real), así que `entidadInfo` caía
  siempre en null; se agregó fallback por nombre de entidad, mismo patrón
  que ya usaba `LosSieteCasos.jsx`.
- **Panorama de Riesgo** (`Panorama.jsx`, "Enclave Georreferenciado"): pedido
  de Diana al notar que el panel mostraba una sola entidad cuando hay dos con
  presencia real entre las escuelas en riesgo. `MapaPin` ahora recibe hasta
  las 2 entidades con más escuelas en riesgo (`entidadesTop`, antes
  `entidadTop` a secas) y pinea ambas en el mismo mapa nacional. **Sin
  cambiar** a propósito: `municipiosTop`, `brechaPct`, `driversConHueco`,
  `celdasEntidadTop`, `cctsEnEntidadTop` siguen calculados solo sobre la
  entidad top-1 -- Diana no pidió extender esas estadísticas, queda como
  decisión suya si también deben cubrir a las dos entidades.

## Verificación

- Balance de `{}`/`[]` verificado línea por línea en cada archivo tocado
  (script de balance corrido a mano); un solo mismatch real encontrado y
  corregido: paréntesis sin cerrar en un comentario `FIX (...)` de
  `MapaPin.jsx`.
- `git diff` completo revisado por archivo antes de cada commit para separar
  hunks de la auditoría de Marina de los de esta sesión.
- **No se corrieron desde este entorno** (sin acceso a los binarios nativos
  ni a `npm`/`pytest` de Diana desde aquí): `npm run lint`, `npm run build`,
  `pytest`. Pendiente que Diana los corra antes de marcar la sección
  "Calidad" de la plantilla del PR.

## Pendientes explícitos para Diana

- Confirmar si el botón real de "Iniciar sesión" en `Header.jsx` (distinto
  del ítem de menú ya retirado) también debe quitarse.
- Decidir si `municipiosTop`/`brechaPct`/demás estadísticas de "Enclave
  Georreferenciado" deben extenderse a las 2 entidades, ya que el mapa ahora
  las muestra a ambas.
- Barra de búsqueda en `Explorador.jsx` (por escuela/alcaldía-municipio/CCT/
  nivel de riesgo): investigado que el backend (`repositorio_gold.py`) no
  trae ese filtro hoy -- Diana pidió dejarla pendiente, no se tocó.
