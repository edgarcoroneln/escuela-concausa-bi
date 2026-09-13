---
project: "FARO"
date: "2026-09-11"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — integración de /agente/consulta/stream en src/api y documentación del login del React"
touches: ["US-305", "US-405", "ADR-012", "DEC-025", "REQ-004"]
tags: [devlog, api, agente, streaming, sse, seguridad, login, adr012]
---

# DevLog — 2026-09-11 — `/agente/consulta/stream` entra por `src/api` y el login queda documentado

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/API_Specification|API_Specification §3.5]] ·
[[vault/07_Security/Threat_Model|Threat_Model §Login]]

## Contexto

**Streaming.** Andrés González (C3) construyó la Fase 3 del chat: la redacción final se transmite por
Server-Sent Events en vez de esperar el texto completo. Su parte de `src/agente/**`
(`procesar_consulta_stream` y `redactar_respuesta_stream_con_llm`) ya está en `main`. La ruta, el
cableado y el contrato viven en `src/api/**` y `api/openapi.v1.json`, así que los sacó de su PR por
ownership (`c4f8e52`) y pidió que entraran por el nuestro. Ya no queda ninguna dependencia de orden,
porque lo suyo está en `main`.

**Login.** Al aprobar el PR #304, Edgar (PO) señaló que el `Threat_Model` documentaba `exchange`,
`refresh` y `logout`, pero **no cómo llega el `code_faro`**. Pidió dejarlo escrito como pendiente
explícito.

## Qué se hizo

### `POST /agente/consulta/stream`

Partí de la implementación de Andrés (`9c39a3b`) y la revisé antes de integrarla. Se conservan su
orquestación, su framing SSE `meta → fragmento → fin` y sus cinco pruebas. Tres ajustes:

- **Invariante del stream fijado: siempre `meta`, al menos un `fragmento` y `fin`.** Si el redactor
  terminaba sin ceder nada, el stream mandaba `meta` y `fin` sin ningún fragmento, y el chat habría
  mostrado una burbuja vacía. Ahora se degrada al mensaje genérico. Lo mismo pasa con un fallo a mitad
  de transmitir: antes quedaba el mensaje de error pegado al texto parcial; ahora el cierre degradado
  es un solo punto, `_cierre_degradado()`.
- **El OpenAPI documenta la ruta.** Antes aparecía como `application/json` con esquema vacío. Ahora
  `response_class=StreamingResponse` y un `responses={200: text/event-stream}` describen los tres
  eventos.
- **Cinco pruebas nuevas, además de las de Andrés:**
  - la forma del stream se verifica en **todas** las pruebas (`_assert_forma_del_stream`);
  - con el redactor sin configurar, se degrada sin exponer el "pendiente C3" interno;
  - un redactor mudo no deja una burbuja vacía;
  - **un `\n\nevent: fin` dentro del texto del LLM no falsifica un evento**, porque viaja escapado en
    el JSON;
  - el cuerpo se valida igual que en `/consulta` (un `sql` en `contexto` da 422);
  - **el stream exige sesión cuando la lectura no es pública**: no es una puerta lateral sin RBAC.
- **Cableado** en `src/api/app.py`: con `ANTHROPIC_API_KEY`, `get_redactar_respuesta_stream` se
  sobreescribe igual que las otras dos etapas del LLM. Sin la clave, se queda con el default seguro.

### Login del React en el `Threat_Model` (v1.3)

Nueva sección *"Cómo llega el `code_faro` al canje"*:

- **Por qué el botón va directo a la API y no por el proxy.** `/auth/login` escribe
  `faro_oauth_state` en el origen que responde, y el callback de Google cae en `GOOGLE_REDIRECT_URI`,
  que es el origen de la API. Si el botón pasara por el proxy, el callback respondería 401.
- **La configuración elegida con Luis:** login y callback directos a la API, y solo el canje por el
  proxy. Así se conserva el callback ya registrado en Google y el login de Streamlit, que sigue siendo
  el respaldo.
- **Los 5 pasos, con su estado.** Los verifiqué en `main`: `getAuthLoginUrl` es absoluta con
  `VITE_API_ORIGIN`, el canje usa `?sesion=cookie` y `session.jsx` hace `replaceState`. Diana lo
  implementó en el PR #322.
- **Pendientes de prod:** `FRONTEND_REDIRECT_URIS` en el deploy, su valor exacto y las credenciales
  de Google.

## Hallazgo que no es de mi alcance

`vault/08_CICD_DevOps/scripts/deploy-cloud-run.sh:86` construye el `--set-env-vars` de producción
**sin `FRONTEND_REDIRECT_URIS`**. Lo encontró Diana Alvarez. Aunque el valor esté bien, nunca llega al
Cloud Run real, y el paso 2 del login responde 400. **No lo toqué:** es de Luis, y `DEC-025` hace que
su ausencia no bloquee el cambio, pero no lo pasa al alcance de nadie más. Queda asignarlo.

## Seguridad / calidad

- [x] 10 casos de streaming en `tests/test_agente_endpoint.py` (5 de Andrés + 5 nuevos) y 1 de
      cableado en `tests/test_agente_wiring_llm.py`
- [x] El stream no expone trazas ni SQL crudo de error; lo verifican dos pruebas de fallo
- [x] RBAC: `require_lectura` aplica a nivel de router; lo verifica una prueba con la lectura no pública
- [x] OpenAPI reexportado; `test_api_contract.py` verde
- [x] `ruff check .` y `vault_lint` limpios

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** este DevLog.
- **Modificados:** `src/api/v1/agente.py`, `src/api/app.py`, `tests/test_agente_endpoint.py`,
  `tests/test_agente_wiring_llm.py`, `api/openapi.v1.json`,
  `vault/03_Architecture/API_Specification.md` (v1.3), `vault/07_Security/Threat_Model.md` (v1.3),
  `vault/_DevLog/_index.md`.
- **Crédito:** la implementación base del streaming es de Andrés González (`9c39a3b`).

## Avisos a otros owners

- **Andrés González (C3):** la ruta ya está en este PR. Cuando se integre, sincroniza para la
  validación de punta a punta.
- **Diana Alvarez (C1):** en el cliente, el stream se lee con `fetch()` + `ReadableStream`, no con
  `EventSource`, que solo hace `GET`. Usa `credentials: "same-origin"` y renderiza cada `fragmento`
  como **texto**, nunca como HTML.
- **Edgar Coronel (PO):** falta asignar el cambio de `deploy-cloud-run.sh`.
