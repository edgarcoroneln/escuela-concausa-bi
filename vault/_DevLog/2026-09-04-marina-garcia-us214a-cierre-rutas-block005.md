---
project: "FARO"
date: "2026-09-04"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sesión: cierre de las rutas de drill-down, corrección del análisis del umbral y alta de BLOCK-005"
touches: ["US-214a", "US-215a", "US-204", "REQ-002", "BUG-045", "DEC-006", "BLOCK-005"]
tags: [devlog, bi, dashboards, superset, drill-down, celula-2]
---

# DevLog — 2026-09-04 — US-214a completa por mi lado, corrección del umbral y BLOCK-005

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/04_UX_Design/Cube_Specs_DB03_DB04]] §8.bis y §8.quinquies

## Contexto

Dos personas destrabaron lo mío el mismo día: Manuel Serranía agregó el filtro `cct` a
DB-06/DB-09 (PR #215) y Diana Alvarez publicó los fixtures de CONEVAL (BUG-045, PR
mergeado). Esta sesión cierra lo que dependía de ambos, y encuentra que uno de los datos
de mi propio análisis del umbral estaba sesgado.

## 1. Las dos rutas que faltaban de US-214a

`DB-03 → DB-06` y `DB-03 → DB-09` estaban `bloqueado` en el contrato porque esos tableros
no exponían filtro `cct`: sin él, el link aterrizaba en el tablero completo en vez de en la
escuela, que es justo lo que la ruta promete, así que no se shippearon.

Manuel lo agregó **al final** de sus `filtros_globales` (índice 3), solo sobre los datasets
de grano escuela (`db06_predicciones_escuela`, `db09_cubo_recomendaciones`). Con eso:

- `link_db06` en `db03_cubo_escuela_360.sql`, colocado en `KPI-17 · Detalle de la predicción`
- `link_db09` en el mismo SQL, colocado en `KPI-18 · Recomendación prescriptiva`

Ambos fijan `id_ciclo` (índice 0) y `cct` (índice 3). El de DB-09 es además el camino a la
narrativa que Edgar eligió para la demo: desde la ficha de una escuela se llega directo al
ranking prescriptivo.

**El contrato queda en 4 de 7 rutas implementadas.** Las 3 restantes nacen en tableros de
Manuel (DB-01, DB-02), así que el link va en sus archivos; para `DB-02 → DB-04` el destino
ya está listo desde la sesión anterior.

### La guarda encontró un defecto en sí misma

Al extenderla a los dos links nuevos, `test_los_indices_del_link_apuntan_a_la_columna_que_dicen`
empezó a fallar en los tres links de DB-03. **La prueba estaba mal, no el código**: escaneaba
el archivo `.sql` completo buscando `NATIVE_FILTER-US203-N`, y ahora ese archivo define
**tres** links con índices distintos — así comparaba los índices de un link contra los
filtros del tablero de otro.

Corregida con un helper que acota el fragmento de cada link antes de validarlo. Es la
segunda vez que esta suite se caza a sí misma (la primera fue el `sin_comentarios` que
buscaba `cct` dentro de un comentario), y ambas veces salió porque las guardas se validan
reintroduciendo el defecto en vez de darlas por buenas.

### Cómo se probó

24 casos, con falsificación de los dos escenarios nuevos:

| Defecto reintroducido | ¿Lo cazó? |
|---|---|
| Apuntar `link_db06` al índice 2 en vez del 3 | ✅ |
| Que Manuel quitara el filtro `cct` de DB-06 | ✅ |

Verificado además contra el Superset desplegado: **los 4 links, 8 de 8 destinos correctos**,
decodificando el RISON con `prison` y contrastando contra `native_filter_configuration` real.

**BUG-037 volvió a pegar** (tercera vez): las columnas nuevas no llegan al esquema del
dataset y los charts revientan con `Columns missing in dataset`. Mitigado a mano con
`PUT /api/v1/dataset/<id>/refresh`; tras eso, 103 charts con datos.

## 2. Corrección de mi análisis del umbral

El fix de CONEVAL de Diana cambió un dato que yo había publicado, y Edgar ya había
ratificado citándolo. **La conclusión no cambia; el dato de apoyo sí.**

Escribí que *"la escuela peor proyecta −4.37 %, ninguna llega a −5 %"*. Eso lo medí cuando
**D1 estaba vacío en las 145 escuelas** por BUG-045, con ML-01 entrenando con 4 de 6
drivers. No era representativo.

Con los fixtures de Diana:

| | Sin D1 (medición original) | Con D1 (correcta) |
|---|---|---|
| Riesgo máximo | 0.5615 | **0.7423** |
| `escuelas_en_riesgo` | 0 | **2** |
| ML-01 MAE | 0.0818 | 0.0844 |
| ML-02 F1 macro | 0.4859 | 0.6458 |

Y las dos que cruzan lo hacen **por la razón correcta**: proyectan **−7.60 %** y **−6.19 %**,
mientras la de riesgo 0.538 (−4.00 %) no cruza. **La calibración de DEC-006 queda verificada
empíricamente**, no solo por lectura del código de C3.

En producción sigue en cero (`escuelas_en_riesgo: 0`, esos CCT allá tienen riesgo 0.129 y
0.098): los fixtures son sintéticos y su distribución no representa a las ~132 000 escuelas
reales.

> **CORRECCIÓN (2026-09-05, señalada por Edgar Coronel).** Aquí escribí *"el número de la
> demo será el de producción"*, y está mal — es el mismo error que este DevLog corrige, una
> capa más abajo. **Producción sirve el Gold anterior al fix de BUG-045, con D1 vacío**:
> misma contaminación que volvió no representativa mi medición de −4.37 %. Verificado el
> 2026-09-05: `indice_completitud_drivers` 0.1966 en producción contra 0.6485 en local.
> Los 0.129 y 0.098 salen de ese mismo Gold empobrecido, así que **no sabemos qué dará
> `escuelas_en_riesgo` allá después del refresco**. Registrado como BUG-048, va con
> BLOCK-005. Detalle en [[vault/04_UX_Design/Cube_Specs_DB03_DB04]] §8.quinquies.3.bis.

Esto **mejora el argumento** en vez de debilitarlo: ya no hay que decir *"nadie cruza,
confíen en que está calibrado"*; se puede mostrar un caso donde sí dispara, a −7.60 %.
Responde por adelantado la pregunta obvia ante un KPI en cero.

**Edgar ratificó: DEC-006 no se reabre**, banda "atención" descartada, y para la demo se usa
el ranking prescriptivo. Registrado en §8.quinquies.5. No queda trabajo de C2 por eso.

## 3. Verificación cruzada del fix de Diana

Antes de dar por bueno BUG-045 lo probé de punta a punta, cargando sus fixtures en la base
local: `silver.rezago_municipio` pasa de 0 a 12 filas, D1 de 145/145 `SIN_DATO` a 145/145
con dato, y `gold.dim_municipio` gana 10 municipios con pobreza y rezago — lo que cierra el
caso 2.7 de US-215a (KPI-14, que salía vacío).

El ambiente local ahora **reproduce exactamente los números de Héctor** (MAE 0.0844, F1
0.6458, 5 de 6 drivers). El repo se reproduce solo, sin los Excel de nadie: era justo lo
que BUG-045 pedía.

## 4. BLOCK-005 — los cubos no existen en Cloud SQL

Dado de alta. **Ningún tablero puede apuntar a producción** porque el import de L1 subió las
10 tablas de Gold y **0 matviews**, y los datasets virtuales leen `gold.cubo_*` y nunca
`gold.fact_*` (regla 1 de `superset/README.md`, protegida por `test_semantic_repunteo_cubos`).

**Diagnóstico corregido.** El DevLog de L1 dice que *"los 9 cubos referencian silver/bronze
ausentes en el import"*. Verificado dependencia por dependencia: **eso aplica solo a
`cubo_pipeline`** (DB-10). Los otros **8** —incluidos los dos míos— leen únicamente dims,
`fact_escuela_ciclo` y `gold.predicciones`/`recomendaciones`: **todo ya está importado**.

No hace falta subir silver ni bronze. Basta materializar 8 cubos contra lo que ya está. Es
un trabajo bastante menor de lo que parecía, y a dos días del freeze la diferencia importa.

No lo ejecuto yo: la instancia es de **solo IP privada** y no tengo credenciales ni ruta de
red. Dueños propuestos: Luis Téllez (acceso o ejecución) y Diana Alvarez (validar modelos).

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Archivos creados/modificados:** `superset/semantic/db03_cubo_escuela_360.sql`,
  `superset/semantic/metrics_db03_db04.yaml`, `superset/dashboards/db03_ficha_escuela.yaml`,
  `tests/test_drill_down_db03_db04.py`, `vault/04_UX_Design/Cube_Specs_DB03_DB04.md`,
  `vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB03_DB04.md`,
  `vault/10_Risk_Governance/Blocker_Register.md`, este DevLog, `vault/_DevLog/_index.md`,
  `vault/02_Requirements/Traceability_Matrix.md`
- **Fuera de alcance, no editado:** los YAML de DB-06/DB-09 (de Manuel: solo se leyeron sus
  índices), `dbt/**` y los fixtures de C1 (se ejecutaron para verificar, no se modificaron),
  `vault/12_Roadmap_Sprints/**`, `Decision_Log.md`.
- **Decisiones autónomas del agente:** colocar cada link en el chart temáticamente
  correspondiente (predicción → DB-06, recomendación → DB-09) en vez de agruparlos;
  corregir la prueba en vez de relajarla cuando falló.

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] 24 casos de drill-down, cada guarda validada reintroduciendo su defecto
- [x] Verificado en vivo contra Superset: 4 links, 8/8 destinos correctos
- [x] `vault_lint.py` ✅ · `ruff` ✅ · suite completa en verde

## Bloqueantes

- **BLOCK-005** (Luis Téllez / Diana Alvarez): materializar 8 cubos en Cloud SQL.
- **BUG-037** sigue `open` (Manuel Serranía): tercera vez que obliga a refrescar datasets
  a mano tras agregar columnas.
- **Manuel Serranía**: las 3 rutas restantes del contrato nacen en DB-01/DB-02, sus archivos.

## Próximos pasos

- Sesión de navegador para cerrar el §3 de US-215a (10 casos de accesibilidad y usabilidad).
- US-207: pendiente de acordar alcance con el PM.

---

## Adenda — sesión de navegador de US-215a (misma fecha)

Marina corrió la primera pasada real con navegador. **De 22 casos, 19 verificados.**

**Lo que se confirmó en vivo**, y no se podía por API: AC-002.4 (la ficha por CCT funciona
con sus 6 drivers, predicción y recomendación), el salto DB-03 → DB-04 con municipio y
ciclo preseleccionados, y **el §3 completo de accesibilidad**. El caso 3.4 —el que más
riesgo tenía, porque el link es un `<a href>` inyectado con `allow_render_html` y no un
control nativo de Superset— **se alcanza con Tab y se activa con Enter**.

**Dos bugs nuevos**, ambos `low` y de presentación, ninguno de datos:

- **BUG-049**: tarjetas alineadas al fondo con hueco vertical, y tablas anchas que exigen
  scroll horizontal para llegar a las columnas de link. Es de C2 y requiere ajustar contra
  el navegador, no a ciegas: la altura correcta depende de cuántas filas devuelve cada tabla.
- **BUG-050**: Lighthouse 93 — contraste insuficiente y `<html>` sin `[lang]`. Dos dueños
  distintos: el `lang` lo emite el shell de Superset (C5), y el contraste no se puede cerrar
  porque **no hay paleta declarada**: `UX_Guidelines.md` sigue vacío con `source_of_truth: true`.

**Un hallazgo de interpretación que no es defecto.** La escuela `15DJN0049A` muestra
`KPI-02 = +26.7 %` y a la vez `en_riesgo = true`. Verificado contra la base: ambos correctos
—creció 26.7 % el ciclo pasado (114 contra 90) y el modelo proyecta −7.60 %—, pero juntos
**se leen como contradicción**, porque la tarjeta no dice cuál es histórico y cuál pronóstico.
Propuesta: rotular `KPI-02` como "observado" y `KPI-17` como "proyectado". Toca el catálogo
de KPIs, así que es de Manuel Serranía.

Quedan **3 casos pendientes**: los saltos a DB-06 y DB-09 (los links se ven bien y su
estructura está verificada por API, pero los charts quedan al final del scroll y no se probó
el salto) y el contraste, que depende de BUG-050.
