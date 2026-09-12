---
project: "FARO"
date: "2026-09-11"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — barrido del estado de US-621, retiro del PDF del criterio de cierre y precisión del alcance de la leyenda. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011", "DEC-024"]
tags: [devlog, equipo-3, ux, s7, us-621]
---

# DevLog — 2026-09-11 — Retiro del PDF y alcance de la leyenda (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]]

## Contexto

Juan Macías propuso sustituir `FARO_UX_UI_Guide.pdf` por `mockups/Design_Tokens_Stitch.md` como
entregable final. Se acepta el fondo —retirar el PDF— y se rechaza el archivo propuesto. Nueva
**§7.ter** del plan.

## El PDF se retira

Sus tres razones son correctas: el `.md` está versionado y sincronizado con los mockups, el Equipo 5
copia valores exactos en vez de transcribirlos, y un PDF exige sincronización a mano.

Se añaden dos que pesan más que el mantenimiento: **el PDF no responde a ninguno de los hallazgos del
profesor** —experiencia, gráficas, storytelling, componentes, chat y ML; ninguno sobre documentación—
y `DEC-024` ya fijó que las únicas compuertas son rama personal, PR, CI, una aprobación humana y QA
sobre la candidata. Un PDF no es ninguna.

Retirado de la §7, la §8 y el punto 2 del criterio de cierre de la §14, más el `_index` del paquete.

## Lo que no se aceptó, y por qué importa la distinción

`Design_Tokens_Stitch.md` **no puede ser el entregable de un criterio de cierre**: su frontmatter es
el YAML crudo de Stitch, sin `id`, `owner` ni `status`, así que incumple la regla 2 y
`Definition_of_Filed`; su propio encabezado lo declara *"no es un artefacto canónico del vault"*; y
por esa misma nota **el sistema de color de datos no vive ahí**, sino en `03_Visual_Identity.md` §3.

O sea que el archivo propuesto como guía de identidad no contiene la parte de la identidad que esta
historia más necesita. Un anexo no puede ser la guía.

La guía ya existía: `03_Visual_Identity.md`, con `id`, `owner`, `status` y trazas. El anexo se queda
como anexo, y le falta frontmatter propio y quedar listado en `mockups/_index.md`, que tampoco existe
—regla 4, con los 7 mockups dentro.

## La leyenda: dos precisiones que faltaban

**Dónde se escribe.** Dentro de `02_Data_Visualization_Spec.md`, como sección propia. No un documento
nuevo: la regla 1 prohíbe abrir un archivo para algo que pertenece a un canónico existente. Queda
como ítem explícito de la entrega del viernes de Monserrat, que la §8 no listaba.

**Alcance: por gráfica, no por pantalla.** Hay gráficas en P2, P3, P4, P5 y P6 —matriz de casos,
pista del índice, comparativa de los 6 drivers, gráfica de unidades del Top 3 y las reutilizadas en
el Explorador—. Se escribe explícito porque la primera lectura del equipo fue acotarla a dos
pantallas, lo que dejaba tres sin cubrir.

## Lo que este cambio no toca

`03_Visual_Identity.md` conserva tres menciones al PDF. **No se editó a propósito:** es el entregable
de Juan, la §13 prohíbe modificar el de otro sin coordinación, y está trabajándolo ahora mismo —
tocarlo le crearía un conflicto. Va en su lista de cambios.

## Pruebas ejecutadas

```
git merge origin/main                        → sincronizada en 7444543, sin conflictos
python vault/_Meta/scripts/vault_lint.py .   → Vault limpio
```

## Siguiente acción recomendada

Avisar al PO: es un cambio a un criterio de cierre de `US-621` y el *go/no-go* es suyo.
