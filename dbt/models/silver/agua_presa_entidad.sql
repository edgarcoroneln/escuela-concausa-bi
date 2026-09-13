-- silver.agua_presa_entidad (D5 v1, US-121a/US-122a, DS-06 CONAGUA) — grano: cve_ent.
--
-- CONTEXTO: DS-06 (CONAGUA/IMTA, dueño Emilio Galnares Ruiz) ya tiene datos reales de presas
-- en bronze.conagua_presas (180 presas, GE 7/7), pero el contrato Silver histórico
-- (models/silver/agua_region.sql) espera un esquema diario/georreferenciado por
-- id_estacion/región hidrológica que ese endpoint NO trae -- por eso D5 seguía en SIN_DATO
-- explícito (ver sources.yml, DS-06_CONAGUA_SINA.md §11). Este modelo NO reemplaza esa
-- decisión ni ese archivo -- es una vía alterna v1, más simple, que sí se puede construir hoy
-- con lo que la fuente real sí trae: capacidad instalada de presas (cap_namo) por estado.
--
-- LIMITACIONES CONOCIDAS DE ESTE v1 (léase antes de aprobar/mergear -- PENDIENTE de revisión
-- de Edgar por tocar gold.fact_escuela_ciclo, y de Emilio por ser el dueño de DS-06):
--   1. Es un proxy de INFRAESTRUCTURA INSTALADA (capacidad NAMO en hm3), no de estrés hídrico
--      real -- no hay serie de tiempo de volumen almacenado ni datos de demanda/población en
--      bronze.conagua_presas (el endpoint solo trae el listado con capacidad, no el histórico
--      "Vol. de almacenamiento" por año que sí documenta DS-06_CONAGUA_SINA.md §9 a nivel
--      detalle-por-presa -- ese detalle no se extrajo, ver extractor_conagua.py).
--   2. La columna `estado` de CONAGUA es texto, no cve_ent -- se cruza contra el seed nacional
--      dim_estado_inegi (verificado contra los 26 nombres reales, ver ese seed).
--   3. Ciudad de México (09) NO tiene presas propias en absoluto en bronze.conagua_presas (su
--      agua viene de fuera de su territorio) -- se le asignan explícitamente las 3 presas del
--      Sistema Cutzamala (Valle de Bravo y Villa Victoria en Edomex, El Bosque en Michoacán)
--      vía el seed dim_presa_cutzamala, decisión de modelado explícita y documentada ahí, NO
--      inferida geoespacialmente. Esas mismas 2 presas de Edomex por lo tanto cuentan tanto
--      para 15 (Edomex) como para 09 (CDMX) -- es intencional: es agua compartida, no un error
--      de doble conteo.
--   4. Dirección del índice: igual que D1/D2, MAYOR d5 = MAYOR riesgo/estrés (no mayor
--      disponibilidad) -- se invierte la capacidad normalizada para que sea comparable.
--   5. Bronze/Silver nacionales (Data_Model.md §7): este modelo no filtra a SCOPE_ENTIDADES,
--      igual que el resto de Silver -- el recorte pasa en gold.fact_escuela_ciclo.

with presas_dedup as (

    -- bronze.conagua_presas puede traer más de un snapshot de carga (distintos _ingested_at)
    -- -- mismo patrón de deduplicación que ya usa (el hoy inactivo)
    -- models/silver/agua_region.sql.
    select *,
        row_number() over (
            partition by id_presa order by _ingested_at desc
        ) as _row_number
    from {{ source('bronze', 'conagua_presas') }}

),

presas as (

    select
        id_presa,
        nombre_oficial,
        estado,
        cast(cap_namo as double precision) as cap_namo
    from presas_dedup
    where _row_number = 1

),

-- Asignación por texto de estado (nacional, ver dim_estado_inegi).
asignacion_directa as (

    select p.id_presa, p.cap_namo, ie.cve_ent
    from presas p
    inner join {{ ref('dim_estado_inegi') }} ie on ie.estado = p.estado

),

-- Asignación explícita Cutzamala -> CDMX (ver seeds/dim_presa_cutzamala.csv y nota #3 arriba).
asignacion_cutzamala as (

    select p.id_presa, p.cap_namo, c.cve_ent_abastece as cve_ent
    from presas p
    inner join {{ ref('dim_presa_cutzamala') }} c on c.id_presa = p.id_presa

),

asignaciones as (

    select * from asignacion_directa
    union all
    select * from asignacion_cutzamala

),

capacidad_entidad as (

    select
        cve_ent,
        count(distinct id_presa) as presas_total,
        sum(cap_namo) as capacidad_namo_total_hm3
    from asignaciones
    group by cve_ent

),

rango as (

    select min(capacidad_namo_total_hm3) as min_val, max(capacidad_namo_total_hm3) as max_val
    from capacidad_entidad

)

select
    ce.cve_ent,
    ce.presas_total,
    ce.capacidad_namo_total_hm3,
    case
        when r.max_val > r.min_val
            then 1 - (ce.capacidad_namo_total_hm3 - r.min_val) / (r.max_val - r.min_val)
        else 0.5
    end as indice_estres_hidrico_infraestructura,
    'OK' as cobertura
from capacidad_entidad ce
cross join rango r
