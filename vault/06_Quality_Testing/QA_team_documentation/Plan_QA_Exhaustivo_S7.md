---
id: DOC-QA-EXHAUSTIVO-S7
title: "Plan de QA exhaustivo — regresión completa del sitio, S7"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["US-621", "REQ-004", "REQ-005", "vault/06_Quality_Testing/Test_Strategy", "vault/06_Quality_Testing/QA_team_documentation/Reporte_Auditoria_QA_UX"]
traces_down: ["vault/06_Quality_Testing/QA_Logs/_index", "vault/06_Quality_Testing/Bug_Register"]
tags: [qa, e2e, regresion, playwright, s7]
---

# Plan de QA exhaustivo — regresión completa del sitio (S7)

> Complementa, no reemplaza, `vault/06_Quality_Testing/QA_team_documentation/Reporte_Auditoria_QA_UX.md`
> (Edward Ruiz, pendiente de mergear a `main` desde `dev/edward-ruiz` al momento de escribir esto —
> conviértelo en wikilink cuando ya esté). Ese documento define el modelo de trabajo ("Owner Checks",
> matriz de perspectivas, criterios Go/No-Go). Este documento agrega lo que faltaba: la lista
> exhaustiva y verificable de qué probar pantalla por pantalla, botón por botón, y el estado real de
> la cobertura automatizada.
> → [[vault/06_Quality_Testing/_index]]

## Por qué existe

Ninguna prueba automatizada del frontend existe hoy en el repositorio: `frontend/package.json` no
declara ningún test runner (ni Playwright, ni Cypress, ni Vitest). La fila `E2E | <Playwright/Cypress>
| QA | CI (nightly)` de [[vault/06_Quality_Testing/Test_Strategy]] sigue siendo el placeholder original
del inicio del proyecto. Todo lo que el vault llama "Playwright" o "E2E" hasta hoy —incluido
[[vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo]]— es un recorrido **humano manual**,
asistido por navegador, no una suite de código que corra sola en CI.

**Con el freeze del domingo 20:00, no es realista construir una suite Playwright real desde cero.**
Este plan formaliza en su lugar un recorrido **manual pero exhaustivo por pantalla**, con evidencia,
que sí se puede ejecutar en el tiempo restante — y dejar la suite automatizada como tarea de la
siguiente entrega, no de esta.

## 1. Inventario completo de pantallas (`frontend/src/main.jsx`)

Verificado contra el router real, no de memoria. Nueve rutas:

| # | Ruta | Pantalla | Qué debe pasar | Botones/acciones a probar |
|---|---|---|---|---|
| 1 | `/` | Home | KPIs reales (`escuelas_en_riesgo`, matrícula), CTA a "Casos" | "Comenzar la investigación", nav completa |
| 2 | `/casos` | Los 7 Casos | 7 tarjetas con `indice_riesgo`, nivel de atención correcto (`>= cortes.alta`) | Cada "Abrir expediente →", "Comparar los 7 casos" |
| 3 | `/casos/:cct` | Expediente | 5 tabs: Resumen, Drivers, Comparación, Predicción, Recomendación | Cambiar cada tab, "Volver a casos" |
| 4 | `/vista-general` | Panorama | "El diferenciador" conectado al par oficial (`15DPR0920D`/`15DPR2254O`); resto con `DemoBadge` si es mock | Todos los enlaces internos |
| 5 | `/comparativa` | Comparativa | Estado "en construcción" con explicación del gap de contrato (`/series` no existe) | — |
| 6 | `/mapa` | Mapa | Estado "en construcción" con explicación (`latitud`/`longitud` sin nombre de municipio) | — |
| 7 | `/drivers` | Matriz de drivers | Estado "en construcción" con explicación (falta endpoint de lote) | — |
| 8 | `/comparacion-territorial` | Comparación territorial | Estado "en construcción" con explicación (falta nombre de municipio) | — |
| 9 | `/hallazgos` | Acerca de / Hallazgos | Distribución de driver dominante y 5 hallazgos, con datos reales | — |

**Regla de aceptación para las 4 rutas "en construcción" (5-8):** no es un defecto que digan
"contenido pendiente" — **sí sería un defecto** que rompieran, mostraran un error técnico crudo, o
mintieran diciendo que hay dato cuando no lo hay. Verificado el 12-sep: las 4 cumplen — muestran la
razón exacta del gap de contrato, no un error genérico.

## 2. Checklist transversal, para cada una de las 9 pantallas

- [ ] Carga sin excepción de JavaScript no controlada (consola del navegador, filtrar por "Uncaught").
- [ ] Ningún error 500/502 crudo visible en pantalla — solo mensajes en español, sin traza ni SQL.
- [ ] Todo `null`/ausencia de dato se lee como "SIN_DATO" o equivalente explícito, nunca como 0 o vacío
  silencioso.
- [ ] Todo botón/enlace visible navega o actúa — cero botones decorativos sin `onClick`/`href`.
- [ ] Con sesión anónima: `/api/v1/auth/me` en 401 no rompe la pantalla (es el estado esperado).
- [ ] Con sesión iniciada (cuando el login esté probado): el avatar y "Cerrar sesión" reemplazan al
  botón de login, sin placeholder "DA" ni iniciales falsas.
- [ ] Responsive: la pantalla no se rompe en viewport móvil (375×812) — usar `resize_window` antes de
  dar por buena una pantalla.
- [ ] Accesibilidad mínima: un solo landmark `banner` por composición visual coherente (verificar con
  `read_page`, no solo captura); foco visible al tabular.

## 3. Verificación E2E que sí se puede automatizar hoy, sin Playwright

El backend (`pytest`) ya cubre contrato, guardarraíles y modelos con **1241 pruebas verdes** (12-sep).
Eso no es lo que falta. Lo que falta es la capa de navegador. Mientras no exista una suite Playwright
real, el sustituto verificado y disponible en esta sesión es conducir un navegador real (Chromium)
contra el frontend local o desplegado, con captura de consola y red — exactamente el método que ya
usó el PO para `BUG-070` ([[vault/06_Quality_Testing/QA_Logs/2026-09-08-edgar-coronel-qa-sin-sesion-playwright]]).
Cualquier integrante de QA con acceso a esta sesión de Claude Code (o a Playwright real, si alguien lo
instala local) puede repetir el recorrido de la sección 1 y pegar evidencia (captura + errores de
consola) en un nuevo `QA_Logs/YYYY-MM-DD-<identidad>-qa-regresion-s7.md`, mismo formato que los
anteriores.

## 4. Verificación local de ML (independiente del frontend)

Requiere `docker compose up -d db mlflow api` y `.env` local (ver `guia-ambiente-local/VERIFICACION.md`).

- [ ] `http://localhost:5001` (MLflow) responde — si no, es el mismo bloqueo que documentó Deni
  Garrido para `DEC-027`; repórtalo, no lo asumas resuelto.
- [ ] `.venv/bin/python3 -m pytest tests/test_entrenar_ml03.py tests/test_ejecutar_cierre_ml03.py
  tests/test_publicar_gold.py tests/test_preflight_ml03.py -q` en verde.
- [ ] Buscar el experimento/run de ML-03 en la UI de MLflow (`http://localhost:5001`). Si la instancia
  local está vacía (sin runs), **no es un fallo de la prueba**: significa que el `run_id` de la
  evidencia histórica no vive en este entorno y hay que decidir si se re-entrena para generar uno
  nuevo y verificable, o si se recupera de otro entorno. Repórtalo como hallazgo, no lo dejes pasar
  en silencio.
- [ ] `curl http://localhost:8000/api/v1/health` y `/api/v1/version` — deben responder `200` con
  `cortes_atencion` presente.

## 5. Quién puede ejecutar cada parte, dado el reparto de S7

No se reasigna nada de lo ya decidido — esto es una guía de a quién pedirle ayuda si el equipo de QA
(3 personas) necesita contexto de un frente específico durante la ejecución del fin de semana:

| Bloque a probar | Dueño natural si algo falla | Por qué |
|---|---|---|
| Rutas 1-3, 9 (datos reales, nivel de atención) | Christian Ruiz / Diana Álvarez (Equipo 5) | Dueños de `frontend/**` y del contrato consumido |
| Rutas 5-8 ("en construcción") | Diana Álvarez (Equipo 5), con Marina García (Equipo 3) si es de UX | El gap declarado es de contrato de API, no de diseño |
| Verificación de ML local (§4) | Estefany Hernández / Héctor Morales (Equipo 4) | Dueños de `src/modelos/**` y de `DEC-027` |
| Login / sesión (cuando se pruebe) | Christian Ruiz (US-405, ADR-012) | Autor del flujo OAuth y del hallazgo de `faro_oauth_state` |
| Accesibilidad / contraste | Juan Macías, con Marina García como gate | Ya hicieron la auditoría WCAG de `03_Visual_Identity.md` |
| Refuerzo general de ejecución | Emilio Galnares, Edgar Jiménez, Eloisa González (Equipo 6, con Edward) | Es exactamente su frente esta S7 — QA integral |
| Escalación de cualquier hallazgo bloqueante | Edgar Coronel (PO) | Compuerta única, decide si bloquea el freeze |

## 6. Post-freeze (deuda declarada, no de esta entrega)

- Agregar `@playwright/test` como devDependency real de `frontend/`, con specs por ruta que repitan
  el inventario de la sección 1.
- Wirearlo a un workflow de CI propio, llenando por fin la fila `E2E` de `Test_Strategy.md`.
- Candidatos naturales para escribirlo: quien ya conoce el árbol de páginas (Christian Ruiz / Diana
  Álvarez) con revisión de QA (Edward Ruiz) sobre qué casos cubrir primero.

## 7. Hallazgos de la corrida del 12-sep (ambiente local del PO)

Ejecutado con Docker local, `main` sincronizado, 55 escuelas de fixture:

- ✅ **1241 pruebas de backend verdes, 0 fallos.** `test_entrenar_ml03.py`,
  `test_ejecutar_cierre_ml03.py`, `test_publicar_gold.py`, `test_preflight_ml03.py`: 66/66.
- ✅ **Cero excepciones de JavaScript no controladas** en las 9 rutas ni en las 5 pestañas del
  expediente.
- ✅ Las 4 rutas "en construcción" degradan exactamente como se documentó: explican el gap real, no
  fallan en silencio ni inventan dato.
- ⚠️ **MLflow local vacío** (sólo el experimento `Default`, sin runs): confirma que el `run_id` de
  `DEC-027` no es recuperable con un `docker compose up` estándar — coincide con lo que ya documentó
  Deni Garrido, ahora confirmado desde un segundo entorno.
- ⚠️ **Esquema de `gold.recomendaciones` desactualizado en el Postgres local del PO**: falta
  `shap_d1..shap_d6`, que `src/modelos/publicar_gold.py` sí declara. Produce `503` en
  `/api/v1/predicciones/{cct}` — **es una condición del entorno local, no un bug de código**;
  pendiente de confirmar contra el ambiente compartido/producción antes de registrar un `BUG-###`.
- ℹ️ El par oficial de demo (`15DPR0920D`/`15DPR2254O`) no existe en el fixture local de 55 escuelas
  usado en esta corrida — "El diferenciador" da 404 por eso, no por un defecto de `VistaGeneral.jsx`.
