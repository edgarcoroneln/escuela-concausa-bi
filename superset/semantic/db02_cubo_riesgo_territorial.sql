-- =============================================================================
-- db02_cubo_riesgo_territorial  ·  DB-02 Mapa de riesgo territorial
-- -----------------------------------------------------------------------------
-- Historia   : US-205  (Manuel Alejandro Serrania Reinada, Celula 2 - Analytics & BI)
-- Contrato   : 04_UX_Design/Screen_Specs.md §2 (cubo de DB-02) y §4 (KPI-03/04/10)
-- Grano      : una fila por cve_mun x nivel x id_ciclo
--
-- REPUNTEO A CUBOS FISICOS (US-205 / US-113): el SQL semantico ya NO agrega el
--   hecho ni une a gold.predicciones; consume gold.cubo_riesgo_territorial
--   (Grano DEC-009, C1), donde C1 ya resolvio la salida de ML-01 por LEFT JOIN
--   con la llave completa (cct, id_ciclo), el filtro de modelo 'ML-01' y el
--   umbral R3 (>= 0.6). La capa semantica solo anade el enrich del nombre
--   oficial INEGI del municipio.
--
-- Los componentes de riesgo (suma_indice_riesgo, escuelas_con_prediccion,
--   escuelas_en_riesgo) y la bandera cobertura_riesgo viajan del cubo tal cual:
--   R2 se cumple en C1 (ausencia de predicciones = cobertura 'SIN_DATO', nunca
--   riesgo cero).
--
-- Reglas aplicadas: R2 (SIN_DATO nunca cero), R5 (Gold ya viene acotado).
--   R1/R3 viven en el cubo C1 (por eso ya no aparecen aqui).
--
-- NOMBRE OFICIAL DEL MUNICIPIO: igual que db01_cubo_matricula — el nombre
--   oficial INEGI vive en gold.geo_municipio mientras dim_municipio trae los
--   placeholders del fixture de C1; se prefiere el oficial con fallback.
-- =============================================================================

SELECT
    -- ---------- identidad y llaves -------------------------------------------
    rt.cve_mun,
    rt.cve_ent,                                -- filtro global: entidad
    COALESCE(g.nombre_municipio, rt.nombre_municipio) AS nombre_municipio,
    rt.nombre_entidad,
    rt.nivel,                                  -- filtro global: nivel educativo
    rt.id_ciclo,                               -- filtro global: ciclo
    rt.ciclo,
    rt.anio_inicio,

    -- ---------- contexto para tooltips / ranking (del cubo C1) ---------------
    rt.escuelas,
    rt.matricula_total,
    rt.variacion_x_matricula AS variacion_ponderada,  -- numerador (fraccion × matricula); unidad en YAML, R-3 DEC-012

    -- ---------- componentes aditivos: riesgo (ML-01, resuelto por C1) --------
    rt.suma_indice_riesgo,
    rt.escuelas_con_prediccion,
    rt.escuelas_en_riesgo,                     -- ya acotado al umbral R3
    rt.cobertura_riesgo

FROM gold.cubo_riesgo_territorial rt
LEFT JOIN gold.geo_municipio g ON rt.cve_mun = g.cve_mun