-- =============================================================================
-- MOCK LOCAL · gold.predicciones y gold.recomendaciones
-- -----------------------------------------------------------------------------
-- Historia : US-203 (Manuel Alejandro Serrania Reinada, Celula 2)
-- Proposito: desbloquear el desarrollo de DB-01/DB-02 mientras C3 entrega las
--            salidas reales de ML-01/ML-02 (US-311/US-313, BLOCK de calendario).
--            Regla del plan de sprint C2: "si un input no llega, trabaja contra
--            mock o fixtures, avisalo en standup y registra el bloqueo".
--
-- ⚠️ ESTO ES UN MOCK:
--   * Solo para DESARROLLO LOCAL. Nunca en staging/prod, nunca lo carga CI.
--   * Los valores son deterministicos (hash del CCT): misma escuela => mismo
--     riesgo en cada corrida, para que los screenshots sean reproducibles.
--   * Un municipio completo queda SIN predicciones a proposito: ejercita la
--     bandera cobertura_riesgo = 'SIN_DATO' en el coropletico.
--   * Cuando C3 publique la tabla real (US-313, job batch a gold.predicciones),
--     este archivo se descarta: TRUNCATE/DROP local y listo. Las filas llevan
--     mlflow_run_id = 'MOCK-US203' para identificarlas.
--   * Único cambio de esquema permitido: ADD COLUMN IF NOT EXISTS sobre
--     gold.predicciones para completar el contrato DEC-005/DEC-010 si la tabla
--     local quedó con el esquema mínimo. Nunca borra ni reescribe nada.
--
-- Esquema conforme a Data_Model.md §4.5, DEC-005 y DEC-010 (grano dual):
--   gold.predicciones    : cct, id_ciclo, modelo, valor, indice_riesgo,
--                          probabilidad, mlflow_run_id, generado_at, grano
--   gold.recomendaciones : cct, id_ciclo, driver_dominante, recomendacion, prioridad
--
-- Uso:
--   docker exec -i faro-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
--       < superset/mock/gold_ml_outputs_mock.sql
-- Idempotente: CREATE IF NOT EXISTS + ON CONFLICT DO NOTHING (sin DELETE/UPDATE/DROP).
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.predicciones (
    cct           TEXT NOT NULL,
    id_ciclo      TEXT NOT NULL,
    modelo        TEXT NOT NULL,
    valor         DOUBLE PRECISION,
    indice_riesgo DOUBLE PRECISION,
    probabilidad  DOUBLE PRECISION,
    mlflow_run_id TEXT,
    generado_at   TIMESTAMPTZ DEFAULT now(),
    grano         TEXT DEFAULT 'escuela',
    UNIQUE (cct, id_ciclo, modelo)
);

CREATE TABLE IF NOT EXISTS gold.recomendaciones (
    cct              TEXT NOT NULL,
    id_ciclo         TEXT NOT NULL,
    driver_dominante TEXT,
    recomendacion    TEXT,
    prioridad        TEXT,
    UNIQUE (cct, id_ciclo)
);

-- Si gold.predicciones ya existe con el esquema minimo de DEC-005 (sin
-- trazabilidad), se completan las columnas del contrato de forma aditiva.
ALTER TABLE gold.predicciones ADD COLUMN IF NOT EXISTS mlflow_run_id TEXT;
ALTER TABLE gold.predicciones ADD COLUMN IF NOT EXISTS generado_at TIMESTAMPTZ DEFAULT now();
-- DEC-010: grano dual. Plano 'escuela' (llave cct x id_ciclo) es el default
-- legacy-safe; las filas existentes se rellenan con 'escuela' al ejecutar ADD
-- COLUMN y las futuras filas municipio x nivel de C3 traen su grano explicito.
ALTER TABLE gold.predicciones ADD COLUMN IF NOT EXISTS grano TEXT DEFAULT 'escuela';

-- ---------------------------------------------------------------------------
-- Mock de ML-01: riesgo deterministico por hash del CCT (0.10 – 0.89).
-- El municipio con menor cve_mun del scope se excluye COMPLETO: su bandera de
-- cobertura debe leer 'SIN_DATO' en DB-01/DB-02, nunca un riesgo inventado.
-- ---------------------------------------------------------------------------
INSERT INTO gold.predicciones
    (cct, id_ciclo, modelo, valor, indice_riesgo, probabilidad, mlflow_run_id, generado_at)
SELECT
    f.cct,
    f.id_ciclo,
    'ML-01',
    f.variacion_matricula,
    ((abs(hashtext(f.cct)) % 80) + 10) / 100.0,
    0.5,
    'MOCK-US203',
    '2026-08-21 00:00:00+00'::timestamptz
FROM gold.fact_escuela_ciclo f
WHERE f.cve_mun <> (SELECT min(cve_mun) FROM gold.fact_escuela_ciclo)
ON CONFLICT (cct, id_ciclo, modelo) DO NOTHING;

-- ---------------------------------------------------------------------------
-- Mock de ML-02: driver dominante derivado del mismo hash + texto de
-- recomendacion prescriptiva alineado al catalogo dim_driver (D1..D6).
--
-- El catalogo local solo tenia D1 sembrado; sin el catalogo completo los
-- drivers D2..D6 colapsan en 'SIN_DATO' al unir con dim_driver. Se siembran
-- los 6 con ON CONFLICT DO NOTHING (no pisa nada existente). Nombres segun
-- Data_Model §4 (d1 pobreza, d2 delitos, d3 infraestructura, d4 conectividad,
-- d5 agua, d6 aire).
-- ---------------------------------------------------------------------------
INSERT INTO gold.dim_driver (id_driver, nombre)
SELECT * FROM (VALUES
    ('D1', 'Pobreza y rezago social'),
    ('D2', 'Seguridad e incidencia delictiva'),
    ('D3', 'Infraestructura escolar'),
    ('D4', 'Conectividad y equipamiento'),
    ('D5', 'Disponibilidad de agua'),
    ('D6', 'Calidad del aire')
) AS v(id_driver, nombre)
ON CONFLICT (id_driver) DO NOTHING;

INSERT INTO gold.recomendaciones
    (cct, id_ciclo, driver_dominante, recomendacion, prioridad)
WITH base AS (
    SELECT
        f.cct,
        f.id_ciclo,
        'D' || (1 + abs(hashtext(f.cct)) % 6)::text AS drv,
        ((abs(hashtext(f.cct)) % 80) + 10) / 100.0  AS riesgo_mock
    FROM gold.fact_escuela_ciclo f
    WHERE f.cve_mun <> (SELECT min(cve_mun) FROM gold.fact_escuela_ciclo)
)
SELECT
    b.cct,
    b.id_ciclo,
    b.drv,
    CASE b.drv
        WHEN 'D1' THEN 'Canalizar a becas y programas de bienestar del municipio'
        WHEN 'D2' THEN 'Coordinar con SESNSP patrullaje preventivo en la zona escolar'
        WHEN 'D3' THEN 'Gestionar rehabilitacion de infraestructura (agua/sanitarios/electricidad)'
        WHEN 'D4' THEN 'Solicitar equipamiento de conectividad (internet/computadoras)'
        WHEN 'D5' THEN 'Revisar disponibilidad hidrica y cisternas con CONAGUA'
        WHEN 'D6' THEN 'Monitorear calidad del aire y protocolos para dias contingentes'
        ELSE 'Sin recomendacion disponible'
    END,
    CASE
        WHEN b.riesgo_mock >= 0.5 THEN 'ALTA'
        WHEN b.riesgo_mock >= 0.4 THEN 'MEDIA'
        ELSE 'BAJA'
    END
FROM base b
ON CONFLICT (cct, id_ciclo) DO NOTHING;
