---
id: DOC-FARO-UX-PLAN
title: "Plan de trabajo — UX/UI y storytelling FARO (Equipo 3, S7)"
owner: "Marina García del Buey"
status: approved
version: "1.3"
traces_up: ["US-621", "REQ-002", "ADR-011", "DEC-023", "DEC-024", "vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09", "vault/13_Reports/Revision_Profesor_2026-09-09"]
traces_down: ["vault/04_UX_Design/FARO_Storytelling_UX/00_Storytelling_Scope", "vault/04_UX_Design/FARO_Storytelling_UX/01_UX_Architecture", "vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec", "vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity"]
last_reviewed: "2026-09-11"
tags: [ux, storytelling, s7, us-621, celula-3, aprobado]
---

# Plan de trabajo — UX/UI y storytelling FARO

> Plan operativo del **Equipo 3 · UX/UI y storytelling** de S7. Implementa `US-621` (`REQ-002`).
> → [[vault/04_UX_Design/FARO_Storytelling_UX/_index]] ·
> [[vault/03_Architecture/ADRs/ADR-011-rediseno-ux-graficas-nativas]] ·
> [[vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09]] ·
> [[vault/13_Reports/Revision_Profesor_2026-09-09]]

**Estado: aprobado.** `DEC-023` aprueba esta propuesta como dirección UX/UI de S7 y `ADR-011` la
declara el paquete que gobierna el diseño. Las seis peticiones de la §11 quedaron resueltas por
`ADR-011` y `DEC-024`. Ver §14.

**Líder:** Marina García del Buey — UX/UI & Storytelling Lead.
**Equipo:** Oscar Antonio Quiroz Lázaro · Monserrat Xcaret Miranda Olivas · Juan Carlos Macías Mayen.
**Aprobador:** Edgar Edmundo Coronel Navarrete — PO.
**Alcance principal:** escritorio. Móvil queda como evolución posterior.

---

## 0. Correcciones respecto a la propuesta original

Se registran en vez de aplicarse en silencio, para que el PO vea qué cambió y por qué.

| # | Propuesta original | Corrección | Motivo |
|---|---|---|---|
| 1 | Carpeta `04_UX_Design/` en la raíz del repositorio | `vault/04_UX_Design/FARO_Storytelling_UX/` | La carpeta no existe en la raíz; vive en el vault. Una ruta raíz no está en el alcance de nadie en `vault/_Meta/ownership.yml` y `check_ownership.py` reprobaría el PR de los cuatro |
| 2 | Sin ID | `US-621` · `REQ-002` | `Definition_of_Filed` exige ID, y el regex del título de PR no acepta un PR sin él |
| 3 | Checkpoint jueves 19:00 · entrega viernes 15:00 | Gate jueves 10 **18:00** · entrega a Equipo 5 viernes 11 15:00 · *code freeze* domingo 13 20:00 · entrega lunes 14 | El calendario canónico de S7 es `Plan_Recuperacion_2026-09-09`; la hora del gate y el corte final no los fija este frente |
| 4 | "Equipo ejecutor: Oscar, Juan Macías y Monse" | Equipo 3 completo con Marina como líder | Así lo registran `DEC-022` y el padrón de `ownership.yml` |
| 5 | `prioridad` obligatoria en Pantallas 4 y 5 | **Resuelto por `ADR-011` §5 y `DEC-024`:** se sustituye por el **nivel de atención** derivado de `indice_riesgo`. El front **no consume** `gold.recomendaciones.prioridad` | `BUG-063` deja su corte `ALTA` por encima del techo del fenómeno. El PO resolvió derivarlo en presentación en vez de esperar a rematerializar Gold. **El contrato expone `prioridad` desde el 2026-09-11 y la resolución no cambia: se expone, no se consume** (§10.quinquies) |
| 6 | Etiqueta Alto / Medio / Bajo "conforme a la definición oficial disponible" | **Resuelto por `ADR-011` §5:** alta `>= 0.50`, media `>= 0.30 y < 0.50`, baja `< 0.30`. Es la misma etiqueta del punto 5, no una segunda | No existía esa definición. Los cortes reutilizan `LINEA_DE_ALERTA` (`DEC-019`) y `RIESGO_ESTABLE`, ya ratificados |
| 7 | "Watson" como nombre del chat | **Resuelto por `ADR-011` §6:** el nombre de producto es **Asistente FARO**. No se usa "Watson" | El nombre no existía en ningún documento y la decisión de producto es del PO con el Equipo 2 |
| 8 | "Las gráficas deben construirse directamente en Front" | **Resuelto por `ADR-011` y `DEC-023`:** concedido. Superset deja de ser la navegación principal y **permanece como evidencia analítica y respaldo** | `ADR-011` supersede a `ADR-002` sólo en la obligación de embeber Superset como experiencia principal. Lo ejecuta el Equipo 5 |

---

## 1. Objetivo

Rediseñar la experiencia UX/UI de FARO para que el usuario entienda de forma intuitiva qué ocurre con
las escuelas en riesgo y llegue a una conclusión clara:

> **Identificar los 3 drivers dominantes que más se repiten entre las escuelas en riesgo, entender la
> problemática que muestran los datos y conocer la recomendación asociada.**

La experiencia se diseña principalmente para el evaluador, pero debe seguir siendo clara para
cualquier persona que consulte FARO tras autenticarse.

Responde a tres de los hallazgos del profesor del 9-sep: experiencia visual no satisfactoria,
gráficas sin valor comunicado y ausencia de una historia de negocio.

---

## 2. Principio de storytelling

La experiencia se presenta como una investigación profesional y sutil. No convierte a FARO en un
juego ni usa una estética detectivesca caricaturesca. El usuario debe sentir que:

1. encuentra una señal;
2. revisa los casos;
3. analiza la evidencia;
4. identifica qué driver destaca;
5. llega a una conclusión;
6. conoce la recomendación;
7. después puede explorar otras escuelas.

La Pantalla 1 todavía no revela cuántas escuelas hay en riesgo. Esa revelación ocurre en la Pantalla 2.

La conclusión oficial siempre se calcula sobre **el conjunto completo de escuelas en riesgo**,
independientemente de los filtros usados durante la exploración.

---

## 3. Datos y guardarraíles

La nueva UX/UI puede reorganizar por completo las visualizaciones existentes. Sin embargo:

- Front consume únicamente datos Gold a través de la API;
- se usan los endpoints que ya existen (§10 lista el mapeo verificado);
- **no se inventan métricas, datos, drivers ni explicaciones**;
- si un dato existe en Gold pero ningún endpoint actual lo expone, queda fuera del alcance **o se
  tramita como petición explícita en §11** — no se dibuja como si existiera. `DEC-024` añade una
  tercera salida: representar la pieza que falta con **fixture contractual o `SIN_DATO`**, para no
  detener el diseño ni las pruebas mientras el dato real llega;
- no se afirma causalidad;
- se usa lenguaje como **driver dominante**, **factor que destaca**, **principal línea de
  investigación** o **factor asociado**;
- donde no hay dato se marca `SIN_DATO` explícito: nunca cero, nunca nulo silencioso.

Los 6 drivers oficiales son: **D1** pobreza y rezago · **D2** inseguridad · **D3** infraestructura ·
**D4** conectividad · **D5** estrés hídrico · **D6** calidad del aire.

### 3.ter No negociables heredados de `ADR-011` §4

La libertad de rediseño no toca nada de esto, y aplica a los cuatro entregables:

PRD · contratos de datos y de API · OAuth2/JWT y RBAC · **WCAG 2.1 AA** · `SIN_DATO` explícito ·
filtros de ciclo, entidad y nivel · no causalidad · pruebas y trazabilidad por PR.

Un cambio total de framework sólo se acepta si conserva despliegue, autenticación, pruebas y plazo
(`ADR-011` §3).

### 3.quater Nivel de atención — la etiqueta que sustituye a `prioridad`

`ADR-011` §5 y `DEC-024` fijan una sola etiqueta, derivada en el front desde `indice_riesgo`:

| Nivel de atención | Corte | Constante que lo respalda |
|---|---|---|
| alta | `indice_riesgo >= 0.50` | `LINEA_DE_ALERTA` (`DEC-019`), `src/api/repositorio_gold.py:55` |
| media | `>= 0.30` y `< 0.50` | `RIESGO_ESTABLE`, `src/modelos/riesgo.py:76` |
| baja | `< 0.30` | — |

**El front no consume `gold.recomendaciones.prioridad`** mientras esa columna siga calculada con el
ancla histórica `0.60`.

> **Corrección del 2026-09-11.** Hasta hoy esta regla era, además, imposible de desobedecer: el campo
> no existía en el contrato. **Ya existe** — `PrediccionOut.prioridad`, `"alta" | "media" | "baja"`,
> expuesto por Christian Imanol Ruiz (`ec1b43b`) y documentado en `API_Specification` §3.4. La regla
> sigue igual y ahora sí hay que sostenerla a mano. Ver §10.quinquies.
> **Advertencia que hay que decir en voz alta, no descubrir el domingo.** La columna Gold `prioridad`
> asigna `ALTA` con `>= 0.60` y `MEDIA` con `>= 0.30` (`src/modelos/publicar_gold.py:197`). O sea que
> **coincide con el nivel de atención en el corte de media y baja, y difiere sólo entre 0.50 y 0.60**
> — exactamente donde viven las escuelas en riesgo, porque el máximo observado es `0.5717`. En la
> práctica: el front dirá *atención alta* para esas escuelas y la columna Gold dirá `MEDIA` para las
> mismas. Las dos son correctas según su propia definición. Como Superset permanece disponible como
> evidencia (`DEC-023`) y DB-09 expone esa columna, **el glosario debe explicar que el nivel de
> atención es un corte de presentación, distinto de la prioridad publicada en Gold.** Es la lectura
> honesta de `ADR-011` §5, no una excepción a él.

### 3.bis El número de escuelas en riesgo

`DEC-019` separó el ancla de la sigmoide (`0.60`, no se toca) de la línea de alerta (`0.50`), y con
`0.50` son **7 escuelas de 45 276**. Los modelos de dbt en `main` ya calculan con `>= 0.5`.

La rematerialización ya ocurrió: la QA de los nueve tableros del 2026-09-08 (Monserrat Miranda,
`TEST-PLAN-PRE-DEMO`) verificó **KPI-04 = 7 en DB-02 contra producción**, con 44 114 escuelas y
completitud de 62 %.

`ADR-011` resuelve **P-05** a nivel de contrato: `KpisOut`, el OpenAPI, el repositorio Gold, el mock
y las pruebas ya usan `escuelas_en_riesgo` con `LINEA_DE_ALERTA = 0.50`, y la comprobación por
despliegue pasa al **smoke continuo de QA** (`US-651`), que no bloquea construcción.

**Aun así, los entregables siguen escribiendo "N escuelas en riesgo" y nunca un literal.** No
contradice al PO: lo refuerza. Si la comprobación vive en el smoke de QA, un número tecleado a mano
en la copy es justo lo único que ese smoke no puede detectar. En producción el número se resuelve del
dato en vivo; en los mockups va `N`.

---

## 4. El Asistente FARO durante la experiencia

**Nombre de producto: Asistente FARO** (`ADR-011` §6). No se usa "Watson" en ninguna superficie ni en
ningún documento.

Está disponible durante toda la experiencia posterior al login como un botón flotante.

- Es un asistente general: permite consultar datos en lenguaje natural.
- No necesita conocer automáticamente la pantalla ni la escuela que el usuario está viendo.
- **Su lógica funcional pertenece al Equipo 2** (`US-611`). Este frente define únicamente su
  presencia, comportamiento visual y coherencia con la identidad.
- El walkthrough inicial menciona brevemente que está disponible durante todo el recorrido.

### 4.bis Tres cosas del Equipo 2 que este frente debe diseñar

El diagnóstico del chat ([[vault/15_ML_Models/Diagnostico_Chat_Agente_2026-09-09]], Andrés González)
cambia lo que el usuario ve, así que entra al diseño:

1. **Viene streaming.** La respuesta se muestra mientras se genera. Hay que diseñar ese estado, no un
   spinner que espera varios segundos en silencio.
2. **Los errores se distinguen en tres:** fuera de alcance, sin datos y timeout. Cada uno necesita su
   propio mensaje; "no disponible" para todo es lo que el diagnóstico marca como defecto.
3. **Ya responde preguntas conceptuales sin tocar la base** — *"¿qué significa `SIN_DATO`?"*,
   *"¿cómo se calcula el índice de riesgo?"*. Eso se solapa con el glosario de la §6, y conviene que
   se refuercen: cada término del glosario puede ofrecer preguntárselo al Asistente. Mete el
   asistente dentro de la narrativa en vez de dejarlo como un botón aparte.
4. **El SQL generado no se muestra por defecto.** Ver §4.ter.

### 4.ter El SQL no es la respuesta

**Hoy sí se muestra.** `src/frontend/pages/3_Chat.py:85-87` pinta `respuesta.sql_generado` con
`st.code(..., language="sql")` en cuanto viene, así que la consulta aparece en pantalla dentro de la
conversación.

El profesor lo señaló el 9-sep con estas palabras: *«la explicación no debe reducirse a mostrar
SQL»*. La brecha está asignada al Equipo 2 (`US-611`), pero **qué se pinta y qué no es una decisión
de presentación**, y eso sí es de este frente: la §4 dice que el Equipo 2 es dueño de la lógica y
este frente del comportamiento visual.

**Decisión de UX:**

- El campo `sql_generado` **se conserva en el contrato**. No se pide quitarlo: sirve para auditar,
  para QA y para que el evaluador compruebe que la respuesta sale de la base y no de un texto
  inventado. En una materia de inteligencia de negocios, poder enseñar la consulta es un activo.
- **No se muestra por defecto.** La respuesta que ve el usuario es la redacción en lenguaje natural,
  y nada más.
- Queda **detrás de una acción discreta y opcional** —del tipo *ver consulta*—, cerrada de inicio y
  fuera del hilo de lectura.

Así se atiende la observación del profesor sin perder la auditabilidad, que es lo que se perdería si
el campo se eliminara del contrato.

**Implementa el Equipo 2 o el Equipo 5**, según dónde viva el componente. Este frente sólo lo
especifica.

---

## 5. Arquitectura de la experiencia

El entregable visual contempla **7 mockups**: un login y 6 pantallas.

### Mockup 0 — Login

**Objetivo:** homologar el acceso con la nueva identidad.

> **Corrección del 2026-09-10.** La versión anterior de esta ficha decía *"los campos y acciones del
> login actual"*. **Era falso y hay que decirlo, porque manda a diseñar una pantalla que no existe.**
> Verificado en `src/frontend/auth.py:194`: el acceso es **un solo botón**,
> `st.link_button("Iniciar sesión con Google", ...)`, que redirige al consentimiento de Google
> (OAuth2, `GET /api/v1/auth/login`). **No hay usuario, no hay contraseña, no hay formulario.**

**Contiene:** nueva identidad y tratamiento del logo; **un único botón de acceso con Google**; recurso
visual alineado a la narrativa. Es una pantalla de una sola acción, y el diseño debe aprovecharlo: casi
todo el espacio es narrativa e identidad.

**No lleva:** campos de usuario o contraseña, ni "¿olvidaste tu contraseña?", ni registro. Tampoco un
estado de *credenciales inválidas*: un fallo de OAuth vuelve por el callback, no por un campo mal
escrito. Los estados reales son **en reposo**, **redirigiendo a Google** y **error de vuelta del
callback**, con mensaje genérico y sin detalle interno.

**Qué cambió por debajo, y por qué la pantalla no lo refleja.** `ADR-012` (`accepted`, 2026-09-11)
movió la sesión a una cookie `httpOnly` que la API pone a través del proxy: el frontend **deja de
manejar tokens** —no los guarda, no los refresca, no los adjunta— y aparece `POST /auth/logout`. Nada
de eso es visible en esta pantalla, que sigue siendo el botón de Google, pero **la ficha ya no puede
decir que no cambia la lógica funcional**, porque cambió. Lo que no cambia son los permisos ni lo que
el usuario ve aquí.

### Pantalla 1 — Entrada

**Objetivo:** explicar qué es FARO y cuál será el propósito del usuario antes de revelar los casos.
**Contiene:** qué es FARO; objetivo del proyecto; imágenes que introducen la historia; explicación
breve del propósito del usuario; CTA principal; acceso a glosario; Asistente FARO flotante; un único
walkthrough inicial, sencillo y breve.
**No revela todavía:** cuántas escuelas están en riesgo.

### Pantalla 2 — Panorama de las escuelas en riesgo

**Objetivo:** revelar los casos y presentar el panorama general.
**Contiene:** revelación clara del número de escuelas en riesgo; información general de matrícula —la
matrícula se muestra únicamente aquí dentro de la historia—; riesgo; filtros limitados; visualización
principal definida por Monserrat; CTA hacia la selección de caso; Asistente FARO flotante.

Monserrat tiene libertad creativa sobre la visualización, dentro de los datos y endpoints existentes.

### Pantalla 3 — Selección de caso

**Objetivo:** que el usuario elija libremente una escuela.
**Contiene:** las escuelas identificables; índice de riesgo numérico; **nivel de atención** según
§3.quater; CTA para abrir el caso.
El usuario **no necesita revisar todas**: puede investigar una sola y continuar.

### Pantalla 4 — Expediente de una escuela

**Objetivo:** entender qué driver destaca y cuál es la recomendación.
**Contiene:** nombre de la escuela; índice de riesgo numérico; **nivel de atención** (§3.quater);
nota al pie o tooltip que explique qué calcula el índice **y qué significa el nivel de atención**;
gráfica comparativa de los 6 drivers; highlight claro del driver dominante; recomendación
correspondiente; regreso a selección; avance hacia la conclusión; Asistente FARO flotante.
**No incluye:** evolución histórica de matrícula.
Por restricción de tiempo no se desarrolla explicabilidad adicional del modelo ni métricas nuevas
para justificar el driver dominante; se usa la contribución que ya entrega `/explicacion`.

### Pantalla 5 — Conclusión Top 3

**Objetivo:** cerrar la historia con el principal hallazgo.
**Muestra:** los 3 drivers dominantes más frecuentes entre las escuelas en riesgo; número o proporción
de escuelas en las que cada uno aparece como dominante; problemática sustentada únicamente en los
datos existentes; recomendación general asociada a cada driver; distribución de niveles de atención
si aporta (§3.quater).

Debe indicarse explícitamente:

> **Esta conclusión se calcula sobre el conjunto completo de escuelas en riesgo, independientemente
> de los filtros utilizados durante la exploración.**

Sin drill-down adicional. **Un único CTA principal:** avanzar a la exploración de otras escuelas.

### Pantalla 6 — Exploración de otras escuelas

**Objetivo:** permitir continuar después de la historia.
Oscar propone 2–3 nombres comprensibles. No debe llamarse "ML" de cara al usuario.
**Contiene:** un único pop-up sencillo al entrar por primera vez; los filtros obligatorios del
proyecto —ciclo, entidad y nivel educativo, los tres soportados hoy—; filtros adicionales sólo si ya
están soportados; selección de escuela; reutilización de la lógica del expediente (índice, etiqueta,
gráfica de 6 drivers, driver dominante, recomendación, nivel de atención); Asistente FARO flotante;
acceso al glosario.

---

## 5.bis "Cómo funciona": la superficie que entrega el Equipo 1

El profesor señaló que **faltó explicar cómo funciona el backend**. Esa brecha es de `US-601`, y el
Equipo 1 ya la construyó: una sección pública llamada **Cómo funciona** con siete apartados.
Documento de referencia: `vault/03_Architecture/Bosquejo_Componentes_US601.md` — dueño formal Héctor
Rafael Morales Marbán, redactada e implementada por Manuel Alejandro Serranía Reinada. Se cita sin
enlace **a propósito**: todavía no está en `main`, y un wikilink a un documento inexistente reprueba
`vault_lint`. Se convierte en enlace cuando aterrice.

Este frente **no la diseña de cero ni la reescribe**: le da identidad y la coloca dentro de la
experiencia.

### Dónde vive

**No es una octava pantalla de la historia.** El recorrido narrativo sigue siendo el de la §5, y los
entregables siguen siendo 7 mockups. *Cómo funciona* es una **superficie hermana**: se llega a ella
desde la Pantalla 1 y desde el glosario, comparte identidad visual y no interrumpe la investigación.

El motivo es de narrativa, no de esfuerzo: la historia va de qué le pasa a las escuelas, no de cómo
está hecho el sistema. Quien quiera auditar el sistema entra ahí; quien quiera seguir la
investigación no tropieza con un diagrama E-R a mitad del camino.

### Qué contiene

Siete apartados que el Equipo 1 ya fijó: `arquitectura` · `modelo-datos` · `capas` · `cubos` ·
`stack` · `decisiones` · `modelos-ml`.

### Cómo se alimenta

Dos rutas, con un contrato pensado para que agregar apartados no rompa nada:

- `GET /api/v1/about/secciones` — el manifest: `[{id, titulo, orden}]`.
- `GET /api/v1/about/secciones/{id_seccion}` — el contenido, siempre con el mismo sobre:
  `{id, titulo, fuente, advertencias, bloques}`.

`bloques` es una lista de **siete tipos**: `markdown`, `mermaid`, `tabla`, `metricas`, `mapa`,
`barras` y `diagrama_flujo`. Los tres últimos son **D3**, que es justo lo que el profesor pidió ver.
Un tipo que el cliente no reconozca se pinta con una advertencia en su propio espacio y **nunca tumba
la página**: es el mismo espíritu de `SIN_DATO` aplicado a la estructura.

El único dato vivo son los conteos de filas por capa. Todo lo demás es contenido fijo, decisión
consciente del Equipo 1 y anotada por ellos como *follow-up*.

### Tres cosas que este frente sí tiene que resolver

1. **La identidad.** Hoy se ve como una página de Streamlit. Con la identidad nueva tiene que dejar
   de parecerlo, aunque no entre al recorrido narrativo. Es trabajo de Juan, con los componentes que
   ya definirá para el resto: no necesita mockup propio, y si sobra tiempo se agrega como octavo.
2. **El contraste de los bloques D3.** Cada bloque D3 vive en **su propio iframe**, y el Equipo 1 ya
   se topó con el defecto: heredaban `prefers-color-scheme: dark` y quedaban letras negras sobre
   fondo negro. Lo resolvieron forzando `color-scheme: light` y fondo blanco explícito. **Si la
   identidad nueva es oscura, esos bloques van a pelear con ella.** Juan tiene que decidirlo a
   propósito, no descubrirlo el sábado.
3. **El acceso.** Oscar define desde dónde se entra y cómo se vuelve, sin romper el hilo de la
   investigación.

### Dependencia declarada

Las dos rutas **todavía no están en `main`**: viven en `dev/manuel-serrania` junto con la página y
sus 54 pruebas. Si no aterrizan, esta superficie no se puede alimentar y se cae del alcance —
como cualquier otra pieza, se declara el recorte y no se dibuja como si existiera.

---

## 6. Glosario

Accesible para usuarios no técnicos. Como mínimo explica en lenguaje sencillo: índice de riesgo ·
driver · driver dominante · recomendación · **nivel de atención** · `SIN_DATO`.

La entrada de **nivel de atención** debe decir, además de qué significa, que es un **corte de
presentación** derivado del índice de riesgo (alta `>= 0.50`, media `>= 0.30`, baja `< 0.30`) y que
**no es** la columna `prioridad` publicada en Gold, que usa el ancla histórica `0.60`. Ver la
advertencia de §3.quater: las dos difieren justo en las escuelas de las que trata la historia.

---

## 7. División de trabajo

> **Marina decide qué historia contamos. Oscar decide cómo se recorre. Monserrat decide qué datos y
> gráficas la demuestran. Juan decide cómo se ve.**

| Persona | Responsabilidad | Archivo propio |
|---|---|---|
| **Marina García del Buey** — líder | Definir la historia oficial; objetivo, alcance y guardarraíles; criterios de aceptación; coherencia transversal; **gate final de UX/UI** | `00_Storytelling_Scope.md` |
| **Oscar Antonio Quiroz Lázaro** — UX / navegación | Flujo de las 7 pantallas; objetivo, contenido, botones y conexiones; walkthrough y navegación; comportamiento UX del chat; 2–3 nombres para la exploración posterior. Su documento es guía directa para el Equipo 5 | `01_UX_Architecture.md` |
| **Monserrat Xcaret Miranda Olivas** — narrativa analítica | Qué dato responde cada pregunta; gráficas de cada pantalla; sólo datos Gold expuestos por endpoints actuales; ejemplos de visualizaciones; cómo se obtiene y comunica el Top 3; **la leyenda de cada gráfica** (§7.bis), que se escribe **dentro de** `02_Data_Visualization_Spec.md` y no en un documento aparte | `02_Data_Visualization_Spec.md` |
| **Juan Carlos Macías Mayen** — UI / identidad visual | Identidad visual desde cero: logo, paleta, tipografías, componentes, botones, cards, iconografía, imágenes, efectos, apariencia del Asistente FARO y los 7 mockups. Mantiene `03_Visual_Identity.md` como **guía de identidad de referencia** y su anexo técnico de tokens (§7.ter) | `03_Visual_Identity.md` |

Monserrat entrega a Juan los ejemplos de gráficas y el contenido analítico aprobado.
Ningún integrante modifica el entregable de otro sin coordinación previa.

---

### 7.bis Leyenda de las gráficas — sugerencia del checkpoint

Salió en el checkpoint y entra al alcance de Monserrat: **cada gráfica debe explicar qué se está
viendo.** No estaba en la versión anterior del plan.

No es la leyenda mínima de colores que trae cualquier librería. Lo que se pide es que el usuario
—que no es técnico y que llega sin contexto— pueda leer una gráfica sin que nadie se la explique en
voz alta. Como mínimo, por gráfica:

- qué representa cada eje, serie o color, con nombres en lenguaje de negocio y no de base de datos;
- en qué unidad está el valor, y si es proporción, conteo o índice;
- cómo se ve un `SIN_DATO` ahí dentro y por qué no es un cero;
- de qué ciclo y qué recorte de escuelas está hablando.

Monserrat decide la forma —leyenda fija, nota al pie, tooltip o una mezcla— y Juan le da tratamiento
visual. Debe resolverse en las gráficas de la historia y también en las del Explorador de escuelas.

**Dónde se escribe:** dentro de `02_Data_Visualization_Spec.md`, como una sección propia. No es un
documento aparte — la regla 1 del vault prohíbe abrir un archivo nuevo para algo que pertenece a un
canónico existente. Es parte de la entrega del viernes de Monserrat (§8).

**Alcance: por gráfica, no por pantalla.** Hay gráficas en P2, P3, P4, P5 y P6 —la matriz de casos,
la pista del índice, la comparativa de los 6 drivers, la gráfica de unidades del Top 3 y las
reutilizadas en el Explorador—, así que la leyenda aplica en las cinco. Acotarla a dos pantallas deja
tres sin cubrir.

Es directamente una respuesta al hallazgo del profesor sobre visualizaciones que no comunicaron
valor: una gráfica que hay que explicar en vivo no comunica sola.

---

### 7.ter La guía de identidad y el retiro del PDF

**Decisión del 2026-09-11, a propuesta de Juan Macías.** El entregable `FARO_UX_UI_Guide.pdf` **se
retira** del alcance y del criterio de cierre.

**Por qué.** Un PDF duplica documentos que ya están versionados y se desactualiza en cuanto se mueve
un token, con la sincronización a mano como única defensa. El Equipo 5 puede copiar valores exactos
del `.md` y tendría que transcribirlos de un PDF. Y hay dos razones que pesan más que el
mantenimiento: **no responde a ninguno de los hallazgos del profesor** —que fueron sobre experiencia,
gráficas, storytelling, componentes, chat y ML, ninguno sobre documentación— y `DEC-024` ya fijó que
las únicas compuertas son rama personal, PR, CI, una aprobación humana y QA sobre la candidata. Un
PDF no es ninguna de ellas.

**Qué ocupa su lugar.** Nada nuevo: el documento ya existe.

| Artefacto | Papel | Requisito |
|---|---|---|
| `03_Visual_Identity.md` | **Guía de identidad de referencia.** Contiene el sistema de color de datos, que es la parte que la historia necesita | Ya tiene `id`, `owner`, `status` y trazas |
| `mockups/Design_Tokens_Stitch.md` | **Anexo técnico** de la anterior: paleta de interfaz, tipografía, radios, espaciado, elevación | **Le falta frontmatter propio** con `id`, `owner` y `status`, y quedar listado en `mockups/_index.md` |
| `mockups/_index.md` | Índice de la carpeta donde viven los 7 mockups | **No existe.** Lo exige la regla 4 |

**Lo que no se aceptó de la propuesta original.** Se planteó que el anexo de tokens sustituyera al PDF
como entregable final. No puede: su frontmatter es el YAML crudo de Stitch, sin `id`, `owner` ni
`status`, así que incumple la regla 2 y `Definition_of_Filed`; su propio encabezado lo declara *"no es
un artefacto canónico del vault"*; y por esa misma nota **el sistema de color de datos no vive ahí**,
sino en `03_Visual_Identity.md` §3. Un anexo no puede ser la guía.

**Trazabilidad.** Es un cambio a un criterio de cierre de `US-621`, cuyo *go/no-go* pertenece al PO.
Se registra aquí en vez de desaparecer en silencio, y se le comunica.

---

## 8. Entregables y calendario

Alineado a `Plan_Recuperacion_2026-09-09`. Cada integrante trabaja en su rama fija `dev/{identidad}`,
sincroniza con `git merge origin/main` y entra por PR. No se requiere merge a `main` para dar por
cumplido un gate interno, pero sí para que el Equipo 5 lo consuma.

### Jueves 10 — gate del frente, antes de las 18:00

Borrador formal committeado por cada integrante. Sin código productivo en este gate.

| Persona | Archivo | Debe contener |
|---|---|---|
| Marina | `00_Storytelling_Scope.md` | Objetivo, público, storytelling, alcance, reglas, arquitectura acordada, criterios de aceptación iniciales |
| Oscar | `01_UX_Architecture.md` | Flujo de las 7 pantallas, ficha breve por pantalla, botones, conexiones, filtros, walkthrough, chat, propuestas de nombre |
| Monserrat | `02_Data_Visualization_Spec.md` | Propuesta de visualización por pantalla, variables necesarias, endpoint actual que la sostiene, ejemplos iniciales |
| Juan | `03_Visual_Identity.md` | **2–3 rutas visuales**, cada una con logo, paleta, tipografías, cards, botones, iconografía, tratamiento de gráficas, imágenes, chat, estados de riesgo y tratamiento del driver dominante |

**Gate del jueves:** Marina selecciona una ruta visual.

### Viernes 11 — entrega a Equipo 5, 15:00

Es la fecha que importa: el Equipo 5 (Diana Alvarez) implementa a partir de aquí.

**No es una compuerta secuencial.** `DEC-024` establece que los seis frentes construyen y prueban en
paralelo contra contratos versionados: el Equipo 5 no espera a que esté todo para empezar
componentes, y este frente entrega de forma incremental lo que ya esté cerrado. La fecha marca
cuándo la especificación deja de moverse, no cuándo empieza la implementación.

- Marina: `00_Storytelling_Scope.md` final.
- Oscar: `01_UX_Architecture.md` final.
- Monserrat: `02_Data_Visualization_Spec.md` final —**con la leyenda de la §7.bis escrita**— más los
  ejemplos finales de visualizaciones.
- Juan: `03_Visual_Identity.md` final, los 7 mockups de escritorio, el anexo de tokens con
  frontmatter propio y `mockups/_index.md` (§7.ter).

```text
FARO_Storytelling_UX/
├── ejemplos_graficas/          Monserrat — ejemplos de visualización que integra Juan
└── mockups/
    ├── 00_Login.png
    ├── 01_Entrada.png
    ├── 02_Panorama_Escuelas_Riesgo.png
    ├── 03_Seleccion_Caso.png
    ├── 04_Expediente_Escuela.png
    ├── 05_Conclusion_Top3.png
    └── 06_Explorador.png
```

`ejemplos_graficas/` se da de alta a petición de Monserrat: sus ejemplos no tenían ubicación en la
estructura anterior. Queda registrada en
[[vault/04_UX_Design/FARO_Storytelling_UX/_index]] (regla 4 del vault).

Escritorio es obligatorio. Móvil queda como evolución futura.

### Jueves 10 por la noche — entrega intermedia de Monserrat a Juan

**Corregido el 2026-09-10 a petición de Monserrat Miranda.** La versión anterior de este plan ponía
sus ejemplos de visualización y los 7 mockups de Juan en el **mismo corte** del viernes 15:00, y a la
vez decía que ella le entrega a él para que los integre a la identidad. Las dos cosas no caben: si
los recibe a las 15:00 no le alcanza.

Monserrat entrega sus ejemplos **hoy después del gate**, y **Juan define el formato**, porque es quien
integra. Esa entrega es un intercambio interno del frente, no un hito del proyecto: no se espera a
que esté completa para seguir.

---

### Sábado 12 a lunes 14 — acompañamiento

El frente no cierra el viernes: acompaña al Equipo 5 durante la integración, responde dudas de
implementación y valida el recorrido en la candidata. *Code freeze* domingo 13 a las 20:00; entrega
el lunes 14 a primera hora.

---

## 9. Criterios de aceptación propuestos

Definidos inicialmente por este frente. El Equipo 6 (QA, `US-651`) puede ampliarlos.

### 9.bis Cómo se verifica cada criterio

Los 29 criterios no se comprueban igual, y tratarlos como si sí duplica el trabajo de QA. Se
clasifican en tres formas de verificación, para que el Equipo 6 no tenga que hacer ese triaje:

| Forma | Qué significa | Criterios |
|---|---|---|
| **A · En el artefacto** | Se comprueba leyendo los documentos y los mockups de este paquete, sin desplegar nada. Se puede hacer hoy | 6, 7, 10, 11, 13, 15, 16, 17, 20, 21, 23, 24, 25, 26, 28 |
| **B · En la candidata desplegada** | Exige la URL viva: datos reales, estados de carga y error, comportamiento del Asistente | 2, 3, 4, 8, 12, 14, 18, 19, 27, 29 |
| **C · Pasada humana** | No se automatiza: alguien que no conoce FARO tiene que recorrerlo y decir si entendió | 1, 5, 9, 22 |

**Los de forma C son los que más valen y los que más fácil se saltan.** El criterio 1 —*"una persona
que no conoce FARO entiende desde la entrada qué busca el proyecto"*— es exactamente lo que el
profesor evaluó el 9-sep, y no hay prueba automática que lo cubra. Conviene que QA reserve a alguien
que no haya trabajado en el frente.

Los de forma A pueden ejecutarse **antes** del despliegue y no deberían esperar a la candidata.

Molde disponible si el Equipo 6 quiere un plan formal:
[[vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB03_DB04]].

1. Una persona que no conoce FARO entiende desde la entrada qué busca el proyecto y qué debe hacer.
2. La Pantalla 2 revela de forma inequívoca cuántas escuelas están en riesgo.
3. El usuario puede seleccionar cualquiera de ellas sin tener que revisar las demás.
4. El índice de riesgo se muestra con valor numérico y con su **nivel de atención** (§3.quater).
5. El significado del índice de riesgo se explica en lenguaje sencillo.
6. El expediente muestra simultáneamente los 6 drivers.
7. El driver dominante queda visualmente destacado.
8. La recomendación proviene de datos existentes. El nivel de atención se **deriva** de
   `indice_riesgo` en el front; ninguna superficie consume `gold.recomendaciones.prioridad`.
9. Ningún texto afirma causalidad que los datos no puedan demostrar.
10. La conclusión muestra los 3 drivers dominantes más frecuentes sobre el conjunto completo.
11. La Pantalla 5 lo indica explícitamente.
12. La problemática presentada está sustentada únicamente por los datos disponibles.
13. La Pantalla 5 tiene un solo CTA principal.
14. El Asistente FARO permanece visible como componente flotante tras el login, con estado de
    streaming y tres mensajes de error distinguibles (§4.bis).
15. Existe un único walkthrough sencillo al inicio.
16. Existe un único pop-up sencillo al entrar por primera vez a la exploración.
17. El glosario explica los términos mínimos acordados.
18. Toda visualización propuesta puede construirse con endpoints existentes, con una resolución de
    §11 o con fixture contractual rotulado como tal (`DEC-024`).
19. Ninguna gráfica requiere un endpoint no acordado.
20. Los 7 mockups comparten una identidad visual consistente.
21. La arquitectura indica objetivo, contenido, botones y conexión de cada pantalla.
22. El Equipo 5 puede implementar con arquitectura + especificación + mockups sin redefinir UX.
23. Escritorio queda completamente resuelto.
24. La identidad propuesta no depende de la identidad visual anterior de FARO.
25. El glosario distingue el **nivel de atención** de la columna `prioridad` de Gold.
26. Ninguna superficie usa el nombre "Watson".
27. La sección *Cómo funciona* comparte la identidad visual del producto y se alcanza desde la
    entrada y desde el glosario, sin interrumpir el recorrido narrativo.
28. Toda gráfica explica qué se está viendo conforme a la §7.bis: ejes o series, unidad, tratamiento
    de `SIN_DATO`, ciclo y recorte. **Aplica también a los tres bloques D3 de la §5.bis** —`mapa`,
    `barras` y `diagrama_flujo`—, donde la leyenda puede vivir en el bloque `markdown` adyacente: es
    el mecanismo que el Equipo 1 ya usa en la sección `cubos` y no exige cambio de contrato.
29. La conversación del Asistente no muestra el SQL generado por defecto; si se ofrece, es tras una
    acción opcional y cerrada de inicio (§4.ter).

---

## 10. Mapeo verificado contra la API v1

Verificado contra `api/openapi.v1.json` el 2026-09-10. Este mapeo es el que hace exigible el
guardarraíl de §3: lo que no está aquí, no se dibuja.

| Necesidad | Endpoint | Campos |
|---|---|---|
| Las escuelas en riesgo, ordenadas | `GET /api/v1/escuelas` con `order_by=indice_riesgo` y `order=desc` | `cct`, `nombre`, `nivel`, `matricula_total`, `indice_riesgo`, `driver_dominante`, `tiene_prediccion`, **`latitud`, `longitud`** (subidas del detalle al listado el 2026-09-11; `None` es `SIN_DATO` real y esa escuela se omite del mapa, nunca se dibuja en el `(0, 0)`) |
| Los 6 drivers de una escuela | `GET /api/v1/escuelas/{cct}` | `d1`…`d6`, `indice_completitud_drivers`, `es_estimado_por_grupo`, `sostenimiento`, `latitud`, `longitud` |
| Recomendación y driver dominante | `GET /api/v1/predicciones/{cct}` | `indice_riesgo`, `driver_dominante`, `recomendacion`, `cluster`. **`prioridad` viaja y no se consume** — ver §10.quinquies |
| Evidencia del driver dominante | `GET /api/v1/predicciones/{cct}/explicacion` | `contribuciones` (SHAP), `driver_dominante`. **El endpoint responde, pero las contribuciones vienen vacías** — ver §10.quater |
| Panorama y matrícula | `GET /api/v1/kpis` | `matricula_total`, `variacion_matricula`, `escuelas_en_riesgo`, `indice_completitud_drivers` |
| Filtros de la exploración | `/escuelas`: `ciclo`, `cve_ent`, `cve_mun`, `nivel` · **`/kpis`: sólo `ciclo`, `cve_ent`, `cve_mun`** | **`/kpis` no acepta `nivel`.** El filtro de nivel actúa sobre la lista de escuelas, nunca sobre los indicadores. Verificado por Monserrat Miranda |
| Chat | `POST /api/v1/agente/consulta` | frente del Equipo 2. **Nombre técnico**, no de producto: lo que ve el usuario es *Asistente FARO* |
| Sección *Cómo funciona* (§5.bis) | `GET /api/v1/about/secciones` · `GET /api/v1/about/secciones/{id_seccion}` | manifest `[{id, titulo, orden}]` y sobre `{id, titulo, fuente, advertencias, bloques}`. **Pendientes de merge**: viven en `dev/manuel-serrania` |

### 10.quater La explicación SHAP existe como endpoint y no como dato

**Corrección del 2026-09-10, hallazgo de Monserrat Miranda.** La versión anterior de la tabla de
arriba listaba `/predicciones/{cct}/explicacion` → `contribuciones` como evidencia disponible del
driver dominante. **Prometía algo que hoy no se puede dibujar.**

`BUG-053` está `fixed` en el sentido correcto —el código lee `gold.recomendaciones.shap_d1…shap_d6`
por `RepositorioModelos`— pero **esas columnas no están pobladas en producción**: existen tras el
`ALTER` de C5 y siguen en `NULL`. Monserrat lo midió el 10-sep: **0 de 42**. El endpoint responde
200 y las contribuciones vienen vacías.

**Consecuencia para el diseño:** el expediente **no** puede mostrar la contribución de cada driver.
Muestra el driver dominante, que sí viene en `PrediccionOut` y en `EscuelaOut`, y declara la
explicación como `SIN_DATO` explícito. Si el Equipo 4 puebla las columnas, la pieza entra sin cambio
de contrato.

Queda dicho aquí y no sólo en el documento de visualizaciones, porque era esta §10 la que lo
prometía.

---

### 10.quinquies `prioridad` ya viaja en el contrato, y sigue sin consumirse

**Cambio del 2026-09-11, de Christian Imanol Ruiz (`ec1b43b`, PR #332, ya en `main`).**
`PrediccionOut` expone **`prioridad`**: `"alta" | "media" | "baja"`, leída de
`gold.recomendaciones`, `None` cuando no hay fila. Viaja en `GET /predicciones/{cct}` y en
`POST /predicciones/batch`. Está documentada en `API_Specification` §3.4.

Hasta ayer, la regla de §3.quater —*el front no consume `prioridad`*— se sostenía sola: el campo no
existía y no había nada que desobedecer. Hoy existe. **Esta sección es la que la sostiene.**

**El front no la consume. Ninguna pantalla, ningún filtro, ningún orden, ningún texto.** El nivel de
atención se deriva de `indice_riesgo` con `LINEA_DE_ALERTA` (§3.quater) y de ninguna otra cosa.

**Por qué, en un número.** `publicar_gold.prioridad_de_riesgo()` asigna `ALTA` sólo con
`riesgo >= ANCLA_SIGMOIDE` (0.60) y el máximo que ML-01 predice sobre el Gold publicado es
**0.5717**. Es decir: **ninguna de las 45 276 filas es `alta`** (`BUG-063`, `open`). Si el expediente
pintara el chip con `prioridad`, **las siete escuelas de las que trata toda la historia dirían
«media» en la pantalla que acaba de decir que están en riesgo.** No es una diferencia de matiz entre
dos cortes: es la contradicción visible, en la pantalla del diferenciador.

**El riesgo real no es discrepar, es confundirse.** Los tres valores del campo se llaman **igual** que
nuestros tres niveles. Quien lea el contrato sin leer esto los va a conectar, y el bug se va a ver
como un dato, no como un error. Por eso queda escrito aquí, en la sección que el Equipo 5 usa como
mapa, y no sólo en el glosario.

**Qué sí cambia con esto:** nada del diseño. `BUG-063` puede alinearse después —es decisión del PO y
del TL de C3, y realinear el corte reescribe las 45 276 filas publicadas, que es justo lo que
`DEC-019` prohíbe— **sin bloquear ni retocar una sola pantalla**. El día que `prioridad` siga la línea
de alerta, coincidirá con el nivel de atención y el front podrá consumirla y retirar su derivación.
Mientras tanto, se deriva.

> **Corrección pedida a `API_Specification` §3.4.** Ese texto describe `prioridad` como *«la urgencia
> con la que el storytelling ordena los casos»*. **No es así:** el storytelling ordena por
> `indice_riesgo` descendente. Pedida la corrección a su autor el 2026-09-11.

### 10.sexies Coordenadas en el listado, y entidad en los municipios

Del mismo cambio, dos campos que **sí** nos sirven:

- **`latitud`/`longitud` en `EscuelaOut`.** Antes vivían sólo en el detalle: pintar siete marcadores
  costaba siete llamadas. `None` es `SIN_DATO` real —hay escuelas sin georreferencia— y esa escuela
  se **omite** del mapa; dibujarla en el `(0, 0)` sería inventar una ubicación.
- **`cve_ent` y `nombre_entidad` en `MunicipioOut`.** Sin ellos, el cliente tenía que mantener su
  propio mapa de cuatro claves a nombre, o pintar `"09"` en una etiqueta. Un diccionario de nombres
  tecleado en el front es exactamente el patrón de `BUG-058` que persigue la §3.bis. Ahora sale del
  contrato.

> **Consecuencia que hay que resolver con el Equipo 5, no aquí.**
> `02_Data_Visualization_Spec` descarta el mapa **dos veces** —§3.3, entre las alternativas
> rechazadas de la Pantalla 2, y §8.1, entre los recortes explícitos— con la misma razón:
> *«ningún endpoint expone geometría y `latitud`/`longitud` sin base cartográfica no se leen»*.
> **Esa mitad de la razón ya no se sostiene:** el frontend de React trae `d3-geo` y una base
> versionada en `frontend/src/data/geo/mexico-states.json`, y `Arquitectura_Frontend_React.md` §5 ya
> compromete `MapaRiesgo.jsx` y una ruta `/mapa`. La base cartográfica existe; vive en el front, no en
> la API. **Se está construyendo un mapa que nuestra especificación aprobada declara recortado.**
>
> **La otra mitad sigue en pie y es la que hay que discutir, no la técnica:** *dónde* no responde *qué
> situación*, las siete escuelas caen en dos municipios, y la base disponible es **estatal**, no
> municipal — pintar siete puntos sobre el contorno de dos estados no distingue nada. Si el mapa se
> queda, necesita una lectura que aporte y no puede ser la única forma de leer el riesgo (`ADR-011`
> §4). Entra al *handoff* con Diana Álvarez junto con la reconciliación de rutas; no se resuelve por
> decisión de este documento ni por edición de uno ajeno.

---

### 10.bis Dos cosas que el contrato no hace, y cómo se resuelven

Reportadas por Monserrat Miranda el 2026-09-10 al verificar el contrato. Van escritas para que el
Equipo 5 no las descubra al implementar:

1. **`/api/v1/escuelas` no tiene filtro por `indice_riesgo`.** El corte en la línea de alerta se hace
   **del lado del cliente**. No obliga a recorrer las 45 276 escuelas: el endpoint sí acepta
   `order_by=indice_riesgo` con `order=desc`, así que **una sola llamada con `size=100`** trae las de
   mayor riesgo y se corta en cuanto el valor baja de `0.50`.
2. **No existe endpoint que devuelva el Top 3 agregado.** Se calcula en Front sobre el conjunto que
   devuelve esa misma llamada.

### 10.ter El nombre visible del chat todavía no está en el código

`src/frontend/pages/3_Chat.py:33` imprime hoy `st.title("Agente FARO")`, que es el nombre **técnico**
del módulo (`src/agente/**`, `/api/v1/agente/consulta`) y no el de producto que fija `ADR-011` §6.

Cambiarlo toca tres líneas, y las dos últimas son la trampa: `tests/test_frontend_chat_streamlit.py`
**afirma el literal viejo** en las líneas **77** y **114**. Quien cambie el título sin tocar las
pruebas rompe CI. Es trabajo del Equipo 5, dueño de `src/frontend/**`, o del Equipo 2.

Los nombres técnicos **no se tocan**: sólo cambia la cadena que ve el usuario.

| Nivel de atención | se **deriva** en Front de `indice_riesgo` | ver §3.quater |

**`prioridad` ya existe en el contrato y este frente sigue sin consumirla.** `ADR-011` §5 resolvió
derivar el nivel de atención en presentación, y esa resolución no cambia porque el campo ahora viaje.
Ver §10.quinquies.

---

## 11. Resoluciones del PO

Las seis peticiones que abrió este plan quedaron **cerradas el 2026-09-10** por
[[vault/03_Architecture/ADRs/ADR-011-rediseno-ux-graficas-nativas]], `DEC-023` y `DEC-024`. Se
conservan con su número porque el `ADR` y la matriz las citan así.

| # | Qué se pidió | Resolución |
|---|---|---|
| **P-01** | Exponer `prioridad` y decidir el corte de `BUG-063` | **Se expone desde el 2026-09-11 y no se consume.** El front deriva el **nivel de atención** desde `indice_riesgo` (§3.quater). El corte de `BUG-063` sigue `open` y puede alinearse después sin bloquear UX (§10.quinquies) |
| **P-02** | Definición oficial de las bandas | alta `>= 0.50` · media `>= 0.30 y < 0.50` · baja `< 0.30`. Reutiliza `LINEA_DE_ALERTA` y `RIESGO_ESTABLE` |
| **P-03** | Nombre del chat | **Asistente FARO.** No se usa "Watson" |
| **P-04** | ADR para retirar Superset de la experiencia | Concedido. Superset deja de ser la navegación principal y **permanece como evidencia analítica y respaldo** |
| **P-05** | Confirmar `escuelas_en_riesgo` en `/api/v1/kpis` | Resuelto a nivel de contrato; la comprobación por despliegue pasa al smoke continuo de QA (`US-651`) y no bloquea construcción. La regla de §3.bis sigue en pie |
| **P-06** | Qué documento manda en UX | **`FARO_Storytelling_UX` gobierna el diseño de S7.** `UX_Guidelines.md` pasó a `superseded` |

Lo que queda abierto ya no son peticiones sino **coordinación**, y `DEC-024` es explícita en que nada
de esto detiene la construcción de nadie:

| Tema | Con quién | Qué necesitamos |
|---|---|---|
| Importar, no reteclear, los cortes | Equipo 5 · Equipo 4 | `LINEA_DE_ALERTA` vive en `src/api/repositorio_gold.py` y `RIESGO_ESTABLE` en `src/modelos/riesgo.py`, que es crítico de Estefany Hernández. El front necesita los dos. Si el `0.30` se teclea en el frontend, es `BUG-058` otra vez: un umbral hardcodeado en varios archivos sin dueño único |
| Estados del Asistente | Equipo 2 | Confirmar cuándo aterriza el streaming y los tres errores distinguibles, para diseñarlos y no improvisarlos (§4.bis) |
| Componentes y memoria técnica | Equipo 1 | Que `GET /api/v1/about/secciones` y `GET /api/v1/about/secciones/{id_seccion}` lleguen a `main`. Hoy viven en `dev/manuel-serrania` y sostienen toda la §5.bis |
| Aceptación | Equipo 6 | Ampliar los criterios de §9 con lo que QA necesite ejecutar sobre la candidata |

---

## 12. Relación con los documentos canónicos de UX

**`P-06` está resuelta.** `ADR-011` declara que el paquete `FARO_Storytelling_UX` gobierna el diseño
de S7, y `UX_Guidelines.md` pasó a `status: superseded`, `source_of_truth: false`,
`superseded_by: ADR-011`, con una nota que lo conserva como baseline histórico. Este frente **no
editó** ese archivo: lo hizo su owner.

| Documento existente | Estado hoy | Relación |
|---|---|---|
| [[vault/04_UX_Design/UX_Guidelines]] | `superseded` por `ADR-011` | Baseline histórico. `03_Visual_Identity.md` es el sistema de diseño de la nueva experiencia. Sus criterios de accesibilidad y `SIN_DATO` **siguen vigentes** |
| [[vault/04_UX_Design/Screen_Specs]] | `in_review`, owner Manuel Serranía | `01_UX_Architecture.md` define la nueva navegación. `Screen_Specs` conserva el catálogo de KPIs y el detalle de los 10 tableros |
| [[vault/04_UX_Design/Manual_Usuario_Dashboards]] | `approved`, owner Oscar Quiroz | **Sigue vigente.** `DEC-023` mantiene Superset como evidencia analítica y respaldo, así que su manual no es documentación histórica |
| [[vault/04_UX_Design/Accessibility]] | vigente | **Aplica sin excepción.** `ADR-011` §4 añade **WCAG 2.1 AA** como no negociable |
| `Cube_Specs_*`, `US221_KPIs_Base` | `approved` | Siguen vigentes: son contratos de datos, no de presentación |

---

## 13. Regla de colaboración y cumplimiento del vault

- Cada integrante trabaja en su rama fija `dev/{identidad}` y es dueño de su archivo.
- `vault/04_UX_Design/**` está en el verde de los cuatro y es ruta **crítica de Marina García**: el
  gate avisa y ella revisa.
- Cada documento lleva frontmatter con `id`, `owner`, `status` y trazas, y queda listado en
  [[vault/04_UX_Design/FARO_Storytelling_UX/_index]].
- Cada PR: título `[Nombre Apellido] - Descripción (US-621) - [sync|CI|DoF|DevLog]`, DevLog propio,
  fila en la matriz de trazabilidad y `vault_lint.py` en verde.
- Los `.md` se guardan en **UTF-8**.
- **Los cortes del nivel de atención se importan, no se retetean.** `LINEA_DE_ALERTA` y
  `RIESGO_ESTABLE` ya existen en el código y viven en capas distintas (§3.quater). Un `0.30` escrito
  a mano en el frontend repite exactamente el patrón de `BUG-058`.
- `DEC-024`: los seis frentes construyen y prueban en paralelo. Las únicas compuertas son rama
  personal, PR, CI, una aprobación humana y QA sobre la candidata.

---

## 14. Estado de aprobación

**Aprobado el 2026-09-10.** `DEC-023` acepta esta propuesta como la dirección UX/UI de S7 y
`ADR-011` la declara el paquete que gobierna el diseño. El PR #297 fue aprobado y mergeado por el PO.

Este plan es, desde esa fecha, el **contexto oficial de UX/UI** del proyecto y de los LLM del equipo.
Lo que siga contradiciéndolo en documentos anteriores queda superado por `ADR-011`.

### Criterio de cierre de `US-621`

`US-621` cierra cuando se cumplen las cuatro:

1. Los cuatro entregables de la §7 en su versión final, committeados y mergeados.
2. Los 7 mockups de escritorio en `mockups/`, con su `_index.md` (regla 4). **Sin PDF** — ver §7.ter.
3. **Handoff aceptado por el Equipo 5** (Diana Alvarez): la arquitectura, la especificación de
   visualizaciones y los mockups bastan para implementar sin redefinir decisiones de UX.
4. QA (`US-651`) ejecuta los criterios de la §9 sobre la candidata desplegada.

Los puntos 1 y 2 son de este frente. El 3 y el 4 dependen de E5 y E6, y `DEC-024` impide que se
usen como pretexto para detener la construcción de nadie.

### Gate de UX/UI — aprobación de los cuatro entregables

**2026-09-11 · Marina García del Buey, gate final de UX/UI (§7).**

Los cuatro entregables de la §7 quedan **aprobados** contra su versión mergeada a `main`. Cada uno
pasa a `status: approved` en su frontmatter.

| Entregable | Dueño | Aprobado contra |
|---|---|---|
| `00_Storytelling_Scope.md` | Marina García del Buey | ya `approved` desde el 2026-09-10 |
| `01_UX_Architecture.md` | Oscar Antonio Quiroz Lázaro | PR #319 |
| `02_Data_Visualization_Spec.md` | Monserrat Xcaret Miranda Olivas | PR #318 |
| `03_Visual_Identity.md` | Juan Carlos Macías Mayen | PR #316 |

**Qué se verificó antes de aprobar**, sobre la versión en `main` y no sobre la revisada en rama:

- **Guardarraíles de la historia:** "Watson" aparece sólo como prohibición en los cuatro documentos;
  cero ocurrencias de `prioritari*`; `SIN_DATO` y *nivel de atención* presentes donde corresponde.
- **Regla de `N`:** cero números tecleados en los siete mockups. Ninguno afirma un conteo como
  hallazgo.
- **Leyenda (§7.bis):** referenciada en las cinco pantallas con gráfica, no sólo en dos.
- **Higiene:** `vault_lint.py` limpio.

**Con esto se cumplen los puntos 1 y 2** del criterio de cierre. Quedan abiertos el 3 y el 4, que no
pertenecen a este frente.

> **Auditoría de contraste: ejecutada el 2026-09-11 desde el gate**, no diferida. Se midieron 14
> pares con la función WCAG 2.1 que ya vive en el repositorio (`contraste()` de Monserrat Miranda en
> `ejemplos_graficas/generar_ejemplos.py`). **11 pasan; dos fallan** y están documentados con número
> y arreglo en la §6 de `03_Visual_Identity.md`: el token `outline` usado como texto micro en 268
> lugares, y el texto blanco del botón *Beacon Action*. **Los dos arreglos son de Juan Macías** y no
> se aplicaron desde el gate: cambiar un token de color en siete mockups es decisión de sistema de
> diseño, no validación.
>
> `ADR-011` §4 hace WCAG 2.1 AA no negociable, así que **la aprobación de `03_Visual_Identity.md`
> queda condicionada a esos dos cambios.** Se aprueba el documento —el resto está completo y el
> Equipo 5 ya implementa con él— con los dos hallazgos medidos, nombrados y asignados, que es lo
> contrario de dejarlos como hueco.
>
> **Sigue abierto y no se cierra midiendo colores:** tamaño mínimo de texto y foco visible (Juan), y
> orden de tabulación (Oscar Quiroz — es interacción, no identidad). Los tres estaban marcados como
> *"no definidos"* en la §6.

### Adenda del 2026-09-11 · el contrato se movió después de aprobar

`ec1b43b` (Christian Imanol Ruiz, PR #332) entró a `main` **después** del gate de arriba y dejó tres
afirmaciones de este plan **factualmente falsas**, no discutibles: la §0 fila 5, la §10.ter y la
`P-01` decían que el contrato *no expone* `prioridad`. Hoy la expone.

No es una corrección cosmética. La §3 fija el guardarraíl *«lo que no está en la §10 no se dibuja»*, y
el Equipo 5 lee la §10 como el mapa de lo construible. Un mapa que afirma que un campo no existe,
frente a un contrato que lo entrega, se resuelve solo y a favor del que se leyó después. Se corrige en
las cuatro ubicaciones y se añade la **§10.quinquies**, que es donde ahora vive la regla de no
consumir `prioridad` y el número que la justifica.

**Lo que NO cambia:** ninguna pantalla, ningún criterio de la §9, ninguna decisión de diseño. El nivel
de atención se sigue derivando de `indice_riesgo`. Los cuatro entregables siguen aprobados y los
puntos 1 y 2 del criterio de cierre siguen cumplidos.

**Lo que queda escalado y no es de este frente:** `BUG-063` sigue `open` —el corte de `prioridad` por
encima del techo del fenómeno— y su efecto visible está en **DB-09 de Superset**, que `DEC-023`
conserva como evidencia analítica. Escalado al PO el 2026-09-11.

**Lo que entra al handoff con el Equipo 5:** la premisa con la que `02_Data_Visualization_Spec` §7.3
descartó el mapa dejó de sostenerse (§10.sexies). No se resuelve desde aquí.
