---
id: DOC-BOSQUEJO-US601
title: "Bosquejo de componentes — US-601"
owner: "Héctor Rafael Morales Marbán"
status: draft
version: "1.0"
traces_up: ["US-601", "REQ-001", "DEC-022"]
last_reviewed: "2026-09-10"
tags: [architecture, components, us-601, s7, equipo-1]
---

# Bosquejo de componentes — Sección "Cómo funciona FARO" (US-601)

> Estado: **implementado**, pendiente de verificación visual final y de confirmación de Héctor Morales
> (líder de Equipo 1 · Componentes y memoria técnica, dueño formal de `US-601`). Redactado por Manuel
> Serranía como integrante de Equipo 1. Este es el "bosquejo enlazado" que pide el gate de hoy: enlaza
> —no duplica— `System_Design.md`, `Data_Model.md`, `API_Specification.md`, `Frontend_Architecture.md`
> y `Technical_Guide.md` de esta misma carpeta, y alimenta a Equipo 3 (storytelling) y Equipo 5
> (frontend). Lo que sobrevive además de este documento es el DevLog
> (`vault/_DevLog/2026-09-09-manuel-serrania-us225-como-funciona.md`, actualizado en cada ronda,
> incluida la migración a `US-601`).
>
> **Nota de renombre:** este documento se llamaba `US-225` en su origen (hotfix pedido antes de que
> `DEC-022` reabriera y renumerara el trabajo como `US-601` dentro del plan de recuperación S7). El
> contenido no cambió por el renombre — sólo el ID, el owner formal y su ubicación (de la raíz del
> repo, prohibida por `Definition_of_Filed`, a `vault/03_Architecture/`).

## Contexto

Se pidió agregar a FARO Web una sección pública que explique cómo funciona el sistema: componentes
del backend, modelo de datos (E-R), capas bronze/silver/gold, cubos de Gold y memoria técnica. Se
pidió como hotfix, con dos restricciones que definieron el diseño desde el principio:

1. **Corre en paralelo con el resto del equipo** — Gold puede ganar columnas o cubos, hay ADRs que
   pueden pasar de `proposed` a `accepted`, los Model Cards de C3 siguen `in_review`. Un endpoint
   por sección se habría desincronizado constantemente.
2. **Streamlit se va a dejar de usar pronto** (migración futura a React/Angular). Todo lo visual
   nuevo se construye portable: JSON puro del lado del backend, HTML/D3 autocontenido del lado del
   frontend — nada que dependa de widgets nativos de Streamlit.

## Arquitectura final del contrato

`src/api/v1/about.py` publica dos rutas:

- `GET /api/v1/about/secciones` — el **manifest**: `[{id, titulo, orden}]` de las secciones
  disponibles. Agregar/quitar/reordenar una sección es un cambio de este archivo únicamente.
- `GET /api/v1/about/secciones/{id}` — el contenido de una sección, siempre con el mismo **sobre
  genérico**: `{id, titulo, fuente, advertencias, bloques}`.

`bloques` es una lista heterogénea de **7 tipos**, cada uno con su propio renderer en
`src/frontend/pages/4_Como_Funciona.py` (`_render_bloque`) y su propio dataclass de parseo en
`src/frontend/about_client.py`:

| Tipo | Para qué | Render |
|---|---|---|
| `markdown` | Texto explicativo | `st.markdown` |
| `mermaid` | Diagramas E-R | HTML embebido (`components.html`) + CDN mermaid |
| `tabla` | Tablas simples | `st.table` |
| `metricas` | KPIs puntuales (ej. total de filas) | `st.metric` en columnas |
| `mapa` | Mapa de los 4 estados de `SCOPE_ENTIDADES`, con silueta nacional de fondo | D3 (`geoMercator`+`geoPath`) vía HTML embebido |
| `barras` | Comparativo bronze/silver/gold | D3 (barras horizontales) vía HTML embebido |
| `diagrama_flujo` | Tablas fuente → cubos → dashboards | D3 (3 columnas, curvas, hover) vía HTML embebido |

Un `tipo` que el cliente no reconozca cae en `BloqueDesconocido` — la sección se pinta con una
advertencia en su propio espacio, nunca tumba la página completa. Esto es lo que permite seguir
agregando tipos de bloque (como pasó 2 veces esta semana) sin romper retrocompatibilidad.

**Único dato vivo de toda la sección**: los conteos de fila de `capas` (`repositorio_about.py`,
consulta Postgres en cada request). Todo lo demás —texto, tablas, geometría— es contenido fijo,
decisión explícita para no perder tiempo parseando documentos en vivo durante el hotfix (queda
como *follow-up* anotado, no bloquea esta entrega).

## Las 7 secciones — contenido final

1. **`arquitectura`** — tabla de 10 componentes del backend con su dueño de célula, + tabla de las
   5 células (integrantes y en qué trabajó cada una, anclado a los componentes de arriba, no un
   roster aparte).
2. **`modelo-datos`** — mapa de los 4 estados con fondo nacional gris, explicación de
   `fact_escuela_ciclo` (qué SÍ vive ahí vs. qué se consulta por `JOIN`), diagrama E-R de Gold,
   diccionario de columnas, tabla de los 6 drivers (ID, nombre, fuente, cobertura).
3. **`capas`** — definición de bronze/silver/gold, tabla de las 8 fuentes de bronze, métrica de
   total de filas, barras bronze/silver/gold, y los **3 E-R titulados** (Bronze, Silver, Gold) con
   narrativa de "qué cambió respecto al anterior", más el detalle de conteos por tabla.
4. **`cubos`** — explicación de qué son los cubos + cómo leer el diagrama de 3 columnas, y el
   diagrama de flujo (tablas fuente reales, verificadas contra el SQL de
   `dbt/models/gold/cubo_*.sql` → 9 cubos → 10 dashboards).
5. **`stack`** — memoria técnica (lenguajes, capas, herramientas), de CLAUDE.md §5.
6. **`decisiones`** — tabla de ADRs (id, título, estado, fecha), marcada explícitamente "sujeto a
   cambio".
7. **`modelos-ml`** — tarjetas de ML-01/02/03 (propósito, métrica actual, estado), de los Model
   Cards de C3.

## Archivos

**Backend**
- `src/api/v1/about.py` — router + los 7 tipos de bloque (Pydantic) + contenido de las 7 secciones.
- `src/api/repositorio_about.py` — único dato vivo (conteos por capa).
- `src/api/v1/__init__.py` — registra el router (público, independiente de `AUTH_LECTURA_PUBLICA`).

**Frontend**
- `src/frontend/about_client.py` — cliente HTTP + parseo de los 7 tipos de bloque.
- `src/frontend/pages/4_Como_Funciona.py` — página, renderer genérico + los 3 renderers D3.
- `src/frontend/app.py` — link de acceso rápido.

**Geografía (nuevo, alcance verde de Manuel/C2 — `superset/**`)**
- `superset/assets/geojson/mexico_silueta.geojson` — silueta nacional simplificada (10 KB,
  decorativa, generada, no fuente de fronteras exactas).
- `superset/generar_geojson_silueta_nacional.py` — script que la genera (descarga los 32 estados,
  rasteriza, traza contorno con marching squares, simplifica).

**Pruebas**
- `tests/fixtures_about.py`, `tests/test_about_client.py`, casos en `tests/test_api_contract.py`.
- 54 casos en verde: `pytest tests/test_api_contract.py tests/test_about_client.py -q`.

**Documentación tocada por el camino**
- `vault/00_Start_Here/Runbook_Ambiente_Local.md` — corrección de identificadores de fixture
  desactualizados (hallazgo real al seguirlo para poblar Postgres local).

## Historial de cambios por ronda

**Ronda 1 — MVP del hotfix.** Diseño del contrato manifest + sobre genérico (4 tipos de bloque:
`markdown`/`mermaid`/`tabla`/`metricas`), las 7 secciones con contenido fijo copiado de las fuentes
canónicas de cada dueño, `repositorio_about.py` con el único dato vivo (conteos por capa). Excepción
de alcance autorizada por el usuario para tocar `src/api/**` (entonces verde de Christian/C4;
**superada por la Ronda 5** — ver abajo, ya no aplica esa lectura de ownership). DevLog inicial.

**Ronda 2 — datos reales + E-R de bronze/silver.** Se siguió el runbook del equipo para poblar
Postgres local con fixtures (bronze 1,016 filas, silver 515, gold 3,297). Se corrigió un hallazgo
real: `Runbook_Ambiente_Local.md` tenía los identificadores de SESNSP/CONAPO desactualizados
(`sources.yml` había cambiado el default después de que el runbook se verificó). Se recreó
`gold.predicciones`/`gold.recomendaciones` (esquema viejo de otra corrida, autorizado por el
usuario). Se agregaron los E-R de bronze y silver (mermaid) a la sección `capas`.

**Ronda 3 — retroalimentación de contenido.** El usuario pidió, en un solo mensaje: narrativa de
células en `arquitectura`; mapa de los 4 estados + explicación de `fact_escuela_ciclo` + drivers en
`modelo-datos`; fuentes de bronze + más visual + los 3 E-R titulados (incluido gold) + total de
filas en `capas`; diagrama en vez de tabla en `cubos`. Confirmó la restricción de "Streamlit se va
a dejar de usar" que definió que todo lo visual nuevo fuera D3/HTML, no widgets nativos. Se
diseñaron y construyeron 3 tipos de bloque nuevos: `mapa` (reutilizando el GeoJSON de municipios ya
versionado), `jerarquia` (icicle D3) y `diagrama_flujo` (D3, 3 columnas). El mapa se limitó a los 4
estados sin fondo nacional (no había fuente ligera en el repo en ese momento).

**Ronda 4 — corrección visual tras ver la página.** El usuario reportó 3 problemas reales viendo la
página en el navegador:
- *Contraste roto* en mapa y cubos (fondo negro, letras negras): cada bloque D3 vive en su propio
  iframe sin estilos propios, heredaba `prefers-color-scheme: dark`. Fix: `color-scheme: light` +
  fondo blanco explícito en los 3 bloques D3 (y en mermaid, mismo riesgo).
- *Icicle ilegible, silver invisible*: con gold ~6x más grande que silver, el icicle repartía el
  ancho por proporción y silver quedaba una franja de pocos píxeles. Se **reemplazó por barras
  horizontales** (tipo de bloque nuevo `barras`) — una fila de alto fijo por capa, nunca compite
  por espacio. Se eliminó `jerarquia`/`NodoJerarquia` del backend y del cliente (código muerto).
- *Cubos sin explicación*: se agregó un bloque de texto explicando las 3 columnas del diagrama.
- *Mapa sin contexto nacional*: el usuario pidió el fondo gris del resto de México después de ver
  el resultado. Se generó `mexico_silueta.geojson` con un script nuevo (32 estados descargados del
  mismo mirror que ya usa el proyecto, rasterizados sobre una rejilla de 0.05°, contorno trazado
  con marching squares implementado a mano). **Bug real encontrado y corregido**: los 2 casos
  "silla de montar" del marching squares emparejaban mal las esquinas (`(O,N)+(S,E)` en vez de
  `(O,S)+(E,N)`), lo que rompía la cadena del contorno y perdía el continente completo (solo
  quedaban 9 islas sueltas). Las 3 pruebas sintéticas iniciales no lo detectaron porque ninguna
  tocaba un punto de silla; el bug solo se manifestó con la geografía real de México. Diagnosticado
  por análisis de grados de entrada/salida del grafo de segmentos, corregido, y verificado contra 9
  ciudades reales (todas dentro del polígono) + 4 puntos fuera del país (todos fuera).

**Ronda 5 — migración a `US-601` tras el plan de recuperación S7.** El usuario compartió la propuesta
de storytelling ("7 casos por investigar") y un mensaje de Equipo 1 pidiendo este bosquejo para el gate
de hoy. Verificado contra `vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO.md` §10: el storytelling
no exige tocar el contenido de "Cómo funciona" (su mapeo de endpoints es `/escuelas`, `/kpis`,
`/predicciones`, `/agente/consulta`, ajeno a `/about/*`). Al jalar `origin/main` apareció
`vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09.md`: reabre esta historia como **`US-601`**,
liderada por **Héctor Morales** (Equipo 1 · Componentes y memoria técnica), con Manuel y Carlos Mayorga
como integrantes. `ownership.yml` ya refleja el cambio de rol de Manuel (`tech_lead: false`), aunque su
`verde`/`amarillo` de Equipo 1 aparece copiado casi idéntico entre los tres integrantes con rutas de
ML/agente (no de componentes backend) — inconsistencia que se documenta aquí para que Héctor la reporte
a Edgar, en vez de tratarla como bloqueo. Cambios de esta ronda: el documento se renombra de `US-225` a
`US-601` y se relocaliza de la raíz del repo (prohibida por `Definition_of_Filed`) a
`vault/03_Architecture/Bosquejo_Componentes_US601.md`; se migra el trabajo de la rama no gobernada
`componentes-back` a la rama permanente `dev/manuel-serrania`, sincronizada primero con `origin/main`.
El contenido técnico de las Rondas 1-4 no cambia.

## Verificación

- `ruff check` limpio en todos los archivos tocados (backend, frontend, script de geografía).
- 54 pruebas propias en verde: `pytest tests/test_api_contract.py tests/test_about_client.py -q`.
- Suite completa del repo corrida tras sincronizar `dev/manuel-serrania` con `origin/main` y
  mergear `componentes-back`: sin regresiones nuevas. Las 20 fallas de `test_validacion_*`
  (`test_cache_predicciones.py`, `test_validacion_coneval.py`, `test_validacion_sinaica.py` y
  familia) son preexistentes — una librería `great_expectations` desalineada en este ambiente
  local, ajena a este trabajo y fuera del alcance de Equipo 1.
- `api/openapi.v1.json` regenerado con `scripts/export_openapi.py` (no editado a mano).
- `python vault/_Meta/scripts/vault_lint.py .` sin bloqueantes nuevos (los 3 que reporta —
  `PLAN_US206_EMBEBIDO.md`, `avisosequipo.md`, `plan7diasporpersona.md` — son preexistentes de
  `componentes-back`, ajenos a `US-601`).
- Verificado por estructura (curl contra la API real, point-in-polygon contra ciudades reales para
  la silueta) — **no verificado visualmente en navegador por el agente** (sin herramienta de
  captura de pantalla en esta sesión); pendiente de confirmación del usuario.
- `dev/manuel-serrania` pusheado a `origin` (commits `19df7f4`, `ad50fc9`). **El PR queda
  pendiente a propósito** — el usuario pidió dejar solo el commit + push por ahora, no abrirlo
  todavía.

## Pendiente (no bloquea lo ya construido)

- **Abrir el PR** `dev/manuel-serrania` → `main` cuando el usuario lo indique (ver "Verificación").
- **Gobernanza**: la historia ya tiene alta oficial como `US-601` (`Héctor Morales`, Equipo 1) —
  falta que Héctor confirme el bosquejo y que reporte a Edgar la inconsistencia de `ownership.yml`
  encontrada en Equipo 1 (ver Ronda 5).
- **Follow-up de contenido dinámico** (anotado desde la ronda 1, no se hizo): sustituir el
  contenido fijo de `arquitectura`, `modelo-datos`, `cubos`, `stack`, `decisiones` y `modelos-ml`
  por lectura en vivo de sus fuentes — ADRs y Model Cards son los candidatos más urgentes por lo
  seguido que cambian.
- **Decisión pendiente**: si Christian apaga `auth_lectura_publica` antes de la demo, decidir
  explícitamente si "Cómo funciona" se queda pública o hereda el candado (el usuario pidió no
  tocarlo por ahora — bloqueada la autenticación en localhost).
- **Retroalimentación en curso (post-Ronda 5)**: mapa estático (sin pan/zoom) y el E-R de
  `modelo-datos` sale con demasiado zoom/incompleto — en revisión, ver DevLog cuando se resuelva.
