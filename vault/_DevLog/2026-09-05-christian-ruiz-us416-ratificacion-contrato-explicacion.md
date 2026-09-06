---
project: "FARO"
date: "2026-09-05"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — ratificación de US-416, cierre de una ventana de KeyError en el cache y alineación del contrato de /predicciones"
touches: ["US-416", "US-412", "US-422", "REQ-004", "SEC-010"]
tags: [devlog, celula-4, api, cache, contrato, rbac, shap, us416]
---

# DevLog — 2026-09-05 — Ratificación de US-416, ventana de `KeyError` en el cache y contrato de `/predicciones`

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/API_Specification|API_Spec §2.2, §3.4]] ·
[[vault/02_Requirements/Traceability_Matrix|Matriz REQ-004]]

## Contexto

Juan Macías pidió, como condición única de cierre de **US-416**, que el TL de C4 ratificara el
diseño del cache y el endurecimiento a `SQLAlchemyError`, y que se confirmara si el E2E con Postgres
real corresponde a **US-422**. Revisando ese código aparecieron dos cosas más que no estaban en la
petición.

## Qué se hizo

### 1. Ratificación de US-416 (🟢, con una corrección)

Leído el código, no solo el reporte. Las tres decisiones se sostienen; la mejor es **`SET LOCAL` en
vez de `SET`**: muere con la transacción y no deja un `statement_timeout` pegado en conexiones que
vuelven al pool compartido con `RepositorioGold`. El endurecimiento a `SQLAlchemyError` es el mismo
aprendizaje que me costó `codigos_login.py` — la excepción que tumba el servicio nunca es la que
anticipaste.

**Confirmado:** el E2E con Postgres real es **US-422** (*"pruebas unitarias y de integración de la
API"*, Eloisa González Rubio, C4, S4, REQ-004).

### 2. Una ventana real de `KeyError` → 500 en el cache (corregida)

`cache_predicciones.py` leía el cache con `if clave in self._cache:` seguido de `self._cache[clave]`.
En `cachetools` 7.1.8 **cada una de esas operaciones consulta el reloj por separado**, así que una
entrada vigente en el `in` puede estar caducada en el `[]` y lanzar `KeyError`, que subiría al
handler genérico como **500**. El `Lock` no protege de esto: guarda el estado compartido, no detiene
el reloj.

En producción la ventana son microsegundos y la probabilidad es minúscula — **no era bloqueante**.
Se corrigió porque el arreglo es una línea y estrictamente mejor: `.get(clave, _AUSENTE)`, una sola
consulta al reloj, con un sentinel propio porque `None` es un valor legítimo aquí.

Dos pruebas de regresión con un reloj que avanza en **cada** consulta (un `_RelojFalso` quieto no
reproduce la ventana). **Comprobado que reprueban con el patrón viejo**, con el `KeyError` exacto.

### 3. El contrato prometía más restricción de la que el código aplica

`API_Specification` §2.2/§3.4 y los docstrings de `v1/predicciones.py` decían que
`/predicciones/batch` y `/predicciones/{cct}/explicacion` son **solo `analista`** y devuelven `403`.
**Nunca fue cierto:** el router se monta con `require_lectura` en `v1/__init__.py`, igual que `gold`
y `agente`. La frase *"se forzará en US-403"* sobrevivió al cierre de US-403.

No es un hueco de seguridad —el comportamiento es el diseñado, el flag híbrido— pero es la clase de
desajuste que se descubre en una demo: alguien lee el contrato, entra como `ciudadano` y obtiene 200
donde el documento decía 403.

**Resuelto a favor del código, deliberadamente.** Restringir ahora a `analista` rompería a cualquier
consumidor de C2/C3 que llame estas rutas como `ciudadano`, y es una **decisión de producto**, no una
corrección de documentación, a dos días del freeze. Hacerlo después es una línea en `v1/__init__.py`.
El estado real queda **fijado por pruebas**: si alguien restringe sin actualizar el contrato,
`test_como_ciudadano_da_200` reprueba.

### 4. `/explicacion` no tenía ninguna prueba, y no puede tener SHAP todavía

Andrés González (C3) pidió que C4 reemplace el mock por las contribuciones SHAP reales. **El bloqueo
no es el mock:** `entrenar_ml02.py::explicar_driver` calcula SHAP con la forma exacta de
`ExplicacionSHAPOut`, pero **no la llama nadie** (`grep`: solo su propia prueba), y `publicar_gold.py`
escribe únicamente `gold.predicciones` y `gold.recomendaciones` — ninguna guarda contribuciones. **No
existe fuente que leer.**

Calcularlo por petición no es opción: `shap` vive en `requirements/celula-3.txt`, no en la imagen de
la API, y `KernelExplainer` tarda segundos por fila — incompatible con el `statement_timeout` y la
degradación 503 que se acaba de ratificar en US-416.

Se escribió `tests/test_explicacion_shap.py` (8 casos) para **fijar el contrato de respuesta ahora**,
de modo que cuando C3 persista en Gold el cambio sea del cuerpo del endpoint y no de la forma que ya
consumen el frontend y el agente.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** `tests/test_explicacion_shap.py`, este DevLog.
- **Modificados:** `src/api/cache_predicciones.py`, `src/api/v1/predicciones.py`,
  `tests/test_cache_predicciones.py` (+2), `vault/03_Architecture/API_Specification.md` (§2.2, §3.4),
  `api/openapi.v1.json`, `vault/_DevLog/_index.md`.
- **Nota:** al reexportar el OpenAPI aparecieron referencias a **`ADR-009`** que quedaron del rename
  a ADR-010 — el snapshot llevaba desactualizado desde entonces. Corregidas de paso.

## Seguridad / calidad

- [x] **10 pruebas nuevas** (2 de regresión del cache + 8 de contrato de `/explicacion`)
- [x] Las 2 de regresión **reprueban con el código anterior**, comprobado
- [x] `pytest` sobre la superficie de API → **137 passed**
- [x] `ruff check src/api tests` → limpio
- [x] `scripts/export_openapi.py` reexportado; `test_api_contract.py` → 32 passed

## Bloqueantes / avisos a otros owners

- **Andrés González (C3):** el orden para cerrar la explicación es **C3 persiste SHAP en Gold → C4
  lee → prueba**. El primer paso no es de esta célula y es el que decide si entra antes del freeze.
  Mi parte son un par de horas una vez exista la fuente. `src/modelos/**` y `dbt/**` no son míos, así
  que no toqué nada ahí.
- **Juan Macías (C4):** toqué `cache_predicciones.py` (mi alcance verde) por la ventana de `KeyError`.
  Nada del diseño cambió — solo cómo se lee el cache.
- **Edgar (PO) — cuarto hueco de propiedad:** `guia-ambiente-local/` en la raíz **no está en
  `ownership.yml`** (ni verde, ni amarillo, ni comunes). Marina y Montserrat detectaron que
  `guia-ambiente-local/configuracion.env` está versionado: son 6 líneas de puertos, **sin
  credenciales**, riesgo bajo, pero incumple `Secrets_Policy`. `.gitignore` ya trae `*.env` desde el
  3-sep; ignorar **no des-trackea**, hace falta `git rm --cached`. **Nadie puede hacerlo hoy sin que
  el gate lo repruebe.** Van cuatro huecos: `ADRs/**`, `.env.example`, `requirements.txt` y este.
- **Producto (Edgar + C2/C3):** si se quiere que la explicación y el batch sean de verdad solo
  `analista`, es una línea en `v1/__init__.py`, pero necesita el visto bueno de quien consuma esas
  rutas. Hoy queda documentado como está.

## Próximos pasos

1. Login e2e real (sigue siendo el mayor riesgo abierto de C4; depende de los *test users* de C5).
2. Con token real de `ciudadano`, cerrar **AC-004.5**: 403 contra `/admin/*`.
3. Conectar `/explicacion` en cuanto C3 persista las contribuciones.
