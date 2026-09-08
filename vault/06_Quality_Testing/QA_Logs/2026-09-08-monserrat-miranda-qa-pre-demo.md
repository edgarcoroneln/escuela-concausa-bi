---
id: QALOG-2026-09-08-MONSERRAT-MIRANDA
title: "QA pre-demo — Monserrat Miranda — Nueve tableros (carga, datos, tabs, drill-down)"
owner: "Monserrat Xcaret Miranda Olivas"
status: done
traces_up: ["vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo"]
traces_down: ["vault/06_Quality_Testing/Bug_Register"]
last_reviewed: "2026-09-08"
tags: [qa, qa-log, pre-demo, celula-2]
---

# QA pre-demo — Monserrat Miranda — Nueve tableros

> → [[vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo]] ·
> [[vault/06_Quality_Testing/QA_Logs/_index]]

## Datos de la sesión

- **Responsable:** Monserrat Xcaret Miranda Olivas (C2)
- **Superficie asignada:** nueve tableros — carga, datos, tabs, filtros y enlaces de drill-down.
  *(DB-03 pasó a Estefany en el replanteo del 7-sep.)*
- **URL probada:** https://faro-frontend-526490367142.us-central1.run.app/Dashboards
- **Fecha y hora:** 2026-09-08, ~11:20–12:40 CST
- **Sesión iniciada como:** `xcaretmirandao@gmail.com` · rol no visible en la UI (ver caso 14)
- **Navegador y sistema:** navegador embebido de Claude Code sobre Windows 11, viewport 1100×780

## Resultados

> Veredictos: **✅ pasa** · **❌ falla** · **⚠️ pasa con reserva** · **⏭️ no ejecutado**.

| # | Caso | Esperado | Obtenido | Evidencia | Veredicto | Bug |
|---|---|---|---|---|---|---|
| 1 | Los 10 tableros embebidos cargan en `/Dashboards` con sesión iniciada | 10 secciones con contenido | 10 secciones, todas con datos; ninguna vacía | Recorrido completo del scroller `section.stMain` (8566 px) con captura por sección | ✅ | — |
| 2 | DB-01 · matrícula total | 6,704,229 (cifra de Diana) | **6,704,229** | Tarjeta KPI-01 | ✅ | — |
| 3 | DB-01 · completitud de drivers | 62 % | **62 %** | Tarjeta KPI-05 | ✅ | — |
| 4 | DB-01 · escuelas en alcance | 44,114 | **44,114** | Tarjeta | ✅ | — |
| 5 | DB-02 · KPI-04 escuelas en riesgo | **7** (punto 6 del plan: si dice 0, es hallazgo) | **7** | Tarjeta KPI-04 de DB-02 | ✅ | — |
| 6 | DB-02 · índice de riesgo promedio | 0.36 | **0.36** | Tarjeta KPI-03 | ✅ | — |
| 7 | **DB-05 · los 6 tabs existen y la nota de fuente va arriba** | 6 tabs D1–D6 + nota | 6 tabs presentes; nota *"CONEVAL (DS-07) · medido a nivel municipio"* en la primera fila | Captura del embebido de DB-05 | ✅ | — |
| 8 | **DB-05 · las tarjetas agrupan en horizontal (`US-213`)** | 4 tarjetas lado a lado por tab | **Apiladas en vertical**: `6.3 %` en una fila y `2,792` en la siguiente, cada una a 3/12 de ancho con el resto en blanco. DB-06, en la misma página, sí muestra sus 4 en línea | Captura comparada DB-05 vs DB-06; `main` trae el layout corregido desde `5415689` | ❌ | ver §Hallazgos — pendiente de re-sync, no de código |
| 9 | DB-08 · los 5 charts cargan | Sin charts vacíos | Los 5 renderizan: 44,114 · 0.08 · pastel de cobertura · pivote · detalle | Captura del embebido de DB-08 | ✅ | — |
| 10 | **DB-08 · la métrica `escuelas` no se infla por el grano de driver** | 44,114 (no ×6) | **44,114** — coincide con DB-01 y DB-04 | El cubo tiene grano `cct × id_driver × id_ciclo`; la métrica es `COUNT(DISTINCT cct)`, no `SUM` | ✅ | contraste con `BUG-067` |
| 11 | DB-08 · leyenda del pastel «Escuelas por cobertura del driver» | Categorías visibles | Leyenda paginada `◀ 1/2 ▶`: sólo una categoría a la vez | Captura del embebido | ⚠️ | `BUG-064` (amplía: también ocurre en DB-08) |
| 12 | DB-02 · «% escuelas en riesgo» | Porcentaje legible | **`0.0 %`** — mismo redondeo que Diana reportó en DB-04 | Tarjeta de DB-02 | ⚠️ | amplía a DB-02 el `BUG-070` de Manuel (rama `dev/manuel-serrania`), que lo registró sólo para DB-04 |
| 13 | DB-09 · «% escuelas con recomendación» | Fracción real | **`0 %`** | `BUG-054` está `fixed` en `main`, con nota *"⬜ Re-sync + reconfirmar antes del 9-sep"* | ❌ | `BUG-054` — pendiente de re-sync, no de código |
| 14 | Encabezado de sesión en `/Dashboards` | Correo y rol visibles (`encabezado()`, `BUG-059`) | No aparece; la barra lateral sólo trae los enlaces de navegación | `main` llama `encabezado()` en las 3 páginas; la imagen desplegada no | ⚠️ | síntoma de `BUG-061` / `BUG-070` |
| 15 | `/Dashboards` **sin sesión** | *"Inicia sesión"* (punto 2 del plan) | Página muda: los 10 títulos, cero contenido, sin aviso ni error. `/Panel_ML` y `/Chat` sí avisan | DOM: `iframes: 10`, `alertas: []`, `botones: []`, sin la cadena "sesión" en 359 caracteres | ❌ | **`BUG-071`** (Edgar, rama `dev/edgar-coronel`) — mismo defecto, reportado por Karla Monter; esto lo corrobora con medición |
| 16 | `/Chat` sin sesión | No error crudo | *"No se pudo consultar el agente: La sesión no es válida o expiró; inicia sesión nuevamente."* | Clic en el chip «Matrícula total» sin sesión | ✅ | — |
| 17 | API · postura de autenticación sin token | `/health` 200, el resto 401 | `/health` 200 · `/version` 200 · `/docs` 200 · `/openapi.json` 200 · `/kpis` 401 · `/escuelas` 401 · `/predicciones/{cct}` 401 | `curl` sin token | ✅ | — |
| 18 | API · versión desplegada | Commit de `main` | `9a654d4` (7-sep 02:09), **en `main`**, con 35 commits posteriores | `GET /api/v1/version` | ⚠️ | la imagen va atrás de `main`, pero es un commit legítimo |
| 19 | DB-05 · enlaces `link_db08` llevan al destino con el filtro aplicado | Navegar a DB-08 filtrado por municipio y driver | — | Requiere abrir la tabla municipal dentro del embebido y seguir el enlace; no alcanzado en esta sesión | ⏭️ | ver §Lo que NO alcancé |
| 20 | Los tableros con **la cuenta del evaluador** | Mismo render que con la propia | — | No tengo acceso a esa cuenta | ⏭️ | ver §Lo que NO alcancé |

## Resumen

- **Casos ejecutados:** 18 de 20
- **✅ pasa:** 10 · **⚠️ con reserva:** 5 · **❌ falla:** 3 · **⏭️ no ejecutado:** 2
- **Bugs levantados:** **ninguno.** Los tres ❌ ya tienen registro ajeno o no son defectos de código:
  el caso 15 es el `BUG-071` de Edgar (reportado por Karla); los casos 8 y 13 son correcciones ya
  mergeadas en `main` que no están desplegadas. El caso 12 amplía el `BUG-070` de Manuel a DB-02.
- **Clasificación para el miércoles:**
  - 🟠 **DB-05 en vertical** (caso 8) — el dato es correcto, pero es el único tablero que se ve
    distinto a los otros nueve, y es el del diferenciador por driver.
  - 🟠 **DB-09 al 0 %** (caso 13) — mismo mecanismo: arreglado en `main`, invisible en producción.
  - 🟠 **`/Dashboards` sin sesión** (caso 15) — sólo se ve al perder la sesión, y la sesión **no
    sobrevive a recargar** (punto 2 del plan), así que es alcanzable en vivo.
  - 🟢 Leyenda paginada en DB-08 (caso 11) y `0.0 %` en DB-02 (caso 12) — deuda declarada, amplían
    hallazgos ajenos.

## Lo que NO alcancé a probar

- **Los enlaces `link_db08` de DB-05 (caso 19).** Hay que abrir la tabla municipal dentro del
  embebido, desplazarse a la columna del enlace y seguirlo. Con el tablero en vertical, esa tabla
  queda muy abajo dentro del iframe, y el enlace abre en pestaña nueva — donde **la sesión se
  pierde** (punto 2). Es justo el caso que el layout corregido facilitaría.
- **Los tableros con la cuenta del evaluador (caso 20).** No tengo acceso. Queda sin cobertura:
  nadie ha verificado que la lista blanca de Superset (`DEC-018`, fail-closed y sin mensaje de
  error) incluya ese correo. Si no está, el evaluador no ve ningún tablero y no sabrá por qué.
- **DB-03** salió de mi alcance en el replanteo del 7-sep; no lo evalué más allá de constatar que
  carga (lo que muestra coincide con `BUG-065`, ya registrado por Oscar).
- **Los 6 tabs uno por uno.** Verifiqué D1 y que los seis existan; el clic sintético del navegador
  automatizado no cambia de tab en los componentes React de Superset (limitación conocida desde
  `BUG-038`). Los seis tabs sí se verificaron contra el `position_json` en el ambiente local.

## Hallazgos que no son bugs

**1. Hay correcciones terminadas que producción no ha visto, y no es una sola.** DB-05 (`US-213`,
en `main` desde el 5-sep) y `BUG-054` de DB-09 están ambos arreglados y ambos invisibles, porque la
carga a producción del 5-sep corrió a las 19:40 y el fix de DB-05 se mergeó a las 23:39. Ningún
workflow de `.github/workflows/` corre el `sync` — es manual. Conviene que el PO lo mire como un
solo pendiente y no como dos bugs sueltos.

**2. Sobre el punto 5 de las «seis cosas»: la interacción sí está verificada.** El plan congela el
`sync` porque *"el import que corre después manda `query_context: None` con `overwrite=true` y esa
interacción no está verificada"*. Se verificó el 2026-09-08 leyendo la fuente de Superset 6.1 en la
imagen desplegada:

- `superset/commands/dashboard/importers/v1/__init__.py:147` llama `import_chart(config,
  **overwrite=False**)` — cableado; el `overwrite=true` del formulario sólo llega a
  `import_dashboard` (línea 183).
- `import_chart` con `overwrite=False` hace `return existing` **sin ejecutar ningún `setattr`**, así
  que el `query_context` guardado no se toca.
- Para los charts que no son *timeseries*, el `PUT` de `ensure_chart` omite `query_context`; ningún
  campo de `ChartPutSchema` es obligatorio y `DAO.update` sólo asigna las claves enviadas.

**Un re-sync no borra el `query_context` de nadie.** No propongo correrlo —la ventana es del PO—,
pero el motivo declarado para congelarlo ya tiene respuesta. La confirmación empírica (correr el
sync y comparar antes/después) sigue sin hacerse, porque hacerla exige justamente correrlo.

**3. La sugerencia para las «seis cosas»:** el punto 1 dice *"sólo `/api/v1/health` responde sin
token"*, y en realidad `/version`, `/docs` y `/openapi.json` también responden 200 — que es lo que
`BUG-057` y `DEC-012` dejaron por escrito a propósito. Vale corregir la redacción para que nadie lo
levante como bug.

**4. Colisión de IDs en curso — para el PO.** Al buscar el siguiente ID libre encontré que
`BUG-070` y `BUG-071` están usados **dos veces cada uno**, para bugs distintos: en
`dev/edgar-coronel` son el refresco del token y las páginas sin sesión; en `dev/manuel-serrania`
son el `0.0 %` de DB-04 y los CCT del Panel ML. Ninguno está en `main`, así que por `DEC-013`
renumera quien llegue segundo — pero conviene resolverlo antes del merge y no después.

**5. El ancho del embebido.** Los iframes miden 704 px en una página de 1100, así que los tableros
se renderizan a ~64 % del ancho y los títulos de las tarjetas se truncan (`Ma… tot`, `KP…`) en los
diez. No lo levanto como bug porque afecta a todos por igual y puede ser decisión de diseño del
shell, pero en la demo se va a notar.
