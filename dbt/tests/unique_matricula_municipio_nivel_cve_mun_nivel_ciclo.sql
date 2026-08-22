-- Si esta prueba devuelve filas, matricula_municipio_nivel.sql tiene un cve_mun+nivel+id_ciclo
-- con mas de una fila -- esto rompe unir_target(..., validate="one_to_one") en
-- target_hibrido.py (PR #56, Hector Morales), que exige exactamente una fila por esa llave.
-- Mismo patron que unique_fact_escuela_ciclo_cct_ciclo.sql / unique_features_escuela_cct_ciclo.sql.

select
    cve_mun,
    nivel,
    id_ciclo,
    count(*) as registros

from {{ ref('matricula_municipio_nivel') }}

group by
    cve_mun,
    nivel,
    id_ciclo

having count(*) > 1