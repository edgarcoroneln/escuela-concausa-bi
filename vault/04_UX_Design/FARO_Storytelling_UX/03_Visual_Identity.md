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
> Único editor del PDF final `FARO_UX_UI_Guide.pdf`.
> → [[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]] ·
> [[vault/04_UX_Design/Accessibility]]

**Estado:** borrador — primer entregable liberado (2026-09-10): identidad visual (§3) y mockup de
Login (Pantalla 0). Quedan 6 de 7 mockups y el PDF final; el doc completo sigue `draft` hasta
cerrarlos.

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
- **Paleta** (con valores; contraste formal contra [[vault/04_UX_Design/Accessibility]] aún sin
  medir — ver advertencia en §6):
  - Base institucional (Command Base): `#0F172A` (slate-900), `#1E293B` (slate-800).
  - Acento "señal" (The Signal): `#0284C7` (cyan-700), `#38BDF8` (cyan-400).
  - Lienzo analítico: `#FFFFFF`, `#F8FAFC`, `#F1F5F9`.
  - Riesgo, escala tri-estado estricta — **nunca decorativa, solo para indicar riesgo**:
    Alto `#E11D48` · Medio `#D97706` · Bajo `#059669`.
  - Los 6 drivers, un color fijo cada uno (no escala secuencial): Pobreza y rezago `#6366F1` ·
    Inseguridad `#F43F5E` · Infraestructura `#EA580C` · Conectividad `#0284C7` · Estrés hídrico
    `#0D9488` · Calidad del aire `#8B5CF6`.
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
- **Estados de riesgo:** Alto → fondo `#FFF1F2` / borde `#FECDD3` / texto `#E11D48`; Medio →
  fondo `#FFFBEB` / borde `#FDE68A` / texto `#D97706`; Bajo → fondo `#ECFDF5` / borde `#A7F3D0`
  / texto `#059669`. **Pendiente de reconciliar** con el nivel de atención oficial de
  `DEC-024` (derivado de `indice_riesgo`: alta `>=0.50`, media `>=0.30`, baja `<0.30`) antes de
  que Equipo 5 lo implemente — esta entrega no trae la lógica de corte, solo el tratamiento
  visual de las 3 bandas.
- **Tratamiento del driver dominante:** badge compacto con cuadro/barra de color del driver +
  índice de impacto (escala 0.0–10.0), un color fijo por driver (ver paleta arriba).

## 4. Componentes

> Inventario base entregado por Stitch (Login + guía de identidad). Variantes de estado
> (hover, foco, deshabilitado, carga, error) **no vienen completas** para todos — Equipo 5 debe
> completarlas al implementar; se marca lo que sí trae la entrega.

| Componente | Qué trae esta entrega | Estados definidos |
|---|---|---|
| Precision Data Card | contenedor, header, métrica | reposo únicamente |
| Chip de riesgo (Alto/Medio/Bajo) | color, borde, texto, punto de estado | reposo únicamente |
| Badge de driver dominante | color fijo + barra de impacto | reposo únicamente |
| Botón primario / beacon / secundario | color, radio, hover | reposo + hover |
| Input / control de formulario | fondo, borde, radio | reposo + foco (anillo cian) |
| Panel inspector de escuela (side sheet) | ancho (`26rem`), contenido esperado | reposo únicamente |
| Nodo flotante Asistente FARO | forma, color, glow, badge | reposo + expandido |
| Pantalla de Login completa | ver `mockups/00_Login.html` | reposo, validación de error visible |

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

> **Advertencia explícita:** los pares de color de esta sección (texto sobre fondo, chips de
> riesgo, botones) **no fueron auditados formalmente contra WCAG 2.1 AA** — son los tokens tal
> como los generó Stitch. Antes de que Equipo 5 implemente, corresponde correr una validación de
> contraste real (por ejemplo con los mismos criterios que ya aplica
> [[vault/04_UX_Design/Accessibility]]) sobre: texto `on-surface` (`#0F172A`) contra los fondos
> `surface-container-*`, texto de los 3 chips de riesgo contra su propio fondo, y el texto blanco
> de los botones primario/beacon contra `#0F172A`/`#0284C7`.
- Todo identificador alfanumérico (CCT, coeficientes, timestamps) va en `JetBrains Mono` para
  legibilidad tabular — no es solo estético, reduce error de lectura en matrices densas.
- Tamaño mínimo de texto, foco visible y orden de tabulación: **no definidos** en esta entrega
  (es un export estático de diseño, no un prototipo interactivo completo) — criterio exigible
  sigue siendo [[vault/04_UX_Design/Accessibility]], sin excepción.

## 7. Mockups

| # | Pantalla | Archivo | Estado |
|---|---|---|---|
| 0 | Login | [`mockups/00_Login.png`](mockups/00_Login.png) / [`mockups/00_Login.html`](mockups/00_Login.html) | **listo — liberado para Equipo 5** |
| 1 | Entrada | `mockups/01_Entrada.png` | pendiente |
| 2 | Panorama | `mockups/02_Panorama_Escuelas_Riesgo.png` | pendiente |
| 3 | Selección de caso | `mockups/03_Seleccion_Caso.png` | pendiente |
| 4 | Expediente | `mockups/04_Expediente_Escuela.png` | pendiente |
| 5 | Conclusión Top 3 | `mockups/05_Conclusion_Top3.png` | pendiente |
| 6 | Explorador | `mockups/06_Explorador.png` | pendiente |

Material de soporte adicional en `mockups/`: [`Guia_Identidad_Visual.png`](mockups/Guia_Identidad_Visual.png)
/ [`Guia_Identidad_Visual.html`](mockups/Guia_Identidad_Visual.html) (guía de identidad completa,
no es una de las 7 pantallas numeradas) y [`Design_Tokens_Stitch.md`](mockups/Design_Tokens_Stitch.md)
(tokens crudos: color, tipografía, radios, espaciado — fuente de los valores citados en §3).

## 8. PDF final

<!-- FARO_UX_UI_Guide.pdf. Qué incluye y en qué orden. -->
