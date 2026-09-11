-- gold.fact_escuela_ciclo (US-103) — hecho central, Data_Model.md §4.1/§6. Grano: cct x
-- ciclo. Contiene únicamente hechos OBSERVADOS (nunca salidas de ML: indice_riesgo vive en
-- gold.predicciones, driver_dominante en gold.recomendaciones -- se consultan por JOIN).
--
-- Acotado a SCOPE_ENTIDADES (Data_Model.md §7) heredado del INNER JOIN contra dim_escuela
-- (que ya viene filtrada) -- no se repite el filtro aquí, un solo lugar de verdad.
--
-- cve_mun se toma de dim_escuela (origen documentado DS-02, Data_Model.md §6), NO de
-- silver.matricula directamente -- a diferencia de gold.features_escuela (US-104), que por ser
-- tabla de entrenamiento ML tomó cve_mun de DS-01 como simplificación aceptada en su momento.
--
-- D1-D4 replican la misma lógica real que gold.features_escuela (mismas fuentes Silver,
-- mismo ADR-005 para D3/D4). D6 aire ya es real (ADR-006, US-105): interpolación IDW de
-- silver.aire_estacion (SINAICA) hacia cada escuela georreferenciada de dim_escuela. D5
-- agua sigue en SIN_DATO explícito: DS-06 CONAGUA (dueño Emilio Galnares Ruiz) todavía no
-- tiene su "prueba de descarga real" completa, no hay bronze.conagua con datos todavía.

with matricula_ciclo as (

    -- NOTA (US-103, Diana): mismo alias que en dim_tiempo.sql/features_escuela --
    -- Data_Model.md documenta `matricula_total`, silver.matricula la entrega como
    -- `alumnos_total`. Pendiente reconciliar el nombre canónico con Deni/Edgar.
    select
        cct,
        ciclo as id_ciclo,
        alumnos_total as matricula_total,
        cast(split_part(ciclo, '-', 1) as int) as anio_inicio
    from {{ ref('matricula') }}

),

con_anterior as (

    select
        *,
        lag(matricula_total) over (
            partition by cct order by anio_inicio
        ) as matricula_ciclo_anterior
    from matricula_ciclo

),

base as (

    -- FIX (2026-08-31, Diana/BUG-031): se expone matricula_ciclo_anterior -- ya se calculaba en
    -- con_anterior pero se descartaba aquí. C2 (Marina/Manuel) lo necesita para corregir KPI-02
    -- (DB-01/02/03/04/06/09) a razón de sumas -- SUM(matricula_total)/SUM(matricula_ciclo_anterior)
    -- - 1 -- en vez del promedio ponderado de "alumnos absolutos" que hoy renderiza mal como %.
    select
        cct,
        id_ciclo,
        matricula_total,
        matricula_ciclo_anterior,
        cast(matricula_total - matricula_ciclo_anterior as double precision)
            as variacion_matricula
    from con_anterior
    where matricula_ciclo_anterior is not null

),

escuela_scope as (

    -- ya viene acotada a SCOPE_ENTIDADES: el join de abajo es lo que restringe el grano
    select cct, cve_mun
    from {{ ref('dim_escuela') }}

),

con_municipio as (

        select
        b.cct,
        b.id_ciclo,
        e.cve_mun,
        b.matricula_total,
        b.matricula_ciclo_anterior,
        b.variacion_matricula
    from base b
    inner join escuela_scope e on e.cct = b.cct
),

-- D3/D4: infraestructura y conectividad, CEMABE por CCT (ADR-005)
cemabe_binarios as (

    select
        cct,
        case when drenaje in ('0', '1') then drenaje::numeric end as drenaje_num,
        case when electricidad in ('0', '1') then electricidad::numeric end as electricidad_num,
        case when sanitarios in ('0', '1') then sanitarios::numeric end as sanitarios_num,
        case when internet in ('0', '1') then internet::numeric end as internet_num,
        case when computadoras in ('0', '1') then computadoras::numeric end as computadoras_num
    from {{ ref('cemabe') }}

),

d3_d4 as (

    select
        cct,
        (coalesce(drenaje_num, 0) + coalesce(electricidad_num, 0) + coalesce(sanitarios_num, 0))
            / nullif(
                (case when drenaje_num is not null then 1 else 0 end)
                + (case when electricidad_num is not null then 1 else 0 end)
                + (case when sanitarios_num is not null then 1 else 0 end), 0)
            as d3,
        case
            when drenaje_num is not null or electricidad_num is not null
                 or sanitarios_num is not null then 'OK'
            else 'SIN_DATO'
        end as d3_cobertura,
        (coalesce(internet_num, 0) + coalesce(computadoras_num, 0))
            / nullif(
                (case when internet_num is not null then 1 else 0 end)
                + (case when computadoras_num is not null then 1 else 0 end), 0)
            as d4,
        case
            when internet_num is not null or computadoras_num is not null then 'OK'
            else 'SIN_DATO'
        end as d4_cobertura
    from cemabe_binarios

),

-- D1: pobreza y rezago social, CONEVAL por municipio, último periodo_medicion disponible
rezago_ultimo as (

    select
        cve_mun,
        indice_rezago_social,
        indice_rezago_social_cobertura,
        row_number() over (
            partition by cve_mun order by periodo_medicion desc
        ) as _rn
    from {{ ref('rezago_municipio') }}

),

rezago_rango as (

    select min(indice_rezago_social) as min_val, max(indice_rezago_social) as max_val
    from rezago_ultimo
    where _rn = 1 and indice_rezago_social_cobertura = 'OK'

),

d1 as (

    select
        r.cve_mun,
        case
            when r.indice_rezago_social_cobertura = 'OK' and rg.max_val > rg.min_val
                then (r.indice_rezago_social - rg.min_val) / (rg.max_val - rg.min_val)
            when r.indice_rezago_social_cobertura = 'OK'
                then 0.5
            else null
        end as d1,
        r.indice_rezago_social_cobertura as d1_cobertura
    from rezago_ultimo r
    cross join rezago_rango rg
    where r._rn = 1

),

-- D2: inseguridad, SESNSP por municipio.
-- FIX (P-10, 2026-08-31, Luis): antes se normalizaba min-max sobre `sum(conteo)` CRUDO, así que
-- el índice ordenaba TAMAÑO de municipio (más habitantes -> más delitos absolutos), no
-- inseguridad. Ahora se convierte a una TASA comparable ANTES de normalizar: delitos por 100 000
-- habitantes y por mes observado. Se divide entre la población municipal (DS-08 CONAPO, sumada
-- sobre grupo_edad y último año disponible, mismo criterio que dim_municipio.sql) y entre los
-- meses con datos de ese municipio (así un municipio con 12 meses observados no se ve "más
-- inseguro" que uno con 3 sólo por acumular más meses). El factor 100 000 es cosmético: el
-- min-max es invariante a un escalado positivo constante -- no cambia d2, sólo hace legible la
-- tasa intermedia. Un municipio sin población CONAPO -> SIN_DATO explícito (nunca cero ni tasa
-- silenciosa), mismo criterio que D1 con rezago. Sigue sin alinear meses al ciclo escolar (misma
-- simplificación documentada en features_escuela).
poblacion_municipal as (

    -- Población total del municipio: se suma sobre grupo_edad y se toma el último año disponible
    -- (mismo criterio que dim_municipio.sql).
    select cve_mun, poblacion_anio as poblacion
    from (
        select
            cve_mun,
            anio,
            sum(poblacion) as poblacion_anio,
            max(anio) over (partition by cve_mun) as anio_max
        from {{ ref('poblacion_municipio') }}
        group by cve_mun, anio
    ) t
    where anio = anio_max

),

delitos_por_municipio as (

    select
        cve_mun,
        sum(conteo) as conteo_total,
        count(distinct (anio, mes)) as meses_con_datos
    from {{ ref('delitos_municipio') }}
    group by cve_mun

),

delitos_tasa as (

    -- delitos por 100 000 habitantes por mes observado; NULL = SIN_DATO (sin población o sin meses)
    select
        d.cve_mun,
        case
            when p.poblacion > 0 and d.meses_con_datos > 0
                then d.conteo_total * 100000.0 / p.poblacion / d.meses_con_datos
        end as tasa
    from delitos_por_municipio d
    left join poblacion_municipal p on p.cve_mun = d.cve_mun

),

delitos_rango as (

    select min(tasa) as min_val, max(tasa) as max_val
    from delitos_tasa
    where tasa is not null

),

d2 as (

    select
        t.cve_mun,
        case
            when t.tasa is null then null
            when dr.max_val > dr.min_val
                then (t.tasa - dr.min_val) / cast(dr.max_val - dr.min_val as double precision)
            else 0.5
        end as d2,
        case when t.tasa is null then 'SIN_DATO' else 'OK' end as d2_cobertura
    from delitos_tasa t
    cross join delitos_rango dr

),

-- FIX (2026-08-22, hallazgo de Luis García en PR #63, US-123b/TEST-010): 21 de 384 estaciones
-- traen el placeholder literal "0.0" en latitud/longitud en vez de un SIN_DATO explícito. El
-- filtro de radio (distancia_km <= 15) ya las descartaba de facto -- ninguna escuela de México
-- cae a <15km de (0,0), frente a la costa de África -- pero era "correcto de casualidad", no
-- por diseño. Se filtran aquí explícitamente para no depender de la geografía (Data_Model.md
-- §3: "SIN_DATO explícito, nunca cero ni nulo silencioso").
aire_pm25 as (

    select
        id_estacion,
        max(latitud) as latitud,
        max(longitud) as longitud,
        avg(valor) as pm25_promedio
    from {{ ref('aire_estacion') }}
    where parametro = 'PM2.5' and dato_valido = 1
        and latitud is not null and longitud is not null
        and latitud != 0 and longitud != 0
    group by id_estacion

),

escuela_geo as (

    select cct, latitud, longitud
    from {{ ref('dim_escuela') }}
    where latitud is not null and longitud is not null

),

-- Haversine: distancia en km entre cada escuela georreferenciada y cada estación con PM2.5
-- válido. El join se acota por caja geográfica (ver el `join ... between` de abajo) para no
-- materializar el producto cruzado completo cuando entren los datos reales.
distancias_aire as (

    select
        e.cct,
        a.pm25_promedio,
        6371 * acos(least(1.0, greatest(-1.0,
            cos(radians(e.latitud)) * cos(radians(a.latitud))
                * cos(radians(a.longitud) - radians(e.longitud))
            + sin(radians(e.latitud)) * sin(radians(a.latitud))
        ))) as distancia_km
    from escuela_geo e
    -- Acota por caja de ±0.2° lat/lon ANTES del Haversine: con datos reales el producto cruzado
    -- (~230 000 escuelas × 384 estaciones ≈ 88 M de pares) no termina. La caja es un superconjunto
    -- EXACTO del disco de 15 km en todo México (a 33°N, 0.2° de longitud ≈ 18.7 km > 15 km), así
    -- que el `where distancia_km <= 15` de dentro_radio_aire da un resultado idéntico al del cross
    -- join, evaluando muchísimos menos pares.
    join aire_pm25 a
        on a.latitud between e.latitud - 0.2 and e.latitud + 0.2
        and a.longitud between e.longitud - 0.2 and e.longitud + 0.2

),

dentro_radio_aire as (

    select
        cct,
        pm25_promedio,
        distancia_km,
        -- evita división entre cero si una escuela cae justo sobre una estación
        greatest(distancia_km, 0.001) as distancia_km_adj
    from distancias_aire
    where distancia_km <= 15

),

d6_interpolado as (

    select
        cct,
        sum(pm25_promedio / power(distancia_km_adj, 2)) / sum(1.0 / power(distancia_km_adj, 2))
            as d6_valor,
        min(distancia_km) as distancia_min_km
    from dentro_radio_aire
    group by cct

),

d6_rango as (

    select min(d6_valor) as min_val, max(d6_valor) as max_val
    from d6_interpolado

),

d6 as (

    select
        i.cct,
        case
            when rg.max_val > rg.min_val then (i.d6_valor - rg.min_val) / (rg.max_val - rg.min_val)
            else 0.5
        end as d6,
        'OK' as d6_cobertura
    from d6_interpolado i
    cross join d6_rango rg

),
ensamblado as (

    select
        cm.cct,
        cm.id_ciclo,
        cm.cve_mun,
        cm.matricula_total,
        cm.matricula_ciclo_anterior,
        cm.variacion_matricula,
        d1.d1,
        coalesce(d1.d1_cobertura, 'SIN_DATO') as d1_cobertura,
        d2.d2,
        coalesce(d2.d2_cobertura, 'SIN_DATO') as d2_cobertura,
        dd.d3,
        coalesce(dd.d3_cobertura, 'SIN_DATO') as d3_cobertura,
        dd.d4,
        coalesce(dd.d4_cobertura, 'SIN_DATO') as d4_cobertura,
        cast(null as double precision) as d5,
        'SIN_DATO' as d5_cobertura,
        d6.d6,
        coalesce(d6.d6_cobertura, 'SIN_DATO') as d6_cobertura
    from con_municipio cm
    left join d3_d4 dd on dd.cct = cm.cct
    left join d1 on d1.cve_mun = cm.cve_mun
    left join d2 on d2.cve_mun = cm.cve_mun
    left join d6 on d6.cct = cm.cct

)

select
    cct,
    id_ciclo,
    cve_mun,
    matricula_total,
    matricula_ciclo_anterior,
    variacion_matricula,
    (
        (case when d1_cobertura = 'OK' then 1 else 0 end)
        + (case when d2_cobertura = 'OK' then 1 else 0 end)
        + (case when d3_cobertura = 'OK' then 1 else 0 end)
        + (case when d4_cobertura = 'OK' then 1 else 0 end)
        + (case when d5_cobertura = 'OK' then 1 else 0 end)
        + (case when d6_cobertura = 'OK' then 1 else 0 end)
    ) / 6.0 as indice_completitud_drivers,
    d1,
    d2,
    d3,
    d4,
    d5,
    d6,
    d1_cobertura,
    d2_cobertura,
    d3_cobertura,
    d4_cobertura,
    d5_cobertura,
    d6_cobertura
from ensamblado