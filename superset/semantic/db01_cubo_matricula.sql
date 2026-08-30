-- =============================================================================
-- db01_cubo_matricula  ·  DB-01 Ejecutivo
-- -----------------------------------------------------------------------------
-- Historia   : US-205  (Manuel Alejandro Serrania Reinada, Celula 2 - Analytics & BI)
-- Contrato   : 04_UX_Design/Screen_Specs.md §2 (cubo de DB-01) y §4 (KPI-01/02/05)
-- Grano      : una fila por cve_mun x nivel x id_ciclo
--
-- REPUNTEO A CUBOS FISICOS (US-205 / US-113): el SQL semantico ya NO agrega el
--   hecho; consume gold.cubo_matricula (Grano DEC-009, C1). La capa semantica
--   solo anade enrich fino: el nombre oficial INEGI del municipio.
--
-- POR QUE COMPONENTES Y NO PROMEDIOS (patron DEC-008): la variacion ponderada y
--   la completitud viajan como numerador y denominador por separado (ya
--   pre-agregados por el cubo); la razon vive en metrics_db01_db02.yaml. Asi
--   cualquier combinacion de los filtros globales (AC-002.2) reagrega bien.
--
-- NOMBRE OFICIAL DEL MUNICIPIO: gold.dim_municipio sigue siendo la dimension
--   canonica, pero mientras C1 no cargue el catalogo real de DS-02 sus nombres
--   son placeholders del fixture ("Municipio 09002"). El GeoJSON versionado ya
--   trajo el nombre oficial INEGI a gold.geo_municipio, asi que se prefiere ese
--   y queda cm.nombre_municipio como fallback. Cuando C1 cargue nombres reales,
--   este COALESCE puede invertirse (o desaparecer) sin tocar los tableros.
--
-- Reglas aplicadas: R2 (SIN_DATO nunca cero), R5 (Gold ya viene acotado).
--   R1/R3 no aplican: DB-01 solo expone hechos observados, sin salidas de ML.
-- =============================================================================

SELECT
    -- ---------- identidad y llaves -------------------------------------------
    cm.cve_mun,
    cm.cve_ent,                                -- filtro global: entidad
    COALESCE(g.nombre_municipio, cm.nombre_municipio) AS nombre_municipio,
    cm.nombre_entidad,
    cm.nivel,                                  -- filtro global: nivel educativo
    cm.id_ciclo,                               -- filtro global: ciclo
    cm.ciclo,
    cm.anio_inicio,

    -- ---------- componentes aditivos (pre-agregados por el cubo C1) ----------
    cm.escuelas,
    cm.matricula_total,
    cm.variacion_x_matricula AS variacion_ponderada,  -- numerador (fraccion × matricula); unidad en YAML, R-3 DEC-012
    cm.suma_completitud

FROM gold.cubo_matricula cm
LEFT JOIN gold.geo_municipio g ON cm.cve_mun = g.cve_mun