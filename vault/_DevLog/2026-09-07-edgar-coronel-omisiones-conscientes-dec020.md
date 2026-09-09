---
project: "FARO"
date: "2026-09-07"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "registro de las omisiones de revisión de la ventana DEC-020, separadas por lo que cada una realmente eludió"
tags: [devlog, pm, gobernanza, vault-steward, dec-020, dec-003, omision-consciente]
---

# DevLog — 2026-09-07 — Las omisiones del 6 al 7 de septiembre, separadas por tipo

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/_Meta/Vault_Steward]] ·
[[vault/10_Risk_Governance/Decision_Log]]

## Qué se hizo

Registro en `Vault_Steward.md` de las revisiones que se saltaron durante la ventana de correcciones
de `DEC-020`. **Van separadas en tres tipos**, porque juntas serían indistinguibles y no se
defienden igual. Los datos salen de la API de GitHub, verificados PR por PR.

**Tipo 1 — gate en rojo con la aprobación del dueño presente.** El `#263`. Ya estaba registrado; lo
que se corrige es el tiempo verbal: la entrada seguía diciendo *"sigue `OPEN` y no se ha
mergeado"*, y se consumó el 6-sep a las 07:13Z. Es exactamente el error por el que esta misma
sección tuvo que corregirse la primera vez —Marina García lo señaló entonces—, así que dejarlo
habría sido repetirlo.

**Tipo 2 — aviso de `criticos` desatendido, con el gate en verde.** Tres PRs sobre
`src/frontend/**`, que es crítico de Manuel Serranía: `#265` (Andrés), `#267` (Christian) y `#268`
(Marina). Los tres con una sola aprobación, la del PM. No hubo bypass —`criticos` es aviso, no veto,
y los tres tenían la ruta en amarillo—: hubo un aviso desatendido tres veces sobre la misma carpeta.
Lo hace tolerable que eran P0/P1 con corte a las 18:00 y que Manuel estuvo sin actividad entre el
6-sep 20:11 y el 7-sep 00:09. No lo hace inocuo que su carpeta acumuló tres cambios sin que él
mirara ninguno, y que su propio PR siguiente tocó los mismos archivos sin saber qué había entrado.

**Tipo 3 — la compuerta única, saltada en los PRs del propio PM.** `#271` y `#278`: cero revisores,
`--admin`. Es la más débil y se registra sin adornos. `DEC-003` define **una** aprobación
obligatoria, la del PM; cuando el PM es el autor no queda ninguna, porque GitHub no permite
aprobarse a uno mismo. El `--admin` no saltó una revisión pendiente: saltó la única que el proceso
contempla.

## La parte incómoda, que es la que da valor al registro

**No era inevitable.** En la misma semana, el `#264` y el `#277` —también del PM— **sí** los revisó
Marina García del Buey. La diferencia no fue estructural: fue haberla pedido. Y el `#278` era
precisamente el que más lo ameritaba, porque movía **23 historias a `done`** en
`Execution_Status.md`.

Un registro de omisiones que sólo justifica no sirve para nada. Éste dice qué se saltó, por qué es
defendible en dos casos, por qué es débil en el tercero, y qué no autoriza ninguno.

## El hueco estructural que esto destapa

`DEC-003` **no dice qué pasa cuando el autor es la compuerta.** Mientras no lo diga, cada PR del PM
depende de que el PM se acuerde de pedir revisión, y el registro de esta semana muestra que a veces
sí y a veces no —dos de cuatro—.

Queda propuesto para después de la demo, no se decide aquí: que el PM pida revisión al TL del área
que toca, y si no hay área clara, al TL de C2 por ser el de mayor superficie compartida.

## Lo que queda pendiente

- Avisarle a Manuel Serranía que su carpeta acumuló tres cambios sin su revisión, con los números de
  PR, para que pueda mirarlos hacia atrás si quiere.
- La regla de `DEC-003` para PRs del PM: post-demo.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code / claude-opus-5.
- **Creados:** este DevLog.
- **Modificados:** `vault/_Meta/Vault_Steward.md` (sección nueva + corrección del tiempo verbal del
  #263), `vault/_DevLog/_index.md`.
- **Verificado por el agente antes de escribir:** el estado y los revisores reales de los PRs #263,
  #264, #265, #267, #268, #271, #277 y #278 vía la API de GitHub — incluido que #264 y #277 sí
  llevan la aprobación de `marina-gdb`, que es lo que convierte el tipo 3 en una omisión evitable y
  no en una limitación del proceso.
- **Correcciones manuales:** pendientes de revisión humana.
