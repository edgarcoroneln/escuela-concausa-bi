---
project: "FARO"
date: "2026-09-05"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sesión: US-207 construida, causa raíz de BUG-049 y cierre de US-215a"
touches: ["US-207", "US-215a", "US-214a", "US-321", "REQ-002", "BUG-049", "BUG-048", "DEC-006", "DEC-015"]
tags: [devlog, frontend, streamlit, ml, bi, celula-2]
---

# DevLog — 2026-09-05 — US-207 construida, BUG-049 con su causa raíz real, US-215a al 21/22

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB03_DB04]]

## Contexto

US-207 llevaba desde el 7-ago marcada `in_progress` con **10 líneas de andamiaje**. La
sesión empezó por una pregunta directa de Marina: *"¿qué te impide hacer US-207?"*. Al
verificarlo en vez de repetir el supuesto, la respuesta fue **nada**.

## 1. Lo que estaba mal en mi propio diagnóstico

Venía arrastrando "bloqueada por Manuel" desde el primer diagnóstico sin volver a
comprobarlo. Tres de las cuatro razones eran falsas:

| Lo que asumí | Lo verificado |
|---|---|
| `src/frontend/**` necesita a Manuel | Está en el **amarillo** de Marina: puede tocarlo |
| Es ruta crítica, bloquea | `criticos` **avisa, no reprueba** — lo dice el propio `check_ownership.py` |
| Falta la API de inferencia | Responde **sin token** (`AUTH_LECTURA_PUBLICA=true`), en local y en producción |
| Falta streamlit | Instalado desde el 3-sep; Manuel además lo agregó a `requirements.txt` |

Era una revisión de PR, no un permiso previo. **La lección: un bloqueo que no se re-verifica
se vuelve una excusa.**

## 2. US-207 entregada, con 2 de 3 modelos y el tercero declarado

`src/frontend/prediccion_client.py` (nuevo) + `pages/2_Panel_ML.py` reescrito. El cliente
sigue el patrón del repo: el verbo HTTP es un **seam inyectable**, así que las pruebas
ejercitan todo sin red.

- **ML-01** — índice de riesgo contra el umbral 0.60 de DEC-006, con la explicación de por
  qué ese umbral significa "proyecta perder ≥ 5 %".
- **ML-02** — driver dominante y su recomendación prescriptiva.
- **ML-03** — **`SIN_DATO` explícito.** US-321 (Estefany Hernández, C3) no ha aterrizado,
  `gold.predicciones` no tiene columna `cluster` y la API devuelve `null` — lo documenta el
  propio contrato en `schemas.py::PrediccionOut`. Se pinta el hueco en vez de esconderlo.

Verificado **contra la API real**, no solo con dobles:

```
local  15DJN0049A  riesgo 0.7423  en_riesgo True   driver D1  ->  becas y apoyo alimentario
local  09DSN0042A  riesgo 0.6692  en_riesgo True   driver D2  ->  rutas escolares seguras
prod   09DBN0007I  riesgo 0.1060  en_riesgo False  driver D1
prod   15DJN0049A  riesgo 0.129   en_riesgo False  driver D3  <- NO coincide con el local
```

Esas dos primeras filas **son la historia del proyecto**: riesgo parecido, recomendación
distinta según el driver que lo explica. El valor de US-207 no es el conteo de modelos.

> **Corrección del 5-sep, señalada por Edgar Coronel al ratificar DEC-015.** Ese par es una
> **medición local** y hay que decirlo así. La URL pública sirve un Gold anterior al fix de
> BUG-045: para `15DJN0049A` devuelve **0.129 / D3** —infraestructura, no pobreza— y
> `escuelas_en_riesgo = 0` en `/kpis`. Yo había escrito en el PR *"verificado contra la API
> real, local y producción"* juntando ambos en un renglón, y eso indujo la lectura de que el
> par era citable en la demo. **No lo es mientras BUG-048 siga abierto.** Reverificado hoy:
> producción sigue devolviendo 0.129 / D3. No cambia la entrega; cambia lo que podemos
> afirmar frente al profesor.

22 casos nuevos (`test_prediccion_client.py` + `test_frontend_panel_ml_streamlit.py`), cada
guarda validada reintroduciendo su defecto: convertir el `cluster` nulo en `0`, mover el
umbral a 0.50, y tratar el 404 como error genérico. Las tres fallan cuando deben.

## 3. BUG-049 — la causa raíz no era la que yo había registrado

Lo registré el 4-sep como *"ajustar `alto`/`ancho` contra el navegador"*. **Estaba mal.**

`_layout_grilla()` ponía **cada chart en su propia fila**, así que el `ancho` declarado en
los YAML no servía para nada: cuatro tarjetas de `ancho: 3` —escritas para ir lado a lado y
sumar 12— se apilaban una debajo de otra, cada una ocupando 3/12 con nueve doceavos vacíos
a su derecha.

Verificado contra el tablero desplegado **antes** de tocar nada: DB-03 tenía **11 charts en
11 filas**, con anchos 3,3,3,3,6,6,12,6,6,6,6. El patrón de agrupación ya estaba declarado;
nadie lo leía.

Nuevo `_agrupar_en_filas()`: agrupa consecutivos mientras quepan en 12, respetando el orden.

| Tablero | Antes | Ahora |
|---|---|---|
| DB-01 | 9 filas | **3** |
| DB-02 | 7 | **3** |
| DB-03 | 11 | **5** |
| DB-04 | 13 | **5** |
| DB-06 | 8 | **3** |
| DB-07 | 7 | **3** |
| DB-09 | 7 | **3** |

**Toca 7 tableros de tres dueños distintos** (Manuel, Oscar y Marina). Por eso las guardas
son de **invariantes**, no del caso de DB-03: ninguna fila excede 12, no se pierde ni
duplica ningún chart, se respeta el orden declarado, y el árbol
`ROOT_ID → GRID_ID → ROW → CHART` conserva sus `parentId`. 18 casos.

### Se tocó una prueba de Manuel, y hay que decirlo

`test_semantic_db01_db02.py::test_el_layout_genera_estructura_v2` **codificaba el
comportamiento defectuoso**: con dos charts de ancho 3 y 6 —que suman 9 y caben juntos—
exigía `["ROW-0", "ROW-1"]`. Su intención declarada es el árbol v2, y esa se conserva
entera; lo que cambió es esa aserción incidental. Cambio acotado sobre `tests/**`, que es
amarillo, y avisado aquí y en el PR.

## 4. US-215a: 21 de 22 casos

Los casos 1.9 y 1.10 (saltos a DB-06 y DB-09) quedaron cerrados **con datos, no solo con
estructura**: aplicando el filtro que lleva cada link, `db06_predicciones_escuela` y
`db09_cubo_recomendaciones` pasan de **145 filas a 2**, todas del CCT de origen.

La razón por la que no se probaron el 4-sep —los charts quedaban al final de un scroll
larguísimo— **era BUG-049**, ya corregido.

Queda **un solo caso**: el contraste (3.1), que depende de **BUG-050** y no se puede cerrar
mientras `UX_Guidelines.md` siga vacío. Sin paleta declarada no hay criterio de aceptación.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Archivos creados:** `src/frontend/prediccion_client.py`,
  `tests/test_prediccion_client.py`, `tests/test_frontend_panel_ml_streamlit.py`,
  `tests/test_layout_filas_bug049.py`, este DevLog
- **Modificados:** `src/frontend/pages/2_Panel_ML.py`, `superset/sync_semantic_layer.py`,
  `tests/test_semantic_db01_db02.py`, `vault/06_Quality_Testing/Bug_Register.md`,
  `vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB03_DB04.md`,
  `vault/_DevLog/_index.md`, `vault/02_Requirements/Traceability_Matrix.md`
- **Herramienta compartida:** `sync_semantic_layer.py` afecta a 7 tableros de 3 dueños.
  **Conviene que Manuel Serranía y Oscar Quiroz revisen visualmente los suyos** antes del
  merge: el cambio es de layout, no de datos, pero cambia cómo se ven.
- **Decisiones autónomas:** entregar US-207 con ML-03 como `SIN_DATO` en vez de esperar a
  US-321; corregir la causa raíz de BUG-049 en vez de tunear alturas a ciegas; actualizar
  la aserción de Manuel en vez de relajar la mía.
- **Correcciones propias:** dos pruebas mías fallaron por mirar la prosa en vez del código
  (una buscaba una ruta que aparecía en un docstring; la otra comparaba docstrings por
  valor cuando `ast.get_docstring()` los devuelve limpiados). Ambas corregidas.

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] 40 casos nuevos, cada guarda validada reintroduciendo su defecto
- [x] Verificado contra la API real (local y producción), no solo con dobles
- [x] `vault_lint.py` ✅ · `ruff` ✅ · **963 pruebas** en verde

## Bloqueantes

- **Manuel Serranía:** llenar la paleta de `UX_Guidelines.md`. Es lo único que impide
  cerrar BUG-050 y con él el último caso de US-215a.
- **Manuel y Oscar:** revisión visual de sus tableros tras el cambio de layout.
- **Edgar Coronel:** ratificar el alcance de US-207 (2 de 3 modelos, ML-03 declarado).
- **Luis Téllez / Diana Alvarez:** BLOCK-005 y BUG-048 siguen abiertos.

## Próximos pasos

- Que Edgar confirme el alcance de US-207 antes del freeze.
- Cerrar el caso 3.1 cuando exista paleta.

---

## Adenda — el documento de vault que faltaba (misma fecha)

Al verificar qué faltaba de verdad para cerrar las historias, apareció un hueco que yo no
había visto: **el entregable de US-207 no es solo código.** Su plan de sprint lo dice
textual — *"Código en `src/frontend/` + **documento en el vault con frontmatter** + fila en
la matriz"*. El código y la matriz estaban; el documento no existía.

`vault/04_UX_Design/Panel_ML_US207.md` (`DOC-PANEL-ML-US207`), listado en el `_index` de su
carpeta.

**Por qué en `04_UX_Design` y no en `03_Architecture`.** `Frontend_Architecture.md` cubre
US-207, pero es de Manuel Serranía y vive en una carpeta que **no está en el alcance de
Célula 2** — no se puede documentar ahí. Y tampoco conviene: ese documento es el canónico de
la capa web completa, y el nuevo especifica **una sola página** al nivel de detalle que la
arquitectura no baja. Es la misma relación que tienen los `Cube_Specs_*` con
`Data_Model.md`. La regla 1 queda explícita en §1 del documento: si algo se dice en los dos,
manda `Frontend_Architecture`.

### Hallazgo para Manuel Serranía

`Frontend_Architecture` §5 dice que el front hace **`POST`** a los endpoints de inferencia.
El contrato real es **`GET /api/v1/predicciones/{cct}`**, verificado en local y en
producción al construir el cliente. No se corrige desde aquí: `vault/03_Architecture/**` no
está en el alcance de C2 y el documento es suyo.

### Lo que sigue faltando de US-207

Solo la **ratificación de alcance por el PM**: la historia enuncia tres modelos y se
entregan dos con el tercero declarado. Todo lo demás del entregable está cerrado.
