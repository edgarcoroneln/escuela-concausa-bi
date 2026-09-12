# Mensajes al equipo — actualización de repo, contexto nuevo y reasignación

Manda PRIMERO el mensaje de grupo. Después, a cada quien SU bloque por privado.

---

## MENSAJE PARA EL GRUPO

```
Equipo: tres cosas antes de arrancar mañana. Léanlas completas, son 3 minutos.

═══ 1) ACTUALICEN SU REPO. Todos, hoy. ═══

El repositorio cambió bastante esta semana: la documentación se movió a vault/,
cambió el flujo de Git y ahora hay verificaciones automáticas en cada PR.
Si trabajan con el repo viejo, TODO les va a fallar.

    git checkout main
    git pull origin main
    git checkout dev/su-nombre-apellido
    git fetch origin
    git merge origin/main

═══ 2) ABRAN UN CHAT NUEVO CON SU AGENTE. Obligatorio. ═══

Esto es lo más importante y lo que más problemas nos ahorra.

NO sigan usando la conversación que ya tenían abierta con Claude, Copilot,
Cursor o el que usen. Ese chat trae en su memoria las reglas VIEJAS: rutas que
ya no existen, la convención de ramas anterior, permisos que cambiaron. Va a
insistir en hacer las cosas como antes y les va a tumbar los PRs.

    Cierren ese chat. Abran uno nuevo. Empiecen de cero.

Y de arranque, péguenle esto para que lea el contexto actualizado:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y mi Agent Context en
    vault/09_AI_Governance/Agent_Contexts/{su-identidad}-agent-context.md
    antes de proponerme nada.

═══ 3) REASIGNACIÓN DE TAREAS ═══

Les mandé a cada uno por privado lo que necesito de ustedes el jueves y el
viernes, y qué historias suyas SE CORTAN. Cortar no es fracasar: es decidir
bien con el tiempo que queda.

El calendario:
  Jueves 3 y viernes 4 .... cerrar código. El viernes es code freeze.
  Sábado 5 ................ pruebas integrales en local, sin código nuevo.
  Domingo 6 ............... despliegue y pruebas en la URL pública.
  Miércoles 9 ............. demo en vivo.

Lo que decide la calificación no es cuántas historias cerremos: es que la
página pública muestre datos reales y el driver dominante por escuela. Todo
lo demás está subordinado a eso.
```

---

## Diana Aracely Alvarez Varela  ·  @DianaVarela96  ·  CRÍTICO

```
Hola Diana. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/diana-alvarez
    git fetch origin
    git merge origin/main

Tu rama es dev/diana-alvarez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/diana-alvarez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/diana-alvarez y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[CRÍTICO]
  · URL real de descarga de DS-02 (Catálogo CCT) + confirmar que la corrida real de DS-01 ya quedó.
  · Cerrar US-106.

Por qué:
  Sin esas URLs, Gold sigue con datos falsos y NADIE del equipo puede avanzar. Es lo primero del jueves.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/diana-alvarez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Diana Alvarez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Deni Garrido Fragoso  ·  @dgdeni  ·  CRÍTICO

```
Hola Deni. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/deni-garrido
    git fetch origin
    git merge origin/main

Tu rama es dev/deni-garrido y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/deni-garrido-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/deni-garrido y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[CRÍTICO]
  · URL de DS-03 (CEMABE) + UNA MUESTRA del CSV (con las primeras filas basta).
  · Cerrar US-113.
  · Confirmar contra qué validamos RISK-008.

Por qué:
  La muestra es tan importante como la URL: sin ver el esquema real no se puede escribir el parser. US-114 se corta.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/deni-garrido

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Deni Garrido] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Emilio Galnares Ruiz  ·  @Starcrossedboy  ·  CRÍTICO

```
Hola Emilio. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/emilio-galnares
    git fetch origin
    git merge origin/main

Tu rama es dev/emilio-galnares y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/emilio-galnares-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/emilio-galnares y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[CRÍTICO]
  · URL de DS-08 (CONAPO) y aclarar DS-06 (CONAGUA): la ficha dice PENDIENTE pero el código parece tener la URL.
  · Mándame el código o la URL.

Por qué:
  Cerraste tus 4 historias, pero esto no está en el tablero y bloquea a todos. De DS-06 sale el driver D5: sin él, D5 queda en SIN_DATO en todos los tableros.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/emilio-galnares

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Emilio Galnares] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Luis Téllez Domínguez  ·  @LuisTellez03  ·  CRÍTICO

```
Hola Luis. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/luis-tellez
    git fetch origin
    git merge origin/main

Tu rama es dev/luis-tellez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/luis-tellez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/luis-tellez y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[CRÍTICO]
  · US-526 NUEVA: contenerizar y desplegar FARO Web (Dockerfile + servicio en compose + Cloud Run).
  · Cerrar BLOCK-001 con C3.
  · US-504/505.

Por qué:
  Descubrimos que FARO Web NO tiene Dockerfile, NO está en docker-compose y la raíz de la URL pública da 404. Sin tu despliegue, lo que construyan Manuel, Marina, Andrés y Christian no se ve desde fuera. Es lo más crítico del proyecto ahora mismo.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/luis-tellez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Luis Tellez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Manuel Alejandro Serranía Reinada  ·  @mserraniaa-png  ·  CRÍTICO

```
Hola Manuel. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/manuel-serrania
    git fetch origin
    git merge origin/main

Tu rama es dev/manuel-serrania y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/manuel-serrania-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/manuel-serrania y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[CRÍTICO]
  · US-206 SE REABRE: el embebido real de los 10 dashboards por guest token.
  · Hoy pages/1_Dashboards.py tiene 10 líneas y dos TODO.
  · Además cerrar US-204 y US-205.

Por qué:
  US-206 estaba marcada 'done' sin estarlo. Es LA página que pide el PRD: dashboards + panel ML + agente en un solo lugar. Sin esto no hay demo.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/manuel-serrania

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Manuel Serrania] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Andrés González Habib  ·  @Agh28  ·  CRÍTICO

```
Hola Andrés. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/andres-gonzalez
    git fetch origin
    git merge origin/main

Tu rama es dev/andres-gonzalez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/andres-gonzalez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/andres-gonzalez y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[CRÍTICO]
  · Cerrar US-305 (el widget de chat DENTRO de FARO Web) y US-302, US-303, US-304a.
  · Y correr con Héctor la confirmación del registry de MLflow.

Por qué:
  US-305 es la tercera pieza de la página única. Y BLOCK-001 lleva 15 días abierto con el fix ya mergeado: solo falta que alguien re-corra y confirme.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/andres-gonzalez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Andres Gonzalez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Héctor Rafael Morales Marbán  ·  @hector677-mm  ·  CRÍTICO

```
Hola Héctor. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/hector-morales
    git fetch origin
    git merge origin/main

Tu rama es dev/hector-morales y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/hector-morales-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/hector-morales y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[CRÍTICO]
  · Re-correr el entrenamiento de ML-01 y CONFIRMAR que el modelo llega al registry (US-311).
  · Cerrar US-313.

Por qué:
  El fix de MLflow está mergeado desde el 18 de agosto (PR #45). Falta la corrida de confirmación. Mientras no pase, Estefany está bloqueada y perdemos 1.5 pts de rúbrica.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/hector-morales

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Hector Morales] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Marina García del Buey  ·  @marina-gdb  ·  CRÍTICO

```
Hola Marina. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/marina-garcia
    git fetch origin
    git merge origin/main

Tu rama es dev/marina-garcia y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/marina-garcia-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/marina-garcia y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[CRÍTICO]
  · US-207: el panel de ML interactivo DENTRO de FARO Web (formulario → endpoints de inferencia → resultado).
  · Cerrar US-212.

Por qué:
  Es una de las tres piezas de la página única. US-214a y US-215a se cortan: concéntrate en US-207.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/marina-garcia

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Marina Garcia] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Christian Imanol Ruiz Hurtado  ·  @ImanolRuiz00  ·  CRÍTICO

```
Hola Christian. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/christian-ruiz
    git fetch origin
    git merge origin/main

Tu rama es dev/christian-ruiz y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/christian-ruiz-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/christian-ruiz y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[CRÍTICO]
  · US-405: login y vistas protegidas por rol DENTRO de FARO Web.
  · Cerrar US-403 y US-404.

Por qué:
  Sin el login, la página única no se puede mostrar con roles distintos, que es parte de lo que evalúan en REQ-004.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/christian-ruiz

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Christian Ruiz] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Carlos Guillermo Mayorga Tapia  ·  @cmayorgat44  ·  ALTO

```
Hola Carlos. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/carlos-mayorga
    git fetch origin
    git merge origin/main

Tu rama es dev/carlos-mayorga y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/carlos-mayorga-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/carlos-mayorga y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[ALTO]
  · Cerrar US-304b (la capa RAG del agente) y US-324.

Por qué:
  Es lo que alimenta el agente que va dentro de la página única.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/carlos-mayorga

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Carlos Mayorga] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Juan Carlos Macías Mayen  ·  @juanmmayen98-pixel  ·  ALTO

```
Hola Juan. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/juan-macias
    git fetch origin
    git merge origin/main

Tu rama es dev/juan-macias y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/juan-macias-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/juan-macias y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[ALTO]
  · Cerrar US-412 y US-416.
  · Y avísame: apareces con 77% de avance y CERO PRs mergeados.

Por qué:
  Necesito entender esa diferencia antes de la demo: o tus historias se cerraron por otra vía, o el estatus está inflado.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/juan-macias

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Juan Macias] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Luis Enrique García Vázquez  ·  @LuisEGarciaV  ·  ALTO

```
Hola Luis. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/luis-garcia
    git fetch origin
    git merge origin/main

Tu rama es dev/luis-garcia y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/luis-garcia-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/luis-garcia y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[ALTO]
  · Estás libre de historias.
  · Te necesito para absorber la CARGA REAL a Bronze de DS-04, DS-05 y DS-07 en cuanto lleguen las URLs.

Por qué:
  Eres el único con ancho de banda en Célula 1 y esto es el cuello de botella del proyecto.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/luis-garcia

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Luis Garcia] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Estefany Lucero Hernández Loredo  ·  @stephi-coder  ·  ALTO

```
Hola Estefany. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/estefany-hernandez
    git fetch origin
    git merge origin/main

Tu rama es dev/estefany-hernandez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/estefany-hernandez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/estefany-hernandez y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[ALTO]
  · US-321 y US-322, en cuanto el registry confirme.
  · US-325 se corta.

Por qué:
  Tu 0% NO es culpa tuya: tus tres historias cuelgan de BLOCK-001. Estoy empujando para que Célula 3 lo confirme el jueves. En cuanto pase, arrancas.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/estefany-hernandez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Estefany Hernandez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Alejandro Velázquez Mendoza  ·  @avmxk01  ·  ALTO

```
Hola Alejandro. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/alejandro-velazquez
    git fetch origin
    git merge origin/main

Tu rama es dev/alejandro-velazquez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/alejandro-velazquez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/alejandro-velazquez y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[ALTO]
  · Cerrar US-522a y US-524a.
  · Apoyar a Luis Téllez en US-526 (el despliegue de FARO Web).
  · US-525a se corta.

Por qué:
  El despliegue del frontend es lo más crítico de Célula 5; si Luis necesita manos, eres tú.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/alejandro-velazquez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Alejandro Velazquez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Monserrat Xcaret Miranda Olivas  ·  @monserratxmiranda  ·  ALTO

```
Hola Monserrat. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/monserrat-miranda
    git fetch origin
    git merge origin/main

Tu rama es dev/monserrat-miranda y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/monserrat-miranda-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/monserrat-miranda y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[ALTO]
  · Cerrar US-214b.
  · US-215b se corta.

Por qué:
  Prioriza lo que ya tienes en vuelo; no abras nada nuevo.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/monserrat-miranda

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Monserrat Miranda] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Oscar Antonio Quiroz Lázaro  ·  @oscarqlazaro-lab  ·  ALTO

```
Hola Oscar. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/oscar-quiroz
    git fetch origin
    git merge origin/main

Tu rama es dev/oscar-quiroz y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/oscar-quiroz-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/oscar-quiroz y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[ALTO]
  · US-222 y US-223.
  · US-224 se corta.

Por qué:
  Vas en 25% con tres historias sin empezar. Si algo te atora más de 2 horas, escríbeme.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/oscar-quiroz

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Oscar Quiroz] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Edgar Ulises Jiménez López  ·  @EJ-by-Me  ·  ALTO

```
Hola Edgar. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/edgar-jimenez
    git fetch origin
    git merge origin/main

Tu rama es dev/edgar-jimenez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/edgar-jimenez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/edgar-jimenez y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[ALTO]
  · Cerrar US-521b y US-522b.
  · US-523b, US-524b y US-525b se cortan.

Por qué:
  Vas en 20% con 5 historias. Enfócate en las dos que ya tienes en vuelo y ciérralas bien.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/edgar-jimenez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Edgar Jimenez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Edward Ulysses Ruiz Bustillos  ·  @Dr4wde064  ·  ALTO

```
Hola Edward. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/edward-ruiz
    git fetch origin
    git merge origin/main

Tu rama es dev/edward-ruiz y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/edward-ruiz-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/edward-ruiz y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[ALTO]
  · Cerrar US-521c y US-522c.
  · US-524c y US-525c se cortan.

Por qué:
  Cierra lo que ya está en revisión; no abras nada nuevo.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/edward-ruiz

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Edward Ruiz] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Karla Alejandra Monter Benitez  ·  @marlakonter  ·  NORMAL

```
Hola Karla. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/karla-monter
    git fetch origin
    git merge origin/main

Tu rama es dev/karla-monter y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/karla-monter-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/karla-monter y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[NORMAL]
  · Cerrar US-411.
  · US-413 y US-414 se cortan.

Por qué:
  Vas en 22% con un solo PR mergeado. Cierra US-411 bien y con eso cerramos tu parte.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/karla-monter

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Karla Monter] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```

## Eloisa González Rubio  ·  @EloisaGonzalezRubio  ·  NORMAL

```
Hola Eloisa. Tres cosas, en orden.

── 1. ACTUALIZA TU REPO (hoy) ──

    git checkout main
    git pull origin main
    git checkout dev/eloisa-gonzalez
    git fetch origin
    git merge origin/main

Tu rama es dev/eloisa-gonzalez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y no se borra al mergear.

── 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ──

No sigas en la conversación que ya tenías. Ese chat recuerda las reglas
viejas —rutas que ya no existen, la forma anterior de crear ramas— y te va
a tumbar los PRs insistiendo en hacerlo como antes.

Cierra ese chat, abre uno nuevo, y arráncalo con esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y vault/09_AI_Governance/Agent_Contexts/eloisa-gonzalez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/eloisa-gonzalez y solo
    toco los archivos de mi alcance.

── 3. LO QUE NECESITO DE TI ──

[NORMAL]
  · Tus dos historias (US-422, US-423) se cortan.
  · Te necesito el SÁBADO en las pruebas integrales.

Por qué:
  Las pruebas de punta a punta valen más ahora que dos historias de pruebas unitarias.

── EL RITUAL DE CADA VEZ ──

Antes de escribir código:      git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/eloisa-gonzalez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que después.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI lo valida):
    [Eloisa Gonzalez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

── CALENDARIO ──
  Jue 3 y vie 4: cerrar código. Viernes es code freeze.
  Sáb 5: pruebas integrales. Dom 6: URL pública. Mié 9: demo.

Si algo te atora más de 2 horas, escríbeme. No te quedes callado. — Edgar
```
