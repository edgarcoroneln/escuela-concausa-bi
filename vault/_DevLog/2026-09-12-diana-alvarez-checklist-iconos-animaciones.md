---
title: "Checklist 100% -- 3 huecos accionables cerrados: iconos de driver, animaciones de relleno y aparición escalonada"
fecha: 2026-09-12
autor: Diana Aracely Alvarez Varela
herramienta: Claude Code / claude-sonnet-5
relacionado: [US-621, ADR-011, DEC-026]
---

## Qué se cierra

De `2026-09-12-diana-alvarez-comparativa-diseno-y-checklist-100.md` §4, sección "Ya accionable
por Equipo 5, sin depender de nadie más", quedaban 3 ítems abiertos justo antes de la fusión con
`origin/main`. Los tres son CSS/D3 puro, sin tocar ningún endpoint ni contrato -- se cierran en
este commit, en el mismo orden en que se atacaron (más rápido/aislado primero):

1. **Icono de driver en las cabeceras de `DriverMatrix.jsx`.** El heatmap ya traía
   `driverNombres` en las cabeceras de columna (envueltas a 2 líneas), pero no el emoji de
   `driverIcons` que sí aparece en la insignia de driver dominante de `LosSieteCasos.jsx` y
   `MapaCasos.jsx`, y en cada fila de `DriverBars.jsx`. Se agrega como un `<text>` propio arriba
   de las 2 líneas de nombre, mismo emoji, ahora identificando la columna completa (no una
   escuela).

2. **Animación de relleno en `RiskGauge.jsx`.** El arco de valor se dibujaba de una vez, en su
   ángulo final. Ahora usa un `arcTween` real de D3 (interpola el ángulo entre 0 y el índice de
   riesgo con `d3.interpolate` + `easeCubicOut`, 700ms) -- el gauge "se llena" en vez de aparecer
   ya lleno. Respeta `prefers-reduced-motion`: si el sistema lo pide, salta directo al ángulo
   final sin interpolar.

3. **Animación de relleno en `DriverBars.jsx`.** Cada barra arrancaba ya con su ancho final. Se
   extrae un subcomponente `Barra` que monta en 0% y, en el siguiente frame
   (`requestAnimationFrame`), transita en CSS (`transition: width 650ms`) hasta su ancho real --
   mismo patrón "crece desde 0" que el gauge, aquí sin D3 porque una barra no lo necesita.

4. **Aparición escalonada de tarjetas en `LosSieteCasos.jsx`.** Se agrega la clase utilitaria
   `.aparicion-escalonada` en `index.css` (keyframe `opacity 0→1` + `translateY(8px)→0`, 420ms,
   con `animation-delay: var(--delay)`) y se aplica a cada `Card` de la cuadrícula de 7 escuelas
   con `--delay: ${i * 60}ms` -- las tarjetas entran en cascada de izquierda a derecha / arriba a
   abajo, no todas de golpe. También respeta `prefers-reduced-motion` (la animación se desactiva
   por completo).

## Actualización -- botón "Comparar los 7 casos" resuelto

Diana decidió (vía pregunta directa, mismo día): **quitar el botón**. No tenía `onClick` ni
destino, no existe ninguna vista de "comparación de los 7" construida en ninguna parte del repo,
y la propia cuadrícula de tarjetas de `LosSieteCasos.jsx` (gauge + driver dominante por escuela,
lado a lado) ya cumple ese rol comparativo -- el botón era un cabo suelto del mockup original sin
destino real. Se retira el `<button>` de `LosSieteCasos.jsx`, dejando solo el link "← Volver al
panorama"; comentario en el propio JSX documentando la decisión y su fecha. Con esto se cierran
los 4 ítems de "ya accionable por Equipo 5, sin depender de nadie más" del checklist -- lo que
queda pendiente en ese documento son los 5 ítems que sí necesitan respuesta de otra persona del
equipo (Christian, Edgar, Estefany/Héctor, Marina, Oscar).

## Verificación

Sin binding nativo de `oxlint`/`esbuild` disponible en este entorno (node_modules instalado para
macOS arm64, este shell es un VM Linux) para correr el lint real -- se verificó balance de
paréntesis/llaves/corchetes (0/0/0 en los 4 archivos) y `git diff --check` (sin errores de
espacios en blanco) en su lugar. Pendiente que Diana confirme visualmente con `npm run dev` desde
su Mac.
