---
title: "Corrección visual: contorno ámbar del driver dominante en la matriz de Panorama (Pantalla 2)"
fecha: 2026-09-13
autor: Diana Aracely Alvarez Varela
herramienta: Claude Code / claude-sonnet-5
relacionado: [US-641, US-621, ADR-011]
---

## Contexto

Revisión visual pedida por Diana el 13-sep, comparando los 7 mockups reales
(`vault/04_UX_Design/FARO_Storytelling_UX/mockups/*.html`) contra el código
tal cual quedó en `dev/diana-alvarez` -- tipografía, colores, radios,
espaciado y trato de cada componente contra `03_Visual_Identity.md` §3 y
`Design_Tokens_Stitch.md`.

## Resultado de la revisión

Coinciden exactamente (colores, tipografía, radios, espaciado, sombras,
ausencia del semáforo rechazado, textura `SIN_DATO`, iconos ▲■● de nivel de
atención). Un solo hallazgo real: `02_Panorama_Escuelas_Riesgo.html` marca
la celda del driver dominante con `outline: 2px solid #B45309` y trae ese
swatch en su leyenda; `DriverMatrix.jsx` no lo dibujaba en ningún lado --
solo pintaba la rampa de magnitud y el rayado de `SIN_DATO`. La causa:
`matrizData` (`Panorama.jsx`) no pasaba el campo `driver_dominante` que cada
escuela ya trae (mismo dato que usa `DriverBars.jsx` en el Expediente,
Pantalla 4, donde el contorno sí estaba bien implementado desde el inicio).

## Qué se corrigió

- `Panorama.jsx`: `matrizData` ahora incluye `dominante: e.driver_dominante`.
- `DriverMatrix.jsx`: importa `DOMINANT_OUTLINE` de `lib/riskRamp.js`; cada
  celda calcula `esDominante` comparando su driver contra `d.dominante`; el
  `rect` de la celda dibuja `stroke` ámbar de 2px cuando es dominante (1px
  gris en el resto, igual que antes); el tooltip agrega "· Driver dominante"
  cuando aplica; se agregó el swatch "Driver dominante" a la leyenda, entre
  la escala de severidad y el swatch de `SIN_DATO`, en el mismo orden del
  mockup.

## Verificación

Balance de paréntesis/llaves/corchetes (0/0/0) en ambos archivos, `git diff
--check` limpio. Sin Docker/oxlint/esbuild en este entorno (igual que en
los DevLogs anteriores de esta rama) -- pendiente que Diana confirme con
`npm run dev` que la matriz de Panorama se ve igual al mockup antes de
avisarle a Marina.
