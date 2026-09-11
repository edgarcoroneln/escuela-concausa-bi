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

<!-- Diagrama o tabla del recorrido completo: Login → P1 → P2 → P3 → P4 → P5 → P6.
     Incluir los caminos de regreso y qué pasa si el usuario entra directo a una URL. -->

## 2. Ficha por pantalla

<!-- Una subsección por pantalla, con la misma estructura para las siete: -->

### Mockup 0 — Login

- **Objetivo:**
- **Contenido:**
- **Botones y CTA:**
- **A dónde conecta:**
- **Estados** (carga, error, sin sesión):

### Pantalla 1 — Entrada

### Pantalla 2 — Panorama de las escuelas en riesgo

### Pantalla 3 — Selección de caso

### Pantalla 4 — Expediente de una escuela

### Pantalla 5 — Conclusión Top 3

### Pantalla 6 — Exploración de otras escuelas

## 3. Filtros

<!-- Cuáles aparecen en cada pantalla. Los tres obligatorios (ciclo, entidad, nivel) están
     soportados hoy por /escuelas y /kpis. Cualquier filtro extra debe existir ya en la API. -->

## 4. Walkthrough inicial

<!-- Un único walkthrough, sencillo y breve. Cuántos pasos, qué dice cada uno, cómo se cierra
     y si vuelve a aparecer. Debe mencionar que el chat está disponible en todo el recorrido. -->

## 5. Pop-up de la exploración

<!-- Uno solo, la primera vez que se entra a la Pantalla 6. -->

## 6. Comportamiento del chat

<!-- Ubicación del botón flotante, apertura y cierre, qué ocurre al navegar entre pantallas.
     La lógica funcional es del Equipo 2 (US-611): aquí sólo se define el comportamiento UX.
     Mientras P-03 siga abierta, llamarlo "el chat". -->

## 7. Nombres propuestos para la exploración posterior

<!-- 2-3 opciones comprensibles. No debe llamarse "ML" de cara al usuario.
     Marina elige una en el gate. -->

## 8. Estados vacíos, de error y SIN_DATO

<!-- Qué ve el usuario cuando un driver no tiene dato, cuando la escuela no tiene predicción
     (tiene_prediccion = false) o cuando la API responde 401. -->
