---
project: "FARO"
date: "2026-09-05"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "el agente entra al guion de la demo y validación de la cola de PRs abierta"
tags: [devlog, pm, us-006, us-305, us-323, demo, agente, prs]
---

# DevLog — 2026-09-05 — El agente entra al guion, y tres PRs revisados

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/01_Product/Guion_Demo_US006]] ·
[[vault/12_Roadmap_Sprints/Execution_Status]]

## 1. El agente valía 0.5 puntos y tenía cero segundos

Al preguntar quién construyó el chat encontré lo que el guion no decía: el agente conversacional
**no tenía un solo minuto asignado** en los 10 de la demo, y pesa **0.5 de rúbrica**. No estaba
decidido que se dejara fuera; simplemente no se había mirado.

Le abrí un minuto (**6:30–7:30**) y lo saqué de dos recortes, con criterio escrito para que no
parezca arbitrario: **se le da tiempo a lo que sólo existe si se ve en vivo, y se le quita a lo que
el evaluador puede auditar después.** Nadie califica un chat leyendo su código; los PRs, el gate de
propiedad y los DevLogs siguen ahí el jueves.

| Bloque | Antes | Ahora |
|---|---|---|
| Cómo trabajamos (Christian) | 1:00 | 0:30 |
| El modelo (Andrés / Héctor) | 2:00 | 1:30 |

Intocables el de Marina —el diferenciador **es** la tesis— y el de Diana, que carga el peso más alto
de la rúbrica.

## 2. Las preguntas ya existían, y dos de ellas no deben enseñarse

El bloque no necesita inventar nada: `US-323` de **Carlos Mayorga** dejó 20 preguntas en
`tests/fixtures/preguntas_evaluacion.json` — 9 válidas, 6 inseguras, 5 fuera de alcance. Reusarlas
amarra la demo a un entregable ya cerrado.

**Dos de las nueve válidas no deben ir como chip**, y lo verifiqué antes de decirlo:

- *"¿Qué porcentaje de las escuelas en riesgo son por estrés hídrico?"* → `escuelas_en_riesgo` = 0.
  Denominador cero en pantalla.
- *"¿Cuál es el cct de la escuela con latitud más al norte?"* → **no existe `latitud` a nivel
  escuela**; `grep` sobre `dbt/` y `src/` sólo la encuentra en `agua_region` y `aire_estacion`.

Y una precisión que le ahorra el mal rato a quien presente: `test_preguntas_validas_recorrer_flujo_completo`
**mockea** `generar_sql`, `ejecutar_sql` y `redactar_respuesta`. "Validada" ahí significa *en alcance
y segura*, **no** *responde bien contra el Gold real*. Cada chip se corre contra producción antes de
quedar fijo.

## 3. Registros vencidos del agente

Al ir a verlo encontré que los registros del agente llevan una semana desfasados:

- `US-304a`, `US-304b` y `US-305` siguen `in_review` con notas del **28 de agosto** que ya no son
  ciertas: dicen *"falta conectar el endpoint real de C4"* —Christian lo conectó el 29-ago— y citan
  `BUG-024` como abierto, cuando está `fixed`.
- **`BUG-025` dice `open` y el código ya no es el stub**: `src/api/v1/agente.py:95` llama a
  `procesar_consulta()` con los guardarraíles reales. No pude confirmarlo en producción porque
  `/api/v1/agente/consulta` respondió **401** — exige sesión, y las credenciales no las manejo yo.

Se lo paso a Andrés con el encargo de los chips, porque la verificación autenticada cierra el bug y
de paso destraba sus dos historias.

## 4. La cola de PRs, revisada

| PR | Autor | Veredicto |
|---|---|---|
| **#262** | Monserrat Miranda | **Aprobar.** Diagnóstico real y verificado |
| **#263** | Luis Téllez | **No todavía.** Gate de propiedad en rojo y cita un `DEC-018` que no existe |
| **#256** | Deni Garrido | Conflicto **falso**; el bloqueo es de fondo y sigue sin respuesta |

**#262** corrige que `_layout_tabs()` nunca recibió el arreglo de `BUG-049` y ponía cada chart en su
propia fila. Verifiqué su afirmación central —**DB-05 es el único de los 10 tableros con `tabs:`**—
con `grep`, así que el radio de impacto es un solo tablero. Lo mejor del PR es que corrige el
docstring falso que mantuvo vivo el defecto un mes: decía que *"DB-05 y DB-08 van por `_layout_tabs()`"*
y las dos mitades eran falsas.

**#263** trae contenido valioso —la medición del universo completo de producción (45 276 escuelas,
máximo 0.5717, cero sobre el umbral de 0.60)— pero toca dos archivos de C2 fuera de su alcance, y su
DevLog dice que la dueña y el PO lo autorizaron **sin traza en el PR**: cero revisiones, cero
comentarios. Y cita `DEC-018`, que **no está en `main`** —el último es `DEC-017`—, contra `DEC-013`.
Esa decisión es mía y está bloqueando a otros; sube de prioridad.

**#256**: `git merge-tree --write-tree` da limpio y el único archivo tocado por ambos lados es
`vault/_DevLog/_index.md`, que lleva `merge=union`. Es el falso positivo conocido. No lo resuelvo
todavía porque cada merge a `main` lo vuelve a ensuciar; se limpia justo antes de mergear.

## Verificado

`vault_lint.py` limpio · suma de los 8 bloques del guion = **10:00 exactos** ·
`grep "^ *tabs:" superset/dashboards/*.yaml` → sólo `db05` · `grep -rn latitud dbt/ src/` → sólo
`agua_region` y `aire_estacion` · `git show origin/main:…/Decision_Log.md | grep DEC-018` → 0 ·
`git merge-tree --write-tree origin/main origin/dev/deni-garrido` → limpio ·
`curl` a `/api/v1/agente/consulta` → **401**

## IDs tocados

`US-006`, `US-305`, `US-323`, `US-304a`, `US-304b`, `BUG-025`, `DEC-018`, `SEC-006`, `BUG-057`, `US-403`, `US-405`, `REQ-004`, `REQ-006`, `REQ-007`

## 5. `DEC-018` escrita — la postura de acceso deja de ser provisional

La escribí en la misma sesión, porque bloqueaba a dos personas. Cierra lo que
`src/api/config.py:72` marcaba literalmente como *"PROVISIONAL; la definitiva la decide Edgar/PO"*
y que `SEC-006` dejó como decisión de producto: **OAuth de Google en las dos capas**,
`AUTH_LECTURA_PUBLICA=false` en producción, reversible sin rebuild.

**Lo que la hace valer la pena no es la postura, es la asimetría que documenta.** Las dos capas
exigen sesión, pero no filtran igual:

| Capa | Filtro de acceso |
|---|---|
| **Superset** | Lista blanca estricta (`SUPERSET_SSO_ALLOWED_EMAILS`), con guarda fail-loud si queda vacía |
| **API** | **Ninguna.** `resolve_role` devuelve `ciudadano` a cualquier correo que Google autentique |

O sea: **cualquiera con cuenta de Google puede leer la API; nadie fuera de la lista puede abrir
Superset.** Se acepta a propósito —lo que se protege es escritura y admin, y todo el dato es
agregado a nivel escuela, nunca alumno— pero el punto de asentarla es que **no se descubra el
miércoles**.

Y deja escrito el modo de falla que más caro sale: si el correo del evaluador no está en la lista
blanca de Superset, **entra correctamente con Google y lo rechazamos**, sin que nada reviente y sin
un mensaje que lo explique. Darlo de alta antes del 9 es mío.

## Próximos pasos

- Andrés deja los chips y verifica `BUG-025` autenticado.
- Marina carga los dos bloques de C2 de Luis; `DEC-018` ya está publicada y su cita es válida.
- Ensayo del guion completo el **lunes 7-sep**, ahora con 8 bloques.
