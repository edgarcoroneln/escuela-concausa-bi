---
project: "FARO"
date: "2026-09-06"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — validación de SEC-006 como dueño de 07_Security y corrección de tres afirmaciones falsas mías"
touches: ["SEC-006", "SEC-007", "AC-004.5", "DEC-018", "BUG-059", "REQ-004"]
tags: [devlog, celula-4, seguridad, revision, correccion, sec006]
---

# DevLog — 2026-09-06 — Validación de `SEC-006` y corrección de tres afirmaciones mías

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/07_Security/Security_Review_US402_US403_US404|Revisión §11, §12]] ·
[[vault/07_Security/Security_Audit_Log|SEC-006]]

## Contexto

Luis Téllez ejecutó el flip `AUTH_LECTURA_PUBLICA=false`, marcó `SEC-006` como `resolved` y me
notificó como dueño de `vault/07_Security/**`. Quedaba pendiente mi validación desde el 05-sep;
esperé a que el PO cerrara `BUG-057` porque su decisión cambiaba la conclusión.

## Qué se hizo

### Validación: 🟢 `SEC-006` queda `resolved`

La condición de cierre que este documento fijó el 02-sep era *"apagar la lectura pública cuando el
login e2e esté validado en vivo"*. **Se cumplió, y en ese orden**: el login e2e real ocurrió el
04-sep (rev `00011-hr5`, tras el fix de `at_hash`) y el flip vino después, el 05-sep. No se cerró
un riesgo apagando la comprobación — se cerró habiendo demostrado primero que la alternativa
funciona. Ejecución correcta: env-var, sin rebuild, reversible, sin cambio de código.

### La parte incómoda: tres cosas que dije y eran falsas

Durante varios días sostuve, y el PO transmitió al equipo, que:

| Lo que dije | Lo real |
|---|---|
| *"El login e2e nunca se ha ejecutado"* | Se ejecutó el **04-sep** en producción, por Luis Téllez |
| *"Falta cerrar `AC-004.5`"* | **Cerrada**: 401 sin token · 200 analista · **403 ciudadano**, cuentas reales |
| *"C5 debe buscar `SEC-007` en los logs"* | **Buscado**: `almacen` en `faro-api`, 3 h, sin coincidencias |

La evidencia llevaba dos días en [[vault/_DevLog/2026-09-04-luis-tellez-redeploy-bug046-e2e]].
El error fue sostener un estado mental viejo en vez de leer el DevLog del owner antes de repetir la
afirmación. **Consecuencia concreta: se le pidió a C5 trabajo que ya había entregado**, en el día
más cargado de la semana. Queda escrito en el Anexo C, no omitido.

`SEC-007` se mantiene en `accepted_risk`, no sube a `resolved`: la búsqueda fue acotada a 3 h y el
propio DevLog lo declara. Con `min=max=1` el riesgo no se materializa, pero ausencia de log no es
prueba.

### Constancia de `DEC-018`

Recomendé lo contrario —volver a lectura pública para la demo— sosteniendo que el flag no aporta
puntos de rúbrica (OAuth2 y RBAC se demuestran con `/admin/*`, que exige `analista` siempre,
independiente del flag) y que cierra la URL pública, que sí vale 1.0 vía `RISK-001`. El PO decidió
la postura contraria. **No la reabro.** Queda registrada para que conste que el costo fue evaluado
y aceptado, no descubierto por accidente.

**Consecuencia técnica que sí es mía:** con la lectura cerrada, el defecto del token de FARO Web
deja de ser latente y pasa a activo. Corregido en `BUG-059`; sin ese arreglo, `DEC-018` deja el
front sin funcionar para alguien con sesión iniciada. **Las dos cosas tienen que desplegarse juntas.**

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Modificados:** `vault/07_Security/Security_Review_US402_US403_US404.md` (§11 Anexo C, §12 firma;
  `version` 1.1 → 1.2, `status` → `approved`), `vault/07_Security/Security_Audit_Log.md`,
  `vault/_DevLog/_index.md`. **Sin cambios de código.**

## Seguridad / calidad

- [x] `SEC-006` validado contra su condición de cierre original, no contra la conveniencia de hoy
- [x] Corrección escrita en el documento canónico, no solo en un chat
- [x] `SEC-007` **no** se sube a `resolved`: la evidencia es razonable, no concluyente
- [x] Revisión de seguridad pasa a `approved` — sin hallazgos bloqueantes abiertos

## Bloqueantes / avisos a otros owners

- **Luis Téllez (C5):** te pedí dos veces cosas que ya habías hecho. Corregido y escrito.
  Lo que **sí** sigue pendiente y es real: **la API está desplegada en `33fcbbb`** y no tiene
  `BUG-053`, `BUG-055`, el cache de `BUG-044` ni el `KeyError` de US-416; y el front desplegado
  tiene el bug de sesión de `BUG-059`.
- **Edgar (PO):** `DEC-018` con constancia. `SEC-006` validado.

## Próximos pasos

1. Redeploy de API y front — el único bloqueo real que queda de C4 hacia la demo.
2. Merge de `BUG-059`; tiene que ir junto con `DEC-018`, no después.
