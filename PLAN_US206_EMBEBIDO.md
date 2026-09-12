# PLAN — US-206: Embebido de los 10 dashboards + cierre US-204/US-205

> Plan de trabajo de **Manuel Alejandro Serranía Reinada** (Tech Lead C2 · Analytics & BI).
> Rama: `dev/manuel-serrania` · Cadena: mandado por Edgar (PM) para la demo del 2026-09-09.
> Documento de trabajo en la raíz; se borra antes del PR (Definition of Filed prohíbe archivos sueltos).

---

## 1. Contexto (verificado en el repo)

### 1.1 Qué pide el PM (US-206, reabierta)
- Construir **FARO Web**: `src/frontend/app.py` (shell/router) + embebido de los **10 dashboards**
  DB-01…DB-10 de Superset.
- Arquitectura ya decidida en `vault/03_Architecture/Frontend_Architecture.md §4` (no diseñar nada nuevo):
  **guest token de Superset por sesión con row-level security según el rol**, cada dashboard por
  **iframe firmado**.
- **AC-002.1** (10 dashboards accesibles desde la URL pública) y **AC-002.2** (filtros ciclo/entidad/nivel
  que aplican al conjunto) no se cumplen sin esto.
- **Sin token válido → no se muestra ningún tablero.**

### 1.2 Estado actual del código (`src/frontend/`)
| Archivo | Estado | Historia |
|---|---|---|
| `app.py` | andamiaje; `TODO(US-206)` en navegación | US-206 |
| `auth.py` | andamiaje; no valida JWT (depende de US-405/Christian) | US-405 |
| `pages/1_Dashboards.py` | **10 líneas, 1 TODO** (lo que hay que construir) | US-206 |
| `pages/2_Panel_ML.py` | andamiaje; 1 TODO | US-207 (Marina) |
| `pages/3_Chat.py` | **ya tiene código real** (52 líneas) | US-305 (Andrés) |

### 1.3 Estado de las historias relacionadas
- **US-204** (DB-06/DB-09): **código ya mergeado** (PR #100). Validación en vivo 15/15 charts sobre mock.
  La validación con datos reales es follow-up de US-313/BUG-013, no bloqueo de cierre.
- **US-205** (repunteo a `gold.cubo_*`): **código ya mergeado** (PR #134). En `Execution_Status.md` la
  evidencia quedó **mal etiquetada como "US-206"** — es el bug que Edgar reportó.
- Ambas cierran **documentalmente** (estatus + matriz + DevLog); no hay implementación pendiente.

### 1.4 Dependencias externas (NO bloquean el código mío, pero sí el embebido en vivo)
- **Guest token de Superset NO está habilitado** (`docker/superset.Dockerfile` / `superset-init.sh` no
  montan `superset_config.py` con `GUEST_ROLE_NAME`, `ENABLE_GUEST_EMBEDDING`, `AUTH_TYPE=AUTH_DB`).
  → Coordinar con **Luis Téllez (C5)** para habilitarlo.
- **DB-07 y DB-10 no tienen slug declarado** en `superset/dashboards/*.yaml` (solo existen DB-01…06, 08, 09).
  → Coordinar con **Oscar Quiroz (US-222/223)** para que los declare.
- Credenciales admin de Superset viven en `.env` (`SUPERSET_ADMIN_USERNAME`/`PASSWORD`).

---

## 2. Decisiones

- **Origen del guest token:** el **front habla directo con Superset** (`POST /api/v1/security/login` →
  `POST /api/v1/security/guest_token/`), NO se añade endpoint en la API. Reutiliza el patrón de
  `superset/sync_semantic_layer.py:login()`. Scope: solo `src/frontend/**` (verde de Manuel).
- **Coordinación obligatoria (hoy)** con Marina (US-207), Andrés (US-305) y Christian (US-405): todos
  tocarán `src/frontend/**`. Manuel es dueño (verde); ellos en amarillo → coordinar antes de cada merge.

---

## 3. Tareas por día

### Jue 3 — Arrancar el embebido real
- [x] Repo actualizado: rama `dev/manuel-serrania` desde `main`.
- [ ] Coordinar con Luis Téllez (guest token de Superset) y Oscar (DB-07/DB-10 declarados).
- [ ] Coordinar con Marina, Andrés y Christian el shell compartido.
- [ ] Escribir `src/frontend/superset_client.py` (login + guest token + cache en sesión).
- [ ] Escribir `pages/1_Dashboards.py` (catálogo DB-01…DB-10 + iframes firmados + filtros AC-002.2).
- [ ] Completar `app.py` (navegación/tarjetas, `TODO(US-206)`).

### Vie 4 — Embebido funcionando en local + cerrar US-204/US-205 (code freeze)
- [ ] Filtros ciclo/entidad/nivel aplicando al conjunto.
- [ ] Sin token válido → no se muestra ningún tablero.
- [ ] **Cierre documental US-204 y US-205** (este plan ya lo ejecuta).
- [ ] Pruebas del front; PR.

### Sáb 5 · Dom 6 · Lun 7 — Pruebas integrales / URL pública / correcciones

---

## 4. Alcance del cierre documental (US-204/US-205) — ejecutado primero

- [x] `vault/12_Roadmap_Sprints/Execution_Status.md`: corregir fila mal etiquetada (US-205 en vez de
  US-206) y marcar `US-204` y `US-205` como `done`.
- [x] `vault/_DevLog/2026-09-02-manuel-serrania-cierre-us204-us205.md` (+ fila en `_index`).
- [ ] Matriz de trazabilidad REQ-002 si aplica.

---

## 5. Riesgos y mitigación

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Guest token no habilitado en Superset (C5) | No carga ningún iframe | Solicitar a C5; si no llega, degradar a link/go-to-dashboard mientras el resto funciona |
| DB-07/DB-10 sin declarar (Oscar) | 2 de 10 tableros ausentes | Coordinar; documentar como dependencia explícita |
| Colisión con Marina/Andrés/Christian en `src/frontend/**` | Merge conflicts | Secuenciar merges; Manuel coordina el shell |
