---
id: DOC-FARO-UX-PLAN
title: "Plan de trabajo — UX/UI y storytelling FARO (Equipo 3, S7)"
owner: "Marina García del Buey"
status: approved
version: "1.2"
source_of_truth: true
traces_up: ["US-621", "REQ-002", "DEC-023", "ADR-011", "vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09", "vault/13_Reports/Revision_Profesor_2026-09-09"]
traces_down: ["vault/04_UX_Design/FARO_Storytelling_UX/00_Storytelling_Scope", "vault/04_UX_Design/FARO_Storytelling_UX/01_UX_Architecture", "vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec", "vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity"]
last_reviewed: "2026-09-10"
tags: [ux, storytelling, s7, us-621, celula-3, approved]
---

# Plan de trabajo — UX/UI y storytelling FARO

> Plan operativo del **Equipo 3 · UX/UI y storytelling** de S7. Implementa `US-621` (`REQ-002`).
> → [[vault/04_UX_Design/FARO_Storytelling_UX/_index]] ·
> [[vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09]] ·
> [[vault/13_Reports/Revision_Profesor_2026-09-09]]

**Estado:** aprobado por el PO el 10-sep mediante PR #297 y `DEC-023` (§14).
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
| 5 | `prioridad` obligatoria en Pantallas 4 y 5 | Condicionada a la petición **P-01** (§11) | El contrato v1 de la API no expone `prioridad` en ningún esquema, y el propio guardarraíl del plan prohíbe pedir endpoints nuevos. Además `BUG-063` sigue abierto |
| 6 | Etiqueta Alto / Medio / Bajo "conforme a la definición oficial disponible" | Condicionada a la petición **P-02** (§11) | No existe esa definición: hay `ANCLA_SIGMOIDE = 0.60` y `LINEA_DE_ALERTA = 0.50` (`DEC-019`), y una banda de atención 0.40–0.60 propuesta por C2 y nunca aprobada |
| 7 | "Watson" como nombre del chat | Condicionado a la petición **P-03** (§11) | El nombre no existe en ningún documento del repositorio; el chat es `POST /api/v1/agente/consulta` y su frente es el Equipo 2 |
| 8 | "Las gráficas deben construirse directamente en Front" | Condicionado a la petición **P-04** (§11) | Sustituye el embebido de Superset entregado en `US-206`. Es un cambio de arquitectura: pide ADR y lo ejecuta el Equipo 5, dueño de `src/frontend/**` |

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
  tramita como petición explícita en §11** — no se dibuja como si existiera;
- no se afirma causalidad;
- se usa lenguaje como **driver dominante**, **factor que destaca**, **principal línea de
  investigación** o **factor asociado**;
- donde no hay dato se marca `SIN_DATO` explícito: nunca cero, nunca nulo silencioso.

Los 6 drivers oficiales son: **D1** pobreza y rezago · **D2** inseguridad · **D3** infraestructura ·
**D4** conectividad · **D5** estrés hídrico · **D6** calidad del aire.

### 3.bis El número de escuelas en riesgo

`DEC-019` separó el ancla de la sigmoide (`0.60`, no se toca) de la línea de alerta (`0.50`), y con
`0.50` son **7 escuelas de 45 276**. Los modelos de dbt en `main` ya calculan con `>= 0.5`.

La rematerialización ya ocurrió: la QA de los nueve tableros del 2026-09-08 (Monserrat Miranda,
`TEST-PLAN-PRE-DEMO`) verificó **KPI-04 = 7 en DB-02 contra producción**, con 44 114 escuelas y
completitud de 62 %.

Lo que falta confirmar es la **otra superficie**: que `GET /api/v1/kpis` devuelva ese mismo 7, porque
es la que va a consumir Front y no la que se probó en esa QA. Es la petición **P-05** de §11. Hasta
que se confirme, los entregables escriben "N escuelas en riesgo" y no un literal.

---

## 4. El chat durante la experiencia

El chat está disponible durante toda la experiencia posterior al login como un botón flotante.

- Es un chat general: permite consultar datos en lenguaje natural.
- No necesita conocer automáticamente la pantalla ni la escuela que el usuario está viendo.
- **Su lógica funcional pertenece al Equipo 2** (`US-611`). Este frente define únicamente su
  presencia, comportamiento visual y coherencia con la identidad.
- El walkthrough inicial menciona brevemente que está disponible durante todo el recorrido.

El nombre **Watson** está propuesto y pendiente de la petición **P-03** (§11). Mientras no se
apruebe, los entregables lo llaman "el chat" y reservan el lugar del nombre.

---

## 5. Arquitectura de la experiencia

El entregable visual contempla **7 mockups**: un login y 6 pantallas.

### Mockup 0 — Login

**Objetivo:** homologar el acceso con la nueva identidad.
**Contiene:** nueva identidad y tratamiento del logo; los campos y acciones del login actual; recurso
visual alineado a la narrativa.
**No cambia:** autenticación, permisos ni lógica funcional.

### Pantalla 1 — Entrada

**Objetivo:** explicar qué es FARO y cuál será el propósito del usuario antes de revelar los casos.
**Contiene:** qué es FARO; objetivo del proyecto; imágenes que introducen la historia; explicación
breve del propósito del usuario; CTA principal; acceso a glosario; chat flotante; un único
walkthrough inicial, sencillo y breve.
**No revela todavía:** cuántas escuelas están en riesgo.

### Pantalla 2 — Panorama de las escuelas en riesgo

**Objetivo:** revelar los casos y presentar el panorama general.
**Contiene:** revelación clara del número de escuelas en riesgo; información general de matrícula —la
matrícula se muestra únicamente aquí dentro de la historia—; riesgo; filtros limitados; visualización
principal definida por Monserrat; CTA hacia la selección de caso; chat flotante.

Monserrat tiene libertad creativa sobre la visualización, dentro de los datos y endpoints existentes.

### Pantalla 3 — Selección de caso

**Objetivo:** que el usuario elija libremente una escuela.
**Contiene:** las escuelas identificables; índice de riesgo numérico; etiqueta de banda (sujeta a
**P-02**); CTA para abrir el caso.
El usuario **no necesita revisar todas**: puede investigar una sola y continuar.

### Pantalla 4 — Expediente de una escuela

**Objetivo:** entender qué driver destaca y cuál es la recomendación.
**Contiene:** nombre de la escuela; índice de riesgo numérico; etiqueta de banda (**P-02**); nota al
pie o tooltip que explique qué calcula el índice; gráfica comparativa de los 6 drivers; highlight
claro del driver dominante; recomendación correspondiente; prioridad (**P-01**); regreso a selección;
avance hacia la conclusión; chat flotante.
**No incluye:** evolución histórica de matrícula.
Por restricción de tiempo no se desarrolla explicabilidad adicional del modelo ni métricas nuevas
para justificar el driver dominante; se usa la contribución que ya entrega `/explicacion`.

### Pantalla 5 — Conclusión Top 3

**Objetivo:** cerrar la historia con el principal hallazgo.
**Muestra:** los 3 drivers dominantes más frecuentes entre las escuelas en riesgo; número o proporción
de escuelas en las que cada uno aparece como dominante; problemática sustentada únicamente en los
datos existentes; recomendación general asociada a cada driver; prioridad si aplica (**P-01**).

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
gráfica de 6 drivers, driver dominante, recomendación, prioridad); chat flotante; acceso al glosario.

---

## 6. Glosario

Accesible para usuarios no técnicos. Como mínimo explica en lenguaje sencillo: índice de riesgo ·
driver · driver dominante · recomendación · prioridad · `SIN_DATO`.

---

## 7. División de trabajo

> **Marina decide qué historia contamos. Oscar decide cómo se recorre. Monserrat decide qué datos y
> gráficas la demuestran. Juan decide cómo se ve.**

| Persona | Responsabilidad | Archivo propio |
|---|---|---|
| **Marina García del Buey** — líder | Definir la historia oficial; objetivo, alcance y guardarraíles; criterios de aceptación; coherencia transversal; **gate final de UX/UI** | `00_Storytelling_Scope.md` |
| **Oscar Antonio Quiroz Lázaro** — UX / navegación | Flujo de las 7 pantallas; objetivo, contenido, botones y conexiones; walkthrough y navegación; comportamiento UX del chat; 2–3 nombres para la exploración posterior. Su documento es guía directa para el Equipo 5 | `01_UX_Architecture.md` |
| **Monserrat Xcaret Miranda Olivas** — narrativa analítica | Qué dato responde cada pregunta; gráficas de cada pantalla; sólo datos Gold expuestos por endpoints actuales; ejemplos de visualizaciones; cómo se obtiene y comunica el Top 3 | `02_Data_Visualization_Spec.md` |
| **Juan Carlos Macías Mayen** — UI / identidad visual | Identidad visual desde cero: logo, paleta, tipografías, componentes, botones, cards, iconografía, imágenes, efectos, apariencia del chat, mockups y PDF final. Único editor del PDF | `03_Visual_Identity.md` |

Monserrat entrega a Juan los ejemplos de gráficas y el contenido analítico aprobado.
Ningún integrante modifica el entregable de otro sin coordinación previa.

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

- Marina: `00_Storytelling_Scope.md` final.
- Oscar: `01_UX_Architecture.md` final.
- Monserrat: `02_Data_Visualization_Spec.md` final + ejemplos finales de visualizaciones.
- Juan: `03_Visual_Identity.md` final, 7 mockups de escritorio y `FARO_UX_UI_Guide.pdf`.

```text
mockups/
├── 00_Login.png
├── 01_Entrada.png
├── 02_Panorama_Escuelas_Riesgo.png
├── 03_Seleccion_Caso.png
├── 04_Expediente_Escuela.png
├── 05_Conclusion_Top3.png
└── 06_Explorador.png
```

Escritorio es obligatorio. Móvil queda como evolución futura.

### Sábado 12 a lunes 14 — acompañamiento

El frente no cierra el viernes: acompaña al Equipo 5 durante la integración, responde dudas de
implementación y valida el recorrido en la candidata. *Code freeze* domingo 13 a las 20:00; entrega
el lunes 14 a primera hora.

---

## 9. Criterios de aceptación propuestos

Definidos inicialmente por este frente. El Equipo 6 (QA, `US-651`) puede ampliarlos.

1. Una persona que no conoce FARO entiende desde la entrada qué busca el proyecto y qué debe hacer.
2. La Pantalla 2 revela de forma inequívoca cuántas escuelas están en riesgo.
3. El usuario puede seleccionar cualquiera de ellas sin tener que revisar las demás.
4. El índice de riesgo se muestra con valor numérico y, si se aprueba **P-02**, con su banda.
5. El significado del índice de riesgo se explica en lenguaje sencillo.
6. El expediente muestra simultáneamente los 6 drivers.
7. El driver dominante queda visualmente destacado.
8. La recomendación proviene de datos existentes; la prioridad sólo aparece si se aprueba **P-01**.
9. Ningún texto afirma causalidad que los datos no puedan demostrar.
10. La conclusión muestra los 3 drivers dominantes más frecuentes sobre el conjunto completo.
11. La Pantalla 5 lo indica explícitamente.
12. La problemática presentada está sustentada únicamente por los datos disponibles.
13. La Pantalla 5 tiene un solo CTA principal.
14. El chat permanece visible como componente flotante tras el login.
15. Existe un único walkthrough sencillo al inicio.
16. Existe un único pop-up sencillo al entrar por primera vez a la exploración.
17. El glosario explica los términos mínimos acordados.
18. Toda visualización propuesta puede construirse con endpoints existentes o con una petición
    aprobada de §11.
19. Ninguna gráfica requiere un endpoint no acordado.
20. Los 7 mockups comparten una identidad visual consistente.
21. La arquitectura indica objetivo, contenido, botones y conexión de cada pantalla.
22. El Equipo 5 puede implementar con arquitectura + especificación + mockups sin redefinir UX.
23. Escritorio queda completamente resuelto.
24. La identidad propuesta no depende de la identidad visual anterior de FARO.

---

## 10. Mapeo verificado contra la API v1

Verificado contra `api/openapi.v1.json` el 2026-09-10. Este mapeo es el que hace exigible el
guardarraíl de §3: lo que no está aquí, no se dibuja.

| Necesidad | Endpoint | Campos |
|---|---|---|
| Las escuelas en riesgo, ordenadas | `GET /api/v1/escuelas` con `order_by=indice_riesgo` y `order=desc` | `cct`, `nombre`, `nivel`, `matricula_total`, `indice_riesgo`, `driver_dominante`, `tiene_prediccion` |
| Los 6 drivers de una escuela | `GET /api/v1/escuelas/{cct}` | `d1`…`d6`, `indice_completitud_drivers`, `es_estimado_por_grupo`, `sostenimiento`, `latitud`, `longitud` |
| Recomendación y driver dominante | `GET /api/v1/predicciones/{cct}` | `indice_riesgo`, `driver_dominante`, `recomendacion`, `cluster` |
| Evidencia del driver dominante | `GET /api/v1/predicciones/{cct}/explicacion` | `contribuciones` (SHAP), `driver_dominante` |
| Panorama y matrícula | `GET /api/v1/kpis` | `matricula_total`, `variacion_matricula`, `escuelas_en_riesgo`, `indice_completitud_drivers` |
| Filtros de la exploración | parámetros de `/escuelas` y `/kpis` | `ciclo`, `cve_ent`, `cve_mun`, `nivel` |
| Chat | `POST /api/v1/agente/consulta` | frente del Equipo 2 |

**Lo que no existe hoy:** `prioridad` no aparece en `EscuelaOut`, `EscuelaDetalleOut`, `PrediccionOut`
ni `ExplicacionSHAPOut`. Es la razón de la petición **P-01**.

---

## 11. Peticiones y decisiones

P-04 y P-06 fueron resueltas por el PO tras aprobar el PR #297. Las demás no impiden diseñar, pero
sí condicionan qué datos o etiquetas pueden llegar a la candidata.

| # | Petición | A quién | Qué bloquea si no se resuelve |
|---|---|---|---|
| **P-01** | Exponer `prioridad` en el contrato de la API, y decidir el corte de `BUG-063` (hoy `ALTA` usa `0.60` y el máximo real es `0.5717`, así que ninguna de las 45 276 escuelas la alcanza) | Equipo 5 (Diana Alvarez / Christian Ruiz) para el contrato · Equipo 4 y PO para el corte | Se cae "prioridad" de las Pantallas 4 y 5 y del criterio 8 |
| **P-02** | Definición oficial de las bandas Alto / Medio / Bajo, como `DEC-###` | PO | Las Pantallas 3 y 4 muestran sólo el valor numérico, sin etiqueta |
| **P-03** | Rebautizar el chat como **Watson** en producto y documentación | Equipo 2 (Andrés González) + PO | Los entregables lo llaman "el chat" |
| **P-04** | ~~ADR que retire el embebido de Superset de la experiencia y adopte gráficas nativas en Front~~ | **Resuelta: `ADR-011`** | Front puede implementar §5; Superset queda como superficie secundaria |
| **P-05** | Confirmar que `GET /api/v1/kpis` devuelve el mismo `escuelas_en_riesgo = 7` que ya se verificó en DB-02 el 2026-09-08. Los tableros están confirmados; la API, que es lo que consume Front, no | Equipo 5 (Luis Téllez / Christian Ruiz) | Los mockups no pueden fijar el número |
| **P-06** | ~~Ratificar que este plan y sus 4 documentos son el contexto oficial de UX/UI~~ | **Resuelta: `DEC-023`** | Este plan gobierna S7; §12 registra la convivencia documental |

---

## 12. Relación con los documentos canónicos de UX

La regla 1 del vault prohíbe duplicar. El PO aprobó la nueva jerarquía en `DEC-023` y `ADR-011`:

> **P-06 está resuelta.** Este plan manda para S7; los cuatro entregables se desarrollan con libertad
> completa dentro de PRD, datos, seguridad, accesibilidad y QA. La identidad se rediseña desde cero,
> las pantallas son nuevas y las visualizaciones no están obligadas a conservar Superset. Los
> documentos anteriores permanecen como baseline histórico o contrato de datos, según esta tabla.

| Documento existente | Estado | Relación propuesta |
|---|---|---|
| [[vault/04_UX_Design/UX_Guidelines]] | `superseded`, baseline histórico | `03_Visual_Identity.md` lo sustituirá como sistema visual cuando su contenido pase el gate de Marina |
| [[vault/04_UX_Design/Screen_Specs]] | `in_review`, owner Manuel Serranía | `01_UX_Architecture.md` cubre la nueva navegación. `Screen_Specs` conserva el catálogo de KPIs y el detalle de los 10 tableros |
| [[vault/04_UX_Design/Manual_Usuario_Dashboards]] | `approved`, owner Oscar Quiroz | Evidencia y manual histórico de Superset; no gobierna la experiencia principal de S7 |
| [[vault/04_UX_Design/Accessibility]] | owner Edgar Coronel | **Sigue vigente y aplica**. La nueva identidad debe cumplirlo, no reemplazarlo |
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

---

## 14. Aprobación y condición de promoción

**Aprobado por Edgar Edmundo Coronel Navarrete, PO, el 10-sep-2026 en el PR #297.** `DEC-023`
resuelve P-06 y `ADR-011` resuelve P-04: este plan es utilizable como contexto oficial del equipo.

Los documentos `00`–`03` conservan su estado propio (`draft`/`in_review`) hasta completar contenido,
revisión de Marina y aceptación de QA. Aprobar el plan no declara terminadas las pantallas ni permite
inventar datos que no existan en los contratos.
