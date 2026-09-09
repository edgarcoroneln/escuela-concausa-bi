{{ config(materialized='materialized_view') }}

-- US-113 / DB-02
-- Grano canónico ratificado en DEC-009:
-- cve_mun × nivel × id_ciclo.
--
-- Replica el contrato semántico C2:
-- riesgo ML-01 por LEFT JOIN, componentes aditivos y umbral (LINEA_DE_ALERTA) >= 0.5.
-- Sin predicciones el municipio/nivel NO desaparece:
-- riesgo queda NULL y cobertura_riesgo='SIN_DATO'.

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

        count(distinct f.cct) as escuelas,
        sum(f.matricula_total) as matricula_total,
        -- FIX (2026-08-31, Diana/BUG-031): mismo defecto y mismo fix que cubo_comparador_municipio
        -- (ver ese archivo) -- este cubo alimenta DB-02 "Mapa de riesgo", también listado como
        -- afectado.
        sum(f.matricula_ciclo_anterior) as suma_matricula_anterior

    from {{ ref('fact_escuela_ciclo') }} f
    inner join {{ ref('dim_escuela') }} e
        on f.cct = e.cct
    inner join {{ ref('dim_tiempo') }} dt
        on f.id_ciclo = dt.id_ciclo
    inner join {{ ref('dim_municipio') }} dm
        on f.cve_mun = dm.cve_mun

    group by
        f.cve_mun,
        dm.cve_ent,
        dm.nombre_municipio,
        dm.nombre_entidad,
        e.nivel,
        f.id_ciclo,
        dt.ciclo,
        dt.anio_inicio
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

    case
        when coalesce(r.escuelas_con_prediccion, 0) = 0 then 'SIN_DATO'
        else 'OK'
    end as cobertura_riesgo

from observado o
left join riesgo r
    on o.cve_mun = r.cve_mun
    and o.nivel = r.nivel
    and o.id_ciclo = r.id_ciclo
