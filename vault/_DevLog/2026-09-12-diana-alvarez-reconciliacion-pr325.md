---
title: "Reconciliación de dev/diana-alvarez-rediseno contra dev/diana-alvarez tras el PR #325: 2 roturas silenciosas restauradas, 1 literal reintroducido corregido, matriz de trazabilidad resuelta sin perder contenido"
fecha: 2026-09-12
autor: Diana Aracely Alvarez Varela
herramienta: Claude Code / claude-sonnet-5
relacionado: [US-641, US-621, US-305, ADR-011, DEC-026]
---

## Contexto

Todo el rediseño Fase 2 (shell, 7 pantallas, checklist de cierre, barrido de literales de Marina)
se construyó sobre `dev/diana-alvarez-rediseno` -- una rama con nombre de historia, que
`vault/_Meta/scripts/check_ownership.py` rechaza explícitamente como origen de PR (regla #2: el PR
sale de `dev/{identidad}` y de ninguna otra rama). Mientras tanto, `dev/diana-alvarez` (la única
rama válida para abrir PR bajo esta identidad) siguió avanzando en paralelo y se acaba de fusionar a
`main` en el **PR #325** (Edgar), con 5 commits que tocan frontend.

Antes de tocar nada se verificó, commit por commit, cuáles de los 5 de PR #325 ya eran ancestros de
`-rediseno` (`git merge-base --is-ancestor`): **3 de los 5 ya estaban incluidos** --el rename de ruta
`/casos/:cct` → `/escuela/:cct`, la lectura de `cortes_atencion` desde `/version`, y la comparación de
2 ciclos de matrícula en `VistaGeneral.jsx`-- porque `-rediseno` arrancó justo después de esos commits
en la historia real, no de un ancestro común más viejo como parecía a primera vista. Solo 2 commits
divergían de verdad: el que borra `postAgenteConsultaStream()` de `api.js` ("sin usar en esta rama",
cierto para `dev/diana-alvarez` pero no para `-rediseno`, que sí la usa desde `AsistenteFaro.jsx`) y
el que agrega distinción loading/error/ok a `useCortesAtencion()` (reintroduce el literal "7 casos" en
un bloque de error nuevo).

## Qué se hizo

Se creó el merge real sobre `dev/diana-alvarez` (local, sincronizada con `origin/dev/diana-alvarez`,
sin push): `git merge dev/diana-alvarez-rediseno --no-ff`, con `--no-commit` primero para revisar cada
conflicto antes de resolverlo.

### 1. `docker/frontend-react.Dockerfile` -- conflicto reportado, sin diferencia real

Git marcó conflicto de contenido pero, al comparar el resultado contra ambas ramas
(`git diff dev/diana-alvarez-rediseno -- docker/frontend-react.Dockerfile`), el archivo terminó
idéntico en ambos lados -- ambas ramas habían llegado por su cuenta al mismo contenido (probablemente
por un merge de `main` en algún punto de cada una). No hizo falta tocar nada.

### 2. `vault/02_Requirements/Traceability_Matrix.md` -- 2 conflictos, resueltos sin perder contenido

- **Separador antes de un encabezado de sección**: una rama tenía una línea en blanco de más, la otra
  ninguna -- se dejó una sola, igual que en el resto del documento.
- **La fila de "cortes de atención" editada distinto en cada rama**: `dev/diana-alvarez` la actualizó
  para reflejar que la decisión del mapa de `VistaGeneral.jsx` **ya se resolvió** (confirmado leyendo
  `vault/_DevLog/2026-09-12-marina-garcia-dec026-mapa-us621.md`: Diana Álvarez eligió que el mapa se
  quede como contexto de ubicación, no como ranking -- documentado por Marina el mismo día, en una
  sesión distinta a la de este redisño); `-rediseno` seguía con la versión vieja de esa fila
  ("depende de la decisión pendiente con Marina"), porque esa actualización nunca llegó a esta rama.
  Se conservó la fila de `dev/diana-alvarez` (la vigente) y, a continuación, **las 8 secciones
  completas** que `-rediseno` agregó documentando el día del rediseño (shell+P1, P2, P3-P6, sidebar
  móvil, auditoría de mockups, login, comparativa/checklist) -- ningún contenido de ninguna de las dos
  ramas se perdió, solo se evitó dejar dos versiones contradictorias de la misma fila.

### 3. Dos roturas silenciosas (sin marcador de conflicto, detectadas por revisión manual antes de
   fusionar de verdad -- ver DevLog de la evaluación previa) -- restauradas

- **`postAgenteConsultaStream()` en `frontend/src/lib/api.js`**: el merge la había borrado (venía del
  commit de `dev/diana-alvarez` que la quitó por no usarse en esa rama), pero
  `frontend/src/components/AsistenteFaro.jsx` (construido hoy en `-rediseno`) la importa y la llama
  para el streaming SSE del Asistente FARO. Restaurada completa (función + su bloque de comentario de
  contrato) desde `-rediseno`, en la misma posición relativa del archivo.
- **`color`/`riskRampColor` en `frontend/src/pages/LosSieteCasos.jsx`**: el merge había dejado
  `color={color}` en el `<RiskGauge>` de cada tarjeta sin la línea `const color = riskRampColor(...)`
  que lo define (ni el import de `riskRampColor`) -- hubiera lanzado `ReferenceError` al renderizar la
  pantalla. Restaurados ambos desde `-rediseno`.

### 4. Literal reintroducido -- corregido con el mismo criterio de Marina

El commit de `dev/diana-alvarez` que agrega el nuevo bloque de error para "cortes de atención no
disponibles" en `frontend/src/pages/ExpedienteEscuela.jsx` trae su propio "← Volver a los 7 casos"
(no existía cuando se hizo el barrido de literales de Marina, porque ese bloque de error no existía
todavía en ninguna rama en ese momento). Corregido a "← Volver a los casos", igual que las otras 2
apariciones ya arregladas en el mismo archivo.

## Verificación

Barrido final de `7 casos`/`7 escuelas`/`siete escuelas` sobre `pages/` y `components/` tras la fusión:
cero apariciones fuera de comentarios de código (que Marina pidió dejar igual a propósito). Balance de
paréntesis/llaves/corchetes (0/0/0) en los 28 archivos `.js`/`.jsx` tocados por el merge, `git diff
--check` limpio (sin conflictos de espacio en blanco) y `vault_lint.py` limpio (mismos 11 huérfanos
preexistentes, ninguno nuevo). Sin binding nativo de `oxlint`/`esbuild` en este entorno para correr el
lint real -- pendiente que Diana lo confirme con `npm run dev` desde su Mac, con datos reales.

## Lo que NO se tocó

- El archivo `diagnostico_duplicado_cct.sql` que apareció sin trackear en el árbol de trabajo -- no es
  parte de este merge ni de esta rama, se dejó tal cual.
- Ningún archivo fuera de frontend/vault -- el merge no toca `src/`, `dbt/`, `dags/` ni `docker/`
  (salvo el Dockerfile ya descrito, sin cambio real).

## Siguiente paso

Rama lista en local (`dev/diana-alvarez`, mergeada con `dev/diana-alvarez-rediseno`, sin push). Falta
que Diana la suba (`git push origin dev/diana-alvarez`) y abra el PR -- no hay `gh` CLI disponible en
este entorno y el flujo de trabajo de la sesión es que ella hace el push y abre PRs, nunca este agente.
