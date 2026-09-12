---
project: "FARO"
date: "2026-09-11"
author_human: "Juan Carlos Macías Mayen"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "Varias sesiones — revisión de 3 entregas sucesivas de Stitch contra los datos reales y las reglas de Marina García y Monserrat Miranda, corrección iterativa vía brief a Stitch, integración final. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011", "DEC-024"]
tags: [devlog, equipo-3, ux, identidad-visual, s7, us-621]
---

# DevLog — 2026-09-11 — Los 7 mockups corregidos y liberados para Equipo 5 (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]]

## Contexto

El PR #310 (2026-09-10) liberó identidad visual + Login, pero construido sobre una redacción
vieja de `PLAN_TRABAJO.md` que describía un login con usuario/contraseña que nunca existió, y con
un sistema de color de datos (semáforo rojo/ámbar/verde + 6 colores por driver) que Marina García
del Buey rechazó por chocar con las reglas de lectura del dato de Monserrat Miranda y con
`ADR-011` §4. Esta sesión cubre las tres rondas de corrección que siguieron hasta la entrega
final ("Version 11_40").

## Qué se hizo

- **Ronda 1** (`00_Login.html` + guía de identidad, sin gráficas de datos): brief a Stitch con la
  ficha corregida del login (`abeb393` de Marina) y el sistema de color nuevo derivado de
  `LEER_PRIMERO.md`.
- **Ronda 2** (las 8 pantallas completas, primera vez): revisión encontró que Stitch había
  construido todo en viewport móvil (contradice "Alcance principal: escritorio" del plan, dicho
  dos veces), inventado datos que contradicen producción (un split falso de niveles de atención
  en Panorama, un Top 3 fabricado en Conclusión cuando la producción solo sostiene Top 2,
  ausencia total de `SIN_DATO` en Expediente) y reintroducido "prioridad"/lenguaje de urgencia.
- **Ronda 3** (ajustes finos + marca): corregido el viewport a escritorio en las 6 pantallas de
  datos; encontrado y corregido un problema serio aislado en el Explorador — afirmaba causalidad
  explícita ("vínculo causal dominante", una cifra de absentismo del 34% inventada) y usaba D5
  (sin fuente de datos integrada) como dominante con valor falso, más programas institucionales
  inventados ("CAEM", "La Escuela es Nuestra"). Se pidió además un solo tagline de marca (había
  tres compitiendo) y que la matriz de la Pantalla 2 llevara solo los 6 drivers como columnas,
  siguiendo una referencia visual que Juan compartió.
- **Entrega final ("Version 11_40"), verificada línea por línea contra el código HTML** (no solo
  las capturas — se encontró que el PNG exportado del Login no reflejaba su propio `code.html`
  actualizado, aunque el código sí traía la corrección): cero `Watson`, cero
  `lh3.googleusercontent.com`, cero "prioridad" como nivel, matriz de la Pantalla 2 solo con
  columnas D1-D6, Pantalla 6 sin causalidad y con el catálogo real de recomendaciones, tagline
  unificado, hex de la paleta de entidades coincidiendo con el código real de Manuel Serranía
  (`#4C72B0`, `#DD8452`), matrícula de Mixcoac corregida a 115 (dato real), bug de codificación
  corregido.
- **Un residuo encontrado en la verificación final, corregido en integración sin otra vuelta a
  Stitch:** una frase en la Pantalla 2 llamaba a la inseguridad "principal detonante de
  deserción" — causalidad explícita, prohibida por el criterio de aceptación 9. Se cambió a "el
  driver dominante más frecuente en el corte actual".
- **`03_Visual_Identity.md` §3, §4, §6 y §7 reescritos** para reflejar el sistema de color
  realmente vigente (antes documentaban el semáforo rechazado). `Design_Tokens_Stitch.md` lleva
  ahora una nota explícita de que su sección de color quedó superada.
- **`Como_Funciona_Preview.*`** se incluyó como material de referencia, no como octavo mockup
  formal — `PLAN_TRABAJO.md` §5.bis es explícito en que esa superficie (Equipo 1, `US-601`) "no
  necesita mockup propio" y que sus dos rutas de API todavía no están en `main`.

## Pendiente

- Auditoría formal de contraste WCAG 2.1 AA sobre la rampa/acento de datos.
- `FARO_UX_UI_Guide.pdf`.
- Chrome decorativo menor sin corregir (algunas menciones de "crítico", "DICTAMEN_LEGISLATIVO",
  "CADENA DE CUSTODIA DIGITAL VERIFICADA") — no son datos incorrectos, no bloquea a Equipo 5.
- Coordinar con Manuel Serranía/Héctor Morales antes de dar por final cualquier tratamiento de
  *Cómo funciona*.
