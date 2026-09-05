---
id: DOC-GUION-DEMO
title: "Guion de la demo en vivo — 9 de septiembre"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["US-006", "REQ-007", "vault/01_Product/PRD_General_Materia"]
traces_down: ["vault/12_Roadmap_Sprints/Execution_Status"]
last_reviewed: "2026-09-05"
tags: [demo, pitch, guion, contingencia, us-006]
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
| 0–1 | **El problema** | Edgar Coronel | Sin pantalla. La escuela como sensor del territorio y las dos preguntas del proyecto | — |
| 1–3 | **El dato es real** | Diana Alvarez | Las 8 fuentes; Bronze→Silver→Gold; cobertura por driver y `SIN_DATO` explícito | `/api/v1/kpis` responde y `indice_completitud_drivers` ≈ 0.62 |
| 3–5 | **El diferenciador** | Marina García | Ficha de escuela → driver dominante → recomendación. **El par**: mismo riesgo, distinta recomendación | El par elegido responde en producción **ese día** |
| 5–7 | **El modelo** | Andrés González / Héctor Morales | Cómo se predice, partición temporal, y por qué `escuelas_en_riesgo` = 0 es un resultado, no una falla | Cifras del rerun a la vista |
| 7–8 | **La plataforma** | Luis Téllez | Cloud Run, las dos URLs vivas, SSO con Google, RBAC 200/403 | Las dos URLs responden y el login entra |
| 8–9 | **Cómo trabajamos** | Christian Ruiz | PRs, gate de propiedad, DevLogs, registros de bugs y decisiones | `vault_lint` y CI en verde |
| 9–10 | **Cierre y preguntas** | Edgar Coronel | Qué falta, qué se cortó y por qué | — |

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
- [ ] Los 10 tableros cargan con datos
- [ ] Ambiente local levantado y verificado como respaldo
- [ ] Video de respaldo accesible sin internet

## Qué falta de este documento

El **ensayo** en sí. Este guion es la mitad de `US-006`; la otra mitad es correrlo completo, con
cronómetro y con las pantallas reales, **antes del 9**. Un guion sin ensayar no cumple la historia:
el objetivo escrito en el plan de sprint dice *"preparar **y ensayar**"*.

**Fecha comprometida del ensayo: lunes 7 de septiembre.** Si el ensayo descubre que un bloque no se
sostiene, se corta ese bloque y se redistribuye el minuto — no se presenta a ver qué pasa.
