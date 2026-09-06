---
project: "FARO"
date: "2026-09-06"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "cierre de la cadena de DEC-019 y revisión del despliegue de FARO Web"
tags: [devlog, pm, dec-019, us-526, bug-061, freeze]
---

# DevLog — 2026-09-06 — La cadena de `DEC-019` cerrada, y `main` que no reproduce producción

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register]] ·
[[vault/10_Risk_Governance/Decision_Log]]

## 1. La cadena de `DEC-019`, completa en un día

Cuatro PRs en orden, cada uno verificado corriendo su rama antes de aprobar:

| # | Quién | PR | Qué |
|---|---|---|---|
| 1 | Edgar Coronel | #271 | La decisión, que cinco ramas citaban sin que existiera |
| 2 | Diana Alvarez | #273 | Los 6 sitios de dbt |
| 3 | Christian Ruiz | #270 | La API, más las guardas |
| 4 | Marina García | #268 | El frontend |

**Lo que hizo que funcionara no fue la coordinación del PM.** Las tres células llegaron por su cuenta
al mismo par de nombres —`ANCLA_SIGMOIDE` / `LINEA_DE_ALERTA`— sin que nadie lo pidiera. Yo mismo no
lo vi: reporté que la API y el frontend *"no los tenía nadie"* porque busqué por el nombre viejo de
la constante.

**Christian construyó, sin que se le pidiera, las dos guardas que yo había registrado como pendientes
post-freeze:** la que ata el mock al repositorio (`BUG-060`) y la que compara los cubos de dbt contra
la constante de la API (mitigación de `RISK-010`). Y dejó los 5 casos de cubos con un **salto
condicional que se disuelve solo**: verificado en vivo — pasaron de `5 skipped` a `12 passed` en el
instante en que el PR de Diana entró a `main`.

Estado final de las constantes, verificado tras el último merge:

| Archivo | Constante | Valor |
|---|---|---|
| `api/repositorio_gold.py` · `frontend/prediccion_client.py` | `LINEA_DE_ALERTA` | **0.50** |
| Los mismos dos | `ANCLA_SIGMOIDE` | 0.60 |
| `modelos/riesgo.py` | `RIESGO_UMBRAL` | **0.60, intacto** |

## 2. `US-526` entregada: la tercera URL pública responde

`https://faro-frontend-eanzfglvyq-uc.a.run.app` → **200**, verificado. Luis Téllez versionó
`docker/frontend.Dockerfile` y `frontend-requirements.txt`, que estaban **untracked**.

## 3. `BUG-061` — y es lo más grave que encontré hoy

Dentro de ese mismo PR, Luis reporta algo que no es suyo y que vale más que el PR: **el embebido de
Superset de FARO Web nunca se commiteó.**

Lo verifiqué: `src/frontend/superset_client.py` tiene **188 líneas en `main`** y la versión que sirve
la URL pública tiene **265**. El código vivía sólo en el working tree y llegó a producción horneado
en una imagen vía `COPY src/frontend/`. Luis lo descubrió del peor modo posible: reconstruyó desde
`main` para bajar `BUG-059` y **la reconstrucción regresó Dashboards y Panel ML**.

**`main` no puede reproducir producción.** Eso rompe una propiedad básica, y el riesgo es concreto
para el miércoles: cualquier redespliegue —un fix de última hora, un rollback, un reinicio que
dispare build— deja los tableros embebidos sin autenticar **sin que nadie lo note hasta abrirlos**.

Hoy la demo funciona porque la revisión `00005-6vs` ya sirve la versión buena. **Eso es una
mitigación, no un arreglo.** El dueño es Célula 2: `src/frontend/**` es su alcance y C5 sólo
conteneriza. El handoff está en `_local/`.

## Verificado

`git show origin/main:src/frontend/superset_client.py | wc -l` → **188** ·
`curl` a `faro-frontend-…run.app` → **200** · `test_linea_de_alerta.py` → **12 passed** tras el merge
de Diana · suites completas corridas en las ramas de Diana (1024), Christian (1036) y Marina (1064) ·
`vault_lint` limpio

## IDs tocados

`BUG-061`, `DEC-019`, `RISK-010`, `BUG-059`, `BUG-060`, `US-526`, `US-206`, `US-207`, `REQ-002`,
`REQ-005`

## Próximos pasos

- **C2 commitea el embebido a `main`** desde el handoff de `_local/`. Es `BUG-061` y es lo último
  que puede romper la demo en silencio.
- **Luis**: reimportar `gold_dec019_2026-09-06_v2.sql` a Cloud SQL y redesplegar la API. Sin eso, la
  URL pública sigue diciendo 0 escuelas en riesgo aunque el código diga 7.
- Marina elige el par de demostración, ahora sí con las 7 escuelas sobre la línea.
