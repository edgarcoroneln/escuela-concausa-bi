---
project: "FARO"
date: "2026-09-12"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión -- primer ítem accionable del checklist de cierre (comparativa-diseno-y-checklist-100), interrumpida por la revisión de BUG-077 pedida por Edgar (documentada aparte)."
touches: ["US-621", "REQ-002", "BUG-077"]
tags: [devlog, equipo-5, frontend, react]
---

# DevLog — 2026-09-12 — Municipio y entidad por nombre real: ComparacionTerritorial conectada al API

→ [[vault/_DevLog/_index|Volver al índice]]

## Contexto

Del checklist para dar el frontend por "100%" (`2026-09-12-diana-alvarez-comparativa-diseno-y-checklist-100.md`,
§4), Diana eligió como siguiente ítem accionable "Municipio y entidad por nombre real": `MunicipioOut`
expone `nombre_municipio`/`nombre_entidad` desde el 11-sep (US-621) pero nadie lo había probado desde
ninguna pantalla, y `getMunicipio(cveMun)` existía en `lib/api.js` sin usarse. Alcance decidido por
Diana: API + `ComparacionTerritorial.jsx` completo, sin construir todavía el mapa visual de
`MapaCasos.jsx`.

Antes de dar esto por bueno se probó `getMunicipio` de verdad contra el API real corriendo en Docker
(no solo el schema) -- esa verificación quedó documentada como parte del cierre de datos de `BUG-077`
(municipios/14113 → `cve_ent: "14"`, `nombre_entidad: "Jalisco"`; 317/317 municipios con
`nombre_entidad` no nulo tras el fix de `dbt`). Sin ese fix, la mitad de los municipios reales seguía
llegando con `nombre_entidad` nulo o el endpoint fallando con 500 -- este trabajo dependía de él.

## Qué se construyó

**`lib/api.js`:** `getMunicipiosPorClaves(cveMuns)` -- una llamada por municipio **único**, no por
escuela (las 7 escuelas en riesgo suelen repetir municipio; deduplicar `cve_mun` antes de llamar evita
llamadas redundantes), componiendo `getMunicipio()` ya existente con `Promise.all`. `getComparacionTerritorial()`
-- compone `getEscuelasEnRiesgo()` + `getMunicipiosPorClaves()`, mismo estilo de composición que
`getPanoramaEscuelas()` (P2), y agrega `nombre_municipio`/`nombre_entidad` a cada escuela.

**`pages/ComparacionTerritorial.jsx` (reescrita por completo, antes `EnConstruccion`):** responde
"¿es un caso aislado?" con lo que el dato real permite responder de forma honesta -- si dos o más de
las 7 escuelas en riesgo comparten municipio -- sin inventar un cálculo de "escuelas similares" que
no existe en ningún endpoint. Usa `useApiResource(getComparacionTerritorial, {mock: escuelasMock})` y
el mismo patrón de 3 estados de `useCortesAtencion()` ya establecido en `ExpedienteEscuela.jsx`/
`LosSieteCasos.jsx` (revisión de Edgar, PR #325): loading / error-o-cortes-ausentes visible / ok.
Normaliza nombre real (API) vs. mock (`municipio`/`entidad` ya vienen como texto en `data/mock.js`).
Dos tarjetas: "Municipios con más de un caso" (agrupación por `cve_mun`+`cve_ent`) y la tabla completa
de las 7 escuelas con Escuela/Nivel/Municipio/Entidad/Riesgo, cada fila enlazando al expediente
(`/escuela/:cct`).

## Fuera de alcance de esta entrega (por decisión explícita de Diana)

- `MapaCasos.jsx` (mapa visual D3 con las coordenadas reales) -- sigue como `EnConstruccion`, con su
  comentario desactualizado citando la revisión de Edgar de PR #302; queda pendiente para una entrega
  aparte.
- No se tocó `LosSieteCasos.jsx`, que también menciona el mismo gap de contrato en un comentario
  propio -- podría revisarse después dado que hoy quedó desbloqueado, pero no fue parte de lo pedido.

## Validación

- Balance de paréntesis/llaves/corchetes verificado por script en los dos archivos modificados.
- Balance de etiquetas JSX (apertura/cierre por nombre de componente) verificado por script en
  `ComparacionTerritorial.jsx`.
- `node --check frontend/src/lib/api.js` → sin errores de sintaxis (archivo sin JSX).
- `python vault/_Meta/scripts/vault_lint.py .` → Vault limpio.
- `git diff --check` sobre ambos archivos → sin problemas de espacios en blanco.
- **Pendiente de Diana:** `npm run dev` real para verificación visual -- no ejecutable desde este
  entorno. `ComparacionTerritorial.jsx` no puede verificarse con `node --check` (JSX) ni con
  `npx vite build` (mismo límite de binario nativo de `rolldown` ya documentado en entregas previas).
