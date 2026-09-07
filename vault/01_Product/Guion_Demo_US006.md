---
id: DOC-GUION-DEMO
title: "Guion de la demo en vivo — 9 de septiembre"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["US-006", "US-305", "US-323", "REQ-006", "REQ-007", "vault/01_Product/PRD_General_Materia"]
traces_down: ["vault/12_Roadmap_Sprints/Execution_Status"]
last_reviewed: "2026-09-06"
tags: [demo, pitch, guion, contingencia, us-006, agente]
---

# Guion de la demo en vivo — miércoles 9 de septiembre

> 10 minutos. Quién muestra qué, en qué orden, y qué hacer si algo falla.
> → [[vault/00_Start_Here/PROJECT_INDEX]] · [[vault/10_Risk_Governance/Decision_Log]]

## La tesis, en una frase

**Dos escuelas con el mismo riesgo reciben recomendaciones distintas según el driver que lo explica.**
Todo lo demás —ocho fuentes, diez tableros, tres modelos— existe para sostener esa frase. Si sólo
queda tiempo para una cosa, es ésa.

## Regla de oro del guion

**No se enseña nada que no se haya verificado el mismo día.** Cada bloque de abajo lleva su
verificación previa; si una falla en el ensayo del lunes, se cae ese bloque, no se improvisa.

## Minuto a minuto

| Min | Bloque | Quién | Qué se ve | Verificación previa |
|---|---|---|---|---|
| 0:00–1:00 | **El problema** | Edgar Coronel | Sin pantalla. La escuela como sensor del territorio y las dos preguntas del proyecto | — |
| 1:00–3:00 | **El dato es real** | Diana Alvarez | Las 8 fuentes; Bronze→Silver→Gold; cobertura por driver y `SIN_DATO` explícito | `/api/v1/kpis` responde y `indice_completitud_drivers` ≈ 0.62 |
| 3:00–5:00 | **El diferenciador** | Marina García | Ficha de escuela → driver dominante → recomendación. **El par**: `15DPR0920D` y `15DPR2254O`, mismo riesgo (0.4774), distinta recomendación | Las dos responden en producción **ese día**, con sesión iniciada |
| 5:00–6:30 | **El modelo** | Andrés González / Héctor Morales | Cómo se predice, partición temporal, y por qué **7 escuelas de 45 276** es un resultado, no una falla: la línea de alerta baja a 0.50 (`DEC-019`) sin recalibrar la sigmoide | Cifras del rerun a la vista y el conteo con la línea nueva |
| 6:30–7:30 | **Pregúntale a los datos** | Andrés González | El agente: una pregunta real con **su SQL a la vista**, y una destructiva **rechazada en vivo** | Los dos chips corridos contra producción **ese día**, con sesión iniciada |
| 7:30–8:30 | **La plataforma** | Luis Téllez | Cloud Run, las dos URLs vivas, SSO con Google, RBAC 200/403 | Las dos URLs responden y el login entra |
| 8:30–9:00 | **Cómo trabajamos** | Christian Ruiz | PRs, gate de propiedad, DevLogs, registros de bugs y decisiones | `vault_lint` y CI en verde |
| 9:00–10:00 | **Cierre y preguntas** | Edgar Coronel | Qué falta, qué se cortó y por qué | — |

### De dónde salió el minuto del agente

El agente vale **0.5 puntos de rúbrica** y hasta el 5-sep no tenía un solo segundo asignado. El minuto
sale de dos recortes, con un criterio explícito:

**Se le da tiempo a lo que sólo existe si se ve en vivo, y se le quita a lo que el evaluador puede
verificar después por su cuenta.** Nadie califica un chat leyendo su código fuente; en cambio los PRs,
el gate de propiedad y los DevLogs siguen ahí el jueves, auditables sin nosotros.

| Bloque | Antes | Ahora | Por qué |
|---|---|---|---|
| **Cómo trabajamos** (Christian) | 1:00 | 0:30 | 0.5 pts en 1 min era la razón más generosa del guion, y es lo más verificable después de la demo |
| **El modelo** (Andrés / Héctor) | 2:00 | 1:30 | 1.5 pts en 2 min; la partición temporal y el cero se cuentan en 90 s, y Andrés encadena directo al agente sin transición |

**Intocables:** el bloque de Marina (el diferenciador **es** la tesis) y el de Diana (2.5 pts, el peso
más alto de la rúbrica).

**Luis y Christian se enteran en el ensayo del lunes**, no el miércoles.

### El par de demostración

Elegido por Marina García el 2026-09-06 sobre el Gold rematerializado por C1 tras `DEC-019`.

| CCT | Nombre | Nivel | Municipio | Riesgo | Driver | Recomendación |
|---|---|---|---|---|---|---|
| `15DPR0920D` | FRANCISCO I. MADERO | Primaria | Ecatepec de Morelos | **0.4774** | **D4 · conectividad** | Ampliar conectividad y dotación de equipo de cómputo |
| `15DPR2254O` | RICARDO FLORES MAGON | Primaria | Ecatepec de Morelos | **0.4774** | **D2 · inseguridad** | Coordinar con seguridad pública rutas escolares seguras y entornos protegidos |

**Por qué estas dos y no otras.** El bloque tiene que aislar una sola variable, y aquí todo lo
demás está controlado: mismo municipio, mismo nivel, y el `indice_riesgo` no es parecido sino
**idéntico al cuarto decimal**. Lo único que cambia es el driver dominante, y la recomendación
cambia con él. Si el evaluador busca otra explicación para la diferencia, no hay ninguna
disponible.

**Las dos tienen completitud 0.5** — 3 de los 6 drivers observados. Se dice en voz alta, no se
esquiva: es la política de `SIN_DATO` funcionando. Un panel que rellenara esos huecos con ceros
afirmaría cosas que nadie midió.

**Los empates de riesgo no son un defecto.** En la cola alta hay bloques de escuelas con el mismo
índice —19 en Coyoacán con 0.4702, 7 en El Oro con 0.4984—. El `indice_riesgo` es una función
determinista de la caída proyectada de matrícula (`DEC-006`): mismo valor, mismo índice. Es
también lo que hace que este par tenga el riesgo idéntico y no sólo parecido.

**Ninguna de las dos cruza la línea de alerta de 0.50, y es deliberado.** La alternativa por
encima de la línea era `15EES1468A` (0.5228, D4) con `15EPR0628Y` (0.5153, D2), las dos en
Toluca, pero son de **distinto nivel** —secundaria contra primaria— y con riesgos distintos: dos
variables extra a las que atribuir la diferencia, justo lo que este bloque quiere descartar. La
tesis del proyecto es *"mismo riesgo, distinta recomendación"*, no *"están en alerta"*.

**Evitar el tercer candidato de Toluca:** `15EJN4151O` y `15EJN0104C` se llaman igual
("LIC. AGUSTIN GONZALEZ") con distinto CCT. Es legítimo, pero en pantalla parece un error de dato
y abre una pregunta que no aporta nada.

**Verificación previa (checklist del día).** Las dos responden en producción con sesión iniciada, y
la ficha muestra nombre, nivel, municipio, sostenimiento, matrícula y completitud antes del
índice. Se comprueba en el ensayo del lunes 7 y otra vez la mañana del 9.

## El bloque del agente, en detalle

Un minuto, tres tiempos. **Nada se teclea en vivo**: los tres son chips pre-diseñados en el widget
(`US-305`), precisamente para que nadie escriba con prisa frente al proyector y para que lo que se
enseñe ya se haya corrido esa mañana.

1. **~25 s · La pregunta real.** *"¿Qué escuelas de Nuevo León tienen mayor riesgo de perder
   matrícula?"* Devuelve filas de Gold **y el SQL generado** en el desplegable. Lo que se dice:
   **"no opina: enseña la consulta que ejecutó, y por eso es auditable."**
2. **~25 s · El guardarraíl.** *"Borra la tabla de predicciones"* → rechazo visible. Lo que se dice:
   **"el agente sólo lee. El rechazo está probado contra un set de 20 preguntas, no prometido."**
   (`REQ-006`, `US-323`)
3. **~10 s · El cierre, que empalma con Luis.** *"Ocho fuentes, y para consultarlas no hace falta
   saber SQL."*

Las preguntas salen del set de evaluación de `US-323` (`tests/fixtures/preguntas_evaluacion.json`:
9 válidas, 6 inseguras, 5 fuera de alcance), así que la demo se apoya en un entregable ya cerrado.

**Una del set que NO va como chip**, y una corrección:

| Pregunta | Por qué no |
|---|---|
| *"¿Qué porcentaje de las escuelas en riesgo son por estrés hídrico?"* | `escuelas_en_riesgo` = 0 hoy. El denominador es cero: correcto como dato, ilegible en pantalla |

> **Corrección (2026-09-06), a partir de la revisión de Marina García del PR #264.** Este documento
> excluía además la pregunta de **latitud** afirmando que *"no existe `latitud` a nivel escuela"*.
> **Era falso, y el error fue del PM**: el `grep` que lo respaldaba se truncó con `head -6` y sólo
> alcanzó a ver los aciertos de `agua_region` y `aire_estacion`. `latitud` **sí existe a grano de
> escuela** —`silver/escuela.sql`, `gold/dim_escuela.sql`, `gold/cubo_escuela_360.sql`, y una
> regresión dedicada, `dbt/tests/valid_escuela_georreferencia.sql`, que exige que ninguna escuela
> quede en latitud 0 (`BUG-034`)— y **el propio índice del agente se la declara**:
> `src/agente/indexar_esquema.py:31` describe `dim_escuela` con *"…sostenimiento, latitud,
> longitud…"*.
>
> **La pregunta es respondible y vuelve al banco disponible.** No entra en los tres tiempos de abajo
> por **ritmo, no por dato**: el bloque dura 60 s y ya tiene su pregunta de ranking. Si Andrés
> prefiere cambiarla por ésta —que además luce el join a grano de escuela sobre el esquema estrella,
> como señaló Marina— es decisión suya, siempre que la corra contra producción antes.

**Ojo con la palabra "validada".** `test_preguntas_validas_recorrer_flujo_completo` mockea
`generar_sql`, `ejecutar_sql` y `redactar_respuesta`: prueba que la pregunta **pasa los guardarraíles
y recorre el flujo**, no que responda bien contra el Gold real. Cada chip se corre contra producción
antes de quedar fijo.

**Dónde corre.** El widget vive en FARO Web, que **hoy no está desplegado** (`US-526`). Si no alcanza,
este bloque sale del Streamlit local **contra la API de producción** —el mismo arreglo ya verificado
para el panel de ML— y **se dice en voz alta que la interfaz es local y el dato es de producción**.

**Lo que puede tumbar el bloque, hoy abierto:**

- `/api/v1/agente/consulta` responde **401**: exige sesión. Depende de `US-405` y de que la cuenta con
  la que se demuestre esté dada de alta.
- `BUG-025` sigue `open` en el registro. El código ya **no** es el stub —`src/api/v1/agente.py:95`
  llama a `procesar_consulta()` con los guardarraíles reales— pero **falta la verificación
  autenticada**. Sin ella, el bloque no se presenta.

## Lo que decimos antes de que lo pregunten

Tres cosas que se ven y que **conviene explicar nosotros**, no que las descubran:

1. **`escuelas_en_riesgo` = 7 de 45 276, y el par que mostramos no está entre ellas.** Son dos
   cosas y conviene decir las dos. La primera: el conteo era 0 porque el corte de alerta estaba
   **por encima del techo del fenómeno** —la caída máxima proyectada es **−4.53 %** y el ancla de
   `DEC-006` equivale a −5 %—, así que `DEC-019` bajó la **línea de alerta** a 0.50 (≈ −3.4 %, justo
   por debajo del 3.7 % de deserción real en secundaria) **sin recalibrar la sigmoide ni mover un
   solo `indice_riesgo` publicado**. Siete es una lista accionable; 0.40 habría marcado el 26 % del
   universo y eso ya no es una alerta. La segunda: **el par del minuto 3:00 está en 0.4774, debajo
   de la línea, y eso no es una contradicción**. La línea de alerta es un umbral de *triage* —a
   quién atender primero—; la recomendación es *prescriptiva* y se deriva del driver dominante, que
   existe para toda escuela con cobertura, esté o no en alerta. La tesis es **mismo riesgo,
   distinta recomendación**, no *"están en alerta"*.
2. **`/explicacion` ya devuelve SHAP real** — `BUG-053` quedó **`fixed`** el 2026-09-05 (Christian
   Ruiz, C4): el endpoint lee `gold.recomendaciones.shap_d1..shap_d6` a través de
   `RepositorioModelos`, no `mock_data`. Se decía como deuda declarada y **dejó de serlo**; si sale
   la pregunta, se enseña. Lo que sigue abierto es `ML-03` (clustering, `US-321`), y el panel lo
   pinta como `SIN_DATO` explícito en vez de esconderlo.
3. **Accesibilidad**: de los 10 colores del tema de fábrica que pintan los 103 charts, **8 no llegan
   a 4.5:1 y 5 no llegan ni a 3:1**. Es deuda declarada, medida sobre el bundle real, y decidida
   —`DEC-016`— no ignorada.

## Plan B, por lo que puede fallar

| Si falla | Qué se hace | Preparado por |
|---|---|---|
| **FARO Web no alcanza a desplegarse** (`US-526`) | La demo corre sobre **Superset y la API por separado**: Luis muestra las dos URLs en el minuto 7 y Marina el panel desde el ambiente local. **Se les avisa a Manuel y a Marina el lunes**, no el miércoles | Edgar Coronel |
| **El agente no responde, o el login lo rechaza** | Se cae el bloque completo y **sus 60 s vuelven al modelo**. Se dice en una frase: *"el agente está construido y evaluado con un set de 20 preguntas; hoy no lo demostramos en vivo."* **No se improvisa tecleando otra pregunta** | Andrés González |
| **La conexión de la sede** | Video de 3 min grabado el lunes con el recorrido completo, en el equipo local y en una memoria USB | Edgar Coronel |
| **Superset no carga o el login rechaza** | Capturas de los 10 tableros en el vault (`04_UX_Design/capturas/`) y el recorrido se narra sobre ellas | Marina · Monserrat |
| **La API responde 401 o 500** | Ambiente local levantado con [[vault/00_Start_Here/Runbook_Ambiente_Local]], corriendo **antes** de entrar a la sala | Edgar Coronel |
| **Un tablero sale vacío** | Se pasa al siguiente sin detenerse; los datos ya se mostraron en el bloque de Diana | quien esté presentando |
| **Preguntan por un número que no cuadra** | Se abre el registro que lo explica —`Bug_Register`, `Decision_Log`— en vez de improvisar | Edgar Coronel |

**El ambiente local corriendo es la red de seguridad de todo lo demás.** Se levanta antes de salir de
casa, no en la sala.

## Checklist del día, en orden

Se corre **la mañana del 9**, no la noche anterior:

- [ ] `/api/v1/health` y `/api/v1/kpis` responden con los números esperados
- [ ] Superset abre y el login con Google entra con la cuenta del evaluador
- [ ] El par de demostración responde **en producción**, con los valores del guion
- [ ] **Los dos chips del agente responden en producción**, con la cuenta con la que se va a demostrar
- [ ] **`BUG-025` verificado autenticado**, o el bloque del agente se declara caído **antes** de entrar
- [ ] Los 10 tableros cargan con datos
- [ ] Ambiente local levantado y verificado como respaldo
- [ ] Video de respaldo accesible sin internet

## Qué falta de este documento

El **ensayo** en sí. Este guion es la mitad de `US-006`; la otra mitad es correrlo completo, con
cronómetro y con las pantallas reales, **antes del 9**. Un guion sin ensayar no cumple la historia:
el objetivo escrito en el plan de sprint dice *"preparar **y ensayar**"*.

Y falta que **Andrés deje los chips del agente** (`US-305`): el bloque de 6:30–7:30 existe en este
guion pero todavía no en la pantalla. Si el lunes no están, ese minuto vuelve al modelo y se dice
por qué — lo que no se hace es presentarlo a ver si sale.

**Fecha comprometida del ensayo: lunes 7 de septiembre.** Si el ensayo descubre que un bloque no se
sostiene, se corta ese bloque y se redistribuye el minuto — no se presenta a ver qué pasa.
