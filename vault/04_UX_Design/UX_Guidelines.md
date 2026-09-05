---
id: DOC-UXGUIDE
title: "UX Guidelines"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["REQ-002", "vault/01_Product/PRD_General_Materia"]
traces_down: ["vault/04_UX_Design/Accessibility", "US-215a", "US-215b"]
last_reviewed: "2026-09-05"
tags: [ux, design-system, accesibilidad]
---

# UX Guidelines — FARO

> Sistema de diseño. → [[vault/04_UX_Design/_index]] · [[vault/04_UX_Design/Accessibility]]

## Para qué sirve este documento

Para poder **decir si algo cumple o no cumple**. Marina García lo pidió al ejecutar el caso 3.1 de
`US-215a` con la frase exacta del problema: *"sin paleta declarada no hay criterio de aceptación — no
puedo decir si un contraste cumple si nadie definió el estándar."* Tenía razón, y el documento llevaba
`source_of_truth: true` con las tablas vacías, que es peor que no existir.

## Principios

1. **Un hueco visible vale más que un número creíble.** Donde no hay dato se marca `SIN_DATO`
   explícito, nunca cero ni espacio en blanco. Es la regla de cobertura parcial del proyecto y ya nos
   costó `BUG-017`, `BUG-031` y `BUG-047`: un número que significa otra cosa es más caro que un hueco
   señalado.
2. **El driver dominante es la unidad de lectura.** Dos escuelas con el mismo riesgo reciben
   recomendaciones distintas; la interfaz existe para hacer visible ese *porqué*, no sólo el ranking.
3. **Ningún tablero abre sin filtrar.** Todo filtro de ciclo llega preseleccionado al ciclo vigente
   (`BUG-047`). Una métrica agregada sin filtro suma ciclos y miente sin marcar error.
4. **Se declara lo que se hereda.** FARO no adopta una identidad visual propia: usa los temas por
   defecto de sus dos herramientas. Eso es una decisión, y está abajo con sus consecuencias.

## Accesibilidad — el estándar

**WCAG 2.1 nivel AA.** Es el criterio de aceptación de todo caso de contraste en
`US-215a` y `US-215b`:

| Elemento | Mínimo | Nota |
|---|---|---|
| Texto normal (< 18.66 px `bold` o < 24 px) | **4.5 : 1** | El caso más común: etiquetas, tablas, subtítulos de KPI |
| Texto grande (≥ 18.66 px `bold` o ≥ 24 px) | **3 : 1** | Cifras de tarjeta `big_number` |
| Componentes de interfaz y estados de foco | **3 : 1** | Bordes de control, indicador de foco |

**Se mide sobre el color y el fondo *efectivos* del nodo, no los declarados**, y **en los dos temas**
—claro y oscuro—: un hallazgo puede estar peor en claro que en oscuro, como pasó con `BUG-049`, así
que fijar un tema por defecto no resuelve nada.

El indicador de foco de Superset es un `box-shadow`, no un `outline` —que viene en `none`—. Quien
audite mirando sólo `outline` concluirá falsamente que no hay indicador. Verificado por Monserrat
Miranda en el caso 3.3 de `US-215b`.

## Tokens — lo que FARO declara y lo que hereda

**FARO no declara paleta, tipografía ni escala de espaciado propias.** Se verificó al escribir esto:
no hay un solo color en `superset/**`, ningún `color_scheme` en los YAML de tablero y ningún
`.streamlit/config.toml` con tema. Todo sale de los valores por defecto de dos herramientas.

| Capa | De dónde salen los tokens |
|---|---|
| Los 10 tableros (DB-01…DB-10) | Tema por defecto de **Superset 6.1.0** |
| FARO Web (`src/frontend/`) | Tema por defecto de **Streamlit** |

**Esto es una decisión, no un olvido**, y se toma con la fecha encima: adoptar una identidad propia a
dos días del *code freeze* significaría re-teñir 103 charts y 10 tableros sin ninguna prueba que lo
respalde. El costo supera el beneficio y el riesgo de romper algo visible en la demo es real.

### Consecuencia para la aceptación

De aquí sale la regla que faltaba, y aplica a `US-215a` y `US-215b`:

- **Elemento que FARO sí escribe** —notas en markdown dentro de los tabs, subtítulos de KPI, textos
  del panel de ML en Streamlit— que no llegue al umbral: **es un defecto y bloquea**.
- **Elemento que FARO hereda del tema de la herramienta** —el acento del tab activo de Superset, su
  paleta de series, el `<html>` sin `[lang]` que emite su shell— que no llegue al umbral: **se
  registra como limitación conocida con su medición**, y **no bloquea el cierre de la historia**.
  Corregirlo es cambiar la imagen o un *upstream*, y eso vive en `REQ-005`, no en `REQ-002`.

Los dos hallazgos abiertos caen del lado heredado y quedan así clasificados:

| Bug | Medición | Origen | Efecto |
|---|---|---|---|
| `BUG-049` | Etiqueta del tab activo de DB-05: **4.07 : 1** oscuro · **3.55 : 1** claro | Color de acento de Superset | Limitación conocida · no bloquea `US-215b` |
| `BUG-050` | Lighthouse 93 en DB-03: contraste y `<html>` sin `[lang]` | Tema y shell de Superset | Limitación conocida · no bloquea `US-215a` |

Ambos siguen `open` en [[vault/06_Quality_Testing/Bug_Register]] — clasificarlos no es cerrarlos.
Quedan como deuda declarada para después de la demo, y se dicen en voz alta si alguien pregunta por
accesibilidad el 9-sep: es más defendible una limitación medida que un silencio.

## Componentes base

FARO no define componentes propios: usa los de Superset y Streamlit tal como vienen. Lo único que sí
es nuestro y sí tiene contrato es el comportamiento:

| Componente | Contrato de estado |
|---|---|
| Filtro de ciclo | Abre **preseleccionado** en el ciclo vigente, resuelto contra los datos (`default: ultimo_ciclo`), con `valor_por_defecto` como respaldo estático (`BUG-047`) |
| Métrica sin dato | `SIN_DATO` explícito con la causa y la historia que lo cierra. **Nunca** cero, nunca vacío (`US-207`, `DEC-015`) |
| Enlace de drill-down | `<a href>` con los filtros del destino preseleccionados por índice y valores citados con `%27`; alcanzable con `Tab` y activable con `Enter` |
| Tarjeta de cifra | Cifra grande + subtítulo que dice **el grano y el ciclo** que la cifra representa |

## Movimiento

No se usa animación en tableros ni en FARO Web. No es una omisión: una transición sobre una cifra que
cambia al filtrar dificulta leer el valor real, y no hay presupuesto de prueba para verificarlo en
diez tableros. Si en algún momento se agrega, respeta `prefers-reduced-motion`.

## Qué falta y quién lo cierra

Nada de esto bloquea el *freeze*. Queda escrito para no volver a descubrirlo:

- **Identidad visual propia** (paleta, tipografía, escala) — post-demo, y con la decisión de si vale
  la pena teñir Superset.
- **`BUG-049` y `BUG-050`** — corrección real del contraste heredado, que es cambio de imagen (C5).
