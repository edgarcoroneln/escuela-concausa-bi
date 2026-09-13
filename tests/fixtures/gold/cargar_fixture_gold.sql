-- Carga el fixture anonimizado de Gold (tests/fixtures/gold/*.csv) a un Postgres LOCAL
-- vacio de pruebas -- para que Andres levante el chat/agente Text-to-SQL en local sin
-- tocar produccion. Generado por tests/fixtures/generate_gold_chat_fixture.py
-- (coordinacion de Luis Tellez, 2026-09-13, a peticion de Andres Gonzalez, C2).
--
-- Uso (desde la raiz del repo, con psql apuntando a tu Postgres local de pruebas):
--   psql "$DATABASE_URL" -f tests/fixtures/gold/cargar_fixture_gold.sql
--
-- El TRUNCATE de abajo es intencional y SOLO valido aqui: es un Postgres de pruebas
-- vacio que se recarga cada vez. No es el patron de ingesta de produccion, que es
-- append-only (ver src/ingesta/cargar_bronze_fixture.py y su nota de CLAUDE.md sobre
-- nunca usar DELETE/UPDATE/DROP en scripts de ingesta real) -- no copiar este patron
-- a un script que toque una base compartida.

CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.dim_municipio (
    cve_mun          TEXT PRIMARY KEY,
    cve_ent          TEXT NOT NULL,
    nombre_municipio TEXT,
    nombre_entidad   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gold.dim_escuela (
    cct     TEXT PRIMARY KEY,
    nombre  TEXT,
    nivel   TEXT,
    cve_mun TEXT REFERENCES gold.dim_municipio (cve_mun)
);

CREATE TABLE IF NOT EXISTS gold.fact_escuela_ciclo (
    cct                        TEXT REFERENCES gold.dim_escuela (cct),
    id_ciclo                   TEXT,
    matricula_total            INTEGER,
    matricula_ciclo_anterior   INTEGER,
    variacion_matricula        INTEGER,
    indice_completitud_drivers DOUBLE PRECISION,
    d1 DOUBLE PRECISION,
    d2 DOUBLE PRECISION,
    d3 DOUBLE PRECISION,
    d4 DOUBLE PRECISION,
    d5 DOUBLE PRECISION,
    d6 DOUBLE PRECISION,
    d1_cobertura TEXT,
    d2_cobertura TEXT,
    d3_cobertura TEXT,
    d4_cobertura TEXT,
    d5_cobertura TEXT,
    d6_cobertura TEXT,
    PRIMARY KEY (cct, id_ciclo)
);

TRUNCATE gold.fact_escuela_ciclo;
TRUNCATE gold.dim_escuela CASCADE;
TRUNCATE gold.dim_municipio CASCADE;

\copy gold.dim_municipio FROM 'tests/fixtures/gold/dim_municipio_fixture.csv' WITH (FORMAT csv, HEADER true);
\copy gold.dim_escuela FROM 'tests/fixtures/gold/dim_escuela_fixture.csv' WITH (FORMAT csv, HEADER true);
\copy gold.fact_escuela_ciclo FROM 'tests/fixtures/gold/fact_escuela_ciclo_fixture.csv' WITH (FORMAT csv, HEADER true);
