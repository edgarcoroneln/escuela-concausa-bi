-- silver.matricula_historica (DS-01, distribucion HISTORICA multi-ciclo) -- mitigacion de
-- RISK-007/DEC-007. AISLADO de silver.matricula (ciclo unico 2024-2025) -- ver
-- src/ingesta/extractor_formato911_historico.py y bronze.formato911_historico.
--
-- Grano de bronze: cct x ciclo x turno. insc_t es matricula POR TURNO, no por escuela --
-- confirmado con datos reales del ciclo 2024-2025 (3,388 cct con >1 turno y valores de insc_t
-- distintos entre turnos, ver DevLog 2026-08-21). Por eso aqui se SUMA por turno para obtener
-- la matricula total real de la escuela en el ciclo.
--
-- nivel se normaliza a MAYUSCULAS (UPPER(TRIM())) para hacer match con gold.dim_escuela.nivel
-- (DS-02), que no se homologa en su propio modelo Silver -- ver silver/escuela.sql.
--
-- Se deja la columna como `ciclo` (no `id_ciclo`): mismo nombre que ya expone silver.matricula
-- hoy (ver nota en dim_tiempo.sql sobre esta ambiguedad pendiente de reconciliar). El cambio a
-- `id_ciclo` que exige unir_target() se hace en Gold, igual que ya hace dim_tiempo.sql.

with normalizado as (

    select
        cct,
        ciclo,
        turno,
        {{ normalize_cve_ent('entidad') }} as cve_ent,
        {{ normalize_cve_mun('entidad', 'municipio') }} as cve_mun,
        upper(trim(nivel)) as nivel,
        matricula_total,
        _ingested_at

    from {{ source('bronze', 'formato911_historico') }}

),

deduplicado as (

    select *,
        row_number() over (
            partition by cct, ciclo, turno
            order by _ingested_at desc
        ) as _row_number

    from normalizado

),

por_turno as (

    select cct, ciclo, cve_ent, cve_mun, nivel, matricula_total
    from deduplicado
    where _row_number = 1

)

select
    cct,
    ciclo,
    cve_ent,
    cve_mun,
    nivel,
    sum(matricula_total) as matricula_total

from por_turno
group by cct, ciclo, cve_ent, cve_mun, nivel