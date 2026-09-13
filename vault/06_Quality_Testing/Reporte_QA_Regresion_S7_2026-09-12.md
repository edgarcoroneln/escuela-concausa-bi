---
id: DOC-QA-REPORTE-REGRESION-S7-20260912
title: "Reporte de regresión completa S7 — para la junta del 12-sep"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["vault/06_Quality_Testing/QA_team_documentation/Plan_QA_Exhaustivo_S7", "vault/06_Quality_Testing/QA_Logs/2026-09-12-edgar-coronel-qa-regresion-completa-s7", "US-621", "REQ-004", "REQ-005"]
traces_down: ["vault/06_Quality_Testing/Bug_Register"]
last_reviewed: "2026-09-12"
tags: [qa, reporte, junta, s7, freeze]
---

# Reporte de regresión completa — S7, para la junta de la tarde del 12-sep

> Ordenado por **impacto sobre el freeze de mañana 20:00**, no por severidad técnica en abstracto.
> Todo lo de este reporte es de una corrida **local** (no contra la URL pública) — cada punto dice
> explícitamente si necesita confirmación en otro ambiente antes de actuar.
> → [[vault/06_Quality_Testing/QA_Logs/2026-09-12-edgar-coronel-qa-regresion-completa-s7]] (bitácora completa, 28 casos) · [[vault/06_Quality_Testing/Bug_Register]] · [[vault/06_Quality_Testing/QA_team_documentation/Plan_QA_Exhaustivo_S7]]

## El estado, en una tabla

| Hallazgo | Severidad | Confirmado en | Dueño propuesto |
|---|---|---|---|
| **`BUG-077`** — `/municipios` responde 500 para el 97% de municipios | **critical** | Local (dbt test + curl) | Diana Alvarez (dato) + Christian Ruiz (código) |
| `cubo_riesgo_territorial` desalineado con `fact_escuela_ciclo`+`predicciones` (5 filas) | medium, sin confirmar | Local (`dbt test`) | Diana Alvarez — confirmar con `dbt run` completo |
| MLflow local sin ningún run (`RISK-011`/`DEC-027`) | alto, ya conocido | Local, segundo entorno independiente | Estefany Hernández |
| `gold.recomendaciones` local sin `shap_d1..shap_d6` → 503 en `/predicciones` | bajo, probable solo local | Local (un solo ambiente: el del PO) | Nadie todavía — confirmar antes de escalar |
| Sin suite automatizada de regresión de frontend | conocido desde antes | — | Ver `Plan_QA_Exhaustivo_S7.md` §6 |

## Prioridad 1 — confirmar hoy, antes del freeze

### `BUG-077`: si producción tiene el mismo hueco, los municipios están rotos

**Lo que se verificó, con evidencia reproducible:**

```
select count(*), count(poblacion), count(nombre_entidad) from gold.dim_municipio;
-- 317 | 10 | 10   (local)

curl http://localhost:8000/api/v1/municipios?size=5
-- {"error":"internal_error", ...}  HTTP 500

curl http://localhost:8000/api/v1/municipios/14113
-- {"error":"internal_error", ...}  HTTP 500
```

`MunicipioOut.nombre_entidad` (`src/api/schemas.py:196`) es `StrictStr` — obligatorio, sin `None`.
`gold.dim_municipio.nombre_entidad` sale de un `LEFT JOIN` contra CONEVAL (`dbt/models/gold/dim_municipio.sql`),
bajo el supuesto —escrito en el propio modelo— de que CONEVAL cubre el 100% de los municipios del
país. En el Postgres local **no lo cubre**: 307 de 317 municipios quedan con `nombre_entidad` y
`poblacion` nulos, y Pydantic revienta al serializar esa fila (`500`, no un `SIN_DATO` degradado).

**Lo importante para la junta, más que el bug en sí:** el equipo **ya había anticipado exactamente
este modo de falla** — existe un `data_test` de dbt (`not_null_dim_municipio_nombre_entidad`)
diseñado para fallar ruidosamente si esto pasa. Y sí falla (verificado, `dbt test --select gold`:
8 `ERROR`). **El hueco real es que nada ejecuta esa prueba en ningún punto del pipeline**: los
workflows de `.github/**` solo corren `dbt parse` (sintaxis), nunca `dbt test` ni `dbt run`. La
guarda existe y está bien diseñada; simplemente nunca se disparó.

**Lo que falta decidir hoy en la junta:**
1. ¿El Postgres compartido/producción tiene el mismo hueco de cobertura CONEVAL, o es exclusivo del
   volumen local del PO? — **Diana Alvarez** es quien puede confirmarlo en minutos.
2. Si sí lo tiene: es un defecto que rompe una superficie pública (`/municipios`) y debería tratarse
   como bloqueante del freeze, no como deuda declarada.
3. Independientemente de la respuesta anterior: `nombre_entidad`/`poblacion` en `MunicipioOut`
   deberían aceptar `None` con el mismo criterio `SIN_DATO` que ya usan otros campos del mismo
   esquema (`pobreza_pct`, `indice_rezago_social`) — hoy es el único campo de ese modelo que no
   degrada. Es un cambio de una línea en `src/api/schemas.py`, propuesto para **Christian Ruiz**.

## Prioridad 2 — confirmar esta semana, no bloquea el freeze si se declara

### `cubo_riesgo_territorial_ml01_parity`: 5 combinaciones no cuadran

`dbt test` encontró 5 filas (`cve_mun × nivel × id_ciclo`) donde el cubo materializado
`gold.cubo_riesgo_territorial` no coincide con la suma directa de `fact_escuela_ciclo` +
`predicciones`. **No se registró como bug todavía**: es indistinguible, sin más investigación, de
que mi Postgres local no pasó por un `dbt run` completo y en orden (en vez de una carga parcial).
**Pedido a Diana Alvarez:** correr `dbt run --select cubo_riesgo_territorial+ dim_municipio+` en un
ambiente limpio y repetir `dbt test` — si sigue fallando ahí, sí es `BUG-###` nuevo.

### `RISK-011` / `DEC-027`: MLflow vacío, confirmado por segunda vez

Ya lo había reportado Deni Garrido; esta corrida lo confirma **desde un ambiente independiente**
(el del PO, no el de ella): `http://localhost:5001` responde, pero el backend de MLflow no tiene
ningún run registrado, solo el experimento `Default`. Dos veces el mismo resultado en dos máquinas
distintas sube la confianza de que el `run_id` histórico de `DEC-027` genuinamente no es recuperable
con un levantamiento estándar del stack — probablemente porque el entrenamiento original corrió en
un entorno que ya no existe. **Pedido a Estefany Hernández:** decidir si se re-entrena para generar
un `run_id` nuevo y verificable, en vez de seguir intentando "recuperar" el viejo.

## Prioridad 3 — deuda declarada, no urgente

- **`gold.recomendaciones` local sin `shap_d1..shap_d6`** (503 en `/predicciones/{cct}`): con muy
  alta probabilidad es solo el volumen de Docker del PO, creado antes de que esas columnas se
  agregaran al modelo. No se escala hasta que alguien más lo reproduzca (o no) en su propio ambiente.
- **Sin suite Playwright automatizada**: ya cubierto en
  [[vault/06_Quality_Testing/QA_team_documentation/Plan_QA_Exhaustivo_S7]] §6 — deuda para la
  siguiente entrega, no de este freeze.

## Lo que sí quedó verificado en verde, y vale decirlo en la junta

- **1241 de 1245 pruebas de backend pasan** (4 `skip` conocidos), incluidas las 66 específicas de
  ML-03/Gold.
- **Cero excepciones de JavaScript no controladas** en las 9 rutas del frontend y las 5 pestañas del
  expediente de escuela — el sitio no se cae en ningún punto navegado.
- **El manejo de errores del contrato es sólido en general**: `422` en validación, `404` en no
  encontrado, `401` en no autenticado — todos correctos y probados con casos concretos. `BUG-077` es
  la excepción puntual, no el patrón.
- **Las 4 pantallas "en construcción" degradan exactamente como se diseñaron**: explican el gap real
  de contrato en vez de fallar en silencio o inventar dato.

## Plan de remediación — quién corrige qué

| Acción | Dueño | Urgencia |
|---|---|---|
| Confirmar si producción/ambiente compartido tiene el hueco de cobertura CONEVAL de `BUG-077` | **Diana Alvarez** | Hoy, antes de decidir si bloquea el freeze |
| Si se confirma: corregir cobertura de `dim_municipio` (dbt) o decidir mitigación | **Diana Alvarez**, con el PO | Antes del freeze si aplica |
| Cambiar `nombre_entidad`/`poblacion` de `MunicipioOut` a degradar `SIN_DATO` en vez de `500` | **Christian Ruiz** | Antes del freeze — cambio pequeño, alto impacto |
| Agregar caso de prueba con municipio `nombre_entidad=None` a `test_api_contract.py` | **Christian Ruiz** | Junto con el fix anterior |
| Repetir `dbt test` sobre un `dbt run` limpio para confirmar/descartar el hallazgo de `cubo_riesgo_territorial` | **Diana Alvarez** | Esta semana |
| Decidir si ML-03 se re-entrena para un `run_id` verificable (en vez de recuperar el histórico) | **Estefany Hernández** | Esta semana, ligado a `DEC-027` |
| Reproducir (o descartar) el hueco de `shap_d1..d6` en un ambiente que no sea el del PO | Cualquiera del Equipo 4/6 con Docker local | Esta semana, no bloqueante |
| Considerar agregar `dbt test` (no solo `dbt parse`) a algún workflow de CI, aunque sea informativo | **Luis Téllez**, decisión del PO | Post-freeze — es la causa raíz de que `BUG-077` no se cazara antes |
