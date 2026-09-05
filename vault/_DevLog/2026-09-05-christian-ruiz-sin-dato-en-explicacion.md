---
project: "FARO"
date: "2026-09-05"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — SIN_DATO representable en /predicciones/{cct}/explicacion antes de que C3 persista SHAP"
touches: ["US-412", "US-302", "REQ-004", "BUG-053"]
tags: [devlog, celula-4, api, contrato, sin-dato, shap, us412]
---

# DevLog — 2026-09-05 — La explicación fabricaba ceros donde no hay dato

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/API_Specification|API_Spec §3.4, §7]]

## Contexto

Preparando el terreno para conectar SHAP real (petición de Andrés González, C3), revisé el contrato
de `GET /predicciones/{cct}/explicacion` y encontré algo que **ya está mal hoy**, no en el futuro.

El endpoint hacía `escuela.get(f"d{i}") or 0.0`. Con un mock que trajera todos los drivers llenos
daría igual. Pero `mock_data` **ya modela cobertura parcial**: `15DPR0100B` tiene `d5 = None` y
`14DPR0250D` tiene `d6 = None` — exactamente los dos drivers que el proyecto sabe que son parciales,
D5 (estrés hídrico, regional) y D6 (aire, ~80 zonas urbanas).

Comprobado contra la app antes del cambio:

```
15DPR0100B  {'D1': 0.77, ..., 'D5': 0.0,  'D6': 0.29}
14DPR0250D  {'D1': 0.35, ..., 'D5': 0.71, 'D6': 0.0}
```

**La API afirmaba que D5 contribuyó cero** al riesgo de esa escuela. No es un redondeo: es una
afirmación falsa sobre *por qué* una escuela está en riesgo, que es la pregunta que el proyecto
existe para responder. Y contradice la regla de cobertura parcial —*"nunca cero, nunca nulo
silencioso"*— que el resto del sistema sí respeta: los cubos marcan `SIN_DATO` y
`indice_completitud_drivers` cuenta el hueco. Solo la explicación lo rellenaba.

El `or` además colapsaba **dos cosas distintas en el mismo número**: un `0.0` medido y un hueco
salían idénticos. Con SHAP real eso vuelve indistinguible un driver irrelevante de uno que nunca se
evaluó.

## Qué se hizo

- `ExplicacionSHAPOut.contribuciones` pasa de `dict[str, float]` a **`dict[str, float | None]`**.
  Las seis claves siguen **siempre presentes**: el hueco se declara, no se omite.
- El endpoint deja de aplicar `or 0.0`.
- `API_Specification` §3.4 y §7 actualizadas, con la instrucción explícita para quien persista las
  contribuciones: **escribir nulos, no ceros**.
- **Momento elegido a propósito:** se hace *antes* de que C3 escriba en Gold. Verifiqué que
  `/explicacion` **no tiene un solo consumidor** en el repo (ni frontend, ni agente, ni Superset),
  así que ensanchar el contrato hoy no rompe a nadie. Hacerlo después de que existan datos reales
  habría sido un cambio incompatible.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Modificados:** `src/api/schemas.py`, `src/api/v1/predicciones.py`,
  `tests/test_explicacion_shap.py` (+3), `vault/03_Architecture/API_Specification.md` (§3.4, §7),
  `api/openapi.v1.json`, `vault/_DevLog/_index.md`.
- **Creados:** este DevLog.

## Seguridad / calidad

- [x] **3 pruebas nuevas**, y las 3 **reprueban con el `or 0.0` anterior** (comprobado)
- [x] Una de ellas fija que `0.0` y `None` llegan **distintos**
- [x] `pytest` superficie de API → **140 passed**
- [x] `ruff check src/api tests` → limpio
- [x] OpenAPI reexportado; `test_api_contract.py` verde
- [x] Verificado el antes/después contra la app: `D5: 0.0` → `D5: null`

## Bloqueantes / avisos a otros owners

- **Andrés González (C3):** cuando persistas las contribuciones, **escribe `NULL` donde no haya
  valor, no `0`**. El contrato ya lo admite. Propuesta de forma: seis columnas nullable
  `shap_d1..shap_d6` en `gold.recomendaciones` — el grano ya es `(cct, id_ciclo)` y la salida de
  `explicar_driver` mapea 1 a 1, así que no hace falta tabla nueva ni source de dbt a un día del
  freeze. Sigue pendiente lo de siempre: hoy `explicar_driver` **no la llama nadie** y
  `publicar_gold.py` no persiste contribuciones, así que C4 no tiene de dónde leer.
- **Marina / QA:** este es el tipo de defecto que ninguna prueba cazaba porque la ruta **no tenía
  ninguna** hasta ayer. Ya son 11 casos.

## Próximos pasos

1. Login e2e real (mayor riesgo abierto de C4, depende de los *test users* de C5).
2. AC-004.5: 403 con token real de `ciudadano` contra `/admin/*`.
3. Leer las contribuciones del repositorio en cuanto C3 persista.
