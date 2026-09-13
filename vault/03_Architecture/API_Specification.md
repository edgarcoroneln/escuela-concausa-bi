---
id: DOC-APISPEC
title: "API Specification — FARO"
owner: "Karla Alejandra Monter Benitez"
status: in_review
version: "1.4"
source_of_truth: true
traces_up: ["REQ-004", "vault/03_Architecture/Data_Model"]
traces_down: ["US-401", "US-402", "US-403", "US-404", "US-405", "US-411", "US-412", "US-415", "US-416", "US-305"]
last_reviewed: "2026-09-12"
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

**`/version` publica los cortes del nivel de atención (2026-09-11, US-621).** `VersionOut.cortes_atencion`
trae `alta` (0.50, `DEC-019`), `media` (0.30) y `ancla_calibracion` (0.60, `DEC-006`). Son
**definiciones, no datos**: cambian con una decisión, no con el Gold, y por eso viajan en un endpoint
público — el front necesita etiquetar **antes** de iniciar sesión. Existen en el contrato porque las
dos constantes viven en capas distintas del repo (la línea de alerta en la API, la matrícula estable
en `src/modelos/riesgo.py`, alcance de C3) y **teclearlas en el front repetiría `BUG-058`**.
`ancla_calibracion` **no es un corte de etiqueta**: se expone para que el glosario de la UI pueda
explicar por qué DB-09 dice `media` donde el front dice *atención alta*, sin escribir el 0.60 a mano.

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

**Los seis drivers y la comparación de matrícula en `EscuelaOut` (2026-09-12, US-621).** `d1`..`d6`,
`indice_completitud_drivers`, `matricula_ciclo_anterior` y `variacion_matricula_alumnos` **suben del
detalle al listado**. Salen de `gold.fact_escuela_ciclo`, que el listado ya tiene unida, así que **no agregan
ninguna consulta**; siguen en el detalle, heredados de `EscuelaOut`.

- **La matriz de drivers y el mapa se llenan con UNA petición**, no una por escuela.
- `indice_completitud_drivers` pasa a **opcional**, y es deliberado: era obligatorio en el detalle, y
  `BUG-077` mostró lo que cuesta — un nulo en una fila reventaba la página completa. En el listado el
  radio de daño es mayor.
- **`null` es SIN_DATO, nunca cero** (CLAUDE.md §4): D5 es regional y D6 cubre ~80 zonas urbanas, así
  que el hueco es el caso **normal**. Un `0.0` afirmaría que ese driver no influyó (`BUG-055`).
- **`variacion_matricula_alumnos` son alumnos, no un porcentaje — y por eso lo dice el nombre.**
  Es `matricula_total - matricula_ciclo_anterior` tal como lo materializa `gold.fact_escuela_ciclo`
  (rango observado −24 a 24), mientras que **`KpisOut.variacion_matricula` es una razón** en [−1, 1]
  (−0.00496 = −0.496 %). Dos unidades con el mismo nombre en el mismo contrato es exactamente el hueco
  de `BUG-031`: la especificación del cubo asumió que la columna ya era una razón y **seis tableros
  pintaron −54.5 % donde el valor real era −0.19 %** (factor 287). Ahí la unidad estaba documentada y
  aun así se asumió mal; el nombre es la única defensa que no se puede dejar de leer. Hallado por Edgar
  (QA) al revisar el PR, antes de que el campo llegara a `main`.
  **Para el porcentaje por escuela:** `matricula_total / matricula_ciclo_anterior - 1`, con guarda de
  denominador cero. La API **no** lo deriva a propósito: el agregado correcto es razón de sumas, no
  promedio de razones, y publicar un porcentaje por escuela invita justo a promediarlo (`BUG-031` otra vez).
- **`matricula_ciclo_anterior` / `variacion_matricula_alumnos` NO son una serie histórica.** Son dos puntos:
  con ellos se dibuja un **cambio**, no una tendencia, y así deben presentarse. Es lo más cercano que
  existe hoy — `/series` sigue fuera de alcance (ver abajo) y la gráfica de `US-212` vivía en un cubo
  de Superset, retirado por `ADR-012`. `fact` ya materializaba las dos columnas (`BUG-031`).
  `matricula_ciclo_anterior` es `null` en el primer ciclo materializado de una escuela, y entonces
  `variacion_matricula_alumnos` no significa nada.
- Fijado por `tests/test_api_contract.py::test_escuelas_listado_trae_los_seis_drivers`,
  `::test_escuelas_listado_trae_la_comparacion_con_el_ciclo_anterior` y
  `::test_la_variacion_por_escuela_y_la_de_kpis_no_comparten_nombre` — esta última falla si el nombre
  ambiguo vuelve al contrato **o** si el valor deja de ser la diferencia en alumnos.

**`latitud` y `longitud` en `EscuelaOut` (2026-09-11, US-621 — mapa de riesgo del frontend):** las
coordenadas **suben del detalle al listado**. Antes, pintar los 7 casos del storytelling costaba 7
llamadas a `/escuelas/{cct}`, y el mapa de una entidad completa, una por escuela. `dim_escuela` ya las
tiene y el listado ya hace ese JOIN, así que **no agrega ninguna consulta**. Siguen en el detalle: se
heredan de `EscuelaOut`, no se movieron. `None` es `SIN_DATO` real —hay CCT sin georreferencia— y el
cliente debe **omitir** esas escuelas del mapa, nunca dibujarlas en el `(0, 0)`. Fijado por
`tests/test_api_contract.py::test_escuelas_listado_trae_coordenadas`.

**`cve_ent`/`nombre_entidad` son `null` cuando no hay dato, no un 500 (2026-09-12).** Al declararlos
obligatorios, una sola fila de `gold.dim_municipio` con la entidad en NULL reventaba la validación de
salida y `/municipios` respondía **500 para la página completa**: un hueco en una fila tumbaba el
listado entero. Es la regla de cobertura parcial del proyecto — donde no hay dato se declara `null`,
igual que `poblacion`, `indice_rezago_social` y `pobreza_pct`, y el cliente pinta el municipio sin la
etiqueta de entidad en vez de quedarse sin tabla. Las claves **siempre están presentes**: el hueco se
declara, no se omite. Fijado por `tests/test_api_contract.py::test_un_municipio_sin_entidad_degrada_a_sin_dato`.

**`cve_ent` y `nombre_entidad` en `MunicipioOut` (2026-09-11, US-621 — pedido de Diana Alvarez):**
la consulta ya los traía (`select(dim_municipio)` devuelve la fila completa), pero el contrato no los
declaraba, así que el cliente tenía que mantener su propio mapa de 4 claves a nombre de entidad, o
pintar `"09"` en una etiqueta. Viajan **en la lista y en el detalle**: solo en el detalle costarían
una petición por fila. Es **aditivo** — ningún cliente existente cambia — y también se puede ordenar
por ellos. Fijado por `tests/test_api_contract.py::test_municipio_trae_la_entidad_y_su_clave`.

**Ordenamiento (Decisión 3 de US-411, Karla Monter, 2026-08-20 — avisado a C2/C3):**
- `order_by` es opcional; si se omite, el orden es el natural de la consulta (no garantizado
  entre llamadas). `order` es `asc` (por defecto) o `desc`. Un `order_by` fuera de la whitelist
  responde `422` (Pydantic `Literal`, no se acepta texto libre → nunca hay SQL inyectado por este
  parámetro).
- `/escuelas` acepta `order_by ∈ {cct, nombre, matricula_total, indice_riesgo}`.
- `/municipios` acepta `order_by ∈ {cve_mun, nombre_municipio, cve_ent, nombre_entidad, poblacion,
  indice_rezago_social, pobreza_pct}`.
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
- **`prioridad`:** `"alta" | "media" | "baja"` de `gold.recomendaciones`. Es **procedencia auditable
  de Gold** y la paridad con la columna que muestra DB-09.
  > **El frontend NO etiqueta con este campo.** La etiqueta de producto es el **nivel de atención**
  > (`DEC-023`), que el front calcula desde `indice_riesgo` con los cortes de `/version`
  > (`cortes_atencion`). El paquete de UX lo dice literal: a esa etiqueta *"no se le dice prioridad …
  > esa palabra nombra una columna de Gold que usa otro corte y que el front no consume"*
  > (`00_Storytelling_Scope.md` §5.3.bis).
  >
  > **Por qué difieren hoy:** `publicar_gold.prioridad_de_riesgo()` llama `alta` solo desde el **ancla
  > de la sigmoide** (0.60, calibración de `DEC-006`) y el máximo que ML-01 predice sobre el Gold real
  > es **0.5717**, así que **ninguna de las 45,276 filas es `alta`** y la tarjeta de DB-09 lee 0
  > (`BUG-063`). **`DEC-026`** alinea la columna a la línea de alerta (0.50) y republica Gold; hasta
  > que eso corra, este campo dirá `media` donde el front dice *atención alta*. El cambio es de C3
  > (`src/modelos/publicar_gold.py:197`) y **no altera este contrato**.
  >
  > Es `StrictStr | None`, no un `Literal`: el valor lo escribe C3 en Gold, y uno inesperado debe
  > poder leerse y verse, no reventar la lectura con un 500. Sin fila de recomendación viaja `None`,
  > mismo criterio `SIN_DATO` que `cluster`.
- **`/predicciones/{cct}/explicacion` sirve contribuciones SHAP reales** desde el 2026-09-05
  (`BUG-053` cerrado). Lee `gold.recomendaciones.shap_d1..shap_d6`, que persiste `publicar_gold.py`
  a partir de `entrenar_ml02.explicar_driver` (C3). **Reutiliza la misma fila** que
  `/predicciones/{cct}` en vez de hacer una consulta propia: hereda el cache TTL y la traducción a
  503 de US-416, y hace imposible que la explicación se desincronice del `driver_dominante` que
  dice explicar. Acepta `?ciclo` igual que la ruta de predicción — sin él tendría que asumir un
  ciclo, que es el default silencioso que causó `BUG-044`.
  > **`null` es SIN_DATO, no cero.** Un driver sin contribución calculable viaja como `null`;
  > colapsarlo a `0.0` afirmaría que ese driver **no contribuyó** al riesgo, que es una afirmación
  > falsa sobre la causa (`BUG-055`). Las seis claves están siempre presentes: el hueco se declara,
  > no se omite. Aplica sobre todo a **D5** (agua, regional) y **D6** (aire, ~80 zonas urbanas),
  > donde el hueco es el caso normal. Quien persista contribuciones escribe `NULL`, nunca `0`.
- No se calcula SHAP por petición y no se va a hacer: `shap` no está en la imagen de la API y
  `KernelExplainer` tarda segundos por fila, incompatible con el `statement_timeout` de US-416. Es
  un job batch por diseño.
- **Un driver sin dato viaja como `None` (SIN_DATO), nunca como `0.0`.** Las seis claves `D1`..`D6`
  están siempre presentes -- el hueco se **declara**, no se omite. Esto no es cosmético: D5 (estrés
  hídrico) es regional y D6 (aire) cubre ~80 zonas urbanas, así que el hueco es el caso **normal**.
  Responder `0.0` afirmaría "este driver no influyó" donde en realidad no se sabe, contradiciendo la
  regla de cobertura parcial del proyecto y a `indice_completitud_drivers`, que sí marcan `SIN_DATO`.
  Con SHAP real la distinción pesa más: *"no influyó"* y *"no lo sabemos"* son respuestas distintas a
  la pregunta que el proyecto existe para responder. Quien persista las contribuciones (C3) debe
  escribir **nulos**, no ceros. Fijado por `tests/test_explicacion_shap.py`.
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
| POST | `/agente/consulta/stream` | ciudadano | `AgenteConsultaIn` | `text/event-stream` (SSE) | 200, 401, 422 |

- El agente responde en lenguaje natural sobre Gold y devuelve la consulta generada para auditoría.
  **Nunca** ejecuta escritura/borrado; rechaza preguntas fuera de alcance (`fuera_de_alcance: true`).

#### `/agente/consulta/stream` — la respuesta por Server-Sent Events (US-305, Fase 3, 2026-09-11)

Mismos guardarraíles, mismo RBAC y **mismo cuerpo** (`contexto`, `historial`) que `/consulta`. Lo
único que cambia es cómo viaja la salida: el SQL se genera y valida completo antes de emitir nada,
y solo la **redacción final** se transmite según la produce el LLM.

| Evento | Cuántas veces | `data` |
|---|---|---|
| `meta` | una, al inicio | `{"sql_generado": str \| null, "fuera_de_alcance": bool}` — los campos de `AgenteRespuestaOut` |
| `fragmento` | una o más | `{"texto": str}` — concatenados en orden forman la respuesta |
| `fin` | una, al final | `{}` |

- **Siempre llegan los tres**, también si algo falla a medio camino: el fallo se convierte en un
  `fragmento` con el mensaje genérico y el `fin` llega igual. El cliente nunca queda esperando.
- Ningún evento lleva trazas, prompts ni SQL crudo de error.
- Un `\n` dentro del texto viaja escapado en el JSON del `data`, así que no puede falsificar un evento.
- Cabeceras: `Cache-Control: no-cache` y `X-Accel-Buffering: no` (nginx no acumula la respuesta).
- **Con sesión por cookie** (`ADR-012`), el cliente usa `fetch()` con `credentials: "same-origin"`
  y lee el cuerpo como stream. `EventSource` no sirve aquí porque solo hace `GET`.
- Fijado por `tests/test_agente_endpoint.py` (sección Fase 3).

**Degradación distinguible y observabilidad (Fase 4, 2026-09-11 — Karla Monter, C4).** Aplica a
`/consulta` **y** a `/consulta/stream`. Hay **dos** mensajes genéricos, no uno:

| Situación | Mensaje | Por qué |
|---|---|---|
| Una colaboración **no está configurada** (sin `ANTHROPIC_API_KEY`, sin DSN read-only) | *"El agente no está disponible en este entorno todavía…"* | No hay nada que reintentar: es la configuración esperada de CI/local |
| Está configurada y **falló en ejecución** (timeout, red, SQL rechazado) | *"No se pudo completar la consulta en este momento. Vuelve a intentarlo…"* | Reintentar sí sirve; decir "no disponible" sería información falsa |
| Falló **con fragmentos ya transmitidos** (solo stream) | se **conserva el texto parcial** y se agrega *"[…] La respuesta quedó incompleta…"* | Mandar el mensaje completo borraría de la pantalla lo que la persona ya leía |

Ninguno de los dos mensajes cambia según el error concreto, así que **la distinción no filtra
detalle interno**. Los fallos se registran con `logging` estructurado (`extra`: etapa, tipo de
excepción, si estaba configurado), con traza solo cuando sí lo estaba — un incidente, no la
degradación esperada. **Nunca se registra la pregunta ni el contexto** (privacidad por diseño).

#### `contexto` — preguntas de seguimiento (US-305, 2026-09-08)

`AgenteConsultaIn` acepta un `contexto` **opcional y retrocompatible**: un cuerpo sin él se comporta
exactamente como antes. Existe para que *"¿y las recomendaciones para **esas** escuelas?"* pueda
resolverse sin que el LLM invente CCTs.

```json
{
  "pregunta": "¿cuáles son las recomendaciones para esas escuelas?",
  "contexto": {
    "ciclo": "2024-2025",
    "ccts": ["19DES0007C"],
    "filtros": {"entidad": "19"},
    "resumen": "Se identificaron 7 escuelas en riesgo"
  }
}
```

> **El contexto lo escribe el cliente: es entrada, no estado de confianza.** `/agente/consulta` es
> público bajo `require_lectura`, así que cualquiera puede mandar lo que quiera ahí, y cada valor
> entra **literalmente** al prompt del sistema. El contrato es la frontera:
>
> | Campo | Regla | Por qué |
> |---|---|---|
> | *(cualquier otro)* | `extra="forbid"` → 422 | Un `sql` o `rol` en el contexto se rechaza; **no hay puerta para SQL del frontend** |
> | `ccts` | `^[0-9A-Z]{10}$`, máx. 200 | Sin comillas ni saltos de línea que alteren el prompt |
> | `ciclo` | `^\d{4}-\d{4}$` | — |
> | `filtros` | máx. 10, 100 chars, sin caracteres de control | Se interpolan en el prompt |
> | `resumen` | máx. 300 chars, sin caracteres de control | Texto libre: un `\n` falsificaría el bloque de contexto |
>
> No se valida que los CCT **existan** — eso lo decide Gold, no el contrato. Y nada de esto
> sustituye a los guardarraíles de C3 (solo `SELECT`/`WITH` sobre Gold, `LIMIT 1000`): es la capa
> de antes. Fijado por `tests/test_agente_contexto.py`.

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
class CortesAtencionOut(BaseModel):
    # Cortes del nivel de atención (DEC-023). Definiciones, no datos: el front los lee en vez de
    # teclearlos, porque las dos constantes viven en capas distintas del repo (BUG-058).
    alta: StrictFloat               # indice_riesgo >= alta  => atención alta (0.50, DEC-019)
    media: StrictFloat              # >= media y < alta      => media (0.30)
    ancla_calibracion: StrictFloat  # 0.60 (DEC-006) -- NO es corte de etiqueta

class VersionOut(BaseModel):
    api: str = "v1"
    commit: StrictStr
    cortes_atencion: CortesAtencionOut | None = None   # 2026-09-11, US-621
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
    # Subidas del detalle al listado el 2026-09-11 (US-621, mapa del frontend). None => SIN_DATO.
    latitud: float | None
    longitud: float | None
    # Subidos el 2026-09-12 (US-621): matriz de drivers y mapa con UNA petición. None => SIN_DATO.
    d1: float | None; d2: float | None; d3: float | None
    d4: float | None; d5: float | None; d6: float | None
    indice_completitud_drivers: float | None = Field(default=None, ge=0, le=1)
    # Dos puntos, no una serie: con ellos se dibuja un cambio, no una tendencia (BUG-031).
    matricula_ciclo_anterior: StrictInt | None = Field(default=None, ge=0)
    # ALUMNOS ABSOLUTOS, y la unidad va en el nombre: KpisOut.variacion_matricula es una razón.
    variacion_matricula_alumnos: float | None = None

class EscuelaDetalleOut(EscuelaOut):
    # Desde 2026-09-12 solo agrega `sostenimiento` y `es_estimado_por_grupo`: drivers, completitud y
    # comparación de matrícula se heredan de EscuelaOut (están en el listado).
    sostenimiento: StrictStr
    es_estimado_por_grupo: bool | None        # DEC-008: indice_riesgo repartido a nivel grupo

class MunicipioOut(BaseModel):
    cve_mun: StrictStr = Field(min_length=5, max_length=5)
    nombre_municipio: StrictStr
    # Agregados 2026-09-11 (US-621): la consulta ya los traía; el contrato no los declaraba.
    # Opcionales desde 2026-09-12: `None` es SIN_DATO, no un 500 que tumba la página completa.
    cve_ent: StrictStr | None = Field(default=None, min_length=2, max_length=2)
    nombre_entidad: StrictStr | None = None
    poblacion: StrictInt = Field(ge=0)
    indice_rezago_social: float | None
    pobreza_pct: float | None

class KpisOut(BaseModel):
    matricula_total: StrictInt
    variacion_matricula: StrictFloat = Field(ge=-1, le=1)   # RAZÓN, no alumnos (BUG-031)
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
    # "alta" | "media" | "baja" (2026-09-11). Sale del ANCLA 0.60, no de la línea de alerta 0.50.
    prioridad: StrictStr | None = None
    mlflow_run_id: StrictStr
class PrediccionBatchIn(BaseModel):
    ccts: list[StrictStr] = Field(min_length=1, max_length=1000)
    id_ciclo: StrictStr
class ExplicacionSHAPOut(BaseModel):
    cct: StrictStr
    driver_dominante: StrictStr
    contribuciones: dict[str, float | None]           # None = SIN_DATO, nunca 0.0 de relleno

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
