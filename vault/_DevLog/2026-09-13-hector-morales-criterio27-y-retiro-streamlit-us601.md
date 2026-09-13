---
project: "FARO"
date: "2026-09-13"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "45m"
touches: ["US-601", "US-621", "REQ-002", "ADR-012"]
tags: [devlog, us-601, componentes, frontend, ux, equipo-1]
---

# DevLog — 2026-09-13 — Criterio 27 (accesos a «Cómo funciona») y retiro de la versión Streamlit

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

Revisión de **Marina García del Buey** (líder E3) sobre el PR #350: visto bueno con **un cambio
obligatorio** y **dos observaciones**. Se validaron los tres antes de aplicar nada.

## 1. Validación de lo que reportó

| Su afirmación | Verificado |
|---|---|
| Solo `App.jsx`, `navFases.js` y `main.jsx` enlazan a `/como-funciona` | ✅ exacto — y ninguno es un enlace de usuario: son la ruta, la compuerta pública y la entrada del rail |
| El criterio 27 pide entrada **desde la entrada y desde el glosario** | ✅ literal, `PLAN_TRABAJO.md:611` |
| El gate reprueba con **21 archivos fuera de alcance** | ✅ exacto |
| «34 archivos tocados, 14 críticos de Diana» | 🟡 eran **40 y 13** al medirlo: la diferencia son commits que entraron después de su revisión (el trabajo de `DEC-026`, que sí es verde propio). Su número que importaba —los 21— estaba bien |
| Los 3 archivos de Streamlit son duplicación (regla 1) | ✅ y son **adiciones nuevas**: 847 líneas que no están en `main`, así que retirarlas es no-agregar, no borrar de `main` |

## 2. El cambio obligatorio: los dos accesos

**Desde la entrada** (`Home.jsx`): un enlace después de los tres pasos —Detección, Síntesis,
Acción—, con peso visual bajo. Va al final a propósito: el criterio pide que **no interrumpa el
recorrido narrativo**, así que acompaña en vez de competir.

**Desde el glosario** (`GlosarioOverlay.jsx`): al cierre del overlay. Marina lo llama el punto más
natural y tiene razón — quien abre el glosario ya está preguntando cómo se calcula algo, así que
el salto de *«qué significa este término»* a *«cómo se produce el dato»* es continuo. Cierra el
overlay al navegar para no dejarlo encima de la pantalla nueva.

## 3. La observación 2 aplicada: fuera la versión Streamlit

Se retiran del PR `src/frontend/about_client.py`, `src/frontend/pages/4_Como_Funciona.py`,
`tests/test_about_client.py`, y se revierte `src/frontend/app.py` al estado de `main`.

**Por qué se aplicó una sugerencia que no bloqueaba:** con la versión React completa, mantener las
dos deja **dos implementaciones vivas del mismo tema**, que es la regla 1 del vault, sobre un shell
que `ADR-012` ya retiró. El trabajo de Manuel Serranía **no se pierde**: la sustancia —el contrato
de bloques y el repositorio, `src/api/v1/about.py` y `repositorio_about.py`— se queda, y la versión
Streamlit sigue en `origin/dev/manuel-serrania` y en la historia.

**Lo que sí se pierde y conviene decirlo:** las **16 pruebas** de `test_about_client.py`, que
cubrían el parseo del cliente de Streamlit. Se verificó antes de quitarlas que el contrato de la
API conserva sus **51**, incluida la cobertura del bloque `svg`: lo que deja de probarse es código
que deja de existir, no una superficie sin guarda. `tests/fixtures_about.py` **se queda** — lo usan
`test_api_contract.py` y `src/api/repositorio_about.py`.

## 4. El efecto real en el gate, medido

Marina esperaba que retirar Streamlit aliviara el pedido de alcance. Lo hace, pero **menos de lo
que parece**, porque su propio cambio obligatorio empuja en sentido contrario:

| | Antes | Después |
|---|---|---|
| Archivos tocados | 40 | 38 |
| Fuera de alcance | 21 | **20** |
| Críticos de Diana | 13 | **12** |

**−3 por retirar Streamlit, +2 por los accesos nuevos** (`Home.jsx` y `GlosarioOverlay.jsx` también
son verde de Diana) **= −1 neto**. Sin los accesos habrían sido 10 críticos, pero el criterio 27 es
obligatorio y la accesibilidad de la superficie pesa más que un archivo menos en el pedido.

**La observación 1 sigue en pie sin cambios**: el gate reprueba y no se arregla con contenido.
Hacen falta Edgar (ampliar el alcance de E1) o Diana (llevar `frontend/**` en su rama).

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Modificados:** `frontend/src/pages/Home.jsx`, `frontend/src/components/GlosarioOverlay.jsx`,
  `src/frontend/app.py` (revertido a `main`)
- **Eliminados:** `src/frontend/about_client.py`, `src/frontend/pages/4_Como_Funciona.py`,
  `tests/test_about_client.py`
- **Decisiones autónomas del agente:** colocar el enlace de la entrada **después** de los tres
  pasos y con peso bajo, para no competir con el recorrido; cerrar el overlay al navegar desde el
  glosario.
- **Correcciones manuales:** ninguna.
- **Prompt inicial:** nota de revisión de Marina García.

## Seguridad / calidad

- [x] `pytest tests/ -q` → **1298 passed, 10 skipped** (eran 1314; −16, exactamente las de
      `test_about_client.py`)
- [x] `ruff` limpio · `npm run build` correcto (674.27 kB)
- [x] `oxlint`: el único aviso en `Home.jsx` es **preexistente** (línea 56, el `setState` del
      walkthrough) — verificado comparando contra `main`; no lo introduce este cambio
- [x] Sin dependencias nuevas

## Bloqueantes

- **El gate de propiedad**, sin cambio: 20 archivos fuera de alcance, 12 críticos de Diana.
  Pendiente de Edgar desde el 11-sep.

## Próximos pasos

- Que Marina confirme los dos accesos contra su criterio 27.
- Que Manuel confirme el retiro de su versión Streamlit — se aplicó por regla 1 y por
  recomendación de la líder de E3, pero es su código y revierte con un solo commit.
- Marina actualiza de su lado al mergear: la fila S de `03_Visual_Identity` pasa a entregada y la
  §5.bis marca resuelto el punto 2 de los iframes.
