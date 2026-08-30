---
id: DOC-CUBESPEC-DB0609
title: "Cube Specs — Contrato semántico de los cubos de DB-06 y DB-09"
owner: "Manuel Alejandro Serranía Reinada"
status: in_review
version: "1.0"
traces_up: ["DOC-SCREENSPECS", "DOC-DATAMODEL", "DEC-010", "DEC-009", "DEC-008", "US-204", "REQ-002"]
traces_down: ["US-205"]
last_reviewed: "2026-08-27"
tags: [bi, cubos, capa-semantica, dashboards, celula-2, predicciones, recomendaciones]
---

# Cube Specs — Contrato semántico de DB-06 y DB-09

> Métricas, jerarquías y granos de los cubos que alimentan **DB-06 (Predicciones)** y
> **DB-09 (Recomendaciones prescriptivas)**. Implementa **US-204** (REQ-002) — el diferenciador
> prescriptivo del proyecto.
> → [[04_UX_Design/_index]] · Fuentes canónicas: [[03_Architecture/Data_Model]] · [[04_UX_Design/Screen_Specs]]
> · Grano dual de `gold.predicciones`: [[_DevLog/2026-08-23-diana-alvarez-dec010-grano-dual-predicciones|DEC-010]]

---

## 1. Alcance y frontera de responsabilidad

| Qué | Quién | Dónde vive |
|---|---|---|
| **Modelar** métricas, jerarquías y granos (este documento) | Manuel Alejandro Serranía Reinada (C2) | `04_UX_Design/Cube_Specs_DB06_DB09.md` |
| **Materializar** los cubos en Gold (`dbt`) | Deni Garrido Fragoso (C1) · **US-113** | `dbt/` |
| **Esquema canónico** de Gold (`gold.predicciones` con grano dual) | Diana Aracely Alvarez Varela (C1) · **DEC-010** | [[03_Architecture/Data_Model]] |
| **Publicación de salidas ML** (`gold.predicciones` / `gold.recomendaciones`) | Héctor Morales Marbán (C3) · US-313 | `src/modelos/` · `15_ML_Models/Publicacion_Gold` |
| **Catálogo canónico de KPIs** | Manuel Alejandro Serranía Reinada (C2) · US-201 | [[04_UX_Design/Screen_Specs]] |
| **Capa semántica de Superset** (convención) | Manuel Alejandro Serranía Reinada (C2) · US-202 | `superset/` |

Este documento **no modifica** el esquema canónico. Donde se necesita un cambio en Gold, se registra
como **solicitud a la Célula 1** (§8), nunca como edición de [[03_Architecture/Data_Model]]
(regla 7 del vault: cambio de esquema = revisión humana explícita).

---

## 2. Reglas de modelado heredadas (no negociables)

| # | Regla | Origen |
|---|---|---|
| R1 | **Las salidas de ML se leen siempre por `JOIN`**, nunca como columna del hecho. `indice_riesgo`, `valor` (variación proyectada), `probabilidad` viven en `gold.predicciones` (`modelo = 'ML-01'`); `driver_dominante`, `recomendacion` y `prioridad` en `gold.recomendaciones`. Se unen por `cct, id_ciclo`. | [[03_Architecture/Data_Model]] §4.1 |
| R2 | **`SIN_DATO` explícito: nunca cero, nunca nulo silencioso.** Prohibido `COALESCE(<driver>, 0)`. Toda métrica de ML viaja con `cobertura_prediccion` / `cobertura_recomendacion`. El **único 0 permitido** es el componente aditivo `recomendacion_emitida` (US-113). | [[03_Architecture/Data_Model]] §1 · Screen_Specs P2 |
| R3 | **Umbral de negocio:** "escuela en riesgo" = `indice_riesgo >= 0.6` ≈ perder ~5% de matrícula. | [[15_ML_Models/Indice_Riesgo_ML01]] · ratificado 2026-08-13 |
| R4 | **Llaves:** `cct` (10 caracteres), `cve_mun` (5 dígitos INEGI = `cve_ent`(2) + municipio(3)), `id_ciclo`. | [[03_Architecture/Data_Model]] §9 |
| R5 | **Gold acotado** a `SCOPE_ENTIDADES = ["09","15","19","14"]`. El filtro ya viene aplicado desde Gold; los cubos **no** lo repiten. | [[03_Architecture/Data_Model]] §7 |
| R6 | **La escuela es la unidad mínima; jamás el alumno.** Ninguna métrica desagrega por persona. | [[03_Architecture/Data_Model]] §1 |
| R7 | **Filtros globales obligatorios:** ciclo, entidad y nivel educativo, aplicables a *ambos* tableros. | AC-002.2 ([[02_Requirements/Requirements_Detailed]]) |

### 2.1 Decisión de diseño — grano de escuela de las predicciones (DEC-010)

`gold.predicciones` tiene **grano dual** (DEC-010): una fila puede ser un **escuela** (`grano='escuela'`,
llave `cct × id_ciclo`) o un **municipio × nivel** (`grano='municipio_nivel'`, llave
`cve_mun × nivel × id_ciclo`, sin `cct`). ML-01 predice al grano de DEC-007 (`municipio × nivel`)
pero publica también el desglose por escuela cuando hay señal escolar.

**DB-06 y DB-09 leen exclusivamente el grano `escuela`.** Se une por `f.cct = p.cct` y se descartan
las filas `municipio_nivel` con el filtro explícito `(p.grano IS NULL OR p.grano = 'escuela')`
(legacy-safe: las filas históricas sin `grano` eran escuelas). Nunca se reparte una predicción de
municipio a sus escuelas: eso inventaría variación proyectada donde el modelo no la puntuó.
El costo honesto es `cobertura_prediccion = 'SIN_DATO'` donde no hay fila de escuela.

### 2.2 Decisión de diseño — componentes aditivos (DEC-008/DEC-009)

Los promedios se guardan como **numerador y denominador por separado** y la razón vive en la capa
semántica (`metrics_db06_db09.yaml`). Un promedio de promedios no es reagregable: si el usuario quita
el filtro de nivel, `SUM(suma_variacion_proyectada)/NULLIF(SUM(escuelas_con_prediccion),0)` recalcula
bien, y `AVG` precalculado mentiría. `gold.cubo_matricula` (físico, C1) ya expone
`suma_variacion_proyectada` / `escuelas_con_prediccion` al mismo grano — decidido en DEC-009.

`gold.cubo_recomendaciones` (físico, C1) ya expone `recomendacion_emitida` + `cobertura_recomendacion`
al grano `cct × id_ciclo`, con paridad validada contra `gold.recomendaciones`.

---

## 3. `db06_cubo_predicciones` — DB-06, agregación municipal (KPI-01/02/05/12/03/04)

### 3.1 Grano y llaves

| | |
|---|---|
| **Grano** | una fila por **`cve_mun` × `nivel` × `id_ciclo`** |
| **Llave primaria** | (`cve_mun`, `nivel`, `id_ciclo`) |
| **Bandea de cobertura** | `cobertura_prediccion` (`OK` / `SIN_DATO`) |
| **Alimenta** | DB-06: tiles KPI, comparación observada vs proyectada, ranking municipal de riesgo |
| **Cubo físico correspondiente** | `gold.cubo_matricula` (DEC-009: ya contiene componentes ML-01) |

### 3.2 Columnas

**Identidad y contexto:** `cve_mun`, `cve_ent`, `nombre_municipio`, `nombre_entidad`, `nivel`,
`id_ciclo`, `ciclo`, `anio_inicio`.

**Componentes observados (aditivos):** `escuelas` (`COUNT(DISTINCT cct)`), `matricula_total`,
`variacion_ponderada` (numerador de KPI-02; el cubo lo conserva como `variacion_x_matricula` =
`variacion_matricula * matricula_total`, re-exportado con el nombre canónico `variacion_ponderada`
en la frontera semántica — unidad fracción, R-3 DEC-012), `suma_completitud`
(`SUM(indice_completitud_drivers)` — numerador de KPI-05).

**Componentes ML-01 (por `LEFT JOIN`, grano escuela):**

| Columna | Tipo | Definición |
|---|---|---|
| `suma_variacion_proyectada` | float | `SUM(p.valor)` — numerador de KPI-12 |
| `escuelas_con_prediccion` | int | `COUNT(p.cct)` — denominador real de KPI-03/12 (0 cuando no hay predicción, bandera lo declara) |
| `suma_indice_riesgo` | float | `SUM(p.indice_riesgo)` — numerador de KPI-03 |
| `escuelas_en_riesgo` | int | `COUNT(*) FILTER (WHERE p.indice_riesgo >= 0.6)` — R3 |
| `cobertura_prediccion` | enum | `SIN_DATO` cuando `escuelas_con_prediccion = 0` |

---

## 4. `db06_predicciones_escuela` — DB-06, grano de detalle (distribución y ranking)

### 4.1 Grano y llaves

| | |
|---|---|
| **Grano** | una fila por **`cct` × `id_ciclo`** |
| **Llave primaria** | (`cct`, `id_ciclo`) |
| **Bandea de cobertura** | `cobertura_prediccion` |
| **Alimenta** | DB-06: distribución del riesgo proyectado, semáforo por escuela |

### 4.2 Columnas

**Identidad y contexto:** `cct`, `nombre_escuela`, `nivel`, `sostenimiento`, `cve_ent`,
`nombre_entidad`, `cve_mun`, `nombre_municipio`, `id_ciclo`, `ciclo`, `anio_inicio`.

**Observadas:** `matricula_total`, `variacion_matricula`, `variacion_ponderada`
(numerador de KPI-02 = `variacion_matricula * matricula_total`, unidad fracción — R-3 DEC-012),
`indice_completitud_drivers`.

**ML-01 (por `LEFT JOIN`, grano escuela):** `indice_riesgo`, `variacion_proyectada` (`p.valor`),
`probabilidad`, `en_riesgo` (bool | `NULL` — `NULL` si no hay predicción, **nunca `false`**),
`rango_riesgo` (cubeta pre-calculada: `0.00 - 0.19`, `0.20 - 0.39`, `0.40 - 0.59`, `0.60 - 0.79`,
`0.80 - 1.00`; `NULL` si no hay predicción), `cobertura_prediccion`.

---

## 5. `db09_cubo_recomendaciones` — DB-09, el diferenciador prescriptivo

### 5.1 Grano y llaves

| | |
|---|---|
| **Grano** | una fila por **`cct` × `id_ciclo`** |
| **Llave primaria** | (`cct`, `id_ciclo`) |
| **Banderas de cobertura** | `cobertura_recomendacion`, `cobertura_prediccion` |
| **Alimenta** | DB-09: KPI-11 por prioridad, KPI-07 por driver, tabla "Escuelas a intervenir" |
| **Cubo físico correspondiente** | `gold.cubo_recomendaciones` (US-113) |

### 5.2 Columnas

El dataset virtual espeja el cubo físico y **añade** el riesgo como contexto (KPIs globales AC-002.5):

**Identidad:** `cct`, `nombre_escuela`, `nivel`, `sostenimiento`, `cve_ent`, `nombre_entidad`,
`cve_mun`, `nombre_municipio`, `id_ciclo`, `ciclo`, `anio_inicio`.

**Observadas:** `matricula_total`, `indice_completitud_drivers`.

**Recomendación (por `LEFT JOIN` a `gold.recomendaciones`):**

| Columna | Tipo | Nota |
|---|---|---|
| `driver_dominante` | str (`D1`…`D6`) \| `'SIN_DATO'` | Etiqueta de categoría (permitido por R2: etiquetar, no rellenar métrica) |
| `nombre_driver` | str \| `'SIN_DATO'` | Etiqueta legible desde `dim_driver` |
| `recomendacion` | str | Texto prescriptivo modelo |
| `prioridad` | str (`ALTA`/`MEDIA`/`BAJA`) | — |
| `recomendacion_emitida` | int 0/1 | Componente aditivo (único 0 permitido, paridad validada en US-113) |
| `cobertura_recomendacion` | enum | `SIN_DATO` cuando no hay fila de recomendación |

**Contexto de riesgo (por `LEFT JOIN` a `gold.predicciones`, `modelo='ML-01'`, grano escuela):**
`indice_riesgo`, `en_riesgo`, `cobertura_prediccion`. Permite el tile KPI-04 y colorear la tabla
de intervención sin un segundo dataset.

---

## 6. Mapeo a los KPIs canónicos

Las fórmulas **no se duplican**: este documento referencia el catálogo de [[04_UX_Design/Screen_Specs]]
§4 y solo precalcula sus componentes.

| Métrica del cubo | KPI canónico | Cubo |
|---|---|---|
| `matricula_total` | KPI-01 | `db06_cubo_predicciones`, `db06_predicciones_escuela`, `db09_cubo_recomendaciones` |
| `variacion_ponderada_pct` | KPI-02 | `db06_cubo_predicciones` |
| `indice_riesgo_promedio` | KPI-03 | `db06_cubo_predicciones` |
| `escuelas_en_riesgo` | KPI-04 | `db06_cubo_predicciones`, `db09_cubo_recomendaciones` |
| `completitud_promedio` | KPI-05 | `db06_cubo_predicciones` |
| `escuelas` por `nombre_driver` | KPI-07 | `db09_cubo_recomendaciones` |
| `recomendaciones_emitidas` / por prioridad | KPI-11 | `db09_cubo_recomendaciones` |
| `variacion_proyectada_promedio` | KPI-12 | `db06_cubo_predicciones`, `db06_predicciones_escuela` |

> KPI-12 y KPI-03/04 dividen entre `escuelas_con_prediccion` (denominador visible en el YAML), nunca
> entre el total de escuelas: decir "media de 8%" cuando solo el 30% fue proyectada inventaría
> cobertura inexistente (misma convención que KPI-03/04 en DB-02).

---

## 7. SQL de referencia

El SQL vive en `superset/semantic/` para poder usarse también como **dataset virtual** de Superset
mientras los cubos físicos no estén cargados:

- `superset/semantic/db06_cubo_predicciones.sql`
- `superset/semantic/db06_predicciones_escuela.sql`
- `superset/semantic/db09_cubo_recomendaciones.sql`

Son **propuestas de implementación**, no código de producción: la materialización (`dbt`, índices,
estrategia de refresco) es decisión de la Célula 1 en US-113/US-114. Cuando el cubo físico exista, el
SQL del dataset virtual se reduce a `SELECT * FROM gold.<cubo>`:

| Dataset virtual | Cubo físico futuro |
|---|---|
| `db06_cubo_predicciones` | `gold.cubo_matricula` (ya lo contiene, DEC-009) |
| `db09_cubo_recomendaciones` | `gold.cubo_recomendaciones` |

`db06_predicciones_escuela` no tiene cubo físico declarado (grano del hecho, sin agregar), igual que
`db02_puntos_escuela`.

---

## 8. Contrato de dependencias

| Columna(s) | Depende de | Historia | Estado hoy (27-ago) |
|---|---|---|---|
| Hecho, dimensiones y drivers | Célula 1 · Gold | US-103, US-112, US-113 | ✅ Materializado |
| `gold.predicciones` (grano dual) | Célula 3 · job batch | US-313 · DEC-010 | 🟡 En progreso (mock local MOCK-US203 mientras tanto) |
| `gold.recomendaciones` + `dim_driver` | Célula 3 | US-313 | 🟡 En progreso (mock local MOCK-US203) |
| Cubos `cubo_matricula`/`cubo_recomendaciones` | Célula 1 | US-113 | 🔵 En revisión |

**Comportamiento mientras las dependencias no llegan:** los bloques de predicción y recomendación
muestran **"sin dato disponible"** vía `cobertura_prediccion` / `cobertura_recomendacion`. El tablero
no se rompe ni miente con ceros (R2). La validación de datos en vivo
(`superset/sync_semantic_layer.py --validar-datos`) queda pendiente de levantar Docker + materializar
Gold (block local 27-ago).

---

## 9. Trazabilidad

- **Implementa:** US-204 (REQ-002)
- **Consume:** [[03_Architecture/Data_Model]] §4 · [[04_UX_Design/Screen_Specs]] §4 (KPI-01…05, 07, 11, 12) ·
  [[15_ML_Models/Publicacion_Gold]] · DEC-010 (grano dual) · DEC-009/DEC-008 (componentes aditivos)
- **Alimenta:** US-205 (integración) · US-214a (filtros cruzados y drill-down DB-06→DB-09)
- **Insumo para:** US-113 (cubos físicos, Célula 1)
- **Sustenta AC:** AC-002.2, AC-002.4, AC-002.5, AC-002.6