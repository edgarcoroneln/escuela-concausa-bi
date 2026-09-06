-- Componentes de KPI-03/04/10 coinciden con ML-01.
with esperado as (
    select
        f.cve_mun,
        e.nivel,
        f.id_ciclo,
        sum(p.indice_riesgo) as suma_indice_riesgo,
        count(*) as escuelas_con_prediccion,
        count(*) filter (where p.indice_riesgo >= 0.5) as escuelas_en_riesgo
    from {{ ref('fact_escuela_ciclo') }} f
    inner join {{ ref('dim_escuela') }} e on f.cct = e.cct
    inner join {{ source('gold_ml_runtime', 'predicciones') }} p
        on f.cct = p.cct
        and f.id_ciclo = p.id_ciclo
        and p.modelo = 'ML-01'
        and coalesce(nullif(to_jsonb(p)->>'grano', ''), 'escuela') = 'escuela'
    group by f.cve_mun, e.nivel, f.id_ciclo
)
select
    e.cve_mun, e.nivel, e.id_ciclo
from esperado e
left join {{ ref('cubo_riesgo_territorial') }} c
    on e.cve_mun = c.cve_mun
    and e.nivel = c.nivel
    and e.id_ciclo = c.id_ciclo
where c.cve_mun is null
   or abs(c.suma_indice_riesgo - e.suma_indice_riesgo) > 0.0000001
   or c.escuelas_con_prediccion <> e.escuelas_con_prediccion
   or c.escuelas_en_riesgo <> e.escuelas_en_riesgo
