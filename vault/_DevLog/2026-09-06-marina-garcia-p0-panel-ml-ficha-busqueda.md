---
project: "FARO"
date: "2026-09-06"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sesión: P0 del panel de ML (ficha + búsqueda) y la línea de alerta de DEC-019"
touches: ["US-207", "US-215a", "REQ-002", "BUG-058", "BUG-059", "DEC-006", "DEC-019", "US-526"]
tags: [devlog, frontend, streamlit, ml, celula-2]
---

# DevLog — 2026-09-06 — P0 del panel de ML, y el umbral que era dos números en uno

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/04_UX_Design/Panel_ML_US207]]

## Contexto

Dos encargos el **día del code freeze**. El P0 de Edgar sobre el minuto 3:00–5:00 —el del
diferenciador, que el guion marca **intocable**— y **BUG-058**, la decisión del umbral.

## 1. Lo primero fue arreglar el ambiente, y menos mal

La API local corría `commit: "dev"`, una imagen anterior al fix de **BUG-044**. Se
comportaba así:

- `/escuelas` sin `ciclo` devolvía **145 filas de 42 escuelas** — cada una repetida por ciclo.
- `/escuelas/15DJN0049A` devolvía el ciclo **2022-2023**: matrícula 90 y
  `tiene_prediccion: false`, cuando el vigente da 114 con riesgo 0.7423.

**Estuve a punto de reportarlo como bug de C4.** Lo verifiqué antes: `origin/main` ya trae
el fix en los dos endpoints. Tras reconstruir la imagen, 55 filas, 55 distintas, cero
duplicados, y la ficha con matrícula 114. **Era mi ambiente, no su código.**

Segundo desfase, del mismo tipo: la imagen nueva consulta `gold.recomendaciones.shap_d1..d6`
(BUG-053) y mi Gold local no tenía esas columnas → **503 en todo `/predicciones`**. Se
resolvió con `publicar_gold --desde-gold`. **Quien reconstruya la API sin re-publicar Gold
se va a topar con esto**, y a tres días de la demo conviene saberlo.

## 2. El P0: la ficha y la búsqueda

`src/frontend/catalogo_client.py` (nuevo) + cascada y ficha en `2_Panel_ML.py`.

**La ficha va antes del índice**, que es el arreglo pedido: nombre, nivel, municipio,
entidad, sostenimiento, matrícula y completitud de drivers. Compacta a propósito — la
instrucción fue *"si la ficha se come esa historia, la ficha se recorta, no la historia"*.

**La búsqueda es solo `st.selectbox`, y no por gusto.** Las pruebas direccionan
`app.text_input[0]` y `app.button[0]` **por índice**; un campo o botón nuevo antes del
formulario las rompe en silencio. Se agregó una guarda que fija ese invariante — y se
validó metiendo un `st.button` de más: reprueban **las dos**, la vieja por una razón que no
lo parece y la nueva diciendo exactamente por qué.

### Tres huecos de la API, verificados y resueltos en el cliente

1. **No existe `/entidades` ni `/niveles`.** Se declaran en el cliente. Sin
   **"Media Superior"**, que `1_Dashboards.py` sí ofrece y que **no existe en Gold**: el
   pipeline filtra a preescolar/primaria/secundaria, así que siempre da cero resultados.
2. **Ni `EscuelaOut` ni `EscuelaDetalleOut` traen `cve_ent` ni `nombre_municipio`.** La
   entidad sale de `cve_mun[:2]`; el municipio, del mapa de `/municipios`.
3. **El mapa de municipios se pagina.** Escribí en el docstring que ninguna entidad pasaba
   de 100 y **era falso**: Jalisco y Edomex tienen **125** cada una. Sin paginar, la ficha
   mostraba `15106` en vez de **Toluca**. **Lo encontré mirando la página renderizada, no
   leyendo el código** — y es la clase de defecto que ninguna prueba de contrato habría
   atrapado, porque el cliente "funcionaba".

## 3. BUG-058: el umbral eran dos números en uno

Hasta hoy `UMBRAL_RIESGO = 0.60` servía para dos cosas distintas: **explicar qué significa**
el índice (0.60 ≡ perder 5 %, que es como está calibrada la sigmoide) y **decidir cuándo
enciende** la alerta. Mientras coincidieran no se notaba, pero hacía imposible bajar la
alerta sin parecer que se recalibraba el modelo.

```
ANCLA_SIGMOIDE  = 0.60   calibración, NO cambia
LINEA_DE_ALERTA = 0.50   criterio de negocio, DEC-019
```

**La evidencia del 0.50.** Sobre el Gold real de producción (45,276 escuelas) el máximo que
ML-01 predice es **0.5717 ≈ −4.53 %**: el corte estaba por encima del techo del fenómeno y
el KPI daba 0 **por construcción**. 0.50 ≈ perder **3.4 %**, justo por debajo del **3.7 %**
de deserción real en secundaria — enciende **antes** de que la escuela alcance la norma
nacional, que es lo que significa "temprana". Bajar más diluye: 0.40 marcaría el 26 % del
universo, 0.35 el 55 %. Con 0.50 son **7 escuelas de 45,276**.

### Lo que la descripción de BUG-058 subestimaba

Dice que B1 *"no re-publica Gold"*. **Solo a medias.** `escuelas_en_riesgo` y `en_riesgo`
son **columnas materializadas** por dbt con el `0.6` **hardcodeado en 5 archivos** — no hay
`var`. Los tableros leen esas columnas, no la constante del frontend.

**Riesgo de orden, y es real:** hasta que Diana rematerialice y Luis reimporte, el panel de
ML y los tableros **van a discrepar**. Por eso **no se tocó** el `umbral: 0.6` declarado en
`metrics_db03_db04.yaml`: es metadato, y cambiarlo antes que el dato lo volvería mentira.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Creados:** `src/frontend/catalogo_client.py`, `tests/test_catalogo_client.py`, este DevLog
- **Modificados:** `src/frontend/pages/2_Panel_ML.py`, `src/frontend/prediccion_client.py`,
  `tests/test_prediccion_client.py`, `tests/test_frontend_panel_ml_streamlit.py`
- **Decisiones autónomas:** construir la búsqueda solo con `selectbox` para no romper las
  pruebas por índice; separar el ancla de la línea de alerta en dos constantes en vez de
  mover un solo número; **no** tocar la anotación `umbral` de la capa semántica hasta que
  dbt rematerialice.
- **Correcciones propias:** (1) casi reporto un bug de C4 que era mi imagen vieja;
  (2) afirmé sin verificar que ninguna entidad pasaba de 100 municipios — dos pasan, y el
  fallo era silencioso.

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] 23 casos nuevos; cada guarda validada **reintroduciendo su defecto** (quitar el
      `order_by`, imputar el riesgo nulo a 0.0, tratar el 401 como caída genérica, volver a
      una sola página de municipios, y meter un botón de más)
- [x] Verificado en el navegador contra la API local, no solo con dobles
- [x] `ruff` ✅ · `vault_lint` ✅ · **1050 pruebas** en verde

## Lo que le toca a cada quien (cadena de DEC-019)

| Quién | Qué |
|---|---|
| **Diana Alvarez (C1)** | 3 modelos dbt + 2 tests dbt, y **rematerializar Gold** |
| **Luis Téllez (C5)** | **Re-importar** el Gold nuevo a Cloud SQL |
| **Christian Ruiz (C4)** | `repositorio_gold.py:325` y los docstrings de `:310` y `v1/gold.py:129` |
| **Manuel Serranía (C2)** | `db09_cubo_recomendaciones.sql:62`, `metrics_db01_db02.yaml:161`, `db02_mapa_riesgo.yaml:46`, `superset/README.md:56`, `test_semantic_db01_db02.py` |
| **Edgar Coronel (PM)** | Firmar **DEC-019**, actualizar DEC-006 y los documentos que citan 0.6 |
| **Andrés / Héctor (C3)** | **Nada** — el ancla de la sigmoide no se toca |

## Pendiente, y es criterio de aceptación

**El par de demostración no está elegido.** El guion dice *"el par elegido responde en
producción ese día"* y no nombra ningún CCT. Hay que elegirlo contra producción, con sesión,
y dejarlo escrito — no de palabra.
