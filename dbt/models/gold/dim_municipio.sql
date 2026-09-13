-- gold.dim_municipio (US-103) — Data_Model.md §4.2/§6. PK: cve_mun. Acotado a
-- SCOPE_ENTIDADES (Data_Model.md §7): CDMX, Edomex, Nuevo León, Jalisco.
--
-- FIX (P-03, 2026-08-31, Luis): antes la dimensión se DERIVABA de silver.rezago_municipio
-- (CONEVAL), así que solo existían los municipios que CONEVAL mide y el nombre_municipio era el
-- de esa fuente (en el fixture, el relleno "Municipio 09002"). Efecto colateral: los ocho cubos
-- con `inner join dim_municipio` borraban, sin dejar rastro, toda escuela cuyo municipio no
-- estuviera en esa lista corta. Ahora el UNIVERSO de la dimensión es el catálogo INEGI de
-- municipios (gold.geo_municipio, nombres oficiales, cargado por Carril B), acotado a
-- SCOPE_ENTIDADES; los atributos de negocio (rezago CONEVAL, población CONAPO) entran por LEFT
-- JOIN, así que donde no hay dato queda NULL/SIN_DATO explícito (Data_Model.md §3) y el
-- municipio nunca se borra. Con datos reales la dimensión pasa de ~10 filas (solo las medidas
-- por CONEVAL) a ~317 (todos los municipios de las 4 entidades), casi todas con drivers en
-- SIN_DATO: es correcto y "se ve peor antes de mejor". Aviso a Carril B: sus tableros mostrarán
-- municipios vacíos y es lo esperado.
--
-- De geo_municipio solo se toman cve_mun y nombre_municipio: son las columnas presentes en todos
-- los entornos (en prod la tabla trae además cve_ent/nombre_entidad/geometria, pero el fixture
-- local no). cve_ent se deriva por substring (INEGI: cve_mun = cve_ent(2)+local(3), correcto por
-- construcción). nombre_entidad se toma de CONEVAL por LEFT JOIN (misma fuente que hoy): CONEVAL
-- publica el índice de rezago para TODOS los municipios del país, así que cada municipio del
-- catálogo INEGI tiene su fila y su nombre_entidad. El data_test not_null de _gold__models.yml
-- verifica esa invariante y fallaría RUIDOSAMENTE (nunca en silencio, Data_Model.md §3) si algún
-- municipio de geo no tuviera CONEVAL -- señal a resolver con datos reales (item P-01), no un
-- hueco escondido.
--
-- NOTA: Data_Model.md §6 documenta nombre_municipio/nombre_entidad como originadas en DS-07,
-- pero silver.rezago_municipio (US-111, Deni) las expone como `entidad`/`municipio` a secas. El
-- nombre_municipio canónico pasa a ser el de INEGI (gold.geo_municipio); pendiente reconciliar
-- la nota de Data_Model.md §6 con Deni/Edgar.
--
-- FIX (BUG-077, 2026-09-12, Edgar Coronel / Diana Alvarez): el párrafo de arriba asumía que
-- "CONEVAL publica el índice de rezago para TODOS los municipios del país", así que
-- nombre_entidad podía tomarse de rezago_ultimo (CONEVAL) por LEFT JOIN sin riesgo. Falso en el
-- Postgres local verificado: 307 de 317 filas quedaban con nombre_entidad NULL, y
-- `MunicipioOut.nombre_entidad` es StrictStr (no admite None) -> 500 en /api/v1/municipios para
-- el 97% del universo. El data_test not_null_dim_municipio_nombre_entidad ya existía para
-- atrapar justo esto y sí falla, pero ningún workflow de CI corre `dbt test` (solo `dbt parse`),
-- así que nunca se vio antes de producción. A diferencia de población/rezago/pobreza (datos
-- reales que legítimamente pueden faltar por municipio, SIN_DATO), el nombre de la entidad NO es
-- un dato variable: las 4 SCOPE_ENTIDADES son fijas y conocidas (scope_entidades()), así que se
-- resuelve contra el catálogo propio `dim_entidad` (seed, ver _gold__seeds.yml) por cve_ent en
-- vez de heredar la cobertura parcial de una fuente externa. cve_ent se sigue derivando por
-- substring del cve_mun de INEGI (100% poblado, no depende de ningún JOIN).

with geo as (

    -- Universo de municipios = catálogo INEGI (gold.geo_municipio, Carril B), acotado a scope.
    -- Solo cve_mun + nombre_municipio: las columnas garantizadas en todos los entornos.
    select cve_mun, nombre_municipio
    from {{ source('gold_geo', 'geo_municipio') }}
    where substring(cve_mun, 1, 2) in {{ scope_entidades() }}

),

poblacion_por_municipio as (

    select
        cve_mun,
        max(anio) over (partition by cve_mun) as anio_max,
        anio,
        sum(poblacion) as poblacion_anio
    from {{ ref('poblacion_municipio') }}
    group by cve_mun, anio

),

poblacion as (

    select cve_mun, poblacion_anio as poblacion
    from poblacion_por_municipio
    where anio = anio_max

),

rezago_ultimo as (

    select
        cve_mun,
        indice_rezago_social,
        indice_rezago_social_cobertura,
        grado_rezago,
        pobreza_pct,
        row_number() over (
            partition by cve_mun order by periodo_medicion desc
        ) as _rn
    from {{ ref('rezago_municipio') }}

)

select
    g.cve_mun,
    substring(g.cve_mun, 1, 2) as cve_ent,
    g.nombre_municipio,
    e.nombre_entidad,
    p.poblacion,
    case when r.indice_rezago_social_cobertura = 'OK' then r.indice_rezago_social end
        as indice_rezago_social,
    r.grado_rezago,
    r.pobreza_pct
from geo g
left join poblacion p on p.cve_mun = g.cve_mun
left join rezago_ultimo r on r.cve_mun = g.cve_mun and r._rn = 1
left join {{ ref('dim_entidad') }} e on e.cve_ent = substring(g.cve_mun, 1, 2)
