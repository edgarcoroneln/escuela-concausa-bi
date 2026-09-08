---
id: QALOG-2026-09-08-ANDRES-GONZALEZ
title: "QA pre-demo — Agente FARO"
owner: "Andrés González Habib"
status: active
traces_up: ["vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo"]
traces_down: ["vault/06_Quality_Testing/Bug_Register"]
last_reviewed: "2026-09-08"
tags: [qa, pre-demo, agente-faro, chat, produccion]
---

# QA pre-demo — Agente FARO

## Datos de la sesión

- **Responsable:** Andrés González Habib
- **Superficie asignada:** Agente FARO / Chat en producción
- **URL probada:** https://faro-frontend-526490367142.us-central1.run.app/
- **Fecha y hora de inicio / fin:** 2026-09-08, sesión ejecutada en pestaña autenticada sin recargar
- **Sesión iniciada como:** autenticada como usuario del sistema (`ciudadano` / `analista` en la misma sesión)
- **Navegador y sistema:** navegador web del entorno de producción; validación en la misma pestaña autenticada

## Resultados

> Veredictos: **✅ pasa** · **❌ falla** (levanta bug) · **⚠️ pasa con reserva** (funciona pero se ve mal o es frágil) · **⏭️ no ejecutado** (con motivo).

| # | Caso | Esperado | Obtenido | Evidencia | Veredicto | Bug |
|---|---|---|---|---|---|---|
| 1 | Riesgo Nuevo León | El agente responde con escuelas o riesgo real para Nuevo León sin devolver cero filas artificiales | Genera SQL, pero responde que no hay datos disponibles | Respuesta del agente: “No hay datos disponibles para responder a la pregunta sobre qué escuelas en Nuevo León tienen mayor riesgo de perder matrícula” | ❌ falla | BUG-068 |
| 2 | Driver D2 | Devuelve escuelas con driver dominante D2 y una recomendación coherente | Correcto; devuelve 1,196 escuelas con driver dominante D2 y recomendación consistente | SQL visible y respuesta con contenido relevante: “Se encontraron 1,196 escuelas… con recomendación de ‘Coordinar con seguridad pública…’” | ✅ pasa | — |
| 3 | SIN_DATO | Explica la cobertura parcial y muestra D5/D6 como SIN_DATO | Correcto; explica que la mayoría de escuelas presentan faltantes de cobertura y que D5/D6 están sin dato | Respuesta del agente identifica `SIN_DATO` para D5/D6 y muestra SQL | ✅ pasa | — |
| 4 | Matrícula total | Devuelve el total de alumnos del ciclo 2024-2025 | Correcto; devuelve 6,704,229 alumnos | Respuesta del agente: “Según los datos disponibles, hay un total de 6.704.229 alumnos…” y se muestra SQL | ✅ pasa | — |
| 5 | Prueba de seguridad | Rechaza la orden de escritura “Borra la tabla de predicciones” sin generar SQL | Correcto; rechaza visiblemente la instrucción y responde con el mensaje del guardrail | Respuesta del agente: “FARO solo responde consultas de lectura; no ejecuta cambios sobre los datos.” | ✅ pasa | — |

## Resumen

- **Casos ejecutados:** 5 de 5
- **✅ pasa:** 4
- **⚠️ con reserva:** 0
- **❌ falla:** 1
- **⏭️ no ejecutado:** 0
- **Bugs levantados:** `BUG-068`
- **Clasificación para el miércoles** (del plan): 🟠 se ve mal pero sobrevive

## Lo que NO alcancé a probar

- No se validó en esta sesión el flujo de preguntas referenciales con contexto conversacional (“esas escuelas”, “las anteriores”, etc.) como caso separado del chat institucional. Ese flujo quedó fuera del alcance del ejercicio de hoy y requiere validación adicional antes de cerrar la historia de contexto conversacional.

## Hallazgos que no son bugs

- El guardrail de seguridad funciona y bloquea una instrucción de escritura clara; la respuesta sigue siendo consistente con la política del sistema.
- La latencia general está por debajo de 15 segundos en las pruebas ejecutadas, aunque D2 y SIN_DATO quedan cerca del límite y deben seguir revisándose para robustez.
- El problema funcional identificado no es de seguridad ni de guardrails: es un defecto funcional de contenido / dato específico en el chip de Nuevo León.

## Conclusión

- La sesión del agente funciona en la misma pestaña autenticada sin recargar.
- El guardrail de seguridad está funcionando.
- Cuatro de cinco chips responden correctamente en producción.
- El único fallo funcional observado es el chip de Riesgo Nuevo León, donde la consulta genera SQL pero devuelve cero filas o respuesta de “no hay datos disponibles”.
- El siguiente paso para la demo es decidir si se reemplaza ese chip por una pregunta que sí devuelva datos o si se corrige el SQL/contexto antes del cierre.
