---
project: "FARO"
date: "2026-09-10"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — revisión de reglas vigentes, corrección de la propuesta de UX/UI y alta de la estructura del frente en el vault. Sin código productivo."
touches: ["US-621", "REQ-002", "DEC-019", "DEC-022", "BUG-063", "US-206"]
tags: [devlog, equipo-3, ux, storytelling, s7, us-621, propuesta]
---

# DevLog — 2026-09-10 — Estructura del frente de UX/UI y storytelling (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]] ·
[[vault/12_Roadmap_Sprints/Plan_Recuperacion_2026-09-09]]

## Contexto

`DEC-022` reabrió el desarrollo el 9-sep tras la revisión del profesor y creó el **Equipo 3 · UX/UI y
storytelling**, que me toca liderar con Oscar Quiroz, Monserrat Miranda y Juan Macías. Tres de los
ocho hallazgos del profesor caen en este frente: experiencia visual no satisfactoria, gráficas sin
valor comunicado y ausencia de una historia de negocio.

Traía una propuesta de plan escrita antes de conocer la reapertura. Esta sesión la contrasta contra
las reglas vigentes del repositorio y la deja como propuesta trazable, **sin modificar ningún
documento canónico existente**.

## Qué se hizo

Alta de `vault/04_UX_Design/FARO_Storytelling_UX/` con seis archivos: el plan maestro, el `_index` de
la carpeta y un entregable por integrante, todos con frontmatter, ID y trazas. `mockups/` queda
sembrada para los siete PNG del viernes.

## Ocho correcciones a la propuesta original

Registradas en la §0 del plan, no aplicadas en silencio:

| # | Hallazgo | Corrección |
|---|---|---|
| 1 | La propuesta ubicaba la carpeta en `04_UX_Design/` **en la raíz del repositorio** | Movida a `vault/04_UX_Design/FARO_Storytelling_UX/`. La ruta raíz no está en el verde, amarillo ni comunes de nadie: `check_ownership.py` habría reprobado el PR de los cuatro, no sólo el mío |
| 2 | Sin ID | `US-621` · `REQ-002`. Sin ID no pasa el regex del título de PR ni `Definition_of_Filed` |
| 3 | Checkpoint jueves 19:00 y entrega viernes 15:00 | Gate jueves 18:00 y entrega al Equipo 5 el viernes 15:00, conforme a `Plan_Recuperacion_2026-09-09`. El corte final no lo fija este frente |
| 4 | "Equipo ejecutor: Oscar, Juan y Monse" | Equipo 3 completo con líder, según `DEC-022` y `ownership.yml` |
| 5 | `prioridad` obligatoria en dos pantallas | Condicionada a `P-01`: no existe en el contrato v1 |
| 6 | Etiqueta Alto/Medio/Bajo "según la definición oficial" | Condicionada a `P-02`: esa definición no existe |
| 7 | "Watson" como nombre del chat | Condicionado a `P-03`: el nombre no aparece en ningún documento del repositorio |
| 8 | "Las gráficas se construyen en Front" | Condicionado a `P-04`: sustituye `US-206` y es cambio de arquitectura |

## Verificación contra el contrato de la API

Se cotejó cada necesidad del diseño contra `api/openapi.v1.json`. El mapeo quedó en la §10 del plan y
es lo que hace exigible el guardarraíl de "no se dibuja lo que no existe".

**Construible hoy:** el conjunto de escuelas en riesgo por `GET /api/v1/escuelas` con
`order_by=indice_riesgo`; los seis drivers por `GET /api/v1/escuelas/{cct}` (`d1`…`d6`,
`indice_completitud_drivers`, `es_estimado_por_grupo`); recomendación y driver dominante por
`GET /api/v1/predicciones/{cct}`; la evidencia del dominante por `/explicacion`; y los tres filtros
obligatorios (`ciclo`, `cve_ent`, `nivel`).

**No construible hoy:** `prioridad` no aparece en `EscuelaOut`, `EscuelaDetalleOut`, `PrediccionOut`
ni `ExplicacionSHAPOut`. Es `P-01`, y arrastra a `BUG-063`: el corte de `ALTA` usa `0.60` contra un
máximo real de `0.5717`, así que exponer el campo sin decidir el corte deja la tarjeta en cero.

## El número de escuelas en riesgo

Verificado que los tres cubos de `dbt/models/gold/` en `main` ya calculan con `>= 0.5` (`DEC-019`), y
que la QA del 2026-09-08 de Monserrat Miranda midió **KPI-04 = 7 en DB-02 contra producción**. Lo que
**no** está confirmado es que `GET /api/v1/kpis` devuelva ese mismo 7 — es otra superficie y es la que
consumirá Front. Queda como `P-05`. Hasta entonces los entregables escriben "N escuelas en riesgo".

## Decisiones

- El plan entra en `status: draft`. No desplaza a `UX_Guidelines.md`, `Screen_Specs.md` ni
  `Manual_Usuario_Dashboards.md` mientras el PO no cierre `P-06`.
- `Accessibility.md` **no se sustituye en ningún caso**: la identidad nueva debe cumplirlo.
- Lo que no se resuelva de `P-01` a `P-05` se documenta como recorte explícito en vez de dibujarse
  como si existiera.

## Preguntas abiertas

Las seis peticiones de la §11 del plan, todas con dueño fuera de este frente. La que urge es `P-06`:
sin ella, Juan no puede arrancar la identidad visual sin chocar con `UX_Guidelines.md`, que está
`approved` y marcado `source_of_truth`.

## Riesgos

- Si `P-04` no se resuelve, el Equipo 5 no puede implementar el diseño sin contradecir `US-206`.
- `BUG-063` sigue abierto y afecta a la pantalla del diferenciador.
- La ventana es corta: el gate es hoy a las 18:00 y la entrega al Equipo 5 mañana a las 15:00.

## Pruebas ejecutadas

```
git merge origin/main          → fast-forward a 27e1f71, sin conflictos
python vault/_Meta/scripts/vault_lint.py .   → Vault limpio
```

## Siguiente acción recomendada

Enviar las seis peticiones al PO y al grupo. Cada integrante toma su archivo en su propia rama para
el gate de las 18:00.
