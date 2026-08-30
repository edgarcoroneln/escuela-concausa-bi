-- =============================================================================
-- db06_predicciones_escuela  ·  DB-06 Predicciones (tab de escuela)
-- -----------------------------------------------------------------------------
-- Historia : US-204  (Manuel Alejandro Serrania Reinada, Celula 2)
--            Repunteo US-205 (Manuel Alejandro Serrania Reinada, C2)
-- Contrato : 04_UX_Design/Cube_Specs_DB06_DB09.md §3.2
--            Filtros: cct, nombre, nivel, sostenimiento, cve_mun (AC-005.x).
-- Grano    : una fila por cct x id_ciclo (detalle, sin agregar)
--
-- REPUNTEO A CUBOS FISICOS (US-205 / US-113): passthrough 1:1 de
--   gold.cubo_escuela_360 (C1), que ya trae la salida ML-01 resuelta por
--   LEFT JOIN (llave cct-id_ciclo, modelo 'ML-01', grano escuela, umbral R3).
--   La unica logica restante es el BUCKET del indice de riesgo (rango_riesgo),
--   que la toxicologia de Superset no expone y los tableros piden al detalle
--   granular (superset/dashboards/db06_predicciones.yaml -> rango_riesgo).
--
-- PEQUEÑA DESVIACION A R3 (ratificada 2026-08-19): en_riesgo es una DERIVADA
--   del cubo, no una salida cruda de ML; el cubo la calcula con las mismas
--   cotas del contrato (>= 0.6) y aqui se re-etiqueta solo la columna. La
--   columna cruda indice_riesgo continua intacta. (La razon 'en_riesgo' de
--   metrics_db06_db09.yaml la recalcula el motor por KPI-03.)
--
-- Reglas aplicadas: R2 (SIN_DATO nunca cero -- cobertura_prediccion del cubo),
--                   R5 (Gold ya viene acotado). R1/R3 viven en C1.
-- Sin GROUP BY: se esta al grano del detalle.
-- =============================================================================

SELECT
    -- ---------- identificadores -------------------------------------------------
    s.cct,
    s.id_ciclo,                               -- filtro global: ciclo
    s.ciclo,
    s.anio_inicio,
    s.nombre_escuela,
    s.nivel,                                  -- filtro global: nivel educativo
    s.sostenimiento,
    s.cve_ent,                                -- filtro global: entidad
    s.cve_mun,                                -- filtro: municipio
    s.nombre_municipio,
    s.nombre_entidad,

    -- ---------- hechos observados ----------------------------------------------
    s.matricula_total,
    s.variacion_matricula,
    s.variacion_matricula * s.matricula_total AS variacion_ponderada,  -- numerador por fila (fraccion × matricula); unidad en YAML, R-3 DEC-012
    s.indice_completitud_drivers,

    -- ---------- salida ML-01 (del cubo C1) ---------------------------------------
    s.indice_riesgo,
    s.variacion_proyectada,
    s.probabilidad,
    s.en_riesgo,                              -- nulo sin prediccion, nunca FALSE
    s.cobertura_prediccion,

    -- ---------- bucket de riesgo (para dashboards por rango) ---------------------
    CASE
        WHEN s.indice_riesgo IS NULL THEN NULL
        WHEN s.indice_riesgo < 0.2  THEN '0.00 - 0.19'
        WHEN s.indice_riesgo < 0.4  THEN '0.20 - 0.39'
        WHEN s.indice_riesgo < 0.6  THEN '0.40 - 0.59'
        WHEN s.indice_riesgo < 0.8  THEN '0.60 - 0.79'
        ELSE '0.80 - 1.00'
    END AS rango_riesgo

FROM gold.cubo_escuela_360 s