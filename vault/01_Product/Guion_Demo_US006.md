---
id: DOC-GUION-DEMO
title: "Guion de la demo en vivo — 9 de septiembre"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["US-006", "US-305", "US-323", "REQ-006", "REQ-007", "vault/01_Product/PRD_General_Materia"]
traces_down: ["vault/12_Roadmap_Sprints/Execution_Status"]
last_reviewed: "2026-09-08"
tags: [demo, pitch, guion, contingencia, us-006, agente]
---

# Guion de la demo en vivo — miércoles 9 de septiembre

> 10 minutos. Quién muestra qué, en qué orden, y qué hacer si algo falla.
> → [[vault/00_Start_Here/PROJECT_INDEX]] · [[vault/10_Risk_Governance/Decision_Log]]

## Corte final — 8 de septiembre

- **Diana Alvarez presenta el guion completo al profesor.** Edgar abre/cierra sólo si Diana lo
  solicita; los Tech Leads quedan como respaldo para preguntas técnicas.
- El despliegue final y el smoke de las tres superficies están cerrados por el PR #294; evidencia:
  [[vault/_DevLog/2026-09-08-luis-tellez-despliegue-agente-us305-frontend-main]].
- Rige el **code freeze definitivo de `DEC-021`**. No se incorporan cambios funcionales antes de la
  demo; sólo se ejecuta el checklist de verificación.
- `US-006` es la única historia abierta: se cierra cuando la demo y la entrega se ejecuten el 9-sep.

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
| 0:00–1:00 | **El problema** | Diana Alvarez | Sin pantalla. La escuela como sensor del territorio y las dos preguntas del proyecto | — |
| 1:00–3:00 | **El dato es real** | Diana Alvarez | Las 8 fuentes; Bronze→Silver→Gold; cobertura por driver y `SIN_DATO` explícito | `/api/v1/kpis` responde y `indice_completitud_drivers` ≈ 0.62 |
| 3:00–5:00 | **El diferenciador** | Diana Alvarez | Ficha de escuela → driver dominante → recomendación. **El par**: `15DPR0920D` y `15DPR2254O`, mismo riesgo (0.4774), distinta recomendación | Las dos responden en producción **ese día**, con sesión iniciada |
| 5:00–6:30 | **El modelo** | Diana Alvarez | Cómo se predice, partición temporal, y por qué **7 escuelas de 45 276** es un resultado, no una falla: la línea de alerta baja a 0.50 (`DEC-019`) sin recalibrar la sigmoide | Cifras del rerun a la vista y **el conteo** con la línea nueva — la **etiqueta** del tablero sigue diciendo 0.6 y eso se dice, ver punto 3 |
| 6:30–7:30 | **Pregúntale a los datos** | Diana Alvarez | El agente: una pregunta real con **su SQL a la vista**, y una destructiva **rechazada en vivo** | Los dos chips corridos contra producción **ese día**, con sesión iniciada |
| 7:30–8:30 | **La plataforma** | Diana Alvarez | Cloud Run, las tres superficies públicas, SSO con Google, RBAC 200/403 | FARO Web, API y Superset responden y el login entra |
| 8:30–9:00 | **Cómo trabajamos** | Diana Alvarez | PRs, gate de propiedad, DevLogs, registros de bugs y decisiones | `vault_lint` y CI en verde |
| 9:00–10:00 | **Cierre y preguntas** | Diana Alvarez | Entrega cerrada, limitaciones declaradas y siguiente iteración | — |

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

**Luis y Christian quedan como respaldo técnico**, sin cambiar de narrador durante los diez minutos.

### El par de demostración

Elegido por Marina García el 2026-09-06 sobre el Gold rematerializado por C1 tras `DEC-019`.

| CCT | Nombre | Nivel | Municipio | Riesgo | Driver | Recomendación |
|---|---|---|---|---|---|---|
| `15DPR0920D` | FRANCISCO I. MADERO | Primaria | Ecatepec de Morelos | **0.4774** | **D4 · conectividad** | Ampliar conectividad y dotación de equipo de cómputo |
| `15DPR2254O` | RICARDO FLORES MAGON | Primaria | Ecatepec de Morelos | **0.4774** | **D2 · inseguridad** | Coordinar con seguridad pública rutas escolares seguras y entornos protegidos |

**Por qué estas dos y no otras.** El bloque tiene que aislar una sola variable, y aquí todo lo
demás está controlado: mismo municipio, mismo nivel, y el `indice_riesgo` no es parecido sino
> **El par es de los menos expuestos a `BUG-062`, y conviene decirlo.** Ese defecto infla los drivers
> de **cobertura angosta** al reescalarlos min-max sobre su propio conjunto, y el caso extremo es **D6**,
> que cubre ~1.3 % del universo. **Este par usa D4 y D2, los dos de cobertura amplia**, así que el
> artefacto no lo explica. Lo señaló Marina García al revisar el PR: tal como estaba redactado parecía
> que el par estuviera en riesgo por el bug, y es al revés.

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
índice. La comprobación final se repite la mañana del 9.

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

**Dónde corre.** El widget vive en FARO Web y está desplegado en
`https://faro-frontend-eanzfglvyq-uc.a.run.app` (`US-526`). Si la superficie falla durante la
evaluación, el plan B conserva el Streamlit local contra la API de producción y se declara la
diferencia de ambiente.

**Verificaciones del bloque para la mañana del 9:**

- `/api/v1/agente/consulta` responde **401 sin sesión**, como exige `SEC-006`; iniciar sesión antes
  de ejecutar el chip.
- El agente completo está desplegado en `faro-api-00018-gjx` y el smoke del PR #294 quedó verde.
  Aun así, los dos chips se repiten el mismo día: una demo depende del dato vivo, no del resultado
  de la víspera.

## Lo que decimos antes de que lo pregunten

Cuatro cosas que se ven y que **conviene explicar nosotros**, no que las descubran:

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
2. **`/explicacion` lee SHAP real, pero todavía devuelve `SIN_DATO` — y las dos cosas son ciertas.**
   `BUG-053` está **`fixed`** desde el 2026-09-05 (Christian Ruiz, C4): el endpoint dejó `mock_data` y
   lee `gold.recomendaciones.shap_d1..shap_d6` a través de `RepositorioModelos`. **El código está;
   el dato no.** Las seis columnas existen en producción desde el `ALTER` de C5 del 2026-09-07, pero
   están en **`NULL`** hasta que C3 republique el Gold con `publicar_gold.py`. Así que se dice como
   deuda declarada, no como logro: *"el desglose por driver ya se lee del modelo, no de un mock; lo
   que falta es repoblar la tabla"*. Lo mismo con `ML-03` (clustering, `US-321`), que el panel pinta
   como `SIN_DATO` explícito en vez de esconderlo.

   > **Corrección del PO (2026-09-07).** La redacción anterior de este punto afirmaba que
   > `/explicacion` *"ya devuelve SHAP real… si sale la pregunta, se enseña"*. Era falso en
   > producción y el error fue mío: leí el estado del **registro de bugs** y no el del **dato
   > desplegado**. Es el mismo modo de falla que ya me señalaron con `latitud` y con `UMBRAL_RIESGO`
   > — dar por verificado lo que sólo se comprobó de un lado.
3. **Las etiquetas de los tableros todavía dicen «Índice ≥ 0.6».** El **conteo es correcto** —los
   cubos ya cuentan con la línea de 0.50 y por eso dicen **7**—, pero el texto del `subheader` sólo se
   actualiza corriendo `sync_semantic_layer.py`, y **`DEC-020` lo prohíbe** porque ese run borraría la
   metadata con la que C5 levantó 20 charts *timeseries*. Es deuda **visible, medida y decidida**: se
   corrige después del 9, junto con `BUG-058`. Lo mismo aplica a la corrección de lectura horizontal de
   **DB-05** de Monserrat Miranda, que está mergeada pero no llega a producción por la misma razón.
4. **Accesibilidad**: de los 10 colores del tema de fábrica que pintan los 103 charts, **8 no llegan
   a 4.5:1 y 5 no llegan ni a 3:1**. Es deuda declarada, medida sobre el bundle real, y decidida
   —`DEC-016`— no ignorada.

## Plan B, por lo que puede fallar

| Si falla | Qué se hace | Preparado por |
|---|---|---|
| **FARO Web no responde** | La demo corre sobre **Superset y la API por separado**; el panel local usa la API de producción y se declara el plan B | Edgar Coronel |
| **El agente no responde, o el login lo rechaza** | Se cae el bloque completo y **sus 60 s vuelven al modelo**. Se dice en una frase: *"el agente está construido y evaluado con un set de 20 preguntas; hoy no lo demostramos en vivo."* **No se improvisa tecleando otra pregunta** | Andrés González |
| **La conexión de la sede** | Video de 3 min grabado el lunes con el recorrido completo, en el equipo local y en una memoria USB | Edgar Coronel |
| **Superset no carga o el login rechaza** | Capturas de los 10 tableros en el vault (`04_UX_Design/capturas/`) y el recorrido se narra sobre ellas | Marina · Monserrat |
| **La API responde 401 o 500** | Ambiente local levantado con [[vault/00_Start_Here/Runbook_Ambiente_Local]], corriendo **antes** de entrar a la sala | Edgar Coronel |
| **Un tablero sale vacío** | Se pasa al siguiente sin detenerse; los datos ya se mostraron en el bloque de Diana | quien esté presentando |
| **Preguntan por un número que no cuadra** | Se abre el registro que lo explica —`Bug_Register`, `Decision_Log`— en vez de improvisar | Edgar Coronel |

**El ambiente local corriendo es la red de seguridad de todo lo demás.** Se levanta antes de salir de
casa, no en la sala.

## La sesión se inicia DENTRO de la demo, no antes

**Antecedente.** `BUG-070` mostró que la imagen anterior no incluía el refresco automático del
access token y la sesión moría a los 15 minutos. El PR #294 documenta la remediación: C5 reconstruyó
FARO Web desde `main` y promovió `faro-frontend-00009-way` al 100 % del tráfico. La verificación de
duración >16 minutos se conserva en el checklist del día como control de operación.

Consecuencia concreta: si iniciamos sesión en la preparación y la demo empieza 15 minutos después,
**el Panel ML y el chat fallan a media presentación** y el mensaje que sale no dice *"vuelve a iniciar
sesión"*, dice que la API rechazó la solicitud.

**Por eso el login se hace dentro de la demo, dirigido por Diana.** Cuesta unos segundos, demuestra
OAuth de Google y reduce el riesgo de llegar con una sesión expirada.

**Lo que esto obliga en los bloques anteriores:** la ficha y el agente usan superficies que exigen
sesión. Diana inicia sesión antes de la primera de ellas y conserva el plan B local preparado:

- Con la imagen final se inicia sesión una vez y el refresco debe sostenerla.
- Si la prueba de duración falla, se reinicia sesión antes del bloque afectado y se registra el
  defecto después de la entrega; no se modifica producción durante el freeze.

**Verificación del arreglo:** iniciar sesión, esperar más de 16 minutos y usar el Panel ML. El
rebuild ya está desplegado; esta prueba confirma comportamiento sostenido, no habilita otro cambio.

## Checklist del día, en orden

Se corre **la mañana del 9**, no la noche anterior:

- [ ] `/api/v1/health` y `/api/v1/kpis` responden con los números esperados
- [ ] Superset abre y el login con Google entra con la cuenta del evaluador
- [ ] **Nadie deja una sesión abierta esperando**: el login va dentro de la demo (`BUG-070`)
- [ ] **Sesión abierta >16 min + Panel ML responde** en la imagen final
- [ ] El par de demostración responde **en producción**, con los valores del guion
- [ ] **Los dos chips del agente responden en producción**, con la cuenta con la que se va a demostrar
- [ ] **`BUG-025` verificado autenticado**, o el bloque del agente se declara caído **antes** de entrar
- [ ] Los 10 tableros cargan con datos
- [ ] Ambiente local levantado y verificado como respaldo
- [ ] Video de respaldo accesible sin internet

## Qué falta para cerrar `US-006`

Sólo **ejecutar la demo y formalizar la entrega el 9 de septiembre**. Diana da el guion completo;
el equipo conserva las respuestas técnicas y los planes B. El checklist de la mañana sigue abierto
porque debe medir el estado vivo del día, no porque falte desarrollo.
