---
project: "FARO"
date: "2026-09-05"
author_human: "Monserrat Xcaret Miranda Olivas"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "sesión: defecto de contraste del link de DB-05 bajo DEC-016 y §3 medido por primera vez sobre DB-08"
touches: ["US-215b", "US-214b", "US-213", "REQ-002", "BUG-051", "BUG-056", "DEC-016"]
tags: [devlog, accesibilidad, superset, bi, qa, celula-2]
---

# DevLog — 2026-09-05 — El link que sólo fallaba en claro, y el §3 que sólo cubría un tablero

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB05_DB08]]

## Contexto

Con el PR #228 ya mergeado, entraron a `main` **DEC-016** y el cierre de US-215a de Marina García.
De ahí salieron dos cosas para esta célula: un defecto en un archivo propio que ella reportó
explícitamente, y —al revisar el propio plan de pruebas contra la nueva regla— un hueco que no era
de nadie más.

## 1. El `<a>` de `link_db08`: defecto real, y por qué no se vio antes

Marina lo dejó escrito en sus *Hallazgos para otros*: `db05_cubo_driver.sql` tenía el mismo link sin
estilo que ella acababa de corregir en DB-03/DB-04.

**No se dio por bueno su número: se midió el propio en DB-05**, sobre color y fondo efectivos y en
los dos temas, como exige DEC-016.

| | Antes | Después |
|---|---|---|
| Claro | `#2893b3` sobre `#f5f5f5` → **3.26 : 1** ❌ | `#000000` → **19.26 : 1** ✅ |
| Oscuro | `#2893b3` sobre `#000000` → 5.91 : 1 ✅ | `#ffffff` → **21 : 1** ✅ |
| Subrayado | `none` | `underline` |

Coincidió exactamente con lo que ella midió en los suyos, lo que confirma que era el mismo defecto
de origen y no una coincidencia.

**Por DEC-016 este sí bloqueaba**, a diferencia de BUG-051: el ancla la escribe FARO, así que FARO
responde por su contraste. El arreglo es el suyo —`color:inherit` + subrayado— y no se buscó otro
azul porque ella ya demostró que no existe: pasar 4.5 : 1 contra el gris de la celda exige
luminancia baja y contra el fondo oscuro exige alta, y los rangos no se cruzan.

### Las dos razones por las que el barrido del 4-sep no lo cazó

Vale dejarlas escritas, porque las dos son trampas de método y no descuidos puntuales:

1. **Se midió primero el tema oscuro**, que es exactamente donde el defecto no aparece.
2. **La tabla que contiene el link está debajo del pliegue.** Sus 30 anclas ni siquiera existen en
   el DOM hasta hacer scroll: Superset las renderiza perezosamente. El barrido recorrió el viewport
   inicial y midió 34 nodos; con la tabla cargada, DB-08 llega a 1209.

Un barrido de contraste que sólo mira lo visible al abrir, y en un solo tema, da un verde que no
significa nada.

### Guarda

`test_el_link_db08_no_depende_del_color_del_tema` en `tests/test_semantic_db05_db08.py`, gemela de
la de Marina y reutilizando su helper `_bloque_del_link()`. **Validada reintroduciendo cada defecto
por separado** —quitar `color:inherit`, quitar el subrayado—: falla con cada uno y pasa restaurada.

> La primera validación dio **verde con los dos defectos puestos**, lo que habría dejado pasar una
> guarda que nunca se probó. La causa no era el test: la sustitución modificaba la primera aparición
> de `style="color:inherit…"` del archivo, que está **en el comentario** escrito unas líneas antes,
> dejando el SQL intacto. Al apuntar al ancla real, la guarda caza los dos.

## 2. El §3 declaraba dos tableros y medía uno

El plan decía "Accesibilidad (DB-05 **y DB-08**)", pero la evidencia lo delataba: el caso 3.2 citaba
*"6/6 tabs y 3/3 filtros globales"*, y **DB-08 no tiene tabs y tiene cinco filtros**. Los casos de
§2 se habían cerrado por API y datos, así que **DB-08 no se había abierto en navegador** en la
pasada anterior.

Medido ahora, y reportado por separado porque los números no son comparables:

| Tablero | Tema | Cumplen AA | Falla |
|---|---|---|---|
| DB-05 | claro / oscuro | 31/34 · 30/32 | etiqueta del tab activo (BUG-051) |
| **DB-08** | **claro** | **1085/1209** | 122 celdas del pivote + 2 del chrome |
| **DB-08** | **oscuro** | **1208/1209** | sólo `Edit dashboard` |

**En oscuro el pivote sí pasa.** El defecto es exclusivo del tema claro — el mismo patrón del link.

§3.2 en DB-08: **1056 elementos enfocables y los 5/5 filtros alcanzables**. §3.3 pasa igual que en
DB-05, con el mismo anillo `box-shadow`.

## 3. BUG-056 — y por qué no se corrige

122 celdas `pvtVal` del pivote quedan en **3.55 : 1** sobre blanco. Superset les aplica el acento
`#2893b3` **en línea**.

Antes de clasificarlo se verificó el YAML: `db08_explorador_cubo.yaml` **no declara ningún color ni
formato condicional**, sólo estructura. Es color heredado, así que por DEC-016 es **limitación
conocida con su medición y no bloquea**. Se registra aparte de BUG-051 porque es otro tablero y otro
elemento, aunque compartan el color de origen.

**Pesa más que el chrome**: no es un botón de la barra, son los valores del explorador — el
contenido central del tablero. Vale que quede dicho aunque la regla no lo bloquee.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5
- **Modificados:** `superset/semantic/db05_cubo_driver.sql`, `tests/test_semantic_db05_db08.py`,
  `vault/06_Quality_Testing/Usability_Accessibility_Test_Plan_DB05_DB08.md`,
  `vault/06_Quality_Testing/Bug_Register.md`, este DevLog, `vault/_DevLog/_index.md`,
  `vault/02_Requirements/Traceability_Matrix.md`
- **No se tocó `sync_semantic_layer.py`**: sólo se ejecutó. El cambio vive en el `.sql` propio.
- **Decisiones autónomas:** medir el link propio en vez de citar el número de Marina; verificar el
  YAML antes de clasificar el pivote como heredado, en vez de asumirlo por el color.
- **Corrección propia registrada:** la primera validación de la guarda fue inválida (ver §1) y se
  rehízo antes de dar el resultado por bueno.

## Seguridad / calidad

- [x] `pytest tests/ -q` → **965 passed, 8 skipped, 0 failed**
- [x] `ruff check .` → limpio · `vault_lint.py` → Vault limpio
- [x] Guarda nueva validada reintroduciendo sus dos defectos por separado
- [x] Contraste medido en el navegador sobre valores **efectivos**, en claro y oscuro, en los dos
      tableros
- [x] Sin secretos hardcodeados

## Bloqueantes

- **Comprobación humana pendiente:** activación por teclado de los filtros de DB-08 (§3.2). El
  navegador automatizado no entrega `Enter` a los componentes React; marcarlo sin comprobar habría
  dado un falso negativo, como casi ocurre el 4-sep en DB-05.

## Hallazgos para otros

- **Edgar Coronel (PM):** `US-215b` sigue `in_review` y su nota dice *"PR #228 abierto"* y *"no
  cierra hasta que Manuel revise"*. **Las dos condiciones ya se cumplieron**: Manuel aprobó y el PR
  se mergeó.
- **Luis Téllez / PM:** reconstruir la imagen de Superset con el `superset_config.py` nuevo mueve la
  metadata a Postgres vacío y **pierde los 9 tableros** hasta re-correr `sync_semantic_layer.py`
  (hallazgo de Marina). Cae justo antes del 9-sep.
- **PM + C1:** **BUG-030** deja D5 en `SIN_DATO`, y en el **pivote de DB-08** el efecto es peor que
  en otros tableros: Superset **omite la columna entera** en vez de mostrarla vacía, así que se ven
  5 drivers donde el proyecto promete 6. La decisión ya está asignada al PM en el propio bug.
- **Manuel Serranía / PM:** **BUG-037** sigue **sin dueño formal**. No mordió esta vez porque el
  cambio no alteró la lista de columnas del dataset, sólo el contenido de una.
- **Oscar Quiroz:** el commit `c059f34` cita "BUG-050" en el asunto, pero su defecto está registrado
  como **BUG-047**; BUG-050 es de Marina. Cosmético y ya mergeado — sólo para que no confunda.

## Próximos pasos

1. Comprobación humana de §3.2 en DB-08.
2. PR con Manuel como reviewer de apoyo (no se tocó herramienta compartida).
