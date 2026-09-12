---
project: "FARO"
date: "2026-09-12"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — BUG-077 (el 500 de /municipios) y los dos pendientes de contrato de Diana"
touches: ["BUG-077", "US-621", "US-411", "US-212", "BUG-031", "REQ-004", "SEC-006"]
tags: [devlog, api, contrato, bugfix, gold, sin-dato]
---

# DevLog — 2026-09-12 — `BUG-077`, y los dos campos que el frontend pedía por escuela

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/06_Quality_Testing/Reporte_QA_Regresion_S7_2026-09-12|Reporte QA de la regresión]] ·
[[vault/03_Architecture/API_Specification|API_Specification §3.3]]

## Contexto

QA (Edgar) encontró en la regresión del 12-sep que **`GET /api/v1/municipios` responde 500**, tanto en
el listado como en el detalle, y Luis lo trajo al equipo con la causa raíz ya verificada con `curl` y
consulta directa a Postgres: `gold.dim_municipio` tiene `nombre_entidad` y `poblacion` nulos en **307
de 317 municipios**, y `MunicipioOut.nombre_entidad` era `StrictStr` obligatorio.

**El defecto es mío y del PR anterior.** Al exponer `cve_ent`/`nombre_entidad` para el frontend
(`US-621`) los declaré obligatorios, sin manejo de `SIN_DATO` — el único campo de ese modelo que no
degradaba como los demás. `BUG-077` tiene dos mitades: el **dato** (Diana: si producción comparte el
hueco de cobertura CONEVAL) y el **código**, que es esto.

No rompía el login, que quedó cerrado hoy en producción, pero tumbaba **cualquier pantalla que liste
municipios**: explorador territorial y mapa.

## Qué se hizo

`cve_ent` y `nombre_entidad` pasan a `None` = `SIN_DATO`, igual que `poblacion`,
`indice_rezago_social` y `pobreza_pct`. **Las claves siguen presentes** en la respuesta: el hueco se
declara, no se omite, que es lo que permite al cliente distinguir *"no hay dato"* de *"no me lo
mandaron"*. El front pinta el municipio sin la etiqueta de entidad en vez de quedarse sin tabla.

**Lo que hacía grave a un error de una línea:** con la validación de salida en un campo obligatorio,
un hueco en **una** fila reventaba la **página completa**. No era "307 municipios sin entidad", era
"ningún municipio", y además en el detalle de cada uno de esos 307.

`poblacion` ya degradaba bien desde `US-103`; lo verifiqué campo por campo antes de tocar nada, en vez
de asumir que el reporte cubría los dos. `nombre_municipio` **también** reventaría con un nulo y **no
lo cambié**: un municipio sin nombre es una fila de dimensión rota, no un hueco de cobertura, y
relajarlo es una decisión de contrato aparte que no corresponde tomar en el freeze.

## Dos cosas que aprendí escribiendo la prueba

- **El repositorio con el hueco se inyecta solo en ese caso**, en vez de agregar la fila a
  `MUNICIPIOS_FAKE`: una `poblacion` en `None` en el fixture compartido habría cambiado el orden que
  verifican las pruebas de `order_by`. Un fixture nuevo no debe mover las pruebas existentes.
- **El override se restaura en un `finally`**, porque el fixture `client` de `test_api_contract.py` es
  de **módulo**: sin eso, el repositorio con hueco se filtraba al resto del archivo y hacía fallar una
  prueba que no tenía nada que ver con este cambio. Me pasó, y quedó comentado ahí.

## Los dos pendientes de Diana, en el mismo PR

Diana tenía asignados dos puntos y **ninguno estaba resuelto**. Los dos salen del mismo lugar:
`gold.fact_escuela_ciclo`, que el listado de `/escuelas` **ya tiene unida**, así que ninguno agrega
una consulta.

### Los seis drivers en lote

`d1`..`d6` e `indice_completitud_drivers` vivían solo en `/escuelas/{cct}`: llenar la matriz de
drivers o el mapa costaba **una petición por escuela**. Ahora viajan en el listado; el detalle los
hereda, no los pierde.

`indice_completitud_drivers` pasa a **opcional**, y es a propósito: era obligatorio, y `BUG-077` —de
este mismo día— mostró exactamente lo que cuesta eso cuando llega un nulo. En el listado el radio de
daño es mayor que en el detalle, así que no repito el error dos veces en un día.

### La "serie histórica" no existe, y lo que existe son dos puntos

`/series` se declaró fuera de alcance en `US-411`, y la gráfica de matrícula pertenecía a `US-212`,
que se consumía como cubo de Superset — retirado por `ADR-012`. Así que la petición, tal como está
escrita, no tiene fuente.

Lo que sí existe es mejor que nada: `fact_escuela_ciclo` ya materializa `matricula_ciclo_anterior` y
`variacion_matricula` (las expuso Diana en `BUG-031`). Ahora viajan en el contrato. **Con dos puntos
se dibuja un cambio, no una tendencia**, y eso quedó escrito en la especificación para que la UI no
lo presente como línea de tiempo. Una serie real de 3 ciclos es una ruta nueva (`/escuelas/{cct}/series`)
y no se abre alcance nuevo a un día del freeze sin decisión del PO.

Verifiqué antes de tocar nada que un `Decimal` de Postgres —`d3`, `d4` e `indice_completitud_drivers`
son `numeric`— no rompe la validación de salida, en vez de asumirlo: Pydantic lo convierte. Era el
riesgo obvio después de `BUG-077`.

## Humo del contrato contra el despliegue real

`BUG-079` dejó la lección clara: **el código en `main` no cambia producción**. La imagen desplegada era
del 8-sep y el login estuvo roto días con el arreglo ya mergeado. `BUG-077` es del mismo tipo — hasta
que se rehaga la imagen, `/municipios` sigue en 500 allá arriba.

`tests/test_smoke_contrato_prod.py` contesta la pregunta que el CI no puede contestar: **¿lo que está
arriba es lo que mergeamos?** Se salta completo salvo que se pida con `FARO_SMOKE=1`, porque sale a la
red y depende de un despliegue que no controla.

- **Sin sesión** verifica salud y que `/version` publique `cortes_atencion`. Con eso solo ya se sabe si
  la imagen es anterior al contrato actual, y el mensaje de fallo incluye el commit desplegado.
- **Con sesión** (`FARO_SMOKE_COOKIE`, `SEC-006`) verifica que `/municipios` **no** responda 500 con los
  huecos de cobertura, que el detalle de un municipio sin entidad tampoco reviente, y que `/escuelas`
  traiga drivers, coordenadas y la comparación de ciclo. Si faltan campos, el mensaje dice
  explícitamente que hay que reconstruir y redesplegar.
- **La credencial se lee del entorno, nunca se imprime, y los cuerpos de respuesta no entran a los
  mensajes de error**: en una ruta autenticada traen datos reales (`Secrets_Policy.md`).

Corriéndolo ya contra producción, la parte pública **pasa**: la imagen desplegada sí incluye los cortes
del nivel de atención. Lo que falta es este PR.

## Seguridad / calidad

- [x] Prueba propia (`test_un_municipio_sin_entidad_degrada_a_sin_dato`), sobre lista **y** detalle
- [x] Dos pruebas de los campos nuevos; la de drivers exige que el fixture **tenga** un hueco, para
      que no pueda pasar por casualidad cuando no hay nulos en los datos de prueba
- [x] Verificado campo por campo que `poblacion` ya degradaba, en vez de asumirlo
- [x] 436 pruebas focalizadas verdes; `ruff` y `vault_lint` limpios
- [x] OpenAPI reexportado; `API_Specification` §3.3 documenta el `SIN_DATO`
- [x] Cambio **compatible**: un cliente que ya leía esos campos sigue recibiéndolos cuando hay dato

> **No toqué `Bug_Register.md`** para cerrar `BUG-077`: el PR de Luis (`BUG-078`/`079`/`080`) edita ese
> mismo archivo y entra antes; dos PRs agregando filas a la misma tabla es un conflicto innecesario.
> El cierre lo registra QA cuando confirme las dos mitades — la de Diana sigue abierta.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** este DevLog, `tests/test_smoke_contrato_prod.py`.
- **Modificados:** `src/api/schemas.py`, `src/api/repositorio_gold.py`,
  `tests/test_api_contract.py`, `tests/fixtures_gold.py`, `api/openapi.v1.json`,
  `vault/03_Architecture/API_Specification.md`, `vault/_DevLog/_index.md`.

## Verificación del login en producción (12-sep)

Aparte del arreglo, comprobé lo que avisó Luis: `/auth/login?redirect=<origen del front>` devuelve
**302** donde ayer devolvía **400**, `faro-frontend` ya sirve el build de React y no Streamlit, y
`/api/v1/health` por el proxy del front responde `application/json`. Los tres bloqueos del corte del
viernes están cerrados.

Sigue en **400** `http://localhost:5173`, el origen local de Diana: si lo quieren para desarrollo, hay
que agregarlo a `FRONTEND_REDIRECT_URIS` junto con el de producción.

## Avisos a otros owners

- **Luis Téllez (C5):** la mitad de código de `BUG-077` está lista. **Sí hace falta reconstruir y
  redesplegar la imagen de la API** para que el arreglo llegue a producción — igual que con `BUG-079`,
  el código en `main` no cambia nada hasta que la imagen se rehace.
- **Diana Alvarez (C1):** sigue abierta tu mitad — si producción comparte el hueco de cobertura
  CONEVAL de los 307 municipios. Con este cambio el endpoint ya **no se cae** en ninguno de los dos
  casos, así que deja de ser bloqueante del freeze, pero el dato sigue faltando y la etiqueta de
  entidad saldrá vacía donde no haya fila.
- **Edgar Coronel (PO/QA):** el cierre de `BUG-077` queda a tu criterio con las dos mitades. Y queda
  una decisión tuya pendiente: si se abre `GET /escuelas/{cct}/series` para la serie real de 3 ciclos,
  que es alcance nuevo. Con los dos puntos actuales el frontend ya puede contar el cambio.
- **Marina García (E3):** la matriz de drivers ya es construible con una sola petición. `null` sigue
  siendo "pista que no pudimos verificar", nunca cero.
