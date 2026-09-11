---
project: "FARO"
date: "2026-09-10"
author_human: "Monserrat Xcaret Miranda Olivas"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — lectura de gobernanza, consulta a producción, especificación de visualizaciones y seis ejemplos con datos reales. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011", "DEC-023", "DEC-024", "DEC-019", "BUG-058", "BUG-063", "US-631", "US-641"]
tags: [devlog, equipo-3, ux, dataviz, storytelling, s7, us-621]
---

# DevLog — 2026-09-10 — Especificación de visualizaciones de la historia FARO (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]]

## Tercera entrega: corrección tras revisión de Marina García (PR #308)

Marina revisó y dio **visto bueno**, con dos hallazgos que corrigen `PLAN_TRABAJO` (los corrige ella,
no este documento): §10 prometía `/explicacion` como evidencia del dominante y SHAP sigue sin poblar;
y confirmó el Top 3 que hoy son dos drivers sin rellenar. Resolvió a mi favor el choque con Oscar
sobre el filtro de `nivel` en `/kpis` y adoptó la recomendación de que la P2 revela siempre sin
filtros. Registrado en la §8.3 del documento.

- **Sincronía:** `origin/main` avanzó con el PR #307 de Estefany (`US-631`, explicación ML-03);
  hice `git merge origin/main` sin conflictos — mi fila en `_DevLog/_index.md` y mi sección en la
  matriz sobrevivieron intactas.
- **Corrección de forma:** `LEER_PRIMERO.md` decía "Cinco reglas" con seis listadas; corregido a
  "Seis reglas".
- **Pendiente, del lado de Marina:** §7.bis (leyenda de las gráficas, es mía de escribir cuando
  llegue), §4.ter (SQL del Asistente FARO no se muestra por defecto) y §5.bis ("Cómo funciona" del
  Equipo 1) todavía no están en `main` ("ya los subo"). Se revisan al sincronizar.
- `generar_ejemplos.py` se queda donde está (decisión de Marina): reproducibilidad de los ejemplos
  vale más que la pureza de tener código fuera de la carpeta de documentación.

## Qué se hizo

- **`02_Data_Visualization_Spec.md` lleno en sus ocho secciones**, con la estructura y el frontmatter
  del esqueleto. Sólo se añadieron `ADR-011`, `DEC-023` y `DEC-024` a `traces_up`, porque son las
  resoluciones que gobiernan el documento.
- **Consulta a producción** (API v1, commit `457715a`, 10-sep 18:24 UTC−06:00): 34 llamadas, todas
  200. La corrió Monserrat en su terminal con su propia sesión; el token se pidió con entrada oculta y
  nunca se escribió, se imprimió ni pasó por el agente. La evidencia cruda vive fuera del repositorio.
- **Seis ejemplos en PNG y SVG** en `FARO_Storytelling_UX/ejemplos_graficas/` (P2, P3, dos P4, P5 y
  P6), con el script reproducible `generar_ejemplos.py` versionado junto a ellos. Paleta neutra y
  provisional, contraste WCAG 2.1 AA medido por el propio script.
- **Coordinación con Marina García** (mensaje reenviado por Monserrat): la carpeta
  `ejemplos_graficas/` la da de alta Marina en su `_index.md`, así que este commit **no toca** ese
  archivo; el formato de entrega a Juan lo define Juan; el conjunto en riesgo se obtiene con una sola
  llamada a `/escuelas`; y el aviso del nombre del asistente queda escrito en la §8.2 del documento.

## Segunda entrega: referencias de forma y libertad de Juan

- **Cinco referencias de forma de Monserrat** (P2 a P6) y su nota `LEER_PRIMERO.md` entran a
  `ejemplos_graficas/referencias/`, sin cambios en las imágenes; a la nota sólo se le añadió el
  frontmatter que exige el vault. La carpeta tiene ahora su propio `_index.md`.
- **Evaluación contra el contrato** en la §7.4 de la especificación. Se adopta casi toda la forma, y
  se corrigen, sin tocar las imágenes, cuatro cosas que el dato de producción contradice: D3 y D4 en
  valor publicado (02 y 04), "D5 y D6 con cobertura parcial" (02), la frase "el dominante es la pista
  que más pesa en la predicción" (04) y los conteos tecleados de la 05. El mapa y el "promedio
  estatal" del rezago quedan como recortes con su forma más cercana (§7.4, §8.1).
- **Juan Carlos Macías tiene libertad total** de maquetación, colores, tipografías y tamaños; la §7.5
  separa eso de las reglas de lectura del dato, que no se mueven.
- **Los ejemplos se regeneraron** para cumplir la regla 4 de la nota: la barra del dominante usaba el
  paso más oscuro de la rampa y ahora usa un acento neutro.
- **Sincronía:** `origin/main` sin commits nuevos desde `c1762f4` al preparar el PR.

## Lo que dijo el dato y cambia el diseño

Todo verificado contra el código o contra la consulta, con su ruta:

| Hallazgo | Consecuencia en el documento |
|---|---|
| `/kpis.escuelas_en_riesgo` = 7 y el corte cliente sobre una página de `/escuelas` da las mismas 7 | La mecánica de la §3.4 queda probada contra producción; `P-05` confirmado en la superficie que consume Front |
| En las 7 escuelas hay dato sólo de D1, D2 y D4: **D3, D5 y D6 son `SIN_DATO` en todas**, evidencia 3 de 6 | El `SIN_DATO` no es caso de borde: es la mitad de cada expediente. La P5 lo dice junto al Top |
| D5 es `null` para todo el universo (`dbt/models/gold/fact_escuela_ciclo.sql:359-360`) | La evidencia máxima posible hoy es 5 de 6; D5 no es "cobertura parcial" |
| `d3` y `d4` suben cuando la escuela está **mejor**; el pipeline elige el dominante con `1 − d3` y `1 − d4` (`features_escuela.sql:385-410`) | Por decisión de Monserrat, D3 y D4 se dibujan como **falta**, en el mismo eje de presión. El dominante de ML-02 coincidió con la barra más larga en las 7 |
| Dominantes: D2 en 5, D4 en 2 | El Top 3 de hoy es un **Top 2**; la copy lo dice sin maquillarlo |
| En Toluca, las 5 escuelas comparten D1 y D2 (valores municipales) y sólo las separa la conectividad | Es el diferenciador en una fila: mismo municipio, mismo riesgo, otra situación, otra recomendación |
| Dos parejas con el mismo nombre y coordenadas, CCT distintos, y conectividad registrada distinta | Queda como dato para QA y E5 (§3.2); la matriz muestra la CCT en cada fila |
| SHAP: 0 de 42 contribuciones con valor; `es_estimado_por_grupo`: `null` en las 7 (`src/api/v1/gold.py:78-80`) | Panel SHAP en estado `SIN_DATO`; "Estimación por grupo: sin dato", nunca "no" |
| El índice se repite exactamente entre escuelas del mismo perfil | Orden de filas por índice, nombre y CCT; los empates se muestran como tales |
| `/kpis` no acepta `nivel`; `variacion_matricula` cae a `0.0` sin ciclo anterior (`src/api/repositorio_gold.py:381`) | Restricción para los filtros de Oscar; aviso a Christian Ruiz |
| Gold guarda `prioridad` en minúsculas (`publicar_gold.py:96-98`) | El glosario dice que DB-09 muestra `media`, como lo guarda Gold |

## Verificación de los criterios de §9 del plan

El plan v1.2 tiene **26** criterios, no 24 (el §7 de `00_Storytelling_Scope` todavía dice 24: aviso a
Marina). Los que toca este documento:

| # | Criterio | Cómo lo cumple el documento |
|---|---|---|
| 2 | La P2 revela cuántas escuelas están en riesgo | Frase de revelación con `N` de `/kpis` en vivo y una fila por caso (§3.2, §3.4) |
| 3 | Se puede seleccionar cualquiera sin revisar las demás | Lista de la P3 con CTA por fila, sin llamadas nuevas (§2, ejemplo P3) |
| 4 | Índice numérico **y** nivel de atención | En P2, P3, P4 y P6; nivel derivado con las constantes importadas (§1.1) |
| 5 | Significado del índice en lenguaje sencillo | Glosario §1.2 con las anclas de la sigmoide y la nota "Qué calcula" del expediente |
| 6 | El expediente muestra los 6 drivers a la vez | Seis filas fijas; las `SIN_DATO` se quedan rayadas en su lugar (§4.2, §4.3) |
| 7 | Dominante destacado | Cuatro señales, ninguna sólo de color (§4.2) |
| 8 | Recomendación de datos existentes; nivel derivado; nadie consume `prioridad` | `recomendacion` de `/predicciones`; nivel de §1.1; `prioridad` sólo en §1.2 y §8 como lo que no se consume |
| 9 | Sin causalidad | Frase fija bajo la gráfica; revisado el texto completo del documento y del script |
| 10 | Top 3 sobre el conjunto completo | Mecánica §5.1, pedida sin filtros; función `top3()` ejecutable |
| 11 | La P5 lo indica explícitamente | Leyenda obligatoria, visible y sin tooltip (§5.2, ejemplo P5) |
| 12 | Problemática sustentada sólo en datos | Texto armado con los valores del grupo y la cobertura calculada (§5.2) |
| 13 | Un solo CTA en la P5 | §5.2 y ejemplo P5 |
| 17 | El glosario explica los términos mínimos | Texto de datos para los seis términos en §1.2 |
| 18 | Todo se construye con endpoints existentes o fixture rotulado | Cada gráfica declara endpoint y campos (§2); lo que no, a §8 con su "mientras tanto" |
| 19 | Ninguna gráfica requiere un endpoint no acordado | El mapa y los agregados por nivel quedaron fuera (§8.1) |
| 22 | El Equipo 5 implementa sin redefinir UX | Endpoints, campos, algoritmo, costo en llamadas, estados de carga y de `SIN_DATO` (§3.4, §4, §5) |
| 25 | El glosario distingue nivel de atención de `prioridad` | Fila propia en §1.2 |
| 26 | Ninguna superficie usa "Watson" | Ni el documento ni los ejemplos; el aviso de la §8.2 es sobre "Agente FARO" en el producto vivo |

Criterios **1, 14, 15, 16, 20, 21, 23 y 24** son de la entrada, el chat, el walkthrough, el pop-up,
la arquitectura y la identidad (Marina, Oscar, Juan y Equipo 2). Este documento no los contradice: los
ejemplos son de escritorio y su paleta es neutra, no la identidad anterior.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5.
- **Archivos creados/modificados:**
  `vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec.md` ·
  `vault/04_UX_Design/FARO_Storytelling_UX/ejemplos_graficas/generar_ejemplos.py` y sus 12 imágenes
  (6 PNG, 6 SVG) · `ejemplos_graficas/_index.md` · `ejemplos_graficas/referencias/` (5 PNG y
  `LEER_PRIMERO.md` de Monserrat) · este DevLog · `vault/_DevLog/_index.md` (una fila) ·
  `vault/02_Requirements/Traceability_Matrix.md` (una sección de evidencia).
- **Decisiones de Monserrat:** dato real con su sesión y el token por entrada oculta; seguir sin
  imágenes de referencia; D3 y D4 orientados como presión; evidencia en la matriz como sección nueva,
  sin tocar la fila compartida con el Equipo 5.
- **Decisiones autónomas del agente:** paleta provisional de grises y un solo tono, con validación de
  contraste que detiene el script si falla; regla de empates del Top 3 por rango compartido; orden de
  filas por índice, nombre y CCT; selección automática y con regla fija de los dos expedientes y del
  filtro de ejemplo; constantes leídas del código con `ast` en vez de importarlas o teclearlas; evidencia
  y entorno virtual fuera del repositorio.
- **Correcciones manuales:** pendientes de la revisión línea por línea de Monserrat antes del push.
- **Prompt inicial:** `referencias_locales/prompt.md` (local, no versionado).

## Seguridad / calidad

- [x] Sin secretos: el token nunca se escribió ni se imprimió; la evidencia no se versiona.
- [x] `ruff check` limpio sobre `ejemplos_graficas/`.
- [x] `pytest --noconftest tests/test_generate_pm_dashboard.py tests/test_check_ownership.py`: 52
  pasan (las pruebas que leen el índice de DevLog y el padrón). La suite completa la corre CI.
- [x] `vault_lint` limpio sobre una copia con sólo lo versionado y lo nuevo. En la carpeta local el
  único bloqueo es `referencias_locales/prompt.md`, que está excluido de git y no llega a CI.
- [ ] Pruebas nuevas: no aplica (documento y script de ejemplos, sin código productivo).
- [x] DevLog enlaza a los IDs afectados.

## Bloqueantes

- Ninguno para este documento. SHAP sin poblar (Equipo 4, `US-631`), D5 sin fuente (DS-06) y
  `es_estimado_por_grupo` sin columna son recortes con su "mientras tanto" en la §8.

## Próximos pasos

- PR `[Monserrat Miranda] - Especificación de visualizaciones de la historia FARO (US-621) - [sync|CI|DoF|DevLog]`,
  abierto a petición de Monserrat. Pide revisión a Edgar Coronel (matriz de trazabilidad) y a Marina
  García (`vault/04_UX_Design/**`). Las casillas de revisión línea por línea y de datos en prompts
  son declaración de Monserrat y las marca ella.
- Marina: visto bueno o no a la franja de rezago contra el promedio estatal (§7.4) y al mapa con la
  base cartográfica versionada (§8.1).
- Marina: alta de `ejemplos_graficas/` en su `_index.md`; "24" → 26 en `00_Storytelling_Scope` §7.
- Juan: formato de entrega de los ejemplos.
- Equipo 5: los avisos de la §8.2 (nombre del asistente y sus dos pruebas, constantes, ciclo explícito).
- Christian Ruiz: `variacion_matricula` en `0.0` sin ciclo anterior.
- Monserrat: su Agent Context sigue en "Célula 2 — Analytics & BI"; es su archivo, se actualiza aparte.
