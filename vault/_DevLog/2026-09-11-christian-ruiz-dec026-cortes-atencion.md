---
project: "FARO"
date: "2026-09-11"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — los cortes del nivel de atención en el contrato y la validación de DEC-026"
touches: ["DEC-026", "DEC-023", "DEC-019", "DEC-006", "BUG-063", "BUG-058", "US-621", "REQ-004"]
tags: [devlog, api, contrato, gobernanza, riesgo, frontend]
---

# DevLog — 2026-09-11 — Los cortes que el front ya no teclea, y la validación de `DEC-026`

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/10_Risk_Governance/Decision_Log|DEC-026]] ·
[[vault/03_Architecture/API_Specification|API_Specification §3.1, §3.4]]

## Contexto

Marina y Edgar plantearon que con la sigmoide como corte de `alta` **ninguna escuela sale con riesgo
alto**, y que la línea de alerta debe ser 0.50. Tienen razón en el fondo, y está medido: es
**`BUG-063`** — el máximo que ML-01 predice sobre el Gold real es **0.5717**, así que el corte quedó
*por encima del techo del fenómeno* y la tarjeta «Recomendaciones de prioridad ALTA» de DB-09 lee 0.
Edgar pidió ayuda para documentarlo "para que se mantenga".

**Lo primero que encontré es que una mitad ya estaba decidida.** El paquete de UX aprobado por
`DEC-023` define el **nivel de atención** —alta desde 0.50, media desde 0.30— como una etiqueta que
**el front calcula** desde `indice_riesgo`, y dice literalmente que a eso no se le dice "prioridad",
porque esa palabra nombra una columna de Gold que usa otro corte y que el front no consume
(`00_Storytelling_Scope.md` §5.3.bis). Así que para que las escuelas salgan en atención alta el
sábado **no hacía falta aprobar ni republicar nada**.

Lo que seguía roto era solo la columna de Gold y DB-09, que `DEC-023` mantiene como respaldo: dos
superficies que se contradicen sobre las mismas escuelas.

## Qué se hizo

### `DEC-026`: la redacté, pero la que queda es la del PO

Edgar me pidió ayuda para documentarlo, así que redacté la decisión y la subí. **Él subió la suya en
paralelo, en su propio PR**, y es la que se conserva: `DEC-013` dice que el ID es de quien llega
primero a `main`, y una decisión de producto la firma el PO. Mi fila se retira de este PR; el resto
del cambio no depende de ella.

**Su redacción es mejor que la mía en dos puntos**, y vale registrarlo: justifica de forma explícita
por qué esto **contradice a propósito** la cláusula de `DEC-019` de "no cambia un solo valor
publicado" —ahí la razón era no invalidar una demo inminente; aquí el propio dato demostró estar mal,
un corte inalcanzable por construcción— y deja escrito el efecto colateral verificado: con
`alta >= 0.50` el conteo coincide con `escuelas_en_riesgo`, así que DB-09 y el KPI-04 dejan de contar
cosas distintas con el mismo nombre.

El contenido es el mismo en lo que importa: `alta` baja de `ANCLA_SIGMOIDE` (0.60) a la línea de
alerta (0.50), el ancla **no se toca** porque es calibración (`DEC-006`), y **Gold se republica** —
`prioridad` es columna almacenada, así que tocar la función no mueve las 45,276 filas ya escritas. La
ejecución es de C3 sobre `src/modelos/publicar_gold.py:197`, alcance de Estefany Hernández. **No lo
toqué**: no es mi alcance y el contrato no cambia por ello.

**Validación que le di a su PR** (aprobado, con tres observaciones en comentario, sin bloquear):

1. **La asignación a Marina reprobaría el gate de propiedad:** la decisión le encarga
   `API_Specification.md` §3.4, y ese archivo no está en su verde ni en su amarillo. Es de mi verde.
2. **Ese punto ya está hecho** en este mismo cambio — tercer choque de trabajo duplicado de la semana,
   después de `/agente/consulta/stream` y de la Fase 4.
3. **La prueba guarda no puede ir en un PR aparte:** antes del cambio de C3 el corte sí está por
   encima del máximo observado, así que dejaría el **CI rojo para todos**. Tiene que viajar con el
   cambio de `publicar_gold.py`.

### Los cortes viajan en el contrato (`GET /version`)

`VersionOut.cortes_atencion` trae `alta` (0.50), `media` (0.30) y `ancla_calibracion` (0.60).

El motivo es un aviso que E3 ya había levantado y nadie había resuelto: **las dos constantes viven en
capas distintas** —la línea de alerta en la API, la matrícula estable en `src/modelos/riesgo.py`— y el
front necesita las dos. Teclearlas en React repetiría exactamente `BUG-058`: un corte hardcodeado que
queda desincronizado de la capa que lo calcula.

Van en `/version` y no en una ruta nueva porque son **metadatos del contrato**: cambian con una
decisión, no con los datos. Y en un endpoint público porque el front tiene que etiquetar **antes** de
iniciar sesión.

`ancla_calibracion` no es un corte de etiqueta. Se expone para que el glosario de la UI pueda explicar
por qué DB-09 dice `media` donde el front dice *atención alta*, sin escribir el 0.60 a mano.

**No importé `src/modelos/riesgo.py` desde la API**: ese módulo trae `numpy` y `scipy`, que la imagen
de la API no instala. La duplicación del 0.30 queda **atada por una prueba que lee ese archivo y
compara** — el mismo patrón con el que `test_linea_de_alerta.py` ata el 0.50 a los `.sql` de dbt.

### El contrato deja de describir mal a `prioridad`

Ayer yo escribí en el docstring y en la especificación que `prioridad` era "la urgencia con la que el
storytelling ordena los casos". **Eso contradecía al paquete de UX aprobado.** Corregido: `prioridad`
es procedencia auditable de Gold y paridad con DB-09; la etiqueta de producto es el nivel de atención,
y el front no consume esta columna.

## Seguridad / calidad

- [x] 2 pruebas nuevas: `/version` publica los cortes y coinciden con las constantes; el 0.30 de la
      API sigue siendo el `RIESGO_ESTABLE` de C3, verificado **leyendo** su archivo
- [x] La prueba de `/version` además fija el orden `media < alta < ancla`: si alguien usara el ancla
      como corte de etiqueta, ninguna escuela calificaría (`BUG-063`)
- [x] `cortes_atencion` es opcional en el modelo: ningún cliente que valide `/version` con su propio
      esquema cerrado se rompe
- [x] OpenAPI reexportado; `ruff` y `vault_lint` limpios

> **Pendiente que NO cierro yo:** la prueba guarda que propone `BUG-063` —que falle si el corte de la
> categoría más alta queda por encima del máximo observado— no puede entrar antes del cambio de C3, o
> deja el CI rojo para todos. Se la paso a Héctor para su PR.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** este DevLog.
- **Modificados:** `src/api/schemas.py`,
  `src/api/v1/health.py`, `src/api/repositorio_gold.py`, `tests/test_api_contract.py`,
  `tests/test_linea_de_alerta.py`, `api/openapi.v1.json`,
  `vault/03_Architecture/API_Specification.md`, `vault/_DevLog/_index.md`.

## Avisos a otros owners

- **Edgar Coronel (PO):** `DEC-026` queda como la escribiste tú; retiré mi fila para que no haya dos
  con el mismo ID. Las tres observaciones a tu PR van en su comentario.
- **Héctor Morales / Andrés González / Estefany Hernández (C3):** la ejecución es de ustedes —
  `publicar_gold.py:197` **y** republicar Gold. Sin republicar, DB-09 sigue en 0.
- **Diana Alvarez (E5):** lee los cortes de `GET /version` (`cortes_atencion`) en vez de escribir 0.50
  y 0.30 en el front. Y etiqueta con **nivel de atención**, no con `prioridad`.
- **Marina García (E3):** el nivel de atención que definiste ya es implementable sin esperar a nada.
