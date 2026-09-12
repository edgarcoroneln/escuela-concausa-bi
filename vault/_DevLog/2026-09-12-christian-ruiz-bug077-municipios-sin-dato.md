---
project: "FARO"
date: "2026-09-12"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — mitad de código de BUG-077: /municipios deja de responder 500 por un nulo"
touches: ["BUG-077", "US-621", "US-411", "REQ-004", "SEC-006"]
tags: [devlog, api, contrato, bugfix, gold, sin-dato]
---

# DevLog — 2026-09-12 — `BUG-077`: un nulo en 307 municipios ya no tumba `/municipios`

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

## Seguridad / calidad

- [x] Prueba propia (`test_un_municipio_sin_entidad_degrada_a_sin_dato`), sobre lista **y** detalle
- [x] Verificado campo por campo que `poblacion` ya degradaba, en vez de asumirlo
- [x] 453 pruebas focalizadas verdes; `ruff` y `vault_lint` limpios
- [x] OpenAPI reexportado; `API_Specification` §3.3 documenta el `SIN_DATO`
- [x] Cambio **compatible**: un cliente que ya leía esos campos sigue recibiéndolos cuando hay dato

> **No toqué `Bug_Register.md`** para cerrar `BUG-077`: el PR de Luis (`BUG-078`/`079`/`080`) edita ese
> mismo archivo y entra antes; dos PRs agregando filas a la misma tabla es un conflicto innecesario.
> El cierre lo registra QA cuando confirme las dos mitades — la de Diana sigue abierta.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** este DevLog.
- **Modificados:** `src/api/schemas.py`, `tests/test_api_contract.py`, `api/openapi.v1.json`,
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
- **Edgar Coronel (PO/QA):** el cierre de `BUG-077` queda a tu criterio con las dos mitades.
