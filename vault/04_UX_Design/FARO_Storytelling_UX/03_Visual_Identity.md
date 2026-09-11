---
id: DOC-FARO-UX-IDENTITY
title: "Visual Identity — identidad visual de FARO"
owner: "Juan Carlos Macías Mayen"
status: draft
traces_up: ["US-621", "REQ-002", "vault/04_UX_Design/FARO_Storytelling_UX/00_Storytelling_Scope"]
traces_down: ["US-641"]
last_reviewed: "2026-09-10"
tags: [ui, identidad-visual, design-system, s7, us-621]
---

# Visual Identity — identidad visual de FARO

> Documento de Juan Carlos Macías Mayen. Fija **cómo se ve** la experiencia.
> Guía de identidad de referencia del proyecto — su anexo técnico de tokens vive en
> `mockups/Design_Tokens_Stitch.md` (`DOC-FARO-UX-TOKENS`).
> → [[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]] ·
> [[vault/04_UX_Design/Accessibility]]

**Estado:** borrador — los 7 mockups de escritorio están listos y liberados para Equipo 5
(2026-09-10/11). **`FARO_UX_UI_Guide.pdf` se cae como entregable** (decisión de Marina García del
Buey, 2026-09-11, avisada a Edgar Coronel como PO — ver §8). Queda pendiente la auditoría formal
de contraste WCAG (§6); el doc completo sigue `draft` hasta cerrar ese punto.

> **Revisión de Marina García del Buey (lead UX/UI), 2026-09-10.** La primera entrega (solo
> Login) tenía tres problemas reales: dibujaba un formulario de usuario/contraseña que no existe
> (el acceso real es un único botón OAuth de Google, `src/frontend/auth.py:194`); la paleta de
> datos usaba semáforo rojo/ámbar/verde y un color por driver, que choca con la regla de
> Monserrat Miranda de una rampa de un solo tono + acento para el dominante
> (`ejemplos_graficas/referencias/LEER_PRIMERO.md`); y faltaba `SIN_DATO` por completo. Las tres
> se corrigieron antes de esta entrega — ver §3 y §7.

> **Convivencia con lo existente — ya resuelta.** `ADR-011` y `DEC-023` (2026-09-10) declararon que
> este paquete gobierna el diseño de S7, y [[vault/04_UX_Design/UX_Guidelines]] pasó a `superseded`.
> Este documento **es** el sistema de diseño de la nueva experiencia; la identidad se rediseña desde
> cero sin atarse a lo anterior.
>
> Lo que **no** se sustituye: [[vault/04_UX_Design/Accessibility]] y **WCAG 2.1 AA**, que `ADR-011`
> §4 declara no negociables. La identidad nueva debe cumplirlos.
>
> El asistente conversacional se llama **Asistente FARO**. No se usa "Watson" en ninguna ruta visual.
> Un cambio total de framework sólo se acepta si conserva despliegue, autenticación, pruebas y plazo.

> **Decisión: claro/oscuro con los bloques D3 de "Cómo funciona" (`PLAN_TRABAJO.md` §5.bis, punto 2)
> — resuelta el 2026-09-11.** Los tres bloques D3 (mapa, barras, diagrama de flujo) que construyó el
> Equipo 1 viven cada uno en su propio iframe forzado a `color-scheme: light` y fondo blanco — no se
> pueden re-skinear sin tocar su código. Esta identidad **no adopta un lienzo oscuro como fondo de
> página en ningún momento**: el lienzo analítico siempre es claro (`#FFFFFF`/`#F8FAFC`/`#F1F5F9`,
> ver §3); el slate profundo (`#0F172A`) se usa solo como acento en componentes puntuales — botones
> primarios, el riel de navegación seleccionado, el nodo del Asistente FARO — nunca como fondo de
> lienzo. Por eso los bloques D3 **no chocan**: entran directo sobre el mismo lienzo claro que ya usa
> el resto de la experiencia, sin necesitar ningún tratamiento especial ni envoltura oscura alrededor
> del iframe. Si en el futuro se agrega un modo oscuro real, ese es el momento de revisar esta
> decisión — no antes.

## 1. Concepto

FARO se presenta como un centro de inteligencia institucional para el análisis y la vigilancia
diagnóstica del riesgo escolar: claridad de un observatorio científico de datos combinada con
la autoridad discreta de un centro de operaciones. Se evita deliberadamente la estética
detectivesca caricaturesca, la gamificación de seguridad y los motivos infantiles/educativos;
en su lugar, transmite rigor analítico, vigilancia proactiva, objetividad algorítmica y
confianza institucional.

Dos corrientes conviven en la identidad: **Corporate Modern** (estructura, orden, jerarquía) y
**Precision Data Lab Minimalism** (legibilidad de alta densidad, precisión instrumental —
bordes finos, metadatos en monoespaciada, micro-badges — y acentos "beacon" de cian/azul
eléctrico contra slate profundo y blanco puro, como una torre de señal temprana — el faro).

## 2. Rutas visuales propuestas

> **Nota de proceso:** este paquete no comparó 2-3 rutas A/B/C internamente — se recibió una
> ruta ya completa (logo, paleta, tipografía, componentes y dos pantallas construidas: Login y
> la guía de identidad) generada con la herramienta de diseño Stitch. Se documenta directo como
> **Ruta seleccionada** (§3) en vez de simular una comparación que no ocurrió. Los tokens crudos
> viven en [`mockups/Design_Tokens_Stitch.md`](mockups/Design_Tokens_Stitch.md).

## 3. Ruta seleccionada

- **Logo FARO:** no se recibió un archivo de logo/isotipo independiente en esta entrega; el
  wordmark "FARO Intelligence" se resuelve tipográficamente en `Space Grotesk` (ver mockups). Un
  isotipo dedicado queda **pendiente**.
- **Paleta de interfaz** (con valores; contraste formal contra [[vault/04_UX_Design/Accessibility]]
  aún sin medir — ver advertencia en §6):
  - Base institucional (Command Base): `#0F172A` (slate-900), `#1E293B` (slate-800).
  - Acento "señal" (The Signal): `#0284C7` (cyan-700), `#38BDF8` (cyan-400).
  - Lienzo analítico: `#FFFFFF`, `#F8FAFC`, `#F1F5F9`.
  - Paleta categórica de las 4 entidades del alcance (fija, un color por entidad, prohibido
    degradado): Ciudad de México `#4C72B0` · Estado de México `#DD8452` · Nuevo León `#55A868` ·
    Jalisco `#C44E52` — **idéntica a la que ya usa Manuel Serranía en "Cómo funciona" (`US-601`)**,
    no se reinventa.
- **Paleta de color de datos** (para índice de riesgo y los 6 drivers — **no confundir con la
  paleta de interfaz de arriba**; corregida el 2026-09-10 tras el rechazo de Marina a la primera
  versión, que usaba semáforo rojo/ámbar/verde y un color por driver):
  - **Rampa secuencial, un solo tono, 5 pasos** — magnitud de cualquier valor 0→1 (índice de
    riesgo, presión de cada driver): `#EEF2F7 → #C7D2E0 → #93A5C0 → #56698C → #0F172A`. El número
    siempre va dentro de la celda; el color nunca es la única fuente de lectura.
  - **Acento del dominante, un solo color, reservado exclusivamente para eso:** `#B45309`
    (ámbar). Se usa como contorno de la celda/barra del driver dominante — **nunca como relleno**,
    nunca para otro propósito (así el dominante no compite por canal con la magnitud, que ya usa
    la rampa).
  - **Gris de contexto** (lo que no destaca): `#94A3B8`.
  - **Textura `SIN_DATO`**: rayado a 45°, `repeating-linear-gradient(45deg, #CBD5E1 0 2px,
    transparent 2px 8px)` sobre `#F8FAFC`, con la etiqueta corta "S/D" dentro de la celda y el
    motivo completo ("SIN DATO — pista que no pudimos verificar" + causa) en tooltip/detalle —
    nunca el paso más claro de la rampa, nunca un `0.00`.
  - **Los 6 drivers ya no tienen un color propio.** Se identifican por posición fija D1…D6 y por
    etiqueta de texto, nunca por color — el color de su celda es siempre la rampa de magnitud.
- **Tipografías:** `Space Grotesk` (encabezados y títulos de módulo, peso 500/600 únicamente,
  nunca decorativo) · `Inter` (interfaz y texto analítico) · `JetBrains Mono` (todo dato
  cuantitativo: CCT, coeficientes de riesgo, timestamps — obligatorio, para eliminar deriva
  óptica al comparar matrices).
- **Cards:** fondo `#FFFFFF`, borde `1px solid #E2E8F0`, radio `6px`, sin sombra en reposo;
  título alineado a la izquierda en `headline-sm`, metadato operativo (CCT, confianza,
  timestamp) en `label-micro-mono` a la derecha; métricas en `JetBrains Mono` con indicador de
  tendencia (`+2.4%`, `-0.8%`).
- **Botones:** primario fondo `#0F172A` / texto blanco / radio `4px` / hover `#1E293B`
  ("Generar Dictamen", "Exportar Censo"); "beacon" (acción analítica) fondo `#0284C7` / hover
  `#0369A1` ("Ejecutar Simulación", "Filtrar Matriz"); secundario/sutil fondo blanco, borde
  `#CBD5E1`, texto `#334155`.
- **Iconografía:** Material Symbols Outlined, trazo fino, coherente con el tono instrumental —
  ver uso en `mockups/00_Login.html`.
- **Tratamiento de gráficas:** sin sombras skeuomórficas; profundidad por capas tonales +
  bordes hairline `1px solid #E2E8F0`. Elevación en 4 niveles (ver §5). Chips de riesgo con un
  punto de estado sólido de `6px` + texto en mayúsculas `label-micro-mono`.
- **Imágenes:** no se recibió tratamiento fotográfico en esta entrega; el sistema es
  primariamente tipográfico/geométrico, sin fotografía de stock.
- **El chat:** se llama **Asistente FARO** (nunca "Watson" — la entrega original de Stitch decía
  "Watson AI" y se corrigió en las 4 superficies del paquete, `DEC-024` P-03). Nodo flotante
  circular fijo en `bottom:24px; right:24px`, superficie `#0F172A` con micro-borde cian
  `#38BDF8` iluminado y resplandor ambiental (`box-shadow: 0 0 20px rgba(2,132,199,.25)`);
  badge de estado `ASISTENTE FARO // ONLINE` en `JetBrains Mono`. Al expandirse abre una
  interfaz de prompt en lenguaje natural para consultas investigativas.
- **Nivel de atención (alta/media/baja):** **sin color propio** — icono + texto únicamente, para
  no competir con la rampa de magnitud y para no repetir el semáforo que Marina rechazó. Iconos
  fijos, tomados de los ejemplos reales de Monserrat: **▲ alta · ■ media · ● baja**, en tinta
  `#0F172A`. La lógica de corte es la de `DEC-024` sobre `indice_riesgo`: alta `>=0.50`, media
  `>=0.30`, baja `<0.30` — el front la deriva, nunca consume `gold.recomendaciones.prioridad`.
- **Tratamiento del driver dominante:** contorno de `2px` en el acento `#B45309` alrededor de la
  celda/barra completa, más el icono ▲ y la etiqueta "Driver dominante" — sin relleno de color
  distinto, sin badge de escala 0–10 (la escala real de presión es 0 a 1, ver `02_Data_Visualization_Spec.md`
  §1.2).

## 4. Componentes

> Inventario de los 7 mockups + guía de identidad. Variantes de estado (hover, foco,
> deshabilitado, carga, error) **no vienen completas** para todos — Equipo 5 debe completarlas al
> implementar; se marca lo que sí trae la entrega.

| Componente | Qué trae esta entrega | Estados definidos |
|---|---|---|
| Precision Data Card | contenedor, header, métrica | reposo únicamente |
| Matriz escuelas × 6 drivers (Pantalla 2) | rampa de magnitud, contorno de dominante, `S/D` con textura, leyenda de degradado + 2 swatches | reposo únicamente |
| Barras de presión por driver (Pantalla 4) | misma rampa/acento/textura que la matriz, orden D1…D6 fijo | reposo únicamente |
| Badge de nivel de atención | icono ▲■● + texto, sin color propio | reposo únicamente |
| Badge de driver dominante | contorno ámbar `#B45309` + icono, sin relleno de color | reposo únicamente |
| Botón primario / beacon / secundario | color, radio, hover | reposo + hover |
| Input / control de formulario | fondo, borde, radio | reposo + foco (anillo cian) |
| Panel inspector de escuela (side sheet) | ancho (`26rem`), contenido esperado | reposo únicamente |
| Nodo flotante Asistente FARO | forma, color, glow, badge | reposo + expandido |
| Selector de OAuth simulado (Login) | 3 estados: reposo, redirigiendo, error de callback | los 3 explícitos |
| Riel de navegación lateral (Pantallas 1-6) | logo, tagline único, 7 rutas + referencia técnica | reposo + activo |

Foco visible, estado deshabilitado y estado de carga **no están cubiertos** por esta entrega en
ningún componente — quedan abiertos para que Equipo 5 los defina siguiendo
[[vault/04_UX_Design/Accessibility]].

## 5. Efectos y animaciones sugeridas

- Profundidad por **capas tonales**, sin sombras pesadas: nivel 0 fondo `#F8FAFC`; nivel 1
  tarjetas sin sombra; nivel 2 hover (`0 4px 12px -2px rgba(15,23,42,.06)` + borde `#CBD5E1`);
  nivel 3 modales/drawers (`0 20px 25px -5px rgba(15,23,42,.1)`).
- Resplandor ambiental sutil (`box-shadow` radial cian) reservado al nodo del Asistente FARO —
  no usar en otros elementos, para que mantenga su función de "único punto vivo" de la interfaz.
- **Pendiente:** la entrega no especifica timings de transición ni comportamiento bajo
  `prefers-reduced-motion`. `ADR-011` §4 lo exige como no negociable — Equipo 5 debe definirlo
  antes de implementar cualquier animación (hover, expansión del chat, transiciones de panel).

## 6. Accesibilidad

> **Advertencia explícita:** los pares de color de esta sección **no fueron auditados
> formalmente contra WCAG 2.1 AA** con una herramienta de contraste — son los tokens tal como
> quedaron tras la corrección de Marina. Antes de que Equipo 5 implemente, corresponde correr una
> validación de contraste real (por ejemplo con los mismos criterios que ya aplica
> [[vault/04_UX_Design/Accessibility]] o el script de Monserrat en `ejemplos_graficas/`) sobre:
> texto `on-surface` (`#0F172A`) contra los fondos `surface-container-*`, cada paso de la rampa
> de magnitud contra el texto que lleva encima, el acento `#B45309` contra el fondo de su celda,
> y el texto blanco de los botones primario/beacon contra `#0F172A`/`#0284C7`.
- **Nada se codifica solo por color, por diseño desde esta corrección:** nivel de atención
  (icono + texto), dominante (contorno + icono + etiqueta), `SIN_DATO` (textura + etiqueta "S/D"
  + motivo) — ninguno depende únicamente del tono para leerse. Esto resuelve directamente el
  criterio de `ADR-011` §4 que la primera versión (semáforo) violaba.
- Todo identificador alfanumérico (CCT, coeficientes, timestamps) va en `JetBrains Mono` para
  legibilidad tabular — no es solo estético, reduce error de lectura en matrices densas.
- Tamaño mínimo de texto, foco visible y orden de tabulación: **no definidos** en esta entrega
  (es un export estático de diseño, no un prototipo interactivo completo) — criterio exigible
  sigue siendo [[vault/04_UX_Design/Accessibility]], sin excepción.

## 7. Mockups

Los 7, de escritorio, **listos y liberados para Equipo 5** (2026-09-10/11):

| # | Pantalla | Archivo | Estado |
|---|---|---|---|
| 0 | Login | [`mockups/00_Login.png`](mockups/00_Login.png) / [`.html`](mockups/00_Login.html) | listo |
| 1 | Entrada | [`mockups/01_Entrada.png`](mockups/01_Entrada.png) / [`.html`](mockups/01_Entrada.html) | listo |
| 2 | Panorama | [`mockups/02_Panorama_Escuelas_Riesgo.png`](mockups/02_Panorama_Escuelas_Riesgo.png) / [`.html`](mockups/02_Panorama_Escuelas_Riesgo.html) | listo |
| 3 | Selección de caso | [`mockups/03_Seleccion_Caso.png`](mockups/03_Seleccion_Caso.png) / [`.html`](mockups/03_Seleccion_Caso.html) | listo |
| 4 | Expediente | [`mockups/04_Expediente_Escuela.png`](mockups/04_Expediente_Escuela.png) / [`.html`](mockups/04_Expediente_Escuela.html) | listo |
| 5 | Conclusión (Top 2 real; el rótulo "Top 3" es el máximo de casillas, no una cuenta fija) | [`mockups/05_Conclusion_Top3.png`](mockups/05_Conclusion_Top3.png) / [`.html`](mockups/05_Conclusion_Top3.html) | listo |
| 6 | Explorador | [`mockups/06_Explorador.png`](mockups/06_Explorador.png) / [`.html`](mockups/06_Explorador.html) | listo |

Todos usan el dataset real de 7 escuelas verificado en producción (10-sep-2026, commit
`457715a`) — mismo conjunto que `02_Data_Visualization_Spec.md` de Monserrat Miranda, no datos de
ejemplo inventados.

Índice completo (7 mockups + soporte, con enlaces): [[vault/04_UX_Design/FARO_Storytelling_UX/mockups/_index]].

Material de soporte en `mockups/`, no numerado (no es de las 7 pantallas de la historia):

- [`Guia_Identidad_Visual.png`](mockups/Guia_Identidad_Visual.png) / [`.html`](mockups/Guia_Identidad_Visual.html)
  — guía de identidad completa (paleta de interfaz, sistema de color de datos, tipografía,
  componentes).
- [`Design_Tokens_Stitch.md`](mockups/Design_Tokens_Stitch.md) — **anexo técnico de este documento**
  (frontmatter propio `DOC-FARO-UX-TOKENS`): tokens crudos de tipografía, radios, espaciado y
  elevación (su sección de color quedó superada, ver nota al inicio del archivo; el color vigente
  es el de §3 de este documento). Sustituye a `FARO_UX_UI_Guide.pdf` como entregable — ver §8.
- [`Como_Funciona_Preview.png`](mockups/Como_Funciona_Preview.png) / [`.html`](mockups/Como_Funciona_Preview.html)
  — borrador de identidad para la superficie *Cómo funciona* de Equipo 1 (`US-601`, §5.bis de
  `PLAN_TRABAJO`). **No es un octavo mockup formal ni reemplaza el trabajo de Manuel Serranía**:
  el plan es explícito en que esta superficie "no necesita mockup propio" y que Juan solo le da
  identidad con los componentes ya definidos arriba. Se deja como referencia de cómo se vería,
  pendiente de coordinar con Manuel/Héctor antes de darla por final — las dos rutas de la API que
  la alimentan (`GET /api/v1/about/secciones*`) todavía no están en `main`.

## 8. PDF final — retirado

**`FARO_UX_UI_Guide.pdf` se cae como entregable de `US-621`** (decisión de Marina García del Buey,
2026-09-11). Un PDF que duplica documentos ya versionados es deuda de mantenimiento, no responde a
ninguno de los hallazgos del profesor (experiencia, gráficas, storytelling, componentes, chat,
ML), y `DEC-024` ya fijó que las únicas compuertas del proyecto son rama, PR, CI, una aprobación y
QA sobre la candidata — un PDF no es ninguna de esas.

En su lugar, la guía de identidad de referencia **es este documento**, y su anexo técnico de
tokens (paleta de interfaz, tipografía, radios, espaciado, elevación) es
[`mockups/Design_Tokens_Stitch.md`](mockups/Design_Tokens_Stitch.md) — ya con frontmatter propio
(`DOC-FARO-UX-TOKENS`, `id`/`owner`/`status`) y listado en
[[vault/04_UX_Design/FARO_Storytelling_UX/mockups/_index]].

Marina retira las referencias a `FARO_UX_UI_Guide.pdf` de `PLAN_TRABAJO.md` §7/§8/§14 y avisa a
Edgar Coronel (PO) — el go/no-go de `US-621` es suyo, así que el cambio no desaparece en silencio.
