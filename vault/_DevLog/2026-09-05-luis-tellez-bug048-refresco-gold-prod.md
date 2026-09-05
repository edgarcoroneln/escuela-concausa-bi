---
project: "FARO"
date: "2026-09-05"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — refresco del Gold de producción (BUG-048) por import server-side a Cloud SQL y verificación en vivo"
touches: ["BUG-048", "US-505", "US-113", "US-311", "US-313", "US-302", "REQ-001", "REQ-003", "REQ-005"]
tags: [devlog, celula-5, deploy, cloud-sql, gold, bug048, import, e2e, modo-reparacion]
---

# DevLog — 2026-09-05 — Refresco del Gold de producción (BUG-048)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/06_Quality_Testing/Bug_Register|BUG-048]] ·
[[vault/_DevLog/2026-09-05-andres-gonzalez-bug048-rerun-ml|Rerun ML de C3 (dump)]] ·
[[vault/_DevLog/2026-09-03-emilio-galnares-fichas-ds06-ds08|DS-06/DS-08 (CONAPO real)]]

## Contexto

`BUG-048`: producción servía un Gold **empobrecido** —`indice_completitud_drivers` 0.197 y
`escuelas_en_riesgo` 0—, porque el snapshot cargado a Cloud SQL se generó **antes de BUG-045**. El código
desplegado siempre fue correcto; el dato estaba viejo. C1 (Diana Alvarez) cerró dos huecos de completitud
reales (SESNSP y CONAPO) y C3 (Andrés González) regeneró ML-01/ML-02 sobre el Gold reconstruido; entre
ambos entregaron el dump definitivo. **La única parte pendiente era C5: llevar ese Gold a producción.**

Antes de este despliegue hubo dos dumps intermedios que **no** se importaron —uno reducido (10 municipios)
y uno `clean` con regresión de drivers (cobertura ~0)—, ambos descartados en evaluación read-only. Este
DevLog es el del **dump bueno** (`final2`), el que sí pasó la evaluación.

## Qué se hizo

Todo **server-side** contra la instancia `faro-postgres` (solo IP privada → `gcloud sql import sql` corre
en el servidor, sin Auth Proxy), con `--user=faro_app` para que los objetos queden owned por el rol del
API. Cada `gcloud`/`gsutil` con OK explícito de Luis, paso a paso (regla 7).

1. **Evaluación read-only previa** del dump `final2` (`gold_bug048_final2_2026-09-05.sql`, 66 MB,
   SHA-256 `b8a3fc50…a5b32a`, confirmado con Andrés) en un contenedor Postgres **desechable** —destruido
   al terminar—: volumen correcto, completitud 0.619, cobertura de drivers recuperada, ML no degenerado,
   diferenciador vivo. Sin regresión frente a prod, superior en completitud. **No se importa un dump que
   no se haya verificado read-only antes.**
2. **Backup de Cloud SQL** `1788644444768` (`pre-BUG-048-final2 2026-09-05`) — punto de rollback.
3. **Subida** de `reset_final2.sql` + el dump al bucket privado `gs://faro-escuela-sensor-sql-import/dumps/`
   (el SA de la instancia ya tenía `storage.objectViewer` desde L1).
4. **Reset** (`reset_final2.sql`): `DROP SCHEMA gold CASCADE` — **exit 0**, `faro_app` resultó ser owner del
   schema (no hizo falta el fallback por objeto). El dump asume DB vacía (trae `CREATE SCHEMA gold` sin
   `IF NOT EXISTS` y 0 FK), así que limpiar primero era obligatorio.
5. **Import** del dump `final2` — **exit 0**. Recreó schema + 11 tablas + 8 `MATERIALIZED VIEW` + el
   `REFRESH MATERIALIZED VIEW` que las repuebla desde `gold` (los 8 cubos son matviews; por eso no salían
   en `pg_tables` en el diagnóstico inicial).

**No hubo redeploy de la API**: es solo dato. La imagen viva (`/version = 33fcbbb`) ya era correcta.

## Cómo lo probé (verificación en vivo vía API)

`BASE=https://faro-api-eanzfglvyq-uc.a.run.app` — sin conexión directa a la BD.

```
/api/v1/kpis  → indice_completitud_drivers 0.6194   (era 0.197 → 3×)
              → matricula_total 6,704,229            (ciclo vigente 2024-2025)
              → escuelas_en_riesgo 0                 (H1 — esperado, ver abajo)
/api/v1/municipios  → 317 municipios
```

**Diferenciador (corazón del proyecto) — dos escuelas de riesgo parecido, recomendación distinta:**

| CCT | Driver dominante | Recomendación |
|---|---|---|
| 09DBN0007I | D4 · conectividad (0.453) | distinta, orientada a brecha digital |
| 09DAL0009J | D2 · seguridad (0.470) | distinta, orientada a entorno inseguro |

Cobertura de drivers del ciclo vigente en el dump importado: D1 100 % · D2 100 % · D3 85.1 % · D4 85.2 % ·
D5 0.0 % (`SIN_DATO`, CONAGUA es regional) · D6 1.3 %. Predicciones ML-01: 45,276 filas (riesgo min 0.029 /
avg 0.351 / **max 0.572**). Recomendaciones: 45,276, por driver dominante D2 27,075 · D4 12,835 · D1 2,843 ·
D3 2,104 · D6 419.

**H1 (no es defecto):** `escuelas_en_riesgo` sigue **0** porque el API cuenta con umbral
`indice_riesgo >= 0.6` y el máximo del dump es 0.572. Es una decisión de umbral/modelo de C2/C3, no del
dato ni de C5. Lo que sí cambia visiblemente es la completitud (0.197 → 0.619).

## Seguridad / calidad

- [x] Instancia solo-IP-privada → import **server-side**, sin exponer la BD ni abrir el Auth Proxy
- [x] **Backup antes de tocar** (`1788644444768`) → rollback disponible
- [x] Dump **evaluado read-only** en contenedor desechable **antes** de importar (SHA confirmado con Andrés)
- [x] `--user=faro_app` → objetos owned por el rol del API, sin GRANTs extra
- [x] Sin credenciales / correos / `.env` en repo, plan ni DevLog; no se tocó ninguna variable de entorno
- [x] Sin cambios de código; único cambio de infra = dato en Cloud SQL, reversible por el backup

## Avisos a otros owners

- **Diana (C1) / Andrés (C3):** `BUG-048` queda **cerrado end-to-end** — producción ya sirve el Gold
  post-BUG-045 con sus fixes de SESNSP/CONAPO y el rerun de ML vivos. Gracias por el dump `final2`.
- **C2 (Manuel Serranía / Oscar Quiroz):** los **8 cubos** quedaron **poblados en prod** (matviews
  refrescadas por el import). Eso **desbloquea la carga de los 10 tableros de Superset** en GCP (Bloque 2
  de la Fase 2). Es tarea aparte de este cierre.
- **Edgar (PO):** `BUG-048 → fixed`. Pendiente registrar las URLs públicas (API + Superset) en
  `vault/00_Start_Here/PROJECT_INDEX.md` (tu alcance exclusivo) — el bloque ya está preparado.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog.
- **Modificados:** `vault/06_Quality_Testing/Bug_Register.md` (BUG-048 → `fixed` + nota de cierre C5),
  `vault/_DevLog/_index.md` (fila de este DevLog).
- **Sin cambios de código.** El único cambio de infraestructura fue el refresco del Gold en Cloud SQL
  (reversible por el backup `1788644444768`).
