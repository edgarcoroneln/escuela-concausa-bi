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
| P6 Exploración | Logo FARO en la barra superior | P1 (reinicia la narrativa; no cierra sesión) |

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

## 2. Ficha por pantalla

### Mockup 0 — Login

- **Objetivo:** homologar el acceso a la nueva identidad de FARO, sin tocar la autenticación existente.
- **Contenido:** nuevo logo/identidad; los campos y la acción de acceso ya existentes; recurso visual
  alineado a la narrativa de investigación.
- **Botones y CTA:** "Iniciar sesión" (único).
- **A dónde conecta:** al autenticar, avanza a P1 — o a la URL solicitada si venía de un enlace directo
  a P4/P6 (§1).
- **Estados:** carga (verificando credenciales); error (credenciales inválidas, mensaje genérico sin
  detalle interno); sin sesión (estado por defecto de esta pantalla).

### Pantalla 1 — Entrada

- **Objetivo:** explicar qué es FARO, qué se investiga y cuál será el papel del usuario, sin revelar
  todavía cuántas escuelas están en riesgo.
- **Contenido:** qué es FARO; objetivo del proyecto; imágenes narrativas de introducción; la frase de
  apoyo *"La matrícula nos dio la primera pista. Ahora descubramos qué está pasando."*; acceso al
  glosario; Asistente FARO flotante; walkthrough único (§4).
- **Botones y CTA:** un único CTA principal (copy final a cargo de Marina/Juan).
- **A dónde conecta:** CTA principal → P2.
- **Estados:** carga (mientras se prepara el panorama); no aplica error propio, es una pantalla
  estática.

### Pantalla 2 — Panorama de las escuelas en riesgo

- **Objetivo:** revelar los casos y comunicar que comparten el riesgo pero no la misma situación
  (§3.5 del scope).
- **Contenido:** la frase central *"N escuelas están en riesgo. Tenemos N casos por investigar."* (`N`
  siempre resuelto en vivo, nunca escrito a mano); la matriz o visualización principal que compara las
  escuelas contra los 6 drivers (decisión de Monserrat); matrícula general de los casos — única
  pantalla donde se muestra dentro de la historia; filtros limitados dentro del universo revelado;
  Asistente FARO flotante.
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
  que explica ambos; gráfica comparativa de los 6 drivers (Monserrat); driver dominante resaltado;
  recomendación; indicador de completitud de la evidencia (`indice_completitud_drivers`); Asistente
  FARO flotante. No incluye evolución histórica de matrícula ni explicabilidad adicional a la que ya
  entrega `/explicacion`.
- **Botones y CTA:** "Regresar a selección"; "Ver la conclusión".
- **A dónde conecta:** "Regresar a selección" → P3; "Ver la conclusión" → P5.
- **Estados:** carga; `tiene_prediccion = false` (§8); drivers con `SIN_DATO` (§8); error de API.

### Pantalla 5 — Conclusión Top 3

- **Objetivo:** cerrar la investigación general con el hallazgo principal.
- **Contenido:** los 3 drivers dominantes más frecuentes sobre el conjunto completo de escuelas en
  riesgo (nunca sobre lo filtrado); en cuántas escuelas aparece cada uno como dominante; problemática
  sustentada solo en los datos existentes; recomendación general por driver; la nota obligatoria:
  *"Esta conclusión se calcula sobre el conjunto completo de escuelas en riesgo, independientemente de
  los filtros utilizados durante la exploración."*
- **Botones y CTA:** un único CTA principal (ver nombre propuesto en §7).
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
| P2 Panorama | Limitados, dentro del universo ya revelado. Ninguno de los 3 obligatorios se expone aquí como filtro de exploración; el panorama se presenta completo |
| P3 Selección | Ninguno adicional; hereda el universo de P2 |
| P4 Expediente | No aplica (una sola escuela) |
| P5 Conclusión | Ninguno — se calcula siempre sobre el conjunto completo |
| P6 Exploración | Los 3 obligatorios: **ciclo escolar, entidad, nivel educativo**, soportados hoy por `/escuelas` y `/kpis`. Un filtro adicional sólo se añade si ya existe como parámetro soportado |

## 4. Walkthrough inicial

Aparece una sola vez, sobre la Pantalla 1, la primera vez que el usuario entra tras autenticarse.

1. "Bienvenido a FARO. Vamos a investigar juntos qué está pasando con la matrícula escolar."
2. "La matrícula nos dio la primera pista. Ahora vamos a revisar la evidencia detrás de cada caso."
3. "En cualquier momento puedes preguntarle al Asistente FARO —el botón flotante— sobre lo que estás
   viendo."

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
- **Preguntas conceptuales:** cada término del glosario puede ofrecer "Pregúntale al Asistente", que
  precarga la pregunta (p. ej. "¿qué significa SIN_DATO?").
- **Al navegar entre pantallas:** el panel permanece abierto y conserva la conversación; no se
  resetea al cambiar de pantalla, coherente con que el scope lo define como un asistente general que
  no necesita conocer automáticamente la pantalla.
- Su lógica funcional (streaming, RAG, memoria) es responsabilidad del Equipo 2 (`US-611`); este
  documento fija solo su presencia y comportamiento visible.

## 7. Nombres propuestos para la exploración posterior

1. **Explorador de escuelas** — directo, describe la acción sin metáfora.
2. **Otros casos** — mantiene el lenguaje de investigación del storytelling.
3. **Sala de seguimiento** — sugiere continuidad sin sonar a "ML" ni a herramienta técnica.

Ninguna usa "ML", "modelo" ni "predicción" de cara al usuario. Marina elige una en el gate de hoy; este
documento se actualiza con la elegida antes de la entrega del viernes.

## 8. Estados vacíos, de error y SIN_DATO

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
