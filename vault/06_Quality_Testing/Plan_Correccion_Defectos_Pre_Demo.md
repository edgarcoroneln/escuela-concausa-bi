---
id: PLAN-FIX-PRE-DEMO
title: "Plan de corrección de defectos — del 8 al 9 de septiembre"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo", "US-006", "REQ-002", "REQ-004"]
traces_down: ["vault/06_Quality_Testing/Bug_Register", "vault/01_Product/Guion_Demo_US006"]
last_reviewed: "2026-09-08"
tags: [qa, fix, pre-demo, prioridad, freeze]
---

# Plan de corrección de defectos — quedan dos días

> Ordenado por **impacto sobre la demo**, no por severidad técnica. Un defecto feo que nadie va a ver
> el miércoles va después de uno cosmético que sí se proyecta.
> → [[vault/06_Quality_Testing/Bug_Register]] · [[vault/01_Product/Guion_Demo_US006]]

## El estado, en una tabla

Ocho defectos abiertos: seis del barrido de **Oscar Quiroz** en producción y dos del barrido de
sesión de **Karla Monter** más la verificación del PM.

| Bug | Qué rompe | Minuto del guion | Dueño |
|---|---|---|---|
| **`BUG-070`** | La sesión muere a los 15 min **sin avisar** | **3:00–5:00 y 6:30–7:30** | C5 + C2 |
| **`BUG-065`** | El par de demostración no se puede filtrar en DB-03 | **3:00–5:00** | C2 |
| **`BUG-068`** | DB-09 pone las escuelas sin predicción arriba | **3:00–5:00** | C2 |
| `BUG-071` | Dashboards y Chat renderizan sin sesión | 7:30–8:30 | C2 |
| `BUG-067` | DB-07 infla los totales ×6 | 1:00–3:00 | C2 |
| `BUG-069` | DB-10 dice 11 fuentes; hay 8 | 1:00–3:00 | C2 |
| `BUG-064` · `BUG-066` | Leyendas truncadas, ejes sin etiquetas | varios | C2 |
| `BUG-061` | `main` no reproduce producción | — (causa de `BUG-070`) | C2 + C5 |

## Prioridad 1 — hoy, o cambia el guion

### `BUG-070` + `BUG-061`: son un solo trabajo

**No se arreglan por separado.** El refresco de token está en `main` desde el 6-sep; lo que falta es
**una imagen del frontend construida desde `main`**. Y no se puede construir mientras el embebido de
Superset siga sin commitear, porque el rebuild lo perdería.

Secuencia, y el orden no es negociable:

1. **C2 commitea el embebido** desde el handoff de `_local/` — `superset_client.py` (265 líneas
   contra las 188 de `main`) y `1_Dashboards.py` con el Embedded SDK. Cierra `BUG-061`.
2. **C5 reconstruye la imagen del frontend desde `main`**, no parchando `embed-combo-dec019-logout`.
3. **Verificación obligatoria antes de cantar victoria**: iniciar sesión, esperar **más de 16
   minutos**, y usar el Panel ML. Es la prueba de Karla; si no se corre, no está arreglado.

**Mitigación de sala mientras tanto, y hay que decidirla hoy:** iniciar sesión **dentro** de la demo,
no en la preparación. Cuesta 20 segundos del minuto 7:30 y elimina el riesgo por completo.

### `BUG-065`: el par de demostración

`15DPR0920D` aparece **duplicado** en el dropdown de DB-03 y *"Apply filters"* queda deshabilitado.
Sin filtro, las cuatro tarjetas muestran el **agregado nacional** — 6,704,229 alumnos — como si fueran
de una escuela.

Oscar ya lo aisló: con un CCT de control sin duplicar el filtro funciona. **La hipótesis a verificar
primero es el duplicado en la dimensión que alimenta el `filter_select`** de `db03_ficha_escuela.yaml`
— una consulta de una línea contra `gold.dim_escuela` la confirma o la descarta.

**Si no se arregla hoy, el bloque 3:00–5:00 se enseña desde el Panel ML de FARO Web**, que sí resuelve
el par por CCT, y DB-03 se salta. Es peor narrativa pero funciona.

### `BUG-068`: el tablero del diferenciador

En DB-09, *"Escuelas a intervenir (mayor riesgo)"* pone primero las escuelas **sin predicción**,
porque Postgres ordena `NULL` primero en `ORDER BY … DESC`. **El arreglo es `NULLS LAST`.** Es el
tablero que sostiene la tesis del proyecto; que la lista prescriptiva empiece con N/A la invalida a la
vista.

## Prioridad 2 — mañana temprano, si hay tiempo

- **`BUG-067`** — DB-07 con totales inflados ×6: el cubo trae una fila por driver y la métrica no
  deduplica. Es un número **visiblemente falso** en el tablero de calidad de datos, que es
  precisamente donde presumimos honestidad.
- **`BUG-069`** — DB-10 declara 11 fuentes cuando el catálogo tiene 8. Contradice al propio subtítulo.
- **`BUG-071`** — guarda de sesión en las tres páginas: `if not current_user(): st.info(...);
  st.stop()`, reusando el `encabezado()` que ya existe en `auth.py:209`.

## Prioridad 3 — se declaran, no se arreglan

`BUG-064` y `BUG-066`: leyendas truncadas y ejes sin etiquetas en DB-01 y DB-04. Son de legibilidad,
no de dato. **Se dicen en la demo si alguien pregunta**, con su registro a la mano.

## Lo que NO es un bug, y por qué se escribe

**El 401 de `/auth/me` en Swagger.** El contrato es correcto —verificado: 401 limpio, sin traza— y la
causa probable es de uso: tras el login del navegador vuelve el **código de un solo uso**, no el
access token. Hay que canjearlo en `POST /api/v1/auth/exchange` primero. Se documenta el paso; no se
levanta bug.

## Pendiente que sólo el PO puede cerrar

**La lista `ANALISTA_EMAILS`.** Karla no pudo probar el rol `analista` porque es una variable de
entorno en Cloud Run que **sólo el PO ve**. Sin eso, el 200 de analista no se verifica en vivo —y el
403 de ciudadano ya está verificado, así que falta la mitad buena del par. Es acción del PO, hoy.

## Cómo se verifica que quedó

| Bug | Prueba que lo cierra |
|---|---|
| `BUG-070` | Sesión abierta, **esperar >16 min**, usar el Panel ML |
| `BUG-065` | Filtrar DB-03 a `15DPR0920D` y ver las 4 tarjetas con datos de esa escuela |
| `BUG-068` | Primera fila de "Escuelas a intervenir" con predicción real, no N/A |
| `BUG-067` | "Total de escuelas" en DB-07 igual al de DB-01 |
| `BUG-071` | `python tests/qa_barrido_sin_sesion.py` → **15/15** |
