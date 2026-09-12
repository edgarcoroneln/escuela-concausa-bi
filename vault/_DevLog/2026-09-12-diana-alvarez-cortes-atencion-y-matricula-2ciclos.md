---
project: "FARO"
date: "2026-09-12"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — resincronización de dev/diana-alvarez con main tras el merge de PR #322, corrección de umbrales de nivel de atención hardcodeados (hallazgo propio de Diana), y comparación de 2 ciclos de matrícula (respuesta de Christian a pregunta de Diana sobre la serie histórica)."
touches: ["US-621", "US-305", "REQ-002", "REQ-006", "DEC-026", "BUG-058"]
tags: [devlog, equipo-5, frontend, react, umbrales, matricula]
---

# DevLog — 2026-09-12 — Cortes de atención desde `/version` y comparación de matrícula (US-621)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/API_Specification|API_Specification]]

## Contexto

Al ponerse al día con el equipo (mensajes de Edgar, Marina, Christian y Andrés del 11/12-sep), Diana
encontró un conflicto de merge commiteado sin resolver en `Traceability_Matrix.md` (marcadores
`<<<<<<<`/`=======`/`>>>>>>>` reales, líneas 887-893) dentro del merge `8292328` que Edgar hizo sobre
`dev/diana-alvarez` — mismo patrón que el incidente ya documentado en la fila `REQ-007` de ese mismo
archivo. Se resolvió con el script que Edgar compartió, conservando la fila más reciente de HEAD y la
fila extra de `origin/main` (gate de Marina/Juan sobre contraste, `US-621`/`ADR-011`).

Al resincronizar con `origin/main` una segunda vez (varios PRs mergeados el mismo día: #333-#337),
se confirmó que `DEC-026`/`cortes_atencion` en `GET /api/v1/version` ya está en `main` — el mensaje
de Diana al equipo ("no escribas 0.50 ni 0.30 en el front") era correcto, solo faltaba este sync.

## Qué se encontró y se corrigió

**El frontend de React tenía exactamente el error que Diana le señaló al equipo.** `nivelRiesgo()`
(`frontend/src/data/mock.js`) y `LINEA_ALERTA_RIESGO` (`frontend/src/lib/api.js`) escribían `0.5`/`0.3`
directo en el código — mismo patrón que ya causó `BUG-058` (diccionario de entidades hardcodeado).
Corregido:

- `getVersion()` nuevo en `api.js` (público, sin login).
- `lib/cortesAtencion.js` (nuevo): hook `useCortesAtencion()` que lee `cortes_atencion` de `/version`,
  con mock explícito de `DEC-024` (`alta=0.50`, `media=0.30`) solo para modo demo.
- `nivelRiesgo(indice, cortes)` ya no tiene los cortes fijos — los recibe como parámetro.
  `LosSieteCasos.jsx` y `ExpedienteEscuela.jsx` los leen del hook antes de renderizar.
- `getEscuelasEnRiesgo()` usa `cortes_atencion.alta` del API real en vez de la constante local.

**Comparación de 2 ciclos de matrícula (pregunta de Diana a Christian sobre la serie histórica).**
Su respuesta: `/series` no existe y nunca existió (`US-411` lo descartó fuera de alcance), y
`fact_escuela_ciclo` solo materializa 2 ciclos — no hay una tendencia real de 3+ puntos que graficar.
Se implementó como comparación de 2 puntos en `VistaGeneral.jsx`, derivada del contrato ya publicado
en `KpisOut` sin pedir un endpoint nuevo: `anterior = matricula_total / (1 + variacion_matricula)`
— ambos números ya son la fuente de verdad del backend, solo se despejan. Reemplaza el mock de 3
ciclos (`matriculaPorCiclo`, que ya no se usa) por datos reales cuando el API responde, con
`DemoBadge` condicional (antes se mostraba siempre, sin importar el modo).

## Ajuste de revisión (PR #325, Edgar, 12-sep)

Segunda vuelta de revisión de Edgar sobre este mismo PR: `useCortesAtencion()` devuelve
`{ status, cortes, error }`, pero `ExpedienteEscuela.jsx` y `LosSieteCasos.jsx` solo desestructuraban
`cortes` y lo trataban igual que "cargando" cuando no llegaba. Si `/version` fallaba (o respondía sin
`cortes_atencion`), `ExpedienteEscuela` se quedaba pegado en "Cargando expediente..." para siempre
(la condición era `status === "loading" || !cortes`, y `!cortes` nunca se volvía falso) y
`LosSieteCasos` simplemente no dibujaba la grilla (`escuelas.length > 0 && cortes`) sin decir por
qué. Corregido en ambos archivos: ahora se leen también `status` (como `cortesStatus`) y `error`
(como `cortesError`) del hook, y se distinguen los 3 estados que pedía Edgar -- loading (indicador de
carga), error o cortes ausentes (mensaje visible explicando que no se pudieron cargar los cortes de
`/version`, sin bloquear el resto de la pantalla ya cargado) y ok/demo (render normal). Limpieza
menor pedida en el mismo comentario: se quitó la variable `color` sin usar en `LosSieteCasos.jsx`
(y el import de `riskRampColor` que solo esa variable consumía) y la línea en blanco sobrante al
final de `vault/_DevLog/_index.md`.

## Pendiente (sin tocar en esta sesión)

- **KPI cards de `VistaGeneral.jsx`** (`kpis` de `mock.js`) siguen sin conectar al API real y muestran
  "Índice de riesgo promedio", el mismo campo que ya se corrigió en `Home.jsx` (PR #302, Edgar) por no
  existir en `KpisOut` — no se tocó aquí porque es una decisión de qué mostrar en su lugar, no un fix
  mecánico como los de arriba.
- **Mapa de `VistaGeneral.jsx`** (`MapaRiesgoCard` con `escuelasEnRiesgo` mock) sigue sin conectar --
  depende de la decisión pendiente con Marina García sobre si el mapa se queda o se recorta (mensaje
  enviado 12-sep, respuesta pendiente antes del freeze).
- **PR #313** (Andrés González, `src/frontend/agente_client.py`) ya se mergeó a `main` tocando ruta
  crítica de Diana sin su aprobación explícita registrada (su propio DevLog lo señala) -- pendiente de
  que ella lo revise post-merge.

## Validación

- `python vault/_Meta/scripts/vault_lint.py .` → Vault limpio.
- `pytest tests/ -q` → 1204 passed, 4 skipped (corrido por Diana antes del primer push de este día).
- Revisión manual de los 6 archivos modificados (diffs completos), sin `node --check` posible en
  `.jsx` desde este entorno -- verificado por inspección línea por línea en su lugar.
