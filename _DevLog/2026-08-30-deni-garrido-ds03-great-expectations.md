---
project: "FARO"
date: "2026-08-30"
author_human: "Deni Garrido Fragoso"
agent: "OpenCode"
model: "GPT-5.6 Sol"
session_duration: "auditoría e implementación acotada de Great Expectations para DS-03"
touches: ["DS-03", "REQ-001"]
tags: [devlog, data-quality, great-expectations, cemabe]
---

# DevLog — 2026-08-30 — Great Expectations para DS-03 CEMABE

→ [[_DevLog/_index|Volver al índice]]

## Contrato auditado

- Tabla objetivo: `silver.cemabe`.
- Grano: una fila por `cct`, deduplicada por la ingesta más reciente.
- Drivers: `agua`, `drenaje`, `electricidad`, `sanitarios`, `internet` y `computadoras`.
- Catálogo conformado: `0`, `1` y `SIN_DATO`.

## Expectations implementadas

- `cct`: no nulo, único y longitud de 10 caracteres.
- Cada driver: no nulo y dentro del catálogo conformado.
- Total: 15 expectations declarativas sobre Silver; no se modificó SQL ni configuración global GE.

## Pruebas y resultados

- `pytest tests/test_validacion_cemabe.py -q`: bloqueado; el host no tiene intérprete Python.
- Runtime GE contra `silver.cemabe`: bloqueado por la misma ausencia de Python.
- Consulta read-only equivalente sobre PostgreSQL local: 72 filas, sin CCT nulos, duplicados o de
  longitud inválida y sin drivers nulos/fuera de catálogo.
- `ruff check`: bloqueado; no hay Python ni Ruff ejecutable en el host.
- `vault_lint.py`: bloqueado; no hay intérprete Python en el host.
- `git diff --check`: PASS.

## Bloqueantes

- Instalar o habilitar el entorno Python del repositorio para ejecutar pytest, GE, Ruff y vault lint.
- La ficha DS-03 mantiene pendiente la descarga real; la tabla local auditada no se presenta como
  evidencia de runtime contra el censo oficial.
