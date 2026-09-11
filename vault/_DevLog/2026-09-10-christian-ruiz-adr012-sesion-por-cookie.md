---
project: "FARO"
date: "2026-09-10"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — parte de C4 de ADR-012: sesión por cookie httpOnly para el frontend de React"
touches: ["ADR-012", "ADR-010", "SEC-006", "BUG-059", "US-402", "US-405", "US-404", "REQ-004"]
tags: [devlog, celula-4, api, seguridad, cookies, react, adr012]
---

# DevLog — 2026-09-10 — Parte de C4 de `ADR-012`: la sesión deja de vivir en el navegador

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/07_Security/Threat_Model|Threat_Model §Sesión React]] ·
[[vault/03_Architecture/ADRs/ADR-010-puente-oauth-frontend|ADR-010]]

## Contexto

El Dr. pidió quitar Streamlit y Superset visibles, así que E5 (Diana, Luis y yo) rehace el frontend
en React + Vite, **estático**, servido por nginx. Eso rompe una premisa de `ADR-010`: hasta hoy el
**servidor** de Streamlit canjeaba el `code_faro` y guardaba los tokens; un sitio estático no tiene
dónde ponerlos.

Diana propuso Bearer administrado por el navegador y **yo lo firmé**, con condiciones. **Luis
objetó, y tenía razón**: verificó que la API no emite una sola cabecera de seguridad —ni en el
código ni en producción— y midió el impacto en CIS v8 (Control 16 de ~9 a ~7). Retiré la firma.

Su propuesta era construir un BFF. **No hizo falta.**

## La decisión: la cookie la pone la API, a través del proxy

nginx ya iba a servir los estáticos, y yo ya había pedido que además hiciera `proxy_pass` de `/api`.
Con eso el navegador ve **un solo origen**, y entonces basta con que la API emita la cookie:

1. `/auth/exchange` responde con `Set-Cookie` **sin atributo `Domain`** → queda **host-only del
   origen del frontend**, porque la respuesta llega por el proxy.
2. Las llamadas siguientes a `/api/*` la mandan solas.
3. `get_current_user` la lee cuando no viene `Authorization`.

**Resultado:** el token nunca toca JavaScript, `ADR-010` se conserva intacto, **el frontend no
maneja tokens en absoluto** —es más simple que la propuesta original, no más compleja— y no hay
servicio nuevo ni destino de despliegue nuevo.

> **No contradice `BUG-059`.** Allí el hallazgo fue que `.run.app` está en la Public Suffix List, así
> que la API **no puede** poner una cookie compartida entre dos subdominios. Aquí es host-only del
> propio origen, puesta por el proxy. Hay una prueba (`test_ninguna_cookie_fija_domain`) que impide
> que alguien "arregle" esto agregando un `Domain` y reviva aquel bug.

## Qué se hizo

- **`src/api/security/cookies.py`** (nuevo) — nombres, siembra y borrado. Dos decisiones:
  - **La cookie de refresco va acotada a `/api/v1/auth/refresh`**, derivando la ruta de
    `url_path_for` en vez de escribirla a mano. El navegador no manda la credencial de **7 días** en
    ninguna otra petición: un fallo en cualquier otro endpoint no puede filtrarla.
  - **El cambio es aditivo**: el cuerpo de `/auth/exchange` **sigue trayendo el par**, así que el
    shell de Streamlit sigue vivo mientras dura la migración. Los dos frontends conviven.
- **`src/api/v1/auth.py`** — `exchange` y `refresh` siembran la sesión; `refresh` acepta el token
  del cuerpo **o** de la cookie; **`POST /auth/logout` nuevo** (204).
- **`src/api/security/deps.py`** — segundo portador. **El encabezado tiene precedencia**: un
  `Authorization` explícito describe la intención del cliente, la cookie la manda el navegador solo.
- **`src/api/security/rbac.py`** — `require_lectura` propaga el `request`. Sin esto el frontend nuevo
  no autenticaría en ninguna ruta de lectura, que con `SEC-006` activo son todas.
- **`src/api/app.py`** — cabeceras: `X-Content-Type-Options`, `Referrer-Policy` y HSTS fuera de
  local. **`CSP` y `X-Frame-Options` quedan para nginx (C5)**, deliberadamente: es donde contienen el
  XSS del chat, y donde no se arriesga romper `/docs`, que carga Swagger UI de un CDN.

## Un bug que encontró una prueba mía

`test_el_logout_borra_las_dos_cookies` reprobó: el logout borraba `faro_sesion` pero **no**
`faro_refresco`. La causa era mía — construía una `Response` nueva con `headers=dict(...)`, y
**`dict()` colapsa los `Set-Cookie` repetidos en uno solo**. En producción eso habría dejado la
sesión reconstruible **7 días después de cerrarla**. Se corrige mutando la respuesta inyectada.

Es exactamente el motivo por el que la condición que puse fue *"el logout borra los dos tokens"* y
no *"hay logout"*.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** `src/api/security/cookies.py`, `tests/test_auth_cookies.py`, este DevLog.
- **Modificados:** `src/api/v1/auth.py`, `src/api/security/deps.py`, `src/api/security/rbac.py`,
  `src/api/app.py`, `api/openapi.v1.json`, `vault/07_Security/Threat_Model.md` (`version: 1.1`),
  `vault/_DevLog/_index.md`.

## Seguridad / calidad

- [x] **34 casos** en `test_auth_cookies.py`; 150 verdes en toda la superficie de auth y contrato
- [x] Las seis pruebas de la fuga de token, **verificadas reprobando** con el defecto reintroducido
- [x] `ruff check .` (todo el repo, como el CI) limpio
- [x] OpenAPI reexportado; `test_api_contract.py` verde
- [x] Los atributos de la cookie están **fijados por pruebas**, no solo escritos: `HttpOnly`,
      `SameSite=Lax`, `Path` de la de refresco y **ausencia de `Domain`**
- [x] Retrocompatibilidad probada: el cuerpo sigue trayendo el par y el refresco por cuerpo funciona

## La corrección que pidió el PO, y que es la parte importante

Edgar solicitó cambios al revisar el PR, y **el punto de seguridad era real y mío**: `/auth/refresh`
aceptaba la cookie y **devolvía el `TokenPair` en el JSON**. Como la cookie de refresco está acotada
a esa ruta, el navegador la adjunta ahí — así que un XSS podía hacer `fetch()` contra el endpoint y
**leer los dos tokens**, dejando `HttpOnly` sin ningún efecto. Todo el diseño se caía por ahí.

Corregido separando los modos, que ya **no se mezclan**:

| Endpoint | Modo | Cómo se elige | Cookies | Cuerpo |
|---|---|---|---|---|
| `/auth/exchange` | legacy *(default)* | sin `?sesion` | no las toca | `TokenPair` |
| `/auth/exchange` | cookie | `?sesion=cookie` | siembra | `SesionOut` — **sin JWT** |
| `/auth/refresh` | legacy | token en el **cuerpo** | no las toca | `TokenPair` |
| `/auth/refresh` | cookie | token en la **cookie** | renueva | `SesionOut` — **sin JWT** |

Dos detalles del diseño:

- **En `refresh` el modo se infiere de dónde vino el token**, que es inequívoco. En `exchange` hace
  falta `?sesion=` porque el cuerpo es idéntico en los dos casos: nada distingue al servidor de
  Streamlit del navegador.
- **El default es el legacy**, así que ahora la retrocompatibilidad es más fuerte que antes: ningún
  cliente existente cambia de comportamiento, ni siquiera recibiendo cookies que no pidió.

Seis pruebas nuevas lo fijan, **verificadas reprobando** con la fuga reintroducida. Una busca la
forma `eyJ` en el texto crudo por si alguien anidara el token bajo otro nombre.

## Residuales aceptados — registrados, no resueltos

- **CSRF.** Con cookie, un tercero puede provocar peticiones. Lo contiene `SameSite=Lax`. **No hay
  token anti-CSRF**; se acepta para la ventana con el criterio de `SEC-003/004/005`.
- **XSS.** `HttpOnly` impide *leer* el token, no impide *usar* la sesión. El vector concreto es la
  respuesta del agente renderizada en el chat.

## Avisos a otros owners

- **Diana Alvarez (C1) — te quita trabajo:** tu app deja de guardar, refrescar y adjuntar tokens.
  Solo `credentials: "same-origin"` en cada llamada, y `POST /api/v1/auth/logout` para cerrar. **Y
  la condición que no se negocia: nada del chat renderizado como HTML** — sin
  `dangerouslySetInnerHTML`, `react-markdown` con HTML crudo desactivado.
- **Luis Téllez (C5) — dos cosas tuyas:** el `proxy_pass` de `/api` (sin él, nada de esto funciona y
  además volvemos a necesitar CORS), y **`Content-Security-Policy` + `X-Frame-Options` en nginx**.
  Con el proxy, `cors_origins` **no se amplía**: queda same-origin.
- **Karla Monter (C4):** `/auth/logout` es ruta nueva del contrato; el OpenAPI ya está reexportado.

## Próximos pasos

1. Luis: `proxy_pass`, CSP y el Dockerfile sobre `nginx-unprivileged`.
2. Diana: `credentials: "same-origin"`.
3. `FRONTEND_REDIRECT_URIS` con el origen nuevo — **es variable de entorno, no código**.
4. **Corte del viernes 18:00:** si el login no funciona contra Cloud Run a esa hora, se le pide a
   Edgar reabrir la lectura pública. Con este diseño lo veo menos probable: el trabajo delicado lo
   hace la API, que ya está probada.
