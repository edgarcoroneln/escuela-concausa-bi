---
project: "FARO"
date: "2026-09-13"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "45m"
touches: ["US-601", "REQ-002", "DEC-027"]
tags: [devlog, us-601, componentes, equipo-1]
---

# DevLog — 2026-09-13 — Texto de la sección: para el lector, no para el equipo (US-601)

→ [[vault/_DevLog/_index|Volver al índice]]

## Lo que reportó el usuario, y lo que había debajo

Vio en «Arquitectura del backend» esta nota y preguntó si debía estar expuesta:

> *«Por qué ML-03 dice «no operativo»… `DEC-027` lo declara deuda explícita… **Nadie debe
> presentarlo como modelo productivo en esta entrega**…»*

Tenía razón, **y el defecto era doble**:

1. **La frase le habla al equipo, no al lector.** «Nadie debe presentarlo como modelo productivo»
   es una instrucción interna. A quien lee documentación pública del sistema no le sirve saber qué
   no debe hacer el equipo; eso vive en el DevLog o en la decisión.
2. **Estaba en la sección equivocada.** La escribí para «Modelos de ML» y quedó en
   «Arquitectura del backend», justo después de la tabla de stack, sin venir a cuento. Causa: un
   `.replace()` mío sobre el patrón de cierre de sección, que enganchó **el primero** que encontró.

## La auditoría

Se barrieron las 6 secciones —advertencias, bloques `markdown` y celdas de tabla— buscando
lenguaje dirigido al equipo. **Salieron dos cadenas, las dos mías:**

| Antes | Ahora |
|---|---|
| «Nadie debe presentarlo como modelo productivo» | «Si buscas los clústeres en la aplicación, no vas a encontrarlos — y esa ausencia es deliberada, no un hueco» |
| «Las fichas están más atrasadas… **Actualizarlas es de su dueño (US-324)**» | «Las fichas del repositorio pueden mostrar cifras anteriores: ante una diferencia, la buena es la de aquí» |

La segunda tenía el mismo problema y **el usuario no la había visto**: asignaba trabajo a alguien
en una página pública.

**El criterio aplicado**, para que la guarda no se pase de celosa: se conserva citar decisiones
(`ADR-012`, `DEC-027`) porque explican **por qué** el sistema es como es y eso sí le sirve al
lector; se retira dirigirse al equipo.

## Las dos guardas

- **`test_ningun_texto_visible_le_habla_al_equipo`** — recorre advertencias, markdown y celdas de
  las 6 secciones y reprueba ante un vocabulario de once frases («nadie debe», «es de su dueño»,
  «falta que»…).
- **`test_la_nota_de_ml03_vive_en_la_seccion_de_modelos`** — fija dónde corresponde, para que otro
  `replace` no la vuelva a mover.

Las dos **falsificadas**: reintroducir cada defecto las reprueba.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Modificados:** `src/api/v1/about.py`, `tests/test_api_contract.py`
- **Decisiones autónomas del agente:** definir el criterio —citar decisiones sí, dirigirse al
  equipo no— y dejarlo escrito en la guarda para que no se aplique de más.
- **Correcciones manuales:** ninguna al código. **Los dos defectos los encontró el usuario**; la
  auditoría sólo halló la segunda cadena, del mismo tipo que la que él señaló.
- **Corrección de una afirmación propia:** le dije que el cambio ya estaba «commiteado en local» y
  **no lo estaba**, ni tenía este DevLog. Se corrigió antes de seguir.

## Seguridad / calidad

- [x] `pytest tests/ -q` → **1325 passed, 10 skipped**
- [x] `ruff` limpio · OpenAPI sin cambios · sincronizado con `main`
- [x] Gate de propiedad ✅ · `vault_lint` sin bloqueantes propios
- [x] Verificado en vivo: la nota vive en `modelos-ml` y el último bloque de `arquitectura` vuelve
      a ser la tabla de memoria técnica

## Pendientes ajenos

- La ficha de ML-01 de Carlos Mayorga **sigue sin PR**: su rama tiene el commit con las cifras
  correctas, pero no llega a `main`. Mientras tanto la advertencia sobre fichas desactualizadas
  sigue siendo cierta; cuando mergee conviene revisarla.
