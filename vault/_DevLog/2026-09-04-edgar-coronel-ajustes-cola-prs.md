---
project: "FARO"
date: "2026-09-04"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "revisión de los 4 PRs abiertos y ajustes mecánicos para destrabarlos"
tags: [devlog, pm, prs, ownership, conflictos]
---

# DevLog — 2026-09-04 — Revisión de la cola de PRs y ajustes para destrabarla

→ [[vault/_DevLog/_index|Volver al índice]] · `vault/_Meta/ownership.yml`

## Qué se pidió

Revisar los 4 PRs abiertos (#219, #220, #221, #222), definir el orden de aprobación, qué ajustar en
cada uno y qué mensaje dar a cada autor.

## Orden determinado por simulación, no por intuición

Tres de los cuatro PRs tocaban `Bug_Register.md` y dos tocaban `Traceability_Matrix.md`, así que el
orden de merge decidía quién heredaba los conflictos. En vez de suponerlo, se simuló cada cadena con
`git merge-tree --write-tree` sobre árboles temporales, sin tocar ninguna rama:

| Orden probado | Resultado |
|---|---|
| #222 → #219 → #220 | los tres limpios, sin un solo conflicto |
| #221 primero | **peor**: hace chocar a #222, #219 y #220 |
| #221 al final | choca solo él, en dos archivos |

Conclusión: **#222 → #219 → #220 → #221**. La fila `BUG-047` de Manuel quedó contigua a la `BUG-046`
de Christian, así que su PR choca en cualquier orden; ponerlo al final concentra el costo en un solo
lugar en vez de repartirlo entre tres personas.

## Ajustes ejecutados

**`ownership.yml` — tercer hueco del mismo patrón en un día.** `vault/_Meta/US-521b-guia-ambiente-local.md`
es la entrega de US-521b de Edgar Jiménez, pero vive en `vault/_Meta/**`, verde exclusivo del PM: el
gate le impedía actualizar **su propio documento**. Es el mismo hueco que ya corregimos hoy para
Marina (`Accessibility.md`) y Diana (`Data_Lineage_US106.md`). Se agrega a `comunes` con nota
estructural: el documento está mal ubicado —es una guía de usuario, no metadatos del vault— y moverlo
a `00_Start_Here` queda como follow-up post-freeze, para no romper su PR abierto.

**Rama de Manuel (#221) sincronizada y sus dos conflictos resueltos**, sin pérdida de contenido:
- `Bug_Register.md`: se toma **BUG-046 de `main`** (la revisión de Christian, más larga) y
  **BUG-047 de su rama** (su corrección de conteo de tests, que es el motivo del PR).
- `Traceability_Matrix.md`: se conserva su fila `REQ-002`/`US-203` corregida **y** el bloque de
  evidencia de BUG-012 que traía `main`.

**Rama propia sincronizada** tras el merge de #222: el auto-refresco del tablero que corre después de
cada merge regenera los mismos dos artefactos que yo había regenerado, así que chocan siempre. De los
tres archivos que GitHub marcaba, **solo dos eran conflictos reales**: `_DevLog/_index.md` fusiona
limpio en local por `merge=union` — GitHub no sabe calcularlo, es el falso positivo ya conocido.

## Trampa que volvió a aparecer

Al abrir el worktree de la rama de Manuel, el branch local `dev/manuel-serrania` apuntaba a un commit
viejo de una sesión anterior, y `git merge origin/main` lo llevó al tip de `main` en vez de a su
trabajo. **Se detectó antes de empujar nada** (su rama remota nunca se tocó) comparando
`git rev-parse dev/X` contra `origin/dev/X`. Se rehízo el worktree con `-b dev/X origin/dev/X`
explícito.

Barrido de las otras ramas locales: `dev/christian-ruiz` y `dev/luis-tellez` también estaban
obsoletas y se borraron; `dev/karla-monter` estaba al día. Los punteros locales de ramas ajenas no
aportan nada y son una fuente activa de error: la referencia buena siempre es `origin/`.

## Hallazgos que quedan para sus dueños

- **#220 (Edgar Jiménez)** cambia la imagen de la base de `postgres:15-alpine` a
  `postgis/postgis:15-3.3-alpine` **sin documentarlo en ningún DevLog**. La motivación es real
  —verificado en los logs del contenedor: `init-db.sql:77` falla hoy con *"extension postgis is not
  available"*— pero **ningún archivo del repo usa PostGIS** (`gold.geo_municipio.geometria` es
  `text`) y cambiaría la imagen compartida de los 21 a dos días del freeze. Se le pide sacarlo de
  ese PR y tratarlo aparte.
- **#220** trae además un **placeholder de plantilla sin llenar** en su DevLog:
  `pytest tests/ -q` → *"(resultado aquí, ej: 884 passed, 7 skipped)"*. La evidencia no se registró.
- Su guía **no duplica** el runbook nuevo: cubre Airflow y jobs ML, con cero menciones a dbt,
  fixtures o Superset. Son complementarias y conviene que se enlacen.

## Verificado

`vault_lint.py` limpio en ambas ramas · gate de ownership simulado en verde para la rama de Manuel ·
YAML de `ownership.yml` válido · los dos conflictos resueltos comprobados sin marcadores residuales y
con el contenido de ambos lados presente.

## IDs tocados

`US-521b`, `BUG-046`, `BUG-047`, `BUG-012`, `REQ-002`, `REQ-007`

## Próximos pasos

- Sincronizar `dev/edgar-jimenez` (29 commits detrás) **después** de que este PR entre a `main`, para
  que su gate encuentre el `ownership.yml` corregido.
- Edgar Jiménez: corregir el DevLog y sacar el cambio de PostGIS.
