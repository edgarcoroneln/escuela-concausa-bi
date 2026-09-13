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

## 11. Verificación de producción (2026-09-13)

- **Contexto:** investigación de un reporte en Panorama de Riesgo (producción) donde D3 salía
  SIN_DATO en las 7 escuelas de mayor riesgo. Verificado contra `gold.fact_escuela_ciclo` en
  Cloud SQL, tras un `dbt run` limpio (PASS=10, ERROR=0) que reconstruyó `silver.cemabe`
  (203,638 filas) y `gold.fact_escuela_ciclo` (132,566 filas).
- **Cobertura por fila de ciclo:** 85.8% OK (113,744 / 132,566).
- **Cobertura por escuela** (exigiendo D3 = OK en todos los ciclos de esa escuela): 84.6% —
  prácticamente igual a la cifra por fila porque `d3_cobertura` se calcula uniendo
  `silver.cemabe` por `cct` (ya deduplicada a una fila por escuela en `cemabe.sql`), así que no
  varía entre los ciclos de una misma escuela.
- **Cobertura en producción:** 85.1% — consistente con las dos cifras anteriores.
- **Por sostenimiento** (`gold.dim_escuela.sostenimiento`, que solo admite `PÚBLICO`/`PRIVADO`
  por diseño de [[vault/14_Data_Sources/DS-02_Catalogo_CCT|DS-02]]): público 86.6% OK
  (90,075/104,032), privado 83.0% OK (23,669/28,534). No existe ninguna categoría
  "comunitario"/CONAFE en los datos reales — se investigó esa hipótesis específicamente y se
  descartó.
- **Explicación del hueco (~14-15%):** coincide con el riesgo ya anotado arriba en §10 ("CCT que
  ya no existen en el catálogo actual (DS-02) → filas huérfanas") — escuelas cuyo `cct` no tiene
  fila en `silver.cemabe` (censo 2013), ya sea por reasignación de clave o por ser de creación
  posterior al levantamiento.
- **Conclusión:** D3 no requiere fix de código ni recarga de producción. El comportamiento
  observado es la limitación de cobertura del censo 2013 ya documentada en este archivo, no una
  regresión de este sprint.
- **Responsable:** Diana Alvarez · **Fecha:** 2026-09-13.
