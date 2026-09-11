-- gold.features_escuela (US-104) — contrato Célula 1 -> Célula 3 (Data_Model.md §5.3/§4.4).
-- Grano: CCT x ciclo. Fuente de la llave y del target: silver.matricula (US-111, Deni).
--
-- Estado de los 6 drivers en esta primera versión:
--   D1 pobreza          -- real, silver.rezago_municipio (DS-07) por cve_mun
--   D2 inseguridad       -- real, silver.delitos_municipio (DS-04) por cve_mun, agregado
--                            SIN alinear meses al ciclo escolar todavía (simplificación
--                            documentada abajo, pendiente de refinar)
--   D3 infraestructura   -- real, silver.cemabe (DS-03) por cct, ADR-005
--   D4 conectividad      -- real, silver.cemabe (DS-03) por cct, ADR-005
--   D5 agua              -- SIN_DATO explícito: DS-06 CONAGUA (dueño Emilio Galnares Ruiz)
--                            todavía no tiene su "prueba de descarga real" completa, no hay
--                            bronze.conagua con datos todavía
--   D6 aire              -- real (2026-08-19, ADR-006, US-105): interpolación IDW de
--                            silver.aire_estacion (SINAICA) hacia cada escuela georreferenciada
--                            de dim_escuela. Radio válido 15km, potencia 2; fuera de radio ->
--                            SIN_DATO explícito
--
-- D5 en SIN_DATO no es un hueco escondido: es la regla del proyecto (Data_Model.md §3,
-- "SIN_DATO explícito, nunca cero ni nulo silencioso") aplicada honestamente a una fuente que
-- todavía no tiene datos reales. Cuando DS-06 entregue su prueba de descarga, se replica aquí
-- el mismo patrón IDW que ya tiene D6.
--
-- driver_dominante (2026-08-28, US-302): etiqueta operativa por argmax sobre D1..D6 con
-- cobertura 'OK', acordada con Andrés González Habib/C3 -- ver el comentario de la CTE
-- `con_driver_dominante` más abajo para la especificación completa.
--
-- FIX (2026-08-19, Diana): Data_Model.md §7 es explícito -- "el filtro WHERE cve_ent IN
-- SCOPE_ENTIDADES se aplica únicamente en la frontera Silver -> Gold (Y EN FEATURES/MODELOS/
-- DASHBOARDS que derivan de Gold)". Esta tabla es Gold y es justo "features" -- debía llevar
-- el filtro desde el día 1 y no lo llevaba. Corregido aquí filtrando por cve_ent de
-- silver.matricula (mismo origen ya aceptado para cve_mun en esta tabla, ver nota de arriba).

with matricula_ciclo as (

    -- NOTA (US-104, Diana): igual que en dim_tiempo.sql, Data_Model.md §5.1/§6 documenta
    -- `matricula_total`, pero silver.matricula (US-111, Deni) la entrega como `alumnos_total`.
    -- Se aliasea aquí por consistencia con el fix ya aplicado en dim_tiempo.sql; sigue pendiente
    -- reconciliar el nombre canónico con Deni/Edgar y, si aplica, actualizar Data_Model.md.
    select
        cct,
        ciclo as id_ciclo,
        cve_mun,
        alumnos_total as matricula_total,
        cast(split_part(ciclo, '-', 1) as int) as anio_inicio
    from {{ ref('matricula') }}
    where cve_ent in {{ scope_entidades() }}

),

con_target as (

    select
        *,
        lag(matricula_total) over (
            partition by cct order by anio_inicio
        ) as matricula_ciclo_anterior
    from matricula_ciclo

),

base as (

    -- Sin ciclo anterior no hay target que entrenar (es la primera observación del cct);
    -- se excluye aquí, no se rellena con 0 (evitaría una fuga de "variación cero" falsa).
    -- FIX (2026-08-31, Diana/BUG-017/BUG-019, ADR-007 ratificado 2026-08-29): target_variacion_
    -- matricula es FRACCIÓN (matricula_total/matricula_ciclo_anterior - 1.0), no diferencia
    -- absoluta de alumnos -- mismo patrón que src/modelos/target_hibrido.py::variacion_desde_serie
    -- (C3). El cast a double precision es necesario ANTES de dividir: matricula_total y
    -- matricula_ciclo_anterior son integer (silver/matricula.sql), y una división integer/integer
    -- trunca en vez de dar el decimal esperado. matricula_ciclo_anterior = 0 se rechaza EXPLÍCITO
    -- vía la división nativa de Postgres (sin nullif) -- si aparece, dbt run truena aquí en vez de
    -- convertirse en un SIN_DATO invisible (así lo pide el ADR, igual que variacion_desde_serie ya
    -- hace raise ValueError en Python).
    select
        cct,
        id_ciclo,
        cve_mun,
        matricula_total,
        (cast(matricula_total as double precision) / matricula_ciclo_anterior) - 1.0
            as target_variacion_matricula
    from con_target
    where matricula_ciclo_anterior is not null

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
            as d3_infraestructura,
        case
            when drenaje_num is not null or electricidad_num is not null
                 or sanitarios_num is not null then 'OK'
            else 'SIN_DATO'
        end as d3_cobertura,
        (coalesce(internet_num, 0) + coalesce(computadoras_num, 0))
            / nullif(
                (case when internet_num is not null then 1 else 0 end)
                + (case when computadoras_num is not null then 1 else 0 end), 0)
            as d4_conectividad,
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
                then 0.5  -- todos los municipios con el mismo valor: normalizado al centro
            else null
        end as d1_pobreza,
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
-- min-max es invariante a un escalado positivo constante -- no cambia d2_inseguridad, sólo hace
-- legible la tasa intermedia. Un municipio sin población CONAPO -> SIN_DATO explícito (nunca cero
-- ni tasa silenciosa), mismo criterio que D1 con rezago. Sigue sin alinear meses al ciclo escolar
-- (simplificación documentada, a refinar cuando haya datos reales).
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
        end as d2_inseguridad,
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
        end as d6_aire,
        'OK' as d6_cobertura
    from d6_interpolado i
    cross join d6_rango rg

),

ensamblado as (

    select
        b.cct,
        b.id_ciclo,
        b.cve_mun,
        d1.d1_pobreza,
        coalesce(d1.d1_cobertura, 'SIN_DATO') as d1_cobertura,
        d2.d2_inseguridad,
        coalesce(d2.d2_cobertura, 'SIN_DATO') as d2_cobertura,
        dd.d3_infraestructura,
        coalesce(dd.d3_cobertura, 'SIN_DATO') as d3_cobertura,
        dd.d4_conectividad,
        coalesce(dd.d4_cobertura, 'SIN_DATO') as d4_cobertura,
        cast(null as double precision) as d5_agua,
        'SIN_DATO' as d5_cobertura,
        d6.d6_aire,
        coalesce(d6.d6_cobertura, 'SIN_DATO') as d6_cobertura,
        b.target_variacion_matricula
    from base b
    left join d3_d4 dd on dd.cct = b.cct
    left join d1 on d1.cve_mun = b.cve_mun
    left join d2 on d2.cve_mun = b.cve_mun
    left join d6 on d6.cct = b.cct

),

-- driver_dominante (US-302, acordado con Andrés González Habib/C3 el 2026-08-28): etiqueta
-- OPERATIVA derivada por argmax sobre los drivers con cobertura 'OK' -- NO es una observación
-- independiente ni evidencia causal (ver advertencia en Evaluacion_Modelos.md). Misma regla
-- que ya usa `generar_driver_dominante_proxy()` en entrenar_ml02.py -- se centraliza aquí para
-- que ML-02 deje de recalcularla por su cuenta; hay una prueba de paridad contra esa función
-- en tests/test_entrenar_ml02.py::test_paridad_driver_dominante_real_contra_proxy.
--
-- Reglas (especificación de Andrés, 2026-08-28):
--   1. Solo entran drivers con valor no nulo y cobertura 'OK' (SIN_DATO queda excluido).
--   2. Desempate determinista por prioridad D1 > D2 > D3 > D4 > D5 > D6 -- `order by valor
--      desc, codigo asc` logra esto porque 'D1' < 'D2' < ... lexicográficamente.
--   3. Si ninguna fila tiene un driver elegible, driver_dominante queda NULL (nunca un driver
--      artificial) -- LEFT JOIN LATERAL preserva la fila con NULL cuando la subconsulta no
--      devuelve nada.
--   4. D3 (infraestructura) y D4 (conectividad) miden SERVICIOS PRESENTES: suben cuando la
--      escuela está MEJOR, al revés que D1/D2/D6 (que suben cuando la situación empeora). Para
--      que el argmax corone al driver que más PRESIONA (la peor situación) y no al mejor
--      servicio, D3 y D4 entran al argmax INVERTIDOS como (1 - valor). Esto SOLO afecta la
--      elección del dominante; las columnas publicadas d3_infraestructura/d4_conectividad
--      conservan su escala original (P-05, 2026-08-31). Mismo arreglo en
--      generar_driver_dominante_proxy() de entrenar_ml02.py y en el perfilado de
--      clústers de entrenar_ml03.py.
con_driver_dominante as (

    select
        e.*,
        ganador.codigo as driver_dominante
    from ensamblado e
    left join lateral (
        select codigo
        from unnest(
            array['D1', 'D2', 'D3', 'D4', 'D5', 'D6'],
            array[
                case when e.d1_cobertura = 'OK' then e.d1_pobreza::double precision end,
                case when e.d2_cobertura = 'OK' then e.d2_inseguridad::double precision end,
                -- D3/D4 invertidos (1 - valor): miden servicios presentes (alto = mejor); el
                -- argmax busca el driver que MÁS presiona, así que entra su complemento. Solo
                -- afecta la elección del dominante, no las columnas publicadas (regla 4, P-05).
                case when e.d3_cobertura = 'OK' then (1 - e.d3_infraestructura)::double precision end,
                case when e.d4_cobertura = 'OK' then (1 - e.d4_conectividad)::double precision end,
                case when e.d5_cobertura = 'OK' then e.d5_agua::double precision end,
                case when e.d6_cobertura = 'OK' then e.d6_aire::double precision end
            ]
        ) as t(codigo, valor)
        where valor is not null
        order by valor desc, codigo asc
        limit 1
    ) as ganador on true

)

select
    cct,
    id_ciclo,
    cve_mun,
    d1_pobreza,
    d2_inseguridad,
    d3_infraestructura,
    d4_conectividad,
    d5_agua,
    d6_aire,
    d1_cobertura,
    d2_cobertura,
    d3_cobertura,
    d4_cobertura,
    d5_cobertura,
    d6_cobertura,
    driver_dominante,
    (
        (case when d1_cobertura = 'OK' then 1 else 0 end)
        + (case when d2_cobertura = 'OK' then 1 else 0 end)
        + (case when d3_cobertura = 'OK' then 1 else 0 end)
        + (case when d4_cobertura = 'OK' then 1 else 0 end)
        + (case when d5_cobertura = 'OK' then 1 else 0 end)
        + (case when d6_cobertura = 'OK' then 1 else 0 end)
    ) / 6.0 as indice_completitud_drivers,
    target_variacion_matricula
from con_driver_dominante