-- =============================================================================
-- db06_cubo_predicciones  ·  DB-06 Predicciones
-- -----------------------------------------------------------------------------
-- Historia : US-204  (Manuel Alejandro Serrania Reinada, Celula 2)
--            Repunteo US-205 (Manuel Alejandro Serrania Reinada, C2)
-- Contrato : 04_UX_Design/Cube_Specs_DB06_DB09.md §3
--            KPI-01 matricula, KPI-02 variacion, KPI-05 completitud, KPI-12
--            variacion proyectada (ML-01) + contexto KPI-03/04 (riesgo).
-- Grano    : una fila por cve_mun x nivel x id_ciclo (DEC-009)
--
-- REPUNTEO A CUBOS FISICOS (US-205 / US-113): el SQL semantico ya NO agrega el
--   hecho ni une a gold.predicciones; consume DOS cubos pre-agregados de C1:
--     * gold.cubo_matricula          -> observado + proyeccion ML-01 (KPI-12)
--     * gold.cubo_riesgo_territorial -> riesgo ML-01 (KPI-03/04, contexto)
--   ambos con el MISMO grano DEC-009 (cve_mun x nivel x id_ciclo), por eso se
--   unen 1:1 sin reagregar.
--
-- POR QUE COMPONENTES Y NO PROMEDIOS (patron DEC-008/DEC-009): variacion
--   observada, completitud y proyeccion viajan como numerador y denominador por
--   separado (ya pre-agregados por C1); la razon vive en
--   metrics_db06_db09.yaml. Asi cualquier combinacion de filtros reagrega bien.
--
-- GRANO DUAL (DEC-010): C1 acota gold.predicciones al grano escuela
--   (coalesce(q.grano, 'escuela') = 'escuela') dentro de sus cubos; aqui se
--   consume ese resultado ya acotado. La proyeccion de municipio x nivel nunca
--   se reparte entre escuelas.
--
-- Reglas aplicadas: R2 (SIN_DATO nunca cero -- cobertura_prediccion del cubo),
--                   R5 (Gold ya viene acotado). R1/R3 viven en C1.
-- =============================================================================

SELECT
    -- ---------- identidad y llaves -------------------------------------------
    cm.cve_mun,
    cm.cve_ent,                                -- filtro global: entidad
    cm.nombre_municipio,
    cm.nombre_entidad,
    cm.nivel,                                  -- filtro global: nivel educativo
    cm.id_ciclo,                               -- filtro global: ciclo
    cm.ciclo,
    cm.anio_inicio,

    -- ---------- componentes aditivos: observado (KPI-01/02/05) ---------------
    cm.escuelas,
    cm.matricula_total,
    cm.variacion_x_matricula AS variacion_ponderada,  -- numerador (fraccion × matricula); unidad en YAML, R-3 DEC-012
    cm.suma_completitud,

    -- ---------- componentes aditivos: proyeccion ML-01 (KPI-12) ---------------
    cm.suma_variacion_proyectada,
    cm.escuelas_con_prediccion,
    cm.cobertura_prediccion,

    -- ---------- componentes aditivos: riesgo ML-01 (KPI-03/04) ---------------
    rt.suma_indice_riesgo,
    rt.escuelas_en_riesgo

FROM gold.cubo_matricula cm
LEFT JOIN gold.cubo_riesgo_territorial rt
    ON cm.cve_mun  = rt.cve_mun
   AND cm.nivel    = rt.nivel
   AND cm.id_ciclo = rt.id_ciclo