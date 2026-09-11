---
name: FARO Intelligence Platform
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45464d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#006398'
  on-secondary: '#ffffff'
  secondary-container: '#5bb8fe'
  on-secondary-container: '#00476e'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#001e2c'
  on-tertiary-container: '#008ebf'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#cce5ff'
  secondary-fixed-dim: '#93ccff'
  on-secondary-fixed: '#001d31'
  on-secondary-fixed-variant: '#004b73'
  tertiary-fixed: '#c4e7ff'
  tertiary-fixed-dim: '#7bd0ff'
  on-tertiary-fixed: '#001e2c'
  on-tertiary-fixed-variant: '#004c69'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Space Grotesk
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 34px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  title-md:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 22px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  label-data-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-micro-mono:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.06em
  label-ui:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.03em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  space-2xs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-base: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  layout-margin-mobile: 1rem
  layout-margin-desktop: 2rem
  layout-gutter: 1rem
  sidebar-width-collapsed: 4.5rem
  sidebar-width-expanded: 17.5rem
  inspector-panel-width: 26rem
---

> Export crudo de la herramienta de diseño (Stitch) para la ruta visual de US-621, referenciado
> desde [[vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity]] §3 (Ruta seleccionada).
> No es un artefacto canónico del vault (sin `id`/`owner`/`status` propios); es material de
> soporte junto con `00_Login.png/.html` y `Guia_Identidad_Visual.png/.html` en esta carpeta.
> Las menciones originales a "Watson" se corrigieron a **Asistente FARO** (`DEC-024`, P-03).

## Brand & Style

This design system establishes an institutional, high-precision intelligence interface for educational risk analysis and diagnostic surveillance. It merges the focused clarity of a modern scientific data observatory with the quiet authority of an intelligence operations center. The aesthetic avoids detective tropes, gamified security metaphors, or playful educational motifs; instead, it projects analytical rigor, proactive guardianship, algorithmic objectivity, and institutional trust.

The visual style blends **Corporate Modern** structure with **Precision Data Lab Minimalism**:
- **High-Density Legibility:** Structural data presentation with purposeful negative space, enabling quick triage across vast school networks.
- **Instrumental Precision:** Crisp hairline borders, monospaced metadata pairings, micro-badges, and calibrated risk markers inspired by signal telemetry.
- **Beacon Dynamic:** Strategic application of focused luminescent blue/cyan accents against deep slate and pure white surfaces, metaphorically operating as an early-warning signal tower (Faro).

## Colors

The color palette is calibrated for institutional decision-makers who require instantaneous differentiation of operational risk without cognitive overload.

### Functional Roles
- **Command Base (Deep Slate Navy - `#0F172A`, `#1E293B`):** Establishes institutional foundation, structural anchoring, and authority. Used in persistent application navigation, primary headings, terminal panels, and deep focal areas.
- **The Signal (Beacon Cyan & Electric Indigo - `#0284C7`, `#38BDF8`):** Signifies telemetry, systematic verification, active telemetry states, and interactive focal points.
- **Analytical Canvas (`#FFFFFF`, `#F8FAFC`, `#F1F5F9`):** A clinical, noise-free backdrop that enhances visual scanning and table interpretation.

### Calibrated Risk Tiers
Risk indicators follow a strict tri-state chromatic scale. Never use these colors decoratively:
- **Critical / High Tier (`#E11D48`):** Demands immediate mitigation protocol.
- **Elevated / Medium Tier (`#D97706`):** Signals negative inflection points or unstable stability.
- **Controlled / Low Tier (`#059669`):** Indicates monitored structural resilience.

### Systematic Risk Drivers
The six diagnostic indices are assigned distinct, non-competing chromatic markers:
- **Pobreza y Rezago:** `#6366F1` (Indigo Horizon)
- **Inseguridad:** `#F43F5E` (Signal Crimson)
- **Infraestructura:** `#EA580C` (Structural Amber)
- **Conectividad:** `#0284C7` (Beacon Cyan)
- **Estrés Hídrico:** `#0D9488` (Hydrologic Teal)
- **Calidad del Aire:** `#8B5CF6` (Atmospheric Violet)

## Typography

The typographic hierarchy uses a calibrated pairing of three distinct typefaces to convey institutional intelligence:

1. **Space Grotesk (Headers & Module Titles):** Brings an architectural, advanced-computing character to summary sections, dashboards, and modal headings.
2. **Inter (Interface & Analytical Copy):** Provides neutral readability across variable screen conditions, high-density data sheets, and diagnostic briefs.
3. **JetBrains Mono (Metrics, School CCT IDs, Telemetry & Coordinate Data):** Standardizes all quantitative outputs, data logs, timestamp audits, and risk delta metrics into strict tabular widths, eliminating optical drift when monitoring matrices.

### Rules for Application
- All alphanumeric identifiers (e.g., CCT school codes, risk coefficients, algorithmic confidence values) must render exclusively in `JetBrains Mono`.
- Headings must never use decorative weights; stick rigidly to Medium (`500`) or SemiBold (`600`).
- Section categorization tags must use `label-micro-mono` transformed to uppercase with explicit letter-spacing (`0.06em`).

## Layout & Spacing

The layout is built on an **Instrumental Fluid-Grid** framework anchored to an 8px base rhythm (with 4px sub-intervals for tight diagnostic widgets). The system maintains maximum viewport efficiency to support multi-layered investigations without requiring excessive vertical scrolling.

### Breakpoints & Responsive Behavior
- **Desktop (≥ 1280px):** 12-column dynamic matrix. Supports a tri-panel investigative workbench: persistent primary rail (left), exploratory analytical canvas (center), and collateral school diagnostic inspector (right).
- **Tablet (768px - 1279px):** 8-column matrix. The school diagnostic inspector transitions into a responsive slide-over drawer; secondary metrics drop into horizontal tabbed disclosures.
- **Mobile (< 768px):** 4-column column flow. Layout shifts to vertical triage mode: interactive micro-cards, collapsed analytical controls, and bottom-sheet drawers for deep risk drivers.

### Density Tiers
- **Comfort:** Reserved for executive summaries and the public-facing diagnostic portal (24px gutter, 24px cell padding).
- **High-Density:** Standard operational view for analysts and regional coordinators (16px gutter, 12px cell padding, compact inline data tables).

## Elevation & Depth

This design system deliberately avoids heavy skeuomorphic drop-shadows or floating visual noise. It achieves depth primarily through **Tonal Layering** combined with **Engineered Hairline Outlines** (`1px solid #E2E8F0`).

### Surface Stack System
- **Level 0 (Canvas Base):** `#F8FAFC` — Foundation backing for application views.
- **Level 1 (Cards & Data Nodes):** `#FFFFFF` — Inset by hairline border `#E2E8F0`. No shadow at rest.
- **Level 2 (Hover & Interactive Focus):** `#FFFFFF` with shadow: `0 4px 12px -2px rgba(15, 23, 42, 0.06), 0 2px 4px -1px rgba(15, 23, 42, 0.03)` and border transition to `#CBD5E1`.
- **Level 3 (Diagnostic Drawers, Modals & Inspector Panels):** `#FFFFFF` with shadow: `0 20px 25px -5px rgba(15, 23, 42, 0.1), 0 8px 10px -6px rgba(15, 23, 42, 0.05)`.
- **Telemetry Float (Asistente FARO Node):** `#0F172A` resting surface accented with ambient beacon bloom: `0 0 0 1px rgba(2, 132, 199, 0.4), 0 8px 24px -4px rgba(2, 132, 199, 0.35)`.

## Shapes

The design system employs **Soft Minimal Radii (Level 1)** to maintain the structural tone of analytical instruments and data sheets:

- **Data Cards, Panels, Modals:** `0.375rem` (6px) or `0.5rem` (8px). Delivers a modern, squared look that preserves screen real estate in dense grid layouts.
- **Controls, Inputs, Action Buttons:** `0.25rem` (4px) to `0.375rem` (6px).
- **Status Pills, Micro-Badges & Driver Chips:** Fully rounded / pill-shaped (`9999px`) to create an immediate optical distinction between interactive operational containers and contextual classification markers.

## Components

### Precision Data Cards
- Container: Background `#FFFFFF`, border `1px solid #E2E8F0`, corner radius `6px`.
- Header: Left-aligned title in `headline-sm`, trailing operational metadata in `label-micro-mono` (e.g., CCT ID, confidence score, update timestamp).
- Metric Display: High-contrast numerical readouts in `JetBrains Mono` paired with small directional trend indicators (`+2.4%`, `-0.8%`).

### Interactive Risk Indicator Chips
- High Risk: Background `#FFF1F2`, border `1px solid #FECDD3`, text `#E11D48`.
- Medium Risk: Background `#FFFBEB`, border `1px solid #FDE68A`, text `#D97706`.
- Low Risk: Background `#ECFDF5`, border `1px solid #A7F3D0`, text `#059669`.
- Format: A left-aligned `6px` solid status beacon dot followed by all-caps text in `label-micro-mono`.

### Diagnostic Driver Matrix Badges
- Represent each of the 6 drivers (Pobreza, Inseguridad, Infraestructura, Conectividad, Estrés Hídrico, Calidad del Aire).
- Renders as a compact tag containing a calibrated driver color square or progress bar showing the calculated impact index (0.0 to 10.0 scale).

### Buttons & Operational Actions
- **Primary:** Background `#0F172A`, text `#FFFFFF`, radius `4px`, hover state `#1E293B`. For high-level operational triggers (e.g., "Generar Dictamen", "Exportar Censo").
- **Beacon Action:** Background `#0284C7`, text `#FFFFFF`, hover `#0369A1`. Used for analytical exploration tools (e.g., "Ejecutar Simulación", "Filtrar Matriz").
- **Subtle / Secondary:** Background `#FFFFFF`, border `1px solid #CBD5E1`, text `#334155`, hover background `#F8FAFC`.

### Form Controls & Query Inputs
- Inputs use an inset background `#FFFFFF`, border `1px solid #CBD5E1`, radius `4px`.
- Active focus state: Hairline ring transition using the Beacon Cyan `#0284C7` (`ring-2 ring-sky-500/20 border-sky-600`).
- Placeholders and input text set in `Inter` (`13px`); numerical search inputs set in `JetBrains Mono`.

### School Diagnostic Inspector (Side Sheet)
- A persistent right-hand intelligence drawer that activates upon selecting any school record.
- Houses the comprehensive multi-driver risk score, Asistente FARO predictive recommendations, local infrastructure logs, and historical risk progression graphs.

### Floating Asistente FARO Intelligence Node
- Form Factor: Fixed floating circular dock element or compact pill pinned to the lower-right workspace (`bottom: 24px`, `right: 24px`).
- Styling: Deep Navy surface (`#0F172A`) framed by an illuminated Beacon Cyan micro-border (`#38BDF8`).
- Glow: Ambient radial dispersion (`box-shadow: 0 0 20px rgba(2, 132, 199, 0.25)`).
- Iconography: Precise algorithmic sparkle/beacon geometry paired with `JetBrains Mono` status badge: `ASISTENTE FARO // ONLINE`.
- Behavior: Expands smoothly into an analytical natural-language prompt interface that accepts investigative queries (e.g., *"¿Qué planteles en la Región Norte combinan estrés hídrico y rezago crítico?"*).