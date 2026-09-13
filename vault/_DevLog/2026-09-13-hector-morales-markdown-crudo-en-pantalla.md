---
project: "FARO"
date: "2026-09-13"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "45m"
touches: ["US-601", "REQ-002"]
tags: [devlog, us-601, api, frontend, equipo-1]
---

# DevLog — 2026-09-13 — Markdown crudo visible en pantalla (US-601)

→ [[vault/_DevLog/_index|Volver al índice]]

## El defecto

**El frontend no interpreta markdown en `advertencias` ni en celdas de tabla.**
`ComoFunciona.jsx` pinta `{a}` y `BloqueAbout.jsx` pinta `{celda}`: texto plano. Todo el `**` y
las comillas invertidas que escribí en esas cadenas **se veían literales en pantalla** — y las
cifras de ML son justo lo que va a leer el profesor.

Lo encontró Edgar Coronel. Escaneé las 6 secciones contra la API en vivo: **7 cadenas** afectadas
—2 celdas en Arquitectura, la advertencia y 4 celdas en Modelos de ML— más **2 advertencias
condicionales** de Capas que no aparecen en un escaneo sano porque sólo salen con la base caída.
Nueve en total.

**Por qué se me pasó:** escribí las cadenas de la API con el mismo estilo que los bloques
`markdown`, que sí pasan por un renderer (`MarkdownLite`). Nunca comprobé cuál de los tres caminos
de render usa cada campo.

## La prueba, y su complemento

`test_ninguna_advertencia_ni_celda_trae_markdown_crudo` recorre las 6 secciones y reprueba si
alguna advertencia o celda trae `**` o comillas invertidas.

Le añadí **el complemento que le faltaba**:
`test_los_bloques_markdown_si_pueden_traer_markdown`. Sin él, alguien podría hacer pasar la
primera "limpiando" también los bloques `markdown` —donde el formato **sí** es correcto— y la
sección perdería su tipografía sin que nada avisara. La prohibición es de dos campos, no general.

## El punto opcional: una rama que ya no se cubría

Edgar notó que `test_un_resultado_con_la_base_caida_no_se_cachea` **dejó de ejercitar** el
`if not resultado.base_no_disponible`: con el motor falso fallando también en el catálogo de
Bronze, `conteos_capas()` sale por su `return` temprano y nunca llega al `if`.

Agregado `test_una_caida_a_media_barrida_tampoco_se_cachea`: catálogo que responde y `COUNT(*)`
que falla con un `OperationalError` **sin** `pgcode` — caída, no timeout. Así el barrido sí se
construye y la rama se ejercita. Dejé anotado en la prueba vieja qué cubre y qué no, para que no
se confunda con la nueva.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Modificados:** `src/api/v1/about.py` (9 cadenas), `tests/test_api_contract.py`,
  `tests/test_repositorio_about.py`, `api/openapi.v1.json`
- **Decisiones autónomas del agente:** añadir el complemento que impide "limpiar de más" los
  bloques `markdown`.
- **Correcciones manuales:** ninguna. **El defecto lo encontró la revisión humana**; el escaneo
  programático sólo lo cuantificó después.
- **Prompt inicial:** nota de revisión de Edgar Coronel.

## Seguridad / calidad

- [x] `pytest tests/ -q` → **1307 passed, 10 skipped** (eran 1304; +3)
- [x] `ruff` limpio · verificado en vivo: **0 cadenas con markdown crudo** en las 6 secciones
- [x] Las dos guardas nuevas **falsificadas**: reintroducir un `**` en una celda reprueba la del
      contrato; cachear la caída a media barrida reprueba la nueva del repositorio

## Corrección de una atribución mía

En el DevLog anterior escribí que *«el hallazgo del SHAP fue de Imanol, no de Christian»*,
corrigiendo a Edgar. **Estaba equivocado: son la misma persona** — Christian Imanol Ruiz Hurtado
(`@ImanolRuiz00`), dueño de `src/api/**`. La corrección que hice era la que sobraba.

## Pendientes

- **Ficha de ML-01**: pedirle a Carlos Mayorga el PR con MAE 0.141458 y RMSE 0.436326.
- **Guarda de `--con-shap`**: va en el PR de `DEC-026`.
