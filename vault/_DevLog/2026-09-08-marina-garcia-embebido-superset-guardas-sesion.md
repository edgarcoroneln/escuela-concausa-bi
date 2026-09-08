---
project: "FARO"
date: "2026-09-08"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sesión: se commitea el embebido de Superset que nunca llegó a main (BUG-061), guardas de sesión en las tres páginas (BUG-071) y un flaky de prueba diagnosticado (BUG-072)"
touches: ["US-206", "US-526", "US-207", "US-305", "BUG-061", "BUG-070", "BUG-071", "BUG-072", "REQ-002", "REQ-004", "DEC-018"]
tags: [devlog, frontend, streamlit, superset, embebido, seguridad, celula-2]
---

# DevLog — 2026-09-08 — El embebido llega a `main`, y las tres páginas dejan de abrirse sin sesión

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/_DevLog/2026-09-06-luis-tellez-frontend-imagen-combinada|La imagen combinada de C5]]

## Contexto

Víspera de la demo. Tres encargos del PO, con el primero bloqueando al resto de la cadena.

**BUG-061** — el embebido de Superset que corre en producción **nunca se commiteó**: vivía
horneado en la imagen desde el working tree. Mientras `main` no lo tenga, **C5 no puede
reconstruir el frontend**, y sin ese rebuild **BUG-070** (`critical`) sigue vivo: el refresco de
token está en `main` desde el 6-sep pero **no en la imagen desplegada**, que está parchada a mano.
Por eso la sesión sigue muriendo a los 15 minutos en producción.

**BUG-071** — las tres páginas internas renderizan sin exigir sesión.

## 1. El código no lo tenía nadie

El encargo decía *"commitea desde el handoff que Luis dejó en `_local/`"*. **`_local/` está en
`.gitignore` (línea 84) y vive en la máquina de Luis.** Lo verifiqué antes de intentar nada:

- Mi disco: `superset_client.py` con **188 líneas**. No tenía el embebido.
- **Ninguna rama del repo lo tiene.** Recorrí las remotas buscando un `superset_client.py` de más
  de 200 líneas: **cero**. La de Manuel también en 188.

Luis lo empaquetó y lo mandó el mismo día. **Su LEEME decía "descomprime en la raíz del repo y
quedan en su sitio", y no era cierto**: el zip traía una carpeta raíz `embebido_frontend_c2/`.
Extraje aparte, leí los cuatro archivos completos y los copié uno por uno a su ruta. Luis ya
reconoció el error de empaquetado.

## 2. Las pruebas del handoff reprobaban tal cual llegaban — y no era el código

`test_frontend_dashboards_streamlit.py` fallaba **2 de 2 antes de tocar nada**.

`SupersetHTTPFake` hereda de `BaseHTTPRequestHandler`, cuyo `protocol_version` es **HTTP/1.0**:
cierra el socket tras cada respuesta. Pero `tableros_embebidos()` reutiliza **un solo**
`httpx.Client` para las ~22 peticiones del flujo —login, csrf, y slug + embed por cada uno de los
10 tableros—, así que a partir de la segunda toma del pool encuentra la conexión cerrada. En Linux
la carrera se pierde solo a veces; **en Windows falla siempre**, con
`httpx.ReadError [WinError 10053]`.

Lo que lo hacía difícil de leer: `1_Dashboards.py` captura `httpx.HTTPError` y lo pinta con
`st.error`, así que el síntoma no era una excepción sino *"no se montó ningún tablero"* — que
parece un defecto del embebido y no lo es.

Una línea lo arregla (`protocol_version = "HTTP/1.1"`; `_respond` ya emitía `Content-Length`).
**5 corridas consecutivas en verde.** El mismo defecto existía en la versión previa de la prueba
en `main`, así que no lo introdujo el handoff. Queda registrado como **BUG-072**.

> **Corrección de mi diagnóstico, y agradezco que me la hicieran.** Lo reporté primero como *"la
> causa raíz de BUG-059"*. **Es falso.** `BUG-059` es la sesión de `auth.py` —refresco de token y
> encabezado en las páginas—, `fixed` por Christian el 6-sep, con `test_frontend_auth.py`. Lo
> verifiqué en el registro tras el aviso de Luis. Son cosas distintas: aquello es de aplicación y
> está cerrado; esto es un defecto de prueba. Registrarlo mal habría reabierto en los papeles algo
> que ya estaba resuelto.

## 3. BUG-071: apagar no es lo mismo que esconder

`encabezado()` **no bloquea a nadie** — lo dice su propio docstring: *"No decide quién entra. Solo
muestra el estado"*. Las tres páginas lo llamaban y seguían de largo. Se trataron distinto **a
propósito**:

- **Dashboards y Chat: guarda completa.** Sin sesión no se dibuja nada operable. En Dashboards
  el agravante es que `superset_client` autentica con **credenciales admin propias**, así que la
  página montaba los diez embebidos igual y quedaban en blanco **en silencio**: quien la abriera
  antes de entrar concluiría que los tableros están rotos. La guarda va **antes** del login a
  Superset, y hay prueba de que sin sesión el servidor falso no recibe ni una petición.
- **Panel de ML: los controles se apagan, no se ocultan.** Es el bloque 3:00–5:00 del guion y
  prefiero que la página siga explicando qué ofrece. `AppTest` **hace cumplir `disabled`** —
  rechaza `set_value` con *"A browser user cannot interact with a disabled widget"*—, así que la
  prueba comprueba comportamiento, no una bandera.

### Un aviso que era falso, y es peor que el defecto reportado

El Panel de ML decía literalmente **"Puedes consultar predicciones sin iniciar sesión: la lectura
es pública"**. Desde **DEC-018** eso **no es cierto**: producción corre con
`AUTH_LECTURA_PUBLICA=false`. La página prometía algo que la API ya no cumple, y el 401 resultante
salía como *"La API rechazó la solicitud"* — **un fallo de permiso disfrazado de fallo de
servicio**. Es la misma confusión que costó el diagnóstico inicial de BUG-070. Hay prueba que
reprueba si alguien restaura la promesa vieja.

## 4. Una guarda mía se rompió, y tenía razón

Al inyectar sesión en las pruebas apareció justo lo que
`test_la_pagina_sigue_teniendo_un_solo_campo_y_un_solo_boton` vigilaba: **con sesión,
`encabezado()` dibuja "Cerrar sesión" en la barra lateral, así que `app.button[0]` deja de ser el
submit del formulario.** Es el modo de falla exacto que esa guarda anticipaba, disparado por un
cambio que no lo parecía.

Se arregló de raíz: las pruebas que direccionaban **por índice** ahora buscan **por etiqueta**, en
Panel ML y en Chat. Ya no dependen del orden de pintado.

## Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Código de terceros:** el embebido (`superset_client.py`, `1_Dashboards.py` y sus dos pruebas)
  es **de Manuel Serranía (C2)**, empaquetado por **Luis Téllez (C5)**. Lo subo yo por
  indisponibilidad de Manuel, con respaldo explícito del PO. **Leí los cuatro archivos completos
  antes de copiarlos** y verifiqué por mi cuenta que no traen secretos: la credencial de Superset
  sale de `SUPERSET_ADMIN_PASSWORD`.
- **Decisiones autónomas:** apagar el Panel de ML en vez de ocultarlo; poner la guarda de
  Dashboards **antes** del login a Superset y no después; corregir las pruebas por etiqueta en vez
  de reordenar la barra lateral.
- **Correcciones propias:** (1) atribuí el flaky a `BUG-059` sin verificarlo — es `BUG-072`;
  (2) quité un `from typing import Any` sin usar que traía el handoff y que **habría reprobado el
  CI** por `ruff`.

## Seguridad / calidad

- [x] Sin secretos en el código (verificado por mí, no asumido del LEEME)
- [x] `ruff` ✅ · **1117 pruebas en verde**, 4 saltadas
- [x] 6 pruebas nuevas de guarda de sesión; el flaky validado con 5 corridas consecutivas
- [x] Las tres páginas exigen sesión; ninguna consulta la API ni Superset sin ella

## Lo que se ve y no se toca

- **`1_Dashboards.py:37` carga el SDK de Superset desde `unpkg.com` sin versión fijada.** Si el
  CDN va lento o la red del aula lo bloquea, no hay tableros — hay mensaje de respaldo, pero el
  bloque se cae. **No se cambia**: hay que mantener paridad con la imagen probada. Luis lo escala
  al PO.
- **`RLS_CLAUSES` está vacío para los dos roles**: hoy `ciudadano` y `analista` ven lo mismo. El
  propio código lo declara. Deuda de diseño, no de esta noche.

## Lo que desbloquea

Con esto en `main`, **C5 puede reconstruir la imagen del frontend** con el patrón de la API
—revisión a 0 %, validar, promover— y eso **cierra BUG-070**: el refresco de token deja de estar
solo en `main` y llega a producción. Es la razón por la que este merge no podía esperar a mañana.
