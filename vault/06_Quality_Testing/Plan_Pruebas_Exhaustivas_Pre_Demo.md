---
id: TEST-PLAN-PRE-DEMO
title: "Plan de pruebas exhaustivas previo a la demo — 6 al 8 de septiembre"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["REQ-002", "REQ-004", "REQ-005", "US-006", "vault/06_Quality_Testing/Test_Strategy"]
traces_down: ["vault/06_Quality_Testing/QA_Logs/_index", "vault/06_Quality_Testing/Bug_Register"]
last_reviewed: "2026-09-07"
tags: [qa, pruebas, e2e, playwright, pre-demo, freeze]
---

# Plan de pruebas exhaustivas previo a la demo

> **Sugeridas, no restringidas.** Lo de abajo es el piso, no el techo: si alguien encuentra un
> camino que no está listado, lo prueba igual y lo reporta. Lo que **no** se vale es no probar algo
> porque "no venía en la lista".
> → [[vault/06_Quality_Testing/Test_Strategy]] · [[vault/01_Product/Guion_Demo_US006]]

## Por qué existe y qué lo hace distinto

El código está en verde: **1064 pruebas unitarias pasando**. Eso no es lo que califica el miércoles.
Lo que califica es **la aplicación funcionando en la URL pública**, y eso nadie lo ha recorrido
completo con un navegador.

**La URL que se prueba, la única:**

> **https://faro-frontend-526490367142.us-central1.run.app/**

**Regla que ordena todo el plan: se prueba contra producción, no contra local.** Si algo sólo
funciona en local, para efectos de la demo no funciona.

## Antes de empezar: seis cosas que hay que saber o se reportan bugs falsos

> Actualizado el **2026-09-07**. Eran dos; el sistema se movió mucho en 24 horas y cuatro de éstas
> se descubrieron después de escribir la primera versión. **Léelas antes de abrir el navegador.**

**1. La API exige sesión.** Desde `DEC-018` (5-sep), `AUTH_LECTURA_PUBLICA=false`. **Sólo
`/api/v1/health` responde sin token; todo lo demás da 401.** Verificado hoy. Un 401 sin sesión
**no es un bug**: es la postura vigente.

**2. La sesión NO sobrevive a recargar la página ni a abrirla en otra pestaña.** No es un defecto y
**no se puede arreglar** con esta arquitectura: `st.session_state` vive en la sesión del websocket, y
no se puede sostener con una cookie porque la API y el front son hosts distintos bajo `run.app`, que
está en la **Public Suffix List** — el navegador rechaza la cookie. Está documentado en
`src/frontend/auth.py::encabezado()`. Lo que sí se logró es que ese caso se vea como *"Inicia
sesión"* en vez de un 401 crudo. **Recargar y perder la sesión no es un bug; que se vea como un error
crudo, sí.**

**3. `/explicacion` devuelve `SIN_DATO` y está bien.** Tras el `ALTER` de C5 (PR #280) las seis
columnas `shap_d1..shap_d6` **existen** en `gold.recomendaciones` pero están en **`NULL`**, hasta que
C3 repueble el Gold con `publicar_gold.py`. `BUG-053` sigue correctamente en `fixed` — el código lee
las columnas reales; el dato aún no está.

**4. La tarjeta «Recomendaciones de prioridad ALTA» de DB-09 muestra 0.** Ya está registrado como
`BUG-063`: el corte de `prioridad` es 0.60 y el máximo real es 0.5717, así que ninguna de las 45 276
escuelas la alcanza. **No lo vuelvas a levantar**; si lo ves, es el bug conocido.

**5. NADIE corre `superset/sync_semantic_layer.py`.** Regla de ventana hasta después del 9. El
`query_context` que C5 aplicó a mano en 20 charts *timeseries* puede borrarse con un re-sync: el PR
#275 lo persiste por el camino REST, pero el import que corre después manda `"query_context": None`
con `overwrite=true` y **esa interacción no está verificada**. Si crees que necesitas correrlo,
avísale al PO antes.

**6. El KPI-04 debe decir 7, no 0 — y si dice 0, eso es el hallazgo.** La cadena de `DEC-019` **ya
está completa en `main`**: dbt (`>= 0.5` en los cubos), API y frontend con `LINEA_DE_ALERTA = 0.50`,
y modelos con `ANCLA_SIGMOIDE = 0.60` separado. Lo que **no** está verificado es si el **Gold
desplegado** se rematerializó con la línea nueva. **Caso concreto:** si el tablero dice 0 y la API
dice 7 sobre el mismo dato, repórtalo con la hora exacta — es la deuda de re-materialización, no un
defecto de código.

## Reparto

**Siete** personas, siete superficies, sin traslape. **Cada quien prueba lo que no construyó** cuando
se puede: se encuentran más cosas mirando código ajeno.

> **Actualizado el 2026-09-07.** La primera versión repartía cinco superficies y dejaba fuera **el
> chat del agente y el Panel de ML** — que son, respectivamente, el minuto 6:30 y el minuto 3:00–5:00
> del guion, y 0.5 y 1.5 puntos de rúbrica. Se agregan con dueño.

| Persona | Célula | Superficie | Por qué esta persona |
|---|---|---|---|
| **Eloisa González Rubio** | C4 | **API completa**: todas las rutas, estados de auth, contrato contra Swagger | Su rol es pruebas de API |
| **Karla Monter Benitez** | C4 | **Flujos de sesión**: login Google, refresco de token, logout, RBAC 200/401/403 | Construyó endpoints y RBAC: sabe qué debe romperse |
| **Monserrat Miranda** | C2 | **Los 10 tableros**: carga, datos, tabs, filtros cruzados, enlaces de drill-down | Es la dueña del modelado semántico |
| **Oscar Quiroz** | C2 | **Corrección visual**: gráficos, mapas, tarjetas vacías, valores de KPI, contraste | Su rol es gráficos, mapas y KPIs |
| **Diana Alvarez** | C1 | **Coherencia del dato de punta a punta**: que el mismo número diga lo mismo en API, tablero y panel | Es quien conoce Gold |
| **Andrés González Habib** | C3 | **El chat del agente en producción** — `/Chat`. Prioridad máxima: hoy **no funciona bien** | Es su historia (`US-305`) **y su minuto 6:30 en la demo**: aquí la regla de "prueba lo que no construiste" cede, porque el guion exige que él mismo lo corra contra producción ese día |
| **Estefany Hernández Loredo** | C3 | **El Panel de ML** — `/Panel_ML`. Con foco en **por qué ML-03 sale `SIN_DATO`** | No lo construyó (es de C2), y el hallazgo que hay que perseguir es de su historia `US-321` |

## Qué prueba cada quien

### Eloisa — la API, ruta por ruta

- **Todas** las rutas de `/api/v1` contra el Swagger de `/api/v1/docs`: que exista, que el esquema
  de respuesta coincida y que los códigos sean los documentados.
- Los tres estados de cada ruta de datos: **sin token → 401**, **ciudadano → 200 o 403**,
  **analista → 200**.
- Entradas inválidas: `cct` inexistente, `cct` mal formado, ciclo inexistente, parámetros fuera de
  rango, `limit` negativo. **Que no filtre detalles internos en el error** (`CLAUDE.md`).
- `/api/v1/health` y `/api/v1/version`: que `version` diga el commit desplegado y **compararlo con
  `main`**. Si va por detrás, es hallazgo.
- Tiempos de respuesta. Cualquier ruta que tarde más de 3 s en la demo es un riesgo.

### Karla — la sesión, que es lo que más caro sale si falla

- **Login con Google de punta a punta** en producción, con al menos dos cuentas: una en
  `ANALISTA_EMAILS` y una fuera.
- **`BUG-059`, el caso de la demo**: iniciar sesión, **esperar más de 15 minutos**, y volver a usar
  la aplicación. El access token dura 15 min y el refresco es nuevo. **Este es el escenario real del
  miércoles.**
- Cerrar sesión y confirmar que **no queda token vivo**: recargar y ver que pide login.
- **403 en vivo con cuenta de ciudadano** sobre una ruta de analista. Es punto de rúbrica.
- Qué pasa si se abre una página interna **sin haber pasado por el login**.

### Monserrat — los 10 tableros

- Que **los 10 carguen** y que **ninguno salga vacío**. Un tablero vacío en la demo es peor que uno
  ausente.
- **DB-05**, que es el único con tabs: los 6 tabs, que agrupen en horizontal (`US-213`) y que la
  nota de fuente esté arriba.
- **Filtros cruzados y drill-down**: los enlaces `link_db08`, que lleven al destino correcto y con
  el filtro aplicado.
- Que los números del tablero **coincidan con los del bloque de Diana** (ver abajo).
- Los tableros **con la cuenta del evaluador**, no sólo con la propia.

### Oscar — que lo que se ve sea correcto

- Cada gráfico: que **tenga datos**, que los ejes estén etiquetados y que las leyendas no tapen la
  serie.
- **Tarjetas de KPI**: ninguna en "No data" ni en `NaN`. Si una dice 0, confirmar que **es un 0
  verdadero** y no un filtro roto (`BUG-054` fue exactamente eso).
- **Mapas**: que pinten, que no haya municipios sin geometría en blanco sin explicación.
- **Contraste**, en los dos temas: la deuda de `DEC-016` es conocida y no bloquea, pero **cualquier
  elemento que escriba FARO sí debe pasar 4.5:1**.
- Ventana angosta (proyector) y ventana ancha. **Que nada desborde en horizontal.**

### Diana — que el mismo número diga lo mismo en todas partes

Es la prueba más valiosa del plan y la única que nadie más puede hacer.

- **`escuelas_en_riesgo`**: comparar `/api/v1/kpis`, el tablero DB-04 y el panel de ML **en el mismo
  minuto**. Con `DEC-019` a medio mergear, es donde va a aparecer la inconsistencia.
- **`indice_completitud_drivers`**: debe rondar **0.62**. Si dice 0.197, el Gold desplegado es viejo.
- **`SIN_DATO` nunca cuenta como 0**: verificar en al menos un driver con cobertura parcial (D3 o
  D4) y en uno completo (**D5 está 100 % en SIN_DATO**, es el caso extremo).
- **Total de matrícula** por entidad: API contra tablero.
- El **par de demostración** que elija C2: que responda en producción con los valores del guion.

### Andrés — el chat del agente, y es la prioridad de hoy

**Entramos sabiendo que no funciona.** En el recorrido del PO, el chat en producción respondió
*«No se pudo consultar el agente: La sesión no es válida o expiró; inicia sesión nuevamente»* a un
`hola`. No hay que confirmarlo: hay que **explicarlo y cerrarlo**.

Sospecha principal y por dónde empezar: la página se abrió en **pestaña propia**, y por el punto 2 de
arriba eso significa sesión nueva sin token → la API responde **401** y el cliente lo traduce a ese
texto (`src/frontend/agente_client.py:48`). Si es eso, **no es un bug del agente** y el arreglo es de
guion, no de código: no abrir pestañas durante la demo.

Pero hay que descartar las otras tres, en este orden:

1. **Sesión iniciada, misma pestaña, pregunta inmediata.** ¿Responde? Si sí, el 401 era la pestaña.
2. **Los cinco chips, uno por uno, contra producción.** Es lo que el guion exige literalmente:
   *«los dos chips corridos contra producción ese día, con sesión iniciada»*. El de seguridad
   —*«Borra la tabla de predicciones»*— tiene que **rechazarse visiblemente**, no degradar a un
   mensaje genérico.
3. **El caso que nadie ha probado y es el que puede arruinar el minuto 6:30:** `src/api/app.py`
   cablea el LLM **sólo cuando hay configuración**. Si Cloud Run no la tiene, el agente degrada sin
   filtrar detalle — y entonces **el rechazo del chip de seguridad se vuelve indistinguible de un
   "no hay configuración"**. Verifica que el guardarraíl se vea rechazando, no callando.
4. **Sesión de 15 minutos.** Inicia sesión, espera, y vuelve a preguntar. `token_de_acceso()` debe
   refrescar con 120 s de margen (`auth.py`). Si a los 16 minutos da 401, el refresco no está vivo en
   la imagen desplegada y eso **sí es rojo**.

**Es rojo por definición:** el agente vale 0.5 de rúbrica y tiene un minuto propio. Si no responde en
vivo, ese minuto se cae.

### Estefany — el Panel de ML, y la pregunta de ML-03

Recorre `/Panel_ML` con los CCT del par de demostración —`15DPR0920D` y `15DPR2254O`— y con los dos
ejemplos de la página. Que la ficha diga **de qué escuela habla** antes del índice, que la búsqueda
por filtros llegue al CCT sin teclearlo, y que ML-01 y ML-02 den números.

**Y luego lo que de verdad te toca:** el panel imprime

> *«SIN_DATO — ML-03 todavía no tiene productor. `gold.predicciones` no expone la columna `cluster`
> porque US-321 sigue en curso, y el contrato de la API lo devuelve como `null`.»*

Ese texto **no es del todo exacto**, y la parte inexacta es la que importa. Lo que hay en `main`:

- **`src/api/repositorio_modelos.py:115` hace `datos["cluster"] = None`, fijo.** La API **nunca
  consulta** una columna `cluster`; la asigna a mano. Así que aunque la columna existiera, el panel
  seguiría diciendo `SIN_DATO`.
- **`src/modelos/publicar_gold.py` no tiene una sola referencia a `cluster`.** Nadie publica la
  salida de ML-03 a Gold.
- **Y sin embargo `src/modelos/entrenar_ml03.py` existe y sus pruebas pasan** desde el PR #132, que es
  tuyo.

O sea: **el modelo se entrena y su salida no llega a ninguna parte.** Son dos cables sueltos, no un
modelo faltante. Lo que necesito de ti, hoy, es **el diagnóstico escrito** —cuál de los dos falta
primero y cuánto cuesta cada uno—, no el arreglo. Con eso decido si ML-03 entra al miércoles o se
declara como deuda, y `DEC-015` ya dejó abierta esa puerta.

**No lo arregles sin avisarme.** Publicar a Gold a dos días toca las 45 276 filas y hay dos decisiones
(`DEC-019`, `BUG-063`) que dependen de que nada publicado se mueva.

## Cómo levantar tu ambiente local

**Producción da el veredicto; local es el banco de trabajo.** La regla de arriba no cambia: lo que
califica el miércoles es la URL pública. Pero un hallazgo sin ambiente local es un hallazgo que no
puedes diagnosticar ni arreglar — por eso todos levantan el suyo hoy.

### Dos cosas en las que local NO es producción

Léelas o vas a sacar conclusiones falsas:

1. **La postura de auth está invertida.** `.env.example` trae `AUTH_LECTURA_PUBLICA=true`; producción
   corre en `false` desde `SEC-006`/`DEC-018`. En local la lectura es pública y **no vas a ver los
   401 que sí da producción**.
2. **El login con Google no funciona en local.** `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` vienen
   **vacíos** en `.env.example` y no se reparten credenciales. Todo lo que dependa de una sesión real
   —RBAC por rol, refresco de token, el chat autenticado— **sólo se puede verificar contra
   producción**. En local se prueba la lógica, no la sesión.

Cualquier cosa que sólo reproduzcas en local y no en producción, dilo así en tu bitácora.

### El prompt base — lo corre todo el mundo

Ábrelo en Claude Code, **parado en la raíz del repositorio**, y pega esto:

```
Levanta mi ambiente local de FARO para hacer pruebas. Antes de ejecutar nada, lee:
- CLAUDE.md en la raíz
- vault/_Meta/US-521b-guia-ambiente-local.md (la guía oficial)
- vault/06_Quality_Testing/Plan_Pruebas_Exhaustivas_Pre_Demo.md, sección "Antes de empezar"

Luego, en este orden, y enseñándome la salida real de cada paso:

1. Verifica que Docker Desktop esté corriendo y que exista .env (si no existe, cópialo de
   .env.example y dime qué variables quedaron vacías; NO inventes valores ni credenciales).
2. Crea/activa el venv e instala requirements.txt.
3. Levanta la infraestructura: docker compose up -d db api
   (agrega superset y chromadb sólo si mi superficie los necesita; te lo digo abajo).
4. Espera a que los healthchecks estén sanos y compruébalo con docker compose ps.
5. Verifica la API: curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health
   Debe dar 200. Si no, enséñame docker compose logs api --tail 50 y diagnostica.
6. Corre la suite: pytest tests/ -q. Debe dar 1064 passed.

Reglas que no puedes romper:
- Trabajo en mi rama fija dev/{mi-identidad}. No crees ramas, no hagas rebase, nunca commits a main.
- No inventes rutas, comandos, endpoints ni variables de entorno: verifícalos leyendo el archivo.
- No escribas credenciales en ningún archivo ni las imprimas en pantalla.
- Si un paso falla, PÁRATE y enséñame el error. No sigas al siguiente.

Cuando termine, dime en una línea qué quedó arriba y qué no.
```

Puertos, para que sepas a dónde apuntar (todos atados a `127.0.0.1`): **API 8000** · **Postgres 5432**
· **Superset 8088** · **MLflow 5001** · **ChromaDB 8001** · **Airflow 8080**.

**El frontend no tiene servicio en `docker-compose.yml`** — existe `docker/frontend.Dockerfile` pero
no está en el compose. Se levanta a mano:

```bash
FARO_API_BASE_URL=http://localhost:8000 \
FARO_FRONTEND_URL=http://localhost:8501 \
streamlit run src/frontend/app.py
```

### Lo que cada quien agrega al prompt base

| Persona | Añade a tu prompt |
|---|---|
| **Eloisa** | *"Levanta sólo `db` y `api`. Cuando estén sanas, abre `http://localhost:8000/api/v1/docs` y hazme un inventario de todas las rutas con su método y sus códigos documentados, para contrastarlo contra producción."* |
| **Karla** | *"Levanta `db` y `api`. Confírmame el valor de `AUTH_LECTURA_PUBLICA` en mi `.env` y recuérdame que producción corre en `false`. Muéstrame `src/frontend/auth.py::token_de_acceso()` y explícame en qué momento exacto dispara el refresco."* |
| **Monserrat** | *"Levanta `db`, `api` y `superset`. NO ejecutes `superset/sync_semantic_layer.py` bajo ninguna circunstancia — está congelado hasta después del 9-sep. Sólo abre Superset en `http://localhost:8088` y déjalo listo."* |
| **Oscar** | *"Levanta `db`, `api` y `superset`. NO ejecutes `superset/sync_semantic_layer.py`, está congelado. Además, léeme los `alto:` y `ancho:` de `superset/dashboards/db01_ejecutivo.yaml` para contrastarlos con lo que veo en pantalla."* |
| **Diana** | *"Levanta `db` y `api`. Conéctate a Postgres local y dime cuántas filas hay en `gold.predicciones`, `gold.recomendaciones` y `gold.features_escuela`, y cuál es el `max(indice_riesgo)`. Quiero contrastarlo contra producción."* |
| **Andrés** | *"Levanta `db`, `api` y `chromadb`. Necesito el stack del agente completo: confírmame que `limits`, `slowapi`, `chromadb` y `sentence_transformers` quedaron instalados, porque en mi entorno anterior no colectaban `tests/test_agente_endpoint.py` ni `tests/test_agente_wiring_llm.py`. Corre esos dos archivos y enséñame la salida. Después dime si `src/api/app.py` cablea el LLM en mi `.env` local o si degrada por falta de configuración — es exactamente lo que tengo que distinguir en producción."* |
| **Estefany** | *"Levanta `db` y `api`. Luego traza para mí, leyendo el código y sin cambiar nada: (1) qué escribe `src/modelos/entrenar_ml03.py` y dónde lo deja; (2) por qué `src/modelos/publicar_gold.py` no tiene ninguna referencia a `cluster`; (3) por qué `src/api/repositorio_modelos.py:115` asigna `datos[\"cluster\"] = None` en vez de consultar una columna. Quiero saber cuál de los dos cables falta primero y cuánto costaría cada uno. NO modifiques nada: sólo el diagnóstico."* |

## Cómo probar: Playwright

No está en el repo todavía. Se instala **fuera del árbol** para no tocar `requirements/` el día del
freeze:

```bash
python -m venv .venv-qa && source .venv-qa/bin/activate
pip install playwright pytest-playwright && playwright install chromium
```

### Prompt sugerido para el agente

> Copiar tal cual, cambiando **sólo el bloque de "Mi superficie"**.

```text
Eres mi copiloto de QA en un proyecto de BI llamado FARO. Vamos a probar la aplicación
DESPLEGADA, no el código local. Usa Playwright con Chromium.

URLs:
- API:      https://faro-api-eanzfglvyq-uc.a.run.app   (rutas bajo /api/v1)
- Superset: https://faro-superset-eanzfglvyq-uc.a.run.app

Contexto que debes tener antes de reportar nada:
- La API EXIGE sesión de Google desde DEC-018. Sólo /api/v1/health responde sin token.
  Un 401 sin sesión NO es un bug.
- Superset exige login con Google y tiene lista blanca de correos. Si un correo válido
  es rechazado, ESO SÍ es un hallazgo.
- El KPI "escuelas en riesgo" está migrando de umbral 0.60 a 0.50 (DEC-019). Si la API
  y el tablero dan números distintos, repórtalo CON LA HORA.
- La convención del proyecto: SIN_DATO nunca significa cero.

Mi superficie: <<PEGAR AQUÍ LA SECCIÓN DEL PLAN QUE ME TOCA>>

Cómo quiero que trabajes:
1. Antes de cada prueba, dime qué vas a hacer y qué esperas ver. Luego hazlo.
2. NO inicies sesión por mí ni escribas credenciales: cuando haga falta login,
   detente y pídeme que yo lo haga en la ventana.
3. Toma captura de cada hallazgo y guárdala con nombre descriptivo.
4. Verifica antes de afirmar. Si un selector no aparece, dilo; no supongas.
5. Cuando algo falle, dame: qué hiciste, qué esperabas, qué pasó, y si se reproduce
   al repetirlo. Un fallo que no se reproduce se reporta COMO intermitente, no como
   fallo firme.
6. NO ejecutes DELETE, UPDATE, DROP ni ningún POST que modifique datos.
7. Al final, dame un resumen en tabla: caso, resultado, evidencia.

Empieza recorriendo mi superficie de arriba a abajo y detente en el primer hallazgo
para que lo veamos juntos.
```

**Por qué el punto 2:** nadie escribe credenciales en un prompt ni deja que el agente las teclee. El
login lo hace la persona, en su ventana.

**Por qué el punto 5:** esta semana perdimos tiempo con un fallo intermitente reportado como firme
(`BUG-052`). Un fallo de 1 de cada 3 se reporta así, con el conteo.

## Dónde se registran los resultados

**Un archivo por persona**, en `vault/06_Quality_Testing/QA_Logs/`:

```
vault/06_Quality_Testing/QA_Logs/2026-09-0X-{identidad}-qa-pre-demo.md
```

Con frontmatter (`id`, `owner`, `status`, `traces_up`) y **la tabla de resultados**: caso, esperado,
obtenido, evidencia, veredicto. **Y hay que agregar la fila al `_index.md` de la carpeta**, o no
cuenta como archivado.

**No inventes el formato:** copia
[[vault/06_Quality_Testing/QA_Logs/PLANTILLA-qa-log|`QA_Logs/PLANTILLA-qa-log.md`]], renómbrala con tu
identidad y llénala. Trae el frontmatter, las columnas y las tres reglas de cómo escribir un caso.

`vault/06_Quality_Testing/**` es **carpeta común**: cualquiera puede escribir su propio log sin
tocar el de otro.

## Qué hacer con lo que se encuentre

**1. Se levanta el bug en `vault/06_Quality_Testing/Bug_Register.md`.** **Al 2026-09-07 el siguiente
libre es `BUG-064`** — 061 (el frontend de prod sin commitear), 062 (el argmax del driver dominante) y
063 (la prioridad ALTA inalcanzable) ya están tomados. Por `DEC-013`, **un ID no está reservado hasta
que está escrito en `main`** — si dos personas registran a la vez, quien llegue segundo renumera.
**Anúncialo en el canal antes de escribirlo**, que hoy prueban siete personas a la vez.

**2. Se le asigna dueño por superficie, no por quien lo encontró:**

| Si el bug está en… | Va con |
|---|---|
| Rutas, contratos, auth, RBAC | **Christian Ruiz** (TL C4) |
| Tableros, cubos, capa semántica | **Manuel Serranía** (TL C2) |
| Gold, dbt, calidad del dato | **Diana Alvarez** (TL C1) |
| Modelos, predicciones, agente | **Andrés González** (TL C3) |
| Despliegue, Cloud Run, Superset, SSO | **Luis Téllez** (TL C5) |
| No está claro | **Edgar Coronel** (PO), y yo lo enrutó |

**3. Se clasifica por lo que significa para el miércoles, no por severidad técnica:**

- **Rojo — rompe la demo.** Se arregla hoy o se saca del guion. Se avisa al PO **de inmediato**.
- **Ámbar — se ve mal pero la demo sobrevive.** Se registra y se decide con el dueño.
- **Verde — deuda.** Se registra con su medición y se declara. `DEC-016` es el precedente:
  **deuda medida y dicha por nosotros vale más que deuda descubierta por el evaluador.**

**Nada se calla.** Un hallazgo que no se registra reaparece el miércoles frente al profesor.

## Fechas

| Cuándo | Qué |
|---|---|
| **Domingo 6-sep** | Correcciones P0/P1 de `DEC-020` · corte 18:00 |
| **Lunes 7-sep — hoy** | **Cada quien recorre su superficie y levanta lo que encuentre** · ensayo del guion con cronómetro · se arregla lo rojo |
| **Martes 8-sep** | Re-prueba de lo arreglado · **congelamiento real** |
| **Miércoles 9-sep** | Checklist de la mañana del [[vault/01_Product/Guion_Demo_US006]] |
