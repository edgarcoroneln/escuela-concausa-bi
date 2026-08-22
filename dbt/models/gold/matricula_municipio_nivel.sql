-- gold.matricula_municipio_nivel -- agregado municipio x nivel x ciclo de silver.matricula_historica
-- (DS-01 distribucion HISTORICA), construido para alimentar unir_target() en
-- src/modelos/target_hibrido.py (PR #56, Hector Morales) -- mitigacion de RISK-007/DEC-007.
--
-- Grano: cve_mun x nivel x id_ciclo, un registro por combinacion -- UNIQUE, requerido por
-- unir_target(agregado, serie_target, validate="one_to_one") en target_hibrido.py (ver
-- LLAVE_AGREGADA = ("cve_mun", "nivel", "id_ciclo") en particion_temporal.py). matricula_total
-- se SUMA de todos los cct de silver.matricula_historica que caen en el mismo municipio x
-- nivel x ciclo.
--
-- Alias ciclo -> id_ciclo: mismo patron que dim_tiempo.sql y fact_escuela_ciclo.sql --
-- silver.matricula_historica expone `ciclo`, el rename al nombre que exige target_hibrido.py
-- se hace aqui, en el limite Silver->Gold.
--
-- nivel: silver.matricula_historica ya normaliza a MAYUSCULAS (ver matricula_historica.sql)
-- para hacer match exacto con gold.dim_escuela.nivel (DS-02), que target_hibrido.py exige
-- via LLAVE_AGREGADA.
--
-- SCOPE_ENTIDADES (Data_Model.md §7): aplicado aqui, en el limite Silver->Gold -- ver
-- scope_entidades.sql. silver.matricula_historica es nacional/sin filtrar, como todo Silver.

select
    cve_mun,
    nivel,
    ciclo as id_ciclo,
    sum(matricula_total) as matricula_total

from {{ source('silver', 'matricula_historica') }}

where cve_ent in {{ scope_entidades() }}

group by
    cve_mun,
    nivel,
    ciclo