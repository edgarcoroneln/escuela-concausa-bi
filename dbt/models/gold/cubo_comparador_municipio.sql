{{ config(materialized='materialized_view') }}

-- US-113 / DB-04
-- Grano ratificado por DEC-008: cve_mun × nivel × id_ciclo.
-- Regla de reagregación: se guardan componentes aditivos, nunca promedios
-- precalculados que Superset pudiera promediar de nuevo.
-- Riesgo ML-01 se agrega sobre la población con predicción; la ausencia
-- permanece explícita como cobertura_riesgo='SIN_DATO'.
-- Drivers: valor faltante nunca se convierte en cero.

with observado as (
    select
        f.cve_mun,
        dm.cve_ent,
        dm.nombre_municipio,
        dm.nombre_entidad,
        e.nivel,
        f.id_ciclo,
        dt.ciclo,
        dt.anio_inicio,

        dm.poblacion,
        dm.pobreza_pct,
        dm.grado_rezago,
        dm.indice_rezago_social,

        count(distinct f.cct) as escuelas,
        sum(f.matricula_total) as matricula_total,
        -- FIX (2026-08-31, Diana/BUG-031): variacion_x_matricula era sum(variacion_matricula *
        -- matricula_total) -- promedio ponderado de una columna que no es razón (alumnos
        -- absolutos), Superset la renderizaba como % y salía 287x el valor real (−54.5% vs
        -- −0.19%). Se reemplaza por el componente aditivo correcto: suma_matricula_anterior, para
        -- que C2 arme la razón de sumas SUM(matricula_total)/SUM(suma_matricula_anterior) - 1.
        sum(f.matricula_ciclo_anterior) as suma_matricula_anterior,
        sum(f.indice_completitud_drivers) as suma_completitud,

        sum(case when f.d1_cobertura = 'OK' then f.d1 end) as suma_d1,
        count(*) filter (where f.d1_cobertura = 'OK') as escuelas_con_d1,
        sum(case when f.d2_cobertura = 'OK' then f.d2 end) as suma_d2,
        count(*) filter (where f.d2_cobertura = 'OK') as escuelas_con_d2,
        sum(case when f.d3_cobertura = 'OK' then f.d3 end) as suma_d3,
        count(*) filter (where f.d3_cobertura = 'OK') as escuelas_con_d3,
        sum(case when f.d4_cobertura = 'OK' then f.d4 end) as suma_d4,
        count(*) filter (where f.d4_cobertura = 'OK') as escuelas_con_d4,
        sum(case when f.d5_cobertura = 'OK' then f.d5 end) as suma_d5,
        count(*) filter (where f.d5_cobertura = 'OK') as escuelas_con_d5,
        sum(case when f.d6_cobertura = 'OK' then f.d6 end) as suma_d6,
        count(*) filter (where f.d6_cobertura = 'OK') as escuelas_con_d6

    from {{ ref('fact_escuela_ciclo') }} f
    inner join {{ ref('dim_escuela') }} e
        on f.cct = e.cct
    inner join {{ ref('dim_municipio') }} dm
        on f.cve_mun = dm.cve_mun
    inner join {{ ref('dim_tiempo') }} dt
        on f.id_ciclo = dt.id_ciclo

    group by
        f.cve_mun,
        dm.cve_ent,
        dm.nombre_municipio,
        dm.nombre_entidad,
        e.nivel,
        f.id_ciclo,
        dt.ciclo,
        dt.anio_inicio,
        dm.poblacion,
        dm.pobreza_pct,
        dm.grado_rezago,
        dm.indice_rezago_social
),

riesgo as (
    select
        f.cve_mun,
        e.nivel,
        f.id_ciclo,

        sum(p.indice_riesgo) as suma_indice_riesgo,
        count(*) as escuelas_con_prediccion,
        count(*) filter (where p.indice_riesgo >= 0.5) as escuelas_en_riesgo

    from {{ ref('fact_escuela_ciclo') }} f
    inner join {{ ref('dim_escuela') }} e
        on f.cct = e.cct
    inner join {{ source('gold_ml_runtime', 'predicciones') }} p
        on f.cct = p.cct
        and f.id_ciclo = p.id_ciclo
        and p.modelo = 'ML-01'
        and coalesce(nullif(to_jsonb(p)->>'grano', ''), 'escuela') = 'escuela'

    group by
        f.cve_mun,
        e.nivel,
        f.id_ciclo
)

select
    o.*,

    r.suma_indice_riesgo,
    coalesce(r.escuelas_con_prediccion, 0) as escuelas_con_prediccion,
    r.escuelas_en_riesgo,

    case when o.escuelas_con_d1 = 0 then 'SIN_DATO' else 'OK' end as cobertura_d1,
    case when o.escuelas_con_d2 = 0 then 'SIN_DATO' else 'OK' end as cobertura_d2,
    case when o.escuelas_con_d3 = 0 then 'SIN_DATO' else 'OK' end as cobertura_d3,
    case when o.escuelas_con_d4 = 0 then 'SIN_DATO' else 'OK' end as cobertura_d4,
    case when o.escuelas_con_d5 = 0 then 'SIN_DATO' else 'OK' end as cobertura_d5,
    case when o.escuelas_con_d6 = 0 then 'SIN_DATO' else 'OK' end as cobertura_d6,

    case
        when coalesce(r.escuelas_con_prediccion, 0) = 0 then 'SIN_DATO'
        else 'OK'
    end as cobertura_riesgo

from observado o
left join riesgo r
    on o.cve_mun = r.cve_mun
    and o.nivel = r.nivel
    and o.id_ciclo = r.id_ciclo
