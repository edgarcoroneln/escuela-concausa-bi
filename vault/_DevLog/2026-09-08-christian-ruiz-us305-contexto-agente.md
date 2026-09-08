---
project: "FARO"
date: "2026-09-08"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — parte de C4 de US-305: contrato validado del contexto conversacional"
touches: ["US-305", "US-404", "US-403", "DEC-020", "REQ-004", "SEC-003"]
tags: [devlog, celula-4, api, agente, contrato, seguridad, us305]
---

# DevLog — 2026-09-08 — Parte de C4 de `US-305`: el contexto conversacional del agente

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/API_Specification|API_Spec §3.5]] ·
[[vault/10_Risk_Governance/Decision_Log|DEC-020]]

## Contexto

El chat no resuelve preguntas de seguimiento. *"¿Cuáles son las escuelas en riesgo?"* funciona;
*"¿y las recomendaciones para **esas** escuelas?"* no, porque el frontend manda solo la pregunta
actual y el LLM no tiene de dónde sacar los CCT.

Andrés González (C3) ya cerró su mitad en `main` (`e6ed616`): `procesar_consulta()` acepta
`contexto_conversacional`, detecta preguntas referenciales y pide aclaración en vez de inventar SQL.
Pero ese seam era **inalcanzable por HTTP**: `/agente/consulta` nunca lo llenaba. Esta sesión abre
la puerta, y por eso mismo es donde tiene que estar la validación.

## La decisión que ordena todo lo demás

Andrés propuso dos contratos: mandar `historial` crudo (pregunta, respuesta y **`sql_generado`** de
cada turno) o mandar `contexto` estructurado. Él ya recomendaba el segundo; aquí queda cerrado el
porqué, que no es de tamaño sino de confianza.

**El contexto lo escribe el cliente. No es estado de sesión: es entrada, y hay que tratarla como
hostil.** `/agente/consulta` es público bajo `require_lectura`, así que cualquiera puede mandar lo
que quiera ahí con un `curl` — no hace falta pasar por el frontend. Y cada valor del contexto entra
**literalmente** al prompt del sistema (`src/agente/prompt.py` lo interpola en un bloque de texto).

Aceptar `sql_generado` habría significado que la API recibe SQL del cliente y se lo devuelve al LLM
como si fuera propio. Con `contexto` estructurado + `extra="forbid"`, mandar un `sql` en el cuerpo
**es un 422**, no un campo ignorado en silencio.

## Qué se hizo

**`src/api/schemas.py`** — `ContextoConversacionalIn`, y `AgenteConsultaIn.contexto` opcional.

| Campo | Regla | Por qué |
|---|---|---|
| *(cualquier otro)* | `extra="forbid"` → 422 | No hay puerta para SQL ni para `rol` |
| `ccts` | `^[0-9A-Z]{10}$`, máx. 200 | Sin comillas ni saltos de línea que alteren el prompt |
| `ciclo` | `^\d{4}-\d{4}$` | — |
| `filtros` | máx. 10, 100 chars, sin caracteres de control | Se interpolan en el prompt |
| `resumen` | máx. 300 chars, sin caracteres de control | Texto libre: el campo más peligroso |

Dos decisiones al escribirlo:

1. **El CCT se valida por forma, no por estructura.** El patrón canónico es
   `\d{2}[A-Z]{3}\d{4}[A-Z]`, pero rechazar un CCT real por una variante de formato rompe el chat,
   mientras que lo que de verdad hay que impedir —espacios, saltos de línea, comillas— ya lo impide
   `^[0-9A-Z]{10}$`. **Que el CCT exista lo decide Gold, no el contrato.**
2. **`resumen` es el único texto libre, y por eso el único con validador propio.** Un `\n` ahí
   permitiría cerrar el bloque de contexto y escribir instrucciones falsas en el prompt. Se rechazan
   los caracteres de control con `str.isprintable()`, que no toca acentos ni signos del español —hay
   una prueba que lo fija, porque un filtro demasiado celoso aquí rompe el uso legítimo.

**`src/api/v1/agente.py`** — pasa `body.contexto.model_dump()` al servicio. Una línea. El resto del
cambio es contrato.

**`api/openapi.v1.json`** reexportado.

## Pruebas

`tests/test_agente_contexto.py`, **30 casos** en seis bloques. Los que importan:

- `test_los_ccts_del_contexto_llegan_al_prompt` — espía el prompt que arma el servicio. **Verificado
  que reprueba** al quitar la línea del endpoint: sin ella, todo lo demás pasaría igual y el cambio
  parecería hecho sin estarlo.
- `test_un_campo_desconocido_en_el_contexto_da_422[sql|sql_generado|rol|historial]` — la puerta que
  no se abre.
- `test_un_resumen_con_saltos_de_linea_da_422` y `test_un_filtro_con_salto_de_linea_da_422`.
- `test_un_resumen_normal_con_acentos_si_pasa` — el contrapeso del anterior.
- `test_un_cct_con_forma_invalida_da_422[...'; DROP TABLE...]`.
- `test_un_sql_destructivo_del_llm_no_se_ejecuta_aunque_haya_contexto` — el guardarraíl de C3 sigue
  puesto; el contexto no es una vía para ablandarlo.
- `test_sin_contexto_sigue_funcionando_igual` — retrocompatible: el frontend actual no se entera.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** `tests/test_agente_contexto.py`, este DevLog.
- **Modificados:** `src/api/schemas.py`, `src/api/v1/agente.py`, `api/openapi.v1.json`,
  `vault/03_Architecture/API_Specification.md` (§3.5, `version: 1.2`), `vault/_DevLog/_index.md`.

## Seguridad / calidad

- [x] 30 casos nuevos; 108 verdes en toda la superficie del agente + contrato
- [x] `ruff check .` (todo el repo, como el CI) limpio
- [x] OpenAPI reexportado; `test_api_contract.py` verde
- [x] Suite completa: mismas fallas de colección que `main` en esta máquina (faltan `psycopg2`,
      `sklearn`, `scipy`, `yaml`, `great_expectations` en el venv local)
- [x] La prueba clave verificada **reprobando** con el cambio desactivado

## ⚠️ Bloqueante de gobernanza

**`DEC-020` no cubre esto.** La excepción al *code freeze* tiene alcance cerrado —`US-405`, `US-207`,
`US-206`— y **corte a las 18:00 del 6-sep**. `US-305` no está en esa lista, y el propio plan de
Andrés pone como paso 1 *"Edgar confirma que el contexto conversacional entra en la demo"*, que al
momento de escribir esto **no ocurrió por escrito**.

La mitad de C3 ya está mergeada en `main` (`e6ed616`, PR #283), así que de hecho el equipo ya se
movió. Lo dejo dicho igual: **no mergeo esto sin que el PO lo autorice**, sea ampliando `DEC-020` o
con una decisión nueva. Es el mismo criterio con el que esperé la firma de `DEC-019`.

## Avisos a otros owners

- **Andrés González (C3):** el seam quedó conectado con el contrato que recomendaste. Nota para
  `agente_client.py`: los CCT tienen que ir en **mayúsculas** y el `resumen` en **una sola línea**;
  si extraes el resumen de la respuesta del LLM, normalízalo antes de mandarlo o te va a llegar 422.
- **Manuel Serranía (C2) / `3_Chat.py`:** el frontend guarda por turno pregunta, respuesta, CCTs,
  ciclo y filtros. **No mandes la respuesta libre del LLM como `resumen` sin recortarla** — el
  límite son 300 caracteres.
- **Luis Téllez (C5):** esto **no** cambia variables de entorno ni dependencias. Es contrato y
  validación; entra con el redespliegue normal de la API.
- **Karla Monter (C4, dueña de `API_Specification`):** subí la §3.5 y `version` a 1.2. El documento
  sigue en `in_review`.

## Próximos pasos

1. Autorización del PO (ver el bloqueante).
2. C3/C2 conectan `agente_client.py` y `3_Chat.py`.
3. C5 redespliega API y agente.
4. Prueba de aceptación en producción: pregunta inicial → CCTs → seguimiento → SQL filtrado por
   esos CCTs → recomendaciones reales, sin 401 ni timeout.
