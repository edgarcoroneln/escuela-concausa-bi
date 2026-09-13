---
project: "FARO"
date: "2026-09-13"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1h"
touches: ["US-601", "REQ-002", "REQ-004"]
tags: [devlog, us-601, api, rendimiento, equipo-1]
---

# DevLog — 2026-09-13 — La caché no se compartía entre peticiones (US-601)

→ [[vault/_DevLog/_index|Volver al índice]]

## El defecto, y por qué no lo vi

Edgar Coronel encontró que **el cache que agregué ayer no servía de nada**. FastAPI llama a
`get_repositorio_about()` en **cada petición**, así que sin `@lru_cache` cada una estrenaba su
propio `TTLCache` vacío y repetía el barrido completo de ~30 `COUNT(*)`. Lo midió pasando por el
endpoint: **3 `GET` daban 3 barridos**.

**Copié el patrón de `cache_predicciones.py` sin copiar lo que lo hace funcionar**, que es el
`@lru_cache` de `get_repositorio_modelos()`. Y mis pruebas no lo cazaron porque **usaban una
instancia directa del repositorio**, nunca el endpoint — probaban el cache aislado de la única
condición que lo vuelve inútil. Es un error de nivel de prueba, no de código: la lógica del cache
era correcta y aun así el sistema no lo tenía.

## Los tres cambios

**1 · `@lru_cache` en la dependencia.** Con eso el repositorio es un singleton por proceso, igual
que `get_repositorio_modelos()`.

**2 · El motivo del fallo viaja DENTRO del resultado.** Consecuencia directa del punto 1 que Edgar
anticipó: con un singleton compartido entre hilos, `self._error_de_conexion` se vuelve una carrera
— dos peticiones concurrentes pueden pisarse la bandera y una acabaría declarando una caída que le
pasó a la otra. Ahora `conteos_capas()` devuelve un `ConteosCapas` inmutable con `filas`,
`base_no_disponible` y `tablas_lentas`. **No hay estado mutable que compartir.**

**3 · Un timeout no es una caída.** psycopg2 reporta las dos como `OperationalError`, así que
`bronze.sesnsp` —12.5 M de filas— podía hacer que la página declarara la base caída con Postgres
perfectamente sano, y además impedía cachear. Se distinguen por SQLSTATE `57014`
(`query_canceled`). Ahora son **tres** causas separadas, cada una con su mensaje:

| Causa | Qué dice | ¿Se cachea? |
|---|---|---|
| La base no responde | «la base de datos no respondió» | **No** — si no, la recuperación no se vería hasta vencer el TTL |
| La consulta excede su tiempo | «la tabla es grande y la consulta excedió su tiempo» | **Sí** — el resultado es legítimo y repetirlo es la carga que el cache evita |
| La tabla no existe | «Tabla no materializada todavía» | Sí |

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Modificados:** `src/api/repositorio_about.py`, `src/api/v1/about.py`, `tests/fixtures_about.py`,
  `tests/test_repositorio_about.py`, `api/openapi.v1.json`
- **Decisiones autónomas del agente:** devolver un dataclass inmutable en vez de mantener la
  bandera de instancia; cachear los resultados con tablas lentas pero no los de caída.
- **Correcciones manuales:** ninguna al código. **El defecto lo encontró la revisión humana**, y
  la lección es del nivel de prueba: una prueba de unidad sobre la instancia no puede ver un
  defecto que vive en cómo el framework construye esa instancia.
- **Prompt inicial:** nota de revisión de Edgar Coronel.

## Seguridad / calidad

- [x] `pytest tests/ -q` → **1304 passed, 10 skipped** (eran 1299; +5)
- [x] `ruff` limpio · sin dependencias nuevas
- [x] **Prueba por el endpoint**, que es la que faltaba: 3 `GET` → **1 barrido**
- [x] Verificado en vivo contra la base real: 3 peticiones, conteos correctos, sin advertencias

**Las dos correcciones se falsificaron:**

| Defecto reintroducido | Reprueba |
|---|---|
| Sin `@lru_cache` | `test_la_dependencia_es_un_singleton` y la del endpoint |
| Sin distinguir el timeout | `test_una_tabla_lenta_no_se_reporta_como_base_caida` y la de cacheo |

## Lo demás de su nota

- **Silhouette de ML-03**: ya no hace falta esperar a Estefany. El 0.4620526551 está en
  `vault/15_ML_Models/ML03_Comparacion_RISK011_20260910.json` — verificado, y agregado a la
  procedencia de la sección.
- **Ficha de ML-01**: confirmó el problema. Hay que pedirle a Carlos Mayorga el PR con
  **MAE 0.141458 y RMSE 0.436326**.
- **Guarda de `--con-shap`**: confirmada, pero **va en el PR de `DEC-026`**, no en éste — toca
  `src/modelos/publicar_gold.py` y este PR es de `US-601`.
- **Atribución**: el hallazgo del SHAP fue de **Imanol**, no de Christian. Se le hace notar.

## Bloqueantes

- Ninguno técnico. Edgar mergeará con `--admin` dejando escrita la excepción de alcance.
