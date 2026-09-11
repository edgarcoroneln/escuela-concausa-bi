---
id: DOC-FARO-UX-ARCH
title: "UX Architecture — flujo, navegación e interacción"
owner: "Oscar Antonio Quiroz Lázaro"
status: draft
traces_up: ["US-621", "REQ-002", "vault/04_UX_Design/FARO_Storytelling_UX/00_Storytelling_Scope"]
traces_down: ["US-641"]
last_reviewed: "2026-09-10"
tags: [ux, navegacion, interaccion, s7, us-621]
---

# UX Architecture — flujo, navegación e interacción

> Documento de Oscar Antonio Quiroz Lázaro. Fija **cómo se recorre** la experiencia.
> Debe servir como guía directa de implementación para el Equipo 5 (`US-641`), sin que ellos
> tengan que redefinir decisiones de UX.
> → [[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]] ·
> [[vault/04_UX_Design/FARO_Storytelling_UX/00_Storytelling_Scope]]

**Estado:** borrador.

## 1. Mapa de navegación

### Recorrido principal

Login (P0) → Entrada (P1) → Panorama (P2) → Selección de caso (P3) → Expediente (P4) → Conclusión Top 3 (P5) → Exploración (P6)

### Caminos de regreso

| Desde | Acción | Hacia |
|---|---|---|
| P3 Selección | "Volver al panorama" | P2 |
| P4 Expediente | "Regresar a selección" | P3, mostrando el panorama completo de nuevo (no un estado a medias) |
| P4 Expediente | "Ver la conclusión" (avance, no regreso) | P5 |
| P6 Exploración | Logo FARO en la barra superior | P1 en su **estado de visita recurrente** (§2) — no cierra sesión ni finge que la investigación no avanzó |

No existe un botón de regreso de P5 a P4: la conclusión cierra la investigación guiada. Si el usuario
quiere revisar otro caso, el único camino hacia atrás es reiniciar desde el logo (a P1) o avanzar a P6,
que es libre.

### Entrada directa por URL

- **Sin sesión activa:** cualquier ruta interna redirige a Login (P0). Al autenticar, continúa a la
  ruta solicitada si es P4 o P6 (ver el punto siguiente); en cualquier otro caso, entra a P1.
- **Con sesión activa:**
  - P1, P2, P3 y P5 siempre se sirven desde el inicio de su tramo; no dependen de estado previo.
  - **P4 y P6 sí aceptan URL directa** (`/escuela/{cct}` y `/explorador`), porque son las dos pantallas
    con valor de compartir: el caso de una escuela puntual, o el explorador con un filtro aplicado. Si
    el usuario llega así, sin pasar por P2/P3, el expediente se muestra igual, pero "Regresar a
    selección" lo manda a P3 con el panorama completo, para que no quede sin contexto.

### Superficie hermana — "Cómo funciona" (plan §5.bis)

No es una octava pantalla ni entra al recorrido P0–P6: es contenido del Equipo 1 (siete apartados —
arquitectura, modelo-datos, capas, cubos, stack, decisiones, modelos-ml) al que este frente solo le da
identidad y ubicación.

- **Acceso:** un enlace discreto desde P1 (junto a la frase de apoyo, sin competir con el CTA
  principal) y desde cada término del glosario que lo amerite (igual que el enlace a "Pregúntale al
  Asistente"). No hay un tercer punto de entrada.
- **Cómo se muestra:** overlay a pantalla completa sobre la pantalla actual, no una ruta nueva del
  recorrido — igual mecánica que el Asistente FARO (§6): abre encima, no navega.
- **Cómo se vuelve:** cerrar el overlay regresa exactamente a la pantalla y al estado desde donde se
  abrió (misma posición de scroll, mismo caso seleccionado si se abrió desde el expediente vía
  glosario). Nunca reinicia el recorrido ni cuenta como "reinicio" a P1.
- Los bloques `mapa`, `barras` y `diagrama_flujo` (D3) viven en iframes propios con `color-scheme:
  light` forzado por el Equipo 1 — si la identidad de Juan es oscura, esos tres bloques quedan
  claros a propósito dentro del overlay oscuro; no es un defecto a corregir, es una restricción a
  respetar en el diseño.
- Depende de que `dev/manuel-serrania` llegue a `main`; mientras no aterrice, este acceso no tiene
  contenido que mostrar y se declara como recorte, no se dibuja.

## 2. Ficha por pantalla

### Mockup 0 — Login

> **Corrección del 2026-09-10 (hallazgo de Marina, verificado en `src/frontend/auth.py:194`).** El
> acceso es un único `st.link_button("Iniciar sesión con Google", ...)` que redirige al consentimiento
> de Google. No hay campos de usuario ni contraseña, y por lo tanto **no existe un estado de
> "credenciales inválidas"**: un fallo de OAuth vuelve por el callback, no por un formulario.

- **Objetivo:** homologar el acceso a la nueva identidad de FARO, sin tocar la autenticación existente.
- **Contenido:** nuevo logo/identidad; **un único botón de acceso con Google**, sin campos de usuario o
  contraseña, sin "¿olvidaste tu contraseña?" ni registro. Es una pantalla de una sola acción: el
  diseño debe aprovechar ese espacio para identidad y narrativa, no para un formulario que no existe.
- **Botones y CTA:** "Iniciar sesión con Google" (único).
- **A dónde conecta:** al autenticar, avanza a P1 — o a la URL solicitada si venía de un enlace directo
  a P4/P6 (§1).
- **Estados:** en reposo; redirigiendo a Google; error de vuelta del callback (mensaje genérico, sin
  detalle interno).

### Pantalla 1 — Entrada

- **Objetivo:** explicar qué es FARO, qué se investiga y cuál será el papel del usuario, sin revelar
  todavía cuántas escuelas están en riesgo.
- **Contenido:** qué es FARO; objetivo del proyecto; imágenes narrativas de introducción; la frase de
  apoyo *"La matrícula nos dio la primera pista. Ahora descubramos qué está pasando."*; acceso al
  glosario; enlace discreto a "Cómo funciona" (§1); Asistente FARO flotante; walkthrough único (§4).
- **Botones y CTA:** un único CTA principal (copy final a cargo de Marina/Juan).
- **A dónde conecta:** CTA principal → P2.
- **Estados:**
  - **Primera visita de la sesión:** carga (mientras se prepara el panorama); walkthrough automático
    (§4); copy completo de introducción, sin revelar el número.
  - **Visita recurrente** (el usuario ya vio la revelación en P2 y volvió por el logo desde P6, §1):
    el walkthrough no se dispara solo (sigue accesible por el ícono "?"); la frase de apoyo cambia de
    tono — deja de fingir que no sabemos nada y reconoce que la investigación continúa (p. ej. "Sigues
    en la misma investigación. Estos son los mismos casos."). **P1 sigue sin decir el número:** la
    revelación es siempre trabajo de P2, lo único que cambia aquí es que no se repite la finta de
    partir de cero.
  - No aplica error propio, es una pantalla estática.

### Pantalla 2 — Panorama de las escuelas en riesgo

- **Objetivo:** revelar los casos y comunicar que comparten el riesgo pero no la misma situación
  (§3.5 del scope).
- **Contenido:** la frase central *"N escuelas están en riesgo. Tenemos N casos por investigar."* (`N`
  siempre resuelto en vivo, nunca escrito a mano); la matriz o visualización principal que compara las
  escuelas contra los 6 drivers (decisión de Monserrat), con espacio reservado para su leyenda
  obligatoria (plan §7.bis, contenido de Monserrat); matrícula general de los casos — única pantalla
  donde se muestra dentro de la historia; filtros que sólo atenúan filas, nunca recortan el conjunto
  (§3); Asistente FARO flotante.
- **Botones y CTA:** "Elegir un caso" (o el copy que se defina).
- **A dónde conecta:** CTA → P3.
- **Estados:** carga (mientras resuelve `escuelas_en_riesgo` y la matriz); error de API → "No pudimos
  cargar el panorama, intenta de nuevo", sin detalle interno.

### Pantalla 3 — Selección de caso

- **Objetivo:** que el usuario elija libremente una de las escuelas reveladas, sin obligación de
  revisarlas todas.
- **Contenido:** listado/tarjetas de las escuelas identificables; índice de riesgo numérico y **nivel
  de atención** (alta/media/baja) de cada una.
- **Botones y CTA:** CTA por escuela ("Abrir expediente"); "Volver al panorama".
- **A dónde conecta:** CTA de escuela → P4; "Volver al panorama" → P2.
- **Estados:** carga; sin estado vacío propio (el universo ya viene filtrado desde P2); escuelas sin
  predicción se marcan igual que en el expediente (§8).

### Pantalla 4 — Expediente de una escuela

- **Objetivo:** entender qué driver destaca en esa escuela y cuál es la recomendación asociada.
- **Contenido:** nombre de la escuela; índice de riesgo numérico + nivel de atención, con nota/tooltip
  que explica ambos; gráfica comparativa de los 6 drivers (Monserrat), con espacio reservado para su
  leyenda obligatoria (plan §7.bis); driver dominante resaltado; recomendación; indicador de
  completitud de la evidencia (`indice_completitud_drivers`); Asistente FARO flotante. No incluye
  evolución histórica de matrícula. El panel de evidencia SHAP existe en el diseño, pero hoy no tiene
  datos que mostrar (§8) — no se dibuja como si `/explicacion` ya entregara esa evidencia.
- **Botones y CTA:** "Regresar a selección"; "Ver la conclusión".
- **A dónde conecta:** "Regresar a selección" → P3; "Ver la conclusión" → P5.
- **Estados:** carga; `tiene_prediccion = false` (§8); drivers con `SIN_DATO` (§8); evidencia SHAP sin
  poblar (§8); ciclo distinto al más reciente (§8); error de API.

### Pantalla 5 — Conclusión Top 3

- **Objetivo:** cerrar la investigación general con el hallazgo principal.
- **Contenido:** los 3 drivers dominantes más frecuentes sobre el conjunto completo de escuelas en
  riesgo (nunca sobre lo filtrado); en cuántas escuelas aparece cada uno como dominante; problemática
  sustentada solo en los datos existentes; recomendación general por driver; la nota obligatoria:
  *"Esta conclusión se calcula sobre el conjunto completo de escuelas en riesgo, independientemente de
  los filtros utilizados durante la exploración."*
- **Botones y CTA:** un único CTA principal — **"Ir al Explorador de escuelas"** (§7).
- **A dónde conecta:** CTA → P6.
- **Estados:** carga; sin drill-down (no hay estado de detalle adicional); error de API.

### Pantalla 6 — Exploración de otras escuelas

- **Objetivo:** permitir que el usuario siga investigando otros casos con libertad, fuera de la
  narrativa guiada.
- **Contenido:** pop-up único de bienvenida la primera vez (§5); filtros obligatorios (ciclo, entidad,
  nivel); selección de escuela; misma lógica de expediente que P4; Asistente FARO flotante; acceso al
  glosario.
- **Botones y CTA:** selección de escuela; logo FARO en la barra superior.
- **A dónde conecta:** selección de escuela → vista de expediente (misma que P4); logo → P1.
- **Estados:** carga; combinación de filtros sin resultados (§8); error de API.

## 3. Filtros

| Pantalla | Filtros disponibles |
|---|---|
| P1 Entrada | Ninguno |
| P2 Panorama | **La revelación es siempre el total sin filtros, y los filtros de P2 solo atenúan filas de la matriz, no recortan el conjunto** (decisión cerrada con Monserrat y Marina, PR #308) — con esto la nota obligatoria de P5 se sostiene sola. Ningún control en P2 dispara una llamada nueva a la API |
| P3 Selección | Ninguno adicional; hereda el universo de P2 |
| P4 Expediente | No aplica (una sola escuela) |
| P5 Conclusión | Ninguno — se calcula siempre sobre el conjunto completo |
| P6 Exploración | Los 3 obligatorios: **ciclo escolar, entidad, nivel educativo**. Ciclo y entidad (`cve_ent`) son soportados por `/escuelas` **y** `/kpis`; **`nivel` sólo existe en `/escuelas`** — filtra la lista de escuelas, no los indicadores de `/kpis`. Un filtro adicional sólo se añade si ya existe como parámetro soportado |

## 4. Walkthrough inicial

Aparece una sola vez, sobre la Pantalla 1, la primera vez que el usuario entra tras autenticarse.

1. "Bienvenido a FARO. Vamos a investigar juntos qué está pasando con la matrícula escolar."
2. "La matrícula nos dio la primera pista. Ahora vamos a revisar la evidencia detrás de cada caso."
3. "En cualquier momento puedes preguntarle al Asistente FARO —el botón flotante— sobre los datos de
   FARO."

Cierre: botón "Empezar", que lo regresa al CTA principal de P1 (el walkthrough se sobrepone a P1, no
la reemplaza ni navega a otra pantalla).

Queda accesible después bajo demanda desde un ícono "?" junto al encabezado de P1, por si el usuario
quiere volver a verlo.

## 5. Pop-up de la exploración

Aparece una sola vez, la primera vez que el usuario entra a P6, sobre la pantalla ya cargada (no
bloquea la carga de datos).

> "Esta es tu zona de exploración libre. Aquí puedes revisar cualquier otra escuela con los filtros de
> ciclo, entidad y nivel. Ya no es parte de la conclusión que acabas de ver: cada caso se analiza por
> separado."

Botón único: "Entendido". No vuelve a aparecer para ese usuario/sesión.

## 6. Comportamiento del Asistente FARO

- **Nombre:** Asistente FARO en toda superficie (`ADR-011` §6, `P-03`). No se usa "Watson" ni "el
  chat" como nombre de producto.
- **Ubicación:** botón flotante, esquina inferior derecha, visible en P1 a P6. No aparece en Login (P0).
- **Apertura/cierre:** panel superpuesto, no navega a otra pantalla. Un clic en el botón lo abre; un
  clic fuera del panel o en una "×" lo cierra.
- **Estado de streaming:** la respuesta se muestra progresivamente mientras se genera, nunca un spinner
  que espera en silencio; mientras streamea, el input queda deshabilitado.
- **Tres errores distinguibles** (del diagnóstico del Equipo 2):
  - *Fuera de alcance:* "Esa pregunta está fuera de lo que el Asistente FARO puede consultar hoy."
  - *Sin datos:* "No encontré información para responder eso con los datos disponibles."
  - *Timeout:* "El Asistente FARO está tardando más de lo esperado. Intenta de nuevo."
- **El SQL generado no se muestra por defecto** (plan §4.ter — decisión de presentación, alcance de
  este frente; la lógica es del Equipo 2). El campo `sql_generado` se conserva en el contrato, pero
  queda detrás de una acción opcional y cerrada al abrir la conversación (p. ej. "Ver la consulta"):
  sirve para auditar y para que el evaluador confirme que la respuesta sale de la base real, sin que
  la explicación se reduzca a mostrar SQL.
- **Preguntas conceptuales:** cada término del glosario puede ofrecer "Pregúntale al Asistente", que
  precarga la pregunta (p. ej. "¿qué significa SIN_DATO?").
- **Al navegar entre pantallas:** el panel permanece abierto y conserva la conversación; no se
  resetea al cambiar de pantalla, coherente con que el scope lo define como un asistente general que
  no necesita conocer automáticamente la pantalla.
- Su lógica funcional (streaming, RAG, memoria) es responsabilidad del Equipo 2 (`US-611`); este
  documento fija solo su presencia y comportamiento visible.

## 7. Nombre de la exploración posterior

**Explorador de escuelas.** Elegido por Marina en el gate del jueves, de las tres opciones
propuestas (Explorador de escuelas / Otros casos / Sala de seguimiento). No usa "ML", "modelo" ni
"predicción" de cara al usuario.

Es el nombre visible de la Pantalla 6 en toda la experiencia: encabezado de P6, CTA de salida de
P5 (§2) y cualquier referencia de navegación (logo, breadcrumbs) que apunte a ella.

## 8. Estados vacíos, de error y SIN_DATO

- **Carga fila por fila en la matriz de P2:** revelar el panorama cuesta 11 llamadas hoy (2 del
  conjunto + 1 por escuela para sus 6 drivers + municipios, verificado por Monserrat). Riesgo y
  matrícula se pintan de inmediato porque llegan en la primera llamada; las celdas de drivers llegan
  después, fila por fila. Mientras cargan, cada fila muestra **su propio estado de carga** — nunca una
  celda vacía ni un cero, porque se leería como `SIN_DATO` sin serlo.
- **Ciclo distinto al más reciente en el Expediente (P4):** `/escuelas`, `/kpis` y `/predicciones`
  deben recibir el mismo `ciclo` para no divergir entre sí, pero `/escuelas/{cct}` no acepta ese
  parámetro. Si el usuario investiga con un ciclo que no es el más reciente materializado, los 6
  drivers que ve en el expediente son del ciclo más reciente, no del que eligió — el expediente lo
  tiene que decir explícito (p. ej. "Estos drivers son del ciclo 2024-2025, el más reciente
  disponible"), nunca en silencio.
- **Evidencia SHAP sin poblar:** las columnas `shap_d1…shap_d6` no están pobladas en producción hoy
  (0 de 42 verificado por Monserrat); `/explicacion` responde, pero sin esa evidencia. El panel de
  SHAP en P4 muestra `SIN_DATO` explícito — el driver dominante y la recomendación siguen viniendo de
  `PrediccionOut`, no dependen de esto.
- **Driver sin dato (`SIN_DATO`):** se muestra como "una pista que no pudimos verificar" (§5.4 del
  scope), nunca como cero ni como espacio vacío. En la gráfica de los 6 drivers, ese driver se marca
  visualmente distinto a los que sí tienen valor.
- **Escuela sin predicción (`tiene_prediccion = false`):** el expediente muestra el índice de riesgo y
  los drivers disponibles, pero reemplaza driver dominante/recomendación por: "Esta escuela todavía no
  tiene una predicción del modelo." No se inventa una recomendación genérica.
- **API responde 401:** se interpreta como sesión expirada, no como error del producto. Mensaje: "Tu
  sesión expiró. Inicia sesión de nuevo para continuar." y redirección a Login (P0); si venía de una
  URL directa a P4/P6 (§1), se conserva esa ruta para retomarla después de autenticar.
- **Combinación de filtros sin resultados (P6):** mensaje explícito — "No hay escuelas que coincidan
  con estos filtros. Prueba con otra combinación." — nunca una tabla vacía sin explicación.
- **Cobertura parcial agregada:** cuando `indice_completitud_drivers` es bajo para una escuela, se
  comunica como evidencia incompleta, igual que un driver individual en `SIN_DATO`, nunca como ausencia
  del problema.
