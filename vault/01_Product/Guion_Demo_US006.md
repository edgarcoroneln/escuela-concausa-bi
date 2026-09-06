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
| 3:00–5:00 | **El diferenciador** | Marina García | Ficha de escuela → driver dominante → recomendación. **El par**: mismo riesgo, distinta recomendación | El par elegido responde en producción **ese día** |
| 5:00–6:30 | **El modelo** | Andrés González / Héctor Morales | Cómo se predice, partición temporal, y por qué `escuelas_en_riesgo` = 0 es un resultado, no una falla | Cifras del rerun a la vista |
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

1. **`escuelas_en_riesgo` = 0.** No es un error: con datos reales, la caída máxima proyectada es
   **−4.53 %** y el umbral de `DEC-006` es −5 %. Nadie cruza porque nadie debe cruzar. La narrativa
   va por el **ranking prescriptivo**, no por el conteo — y eso está ratificado desde antes de
   conocer el número.
2. **`/explicacion` no devuelve SHAP todavía** (`BUG-053`). El driver dominante y la recomendación
   **sí son reales**, salen de ML-02; lo que falta es el desglose de contribuciones. Está registrado
   con el orden de cierre.
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
