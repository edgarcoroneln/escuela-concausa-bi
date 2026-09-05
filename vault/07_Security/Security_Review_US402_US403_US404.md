---
id: DOC-SECREV-C4
title: "Revisión de seguridad — cierre de US-402, US-403 y US-404"
owner: "Christian Imanol Ruiz Hurtado"
status: in_review
version: "1.1"
source_of_truth: true
traces_up: ["REQ-004", "vault/07_Security/Security_Review_Checklist", "vault/_Meta/Vault_Rules"]
traces_down: ["US-402", "US-403", "US-404", "US-405", "SEC-002", "SEC-003", "SEC-004", "SEC-005", "SEC-006", "SEC-007", "SEC-009", "BUG-046"]
last_reviewed: "2026-09-04"
tags: [security, review, oauth2, jwt, rbac, hardening, celula-4]
---

# Revisión de seguridad — cierre de US-402, US-403 y US-404

> **Regla 7 del vault:** todo cambio de seguridad requiere revisión humana explícita del dueño del
> área. Este documento **es** ese registro para la superficie de autenticación y autorización de la
> API. Lo firma Christian Imanol Ruiz Hurtado (Tech Lead C4, dueño de `vault/07_Security/**`).
> → [[vault/07_Security/_index]] · [[vault/07_Security/Security_Review_Checklist]] ·
> [[vault/03_Architecture/API_Specification]] · [[vault/07_Security/Security_Audit_Log]]

## 1. Alcance

| Historia | Qué cubre | Estado tras esta revisión |
|---|---|---|
| `US-402` | OAuth2 con Google + JWT propio (access/refresh) | ✅ cerrada — se implementó la verificación real del `id_token` y el `state` anti-CSRF |
| `US-403` | RBAC de 2 roles (`ciudadano` / `analista`) | ✅ cerrada con **una salvedad abierta**: la política `ANALISTA_EMAILS` es del PO (ver §5) |
| `US-404` | Hardening: rate limiting, CORS, validación estricta, errores sin fuga | ✅ cerrada con **dos follow-ups aceptados** (RS256 y rotación de refresh, §5) |
| `US-405` | Login/logout y vistas por rol en FARO Web | ⛔ **no** cubierta aquí: vive en `src/frontend/**`, cuyo dueño es Manuel Serranía (C2) |

Lo que **no** entra: la política de producto sobre quién es `analista`, el flip de
`AUTH_LECTURA_PUBLICA` en el entorno desplegado (C5) y el frontend.

## 2. Qué se corrigió en esta revisión

### 2.1 El `state` de OAuth era una constante (`SEC-002`)

`GET /auth/login` mandaba a Google el literal `state=faro`. Un `state` constante **no protege de
nada**: cualquiera podía reproducirlo y forjar una llamada a `/auth/callback` con un `code` propio,
que es exactamente el ataque de *login CSRF* que el parámetro existe para impedir. Era observable
desde fuera, sin credenciales, en la URL pública.

**Corregido.** El `state` ahora es un JWT propio de 10 minutos con `nonce` aleatorio, que viaja por
dos canales independientes: el parámetro de la URL de Google y la cookie de primera parte
`faro_oauth_state` (`HttpOnly`, `Secure` fuera de local, `SameSite=Lax`, un solo uso). El callback
exige que ambos existan, coincidan (`secrets.compare_digest`) y que el token sea válido y vigente;
si no, **401** uniforme, sin decir cuál de las tres condiciones falló.

Se eligió un `state` firmado y no uno en memoria del servidor porque Cloud Run corre varias
instancias sin estado compartido: un `state` en RAM se perdería entre la ida y la vuelta del
navegador. Detalle en [[vault/03_Architecture/API_Specification]] §2.1.1.

### 2.2 La identidad de Google no se verificaba de verdad

`RealGoogleVerifier.verify()` levantaba `NotImplementedError`: el login **no podía completarse** ni
siquiera con las credenciales que C5 dejó vivas en Cloud Run el 30-ago (revisión `faro-api-00007-4dd`).

**Implementado** el *authorization code flow* completo:

1. `POST` al *token endpoint* con `code`, `client_id`, `client_secret` y `redirect_uri`.
2. Verificación del `id_token`: firma **RS256** contra la llave del JWKS público de Google que
   corresponde al `kid` del encabezado, `aud == GOOGLE_CLIENT_ID`, `iss` de Google y `exp` vigente.
   La lista de algoritmos se pasa **explícita** — nunca se confía en el `alg` del token entrante
   (*algorithm confusion*).
3. Se exige `email_verified == true`: el rol se resuelve por correo, así que un correo sin verificar
   permitiría suplantar a un futuro `analista` registrando esa dirección en otro proveedor.

El módulo **no registra ni devuelve** el `code`, el `client_secret` ni el `id_token`; todo fallo del
intercambio se convierte en un `ValueError` genérico que la capa HTTP traduce a **401** uniforme.

## 3. Checklist ejecutado

| Punto de [[vault/07_Security/Security_Review_Checklist]] | Veredicto | Evidencia |
|---|---|---|
| Auth aplicada en endpoints no públicos (401 sin token) | 🟢 | `tests/test_rbac.py`, `tests/test_auth_jwt.py`; `/auth/me` → 401 en la URL pública |
| Autorización por rol (403 con token válido pero rol corto) | 🟢 | `tests/test_rbac.py` — matriz 401/403/200 sobre `/admin/*` |
| Validación/sanitización de entrada | 🟢 | `EntradaEstricta` (`extra="forbid"`) en los 4 modelos de entrada → 422; SQL del agente pasa por `preparar_sql_seguro` |
| Sin secretos hardcodeados | 🟢 | Todo por `Settings`; el `client_secret` vive en Secret Manager (C5) |
| Sin fuga de información en errores | 🟢 | `ErrorOut` uniforme; el 500 registra en log y devuelve mensaje genérico (`tests/test_hardening.py`) |
| Rate limiting en endpoints sensibles | 🟡 | Activo (`120/minute` por IP+path) pero **en memoria por proceso** → `SEC-003` |
| Logs sin datos personales | 🟢 | Se registra el tipo de excepción y el `request_id`, nunca el `code`, el token ni el correo |
| CSRF en el flujo OAuth | 🟢 | Corregido en esta revisión (§2.1), `tests/test_oauth_google.py` |
| Algoritmo de firma de los JWT propios | 🟡 | HS256 simétrico → `SEC-004` |
| Ciclo de vida del refresh token | 🟡 | Sin rotación ni revocación → `SEC-005` |
| SCA / dependencias | ⬜ | No ejecutado en esta sesión; corresponde al gate de CI (C5) |

**Veredicto global: 🟡** — sin hallazgos bloqueantes abiertos; cuatro riesgos residuales aceptados y
registrados, con dueño y condición de cierre.

## 4. Pruebas que sostienen el veredicto

| Archivo | Casos | Qué prueba |
|---|---|---|
| `tests/test_oauth_google.py` | 18 | `state` (roundtrip, no reutilizable como access, cookie `HttpOnly`, sin `state` → 401, sin cookie → 401, `state` ajeno → 401, un solo uso) y `RealGoogleVerifier` contra un Google falso con llave RSA en memoria: audiencia ajena, emisor ajeno, token expirado, `kid` desconocido, correo no verificado, rechazo de Google → 401 sin fuga |
| `tests/test_auth_jwt.py` | 16 | Núcleo JWT, política de rol y `/auth/*` (el callback ahora ejercita el flujo `login → callback` completo) |
| `tests/test_rbac.py` | 10 | Matriz 401/403/200 y ambas ramas de `AUTH_LECTURA_PUBLICA` |
| `tests/test_hardening.py` | 7 | CORS, 429 con `ErrorOut`, 422 por campo extra, 500 sin fuga |

Ejecutado: `pytest tests/test_oauth_google.py tests/test_auth_jwt.py tests/test_rbac.py
tests/test_hardening.py tests/test_api_contract.py -q` → **79 passed**. `ruff check src/api tests` →
limpio.

> Nota de honestidad: la suite completa del repositorio **no** se corrió en esta sesión — la máquina
> no tiene el ambiente 3.11 con las dependencias de las Células 1 y 3 (Great Expectations, MLflow).
> Lo verifica el CI.

## 5. Riesgos residuales aceptados (registrados en el Security Audit Log)

| ID | Hallazgo | Severidad | Dueño del cierre | Condición de cierre |
|---|---|---|---|---|
| `SEC-002` | `state` de OAuth constante (`faro`) | high | Christian Ruiz | ✅ **resuelto** en esta revisión |
| `SEC-003` | Rate limiting en memoria por proceso: con varias instancias de Cloud Run el límite real se multiplica por el número de instancias | medium | Luis Téllez (C5) + Christian | Backend compartido (Redis) o límite en el balanceador. Aceptado para la demo: hoy corre 1 instancia |
| `SEC-004` | JWT propios firmados con **HS256** (secreto simétrico): quien pueda leer `JWT_SECRET_KEY` puede **emitir** tokens, no solo verificarlos | medium | Christian + C5 (llaves) | Migrar a RS256 con par de llaves en Secret Manager. Aceptado: el secreto ya vive en Secret Manager y no sale de ahí |
| `SEC-005` | Refresh tokens sin rotación ni revocación: un refresh filtrado sirve 7 días y no hay forma de invalidarlo | medium | Christian | Rotación en cada canje + lista de revocación. Aceptado para la ventana del proyecto |
| `SEC-006` | `AUTH_LECTURA_PUBLICA=true` en el entorno desplegado: la lectura de datos no exige sesión | low (decisión de producto) | Luis Téllez (C5) | Poner `false` cuando el login e2e esté validado en vivo. Es un **interruptor de configuración**, no un cambio de código |

## 6. Pendientes que **no** son míos

- **Edgar (PO):** ratificar `ANALISTA_EMAILS` — quién es `analista`. Hoy la allowlist está vacía, así
  que **todos** son `ciudadano` (mínimo privilegio). US-403 no puede darse por cerrada de producto
  hasta que exista esa decisión, aunque el mecanismo esté completo y probado.
- **Luis Téllez (C5):** dar de alta a los evaluadores como *test users* de la pantalla de
  consentimiento (está en modo Testing) y, tras validar el login en vivo, coordinar el flip de
  `AUTH_LECTURA_PUBLICA`.
- **Manuel Serranía (C2):** `src/frontend/**` — US-405 consume este flujo desde FARO Web.
- **Edgar (PO):** `vault/03_Architecture/ADRs/**` **no tiene dueño en `ownership.yml`**, así que nadie
  puede actualizar `ADR-004` sin que el gate de propiedad repruebe el PR. Los cambios de §2 de este
  documento deberían reflejarse ahí.

## 7. Firma

| | |
|---|---|
| **Revisor** | Christian Imanol Ruiz Hurtado — Tech Lead C4, dueño de `vault/07_Security/**` |
| **Fecha** | 2026-09-02 |
| **Veredicto** | 🟡 Aprobado con riesgos residuales aceptados (§5) |
| **Asistencia de IA** | Claude Code / claude-opus-5 — código revisado línea por línea antes de commitear ([[vault/_DevLog/2026-09-02-christian-ruiz-us402-cierre-oauth-e2e]]) |

---

## 8. Anexo A (2026-09-04) — Revisión de C4 sobre `BUG-046` (`options={"verify_at_hash": False}`)

> **Este anexo es el sello de regla 7 que faltaba.** El parche de `BUG-046` toca
> `src/api/security/**` —alcance verde de C4— pero lo diagnosticó y validó Luis Téllez (C5) y lo
> mergeó Edgar Coronel (PO) como excepción, porque el gate de propiedad reprueba —correctamente— un
> PR de C5 sobre esta ruta. El procedimiento fue el adecuado: se pidió mi revisión **antes** del
> redespliegue. Lo que no existía hasta ahora era el registro. Aquí está.

### 8.1 Qué se cambió

Una línea en `_verificar_id_token` (`src/api/security/google.py`): `options={"verify_at_hash": False}`
en la llamada a `jwt.decode`, con el comentario que explica el porqué.

### 8.2 Verificación independiente (no me basé en el reporte)

| Comprobación | Resultado |
|---|---|
| Revertir el parche y correr `tests/test_oauth_google.py` | **1 failed, 23 passed** — `JWTClaimsError`, el mismo tipo de excepción de los logs de producción. El fallo es exclusivamente el caso de `at_hash` |
| Reponer el parche y correr la familia completa de auth (`test_oauth_google`, `test_puente_oauth_frontend`, `test_auth_jwt`, `test_frontend_auth`) | **66 passed** |
| Lectura del código de `jose` en vez de asumir su comportamiento | Ver §8.3 |

El bug era real, el fix lo cierra y no arrastra efectos colaterales en la superficie de auth.

### 8.3 Dos detalles del código de `jose` que sostienen el veredicto

1. **`jwt.py:458` — `_validate_at_hash` retorna de inmediato si el claim no está presente**, y
   `require_at_hash` es `False` por defecto. Es decir: no truena por *no traer* `at_hash`, truena por
   **traerlo sin el `access_token` para compararlo**. Esto explica por qué 23 pruebas pasaban en verde
   contra un flujo que en producción estaba roto al 100 %: el fixture nunca emitía el claim.
2. **`jwt.py:153` — `defaults.update(options)`**, no reemplazo. Pasar `options` **actualiza** los
   valores por defecto en vez de sustituirlos, así que **firma RS256, `aud`, `iss` y `exp` siguen
   activas**. Es un apagado quirúrgico de una comprobación, no un `verify_signature: False`
   encubierto. Este es el punto que decide el veredicto de seguridad.

### 8.4 El razonamiento de seguridad, y lo que sí queda pendiente

`at_hash` existe para **atar dos tokens que llegan por canales distintos**: es el caso del *implicit
flow*, donde el `id_token` viaja por el navegador y podría ser sustituido por otro. En el
*authorization code flow* server-to-server los dos llegan en el **mismo cuerpo de respuesta TLS** del
token endpoint de Google. No hay nada que atar. OIDC Core lo declara REQUIRED en implicit y
**OPTIONAL** en code flow, precisamente por esto.

**Pero existe un fix más fuerte, y conviene decirlo en voz alta:** `_intercambiar_code` lee
únicamente `id_token` de la respuesta de Google y **descarta el `access_token`**, que viene en ese
mismo JSON. Pasarlo a `jwt.decode` haría que `at_hash` se **verificara** de verdad en vez de
desactivarse.

**No se pide para la entrega**, y la razón es explícita: cambia el tipo de retorno de una función en
el camino crítico del login a dos días del *code freeze*, y la ganancia real de seguridad en este
flujo es **nula** por lo dicho arriba. Queda como `SEC-009`, follow-up con dueño, no como deuda
silenciosa.

### 8.5 El hallazgo de fondo, que es responsabilidad de C4

La causa raíz no es la línea que faltaba: es que **el doble de prueba era más angosto que el
proveedor real**. `google_falso` emitía los claims que se nos ocurrió emitir, no los que Google
emite. Veintitrés pruebas daban verde contra un Google que no se comportaba como Google.

El test de regresión de Luis (`test_verifier_acepta_id_token_con_at_hash`, que reprueba con el parche
revertido) cierra este hueco concreto. La lección general —un *fake* de un proveedor de identidad
debe modelarse sobre la respuesta real, no sobre la esperada— es de C4 y queda aquí escrita.

### 8.6 Veredicto del anexo A

**🟢 Aprobado por C4 sin cambios.** El fix entra tal cual. `SEC-009` queda abierto como follow-up de
severidad *low*.

## 9. Anexo B (2026-09-04) — Verificación contra la URL pública, y su límite

Tras el redespliegue de C5 se ejercitaron **11 comprobaciones de seguridad contra la URL pública**
(revisión `faro-api-00009-svt`), todas con el resultado esperado: `state` firmado y distinto en cada
`/auth/login`; cookie `faro_oauth_state` con `HttpOnly`, `Secure` y `SameSite=Lax`; allowlist de
`redirect` respondiendo **400** —incluido el ataque por sufijo `...8501.evil.tld`, que un `startswith`
habría dejado pasar—; `/auth/callback` **401** sin `state` y sin cookie; `/auth/exchange` **401** con
código inventado y **422** con cuerpo malformado; `/auth/me` **401** sin token; `/admin/*` **401**; y
`ErrorOut` uniforme sin fuga de detalle interno en todos los casos.

> **El límite de esa verificación, y hay que decirlo con claridad.** Las 11 comprobaciones son
> **casos negativos**: confirman que el perímetro *rechaza* lo que debe rechazar. **Ninguna ejercitó
> un login real completo**, porque en ese momento no había *test users* dados de alta. `BUG-046` cayó
> exactamente en ese punto ciego: el perímetro estaba perfecto y el camino feliz estaba roto al
> 100 %. Un tablero en verde compuesto solo de rechazos no es evidencia de que el sistema funcione.
>
> Por eso **el login e2e real sigue siendo la única prueba que falta y la de mayor riesgo abierto**
> de C4. No se puede cerrar `US-402` de producto hasta ejecutarla contra la revisión que ya incluye
> el parche de `BUG-046`, que al momento de escribir esto **aún no está desplegada**.

## 10. Firma del anexo

| | |
|---|---|
| **Revisor** | Christian Imanol Ruiz Hurtado — Tech Lead C4, dueño de `vault/07_Security/**` |
| **Fecha** | 2026-09-04 |
| **Alcance** | `BUG-046` (anexo A) y verificación en la URL pública (anexo B) |
| **Veredicto** | 🟢 `BUG-046` aprobado sin cambios · `SEC-009` abierto como follow-up · login e2e real **pendiente** |
| **Asistencia de IA** | Claude Code / claude-opus-5 — reversión del parche y lectura del código de `jose` ejecutadas y comprobadas antes de firmar |
