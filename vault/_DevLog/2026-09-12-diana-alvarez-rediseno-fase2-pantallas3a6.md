---
project: "FARO"
date: "2026-09-12"
author_human: "Diana Aracely Alvarez Varela"
agent: "Claude Code"
model: "claude-sonnet-5"
session_duration: "1 sesión -- cierre del rediseño Fase 2 (US-641): Pantallas 3 a 6, bajo una meta de entrega el mismo día antes de las 3pm. Turno único, sin pausa de revisión visual entre pantalla y pantalla (a diferencia de la 1 y la 2)."
touches: ["US-641", "US-621", "US-305", "DEC-023", "DEC-024", "DEC-026", "BUG-058"]
tags: [devlog, equipo-5, frontend, react, rediseño, ux-ui]
---

# DevLog — 2026-09-12 — Rediseño Fase 2 (US-641): Pantallas 3 a 6

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/04_UX_Design/FARO_Storytelling_UX/01_UX_Architecture|01_UX_Architecture]] · [[vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec|02_Data_Visualization_Spec]]

## Contexto

Con las Pantallas 1 y 2 ya revisadas por Diana, esta entrega cierra el rediseño completo (US-641)
contra una meta de tiempo explícita: las 7 pantallas listas el mismo día antes de las 3pm. Por eso el
ritmo cambia respecto a las dos entregas anteriores -- se construyen las 4 pantallas restantes en un
solo turno, sin pausa de revisión visual entre una y otra, documentando cada simplificación tal como
se hace el resto de la sesión.

Antes de escribir código se releyó completo `01_UX_Architecture.md` §2 (fichas de Pantalla 3 a 6),
§3 (filtros), §5 (pop-up del Explorador) y §7 (nombre "Explorador de escuelas"), y
`02_Data_Visualization_Spec.md` §7.bis completo (qué declara toda leyenda, y la tabla resuelta
gráfica por gráfica) -- ese documento ya trae el texto literal de cada leyenda obligatoria, así que
esta entrega lo usa tal cual, no lo redacta de nuevo.

## Qué se construyó

**`components/LeyendaGrafica.jsx` (nuevo):** bloque compartido de las 4 declaraciones fijas que pide
la §7.bis.1 (qué se ve / unidad / SIN_DATO aquí / ciclo y recorte), visible siempre, nunca solo
tooltip. Se usa en P2 (Panorama, retro-agregado a la entrega anterior), P3, P4 y P5, cada una con el
texto literal de su fila en la tabla de la §7.bis.2.

**Pantalla 3 (`pages/LosSieteCasos.jsx`, ajustada):** el índice de riesgo pasa de número plano a
`RiskGauge` (pista 0-1 con la línea de alerta marcada, tal como pide la ficha de §2) -- mismo
componente que ya usaba el Expediente, ahora también aquí. Se agregó el CTA "Volver al panorama"
(→ `/panorama`) que la ficha exige y que faltaba. Legend obligatoria agregada una sola vez, debajo de
la cuadrícula de tarjetas (no repetida por tarjeta).

**Pantalla 4 (`pages/ExpedienteEscuela.jsx`, corrección real encontrada):** el `RiskGauge` del tab
Resumen llamaba sin `alertLine` ni `max`, así que usaba los valores por defecto del componente
(`0.5`/`0.6` escritos en `RiskGauge.jsx`) en vez de los cortes reales de `useCortesAtencion()` --
**el mismo patrón que causó `BUG-058`** (cortes de nivel de atención tecleados a mano), solo que esta
vez viviendo en un valor por defecto de prop en lugar de una constante. Corregido a
`alertLine={cortes.alta}` / `max={cortes.ancla_calibracion ?? 0.6}`. El tab Drivers, que mostraba una
cuadrícula de insignias con el valor de cada driver, se reemplaza por `components/DriverBars.jsx`
(nuevo): una gráfica de barras real -- horizontal, rampa monocromática, SIN_DATO como pista rayada de
punta a punta -- que es la "gráfica comparativa de los 6 drivers" que pide la ficha de §2 y no una
tabla de números. Legend obligatoria agregada (texto de la fila "P4 · Comparativa de los 6 drivers").
CTA "Ver la conclusión" agregado (→ `/conclusion`); el botón de regreso se renombra de "← Volver a
casos" a "← Regresar a selección" (mismo destino, `/casos`, coincide con el texto exacto de la ficha).

**Pantalla 5 (`pages/Conclusion.jsx`, nueva por completo):** Top 3 (o menos, si de verdad solo
dominan uno o dos -- nota de Marina en §8.3, no se rellena) de `driver_dominante` sobre el **conjunto
completo** de escuelas en riesgo, nunca sobre nada filtrado -- por diseño, llama a
`getPanoramaEscuelas()` de cero en vez de recibir props de otra pantalla. Esa misma función (ya
construida para P2) resuelve de paso la nota de cobertura que pide la §7.bis.2: como ya trae `d1..d6`
de cada escuela, se puede saber qué driver nunca tuvo dato en NINGUNA escuela del conjunto y
declararlo aparte, sin confundirlo con "nunca domina". **Recomendación general por driver: texto
autoral de este frente** (`recomendacionGeneralPorDriver` en `data/mock.js`) -- se buscó en todo el
vault un texto ya redactado por Monserrat/Marina para esto y no existe ninguno, solo ejemplos por
escuela (`parDiferenciador`); las seis líneas nuevas siguen ese mismo tono operativo. Concentración
por municipio mostrada con `cve_mun` (el contrato no trae el nombre, mismo gap ya documentado). Nota
obligatoria de la ficha incluida literal. CTA único "Ir al Explorador de escuelas" → `/explorador`.

**Pantalla 6 (`pages/Explorador.jsx`, nueva por completo):** pop-up de bienvenida la primera vez
(texto literal de §5, `localStorage`, mismo patrón que el walkthrough de P1), los 3 filtros
obligatorios del §3 (ciclo, entidad `cve_ent`, nivel -- los tres ya soportados por `GET /escuelas`
según `src/api/v1/gold.py`), y selección de escuela que navega a **la misma ruta `/escuela/:cct` que
usa la Pantalla 3** -- no una vista nueva, tal como pide la ficha ("misma lógica de expediente,
reutilizando sus mismas gráficas"). Mensaje literal de "sin resultados" (§8). Las 4 páginas heredadas
que este Explorador consolida en destino (Mapa, Matriz de drivers, Comparación territorial,
Comparativa) **no se borran todavía** -- siguen accesibles en "Vistas heredadas" del Sidebar, mismo
criterio de no dejar a nadie del equipo sin acceso mientras se confirma que el Explorador nuevo cubre
lo que cada una resolvía.

**`lib/navFases.js` / `main.jsx`:** rutas `/conclusion` y `/explorador` habilitadas en el Sidebar
(antes mostraban `disabledHint`) y registradas en el router.

## Pendiente / simplificado a propósito (por la meta de tiempo de hoy)

- **Filtros de §3 en la matriz de P2** -- siguen sin implementarse (ya deferido en la entrega
  anterior); no cambia con esta entrega.
- **Carga fila por fila de la matriz de P2 (§8)** -- sigue como un solo estado de carga para toda la
  matriz, no por fila.
- **Legend de P6 con su línea de recorte propia** -- la §7.bis.2 dice que la única diferencia de la
  leyenda reutilizada en P6 es la línea de ciclo/recorte (filtro activo en vez de "conjunto en
  riesgo"). Hoy `ExpedienteEscuela.jsx` muestra siempre la misma leyenda sin distinguir si se llegó
  desde P3 o desde el Explorador -- simplificación explícita por tiempo, no un olvido.
- **Panel de explicación del modelo (SHAP) en P4** -- sigue sin dibujarse; su leyenda ya está escrita
  en el documento canónico pero no hay panel que la use (las columnas `shap_d1..shap_d6` siguen sin
  poblarse en producción, §7.bis.2).
- **Reconciliación completa de las 4 rutas heredadas** -- el Explorador nuevo cubre el destino
  (seleccionar y ver el expediente de cualquier escuela con filtros), pero no se auditó pantalla por
  pantalla si cada una de las 4 páginas heredadas tiene alguna lectura que el Explorador todavía no
  reproduce (p. ej. el mapa de `MapaCasos.jsx`). Se dejan visibles en "Vistas heredadas" hasta esa
  auditoría.
- **`ciclo` en el filtro de P6** -- la opción existe en el `<select>` (los 5 ciclos materializados en
  `CICLOS` de `generar_fixture.py`), pero no se verificó en esta sesión que `/escuelas?ciclo=...`
  cambie de verdad el resultado contra un servidor real -- queda para la revisión de Diana con su
  propio `npm run dev`.
- **Modo demo del Explorador** -- el mock de "los 7 casos" no trae `cve_ent`/`nivel` reales por
  escuela, así que en modo demo (`VITE_USE_MOCK=true`) los filtros no recortan el set de ejemplo;
  documentado en el propio código, no es un bug.

## Validación

- Balance de llaves/paréntesis/corchetes verificado por script en los 10 archivos nuevos/modificados.
- `node --check` corrido sobre los 3 archivos `.js` sin JSX que se tocaron (`lib/navFases.js`,
  `data/mock.js`, `lib/api.js`) -- los tres pasan. Los `.jsx` siguen sin poder verificarse así (mismo
  límite ya documentado: `node --check` no entiende JSX) ni con `npx vite build` (mismo error de
  binario nativo de `rolldown` para otra arquitectura, ya documentado en la entrega de Pantalla 1/2) --
  verificación visual real queda en manos de Diana con su `npm run dev`.
- `python vault/_Meta/scripts/vault_lint.py .` → Vault limpio.
