---
id: DOC-LINEAGE
title: "Linaje de datos completo — fuente → dashboard (US-106)"
owner: "Diana Aracely Alvarez Varela"
status: draft
version: "0.2"
source_of_truth: true
traces_up: ["US-106", "03_Architecture/Data_Model", "REQ-001"]
traces_down: ["02_Requirements/Traceability_Matrix"]
last_reviewed: "2026-08-26"
tags: [architecture, lineage, freeze, us-106]
---

# Linaje de datos completo — fuente → dashboard (US-106)

> Diagrama de linaje **nodo por nodo** de las 8 fuentes hasta los 10 dashboards, y la declaración de
> **freeze** del esquema Gold. Complementa el linaje de capas (alto nivel) de
> [[03_Architecture/Data_Model#8-linaje-fuente-dashboard|Data_Model §8]] — este documento es el
> **detalle completo**, objeto propio de **US-106**.
> → [[03_Architecture/Data_Model]] · [[03_Architecture/_index]]

---

## 1. Estado de este documento

**`status: draft`** — no es un freeze todavía. US-106 vence en el **Sprint S5 (31 ago – 6 sep
2026)**; el freeze real se declara el **6 de septiembre**, una vez cerrados los pendientes de la
§4. Este documento se preparó el 23-ago porque el esquema Gold ya estaba mayormente estable y
no tenía sentido esperar al último día para documentar el linaje. Actualizado el 26-ago: BUG-009
(DEC-011, PR #82) y el PR de Monserrat (#73) ya cerraron — pero **declarar el freeze hoy seguiría
siendo prematuro** mientras sigan abiertos los 4 cubos de DEC-009 (bloqueados además por un
conflicto real con DEC-010, ver §3) y la confirmación de `coneval_periodo_medicion` (RISK-008).

## 2. Cómo leer el diagrama

Cada nodo es una tabla o artefacto real (no una capa). El color/forma indica su estado:

- **Materializado** — existe hoy como modelo dbt o tabla real, con datos.
- **Especificado, pendiente de materializar** — existe su contrato/SQL de referencia en el vault,
  pero la tabla real todavía no se construye en el pipeline (dbt o Superset).
- **Documental** — no es una tabla, es la fuente pública o la capa lógica.

```mermaid
flowchart TD
    subgraph FUENTES["Fuentes públicas (DS-01…DS-08)"]
        DS01["DS-01<br/>SEP Formato 911"]
        DS02["DS-02<br/>SEP Catálogo CCT"]
        DS03["DS-03<br/>SEP/INEGI CEMABE"]
        DS04["DS-04<br/>SESNSP Incidencia Delictiva"]
        DS05["DS-05<br/>SINAICA Calidad del Aire"]
        DS06["DS-06<br/>CONAGUA SINA"]
        DS07["DS-07<br/>CONEVAL Rezago Social"]
        DS08["DS-08<br/>CONAPO Proyecciones"]
    end

    subgraph BRONZE["BRONZE — crudo, nacional"]
        B_f911["bronze.formato911_2024_2025"]
        B_f911h["bronze.formato911_historico"]
        B_cct["bronze.cct_&lt;fecha&gt;<br/>(RISK-009: identifier real pendiente de fijar en sources.yml)"]
        B_cemabe["bronze.cemabe_2013"]
        B_sesnsp["bronze.sesnsp_&lt;aaaa_mm&gt;<br/>(BUG-009)"]
        B_sinObs["bronze.sinaica_observaciones<br/>(BUG-009)"]
        B_sinEst["bronze.sinaica_estaciones<br/>(BUG-009)"]
        B_conagua["bronze.conagua_&lt;fecha&gt;<br/>⚠️ sin datos ingeridos todavía"]
        B_coneval["bronze.coneval_&lt;aaaa&gt;<br/>(BUG-009 — 2 versiones sin reconciliar: test/v2)"]
        B_conapo["bronze.conapo_&lt;aaaa&gt;<br/>(BUG-009)"]
    end

    subgraph SILVER["SILVER — tipado, conformado, nacional"]
        S_matricula["silver.matricula"]
        S_matriculaHist["silver.matricula_historica<br/>(RISK-007/DEC-007)"]
        S_escuela["silver.escuela"]
        S_cemabe["silver.cemabe"]
        S_delitos["silver.delitos_municipio"]
        S_aire["silver.aire_estacion<br/>(IDW, ADR-006, D6)"]
        S_agua["silver.agua_region<br/>⚠️ bloqueado por BUG-009/DS-06"]
        S_rezago["silver.rezago_municipio"]
        S_poblacion["silver.poblacion_municipio"]
    end

    subgraph GOLD_CORE["GOLD — estrella (SCOPE_ENTIDADES)"]
        G_dimEscuela["gold.dim_escuela"]
        G_dimMunicipio["gold.dim_municipio"]
        G_dimTiempo["gold.dim_tiempo"]
        G_dimDriver["gold.dim_driver<br/>(catálogo, ADR-005)"]
        G_fact["gold.fact_escuela_ciclo<br/>(hecho central)"]
        G_features["gold.features_escuela<br/>(contrato C1↔C3, §5.3 Data_Model)"]
        G_matNivel["gold.matricula_municipio_nivel<br/>(RISK-007/DEC-007)"]
    end

    subgraph GOLD_CUBOS["GOLD — cubos materializados (§4.3 Data_Model)"]
        C_matricula["gold.cubo_matricula<br/>⏳ pendiente US-113 (Deni)<br/>SQL ref. mergeado (PR #71, Manuel)"]
        C_riesgo["gold.cubo_riesgo_territorial<br/>⏳ pendiente US-113<br/>SQL ref. mergeado (PR #71)"]
        C_360["gold.cubo_escuela_360<br/>✅ SQL semántico (db03)"]
        C_comparador["gold.cubo_comparador_municipio<br/>✅ SQL semántico (db04, DEC-008)"]
        C_driver["gold.cubo_driver<br/>⏳ pendiente US-211b (Monserrat, PR sin abrir)"]
        C_completitud["gold.cubo_completitud<br/>⏳ pendiente, sin SQL aún (DEC-009)"]
        C_pivot["gold.cubo_pivot<br/>⏳ pendiente"]
        C_recomendaciones["gold.cubo_recomendaciones<br/>⏳ pendiente"]
        C_pipeline["gold.cubo_pipeline<br/>⏳ pendiente"]
    end

    subgraph ML["ML — Célula 3 (MLflow, walk-forward, ADR-003)"]
        ML01["ML-01<br/>Regresión de matrícula"]
        ML02["ML-02<br/>Clasificación de driver dominante"]
        ML03["ML-03<br/>Clustering de escuelas"]
    end

    subgraph GOLD_ML["GOLD — salida de modelos"]
        G_pred["gold.predicciones<br/>(indice_riesgo, valor)"]
        G_reco["gold.recomendaciones<br/>(driver_dominante, prioridad)"]
    end

    subgraph DASHBOARDS["Superset — 10 dashboards"]
        DB01["DB-01 Ejecutivo"]
        DB02["DB-02 Mapa de riesgo territorial"]
        DB03["DB-03 Ficha de escuela"]
        DB04["DB-04 Comparador de municipios"]
        DB05["DB-05 Análisis por driver"]
        DB06["DB-06 Predicciones"]
        DB07["DB-07 Calidad y cobertura"]
        DB08["DB-08 Explorador del cubo"]
        DB09["DB-09 Recomendaciones prescriptivas"]
        DB10["DB-10 Monitor del pipeline"]
    end

    DS01 --> B_f911
    DS01 --> B_f911h
    DS02 --> B_cct
    DS03 --> B_cemabe
    DS04 --> B_sesnsp
    DS05 --> B_sinObs
    DS05 --> B_sinEst
    DS06 --> B_conagua
    DS07 --> B_coneval
    DS08 --> B_conapo

    B_f911 --> S_matricula
    B_f911h --> S_matriculaHist
    B_cct --> S_escuela
    B_cemabe --> S_cemabe
    B_sesnsp --> S_delitos
    B_sinObs --> S_aire
    B_sinEst --> S_aire
    B_conagua --> S_agua
    B_coneval --> S_rezago
    B_conapo --> S_poblacion

    S_escuela --> G_dimEscuela
    S_cemabe --> G_dimEscuela
    S_poblacion --> G_dimMunicipio
    S_rezago --> G_dimMunicipio
    S_matricula --> G_dimTiempo

    S_matricula --> G_fact
    G_dimEscuela --> G_fact
    S_cemabe --> G_fact
    S_rezago --> G_fact
    S_delitos --> G_fact
    S_aire --> G_fact
    S_agua -.-> G_fact

    S_matricula --> G_features
    G_dimEscuela --> G_features
    S_cemabe --> G_features
    S_rezago --> G_features
    S_delitos --> G_features
    S_aire --> G_features
    S_agua -.-> G_features

    S_matriculaHist --> G_matNivel

    G_fact --> C_matricula
    G_fact --> C_riesgo
    G_fact --> C_360
    G_dimDriver --> C_360
    G_fact --> C_comparador
    G_fact --> C_driver
    G_dimDriver --> C_driver
    G_fact --> C_completitud
    G_fact --> C_pivot
    G_dimDriver --> C_pivot

    G_features --> ML01
    G_features --> ML02
    G_features --> ML03

    ML01 --> G_pred
    ML03 --> G_pred
    ML02 --> G_reco

    G_pred --> C_recomendaciones
    G_reco --> C_recomendaciones
    G_reco --> C_driver

    B_f911 -.->|"metadatos de ingesta"| C_pipeline
    B_cct -.-> C_pipeline
    B_cemabe -.-> C_pipeline
    B_sesnsp -.-> C_pipeline
    B_sinObs -.-> C_pipeline
    B_coneval -.-> C_pipeline
    B_conapo -.-> C_pipeline

    C_matricula --> DB01
    C_matricula --> DB06
    C_riesgo --> DB02
    C_360 --> DB03
    C_comparador --> DB04
    C_driver --> DB05
    C_completitud --> DB07
    C_pivot --> DB08
    C_recomendaciones --> DB09
    C_pipeline --> DB10
```

> Líneas punteadas (`-.->`): dependencia condicionada o parcial — `silver.agua_region` alimenta
> `fact_escuela_ciclo`/`features_escuela` solo como `SIN_DATO` explícito mientras DS-06 siga sin
> datos reales (ver §3.5 y §4). Las flechas de metadatos hacia `cubo_pipeline` son de *lectura de
> `_ingested_at`/`_source`*, no de transformación de negocio.

---

## 3. Qué está materializado hoy (26-ago-2026) vs. qué falta

| Capa | Materializado | Pendiente |
|---|---|---|
| Bronze | 10/10 tablas con `identifier` por default (**DEC-011**, PR #82, 24-ago) | `conagua` sigue sin ninguna tabla real ingerida — default deliberadamente falso (`conagua_no_ingerido`) |
| Silver | 8/9 modelos dbt construidos y probados | `agua_region` sin datos reales (depende de bronze conagua) |
| Gold — estrella | `dim_escuela`, `dim_municipio`, `dim_tiempo`, `fact_escuela_ciclo`, `features_escuela`, `matricula_municipio_nivel` — construidos, testeados (dbt tests nativos) | `dim_driver` es catálogo estático (ADR-005), no depende de pipeline |
| Gold — ML runtime | `gold.predicciones` con **grano dual** (**DEC-010**, PR #83, mergeado 24-ago) y `gold.recomendaciones` — publicados por el job idempotente `publicar_gold.py` (US-313); verificado contra Postgres real (80 filas grano escuela + 46 grano municipio_nivel, Héctor) | — |
| Gold — cubos | `cubo_escuela_360` y `cubo_comparador_municipio` (SQL semántico, Manuel, PR #71); `cubo_driver` (SQL semántico, Monserrat, **PR #73, ya mergeado**) | Los 8 cubos reales en `dbt/models/gold/` siguen sin mergear — viven en el **PR #81** (Deni, draft); bloqueado además porque 5 de ellos no filtran `grano = 'escuela'` en su JOIN contra `gold.predicciones` (colisión con DEC-010, señalada por Edgar) |
| API / consumo | — | **BUG-010** (nuevo, 26-ago): `/api/v1/predicciones/*` sigue leyendo `mock_data.py`, no `gold.predicciones` real — bloquea la verificación #4 del ensayo E2E del 28-29 |
| Gobernanza de esquema | DEC-008, DEC-009, **DEC-010**, **DEC-011** registradas en `Decision_Log.md` y `Data_Model.md` §4.3/§4.5 | — |

## 4. Checklist para el freeze del 6 de septiembre

No declarar el freeze hasta que:

- [x] PR #74 (fix D6 IDW), #75 (DEC-009) y #76 (hallazgos BUG-009) estén mergeados a `main`
      — los tres mergeados el 2026-08-23, junto con #73, #77, #78 y #79
- [ ] Los 4 cubos de DEC-009 (`cubo_matricula`, `cubo_riesgo_territorial`, `cubo_driver`,
      `cubo_completitud`) estén materializados con el grano nuevo (US-113, Deni) o, si no alcanza
      el tiempo, quede documentado explícitamente como deuda técnica aceptada por Edgar
      — **bloqueado además**: PR #81 (draft) no filtra `grano = 'escuela'` en sus JOIN contra
      `gold.predicciones` (colisión con DEC-010, señalada por Edgar el 23-ago) — silenciosamente
      descartaría las filas de grano `municipio_nivel` sin marcar error hasta que se corrija
- [x] BUG-009 tenga default permanente en `sources.yml` (o, alternativa, se documenten los valores
      reales como configuración estándar del ambiente) — Edgar decide el reparto
      — cerrado por **DEC-011**: las 11 vars (no 7) con default permanente, identifiers inline en
      `sources.yml` y vars de modelo en `dbt_project.yml`; `dbt parse` en CI como test de regresión
- [ ] `coneval_periodo_medicion` esté confirmado por Deni (no el placeholder `2020`)
      — **sigue abierto**: `2020` quedó como deuda técnica aceptada explícitamente por Edgar Coronel
      (PM) en DEC-011, no como valor confirmado. Rastreado como **RISK-008** (dueña: Deni, fecha
      objetivo: 6-sep). Si no lo confirma antes del freeze, se declara con esta deuda a la vista, no
      cerrada en silencio. Incluye confirmar que `coneval_v2` es la tabla correcta y no `coneval_test`
- [x] El PR de Monserrat (`feat/monserrat-olivas-us211b-cubos-db05-db08`) esté abierto y su SQL de
      `cubo_driver` revisado — PR #73, revisado y aprobado por Manuel Serranía, mergeado el 2026-08-23
- [ ] Este documento pase de `status: draft` a `status: approved` con fecha de freeze real

## 5. Qué significa "congelar" el esquema

A partir de la fecha de freeze, cualquier cambio a la forma de una tabla **Gold** (agregar,
quitar o renombrar columnas; cambiar el grano) deja de ser un ajuste normal de desarrollo y pasa a
requerir:

1. Un **ADR** o entrada en `10_Risk_Governance/Decision_Log.md` (mismo criterio que DEC-008/DEC-009).
2. Revisión explícita de Diana Alvarez Varela (Tech Lead Célula 1, regla 7 del vault).
3. Aviso a las células consumidoras afectadas (**C2** Superset, **C3** ML, **C4** API) antes del
   merge, no después.

Esto **no** congela Bronze ni Silver — esas capas pueden seguir absorbiendo fuentes nuevas o
correcciones de calidad sin pasar por este proceso, mientras no cambien el contrato hacia Gold.

---

## 6. Ver también

- [[03_Architecture/Data_Model|Data_Model.md]] — diccionario de columnas y contratos Pydantic completos
- [[10_Risk_Governance/Decision_Log|Decision_Log]] — DEC-008, DEC-009
- [[06_Quality_Testing/Bug_Register|Bug_Register]] — BUG-009
- [[04_UX_Design/Screen_Specs|Screen_Specs]] — catálogo completo de KPIs por dashboard
- [[15_ML_Models/ML_Strategy|ML_Strategy]] — ML-01/ML-02/ML-03