---
project: "FARO"
date: "2026-09-13"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "3h"
touches: ["US-641", "US-601", "REQ-002"]
tags: [devlog, us-641, frontend, p6, explorador, referencia-tecnica]
---

# DevLog — 2026-09-13 — P6 Explorador (color de atención + botones) y reconciliación de Referencia Técnica con PR #350 (US-641)

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

1. **Explorador de escuelas (P6):** color por severidad en el badge de "Atención", SOLO en
   esta pantalla; restaurados los 2 botones del panel de expediente que el pase de fidelidad
   anterior había excluido por fabricados.
2. **Reconciliación de "Referencia Técnica"** contra el PR #350 de Héctor Morales (US-601,
   ya mergeado a `main`): el placeholder deshabilitado que dejó el rediseño de P1 se
   convierte en el enlace real a `/como-funciona`.
3. **Merge de `main` a `dev/diana-alvarez`** antes de abrir PR, con los 2 conflictos
   resultantes (`navFases.js`, `Sidebar.jsx`) resueltos a mano.
4. **Hallazgo pendiente, sin resolver todavía:** `check_ownership.py` reprueba 2 archivos de
   un commit anterior de esta misma rama, fuera de alcance.

## 1. Color por severidad en P6, excepción deliberada al S3

`03_Visual_Identity.md §S3` y `riskRamp.js` (`NIVEL_ICONOS`) son explícitos: el nivel de
atención se pinta con icono + texto, nunca con color, para no repetir el patrón de
"Calibrated Risk Tiers" que el propio proyecto rechazó. El pase de fidelidad de esta
mañana respetó esa regla en las 5 pantallas, incluida P6.

Diana pidió después, explícitamente y dos veces (primero en general, luego confirmando el
alcance con "Solo en P6, como el mockup"), que el semáforo rojo/ámbar/verde del mockup
`06_Explorador.html` sí se vea en esta pantalla en concreto, aceptando la inconsistencia
resultante con las otras 4. Se implementó así, acotado con un comentario explícito en
`Explorador.jsx` que documenta la excepción y por qué las demás pantallas no cambian.
Los 3 colores usados no son nuevos: son `--color-risk-high/mid/low`, tokens que ya existían
en `index.css` sin otro uso hasta hoy más que el texto de error genérico.

## 2. Los 2 botones fabricados del mockup, restaurados con una decisión honesta distinta cada uno

El pase de fidelidad de la mañana había excluido "Exportar Ficha CCT (PDF)" y "Vincular a
Mesa de Enlace" del panel de expediente de P6 por no existir en el backend. Diana pidió
restaurarlos igual. Ninguno de los dos se fabricó como si funcionara:

- **"Exportar Ficha CCT (PDF)" sí quedó funcional de verdad**: dispara la impresión del
  navegador (que cualquiera puede "Guardar como PDF"), acotada por `@media print` +
  `#ficha-imprimible` a la tarjeta seleccionada, no a la pantalla completa.
- **"Vincular a Mesa de Enlace" queda deshabilitado con `title`**: "Mesa de Enlace" no
  aparece en ningún doc del vault ni en `schemas.py` -- no hay campo, cálculo ni endpoint
  real que conectar, así que se documenta como pendiente en vez de simular una conexión
  que no existe (mismo patrón que `disabledHint` de `navFases.js`).

2 íconos nuevos en `Icons.jsx` (`IconDownload`, `IconLink`), dibujados a mano por el mismo
criterio que el resto del archivo: sin certeza del trazo SVG exacto de los glifos oficiales
de Material Symbols para estos 2, un path adivinado saldría peor que un equivalente honesto.

## 3. Referencia Técnica: de placeholder a enlace real

El PR #350 de Héctor Morales (US-601, "Cómo funciona FARO") adoptó a propósito los mismos
2 nombres que el rediseño de P1 ya había dejado como placeholder deshabilitado bajo
"Referencia Técnica" (comentario del propio PR #350), para que reconciliar fuera solo
habilitar el item, no fusionar 2 definiciones. Con el PR #350 ya mergeado a `main`:

- `navFases.js`: `REFERENCIA_TECNICA` -- "Cómo funciona FARO" deja `disabledHint` y rutea a
  `/como-funciona`. "Guía de Identidad" se queda igual (`disabledHint`): no es parte de ese
  PR, sigue sin ningún avance conocido en el repo.
- `Sidebar.jsx`: el merge automático de git había dejado los 2 arreglos antiguos
  (`REFERENCIA_TECNICA` + `REFERENCIA` de Héctor) declarados y renderizados por separado,
  con la etiqueta "Referencia Técnica" duplicada -- se consolidó en un solo arreglo, un
  solo bloque de render.

## 4. Merge de `main`, y un hallazgo sin resolver: `check_ownership.py` reprueba 2 archivos

`git merge origin/main` sobre `dev/diana-alvarez` trajo, además del PR #350, todo lo demás
que se mergeó a `main` desde el último `merge-base` (US-405/BUG-079 de Luis Téllez, US-601
completo de Héctor, etc.) -- 12 archivos nuevos/modificados fuera de `frontend/**`, todos
legítimos porque vienen de commits ya aprobados en otros PRs, no de este.

Al correr `check_ownership.py` contra esta rama para preparar el PR, **reprueba 2 archivos
de un commit anterior de este mismo día** (`24a00bd`, antes de esta sesión):
`diagnostico_duplicado_cct.sql` (raíz, sin dueño en ningún verde/amarillo/comunes) y
`vault/13_Reports/Recortes_Pendientes_Junta_2026-09-12.md` (verde exclusivo de Edgar
Coronel). **No resuelto en esta sesión** -- necesita una decisión de Diana (moverlos a otra
rama del dueño real, o sacarlos de este PR) antes de abrir el PR, porque el gate de
propiedad no deja mergear así.

## Verificación

- `npx esbuild` (sintaxis) limpio en `Explorador.jsx`, `Icons.jsx`, `navFases.js`,
  `Sidebar.jsx` ✅
- `git diff --check` limpio ✅
- `python3 vault/_Meta/scripts/vault_lint.py .` limpio (solo un archivo ajeno al repo,
  sin trackear, generado por la propia app de escritorio -- no viaja en ningún commit) ✅
- `python3 vault/_Meta/scripts/check_ownership.py` -- ❌ 2 archivos fuera de alcance (ver
  punto 4), sin resolver
- `npm run build` -- no se pudo correr desde este entorno: error de binding nativo de
  `rolldown`/npm en `node_modules` (bug conocido de npm con dependencias opcionales), no
  relacionado con este cambio -- pendiente que Diana lo confirme desde su Mac
- `pytest tests/ -q` -- no se corrió desde este entorno (el `.venv` del repo apunta a un
  intérprete de macOS que no existe en esta VM Linux) -- pendiente que Diana lo confirme
- Balance de llaves/paréntesis/corchetes no se verificó por separado en esta sesión (los
  `esbuild` de cada archivo ya lo hubieran atrapado como error de sintaxis)
