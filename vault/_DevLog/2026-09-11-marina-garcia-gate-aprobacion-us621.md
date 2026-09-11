---
project: "FARO"
date: "2026-09-11"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — verificación y aprobación de los cuatro entregables de UX/UI, más cuatro ajustes al plan. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011", "ADR-012", "DEC-024", "US-641", "US-651", "US-601"]
tags: [devlog, equipo-3, ux, s7, us-621, gate]
---

# DevLog — 2026-09-11 — Gate de UX/UI: los cuatro entregables aprobados (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]]

## Contexto

Con los PRs de Oscar Quiroz (#319), Monserrat Miranda (#318) y Juan Macías (#316) mergeados, el gate
de UX/UI aprueba los cuatro entregables de la §7. Se verificó **la versión en `main`**, no la que se
había revisado en rama — es la diferencia que en este frente ya falló tres veces.

## Qué se verificó antes de firmar

| Comprobación | Resultado |
|---|---|
| "Watson" en los cuatro documentos | Sólo como prohibición explícita |
| `prioritari*` / `prioridad` como vocabulario | Cero ocurrencias |
| `SIN_DATO` y *nivel de atención* | Presentes donde corresponde |
| Regla de `N` en los 7 mockups | Cero números tecleados |
| Leyenda §7.bis | Referenciada en las **cinco** pantallas con gráfica |
| `vault_lint.py` | Limpio |

Los cuatro pasan a `status: approved` y llevan el sello del gate con fecha y contra qué versión.
Registro en la §14 del plan.

## Lo que se aprueba con un hueco declarado

`03_Visual_Identity.md` se aprueba **sin la auditoría formal de contraste WCAG 2.1 AA**, que su
propia §6 declara pendiente. `ADR-011` §4 la hace no negociable, así que la aprobación cubre diseño y
especificación, **no** conformidad de accesibilidad.

Se aprueba igual, y con el hueco escrito, porque el Equipo 5 ya está implementando con esos tokens:
retener el documento no haría la auditoría más rápida, y sí dejaría a Diana trabajando contra algo
sin aprobar. La verificación pertenece a `US-651`.

## Cuatro ajustes al plan

**Criterio 28 ampliado a los bloques D3 de la §5.bis.** Decidido tras la §8.4 de Monserrat, que
señaló que *"toda gráfica"* no distingue superficies. Se extiende con la precisión que lo abarata: la
leyenda puede vivir en el bloque `markdown` adyacente, que es el mecanismo que el Equipo 1 **ya usa**
en la sección `cubos`. Sin esa frase, el criterio obligaría a añadir un campo a tres esquemas de
Pydantic a dos días del cierre; con ella, es contenido.

**Nueva §9.bis: cómo se verifica cada criterio.** Los 29 no se comprueban igual. Se clasifican en
verificables en el artefacto (15), en la candidata desplegada (10) y por pasada humana (4). Los de
forma C son los que más valen y los que más fácil se saltan: el criterio 1 es literalmente lo que el
profesor evaluó el 9-sep y no hay prueba automática que lo cubra.

**Ficha del Mockup 0, tercera corrección.** `ADR-012` quedó `accepted` y dejó falsa la frase *"no
cambia la lógica funcional"*: la sesión pasó a cookie `httpOnly` por proxy, el frontend dejó de
manejar tokens y apareció `POST /auth/logout`. Lo visible no cambia —sigue siendo el botón de
Google—, pero la ficha afirmaba algo que dejó de ser cierto.

**Sello de aprobación en la §14** con la tabla de qué se aprobó contra qué PR.

## Lo que queda fuera de este frente

- **Punto 3 del cierre:** el handoff a E5 ya ocurrió de hecho —Diana aplica los tokens y conectó los
  tabs del expediente a la API real— pero **nadie lo ha declarado**, y no lo puede declarar este
  frente: la aceptación es afirmación de quien recibe.
- **Punto 4:** `US-651` sigue `planned` y sin desglose, a dos días del corte.
- `US-641` y `US-651` figuran `planned` en `Execution_Status` pese al avance real. El tablero del PM
  se deriva de ese archivo.

## Pruebas ejecutadas

```
git merge origin/main                        → 102 commits integrados, sin conflictos
python vault/_Meta/scripts/vault_lint.py .   → Vault limpio
```

## Siguiente acción recomendada

Pedir a Diana que declare el handoff, a Edward el desglose de `US-651`, a Edgar la actualización de
`Execution_Status`, y a Héctor y Manuel la leyenda de sus tres bloques D3 más el sync antes del PR.

---

## Addendum — *Cómo funciona* pasa a declararse como superficie

**Hallazgo de Marina al revisar `03_Visual_Identity.md` a mano.** El preview de *Cómo funciona*
existía en `mockups/` y estaba indexado, pero **ninguna de las dos tablas lo declaraba como
superficie**: en la §7 del documento de Juan y en `mockups/_index.md` aparecía en el mismo grupo que
`Guia_Identidad_Visual` y `Design_Tokens_Stitch`, o sea catalogado como material de apoyo.

Los dos documentos eran consistentes entre sí, y los dos decían lo mismo: *esto no es una pantalla*.

### Por qué era un hueco y no un error de Juan

Él seguía el plan al pie de la letra: la §5.bis dice *"no es una octava pantalla"* y *"no necesita
mockup propio"*, y citó esa frase para justificar dónde lo puso. **La redacción corta era mía.**

Lo que esa redacción no distinguió son dos cosas distintas: que algo **no entre al recorrido
narrativo** —correcto, la historia son 7 pantallas— y que **no se declare como superficie del
producto**. Y *Cómo funciona* sí lo es: el usuario la ve, tiene overlay, acceso desde P1 y desde el
glosario, y responde a uno de los hallazgos del profesor.

La asimetría lo delataba: **Oscar sí la trata como superficie**, con sección propia en su mapa de
navegación —acceso, comportamiento y retorno—, mientras Juan la dejó como archivo suelto. Dos
documentos del mismo frente describiendo la misma cosa con estatus distinto.

### Qué se hizo

Fila **`S`** en las dos tablas —identificador propio y no un `7`, para no romper el recorrido
P0–P6—, con una nota que explica la distinción y, sobre todo, **le dice al Equipo 5 dónde está cada
pieza**: comportamiento en `01_UX_Architecture.md` §1, alcance y dependencia en `PLAN_TRABAJO.md`
§5.bis, reglas de forma de los bloques D3 en `02_Data_Visualization_Spec.md` §8.4, y la decisión de
claro/oscuro en la §1 de `03_Visual_Identity.md`. Se eliminó la entrada duplicada de la tabla de
soporte.

**Son dos archivos de Juan Macías.** Se editan desde el gate y se le avisa, que es lo que pide la
§13 —coordinación, no permiso—; queda dicho en ambas notas quién los tocó y por qué.

### Lo que sí resolvió Juan y conviene no perder de vista

La decisión de claro/oscuro que quedaba pendiente: fijó que el lienzo analítico es **siempre claro** y
que el slate profundo se usa sólo como acento en componentes puntuales, nunca como fondo de página.
Conclusión: los tres bloques D3 del Equipo 1, forzados a `color-scheme: light`, **no chocan** —entran
sobre el mismo lienzo—. Y alineó el color de Jalisco con el que Manuel ya usaba en `US-601`.
