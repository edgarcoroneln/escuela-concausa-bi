---
project: "FARO"
date: "2026-08-30"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "2h"
touches: ["US-004", "REQ-007", "BUG-020", "BUG-025", "BUG-033", "BUG-019", "DEC-012", "DEC-013", "BLOCK-002", "ADR-007"]
tags: [devlog, pm, reconciliacion, gobernanza]
---

# DevLog — 2026-08-30 — Reconciliación posterior a la ratificación de ADR-007

→ [[_DevLog/_index|Volver al índice]]

## Por qué esta pasada

Entre el 29 y el 30 de agosto se mergearon quince PR (#133 a #147). Dos de ellos cambian hechos que
el vault seguía declarando de otra forma, y ninguno es un detalle: **BUG-020 quedó curado en
producción** y **el agente dejó de ser un stub**. Un registro que sigue diciendo `critical / open`
sobre algo ya resuelto cuesta tan caro como uno que declara resuelto lo que no lo está.

## Lo que verifiqué antes de escribir

No actualicé el registro contra los DevLogs ajenos, sino **contra la URL pública**:

```
/api/v1/health              HTTP 200
/api/v1/version             HTTP 200
/api/v1/escuelas            HTTP 200   (antes 500)
/api/v1/municipios          HTTP 200   (antes 500)
/api/v1/kpis                HTTP 200   (antes 500)
/api/v1/predicciones/{cct}  HTTP 404   (antes 500)
```

Coincide exactamente con lo que reportó Luis en US-505. **BUG-020 → `fixed`.**

El `404` de `/predicciones/{cct}` **no es el bug**: la base conecta y la ruta responde con su error
estructurado. `gold.predicciones` está vacío en producción, y eso lo destraba el paso 1 de ADR-007,
que es de Célula 1.

De paso quedó rectificado un error de alcance que este registro arrastraba: afirmaba que la
autenticación «no se podía comprobar en producción, y eso toca US-402». Era falso —`/auth/login`
responde 302 y `/auth/me` responde 401— y ya estaba escrito en un documento que la gente lee.

## El agente: una buena noticia y una mala

El PR #142 conectó `/agente/consulta` al servicio real. Verificado:

```
"cual es la capital de Francia"   -> {"fuera_de_alcance": true,  "sql_generado": null}
"cuantas escuelas hay en riesgo"  -> {"fuera_de_alcance": false, "sql_generado": null}
```

La primera respuesta prueba que **BUG-025 está cerrado**: ya no devuelve la misma cadena a todo, y
quien decide es el guardarraíl real de `src/agente/guardrails.py`, no la lista de subcadenas del
stub.

La segunda destapa un problema nuevo. Una pregunta legítima devuelve *«El contexto de FARO no está
disponible temporalmente»*. Mi primera lectura fue «solo falta desplegar ChromaDB»; al revisar el
PR #148 de Luis resultó ser bastante más, y el registro habría inducido a error si lo dejo así.

El servicio necesita **cuatro colaboraciones** y **ninguna está conectada**: `recuperar_contexto`
falla porque ChromaDB no está desplegado, y `generar_sql`, `ejecutar_sql` y `redactar_respuesta`
levantan `AgenteNoConfigurado` por defecto. Lo comprobé: `grep` sobre `src/` y sobre todos los
`requirements` **no encuentra ningún cliente LLM** —ni declarado como dependencia—, así que el
Text-to-SQL, que es el núcleo del agente, no está escrito. Desplegar ChromaDB destraparía la primera
pieza y la siguiente pregunta fallaría en la segunda.

Queda como **BUG-033** con las cuatro piezas y sus dueños, separado de BUG-025 porque aquello era el
stub y esto es la cadena incompleta detrás del seam. Bloquea el punto de rúbrica del agente (0.5).

También corregí la acreditación de BUG-025: lo cerró el PR #142 (código) **más el PR #148** (el
redeploy). Mergear a `main` no cambiaba producción — Cloud Run seguía sirviendo la imagen
`v0.2.1-hotfix-bug008` hasta que Luis reconstruyó y redesplegó. Vale como recordatorio general: en
este proyecto **un bug de producción no se cierra con un merge, se cierra con un deploy verificado.**

## Dos decisiones que solo existían en conversaciones

**DEC-012 — criterio de cierre por superficie desplegada.** Nació de una asimetría que encontró
Héctor al revisar la reconciliación del 28-ago: US-411 se sostenía abierta por BUG-020 mientras
US-412 —que entrega `/predicciones/*`, rotas en el mismo despliegue— se cerraba difiriendo el E2E a
una historia que ni siquiera había arrancado. La regla queda escrita: *una historia cuyo entregable
es una ruta HTTP no cierra mientras esa ruta no responda en el despliegue que se va a demostrar; una
cuyo entregable es un contrato o una biblioteca sí*.

**DEC-013 — reserva de identificadores.** Tres colisiones de `BUG-###` en una semana, todas por
acuerdos verbales. La regla: **un número queda reservado únicamente cuando está escrito en su
registro canónico en `main`.** Un hueco en la numeración es aceptable; un duplicado no.

Las dos venían aplicándose de hecho desde hace días sin estar registradas, que es exactamente la
situación que ADR-007 acaba de corregir en su propio terreno: un acuerdo que solo vive en la memoria
de quienes estuvieron no es un acuerdo.

## Un defecto en el propio registro de estados

`US-004` tenía **ocho columnas** en una tabla de seis. Dos causas sumadas: un pipe sin escapar dentro
del alias de un wikilink —`[[…|texto]]` en vez de `[[…\|texto]]`— y una celda de fecha duplicada al
final. Ninguna herramienta lo detecta: `vault_lint` no valida la forma de las tablas y el generador
del tablero lee la fila con una expresión regular que tolera columnas de más.

Vale la pena anotarlo como deuda: **los documentos marcados `source_of_truth: true` no tienen una
comprobación de integridad de su propia tabla.** Escribí el contador de columnas para verificar mi
propia corrección y, al pasarlo por los cuatro registros canónicos, apareció lo mismo en el
`Bug_Register`: `BUG-010` tenía seis columnas y `BUG-032` ocho, en una tabla de siete. Ambas
corregidas —a `BUG-010` le faltaba separar las pruebas de regresión, y a `BUG-032` le sobraba una
celda con el dueño—.

Son tres filas rotas en dos documentos que el proyecto declara fuente de verdad, y ninguna herramienta
las veía. Un contador de columnas por fila en `vault_lint` es media hora de trabajo y las habría
atrapado el día que se introdujeron. Queda propuesto para después del code freeze; tocar `_Meta/scripts`
hoy abriría una revisión de regla 7 que no urge.

## Lo que quedó

- `Bug_Register`: BUG-020 `fixed` con evidencia en vivo · BUG-025 `fixed` · **BUG-033** registrado ·
  BUG-019 anotado (decidido por ADR-007, pendiente de implementar).
- `Blocker_Register`: **BLOCK-002** — el paso 1 de ADR-007, sin dueño.
- Integridad de tablas: `US-004` (8→6 columnas), `BUG-010` (6→7) y `BUG-032` (8→7).
- `Decision_Log`: **DEC-012** y **DEC-013**.
- `Execution_Status`: US-004 (corregida), US-104 (anotada), US-304a, US-304b, US-305, US-313, US-411, US-412, US-524a.
- `Traceability_Matrix`: bloque de evidencia del 30-ago para REQ-004/005, REQ-006 y REQ-007.
- Tablero PM regenerado.

## «Ratificado» se está leyendo como «resuelto»

Al revisar esta pasada surgió que ADR-007 se daba por implementado. **No lo está**, y conviene dejar
por qué con evidencia y no con opinión:

```
dbt/models/gold/features_escuela.sql:71
    cast(matricula_total - matricula_ciclo_anterior as double precision)
        as target_variacion_matricula          <- alumnos absolutos, no fracción
```

Los cuatro pasos del ADR siguen pendientes. El paso 2 tampoco está: la línea 74 filtra
`matricula_ciclo_anterior is not null`, pero `matricula_previa == 0` no se rechaza explícitamente. Y
`verificar_escala_variacion()` en `src/modelos/riesgo.py:171` sigue deteniendo la publicación, que es
la prueba operativa de que la unidad no cambió.

El propio PR #147 lo decía —«ratificar no cambia el dato», con la tabla de lo que falta— pero el
frontmatter dice `status: accepted` y eso es lo que la gente escanea. **Un ADR aceptado describe una
decisión tomada, no un cambio aplicado.**

La corrección no es documental sino de seguimiento: el trabajo pendiente no vivía en ningún registro
que el tablero PM lea. Queda como **BLOCK-002**, con dueño explícitamente `SIN ASIGNAR` para que el
hueco se vea en vez de esconderse en la prosa de un ADR. Anotado también en la fila de `US-104`
—cuyo artefacto es el que hay que cambiar— y en `BUG-019`, que sigue `open` por esta razón exacta.

## Lo que sigue, en orden de lo que topa la nota

1. **BLOCK-002 · paso 1 de ADR-007** — normalizar el target a fracción y reprocesar Gold. Bloquea los
   otros tres pasos, US-313, US-412 y la demo de ML. **Sigue sin dueño asignado.**
2. **BUG-033** — desplegar ChromaDB e indexar el esquema, o declarar el fallback en el guion.
3. **BUG-031** — KPI-02 pinta −54.5 % donde el valor real es −0.19 %, en seis tableros.
4. **PR #102** — conflicto por resolver y visto bueno de C5; sin conflicto no ha corrido el CI nunca.
5. **PR #87** — sin movimiento desde el 26-ago.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Archivos modificados:** `06_Quality_Testing/Bug_Register.md`,
  `10_Risk_Governance/Decision_Log.md`, `12_Roadmap_Sprints/Execution_Status.md`,
  `02_Requirements/Traceability_Matrix.md`, tablero PM generado, `_DevLog/_index.md` y esta entrada.
- **Decisiones autónomas del agente:**
  - Verificar la URL pública en vivo antes de cambiar cualquier estado, en vez de confiar en los
    DevLogs de quienes reportaron el arreglo.
  - Registrar **BUG-033** aparte en lugar de reabrir BUG-025: la causa y el dueño son distintos.
  - **No** cerrar US-411 ni US-412 pese a cumplirse DEC-012: la primera espera la validación de
    Karla y la segunda no tiene datos en Gold. Cerrar una historia es decisión del PM con su dueño.
- **Correcciones manuales:** ninguna; cada edición se aplicó con aserciones que abortan sin escribir
  si el texto de origen no coincide.
