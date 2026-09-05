---
project: "FARO"
date: "2026-09-04"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — revisión de regla 7 sobre el parche de BUG-046 (at_hash) y anexos a la revisión de seguridad"
touches: ["BUG-046", "SEC-009", "US-402", "US-403", "REQ-004", "DOC-SECREV-C4"]
tags: [devlog, celula-4, seguridad, oauth2, revision, bug046, us402]
---

# DevLog — 2026-09-04 — Revisión de C4 sobre `BUG-046` y anexos a la revisión de seguridad

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/07_Security/Security_Review_US402_US403_US404|Revisión §8, §9]] ·
[[vault/07_Security/Security_Audit_Log|SEC-009]] · [[vault/06_Quality_Testing/Bug_Register|BUG-046]]

## Contexto

Luis Téllez (C5) encontró `BUG-046`: **ningún login real completaba en producción**, ni analista ni
ciudadano, todos 401. Diagnosticó, parcheó y validó el fix; Edgar Coronel (PO) lo mergeó como
excepción, porque el cambio toca `src/api/security/**` —alcance verde de C4— y el gate de propiedad
reprueba, correctamente, un PR de C5 sobre esa ruta.

El procedimiento fue el adecuado y se pidió mi revisión **antes** del redespliegue, que es el momento
útil. Lo que no existía era el registro: la **regla 7 exige revisión humana explícita del dueño del
área** para todo cambio de seguridad, y el propio `Bug_Register` decía *"se recomienda revisión de
C4"*. Esa revisión vivía en un chat. Esta sesión la convierte en artefacto.

## Qué se hizo

### Verificación independiente del parche (no me basé en el reporte)

- **Reverti la línea** `options={"verify_at_hash": False}` y corrí `tests/test_oauth_google.py`:
  **1 failed, 23 passed**, con `JWTClaimsError` — el mismo tipo de excepción de los logs de Cloud Run.
  Falla exclusivamente el caso de `at_hash`. El bug era real y el fix lo cierra.
- **Repuesto el parche**, la familia completa de auth (`test_oauth_google`,
  `test_puente_oauth_frontend`, `test_auth_jwt`, `test_frontend_auth`) → **66 passed**.
- **Leí el código de `jose`** en vez de asumir su comportamiento. Dos detalles deciden el veredicto:
  - `jwt.py:458` — `_validate_at_hash` **retorna si el claim no está**, y `require_at_hash` es `False`
    por defecto. No truena por *no traer* `at_hash`, truena por **traerlo sin el `access_token`**. Eso
    explica por qué 23 pruebas daban verde contra un flujo roto al 100 % en producción.
  - `jwt.py:153` — `defaults.update(options)`, **no** reemplazo: firma RS256, `aud`, `iss` y `exp`
    **siguen activas**. Es un apagado quirúrgico, no un `verify_signature: False` encubierto.

**Veredicto: 🟢 aprobado sin cambios.** El razonamiento de seguridad de C5 se sostiene: `at_hash` ata
dos tokens que llegan por canales distintos —defensa del *implicit flow*—; en *code flow*
servidor-a-servidor ambos llegan en el mismo cuerpo TLS del token endpoint. OIDC Core lo declara
REQUIRED en implicit y **OPTIONAL** en code flow, precisamente por eso.

### `SEC-009` — el follow-up que sí existe

`_intercambiar_code` lee solo el `id_token` y **descarta el `access_token`** que Google devuelve en
ese mismo JSON. Propagarlo haría que `at_hash` se **verificara** en vez de desactivarse. **No se pide
para la entrega**: cambia el tipo de retorno de una función en el camino crítico del login a dos días
del *code freeze*, y la ganancia real es nula por lo anterior. Queda registrado con dueño y condición
de cierre, no como deuda silenciosa.

### El hallazgo de fondo, que es mío

La causa raíz no es la línea que faltaba: **el doble de prueba era más angosto que el proveedor
real**. `google_falso` emitía los claims que se nos ocurrió emitir, no los que Google emite. El test
de regresión de Luis cierra el hueco concreto; la lección general —un *fake* de un IdP se modela
sobre la respuesta real, no sobre la esperada— es de C4 y queda escrita en §8.5.

### Anexo B — el límite de la verificación en la URL pública

Aproveché para cerrar algo que la revisión arrastraba abierto desde el lunes: las **11 comprobaciones
contra la URL pública** quedaron registradas con su evidencia… y con su límite dicho en voz alta.
**Las 11 son casos negativos**: confirman que el perímetro rechaza lo que debe rechazar. **Ninguna
ejercitó un login real completo.** `BUG-046` cayó exactamente en ese punto ciego — perímetro
impecable, camino feliz roto del todo. Un tablero verde hecho solo de rechazos no prueba que el
sistema funcione, y eso merecía quedar escrito antes que después.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** este DevLog.
- **Modificados:** `vault/07_Security/Security_Review_US402_US403_US404.md` (§8 anexo A, §9 anexo B,
  §10 firma; `version` 1.0 → 1.1), `vault/07_Security/Security_Audit_Log.md` (`SEC-009`),
  `vault/_DevLog/_index.md`.
- **Sin cambios de código.** La revisión no pide modificar el parche. La reversión de prueba se
  deshizo con `git checkout --` y el árbol quedó limpio.

## Seguridad / calidad

- [x] Parche verificado por reversión: reprueba, y solo el caso esperado
- [x] `66 passed` en la familia de auth con el parche puesto
- [x] Comportamiento de `jose` leído en el código fuente, no asumido
- [x] Se confirmó que `options` **no** desactiva las demás verificaciones (`defaults.update`)
- [x] Regla 7 satisfecha: revisión humana explícita del dueño del área, firmada y fechada

## Bloqueantes / avisos a otros owners

- **Luis Téllez (C5):** puedes **redesplegar sin esperarme** — el fix está aprobado y en `main`. Tras
  el redespliegue quedan dos cosas: (1) el **login e2e real**, que sigue siendo la única prueba que
  falta y el mayor riesgo abierto de C4, y (2) revisar en los logs de Cloud Run si aparece
  `No se pudo preparar el almacen de codigos` — es `SEC-007`, y distingue si el almacén quedó en
  Postgres o degradó a memoria. Desde fuera no se puede saber: con una instancia se comportan igual.
- **Edgar (PO):** el sello de regla 7 sobre `BUG-046` ya existe (§8). La excepción de propiedad quedó
  documentada y ratificada, no pendiente.

## Próximos pasos

1. Login e2e real contra la revisión que ya incluya el parche de `BUG-046`.
2. Con un token real de `ciudadano`, cerrar el último caso de RBAC: **403** contra `/admin/*` (AC-004.5).
3. Decidir con C5 el flip de `AUTH_LECTURA_PUBLICA` (`SEC-006`) una vez validado el login.
