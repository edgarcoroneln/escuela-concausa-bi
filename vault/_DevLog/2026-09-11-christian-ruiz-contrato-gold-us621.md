---
project: "FARO"
date: "2026-09-11"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — tres huecos del contrato de lectura que bloqueaban al frontend de React"
touches: ["US-621", "US-411", "US-412", "REQ-004", "DEC-019", "BUG-063"]
tags: [devlog, api, contrato, gold, frontend, react]
---

# DevLog — 2026-09-11 — Tres campos que el frontend necesitaba y el contrato no declaraba

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/API_Specification|API_Specification §3.3-3.4]]

## Contexto

Con Streamlit retirado (`ADR-012`), el frontend de React consume la API directamente y aparecieron
tres huecos del contrato. Los tres tienen la misma forma: **el dato ya estaba en Gold y la consulta ya
lo traía; lo que faltaba era declararlo en el esquema de salida.** Ninguno agrega una consulta nueva.

Los pedidos vienen de Diana Alvarez (E5, frontend) y Marina García (E3, storytelling). Los tres
cambios son **aditivos**: ningún cliente existente cambia de comportamiento.

## Qué se hizo

### 1. `MunicipioOut` declara la entidad

`select(dim_municipio)` ya devolvía `cve_ent` y `nombre_entidad`, pero el esquema los descartaba. El
cliente tenía que mantener su propio mapa de 4 claves a nombre, o pintar `"09"` en una etiqueta.
Ahora viajan **en la lista y en el detalle** —solo en el detalle costarían una petición por fila— y
además se puede **ordenar** por ellos, que es lo que necesita una tabla agrupada por entidad.

### 2. `EscuelaOut` trae las coordenadas

Vivían solo en `EscuelaDetalleOut`, así que pintar los 7 casos del storytelling costaba **7 llamadas**
a `/escuelas/{cct}`, y el mapa de una entidad completa, una por escuela. Se subieron al listado:
`dim_escuela` ya está unida en esa consulta. Siguen en el detalle, heredadas.

`None` es `SIN_DATO` real —hay CCT sin georreferencia—, así que el front debe **omitir** esas escuelas
del mapa. Dibujarlas en el `(0, 0)` pondría escuelas mexicanas en el Golfo de Guinea.

### 3. `PrediccionOut` expone `prioridad`

`gold.recomendaciones.prioridad` existía desde la publicación de ML-02, pero nunca salió por la API.
Es lo que Marina pidió para ordenar los casos.

**Lo importante es lo que NO significa.** `prioridad` sale del **ancla de la sigmoide** (0.60,
`DEC-006`) vía `publicar_gold.prioridad_de_riesgo()`, **no** de la línea de alerta con la que `/kpis`
cuenta escuelas en riesgo (0.50, `DEC-019`). Son dos números distintos a propósito: mover `alta` a
0.50 reescribiría las 45,276 filas ya publicadas, y `DEC-019` dice que no cambia un solo valor
publicado. Queda como pregunta abierta del PO y el TL de C3 (`BUG-063`); cuando se resuelva cambia el
productor en Gold, no este contrato. Lo dejé escrito en el docstring y en la especificación para que
nadie lo lea como "riesgo ≥ 0.5".

Es `StrictStr | None` y no un `Literal`: el valor lo escribe C3, y uno inesperado debe poder **leerse
y verse**, no reventar la lectura con un 500. Sin fila de recomendación viaja `None`, mismo criterio
`SIN_DATO` que `cluster`.

## Seguridad / calidad

- [x] 3 pruebas nuevas en `tests/test_api_contract.py`, una por campo
- [x] El fixture de predicciones trae `alta` y `media`, no dos veces el mismo valor: una prueba que
      solo viera `alta` no notaría si el campo se quedara fijo
- [x] 426 pruebas focalizadas verdes; `ruff` y `vault_lint` limpios
- [x] OpenAPI reexportado; `test_api_contract.py` verde
- [x] Los tres cambios son aditivos y opcionales: no rompen a Streamlit ni a ningún consumidor

> **No se tocó `RISK-010`** (la línea de alerta duplicada en ~11 sitios). La mitigación está marcada
> como **post-freeze** por decisión del PO: "tocar 4 células el día del freeze cambia lo que la demo
> enseña". Se respeta.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** este DevLog.
- **Modificados:** `src/api/schemas.py`, `src/api/repositorio_gold.py`,
  `src/api/repositorio_modelos.py`, `src/api/v1/gold.py`, `tests/fixtures_gold.py`,
  `tests/fixtures_modelos.py`, `tests/test_api_contract.py`, `api/openapi.v1.json`,
  `vault/03_Architecture/API_Specification.md`, `vault/_DevLog/_index.md`.

## Avisos a otros owners

- **Diana Alvarez (E5):** `/escuelas` ya trae `latitud`/`longitud` (omite las `None` en el mapa) y
  `/municipios` trae `nombre_entidad` y `cve_ent`, ordenables.
- **Marina García (E3):** `prioridad` ya viaja en `/predicciones/{cct}` y en `/predicciones/batch`.
  Ojo con el corte: es el ancla 0.60, no la línea de alerta 0.50.
- **Karla Monter (C4) y Andrés González (C3):** el contrato cambió en `MunicipioOut`, `EscuelaOut` y
  `PrediccionOut` — aditivo, nada que adaptar.
