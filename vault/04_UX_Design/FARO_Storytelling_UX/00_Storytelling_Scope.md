---
id: DOC-FARO-UX-SCOPE
title: "Storytelling Scope — historia oficial de FARO"
owner: "Marina García del Buey"
status: draft
traces_up: ["US-621", "REQ-002", "vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO"]
traces_down: ["vault/04_UX_Design/FARO_Storytelling_UX/01_UX_Architecture", "vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec", "vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity"]
last_reviewed: "2026-09-10"
tags: [ux, storytelling, s7, us-621]
---

# Storytelling Scope — historia oficial de FARO

> Documento de Marina García del Buey, líder del Equipo 3. Fija **qué historia contamos**.
> Es el gate del que dependen los otros tres entregables.
> → [[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]] ·
> [[vault/04_UX_Design/FARO_Storytelling_UX/_index]]

**Estado:** borrador formal del gate del jueves. La propuesta completa sigue pendiente de la
aprobación del PO descrita en la §14 del plan.

> **Jerarquía.** Si algo de este documento contradice al
> [[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO|plan]], **manda el plan**. La §10 del plan
> dice qué endpoint sostiene cada pieza, y la §11 registra lo que hace falta pedir.

---

## 1. Objetivo de la experiencia

Que el usuario entienda, sin ayuda y sin conocimiento previo del proyecto, que **las escuelas en
riesgo no están viviendo todas la misma situación**, y que pueda llegar por sí mismo a los tres
factores que más se repiten entre ellas y a la recomendación asociada a cada uno.

La experiencia se plantea como una **investigación**: el usuario reúne evidencia para entender cada
caso. La metáfora organiza la información y sostiene el avance; no convierte a FARO en un juego. El
producto debe seguir viéndose profesional, analítico e institucional, sin estética caricaturesca de
detective.

---

## 2. Público

**Primario: el evaluador.** No conoce el detalle del proyecto, dispone de pocos minutos y va a juzgar
si la experiencia comunica valor. Necesita entender el problema, ver la evidencia y llegar a una
conclusión sin que alguien se la explique en voz alta.

**Secundario: cualquier persona autenticada.** No es técnica, no sabe qué es un driver ni un índice
de riesgo. De ahí el glosario y la nota que explica en lenguaje sencillo qué calcula el índice.

Ninguno de los dos ve datos de alumnos: el Formato 911 observa la escuela, y todo es agregado.

---

## 3. La historia, paso a paso

### 3.1 Las siete pistas

**La matrícula es la primera pista.** Es la señal que hizo que estas escuelas llamaran nuestra
atención: un grupo de ellas cruza el umbral de riesgo, y eso abre la investigación.

A partir de esa señal se abren las otras seis líneas, que son los seis drivers oficiales:

| Pista | Qué es |
|---|---|
| 1 | Matrícula — la señal inicial |
| 2 | Pobreza y rezago (D1) |
| 3 | Inseguridad (D2) |
| 4 | Infraestructura escolar (D3) |
| 5 | Conectividad (D4) |
| 6 | Estrés hídrico (D5) |
| 7 | Calidad del aire (D6) |

**No se crea un séptimo driver.** La matrícula es la señal de entrada, no un driver más.

### 3.2 Las preguntas que la historia responde, en orden

1. ¿Qué nos dice su matrícula?
2. ¿Dónde están?
3. ¿Qué características tienen?
4. ¿Qué pistas encontramos en su entorno?
5. ¿Todas muestran el mismo patrón?
6. ¿Qué driver destaca en cada caso?
7. ¿Qué podría pasar después según el modelo?
8. ¿Qué recomienda FARO?
9. ¿Qué tan completa es la evidencia disponible?

### 3.3 Los siete momentos del usuario

Encuentra una señal · revisa los casos · analiza la evidencia · identifica qué driver destaca · llega
a una conclusión · conoce la recomendación · explora otras escuelas.

### 3.4 La revelación va en la Pantalla 2, no en la 1

Es la regla que más se confunde, y por eso queda escrita aparte.

La **entrada no dice cuántas escuelas están en riesgo**. Explica qué es FARO, qué queremos investigar
y cuál será el papel del usuario. Su frase es la de apoyo:

> *La matrícula nos dio la primera pista. Ahora descubramos qué está pasando.*

La revelación ocurre en la **Pantalla 2**, y ahí entra la frase central:

> *N escuelas están en riesgo. Tenemos N casos por investigar.*

**El número sale siempre del dato en vivo, nunca escrito a mano.** En los mockups va `N` hasta que el
Equipo 5 confirme qué devuelve `GET /api/v1/kpis` (petición `P-05`). Hoy son 7 por `DEC-019`, pero si
cambian el ciclo o el umbral, la copy tiene que cambiar sola.

### 3.5 El mensaje que sostiene todo

> **Todas las escuelas están en riesgo, pero no necesariamente están viviendo la misma situación.**

Es el diferenciador del proyecto y la razón de ser de la matriz de la Pantalla 2. Si el usuario se
lleva una sola idea, es ésta.

---

## 4. Alcance

### 4.1 Dentro

- Las 7 pantallas de la §5 del plan, en escritorio.
- La matriz que compara las escuelas en riesgo contra los seis drivers.
- El expediente individual: perfil, seis drivers, driver dominante, predicción, recomendación y
  calidad de la evidencia.
- La conclusión sobre el conjunto completo: tres drivers dominantes más frecuentes, en cuántas
  escuelas aparece cada uno, concentración por municipio y cobertura de la evidencia.
- Glosario, walkthrough único, pop-up único del explorador y el chat flotante.

### 4.2 Fuera

- **Móvil.** Evolución posterior.
- **Evolución histórica de la matrícula.** La señal se cuenta en la Pantalla 2; el expediente
  investiga el entorno, no la serie. Además no hay endpoint directo: `/escuelas/{cct}` no acepta
  `ciclo`. Si se quisiera recuperar, es cambio de plan más petición nueva.
- **Comparación contra el territorio por driver.** Sólo se sostiene para pobreza y rezago, que es lo
  que expone `MunicipioOut` (`indice_rezago_social`, `pobreza_pct`, `poblacion`). No hay promedio
  municipal de D2 a D6.
- **Afirmar cuánta matrícula perdió una escuela en particular.** `variacion_matricula` existe
  agregada, no por escuela.
- Explicabilidad adicional del modelo y métricas nuevas para justificar el driver dominante. Se usa
  la contribución que ya entrega `/explicacion`.
- Drill-down en la conclusión.

---

## 5. Reglas de lenguaje

### 5.1 Nunca causalidad

FARO identifica **factores asociados** y un **driver dominante** que orienta la investigación y la
recomendación.

| Se usa | No se usa |
|---|---|
| principal pista | ésta es la causa |
| factor que más destaca | la escuela perdió matrícula por X |
| driver dominante | X provocó la caída |
| línea de investigación | se debe a |
| factor asociado | por culpa de |

### 5.2 Los datos cuentan la historia

Los textos del front son **dinámicos**, construidos con datos reales, no fijos. Ejemplos de formato,
no de contenido:

- *N escuelas superan el umbral de riesgo.*
- *La inseguridad es el driver dominante más frecuente entre los casos analizados.*
- *Esta escuela está en un municipio con un índice de rezago social por encima del promedio estatal.*
- *Tenemos información disponible para 5 de los 6 drivers de esta escuela.*

### 5.3 Dos frases que no se pueden escribir hoy

Quedan prohibidas porque el dato no existe, no por estilo:

- Cualquier frase que afirme la caída de matrícula **de una escuela concreta**.
- Cualquier comparación de una escuela contra el promedio de su municipio en **inseguridad,
  infraestructura, conectividad, agua o aire**.

Si se necesitan, se piden como en la §11 del plan. No se inventan.

### 5.4 `SIN_DATO` es parte de la investigación

Se presenta como **"una pista que no pudimos verificar"**. Nunca como cero y nunca como ausencia del
problema.

Esto le da valor narrativo a la completitud, que es medible: `indice_completitud_drivers` existe por
escuela y agregado.

> Un buen investigador no sólo sabe qué evidencia tiene; también sabe qué evidencia le falta.

### 5.5 Cómo se nombra el chat

Mientras `P-03` siga abierta se le llama **"el chat"** y se reserva el lugar del nombre. La propuesta
es *Watson* y la decide el Equipo 2 con el PO.

---

## 6. Arquitectura acordada

Las siete pantallas de la §5 del plan, con la historia repartida así. El chat flotante y el acceso al
glosario están disponibles en todas las posteriores al login.

| # | Pantalla | Qué hace en la historia | Qué **no** hace |
|---|---|---|---|
| 0 | Login | Homologa el acceso con la identidad nueva | No cambia autenticación ni permisos |
| 1 | Entrada | Qué es FARO, qué investigamos y cuál es el papel del usuario. Walkthrough único que menciona el chat | **No revela cuántas escuelas están en riesgo** |
| 2 | Panorama | **Revela los casos.** Riesgo, matrícula, ubicación, nivel, municipio y driver dominante. Aquí va la matriz escuelas × 6 drivers, que sostiene el mensaje de §3.5 | La matrícula se muestra únicamente aquí dentro de la historia |
| 3 | Selección de caso | Las escuelas identificables con su índice. El usuario puede investigar una sola y seguir | No obliga a revisarlas todas |
| 4 | Expediente | Perfil → seis drivers → driver dominante → predicción → recomendación → calidad de la evidencia | **No incluye evolución histórica de matrícula** |
| 5 | Conclusión | Qué aprendimos: tres drivers dominantes más frecuentes, en cuántas escuelas aparece cada uno, concentración por municipio y cobertura. Sobre el conjunto completo, sin importar los filtros | Sin drill-down. Un solo CTA principal |
| 6 | Exploración | Seguir investigando otros casos con ciclo, entidad y nivel | No se llama "ML" de cara al usuario |

---

## 7. Criterios de aceptación iniciales

Los 24 criterios canónicos viven en la **§9 del plan** y no se repiten aquí, por la regla 1 del vault.

Este documento agrega cuatro que nacen de la narrativa y que conviene que QA (`US-651`) recoja:

1. La pantalla de entrada **no** deja saber cuántas escuelas están en riesgo, ni por texto ni por
   ninguna visualización.
2. El número de escuelas en riesgo se resuelve del dato en vivo; ningún texto lo lleva escrito a mano.
3. La Pantalla 2 comunica de forma inequívoca que los casos comparten el riesgo pero no la situación.
4. Ningún texto del producto afirma la caída de matrícula de una escuela concreta ni compara una
   escuela contra su municipio en un driver distinto de pobreza y rezago.

---

## 8. Dependencias abiertas

Las seis peticiones de la §11 del plan. Su efecto sobre la historia:

| Petición | Si no se resuelve, la historia pierde |
|---|---|
| `P-01` `prioridad` en la API + corte de `BUG-063` | El expediente y la conclusión dejan de decir por dónde empezar |
| `P-02` bandas Alto / Medio / Bajo | El índice se muestra sin etiqueta, sólo el número |
| `P-03` nombre del chat | El chat se queda sin nombre propio en la narrativa |
| `P-04` ADR que retire Superset | El Equipo 5 no puede construir estas pantallas sin contradecir `US-206` |
| `P-05` confirmar `escuelas_en_riesgo` en `/api/v1/kpis` | La frase central no puede fijar el número |
| `P-06` qué documento manda en UX | La identidad visual nueva no puede sustituir a `UX_Guidelines` |

Ninguna detiene el trabajo de esta semana. Lo que no llegue se documenta como **recorte explícito**
en vez de dibujarse como si existiera.
