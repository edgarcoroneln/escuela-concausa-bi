---
id: DS-06
title: "DS-06 · CONAGUA SINA"
owner: "Emilio Galnares Ruiz"
status: in_review
traces_up:
  - vault/02_Requirements/User_Stories
traces_down:
  - US-121a
  - US-122a
  - US-123a
  - US-124a
tags: [data-source, bronze, driver-d5, ingesta-continua]
---

# DS-06 · CONAGUA SINA (Sistema Nacional de Información del Agua)

> → [[vault/14_Data_Sources/_index]] · Prueba de descarga real **CONFIRMADA** (ver §9, 24/08/2026)
> **Ingesta continua #3** (diaria).

## 1. Identificación
- **Nombre oficial:** SINA — Sistema Nacional de Información del Agua.
- **Institución responsable:** CONAGUA (Comisión Nacional del Agua).
- **Qué aporta al proyecto:** disponibilidad hídrica, nivel de presas y estrés hídrico regional.

## 2. Acceso
- **URL de descarga / API:** https://sisuar.imta.mx/aplicacion/vista/presa/presas.php (IMTA, con datos oficiales de CONAGUA); extracción automatizada vía POST al endpoint interno `mapa.php` (Accion=Presas, 33 id_estado), ver §9.
- **Formato:** HTML/POST — no hay CSV ni API pública directa; el extractor replica la petición del formulario web.
- **Tamaño aproximado:** 180 presas por corrida.

## 3. Frecuencia real de actualización
- **Diaria.** → satisface el requisito de ingesta continua.

## 4. Cobertura geográfica y temporal
- **Geográfica:** **Regional** (por región hidrológica / presa, no por municipio directo).
- **Temporal:** serie histórica por estación/presa; confirmar profundidad en la prueba de descarga.

## 5. Esquema esperado (confirmar en prueba de descarga)
| Campo | Tipo | Nota |
|---|---|---|
| `id_estacion` / `id_presa` | str | Identificador del punto |
| `region_hidrologica` | str | Región |
| `latitud` | float | Georreferencia |
| `longitud` | float | Georreferencia |
| `indicador` | str | Nivel / almacenamiento / disponibilidad |
| `valor` | float | Medición |
| `fecha` | date | Marca temporal diaria |

## 6. Llave de unión
- **Geoespacial / regional**: se asocia a municipios por región hidrológica o por cercanía (lat/lon).
  Donde no aplica → **`SIN_DATO`**. No hay CCT ni clave INEGI directa.

## 7. Driver que alimenta
- **D5 · Estrés hídrico regional** (parcial).

## 8. Licencia de uso
- Términos de Libre Uso MX (CONAGUA) — **confirmar** en la ficha oficial.

## 9. Prueba de descarga real — PENDIENTE (Semana 1)
- [x] Fuente identificada y accesible: https://sisuar.imta.mx/aplicacion/vista/presa/presas.php
      (IMTA, con datos oficiales de CONAGUA)
- [x] Datos utilizables — confirmado
- [x] Registros contados: listado principal con múltiples presas a nivel nacional
      (filtrable por Organismo de Cuenca y Estado); cada presa tiene su propia serie
      histórica de "Vol. de almacenamiento (hm3)" por año (ej. presa 118 - Der. Jocoqui:
      2 registros, años 2017-2018).
- [x] Esquema verificado:
      - Listado general: Nombre Oficial, Corriente, Altura de cortina (m),
        Capacidad al NAME (hm3), Capacidad al NAMO (hm3), Estado, Año Término
      - Detalle por presa: Presa, Año, Vol. de almacenamiento (hm3) — SERIE DE TIEMPO
        confirmada (no es un valor fijo)
- [x] Llave confirmada: nombre/ID de presa + Estado (texto). NO trae clave INEGI de
      municipio directa; requiere mapeo posterior (Estado → municipio vía otra fuente,
      o geoespacial con lat/lon del catálogo de datos.gob.mx).
      
- [x] Extractor automatizado construido (US-122a): script `extractor_ds06.py` que
      replica la petición POST del formulario web (endpoint interno
      `mapa.php`, Accion=Presas, query con los 33 id_estado) y trae 180 presas
      con datos volumétricos (cap_name, cap_namo) sin necesidad de scraping HTML
      ni navegación manual. Guardado en `data/bronze/ds06_conagua_presas.parquet`
      con columnas `_ingested_at`, `_source`, `_source_url`.
- [x] Validaciones Great Expectations (US-123a): suite `ds06_suite` con 7 expectativas
      (nulos en nombre_oficial/estado/cap_namo, unicidad de id_presa, rangos físicos
      de cap_namo 0-100,000 hm³ y alt_cort 0-500m). Resultado: 7/7 exitosas (100%).
      Script: `validaciones_ds06.py`. Data Docs generado localmente.
- [x] Fixture de prueba generado (US-124a): `tests/fixtures/ds06_fixture.csv` con
      180 filas (muestra completa, la fuente ya tiene menos de 500 registros).
      Semilla fija (random_state=42) para reproducibilidad en CI.
- Nota: 180 registros vía este endpoint vs. 210 en el catálogo estático de
  datos.gob.mx — posible diferencia entre "presas principales" (monitoreadas)
  y el catálogo completo de estructuras. Pendiente de confirmar con el equipo.
- **Responsable:** Emilio Galnares Ruiz · **Fecha:** 24/08/2026

## 10. Riesgos conocidos (actualizado)
- No hay descarga CSV/API directa: los datos están en tablas web (HTML), se requiere
  automatizar la consulta (scraping) en US-122a para extraer el histórico completo.
- La granularidad temporal varía por presa (algunas solo tienen 2 años, otras podrían
  tener series más largas) — se debe confirmar rango real al construir el extractor.
- Llave de unión a municipio no es directa (ver sección 6); requiere regla de cruce.

## 11. Integración Bronze/Postgres para DB-10 — 2026-08-30

- Snapshot real 1:1 en `bronze.conagua_presas`.
- DB-10 registra DS-06 desde Bronze real.
- **D5 permanece `SIN_DATO` explícito**: el endpoint no trae el contrato diario/georreferenciado de `silver.agua_region`.
- No se inventan fecha, región hidrológica ni georreferencia.
