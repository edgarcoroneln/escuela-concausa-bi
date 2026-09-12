---
project: "FARO"
date: "2026-09-12"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — arranque del rediseño Fase 2 (US-641) contra las 7 plantillas de UX/UI liberadas por Equipo 3: shell persistente (Sidebar + Header + Asistente FARO flotante) y la Pantalla 1 (Entrada), primera de 7 en revisión pantalla por pantalla."
touches: ["US-641", "US-621", "US-305", "DEC-023", "DEC-024", "DEC-026", "BUG-058"]
tags: [devlog, equipo-5, frontend, react, rediseño, ux-ui]
---

# DevLog — 2026-09-12 — Rediseño Fase 2 (US-641): shell persistente + Pantalla 1 (US-641)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/04_UX_Design/FARO_Storytelling_UX/01_UX_Architecture|01_UX_Architecture]]

## Contexto

Diana pidió cerrar el rediseño de frontend contra las 7 plantillas de UX/UI que Equipo 3 liberó para
Equipo 5 (`dd282fd`, `vault/04_UX_Design/FARO_Storytelling_UX/mockups/0[0-6]_*.html`), alcance completo
(las 7 pantallas) con revisión pantalla por pantalla: se construye una, Diana la revisa con su propio
`npm run dev`, y solo entonces se avanza a la siguiente. Esta entrega es la primera pantalla: la 01
(Entrada) más el shell de layout que las 6 pantallas autenticadas comparten.

**Antes de escribir código** se leyeron completos: `frontend/src/index.css` (el sistema de tokens
`--faro-*`, ya implementado en Fase 1, PR #310), `Design_Tokens_Stitch.md` (identidad y especificación
del nodo flotante Asistente FARO) y `01_UX_Architecture.md` completo (mapa de navegación, ficha de las
7 pantallas, filtros, walkthrough, pop-up del explorador, comportamiento del Asistente FARO, nombre de
"Explorador de escuelas" y los estados vacíos/error/SIN_DATO). Después se abrieron las 6 plantillas
HTML autenticadas: **el mismo `<aside>` de navegación aparece idéntico en las 6** (`00_Login.html` no
lo tiene) — confirmado por diff de estructura, no es un navegador de prototipo de Stitch, es chrome
persistente real del producto.

## Qué se construyó

**Shell persistente** (`App.jsx` reescrito, 3 componentes nuevos):

- `components/Sidebar.jsx` -- rail izquierdo fijo (`--faro-sidebar-expanded`, 17.5rem), con las 6 fases
  del recorrido guiado + "Explorador de escuelas" como sección de exploración libre, más una sección
  "Vistas heredadas" que lista las 5 páginas actuales que todavía no caen dentro de una de las 6 fases
  (Mapa, Drivers, Comparación territorial, Comparativa, Hallazgos) -- **a propósito, para no dejar a
  nadie del equipo sin acceso a ellas mientras se migra pantalla por pantalla.** Ver el mapeo completo
  de fase→ruta (con su justificación) en `lib/navFases.js`.
- `components/Header.jsx` -- reemplaza a `Topbar.jsx` (eliminado, único punto que lo importaba era
  `App.jsx`): breadcrumb "FARO / <pantalla>" + sesión (mismo `getAuthLoginUrl()`/`useSession()` que ya
  existía, sin tocar auth).
- `components/AsistenteFaro.jsx` -- nodo flotante inferior-derecho (Design_Tokens_Stitch.md), montado
  una sola vez en `App.jsx` para que la conversación sobreviva la navegación entre pantallas (§6).
  Conecta al cliente SSE ya construido (`postAgenteConsultaStream`, mergeado a `main` el 12-sep): los 3
  mensajes de error son literales del spec (fuera de alcance / sin datos / timeout), el SQL generado
  nunca se muestra por defecto (corrige el patrón de `src/frontend/pages/3_Chat.py:85-87`, queda detrás
  de "Ver la consulta"), y el input se deshabilita mientras streamea.
- `components/GlosarioOverlay.jsx` -- términos reales del sistema (SIN_DATO, índice de riesgo, nivel de
  atención, driver dominante, completitud de evidencia). El nivel de atención lee sus cortes de
  `useCortesAtencion()` (el mismo hook de la entrega anterior) en vez de escribir `0.50`/`0.30`.
- `components/WalkthroughOverlay.jsx` -- las 3 líneas literales de §4, primera visita automática
  (`localStorage`, se documenta el límite de esto en navegador compartido), accesible después vía "¿".

**Pantalla 1 (`pages/Home.jsx`, reescrita completa):**

Contra la ficha de §2 "Pantalla 1", no contra la copy de las plantillas Stitch (esas narran una
mitología de "sensores"/"telemetría" que no está en el PRD ni en el spec aprobado -- se dejó fuera a
propósito, junto con el badge falso "TELEMETRÍA EN VIVO" del mockup, porque los datos son ETL
periódico, no tiempo real). **Corrección real encontrada:** el `Home.jsx` de Fase 1 revelaba
`escuelas_en_riesgo` en el hero (`tituloHero()`, PR #302) -- el spec es explícito en que **P1 nunca
revela el conteo de casos, eso le toca a P2 (Panorama)**. La pantalla nueva ya no llama a `getKpis()`
ni muestra ningún número agregado; es estática, sin carga ni error (como pide §2).

## Pendiente (sin tocar en esta sesión, explícito)

- **Pantallas 2 a 6** -- construcción pantalla por pantalla, siguiente turno tras la revisión visual de
  Diana sobre esta entrega.
- **Sidebar sin colapso en móvil** -- el token `--faro-sidebar-collapsed` (4.5rem) ya existe en
  `index.css` para esto, pero el rail queda fijo a 17.5rem en cualquier ancho por ahora; no se construyó
  el breakpoint de 8/4 columnas de `Design_Tokens_Stitch.md`.
- **"Cómo funciona"** -- no se dibuja (ni el enlace discreto de P1 ni el ítem del sidebar) porque su
  contenido depende de `dev/manuel-serrania`, que sigue sin llegar a `main`; el propio spec dice que
  mientras no aterrice "se declara como recorte, no se dibuja" (§1).
- Los 3 pendientes ya documentados en el DevLog anterior (KPI cards de `VistaGeneral.jsx`, el mapa
  pendiente de Marina, PR #313 sin revisión de Diana) siguen igual, sin tocar.

## Validación

- `python vault/_Meta/scripts/vault_lint.py .` → Vault limpio.
- Balance de llaves/paréntesis verificado por script en los 8 archivos nuevos/modificados; sin
  `node --check` posible en `.jsx` desde este entorno (mismo límite ya documentado) ni binarios nativos
  de `oxlint`/`rolldown` disponibles (compilados para otra arquitectura) -- verificación visual real
  queda en manos de Diana con `npm run dev`, como acordamos para esta entrega pantalla por pantalla.
