---
project: "FARO"
date: "2026-09-08"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "barrido QA sin sesión con Playwright, diagnóstico del refresco de token y plan de corrección"
tags: [devlog, pm, qa, playwright, bug-070, bug-071, bug-061, pre-demo]
---

# DevLog — 2026-09-08 — El refresco que sí existe y nunca se desplegó

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/06_Quality_Testing/QA_Logs/2026-09-08-edgar-coronel-qa-sin-sesion-playwright]] ·
[[vault/06_Quality_Testing/Plan_Correccion_Defectos_Pre_Demo]]

## 1. `BUG-070` — el hallazgo del día, y el diagnóstico cambia el arreglo

Karla Monter reportó que la sesión se rompe a los 15 minutos: login 6:24, y a los 16 min el Panel ML
rechaza la predicción. Su diagnóstico fue *"el frontend guarda el `refresh_token` pero nunca llama a
`/auth/refresh`; no existe esa llamada en `src/frontend/**`"*.

**Fui a verificarlo y su observación es correcta pero su causa es falsa — y esa diferencia es el
bug.** En `main` la llamada **sí existe**: `auth.py:115` define `_refrescar()`, la 126 hace el `POST
/api/v1/auth/refresh`, la 148 refresca dentro del margen de 120 s, y `2_Panel_ML.py:260,294` y
`3_Chat.py:39` ya piden el token por `token_de_acceso()`. Entró con el **PR #267 de Christian, el
6-sep a las 01:38**.

**Lo que falla es el despliegue.** La imagen que corre es la cadena `embed-combo-dec019` →
`embed-combo-dec019-logout` (rev `faro-frontend-00008-fpw`), y el propio DevLog de C5 lo dice sin
ambigüedad: *"el diff frente a la imagen desplegada es SOLO el logout"*. **Nunca se construyó una
imagen del frontend desde `main`.**

Es **`BUG-061` materializándose como falla de demo**. Lo registré hace dos días como *"main no puede
reproducir producción"* y sonaba a deuda de higiene; hoy es la razón por la que la sesión se cae a
media presentación.

**Por eso el arreglo no es escribir código: es commitear el embebido y reconstruir desde `main`.** Si
alguien "arregla" el refresco escribiéndolo otra vez, lo escribe donde ya está.

## 2. El barrido con Playwright: 13 de 15

Corrí la superficie **sin sesión** contra producción. No inicio sesión por nadie, así que ese fue el
alcance — y resultó ser donde estaban dos hallazgos.

Los dos rojos confirman de forma independiente el punto 3 de Karla: **Dashboards y Chat renderizan
sin exigir login ni avisar**. Verificado también en código —cero guardas en los tres archivos de
`pages/`— con un agravante que ella ya había visto y yo confirmé: `superset_client.py:51` autentica
con **credenciales admin propias**, así que el embebido **no depende de la sesión FARO**. Sin login,
los 10 tableros quedan en blanco y en silencio. `BUG-071`.

## 3. Un falso positivo mío, corregido en la misma bitácora

La primera pasada marcó **el login de Superset sin botón de Google** — el peor hallazgo posible a un
día de la demo. **Era mío**: usé `domcontentloaded` y el selector corrió antes del render. Con
`networkidle` el botón está ahí.

Lo dejo escrito porque el modo de falla importa más que el error: **una prueba de navegador que no
espera al render produce rojos falsos**, y un rojo falso a un día de la demo cuesta más que no haber
probado.

## 4. Lo que se revisó y NO es bug

El **401 de `/auth/me` en Swagger**. El contrato es correcto —401 limpio, sin traza, medido— y la
causa probable es de uso: tras el login del navegador vuelve el **código de un solo uso**, no el
access token; hay que canjearlo en `/auth/exchange`. Se documenta el paso que falta en vez de abrir
un bug que no existe.

## Verificado

`tests/qa_barrido_sin_sesion.py` contra producción → **13/15** · `grep -cE "st.stop\(\)|require_role"`
→ **0** en las tres páginas · `auth.py:115,126,148` leídas · fecha del PR #267 y linaje de la imagen
desplegada cotejados contra el DevLog de C5 · `pytest tests/ -q` **1078 passed, 4 skipped** · `ruff`
limpio · `vault_lint` limpio

## IDs tocados

`BUG-070`, `BUG-071`, `BUG-061`, `BUG-059`, `US-405`, `US-207`, `US-305`, `US-206`, `REQ-002`,
`REQ-004`, `REQ-005`

## Próximos pasos

- **C2 commitea el embebido**; **C5 reconstruye desde `main`**. Es un solo trabajo y cierra `BUG-070`.
- Decidir hoy la **mitigación de sala**: iniciar sesión dentro de la demo, no en la preparación.
- El PO confirma `ANALISTA_EMAILS` para que Karla cierre su prueba 4.
