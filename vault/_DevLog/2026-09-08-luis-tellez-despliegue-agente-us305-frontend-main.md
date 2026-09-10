---
project: "FARO"
date: "2026-09-08"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — víspera de demo (9-sep): promoción del agente US-305 a 100 % tras revalidar el delta de `main`, reconstrucción sellada del frontend desde `main` (remediación C5 de BUG-070, habilitada por el cierre de BUG-061), y smoke integral en vivo de las tres capas. Dos mutaciones de tráfico, ambas verificadas y con rollback documentado."
touches: ["US-305", "BUG-070", "BUG-061", "US-304", "SEC-006", "US-505", "US-526", "US-207", "US-405", "DEC-015", "REQ-004", "REQ-005"]
tags: [devlog, celula-5, cloud-run, despliegue, agente, frontend, bug-070, bug-061, smoke, freeze]
---

# DevLog — 2026-09-08 — Dos despliegues a prod la víspera de la demo: agente US-305 completo + frontend reconstruido desde `main` (cierra la remediación C5 de BUG-070)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/_DevLog/2026-09-08-luis-tellez-health-check-vispera-demo|Health check + decisión de congelar]] · [[vault/_DevLog/2026-09-08-marina-garcia-embebido-superset-guardas-sesion|C2: embebido a main (BUG-061)]] · [[vault/_DevLog/2026-09-08-christian-ruiz-us305-contexto-agente|C4: contexto del agente (US-305)]] · [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Deploy a Cloud Run]]

## Contexto

Este DevLog **revierte, con fundamento, dos decisiones del health check de esta misma mañana** (`2026-09-08-luis-tellez-health-check-vispera-demo`, que **congeló** en `9a654d4` y pidió **no** redesplegar el frontend). No es un cambio de criterio arbitrario: **`main` avanzó entre una sesión y otra** y disolvió exactamente los dos motivos que sostenían el congelamiento. Ambos despliegues se ejecutaron con OK de Luis y se verificaron en vivo; el freeze del 6-sep sigue respetado en espíritu (no se escribió código, solo se llevó a prod lo que ya estaba en `main`).

Por qué la mañana decía "no" y la tarde dice "sí":

| Motivo del congelamiento (mañana, sobre `7e514b8`) | Qué cambió en `main` después | Efecto |
|---|---|---|
| **US-305** "no cableado en `src/api` → solo activaría la guarda, que rechaza preguntas con 'estas/esas' = regresión sin upside" | Entraron 3 commits US-305 **posteriores a `7e514b8`**: `a8b98c7` (C4: **cablea/valida `contexto_conversacional` en `/agente/consulta`**), `726a8ac` (**corrige los falsos positivos del guardrail**), `06f94eb` (distingue errores SQL + amplía dominio) | El riesgo (falsos positivos) queda **corregido en origen** por C3/C4 |
| **BUG-061** "el frontend no se reproduce desde `main` → no redesplegar o se pierde el embebido" | **PR #293 de Marina** commitea el embebido a `main` (superset_client + Embedded SDK + guardas de sesión BUG-071) | El frontend **ya se reproduce desde `main`**; Marina misma anota "desbloquea a C5 para reconstruir la imagen y cerrar BUG-070" |

## Qué se hizo

### A) Agente US-305 → 100 % (`faro-api-00018-gjx`, imagen `457715a`)

Antes de mover tráfico verifiqué en git que la imagen candidata es correcta y no es una regresión:

- `457715a` **contiene los 5 commits US-305** (`e6ed616`, `ae5bd53`, `a8b98c7`, `726a8ac`, `06f94eb`) — comprobado con `git merge-base --is-ancestor`.
- `457715a` es **posterior a `9a654d4`** (la imagen congelada) — es descendiente, no una rama divergente.

Promoción de tráfico a la revisión ya validada en preview. **La revisión preserva TODO** (verificado leyendo la spec de la revisión, sin imprimir valores sensibles):

| Elemento | Estado en `00018-gjx` |
|---|---|
| Contenedores | `api` + sidecar `chromadb` (2) |
| `ANALISTA_EMAILS` | **4 correos** (profesor + Karla + Edgar + Luis, intactos del alta previa) |
| `AUTH_LECTURA_PUBLICA` | `false` (SEC-006 vigente) |
| `AGENTE_MODELO` | `claude-haiku-4-5-20251001` (fix de latencia) |
| Secretos por referencia | 5 (`ANTHROPIC_API_KEY`, `DATABASE_URL_READ_ONLY`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`) |

**Alcance real del upside** (para no sobrevender): lo que gana la demo es el **guardrail sin falsos positivos** + **mejor manejo de errores SQL / dominio ampliado** + el **contrato de contexto ya cableado en la API**. La **memoria multi-turno end-to-end todavía NO está activa desde la UI**: Manuel (C2) documenta que "el cliente se conecta cuando Edgar autorice", así que el chat sigue respondiendo **single-turn** desde el front, ahora con la guarda corregida. Agente verificado respondiendo en el chat.

**Rollback:** `gcloud run services update-traffic faro-api --region=us-central1 --to-revisions=faro-api-00017-cv7=100`.

### B) Frontend reconstruido desde `main` → 100 % (`faro-frontend-00009-way`, imagen `main-1e413e1`)

Esta es **la acción de remediación de BUG-070 asignada a C5** en el Bug_Register ("C5 (Luis Téllez): reconstruir la imagen del frontend desde `main`, no parchar la anterior"). La causa raíz de BUG-070 era que la imagen viva (`embed-combo-dec019-logout`, rev `00008-fpw`) estaba **parchada a mano** y **nunca se construyó desde `main`**, por lo que el refresco de token que vive en `main` desde el 6-sep nunca llegó a prod → **la sesión moría a ~15 min en silencio** (reportado por Karla Monter).

Evidencia del defecto (diff imagen viva vs `main`), que motivó el rebuild:

- `src/frontend/auth.py`: **163 líneas en la imagen viva vs 248 en `main`**. A la imagen viva le faltaban `_refrescar()`, `token_de_acceso()`, `encabezado()` y la llamada `POST /api/v1/auth/refresh` — justo el mecanismo de refresco.

Procedimiento (sellado y sin tocar el worktree ajeno): build desde `origin/main` con `--build-arg GIT_SHA=1e413e1` (imagen etiquetada `main-1e413e1`) → `gcloud run deploy --no-traffic` (nace a 0 %, URL `preview---`) → validación en preview → promoción de tráfico a `00009-way`. Como BUG-061 ya está en `main`, el rebuild **no** regresó Dashboards/Panel ML.

**Rollback:** `gcloud run services update-traffic faro-frontend --region=us-central1 --to-revisions=faro-frontend-00008-fpw=100`.

### C) Smoke integral en vivo (read-only, tras ambas promociones)

| Capa | Sonda | Resultado |
|---|---|---|
| API | `/api/v1/version` | **200** · `commit=457715a` |
| API | `/api/v1/health`, `/api/v1/docs` | **200** |
| API — SEC-006 | `kpis`, `escuelas`, `escuelas/{cct}`, `municipios`, `predicciones/{cct}`, `.../explicacion`, `auth/me`, `admin/metrics` sin token | **401 las 9** (fail-closed) |
| API — agente | `POST /agente/consulta` sin token | **401** |
| API | `/api/v1/auth/login` | **302** (inicia OAuth) |
| Frontend | `/`, `/_stcore/health` | **200 / 200** |
| Superset | `/health` | **200** |
| Superset — SSO | `/superset/welcome/` sin sesión | **302 → /login/** con botón **Google** (fail-closed) |

**Todo verde.** Nada quedó abierto ni caído.

## 🤖 Sesión de IA
- **Agente / modelo:** Claude Code · claude-opus-4-8
- **Archivos creados/modificados (versionados):** este DevLog + fila en `vault/_DevLog/_index.md`. **Nada de código** (los fixes son de C2/C3/C4 y ya estaban en `main`; C5 solo despliega).
- **Decisiones autónomas del agente:** verificar la cadena de commits (`457715a ⊇ 5×US-305`, posterior a `9a654d4`) y la preservación del env de la revisión **antes** de mover tráfico; construir la imagen del frontend con `git archive`/staging para no tocar el worktree con material ajeno; mantener el PR estrictamente en artefactos comunes.
- **Correcciones manuales:** las promociones de tráfico y el rebuild se ejecutaron con OK explícito de Luis (regla 7). La verificación e2e visual (login, dashboards, chat) es gate manual de Luis.
- **Prompt inicial:** "arranca el cierre documental" (tras validar el smoke integral).

## Seguridad / calidad
- [x] Sin secretos hardcodeados — los correos de `ANALISTA_EMAILS` viven **solo** en la revisión de Cloud Run (efímeros), cero en repo/DevLog; los 5 secretos siguen por `secretKeyRef`.
- [x] SEC-006 vigente tras ambos despliegues (401 en las 9 rutas de lectura + agente, verificado en vivo).
- [x] Imágenes **selladas** (`GIT_COMMIT`): API `/version`=`457715a`; frontend etiquetada `main-1e413e1`.
- [x] DevLog enlaza a los IDs afectados y a los DevLogs de C2/C4 que produjeron el código.

## Bloqueantes
- **Ninguno de C5.** Deuda viva que **no** bloquea la demo:
  - ⚠️ El Embedded SDK de `src/frontend/pages/1_Dashboards.py` se carga desde **unpkg sin versión fija** (riesgo de demo escalado al PO; plan B = Superset directo). Owner del archivo: C2.
  - **Memoria multi-turno del chat**: el front aún no envía `contexto_conversacional`; se activa cuando C2 conecte el cliente con OK del PO.
  - **ML-03 · clustering = SIN_DATO por diseño** (US-321 de C3 en curso, sin promoción productiva; `gold.predicciones` no expone `cluster`, la API lo devuelve `null`; DEC-015 acepta 2/3 modelos). El Panel ML lo muestra honestamente — **no** es defecto ni regresión del rebuild.

## Próximos pasos
- **Gate e2e de BUG-070 (Luis/QA):** iniciar sesión y confirmar que **aguanta > 15 min** sin caerse (la prueba definitiva del refresco). Con eso, QA/PO puede mover la fila BUG-070 a `fixed` en el Bug_Register (la remediación C5 ya está desplegada y verificada técnicamente; **no la marco aquí** para no adelantar el cierre a la verificación de duración).
- **C2/PO:** reconciliar en el Bug_Register las filas de **BUG-061** (código ya en `main` por PR #293) y **BUG-070** tras el gate e2e.
- **Demo:** usar ML-01/ML-02 en el Panel ML; el SIN_DATO de ML-03 es defendible como honestidad de cobertura.
