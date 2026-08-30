---
id: PLAN-QA-S6
title: "Plan de Control de Calidad — Semana 6 (post-desarrollo)"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
source_of_truth: true
traces_up:
  - "12_Roadmap_Sprints/Execution_Status"
  - "01_Product/PRD_General_Materia"
traces_down:
  - "06_Quality_Testing/Bug_Register"
  - "02_Requirements/Traceability_Matrix"
last_reviewed: "2026-08-29"
tags: [qa, testing, plan, sprint-6, rubrica]
---

# Plan de Control de Calidad — Semana 6

> **Se ejecuta cuando el desarrollo esté cerrado, no antes.** Probar sobre código que aún se mueve
> produce hallazgos que caducan el mismo día.
> → [[12_Roadmap_Sprints/Execution_Status]] · [[06_Quality_Testing/Bug_Register]]

## Calendario

| Fecha | Hito | Qué significa |
|---|---|---|
| **Miércoles 2-sep** | **Congelamiento de desarrollo** | Toda US en `done` con evidencia. No se abren PRs de funcionalidad nueva |
| Jueves 3 – viernes 5 sep | **Ejecución de este plan** | Solo correcciones de lo que el plan encuentre |
| **Domingo 6-sep** | **CODE FREEZE** | Ni una línea más |
| Lunes 7 – martes 8 sep | Ensayo de la demo | Guion, tiempos, plan B |
| **Miércoles 9-sep** | **Demo en vivo** | Evaluación |

**Quedan 3 días de desarrollo.** Después de eso, cualquier cosa sin cerrar entra a la demo como
deuda declarada, no como sorpresa.

> **Actualización del 30-ago tras la junta de liderazgo.** ADR-007 quedó ratificado en fracción
> (`DEC-012`), BUG-020 cerrado y verificado en vivo, el choque de DB-05 resuelto con la salida B
> (`DEC-013`) y DS-07 atacado por tres vías en paralelo (`DEC-014`, `BLOCK-002`). De nueve bugs
> abiertos quedan cuatro y ninguno es crítico.
>
> **El camino crítico cambió de dueño:** ya no es BUG-020 sino el **reentrenamiento de ML-01**
> (Héctor, R-4 del ADR). De él dependen US-311, US-313, US-212 y US-204.

## Principio de asignación: nadie prueba lo suyo

Cada módulo lo prueba alguien de **otra célula**. No es desconfianza: quien escribió el código conoce
el camino feliz y lo recorre sin darse cuenta. Los tres defectos más caros de esta semana
—BUG-017, BUG-026 y BUG-028— los encontró alguien ajeno al código, y ninguno producía error.

Los probadores se eligieron por evidencia de rigor demostrado, no por disponibilidad.

---

## Asignaciones

### QA-01 · Frontend BI y tableros · **2.5 pts de rúbrica**

**Probadora: Marina García del Buey** · Área evaluada: Célula 2

Marina ya demostró el estándar que quiero para todo el equipo: **verifica corriendo, no leyendo.**
Su revisión del PR #129 trajo conteos reales contra Postgres, MD5 del fixture regenerado y la
corrida completa de `dbt run`. Prueba los tableros que **no** construyó ella.

| # | Caso | Criterio de aceptación |
|---|---|---|
| QA-01.1 | Los 10 tableros cargan sobre Gold real, no mock | Cada uno muestra datos; ninguno vacío sin bandera |
| QA-01.2 | Filtros globales de AC-002.2 en los 10 | Ciclo, entidad y nivel aplican y se propagan |
| QA-01.3 | `SCOPE_ENTIDADES` respetado | Solo 09, 15, 19, 14; ninguna entidad fuera de alcance |
| QA-01.4 | `SIN_DATO` visible, nunca cero silencioso | D5 y D6 muestran su bandera de cobertura |
| QA-01.5 | Ningún porcentaje duplicado por `*100` | Contrastar 3 KPIs contra consulta SQL directa |
| QA-01.6 | DB-04 no marca 100 % de escuelas en riesgo | **ADR-007 ratificado en fracción (DEC-012)**: el umbral 0.6 sigue válido. Verificar contra predicciones **reentrenadas**, no contra el ADR firmado |

### QA-02 · Capa semántica y cubos

**Probadora: Monserrat Xcaret Miranda Olivas** · Área evaluada: Célula 2 (cruzada)

Monserrat validó DB-05 y DB-08 **levantando el pipeline dbt completo en vez del mock**, que es la
diferencia entre «los tests pasan» y «el tablero funciona». Le toca verificar el repunteo de US-205,
que cambió la convención de los 10 tableros.

| # | Caso | Criterio de aceptación |
|---|---|---|
| QA-02.1 | Ningún `.sql` de `superset/semantic/` lee `gold.fact_*` | `test_semantic_repunteo_cubos` en verde contra Gold real |
| QA-02.2 | Toda métrica usa columnas expuestas por su dataset | Cero referencias a columnas inexistentes |
| QA-02.3 | Sin doble conteo en DB-08 | `matricula_total` fuera del pivote por defecto |
| QA-02.4 | Los 6 drivers con nombre canónico corto | Contrastar contra `dbt/seeds/dim_driver.csv` |
| QA-02.5 | Ningún chart apunta a dataset o métrica no declarada | Sincronización completa sin abortar |

### QA-03 · Pipeline Bronze → Silver → Gold · **2.5 pts de rúbrica**

**Probador: Héctor Rafael Morales Marbán** · Área evaluada: Célula 1

Héctor entiende el contrato desde el lado del consumidor: encontró que `isna()` dejaba pasar
escuelas ausentes de la dimensión, y su guarda de escala detuvo una publicación saturada antes de
que llegara a los tableros. Prueba el pipeline que **consume**, no el que escribe.

| # | Caso | Criterio de aceptación |
|---|---|---|
| QA-03.1 | `dbt run --full-refresh` desde cero con fixtures | 22+ modelos OK; fallos solo los esperados y documentados |
| QA-03.2 | `dbt test` completo | 149/149 o justificación por cada excepción |
| QA-03.3 | Idempotencia de ingesta | Doble corrida no duplica filas |
| QA-03.4 | Metadatos en las 8 fuentes | `_ingested_at`, `_source`, `_source_url` presentes |
| QA-03.5 | Cobertura parcial explícita | Donde no hay dato hay `SIN_DATO`, nunca cero ni nulo |
| QA-03.6 | `features_escuela` con ≥3 ciclos y solape total | 60/60 CCT cruzan `dim_escuela` |

### QA-04 · Modelos ML y MLflow · **1.5 pts de rúbrica**

**Probadora: Diana Aracely Alvarez Varela** · Área evaluada: Célula 3

Diana produce el contrato que los modelos consumen y ya detectó de rebote lo que a otros se les
pasó: los 10 municipios de `dim_municipio`, el desfase de esquema de DS-06. Prueba los modelos que
**se alimentan** de su trabajo.

| # | Caso | Criterio de aceptación |
|---|---|---|
| QA-04.1 | Partición temporal, nunca aleatoria | `verificar_sin_fuga()` en cada ventana |
| QA-04.2 | Los 3 modelos registrados en MLflow | ML-01, ML-02, ML-03 con versión canónica |
| QA-04.3 | Cada modelo reporta su métrica (AC-003.2) | Reporte con las tres, sin «pendiente» |
| QA-04.4 | `indice_riesgo` en rango creíble | No saturado en ≈1.00. La guarda `verificar_escala_variacion()` **es control permanente** (R-4), no medida temporal: verificar que siga activa |
| QA-04.5 | Escuelas sin driver no reciben recomendación inventada | `SIN_DATO`, nunca un driver por defecto |
| QA-04.6 | Umbrales declarados vs alcanzados | Distingue «entrenado» de «supera su criterio» |

### QA-05 · Backend, API y autenticación · **1.5 pts de rúbrica**

**Probador: Andrés González Habib** · Área evaluada: Célula 4

Andrés construyó los guardarraíles del agente y sabe buscar el caso que atraviesa la validación
—encontró que `SELECT ... INTO` pasaba el filtro de solo lectura—. Prueba la API que él **consume**
desde el agente.

| # | Caso | Criterio de aceptación |
|---|---|---|
| QA-05.1 | Las 18 rutas del contrato responden | Ninguna 500 en la URL pública |
| QA-05.2 | Sin token → 401, nunca 500 | El fallo de auth se distingue del de datos |
| QA-05.3 | RBAC ciudadano vs analista | 403 donde corresponde, con `ANALISTA_EMAILS` definido |
| QA-05.4 | Errores sin filtrar detalle interno | Ningún stack trace ni nombre de tabla al cliente |
| QA-05.5 | Entradas validadas con Pydantic | CCT malformado → 422, no 500 |
| QA-05.6 | Los 3 modelos servidos por API | Predicción real, no `mock_data` |

### QA-06 · Despliegue, Docker y URL pública · **1.0 pt de rúbrica**

**Probadores: Luis Téllez Domínguez y Eloisa González Rubio** · Área evaluada: Célula 5

Único módulo con dos probadores, porque es el **único riesgo vivo de la demo**. Luis conoce la
infraestructura; Eloisa acaba de construir la guarda de regresión del entrypoint y prueba desde
fuera, sin permisos de GCP, que es exactamente la posición del evaluador.

| # | Caso | Criterio de aceptación |
|---|---|---|
| QA-06.1 | `smoke-test-bug020.sh` pasa las 4 etapas | Exit code 0. **Ya verificado el 30-ago tras la Fase 2**; reejecutar en frío el día del ensayo |
| QA-06.2 | `docker compose up -d` desde cero | Todos los servicios `healthy` |
| QA-06.3 | El contenedor arranca el contrato v1 | `test_docker_api_entrypoint` en verde |
| QA-06.4 | Cloud SQL sin IP pública | Solo alcanzable por el connector |
| QA-06.5 | Ningún secreto en logs ni en el repo | Barrido de `git log -p` y de Cloud Logging |
| QA-06.6 | La URL sobrevive un reinicio en frío | `min-instances=0` → primera petición responde |

### QA-07 · Agente conversacional · **0.5 pts de rúbrica**

**Probador: Carlos Guillermo Mayorga Tapia** · Área evaluada: Célula 3 (cruzada)

| # | Caso | Criterio de aceptación |
|---|---|---|
| QA-07.1 | Preguntas destructivas rechazadas | «Borra la tabla de predicciones» → fuera de alcance |
| QA-07.2 | El endpoint desplegado usa el RAG real | **BUG-025 cerrado en el PR #142**; verificar sobre la URL pública, no en local |
| QA-07.3 | Solo lectura garantizada | `SELECT INTO`, `COPY`, `CREATE` rechazados |
| QA-07.4 | Preguntas fuera de dominio | Responde que no aplica, no inventa |

### QA-08 · Gobernanza, trazabilidad y Git · **0.5 pts de rúbrica**

**Probador: Edgar Coronel (PM)** — ver sección propia abajo.

---

## Plan de pruebas del PM

Mi módulo de rúbrica es gobernanza, pero mi trabajo real en esta fase es otro: **recorrer la demo
como la va a recorrer el evaluador**, sin conocimiento previo y sin atajos.

### PM-01 · El recorrido del evaluador

Se ejecuta **una sola vez, en frío**, sin abrir el repositorio y sin preguntarle nada a nadie. Si
necesito ayuda de alguien para completarlo, ese es el hallazgo.

| # | Paso | Qué estoy midiendo |
|---|---|---|
| PM-01.1 | Abrir la URL pública sin contexto | ¿Se entiende qué es esto en 30 segundos? |
| PM-01.2 | Consultar una escuela concreta | ¿Devuelve predicción **y** driver dominante? |
| PM-01.3 | Comparar dos escuelas con el mismo riesgo | **¿Reciben recomendaciones distintas?** |
| PM-01.4 | Buscar un municipio sin datos de agua | ¿Dice `SIN_DATO` o miente con un cero? |
| PM-01.5 | Preguntarle al agente algo del proyecto | ¿Responde con datos reales? |
| PM-01.6 | Pedirle al agente algo destructivo | ¿Se niega? |

**PM-01.3 es la prueba que define el proyecto.** Todo lo demás es infraestructura; el diferenciador
es que dos escuelas con el mismo riesgo reciban recomendaciones distintas según su driver dominante.
Si eso no se puede demostrar en vivo, no importa cuánto de lo demás funcione.

### PM-02 · Verificación de la rúbrica módulo por módulo

Para cada uno de los 7 módulos: **abrir la evidencia que citaría ante el profesor** y comprobar que
existe, está en `main` y es verificable por un tercero.

| # | Módulo | Evidencia que debo poder mostrar |
|---|---|---|
| PM-02.1 | Data Engineering (2.5) | `dbt run` en vivo + 8 fuentes con metadatos |
| PM-02.2 | Frontend BI (2.5) | 10 tableros sobre Gold real, no mock |
| PM-02.3 | 3 modelos vía API (1.5) | Petición HTTP que devuelve predicción real |
| PM-02.4 | Backend y Auth (1.5) | 401 sin token, 403 por rol, 200 con token |
| PM-02.5 | GCP y URL pública (1.0) | La URL responde; sin esto el techo es 6.0 |
| PM-02.6 | Agente (0.5) | Conversación en vivo con guardarraíl |
| PM-02.7 | Equipo, Git y docs (0.5) | Vault limpio, trazabilidad completa, DevLogs |

### PM-03 · Integridad del vault

| # | Caso | Criterio |
|---|---|---|
| PM-03.1 | `vault_lint.py` limpio | Cero bloqueantes |
| PM-03.2 | Sin IDs duplicados ni huérfanos | Cada artefacto en su `_index.md` |
| PM-03.3 | Trazabilidad completa | Toda US con REQ, evidencia y DevLog |
| PM-03.4 | Bugs abiertos con dueño y severidad | Ninguno sin asignar |
| PM-03.5 | Todo archivo decodifica como UTF-8 | Barrido con `iconv` (V-01) |
| PM-03.6 | Cada persona con DevLogs propios | Participación demostrable e individual |

### PM-04 · Lo que voy a declarar como deuda

Cerrar el proyecto no es fingir que todo está completo: es **decidir qué queda fuera y decirlo
antes de que lo pregunten.** Al cierre del plan escribo una lista de limitaciones conocidas con su
justificación técnica, y la llevo a la demo. Hoy los candidatos son:

- **D5 (agua)** — el esquema del extractor no entrega volumen ni coordenadas (BUG-030).
- **D1 (pobreza)** — DS-07 sin descarga real (**BLOCK-002**). Si la vía 1 de DEC-014 no llega a
  tiempo, la vía 2 lo convierte en cobertura parcial declarada, que sí es defendible.
- **ML-03** — entrena con Silhouette 0.1086 contra un umbral de 0.3.
- **CEMABE 2013** — censo de hace 13 años; D3 y D4 se apoyan en él.

Una limitación explicada es rigor. La misma limitación descubierta en vivo es un error.

---

## Reglas de ejecución

1. **Todo hallazgo se registra como `BUG-###`**, aunque se arregle en el momento. Sin ID no existe.
2. **Se prueba sobre `main`, nunca sobre una rama.** Si no está mergeado, no se prueba.
3. **Un hallazgo sin pasos de reproducción no es un hallazgo**, es una impresión.
4. **Severidad la pone quien reporta; la prioridad la pone el PM.**
5. **Nadie cierra su propio hallazgo.** Lo cierra quien lo reportó, verificando.
6. **Si un caso no se puede ejecutar, eso es el resultado** y se registra igual.
