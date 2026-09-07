---
id: DOC-INDICE-RIESGO
title: "Índice de riesgo de ML-01 — de variación de matrícula a [0,1]"
owner: "Héctor Rafael Morales Marbán"
status: in_review
traces_up: ["vault/02_Requirements/User_Stories", "vault/03_Architecture/Data_Model", "vault/15_ML_Models/ML_Strategy"]
traces_down: ["US-311", "US-313"]
tags: [ml, celula-3, ml-01, contrato]
---

# Índice de riesgo de ML-01 — de variación de matrícula a [0,1]

> Define cómo la predicción de ML-01 se convierte en el `indice_riesgo` que consumen la API, los
> cubos de Superset y FARO Web.
>
> **Queda una sola decisión abierta: el ancla `0.30`** (ver §4). Las otras dos que este documento
> listaba ya están cerradas por hechos, no por opinión: `DEC-006` ratificó el umbral de −5 % el
> 13-ago, y `ADR-007` ratificó el 29-ago que el target se expresa en **fracción**, que es la unidad
> sobre la que esta sigmoide está calibrada.
>
> **Desde `DEC-019` (6-sep) este documento define el ancla, no el corte de los tableros.** Eran el
> mismo número —`0.60`— haciendo dos trabajos; ahora la **línea de alerta** es `0.50` y vive en la
> capa de consulta. Ver §4.4.
> → [[vault/15_ML_Models/_index]] · [[vault/15_ML_Models/ML_Strategy]] · [[vault/03_Architecture/Data_Model]]

## 1. El hueco que cierra

ML-01 predice `target_variacion_matricula`: un float **con signo y sin cota**, la variación de
matrícula respecto al ciclo anterior. Negativo significa que la escuela pierde alumnos.

Pero todo aguas abajo espera un número **acotado a [0,1]**, donde más alto = más riesgo:

| Consumidor | Qué espera | Dónde |
|---|---|---|
| API de inferencia | `indice_riesgo: float` con `Field(ge=0, le=1)` | `src/api/schemas.py::PrediccionOut` (US-401) |
| Almacén Gold | `valor` de `gold.predicciones` con `modelo = 'ML-01'` | [[vault/03_Architecture/Data_Model]] §4.5 |
| Tableros | cuenta "escuelas en riesgo" con `indice_riesgo >= 0.6` | [[vault/04_UX_Design/Screen_Specs]] |

La conversión entre ambas cosas **no estaba definida en ningún lado**. Este documento y
`src/modelos/riesgo.py` la fijan en un solo lugar, para que los tres consumidores lean el mismo
número.

## 2. La definición

Una **sigmoide monótona decreciente** en la variación, determinada por dos anclas de negocio:

| Variación de matrícula | `indice_riesgo` | Lectura |
|---|---|---|
| `0.00` — matrícula estable | **0.30** | riesgo bajo, no nulo |
| `-0.05` — pierde 5 % | **0.60** | exactamente el umbral de "escuela en riesgo" de los tableros |

```
indice_riesgo(v) = expit((centro - v) / escala)

con centro y escala despejados de las dos anclas:
   centro = -0.033817     escala = 0.039912
```

Las constantes **no se escriben a mano**: se derivan de las anclas en tiempo de importación. Mover
una ancla recalibra todo el sistema de forma consistente y sin tocar el código que la consume.

### Valores de referencia

| Variación | Riesgo | Interpretación |
|---|---|---|
| `+0.10` | 0.09 | crece 10 %: riesgo mínimo |
| `0.00` | 0.30 | estable |
| `-0.05` | 0.60 | umbral de alerta |
| `-0.10` | 0.84 | pierde 10 %: alerta alta |
| `-0.20` | 0.99 | colapso de matrícula |

## 3. Por qué una sigmoide

| Alternativa | Por qué se descartó |
|---|---|
| **Min-max** sobre el conjunto | El índice cambia si entra una escuela atípica, y no es comparable entre ciclos. Una escuela idéntica saldría con riesgo distinto según con quién la midan. |
| **Percentil (ECDF)** | Es relativo: si un año caen todas las escuelas, la mitad seguiría saliendo con riesgo bajo. Pésima propiedad para un sistema de alerta temprana. |
| **Sigmoide** ✅ | **Absoluta y estable**: la misma variación produce siempre el mismo riesgo, sin importar el resto del universo ni el ciclo. Acotada por construcción, así que nunca viola el contrato de la API. Monótona, así que el orden de las escuelas se preserva. |

La monotonía importa además porque la métrica reportada de ML-01 sigue siendo **MAE/RMSE sobre la
variación** (AC-003.2). El índice es una capa de presentación: no cambia el modelo, no cambia la
métrica y no se entrena contra él.

## 4. Lo que hay que ratificar

La forma funcional no está en discusión; las anclas sí. De las tres preguntas que este documento
abrió, **queda una**.

### 4.1 Abierto — ¿`0.30` es el riesgo de una escuela estable?

Es el único juicio de negocio pendiente, y conviene plantearlo por lo que se ve en pantalla y no por
la sigmoide:

| Escuela | `indice_riesgo` |
|---|---|
| crece 10 % | 0.034 |
| crece 5 % | 0.109 |
| **estable** | **0.300** |
| pierde 2 % | 0.414 |
| pierde 5 % | 0.600 |
| pierde 10 % | 0.840 |

La pregunta concreta: **¿una escuela que no pierde un solo alumno debe aparecer con 30 % de riesgo
en el tablero?** Se eligió distinto de cero porque ninguna escuela tiene riesgo nulo, pero es un
juicio que no le toca a Célula 3. No es inocuo: mueve el punto medio de la escala — hoy un riesgo de
`0.50` equivale a perder **3.4 %** de la matrícula.

Quien debe firmarlo: **Manuel Serranía** y **Marina García** (es lo que muestran sus tableros) y
**Christian Ruiz** (contrato de la API). Mientras siga abierto, este documento se queda en
`in_review`.

### 4.2 Cerrado — el umbral de −5 % (`DEC-006`, 13-ago)

Ratificado por Manuel Serranía leyendo el `>= 0.6` de [[vault/04_UX_Design/Screen_Specs]]. Queda como la
segunda ancla de la calibración: `−0.05 → 0.60`.

Vale la pena dejar asentado algo que apareció al revisarla: **`DEC-006` define el umbral como
"pérdida de ~5 % de matrícula", o sea que ya presuponía la fracción**. Ratificar ADR-007 no fue una
decisión nueva sino hacer explícito lo que esta decisión ya suponía desde agosto.

### 4.3 Cerrado — `indice_riesgo` **y** variación cruda, no una u otra

Se publican **ambos**, que era la propuesta: `gold.predicciones.valor` guarda la variación cruda
—necesaria para el MAE/RMSE de ML-01— e `indice_riesgo` es una columna derivada acotada a [0,1].
Implementado en `src/modelos/publicar_gold.py` y documentado en `Data_Model` §4.5.

> [!warning] Contradicción pendiente en `Data_Model.md`
> La línea 181 (§4.5) describe correctamente las dos columnas, pero la nota de la **línea 313** dice
> que `indice_riesgo` vive *"en la columna `valor`"*. Quien lea §5.3 consultaría `valor` esperando un
> `[0,1]` y recibiría la variación cruda. Es archivo de Célula 1; reportado, no corregido aquí.

### 4.4 Cerrado — el ancla y la línea de alerta se separan (`DEC-019`, 6-sep)

Hasta el 6 de septiembre **`0.60` hacía dos trabajos distintos**, y este documento los trataba como
uno solo: era el ancla que calibra la sigmoide (`−0.05 ↦ 0.60`, §4.2) **y** el corte con el que los
tableros contaban escuelas en riesgo. `DEC-019` los separó:

| | Valor | Qué es | Quién lo define |
|---|---|---|---|
| **Ancla de la sigmoide** | `0.60` | calibración: `DEC-006`, "pierde 5 % de su matrícula" | este documento · `src/modelos/riesgo.py::ANCLA_SIGMOIDE` |
| **Línea de alerta** | `0.50` | corte de negocio para *contar* escuelas en riesgo | `DEC-019` · `src/api/repositorio_gold.py::LINEA_DE_ALERTA` (C4) |

**El ancla no se mueve.** `DEC-019` cambia el criterio de alerta, no la calibración: no se
recalibra, no se re-entrena y no cambia un solo `indice_riesgo` publicado.

**El `0.50` sale de la aritmética de este documento.** §4.1 ya decía que *"un riesgo de `0.50`
equivale a perder **3.4 %** de la matrícula"*, y ése es exactamente el argumento con el que `DEC-019`
lo eligió: 3.4 % queda **justo por debajo** del 3.7 % de deserción real en secundaria, así que la
alerta enciende antes de que la escuela alcance la norma nacional. Reverificado al aplicar este
cambio: `variacion_equivalente(0.50) = −0.03382`.

**Por qué la línea de alerta no se define aquí ni en `riesgo.py`.** `RISK-010` está abierto porque
`0.50` ya está escrito **dos veces** —C4 y C2— sin una prueba que las ate. Añadir una tercera
definición en la capa de modelos agravaría justo lo que ese riesgo señala. La fuente única (una
`var` de dbt para la capa de datos y una constante importada para Python) es trabajo **post-freeze**.

> [!question] Abierto — ¿`prioridad` debe seguir la línea de alerta?
> `publicar_gold.py::prioridad_de_riesgo()` marca `ALTA` a partir del **ancla** (`0.60`), no de la
> línea (`0.50`). Se dejó **sin cambiar a propósito**: moverla reescribiría la columna `prioridad`
> de las 45,276 filas ya publicadas en `gold.recomendaciones`, y `DEC-019` dice explícitamente que
> no cambia un solo valor publicado. Es un juicio de negocio para el **PO** y el **TL de C3**, no
> una decisión de implementación, y menos en día de freeze.

## 5. Pruebas

`tests/test_riesgo.py` — 16 casos. Los que importan:

- `test_reproduce_el_ancla_del_umbral_de_negocio` — perder 5 % cae exactamente en 0.60.
- `test_esta_acotada_incluso_en_extremos` — ni con ±1e6 se sale de [0,1].
- `test_cumple_el_contrato_de_la_api` — construye un `PrediccionOut` real de la Célula 4 con el
  valor calculado. Si alguien recalibra fuera de rango, el CI lo detiene antes de que falle la API.
- `test_la_inversa_traduce_el_umbral_del_tablero` — permite explicar un número del tablero en
  lenguaje de negocio: "riesgo 0.60 = perder 5 % de matrícula".
