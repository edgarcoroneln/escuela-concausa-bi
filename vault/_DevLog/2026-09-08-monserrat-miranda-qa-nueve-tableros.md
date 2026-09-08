---
project: "FARO"
date: "2026-09-08"
author_human: "Monserrat Xcaret Miranda Olivas"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sesión: QA pre-demo de los nueve tableros en producción; ningún bug nuevo y tres cosas que el PO necesita saber"
touches: ["US-213", "US-214b", "REQ-002", "BUG-054", "BUG-064", "BUG-067", "BUG-070", "BUG-071", "TEST-PLAN-PRE-DEMO"]
tags: [devlog, qa, pre-demo, superset, bi, celula-2]
---

# DevLog — 2026-09-08 — Nueve tableros en producción: nada roto, y dos arreglos que nadie ve

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/06_Quality_Testing/QA_Logs/2026-09-08-monserrat-miranda-qa-pre-demo]] ·
[[vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo]]

## Contexto

Ejecución del alcance que el plan de pruebas asigna a esta autora: los nueve tableros —carga,
datos, tabs, filtros y drill-down— **contra producción**, no contra local, como ordena el plan.
La bitácora con los 20 casos está en `QA_Logs`; aquí va lo que no cabe en una tabla.

**Resultado corto: los 10 tableros cargan, ninguno sale vacío, y no se levantó ningún bug nuevo.**
Los tres casos en rojo ya tenían registro ajeno o no son defectos de código.

## 1. Lo que confirma que el dato está bien

Las cifras cuadran con el bloque de Diana Alvarez, que es la comprobación que el plan pide:

| Dato | Producción |
|---|---|
| Matrícula total | 6,704,229 |
| Completitud de drivers | 62 % |
| Índice de riesgo promedio | 0.36 |
| Escuelas en alcance | 44,114 |

Y **KPI-04 muestra 7** en DB-02, con lo que el **punto 6 de las «seis cosas»** queda respondido: el
Gold desplegado **sí** se rematerializó con la línea de alerta de `DEC-019`. Era la duda explícita
del plan (*"lo que no está verificado es si el Gold desplegado se rematerializó"*), y ya no lo es.

**DB-08 sale limpio, y por una razón que vale anotar.** Su métrica `escuelas` da **44,114**, sin
inflar, aunque el cubo tenga grano `cct × id_driver × id_ciclo` — el mismo grano multi-fila que
produjo el ×6 de `BUG-067` en DB-07 (264 684 = 44 114 × 6). La diferencia es que aquí la métrica es
`COUNT(DISTINCT cct)` y allá un `SUM`. Revisadas también las métricas de DB-05: sus 36 charts
llevan el `adhoc_filter` de `id_driver` por tab, así que la `dimension_obligatoria_en_agregacion`
declarada en el contrato hizo exactamente lo que documentaba.

> Queda un arma cargada con el seguro puesto: `matricula_total` está declarada en el dataset de
> DB-08 y **no la usa ningún chart**. Si alguien agrega uno con ella —o enciende los totales del
> pivote— se infla ×6 al instante.

## 2. El hallazgo que importa: dos arreglos terminados que producción no ha visto

**DB-05 sigue en vertical.** Las tarjetas se apilan una debajo de otra, a 3/12 de ancho con el resto
en blanco, mientras DB-06 —en la misma página— muestra sus cuatro en línea. Es el layout previo a
`US-213`.

**DB-09 sigue mostrando `0 %`** en «escuelas con recomendación». Es `BUG-054`, que Manuel Serranía
ya corrigió y cuya propia ficha dice *"⬜ Re-sync + reconfirmar en navegador antes del 9-sep"*.

**Los dos tienen la misma causa, y no es código.** La carga a producción corrió el **5-sep a las
19:40**; el fix de DB-05 se mergeó a `main` a las **23:39**. Cuatro horas. Y **ningún workflow de
`.github/workflows/` corre el `sync`** —verificado en los cinco—, así que sólo se actualiza a mano.

Conviene que el PO lo mire como **un solo pendiente de despliegue y no como dos bugs sueltos**,
porque la acción que los cierra es la misma y no es de Célula 2.

## 3. Sobre el punto 5 del plan: la interacción sí quedó verificada

El plan congela el `sync` con este motivo textual: *"el import que corre después manda
`query_context: None` con `overwrite=true` y **esa interacción no está verificada**"*.

Se verificó leyendo la fuente de **Superset 6.1 dentro de la imagen desplegada**:

- `superset/commands/dashboard/importers/v1/__init__.py:147` llama
  `import_chart(config, overwrite=False)` — **cableado**. El `overwrite=true` del formulario sólo
  llega a `import_dashboard` (línea 183), que gobierna el tablero y sus relaciones, no los campos
  del chart.
- `import_chart` con `overwrite=False` hace `return existing` **sin ejecutar un solo `setattr`**.
- Para los charts que no son *timeseries*, el `PUT` de `ensure_chart` omite `query_context`; ningún
  campo de `ChartPutSchema` es obligatorio y `DAO.update` sólo asigna las claves enviadas.

**Un re-sync no borra el `query_context` de nadie**: ni los 20 *timeseries* que el `PR #275` ya
reescribe, ni los ~106 que C5 materializó a mano el 5-sep.

**No se propone correrlo** — la ventana es del PO y la regla sigue vigente. Lo que cambia es que el
motivo declarado para congelarlo ya tiene respuesta, y que la decisión puede tomarse con evidencia
en vez de con una incógnita. La confirmación empírica —correr el sync y comparar antes y después—
sigue sin hacerse, porque hacerla exige justamente correrlo.

> **Corrección propia:** el sábado se señaló esta misma interacción como una mina que apagaría ~106
> charts, a partir de leer `_export_chart` y el `overwrite=true` del formulario. Era una conclusión
> creíble sacada de leer una parte: el importador no aplica ese flag a los charts. Se corrige aquí
> porque el aviso llegó a circular.

## 4. Colisión de IDs en curso — para el PO

Al buscar el siguiente ID libre para registrar un hallazgo apareció esto:

| ID | En `dev/edgar-coronel` | En `dev/manuel-serrania` |
|---|---|---|
| `BUG-070` | Refresco del token no desplegado (*critical*) | DB-04 `0.0 %` (*low*) |
| `BUG-071` | Páginas internas sin exigir sesión (*medium*) | Panel ML con CCT viejos (*low*) |

**Cuatro bugs distintos, dos IDs, ninguno en `main`.** Por `DEC-013` renumera quien llegue segundo,
así que el mecanismo funciona — pero ahora mismo dos personas creen tener el mismo número, y
resolverlo antes del merge cuesta menos que después.

Gracias a eso **no se levantó ningún bug**: el hallazgo propio —`/Dashboards` sin sesión se queda
mudo, sin *"Inicia sesión"*, mientras Panel ML y Chat sí avisan— resultó ser el `BUG-071` de Edgar,
reportado por Karla Monter. Lo de esta sesión sólo lo corrobora con medición del DOM: 10 iframes,
`alertas: []`, `botones: []`, y la cadena "sesión" ausente en 359 caracteres de página.

## 5. Dos huecos, dichos porque no cubrirlos es peor que declararlos

- **Los enlaces `link_db08` de DB-05 no se pudieron seguir.** Hay que abrir la tabla municipal
  dentro del embebido y seguir el enlace, que abre en pestaña nueva — donde **la sesión se pierde**
  (punto 2 del plan). Con el tablero en vertical esa tabla queda hundida dentro del iframe. Es
  justo el caso que el layout corregido facilitaría.
- **Nadie ha verificado que el correo del evaluador esté en la lista blanca de Superset.** Por
  `DEC-018` es *fail-closed* y **sin mensaje de error**. Si ese correo no está, el miércoles no ve
  un solo tablero y no habrá nada en pantalla que explique por qué. No está en el alcance de esta
  autora y no aparece en ninguna bitácora: queda sin cobertura.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Modificados:** `vault/06_Quality_Testing/QA_Logs/2026-09-08-monserrat-miranda-qa-pre-demo.md`
  (nuevo), `vault/06_Quality_Testing/QA_Logs/_index.md`, este DevLog, `vault/_DevLog/_index.md`
- **No se tocó código.** Sesión de verificación: nada de `superset/**`, `src/**` ni `tests/**`.
- **No se corrió `sync_semantic_layer.py`** — regla de ventana del punto 5, respetada.
- **Decisiones autónomas:** verificar el ID libre antes de escribir el bug (evitó una colisión y un
  registro duplicado del hallazgo de Karla); y probar el chip del Chat sin sesión antes de
  reportarlo, lo que descartó un falso positivo — falla con mensaje claro, no con error crudo.
- **Corrección propia registrada:** la mina del `query_context` señalada el 6-sep era falsa (§3).

## Seguridad / calidad

- [x] `vault_lint.py` → Vault limpio · `check_ownership.py` → alcance correcto (2 archivos, carpeta
      común `vault/06_Quality_Testing/**`)
- [x] Pruebas ejecutadas **contra producción**, como ordena el plan; ningún ambiente local levantado
- [x] Sin credenciales tecleadas por el agente: la sesión de Google la abrió la autora
- [x] Ningún bug levantado sin verificar antes que el ID estuviera libre y que el hallazgo no
      estuviera ya registrado

## Bloqueantes

Ninguno propio. El único pendiente que afecta a esta autora —que DB-05 se vea en producción como se
ve en `main`— **no es suyo**: depende de la ventana de re-sync que decide el PO y ejecuta C5.

## Hallazgos para otros

- **Edgar Coronel (PO):** tres cosas. (1) DB-05 y `BUG-054` son **un solo pendiente de despliegue**,
  no dos bugs. (2) El motivo escrito para congelar el `sync` ya tiene respuesta (§3). (3) La
  colisión de `BUG-070`/`BUG-071` entre dos ramas (§4). Y una sugerencia sobre las «seis cosas»: el
  punto 1 dice *"sólo `/api/v1/health` responde sin token"*, pero `/version`, `/docs` y
  `/openapi.json` también dan 200 —a propósito, por `BUG-057` y `DEC-012`—; conviene precisarlo o
  alguien lo levantará como bug.
- **Manuel Serranía (C2):** el `0.0 %` que registraste para DB-04 aparece **también en DB-02**.
  Mismo redondeo, otro tablero.
- **Oscar Quiroz (C2):** la leyenda paginada de `BUG-064` (`◀ 1/2 ▶`) aparece **también en DB-08**,
  en el pastel «Escuelas por cobertura del driver». Cuarto tablero con el mismo síntoma.
- **Luis Téllez (C5) / PO:** si se abre la ventana de re-sync, esa sola corrida deja los tres
  pendientes: el `query_context` correcto, el layout de DB-05 y el `BUG-054` de DB-09.

## Próximos pasos

1. PR con la bitácora y este DevLog.
2. Que el PO decida sobre la ventana de re-sync con la evidencia de §3.
3. Que alguien confirme el correo del evaluador en la lista blanca de Superset (§5).
