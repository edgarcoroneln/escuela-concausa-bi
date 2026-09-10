---
project: "FARO"
date: "2026-09-09"
author_human: "Manuel Alejandro Serranía Reinada"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — diseñar y construir la sección 'Cómo funciona' de FARO Web (hotfix): endpoint /api/v1/about/* (manifest + sobre genérico de bloques), repositorio de conteos en vivo por capa, cliente y página nuevos en el frontend, pruebas de contrato y del cliente."
touches: ["US-225", "US-601", "REQ-001", "REQ-002", "ADR-002", "DOC-RUNBOOK-LOCAL"]
tags: [devlog, celula-2, hotfix, backend, frontend, us225, us601, s7, runbook, dbt]
---

# DevLog — 2026-09-09 — Sección "Cómo funciona" (US-225, hotfix)

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

Se agregó a FARO Web una sección pública que explica los componentes del backend, el modelo de
datos (diagrama E-R), las capas bronze/silver/gold (con conteo de filas en vivo), los cubos de
Gold, la memoria técnica y un resumen de ADRs y de los tres Model Cards de ML. Fue pedido como
hotfix un día antes de la demo, con la restricción explícita de que corre en paralelo con cambios
de otras células (Gold, ADRs, Model Cards), así que el contrato entre backend y página se diseñó
como un **manifest + sobre genérico de bloques** en vez de un endpoint por sección: agregar,
quitar o reordenar una sección es un cambio de backend únicamente. Detalle completo del diseño en
`PLAN_US225_COMO_FUNCIONA.md` (raíz del repo, se borra antes del PR).

**Archivos nuevos:**
- `src/api/repositorio_about.py` — único dato vivo: conteo de filas por tabla de bronze/silver/gold.
- `src/api/v1/about.py` — router `/api/v1/about/secciones` (manifest) y `/secciones/{id}` (sobre genérico).
- `src/frontend/about_client.py` — cliente HTTP, mismo patrón que `prediccion_client.py`.
- `src/frontend/pages/4_Como_Funciona.py` — página con renderer genérico por tipo de bloque.
- `tests/fixtures_about.py`, `tests/test_about_client.py`.

**Archivos modificados:** `src/api/v1/__init__.py` (registra el router, público siempre,
independiente de `AUTH_LECTURA_PUBLICA`), `src/frontend/app.py` (cuarta tarjeta de acceso rápido),
`tests/test_api_contract.py` (pruebas del contrato de `/about/*`), `api/openapi.v1.json`
(regenerado).

## 🤖 Sesión de IA
- **Agente / modelo:** Claude Code / claude-sonnet-5.
- **Archivos creados/modificados:** ver arriba.
- **Decisiones autónomas del agente:** ninguna fuera de lo acordado explícitamente en el plan
  (todas las decisiones de diseño —manifest genérico, contenido fijo por ahora, endpoint público,
  fuente de los Model Cards— se revisaron con el usuario antes de escribir código).
- **Correcciones manuales:** ninguna todavía; pendiente de revisión por Christian Ruiz (C4, dueño
  de `src/api/**`) y de que Edgar Coronel dé de alta formalmente US-225.
- **Prompt inicial:** "hay que evaluar el repo, tenemos que agregar una sección a la aplicación
  web donde se pueda ver cómo funciona el backend..." (conversación completa en
  `PLAN_US225_COMO_FUNCIONA.md`).

## Corrida local del pipeline (verificar la sección con datos reales, no mocks)

Para ver la pestaña "Capas" con números reales en vez de `SIN_DATO` se siguió al pie de la letra
`vault/00_Start_Here/Runbook_Ambiente_Local.md` (`docker compose up -d db` + fixtures de
`tests/fixtures/` + `dbt seed`/`dbt run --full-refresh` + `publicar_gold --desde-gold` + cubos).
Resultado: 1,016 filas en Bronze, 515 en Silver, 3,297 en Gold, `matricula_total: 11828` — coincide
con las cifras que documenta el runbook. Solo `cubo_pipeline` queda `SIN_DATO` (falta el Parquet
real de CONAGUA, techo conocido y documentado en el propio runbook §5). Todo en el Postgres local
de esta máquina (`docker-compose`), nada tocó datos compartidos.

**Dos hallazgos reales en el camino, ambos corregidos:**

1. **`Runbook_Ambiente_Local.md` quedó desactualizado** (dueño: Edgar Coronel, `vault/00_Start_Here/**`
   es su alcance verde, no el de Manuel — excepción de la misma naturaleza que la de `src/api/**`,
   pendiente de que Edgar la revise/formalice). `dbt/models/sources.yml` cambió el `identifier` por
   default de `sesnsp`/`conapo` de vuelta a esos nombres "reales" (antes `sesnsp_test`/
   `conapo_sample`) después de que el runbook se verificó el 04-sep. Se corrigió la tabla de §3.2 y
   se agregó una nota fechada explicando el porqué y cómo diagnosticarlo si vuelve a pasar con otra
   fuente.
2. **`gold.predicciones`/`gold.recomendaciones` tenían un esquema viejo** (de una corrida anterior
   de otra persona del equipo en este mismo Postgres local, sin `cve_mun`/`nivel` de DEC-010).
   Autorizado por el usuario: `DROP TABLE ... CASCADE` de esas dos tablas derivadas (arrastró 7
   vistas materializadas de cubos, todas reproducibles por `dbt run --select "gold.cubo_*"`) +
   re-ejecución de `publicar_gold.py` y de los cubos. No se tocó ninguna tabla de Bronze/Silver ni
   dato fuente.

## Diagramas E-R de Bronze y Silver (pedido explícito del usuario)

Se agregaron dos bloques `mermaid` más a la sección `capas` de `src/api/v1/about.py`:

- **Bronze**: tablas de aterrizaje independientes (sin FK real entre ellas); las relaciones se
  dibujan **punteadas** (`..`, no-identificantes en la sintaxis de mermaid) para dejar claro que es
  la llave natural que Silver usará para conformar, no una restricción de Postgres. Incluye
  `bronze.conagua_presas` marcada explícitamente como `SIN_DATO` en este ambiente, en vez de
  omitirla.
- **Silver**: mismas fuentes ya conformadas por `cct`/`cve_mun` (verificado contra
  `dbt/models/silver/*.sql`, no inventado). Las relaciones hacia `aire_estacion`/`agua_region`
  también van punteadas con la nota "IDW ADR-006, no FK": D5/D6 se asignan por interpolación
  espacial, no por coincidencia de llave — un `JOIN` sólido ahí sería una afirmación falsa sobre
  cómo se calculan esos dos drivers.

## Ronda 2 — retroalimentación visual tras revisar la página (mismo día)

El usuario revisó la página funcionando y pidió, en un solo mensaje: narrativa de células en
`arquitectura`; mapa de los 4 estados + mejor explicación de `fact_escuela_ciclo` + explicación de
los drivers en `modelo-datos`; fuentes de bronze + más visual + los 3 E-R (bronze/silver/gold)
titulados y con narrativa de "qué cambia" + total de filas en `capas`; y reemplazar la tabla de
`cubos` por un diagrama. Aclaró también una restricción de arquitectura importante: **Streamlit se
va a dejar de usar pronto** (migración a React/Angular) — por eso todo lo visual nuevo se construyó
como D3 vía HTML embebido (`components.html`, mismo patrón que el mermaid existente), no como
widgets nativos de Streamlit, que se perderían en la migración.

**Tres tipos de bloque nuevos** en el sobre genérico (`src/api/v1/about.py` +
`src/frontend/about_client.py`, con `BloqueDesconocido` cubriendo hacia atrás cualquier cliente que
no los reconozca todavía):

- `mapa` — reutiliza `superset/assets/geojson/municipios_scope.geojson` (ya versionado, INEGI/
  CONABIO vía PhantomInsights/mexico-geojson MIT, ya usado por el coroplético de Superset). Cero
  llamada de red nueva: se lee del disco y se cachea (`functools.lru_cache`). Solo los 4 estados de
  `SCOPE_ENTIDADES` coloreados, sin fondo nacional (decisión explícita: no hay fuente de las 32
  entidades en el repo y no se iba a inventar una URL).
- `jerarquia` (icicle D3) — árbol Total → capa → tabla con los conteos de
  `repositorio_about.conteos_capas()`. Una tabla `SIN_DATO` recibe un **valor nominal** (1% del
  total conocido) solo para que el rectángulo sea visible/clicable, coloreado distinto (patrón de
  rayas) — el dato real sigue siendo `null`, el nominal es puramente de layout (`disponible: false`
  es la señal real, nunca se disfraza de conteo).
- `diagrama_flujo` — 3 columnas con curvas y resaltado al pasar el mouse. Para cubos: tablas
  fuente (verificadas contra el `FROM`/`JOIN` real de cada `dbt/models/gold/cubo_*.sql`, no
  inventadas) → 9 cubos → 10 dashboards.

**Contenido nuevo verificado contra fuente real, no inventado:** narrativa de las 5 células
(`ownership.yml` + `avisosequipo.md`), los 6 drivers (CLAUDE.md §4, no se había usado antes), las 8
fuentes de bronze (CLAUDE.md §4), y la tabla fuentes-por-cubo. El E-R de gold ahora vive tanto en
`modelo-datos` (estructura) como en `capas` (progresión) — misma figura (`_ER_GOLD_MERMAID`,
constante compartida para que no se desalineen), dos preguntas distintas.

Verificado estructuralmente vía `curl` contra la API real (317 municipios/4 resaltados en el mapa,
34 nodos/63 enlaces en el diagrama de cubos, jerarquía + 3 E-R titulados en capas) y con la suite
completa en verde. **No verificado visualmente en navegador por el agente** (sin herramienta de
captura de pantalla en esta sesión): la corrección del layout/D3 real queda pendiente de que el
usuario la revise en `http://localhost:8501/Como_Funciona`.

## Ronda 3 — retroalimentación tras ver la página en el navegador

El usuario probó la página real y reportó 3 problemas concretos:

1. **Contraste roto en mapa y cubos** ("fondo negro, letras negras"): cada bloque D3 vive en su
   propio iframe (`components.html`), documento HTML aparte sin estilos propios -- heredaba
   `prefers-color-scheme: dark` del navegador/SO, y el texto (`fill:#0f172a`, oscuro a propósito
   para fondo claro) quedaba invisible sobre un fondo igual de oscuro. Fix: `color-scheme: light`
   + fondo blanco explícito en los 3 bloques D3 (mapa, barras, diagrama de flujo) y también en
   mermaid (mismo riesgo, no reportado pero mismo bug).
2. **El icicle "no se entiende" y silver no se ve**: con gold (~3,300 filas) ~6x más grande que
   silver (~500), el icicle reparte el ANCHO por proporción y silver queda una franja de pocos
   píxeles. Se reemplazó por **barras horizontales** (bloque nuevo `barras`) -- cada capa tiene su
   propia fila de alto fijo, nunca compite por espacio con las demás. Se **eliminó**
   `BloqueJerarquia`/`NodoJerarquia` de `about.py` y `about_client.py` (no dejar código muerto).
3. **Cubos sin explicación**: se agregó un bloque `markdown` explicando las 3 columnas del
   diagrama y cómo usar el hover, antes del diagrama.
4. **Mapa: pidió fondo gris del resto de México**, tras confirmar que no había una fuente ligera
   de solo-contorno-nacional en el mirror que ya usa el proyecto. Se generó un asset nuevo,
   `superset/assets/geojson/mexico_silueta.geojson` (10 KB, decorativo, NO fronteras exactas):
   `superset/generar_geojson_silueta_nacional.py` descarga los 32 estados (mismo mirror
   PhantomInsights/mexico-geojson ya usado por `generar_geojson_municipios.py`), rasteriza todos
   los municipios sobre una rejilla de 0.05° con numpy (ya es dependencia del proyecto, nada
   nuevo) y traza el contorno con **marching squares** binario implementado a mano.

   **Bug real encontrado y corregido en el camino**: la primera versión del marching squares
   emparejaba mal los 2 casos "silla de montar" (diagonal ambigua) -- cruzaba las esquinas
   incorrectamente (`(O,N)+(S,E)` en vez de `(O,S)+(E,N)`), lo que rompía la cadena del contorno
   exactamente en esos puntos y perdía el continente completo (solo quedaban 9 islas sueltas de
   334 puntos, de 3506 segmentos generados). 3 pruebas sintéticas (cuadrado, forma en L,
   componentes separadas) pasaron con el bug porque ninguna tocaba un punto de silla -- el bug
   solo se manifestó con la geografía real de México, que sí tiene varios. Diagnosticado
   instrumentando grados de entrada/salida del grafo de segmentos (`solo fuente`/`solo destino`:
   6 y 6, exactamente los 2 casos de silla), corregido, y **verificado contra 9 ciudades reales**
   (CDMX, Guadalajara, Monterrey, Tijuana, La Paz BCS, Mérida, Cancún, Oaxaca, Villahermosa → las
   9 DENTRO del polígono) + 4 puntos fuera del país (Pacífico, Golfo, Guatemala, Caribe → los 4
   fuera). Resultado: 634 vértices, 10 KB, anillo principal cubre correctamente el continente +
   Baja California (unidos en el trazo a la resolución de 0.05°, simplificación aceptable para un
   fondo decorativo).

   `superset/**` es alcance verde de Manuel (C2) — sin excepción de ownership para este cambio.

**No verificado visualmente por el agente** (sin herramienta de captura de pantalla): verificado
por estructura (JSON vía curl, point-in-polygon contra ciudades reales) y por las pruebas
automatizadas, no por cómo se ve realmente en el navegador. Pendiente de que el usuario confirme.

## Seguridad / calidad
- [x] Sin secretos hardcodeados.
- [x] Tests agregados/actualizados: `tests/test_about_client.py` (14 casos, incluye `barras` y
  `mapa` con/sin `fondo`) + `tests/test_api_contract.py` (11 casos de `/about/*`). Suite rápida
  completa: `pytest tests/test_api_contract.py tests/test_about_client.py -q` → 54 passed.
- [x] DevLog enlaza a US-225.

## Excepción de alcance (actualizado 2026-09-10, ver "Migración a US-601" arriba)

Estado original (2026-09-09): este hotfix tocaba `src/api/v1/about.py` y
`src/api/repositorio_about.py`, entonces alcance verde de Christian Ruiz (C4) según
`vault/_Meta/ownership.yml`, no de Manuel (C2), autorizado explícitamente por el usuario como Tech
Lead de C2 de entonces.

**Ya no aplica esa lectura**: el plan de recuperación S7 reasignó esta historia como `US-601` a
Equipo 1 (Héctor Morales, líder; Manuel y Carlos Mayorga, integrantes) — el alcance de
`src/api/**`/`src/frontend/**` para este trabajo es ahora mandato de equipo, no una excepción
personal de Manuel. `ownership.yml` ya no lista a Christian sobre estos dos archivos en el contexto
de este trabajo; ver el hallazgo de inconsistencia documentado arriba (el verde/amarillo de Equipo 1
apunta a rutas de ML/agente, no a componentes backend — a reportar a Edgar). Pendiente antes de abrir
el PR:

1. Héctor Morales (dueño formal de `US-601`) confirma `src/api/v1/about.py` y
   `src/api/repositorio_about.py`, y el documento `Bosquejo_Componentes_US601.md`.
2. Héctor reporta a Edgar Coronel la inconsistencia de `verde`/`amarillo` de Equipo 1 en
   `ownership.yml`, para que la corrija si aplica.
3. Edgar Coronel revisa la corrección a `vault/00_Start_Here/Runbook_Ambiente_Local.md` (su alcance
   verde) y decide si actualiza `last_reviewed` del frontmatter — no se tocó ese campo en esta sesión
   porque implica una revisión formal que no le corresponde a quien sólo corrigió un dato
   desactualizado.

## Bloqueantes
- Ninguno de código. La confirmación de Héctor sobre el bosquejo y el reporte de la inconsistencia
  de `ownership.yml` a Edgar son bloqueantes de proceso para el PR, no de la implementación.

## Próximos pasos
- [x] Levantar `docker compose up -d db` y validar visualmente las 7 secciones en FARO Web con
  Postgres real — hecho en esta sesión, ver "Corrida local del pipeline" arriba.
- **Pendiente del usuario**: revisar visualmente en el navegador los 3 bloques D3 nuevos (mapa,
  icicle, diagrama de cubos) en `http://localhost:8501/Como_Funciona` — el agente verificó la
  estructura de datos, no el render real.
- Follow-up explícito (no bloquea esta entrega, ver
  `vault/03_Architecture/Bosquejo_Componentes_US601.md`): sustituir el contenido fijo de
  `arquitectura`, `modelo-datos`, `cubos`, `stack`, `decisiones` y `modelos-ml` por lectura en vivo
  de sus fuentes — ADRs y Model Cards son los candidatos más urgentes.

## Migración a US-601 — plan de recuperación S7 (2026-09-10)

Antes de seguir, se revisaron dos mensajes del equipo: la propuesta de storytelling "7 casos por
investigar" (Equipo 3) y un recordatorio de Equipo 1 pidiendo este bosquejo para su gate de hoy. Al
verificar contra el repo (`git fetch origin` trajo commits nuevos) aparecieron dos hallazgos:

1. **El storytelling no exige cambios a esta sección.** Su mapeo de endpoints verificado
   (`vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO.md` §10) es `/escuelas`, `/kpis`,
   `/predicciones`, `/agente/consulta` — la narrativa de riesgo por escuela no toca `/about/*`. El
   contenido de "Cómo funciona" no cambió por esto.
2. **El plan de recuperación S7 ya está en `main`**
   (`vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09.md`), reorganizando el equipo en 6
   "Equipos" nuevos: este trabajo es ahora oficialmente **`US-601`**
   (`vault/02_Requirements/User_Stories.md`, `Requirements_Detailed.md` REQ-001), reabierto por
   `DEC-022`, liderado por **Héctor Morales** (Equipo 1 · Componentes y memoria técnica), con Manuel
   y Carlos Mayorga como integrantes.

**Hallazgo de `ownership.yml` para reportar a Edgar (no bloqueante, documentado en vez de corregido
unilateralmente):** los tres integrantes de Equipo 1 (Héctor, Manuel, Carlos) tienen un `verde`/
`amarillo` casi idéntico entre sí (`src/modelos/**`, `src/agente/**`, `vault/15_ML_Models/**`,
`notebooks/**` en verde) que corresponde a rutas de ML/agente, no al mandato real de "Componentes y
memoria técnica" del gate (`src/api/**`, `src/frontend/**`, `vault/03_Architecture/**`). Parece un
efecto del refresco automático del tablero copiando el mismo bloque a los tres. Se sigue tocando
`src/api/**`/`src/frontend/**` porque es el mandato explícito de Equipo 1 en el plan de recuperación,
no como excepción personal — Manuel lo comparte con Héctor para que decida si lo reporta a Edgar.

**Cambios de esta ronda:**
- `PLAN_US225_COMO_FUNCIONA.md` se renombra a **`vault/03_Architecture/Bosquejo_Componentes_US601.md`**
  (de la raíz, prohibida por `Definition_of_Filed`, a su lugar canónico junto a `System_Design.md`,
  `Data_Model.md`, `API_Specification.md`, `Frontend_Architecture.md`, `Technical_Guide.md`, a los
  que enlaza sin duplicar). Frontmatter nuevo con `owner: Héctor Morales`, `traces_up: [US-601,
  REQ-001, DEC-022]`. Registrado en `vault/03_Architecture/_index.md`.
- El trabajo se migra de la rama no gobernada `componentes-back` (el plan de recuperación prohíbe
  crear trabajo nuevo ahí) a la rama permanente `dev/manuel-serrania`, sincronizada primero con
  `origin/main` y verificada con la suite completa de pruebas antes de abrir PR.
- El contenido técnico de las Rondas 1-3 (arriba) no cambió — sólo gobernanza y ubicación.

## Ronda 6 — bug real de renderizado de los E-R + ajustes de legibilidad (2026-09-10)

El usuario reportó que los diagramas E-R "no se visualizan". Diagnosticado con **Playwright real**
contra la página corriendo (no adivinado): `st.tabs` monta las 7 secciones de una vez; las pestañas
inactivas quedan en `display:none`, y un iframe dentro de un `display:none` tiene
`clientWidth/clientHeight = 0` — confirmado inyectando JS en los iframes reales. `mermaid.run()`
corría de inmediato al cargar, sin esperar a que su pestaña estuviera visible, y calculaba el
enrutado de las relaciones contra ese viewport de tamaño cero: rutas SVG degeneradas,
`getPointAtLength` sobre un `<path>` vacío truena internamente, y mermaid **no rechaza la
promesa** — renderiza su propio ícono "Syntax error in text" como si fuera un resultado normal, por
eso parecía un problema de contenido y no lo era. Fix real: esperar a que `clientWidth > 0`
(`requestAnimationFrame`, que el navegador pausa solo mientras el iframe está oculto y retoma solo
al mostrarla) antes del primer `mermaid.run()`, con reintento por contenido como red de seguridad
adicional. Verificado repetidamente contra la página real: 0 "Syntax error" en los 4 E-R (Gold en
Modelo de datos; Bronze, Silver, Gold en Capas).

**Mismo patrón de bug, encontrado también en las barras de Capas** ("se sale de la pantalla los
datos de Gold"): el ancho se medía con `clientWidth || 760` en el mismo instante potencialmente
oculto, horneando un ancho supuesto que no coincidía con el contenedor real una vez visible — la
barra de Gold (el valor máximo) es la que menos margen deja al borde derecho. Mismo fix: esperar
visibilidad antes de medir. Se amplió además el margen reservado para la etiqueta de valor (90→110px)
para que nunca quede pegada al borde. Verificado en 900/1000/1280px de ancho de ventana.

**Espacio en blanco bajo Bronze/Silver:** medido en vivo con Playwright, Bronze renderiza a ~110px
de alto natural y Silver a ~260px, muy por debajo de los 560px que usaba un único alto compartido
para los 4 E-R (elegido pensando en Gold, el más grande). Streamlit `components.html` no tiene
mecanismo de auto-resize (se probó explícitamente `postMessage({type:
"streamlit:setFrameHeight"})`: lo ignora fuera de un custom component registrado), así que la
solución no es "ajustar automático" sino que cada `BloqueMermaid` ahora trae su propio campo
`alto` (nuevo, opcional, retrocompatible) con el valor medido para su diagrama específico —
Bronze 220px, Silver 340px, Gold 540px. Espacio muerto casi eliminado sin sacrificar la legibilidad
de Gold.

**Diccionario de columnas de `gold.fact_escuela_ciclo` sin explicar:** el usuario señaló que la
tabla de columnas en "Modelo de datos" aparecía sin contexto, sin quedar claro de dónde salía. Se
agregó un `markdown` de título antes de la tabla explicando que son solo las columnas del hecho
central (no de todo Gold — las dimensiones tienen su propio diccionario en `Data_Model.md §6`, no
repetido aquí), de dónde sale (`Data_Model.md §6`), y qué responde en relación al E-R justo arriba.

**Nota operativa:** ni `uvicorn` ni `streamlit` corrían con `--reload` en esta máquina, así que los
cambios en `src/api/v1/about.py`/`about_client.py` no se reflejaban solos — se reiniciaron ambos
procesos manualmente en cada cambio de contrato, incluyendo restaurar `POSTGRES_HOST=localhost`
(se había perdido en un reinicio) para que "Capas" volviera a mostrar datos reales en vez de
`SIN_DATO`.

Suite completa verificada de nuevo tras estos cambios: 1103 passed / 4 skipped (las fallas de
`test_validacion_*` son preexistentes, por una versión de `great_expectations` desalineada en este
ambiente local, ajenas a este trabajo). `ruff` limpio, `api/openapi.v1.json` regenerado con
`scripts/export_openapi.py`.
