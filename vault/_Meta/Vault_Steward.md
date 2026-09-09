---
id: DOC-VAULT-STEWARD
title: "Vault Steward — rol rotativo y turnos"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["US-005", "REQ-007", "vault/_Meta/Vault_Rules"]
traces_down: ["vault/10_Risk_Governance/Risk_Register"]
last_reviewed: "2026-09-05"
tags: [meta, gobernanza, higiene, steward]
---

# Vault Steward — rol rotativo y turnos

> Un responsable por sprint que corre el linter, revisa la matriz y caza documentos huérfanos.
> → [[vault/_Meta/_index|Volver a _Meta]] · [[vault/_Meta/Vault_Rules]] · [[vault/_Meta/Link_Hygiene]]

## Por qué existe

`RISK-006` —*el vault pierde trazabilidad con 21 contribuidores*— se mitiga con cuatro cosas:
**linter, steward, matriz y generador validado**. Tres estaban construidas desde S1. La cuarta, el
steward, sólo existía como palabra en el plan.

**No operó en S1–S4.** Esto no se descubre por auditoría: se descubre por el costo, y el costo es
medible. Todo lo de abajo apareció en una sola semana, y lo habría cazado alguien corriendo una
lista de verificación una vez por sprint:

| Lo que se degradó | Cómo se manifestó |
|---|---|
| `ownership.yml` sin cobertura | El mismo hueco parchado **seis veces** en tres días: `Accessibility.md` (Marina), `Data_Lineage_US106.md` (Diana), `requirements.txt` (Manuel), `US-521b-guia-ambiente-local.md` (Edgar Jiménez), `UX_Guidelines.md` (el PM sobre su propio documento) y `guia-ambiente-local/` (aún sin dueño). Cada vez, alguien no pudo tocar **su propio entregable** |
| Secreto versionado | `guia-ambiente-local/configuracion.env` sigue en git contra `Secrets_Policy`. Sin credenciales dentro —verificado—, pero el patrón `*.env` no des-trackea lo ya versionado |
| Registro mal formado | La fila de `BUG-018` tenía `**fixed**` en la columna de US y `open` en la de estado: **contaba como bug abierto** en cualquier conteo, con el arreglo mergeado desde el 28-ago |
| Regla 1 rota | Tres documentos de ambiente local solapados: `vault/_Meta/US-521b-guia-ambiente-local.md`, `guia-ambiente-local/VERIFICACION.md` y `Runbook_Ambiente_Local.md` con `source_of_truth: true` |
| Colisión de IDs | `BUG-049` registrado por dos personas el mismo día para defectos distintos, con `DEC-013` ya escrita justo para evitarlo. **Resuelto**: Monserrat Miranda renumeró el suyo a `BUG-051` por su cuenta y entró con el PR #228 |
| Tablero desinformando | El bloque §Estado del proyecto de la matriz llevaba cifras de agosto —*"0 REQ Done"*— tres semanas después de dejar de ser ciertas |

Ninguno es culpa de quien lo escribió. Son **higiene**, y la higiene sin dueño no ocurre.

### La octava vez, y la excepción que se decidió conceder (2026-09-05, pendiente al 2026-09-06)

El mismo patrón volvió con el **PR #263** de Luis Téllez: midió el universo completo de producción
tras cerrar `BUG-048` y escribió el resultado en dos documentos de C2 —`Cube_Specs_DB03_DB04.md` y
`Panel_ML_US207.md`—, que no están en su alcance. `quality-checks` en rojo, PR bloqueado.

**Estado al escribirse (2026-09-06): el #263 seguía `OPEN`.** Lo que existía entonces era la decisión
del PO de mergearlo con bypass de admin, y esta entrada se asentó **por adelantado** para que el
registro existiera antes que el acto, no después.

> **Consumado el 2026-09-06 a las 07:13Z**, con `gh pr merge 263 --merge --admin`, después de que
> `DEC-018` entrara a `main` con el PR #264 — el orden comprometido abajo se respetó. Se actualiza
> aquí el tiempo verbal por la misma razón que obligó a corregir esta sección la primera vez: un
> documento con `source_of_truth: true` no puede quedarse describiendo como pendiente algo que ya
> ocurrió.

> **Corrección de esta misma sección, 2026-09-06.** La primera redacción decía *"Se merge con bypass
> de admin"* en un tiempo verbal que se lee como hecho consumado, y afirmaba que la aprobación de
> Marina García del Buey respaldaba un merge que no había ocurrido. **Lo señaló ella al revisar el
> PR #264**, comprobando con `git merge-base --is-ancestor` que el commit de Luis no es ancestro de
> `main`. Tenía razón en las dos mitades: el tiempo verbal y la contradicción con el DevLog de la
> misma rama, escritos con minutos de diferencia. Un documento con `source_of_truth: true` que
> atribuye a alguien el aval de un bypass **no puede tener tres versiones**; ésta es la única.

**Lo que sí es un hecho verificado**, y es lo que hace defendible la excepción:

- **Las dos aprobaciones están en el PR #263**, en GitHub y con fecha: `marina-gdb` —dueña del
  contenido de `Panel_ML_US207.md` (US-207) y con `vault/04_UX_Design/**` en verde— y
  `edgarcoroneln`. `reviewDecision: APPROVED`. Eso es lo que faltaba cuando el DevLog original de
  Luis afirmaba una autorización sin respaldo.
- **El gate compara rutas y no puede ver una aprobación.** Lo que se saltará es el mecanismo, no el
  control.
- **`04_UX_Design/**` está en `criticos` a nombre de Manuel Serranía como *"aviso, no veto"***,
  redacción que la propia Marina originó al revisar el PR #234.

**Orden comprometido:** el #263 no se mergea antes que `DEC-018`, porque la cita. Primero entra el
PR del PM.

**Lo que esta excepción no autoriza:** repetirla sin la aprobación del dueño escrita en el PR
**antes** del merge. Lo que la hace defendible es exactamente que la autorización se documentó.

**Para el Steward que tome el turno:** ocho apariciones del mismo patrón en cuatro días es la señal
de que `ownership.yml` no describe cómo trabaja el equipo — la gente escribe donde su trabajo lo
lleva, no donde el padrón dice. Revisar el padrón contra los PRs reales del sprint es el punto 2 de
la lista de verificación, y existe por esto.

### Lo que se omitió del 6 al 7 de septiembre, y en qué se distingue (2026-09-07)

La ventana de correcciones de `DEC-020` movió doce PRs en dos días. Se saltaron revisiones, y **no
todas se saltaron igual**. Registrarlas juntas las volvería indistinguibles, así que van separadas
por lo que cada una realmente eludió. Los datos son de la API de GitHub, verificados uno por uno.

**Tipo 1 — Gate en rojo, con la aprobación del dueño presente.** Un caso: el **#263**, arriba. Es la
más defendible de las tres, porque lo que se saltó fue el mecanismo y no el control: las dos
aprobaciones estaban escritas en el PR antes del merge.

**Tipo 2 — Revisión de ruta crítica omitida, con el gate en verde.** Tres casos, todos sobre
`src/frontend/**`, que está en `criticos` a nombre de **Manuel Serranía**:

| PR | Autor | Aprobó | Revisión de Manuel |
|---|---|---|---|
| **#265** | Andrés González Habib | sólo `edgarcoroneln` | no |
| **#267** | Christian Ruiz Hurtado | sólo `edgarcoroneln` | no |
| **#268** | Marina García del Buey | sólo `edgarcoroneln` | no |

El gate pasó en los tres —`criticos` es **aviso, no veto**, y los tres autores tenían la ruta en su
amarillo—, así que no hubo bypass: hubo un aviso desatendido, tres veces seguidas, sobre la misma
carpeta y la misma persona. **Lo que lo hace tolerable** es que las tres entregas eran P0/P1 de
`DEC-020` con corte a las 18:00 y Manuel estuvo sin actividad entre el 6-sep 20:11 y el 7-sep 00:09.
**Lo que no lo hace inocuo** es que `src/frontend/**` acumuló tres cambios sin que su dueño mirara
ninguno, y el cuarto —el PR #275, suyo— tocó los mismos archivos sin saber qué había entrado antes.

**Tipo 3 — La compuerta única, saltada en los PRs del propio PM.** Dos casos: **#271** y **#278**,
los dos con `reviewDecision: REVIEW_REQUIRED`, **cero revisores**, mergeados con `--admin`.

Ésta es la más débil de las tres y conviene decirlo sin adornos. `DEC-003` define **una** aprobación
obligatoria —la del PM— y cuando el PM es el autor, **no queda ninguna**: GitHub no permite
aprobarse a uno mismo, así que el `--admin` no saltó una revisión pendiente, saltó la *única* que el
proceso contempla.

**Y no era inevitable.** En el mismo periodo, el **#264** y el **#277** —también del PM— **sí** los
revisó Marina García del Buey. La diferencia entre unos y otros no fue estructural: fue haberla
pedido. El #278 tocaba `Execution_Status.md` con **23 historias pasando a `done`**, que es
precisamente el artefacto donde una segunda mirada vale más.

**Lo que estas omisiones no autorizan:**

- Repetir el tipo 2 fuera de una ventana declarada. Si `DEC-020` no estuviera vigente, un aviso de
  `criticos` desatendido tres veces sería un defecto de proceso, no una excepción.
- Tratar el tipo 3 como práctica. **Un PR del PM que cambia estado, alcance o decisiones se pide
  revisado**, y hay dos precedentes de la misma semana que demuestran que se puede.

**Para el Steward que tome el turno.** Aquí está el hueco estructural que este registro destapa:
`DEC-003` no dice qué pasa cuando el autor **es** la compuerta. Mientras no lo diga, cada PR del PM
depende de que el PM se acuerde de pedir revisión — y el registro de esta semana muestra que a veces
sí y a veces no. Proponer la regla (por ejemplo: *el PM pide revisión al TL del área que toca, y si
no hay área, al TL de C2 por ser el de mayor superficie compartida*) es trabajo de post-demo, y es el
punto 2 de la lista de verificación aplicado al propio proceso.

## Qué hace el Steward

Un turno son **treinta minutos al cierre del sprint**. No es revisar PRs ni aprobar trabajo ajeno:
es correr una lista y **reportar**, no arreglar en silencio lo que es de otro.

### Lista de verificación

```bash
python vault/_Meta/scripts/vault_lint.py .
python vault/_Meta/scripts/validate_pm_dashboard.py
```

1. **Linter y TEST-002 en verde.** Si algo truena, se reporta al dueño del artefacto; el Steward no
   edita fuera de su alcance de `ownership.yml`.
2. **Cobertura de `ownership.yml`.** Todo archivo tocado en el sprint cae en el verde, amarillo o
   comunes de alguien. Un archivo sin dueño es un PR que alguien no va a poder abrir.
3. **IDs únicos y sin recicle.** `BUG-`, `DEC-`, `RISK-`, `ADR-`, `INC-`, `BLOCK-`: el máximo escrito
   en `main` es el que reserva (`DEC-013`). Un ID en dos registros es una colisión que hay que
   resolver antes de que se ramifique.
4. **Registros bien formados.** Las filas de `Bug_Register` y `Blocker_Register` tienen el estado en
   la columna de estado. Una columna corrida convierte un bug cerrado en uno abierto.
5. **Regla 1.** Ningún tema con dos documentos canónicos. Dos `source_of_truth: true` sobre lo mismo
   es un conflicto, no una redundancia.
6. **Huérfanos.** Todo artefacto está en el `_index.md` de su carpeta (regla 4).
7. **Estado del proyecto al día.** El bloque §Estado del proyecto de
   [[vault/02_Requirements/Traceability_Matrix]] se **transcribe a mano** desde
   `vault/13_Reports/data/pm-dashboard.json`. El turno lo compara contra el snapshot y lo corrige si
   se desfasó — se desfasa solo, con cada merge. **Follow-up post-freeze**: que el generador lo
   escriba entre marcadores y esta comparación deje de existir. Hoy no se hace porque cada refresco
   automático tocaría la matriz, donde todo el equipo agrega evidencia al final del archivo.
8. **Secretos.** Ningún `.env` ni credencial versionada — `git ls-files | grep -iE '\.env$'`.

### Qué entrega

Una entrada de DevLog con el resultado de los ocho puntos y **a quién le tocó cada hallazgo**. Si
todo salió limpio, se dice en una línea: un turno sin hallazgos también es información.

## Turnos

| Sprint | Fechas | Steward | Estado |
|---|---|---|---|
| S1 | 3–9 ago | — | ⚠️ No operó |
| S2 | 10–16 ago | — | ⚠️ No operó |
| S3 | 17–23 ago | — | ⚠️ No operó |
| S4 | 24–30 ago | — | ⚠️ No operó |
| S5 | 31 ago – 6 sep | Edgar Coronel (PO) | 🔵 En curso — hallazgos de esta semana en la tabla de arriba |
| S6 | 7–8 sep | Diana Alvarez (C1) | ⬜ Pendiente · corre la lista **antes** del ensayo de `US-006` |

**Criterio de asignación:** el turno de S6 va a quien tenga su alcance cerrado, para que la higiene
no compita con una entrega. Diana cerró sus 6 historias al 100 %.

**Después del proyecto**, la rotación sigue el orden de células —C1 → C2 → C3 → C4 → C5 → PO— y el
Tech Lead de cada célula nombra a quien le toca.

## Lo que el Steward no es

- **No es un revisor de PRs.** La compuerta de aprobación es del PM y no cambia.
- **No arregla lo ajeno.** Reporta al dueño. La única excepción son los arreglos mecánicos que el
  PM ya autoriza —resolver conflictos, sincronizar ramas—, y esos son del PM, no del rol.
- **No es un auditor de personas.** La lista mira artefactos, nunca desempeño.
