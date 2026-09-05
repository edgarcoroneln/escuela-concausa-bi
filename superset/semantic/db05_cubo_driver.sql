-- =============================================================================
-- db05_cubo_driver  ·  DB-05 Analisis por driver
-- -----------------------------------------------------------------------------
-- Historia   : US-211b  (Monserrat Xcaret Miranda Olivas, Celula 2)
--              REPUNTEO Y RE-ESCALA US-205 (Manuel Alejandro Serrania, C2)
-- Contrato   : 04_UX_Design/Cube_Specs_DB05_DB08.md  (DOC-CUBESPEC-DB0508) §3
-- Grano      : una fila por id_driver x cve_mun x nivel x id_ciclo
--
-- RE-ESCALA A RECOMENDACION (decision C2-US-205, ratifica Cube_Specs §8.3):
--   DB-05 pasa de analizar el driver OBSERVADO (d1..d6 del hecho, KPI-19
--   propuesto) a analizar el driver DOMINANTE de ML-02 (KPI-07 ratificado).
--   El cubo fisico gold.cubo_driver (C1) ya fue construido sobre
--   gold_ml_runtime.recomendaciones (no sobre el hecho): distingue el 0 real
--   (hay recomendaciones pero ninguna eligio ese driver: escuelas_driver = 0)
--   del SIN_DATO (el grupo no tiene recomendaciones: escuelas_driver NULL) y
--   publica los denominadores reales escuelas_con_recomendacion /
--   escuelas_sin_recomendacion en cada grupo.
--
-- REPUNTEO A CUBOS FISICOS (US-205 / US-113): passthrough 1:1 de
--   gold.cubo_driver. La lista de columnas es explicita; la capa semantica no
--   agrega (el cubo ya viene al grano DEC-009) ni filtra salidas de ML crudas.
--
-- FORMATO LARGO: una fila por driver. 'dimension_obligatoria_en_agregacion:
--   id_driver' en metrics_db05_db08.yaml documenta que ninguna metrica se suma
--   sin agrupar/filtrar por id_driver (si no se infla x6).
--
-- Reglas aplicadas: R2 (SIN_DATO nunca cero -- cobertura_recomendacion lo
--   gobierna), R5 (Gold ya viene acotado). R1/R3 viven en C1.
-- =============================================================================

SELECT
    -- ---------- identidad del driver ------------------------------------------
    cd.id_driver,                               -- filtro/selector: tab del driver
    cd.nombre_driver,
    cd.fuente_driver,
    cd.nivel_geografico        AS driver_nivel_geografico,

    -- ---------- identidad y llaves geograficas --------------------------------
    cd.cve_mun,
    cd.cve_ent,                                 -- filtro global: entidad
    cd.nombre_municipio,
    cd.nombre_entidad,
    cd.nivel,                                   -- filtro global: nivel educativo
    cd.id_ciclo,                                -- filtro global: ciclo
    cd.ciclo,
    cd.anio_inicio,

    -- ---------- componentes aditivos (del cubo C1, recomendacion) -------------
    cd.total_escuelas,
    cd.escuelas_con_recomendacion,
    cd.escuelas_sin_recomendacion,
    cd.escuelas_driver,                         -- NULL + SIN_DATO por grupo sin ML-02
    cd.cobertura_recomendacion,                 -- OK / SIN_DATO

    -- ---------- navegacion cruzada hacia DB-08 (US-214b) ----------------------
    -- Native filter IDs fijados por posicion en filtros_globales de
    -- db08_explorador_cubo.yaml (ver _filtros_nativos() en sync_semantic_layer.py):
    -- cve_mun = indice 3, id_driver = indice 4 -> NATIVE_FILTER-US203-3/-4.
    -- RISON verificado con la libreria prison (la misma que usa Superset en
    -- reports/models.py) contra Superset 6.1.0 real. cve_mun va entre %27...%27
    -- (mismo workaround del backend) porque prison cita valores con forma
    -- numerica; id_driver (D1..D6) no, porque es identificador RISON valido.
    --
    -- `style="color:inherit;text-decoration:underline"` (2026-09-05, DEC-016):
    -- este <a> lo escribe FARO, asi que FARO responde por su contraste. Sin
    -- estilo propio heredaba el azul de acento de Superset y reprobaba WCAG AA
    -- en tema CLARO sobre el fondo de la celda de tabla, aunque pasara en
    -- oscuro -- que es donde se reviso el 4-sep, por eso no se vio.
    -- No se arregla eligiendo otro azul: pasar 4.5:1 contra el gris de la celda
    -- exige luminancia baja y contra el negro exige alta, y los rangos no se
    -- cruzan (demostrado por Marina Garcia en US-215a). Heredar el color del
    -- texto de la celda pasa en ambos temas, y el subrayado cumple ademas
    -- WCAG 1.4.1: el color deja de ser el unico medio para reconocer el link.
    -- Guarda: tests/test_semantic_db05_db08.py::test_el_link_db08_no_depende_del_color_del_tema
    '<a href="/superset/dashboard/db08-explorador-cubo/?native_filters=' ||
        '(NATIVE_FILTER-US203-3:(extraFormData:(filters:!((col:cve_mun,op:IN,val:!(%27' || cd.cve_mun || '%27)))),' ||
        'filterState:(label:cve_mun,validateStatus:!f,value:!(%27' || cd.cve_mun || '%27)),' ||
        'id:NATIVE_FILTER-US203-3,ownState:()),' ||
        'NATIVE_FILTER-US203-4:(extraFormData:(filters:!((col:id_driver,op:IN,val:!(' || cd.id_driver || ')))),' ||
        'filterState:(label:id_driver,validateStatus:!f,value:!(' || cd.id_driver || ')),' ||
        'id:NATIVE_FILTER-US203-4,ownState:()))' ||
        '" target="_blank" style="color:inherit;text-decoration:underline">Ver detalle del municipio →</a>' AS link_db08
    -- Texto de ancla decidido solo para DB-05 (Monserrat). Si este patron de
    -- link cruzado se reusa en otro tablero, falta una pasada de homologacion
    -- de nomenclatura orientada a usuario -- pendiente, no bloqueante hoy.

FROM gold.cubo_driver cd