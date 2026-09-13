---
project: "FARO"
date: "2026-09-12"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1.5h"
touches: ["US-601", "US-621", "REQ-002", "ADR-012"]
tags: [devlog, us-601, componentes, frontend, react, equipo-1]
---

# DevLog — 2026-09-12 — Portación completa de «Cómo funciona» a React, sin dependencias nuevas (US-601)

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

La pantalla de React quedaba con **5 de 8** tipos de bloque; los tres restantes se declaraban como
«pendiente de portar». Ahora están **los ocho**, y el contrato no necesita ninguna dependencia que
el proyecto no tuviera ya. Es lo que hace viable retirar Streamlit conforme a `ADR-012` **sin
perder seis diagramas por el camino**.

| Bloque | Antes | Ahora |
|---|---|---|
| `mermaid` (4 E-R) | requería un motor de diagramas en el cliente | los diagramas se sirven como `svg` desde la API; **ninguna sección emite `mermaid`** |
| `mapa` | D3 dentro del iframe de Streamlit | `MapaScope.jsx`, con `d3-geo` que ya era dependencia |
| `diagrama_flujo` | D3 dentro del iframe de Streamlit | `DiagramaFlujo.jsx`, con `d3-shape` que ya era dependencia |

## La decisión de fondo: dibujar los E-R en el servidor

Servirlos como código mermaid obligaba a que **cada** interfaz trajera un motor de diagramas. En la
SPA eso costaba `chevrotain` → `lodash-es` con dos avisos de severidad **alta**, en la línea 12 y
también en la 11 —no hay versión limpia hoy—, 69 paquetes transitivos y 123 MB. Para cuatro cajas
con flechas.

Dibujarlos aquí una sola vez los convierte en `svg`, el mismo tipo que ya usaba el diagrama de
arquitectura: **cero dependencias de dibujo en cualquier frontend, presente o futuro**, y un solo
lugar donde se editan. `_er_a_svg()` es un generador genérico; los tres diagramas
—Bronze, Silver, Gold— viven como **tablas de datos** (`_ER_*_ENTIDADES`, `_ER_*_RELACIONES`), así
que editarlos es editar datos, no marcado.

**Lo que el dibujo propio conserva y el anterior también decía:** en Bronze las siete relaciones
van punteadas porque **ninguna** está respaldada por una llave foránea —los cruces son posibles, no
obligados—; en Silver esas mismas se vuelven sólidas salvo `aire_estacion`/`agua_region`, que
siguen punteadas porque no son un `JOIN` por llave sino interpolación espacial IDW (`ADR-006`).

**`BloqueMermaid` se conserva en el contrato, no se retira.** El tipo lo diseñó Manuel Serranía y
quitarlo es decisión suya, no un efecto colateral de esta portación; queda anotado en su docstring
que hoy ninguna sección lo emite. Si al revisarlo confirma que no vuelve, retirarlo deja el
contrato honestamente libre de dependencias de dibujo.

## Costo, medido

Se construyó con y sin la pantalla en el mismo árbol, en tres cortes:

| | JS | gzip |
|---|---|---|
| Sin la pantalla | 959.57 kB | 293.78 kB |
| Con 5 tipos portados | 968.67 kB | 296.29 kB |
| **Con los 8** | **982.59 kB** | **300.83 kB** |

**Aporte total: +23.0 kB (+7.1 kB gzip)**, sin una sola dependencia nueva. El aviso de chunk
>500 kB ya existía por d3 + recharts.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Creados:** `frontend/src/components/MapaScope.jsx`,
  `frontend/src/components/DiagramaFlujo.jsx`
- **Modificados:** `src/api/v1/about.py` (generador `_er_a_svg` + los 3 E-R como datos, sustitución
  de los 4 bloques `mermaid`, retiro de `_ER_GOLD_MERMAID` que quedó muerto),
  `frontend/src/components/BloqueAbout.jsx`, `frontend/src/lib/about.js`,
  `tests/test_about_diagrama.py`, `tests/test_api_contract.py`, `api/openapi.v1.json` (regenerado
  con su script)
- **Decisiones autónomas del agente:** dibujar los E-R en el servidor en vez de buscar otra
  librería; escribir un generador genérico con los diagramas como datos; **conservar**
  `BloqueMermaid` en el contrato en vez de retirarlo unilateralmente.
- **Correcciones manuales:** ninguna al código.
- **Prompt inicial:** «prepara para que sea React; si hay dependencias, coméntamelas».

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] **`package.json` y `package-lock.json` idénticos a `HEAD`** — cero dependencias nuevas
- [x] `npm audit --omit=dev` → **0 vulnerabilidades**
- [x] `npx oxlint` limpio en los archivos tocados (los 3 avisos restantes son de archivos ajenos
      preexistentes: `LosSieteCasos.jsx`, `useApiResource.js`, `session.jsx`)
- [x] `ruff check` limpio · `npm run build` correcto
- [x] `pytest tests/ -q` → **1298 passed, 4 skipped** (eran 1285; +13)
- [x] Verificado en vivo: las 6 secciones responden 200 y **ninguna emite ya `mermaid`**

**La suite de geometría se extendió a los tres E-R nuevos** (`tests/test_about_diagrama.py`, 30
casos): cajas sin encimar, todo dentro del `viewBox`, relaciones que apuntan a entidades que
existen, marcado balanceado, sin `<style>`/`<script>` propios, y una prueba de que **los tres
dibujos son distintos entre sí** — la regresión plausible es copiar el generador y olvidar cambiar
los datos.

## Bloqueantes

- **El gate de propiedad reprueba y no se arregla con código.** `frontend/**` es verde de **Diana
  Alvarez** (`DEC-022/023`) y `src/api/**` no está en el alcance de ningún integrante de E1. Se
  sube a la rama propia **para revisión, no para mergear así**.
- Sigue pendiente lo de `DEC-026`, con las tres dependencias del DevLog anterior.

## Próximos pasos

- Revisión de Manuel Serranía y Carlos Mayorga sobre la pantalla ya completa.
- **Decisión de Manuel:** retirar o no `BloqueMermaid` del contrato ahora que nada lo emite.
- Pedir a Edgar el alcance de E1 y el destino de esta pantalla frente a Diana.
- Con los ocho tipos portados, **retirar el shell de Streamlit deja de perder funcionalidad**: la
  decisión es de E5 (`ADR-012`), pero ya no está bloqueada por esta sección.
