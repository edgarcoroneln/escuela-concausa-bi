# Plan — Sección "Cómo funciona FARO" (US-225, hotfix para mañana)

## Contexto

Se pide agregar a FARO Web una sección que explique, para quien evalúa el proyecto: los componentes
del backend, el diagrama E-R, cómo se distribuyen y cuántos datos hay, cómo se filtran las capas
bronze/silver/gold, cómo se construyen los cubos, y la memoria técnica (stack). El pedido llegó como
"hotfix para mañana" y en el camino surgieron dos restricciones reales del propio repo que cambian el
diseño:

1. **El contenido ya tiene dueño.** `vault/03_Architecture/Data_Model.md` (Diana Alvarez, C1) ya es
   la fuente canónica del diagrama E-R, el esquema estrella, el diccionario de datos y la lógica de
   capas. La regla 1 del CLAUDE.md prohíbe un segundo archivo canónico sobre el mismo tema, así que
   esta sección **reexpone** ese contenido — no lo reinventa.
2. **No hay stack de React/Angular en el repo** (sin `package.json`, sin Node) y ADR-002 fija
   Streamlit como frontend. Para no atarse a Streamlit y poder migrar a React/Angular después sin
   reescribir lógica, el contenido se sirve por un **endpoint nuevo de la API** (`/api/v1/about/*`,
   JSON) y la página de Streamlit de hoy es solo un consumidor más — el mismo contrato podría
   alimentar un frontend distinto mañana.

Ese endpoint vive en `src/api/v1/`, que es alcance verde de Christian Ruiz (C4), no de Manuel (C2).
El usuario, como Tech Lead de C2, autorizó tocar esa carpeta para este hotfix — la sección
"Coordinación y excepción de alcance" abajo documenta esa excepción tal como el propio repo lo hace
en casos similares (ver comentarios de `ownership.yml`).

## Decisiones ya tomadas (de la conversación)

- Endpoint JSON en la API, no una página Streamlit acoplada (para poder migrar a React/Angular).
- El endpoint **reexpone contenido canónico** de Diana (Data_Model.md) y Christian
  (System_Design.md/API_Specification.md) — no redacta una segunda versión de la arquitectura.
- Las cifras de "cantidad de datos" y "distribución" salen de **queries en vivo** contra
  bronze/silver/gold, con `SIN_DATO` explícito donde falte una tabla o capa — nunca cero ni nulo
  silencioso (regla del proyecto, Data_Model.md §1/§3).
- Secciones extra: **resumen de decisiones (ADRs)** — explícitamente marcado como "sujeto a cambio"
  — y **tarjetas de los 3 modelos ML**, leyendo los Model Cards ya existentes de C3
  (`vault/15_ML_Models/ML0{1,2,3}_Model_Card.md`) en vez de conectar a MLflow en vivo (más rápido y
  sin nueva dependencia para mañana).

## Coordinación y excepción de alcance (bloqueante, hacer HOY)

- **Avisar a Christian Ruiz (C4)** que se va a agregar `src/api/v1/about.py` +
  `src/api/repositorio_about.py` bajo autorización de Manuel (Tech Lead C2) como hotfix; pedirle que
  revise el PR (es su área).
- **Avisar a Edgar Coronel (PM)** — dueño de `vault/_Meta/ownership.yml` — para que agregue la
  excepción (Manuel en amarillo sobre esos dos archivos nuevos, con Christian en `criticos` como
  revisor), igual que ya existe para el caso de Marina con el runbook de Superset. Sin esto, el CI
  (`check_ownership.py`) va a rechazar el PR por "fuera de alcance" aunque el código esté bien.
- **Asignar el ID de historia**: el siguiente libre en el rango de Célula 2 es **US-225** (después de
  US-224); Edgar confirma y da de alta en `vault/02_Requirements/User_Stories.md` +
  `Traceability_Matrix.md`.
- Si alguna de las dos coordinaciones no se resuelve a tiempo, la salida de emergencia es: dejar el
  código listo en la rama y que Christian lo mergee desde la suya, o pedir que Edgar apruebe la
  excepción por escrito para documentarla en el DevLog aunque el PR quede pendiente de revisión.

## Diseño técnico

### 1. Backend — `src/api/v1/about.py` (nuevo router)

Mismo patrón que `gold.py`: `APIRouter`, rutas de solo lectura, inyección de un repositorio por
`Depends`, sin fugar detalle interno en errores (`app.py` ya cubre esto). Registrar en
`src/api/v1/__init__.py` junto a los demás (`api_v1_router.include_router(about.router, ...)`),
público como `health`/`auth` — es documentación del sistema, no dato de escuela — a confirmar con
Christian si prefiere `require_lectura` por consistencia.

Rutas:
- `GET /api/v1/about/arquitectura` — componentes del backend (Airflow, dbt, Great Expectations,
  Postgres, MLflow, FastAPI, ChromaDB, Superset) y su responsabilidad, tomado de CLAUDE.md §4/§5 y
  `System_Design.md` (que hoy es un stub sin tabla de componentes — se usa CLAUDE.md como fuente real
  y se le avisa a Edgar/Christian que `System_Design.md` quedó desactualizado).
- `GET /api/v1/about/modelo-datos` — el diagrama E-R en mermaid y el diccionario de columnas,
  copiados literalmente de `Data_Model.md` §4 y §6 (con comentario en el código apuntando a esas
  secciones como fuente, para que un cambio ahí se note en revisión).
- `GET /api/v1/about/capas` — descripción bronze/silver/gold (Data_Model.md §1-§3) + conteo de filas
  en vivo por tabla conocida (ver repositorio abajo) + nota de qué capas son nacionales vs acotadas a
  `SCOPE_ENTIDADES`.
- `GET /api/v1/about/cubos` — tabla cubo → dashboard → grano de Data_Model.md §4.3.
- `GET /api/v1/about/stack` — memoria técnica (lenguajes, BD, librerías), tomada de CLAUDE.md §5 y
  `requirements/*.txt` reales (no inventar versiones).
- `GET /api/v1/about/decisiones` — lista de ADRs parseada de `vault/03_Architecture/ADRs/_index.md`
  (id, título, estado, fecha) — no se copia el contenido de cada ADR, solo el índice, con nota
  explícita "sujeto a cambio" en la respuesta.
- `GET /api/v1/about/modelos-ml` — para ML-01/02/03: parsear frontmatter + secciones "Propósito" y
  "Métrica Obtenida" de cada `vault/15_ML_Models/ML0#_Model_Card.md`; si un modelo no tiene corrida
  real todavía (como ML-01 hoy, que documenta que sus métricas son de datos sintéticos), esa
  advertencia se propaga tal cual al JSON, no se oculta.

### 2. `src/api/repositorio_about.py` (nuevo, lectura pura)

- Conteo de filas por capa: usa el mismo engine de `src/api/db.py` (`get_engine()`), corre
  `SELECT COUNT(*)` sobre la lista de tablas documentada en Data_Model.md §2-§4. Si una tabla no
  existe todavía (`ProgrammingError`/`OperationalError`), se captura y esa fila responde `SIN_DATO`,
  nunca `0` ni una excepción que tumbe el endpoint completo.
- Helper de frontmatter: parser mínimo (YAML entre los `---`) para leer ADRs y Model Cards sin
  reinventar `vault_lint.py` (que no expone una función reutilizable, solo un script).

### 3. Frontend — `src/frontend/pages/4_Como_Funciona.py` (nuevo) + `src/frontend/about_client.py`

- `about_client.py` sigue el patrón de `prediccion_client.py`/`superset_client.py`: `httpx`, un
  `get: Callable` inyectable para pruebas sin red, dataclasses por sección, propaga `SIN_DATO` como
  `None` explícito.
- La página nueva llama a cada endpoint por separado (una sección puede fallar sin tumbar las demás),
  usa `encabezado()` de `auth.py` igual que las otras páginas, y por ahora es de **lectura pública**
  (no exige rol), salvo que Christian prefiera protegerla.
- Se agrega su link en `app.py` (cuarta tarjeta de "Acceso rápido").
- El diagrama E-R en mermaid se muestra igual que ya resuelve el proyecto un HTML embebido
  (`components.html`, mismo patrón que `1_Dashboards.py`) con la librería `mermaid.js` por CDN, o con
  `st.markdown` si Streamlit ya soporta mermaid en la versión instalada (verificar `streamlit==1.62.0`
  antes de elegir).

## Verificación

- `pytest tests/ -q` — agregar pruebas del repositorio (conteos con tabla inexistente → `SIN_DATO`,
  nunca excepción) y del `about_client.py` (mismo estilo que las pruebas existentes de
  `prediccion_client`, con el `get` fake).
- Levantar `docker compose up -d`, abrir FARO Web, entrar a "Cómo funciona", confirmar que las 6
  secciones cargan con datos reales de Postgres (no mocks) y que si Postgres no tiene una tabla
  todavía, la sección lo dice explícito en vez de mostrar un error crudo o un cero.
- Confirmar con Christian que `/api/v1/about/*` aparece en `api/openapi.v1.json` regenerado.

## Cierre de gobernanza (antes del PR)

- DevLog: `vault/_DevLog/2026-09-09-manuel-serrania-us225-como-funciona.md` (Manuel está autorizado,
  es "comunes").
- Actualizar `vault/02_Requirements/Traceability_Matrix.md` (fila de US-225, apenas Edgar la dé de alta).
- Título del PR: `[Manuel Serrania] - Sección "Cómo funciona" con backend/ER/capas/cubos (US-225) - [sync|CI|DoF|DevLog]`.
- Recordatorio pendiente para el usuario: actualizar el `_index.md` correspondiente si se agrega algún
  artefacto de vault, y confirmar con Edgar el ID definitivo de la historia antes de abrir el PR.
