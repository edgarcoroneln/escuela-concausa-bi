-- =============================================================================
-- db09_cubo_recomendaciones  ·  DB-09 Recomendaciones prescriptivas
-- -----------------------------------------------------------------------------
-- Historia : US-204  (Manuel Alejandro Serrania Reinada, Celula 2)
--            Repunteo US-205 (Manuel Alejandro Serrania Reinada, C2)
-- Contrato : 04_UX_Design/Cube_Specs_DB06_DB09.md  (DOC-CUBESPEC-DB0609, §5.1/§5.2/§5.3)
-- Grano    : una fila por cct x id_ciclo (detalle)
--
-- REPUNTEO A CUBOS FISICOS (US-205 / US-113): passthrough de
--   gold.cubo_recomendaciones (C1). Covariancias del cubo (ver
--   dbt/models/gold/cubo_recomendaciones.sql):
--     * varianza flechada: driver_dominante / nombre_driver / recomendacion /
--       prioridad vienen de gold.recomendaciones, mientras que la fila en si
--       existe por LATENCY (UNION 08 -- escuelas sin triangulacion). Por eso
--       aqui se etiquetan SQL NULL como 'SIN_DATO' (R2) y como designador v1 el
--       cubo preserva driver_clave AS driver_dominante.
--     * valor 0 real vs SIN_DATO: pct_escuelas_recomendadas =
--       SUM(recomendacion_emitida)/COUNT(DISTINCT cct) (KPI-07).
--
-- Lo unico que falta en el cubo C1 es la salida ML-01 (indice/en_riesgo) para
--   el ranking de urgencia (AC-010.0): aqui NO se re-agrega el hecho ni se
--   duplica la llave -- se hace el mismo LEFT JOIN de C1 contra gold.predicciones
--   (llave cct-id_ciclo, modelo 'ML-01', grano escuela) y la razon KPI-03 la
--   recalcula el motor. cobertura_prediccion hace explícitas las filas sin
--   prediccion (nunca se inventa es_riesgo).
--
-- Reglas aplicadas: R1 (salidas de ML por LEFT JOIN, aqui y en C1), R2 (SIN_DATO
--                   nunca cero -- 'SIN_DATO' literal y cobertura), R3 (en_riesgo
--                   derivado con la misma cota del contrato debajo), R5 (Gold
--                   acotado). Sin GROUP BY: detalle.
-- =============================================================================

SELECT
    -- ---------- identidad y llaves -------------------------------------------
    cr.cct,
    cr.id_ciclo,                               -- filtro global: ciclo
    cr.ciclo,
    cr.anio_inicio,
    cr.nombre_escuela,
    cr.nivel,                                  -- filtro global: nivel educativo
    cr.sostenimiento,
    cr.cve_ent,                                -- filtro global: entidad
    cr.cve_mun,                                -- filtro: municipio
    cr.nombre_municipio,
    cr.nombre_entidad,

    -- ---------- contexto observado --------------------------------------------
    cr.matricula_total,
    cr.driver_dominante,                       -- clave del driver (designador v1)
    COALESCE(cr.nombre_driver, 'SIN_DATO')     AS nombre_driver,
    cr.recomendacion,
    cr.prioridad,                              -- ALTA/MEDIA/BAJA (chart por prioridad)
    cr.cobertura_recomendacion,                -- OK / SIN_DATO (ML-02)

    -- ---------- progreso de ML-02 (KPI-07) ------------------------------------
    cr.recomendacion_emitida,                  -- 1 si hay recomendacion

    -- ---------- ranking de urgencia (AC-010.0): riesgo ML-01 por LEFT JOIN ----
    p.indice_riesgo,
    CASE
        WHEN p.indice_riesgo IS NULL THEN NULL     -- sin prediccion: desconocido
        WHEN p.indice_riesgo >= 0.5   THEN TRUE    -- DEC-019: linea de alerta
        ELSE FALSE
    END                                          AS en_riesgo,
    CASE
        WHEN p.cct IS NULL THEN 'SIN_DATO'
        ELSE 'OK'
    END                                          AS cobertura_prediccion

FROM gold.cubo_recomendaciones cr
LEFT JOIN gold.predicciones p
    ON cr.cct     = p.cct
   AND cr.id_ciclo = p.id_ciclo
   AND p.modelo    = 'ML-01'
   AND (p.grano IS NULL OR p.grano = 'escuela')