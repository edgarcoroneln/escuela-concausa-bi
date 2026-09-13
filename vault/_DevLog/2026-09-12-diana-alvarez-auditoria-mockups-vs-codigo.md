---
id: DOC-DEVLOG-2026-09-12-diana-alvarez-auditoria-mockups-vs-codigo
title: "Auditoría pantalla por pantalla: mockups de Equipo 3 vs. código real (rediseño Fase 2)"
owner: Diana Aracely Alvarez Varela
status: done
fecha: 2026-09-12
---

# Auditoría pantalla por pantalla: mockups de Equipo 3 vs. código real

Petición de Diana tras terminar las Pantallas 3-6 del rediseño: comparar los 7 mockups liberados por
Equipo 3 (`vault/04_UX_Design/FARO_Storytelling_UX/mockups/*.html`) contra el código ya construido,
pantalla por pantalla, para separar diferencias intencionales (ya documentadas y aprobadas) de huecos
reales que valga la pena corregir.

## Método

Extracción de texto visible de cada mockup (`<main>`/`<body>`, regex + `html.unescape`), comparado
línea por línea contra la pantalla real (`Home.jsx`, `Panorama.jsx`, `LosSieteCasos.jsx`,
`ExpedienteEscuela.jsx`, `Conclusion.jsx`, `Explorador.jsx`) y sus componentes de apoyo
(`GlosarioOverlay.jsx`, `WalkthroughOverlay.jsx`, `AsistenteFaro.jsx`). Cada diferencia se contrastó
contra `01_UX_Architecture.md` (fichas por pantalla, §3 filtros, §4 walkthrough, §6 asistente) y
`02_Data_Visualization_Spec.md` (§1.2 glosario, tabla de datos por pantalla, tabla de reconciliación)
antes de decidir si era un hueco real o una corrección ya aprobada del mockup.

## Hallazgo principal: catálogo de recomendaciones corregido

`recomendacionGeneralPorDriver` en `data/mock.js` (creado el mismo día para la Pantalla 5) traía texto
autoral de este frente porque la búsqueda original en el vault no encontró un catálogo oficial. **Sí
existe:** es el catálogo prescriptivo canónico de `vault/15_ML_Models/Publicacion_Gold.md` §4,
implementado en `src/modelos/recomendaciones.py` (`RECOMENDACION_POR_DRIVER`) y expuesto por
`PrediccionOut.recomendacion` (el mismo campo que ya consume, correctamente, la pestaña "Recomendación"
de `ExpedienteEscuela.jsx` vía `getPrediccion(cct)`). Confirmado contra los propios mockups: el texto
de D2 y D4 en `04_Expediente_Escuela.html` y `05_Conclusion_Top3.html` coincide literal con el catálogo.
Corregidas las 4 líneas que no coincidían (D1, D3, D5, D6); D2 y D4 ya coincidían por casualidad. Riesgo
declarado en el comentario nuevo: no hay endpoint de catálogo por driver, solo por escuela vía
`/predicciones/{cct}`, así que un cambio futuro del backend no se detecta aquí automáticamente.

## Glosario metodológico completado

`GlosarioOverlay.jsx` traía 5 de los 8 términos que `02_Data_Visualization_Spec.md` §1.2 exige
textualmente. Agregados "Driver" y "Recomendación" (texto literal del spec) y "Nivel de atención ≠
prioridad" (la aclaración explícita que evita la confusión de `BUG-063` entre el nivel de atención del
front y la columna `prioridad` de Gold/Superset -- vigente el mismo día por el mensaje de Christian).
"Índice de riesgo" se completó con las anclas de calibración (conservación de matrícula, pérdida del 5%,
línea de alerta ~3.4%) que el spec pide explícitas, tomadas de `useCortesAtencion()` -- nunca tecleadas
(mismo criterio anti-`BUG-058`). "Completitud de evidencia" se deja con su nombre ya usado en el resto
del producto en vez de renombrarla "Evidencia disponible" como dice el spec -- mismo concepto, un solo
nombre en toda la app.

## Panorama (P2): dos agregados que faltaban

`02_Data_Visualization_Spec.md` lista `variacion_matricula` e `indice_completitud_drivers` de `KpisOut`
como datos que P2 necesita, y su tabla de reconciliación resuelve explícito que la variación de
matrícula agregada (no por escuela) se muestra "en la P2". `Panorama.jsx` ya mostraba N y la matrícula
de las escuelas en riesgo, pero no estos dos agregados del alcance completo. Agregada una llamada
independiente a `getKpis()` (no bloquea el resto de la pantalla si falla) y una línea con ambos datos,
sin el lenguaje de "telemetría/sensores" del mockup -- mismo criterio que el resto de esta pantalla.

## Confirmado como corrección intencional, no se revierte

- P1: sin narrativa de "sensores"/"telemetría" (`Home.jsx` ya lo declara contra `01_UX_Architecture.md`
  §2); sin revelar el conteo de casos; walkthrough con el texto literal de §4 (verificado idéntico,
  incluye los 3 pasos y el cierre "Empezar").
- Asistente FARO: sin simulador de estados de error ni chips de "prompt sugerido" -- no están en §6 del
  spec y son artefacto de la plantilla Stitch, no una funcionalidad a construir.
- P3: sin los filtros "Entidad/Nivel" ni el botón "Saltar a Conclusión" del mockup -- §3 dice
  explícito "Ninguno adicional; hereda el universo de P2" y la ficha de P3 no lista un atajo de salto.
- P5: Top 2 real en vez de rellenar hasta 3 (decisión ya cerrada con Marina, PR #308/§8.3); sin la
  tabla de "distribución paramétrica total" con los 4 drivers en 0% -- mismo criterio de no rellenar.
- P6: card-grid en vez de tabla con panel lateral -- el spec no exige un layout tabular, y el resto del
  producto ya usa tarjetas (consistencia visual); niveles educativos con los códigos reales del sistema
  (`DPR/DJN/DES/DCT`), no las etiquetas genéricas del mockup.
- Escala 0-10 y fuentes por driver inventadas (INEGI/SESNSP/etc., solo en el mockup de P6): la API
  entrega 0-1 sin campo de fuente por driver -- no se inventa un dato que el contrato no tiene.

## Pendiente, no resuelto en este commit

- P0 (Login): no hay pantalla construida en el frontend -- fuera de alcance de Equipo 5 (OAuth real,
  responsabilidad de otro frente); no se improvisa un login de ejemplo.
- P6: leyenda no distinguida de la de P4 (pendiente ya conocido, confirmado por esta auditoría, no
  nuevo).

`vault_lint` no corrido en este commit (cambios solo en `frontend/src` y este DevLog).
