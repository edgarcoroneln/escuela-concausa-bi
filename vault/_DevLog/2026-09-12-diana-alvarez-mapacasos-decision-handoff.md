---
project: "FARO"
date: "2026-09-12"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión -- último ítem del checklist de cierre antes de la junta de las 18:00, inmediatamente después de conectar ComparacionTerritorial.jsx."
touches: ["US-621", "REQ-002", "ADR-011"]
tags: [devlog, equipo-5, frontend, react, decision]
---

# DevLog — 2026-09-12 — MapaCasos conectado: la decisión de handoff del mapa, resuelta

→ [[vault/_DevLog/_index|Volver al índice]]

## Contexto -- esto no era solo conectar datos

Antes de tocar código se encontró que `MapaCasos.jsx` no era un simple "pendiente de conectar": es
la fila **"Mapa de ubicación"** de `02_Data_Visualization_Spec.md` §8.1, ampliada en
`PLAN_TRABAJO.md` §10.sexies, y ambas dicen lo mismo de forma explícita: la mitad técnica de la razón
para no construirlo -- *"la API no expone geometría"* -- cayó el 11-sep (`latitud`/`longitud` reales
en `EscuelaOut`, base cartográfica de `d3-geo` ya en el front), pero la otra mitad seguía en pie --
*"dónde" no responde "qué situación"*, y unos puntos sobre el contorno de un par de estados no
distinguen nada por sí solos. El propio documento dice, textual: **"Decisión pendiente en el handoff
con el Equipo 5 (Diana Álvarez), no aquí"** -- si el mapa se queda, `ADR-011` §4 exige que el riesgo
se pueda leer sin él.

Esta entrega **es** ese handoff, resuelto por Diana hoy: se construye el mapa (la base cartográfica y
el componente D3 ya existían, sin usar con datos reales) y se satisface la condición de `ADR-011` §4
agregando una tabla de texto plano con las 7 escuelas y su nivel de riesgo, independiente del mapa.

## Qué se construyó

**`pages/MapaCasos.jsx` (reescrita por completo, antes `EnConstruccion`):** conecta
`getEscuelasEnRiesgo()` (ya trae `latitud`/`longitud` reales desde US-621, sin llamada adicional) al
componente `MapaRiesgo.jsx`/`MapaRiesgoCard` que **ya existía en el repo** -- se construyó junto con
`VistaGeneral.jsx` (pantalla heredada de una fase anterior) pero solo se había usado con datos mock,
nunca conectado a una pantalla real ni usado aquí. Selección de escuela sincronizada entre el mapa
(clic en un punto) y una tabla nueva debajo (clic en una fila) -- ambas controlan el mismo estado
`selectedCct`. Un panel "Escuela seleccionada" muestra nombre, nivel, matrícula (real), nivel de
atención (mismo `nivelRiesgo()`/cortes que el resto de pantallas) y el driver dominante, con link al
expediente completo.

**Tabla accesible (nueva, es la pieza que resuelve `ADR-011` §4):** las 7 escuelas con Escuela /
Nivel / Riesgo (ícono + etiqueta, sin depender del mapa) / Driver dominante / si aparece o no en el
mapa -- el riesgo de cada escuela se puede leer completo sin mirar el mapa ni un solo pixel de él.

**SIN_DATO real:** una escuela sin `latitud`/`longitud` (el contrato ya lo declara `None` explícito,
no `(0,0)`) se omite del mapa -- `MapaRiesgo.jsx` ya filtraba esto -- pero sigue apareciendo en la
tabla con su riesgo y una nota "Sin georreferencia -- no aparece como punto en el mapa". Con las 7
escuelas de este ciclo esto no aplica hoy (todas georreferenciadas), pero la pantalla no asume que
siempre será así.

## Validación

- Balance de paréntesis/llaves/corchetes verificado por script.
- Balance de etiquetas JSX verificado por script (con `re.DOTALL` para las etiquetas que abren
  atributos en varias líneas, como `<MapaRiesgoCard ... />`).
- `python vault/_Meta/scripts/vault_lint.py .` → Vault limpio.
- `git diff --check` → sin problemas de espacios en blanco.
- Sin cambios en `lib/api.js` ni en ningún otro archivo -- `getEscuelasEnRiesgo()` ya traía todo lo
  necesario.
- **Pendiente de Diana:** `npm run dev` real para verificar la interacción mapa↔tabla y el
  comportamiento con `VITE_USE_MOCK=true` (el mock de `data/mock.js` ya trae `latitud`/`longitud` de
  ejemplo, así que el modo demo también debería pintar el mapa).
