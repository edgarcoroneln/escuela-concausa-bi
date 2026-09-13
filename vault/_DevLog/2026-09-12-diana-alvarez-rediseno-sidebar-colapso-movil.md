---
project: "FARO"
date: "2026-09-12"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión -- pendiente puntual del rediseño Fase 2 (US-641): colapso del sidebar en móvil."
touches: ["US-641", "US-621"]
tags: [devlog, equipo-5, frontend, react, rediseño, ux-ui, responsive]
---

# DevLog — 2026-09-12 — Rediseño Fase 2 (US-641): sidebar sin colapso en móvil, resuelto

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/04_UX_Design/FARO_Storytelling_UX/mockups/Design_Tokens_Stitch|Design_Tokens_Stitch]]

## Contexto

Pendiente explícito desde el DevLog de shell + Pantalla 1 (12-sep): el rail de navegación
(`Sidebar.jsx`) quedaba fijo a `--faro-sidebar-expanded` (17.5rem) en cualquier ancho de pantalla,
aunque el token `--faro-sidebar-collapsed` (4.5rem) ya existía en `index.css` desde la Fase 1.

Ningún mockup de Stitch (`00`–`06_*.html`) define una navegación móvil distinta -- los 7 son
capturas de escritorio, sin clases `md:`/`sm:` en su `<aside>`. La única referencia escrita es la de
`Design_Tokens_Stitch.md` §"Breakpoints & Responsive Behavior": *"Mobile (< 768px): ... collapsed
analytical controls"*. Se tomó la interpretación más conservadora del token ya diseñado: el rail no
desaparece ni se convierte en un drawer nuevo, se angosta al ancho colapsado y sus etiquetas de
texto se ocultan -- mismo patrón que un rail de iconos convencional, sin inventar una pantalla que
nadie maquetó.

## Qué se construyó

- **`index.css`:** variable nueva `--faro-sidebar-width` (por defecto `var(--faro-sidebar-expanded)`),
  redefinida a `var(--faro-sidebar-collapsed)` dentro de `@media (max-width: 767px)` -- coincide
  exactamente con el breakpoint `md` de Tailwind (768px), así que las clases `md:*` de `Sidebar.jsx`
  cambian en el mismo punto que el ancho del rail, sin JS ni `matchMedia`.
- **`Sidebar.jsx`, `Header.jsx`, `App.jsx`:** los tres leían `--faro-sidebar-expanded` fijo cada uno
  por su lado (ancho del `<aside>`, offset `left` del `<header>`, `padding-left` del `<main>`) --
  ahora los tres leen `--faro-sidebar-width`, así que quedan sincronizados por CSS sin duplicar el
  breakpoint en tres archivos.
- **`Sidebar.jsx`:** bajo el breakpoint, se ocultan (`hidden md:inline`/`md:block`) el wordmark
  "FARO", la leyenda "Alerta temprana de abandono escolar", los encabezados de sección
  ("Investigación guiada", etc.) y la etiqueta de texto de cada ítem de navegación -- se queda
  visible el número/icono de cada fase, centrado. El panel de sesión inferior hace lo mismo: el
  avatar se queda, el nombre/rol se oculta; en anónimo, el texto "Sin sesión iniciada" se reemplaza
  por un guion decorativo, con el texto completo disponible en el `title` (tooltip).

## Pendiente / simplificado a propósito

- **No es un menú hamburguesa ni un drawer** -- el rail colapsado se queda siempre visible y
  ocupando 4.5rem, no se puede cerrar del todo. Si el equipo de UX/UI decide que móvil necesita un
  patrón distinto (drawer, bottom nav), esto se reemplaza, no se parte de cero (la variable
  `--faro-sidebar-width` ya centraliza el ancho).
- **Sin prueba en un dispositivo real ni en breakpoints intermedios** (tablet 768–1279px que
  `Design_Tokens_Stitch.md` describe con su propio comportamiento de "8 columnas") -- esta entrega
  solo distingue móvil (< 768px) de todo lo demás; verificación visual real en manos de Diana con su
  `npm run dev` y las herramientas de dispositivo del navegador.
- **Tooltips (`title`) no son accesibles al tacto** -- en un teléfono real nadie puede "hacer hover"
  para leer la etiqueta completa de un ítem deshabilitado o el texto de "Sin sesión iniciada"; queda
  como limitación conocida, no se construyó un patrón de tooltip táctil.

## Validación

- Balance de llaves/paréntesis/corchetes verificado por script en los 4 archivos tocados
  (`index.css`, `Sidebar.jsx`, `Header.jsx`, `App.jsx`).
- `python vault/_Meta/scripts/vault_lint.py .` → Vault limpio.
- Mismo límite de siempre: sin `npm run dev`/`build` posible en este entorno (binario nativo de
  `rolldown` para otra arquitectura) -- verificación visual real, especialmente en un viewport
  angosto de verdad, queda en manos de Diana.
