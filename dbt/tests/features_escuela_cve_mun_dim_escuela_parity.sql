-- ADR-011: el municipio de features se toma de la dimensión canónica DS-02.
select
    f.cct,
    f.id_ciclo,
    f.cve_mun as cve_mun_features,
    e.cve_mun as cve_mun_dimension
from {{ ref('features_escuela') }} f
inner join {{ ref('dim_escuela') }} e on e.cct = f.cct
where f.cve_mun is distinct from e.cve_mun
