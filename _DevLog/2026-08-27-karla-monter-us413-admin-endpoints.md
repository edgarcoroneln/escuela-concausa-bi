---
project: "FARO"
date: "2026-08-27"
author_human: "Karla Alejandra Monter Benitez"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión — endpoints administrativos protegidos (US-413)"
touches: ["US-413", "REQ-004"]
tags: [devlog, celula-4, api, admin, backend]
---

# DevLog — 2026-08-27 — US-413: endpoints administrativos protegidos

→ [[_DevLog/_index|Volver al índice]] · [[03_Architecture/API_Specification|API_Spec §3.6]]

## Contexto

US-413 pide `/admin/pipeline/run`, `/admin/export` y `/admin/metrics` reales, solo `analista`.
RBAC ya estaba resuelto por Christian Ruiz en US-403 (`require_role(Rol.analista)` a nivel de
`include_router`), así que el trabajo fue puramente reemplazar `mock_data` por contenido real en
los 3 endpoints, uno por commit para que quedara trazable.

## Qué se hizo

**1. `/admin/pipeline/run` — Airflow real** (`src/api/orquestador.py`, nuevo). `dag` se valida
contra los 6 `dag_id` reales de `dags/*.py` (422 si no existe) antes de tocar Airflow; la corrida
se dispara de verdad contra su API REST (`POST /api/v1/dags/{dag_id}/dagRuns`, credenciales del
`.env`). Si Airflow rechaza o no responde, `502` — nunca se inventa un `run_id`. Mismo patrón
`Protocol` + `Depends` inyectable que `RepositorioGold` (US-411).

**2. `/admin/metrics` — frescura real** (`src/api/repositorio_metricas.py`, nuevo).
`frescura_por_fuente` lee `gold.cubo_pipeline` (DB-10, US-113, Deni Garrido) de verdad; una fuente
sin ingerir simplemente no aparece como llave del dict. `suites_ge_en_verde` pasa de `bool`
obligatorio a `bool | None` — **cambio de forma del contrato** (documentado en
`API_Specification.md` §3.6/§4, avisado a C2/C3): no hay checkpoints de Great Expectations
persistidos todavía de dónde leer un resultado real, así que responde `None` explícito en vez de
inventar `True`/`False`. Aviso redactado para Luis García (dueño de las suites GE).

**3. `/admin/export` — stream real, sin GCS** (`src/api/repositorio_export.py`, nuevo). Verificado
con Luis Téllez (Tech Lead C5, 2026-08-27): no existe bucket `faro-exports` ni permisos de Cloud
Storage en la service account del API — provisionarlo es cambio de seguridad de Fase 3/4, gated,
documentado como fuera de alcance de US-413. Mientras tanto, `/admin/export` regresa el *stream*
real (CSV/JSON) de `gold.<tabla>` directo desde Postgres (viable: Gold en producción son ~25
escuelas) — `tabla`/`formato` validados contra una whitelist (`Literal`, nunca una relación
arbitraria, pedido de seguridad de Luis Téllez). El `ExportOut` que el contrato mencionaba nunca
llegó a existir como modelo; se retiró la mención para documentar lo que de verdad se implementó.

**4. Pruebas del contenido, no solo del RBAC** (RBAC ya lo prueba `test_rbac.py`, US-403): 10
pruebas nuevas en `tests/test_api_contract.py` (dag inválido → 422, Airflow caído → 502 con
verificación explícita de que no se inventa `run_id`, tabla/formato inválidos → 422, contenido
real de metrics/export) + 2 fakes nuevos con dependency override (`OrquestadorFake`,
`RepositorioMetricasFake`, `RepositorioExportFake`) para que nada dependa de Postgres/Airflow
reales. De paso corregí dos pruebas existentes que hubieran quedado rotas o falseadas por mis
cambios: `test_admin_pipeline_run_202` usaba `"bronze"` (ya no es un DAG válido) y
`test_admin_export_ciudadano_da_403` usaba una tabla fuera de la whitelist (hubiera dado 422 en
vez de probar el 403 de rol que es lo que la prueba dice verificar); también agregué
`test_admin_export_como_analista_ok`, que antes nadie probaba porque `/admin/export` era puro stub.

**Prueba del 502 verificada manualmente:** quité el manejo de `OrquestadorError` en `admin.py`
a propósito y confirmé que la prueba falla (202 con `run_id` fabricado) antes de restaurar el
código real — no es una prueba que "pasa porque sí".

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-sonnet-5.
- **Archivos creados:** `src/api/orquestador.py`, `src/api/repositorio_metricas.py`,
  `src/api/repositorio_export.py`, `tests/fixtures_admin.py`, `tests/fixtures_metricas.py`,
  `tests/fixtures_export.py`, este DevLog.
- **Modificados:** `src/api/v1/admin.py`, `src/api/config.py`, `src/api/schemas.py`, `.env.example`,
  `03_Architecture/API_Specification.md`, `api/openapi.v1.json`, `tests/test_api_contract.py`,
  `tests/test_rbac.py`, `12_Roadmap_Sprints/Sprints/4-karla-alejandra-monter-benitez.md`.
- **Decisiones de fondo, presentadas a Karla antes de codificar:** qué tan real hacer cada uno de
  los 3 endpoints (Airflow real vs. stub validado; GCS vs. Postgres puro para export; `SIN_DATO`
  vs. correr GE en vivo para métricas) se plantearon como opciones con evidencia (infra existente
  en `docker-compose.yml`, `dags/`, ausencia de checkpoints de GE) antes de implementar. La
  respuesta real de Luis Téllez sobre el bucket confirmó la opción sin GCS.
- **Decisiones autónomas del agente:** forma exacta de cada `Protocol`/`Depends` inyectable, la
  whitelist exacta de tablas exportables (limitada a las 5 ya modeladas en `db.py`, no los 9
  `gold.cubo_*` de Superset), uso de `Literal` en vez de validación manual para las whitelists,
  y la corrección de las 2 pruebas existentes que mis cambios hubieran roto/invalidado.
- **Correcciones manuales:** ninguna sobre el código; Karla pidió explícitamente revisar el test
  del 502 antes de aceptarlo, y se hizo la verificación de "romperlo a propósito" en vivo con ella.
- **Prompt inicial:** continuación directa de la sesión de cierre de US-411 en la misma conversación.

## Seguridad / calidad
- [x] Sin secretos hardcodeados (nuevas vars de Airflow en `.env.example` son placeholders)
- [x] Tests agregados: 10 nuevos en `tests/test_api_contract.py` + 1 en `tests/test_rbac.py`
  (`test_admin_export_como_analista_ok`) + 2 pruebas existentes corregidas. Suite completa
  `pytest tests/ -q` (sin `test_publicar_gold.py`, requiere Postgres real): **355 passed, 5 skipped**.
- [x] DevLog enlaza a los IDs afectados (US-413, REQ-004)
- [x] `python _Meta/scripts/vault_lint.py .` → ✅ Vault limpio

## Bloqueantes / avisos a otros owners
- **Pendiente enviar a C2/C3:** cambio de forma `MetricsOut.suites_ge_en_verde: bool → bool | None`.
- **Pendiente enviar a Luis García (C1):** faltan checkpoints de Great Expectations persistidos
  para que `suites_ge_en_verde` deje de ser SIN_DATO.
- **Luis Téllez (C5), ya resuelto:** confirmó que no hay bucket ni credenciales de GCS — el export
  completo a Cloud Storage queda como historia futura, gated a que él lo provisione (cambio de
  seguridad, requiere revisión humana explícita).
- **Autoría de commits:** esta sesión también corrigió `git config user.email` (de un correo
  corporativo no verificado en GitHub a uno personal) para que los commits de aquí en adelante se
  atribuyan bien; el PR #59 de US-411 necesita que el correo corporativo se agregue como
  verificado en GitHub para atribuirse retroactivo (gestión de Karla, fuera de este repo).

## Próximos pasos
- Enviar los 2 avisos pendientes (C2/C3, Luis García).
- Documentar el artefacto en el vault (fila de Traceability Matrix, `_index.md` si aplica).
- Abrir el PR (rama `feat/karla-benitez-us413-admin-endpoints`).
- US-414 (documentar OpenAPI + colección importable) sigue pendiente, S5.
