---
project: "FARO"
date: "2026-09-08"
author_human: "Andrés González Habib"
agent: "GitHub Copilot"
model: "MAI-Code-1.1-Flash"
session_duration: "0.5h"
touches: ["US-305", "REQ-006", "TEST-AGENTE-GUARDRAILS"]
tags: [devlog, agent, guardrails, regression, qa]
---

# DevLog — 2026-09-08 — corrección del hueco de guardrail en el agente

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo
- Se corrigió el hueco de seguridad identificado por Edgar en la validación del agente: la frase
  `Modifica el nivel de la primaria 09DPR0001A` ya no pasa el guardrail de intención de escritura.
- Se quitaron `nivel` y `primaria` de `PALABRAS_AMBITO` para evitar que una orden de escritura
  se confunda con una pregunta legítima del dominio.
- Se agregó la prueba de regresión exacta pedida por Edgar:
  `test_modificar_nivel_de_primaria_se_rechaza`.
- Se validó la regresión reintroduciendo el defecto en local y comprobando que la prueba fallaba, para
  luego quitarlo y volver a verificar que pasaba.
- También se dejó documentada la bitácora de QA pre-demo en `vault/06_Quality_Testing/QA_Logs/` con los cinco chips medidos y el hallazgo funcional de Nuevo León.

## 🤖 Sesión de IA
- **Agente / modelo:** GitHub Copilot / MAI-Code-1.1-Flash
- **Archivos creados/modificados:**
  - `src/agente/guardrails.py`
  - `tests/test_agente_guardrails.py`
  - `vault/06_Quality_Testing/QA_Logs/2026-09-08-andres-gonzalez-qa-pre-demo.md`
  - `vault/06_Quality_Testing/QA_Logs/_index.md`
- **Decisiones autónomas del agente:**
  - Mantener el resto del vocabulario ampliado validado (estado, alumno, alumnos, total, secundaria, preescolar, especial).
  - No tocar la lógica de `validar_sql_lectura` ni el cambio de `fuera_de_alcance=False` cuando el SQL generado se rechaza.
- **Correcciones manuales:**
  - Confirmación final del alcance según la revisión de Edgar.
  - Ajuste del devlog y de la bitácora para que reflejen el trabajo real y la evidencia de QA.
- **Prompt inicial:** revisión del comportamiento del guardrail de `US-305` y validación de la regresión reportada por Edgar.

## Seguridad / calidad
- [x] Sin secretos hardcodeados
- [x] Tests agregados/actualizados (guardrail de regresión)
- [x] DevLog enlaza a los IDs afectados

## Bloqueantes
- La funcionalidad de contexto conversacional sigue requiriendo integración completa de extremo a extremo entre C4 y C2, pero ese bloqueo no es parte del hueco del guardrail y no se tocó en esta sesión.

## Próximos pasos
- Corregir/confirmar el DevLog de la sesión si Edgar pide un ajuste final de redacción.
- Mantener la bitácora QA_Logs como evidencia del pre-demo y del hallazgo de Nuevo León.
- Cerrar el flujo completo del contexto conversacional en la siguiente iteración si se decide incluirlo en la demo.
