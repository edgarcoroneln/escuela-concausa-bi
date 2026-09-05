---
project: "FARO"
date: "2026-09-04"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "levantar el ambiente local desde cero y escribir el runbook que faltaba"
tags: [devlog, runbook, local, docker, dbt, superset, bug-012]
---

# DevLog — 2026-09-04 — Ambiente local levantado desde cero y BUG-012 cerrado

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/00_Start_Here/Runbook_Ambiente_Local]] ·
[[vault/06_Quality_Testing/Bug_Register]]

## Qué se pidió

Preparar mi ambiente local para poder jugar con la API, ver la base de datos y abrir los tableros de
Superset. De paso, cerrar BUG-012 documentando los pasos.

## Punto de partida

Máquina sin nada configurado, verificado antes de tocar: Docker Desktop instalado pero apagado,
**`.env` inexistente** (bloqueante: `db` no arranca, `POSTGRES_*` no tiene defaults en Compose),
**`~/.dbt/profiles.yml` inexistente** (bloqueante: dbt no conecta), `.venv` sano con dbt-core 1.12.0
y psycopg2.

Tres agentes de exploración mapearon en paralelo la documentación existente, la secuencia real del
pipeline y la configuración de contenedores. El hallazgo de fondo: **las piezas estaban todas, el
documento que las une no existía** — exactamente BUG-012.

## Qué se hizo

Ambiente levantado con `db` + `api` + `superset` (Airflow, MLflow y ChromaDB omitidos: no son
dependencia de ninguno de los tres). Cadena completa corrida de punta a punta, con cada cifra
verificada contra lo que reportaron Marina y Héctor el 3-sep:

| Paso | Resultado obtenido |
|---|---|
| Bronze Formato 911 (3 fixtures, misma tabla) | 73 + 25 + 144 = **242 filas** |
| Bronze drivers (8 fixtures) | 72/72/12/12/72/36/4/10 |
| `cargar_geojson_municipios.py` | **317 geometrías** |
| `dbt run --full-refresh` | `fact_escuela_ciclo` **145**, `features_escuela` **145 / 3 ciclos** |
| `publicar_gold --desde-gold` | ML-01 MAE **0.0844**, **55** predicciones · ML-02 F1 **0.6458**, **55** recomendaciones |
| `dbt run --select "gold.cubo_*"` | **8 de 9** cubos |
| `sync_semantic_layer.py --validar-datos` | **103 charts**, **9 tableros** |
| `/api/v1/kpis` | `matricula_total` **11 828** (ciclo vigente, no la suma de los 3) |

MAE 0.0844 y F1 0.6458 coinciden **exactamente** con la corrida de Héctor Morales del 3-sep, lo que
descarta un ambiente afortunado.

## El runbook

[[vault/00_Start_Here/Runbook_Ambiente_Local]], `approved` / `source_of_truth: true`. Documenta los
cuatro pasos que ningún artefacto del repo recogía —`dbt seed` antes de `dbt run`, ML antes de los
cubos, `export POSTGRES_HOST=localhost` porque el `.env` trae `db`, y `DATABASE_URL` para
`publicar_gold`— y **corrige dos cifras que la documentación previa tenía mal**: son tres fixtures de
Formato 911, no dos (el tercero llegó con BUG-026), y ocho de drivers, no siete (BUG-045 partió
CONEVAL en `irs`/`pobreza` este mismo día).

Cada paso lleva escrita su cifra esperada. Es deliberado: es la única defensa contra el modo de falla
que ya nos cobró una vez, cuando Héctor siguió el DevLog de Marina —correcto al escribirse, incompleto
después— y terminó atribuyéndole a un modelo de Célula 1 un defecto que era suyo. Si el pipeline
cambia, el número deja de cuadrar en el paso exacto donde ocurre.

## Hallazgo: `escuelas_en_riesgo` ya no es cero

Este ambiente devuelve **2 escuelas en riesgo** (máx. `indice_riesgo` 0.7423, peor variación
proyectada −7.60 %) y 12 más en la banda 0.40–0.60. Las corridas del 3-sep reportaban **0**, con
máximo 0.5615.

No es azar: ML-01 fija `random_state: 0`. Es **cobertura de datos**. El 3-sep CONEVAL no tenía
fixture compatible —Marina tuvo que crear las tablas vacías a mano— así que D1 iba en blanco. Hoy,
con el fix de BUG-045 de Diana, `d1_pobreza` tiene dato en **145 de 145**.

Esto **no** invalida la ratificación de DEC-006 de hoy: el umbral 0.60 ↔ −5 % sigue siendo el
criterio correcto y el ranking prescriptivo sigue siendo la narrativa de la demo. Lo que invalida es
la **premisa** de que el conteo siempre dará cero. Conviene reconfirmarlo contra los datos reales de
producción antes del 9-sep.

## Pendiente ajeno, anotado y no corregido

`scripts/verificar-servicios.sh` consulta `localhost:8000/health`, pero `src/api/app.py:131` monta
todo bajo `/api/v1` → reporta un **FAIL falso** de la API justo a quien lo use para verificar que su
ambiente quedó bien. También consulta ChromaDB en `/api/v1/heartbeat` cuando el compose usa
`/api/v2/heartbeat`. `scripts/**` es amarillo de C5: queda para **Luis Téllez**, documentado en el
runbook y en la matriz.

`dbt/README.md` sigue siendo el scaffold de `dbt init`. `dbt/**` es verde de C1: queda para **Diana**
convertirlo en un puntero al runbook.

## Verificado

`vault_lint.py` limpio · ambiente corriendo con los 3 servicios en `healthy` · las 8 cifras de la
tabla de arriba comprobadas una por una contra Postgres y contra la API.

## IDs tocados

`BUG-012`, `BUG-045`, `US-502`, `US-112`, `US-113`, `US-313`, `REQ-001`, `REQ-005`, `DEC-006`

## Próximos pasos

- Avisar a Luis Téllez del falso FAIL de `verificar-servicios.sh`.
- Avisar a Diana para que `dbt/README.md` apunte al runbook.
- Reconfirmar `escuelas_en_riesgo` contra producción antes de la demo.
