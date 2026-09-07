---
project: "FARO"
date: "2026-09-07"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — cierre e2e del camino A (DEC-019 a 0.50 en prod): el Panel ML del shell daba 503 en toda predicción (columnas SHAP ausentes en el Gold desplegado tras BUG-053) y faltaba el botón de cerrar sesión en las páginas internas; ambos diagnosticados, corregidos y verificados en vivo"
touches: ["US-207", "US-405", "US-526", "BUG-053", "BUG-048", "DEC-019", "REQ-004", "REQ-005"]
tags: [devlog, celula-5, api, gold, cloud-sql, schema, frontend, streamlit, cloud-run, despliegue, sin-dato]
---

# DevLog — 2026-09-07 — Camino A cerrado e2e: el 503 del Panel ML (columnas SHAP) y el logout en todas las páginas

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/_DevLog/2026-09-06-luis-tellez-frontend-imagen-combinada|Imagen combinada del frontend]] · [[vault/_DevLog/2026-09-05-christian-ruiz-bug053-shap-real-en-explicacion|BUG-053 SHAP real]] · [[vault/08_CICD_DevOps/Cloud_Run_Deploy|Deploy a Cloud Run]]

## Contexto

El **camino A** (coherencia DEC-019: la línea de alerta del KPI-04 a **0.50**, distinta del ancla de la
sigmoide 0.60) ya está vivo en prod: la API corre la imagen **`c4410d1`** (rev `faro-api-00014-24b`), que
incluye `0f4b37c` (DEC-019) y **BUG-053** (`/explicacion` y la consulta de predicción dejan el mock y leen
`gold.recomendaciones.shap_d1..shap_d6`). El shell **FARO Web** (US-526, Streamlit) expone el **Panel de ML**
(US-207), que consume `/api/v1/predicciones/{cct}`.

Al verificar el camino A **de extremo a extremo** aparecieron dos defectos que las pruebas y los smokes de
salud no cazaban:

1. El **Panel de ML devolvía 503** («La capa Gold no está disponible; vuelve a intentar en un momento») para
   **todo** CCT.
2. El botón **«Cerrar sesión» faltaba** en Panel de ML, Chat y Dashboards (solo aparecía en la home).

## Causa raíz (confirmada con evidencia)

**Fix A — el 503 es un desajuste dato↔código de despliegue, no un defecto de código.** BUG-053 (C4/C3, ya en
`main` y ahora desplegado por el camino A) hizo que la consulta unificada de predicción (`predicciones ⋈
recomendaciones` en `repositorio_modelos.py`, la que sirve `/predicciones/{cct}` y `/explicacion`)
**seleccione siempre** `gold.recomendaciones.shap_d1..shap_d6`. El productor de esas columnas es C3
(`src/modelos/publicar_gold.py`, commit `924c8b4`), y `src/api/db.py` ya las declara `Float nullable`. **Pero
el Gold que vive en Cloud SQL** —el dump `final2` importado al cerrar **BUG-048** el 2026-09-05— **se generó
antes** de ese cambio, así que las columnas **no existían físicamente** en la tabla. Resultado:
`psycopg.errors.UndefinedColumn` → el repositorio lo traduce a `RepositorioModelosNoDisponible` → **503**.
Reconstruir la imagen desde `main` **no** ayudaba: la selección de SHAP es incondicional.

**Fix B — el logout vivía en un solo sitio.** `logout_button()` solo se llamaba desde `app.py`; como Streamlit
**reejecuta únicamente el script de la página activa** al navegar, el botón no sobrevivía al cambio de página.

## Qué se hizo

### Fix A — columnas SHAP en el Gold (operación de datos, autorizada por Luis)

Cambio **aditivo, reversible y de esquema (regla 7)** — sometido a revisión humana por este DevLog + PR:

1. **Respaldo de Cloud SQL ANTES:** backup **`1788759819478`** (SUCCESSFUL).
2. `ALTER TABLE gold.recomendaciones ADD COLUMN IF NOT EXISTS shap_d1..shap_d6 double precision` (nullable),
   vía **Cloud Run Job efímero in-VPC** `faro-alter-shap` (reutiliza la imagen de la API, conector
   `faro-connector`, SA `faro-api-sa`, contraseña por secreto `db-password` **nunca impresa**). El dueño de la
   tabla es `faro_app` (el mismo usuario del SA), por eso el `ALTER` corrió sin fricción de permisos.
3. **Sin redeploy de la API** — es solo dato; la imagen `c4410d1` queda intacta.
4. Ambos jobs efímeros (`faro-alter-shap` y el verificador `faro-pred-check`) **borrados** al terminar (sin
   infraestructura residual).

Las 6 columnas quedan **`NULL` = `SIN_DATO`** hasta que **C3** regenere y republique el Gold con `publicar_gold.py`
(que ya las escribe, `924c8b4`). El contrato lo respeta: `PrediccionOut` transporta `null` como `null`, nunca
`0.0` (colapsarlo reintroduciría BUG-055 con datos reales).

### Fix B — logout en todas las páginas (código C2, NO se commitea aquí)

Se añadió el helper `barra_sesion(user)` en `src/frontend/auth.py` (identidad + rol + `logout_button()` en la
barra lateral) y se invoca desde las 4 páginas (`app.py`, `1_Dashboards.py`, `2_Panel_ML.py`, `3_Chat.py`).
**El código del shell es de C2** (Manuel/Marina); C5 solo lo conteneriza y despliega. Se rehorneó la **imagen
combinada** `--platform linux/amd64` **`faro-frontend:embed-combo-dec019-logout`** (base = la imagen embebida
`embed-combo-dec019` que ya servía Dashboards + Panel ML a 0.50, **más** el logout; el **diff frente a la
imagen desplegada es SOLO el logout**, sin tocar el embebido ni la línea 0.50) → **rev `faro-frontend-00008-fpw`**,
100 % de tráfico, env-vars y secreto de Superset **preservados** (`services update --image`, merge no reemplazo).

## Cómo se probó

- **Fix A (read-only, Job efímero `faro-pred-check`):** la consulta unificada **exacta** de
  `repositorio_modelos.py` ya corre y devuelve fila para los tres CCT probados —
  `15PES0343S` (índice **0.5717**, driver **D2**, en riesgo), `15DJN0049A` (**0.3466**, **D4**, el del reporte
  original) y `09DSN0042A` (**0.1339**, **D2**) — con `shap_d1..d6 = None` (SIN_DATO). El 503 desaparece.
- **Fix B (local):** smoke del contenedor amd64 verde — `/_stcore/health` 200 e import de la app OK.
- **Smoke en PROD:** frontend `/_stcore/health` **200** (rev `00008-fpw`); API `c4410d1` `/health` **200**.
- **En vivo, por Luis (gate final e2e):** confirma que el **Panel de ML ya no da 503** (CCT en riesgo y CCT
  sanos) y que **«Cerrar sesión» aparece en Dashboards, Panel de ML y Chat** y funciona ("ya confirmé todo ok").

## Diagnósticos / aprendizajes

- **Un redeploy de código puede romper una ruta si el dato desplegado quedó atrás.** BUG-053 estaba probado en
  `main`, pero el Gold en prod era anterior al productor de las columnas SHAP; el contrato SELECT las exigía y
  la tabla no las tenía. El aprendizaje: al desplegar código que amplía el contrato de lectura de Gold, hay que
  **verificar que el Gold desplegado tenga el esquema** (o migrarlo), no solo que la imagen sea la nueva.
- **`SIN_DATO` honesto sobre el cero:** se agregaron las columnas vacías en vez de fabricar `0.0`. Un `0.0` en
  D5/D6 sería indistinguible de "driver irrelevante"; `null` dice "aún no calculado". Las poblará C3.
- **La salud (`/health`) no cubre el camino de negocio.** El 503 era por CCT en `/predicciones`, no en
  `/health`; solo la verificación e2e lo destapó — de ahí la regla de Luis de probar en persona cada ambiente.

## Seguridad / calidad

- [x] **Cambio de esquema (regla 7):** `ADD COLUMN ... nullable`, **aditivo y reversible**
  (`ALTER TABLE gold.recomendaciones DROP COLUMN shap_d1..shap_d6`), autorizado por Luis y sometido a revisión
  del PO por este DevLog + PR. **Respaldo previo** de Cloud SQL `1788759819478`.
- [x] **Cero secretos** en repo/chat/DevLog: la contraseña de la DB se inyectó como `secretKeyRef`
  (`db-password`) al Job efímero y **nunca** se imprimió.
- [x] **No se tocaron env-vars de seguridad:** `AUTH_LECTURA_PUBLICA=false` (SEC-006), OAuth/whitelist y
  redirect URIs intactos; el frontend se desplegó con `--image` (merge), preservando el secreto de Superset.
  Los correos de login siguen **efímeros** solo en la revisión de Cloud Run, nunca en archivo.
- [x] **Este PR NO toca código de aplicación** (`src/**`): sube solo este DevLog + su fila de índice (comunes).
  El gate de propiedad pasa.
- [x] **Sin residual:** ambos Jobs efímeros borrados; el único cambio persistente en GCP es el dato (columnas
  vacías en Cloud SQL, reversibles) y la rev `00008-fpw` del frontend (reversible por `update-traffic`).

## Avisos a otros owners

- **C3 (Andrés González) — puebla las SHAP reales (no bloquea la demo):** las 6 columnas están en `NULL`. Al
  regenerar/republicar el Gold con `publicar_gold.py` (`924c8b4`) quedarán con los valores reales y
  `/explicacion` dejará de devolver `SIN_DATO`. El `ALTER` ya dejó la tabla lista para recibirlos.
- **C4 (Christian Ruiz) — informativo:** **BUG-053 ya está desplegado** (imagen `c4410d1`) y **operativo** tras
  el `ALTER`; el aviso "la API sigue en `33fcbbb`" de tu DevLog de BUG-053 quedó superado por el camino A.
- **C2 (Manuel / Marina) — deuda de reproducibilidad (no bloquea la demo):** el shell corre en prod horneado
  desde el working tree; para que un rebuild desde `main` no regrese Dashboards/Panel ML/logout, hay que
  commitear a `main` desde la rama de C2 el embebido (`superset_client.py`, `1_Dashboards.py`), el parche 0.50
  (`prediccion_client.py`, `2_Panel_ML.py`) y el logout (`auth.py` con `barra_sesion()` + su llamada en las 4
  páginas). C5 no puede llevarlos (`src/frontend/**` es alcance de C2, el gate de propiedad reprueba).
- **PO (Edgar):** merge de este DevLog (solo comunes). El `ALTER` de esquema queda sometido a tu revisión
  (regla 7); es aditivo, reversible y con respaldo.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Creados:** este DevLog.
- **Modificados:** `vault/_DevLog/_index.md` (fila de este DevLog).
- **Infra GCP (sin cambio de imagen de seguridad):** `ALTER` de `gold.recomendaciones` (columnas SHAP nullable)
  vía Job efímero in-VPC + backup `1788759819478`; frontend rev `faro-frontend-00008-fpw` con imagen
  `embed-combo-dec019-logout` (diff = solo logout), env-vars y secreto preservados.
- **Sin cambios de código** de aplicación (`src/`) en este PR; el logout es código de C2 (deuda de C2, arriba).
