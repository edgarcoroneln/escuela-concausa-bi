---
project: "FARO"
date: "2026-08-30"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "Sonnet 5"
session_duration: "larga — revisión completa de US contra calendario y plan de control de calidad"
touches: ["US-004", "PLAN-QA-S6", "PLAN-EXEC-STATUS", "BUG-020", "BUG-030", "ADR-007", "DS-07", "REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005", "REQ-006", "REQ-007"]
tags: [devlog, pm, qa, plan, sprint-6]
---

# DevLog — 2026-08-30 — Plan de control de calidad y cierre de desarrollo

→ [[_DevLog/_index|Volver al índice]] · [[06_Quality_Testing/Plan_Control_Calidad_S6]] ·
[[12_Roadmap_Sprints/Execution_Status]]

## El corte contra el calendario

39 cerradas, 20 en revisión, 8 en curso. Contra el calendario quedan **4 días** hasta el
congelamiento del miércoles 2-sep, y el dato que cambia la lectura no es el total abierto sino su
composición: **20 de las 28 abiertas ya tienen el código escrito.** Lo que les falta es una
verificación, una firma o una decisión — no más desarrollo.

Eso convierte el problema en uno de coordinación, no de capacidad. Y explica por qué el reporte al
equipo se organiza **por persona** y no por célula: el trabajo de esta semana es que cada quien
encuentre su nombre y cierre lo suyo.

## El 30 % se destraba con tres decisiones

- **ADR-007** detiene US-212, US-313, US-311 y US-104.
- **BUG-020** detiene US-411, US-412, US-403, US-305 y US-304a, y vale **1.0 punto de rúbrica**.
- **DS-07** no detiene ninguna formalmente, y por eso nadie la mira; pero sin D1 con dato real la
  recomendación prescriptiva pierde su driver de mayor peso.

## El plan de calidad, y por qué se asignó así

`06_Quality_Testing/Plan_Control_Calidad_S6.md`. Ocho módulos, cada uno probado por alguien de
**otra célula**.

El principio no es desconfianza: quien escribió el código recorre el camino feliz sin darse cuenta.
La evidencia de esta semana lo respalda — **los tres defectos más caros (BUG-017, BUG-026, BUG-028)
los encontró alguien ajeno al código, y ninguno producía error.** Se veían bien y estaban mal.

Los probadores se eligieron por rigor demostrado, no por disponibilidad:

- **Marina** en tableros, porque verifica corriendo en vez de leyendo.
- **Monserrat** en capa semántica, porque validó DB-05/DB-08 levantando el pipeline completo en vez
  del mock.
- **Héctor** en pipeline, porque entiende el contrato desde el lado del consumidor.
- **Diana** en modelos, porque produce el contrato que consumen y detecta de rebote.
- **Andrés** en API, porque sabe buscar el caso que atraviesa la validación.
- **Luis y Eloisa** en despliegue — dos personas porque es el único riesgo vivo, y Eloisa prueba
  desde fuera sin permisos de GCP, que es exactamente la posición del evaluador.

## Mi plan de pruebas

Recorrer la demo como la va a recorrer el profesor: **en frío, sin abrir el repositorio y sin
preguntarle nada a nadie.** Si necesito ayuda para completarlo, ese es el hallazgo.

El caso que importa es **PM-01.3**: comparar dos escuelas con el mismo riesgo y verificar que
reciben recomendaciones distintas. Todo lo demás es infraestructura; ese es el diferenciador del
proyecto. Si no se demuestra en vivo, no importa cuánto de lo demás funcione.

También incluí **PM-04**, que es la parte que suele faltar en los planes de cierre: escribir la
lista de limitaciones conocidas **antes** de la demo. Hoy son cuatro — D5 sin volumen ni
coordenadas, D1 sin descarga real, ML-03 bajo su umbral, y CEMABE con 13 años de antigüedad.

Una limitación explicada es rigor. La misma limitación descubierta en vivo es un error.

## Uso de IA

Claude Code cruzó `Execution_Status` con `User_Stories` para mapear las 28 abiertas a sus dueños,
midió la contribución real por PRs mergeados y DevLogs para fundamentar las asignaciones de QA, y
redactó el plan y el reporte. Revisé las asignaciones una por una antes de publicarlas, porque
nombrar a alguien como probador de un módulo ajeno es una decisión de equipo, no una salida
automática.

## Pendiente

- Publicar el reporte al equipo y confirmar que cada quien revisó su tarjeta.
- Las tres decisiones: ADR-007, BUG-020 y DS-07.
- Ejecutar el plan a partir del jueves 3-sep, no antes.
