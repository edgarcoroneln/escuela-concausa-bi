---
id: DEVLOG-2026-09-11-EDGAR-CORONEL-REVISION-PRS-S7-GATE-JUEVES
title: "Revisión del gate de jueves 10: PRs de Estefany, Andrés, Christian y Diana"
owner: "Edgar Edmundo Coronel Navarrete"
status: active
traces_up: ["PLAN-RECUPERACION-2026-09-09", "US-654", "DEC-022"]
traces_down: ["US-631", "US-611", "US-305", "US-641", "ADR-012", "RISK-011"]
last_reviewed: "2026-09-11"
tags: [devlog, pr-review, sprint-7, recovery, compuerta-unica]
---

# Revisión del gate de jueves 10 — PRs de Estefany, Andrés, Christian y Diana

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

Revisión de compuerta única (`DEC-003`) sobre los cuatro PR abiertos al cierre del gate del
jueves 10: `#307` (Estefany, US-631), `#306` (Andrés, US-305/US-611), `#304` (Christian,
ADR-012/cookies) y `#302` (Diana, US-641/ADR-012). Verificación línea por línea contra el código de
cada rama (no solo el texto del PR), simulación de los merges secuenciales con `git merge-tree`
para fijar el orden y anticipar el conflicto conocido de `vault/_DevLog/_index.md` (GitHub no
aplica `merge=union` en la web; el merge local sí lo resuelve solo, como se confirmó al sincronizar
esta misma rama con `main` en esta sesión).

**`#307` (Estefany) — aprobado y mergeado.** Cifras verificadas contra
`ML03_Entrenamiento_US321.md`/`ML03_Evidencia_20260908.json`: `k=3`, Silhouette `0.4644549058`,
114,200 elegibles / 21,846 excluidas. El único cambio de código es un docstring, coherente con
`FEATURES_ML03`. Pendientes menores dejados para el siguiente PR de Estefany (no bloquearon):
DevLog con `status: done` pero *tests pendientes*, la explicación citada en la celda de *Test* de
la matriz en vez de `test_entrenar_ml03`, y el docstring sin remitir a `RISK-011`. Se le pidió a
Andrés (revisor técnico, no bloqueante) un dictamen sobre `RISK-011` con fecha: viernes 18:00.

**`#306` (Andrés) — solicité cambios, corrigió, aprobado y mergeado.** El código estaba bien: lee
las mismas llaves del contrato de Karla (`#301`, ya en `main`), retrocompatible, 4 pruebas nuevas.
Pero el PR declaraba "Fase 2 completa end-to-end" cuando **ningún cliente enviaba `historial`**
(ni el shell de Streamlit ni el React de Diana), no trazaba a `US-611` (su historia de equipo en
S7) y citaba `SEC-003` (rate limiting), que no aplica. Corrigió los tres puntos en `b1f5b15` y dejó
un aviso importante para el E2E: `redactar_respuesta_con_llm` solo hace `.strip()`, así que una
respuesta larga del agente puede violar las cotas de `HistorialTurnoIn` (sin caracteres de control,
máx. 500) si un cliente la reenvía tal cual — pendiente de definir con Karla/Diana quién normaliza.

**`#304` (Christian) — aprobado, pendiente de que resincronice.** Diseño de sesión por cookie
`httpOnly` sólido: `HttpOnly`/`SameSite=Lax`/sin `Domain`, refresco acotado a su ruta,
`Authorization` con precedencia sobre la cookie, logout borra las dos. La corrección que yo había
pedido en una vuelta anterior (que el modo cookie no filtrara el `TokenPair` en el JSON de
`/auth/refresh`) ya venía resuelta con 6 pruebas nuevas, incluida una que busca la forma `eyJ` en el
texto crudo. Encontré un hallazgo para el equipo de cara al viernes: `/auth/login` fija la cookie de
`state` anti-CSRF en el origen que responde, y Google vuelve a `GOOGLE_REDIRECT_URI` (origen de la
API) — si el React arranca el login por el proxy del frontend, esa cookie queda en el origen
equivocado y el callback da 401. En local no se nota porque las cookies no distinguen puerto. La
salida no toca la API: el botón de login debe navegar directo al origen de la API, y sólo el canje
(`?sesion=cookie`) pasa por el proxy. Quedó anotado en el mensaje a Christian y a Diana.

**`#302` (Diana) — solicité cambios.** Buen avance en la decisión de arquitectura (React+Vite+nginx
no-root, proxy same-origin, modo demo explícito con `DemoBadge`/`isDemoMode` en vez de fallback
silencioso — exactamente lo que pedí en mi revisión anterior de este PR). Pendientes antes de
mergear: 5 pantallas (3 en el menú) siguen pintando `mock.js` sin rotular, incluido el par
diferenciador del guion de demo con CCT reales congelados en código; el PoC completo de Angular
(22 archivos) y la página de comparación de stacks (evidencia de ADR-012, no producto) siguen en el
árbol y arrastran dependencias sin otro uso (`react-simple-maps`, `@observablehq/plot`); la CSP de
nginx bloquea Google Fonts; `.dockerignore` no excluye `frontend/.env*` ni `node_modules`; falta su
fila en la matriz; y `docker/**`/`vault/08_CICD_DevOps/**` son crítico de Luis Téllez (regla 7) —
pedí su aprobación explícita. Encontré además que ningún cliente React arranca el login todavía, y
con `AUTH_LECTURA_PUBLICA=false` (SEC-006) en producción eso deja todas las pantallas reales en 401
en la candidata — es la ruta crítica real del viernes, más que cualquier pendiente de este PR.

## Estado que actualiza este DevLog

- `Execution_Status.md`: `US-631` y `US-611` pasan de `planned` a `in_progress` con la evidencia de
  `#307` y `#306` (mergeados). `US-641` sigue `planned`: `#302` no mergeó.
- No se tocó `Traceability_Matrix.md` en esta sesión: cada autor actualiza su propia fila
  (`comunes` en `ownership.yml`); las correcciones pedidas ya viven en los mensajes de revisión de
  cada PR, no las apliqué yo por encima de su trabajo.

## Decisiones que quedan abiertas, con dueño y fecha

1. **`RISK-011`** (Andrés) — dictamen sobre si la completitud de drivers funciona como bandera
   indirecta de D6 en el cluster 2 de ML-03. Fecha: viernes 18:00 (gate diario).
2. **Ratificación de `ADR-012`** (yo) — pendiente hasta que `#302` se apruebe; hoy sigue
   `status: proposed`. Cuando se ratifique, falta reflejarlo en `superseded_by` de `ADR-002`.
3. **Login del frontend React** (Diana/Luis, con el hallazgo de Christian arriba) — sin esto la
   candidata no pasa el recorrido del profesor. No es parte de `#302` ni de `#304`; es trabajo
   nuevo para el viernes.
4. **Corte del viernes 18:00** — el DevLog de Christian propone reabrir `AUTH_LECTURA_PUBLICA=true`
   si el login no funciona para esa hora. No lo autoricé por adelantado: revertiría `SEC-006`
   (`resolved` desde el 2-sep) y el arreglo del login no toca la API. Se decide con evidencia en el
   gate, no antes.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5 (revisión) y claude-sonnet-5 (este DevLog).
- **Archivos creados/modificados:** este DevLog, su fila en `vault/_DevLog/_index.md`,
  `vault/12_Roadmap_Sprints/Execution_Status.md` (filas `US-631`, `US-611`).
- **Decisiones autónomas del agente:** ninguna acción GitHub-facing (aprobar/mergear/comentar) — se
  prepararon los mensajes de revisión y los comandos exactos para que el PO los ejecute él mismo.
  El PO ejecutó los `gh pr review`/`gh pr merge` de `#307` y `#306` fuera de esta sesión de
  generación de documento.
- **Correcciones manuales:** ninguna sobre este DevLog.

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] No aplica (sesión de revisión y documentación, sin código productivo)
- [x] DevLog enlaza a los IDs afectados

## Bloqueantes

- Ninguno para el gate del jueves. `#302` queda bloqueado por sus propios pendientes y por la
  aprobación de Luis Téllez (regla 7).

## Próximos pasos

- Revisar `#302` cuando Diana suba los cambios pedidos y Luis apruebe.
- Revisar `#309` (Alejandro Velázquez, runbooks de observabilidad), abierto tras este gate y aún
  sin revisar.
- Dar seguimiento al dictamen de `RISK-011` y a la ratificación de `ADR-012` en el gate de mañana.

→ [[vault/_DevLog/_index|Volver al índice]]
