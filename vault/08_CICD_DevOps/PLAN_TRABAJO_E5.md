---
id: DOC-E5-PLAN-TRABAJO
title: "Plan de trabajo — Frontend y despliegue (Equipo 5, S7)"
owner: "Diana Álvarez (líder E5)"
status: draft
version: "1.0"
traces_up: ["US-641", "REQ-005", "vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09"]
traces_down: ["vault/08_CICD_DevOps/Arquitectura_Frontend_React", "vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo"]
last_reviewed: "2026-09-10"
tags: [frontend, deploy, s7, us-641, equipo-5, plan]
---

# Plan de trabajo — Frontend y despliegue (Equipo 5)

> Plan operativo de **Equipo 5 · Frontend y despliegue** de S7 (`US-641`, `REQ-005`).
> → [[vault/08_CICD_DevOps/Arquitectura_Frontend_React]] ·
> [[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo]] ·
> [[vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09]]

**Líder:** Diana Aracely Alvarez Varela. **Equipo:** Luis Téllez Domínguez, Christian Imanol Ruiz
Hurtado. **Entrega a:** Equipo 6 (QA). **Recibe de:** Equipo 1 (componentes/datos), Equipo 2 (chat),
Equipo 3 (storytelling/UX), Equipo 4 (ML-03).

---

## 0. Corrección de calendario

Esta sesión veníamos trabajando bajo el supuesto de "producción el sábado en la mañana". El
`Plan_Recuperacion_2026-09-09` (canónico, `source_of_truth`, firmado por el PO) fija otra cosa:

| Fecha | Hito real |
|---|---|
| Vie 11 | Primera integración E1→E3→E5, chat y ML-03 consumibles |
| **Sáb 12, temprano** | Candidata **completa y funcional** en entorno de prueba — no solo "integrada a medias": todo el recorrido debe poder probarse de principio a fin. Es el corte real de Equipo 5, aunque no sea el corte formal del proyecto |
| Sáb 12 → Dom 13 | Ventana de margen: QA (E6) y cada dueño de frente prueban sobre la candidata del sábado y corrigen lo que encuentren, antes de que deje de poder tocarse |
| **Dom 13, 20:00** | *Code freeze* de la candidata aprobada, decisión go/no-go |
| **Lun 14, primera hora** | Entrega y cierre en producción |

Se corrige el plan interno a este calendario, con una precisión importante: que el *code freeze*
formal sea el domingo no mueve nuestro corte real. **El sábado temprano la candidata tiene que estar
completa y funcional**, no parcialmente integrada — es lo que le da a QA (E6) y a cada dueño de frente
el sábado y el domingo antes de las 20:00 para probar y corregir. Tratar el sábado como "a medias"
y el domingo como el día para terminar de construir deja cero margen real para que otros reaccionen;
el margen es el punto de tener dos días de colchón antes del freeze, y solo existe si el sábado
temprano ya funciona de principio a fin.

---

## 1. Objetivo

`US-641`: frontend integrado (storytelling de UX, chat, tres modelos) y candidata desplegada, con
release identificable y rollback probado. Es el frente que **recibe** de los otros cuatro e
**integra** — no construye contenido de cero, ensambla lo que entregan E1-E4 sobre la base ya
construida hoy (stack, componentes, arquitectura, ADR).

---

## 2. Decisiones ya tomadas (no se reabren sin evidencia nueva)

### 2.1 Stack

Combo #1: **React 18 + Vite + Recharts + D3 dirigido** (gauge de riesgo, mapa). Probado en código
real contra otras 4 combinaciones — [[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo|ADR-012]]
(`supersedes: ADR-002`), pendiente de ratificación del PO.

### 2.2 Auth — cerrada 10-sep (Luis + Christian, gate E5)

**Cookie `httpOnly` de un solo origen, no Bearer-en-navegador, no BFF.** Se revisó la propuesta
original (Bearer tras canjear `ADR-010`) y se descartó: bajaba CIS v8 Control 16 de ~9 a ~7 por
exponer el token a JS. Diseño final:

1. `nginx` del frontend hace `proxy_pass` de `/api/*` a la API — un solo origen para el navegador.
2. `POST /auth/exchange` responde `Set-Cookie` sin `Domain` → cookie host-only (no choca con
   `BUG-059`, que era cookie compartida entre subdominios).
3. `deps.py` (Christian) gana fallback: sin `Authorization`, lee la cookie. Bearer sigue vivo para
   clientes no-navegador.
4. El frontend **no maneja tokens** — ni los guarda ni los adjunta. Solo `credentials: "same-origin"`.

Costo: ~1h de Christian (API) + el `proxy_pass` que Luis ya iba a escribir. Riesgo residual: CSRF,
mitigado con `SameSite=Lax` (cubre los POST del sistema), documentado en `Threat_Model` por Christian
como residual, no resuelto. Detalle completo:
[[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo|ADR-012]].

**Ya no aplica `FRONTEND_REDIRECT_URIS`/CORS como bloqueante** — con un solo origen vía proxy, el
navegador nunca cruza orígenes. Lo que sí queda pendiente, repartido:
- Luis: `proxy_pass /api/*` + headers `CSP`/`X-Frame-Options` en `docker/nginx-frontend.conf.template`.
- Christian: `Set-Cookie` en `/auth/exchange` y `/refresh`, fallback en `deps.py`, headers
  `HSTS`/`X-Content-Type-Options`/`Referrer-Policy` en la API.
- Diana: rehacer `docker/frontend-react.Dockerfile` para correr non-root (pedido de Christian en la
  revisión de seguridad) y cambiar `credentials: "include"` → `"same-origin"` en `frontend/src/lib/api.js`
  una vez que el `proxy_pass` de Luis esté activo.

### 2.3 Deploy

Mismo patrón que `faro-api` (Luis): mismo `PROJECT_ID`/`REGION`/Artifact Registry (`faro-images`),
scripts ya escritos (`build-and-push-frontend.sh`, `deploy-cloud-run-frontend.sh`). Sin Secret Manager
ni VPC connector — estático, 256Mi/1 CPU.

---

## 3. Qué recibimos de cada frente, y cuándo

Orden de integración fijado por el PO: **E1 → E3 → E5**, **E4 → E5**, **E2 → E5**, **E6 prueba
continuamente**.

| De | Qué | Cuándo (según su propio plan) | Qué hacemos con eso |
|---|---|---|---|
| E1 (Héctor) | Documentación de componentes, datos, capas Bronze/Silver/Gold, cubos, ER | Gate hoy 18:00 | Insumo para la narrativa de "cómo funciona" que pidió el profesor — no bloquea código |
| E3 (Marina) | `00_Storytelling_Scope`, `01_UX_Architecture` (guía directa para nosotros), `02_Data_Visualization_Spec`, `03_Visual_Identity` | Borrador hoy 18:00 · final viernes 15:00 | Reconciliar las ~9 rutas ya construidas contra el plan oficial de **7 pantallas** (Login + 6) — ver §4 |
| E4 (Estefany/Deni) | ML-03 cerrado con D1-D4, `cluster` real en Gold/API | Evidencia hoy, funcional viernes | No afecta `indice_riesgo`/`escuelas_en_riesgo` (son de ML-01) — confirmado, sin riesgo para el storytelling de "7 escuelas" |
| E2 (Andrés) | Chat funcional (`POST /api/v1/agente/consulta`) | Consumible viernes | Widget flotante ya definido por UX (E3) — solo lo montamos, la lógica es de E2 |

---

## 4. Pendientes con dueño (para cerrar hoy o mañana)

| # | Pendiente | Dueño | Vence |
|---|---|---|---|
| P-04 (de E3) | ADR de retiro de Superset | **Cerrado** — `ADR-012` ya escrito, pendiente ratificación PO | — |
| Auth | **Cerrado 10-sep** — cookie httpOnly de un solo origen vía proxy (ver §2.2) | Luis (proxy+CSP) / Christian (cookie+headers) / Diana (Dockerfile non-root) | Hoy |
| P-05 (de E3) | Confirmar `escuelas_en_riesgo=7` en `/api/v1/kpis` en vivo | Diana + Luis | Hoy 18:00 |
| Docker build | **Validado 10-sep** — `docker build` corre limpio (17/17), fix aplicado: `npm ci` necesitaba `--legacy-peer-deps` (mismo choque de peers que en local, `react-simple-maps` vs React 19) | Diana/Luis | Cerrado — falta probar el contenedor corriendo (`docker run`) y luego push a Artifact Registry |
| `prioridad`/`BUG-063` | **Resuelto 10-sep por el PO — `ADR-011` (Edgar) + `DEC-024`.** No se toca `gold.recomendaciones.prioridad` (sigue en 0.60, sin republicar). El frontend deriva su propio "nivel de atención" directo de `indice_riesgo`: alta `>= 0.50`, media `>= 0.30 y < 0.50`, baja `< 0.30` (reutiliza `LINEA_DE_ALERTA`/`RIESGO_ESTABLE`, cero cambios de backend). Pendiente: implementarlo en `frontend/src/lib/api.js` o un util nuevo — ver §9 | Diana/E5 (implementación, no decisión) | Antes del viernes, no bloqueante hoy |
| Reconciliación de páginas | 9 rutas construidas vs. 7 pantallas del plan de E3 | Diana | Con el borrador de E3 de hoy 18:00 |
| `/municipios` sin `nombre_entidad`/`cve_ent` en el schema | Fix de minutos en `MunicipioOut` | Christian | Solo si el plan de 7 pantallas de E3 sigue necesitando ranking/comparador municipal — **confirmar primero, no construir a ciegas** |
| Rollback | No existe runbook específico de frontend (el genérico es de Edgar, `Rollback_Runbook.md`) | Diana/Luis | Ver §6 |

---

## 5. Gate de hoy, 18:00

Lo que pide `Plan_Recuperacion_2026-09-09` para nuestro frente específicamente: **"Arquitectura de
frontend/integración (incluido uso de RAG) y estrategia de despliegue/rollback"** — no código
productivo nuevo todavía.

Lo que ya tenemos listo para presentar:
- Arquitectura y stack: [[vault/08_CICD_DevOps/Arquitectura_Frontend_React]] + `ADR-012`.
- Decisión de auth (§2.2) — a cerrar en la reunión misma.
- Estrategia de deploy: §2.3 + scripts ya escritos.
- Estrategia de rollback: §6 (nueva, se agrega en este plan).
- Uso de RAG/chat: recibido de E2, solo montaje de UI — sin lógica propia de nuestro lado.

Agenda (siguiendo el formato de control de 18:00 del PO): 5 min de demo contra evidencia (no
reporte verbal) — mostrar el combo #1 corriendo, el ADR, y la decisión de auth ya tomada.

---

## 6. Estrategia de rollback (frontend)

`faro-frontend` es un servicio Cloud Run adicional, sin estado y sin tocar la base de datos
directamente — el rollback es más simple que el del API (ver
[[vault/08_CICD_DevOps/Rollback_Runbook]] para el procedimiento general del proyecto).

1. **Criterio para revertir:** el sitio no carga, el login no completa el intercambio de token, o una
   pantalla del storytelling muestra datos incorrectos/rotos en producción.
2. **Procedimiento:** Cloud Run conserva la revisión anterior desplegada. Revertir es:
   ```bash
   gcloud run services update-traffic faro-frontend \
     --to-revisions=<REVISION_ANTERIOR>=100 \
     --region=us-central1
   ```
   Sin rebuild, sin migración — el tráfico vuelve a la imagen anterior en segundos.
3. **Verificación:** smoke test manual de las 6 pantallas + login, antes de declarar resuelto.
4. **Comunicación:** aviso en el canal del equipo + registro en `Incident_Log` si aplica, mismo
   procedimiento que el runbook general.

Kill-switch específico: si el problema es solo el widget de chat (E2) y no el resto del sitio, se
puede ocultar el botón flotante con una bandera de build sin redeploy completo del resto — pendiente
de confirmar con Andrés si eso es viable de su lado antes de necesitarlo.

---

## 7. Calendario

| Día | Entregable de Equipo 5 |
|---|---|
| **Jue 10, 18:00** | Este plan + arquitectura + decisión de auth cerrada + estrategia de rollback (gate, sin código nuevo) |
| **Vie 11** | Docker build validado (hecho 10-sep); `proxy_pass` + cookie de auth activos; reconciliación de páginas con el plan final de E3 (entrega 15:00); primera integración de chat (E2) y ML-03 (E4) si están listos |
| **Sáb 12, temprano** | Candidata **completa y funcional** en entorno de prueba — recorrido navegable de principio a fin, sin pantallas rotas ni placeholders sin rotular. Es nuestro corte real: deja el resto del sábado y el domingo como margen para que QA y cada frente prueben y pidan ajustes antes del freeze |
| **Dom 13, 18:00** | Ensayo final con QA (E6) |
| **Dom 13, 20:00** | *Code freeze* |
| **Lun 14** | Entrega en producción, healthchecks, cierre |

---

## 8. Definition of Done (heredado del plan canónico)

- PR aprobado y mergeado con CI, `vault_lint`, prueba y DevLog.
- Evidencia enlazada REQ → US → prueba → PR/DevLog → release.
- Validado en la revisión desplegada, no solo en local.
- Recorrido demostrable en máximo 12 minutos.
- Sin secretos, sin mocks sin rotular, sin defectos críticos/altos abiertos.
