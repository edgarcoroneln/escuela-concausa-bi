---
id: DOC-CUBESPEC-DB0304
title: "Cube Specs — Contrato semántico de los cubos de DB-03 y DB-04"
owner: "Marina García del Buey"
status: approved
version: "1.1"
traces_up: ["DOC-SCREENSPECS", "DOC-DATAMODEL", "US-211a", "US-214a", "REQ-002"]
traces_down: ["US-212", "US-214a", "US-215a"]
last_reviewed: "2026-09-03"
tags: [bi, cubos, capa-semantica, dashboards, celula-2]
---

# Cube Specs — Contrato semántico de DB-03 y DB-04

> Métricas, jerarquías y granos de los cubos que alimentan **DB-03 (Ficha de escuela)** y
> **DB-04 (Comparador de municipios)**. Implementa **US-211a** (REQ-002) y es el **insumo formal
> para US-113** (construcción de los cubos, Célula 1).
> → [[vault/04_UX_Design/_index]] · Fuentes canónicas: [[vault/03_Architecture/Data_Model]] · [[vault/04_UX_Design/Screen_Specs]]

---

## 1. Alcance y frontera de responsabilidad

| Qué | Quién | Dónde vive |
|---|---|---|
| **Modelar** métricas, jerarquías y granos (este documento) | Marina García del Buey (C2) | `vault/04_UX_Design/Cube_Specs_DB03_DB04.md` |
| **Materializar** los cubos en Gold (`dbt`) | Deni Garrido Fragoso (C1) · **US-113** | `dbt/` |
| **Esquema canónico** de Gold | Diana Aracely Alvarez Varela (C1) | [[vault/03_Architecture/Data_Model]] |
| **Catálogo canónico de KPIs** | Manuel Alejandro Serranía Reinada (C2) · US-201 | [[vault/04_UX_Design/Screen_Specs]] |
| **Capa semántica de Superset** (convención) | Manuel Alejandro Serranía Reinada (C2) · US-202 | `superset/` |
| **Datasets y métricas de DB-03/DB-04** | Marina García del Buey (C2) | `superset/semantic/` |

Este documento **no modifica** el esquema canónico. Donde se necesita un cambio en Gold, se registra
como **solicitud a la Célula 1** (§8), nunca como edición de [[vault/03_Architecture/Data_Model]]
(regla 7 del vault: cambio de esquema = revisión humana explícita).

---

## 2. Reglas de modelado heredadas (no negociables)

| # | Regla | Origen |
|---|---|---|
| R1 | **Las salidas de ML se leen siempre por `JOIN`**, nunca como columna del hecho. `indice_riesgo` vive en `gold.predicciones` (`modelo = 'ML-01'`); `driver_dominante`, `recomendacion` y `prioridad` en `gold.recomendaciones`. Se unen por `cct, id_ciclo`. | [[vault/03_Architecture/Data_Model]] §4.1 · [[vault/_DevLog/2026-08-13-manuel-serrania-screenspecs-cubos]] |
| R2 | **`SIN_DATO` explícito: nunca cero, nunca nulo silencioso.** Prohibido `COALESCE(<driver>, 0)`. Toda métrica de driver viaja con su bandera `d#_cobertura`. | [[vault/03_Architecture/Data_Model]] §1 · Screen_Specs P2 |
| R3 | **Umbral de negocio:** "escuela en riesgo" = `indice_riesgo >= 0.6` ≈ perder ~5% de matrícula. | [[vault/15_ML_Models/Indice_Riesgo_ML01]] · ratificado 2026-08-13 |
| R4 | **Llaves:** `cct` (10 caracteres), `cve_mun` (5 dígitos INEGI = `cve_ent`(2) + municipio(3)), `id_ciclo`. | [[vault/03_Architecture/Data_Model]] §9 |
| R5 | **Gold acotado** a `SCOPE_ENTIDADES = ["09","15","19","14"]`. El filtro ya viene aplicado desde Gold; los cubos **no** lo repiten. | [[vault/03_Architecture/Data_Model]] §7 |
| R6 | **La escuela es la unidad mínima; jamás el alumno.** Ninguna métrica desagrega por persona. | [[vault/03_Architecture/Data_Model]] §1 |
| R7 | **Filtros globales obligatorios:** ciclo, entidad y nivel educativo, aplicables a *ambos* tableros. | AC-002.2 ([[vault/02_Requirements/Requirements_Detailed]]) |

### 2.1 Decisión de diseño: promedios que **excluyen** `SIN_DATO`

Un promedio de driver **nunca** se calcula sobre el total de escuelas: se calcula sobre las escuelas
con cobertura `OK` y se publica junto al **denominador real** (`escuelas_con_d#`). Promediar tratando
`SIN_DATO` como cero afirmaría "aquí no hay problema" justo donde el Estado no está midiendo — que es
el hallazgo que el proyecto quiere mostrar, no esconder.

### 2.2 Decisión de diseño: `LEFT JOIN` a las salidas de ML

Los KPI agregados del catálogo de Manuel (KPI-03, KPI-04, KPI-10) usan `JOIN` interno porque miden
poblaciones donde la predicción existe. **En DB-03 el `JOIN` debe ser `LEFT`**: la ficha de una escuela
tiene que renderizarse aunque el modelo todavía no la haya puntuado (hoy `gold.predicciones` ni existe;
llega en S4). Con `JOIN` interno, la escuela desaparecería del tablero sin explicación — un nulo
silencioso a nivel de fila, que es exactamente lo que R2 prohíbe.

Por eso ambos cubos exponen `cobertura_prediccion` y `cobertura_recomendacion` con valores
`OK` / `SIN_DATO`, y la ficha muestra literalmente **"sin dato disponible"** en esos bloques.

> ✅ **Ratificado por [[vault/04_UX_Design/Screen_Specs|Manuel]] el 2026-08-15** (US-201): el catálogo canónico
> adoptó el `LEFT JOIN` en el grano de escuela y lo documenta en KPI-17 y KPI-18. Este documento no cambia la
> regla R1 (la lectura sigue siendo por `JOIN`), solo fija el **tipo de `JOIN`** para el grano de
> escuela.

---

## 3. `gold.cubo_escuela_360` — DB-03 Ficha de escuela

### 3.1 Grano y llaves

| | |
|---|---|
| **Grano** | una fila por **`cct` × `id_ciclo`** |
| **Llave primaria** | (`cct`, `id_ciclo`) |
| **Cardinalidad esperada** | escuelas de las 4 entidades × ciclos disponibles |
| **Banderas de cobertura** | `d1_cobertura`…`d6_cobertura`, `cobertura_prediccion`, `cobertura_recomendacion` |
| **Alimenta** | DB-03 (AC-002.4: perfil, drivers, predicción y recomendación por CCT) |

### 3.2 Columnas del cubo

**Identidad y contexto** (dimensiones conformadas, no se agregan):

| Columna | Tipo | Origen | Uso en DB-03 |
|---|---|---|---|
| `cct` | str(10) | `fact_escuela_ciclo` | Llave de drill-down y de búsqueda |
| `id_ciclo` / `ciclo` | str | `dim_tiempo` | Filtro global de ciclo · eje de la serie de tiempo |
| `anio_inicio` | int | `dim_tiempo` | Orden cronológico de la serie |
| `nombre_escuela` | str | `dim_escuela.nombre` | Encabezado de la ficha |
| `nivel` | str | `dim_escuela` | **Filtro global de nivel** |
| `sostenimiento` | str | `dim_escuela` | Segmentación |
| `latitud` / `longitud` | float | `dim_escuela` | Mini-mapa de ubicación |
| `cve_ent` | str(2) | `dim_escuela` | **Filtro global de entidad** |
| `cve_mun` | str(5) | `fact_escuela_ciclo` | Salto a DB-04 |
| `nombre_municipio` / `nombre_entidad` | str | `dim_municipio` | Migas de pan de la jerarquía |

**Métricas observadas** (aditivas salvo nota):

| Columna | Tipo | Agregación | Nota |
|---|---|---|---|
| `matricula_total` | int | `SUM` | Serie de tiempo del tablero |
| `variacion_matricula` | float | **no aditiva** — ponderar por matrícula | Ver métrica derivada §3.4 |
| `indice_completitud_drivers` | float[0,1] | `AVG` | Cuántos de los 6 drivers se observaron |

**Drivers** (uno por cada D1…D6):

| Columna | Tipo | Nota |
|---|---|---|
| `d1`…`d6` | float \| `NULL` | Score del driver. **`NULL` solo cuando la bandera dice `SIN_DATO`** |
| `d1_cobertura`…`d6_cobertura` | enum `OK`/`SIN_DATO` | **Fuente de verdad de la cobertura.** El tablero lee esta columna, no el nulo |

**Infraestructura CEMABE** (perfil de la escuela, D3/D4):

`agua`, `drenaje`, `electricidad`, `sanitarios`, `internet`, `computadoras` — desde `dim_escuela`.
Se muestran como *chips* con tres estados: **sí / no / sin dato**. Nunca "no" cuando es `SIN_DATO`.

**Salidas de modelos** (`LEFT JOIN`, §2.2):

| Columna | Tipo | Origen | Nota |
|---|---|---|---|
| `indice_riesgo` | float[0,1] \| `NULL` | `gold.predicciones` (`ML-01`) | R1 |
| `en_riesgo` | bool \| `NULL` | derivado | `indice_riesgo >= 0.6` (R3). `NULL` si no hay predicción — **nunca `false`** |
| `variacion_proyectada` | float \| `NULL` | `gold.predicciones.valor` | Variación cruda del modelo |
| `probabilidad` | float \| `NULL` | `gold.predicciones` | — |
| `cobertura_prediccion` | enum `OK`/`SIN_DATO` | derivado | Gobierna qué muestra el bloque de predicción |
| `driver_dominante` | str (`D1`…`D6`) \| `NULL` | `gold.recomendaciones` | R1 |
| `nombre_driver` | str \| `NULL` | `dim_driver` | Etiqueta legible del driver dominante |
| `recomendacion` | str \| `NULL` | `gold.recomendaciones` | El diferenciador prescriptivo del proyecto |
| `prioridad` | str \| `NULL` | `gold.recomendaciones` | — |
| `cobertura_recomendacion` | enum `OK`/`SIN_DATO` | derivado | Gobierna el bloque de recomendación |

### 3.3 Jerarquías y drill-down

```
Entidad (cve_ent)
   └── Municipio (cve_mun)
         └── Escuela (cct)                    ← grano del cubo
               └── Driver (D1…D6)             ← dimensión transversal, dentro de la ficha
```

| Ruta | Desde | Hacia | Llave |
|---|---|---|---|
| Entrada | DB-01 / DB-02 | **DB-03** | `cct` |
| Lateral | **DB-03** | DB-04 | `cve_mun` de la escuela |
| Salida | **DB-03** | DB-06 / DB-09 | `cct` + `id_ciclo` |

Las rutas se implementan en **US-214a**; aquí solo se fija la llave que las hace posibles.
Coinciden con la tabla de navegación cruzada de [[vault/04_UX_Design/Screen_Specs]] §3.

### 3.4 Métricas derivadas (capa semántica de Superset)

| Métrica | Expresión | Formato |
|---|---|---|
| `matricula_total` | `SUM(matricula_total)` | entero |
| `variacion_ponderada_pct` | `SUM(matricula_total) / NULLIF(SUM(matricula_ciclo_anterior), 0) - 1` | % 1 decimal |
| `completitud_promedio` | `AVG(indice_completitud_drivers)` | % 0 decimales |
| `indice_riesgo` | `AVG(indice_riesgo)` | 0.00 |
| `escuelas_en_riesgo` | `COUNT(*) FILTER (WHERE en_riesgo)` | entero |
| `drivers_sin_dato` | `6 - ROUND(indice_completitud_drivers * 6)` | entero |

> En el grano de una sola escuela estas agregaciones devuelven el valor de la fila; se declaran así
> para que los mismos objetos sirvan cuando DB-03 muestre varias escuelas de un municipio.

---

## 4. `gold.cubo_comparador_municipio` — DB-04 Comparador de municipios

### 4.1 Grano y llaves

| | |
|---|---|
| **Grano propuesto** | una fila por **`cve_mun` × `nivel` × `id_ciclo`** |
| **Grano en el esquema canónico hoy** | `municipio × ciclo` ([[vault/03_Architecture/Data_Model]] §4.3) |
| **Llave primaria** | (`cve_mun`, `nivel`, `id_ciclo`) |
| **Banderas de cobertura** | `escuelas_con_d1`…`escuelas_con_d6`, `cobertura_riesgo` |
| **Alimenta** | DB-04 (comparación lado a lado de municipios) |

> 🔴 **Cambio de grano solicitado a la Célula 1 — ver §8.1.** El grano canónico (`municipio × ciclo`)
> **no puede satisfacer AC-002.2**: si el cubo se pre-agrega sin `nivel`, el filtro global de nivel
> educativo no tiene sobre qué operar en DB-04. La solución estándar es bajar un nivel el grano y
> **reagregarlo con métricas aditivas** (§4.3).

### 4.2 Columnas del cubo

**Identidad y contexto:**

| Columna | Tipo | Origen |
|---|---|---|
| `cve_mun` | str(5) | `fact_escuela_ciclo` |
| `cve_ent` | str(2) | `dim_municipio` |
| `nombre_municipio` / `nombre_entidad` | str | `dim_municipio` |
| `nivel` | str | `dim_escuela` |
| `id_ciclo` / `ciclo` / `anio_inicio` | str/int | `dim_tiempo` |

**Contexto socioeconómico** (KPI-14, constante dentro del municipio × ciclo):

`poblacion`, `pobreza_pct`, `grado_rezago`, `indice_rezago_social` — desde `dim_municipio`.

**Componentes aditivos** (§4.3 explica por qué son componentes y no promedios):

| Columna | Tipo | Definición |
|---|---|---|
| `escuelas` | int | `COUNT(DISTINCT cct)` |
| `matricula_total` | int | `SUM(matricula_total)` |
| `suma_matricula_anterior` | bigint | `SUM(matricula_ciclo_anterior)` — **denominador** de la variación. Nunca guardar el producto ya ponderado: ver BUG-031 |
| `suma_completitud` | float | `SUM(indice_completitud_drivers)` |
| `suma_d1`…`suma_d6` | float | `SUM(d#)` **solo sobre `d#_cobertura = 'OK'`** |
| `escuelas_con_d1`…`escuelas_con_d6` | int | Denominador real de cada driver |
| `suma_indice_riesgo` | float | `SUM(indice_riesgo)` sobre las escuelas con predicción |
| `escuelas_con_prediccion` | int | Denominador del riesgo promedio |
| `escuelas_en_riesgo` | int | `COUNT(*) FILTER (WHERE indice_riesgo >= 0.6)` (R3) |
| `cobertura_riesgo` | enum `OK`/`SIN_DATO` | `SIN_DATO` cuando `escuelas_con_prediccion = 0` |

### 4.3 Por qué componentes aditivos y no promedios

Un promedio **no se puede reagregar**: el promedio de los promedios de tres niveles educativos no es el
promedio del municipio. Si el cubo guardara `indice_riesgo_promedio` y el usuario quitara el filtro de
nivel, Superset promediaría promedios y daría un número **incorrecto**.

Guardando el **numerador** y el **denominador** por separado, cualquier combinación de filtros se
recalcula bien:

```
indice_riesgo_promedio  = SUM(suma_indice_riesgo)  / NULLIF(SUM(escuelas_con_prediccion), 0)
variacion_ponderada_pct = SUM(matricula_total)       / NULLIF(SUM(suma_matricula_anterior), 0) - 1
d1_promedio             = SUM(suma_d1)             / NULLIF(SUM(escuelas_con_d1), 0)
```

Las dos primeras fórmulas son **idénticas** a KPI-03 y KPI-02 de [[vault/04_UX_Design/Screen_Specs]]: el cubo
solo las precalcula, no las redefine.

> ⚠️ **Un componente aditivo es una suma simple, nunca un producto ya ponderado.** La versión
> original de §4.4 declaraba `variacion_x_matricula = SUM(variacion_matricula * matricula_total)`, y
> eso resultó ser **BUG-031**: el producto congela dos supuestos que el contrato no había declarado
> —que `variacion_matricula` es una razón, cuando son alumnos absolutos, y que la agregación correcta
> es un promedio ponderado de razones, cuando es una razón de sumas— y una vez materializado en el
> cubo ya **no se puede corregir desde la capa semántica**, porque el numerador y el denominador
> reales dejaron de existir como columnas. KPI-02 pintó **−54.5 %** durante dos semanas donde el valor
> real era **−0.19 %**.
>
> La regla que se sigue de aquí: **toda razón se guarda como numerador y denominador por separado, y
> ambos son sumas de una sola columna.** Si hace falta multiplicar dos medidas para construir un
> componente, la métrica está mal planteada. Formulada así, además, KPI-02 solo depende de matrículas
> —que son alumnos y lo seguirán siendo— y por tanto **es inmune al resultado de ADR-007**.

### 4.4 Métricas derivadas (capa semántica de Superset)

| Métrica | Expresión | Formato |
|---|---|---|
| `escuelas` | `SUM(escuelas)` | entero |
| `matricula_total` | `SUM(matricula_total)` | entero |
| `variacion_ponderada_pct` | `SUM(matricula_total) / NULLIF(SUM(suma_matricula_anterior), 0) - 1` | % 1 decimal |
| `matricula_por_escuela` | `SUM(matricula_total) / NULLIF(SUM(escuelas), 0)` | 1 decimal |
| `indice_riesgo_promedio` | `SUM(suma_indice_riesgo) / NULLIF(SUM(escuelas_con_prediccion), 0)` | 0.00 |
| `escuelas_en_riesgo` | `SUM(escuelas_en_riesgo)` | entero |
| `pct_escuelas_en_riesgo` | `SUM(escuelas_en_riesgo) / NULLIF(SUM(escuelas_con_prediccion), 0)` | % 1 decimal |
| `completitud_promedio` | `SUM(suma_completitud) / NULLIF(SUM(escuelas), 0)` | % 0 decimales |
| `d1_promedio`…`d6_promedio` | `SUM(suma_d#) / NULLIF(SUM(escuelas_con_d#), 0)` | 0.00 |
| `pct_escuelas_con_d1`…`d6` | `SUM(escuelas_con_d#) / NULLIF(SUM(escuelas), 0)` | % 0 decimales |

> `pct_escuelas_en_riesgo` divide entre **escuelas con predicción**, no entre el total: decir "10% en
> riesgo" cuando solo el 30% de las escuelas fue puntuada sería inventar una cobertura que no existe.
> Todo gráfico que use esta métrica muestra al lado `escuelas_con_prediccion` como denominador visible.

> ⚠️ **Las razones porcentuales se guardan como fracción, nunca multiplicadas por 100.** El campo
> `formato: porcentaje_0|1` se mapea al formato d3 `,.0%` / `,.1%`, que **ya multiplica por 100 al
> renderizar**. Una expresión con `* 100.0` y formato de porcentaje pinta el número cien veces más
> grande: `0.318` se vería como `3,180.0%`. Este error ya apareció tres veces en el proyecto
> (US-203, US-211b y US-212), así que `tests/test_semantic_db03_db04.py` lo hace cumplir en CI.

### 4.5 Jerarquías y drill-down

```
Entidad (cve_ent)
   └── Municipio (cve_mun)          ← grano de comparación (n a n, 2 a 4 municipios)
         └── Nivel educativo         ← desglose interno / filtro global
               └── (salto a DB-03 por cct)
```

| Ruta | Desde | Hacia | Llave |
|---|---|---|---|
| Entrada | DB-02 Mapa | **DB-04** | `cve_mun` seleccionado |
| Lateral | **DB-04** | DB-03 | `cct` de la escuela elegida en el municipio |

---

## 5. Mapeo a los KPIs canónicos

Las fórmulas **no se duplican**: este documento referencia el catálogo de
[[vault/04_UX_Design/Screen_Specs]] §4 y solo precalcula sus componentes.

| Métrica del cubo | KPI canónico | Cubo |
|---|---|---|
| `matricula_total` | KPI-01 | ambos |
| `variacion_ponderada_pct` | KPI-02 | ambos |
| `indice_riesgo_promedio` | KPI-03 | `cubo_comparador_municipio` |
| `escuelas_en_riesgo` | KPI-04 | ambos |
| `completitud_promedio` | KPI-05 | ambos |
| `pct_escuelas_con_d#` | KPI-06 (complemento) | `cubo_comparador_municipio` |
| `driver_dominante` / `nombre_driver` | KPI-07 | `cubo_escuela_360` |
| `poblacion`, `pobreza_pct`, `grado_rezago`, `indice_rezago_social` | KPI-14 | `cubo_comparador_municipio` |

### 5.1 KPIs de DB-03 — propuestos aquí, **publicados por Manuel en el catálogo**

El catálogo va de KPI-01 a KPI-14 y **DB-03 no tiene ningún KPI propio**, pero **AC-002.4** exige que la
ficha muestre perfil, drivers, predicción y recomendación por CCT. Se proponen cuatro altas para que
Manuel las incorpore a [[vault/04_UX_Design/Screen_Specs]] (documento canónico suyo — regla 1 del vault:
un tema, un archivo canónico):

| ID propuesto | KPI | Grano | Expresión | Sustenta |
|---|---|---|---|---|
| **KPI-15** | Perfil de matrícula de la escuela | cct × ciclo | `SUM(matricula_total)` + serie por `anio_inicio` | AC-002.4, AC-002.5 |
| **KPI-16** | Perfil de drivers de la escuela | cct × ciclo | `d1`…`d6` con su `d#_cobertura`; `SIN_DATO` se dibuja como hueco, no como cero | AC-002.4, AC-002.6 |
| **KPI-17** | Predicción de la escuela | cct × ciclo | `indice_riesgo` (`LEFT JOIN gold.predicciones`, `modelo='ML-01'`), semáforo en 0.6 | AC-002.4 |
| **KPI-18** | Recomendación prescriptiva de la escuela | cct × ciclo | `driver_dominante` + `recomendacion` + `prioridad` (`LEFT JOIN gold.recomendaciones`) | AC-002.4 |

✅ **Los cuatro ya están publicados** en [[vault/04_UX_Design/Screen_Specs]] §4 (2026-08-15, US-201), con las
mismas fórmulas y el mismo grano que se proponen aquí. El catálogo de Manuel es la **fuente canónica**
de KPI-15…KPI-18; esta tabla queda como registro del origen de la propuesta.

---

## 6. SQL de referencia — entregable para US-113 (Célula 1)

El SQL vive en `superset/semantic/` para poder usarse también como **dataset virtual** de Superset
mientras los cubos físicos no existan:

- `superset/semantic/db03_cubo_escuela_360.sql`
- `superset/semantic/db04_cubo_comparador_municipio.sql`

Son **propuestas de implementación**, no código de producción: la materialización (`dbt`, índices,
estrategia de refresco) es decisión de la Célula 1 en US-113 y US-114.

Índices sugeridos a C1:

| Cubo | Índice sugerido | Motivo |
|---|---|---|
| `cubo_escuela_360` | `(cct, id_ciclo)` único · `(cve_mun, id_ciclo)` · `(cve_ent, nivel, id_ciclo)` | Búsqueda por CCT y filtros globales |
| `cubo_comparador_municipio` | `(cve_mun, nivel, id_ciclo)` único · `(cve_ent, id_ciclo)` | Comparación n a n y filtro de entidad |

---

## 7. Contrato de dependencias

| Columna(s) | Depende de | Historia | Estado hoy (14-ago) |
|---|---|---|---|
| Todo el hecho, dimensiones y `d1`…`d6` | Célula 1 · Gold | US-103, US-112, US-113 | ⬜ No existe `gold.*`; `dbt/` vacío |
| `indice_riesgo`, `variacion_proyectada`, `probabilidad` | Célula 3 · `gold.predicciones` | US-311 (ML-01) | 🟡 En progreso |
| `driver_dominante`, `recomendacion`, `prioridad` | Célula 3 · `gold.recomendaciones` | US-302 / US-303 | ⬜ S4 |
| Convención de datasets y métricas de Superset | Célula 2 · Manuel | US-202 | ⬜ S3, en paralelo |

**Comportamiento mientras las dependencias no llegan:** los bloques de predicción y recomendación de
DB-03 y las métricas de riesgo de DB-04 muestran **"sin dato disponible"** vía `cobertura_prediccion`,
`cobertura_recomendacion` y `cobertura_riesgo`. El tablero no se rompe ni miente con ceros.

---

## 8. Solicitudes formales a otras células

### 8.1 A Diana Alvarez (C1) — cambio de grano de `cubo_comparador_municipio`

- **Qué:** grano de `municipio × ciclo` → **`municipio × nivel × ciclo`** en
  [[vault/03_Architecture/Data_Model]] §4.3, con métricas guardadas como componentes aditivos (§4.3).
- **Por qué:** con el grano actual, **AC-002.2 no se puede cumplir en DB-04** — el filtro global de
  nivel educativo no tendría sobre qué operar, y reagregar promedios daría números incorrectos.
- **Impacto:** cambio de esquema ⇒ **regla 7, revisión humana explícita**. Afecta a US-113 (Deni).
- **Estado:** ✅ **Aceptado por Diana Alvarez el 2026-08-14.** [[vault/03_Architecture/Data_Model]] §4.3 ya
  declara el grano `municipio × nivel × ciclo` y adopta las métricas como numerador y denominador
  separados, con nota de diseño que traza el cambio a este hallazgo de US-211a. Queda pendiente que el
  PM lo registre en [[vault/10_Risk_Governance/Decision_Log]].

### 8.2 A Diana Alvarez (C1) — codificación de `SIN_DATO` en `d1`…`d6`

- **Qué:** el diccionario ([[vault/03_Architecture/Data_Model]] §6) tipa `d1`…`d6` como `float | SIN_DATO`,
  pero una columna `float` no puede almacenar la cadena `SIN_DATO`. Confirmar que la codificación
  real es **valor `NULL` + `d#_cobertura = 'SIN_DATO'`**.
- **Mitigación mientras responde:** todo el SQL de este contrato filtra por `d#_cobertura`, que es
  inequívoca en ambas interpretaciones. No hay bloqueo.
- **Estado:** ⬜ **pendiente de confirmación al 2026-08-21.** `Data_Model` §6 sigue tipando
  `float | SIN_DATO`. **No bloquea** US-211a ni US-212 por la mitigación de arriba.

### 8.3 A Manuel Serranía (C2) — ✅ resuelto

| Solicitud | Resultado |
|---|---|
| Alta de **KPI-15…KPI-18** en el catálogo (§5.1) | ✅ Publicados en [[vault/04_UX_Design/Screen_Specs]] §4 (2026-08-15, US-201) |
| Ratificar el **`LEFT JOIN`** en el grano de escuela (§2.2) | ✅ Ratificado en el mismo cambio; KPI-17 y KPI-18 lo documentan |
| Adoptar la convención `superset/semantic/` en **US-202** | ✅ Adoptada; US-202 cerrada con [[vault/04_UX_Design/Superset_Setup_US202]] y `superset/sync_semantic_layer.py` |

**Verificación de alineación (2026-08-21):** se comparó KPI-15…KPI-18 del catálogo contra §5.1 y §3.2 de
este documento. Coinciden en fórmula, grano, tipo de `JOIN`, umbral 0.6 y banderas de cobertura.
**Sin divergencias.**

---

## 8.ter Cierre de US-212 — evidencia (2026-09-03)

> US-212 estuvo al 95 % desde el 29-ago con **un solo bloqueo**: ratificar ADR-007 y que la
> unidad del target llegara al dato. Ambas cosas ocurrieron; aquí queda la evidencia de que
> el 5 % restante está verificado. **El cambio de estado en `Execution_Status.md` lo hace el
> PM**: esa ruta no está en el alcance de Célula 2.

### 8.ter.1 El bloqueo desapareció, y no por decreto

| Paso de ADR-007 | Dueño | Evidencia |
|---|---|---|
| 1 · Normalizar el target a fracción en `features_escuela.sql` | C1 · Diana Alvarez | ✅ 2026-08-31 |
| 2 · Rechazar `matricula_previa = 0` explícito, sin `NULLIF` silencioso | C1 · Diana Alvarez | ✅ 2026-08-31 |
| 3 · Regenerar `gold.predicciones` | C3 · Héctor Morales | ✅ 2026-09-03 |
| 4 · Reentrenar ML-01 | C3 · Héctor Morales | ✅ 2026-09-03 |

Verificado corriéndolo, no leyéndolo: `gold.predicciones.valor` sale en rango
**−0.0437 … +0.0313**. Es una **fracción**, no alumnos absolutos. Y el `indice_riesgo` va de
**0.1637 a 0.5615** — deja de estar saturado, que era el síntoma con el que BUG-017 detuvo
correctamente la publicación.

### 8.ter.2 AC-002.4 verificado

El criterio que no se podía comprobar —"DB-03 permite drill-down a una escuela por CCT y
muestra su perfil, drivers, predicción y recomendación"— hoy se comprueba:

| Qué | Resultado |
|---|---|
| `cobertura_prediccion = OK` | **55** escuelas (ciclo 2024-2025) |
| `cobertura_prediccion = SIN_DATO` | **90** (los ciclos sin predicción — correcto, no un hueco) |
| Charts de DB-03 y DB-04 con datos | **24/24** |
| Bloques de predicción y recomendación | pueblan con datos reales de `gold.predicciones` |

Reproducible **solo con fixtures del repositorio**, que es lo que BUG-013 exigía y no se podía:
los tres fixtures de Formato 911 dan `gold.features_escuela` con 145 filas y 3 ciclos, y
`publicar_gold --desde-gold` publica 55 + 55. Mismas cifras que obtuvo Héctor Morales el mismo
día por su cuenta, que es la comprobación de que no es un ambiente afortunado.

### 8.ter.3 KPI-02 concuerda por cinco caminos (BUG-031)

> **Corregido el 2026-09-04.** La primera versión de esta sección daba **−0.192 %** como
> "el" KPI-02. Ese número es la **mezcla de los tres ciclos**, no el valor de un ciclo, y
> por lo tanto no es lo que el tablero muestra. Ver §8.quater: es el mismo defecto de
> agregación que motivó el ciclo por defecto. El número correcto del ciclo vigente es
> **−0.496 %**. La concordancia entre cubos —que es lo que BUG-031 verificaba— **se
> sostiene igual**, y ahora se comprueba al grano correcto.

KPI-02 del ciclo **2024-2025**, por los cinco caminos que lo alimentan:

| Origen | KPI-02 (2024-2025) |
|---|---|
| `gold.fact_escuela_ciclo` (fuente de verdad) | **−0.496 %** |
| `gold.cubo_matricula` → DB-01, DB-06 | **−0.496 %** |
| `gold.cubo_riesgo_territorial` → DB-02 | **−0.496 %** |
| `gold.cubo_escuela_360` → DB-03 | **−0.496 %** |
| `gold.cubo_comparador_municipio` → DB-04 | **−0.496 %** |

Sobre 11 828 / 11 887 alumnos del ciclo.

Por qué importa la distinción, y no es cosmética: los tres ciclos **no van en la misma
dirección**, así que el promedio mezclado esconde el signo.

| Ciclo | Matrícula | Anterior | KPI-02 |
|---|---|---|---|
| 2022-2023 | 13 267 | 13 235 | **+0.242 %** |
| 2023-2024 | 7 217 | 7 252 | −0.483 % |
| 2024-2025 | 11 828 | 11 887 | −0.496 % |
| *(mezcla de los tres)* | *32 312* | *32 374* | *−0.192 %* |

Un tablero que respondiera "la matrícula cayó 0.19 %" estaría promediando un año que
**subió** con dos que bajaron. La cifra parece razonable y significa otra cosa — el mismo
modo de falla que BUG-017 y BUG-031.

### 8.ter.4 La regla `SIN_DATO` aguanta de punta a punta

| Driver | Escuelas `SIN_DATO` | Por qué |
|---|---|---|
| D1 · pobreza | 145 / 145 | CONEVAL no ingerible desde los fixtures del repo |
| D2 · inseguridad | 0 / 145 | SESNSP con dato |
| D3 · infraestructura | 12 / 145 | cobertura parcial de CEMABE |
| D4 · conectividad | 12 / 145 | cobertura parcial de CEMABE |
| D5 · agua | 145 / 145 | CONAGUA no ingerida |
| D6 · aire | 140 / 145 | SINAICA cubre ~80 zonas urbanas |

Y lo que de verdad importa: **cero casos** en que un driver marcado `SIN_DATO` traiga un valor.
Donde el Estado no mide, el tablero lo dice; no inventa un cero.

### 8.ter.5 Lo que NO cierra con esto

- `en_riesgo = 0` en las 55 escuelas con predicción. **No es un defecto**: el riesgo máximo es
  0.5615 y el umbral de DEC-006 es 0.60. Con datos de fixture nadie lo cruza. Con los datos
  reales de Diana el resultado puede ser otro, y conviene revisarlo antes de la demo.
- El criterio de cierre por URL pública **no aplica** a US-212: Edgar lo precisó el 29-ago —
  ese gate se escribió para rutas HTTP de la API. Un tablero cierra con evidencia de código
  más capa de datos validada.

---

## 8.quinquies `escuelas_en_riesgo = 0` — análisis para la mesa (2026-09-04)

> **Insumo de decisión, no una decisión.** El umbral lo fija **DEC-006**, ratificado por
> Manuel Serranía y registrado por Edgar Coronel. Esta sección aporta la evidencia; el
> cambio —si lo hay— no es de Célula 2.

### 8.quinquies.1 Qué se reportó

Luis Téllez lo marcó el 2026-09-04 como **H1** al liberar la URL pública: *"ojo con
`escuelas_en_riesgo=0` — el riesgo real máximo es 0.401 y el umbral del KPI es 0.6, hay
que ajustar umbral o narrativa antes de la demo"*. Afecta `KPI-04` (DB-04) y `KPI-17`
(DB-03), que son de esta historia.

### 8.quinquies.2 No es un defecto: el cero es correcto

`src/modelos/riesgo.py` (C3) define el `indice_riesgo` como una sigmoide fijada por **dos
anclas de negocio explícitas**, no por constantes arbitrarias:

| Variación de matrícula | `indice_riesgo` |
|---|---|
| `0.00` (matrícula estable) | 0.30 |
| **`-0.05` (pierde 5 %)** | **0.60 — exactamente el umbral de DEC-006** |

Es decir: **`indice_riesgo ≥ 0.6` significa "se proyecta que pierda 5 % o más de su
matrícula"**. Verificado contra los datos (ciclo 2024-2025, 55 escuelas con predicción):

| `indice_riesgo` | Variación proyectada |
|---|---|
| 0.56 (el máximo observado) | **−4.37 %** |
| 0.52 | −3.73 % |
| 0.50 | −3.36 % |
| 0.41 | −1.97 % |

**Ninguna escuela llega a −5 %.** El cero no es un KPI roto: es la afirmación verdadera de
que, con estos datos, ninguna escuela cruza el criterio de negocio que el propio equipo
definió. La sigmoide, el umbral y el conteo son internamente coherentes.

Bajar el umbral "para que se vea algo" **rompería esa coherencia**: desharía el
significado de −5 % que DEC-006 fijó, y volvería el número incomparable entre ciclos —
justo la propiedad por la que C3 eligió una sigmoide absoluta sobre un percentil relativo.

### 8.quinquies.3 Qué se vería con cada umbral

Si aun así se decide mover el umbral, este es el costo en interpretación:

| Umbral | Escuelas en riesgo | % del universo | Qué significaría |
|---|---|---|---|
| **0.60** (hoy, DEC-006) | 0 | 0 % | "pierde ≥ 5 %" — coherente, pero muestra cero |
| 0.50 | 5 | 9.1 % | ≈ "pierde ≥ 3.4 %" — hay que redefinir el criterio |
| 0.40 | 15 | 27.3 % | ≈ "pierde ≥ 1.9 %" — el 27 % del universo "en riesgo" diluye la señal |
| 0.35 | 23 | 41.8 % | casi la mitad marcada: deja de ser una alerta |

Distribución real (55 escuelas con predicción, ciclo 2024-2025): mínimo 0.164, mediana
0.317, p90 0.499, p95 0.515, máximo **0.562**.

### 8.quinquies.3.bis CORRECCIÓN (2026-09-04) — el dato de "nadie cruza" estaba sesgado

> **La conclusión de §8.quinquies.4 no cambia; un dato de apoyo sí.** Se corrige aquí en
> vez de reescribir arriba, porque Edgar Coronel ya ratificó citando este análisis y hay
> que poder ver qué cambió.

Las cifras de §8.quinquies.2 (*"la escuela peor proyecta −4.37 %, ninguna llega a −5 %"*)
se midieron en el ambiente local **cuando CONEVAL no era ingerible** (BUG-045), así que
**D1 estaba vacío en las 145 escuelas** y ML-01 entrenaba con 4 de 6 drivers. No era una
muestra representativa.

Con los fixtures que publicó Diana Alvarez el 2026-09-04 (BUG-045 `fixed`), D1 vuelve, el
modelo entrena con 5 de 6 y la distribución del riesgo cambia:

| | Sin D1 (medición original) | Con D1 (correcta) |
|---|---|---|
| Riesgo mínimo | 0.1637 | 0.0841 |
| Riesgo máximo | 0.5615 | **0.7423** |
| `escuelas_en_riesgo` | 0 | **2** |
| ML-01 MAE | 0.0818 | 0.0844 |

**Y las dos que cruzan lo hacen por la razón correcta:**

| CCT | `indice_riesgo` | Variación proyectada | Driver dominante |
|---|---|---|---|
| `15DJN0049A` | 0.7423 | **−7.60 %** | D1 |
| `09DSN0042A` | 0.6692 | **−6.19 %** | D2 |
| `14DJN0061A` | 0.5384 | −4.00 % | *(no cruza — correcto)* |

Ambas proyectan perder **más del 5 %**, que es exactamente lo que DEC-006 define. La
sigmoide dispara cuando debe y no dispara cuando no debe: **la calibración queda
verificada empíricamente**, no solo por lectura del código.

**En producción sigue en cero.** Consultado el 2026-09-04:
`/api/v1/kpis` → `escuelas_en_riesgo: 0`, y esos dos CCT allá tienen riesgo 0.129 y 0.098.
Los fixtures son sintéticos (12 municipios CONEVAL, generación determinista), así que su
distribución no representa a las ~132 000 escuelas reales. **Para la demo, el número que
se verá es el de producción.**

Qué cambia en la práctica: nada de la recomendación, y **mejora el argumento**. Ya no hay
que decir *"nadie cruza el umbral, confíen en que está bien calibrado"*; ahora se puede
mostrar un caso donde **sí dispara, a −7.60 %**. Eso responde por adelantado la pregunta
obvia de cualquiera que vea un KPI en cero: *"¿y cómo sé que no está roto?"*

### 8.quinquies.4 Recomendación de Célula 2

**No mover DEC-006.** Tres razones: el cero es verdadero, el umbral tiene un significado
de negocio explícito y trazable, y cambiarlo a dos días del freeze reabre una decisión
ratificada sin ganar información.

Lo que sí resuelve el problema de la demo, sin tocar la decisión: **dejar de contar y
empezar a ordenar**. El valor del proyecto no es "cuántas escuelas cruzan un umbral", es
"cuáles son las más urgentes y por qué driver" — que es el diferenciador prescriptivo y ya
funciona. Un ranking de las escuelas de mayor riesgo con su driver dominante y su
recomendación cuenta la historia completa aunque ninguna llegue a 0.60.

Alternativa si se quiere conservar un conteo: **una banda intermedia** ("atención",
0.40–0.60) como KPI adicional, sin redefinir "en riesgo". No toca DEC-006 y da 15 escuelas
que mostrar. Requiere aval de Manuel (catálogo de KPIs) y de Edgar.

### 8.quinquies.5 Resolución — ratificado por el PM (2026-09-04)

**Edgar Coronel ratificó la recomendación: DEC-006 no se reabre.** El umbral 0.6 se queda.

> *"Está calibrado contra el criterio de negocio real (~5 % de pérdida), y bajarlo sería
> mover la meta para que el conteo no dé cero. Para la demo del 9 usamos el ranking de
> mayor riesgo con driver dominante y recomendación."*

La banda "atención" queda **descartada por ahora**. El ranking que se usará ya existe y
funciona con datos reales: es el chart *"Escuelas a intervenir (mayor riesgo)"* de DB-09
(US-204, Manuel Serranía), y desde US-214a se llega a él directo con el link `link_db09`
de la ficha de escuela. **No hay trabajo pendiente de Célula 2 por esta decisión.**

---

## 8.quater Ciclo por defecto en los filtros — US-214a (2026-09-04)

### 8.quater.1 El defecto

Un filtro nativo de Superset **sin valor inicial** deja el tablero sin filtrar al abrirlo.
Cualquier tarjeta que agregue sobre un cubo con grano multi-ciclo suma **todos** los ciclos:

| | Matrícula que pintaba `KPI-15` / `KPI-01` |
|---|---|
| Al abrir el tablero (sin filtro) | **32 312** |
| Ciclo 2024-2025 (lo correcto) | **11 828** |

2.7× inflado, sin ningún error en el sync, en la API ni en la consola del navegador.
Afectaba a las **8 tarjetas** de DB-03 y DB-04, no solo a las de matrícula: toda métrica
agregada sin dimensión tiene el mismo problema.

Lo detonó el aviso de **Luis Téllez del 2026-09-04**: el mismo defecto en
`/api/v1/kpis` de producción pintaba 20 638 574 contra ~6.7 M reales. Allá se corrigió en
la API; **los tableros no pasan por la API** —consultan la base directo— así que ese
arreglo no los cubría y necesitaban el suyo.

### 8.quater.2 El arreglo

Clave nueva `valor_por_defecto` en las entradas de `filtros_globales`, que
`_filtros_nativos()` traduce al `defaultDataMask` que Superset entiende — la misma
estructura que ya usan los links de drill-down en su parámetro `native_filters`, así que
el formato estaba verificado contra 6.1.0 desde US-214b.

**Es aditivo y opt-in.** `sync_semantic_layer.py` es herramienta compartida de la Célula 2
(la usan DB-01/02/05/06/07/08/09/10): un tablero que no declara la clave se comporta
exactamente igual que antes, y hay una prueba de compatibilidad hacia atrás que lo exige.

> **Mantenimiento:** el valor es explícito (`"2024-2025"`), no se deriva de los datos. Al
> cargar un ciclo nuevo hay que actualizarlo en los dos YAML. Se eligió explícito sobre
> dinámico por ser predecible y revisable a dos días del freeze; si el proyecto sigue
> vivo después de la demo, derivarlo de `MAX(id_ciclo)` es la mejora natural.

### 8.quater.3 Guarda

`tests/test_filtro_ciclo_por_defecto.py` (8 casos) cubre las dos **clases** de error:
que un tablero multi-ciclo publique tarjetas agregadas sin ciclo por defecto, y que el
traductor deje de emitir el `defaultDataMask` o rompa a quien no usa la clave. Validado
reintroduciendo ambos defectos. Verificado además en vivo contra el Superset desplegado:
los dos tableros persisten su ciclo por defecto, y el drill-down de §8.bis sigue apuntando
a los índices correctos (el filtro nuevo no corrió ninguna posición).

---

## 8.bis Navegación cruzada — US-214a

> Sección añadida el 2026-09-03 al implementar US-214a. El contrato de rutas vive en el
> bloque `drill_down:` de `superset/semantic/metrics_db03_db04.yaml`, con el `estado` de
> cada una; aquí queda el **porqué** y lo que hay que pedirle a quién.

### 8.bis.1 Por qué un `<a href>` y no una función de Superset

Superset **no tiene** navegación entre tableros. El *cross-filtering* y el *Drill to Detail*
nativos operan **solo dentro del mismo tablero**, y la propuesta de una columna tipo enlace
(SIP-77) fue rechazada. El único mecanismo disponible es una **columna calculada con un
`<a href>`** que lleva el parámetro `native_filters` codificado en RISON, más
`allow_render_html: true` en el chart. Lo estableció Monserrat Miranda en US-214b
(DB-05 → DB-08), verificado contra Superset 6.1.0 real; US-214a **reusa ese patrón**.

### 8.bis.2 La fragilidad que hay que conocer

Los IDs de filtro nativo los genera `_filtros_nativos()` **por posición**:
`NATIVE_FILTER-US203-{índice}` sobre `filtros_globales` del tablero **destino**.

> **Reordenar o insertar un filtro en medio de esa lista rompe la navegación en silencio.**
> El link sigue existiendo y sigue navegando, pero preselecciona la columna equivocada. No
> hay error en el sync, ni en la API, ni en la consola del navegador.

Por eso: **todo filtro nuevo se agrega al final de la lista**, y la correspondencia
índice ↔ columna está protegida por `tests/test_drill_down_db03_db04.py`.

Índices vigentes:

| Tablero | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| **DB-03** | `cct` | `id_ciclo` | `nombre_entidad` | `nivel` | `cve_mun` ← US-214a |
| **DB-04** | `id_ciclo` | `nombre_entidad` | `nombre_municipio` | `nivel` | `cve_mun` ← US-214a |

Ambos valores viajan citados con `%27`: `cve_mun` (`09002`) e `id_ciclo` (`2024-2025`)
tienen forma que RISON obliga a citar, y es el mismo reemplazo que hace el backend de
Superset en `reports/models.py`.

### 8.bis.3 Corrección de contrato: `DB-04 → DB-03`

US-211a declaró esta ruta con llave **`cct`**, y es **imposible**: DEC-008 fijó el grano de
`cubo_comparador_municipio` en `[cve_mun, nivel, id_ciclo]` y ese cubo **no tiene columna
`cct`**. La llave real es **`cve_mun`** — desde un municipio se baja a *sus* escuelas y el
usuario elige cuál; por eso el link deja libre el filtro `cct` de DB-03 a propósito.

El contrato quedó corregido y hay una prueba que rechaza la **clase** de error, no solo esta
instancia: `test_ninguna_ruta_declara_una_llave_que_el_cubo_de_origen_no_tiene`.

### 8.bis.4 Estado de las siete rutas

| Ruta | Llave | Estado | Qué falta |
|---|---|---|---|
| DB-03 → DB-04 | `cve_mun` | ✅ implementado | — |
| DB-04 → DB-03 | `cve_mun` | ✅ implementado | — |
| DB-03 → DB-06 | `[cct, id_ciclo]` | ⬜ bloqueado | **Manuel Serranía**: DB-06 no expone filtro `cct` |
| DB-03 → DB-09 | `[cct, id_ciclo]` | ⬜ bloqueado | **Manuel Serranía**: DB-09 no expone filtro `cct` |
| DB-01 → DB-03 | `cct` | ⬜ ajeno | El link vive en el SQL de DB-01 (Manuel) |
| DB-02 → DB-03 | `cct` | ⬜ ajeno | El link vive en el SQL de DB-02 (Manuel) |
| DB-02 → DB-04 | `cve_mun` | ⬜ ajeno | Origen de Manuel; **el destino ya está listo** (`cve_mun`, índice 4) |

### 8.bis.5 Dependencia operativa: BUG-037

Al agregar una columna a un `.sql` de `superset/semantic/`, `sync_semantic_layer.py`
actualiza el texto del SQL pero **no vuelve a leer las columnas del dataset**. Los charts
revientan con `Columns missing in dataset: ['link_db04']`, y el error **solo aparece al
abrir el tablero**, nunca en la corrida del sync. Reproducido el 2026-09-03 al construir
esta historia, exactamente como lo describe **BUG-037** (abierto, reportado por Monserrat).

Mitigación mientras siga abierto: `PUT /api/v1/dataset/<id>/refresh` después del sync.
El arreglo de fondo toca `sync_semantic_layer.py`, que es herramienta compartida de la
Célula 2 — requiere acuerdo con Manuel Serranía antes de tocarla.

---

## 9. Trazabilidad

- **Implementa:** US-211a (REQ-002) · US-214a (navegación cruzada, §8.bis)
- **Consume:** [[vault/03_Architecture/Data_Model]] §4 · [[vault/04_UX_Design/Screen_Specs]] §4 · [[vault/15_ML_Models/Indice_Riesgo_ML01]]
- **Alimenta:** US-212 (construcción de DB-03/DB-04), US-214a (filtros y drill-down), US-215a (usabilidad)
- **Insumo para:** US-113 (construcción de los cubos, Célula 1)
- **Sustenta AC:** AC-002.2, AC-002.4, AC-002.5, AC-002.6
