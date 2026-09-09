{{ config(materialized='materialized_view') }}

-- US-113 / DB-03
-- Grano: una fila por cct × id_ciclo.
-- `nivel` viaja como atributo de dim_escuela; no cambia el grano.
-- ML por LEFT JOIN. Ausencia ML = cobertura explícita SIN_DATO, nunca 0.

select
    f.cct,
    f.id_ciclo,
    dt.ciclo,
    dt.anio_inicio,

    e.nombre as nombre_escuela,
    e.nivel,
    e.sostenimiento,
    e.latitud,
    e.longitud,
    e.cve_ent,
    f.cve_mun,
    dm.nombre_municipio,
    dm.nombre_entidad,

    f.matricula_total,
    f.matricula_ciclo_anterior,
    f.variacion_matricula,
    f.indice_completitud_drivers,

    f.d1,
    f.d1_cobertura,
    f.d2,
    f.d2_cobertura,
    f.d3,
    f.d3_cobertura,
    f.d4,
    f.d4_cobertura,
    f.d5,
    f.d5_cobertura,
    f.d6,
    f.d6_cobertura,

    e.agua,
    e.drenaje,
    e.electricidad,
    e.sanitarios,
    e.internet,
    e.computadoras,

    p.indice_riesgo,
    case
        when p.indice_riesgo is null then null
        else (p.indice_riesgo >= 0.5)
    end as en_riesgo,
    p.valor as variacion_proyectada,
    p.probabilidad,
    case when p.cct is null then 'SIN_DATO' else 'OK' end as cobertura_prediccion,

    r.driver_dominante,
    dd.nombre as nombre_driver,
    r.recomendacion,
    r.prioridad,
    case when r.cct is null then 'SIN_DATO' else 'OK' end as cobertura_recomendacion

from {{ ref('fact_escuela_ciclo') }} f
inner join {{ ref('dim_escuela') }} e
    on f.cct = e.cct
inner join {{ ref('dim_tiempo') }} dt
    on f.id_ciclo = dt.id_ciclo
inner join {{ ref('dim_municipio') }} dm
    on f.cve_mun = dm.cve_mun
left join {{ source('gold_ml_runtime', 'predicciones') }} p
    on f.cct = p.cct
    and f.id_ciclo = p.id_ciclo
    and p.modelo = 'ML-01'
    and coalesce(nullif(to_jsonb(p)->>'grano', ''), 'escuela') = 'escuela'
left join {{ source('gold_ml_runtime', 'recomendaciones') }} r
    on f.cct = r.cct
    and f.id_ciclo = r.id_ciclo
left join {{ ref('dim_driver') }} dd
    on r.driver_dominante = dd.id_driver
