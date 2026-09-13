---
id: DS-03
title: "DS-03 · SEP CEMABE"
owner: "Deni Garrido Fragoso"
status: in_review
version: "1.1"
last_reviewed: "2026-09-03"
traces_up: ["vault/01_Product/PRD", "vault/12_Roadmap_Sprints/PLAN_MAESTRO"]
traces_down: ["src/ingesta/extractor_cemabe.py", "dbt/models/silver/cemabe.sql"]
tags: [data-source, bronze, driver-d3, driver-d4]
---

# DS-03 · SEP CEMABE (Censo de Escuelas, Maestros y Alumnos de Educación Básica y Especial)

> → [[vault/14_Data_Sources/_index]] · Prueba de descarga real ejecutada contra SEP-SIGED.

## 1. Identificación
- **Nombre oficial:** CEMABE — Censo de Escuelas, Maestros y Alumnos de Educación Básica y Especial.
- **Institución responsable:** INEGI en coordinación con SEP.
- **Qué aporta al proyecto:** **infraestructura por escuela** (agua, drenaje, electricidad, sanitarios,
  internet, computadoras). Es la "joya escondida": datos **a nivel escuela** que alimentan dos drivers
  nacionales.

## 2. Acceso
- **Página institucional:** `https://www.siged.sep.gob.mx/SIGED/estadistica_educativa.html#CEMABE`
- **Catálogo oficial:** `https://api.siged.sep.gob.mx/CoreServices/servicios/archivo/buscarArchivos/grupo=CEMABE&id=`
- **Infraestructura por inmueble (`idFile=343`):** `https://api.siged.sep.gob.mx/CoreServices/servicios/archivo/buscarArchivos/grupo=CEMABE&id=343`
- **Centro de trabajo y conectividad (`idFile=352`):** `https://api.siged.sep.gob.mx/CoreServices/servicios/archivo/buscarArchivos/grupo=CEMABE&id=352`
- **Diccionario oficial (`idFile=26`):** `https://api.siged.sep.gob.mx/CoreServices/servicios/archivo/buscarArchivos/grupo=CEMABE&id=26`
- **Formato de distribución:** respuesta JSON oficial con archivo en Base64. Los archivos de datos son
  `INMUEBLE_CSV.zip` y `CENTRAB_CSV.zip`; cada ZIP contiene un CSV.
- **Tamaño medido:** 13,254,201 bytes (`INMUEBLE_CSV.zip`) y 16,146,102 bytes
  (`CENTRAB_CSV.zip`).

> La API y la página pertenecen a SEP-SIGED. INEGI coordinó el levantamiento, pero la distribución
> tabular vigente localizada y verificada está publicada por SEP.

## 3. Frecuencia real de actualización
- **Censo único 2013** (no se actualiza periódicamente). Se trata como snapshot estructural.

## 4. Cobertura geográfica y temporal
- **Geográfica:** Nacional · nivel escuela.
- **Temporal:** levantamiento **2013**.

## 5. Esquema físico confirmado

Los indicadores no vienen en una tabla plana ya renombrada. El contrato real requiere unir dos
archivos oficiales mediante `ID_INM`:

| Archivo | Filas | Columnas | Llave / uso |
|---|---|---|
| `INMUEBLE_CSV.csv` | 166,138 | 162 | `ID_INM`; infraestructura del inmueble |
| `CENTRAB_CSV.csv` | 205,912 | 202 | `ID_INM` + `CLAVE_CT`; centro de trabajo, internet y cómputo |

Mapeo mínimo confirmado contra `Cuestionarios.xlsx`:

| Campo FARO | Archivo / columna oficial | Regla física |
|---|---|---|
| `cct` | `CENTRAB.CLAVE_CT` | Campo físico de 11 caracteres: CCT (10) + turno (1); el parser retira el turno |
| `agua_red` | `INMUEBLE.P17A` | `1` = red pública; `2..6` otras fuentes/sin agua; `9` no especificado |
| `drenaje` | `INMUEBLE.P22` | `1` sí, `2` no, `9` no especificado |
| `electricidad` | `INMUEBLE.P18A` | `1..4` fuente disponible; `5` no tiene; `9` no especificado |
| `sanitarios` | `INMUEBLE.P21` | `1` sí, `2` no, `9` no especificado |
| `internet` | `CENTRAB.P268` | `1` sí, `2` no, `9` no especificado |
| `computadoras` | `CENTRAB.P277` | equipos que sirven: `0..999`; `9999` no especificado |

El extractor valida los ZIP oficiales durante la descarga y genera el contrato Bronze vigente de
FARO con una fila por CCT. Traduce los códigos a `1`/`0`/vacío y consolida los turnos; Silver
convierte el vacío en `SIN_DATO`. Para `P277`, cero significa ausencia, `1..999` disponibilidad y
`9999` dato no especificado.

## 6. Llave de unión
- **Entre archivos oficiales:** `ID_INM`.
- **Llave escolar resultante:** los primeros 10 caracteres de `CENTRAB.CLAVE_CT`; el carácter 11
  identifica el turno según `Cuestionarios.xlsx`.
- Un inmueble puede alojar más de un centro de trabajo; el resultado debe conservar una fila por
  CCT antes de deduplicar el contrato Silver.

## 7. Driver que alimenta
- **D3 · Infraestructura escolar** (agua, drenaje, luz, sanitarios).
- **D4 · Conectividad digital** (internet / computadoras).

## 8. Licencia de uso
- Descarga pública desde SEP-SIGED. La página oficial advierte que las celdas con datos personales
  se publican como `ELIMINADO`; el pipeline no debe intentar reconstruirlas.
- Términos específicos de redistribución del paquete: pendientes de confirmación institucional.

## 9. Prueba de descarga real — EJECUTADA
- [x] Catálogo consultado directamente en la API oficial SEP-SIGED.
- [x] `INMUEBLE_CSV.zip`, `CENTRAB_CSV.zip` y `Cuestionarios.xlsx` descargados físicamente.
- [x] ZIP abiertos: contienen CSV utilizables.
- [x] Conteos: 166,138 inmuebles y 205,912 centros de trabajo con CCT no vacío.
- [x] Esquema contrastado contra el diccionario oficial.
- [x] Unión confirmada: `INMUEBLE.ID_INM = CENTRAB.ID_INM`; CCT en `CENTRAB.CLAVE_CT`.
- [x] Muestras reales de cinco filas guardadas localmente en
  `data/raw/cemabe/muestra/INMUEBLE_CSV_head5.csv` y
  `data/raw/cemabe/muestra/CENTRAB_CSV_relacionado.csv`. Permanecen ignoradas por Git conforme
  a la regla que prohíbe versionar datos reales; el esquema y los conteos sí quedan documentados.
- [x] Extractor reproducible ejecutado: 203,570 CCT únicos escritos a Parquet. Se excluyeron
  explícitamente 68 claves de 11 caracteres que no cumplen el patrón oficial CCT + turno
  (por ejemplo, `27DJNTEMP31`); no se fabricó una equivalencia para esas claves temporales.
- [x] Carga real ejecutada en `bronze.cemabe_2013`: 203,570/203,570 filas insertadas. Se retiraron
  72 filas de fixture identificadas por su URL sintética antes de reconstruir Silver.
- [x] `silver.cemabe`: 203,570 CCT reales; 8/8 pruebas propias dbt en PASS.
- **Responsable:** Deni Garrido Fragoso · **Fecha:** 2026-09-03.

## 10. Riesgos conocidos
- **Antigüedad (2013):** la infraestructura pudo cambiar; documentar como limitación temporal.
- Cobertura de educación básica/especial (no media superior).
- CCT que ya no existen en el catálogo actual (DS-02) → filas huérfanas.
- Campos booleanos codificados de forma heterogénea (1/0, Sí/No, texto).
- El CSV mezcla UTF-8 con caracteres de control heredados; el parser debe declarar estrategia de
  decodificación y reportar reemplazos, no fallar silenciosamente.
- El fixture sintético actual supone un único CSV ya conformado; no representa el contrato físico
  de los dos archivos oficiales.

## 11. Verificación de cobertura de D3 (2026-09-13) — corregido en revisión de Edgar (PR #358)

> **Corrección (2026-09-13, Edgar Coronel, revisión de PR #358):** esta sección decía
> "verificado en Cloud SQL" y "cobertura en producción: 85.1%" con las mismas cifras
> (`silver.cemabe` 203,638 filas / `gold.fact_escuela_ciclo` 132,566 filas) que ya se reconoció,
> en el DevLog de D6 de esta misma fecha, que **no son de producción**. Confirmado con Diana: las
> tres cifras de abajo (85.8%, 84.6% y el "85.1% en producción" ya retirado) salieron del mismo
> entorno usado para verificar D6 — no de una consulta contra Cloud SQL de producción real. Se
> corrige toda la sección con la misma honestidad que el DevLog de D6.

- **Contexto:** investigación de un reporte en Panorama de Riesgo (producción) donde D3 salía
  SIN_DATO en las 7 escuelas de mayor riesgo.
- **Lo que sí se verificó — comportamiento del join/lógica, con censo real cargado:** contra un
  entorno con `bronze.cemabe_2013` real cargado (203,638 filas en `silver.cemabe`, 132,566 en
  `gold.fact_escuela_ciclo`) — **no producción** — la cobertura da 85.8% OK por fila de ciclo
  (113,744/132,566) y 84.6% por escuela (exigiendo D3 = OK en todos los ciclos de esa escuela;
  prácticamente igual a la cifra por fila porque `d3_cobertura` se calcula uniendo
  `silver.cemabe` por `cct`, ya deduplicada a una fila por escuela en `cemabe.sql`, así que no
  varía entre ciclos de una misma escuela). Esto confirma que el join/la lógica de D3 funciona
  correctamente cuando hay censo real cargado.
- **Lo que NO se verificó:** no hay ninguna consulta confirmada contra Cloud SQL de producción
  real para D3. Edgar confirma que producción hoy solo tiene el Bronze de prueba de
  `cemabe_2013` (72 filas) — el mismo patrón que SINAICA en D6 (ver DevLog
  `2026-09-13-diana-alvarez-d5-agua-d6-fix-produccion-ds03.md`, sección 1). Con solo 72 filas de
  censo real en Bronze, **la cobertura real de D3 en producción hoy es muchísimo menor que
  85%** — no se puede afirmar un número sin correr la consulta ahí.
- **Por sostenimiento** (`gold.dim_escuela.sostenimiento`, que solo admite `PÚBLICO`/`PRIVADO`
  por diseño de [[vault/14_Data_Sources/DS-02_Catalogo_CCT|DS-02]]): 86.6%/83.0% OK — mismas
  cifras del entorno no productivo de arriba, mismo caveat. La ausencia de una categoría
  "comunitario"/CONAFE sí es un hecho de esquema confirmado independientemente del entorno (ver
  [[vault/14_Data_Sources/DS-02_Catalogo_CCT|DS-02]]: `sostenimiento` solo admite esos dos
  valores) — esa parte del descarte se mantiene.
- **Explicación del hueco (~14-15%) que sí se sostiene, con censo real cargado:** coincide con el
  riesgo ya anotado arriba en §10 ("CCT que ya no existen en el catálogo actual (DS-02) → filas
  huérfanas") — escuelas cuyo `cct` no tiene fila en `silver.cemabe` (censo 2013), ya sea por
  reasignación de clave o por ser de creación posterior al levantamiento.
- **Conclusión corregida:** el join/la lógica de D3 **no requiere fix de código** — igual que con
  D6, el comportamiento en producción hoy es un problema de **carga de datos, no de lógica**. A
  diferencia de lo que decía la versión anterior de esta sección, **sí hace falta cargar el censo
  CEMABE 2013 real en el Bronze de producción** (hoy solo tiene el fixture de 72 filas) y
  regenerar/importar Gold ahí para que D3 refleje su cobertura real — mismo pendiente que D6/
  SINAICA, no algo ya resuelto.
- **Responsable:** Diana Alvarez · **Fecha:** 2026-09-13 (corregido 2026-09-13, revisión Edgar
  Coronel, PR #358).
