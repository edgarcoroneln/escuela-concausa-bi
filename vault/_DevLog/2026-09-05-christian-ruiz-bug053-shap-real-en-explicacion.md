---
project: "FARO"
date: "2026-09-05"
author_human: "Christian Imanol Ruiz Hurtado"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — /explicacion deja el mock y sirve contribuciones SHAP reales desde Gold"
touches: ["BUG-053", "BUG-055", "US-412", "US-302", "REQ-003", "REQ-004"]
tags: [devlog, celula-4, api, ml, shap, sin-dato, bug053]
---

# DevLog — 2026-09-05 — `/explicacion` sirve SHAP real (BUG-053)

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/03_Architecture/API_Specification|API_Spec §3.4]] ·
[[vault/06_Quality_Testing/Bug_Register|BUG-053]]

## Contexto

`GET /predicciones/{cct}/explicacion` devolvía los seis drivers de `mock_data`, no la salida de
ningún modelo (`BUG-053`). El bloqueo **no era del endpoint**: `entrenar_ml02.explicar_driver`
calculaba SHAP con la forma exacta de `ExplicacionSHAPOut`, pero no la llamaba nadie y
`publicar_gold.py` no persistía contribuciones. No había fuente que leer.

Andrés González (C3) cerró ese lado en `924c8b4`: `shap_d1..shap_d6` **nullable** en
`gold.recomendaciones`, con un validador que convierte `NaN`/infinito en `None` — un detalle mejor
que lo que se había pedido. Esta sesión conecta el otro extremo.

## Qué se hizo

### La decisión que hizo el cambio pequeño

La ruta obvia era añadir `obtener_explicacion()` al repositorio. Habría obligado a tocar el
`Protocol`, el decorador de cache (`RepositorioModelosCacheado` no conoce métodos nuevos y un
`AttributeError` ahí sale como 500), los dos fakes y el cableado: **siete archivos**.

Pero `_seleccion_prediccion()` **ya hace el join con `gold.recomendaciones`**, que es justo donde
Andrés puso las columnas. Verificado que `PrediccionOut` ignora las claves extra (pydantic v2,
`extra="ignore"` por defecto), así que añadirlas al `SELECT` no toca la ruta de predicción.

`/explicacion` reutiliza `obtener_prediccion()` y hereda **gratis** el cache TTL y la traducción a
503 de US-416. Y hay un beneficio que no es de tamaño sino de corrección: explicación y predicción
salen de la **misma fila**, así que **no se pueden desincronizar** — es imposible servir una
explicación de un `driver_dominante` distinto al que se reportó. Hay una prueba que lo fija.

Tres archivos de código en vez de siete.

### Cambios

- **`src/api/db.py`** — declara las seis columnas en el `Table` de `recomendaciones`. No estaban:
  sin esto, SQLAlchemy no las conoce por más que existan en Postgres.
- **`src/api/repositorio_modelos.py`** — `COLUMNAS_SHAP` y las seis al `SELECT`.
- **`src/api/v1/predicciones.py`** — el endpoint lee del repositorio. Se elimina `_buscar_escuela`,
  que era el último consumidor de `mock_data` en este router.

Dos decisiones tomadas al escribirlo:

1. **`?ciclo` como parámetro real**, igual que `/predicciones/{cct}`. Sin él habría que asumir un
   ciclo, que es exactamente el default silencioso que causó `BUG-044`. Pedir un ciclo sin fila es
   **404**, no la fila de otro ciclo.
2. **`null` se transporta como `null`.** Colapsarlo a `0.0` sería reintroducir `BUG-055` — y con
   datos reales es peor que con el mock, porque la explicación responde *por qué* una escuela está
   en riesgo y un cero inventado ahí es una afirmación falsa sobre la causa.

### Pruebas

`tests/test_explicacion_shap.py` pasa de 8 a **15 casos**. Los que importan:

- `test_un_cero_medido_no_se_confunde_con_un_hueco` — `D5` vale `0.0` en una escuela y `null` en
  otra; tienen que llegar **distintos**. Si se confunden, un driver irrelevante y uno que nunca se
  evaluó se vuelven indistinguibles.
- `test_una_contribucion_sin_dato_viaja_como_null[D5|D6]` — los dos drivers de cobertura parcial
  del proyecto, donde SIN_DATO es el caso **normal**.
- `test_el_driver_dominante_es_el_de_la_misma_fila` — fija la propiedad de no-desincronización.
- `test_gold_caido_da_503_no_500` y `test_ciclo_sin_fila_da_404`.

El fixture (`tests/fixtures_modelos.py`) modela una escuela con las seis contribuciones y otra con
`D5`/`D6` en `None`. Que el hueco esté en el fixture es lo que impide que alguien lo "arregle"
colapsándolo a cero.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Modificados:** `src/api/db.py`, `src/api/repositorio_modelos.py`, `src/api/v1/predicciones.py`,
  `tests/fixtures_modelos.py`, `tests/test_explicacion_shap.py` (reescrito), `api/openapi.v1.json`,
  `vault/03_Architecture/API_Specification.md` (§3.4), `vault/06_Quality_Testing/Bug_Register.md`
  (`BUG-053` → `fixed`), `vault/_DevLog/_index.md`.
- **Creados:** este DevLog.

## Seguridad / calidad

- [x] 15 casos en `test_explicacion_shap.py`; superficie de API completa en verde
- [x] `ruff check .` (todo el repo, como el CI) limpio
- [x] `vault_lint.py` y `validate_pm_dashboard.py` en verde
- [x] OpenAPI reexportado; `test_api_contract.py` verde
- [x] Ningún `0.0` fabricado: el hueco viaja como `null` de Gold a la respuesta

## Bloqueantes / avisos a otros owners

- **Andrés González (C3):** conectado. Tu validador de `NaN`/infinito → `None` es justo lo que hacía
  falta; la API lo transporta sin colapsarlo. `US-302` pierde su pendiente *"conectar SHAP al
  endpoint"*.
- **Luis Téllez (C5) — sigue siendo lo más urgente:** la API en producción está en `33fcbbb`, **213
  commits atrás**. Nada de esto —ni `BUG-053`, ni `BUG-055`, ni el cache de `BUG-044` de Karla, ni
  el `KeyError` de US-416— está en el aire. Sin reseal y redeploy, la demo corre código de hace días.
- **`SEC-006`:** pendiente mi validación del flip a `AUTH_LECTURA_PUBLICA=false`, y su consecuencia
  está registrada como `BUG-057` (`high`, del PO). Va en sesión aparte: es decisión de producto, no
  código.

## Próximos pasos

1. Redeploy de la API (C5) — sin eso nada de esto existe para quien evalúe.
2. Login e2e real; con la lectura pública apagada ya no hay red de seguridad.
3. Resolver `BUG-057` con el PO.
