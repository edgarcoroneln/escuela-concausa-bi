---
project: "FARO"
date: "2026-08-30"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "Sonnet 5"
session_duration: "media — corrección de BUG-025, alta de BLOCK-003 y regeneración de los planes"
touches: ["US-004", "US-304a", "US-305", "BUG-025", "BUG-031", "BLOCK-002", "BLOCK-003", "PLAN-QA-S6", "ADR-007", "REQ-006"]
tags: [devlog, pm, agente, bloqueos, plan]
---

# DevLog — 2026-08-30 — BUG-025 no estaba cerrado, y el LLM bloquea a tres células

→ [[_DevLog/_index|Volver al índice]] · [[06_Quality_Testing/Plan_Control_Calidad_S6]] ·
[[10_Risk_Governance/Blocker_Register]]

## Corregí un error mío: BUG-025 no estaba cerrado

Lo marqué `fixed` al ver el PR #142 mergeado. **No lo estaba.** Christian lo dijo con claridad en el
canal: el PR entrega el *seam* de inyección y los guardarraíles reales —el SQL destructivo sí se
rechaza, que no es poco—, pero la generación no existe. Faltan tres cosas en tres células.

Pasa a `parcial` con el desglose por dueño. **La lección es mía**: un PR mergeado no es un bug
cerrado, y di por bueno el estado sin verificar el comportamiento completo. Es exactamente lo que
Marina formuló mejor que yo esta semana — *«devuelve datos» no es «devuelve el dato correcto»*.

## BLOCK-003 · el bloqueo que no estaba nombrado

Andrés, Christian y Luis están **detenidos en el mismo punto**, y hasta hoy no había un ID que lo
dijera: no hay proveedor ni modelo de LLM acordado. Andrés no puede programar contra un cliente que
no existe, Luis no sabe qué dependencia ni qué secreto añadir, Christian no sabe qué formato
consumir.

Lo registré como `BLOCK-003` y **la decisión es mía**, no del equipo: llevaban horas debatiéndolo sin
que nadie tuviera la autoridad para cerrarlo.

### Sobre Ollama y Qwen, que es lo que se propuso

Alguien sugirió usar lo mismo que el profesor en clase. Vale nombrar el problema antes de elegirlo:
**Ollama es un runtime local.** Servirlo desde Cloud Run implica cargar el modelo dentro del
contenedor — en CPU, con `min-instances=0`, eso da arranques en frío de decenas de segundos y una
imagen de varios GB. Para una demo sobre URL pública es frágil justo donde no puede fallar.

Un cliente HTTP alojado es una llamada de red y una dependencia pequeña, y el secreto ya tiene dónde
vivir: Secret Manager, con el patrón que Luis dejó funcionando en la Fase 2.

**El costo no es el criterio y conviene decirlo**, porque la conversación derivó hacia precios: a
este volumen —decenas de consultas con prompts de esquema pequeños— cualquier proveedor alojado
cuesta centavos. Lo que decide es el riesgo de despliegue contra el reloj.

## Las tres correcciones de Andrés eran correctas

Las verifiqué una por una contra el repositorio antes de incorporarlas al plan:

1. **ChromaDB ya existe** en `docker-compose.yml` línea 275, con volumen `faro-chroma-data`. El plan
   original lo habría duplicado.
2. **`app.dependency_overrides` es para pruebas.** Usarlo como cableado de producción hace que el
   comportamiento dependa del orden de importación.
3. **Las deps ya están fijadas** en `requirements/celula-3.txt` con versión exacta
   (`chromadb==1.5.9`, `sentence-transformers==5.7.0`). Instalarlas sueltas en el Dockerfile con
   rangos abiertos rompe la reproducibilidad de la imagen.

Agregué un cuarto punto que nadie había mencionado: `sentence-transformers` arrastra el modelo de
embeddings, del orden de cientos de MB, y **engorda la imagen para todas las rutas, no sólo para el
agente**. Vale preguntarse si el agente debe compartir imagen con la API.

## BUG-031 y la petición de Marina a C1

La corrección de Marina va a medias por diseño: arregló lo suyo y escaló lo ajeno, que es lo
correcto. **DB-01, DB-02, DB-06 y DB-09 siguen mostrando −54.5 % donde el real es −0.19 %**, y las
dos aserciones de Manuel impiden corregirlo porque exigen el componente defectuoso como si fuera
requisito.

Su petición a Diana y Deni son cuatro líneas de dbt, y **el argumento de por qué van en el mismo PR
de la normalización de ADR-007 es el que hay que conservar**: C1 va a tocar `fact_escuela_ciclo.sql`
de todos modos, y cada `dbt run --full-refresh` es un momento de riesgo para los diez tableros.
Mejor uno que dos.

Y su nota a Deni merece quedar registrada: *«tu implementación no tiene nada malo; el defecto está en
§4.4 de mi contrato»*. Escribió el bug contra sí misma cuando lo fácil era dejarlo ambiguo.

## Los planes regenerados

`PLAN-QA-S6` ahora abre con **los cinco frentes que hay que cerrar antes del miércoles**, con dueño
por tarea. El cambio de enfoque importa: ninguno es «más desarrollo», todos son **dependencias entre
personas**.

Y dos casos de prueba nuevos salidos de BUG-031:

- **QA-01.5 se amplió de la forma a la clase.** Decía «ningún porcentaje duplicado por `*100`».
  Marina demostró que eso cubría la forma del error y no su clase — su métrica nunca tuvo `*100` y
  estaba mal por 287×. Ahora dice: ninguna métrica de porcentaje multiplica dos columnas de medida
  dentro de un agregado.
- **QA-01.7** contrasta KPI-02 contra el cálculo directo en Postgres.

## Uso de IA

Claude Code verificó las tres correcciones de Andrés contra el repositorio, comprobó que ChromaDB ya
existía en el compose y que las deps ya estaban fijadas, corrigió BUG-025 y regeneró el plan y el
reporte. Revisé el argumento sobre Ollama antes de publicarlo, porque una recomendación técnica que
descarta la opción del profesor necesita sostenerse sola.

## Pendiente

- **Decidir el LLM hoy** — BLOCK-003, bloquea tres células.
- Manuel: las dos aserciones y las tres expresiones de BUG-031.
- Diana/Deni: las cuatro líneas de dbt, en el PR del ADR.
- Héctor: fecha del reentrenamiento de ML-01.
