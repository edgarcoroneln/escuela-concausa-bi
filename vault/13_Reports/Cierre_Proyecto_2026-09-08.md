---
id: RPT-CIERRE-PROYECTO-2026-09-08
title: "Cierre del proyecto y cumplimiento del PRD — 8 de septiembre de 2026"
owner: "Edgar Edmundo Coronel Navarrete"
status: archived
version: "1.0"
traces_up: ["PRD", "PRD-GENERAL", "PLAN-EXEC-STATUS", "DEC-021"]
traces_down: ["US-006", "vault/01_Product/Guion_Demo_US006"]
last_reviewed: "2026-09-10"
tags: [reports, closure, prd, delivery, demo, code-freeze]
---

# Cierre del proyecto y cumplimiento del PRD — 8 de septiembre de 2026

> [!WARNING] Corte histórico superado
> La revisión del profesor del 9-sep no aceptó la entrega como satisfactoria. `DEC-022` reabrió el
> desarrollo hasta el 13-sep y movió la entrega al 14-sep. El estado vigente está en
> [[vault/13_Reports/Revision_Profesor_2026-09-09]] y
> [[vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09]]. Las cifras de este reporte no deben
> presentarse como estado actual.

> Corte ejecutivo previo a la demo. Las fuentes canónicas siguen siendo
> [[vault/01_Product/PRD]], [[vault/01_Product/PRD_General_Materia]],
> [[vault/12_Roadmap_Sprints/Execution_Status]] y
> [[vault/02_Requirements/Traceability_Matrix]]. Este reporte las resume; no las sustituye.

## Dictamen de cierre

FARO termina la fase de construcción con **91 de 92 historias cerradas administrativamente** y una
única historia abierta: **`US-006`, ejecutar la demo y formalizar la entrega el 9 de septiembre**.
El despliegue final y el smoke de producción quedaron documentados en el PR #294. Desde este corte
rige el *code freeze* definitivo de `DEC-021`.

`done` no significa que toda deuda técnica desapareció. En las historias cerradas por aceptación
del PO, [[vault/12_Roadmap_Sprints/Execution_Status]] conserva qué se entregó y qué residual fue
aceptado. Esa separación evita confundir **cierre administrativo** con **cumplimiento técnico
perfecto**.

## Superficies públicas verificadas

| Superficie | URL | Evidencia del 8-sep |
|---|---|---|
| FARO Web | `https://faro-frontend-eanzfglvyq-uc.a.run.app` | `/` 200 · `/_stcore/health` 200 · revisión `faro-frontend-00009-way` |
| API | `https://faro-api-eanzfglvyq-uc.a.run.app` | `/api/v1/health` 200 · `/api/v1/docs` 200 · revisión `faro-api-00018-gjx` |
| Superset | `https://faro-superset-eanzfglvyq-uc.a.run.app` | `/health` 200 · login Google disponible |

Las rutas de datos devuelven 401 sin sesión por `SEC-006`/`DEC-018`; no es una caída. Evidencia
completa: [[vault/_DevLog/2026-09-08-luis-tellez-despliegue-agente-us305-frontend-main]].

## Verificación del commit `d8872df`

El SHA exacto **no es ancestro de `main`** y sólo permanece en
`origin/feat/hector-morales-e2e-gold-api`. Esto describe una rama duplicada, pero **no una pérdida
funcional vigente**:

- sus dos padres, `d595834` y `d515e81`, sí están contenidos en `origin/main`;
- el trabajo histórico de matrícula entró por el PR #68 (`8409fb1`): extractor Formato 911
  histórico, Silver `matricula_historica` y Gold `matricula_municipio_nivel` existen y después
  recibieron correcciones adicionales;
- el trabajo E2E de Héctor entró por el PR #70 (`bba0ca7`) desde la rama equivalente
  `feat/hector-marban-e2e-gold-api`;
- la resolución funcional visible del merge —documentar que
  `construir_recomendaciones_ml02()` ya conecta ML-02— también está presente en la versión actual de
  `src/modelos/publicar_gold.py`.

**Dictamen:** no se debe mergear ni *cherry-pickear* `d8872df` ahora. Reintroduciría una fotografía
obsoleta sobre un árbol que ya evolucionó miles de líneas. La acción correcta después de la entrega
es cerrar/eliminar la rama remota duplicada mediante el proceso de gobierno de ramas, conservando
este registro como evidencia de que el contenido fue reconciliado.

## Cumplimiento de los siete módulos del PRD del profesor

| REQ | Peso | Dictamen | Evidencia principal | Salvedad que debe decirse con precisión |
|---|---:|---|---|---|
| `REQ-001` · Data Engineering | 2.5 | **Cumple** | 8 fuentes, DAGs de distintas cadencias, Bronze→Silver→Gold, 4 entidades, cubos y política `SIN_DATO`; [[vault/03_Architecture/Data_Lineage_US106]] | Persisten deuda de reproducibilidad/metadata en `RISK-008` y cargadores históricos con caminos alternos; la entrega supera el mínimo de 5 fuentes |
| `REQ-002` · Frontend BI | 2.5 | **Cumple con salvedades visuales** | FARO Web vivo, 10 dashboards, filtros, mapas, ficha, panel ML y chat; QA pre-demo en [[vault/06_Quality_Testing/QA_Logs/2026-09-08-monserrat-miranda-qa-pre-demo]] | Contraste heredado, precisión porcentual y algunos ajustes de sync quedan registrados; el Panel sirve ML-01/ML-02, no ML-03 |
| `REQ-003` · 3 modelos ML | 1.5 | **Parcial bajo lectura estricta** | ML-01 y ML-02 entrenados, publicados e integrados; ML-03 ejecutado con `k=3` y Silhouette 0.4645 en [[vault/15_ML_Models/ML03_Entrenamiento_US321]] | ML-03 **no está promovido a Gold/API/UI** por `RISK-011`; el desglose SHAP de producción permanece `SIN_DATO`. Es la brecha material frente al §3.2 del profesor |
| `REQ-004` · Backend y Auth | 1.5 | **Cumple** | FastAPI/OpenAPI, OAuth2 Google, JWT access/refresh, RBAC y validación 401/403/200 en vivo; [[vault/07_Security/Security_Review_US402_US403_US404]] | Riesgos residuales aceptados: rate limit por instancia, HS256 y refresh sin revocación (`SEC-003/004/005/009`) |
| `REQ-005` · GCP y Docker | 1.0 | **Cumple para la entrega** | Cloud Run + Cloud SQL + Artifact Registry + Secret Manager; tres superficies públicas sanas y rollbacks por revisión | Monitoreo y runbooks no tienen la misma profundidad en todos los servicios; ver residuales de `US-524b/c` y `US-525a/b/c` |
| `REQ-006` · Agente | 0.5 | **Cumple** | Chat integrado, RAG/Text-to-SQL, SQL auditable, rechazo de órdenes destructivas y agente vivo en `faro-api-00018-gjx` | La UI opera *single-turn*; el contrato de contexto existe en la API pero el frontend no envía memoria multi-turno |
| `REQ-007` · Equipo, Git y documentación | 0.5 | **Cumple con deuda de proceso declarada** | Vault enlazado, ownership, PRs, CI, DevLogs, linter y tablero generado | Hubo excepciones de revisión registradas en [[vault/_DevLog/2026-09-07-edgar-coronel-omisiones-conscientes-dec020]]; no se presentan como cumplimiento perfecto |

### Lectura ejecutiva

- **Seis de siete módulos** tienen evidencia suficiente para la banda alta de la rúbrica.
- **El módulo de ML es el único parcial bajo la letra estricta**: hay tres modelos implementados y
  ML-03 ya tiene corrida real, pero sólo ML-01 y ML-02 están integrados a la API/frontend.
- Una estimación prudente por bandas de la rúbrica es **9.0–9.5/10**, no una promesa de nota. El
  techo técnico de 9.5 aparece si el profesor asigna 1.0/1.5 a ML por tener sólo dos modelos
  integrados; las salvedades de calidad visual/operativa podrían mover la valoración dentro del rango.
- La penalización de techo 6.0 por falta de URL pública **no aplica en este corte**: las tres
  superficies respondieron 200.

## Criterios de éxito del PRD interno

| Criterio de [[vault/01_Product/PRD]] §13 | Estado al cierre |
|---|---|
| ≥5 fuentes y al menos una continua | ✅ Cumplido |
| Gold en 4 entidades | ✅ Cumplido |
| ML-01 con MAE/RMSE y validación temporal | ✅ Cumplido |
| ML-02 con F1 y explicación SHAP por escuela | ⚠️ Parcial: F1 y driver/recomendación disponibles; SHAP productivo `SIN_DATO` |
| ML-03 con Silhouette y perfiles | ✅ Cumplido como evidencia analítica; no promovido |
| Dos escuelas con mismo riesgo y distinta recomendación | ✅ Cumplido con `15DPR0920D` / `15DPR2254O` |
| Calidad y cobertura explícita | ✅ Cumplido con `SIN_DATO` e índice de completitud |
| OAuth2/JWT + RBAC | ✅ Cumplido y verificado 401/403/200 |
| URL pública viva | ✅ Cumplido |
| Agente sobre datos consolidados | ✅ Cumplido en modo single-turn |
| Trazabilidad REQ→US→prueba→DevLog | ✅ Cumplido con residuales declarados |

Resultado: **10 criterios cumplidos y 1 parcial**. Este conteo no sustituye la rúbrica externa: el
profesor exige además que los tres modelos estén integrados a API/frontend, por eso `REQ-003` se
mantiene parcial en el dictamen anterior.

## Deuda aceptada que no debe esconderse en la demo

1. **ML-03:** entrenado y medido, no promovido por sesgo de cobertura (`RISK-011`).
2. **SHAP:** el endpoint lee columnas reales, pero siguen sin poblarse en producción.
3. **Monitoreo:** Airflow/MLflow tienen monitor; seis DAGs de ingesta no tienen callback y
   Superset/agente carecen de alerta dedicada.
4. **Rollback:** existen comandos y revisiones recuperables, pero los runbooks dedicados y sus
   ejercicios no quedaron completos.
5. **UX:** deudas de contraste/formato y sync están registradas; no impiden que los diez tableros
   carguen.
6. **Gobernanza:** algunas historias se cerraron por aceptación administrativa y no por un PR propio;
   la evidencia y la ausencia están ambas escritas.

## Único trabajo pendiente — 9 de septiembre

Diana Alvarez ejecuta el guion completo de [[vault/01_Product/Guion_Demo_US006]]. Antes de entrar:

- verificar las tres URLs y los healthchecks;
- confirmar login Google y allowlist del evaluador;
- validar sesión >16 minutos, el par de escuelas y los dos chips del agente;
- mantener listo el ambiente local y el material de contingencia;
- no desplegar ni sincronizar componentes durante el *code freeze*.

Después de la demo: mover `US-006` a `done`, registrar el resultado de la entrega en un DevLog y
crear el tag/release final sólo mediante PR aprobado.
