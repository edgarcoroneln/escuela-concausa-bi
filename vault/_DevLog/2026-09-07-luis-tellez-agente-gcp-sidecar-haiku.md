---
project: "FARO"
date: "2026-09-07"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — encender el agente conversacional (RAG Text-to-SQL) en producción: imagen de la API con las deps del agente + modelo de embeddings horneado + sidecar ChromaDB (índice horneado), revisión multi-contenedor en Cloud Run con secretos, y fix de latencia (el cliente cortaba a 15 s y el pipeline con Sonnet tardaba 4–26 s) sin tocar código de nadie; verificado e2e por Luis en el shell en vivo"
touches: ["US-304", "US-304a", "US-304b", "REQ-006", "REQ-005", "SEC-006", "US-505", "BUG-025"]
tags: [devlog, celula-5, agente, rag, cloud-run, sidecar, chromadb, despliegue, secret-manager, latencia]
---

# DevLog — 2026-09-07 — El agente conversacional, vivo en producción: sidecar ChromaDB + fix de latencia con Haiku

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Deploy a Cloud Run §4.6]] · [[vault/_DevLog/2026-08-29-luis-tellez-bug025-redeploy-agente-prod|BUG-025: redeploy del agente (stub)]] · [[vault/_DevLog/2026-09-07-luis-tellez-camino-a-503-shap-logout|Camino A: 503 del Panel ML]]

## Contexto

El **agente conversacional** (RAG Text-to-SQL, **0.5 pts** de rúbrica) era el **último frente de C5** que
quedaba abierto para la demo del 9 de septiembre. Hasta hoy prod servía solo el **stub degradado** de
BUG-025: `/agente/consulta` respondía sin fallar (`sql_generado:null`) porque la imagen de la API **no traía
las dependencias del agente** (`chromadb`, `sentence-transformers`, `anthropic`), no había **ChromaDB** en
GCP, y faltaban los secretos `ANTHROPIC_API_KEY` y `DATABASE_URL_READ_ONLY`. El código del agente ya existía
—`src/agente/**` (C3) y el cableado condicional de `src/api/app.py` (C4)— pero **nunca se había encendido en
producción**. El pendiente estaba escrito en `Cloud_Run_Deploy.md` §4.4: *"el RAG real sigue pendiente de C3
(LLM) + añadir `chromadb`/`sentence-transformers` a la imagen"*.

La consigna de esta sesión fue **LOCAL-FIRST**: validar el agente completo en local con LLM y BD reales
**antes** de tocar GCP, y luego desplegar a Cloud Run sin tocar código ajeno.

## Qué se hizo

### 1. Imagen de la API con las deps del agente + modelo horneado (código C5: `docker/api.Dockerfile`)

Dos commits sobre `docker/api.Dockerfile` (alcance **verde** de C5):

- **`72aecab`** — capa `pip install` extra: **torch CPU-only** (índice de PyTorch
  `--index-url https://download.pytorch.org/whl/cpu`, para evitar la variante CUDA ~2 GB en `linux/amd64`;
  Cloud Run no tiene GPU) + `chromadb==1.5.9` + `sentence-transformers==5.7.0` + `"anthropic>=0.116"`. La
  fuente de verdad de los pines es `requirements/celula-3.txt` (C3); se instala **solo el subconjunto** que la
  API necesita en runtime, no todo el requirements de C3 (que arrastra mlflow, streamlit, etc.).
- **`9a654d4`** — **hornea el modelo de embeddings** `all-MiniLM-L6-v2` (~90 MB) en la imagen
  (`SentenceTransformer('all-MiniLM-L6-v2')` en build) y fija el runtime **OFFLINE** (`HF_HUB_OFFLINE=1`,
  `TRANSFORMERS_OFFLINE=1`), para que la 1.ª consulta RAG **no dependa de HuggingFace** en runtime (Cloud Run
  con egress `private-ranges-only` no alcanza Internet). Va antes de `COPY src/` para quedar cacheado.

Verificado dentro de la imagen: **torch 2.14.0+cpu** (CUDA=False), `chromadb`/`sentence-transformers`/`anthropic`
OK, y los módulos reales del agente (`llm`, `recuperacion`, `servicio`, `ejecutor_gold`) importan. La imagen de
prod quedó **sellada** con `GIT_COMMIT=9a654d4678e9848b63079221a7c710faf67a4df8`.

### 2. Sidecar de ChromaDB (por qué, y cómo)

`src/agente/recuperacion.py` (código de **C3, no se toca**) crea `chromadb.HttpClient(host, port)` **sin el
parámetro `ssl`**, así que no puede hablarle a una URL `https://*.run.app`. La única vía sin tocar código
ajeno es un **sidecar**: ChromaDB como **segundo contenedor dentro del mismo servicio `faro-api`**,
comunicándose por **`localhost`** sin TLS (el frontend sigue llamando a la misma URL; cero cambios en C2).

- Imagen del sidecar sobre `chromadb/chroma@sha256:abcce7c335e2…` (digest **amd64** de la imagen oficial,
  inmutable) con el **índice horneado**: `COPY faro_chroma_index/ /data/` + `IS_PERSISTENT=1`. La colección
  `faro_gold_schema` (**7 docs** del esquema Gold) arranca poblada; **cero indexado en runtime** (indexar
  exigiría tocar `app.py` de C4).
- En la revisión: contenedor `api` (puerto 8080) + contenedor `chromadb` (sin puerto), con
  `CHROMA_HOST=localhost` / `CHROMA_PORT=8000` y `container-dependencies={"api":["chromadb"]}`.

### 3. Validación LOCAL-FIRST (E2E, LLM + BD reales)

Se levantaron **los dos artefactos que van a GCP** juntos en local (red Docker, secretos por variable de
entorno **nunca impresa**) y se corrieron 3 pruebas contra ellos:

1. Conteo de escuelas en riesgo → SQL válido sobre `gold.predicciones`, responde.
2. Recomendaciones por conectividad → **26 escuelas D4** con recomendación y prioridades → **diferenciador
   prescriptivo VIVO**.
3. "Borra la tabla" → `fuera_de_alcance=true`, `sql_generado=null` → **el guardrail bloquea antes de generar
   SQL**.

Medición de memoria del combo: API **617 MiB** + sidecar **64 MiB** ⇒ **512Mi no alcanza**; Cloud Run se
configuró a **2Gi**.

### 4. Deploy a producción (revisión multi-contenedor)

Con OK de Luis paso a paso (regla 7):

- **Secretos en Secret Manager:** `anthropic-api-key` (desde archivo local, **valor nunca visto** por el
  agente) y `database-url-read-only`. **Decisión de Luis:** el DSN de lectura **reusa el usuario `faro_app`**
  (mismo secreto `db-password`), no un rol SELECT-only dedicado — es seguro para la demo porque
  `src/api/ejecutor_gold.py::ejecutar_sql_read_only` fuerza `SET TRANSACTION READ ONLY` **y** valida el SQL, así
  que no puede escribir aunque el rol pudiera. El DSN se compuso en una variable de shell y **nunca se imprimió**.
  El rol SELECT-only queda como **endurecimiento posterior**.
- **Revisión multi-contenedor** vía `gcloud run services replace` con un **YAML curado** (`namespace` = número
  de proyecto; contenedor `api` con puerto y `chromadb` sin puerto) que **preserva todo el env**. Hubo que
  habilitar `cloudresourcemanager.googleapis.com` (estaba deshabilitada; API benigna de metadatos, reversible)
  porque `replace` la exige; el `update` con flags no servía (el servicio tenía **1 contenedor sin nombre** y
  gcloud creaba un 2.º con puerto → error *"should contain exactly one container with an exposed port"*).
- Revisión inicial **`faro-api-00015-f29`** (modelo por defecto Sonnet), tráfico al 100 %. Verificado: 2
  contenedores, env preservado (OAuth, JWT, `POSTGRES_*`, `AUTH_LECTURA_PUBLICA`, `ANALISTA_EMAILS`) + los 5
  secretos (`ANTHROPIC_API_KEY`, `DATABASE_URL_READ_ONLY`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET_KEY`,
  `POSTGRES_PASSWORD`←`db-password`), **VPC connector `faro-connector` + egress `private-ranges-only`
  preservados**. Smokes en vivo: `/health` 200 · `/version` = `9a654d4…` · **SEC-006 intacto**
  (`/agente/consulta` sin token → **401**, no 500).

### 5. Fix de latencia — `AGENTE_MODELO=claude-haiku-4-5-20251001` (config de deploy, sin tocar código)

La 1.ª prueba de Luis en el shell (rev `00015-f29`, Sonnet) dio **"No se pudo consultar el agente: La API del
agente no está disponible"**.

**Diagnóstico (código + logs, lectura autorizada):** ese texto sale de `src/frontend/agente_client.py:58`
(C2) y **solo** con `httpx.HTTPError` sin respuesta = **timeout** — el cliente tiene `timeout=15.0` (línea 43).
En los logs de Cloud Run, **todas** las consultas del agente terminan en **HTTP 200** pero con latencia
**4–26 s** (el pipeline hace **dos** llamadas al LLM en serie —generar SQL y redactar respuesta— más
embeddings y query); las que pasan de 15 s hacen que el shell corte y muestre el error rojo. **No es arranque
en frío** (el contenedor estaba caliente entre requests) ⇒ `min-instances` no ayuda; ninguna palanca de infra
baja la latencia de red del LLM.

**Hallazgo clave:** `src/agente/llm.py` **lee el modelo de una variable de entorno** (`AGENTE_MODELO`, por
defecto `claude-sonnet-5`; también `AGENTE_MAX_TOKENS` y `AGENTE_TIMEOUT_S`). Se puede cambiar el modelo del
agente **por env var de la revisión, sin tocar el código de nadie** (alcance C5, reversible al instante).

**Decisión de Luis:** usar **Haiku** por env var (la alternativa —subir el timeout del cliente a 60 s— toca
`agente_client.py`, que es **de C2** → el gate de propiedad reprobaría el PR, y obligaría a rebuild+redeploy del
frontend). **No** se tocó `AGENTE_MAX_TOKENS` (bajarlo trunca respuestas y `llm.py` lo convierte en error).

```bash
gcloud run services update faro-api --project=faro-escuela-sensor --region=us-central1 \
  --container=api --update-env-vars AGENTE_MODELO=claude-haiku-4-5-20251001
```

→ revisión **`faro-api-00016-hj5`** (misma imagen `9a654d4`, solo cambió la env var), tráfico al 100 %.

## Cómo se probó

- **Local (E2E, artefactos de prod):** las 3 pruebas de arriba, verdes contra la imagen `9a654d4` + el sidecar
  reales.
- **Smoke en PROD (rev `00016-hj5`):** `/health` 200 · `/version` = `9a654d4…` · agente sin token → **401**
  (SEC-006 intacto).
- **En vivo, por Luis (gate final e2e en el shell → login → "Agente FARO"):** el agente **responde sin el
  error rojo** (latencia dentro de los 15 s con Haiku); el **diferenciador se ve bien** (D2 inseguridad ≠ D4
  conectividad → escuelas y recomendaciones distintas, SQL correcto ⇒ la **calidad se sostiene** con Haiku); y
  el **guardrail bloquea** la prueba destructiva sin generar SQL. *"ya responde, sin el error rojo"* · *"se ve
  bien el diferenciador y el guardrail bloquea"*.

⇒ **El agente conversacional está COMPLETO Y VIVO en producción — cierra el último frente de C5 (0.5 pts).**

## Diagnósticos / aprendizajes

- **El sidecar era la única vía limpia.** `recuperacion.py` (C3) usa `HttpClient` sin `ssl`, así que ChromaDB
  tenía que estar en `localhost` dentro del mismo servicio. Hornear el índice y el modelo de embeddings evita
  indexar/descargar en runtime (que habría exigido tocar código ajeno).
- **La latencia del agente es de red del LLM, no de infra.** La palanca correcta fue el **modelo**, expuesto
  por env var en `llm.py`. Haiku entra holgado bajo el `timeout=15.0` del cliente y sostiene la calidad del
  diferenciador; Sonnet lo rebasaba.
- **El contrato dato↔config manda:** el modelo se cambia sin rebuild porque el código ya lo parametriza. Un
  cambio de una línea de env var resolvió lo que un rebuild no habría tocado.

## Seguridad / calidad

- [x] **Cero secretos** en repo/chat/DevLog: `ANTHROPIC_API_KEY` vía Secret Manager (**nunca vista** por el
  agente); el DSN de lectura se compuso en variable y **nunca se imprimió**; la contraseña de la DB por
  `secretKeyRef` (`db-password`). Los **correos de login siguen efímeros** solo en la revisión de Cloud Run,
  nunca en archivo.
- [x] **SEC-006 intacto:** `AUTH_LECTURA_PUBLICA=false`; `/agente/consulta` va tras `require_lectura`
  (`src/api/v1/__init__.py:26`) ⇒ sin token responde **401** (correcto, no bug). OAuth/whitelist/redirect URIs
  sin cambios.
- [x] **No se tocó código ajeno:** este PR sube solo `docker/api.Dockerfile` (verde C5) + este DevLog + su fila
  de índice + §4.6 del runbook `Cloud_Run_Deploy.md` (verde C5 / comunes). `src/agente/**` (C3),
  `src/api/**` (C4) y `src/frontend/**` (C2) **no se tocan**. El gate de propiedad pasa.
- [x] **Cambio de config reversible:** `AGENTE_MODELO` es env var de la revisión (no diff de código).
  **Rollback a Sonnet:** `gcloud run services update-traffic faro-api --region=us-central1
  --to-revisions=faro-api-00015-f29=100`. **Rollback pre-agente:** revisión `faro-api-00014-24b` (imagen
  `c4410d1`).
- [x] **Cambio de infra (regla 7):** revisión multi-contenedor + secretos + habilitación de
  `cloudresourcemanager.googleapis.com`, sometido a revisión del PO por este DevLog + PR. Sin residual: la
  imagen de la API no cambia (`9a654d4`); solo se añadió un sidecar y 2 secretos.

## Avisos a otros owners

- **C3 (Andrés González) — informativo:** el agente ya corre en prod con tu código sin modificarlo. El sidecar
  hornea el índice de **7 docs** (`faro_gold_schema`); si el esquema Gold cambia, hay que **re-hornear el índice**
  del sidecar (no es automático). `recuperacion.py` sigue con `HttpClient` sin `ssl` (por eso el sidecar); si
  algún día se quiere un ChromaDB gestionado con TLS, habría que añadir el parámetro `ssl` en tu cliente.
- **C4 (Christian Ruiz) — informativo:** `src/api/app.py` cablea el LLM y el ejecutor **condicional a los
  secretos**; con los secretos ya presentes, el agente quedó activo **sin tocar tu código**. BUG-025 (stub)
  queda **superado**: `/agente/consulta` ya no degrada, responde con SQL real.
- **C2 (Manuel / Marina) — informativo:** `3_Chat.py` ya estaba cableado y funciona. El `timeout=15.0` de
  `agente_client.py:43` se **mantiene**; con Haiku las respuestas entran holgadas. Si en el futuro se quisiera
  volver a Sonnet, habría que **subir ese timeout** (es código de C2) — hoy no hace falta.
- **PO (Edgar):** merge de este PR — `docker/api.Dockerfile` (C5) + este DevLog + índice + §4.6 del runbook. El
  `AGENTE_MODELO=claude-haiku…` es **config de deploy**, ya aplicado en la rev `00016-hj5`; queda documentado en
  el runbook para que un futuro deploy no lo pierda.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog; §4.6 nueva en `vault/08_CICD_DevOps/Cloud_Run_Deploy.md`.
- **Modificados:** `docker/api.Dockerfile` (commits `72aecab` deps + `9a654d4` modelo horneado/OFFLINE);
  `vault/_DevLog/_index.md` (fila de este DevLog); footer del runbook (v1.2 → v1.3).
- **Infra GCP (sin cambio de la imagen sellada `9a654d4`):** revisión multi-contenedor `faro-api-00015-f29`
  (Sonnet) → `faro-api-00016-hj5` (Haiku por env var); sidecar ChromaDB con índice horneado; secretos
  `anthropic-api-key` y `database-url-read-only`; habilitación de `cloudresourcemanager.googleapis.com`.
- **Decisiones autónomas del agente:** diagnóstico del timeout por descarte (texto de `agente_client.py` + logs
  de latencia), y proponer la palanca `AGENTE_MODELO` por env var (leída en `llm.py`) como fix sin tocar código
  ajeno.
- **Correcciones / decisiones del humano:** Luis eligió Haiku por env var (vs. subir el timeout de C2), reusar
  el DSN de `faro_app`, y verificó el e2e en vivo. Ningún comando `gcloud` se ejecutó sin su OK.
- **Prompt inicial:** reactivar el Chat/agente con destino GCP full, LOCAL-FIRST.
