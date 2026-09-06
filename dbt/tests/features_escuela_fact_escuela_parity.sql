-- ADR-011: ambos productos Gold deben compartir exactamente el universo CCT x ciclo.
select
    coalesce(f.cct, h.cct) as cct,
    coalesce(f.id_ciclo, h.id_ciclo) as id_ciclo
from {{ ref('features_escuela') }} f
full outer join {{ ref('fact_escuela_ciclo') }} h
    on f.cct = h.cct
    and f.id_ciclo = h.id_ciclo
where f.cct is null
   or h.cct is null
