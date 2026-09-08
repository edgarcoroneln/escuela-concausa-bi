---
id: QA-2026-09-08-PM
title: "QA pre-demo — superficie sin sesión, con Playwright contra producción"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
traces_up: ["vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo", "REQ-004", "REQ-005"]
traces_down: ["vault/06_Quality_Testing/Bug_Register"]
last_reviewed: "2026-09-08"
tags: [qa, playwright, produccion, sin-sesion, pre-demo]
---

# QA pre-demo — la superficie sin sesión, medida con Playwright

> Ejecutado contra **producción**, no contra local, como exige el plan.
> Script reproducible: `tests/qa_barrido_sin_sesion.py`. Cualquiera puede re-correrlo.

## Alcance y su límite, declarado

**Este barrido NO inicia sesión.** Iniciar sesión con Google exige credenciales de una persona, y el
PM no las introduce por nadie. Lo que se cubre es exactamente **lo que ve quien llega sin
credenciales** — que resultó ser donde estaban dos de los hallazgos.

La parte autenticada la ejecutan sus dueños con su propia sesión, según el reparto del plan.

## Resultado: 13 de 15

| # | Caso | Esperado | Obtenido | |
|---|---|---|---|---|
| API-health | `GET /api/v1/health` | 200 | 200 | 🟢 |
| API-version | `GET /api/v1/version` | 200 | 200 | 🟢 |
| API-me | `GET /api/v1/auth/me` sin sesión | 401 | 401 | 🟢 |
| API-kpis | `GET /api/v1/kpis` sin sesión | 401 | 401 | 🟢 |
| API-escuelas | `GET /api/v1/escuelas` sin sesión | 401 | 401 | 🟢 |
| API-consulta | `GET` sobre ruta POST | 405 | 405 | 🟢 |
| API-docs | `/api/v1/docs` | 200 | 200 | 🟢 |
| API-docs | `/docs` (raíz, no existe) | 404 | 404 | 🟢 |
| SEC-01 | 401 con token inválido no filtra detalle | sin traza | limpio | 🟢 |
| SUP-01 | Superset sin sesión redirige a login | `/login/` | `/login/?next=…` | 🟢 |
| SUP-02 | El login de Superset ofrece Google | botón visible | `<a> Sign in with Google → /login/google` | 🟢 |
| WEB-01 | La portada de FARO Web carga | carga | carga | 🟢 |
| WEB-Panel_ML | ¿avisa sin sesión? | avisa | avisa | 🟢 |
| **WEB-Dashboards** | **¿exige login antes de renderizar?** | **bloquea o avisa** | **renderiza sin aviso** | **🔴** |
| **WEB-Chat** | **¿exige login antes de renderizar?** | **bloquea o avisa** | **renderiza sin aviso** | **🔴** |

## Corrección dentro de esta misma bitácora

La primera pasada reportó **`SUP-02` en rojo** — *"el login de Superset no ofrece Google"*—, que
habría sido el hallazgo más grave posible a un día de la demo. **Era un falso positivo mío**: usé
`wait_until="domcontentloaded"` y el selector corrió antes de que la página terminara de pintar. Con
`networkidle` el botón aparece: `<a> Sign in with Google → /login/google`.

Queda escrito porque el modo de falla importa más que el error: **una prueba de navegador que no
espera al render produce rojos falsos**, y un rojo falso a un día de la demo cuesta más que no haber
probado. El script ya corregido usa `networkidle` en esa navegación.

## Los dos hallazgos, y qué los hace subir de cosméticos

Confirman de forma independiente el punto 3 del reporte de sesión de **Karla Monter**. Verificado
además en código: `grep -cE "st.stop\(\)|require_role|if not user"` da **0** en los tres archivos de
`src/frontend/pages/`.

El agravante lo aporta `superset_client.py:51::_admin_token()`: el embebido autentica con
**credenciales admin propias**, así que **no depende en absoluto de la sesión FARO**. Sin login, los
10 tableros quedan **en blanco y en silencio**. Si el evaluador abre Dashboards antes de iniciar
sesión, concluye que están rotos.

Registrado como `BUG-071`.

## Lo que este barrido NO pudo cubrir, y quién lo tiene

- **La parte autenticada completa** — de sus dueños, con su sesión.
- **El punto 4 de Karla**: no pudo probar el rol `analista` porque `ANALISTA_EMAILS` es una variable
  de entorno en Cloud Run que **sólo el PO puede ver**. Es una acción del PO, no un bug.

## Sobre el 401 de `/auth/me` en Swagger

Reportado como posible fallo de validación del token. **Revisado: no es un bug.** El endpoint es
`src/api/v1/auth.py:224` con `Depends(get_current_user)`, y su contrato es 401 sin token válido —
medido arriba, y el error sale limpio, sin traza.

La causa probable es de uso: el flujo tiene **tres** rutas (`/login` → 302, `/callback` → `TokenPair`,
`/exchange` → `TokenPair` a partir del código de un solo uso). Tras el login del navegador, lo que
vuelve al frontend es el **código `code_faro`**, no el access token. **Autorizar Swagger con ese
código da 401.** Hay que canjearlo primero en `POST /api/v1/auth/exchange` y usar el `access_token`
de la respuesta.

**No se levanta bug; se documenta el paso que falta.** Si vuelve a pasarle a alguien más, entonces sí
es un defecto de usabilidad del contrato y se registra.

## Cómo re-correrlo

```bash
pip install playwright pytest-playwright && playwright install chromium
python tests/qa_barrido_sin_sesion.py resultados.json
```
