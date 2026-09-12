---
project: "FARO"
date: "2026-09-12"
author_human: "Luis Téllez Domínguez"
agent: "Claude Code"
model: "claude-opus-4-8"
session_duration: "1 sesión — cableado de FRONTEND_REDIRECT_URIS en el deploy de Cloud Run (BUG-075), el gemelo en producción del hueco que Diana corrigió en docker-compose.yml. Sin tocar prod ni credenciales."
touches: ["BUG-075", "US-405", "ADR-012", "REQ-004", "REQ-005"]
tags: [devlog, equipo-5, deploy, cloud-run, auth, ci-cd]
---

# DevLog — 2026-09-12 — BUG-075: `FRONTEND_REDIRECT_URIS` nunca llegaba al Cloud Run real

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo|ADR-012]] ·
[[vault/07_Security/Threat_Model|Threat_Model]]

## Contexto

Al probar en vivo el botón de login del React (US-405), **Diana Álvarez** encontró y reportó dos
huecos que bloquean el login end-to-end y que tocan alcance de CI/CD (regla 7): (1) el `environment:`
del servicio `api` en `docker-compose.yml` nunca pasaba las variables de auth al contenedor —lo
corrigió ella para local—, y (2) **el mismo hueco existe en producción**:
`vault/08_CICD_DevOps/scripts/deploy-cloud-run.sh` no incluye `FRONTEND_REDIRECT_URIS` en su
`--set-env-vars`, así que aunque el valor sea correcto, hoy **nunca llegaría al Cloud Run real**.
Christian lo dejó anotado igual en su DevLog del 11-sep ("`deploy-cloud-run.sh` no pasa
`FRONTEND_REDIRECT_URIS` al Cloud Run real") y en el `Threat_Model` v1.3 (paso 2 del flujo OAuth:
"⏳ valor de prod"). Ese segundo hueco es de mi alcance (`vault/08_CICD_DevOps/**` es ruta crítica de
`luis-tellez` en `ownership.yml`). Esta sesión lo cierra.

El detalle que lo hace crítico: la API compara el `redirect` que manda el front contra
`FRONTEND_REDIRECT_URIS` por **coincidencia exacta, no por prefijo** (`src/api/config.py:130`
`frontend_redirect_list` hace `split(",")`; `src/api/v1/auth.py:100` hace `if redirect not in ...`).
El React manda `redirect=window.location.origin` (sin barra final ni ruta). Si la variable no llega,
la API se queda con el default de desarrollo `http://localhost:8501` (`src/api/config.py:59`), que en
producción **nunca** iguala a `https://faro-frontend-eanzfglvyq-uc.a.run.app` → `_validar_redirect`
responde 400 y el login no completa.

## Qué se hizo

Un solo archivo tocado: `vault/08_CICD_DevOps/scripts/deploy-cloud-run.sh`.

1. **Se define `FRONTEND_REDIRECT_URIS`** con default al **origen canónico de FARO Web**
   (`https://faro-frontend-eanzfglvyq-uc.a.run.app`, sin barra final), overridable por entorno igual
   que `ANALISTA_EMAILS`. Elegí ese origen porque es el que los documentos oficiales declaran como
   "entrada principal" (`README.md`, `vault/00_Start_Here/PROJECT_INDEX.md`, `Guion_Demo_US006.md`);
   Cloud Run también responde en el alias con número de proyecto
   (`faro-frontend-526490367142.us-central1.run.app`, que aparece solo en QA logs), y como
   `window.location.origin` refleja el origen que el usuario abra, dejé anotado en el comentario que si
   el recorrido del profesor usará ese alias u otro origen hay que **añadirlo**.
2. **Se agrega al `--set-env-vars`**, colocado **antes** de `ANALISTA_EMAILS` a propósito:
   `ANALISTA_EMAILS` debe quedar al final porque con varios correos lleva comas y `--set-env-vars`
   separa pares por coma (ya lo advertía el comentario preexistente del script). El comentario nuevo
   documenta la misma trampa para el caso multi-origen y da la receta con delimitador alterno
   (`--update-env-vars="^|^FRONTEND_REDIRECT_URIS=https://a,https://b"`).
3. **Se agrega un `echo`** de la allowlist en el resumen previo al deploy, para que el operador vea el
   valor efectivo antes de desplegar y no descubra un origen equivocado como un 400 silencioso.

**Lo que NO se hizo, a propósito** (regla 7 / autorización del PO): no se ejecutó ningún `gcloud`, no
se redesplegó nada, no se tocó producción y no se ingresó ninguna credencial real de Google. El valor
solo tiene efecto cuando alguien **corra** el script de deploy.

## Pruebas ejecutadas

```
bash -n vault/08_CICD_DevOps/scripts/deploy-cloud-run.sh   → sin errores de sintaxis
python vault/_Meta/scripts/vault_lint.py .                 → limpio
grep de faro-frontend-* en el repo                          → hash (9 usos, docs oficiales) vs
                                                              número-de-proyecto (6 usos, solo QA)
```

No se probó el login e2e: requiere el redeploy con las credenciales reales de Google, que quedan
pendientes (abajo). Esta sesión deja **1 de los 3 bloqueantes** listo; por sí solo no habilita el
login.

## Ownership y reglas

- `vault/08_CICD_DevOps/**` es alcance de `luis-tellez` — este cambio lo hace el dueño en su propia
  rama, así que `check_ownership.py` pasa sin excepción. **No se invoca `DEC-025`** (esa autorización
  es para que *otros* toquen mis rutas críticas sin bloquearse; aquí no aplica). `DEC-025` sí es el
  contexto de por qué el login se está armando ahora, durante mi viaje, pieza por pieza.
- **Regla 7 (cambio de CI/CD):** requiere revisión humana explícita. La aporta la compuerta única del
  PM (`DEC-003`) sobre el PR; no se mergea en silencio.

## Bloqueantes

Ninguno para este cambio. Para el login e2e siguen abiertos los otros dos bloqueantes, ambos de
decisión de Luis (regla 7), no de esta sesión:

1. **`GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` reales** — sin ellos el login no completa en ningún
   entorno. Secretos: no se ingresan por chat ni se versionan.
2. **Redeploy del front React + API a Cloud Run** y validación del recorrido completo hasta la sesión
   FARO en la URL pública.

## Próximos pasos

- Al abrir el PR, dejar constancia de que es un cambio de CI/CD revisado por la compuerta del PM
  (regla 7).
- Confirmar con el equipo cuál es el origen exacto que abrirá el profesor y, si es el alias con número
  de proyecto, añadirlo a `FRONTEND_REDIRECT_URIS` con la receta del comentario antes del redeploy.
- Coordinar con quien haga el redeploy (Luis) que el valor efectivo del `echo` sea el correcto.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-4-8.
- **Archivos creados/modificados:** `vault/08_CICD_DevOps/scripts/deploy-cloud-run.sh` (fix), este
  DevLog, su fila en `vault/_DevLog/_index.md`, y la fila `BUG-075` en
  `vault/06_Quality_Testing/Bug_Register.md`.
- **Decisiones autónomas del agente:** ninguna acción sobre producción ni GitHub-facing más allá de
  abrir el PR autorizado por el PO. No se ejecutó `gcloud` ni se tocaron credenciales.
- **Correcciones manuales:** ninguna sobre este DevLog.

## Seguridad / calidad

- [x] Sin secretos hardcodeados (la URL del front es pública; viaja en la URL de consentimiento)
- [x] Ningún correo ni credencial versionados
- [x] No se tocó producción ni se ejecutó `gcloud`
- [x] DevLog enlaza a los IDs afectados

→ [[vault/_DevLog/_index|Volver al índice]]
