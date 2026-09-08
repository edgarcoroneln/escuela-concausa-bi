---
project: "FARO"
date: "2026-09-08"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — health check integral de producción la víspera de la demo (9-sep): sondeo en vivo de las tres capas, confirmación de la imagen desplegada y evaluación del delta de `main` sobre esa imagen para decidir si redesplegar antes del freeze. Sin mutaciones: verificación + decisión de congelar."
touches: ["US-505", "US-526", "SEC-006", "US-305", "DEC-019", "BUG-061", "RISK-010", "REQ-004", "REQ-005"]
tags: [devlog, celula-5, cloud-run, despliegue, smoke, readiness, freeze, sin-cambio]
---

# DevLog — 2026-09-08 — Health check de producción la víspera de la demo (decisión: congelar en `9a654d4`)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/_DevLog/2026-09-07-luis-tellez-camino-a-503-shap-logout|Camino A e2e (503 + logout)]] · [[vault/_DevLog/2026-09-07-luis-tellez-agente-gcp-sidecar-haiku|Agente en GCP (sidecar + Haiku)]] · [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Deploy a Cloud Run]]

## Contexto

La demo en vivo es **mañana, 9 de septiembre de 2026**, y el **CODE FREEZE fue el 6 de septiembre**. Norma de
Luis: la víspera se **verifica en vivo** que las tres capas públicas están sanas y se decide, con evidencia, si
algo de lo que entró a `main` después de la imagen desplegada justifica un redeploy de última hora. Esta sesión
**no cambia nada en producción**: es sondeo (read-only) + evaluación del delta + decisión.

Estado de partida (confirmado, read-only):

- **API** — servicio `faro-api`, revisión viva **`faro-api-00016-hj5`**, dos contenedores:
  `api` → `faro-api:agente-9a654d4` y sidecar `chromadb` → `faro-chroma-sidecar:agente-9a654d4`
  (el agente en GCP del 2026-09-07: ChromaDB como 2.º contenedor por `localhost`, modelo `claude-haiku-4-5`).
- **Git** — `HEAD` = `origin/main` = **`7e514b8`**. La imagen viva (`9a654d4`) es **ancestro** de `main`.

## Qué se verificó (sondeo en vivo, 2026-09-08 ~16:52 UTC)

| Capa | Sonda | Resultado | Lectura |
|---|---|---|---|
| API | `GET /api/v1/health` | **200** `{"status":"ok"}` | viva |
| API | `GET /api/v1/version` | **200** `commit=9a654d4678…` | imagen desplegada = `9a654d4` |
| API | `GET /api/v1/docs` | **200** | doc pública viva |
| API | `GET /api/v1/openapi.json` | **200** | contrato público vivo |
| API | `GET /api/v1/kpis` **sin token** | **401** | SEC-006 vigente (lectura exige sesión) |
| API | `POST /api/v1/agente/consulta` **sin token** | **401** | SEC-006 vigente en el agente |
| Frontend | `GET /` y `GET /_stcore/health` | **200 / 200** | shell FARO Web vivo |
| Superset | `GET /health` y `GET /login/` | **200 / 200** | BI vivo, login por delante |

**7/7 verde.** La matriz de acceso de SEC-006/DEC-018 se sostiene: público (`health`/`version`/`docs`/`openapi`),
lectura con sesión (401 sin token) y admin siempre `analista`.

## Delta de `main` sobre la imagen viva, evaluado para decidir el redeploy

`git diff 9a654d4..7e514b8 -- src/` trae **tres** cambios; solo uno afecta el runtime del contenedor, y como
riesgo:

| Cambio | Célula | Archivos | ¿Corre en el contenedor `api`? | Impacto de desplegarlo hoy |
|---|---|---|---|---|
| **US-305** — contexto conversacional seguro del agente | C3 | `src/agente/prompt.py`, `src/agente/servicio.py` | Sí (`/agente/consulta`) | **Riesgo de regresión, sin upside** (abajo) |
| **DEC-019 / US-311+US-313** — separar ancla de sigmoide (0.60) de línea de alerta (0.50) | C3 | `src/modelos/riesgo.py`, `src/modelos/publicar_gold.py` | Uno es batch offline; el otro usa valor idéntico | **Cero.** Rename de constante + documentación |
| **QA visual pre-demo** BUG-064..069 | C2 | 3 archivos de `vault/06_Quality_Testing/` | No | **Cero.** Solo documentación |

**US-305** agrega un parámetro **opcional** `contexto_conversacional` y una **guarda de pregunta referencial**
(regex `estas|esas|los anteriores|…`) que, sin contexto, responde "Necesito el contexto de la consulta
anterior". Pero `contexto_conversacional` **no está cableado en `src/api` ni en `src/frontend`** → la memoria
multi-turno **no funciona de punta a punta**; desplegar US-305 activaría **solo la guarda**, que puede **rechazar
preguntas libres legítimas** que contengan esas palabras (p. ej. "¿cuántas escuelas hay en **estas**
entidades?"). Beneficio visible en la demo: ninguno. Riesgo: regresión del agente en vivo.

**DEC-019 (`6f8684b`)** renombra `RIESGO_UMBRAL` (0.60) → `ANCLA_SIGMOIDE` (0.60) dejando `RIESGO_UMBRAL` como
**alias** para no romper imports; `publicar_gold.py::prioridad_de_riesgo()` pasa a `ANCLA_SIGMOIDE` (mismo 0.60).
**El valor no cambia, no recalibra, no re-entrena, no toca un `indice_riesgo` publicado**, y `publicar_gold.py`
es un job **offline** que no corre dentro del contenedor de la API. Impacto en runtime = **cero**. Nota:
**no cierra `RISK-010`** — el propio código dice que el `0.50` sigue escrito a mano en C4/C2 y que la fuente única
es trabajo post-freeze.

## Decisión

**Congelar producción en `9a654d4`. No redesplegar la API la víspera de la demo.** Razones:

1. **Cero beneficio visible** — la única función de runtime nueva (US-305) no está cableada de punta a punta.
2. **Riesgo de regresión en vivo** — lo único que se activaría es una guarda que puede rechazar preguntas válidas.
3. **DEC-019 es invisible en runtime** — no hay nada que ganar bajándolo hoy.
4. **Disciplina de ventana** — misma lógica con la que ya se congeló el frontend (`BUG-061`: el shell corre
   horneado desde el working tree y no es reproducible desde `main`; un rebuild regresaría embebido/0.50/logout).
   La víspera no se mueve lo que funciona.

**Post-demo (no bloquea):** completar el cableado de US-305 (API + frontend enviando el historial) para que la
guarda tenga sentido, y cerrar `RISK-010` con fuente única del `0.50`. Ambas son de C3/C4, no de C5.

## Cómo se probó

- **Sondas HTTP (C5)** contra las URLs públicas de las tres capas — resultados en la tabla de arriba,
  reproducibles con el bloque de `curl` del handoff (ver "Avisos").
- **Estado de despliegue** confirmado read-only con `gcloud run services describe faro-api` (revisión y las dos
  imágenes de contenedor) y `git diff/log` para el delta de `main`.
- **Sin mutaciones**: no se corrió ningún `gcloud … update`, ni build, ni push, ni cambio de tráfico.

## Diagnósticos / aprendizajes

- **Los endpoints públicos de la API viven bajo `/api/v1/`**, no en la raíz: `GET /health` y `GET /version`
  devuelven **404**, mientras que `GET /api/v1/health` y `GET /api/v1/version` dan **200**. Útil para no concluir
  falsamente "la API está caída" durante la demo o un smoke apurado. El montaje raíz sin prefijo no existe.
- **Un redeploy la víspera solo se justifica por un beneficio visible que supere el riesgo.** Aquí el delta de
  `main` es, en runtime, o inocuo (DEC-019) o una regresión potencial (US-305 a medio cablear): el balance dice
  congelar.

## Seguridad / calidad

- [x] **Sin mutaciones en GCP ni en `main`.** Solo sondas read-only y `describe`. La imagen `9a654d4` y la
  revisión `faro-api-00016-hj5` quedan intactas.
- [x] **Cero secretos** en repo/chat/DevLog. Las sondas de lectura se hicieron **sin token** a propósito
  (para verificar el 401 de SEC-006); no se usó ninguna credencial.
- [x] **Este PR NO toca código de aplicación** (`src/**`): sube solo este DevLog + su fila de índice (comunes).
  El gate de propiedad pasa.
- [x] **SEC-006 verificado vigente** en vivo (401 en `kpis` y `agente/consulta` sin token); no se tocó ninguna
  env-var de seguridad.

## Avisos a otros owners

- **PO (Edgar) / C2 (Manuel) — `BUG-065` es 🔴 y toca el guion de la demo:** en DB-03 el filtro "Escuela (CCT)"
  **no se puede aplicar para `15DPR0920D`** (uno de los dos CCT del par de demostración, `US-006`) porque sale
  **duplicado** en el dropdown y "Apply filters" queda deshabilitado. Ya fue escalado a Edgar. Alcance C2/PO
  (`db03_ficha_escuela.yaml`), no C5 — pero conviene confirmar que el guion no dependa de filtrar esa escuela
  desde la UI, o usar el CCT de control. Los demás (BUG-064/066/067/068/069) son legibilidad/agregación, `open`,
  con la nota expresa de **no** correr `sync_semantic_layer.py` antes del 9-sep.
- **C3 (Andrés) — US-305 no está cableado de punta a punta:** el agente en prod nunca recibe
  `contexto_conversacional` (ni la API ni el frontend lo pasan), así que en `main` solo queda activa la guarda
  referencial. Cablear el historial es tarea **post-demo**; desplegarlo hoy sería regresión sin beneficio.
- **PO / C3 — `RISK-010` sigue abierto:** DEC-019 documenta la separación ancla(0.60)/línea-de-alerta(0.50) pero
  el `0.50` sigue escrito a mano en C4 y C2. Fuente única (var de dbt + constante + prueba) es post-freeze.
- **PO (Edgar):** merge de este DevLog (solo comunes).

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog.
- **Modificados:** `vault/_DevLog/_index.md` (fila de este DevLog).
- **Infra GCP:** **ninguna** — sesión read-only (sondas HTTP + `describe`); producción congelada en `9a654d4`.
- **Sin cambios de código** de aplicación (`src/`).
