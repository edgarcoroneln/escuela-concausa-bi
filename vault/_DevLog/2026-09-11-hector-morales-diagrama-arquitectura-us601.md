---
project: "FARO"
date: "2026-09-11"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "2h"
touches: ["US-601", "REQ-001", "REQ-007"]
tags: [devlog, us-601, componentes, equipo-1]
---

# DevLog — 2026-09-11 — Diagrama de arquitectura y fusión de Memoria Técnica (US-601)

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

Dos cambios sobre la sección «Cómo funciona» que construyó Manuel Serranía
([[vault/03_Architecture/Bosquejo_Componentes_US601|Bosquejo_Componentes_US601]]), pedidos tras
revisarla en local:

1. **Un diagrama de flujo de la arquitectura** en la sección `arquitectura`, que hasta ahora era
   solo dos tablas. Muestra los 10 componentes, quién es dueño de cada uno y por dónde viaja el
   dato entre ellos.
2. **`stack` («Memoria técnica») deja de ser sección propia** y su tabla por capa se funde al
   final de `arquitectura`. Quedan **6 secciones**, renumeradas.

## Decisiones y por qué

**El color codifica la célula dueña, no la etapa del flujo.** La propia sección afirma que el
backend se construyó como *«5 franjas verticales»*; el diagrama lo enseña en vez de repetirlo. Los
tres primeros colores son los que ya usa el diagrama de cubos (`_flujo_html`); C3/C4/C5 extienden
la misma familia. Las capas dentro de PostgreSQL reusan los colores de las barras de `capas`, para
que bronze/silver/gold se lean como la misma cosa en las dos secciones.

**Tipo de bloque nuevo `svg`, el octavo — y es el único que no manda datos.** Los otros siete
mandan datos y el frontend dibuja. Aquí no: la disposición es una decisión editorial (por dónde
rodea una flecha para no cruzar una caja, cuáles llevan borde grueso), no un resultado de los
datos. Mandar nodos y aristas obligaría a escribir un motor de layout en el cliente para
reproducir una colocación que de todas formas se fijó a mano, y cualquier reacomodo automático
volvería a cruzar las cajas que este trazo evita a propósito. **Mitigación:** el SVG se genera
desde tablas de datos (`_ARQ_COMPONENTES`, `_ARQ_FLECHAS`), así que editar el diagrama es editar
datos, no marcado. Degrada por `BloqueDesconocido` como el resto del contrato.

**Por qué la Memoria Técnica no se quedó sola.** Su contenido son las mismas piezas de la tabla de
componentes, vistas por capa en vez de por dueño. Como sección aparte eran dos bloques sin
contexto; fundida, entra con un encabezado que dice exactamente eso, y el lector ya tiene arriba a
qué componente corresponde cada herramienta.

**`alt` viaja aparte del marcado.** El `aria-label` de un `<svg>` dentro de `components.html` no
llega al lector de pantalla del documento padre (el iframe es otro documento), así que la página
repite la descripción fuera, en un expander.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Archivos creados/modificados:**
  - `src/api/v1/about.py` — `BloqueSvg`, `_diagrama_arquitectura()`, fusión de `stack`, registro
  - `src/frontend/about_client.py` — dataclass y parseo de `svg`
  - `src/frontend/pages/4_Como_Funciona.py` — `_svg_html()` y su rama del dispatcher
  - `tests/test_about_diagrama.py` — **nuevo**, geometría del diagrama
  - `tests/test_api_contract.py`, `tests/test_about_client.py` — contrato del bloque y de la fusión
  - `api/openapi.v1.json` — regenerado con `scripts/export_openapi.py`, no editado a mano
- **Decisiones autónomas del agente:** proponer `svg` como tipo de bloque en vez de forzar el
  diagrama a `diagrama_flujo`; generar el SVG desde tablas de datos; escribir la suite de
  geometría; sacar `alt` del marcado.
- **Correcciones manuales:** ninguna al código. La verificación de geometría **encontró tres
  etiquetas encimadas** en la primera versión del trazo (`features_escuela` sobre la caja de
  scikit-learn, `predicciones` sobre la de PostgreSQL, `contexto RAG` sobre la de ChromaDB); se
  reubicaron las tres y la prueba quedó como regresión.
- **Prompt inicial:** integrar a la sección el diagrama que se había hecho como HTML
  independiente, y fundir en ella la Memoria Técnica.

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] Tests agregados/actualizados — `tests/test_about_diagrama.py` + casos en
      `test_api_contract.py` y `test_about_client.py`
- [x] DevLog enlaza a los IDs afectados

**Verificación corrida, no supuesta:**

| Comprobación | Resultado |
|---|---|
| `pytest tests/test_api_contract.py tests/test_about_client.py tests/test_about_diagrama.py -q` | 78 passed (eran 54) |
| `pytest tests/ -q` | **1276 passed, 4 skipped** |
| `ruff check` sobre los 6 archivos tocados | limpio |
| Las 6 secciones contra la API local | HTTP 200, `orden` 1..6 sin huecos |
| `GET /about/secciones/stack` | **404**, como debe ser tras la fusión |
| La API con la base **inalcanzable** | 200 en las 6 secciones; `capas` degrada a `SIN_DATO` con su nota |

**Sobre la suite de geometría.** Existe porque este defecto no lo caza ninguna prueba de contrato:
el JSON sale válido y el SVG renderiza sin error, simplemente queda texto sobre texto. Afirma una
propiedad del trazo, no el trazo — mover una caja está permitido, dejarla encima de una etiqueta
no. Cubre: etiqueta sobre caja, cajas encimadas entre sí, todo dentro del `viewBox`, células
declaradas válidas, marcado balanceado, y que el SVG no traiga `<style>`/`<script>`/`<foreignObject>`
propios.

**No verificado por el agente:** el aspecto visual en el navegador (sin herramienta de captura en
esta sesión). Queda a revisión de Manuel Serranía y Carlos Mayorga en su local.

## Bloqueantes

- **El gate de propiedad reprueba, y no se arregla con código.** Este trabajo toca `src/api/**` y
  `src/frontend/**`, que **no están en el verde ni el amarillo de ningún integrante de E1** —
  `ownership.yml` conserva para los tres los alcances de sus células anteriores (ML para Héctor y
  Carlos, BI para Manuel). Es el mismo bloqueo que ya traía `dev/manuel-serrania`. Requiere que
  Edgar Coronel amplíe el alcance de E1 o firme la excepción; se reporta, no se evade.
  `src/frontend/**` es además verde de **Diana Alvarez**, así que su revisión es necesaria por la
  regla 7.

## Próximos pasos

- Revisión de Manuel Serranía y Carlos Mayorga en local (receta corta: no necesita Docker; la
  sección responde igual con la base apagada, solo `capas` sale en `SIN_DATO`).
- Pedir a Edgar la resolución del alcance de E1 antes de abrir el PR.
- Pendiente de Manuel, sin relación con este cambio: `dev/manuel-serrania` arrastra 7 archivos
  ajenos a US-601 del merge de `componentes-back` (`.claude/settings.json`, `gx/**`, y tres `.md`
  sueltos en la raíz que `vault_lint` marca como bloqueantes).
