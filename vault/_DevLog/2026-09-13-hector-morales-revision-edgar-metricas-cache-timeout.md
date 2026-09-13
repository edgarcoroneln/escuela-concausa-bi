---
project: "FARO"
date: "2026-09-13"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1.5h"
touches: ["US-601", "REQ-002", "REQ-004", "DEC-027", "US-324"]
tags: [devlog, us-601, componentes, api, rendimiento, equipo-1]
---

# DevLog — 2026-09-13 — Los tres puntos de la revisión de Edgar: métricas, causa del fallo y carga

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

Edgar Coronel revisó el PR #350 a fondo —corrió la suite, `ruff`, `vault_lint` y el build, y
levantó API y front en local con `AUTH_LECTURA_PUBLICA=false`— y pidió tres cosas antes de
aprobar. Las tres aplicadas. También confirmó que **el «tercer ajuste» pendiente desde ayer era el
ok de Diana sobre `App.jsx`**, que ya llegó.

## 1. Las métricas de ML estaban desactualizadas

La tabla decía de ML-01: *«MAE < 0.03, RMSE < 0.05 — provienen de datos sintéticos, la corrida con
datos reales está bloqueada por un error interno de scikit-learn»*. Las dos afirmaciones dejaron de
ser ciertas el 5 de septiembre. **Es lo que va a ver el profesor.**

Edgar pidió confirmarlas con Estefany. No pude, así que las **crucé contra las fuentes canónicas**:
`Publicacion_Gold.md §9` (estado `approved`, con la corrida real por dos vías independientes que
coinciden) y `DEC-027`.

| | Antes | Ahora | Fuente |
|---|---|---|---|
| ML-01 | «MAE < 0.03, sintéticos, bloqueado» | **MAE 0.1415**, no alcanza su umbral (0.03, 4.7×) pero supera el baseline por 11.04 % | `Publicacion_Gold §9` |
| ML-02 | «F1 ≥ 0.60» | **F1 macro 0.8333**, con la salvedad del target proxy | `Publicacion_Gold §9` |
| ML-03 | «Silhouette 0.1086, requiere iteración» | **Silhouette 0.4621, `k=2`**, y estado **«no operativo esta entrega»** | `DEC-027` |

Se cambió `fuente` para que apunte a esos documentos en vez de a los Model Cards, y la advertencia
ahora dice lo incómodo: **las fichas están más atrasadas que esta tabla**, la de ML-01 sigue
afirmando dos cosas falsas, y actualizarlas es de su dueño (`US-324`). Se añadió una nota
explicando por qué ML-03 dice «no operativo» y no un estado de avance: `DEC-027` lo declara deuda
explícita — sin Gold, sin endpoint, sin panel — y nadie debe presentarlo como productivo.

**Pendiente:** el 0.4621 de ML-03 es el único que no pude cruzar con una segunda fuente. Falta que
Estefany lo ratifique.

## 2. «No disponible» no es lo mismo que «no existe»

`_contar()` atrapaba todo con `except DBAPIError` y devolvía *«Tabla no materializada todavía»*. Con
la base caída eso **afirma algo sobre el esquema cuando el problema es la conexión** — exactamente
el tipo de invención que la política `SIN_DATO` existe para evitar: no saber por qué falta un dato
no autoriza a inventar la causa.

Ahora `OperationalError` (base inalcanzable o consulta cancelada) se distingue del resto de
`DBAPIError` (tabla o esquema ausente), y `hubo_error_de_conexion()` deja que la sección **declare
la causa una vez arriba** en vez de repetir treinta notas equivocadas.

## 3. Carga: ~30 `COUNT(*)` por visita en un endpoint público

- **`TTLCache` de 60 s.** El contenido cambia cuando corre el pipeline —minutos u horas—, no entre
  dos recargas, así que el TTL no le quita frescura útil a nadie.
- **`SET LOCAL statement_timeout` de 5 s** por consulta. `LOCAL` y no `SET` a secas: el efecto muere
  con la transacción y no se lleva el timeout al motor compartido cuando la conexión vuelve al pool.
- Los tres valores viven en `Settings`, no escritos a mano.

**Un resultado producido con la base caída no se cachea.** Si se guardara, la página seguiría
diciendo «no disponible» hasta que venciera el TTL aunque Postgres ya hubiera vuelto. Mismo criterio
que `cache_predicciones.py`, que nunca cachea errores.

## 4. Sobre el Gold, con la respuesta de Diana

Diana confirmó que el autoritativo es **producción** y que el 0.3744 de este ambiente **no es una
variación de esa base sino otra base**, probablemente por un target de dbt desalineado
(`faro_gold` en vez de `faro`).

Dos consecuencias, las dos importantes:

- **El republish no lo puedo correr**: necesita credenciales de producción que no tengo. Es de C5 o
  de quien administre Cloud SQL.
- **Su criterio de cierre es mejor que el que yo había escrito.** Yo comparaba el corte contra un
  máximo declarado como dato; ella pide comprobar contra producción que exista **al menos una fila
  `alta`** y que **ese conteo coincida con `escuelas_en_riesgo` de `/kpis`**. Es más fuerte: ata las
  dos superficies que hoy cuentan cosas distintas con el mismo nombre. La guarda de
  `dec026-pendiente` se ajustará a ese criterio cuando se abra ese PR.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Modificados:** `src/api/v1/about.py`, `src/api/repositorio_about.py`, `src/api/config.py`,
  `api/openapi.v1.json` (regenerado con su script)
- **Creado:** `tests/test_repositorio_about.py`
- **Decisiones autónomas del agente:** cachear la lista completa bajo una sola clave en vez de por
  capa; no cachear resultados producidos con la base caída; tolerar en `_hubo_error_de_conexion()`
  los dobles de prueba que no implementen el método nuevo, para no obligarlos a crecer.
- **Correcciones manuales:** ninguna.
- **Prompt inicial:** nota de revisión de Edgar Coronel.

## Seguridad / calidad

- [x] `pytest tests/ -q` → **1299 passed, 10 skipped** (eran 1287; +12)
- [x] `ruff` limpio · sin dependencias nuevas (`cachetools` ya era del proyecto)
- [x] `vault_lint`: 7 bloqueantes, **todos duplicados de iCloud sin rastrear**. Esta vez se
      revisaron **todas** las categorías, no una — ayer ese atajo dejó pasar un link roto al CI
- [x] Verificado en vivo: las tres filas de ML salen con las cifras nuevas

**Las 12 pruebas nuevas se falsificaron**, que es lo único que demuestra que una guarda sirve:

| Defecto reintroducido | Reprueba |
|---|---|
| Sin distinguir la causa del fallo | `test_base_caida_no_se_reporta_como_tabla_inexistente` |
| Sin caché | `test_la_segunda_visita_no_vuelve_a_consultar_postgres` |

## Bloqueantes

- **El gate de propiedad**, sin cambio.
- **`DEC-027` sin ratificar por Estefany** en lo que toca al 0.4621 de ML-03.
- **El republish de `DEC-026`** necesita credenciales de producción.

## Próximos pasos

- Corregir en la descripción del PR dos imprecisiones que Edgar señaló: el conteo de `vault_lint`
  (decía 10, son 7, y la casilla afirmaba «Vault limpio» sin matizar que los bloqueantes son copias
  locales que el CI no ve) y la comparación 0.3744 / 0.5717, que con la aclaración de Diana ya no
  se describe como una diferencia de la misma base.
- Que Estefany ratifique el Silhouette de ML-03.
