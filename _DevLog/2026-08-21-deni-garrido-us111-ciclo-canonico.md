---
project: "FARO"
date: "2026-08-21"
title: "US-111 · Alineación canónica de ciclo en Silver"
author_human: "Deni Garrido Fragoso"
agent: "ChatGPT"
model: "GPT-5.6 Sol"
session_duration: "ajuste puntual US-111"
touches: ["US-111", "REQ-001", "DOC-DATAMODEL", "DS-01"]
tags: [devlog, ai-assisted, celula-1, dbt, silver, schema]
---

# DevLog — 2026-08-21 — Alineación canónica de ciclo en Silver

> [[_DevLog/_index|Volver al índice]]

## Contexto

Después del merge de `US-111` se reportó un desajuste entre el contrato Pydantic de `SilverMatricula` en `Data_Model.md` §5.1 y la implementación real de `silver.matricula`.

La implementación Silver ya expone la columna `ciclo`; el contrato documental todavía declaraba `id_ciclo`.

## Decisión

- El nombre canónico en **Silver** se mantiene como `ciclo`, consistente con `dbt/models/silver/matricula.sql`, `dbt/models/silver/schema.yml` y los tests de Silver.
- `id_ciclo` se conserva en **Gold** como llave de ciclo en `dim_tiempo`, `fact_escuela_ciclo`, `features_escuela` y contratos downstream.
- La frontera Silver → Gold realiza explícitamente la transformación/alias de `ciclo` a `id_ciclo`; por lo tanto no se requiere cambiar el modelo dbt de Silver.

## Cambio realizado

En `03_Architecture/Data_Model.md` §5.1, dentro de `SilverMatricula`:

- `id_ciclo: StrictStr` → `ciclo: StrictStr`.

No se modificaron los contratos Gold.

## Validación

- Verificado que `silver.matricula` usa `ciclo` para selección y deduplicación.
- Verificado que `dbt/models/silver/schema.yml` documenta `ciclo`.
- Verificado que no existen referencias a `id_ciclo` dentro de los modelos Silver.
- `python _Meta/scripts/vault_lint.py .` → `Vault limpio`.
- `python -m pytest tests/ -q` → ejecución en verde durante el cierre del ajuste.
- `git diff --cached --check` → sin errores antes del commit.
- No se reejecutó `dbt compile/test` porque el ajuste es únicamente documental y no modifica SQL, YAML de dbt ni lógica ejecutable.

## Revisión requerida

`Data_Model.md` es `source_of_truth` y su owner es Diana Aracely Alvarez Varela. De acuerdo con la regla 7 de `_Meta/Vault_Rules.md`, este ajuste de schema requiere revisión humana explícita del owner antes de integrarse.
