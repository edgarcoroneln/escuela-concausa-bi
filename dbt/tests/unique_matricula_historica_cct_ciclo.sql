-- Si esta prueba devuelve filas, matricula_historica.sql tiene un cct+ciclo con mas de una
-- fila -- normalmente porque nivel (o cve_mun) vino inconsistente entre turnos del mismo cct
-- en el mismo ciclo, y el GROUP BY de matricula_historica.sql los partio en dos grupos. Mismo
-- patron que unique_matricula_cct_ciclo.sql, para el modelo AISLADO de RISK-007/DEC-007.

select
    cct,
    ciclo,
    count(*) as registros

from {{ ref('matricula_historica') }}

group by
    cct,
    ciclo

having count(*) > 1