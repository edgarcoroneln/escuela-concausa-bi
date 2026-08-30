---
id: ADR-007
title: "ADR-007 — Unidad de target_variacion_matricula: fracción, no diferencia absoluta"
owner: "Héctor Rafael Morales Marbán"
status: accepted
traces_up: ["REQ-003", "ADR-003", "DEC-006"]
traces_down: ["US-104", "US-311", "US-313", "US-212", "US-204", "DEC-012", "BUG-017", "BUG-019", "15_ML_Models/Indice_Riesgo_ML01", "03_Architecture/Data_Model", "DEC-006"]
supersedes: []
tags: [architecture, adr, ml, celula-1, celula-2, celula-3, celula-4]
date: "2026-08-28"
---

# ADR-007 — Unidad de `target_variacion_matricula`: fracción, no diferencia absoluta

> **Estatus: propuesta.** Requiere ratificación de Andrés González Habib (ADR-003, modelado),
> Christian Ruiz (contrato de la API), Diana Alvarez (producción en Gold) y **Marina García**
> (consumo en los tableros). Convoca: Edgar Coronel.
>
> Marina se agrega el 2026-08-28 a petición suya y con razón: el rechazo de la alternativa B más
> abajo se apoya en que **Superset lee Gold directo**, así que su área es la que sostiene el
> argumento. Usar a un equipo como razón para descartar una opción y no sentarlo en la mesa era un
> defecto de esta propuesta, no una omisión de cortesía.
>
> El costo de la decisión es asimétrico y conviene tenerlo a la vista: si se ratifica fracción,
> `DEC-006` y el umbral 0.6 siguen válidos sin tocar nada; si no, hay que rehacer §5.1 del contrato
> de DB-03/DB-04. Cinco minutos para Célula 3, medio sprint para Célula 2.

## Ratificación — 2026-08-30

> **RATIFICADO.** La mesa (Andrés González, Christian Ruiz, Diana Alvarez, Marina García; convoca
> Edgar Coronel) ratifica **fracción**, sin cambios a la calibración de la sigmoide ni al umbral 0.6
> de `DEC-006`. Registrado como **DEC-012**.

La ratificación **no fue una decisión nueva**: `DEC-006` fijó el 13 de agosto que «escuela en riesgo
= `indice_riesgo ≥ 0.6` ↔ pérdida de ~5 % de matrícula», y ese «~5 %» ya es una fracción. Lo que se
decidió fue **alinear el código con una decisión que el equipo ya había tomado** y que la unidad
actual contradecía en silencio.

La mesa amplió el alcance en cuatro puntos, todos aportados por Célula 2:

### R-1 · El ADR se extiende más allá del target de ML

`fact_escuela_ciclo.variacion_matricula` tiene **exactamente el mismo defecto** y no estaba cubierta.
Es la que leen los tableros — **cuatro, no uno**. Ratificar sólo el target dejaba el ML coherente y
el frontend roto.

### R-2 · La unidad se declara en el contrato, no en el acuerdo

`Data_Model.md` §5.3 dice `StrictFloat` y nada más. **Mientras la unidad viva en la memoria de una
junta y no en el contrato, el siguiente productor vuelve a elegir por su cuenta.** Ésa es la causa
raíz; lo demás es síntoma.

### R-3 · Convención de nombres, para que no se repita

Toda columna que exprese una razón lleva la unidad en el nombre — **`_pct` o `_frac`** — o se guarda
como **numerador y denominador por separado**. Lo segundo ya es la convención de los cubos de C2
(`DEC-008`), y es la razón de que el resto de sus métricas estén bien: ésta se escapó por
reconstruirse dentro de la expresión en vez de guardar los componentes.

### R-4 · Tres cosas con dueño y fecha antes de cerrar la mesa

| Qué | Dueño | Por qué |
|---|---|---|
| **Fecha del reentrenamiento de ML-01**, no sólo de la firma | Héctor Morales | C2 verifica DB-03 con predicciones nuevas publicadas, no con el ADR firmado |
| **Dueño de BUG-019** | por asignar en el standup | DB-06 y DB-09 de Manuel también leen `gold.predicciones` |
| **La guarda de escala queda como control permanente**, no medida temporal | Héctor Morales | Es lo único que impidió publicar 45,249 filas saturadas en silencio |

---

## Contexto

El contrato nunca dijo en qué unidad se expresa `target_variacion_matricula`. `Data_Model.md` §5.3 lo
declara `StrictFloat` y nada más. Con esa ambigüedad, los dos productores eligieron distinto:

| Productor | Grano | Fórmula | Unidad |
|---|---|---|---|
| `dbt/models/gold/features_escuela.sql` (C1, US-104) | escuela | `matricula_total - matricula_ciclo_anterior` | **alumnos** |
| `src/modelos/target_hibrido.variacion_desde_serie` (C3, DEC-007) | municipio × nivel | `matricula_total / matricula_previa - 1.0` | **fracción** |

Ambos escriben en la misma columna y ambos alimentan `gold.predicciones.valor`, distinguidos sólo por
`grano` (DEC-010). Hoy esa columna **mezcla alumnos y fracciones**.

Se descubrió el 2026-08-28, cuando la primera corrida real de ML-01 reportó `MAE 10.90` y la guarda de
escala de `verificar_escala_variacion()` detuvo la publicación (BUG-017). Diana confirmó la fórmula de
C1 en el SQL. El `indice_riesgo` está calibrado sobre fracción (`-0.05` = "pierde 5 % de su
matrícula"), calibración que ADR-003 dejó explícitamente pendiente de ratificar.

## Decisión propuesta

**`target_variacion_matricula` se expresa como fracción del ciclo anterior**:
`matricula_total / matricula_previa - 1.0`. La unidad se declara en el contrato.

C1 normaliza en `features_escuela.sql`. La calibración de `indice_riesgo` **no cambia**.

## Por qué no es una preferencia de estilo

La diferencia absoluta responde una pregunta distinta a la del proyecto. El PRD pregunta *"¿qué
escuelas van a perder matrícula?"*, y el entregable las **ordena** por riesgo. Con target absoluto,
ese orden es aproximadamente un orden por tamaño de escuela.

Mismos datos, dos targets:

| Escuela | Antes | Después | Absoluta | Fracción | Rank abs. | Rank frac. |
|---|---|---|---|---|---|---|
| Primaria rural | 48 | 29 | −19 | −39.6 % | 4.º | **1.º** |
| Telesecundaria rural | 62 | 44 | −18 | −29.0 % | 5.º | 2.º |
| Primaria urbana media | 420 | 398 | −22 | −5.2 % | 3.º | 3.º |
| Secundaria urbana grande | 1 850 | 1 808 | −42 | −2.3 % | **1.º** | 4.º |
| Bachillerato metropolitano | 2 400 | 2 360 | −40 | −1.7 % | 2.º | 5.º |

**El orden se invierte.** Con target absoluto, la escuela más urgente del país sería la secundaria
grande que perdió 2.3 % de su matrícula, y la primaria rural que perdió casi 40 % quedaría en cuarto
lugar.

Sobre 4 000 escuelas simuladas con distribución de tamaños realista:

- correlación entre `|variación absoluta|` y tamaño de escuela: **0.70**
- correlación entre `|fracción|` y tamaño de escuela: **0.00**

Un modelo entrenado sobre diferencia absoluta aprende sobre todo a predecir **cuán grande es la
escuela**, no cuán en riesgo está.

### La consecuencia que importa para este proyecto

El sesgo no es neutro: empuja sistemáticamente hacia abajo a las escuelas pequeñas y rurales, que son
exactamente las que "la escuela como sensor social" existe para hacer visibles. Una telesecundaria que
pierde un tercio de sus alumnos es una señal de territorio; cuarenta alumnos menos en un bachillerato
metropolitano de 2 400 es ruido estadístico. El target absoluto los ordena al revés.

### El equipo ya había decidido esto sin notarlo

`DEC-006` (13-ago, ratificada por Manuel Serranía leyendo `Screen_Specs`) fija el umbral de negocio
así:

> **"escuela en riesgo" = `indice_riesgo ≥ 0.6` ↔ pérdida de ~5 % de matrícula**

Ese "~5 %" es una **fracción**. El umbral que la Célula 2 ya usa en sus tableros sólo significa algo
si el target lo es. Con diferencia absoluta, "0.6" no corresponde a ninguna pérdida porcentual
concreta: corresponde a una cantidad de alumnos distinta en cada escuela.

Es decir, ratificar fracción no introduce una decisión nueva — hace explícito lo que `DEC-006` ya
supuso al definirse. La alternativa A obligaría a **reabrir DEC-006**, no sólo a recalibrar la
sigmoide.

## Alternativas consideradas

**A. Recalibrar `indice_riesgo` sobre alumnos absolutos.** Rechazada: no existe un umbral absoluto que
signifique "en riesgo" para escuelas de 48 y de 2 400 alumnos a la vez. Cualquier constante elegida es
arbitraria para una de las dos, y el problema del orden por tamaño persiste intacto.

**B. Dejar ambas unidades y convertir en la API.** Rechazada: mueve la ambigüedad a C4 y deja
`gold.predicciones.valor` sin significado propio. Un tablero que lea Gold directo —que es justo lo que
hace Superset— seguiría mezclando.

**C. Normalizar en C3 al leer, sin tocar Gold.** Rechazada: dejaría a `gold.features_escuela` como
fuente con unidad implícita, y cualquier otro consumidor repetiría el error.

## Consecuencias

- C1 cambia una línea de `features_escuela.sql` y **reprocesa** Gold.
- Las 45 249 filas ya publicadas en `gold.predicciones` deben regenerarse: su `indice_riesgo` está
  saturado y no significa nada.
- `Data_Model.md` §5.3 y `src/modelos/contrato.py` declaran la unidad explícitamente (Diana ya lo
  ofreció).
- ML-01 hay que reentrenarlo; el MAE dejará de leerse en alumnos y pasará a leerse en fracción, lo que
  además lo vuelve comparable entre entidades de tamaños distintos.
- **Célula 2 no toca nada si se ratifica fracción**: `indice_riesgo` vuelve a caer dentro de [0,1]
  con resolución real y el umbral 0.6 de `DEC-006` conserva su significado. Con la unidad actual,
  `escuelas_en_riesgo` marcaría el **100 %** del universo y el tablero se vería normal — el mismo
  modo de falla que BUG-017, pero en pantalla.
- `matricula_previa == 0` deja de ser divisible. `variacion_desde_serie` ya rechaza ese caso de forma
  explícita; C1 necesita la misma regla, no un `NULLIF` silencioso que produzca `SIN_DATO` invisible.

## Qué pasa si no se decide

`verificar_escala_variacion()` seguirá deteniendo la publicación, que es el comportamiento correcto
pero deja el tramo ML → Gold bloqueado para el ensayo E2E.
