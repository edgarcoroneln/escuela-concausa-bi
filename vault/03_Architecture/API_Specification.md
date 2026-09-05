---
id: DOC-APISPEC
title: "API Specification — FARO"
owner: "Karla Alejandra Monter Benitez"
status: in_review
version: "1.1"
source_of_truth: true
traces_up: ["REQ-004", "vault/03_Architecture/Data_Model"]
traces_down: ["US-401", "US-402", "US-403", "US-404", "US-405", "US-411", "US-412", "US-415", "US-416"]
last_reviewed: "2026-09-03"
tags: [architecture, api, contract, fastapi, oauth2]
---

# API Specification — FARO

> **Contrato de la API** (OpenAPI). Se publica en la **Semana 1** para **desbloquear a las Células 2 y
> 3**: pueden construir dashboards y consumir modelos **contra mocks** de este contrato sin esperar a
> que la API exista. Implementa **REQ-004** ([[vault/02_Requirements/Requirements_Detailed]]); los datos y
> tipos derivan de [[vault/03_Architecture/Data_Model]].
> → [[vault/03_Architecture/_index]] · [[vault/01_Product/PRD]]
>
> **Regla de oro:** este documento es la fuente de verdad del contrato. Cambiar una ruta o un modelo
> = PR con aviso a C2 y C3. Nunca romper el contrato en silencio.

---

## 1. Principios

- **REST sobre JSON.** Recursos en plural (`/escuelas`, `/municipios`), sustantivos, no verbos.
- **Versionado en la ruta:** todo bajo **`/api/v1`**. Un cambio incompatible abre `/api/v2`.
- **Framework:** FastAPI; **validación de entrada y salida con Pydantic**; OpenAPI autogenerado en
  `/api/v1/docs` y `/api/v1/openapi.json` (este último es el que consumen los mocks).
- **Formato de error uniforme** (ver §5); **nunca** se filtran trazas ni detalles internos.
- **Paginación** por *offset* en las listas: parámetros `page` (≥1, def. 1) y `size` (1–100, def. 50);
  la respuesta es un sobre `Page[T]` con `items`, `total`, `page`, `size`.
- **Idempotencia y solo lectura:** todos los `GET` son de solo lectura; el agente y los endpoints de
  datos **nunca** ejecutan `DELETE`/`UPDATE`/`DROP`.
- **Alcance:** los datos expuestos son los de Gold, acotados a `SCOPE_ENTIDADES` (CDMX, Edomex, Nuevo
  León, Jalisco). Fuera de alcance → lista vacía o 404, nunca datos de otra entidad.
- **Zona horaria** UTC (ISO-8601) en todos los timestamps.

---

## 2. Autenticación y autorización

### 2.1 Flujo OAuth2 con Google + JWT
1. El cliente inicia sesión con **Google OAuth2** (`GET /api/v1/auth/login` → redirección; callback en
   `GET /api/v1/auth/callback`).
2. La API valida la identidad y emite dos JWT propios:
   - **access token** — vida corta (**15 min**), viaja en `Authorization: Bearer <token>`.
   - **refresh token** — vida larga (**7 días**), se canjea en `POST /api/v1/auth/refresh`.
3. El access token lleva los *claims* `sub` (usuario), `role` (`ciudadano`|`analista`) y `exp`.
4. Al expirar el access token, el cliente usa el refresh token para obtener uno nuevo sin re-login.

**Verificación de la identidad (cerrada en S5, US-402).** `/auth/callback` no confía en el `code`:
lo canjea en el *token endpoint* de Google y **verifica el `id_token`** — firma `RS256` contra la
llave del JWKS público que corresponde al `kid`, `aud` == `GOOGLE_CLIENT_ID`, `iss` de Google y `exp`
vigente — y además exige `email_verified == true`, porque el rol se resuelve por correo. La lista de
algoritmos se pasa explícita: nunca se confía en el `alg` que traiga el token.

### 2.1.1 `state` anti-CSRF del callback

`/auth/login` genera un `state` **firmado** (JWT propio de 10 min con un `nonce` aleatorio), lo manda
a Google en la URL y guarda el mismo valor en la cookie `faro_oauth_state` (`HttpOnly`, `Secure`
fuera de local, `SameSite=Lax`, un solo uso). `/auth/callback` exige que el parámetro `state` **y** la
cookie existan y coincidan, y que el token sea válido y esté vigente; si no, responde **401**. Un
tercero puede provocar la llamada al callback, pero no puede leer ni fabricar la cookie.

Se eligió un `state` firmado, y no uno guardado en memoria del servidor, porque Cloud Run corre
varias instancias sin estado compartido: un `state` en RAM se perdería entre la ida y la vuelta del
navegador.

> **Cambio de contrato para los clientes:** un `GET /auth/callback` sin `state` (o con uno que no
> case con la cookie) ahora devuelve **401**, no 200. El flujo correcto siempre entra por
> `/auth/login`; no se debe llamar al callback a mano.

### 2.1.2 Puente al frontend: código de un solo uso (US-405)

FARO Web no puede leer cookies del navegador (limitación de Streamlit), y mandarle el token por la
query string dejaría la credencial en el historial, en los logs del proxy y en el `Referer`. Por eso:

1. El front llama a `/auth/login?redirect=<su URL>`. El destino se valida contra la **allowlist**
   `FRONTEND_REDIRECT_URIS` (comparación **exacta**, no por prefijo) y viaja **dentro del `state`
   firmado**, así que Google lo devuelve intacto y nadie puede alterarlo.
2. `/auth/callback` guarda la identidad verificada, emite un **código opaco de un solo uso** (60 s) y
   responde **302** a `<front>?code_faro=<código>`. **Por la URL nunca viaja un token.**
3. El servidor del front canjea el código en `POST /auth/exchange` y recibe ahí el `TokenPair`.

Del código solo se almacena su SHA-256, el canje es atómico y el rol se **re-resuelve** al canjear
con la política vigente. Sin `redirect`, `/auth/callback` sigue devolviendo el `TokenPair` como JSON
(clientes que no son navegador). Detalle y alternativas descartadas en
[[vault/03_Architecture/ADRs/ADR-010-puente-oauth-frontend|ADR-010]].

### 2.2 Matriz RBAC (los 2 roles del PRD)

| Recurso / acción | `ciudadano` (estándar) | `analista` (admin) |
|---|---|---|
| `/health`, `/version` | ✅ (público, sin token) | ✅ |
| `/auth/*` | ✅ | ✅ |
| Lectura `/escuelas`, `/municipios`, `/kpis` | ✅ | ✅ |
| `/predicciones/{cct}` (riesgo y driver por escuela) | ✅ (básica) | ✅ |
| `/agente/consulta` | ✅ | ✅ |
| `/predicciones/*` avanzada (batch, explicación) | ⚠️ ✅ **en el código** | ✅ |
| `/admin/pipeline/run` (relanzar pipeline) | ❌ | ✅ |
| `/admin/export` (datos en bruto) | ❌ | ✅ |
| `/admin/metrics` (métricas internas) | ❌ | ✅ |

> ⚠️ **Discrepancia conocida, resuelta a favor del código (2026-09-05, Christian Ruiz, TL C4).**
> La fila marcada arriba describía una intención que **nunca se implementó**. El router de
> predicciones se monta con `require_lectura` en `src/api/v1/__init__.py`, igual que `gold` y
> `agente`: las tres rutas de `/predicciones/*` son públicas con `AUTH_LECTURA_PUBLICA` encendido y
> aceptan **cualquier rol** con él apagado. **Ninguna exige `analista` ni devuelve 403.**
>
> Se documenta la realidad en vez de cambiar el enforcement a dos días del *code freeze*: restringir
> ahora rompería a cualquier consumidor de C2/C3 que llame estas rutas como `ciudadano`, y es una
> decisión de producto, no una corrección de documentación. Hacerlo después es una línea en
> `v1/__init__.py`. El estado real quedó fijado por pruebas en `tests/test_explicacion_shap.py`
> (`test_como_ciudadano_da_200` reprueba si alguien restringe sin actualizar este contrato).

### 2.3 Códigos: 401 vs 403
- **401 Unauthorized** — no hay token, está mal formado, o expiró. *"No sé quién eres."*
- **403 Forbidden** — token válido pero el `role` no alcanza para el recurso. *"Sé quién eres, pero no
  puedes."*
- **200 OK** — autenticado y autorizado.

---

## 3. Catálogo de endpoints

> Todas las rutas cuelgan de `/api/v1`. "Rol" = rol mínimo requerido. Todos pueden devolver
> `401` (token inválido) salvo los públicos, y `422` ante entrada inválida.

### 3.1 Salud y versión (públicos)
| Método | Ruta | Rol | Request | Response | Códigos |
|---|---|---|---|---|---|
| GET | `/health` | público | — | `HealthOut` | 200 |
| GET | `/version` | público | — | `VersionOut` | 200 |

### 3.2 Autenticación `/auth/*`
| Método | Ruta | Rol | Request | Response | Códigos |
|---|---|---|---|---|---|
| GET | `/auth/login` | público | `?redirect` (opcional, allowlist) | 302 → Google | 302, 400 |
| GET | `/auth/callback` | público | `?code`, `?state` | `TokenPair`, o 302 al front con `?code_faro` | 200, 302, 401 |
| POST | `/auth/exchange` | público* | `ExchangeIn` | `TokenPair` | 200, 401, 422 |
| POST | `/auth/refresh` | público* | `RefreshIn` | `TokenPair` | 200, 401 |
| GET | `/auth/me` | ciudadano | — | `UserOut` | 200, 401 |

\* requiere un refresh token válido en el cuerpo, no un access token. `/auth/exchange` requiere un
código de un solo uso vigente (§2.1.2); un código usado, expirado o inventado devuelve 401 sin
distinguir entre los casos.

### 3.3 Lectura sobre Gold
| Método | Ruta | Rol | Request | Response | Códigos |
|---|---|---|---|---|---|
| GET | `/escuelas` | ciudadano | `?cve_ent&cve_mun&nivel&ciclo&order_by&order&page&size` | `Page[EscuelaOut]` | 200, 401, 422 |
| GET | `/escuelas/{cct}` | ciudadano | path `cct` | `EscuelaDetalleOut` | 200, 401, 404 |
| GET | `/municipios` | ciudadano | `?cve_ent&ciclo&order_by&order&page&size` | `Page[MunicipioOut]` | 200, 401, 422 |
| GET | `/municipios/{cve_mun}` | ciudadano | path `cve_mun` | `MunicipioOut` | 200, 401, 404 |
| GET | `/kpis` | ciudadano | `?cve_ent&cve_mun&ciclo` | `KpisOut` | 200, 401 |

**`ciclo` por default (BUG-044, Karla Monter, 2026-09-03):** si se omite en `/escuelas`,
`/escuelas/{cct}` y `/kpis`, se usa el **ciclo más reciente materializado** en
`gold.fact_escuela_ciclo`, nunca todos los ciclos a la vez. Antes de esta corrección, omitir
`ciclo` dejaba `fact` sin filtrar: `/escuelas` listaba la misma escuela una vez por ciclo (sin
forma de distinguirlas, `EscuelaOut` no expone `id_ciclo`) y `/kpis.matricula_total` sumaba los ~3
ciclos materializados a la vez (**20.6M en vez de ~7M reales** para las 4 entidades en producción).

> **Ese default es GLOBAL, no por `cve_ent`/`cve_mun`** (ratificado por Christian Ruiz, TL C4,
> 2026-09-05): es el máximo de ciclo en TODA `fact_escuela_ciclo`, no el máximo dentro de la
> entidad o municipio que pida el filtro. Si una entidad todavía no tiene filas para ese ciclo
> global, la respuesta es **lista vacía**, no el último ciclo *disponible para esa entidad*. Es a
> propósito: resolver el ciclo por entidad mostraría matrículas de periodos distintos una junto a
> otra sin ninguna marca que lo distinga, el mismo tipo de número engañoso que BUG-017/BUG-030
> evitan en otras capas. **No es un bug si una entidad rezagada sale vacía sin `ciclo` explícito**
> — es el filtro correcto y hay que pasar `ciclo` explícito para leer su último dato disponible.

**Ordenamiento (Decisión 3 de US-411, Karla Monter, 2026-08-20 — avisado a C2/C3):**
- `order_by` es opcional; si se omite, el orden es el natural de la consulta (no garantizado
  entre llamadas). `order` es `asc` (por defecto) o `desc`. Un `order_by` fuera de la whitelist
  responde `422` (Pydantic `Literal`, no se acepta texto libre → nunca hay SQL inyectado por este
  parámetro).
- `/escuelas` acepta `order_by ∈ {cct, nombre, matricula_total, indice_riesgo}`.
- `/municipios` acepta `order_by ∈ {cve_mun, nombre_municipio, poblacion, indice_rezago_social,
  pobreza_pct}`.
- Los valores `SIN_DATO` (`indice_riesgo`/`indice_rezago_social`/`pobreza_pct` en `None`) siempre
  quedan **al final**, sin importar `asc`/`desc` — nunca se ordenan como si fueran cero.

**`/series` — declarado fuera de alcance de US-411 (Decisión 3, Karla Monter, 2026-08-20 — avisado
a C2/C3):** el sprint plan de US-411 menciona "series" en su objetivo, pero:
1. La única serie de tiempo documentada en el proyecto (matrícula por `cct × ciclo`, KPI-15 /
   AC-002.5 de `vault/12_Roadmap_Sprints/PLAN_MAESTRO.md`) pertenece a **US-212 (Célula 2, Ficha de
   escuela)** y se consume como cubo de Superset (`gold.cubo_escuela_360`), no como endpoint REST.
2. Hoy `gold.fact_escuela_ciclo` solo materializa 2 ciclos (actual + anterior, ver
   `dbt/models/gold/fact_escuela_ciclo.sql`) — no hay una serie real que servir todavía.
3. Ningún consumidor (mocks, dashboards, agente) referencia hoy un endpoint `/series`.

Si en un ciclo futuro hay ≥3 ciclos materializados y un consumidor concreto lo necesita, se abre
como historia nueva sobre `vault/03_Architecture/API_Specification.md` (misma regla de oro: PR + aviso a
C2/C3), no se retoma como pendiente de US-411.

### 3.4 Predicciones (inferencia ML)
| Método | Ruta | Rol | Request | Response | Códigos |
|---|---|---|---|---|---|
| GET | `/predicciones/{cct}` | ciudadano | path `cct`, `?ciclo` | `PrediccionOut` | 200, 401, 404, 503 |
| POST | `/predicciones/batch` | ciudadano | `PrediccionBatchIn` | `Page[PrediccionOut]` | 200, 401, 422, 503 |
| GET | `/predicciones/{cct}/explicacion` | ciudadano | path `cct` | `ExplicacionSHAPOut` | 200, 401, 404 |

- `PrediccionOut` combina **ML-01** (`indice_riesgo`), **ML-02** (`driver_dominante` + recomendación)
  y **ML-03** (`cluster`, `None` mientras ML-03 no exista -- US-321, BUG-010).
- **`/predicciones/{cct}/explicacion` todavía NO devuelve valores SHAP.** Las `contribuciones` salen
  de `mock_data`, no de ningún modelo. La causa no es el endpoint: **no hay fuente que leer**.
  `src/modelos/entrenar_ml02.py::explicar_driver` calcula SHAP con la forma exacta de
  `ExplicacionSHAPOut`, pero no la invoca nadie y `publicar_gold.py` solo escribe
  `gold.predicciones` y `gold.recomendaciones` -- ninguna guarda contribuciones. Calcularlo por
  petición no es opción (`shap` no está en la imagen de la API y `KernelExplainer` tarda segundos
  por fila, incompatible con el `statement_timeout` de US-416). Orden de cierre: **C3 persiste en
  Gold → C4 lee del repositorio → prueba de contrato**; el contrato de respuesta ya está fijado por
  `tests/test_explicacion_shap.py`, así que el cambio será del cuerpo, no de la forma.
- `/predicciones/{cct}` y `/predicciones/batch` leen `gold.predicciones` + `gold.recomendaciones`
  (US-412, cierra BUG-010) vía `RepositorioModelos`; un CCT sin fila en `gold.predicciones` es
  `404`, nunca un valor inventado. `mlflow_run_id` conserva el enlace auditable a la corrida.
  > **Nota de despliegue:** en el despliegue actual las tablas `gold.predicciones` /
  > `gold.recomendaciones` están vacías (la publicación de ML-01 a esa base, US-313, aún no
  > corre), así que **todo CCT devuelve `404` estructurado** hasta esa publicación. La ruta
  > responde correctamente; lo que falta es dato, no código.
- **Cache y degradación (US-416):** las lecturas pasan por un cache TTL en memoria por
  `(cct, id_ciclo)`, compartido entre ambas rutas (`src/api/cache_predicciones.py`). Si Postgres
  no responde dentro del timeout configurado **o el esquema/tabla `gold.*` no existe o es
  inalcanzable**, la respuesta es `503` `service_unavailable` (§5) — nunca un `500` genérico ni
  una predicción a medias (`RepositorioModelosPostgres._con_timeout` traduce cualquier
  `SQLAlchemyError`). El timeout de `/predicciones/batch` es atómico: si falla, falla toda la
  petición, aunque parte de los CCT ya estuvieran en cache.

### 3.5 Agente conversacional `/agente/*`
| Método | Ruta | Rol | Request | Response | Códigos |
|---|---|---|---|---|---|
| POST | `/agente/consulta` | ciudadano | `AgenteConsultaIn` | `AgenteRespuestaOut` | 200, 401, 422 |

- El agente responde en lenguaje natural sobre Gold y devuelve la consulta generada para auditoría.
  **Nunca** ejecuta escritura/borrado; rechaza preguntas fuera de alcance (`fuera_de_alcance: true`).

### 3.6 Administración `/admin/*` (solo `analista`)
| Método | Ruta | Rol | Request | Response | Códigos |
|---|---|---|---|---|---|
| POST | `/admin/pipeline/run` | analista | `PipelineRunIn` | `PipelineRunOut` | 202, 401, 403, 422 |
| GET | `/admin/export` | analista | `?tabla&ciclo&formato` | `ExportOut` (o stream) | 200, 401, 403 |
| GET | `/admin/metrics` | analista | — | `MetricsOut` | 200, 401, 403 |

---

## 4. Modelos Pydantic (request/response)

> Alineados 1:1 con [[vault/03_Architecture/Data_Model]]. Tipos estrictos; `cct` 10 chars, `cve_mun` 5.

```python
from pydantic import BaseModel, Field, StrictStr, StrictInt, StrictFloat
from enum import Enum
from datetime import datetime
from typing import Generic, TypeVar

# ---- infra ----
class Rol(str, Enum):
    ciudadano = "ciudadano"
    analista = "analista"

T = TypeVar("T")
class Page(BaseModel, Generic[T]):
    items: list[T]
    total: StrictInt
    page: StrictInt = Field(ge=1)
    size: StrictInt = Field(ge=1, le=100)

# ---- salud / auth ----
class HealthOut(BaseModel):
    status: str = "ok"
class VersionOut(BaseModel):
    api: str = "v1"
    commit: StrictStr
class TokenPair(BaseModel):
    access_token: StrictStr
    refresh_token: StrictStr
    token_type: str = "bearer"
    expires_in: StrictInt = 900          # 15 min
class RefreshIn(BaseModel):
    refresh_token: StrictStr
class ExchangeIn(BaseModel):
    # Codigo de un solo uso del puente OAuth -> frontend (US-405, ADR-010). Opaco: no transporta
    # identidad, solo apunta a ella en el almacen del servidor.
    code: StrictStr = Field(min_length=16, max_length=256)

class UserOut(BaseModel):
    sub: StrictStr
    email: StrictStr
    role: Rol
    # `name` agregado 2026-09-03 (US-405): nombre para mostrar, del claim `name` del id_token de
    # Google (scope `profile`). OPCIONAL -- default "" cuando el perfil no lo expone. Es solo de
    # presentacion: el rol se resuelve por `email`, nunca por `name`. El front cae a `email` si
    # viene vacio. Acordado entre Christian Ruiz (C4) y Manuel Serrania (C2); avisado a C3.
    name: StrictStr = ""

# ---- lectura sobre Gold ----
# EscuelaOut/EscuelaDetalleOut actualizados 2026-08-20: indice_riesgo/driver_dominante pasan
# a Optional (vienen por LEFT JOIN a gold.predicciones/gold.recomendaciones, Data_Model.md §4.1;
# None => SIN_DATO, nunca inventado). Decisión de Christian Ruiz (Tech Lead C4), avisada a C2/C3.
class EscuelaOut(BaseModel):
    cct: StrictStr = Field(min_length=10, max_length=10)
    nombre: StrictStr
    nivel: StrictStr
    cve_mun: StrictStr = Field(min_length=5, max_length=5)
    matricula_total: StrictInt = Field(ge=0)
    indice_riesgo: StrictFloat | None = Field(None, ge=0, le=1)
    driver_dominante: StrictStr | None       # "D1".."D6"
    tiene_prediccion: bool                    # True si hay fila en gold.predicciones (ML-01)

class EscuelaDetalleOut(EscuelaOut):
    sostenimiento: StrictStr
    latitud: float | None
    longitud: float | None
    indice_completitud_drivers: StrictFloat = Field(ge=0, le=1)
    d1: float | None; d2: float | None; d3: float | None
    d4: float | None; d5: float | None; d6: float | None   # None => SIN_DATO
    es_estimado_por_grupo: bool | None        # DEC-008: indice_riesgo repartido a nivel grupo

class MunicipioOut(BaseModel):
    cve_mun: StrictStr = Field(min_length=5, max_length=5)
    nombre_municipio: StrictStr
    poblacion: StrictInt = Field(ge=0)
    indice_rezago_social: float | None
    pobreza_pct: float | None

class KpisOut(BaseModel):
    matricula_total: StrictInt
    variacion_matricula: StrictFloat
    escuelas_en_riesgo: StrictInt
    indice_completitud_drivers: StrictFloat = Field(ge=0, le=1)

# ---- predicciones ----
class PrediccionOut(BaseModel):
    cct: StrictStr = Field(min_length=10, max_length=10)
    id_ciclo: StrictStr
    indice_riesgo: StrictFloat = Field(ge=0, le=1)   # ML-01
    driver_dominante: StrictStr                       # ML-02
    recomendacion: StrictStr
    cluster: StrictInt | None = None                  # ML-03, None sin productor (BUG-010)
    mlflow_run_id: StrictStr
class PrediccionBatchIn(BaseModel):
    ccts: list[StrictStr] = Field(min_length=1, max_length=1000)
    id_ciclo: StrictStr
class ExplicacionSHAPOut(BaseModel):
    cct: StrictStr
    driver_dominante: StrictStr
    contribuciones: dict[str, float]                  # driver -> valor SHAP

# ---- agente ----
class AgenteConsultaIn(BaseModel):
    pregunta: StrictStr = Field(min_length=3, max_length=500)
class AgenteRespuestaOut(BaseModel):
    respuesta: StrictStr
    sql_generado: StrictStr | None                    # auditable
    fuera_de_alcance: bool = False

# ---- admin ----
class PipelineRunIn(BaseModel):
    dag: StrictStr
    ciclo: StrictStr
class PipelineRunOut(BaseModel):
    run_id: StrictStr
    estado: str = "accepted"
class MetricsOut(BaseModel):
    frescura_por_fuente: dict[str, datetime]
    suites_ge_en_verde: bool
```

---

## 5. Contrato de errores

Estructura **uniforme** en todos los `4xx`/`5xx`; **sin** stack traces ni SQL ni rutas internas:

```python
class ErrorOut(BaseModel):
    error: str        # codigo estable, p.ej. "not_found", "forbidden", "validation_error"
    message: str      # mensaje humano, seguro para el cliente
    request_id: str   # correlacion para soporte (el detalle real vive en logs internos)
```

```json
{ "error": "forbidden", "message": "Tu rol no permite esta operacion.", "request_id": "req_9f2a" }
```

| Código | `error` | Cuándo |
|---|---|---|
| 401 | `unauthorized` | Sin token / inválido / expirado |
| 403 | `forbidden` | Rol insuficiente |
| 404 | `not_found` | CCT/municipio inexistente o fuera de `SCOPE_ENTIDADES` |
| 422 | `validation_error` | Falla la validación Pydantic (formato de entrada) |
| 429 | `rate_limited` | Exceso de peticiones |
| 503 | `service_unavailable` | Gold no disponible para inferencia: timeout de Postgres **o** esquema/tabla `gold.*` ausente o inalcanzable (US-416) |
| 500 | `internal_error` | Error interno (detalle solo en logs, nunca en la respuesta) |

---

## 6. Cómo mockear (desacople de C2 y C3)

El objetivo del contrato en Semana 1 es que **nadie espere a que la API exista**:

1. **Fuente única:** este documento genera `openapi.json`. La Célula 4 publica un
   `api/openapi.v1.json` estable en el repo aunque la implementación aún no exista.
2. **Servidor mock:** levantar un mock desde el OpenAPI, p. ej. `prism mock api/openapi.v1.json`
   (Stoplight Prism) o respuestas de ejemplo en un FastAPI stub. Devuelve payloads que **cumplen los
   modelos Pydantic** de §4.
3. **Fixtures compartidos:** las respuestas de ejemplo usan los fixtures anonimizados (≤500 filas) de
   la Célula 1, para que los números sean coherentes entre mock y real.
4. **Célula 2 (BI):** Superset y el frontend consumen `/escuelas`, `/municipios`, `/kpis` y
   `/predicciones/{cct}` del **mock**; al llegar la API real solo cambian la URL base.
5. **Célula 3 (ML/Agente):** valida el contrato de `/predicciones/*` y `/agente/consulta` contra el
   mock; el `PrediccionOut` es el mismo que producirá su modelo, así que la integración es un *swap*.
6. **Contrato-primero, no código-primero:** cualquier cambio de forma se hace **aquí** y se regenera
   el `openapi.json`; los mocks se actualizan solos. Así C2 y C3 nunca se bloquean por C4.

> **Definición de "desbloqueado":** C2 y C3 pueden construir y probar end-to-end contra el mock antes
> de que exista una sola línea de la implementación de la API.

---

## 7. Contrato interno API ↔ modelos (US-415)

> Este contrato es **interno**: no es parte de la superficie REST del §3 ni del `PrediccionOut`
> público. Define cómo `src/api` traduce entre `gold.features_escuela` (entrada) y las 3 salidas
> crudas de ML-01/02/03 (Célula 3) **antes** de que `/predicciones/*` (US-412) las combine en la
> respuesta pública. Vive en código en `src/api/schemas_ml.py`.

1. **Entrada — `FeaturesEscuela`:** se **reutiliza** el contrato canónico de
   `src/modelos/contrato.py` (dueño Célula 1/3, `Data_Model.md` §5.3); `schemas_ml.py` lo
   reexporta, nunca lo redefine. Evita la divergencia que `Publicacion_Gold.md` §9 ya señala como
   riesgo para el catálogo de recomendaciones.
2. **Salidas crudas por modelo:**
   - `ML01Salida` — `variacion_predicha` (float con signo, sin cota; mismo dominio que
     `target_variacion_matricula`). La conversión a `indice_riesgo` ∈ [0,1] es
     `src/modelos/riesgo.py::indice_riesgo`, capa de presentación de la Célula 3 — este contrato
     no la reimplementa.
   - `ML02Salida` — `driver_dominante` restringido a `Literal["D1"…"D6"]` (nunca texto libre) y
     `probabilidades` opcional por clase.
   - `ML03Salida` — `cluster` (entero ≥ 0).
   - Las 3 llevan `cct`, `id_ciclo` y `mlflow_run_id` propios de su corrida.
3. **`PrediccionModelos`:** combina las 3 salidas de una escuela × ciclo; un `model_validator`
   rechaza el conjunto si no comparten `cct`/`id_ciclo` — mismo principio que el `CHECK` de
   `gold.predicciones` (`Publicacion_Gold.md` §2). Es el insumo directo de `PrediccionOut` (§4);
   `recomendacion` no es salida de ningún modelo, se deriva del catálogo prescriptivo compartido
   con `src/modelos/recomendaciones.py`.

> **Estado de los modelos en MLflow (26-ago-2026):** en el ambiente local, el registry no tiene
> ninguno de los 3 modelos publicados todavía (`ML03_ClusteringEscuelas` en particular no tiene
> aún código de entrenamiento propio — ver `vault/15_ML_Models/_index.md`, US-321 sin entregar). US-412
> implementa el servicio de inferencia contra este contrato con un *fake* inyectable (mismo patrón
> `Depends` que `RepositorioGold` en `repositorio_gold.py`, US-411) mientras los 3 registros no
> estén disponibles, siguiendo la regla de "no bloqueo silencioso" del plan de sprint.
