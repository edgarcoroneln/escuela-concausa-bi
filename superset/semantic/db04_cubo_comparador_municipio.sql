-- =============================================================================
-- db04_cubo_comparador_municipio  ·  DB-04 Comparador de municipios
-- -----------------------------------------------------------------------------
-- Historia   : US-211a  (Marina Garcia del Buey, Celula 2 - Analytics & BI)
--              Repunteo US-205 (Manuel Alejandro Serrania Reinada, C2)
-- Contrato   : 04_UX_Design/Cube_Specs_DB03_DB04.md  (DOC-CUBESPEC-DB0304) §4
-- Grano      : una fila por cve_mun x nivel x id_ciclo
--
-- REPUNTEO A CUBOS FISICOS (US-205 / US-113): passthrough 1:1 de
--   gold.cubo_comparador_municipio (C1, grano DEC-008). La lista de columnas es
--   EXPLICITA a proposito: documenta el contrato de salida.
--
-- Reglas ya garantizadas por C1 (ver cubo_comparador_municipio):
--   El cubo guarda COMPONENTES aditivos, nunca promedios (patron DEC-008):
--   suma_d#/escuelas_con_d# y suma_indice_riesgo/escuelas_con_prediccion viajan
--   por separado; la razon se calcula en la capa semantica (metrics_db03_db04.
--   yaml). Esto permite reagregar con cualquier combinacion de filtros (AC-002.2).
--   R1: riesgo ML-01 por LEFT JOIN (C1), modelo 'ML-01'. R2: SIN_DATO nunca se
--   convierte en cero: cada driver publica cobertura_d# y el riesgo cobertura_
--   riesgo. R3: escuelas_en_riesgo acotado al umbral 0.6. R5: Gold acotado.
-- =============================================================================

SELECT
    -- ---------- identidad y llaves -------------------------------------------
    c.cve_mun,
    c.cve_ent,                                -- filtro global: entidad
    c.nombre_municipio,
    c.nombre_entidad,
    c.nivel,                                  -- filtro global: nivel educativo
    c.id_ciclo,                               -- filtro global: ciclo
    c.ciclo,
    c.anio_inicio,

    -- ---------- contexto socioeconomico (KPI-14) -----------------------------
    c.poblacion,
    c.pobreza_pct,
    c.grado_rezago,
    c.indice_rezago_social,

    -- ---------- componentes aditivos: volumen --------------------------------
    c.escuelas,
    c.matricula_total,
    c.suma_matricula_anterior,                -- SUM(matricula_ciclo_anterior); denominador de KPI-02 (BUG-031)
    c.suma_completitud,

    -- ---------- componentes aditivos: drivers --------------------------------
    -- Numerador (suma_d#) y denominador real (escuelas_con_d#) por separado;
    -- cobertura_d# gobierna el SIN_DATO (nunca cero).
    c.suma_d1, c.escuelas_con_d1, c.cobertura_d1,
    c.suma_d2, c.escuelas_con_d2, c.cobertura_d2,
    c.suma_d3, c.escuelas_con_d3, c.cobertura_d3,
    c.suma_d4, c.escuelas_con_d4, c.cobertura_d4,
    c.suma_d5, c.escuelas_con_d5, c.cobertura_d5,
    c.suma_d6, c.escuelas_con_d6, c.cobertura_d6,

    -- ---------- componentes aditivos: riesgo (ML-01) -------------------------
    c.suma_indice_riesgo,
    c.escuelas_con_prediccion,
    c.escuelas_en_riesgo,
    c.cobertura_riesgo,

    -- ---------- navegacion cruzada hacia DB-03 (US-214a) ---------------------
    -- Ruta `DB-04 -> DB-03` del contrato drill_down. OJO: el contrato de
    -- US-211a la declaraba con llave `cct`, y eso es IMPOSIBLE a este grano —
    -- DEC-008 fijo el cubo en [cve_mun, nivel, id_ciclo] y aqui no existe `cct`.
    -- La llave real es `cve_mun`: desde un municipio se baja a SUS escuelas.
    -- El contrato quedo corregido en metrics_db03_db04.yaml (US-214a).
    --
    -- IDs por posicion en `filtros_globales` de db03_ficha_escuela.yaml:
    -- id_ciclo = 1, cve_mun = 4. El filtro `cct` (indice 0) se deja SIN tocar
    -- a proposito: al aterrizar se quiere ver el municipio completo, y que el
    -- usuario elija la escuela. Fijar cct aqui anularia el drill-down.
    -- >>> Guarda de los indices en tests/test_drill_down_db03_db04.py.
    '<a href="/superset/dashboard/db03-ficha-escuela/?native_filters=' ||
        '(NATIVE_FILTER-US203-1:(extraFormData:(filters:!((col:id_ciclo,op:IN,val:!(%27' || c.id_ciclo || '%27)))),' ||
        'filterState:(label:id_ciclo,validateStatus:!f,value:!(%27' || c.id_ciclo || '%27)),' ||
        'id:NATIVE_FILTER-US203-1,ownState:()),' ||
        'NATIVE_FILTER-US203-4:(extraFormData:(filters:!((col:cve_mun,op:IN,val:!(%27' || c.cve_mun || '%27)))),' ||
        'filterState:(label:cve_mun,validateStatus:!f,value:!(%27' || c.cve_mun || '%27)),' ||
        'id:NATIVE_FILTER-US203-4,ownState:()))' ||
        '" target="_blank" style="color:inherit;text-decoration:underline">Ver sus escuelas →</a>' AS link_db03

FROM gold.cubo_comparador_municipio c