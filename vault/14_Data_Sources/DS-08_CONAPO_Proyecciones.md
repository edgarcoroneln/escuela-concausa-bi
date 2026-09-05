---
id: DS-08
title: "DS-08 · CONAPO Proyecciones de Población"
owner: "Emilio Galnares Ruiz"
status: in_review
traces_up:
  - vault/02_Requirements/User_Stories
traces_down:
  - US-121a
  - US-122a
  - US-123a
  - US-124a
tags: [data-source, bronze, conapo, proyecciones]
---

# DS-08 · CONAPO Proyecciones de Población

> → [[vault/14_Data_Sources/_index]] · Prueba de descarga real **CONFIRMADA** (ver §9, 24/08/2026)

## 1. Identificación
- **Nombre oficial:** Proyecciones de la Población de México.
- **Institución responsable:** CONAPO (Consejo Nacional de Población).
- **Qué aporta al proyecto:** población por municipio, edad y año. Es el **denominador** para calcular
  tasas y normalizar (permite comparar municipios de distinto tamaño).

## 2. Acceso
- **URL de descarga:** gob.mx/conapo no ofrece un enlace de descarga fijo/estable para este archivo; se descargó de forma manual desde ese portal (ver limitación en §10).
- **Formato:** CSV (descarga manual, sin API).
- **Tamaño aproximado:** 252,450 registros.

## 3. Frecuencia real de actualización
- **Anual** (proyección por año; la serie completa se republica al recalibrar).

## 4. Cobertura geográfica y temporal
- **Geográfica:** Nacional, desagregado municipal (y por grupo de edad).
- **Temporal:** serie proyectada (histórico + años futuros); confirmar rango en la prueba de descarga.

## 5. Esquema esperado (confirmar en prueba de descarga)
| Columna | Tipo | Nota |
|---|---|---|
| `cve_ent` | str (2) | Clave entidad |
| `cve_mun` | str (5) | Clave INEGI municipal |
| `anio` | int | Año de proyección |
| `edad` / `grupo_edad` | int/str | Edad o grupo etario |
| `poblacion` | int | Población proyectada |

## 6. Llave de unión
- **Clave INEGI de 5 dígitos** (municipio); filtrable por grupo de edad escolar.

## 7. Driver que alimenta
- Ninguno directamente: es el **denominador** para tasas y normalización; junto con DS-07 sustenta
  **D1** y normaliza los cruces municipales de otros drivers.

## 8. Licencia de uso
- Términos de Libre Uso MX (CONAPO) — **confirmar** en la ficha oficial.

## 9. Prueba de descarga real — PENDIENTE (Semana 1)
- [x] Archivo descargado físicamente
- [x] Abierto y con datos utilizables
- [x] Registros contados: `252450`
- [x] Esquema verificado (campos y tipos)
- [x] Llave confirmada: columna `CLAVE` (tipo int64 en el archivo original), requiere
      conversión a texto con relleno de ceros a la izquierda (`.astype(str).str.zfill(5)`)
      para obtener la clave INEGI de 5 dígitos estándar. Columna resultante: `cve_mun`.
- [x] Extractor construido (US-122a): script `extractor_conapo.py` que lee el archivo
      local descargado (CONAPO no ofrece link de descarga fijo, ver limitación en
      sección 10), corrige la clave de municipio a 5 dígitos (`cve_mun`), y guarda
      252,450 registros en `data/bronze/ds08_conapo.parquet` con columnas
      `_ingested_at`, `_source`, `_source_url`.
- [x] Validaciones Great Expectations (US-123a): suite `ds08_suite` con 7 expectativas
      (nulos en cve_mun/NOM_MUN/POB_TOTAL/ANO/SEXO, rango de POB_TOTAL 0-25M,
      longitud de cve_mun=5 caracteres). Resultado: 7/7 exitosas (100%) sobre
      252,450 registros. Script: `validacion_conapo.py`. Data Docs generado localmente.
- [x] Fixture de prueba generado (US-124a): `tests/fixtures/bronze_ds08_conapo_sample.csv` con
      muestra aleatoria de 500 filas (de 252,450 totales). Semilla fija
      (random_state=42) para reproducibilidad en CI. Sin datos personales
      (población agregada por municipio/sexo/año, no hay identificación individual).
- **Responsable:** Emilio Galnares Ruiz · **Fecha:** 24/08/2026

## 10. Riesgos conocidos
- Son **proyecciones**, no censos: hay incertidumbre inherente.
- Recalibraciones que cambian valores históricos entre ediciones.
- Necesidad de filtrar el grupo de edad escolar correcto para el denominador.
- Compatibilidad de claves municipales con las demás fuentes.

## 11. Integración Bronze/Postgres para D1/D2 — 2026-09-05 (BUG-048)

- Hasta esta fecha, `dbt/models/sources.yml` seguía apuntando `bronze.conapo` al fixture
  (`conapo_sample`, 36 filas) — el dato real (252,450 registros) nunca había corrido en el
  pipeline compartido del equipo.
- Se resolvió con `BUG-048`: nuevo loader `cargar_bronze_conapo_real.py` que transforma el parquet
  real al formato esperado por `poblacion_municipio.sql`, y corrección de `sources.yml` al
  identifier real.
- Resultado: D1 y D2 ahora tienen cobertura completa contra Postgres. `SIN_DATO` bajó de ~36 mil
  a 0 en los 3 ciclos evaluados.
