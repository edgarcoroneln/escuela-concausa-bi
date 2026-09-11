---
id: DOC-FARO-UX-DATAVIZ-REFS
title: "Referencias de forma de las Pantallas 2 a 6 (para identidad visual)"
owner: "Monserrat Xcaret Miranda Olivas"
status: draft
traces_up: ["US-621", "vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec"]
traces_down: ["vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity"]
last_reviewed: "2026-09-10"
tags: [ux, dataviz, referencias, s7, us-621]
---

# FARO · Pantallas 2 a 6 — referencias de forma para identidad visual

Equipo 3 · UX/UI y storytelling (`US-621`)
Monserrat Xcaret Miranda Olivas — narrativa analítica y visualización
Para: Juan Carlos Macías Mayen — identidad visual

---

## Qué son estos archivos

Cinco PNG que fijan **la forma y la lectura del dato** de cada pantalla: qué gráfica
responde cada pregunta de la historia y cómo se lee. **No fijan identidad visual.**

La paleta es neutra y provisional a propósito. El tono, la tipografía, los
componentes y el acabado los define `03_Visual_Identity.md`.

| Archivo | Pantalla |
|---|---|
| `02_Panorama.png` | Revelación de los casos + matriz de escuelas × 6 drivers |
| `03_Seleccion_de_caso.png` | Tabla de casos con índice y nivel de atención |
| `04_Expediente.png` | Una escuela: 6 pistas, dominante, ubicación y recomendación |
| `05_Conclusion.png` | Pistas que más se repiten y recomendación por pista |
| `06_Explorador.png` | Exploración libre del padrón, con filtros y paginación |

---

## Procedencia de lo que se ve

- **Valores de drivers y banderas de cobertura**: `tests/fixtures/features_escuela_mock.csv`
  (ciclo 2023-2024). Son de fixture, **no son hallazgos**.
- **Geometría del mapa**: `superset/assets/geojson/municipios_scope.geojson`, real.
- **Textos de recomendación**: reales, documentados en `vault/04_UX_Design/Panel_ML_US207.md`.
- **Nombres de escuela, índices y conteos**: aparecen como `N` o `[ nombre ]`. El número
  nunca se teclea: sale del dato en vivo.

---

## Seis reglas que el diseño no puede romper

1. **Un solo tono para magnitud**, de claro a oscuro, en pasos discretos. Nunca arcoíris,
   nunca rojo/verde de semáforo.
2. **`SIN_DATO` tiene tratamiento propio** (textura en la matriz, muesca vacía en los medidores)
   y nunca el paso más claro de la rampa. No es cero ni ausencia del problema. Debe verse igual
   en las tres pantallas donde aparece.
3. **Nada se codifica sólo por color.** Cada estado lleva texto, forma o icono además del tono.
   WCAG 2.1 AA es no negociable (`ADR-011` §4).
4. **La pista dominante se marca con contorno o acento**, no con un color de la rampa:
   el color ya está ocupado por la magnitud.
5. **Las barras terminan en el valor.** Sin puntas, sin degradados que alarguen la forma.
6. **Conteos con muescas, magnitudes con barra.** Donde el dato es "x de y" y ambos son enteros
   —las pistas verificadas de una escuela, la evidencia total— va el medidor de muescas: se
   cuentan las llenas y se ve la que falta como unidad ausente. Donde el dato es continuo o un
   promedio —el rezago social del municipio, la completitud promedio del panorama— va la barra
   continua. Una muesca partida a la mitad sería mentira.

## Lo que Juan necesita definir

1. Rampa secuencial de **un solo tono**, 5 pasos.
2. Un color de **acento** para la pista dominante y el Top.
3. Un **gris de contexto** para lo que no destaca.
4. Una **textura** para `SIN_DATO`, distinta de cualquier paso de la rampa.
5. Tres **etiquetas de nivel de atención** (alta / media / baja) con texto e icono.
