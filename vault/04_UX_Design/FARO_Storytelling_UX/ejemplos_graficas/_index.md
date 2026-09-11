---
id: MOC-04-FARO-UX-EJEMPLOS
title: "Ejemplos de gráficas — especificación de visualizaciones"
owner: "Monserrat Xcaret Miranda Olivas"
status: active
tags: [moc, ux, dataviz, s7, us-621]
---

# Ejemplos de gráficas

> Material de apoyo de [[vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec]]
> (Monserrat Xcaret Miranda Olivas) para Juan Carlos Macías. Demuestra **forma y lectura del dato**,
> no identidad visual: la maquetación, los colores y la tipografía los decide Juan (§7.5 de la
> especificación).
> → [[vault/04_UX_Design/FARO_Storytelling_UX/_index]]

## Ejemplos con datos reales de producción

Consulta del 10-sep-2026 18:24 (UTC−06:00), API v1, commit `457715a`. Se regeneran con el script.

| Archivo | Pantalla | Qué demuestra |
|---|---|---|
| [generar_ejemplos.py](generar_ejemplos.py) | — | Script reproducible: `descargar` (evidencia fuera del repo) y `graficar` (PNG y SVG) |
| [P2_matriz_casos](P2_matriz_casos.png) · [SVG](P2_matriz_casos.svg) | P2 | Matriz de casos N × 6 drivers |
| [P3_seleccion_caso](P3_seleccion_caso.png) · [SVG](P3_seleccion_caso.svg) | P3 | Lista de casos con la línea de alerta |
| [P4_expediente_15EJN4151O](P4_expediente_15EJN4151O.png) · [SVG](P4_expediente_15EJN4151O.svg) | P4 | Expediente con dominante D4 |
| [P4_expediente_15DJN1794N](P4_expediente_15DJN1794N.png) · [SVG](P4_expediente_15DJN1794N.svg) | P4 | Expediente con dominante D2, mismo municipio y nivel |
| [P5_conclusion_top3](P5_conclusion_top3.png) · [SVG](P5_conclusion_top3.svg) | P5 | Top por conteo con gráfica de unidades |
| [P6_exploracion](P6_exploracion.png) · [SVG](P6_exploracion.svg) | P6 | Lista filtrada con niveles de atención |

## Referencias de forma (Monserrat)

En `referencias/`. Construidas con valores de fixture: **no son hallazgos**. Su evaluación contra el
contrato está en la §7.4 de la especificación. Nota de autora:
[[vault/04_UX_Design/FARO_Storytelling_UX/ejemplos_graficas/referencias/LEER_PRIMERO]].

| Archivo | Pantalla |
|---|---|
| [02_Panorama](referencias/02_Panorama.png) | P2 — revelación y matriz escuelas × 6 drivers |
| [03_Seleccion_de_caso](referencias/03_Seleccion_de_caso.png) | P3 — casos con índice y nivel de atención |
| [04_Expediente](referencias/04_Expediente.png) | P4 — seis pistas, dominante, ubicación y recomendación |
| [05_Conclusion](referencias/05_Conclusion.png) | P5 — pistas que más se repiten |
| [06_Explorador](referencias/06_Explorador.png) | P6 — exploración con filtros y paginación |
