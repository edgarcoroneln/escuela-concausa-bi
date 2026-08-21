---
id: DS-05
title: "DS-05 · SINAICA Calidad del Aire"
owner: "Luis Enrique García Vázquez"
status: draft
traces_up: ["01_Product/PRD", "12_Roadmap_Sprints/PLAN_MAESTRO"]
tags: [data-source, bronze, driver-d6, ingesta-continua, cobertura-parcial]
---

# DS-05 · SINAICA Calidad del Aire

> → [[14_Data_Sources/_index]] · Prueba de descarga real **✅ COMPLETADA** (Semana 1, 2026-08-14)
> **Ingesta continua #2** (horaria, vía API). **Cobertura parcial.**

## 1. Identificación
- **Nombre oficial:** SINAICA — Sistema Nacional de Información de la Calidad del Aire.
- **Institución responsable:** INECC (Instituto Nacional de Ecología y Cambio Climático).
- **Qué aporta al proyecto:** concentraciones de contaminantes (PM2.5, PM10, O₃, etc.) **por estación**
  de monitoreo.

## 2. Acceso
- **No es una API REST/JSON pública documentada.** SINAICA no publica OpenAPI ni Swagger; los
  endpoints son los mismos que usa internamente el sitio `sinaica.inecc.gob.mx` (confirmados por
  ingeniería inversa contra el paquete open-source `rsinaica` y probados en vivo el 14-ago-2026):
  - **Catálogo de estaciones (activas recientemente):**
    `POST https://sinaica.inecc.gob.mx/lib/libd/cnxn.php` con body `metodo=getUltimosEnvios`
  - **Catálogo completo de estaciones (nombre, código, red, lat/lon, municipioId):**
    `POST https://sinaica.inecc.gob.mx/lib/j/php/getData.php` con body `tabla`, `fields`, `where`
    (consulta tipo SQL armada por el propio sitio)
  - **Parámetros disponibles por estación:**
    `POST https://sinaica.inecc.gob.mx/lib/libd/cnxn.php` con body
    `estId=<id>&metodo=getParamsPorEstAjax&tipoDatos=`
  - **Datos horarios por estación/parámetro:**
    `POST https://sinaica.inecc.gob.mx/pags/datGrafs.php` con body
    `estacionId=<id>&param=<código>&fechaIni=YYYY-MM-DD&rango=<1-6>&tipoDatos=<'', V o M>&datoBase=1`
    (`tipoDatos`: vacío = Cruda, `V` = Validada, `M` = Manual; `rango`: 1=día … 6=2 años)
- **⚠️ Hallazgo:** `datGrafs.php` no devuelve JSON limpio — devuelve HTML+JS con los datos embebidos
  en una línea `var dat = [...];` que hay que extraer con regex antes de parsear como JSON. El
  extractor de `US-122b` debe implementar ese parseo, no un `response.json()` directo.
- **Formato:** HTML con JSON embebido (requiere extracción) para datos; JSON puro para catálogo de
  estaciones y parámetros.
- **Tamaño aproximado:** una estación-parámetro con 2 semanas de datos ≈ 35 KB de respuesta cruda
  (~287 registros horarios). Rango máximo permitido por request: 2 años.

## 3. Frecuencia real de actualización
- **Horaria** (API). → satisface el requisito de ingesta continua.

## 4. Cobertura geográfica y temporal
- **Geográfica:** **Parcial** — ~80 zonas urbanas con estación de monitoreo.
- **Temporal:** histórico por estación; confirmar profundidad en la prueba de descarga.

## 5. Esquema real (confirmado en prueba de descarga, 2026-08-14)

**Respuesta de `datGrafs.php` (dato horario), tras extraer el arreglo `var dat = [...]`:**

| Campo | Tipo | Nota |
|---|---|---|
| `id` | str | Compuesto: `<estacionId><param><YYMMDDHH>` — no usar como llave, es interno |
| `fecha` | str (YYYY-MM-DD) | Fecha del dato |
| `hora` | int (0-23) | Hora del dato |
| `valor` | float | Concentración/medición en la unidad del parámetro (ver `.recode_sinaica_units`) |
| `bandO` | str | Bandera interna de origen del dato (no documentada por INECC; descartar o guardar tal cual) |
| `val` | int (0/1) | Bandera de validez del dato |

**Respuesta de `getData.php` (catálogo de estaciones) — campos usados por el proyecto:**

| Campo | Tipo | Nota |
|---|---|---|
| `id` | int | `id_estacion`, llave de la estación |
| `nombre` | str | Nombre de la estación |
| `municipioId` | str | Clave INEGI de municipio (verificar si viene a 2 o 5 dígitos antes de homologar) |
| `latitud` / `longitud` | str→float | Georreferencia (viene como string, convertir) |
| `fechaIniDatos` | str (YYYY-MM-DD) | Inicio de la serie histórica de la estación |

## 6. Llave de unión
- **Geoespacial**: la estación (lat/lon) se asocia a escuelas/municipios por **interpolación IDW**
  dentro de un radio válido. Fuera del radio → **`SIN_DATO`** (nunca cero). No hay CCT ni clave INEGI
  directa.

## 7. Driver que alimenta
- **D6 · Calidad del aire** (parcial, con IDW e índice de confianza).

## 8. Licencia de uso
- Términos de Libre Uso MX (INECC) — **confirmar** en la ficha oficial.

## 9. Prueba de descarga real — **✅ COMPLETADA** (Semana 1)
- [x] API llamada exitosamente (respuesta con datos embebidos válidos, tras extracción regex)
- [x] Respuesta con datos utilizables
- [x] Registros/estaciones contados: **200 estaciones activas** (con envío reciente, de
  **384 en el catálogo histórico completo**) · **287 registros horarios** de PM2.5 descargados de
  prueba para la estación 33 ("Centro", Aguascalientes) del 2026-08-01 al 2026-08-13/14
- [x] Esquema verificado (campos y tipos) — ver sección 5
- [x] Llave confirmada: `id` de estación (int) + `latitud`/`longitud` del catálogo de estaciones
  para la interpolación IDW. **No** hay `cve_mun` directa: la estación trae `municipioId`, pero
  llegó como `"1"` (numérico corto) en la prueba — falta confirmar si se combina con `estadoId`
  para armar la clave INEGI de 5 dígitos, o si conviene usar solo lat/lon + IDW como estaba
  planeado.
- **Responsable:** Luis Enrique García Vázquez · **Fecha:** 2026-08-14
- **Estación de prueba:** id `33`, "Centro" (Aguascalientes), lat `21.883780555556`,
  lon `-102.295825`, `fechaIniDatos: 2016-01-01`

## 10. Riesgos conocidos
- **Nuevo (2026-08-21, confirmado con Great Expectations — ver `TEST-010`):** ~6.3% de las
  estaciones del catálogo (24/384) traen `latitud`/`longitud` inutilizables: 3 con nulo genuino y
  21 con el placeholder literal `"0.0"` en vez de un `SIN_DATO` explícito. **Relevante para la
  interpolación IDW de `US-105`:** si no se filtran antes de interpolar, arrastran coordenadas
  `(0,0)` (frente a la costa de África) hacia el cálculo de escuelas cercanas.
- **Nuevo (2026-08-14):** los endpoints no son una API REST/JSON documentada — son los mismos que
  usa el sitio web internamente (confirmados vía ingeniería inversa del paquete `rsinaica`, no vía
  documentación oficial de INECC). Pueden cambiar sin aviso; el extractor de `US-122b` debe
  manejar errores de parseo defensivamente.
- **Nuevo (2026-08-14):** `datGrafs.php` devuelve HTML+JS, no JSON puro — requiere extracción por
  regex antes de parsear (ver sección 2).
- **Nuevo (2026-08-14):** `municipioId` del catálogo de estaciones no vino en formato de 5 dígitos
  INEGI en la prueba — confirmar transformación antes de usarlo como llave alterna a lat/lon.
- **Cobertura parcial** (~80 zonas urbanas con estación, ~200 estaciones activas de 384 históricas):
  grandes áreas sin estación → mucho `SIN_DATO`.
- Estaciones con huecos horarios o en mantenimiento.
- Límites de tasa (rate limit) o inestabilidad de la API — no documentados oficialmente, aplicar
  espera entre llamadas (el propio `rsinaica` espera un tiempo aleatorio entre requests).
- Interpolación IDW poco confiable lejos de estaciones → exigir índice de confianza.
