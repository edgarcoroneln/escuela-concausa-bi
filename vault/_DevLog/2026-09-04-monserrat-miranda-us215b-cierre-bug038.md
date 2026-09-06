---
project: "FARO"
date: "2026-09-04"
author_human: "Monserrat Xcaret Miranda Olivas"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sesión larga: contextualización tras la reestructura, ambiente local desde cero, cierre de US-215b y corrección de BUG-038 validada en navegador real"
touches: ["US-215b", "US-213", "US-214b", "REQ-002", "BUG-038", "BUG-051", "BUG-047"]
tags: [devlog, bi, dashboards, superset, qa, accesibilidad, celula-2]
---

# DevLog — 2026-09-04 — US-215b cerrada y BUG-038 corregido

→ [[vault/_DevLog/_index|Volver al índice]]

## Contexto

Primera sesión después de la reestructura del repositorio. Arrancó como contextualización pura
(leer AGENTS/CLAUDE/Vault_Rules/ownership/Agent_Context antes de tocar nada) y terminó cerrando la
única historia que quedaba abierta, más el bug `high` que la bloqueaba.

## 1. Punto de partida: tres cosas no eran lo que parecían

- **La rama `dev/monserrat-miranda` sí existía.** El diagnóstico inicial dijo que no, y era falso:
  el clon local nunca había corrido `git fetch`, así que no veía ninguna rama `dev/*` del remoto.
  La creó el PM en el commit de gobernanza `78695f7` (US-001) y nunca se usó: **0 commits propios,
  242 de atraso**. Se adoptó y se sincronizó con `git merge origin/main` (fast-forward, sin
  `rebase` ni `--force`). Las 4 ramas `feat/monserrat-olivas-*` —que violan la regla 8 y usan el
  apellido materno— están 100 % mergeadas y **no se borraron**: sostienen los diffs de los PRs
  #73/#78/#114/#161/#162.
- **US-214b ya estaba `done`** en el tablero del PM desde el 3-sep; la §9 del plan de sprint decía
  "90 %". Sincronizado.
- **La única historia abierta era US-215b**, y sus dos casos en ❌ dependían de BUG-038.

## 2. Ambiente local desde cero

Se levantó siguiendo [[vault/00_Start_Here/Runbook_Ambiente_Local]] (el runbook de BUG-012,
publicado ese mismo día) tras un `docker compose down -v`. **Las siete cifras de control salieron
exactas**: `fact_escuela_ciclo` 145 · `features_escuela` 145/3 ciclos · ML-01 MAE 0.0844 con 55
predicciones · ML-02 F1 macro 0.6458 · 8 de 9 cubos · 103 charts / 9 tableros · `matricula_total`
11 828. Importa para lo que sigue: la evidencia de abajo corre sobre un Gold íntegro.

Tres fricciones reales del camino, ninguna del alcance de C2 (ver §6):

1. **El runbook no corre en Windows sin `PYTHONUTF8=1`** — `dbt` truena con `UnicodeDecodeError`
   leyendo `dbt_project.yml` con el locale cp1252.
2. **La imagen de `api` estaba en crashloop** por `ModuleNotFoundError: No module named 'limits'`.
   `slowapi>=0.1.9` sí está declarado en `requirements.txt`; la imagen se había construido antes de
   que se agregara y nada fuerza el rebuild.
3. `docker compose up -d --build api` **recreó también `db`**, perdiendo en silencio una carga de
   Bronze recién hecha. Se detectó porque `dbt run` reportó que `bronze.formato911_2024_2025` no
   existía pese a que el cargador había confirmado 242 filas.

## 3. BUG-038 — eran dos defectos, no uno

Las dos hipótesis probadas el 30-ago fallaron porque **cada una tapaba sólo la mitad**:

| # | Defecto | Síntoma |
|---|---|---|
| A | `ROOT_ID` se declaraba `type: "TABS"`; Superset espera `ROOT` con el contenedor de tabs como nodo aparte | No dibuja la barra: D2-D6 inalcanzables |
| B | Se interponía un `GRID-<id>` entre cada `TAB` y sus `ROW`; con tabs las filas cuelgan **directo del TAB** | Contenido de los tabs en blanco |

La hipótesis (1) del 30-ago corrigió A y por eso apareció la barra, pero dejó B: de ahí que todos
los tabs salieran vacíos. El árbol quedó `ROOT_ID(ROOT) → TABS-ROOT(TABS) → TAB-<id> → ROW → CHART`.

**Cambio aditivo**, conforme al acuerdo con Manuel Serranía (US-202): `_layout_grilla()` no se tocó
y los 8 tableros del camino plano no cambian.

### Los tests estaban en verde y mentían

`test_layout_tabs_arma_root_de_tipo_tabs` afirmaba `ROOT_ID.type == "TABS"`: **codificaba el defecto
como comportamiento esperado**. Por eso el sync pasaba en verde mientras el tablero estaba roto en el
navegador. Eran **3** los tests que fijaban la estructura defectuosa (el registro decía 1) más 3 que
dependían del `GRID`. Se reescribieron los 6 y se añadieron dos guardas por defecto:
`test_layout_tabs_root_es_root_y_cuelga_del_contenedor_de_tabs` y
`test_layout_tabs_sin_grid_intermedio_entre_tab_y_filas`.

### Verificado en navegador real, que es la lección del bug

- Los **6 tabs** se dibujan y son navegables; D4 carga sus 6 charts con nota propia.
- Los valores son de cada tab, no heredados: D1 → 52.7 % / 18 escuelas, D4 → 30.9 % / 17.
- **Los filtros globales ya llegan a los charts**: con `nombre_entidad = 'Jalisco'`, KPI-07 pasa de
  52.7 % a 0.0 % y las escuelas de 18 a 0. **Contrastado contra la base**: `gold.cubo_driver` da
  para Jalisco/D1/2024-2025 `escuelas_driver = 0` sobre `total_escuelas = 7`, y el tile muestra 7.

## 4. US-215b — 13 de 13 casos ejecutados

12 ✅ · 1 ⚠️ · **0 ❌**. Siguiendo el patrón de Marina García en US-215a: verificar por datos/API lo
verificable y no marcar nada sin correrlo.

- **2.4** (`SIN_DATO` nunca cero) se cerró con la prueba discriminante: **309 filas** marcadas
  `SIN_DATO` y **ninguna** con valor, conviviendo con **60 ceros legítimos** en filas `OK`. El cero
  real existe y no se confunde con el hueco.
- **2.1 se reescribió antes de ejecutarlo.** Su esperado era anterior a BUG-047 y habría marcado una
  falla falsa: el Ciclo hoy llega preseleccionado a propósito. De paso se revisó la regresión que
  Marina advirtió —los IDs de filtro van por posición—: `link_db08` sigue apuntando a `-3`/`-4`,
  los índices reales.
- **3.3** pasa: el foco visible de Superset es un `box-shadow`, no un `outline` (que es `none`).
  Quien audite mirando sólo `outline` concluiría falsamente que no hay indicador. Además, un
  `.focus()` programático no dispara `:focus-visible` y no sirve para verificar este caso.
- **3.1 ⚠️** → BUG-051 nuevo (abajo). Medido en **ambos temas**: el tab activo está **peor en
  claro (3.55:1) que en oscuro (4.07:1)**, así que no se resuelve fijando un tema por defecto.
- **3.2 ✅, y el proceso importa.** La alcanzabilidad se midió (6/6 tabs y 3/3 filtros en el orden
  de tabulación, cada tab anunciado como "Tab N of 6"), pero la **activación** quedó deliberadamente
  sin marcar: el navegador automatizado no entregaba ni clic ni `Enter` a los tabs de React, aunque
  un `.click()` del DOM sí funcionaba, y con ese instrumento no se podía separar el defecto del
  artefacto de medición. **La autora lo verificó a mano en Chrome: `Tab` + `Enter` sí cambia de
  pestaña.** Era artefacto, no defecto — de haberlo marcado ❌ se habría abierto un bug inexistente.
  Salvedad: las flechas ← → no navegan entre tabs (patrón ARIA incompleto de Superset, no bloquea).

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Archivos creados/modificados:** `superset/sync_semantic_layer.py`,
  `tests/test_semantic_db05_db08.py`,
  `vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB05_DB08.md`,
  `vault/06_Quality_Testing/Bug_Register.md`,
  `vault/12_Roadmap_Sprints/Sprints/2-monserrat-xcaret-miranda-olivas.md`, este DevLog,
  `vault/_DevLog/_index.md`, `vault/02_Requirements/Traceability_Matrix.md`. Fuera del repo:
  `~/.dbt/profiles.yml` (tenía `schema: dev` donde el runbook exige `public`).
- **Herramienta compartida:** se tocó `sync_semantic_layer.py`, que usan los 10 tableros. El cambio
  es aditivo, el camino plano quedó intacto y hay guardas de regresión, pero **Manuel Serranía va
  como reviewer del PR**, como él pidió al aprobar la opción A de US-213.
- **Fuera de alcance, no editado:** `src/**`, `dbt/**`, `.github/**`, `vault/_Meta/**`. Los scripts
  de `src/ingesta` y `src/modelos` se **ejecutaron** para poblar el ambiente, no se modificaron.
  El `.env` no se leyó ni se editó: las credenciales sólo se cargaron como variables de entorno.
- **Decisiones autónomas del agente:** ninguna de fondo sin aprobación. Se detuvo a preguntar antes
  de crear la rama, antes de `down -v` y antes de tocar archivos. **Se negó a hacer login en
  Superset** (escribir contraseñas en un formulario) y a transcribir el `.env` al chat; el login lo
  hizo la autora.
- **Corrección registrada:** el primer diagnóstico afirmó que `dev/monserrat-miranda` no existía.
  Era falso —faltaba `git fetch`— y quedó corregido arriba y en el plan de la sesión.

## Seguridad / calidad

- [x] `pytest tests/ -q` → **886 passed, 7 skipped, 0 failed**
- [x] `pytest tests/test_semantic_db05_db08.py` → 54 passed
- [x] `ruff check superset/ tests/` → limpio
- [x] `python vault/_Meta/scripts/vault_lint.py .` → ✅ Vault limpio
- [x] `check_ownership.py --autor monserratxmiranda` → identidad, rama y alcance correctos
- [x] Sin secretos hardcodeados; el `.env` nunca se leyó ni se pegó en un prompt
- [x] Validado en vivo contra Superset 6.1.0 real, no sólo por API ni por prueba estática

## Bloqueantes

- **Manuel Serranía (TL C2):** revisión del PR por `sync_semantic_layer.py`. Además, **BUG-037 sigue
  sin dueño formal**: el registro dice "pendiente de dueño del script", Marina lo lista como
  bloqueante suyo, y lo reportó esta autora. Aparece ya en el runbook de ambiente local como
  problema conocido, así que le pega a todo el equipo.
- **Edgar Coronel (PM):** los hallazgos de §6, todos fuera del alcance de C2.

## Hallazgos fuera de alcance — reportados, no corregidos

1. **`guia-ambiente-local/` no está en ningún verde/amarillo/comunes de `ownership.yml`.**
   Verificado ejecutando la propia `coincide()` de `check_ownership.py` contra las 21 personas:
   `VERIFICACION.md` y `configuracion.env` **no están permitidos para ninguna**. Es el quinto caso
   del patrón que `ownership.yml` ya documenta cuatro veces (Accessibility.md, Data_Lineage_US106,
   US-521b, requirements.txt) y está **resuelto a medias**: el 4-sep se agregó a `comunes` el
   archivo `vault/_Meta/US-521b-guia-ambiente-local.md`, pero no la carpeta de la raíz — que es de
   **la misma entrega y el mismo dueño** (Edgar Jiménez, según el frontmatter de `VERIFICACION.md`).
   Su propio autor no puede actualizar su anexo.
2. ~~`guia-ambiente-local/configuracion.env` versionado~~ — **retirado: no es un hallazgo.** Se
   reportó como incumplimiento de `Secrets_Policy`, pero al verificar el CI antes de dar el aviso
   resultó que el equipo ya lo había resuelto el 3-sep: `ci.yml` lleva una **excepción explícita**
   (`grep -vxF 'guia-ambiente-local/configuracion.env'`) con la justificación escrita en el propio
   workflow —contenido verificado sin secretos, y GitLeaks lo sigue escaneando por contenido, así
   que la excepción es del nombre de archivo, no del escaneo—. Se anota el error en lugar de
   borrarlo: la lectura parcial de un comando multilínea del CI casi produce un aviso falso de
   "PRs bloqueados" a dos días del freeze.
3. ~~Tres documentos de ambiente local, posible choque con la regla 1~~ — **retirado: no es un
   hallazgo.** Al revisar el contenido resultó que los tres tienen alcances distintos y
   trazabilidad correcta: `Runbook_Ambiente_Local.md` cubre db/api/superset/dbt (canónico,
   `source_of_truth`), `US-521b-guia-ambiente-local.md` cubre Airflow y jobs ML, y
   `VERIFICACION.md` es su anexo con `traces_up` explícito hacia ella. Eso es exactamente lo que
   la regla 1 pide, no lo que prohíbe. El reporte inicial se hizo por los nombres de archivo,
   sin comparar los contenidos.
4. **El runbook no corre en Windows** sin `PYTHONUTF8=1` (§2). Tercera aparición del patrón de
   BUG-005 y BUG-011.
5. **La imagen de `api` queda obsoleta en silencio** (§2): ni el compose ni el runbook fuerzan
   `--build`, y `up --build <servicio>` recrea otros servicios llevándose datos.
6. **BUG-018 tiene la fila mal formada** (`Bug_Register.md`): severidad `high`, estado `open`, y
   `**fixed**` escrito en la columna de US. Se cuenta como abierto en cualquier conteo. Es de C3.
7. **`vault/04_UX_Design/UX_Guidelines.md` está vacío con `source_of_truth: true`.** Ya lo reportó
   Marina. Pega directo aquí: sin paleta oficial no hay contra qué ratificar el color de BUG-051.

## Próximos pasos

1. Avisar a Manuel (BUG-038 + dueño de BUG-037) y al PM (hallazgos de arriba) antes del PR.
2. ~~Comprobación humana de §3.2 y tema claro en §3.1~~ — ambos cerrados el mismo día.
3. PR desde `dev/monserrat-miranda` con Manuel como reviewer.
