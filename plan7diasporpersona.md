# Plan personal de 7 días — uno por integrante

Manda a cada quien SU bloque por privado. El calendario común está en todos.

---

## Diana Aracely Alvarez Varela  ·  @DianaVarela96  ·  CRÍTICO

```
Diana, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Destrabar los datos reales. Todo el proyecto cuelga de ti el jueves.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/diana-alvarez
    git fetch origin
    git merge origin/main

Tu rama es dev/diana-alvarez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/diana-alvarez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/diana-alvarez
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Antes del mediodía: la URL real de descarga de DS-02 (Catálogo CCT)
     y confirmar que la corrida real de DS-01 ya quedó. Es lo primero que
     hago yo también.

  ── VIE 4 ──
     Cerrar US-106. Validar el Gold recalculado con las 8 fuentes reales.

  ── SÁB 5 ──
     Correr el pipeline punta a punta en compose y confirmar que los
     números de Gold son creíbles.

  ── DOM 6 ──
     Verificar que la URL pública sirve datos reales, no fixtures. Hoy
     sirve 5,837 alumnos.

  ── LUN 7 ──
     Corregir lo que salga de las pruebas del domingo.

  ── MAR 8 ──
     Ensayo general. Prepara 2 minutos sobre el pipeline por si el
     profesor pregunta.

  ── MIÉ 9 ──
     Demo. Eres quien explica la capa de datos si se abre esa pregunta.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Nadie. Puedes entregar la URL hoy mismo.

  ── Dependen de ti ──
     Luis García (carga a Bronze) · Deni (Silver/Gold) · Héctor
     (predicciones) · TODOS los tableros

  Eres el primer eslabón. Si tu URL llega el jueves temprano, la
  cadena completa alcanza.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/diana-alvarez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Diana Alvarez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Deni Garrido Fragoso  ·  @dgdeni  ·  CRÍTICO

```
Deni, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: La URL de CEMABE y su muestra. Sin el esquema real nadie puede escribir el parser.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/deni-garrido
    git fetch origin
    git merge origin/main

Tu rama es dev/deni-garrido y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/deni-garrido-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/deni-garrido
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Antes del mediodía: URL de DS-03 (CEMABE) y una muestra del CSV —
     con las primeras filas basta. También confirmar contra qué validamos
     RISK-008 (`coneval_periodo_medicion = 2020` es un placeholder).

  ── VIE 4 ──
     Parser de CEMABE + cargador real a Bronze. Cerrar US-113.

  ── SÁB 5 ──
     Validar los modelos dbt de punta a punta con los datos reales.

  ── DOM 6 ──
     Verificar Silver y Gold en la URL pública.

  ── LUN 7 ──
     Correcciones de transformación si algo sale raro.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

  ── SE CORTA ──
     US-114 (optimización de consultas e índices)
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

La muestra del CSV es tan importante como la URL: sin ver el esquema
real, el parser se escribe a ciegas.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Nadie para la URL. Para el parser: tu propia muestra del CSV.

  ── Dependen de ti ──
     Luis García · Héctor · los 10 dashboards · el agente

  Si la muestra llega el jueves, el parser se escribe el viernes. Si
  llega el viernes, ya no.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/deni-garrido

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Deni Garrido] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Emilio Galnares Ruiz  ·  @Starcrossedboy  ·  CRÍTICO

```
Emilio, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Dos URLs que nadie más tiene, y una de ellas define si el driver D5 existe.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/emilio-galnares
    git fetch origin
    git merge origin/main

Tu rama es dev/emilio-galnares y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/emilio-galnares-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/emilio-galnares
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Antes del mediodía: URL de DS-08 (CONAPO) y aclarar DS-06 (CONAGUA)
     — la ficha dice PENDIENTE pero el código parece tener la URL.
     Mándame el código o la URL que usaste.

  ── VIE 4 ──
     Cargadores reales a Bronze de DS-06 y DS-08.

  ── SÁB 5 ──
     Confirmar que el driver D5 (estrés hídrico) sale de SIN_DATO en los
     tableros.

  ── DOM 6 ──
     Verificar DS-06 y DS-08 en la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Cerraste tus 4 historias, y bien. Pero estas dos URLs no están en el
tablero y bloquean a todos: de DS-06 sale el driver D5, y sin él, D5
queda en SIN_DATO en todos los tableros.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Nadie.

  ── Dependen de ti ──
     El driver D5 en DB-07 y en el cálculo del driver dominante

  Sin DS-06 confirmada, D5 se queda en SIN_DATO y el mapa de drivers
  sale incompleto.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/emilio-galnares

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Emilio Galnares] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Luis Enrique García Vázquez  ·  @LuisEGarciaV  ·  ALTO

```
Luis, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Eres el único con ancho de banda en Célula 1 y el cuello de botella está justo ahí.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/luis-garcia
    git fetch origin
    git merge origin/main

Tu rama es dev/luis-garcia y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/luis-garcia-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/luis-garcia
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Preparar los cargadores reales a Bronze de DS-04, DS-05 y DS-07 para
     que estén listos cuando lleguen las URLs.

  ── VIE 4 ──
     Cargar en cuanto Diana, Deni y Emilio confirmen. Es la ruta crítica
     del proyecto.

  ── SÁB 5 ──
     Pruebas integrales del pipeline completo.

  ── DOM 6 ──
     Apoyar la verificación de datos en la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Terminaste tus 4 historias. Te pido esto justamente porque tienes
espacio y el equipo no.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Diana (DS-02), Deni (DS-03), Emilio (DS-06/DS-08)

  ── Dependen de ti ──
     Gold real → predicciones → dashboards → agente. Todo.

  No puedes arrancar hasta que lleguen las URLs. Ten los cargadores
  listos para no perder ni una hora.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/luis-garcia

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Luis Garcia] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Manuel Alejandro Serranía Reinada  ·  @mserraniaa-png  ·  CRÍTICO

```
Manuel, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Tienes la pieza central de la página que evalúan: el embebido de los 10 dashboards.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/manuel-serrania
    git fetch origin
    git merge origin/main

Tu rama es dev/manuel-serrania y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/manuel-serrania-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/manuel-serrania
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Arrancar el embebido real en `pages/1_Dashboards.py`. Y ponerte de
     acuerdo hoy con Marina, Andrés y Christian: los tres van a trabajar
     sobre tu mismo shell.

  ── VIE 4 ──
     Embebido funcionando en local, con los filtros aplicando al
     conjunto. Cerrar US-204 y US-205. Code freeze al final del día.

  ── SÁB 5 ──
     Pruebas integrales con Luis en compose: tu página con las tres
     piezas dentro.

  ── DOM 6 ──
     Ajustes visuales sobre la URL pública ya desplegada.

  ── LUN 7 ──
     Corregir lo que salga del domingo.

  ── MAR 8 ──
     Ensayo general. Tú manejas la navegación de la demo.

  ── MIÉ 9 ──
     Demo. La página que presentas es tuya.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Reabrí US-206. Estaba en 'done' con la evidencia del PR #134, que es
trabajo de US-205: se cerró por confusión entre las dos. El repunteo que
hiciste fue trabajo real y quedó bien — solo se le puso la etiqueta
equivocada.

Qué falta, concreto (la arquitectura ya está en Frontend_Architecture.md
§4, no hay que diseñar nada):
1. Guest token de Superset por sesión, con RLS según el rol
2. Los 10 dashboards DB-01…DB-10 por iframe firmado
3. Filtros de ciclo / entidad / nivel aplicando al conjunto
4. Sin token válido, no se muestra ningún tablero


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Superset (ya funciona) · Christian para el token de sesión

  ── Dependen de ti ──
     Marina, Andrés y Christian trabajan SOBRE tu shell · Luis Téllez
     necesita la página para contenerizarla

  Eres el cuello de botella de la página. Si el shell no está el
  viernes, Luis no tiene qué desplegar el domingo.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/manuel-serrania

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Manuel Serrania] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Marina García del Buey  ·  @marina-gdb  ·  CRÍTICO

```
Marina, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: El panel de ML dentro de la página. Es una de las tres piezas que se integran.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/marina-garcia
    git fetch origin
    git merge origin/main

Tu rama es dev/marina-garcia y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/marina-garcia-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/marina-garcia
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Arrancar US-207 en `pages/2_Panel_ML.py` (hoy son 10 líneas con dos
     TODO). Coordinar con Manuel antes de tocar `src/frontend/`.

  ── VIE 4 ──
     Formulario de parámetros → POST a los endpoints de inferencia
     (US-412/415) → resultado de los 3 modelos. Cerrar US-212.

  ── SÁB 5 ──
     Pruebas integrales: tu panel dentro de la página de Manuel.

  ── DOM 6 ──
     Ajustes sobre la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo. Tú muestras el panel de ML en vivo.

  ── SE CORTA ──
     US-214a y US-215a
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Te corto dos historias para que te concentres en US-207. Es más valiosa
que las dos juntas: sin ella, la página no tiene el panel de ML que pide
el PRD.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Manuel (el shell) · Juan Macías (US-412, los endpoints de
     inferencia)

  ── Dependen de ti ──
     La demo del panel de ML

  Habla con Juan el jueves: si sus endpoints no responden, tu
  formulario no tiene a dónde pegarle.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/marina-garcia

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Marina Garcia] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Monserrat Xcaret Miranda Olivas  ·  @monserratxmiranda  ·  ALTO

```
Monserrat, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Cerrar limpio lo que ya tienes en vuelo.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/monserrat-miranda
    git fetch origin
    git merge origin/main

Tu rama es dev/monserrat-miranda y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/monserrat-miranda-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/monserrat-miranda
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Avanzar US-214b.

  ── VIE 4 ──
     Cerrar US-214b. Code freeze.

  ── SÁB 5 ──
     Pruebas integrales de los dashboards.

  ── DOM 6 ──
     Verificar tus tableros en la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

  ── SE CORTA ──
     US-215b
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

No abras nada nuevo. Cierra bien lo que ya empezaste.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Gold real (Célula 1)

  ── Dependen de ti ──
     Nada crítico

  Tus tableros ya existen; con datos reales solo cambian los números.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/monserrat-miranda

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Monserrat Miranda] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Oscar Antonio Quiroz Lázaro  ·  @oscarqlazaro-lab  ·  ALTO

```
Oscar, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Vas en 25% con tres historias sin empezar. Dos de ellas sí caben.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/oscar-quiroz
    git fetch origin
    git merge origin/main

Tu rama es dev/oscar-quiroz y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/oscar-quiroz-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/oscar-quiroz
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Arrancar US-222.

  ── VIE 4 ──
     Cerrar US-222 y US-223. Code freeze.

  ── SÁB 5 ──
     Pruebas integrales de DB-07 y DB-10.

  ── DOM 6 ──
     Verificar tus tableros en la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

  ── SE CORTA ──
     US-224
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Si algo te atora más de dos horas, escríbeme el mismo día. No esperes al
viernes.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Gold real (Célula 1)

  ── Dependen de ti ──
     DB-07 muestra la completitud de drivers

  Si Emilio no confirma DS-06, DB-07 va a mostrar D5 vacío. Aváncalo
  igual.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/oscar-quiroz

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Oscar Quiroz] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Andrés González Habib  ·  @Agh28  ·  CRÍTICO

```
Andrés, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: El agente dentro de la página, y empujar el registry que tiene parada a Estefany.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/andres-gonzalez
    git fetch origin
    git merge origin/main

Tu rama es dev/andres-gonzalez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/andres-gonzalez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/andres-gonzalez
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Con Héctor: re-correr y confirmar el registry de MLflow (BLOCK-001).
     El fix está mergeado desde el 18-ago; solo falta la corrida. Cerrar
     US-304a.

  ── VIE 4 ──
     Cerrar US-305 (el chat dentro de FARO Web), US-302 y US-303.
     Coordinar con Manuel antes de tocar `src/frontend/`. Code freeze.

  ── SÁB 5 ──
     Pruebas integrales: el agente respondiendo con datos reales, no con
     el stub.

  ── DOM 6 ──
     Ajustes del agente sobre la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo. Tú haces la pregunta en vivo al agente — es el momento más
     vistoso.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

BLOCK-001 lleva 15 días abierto y tiene a Estefany en 0%. En cuanto el
registry confirme, ella arranca.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Manuel (el shell) · Carlos (US-304b, la capa RAG)

  ── Dependen de ti ──
     Estefany (el registry la destraba) · la demo del agente

  Tu chat necesita el shell de Manuel y el RAG de Carlos. Coordina con
  ambos el jueves.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/andres-gonzalez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Andres Gonzalez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Héctor Rafael Morales Marbán  ·  @hector677-mm  ·  CRÍTICO

```
Héctor, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: La corrida que destraba REQ-003 y a Estefany.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/hector-morales
    git fetch origin
    git merge origin/main

Tu rama es dev/hector-morales y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/hector-morales-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/hector-morales
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Re-correr el entrenamiento de ML-01 y confirmar que el modelo llega
     al registry (US-311). Es lo único que falta de BLOCK-001.

  ── VIE 4 ──
     Cerrar US-313. Regenerar predicciones con el Gold real. Code freeze.

  ── SÁB 5 ──
     Pruebas integrales: predicciones y driver dominante por escuela.

  ── DOM 6 ──
     Verificar predicciones en la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo. Tú explicas el índice de riesgo y el driver dominante.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

El fix de MLflow está mergeado (PR #45, MLflow a 3.15.1). Solo falta la
corrida de confirmación. Mientras no pase: AC-003.4 no se cumple, el
gate 'tres modelos registrados' sigue rojo y perdemos 1.5 pts de
rúbrica.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Luis Téllez (la infra de MLflow, ya arreglada) · Gold real para las
     predicciones finales

  ── Dependen de ti ──
     Estefany (3 historias) · el driver dominante · REQ-003 completo

  La corrida de confirmación no depende de datos reales: puedes
  hacerla el jueves con lo que hay.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/hector-morales

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Hector Morales] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Estefany Lucero Hernández Loredo  ·  @stephi-coder  ·  ALTO

```
Estefany, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Arrancas en cuanto el registry confirme. Tu 0% no es culpa tuya.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/estefany-hernandez
    git fetch origin
    git merge origin/main

Tu rama es dev/estefany-hernandez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/estefany-hernandez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/estefany-hernandez
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Prepara US-321 y US-322 para arrancar en cuanto Héctor confirme el
     registry. Deja listo el notebook y las features.

  ── VIE 4 ──
     Ejecutar US-321 y US-322. Code freeze.

  ── SÁB 5 ──
     Pruebas integrales del clustering.

  ── DOM 6 ──
     Verificar en la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

  ── SE CORTA ──
     US-325
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Quiero que quede claro: tus tres historias cuelgan de BLOCK-001, que no
depende de ti. Estoy empujando a Héctor y Luis para que se confirme el
jueves. Si el viernes sigue trabado, te reasigno a las pruebas del
sábado y no pasa nada.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Héctor (la confirmación del registry). Es tu único bloqueo.

  ── Dependen de ti ──
     Nada crítico

  Por eso tu 0% no es tuyo. En cuanto Héctor confirme, arrancas.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/estefany-hernandez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Estefany Hernandez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Carlos Guillermo Mayorga Tapia  ·  @cmayorgat44  ·  ALTO

```
Carlos, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: La capa RAG que alimenta al agente de la página.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/carlos-mayorga
    git fetch origin
    git merge origin/main

Tu rama es dev/carlos-mayorga y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/carlos-mayorga-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/carlos-mayorga
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Cerrar US-304b (ChromaDB + embeddings).

  ── VIE 4 ──
     Cerrar US-324. Code freeze.

  ── SÁB 5 ──
     Pruebas del agente con el set de evaluación (US-323, ya cerrada).

  ── DOM 6 ──
     Verificar el agente en la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Nadie

  ── Dependen de ti ──
     Andrés (su chat usa tu capa RAG)

  Si cierras US-304b el jueves, Andrés puede cerrar US-305 el viernes.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/carlos-mayorga

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Carlos Mayorga] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Christian Imanol Ruiz Hurtado  ·  @ImanolRuiz00  ·  CRÍTICO

```
Christian, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: El login que hace que la página se pueda mostrar con roles distintos.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/christian-ruiz
    git fetch origin
    git merge origin/main

Tu rama es dev/christian-ruiz y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/christian-ruiz-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/christian-ruiz
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Arrancar US-405 en FARO Web. Coordinar con Manuel antes de tocar
     `src/frontend/`.

  ── VIE 4 ──
     Login y vistas por rol funcionando. Cerrar US-403 y US-404. Code
     freeze.

  ── SÁB 5 ──
     Pruebas integrales de seguridad: roles, tokens, endpoints
     protegidos.

  ── DOM 6 ──
     Verificar OAuth en la URL pública desplegada.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo. Tú muestras el login y el cambio de rol.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Sin el login, la página no se puede demostrar con roles distintos, que
es parte de lo que evalúan en REQ-004.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Manuel (el shell)

  ── Dependen de ti ──
     Manuel (necesita tu token de sesión) · la demo con roles

  Tu login y el shell de Manuel se necesitan mutuamente. Trabájenlo
  juntos el jueves.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/christian-ruiz

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Christian Ruiz] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Karla Alejandra Monter Benitez  ·  @marlakonter  ·  NORMAL

```
Karla, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Cerrar bien una historia vale más que dejar tres a medias.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/karla-monter
    git fetch origin
    git merge origin/main

Tu rama es dev/karla-monter y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/karla-monter-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/karla-monter
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Avanzar US-411.

  ── VIE 4 ──
     Cerrar US-411. Code freeze.

  ── SÁB 5 ──
     Apoyar las pruebas integrales de la API.

  ── DOM 6 ──
     Verificar endpoints en la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

  ── SE CORTA ──
     US-413 y US-414
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Vas en 22% con un solo PR mergeado en todo el proyecto. Prefiero que
cierres US-411 completa y bien documentada a que abras dos más.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Nadie

  ── Dependen de ti ──
     Nada crítico

  Cierra US-411 con calma y bien documentada.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/karla-monter

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Karla Monter] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Juan Carlos Macías Mayen  ·  @juanmmayen98-pixel  ·  ALTO

```
Juan, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Cerrar tus dos historias en revisión, y aclararme algo.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/juan-macias
    git fetch origin
    git merge origin/main

Tu rama es dev/juan-macias y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/juan-macias-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/juan-macias
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Cerrar US-412 (inferencia ML) — es lo que consume el panel de
     Marina.

  ── VIE 4 ──
     Cerrar US-416. Code freeze.

  ── SÁB 5 ──
     Pruebas integrales de los contratos de API.

  ── DOM 6 ──
     Verificar en la URL pública.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Necesito entender algo antes de la demo: apareces con 77% de avance y
CERO PRs mergeados. O tus historias se cerraron por otra vía, o el
estatus está inflado. Dime cuál es, sin problema — solo necesito que el
tablero diga la verdad.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Nadie

  ── Dependen de ti ──
     Marina (su panel de ML llama a tus endpoints de inferencia)

  US-412 es lo primero: sin ella, Marina no puede terminar US-207.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/juan-macias

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Juan Macias] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Eloisa González Rubio  ·  @EloisaGonzalezRubio  ·  NORMAL

```
Eloisa, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Te muevo a pruebas integrales, que ahora valen más que tus dos historias.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/eloisa-gonzalez
    git fetch origin
    git merge origin/main

Tu rama es dev/eloisa-gonzalez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/eloisa-gonzalez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/eloisa-gonzalez
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Preparar el guion de pruebas E2E con el equipo de calidad.

  ── VIE 4 ──
     Terminar de preparar los casos. Code freeze.

  ── SÁB 5 ──
     Tu día grande: ejecutar el guion E2E completo sobre el stack en
     local y levantar los defectos.

  ── DOM 6 ──
     Repetir las pruebas sobre la URL pública real.

  ── LUN 7 ──
     Verificar las correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

  ── SE CORTA ──
     US-422 y US-423
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Te corto tus dos historias de pruebas unitarias porque el sábado
necesito a alguien ejecutando el recorrido completo, y eres la persona
indicada. Vale más para la rúbrica que dos suites más.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Que todo esté armado el viernes

  ── Dependen de ti ──
     Todo el equipo depende de tus hallazgos del sábado

  Tu valor está el sábado y el domingo, no antes. Usa jueves y viernes
  para preparar el guion.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/eloisa-gonzalez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Eloisa Gonzalez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Luis Téllez Domínguez  ·  @LuisTellez03  ·  CRÍTICO

```
Luis, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Sin tu despliegue, nada de lo que construya el equipo se ve desde fuera.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/luis-tellez
    git fetch origin
    git merge origin/main

Tu rama es dev/luis-tellez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/luis-tellez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/luis-tellez
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Arrancar US-526: `docker/frontend.Dockerfile` + servicio `frontend`
     en compose. Y empujar a C3 para que confirme el registry (BLOCK-001,
     15 días abierto contigo como dueño).

  ── VIE 4 ──
     FARO Web levantando en compose con las tres piezas dentro. Cerrar
     US-504 y US-505. Code freeze.

  ── SÁB 5 ──
     Pruebas integrales de todo el stack en local, con Eloísa.

  ── DOM 6 ──
     Tu día grande: desplegar FARO Web a Cloud Run, redesplegar la API y
     verificar que la raíz deje de dar 404.

  ── LUN 7 ──
     Corregir lo que salga del domingo.

  ── MAR 8 ──
     Ensayo general con la URL definitiva.

  ── MIÉ 9 ──
     Demo. Tú garantizas que la URL esté viva.

  ── SE CORTA ──
     US-525a/b/c
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

US-526 es nueva y es tuya. Descubrimos que FARO Web NO tiene Dockerfile,
NO está en docker-compose y la raíz de la URL pública da 404: hoy solo
está publicada la API.

Qué necesito, concreto:
1. docker/frontend.Dockerfile para la app Streamlit (src/frontend/)
2. Servicio 'frontend' en docker-compose.yml, conectado a API y Superset
3. Despliegue a Cloud Run sirviendo la página en la RAÍZ
4. CORS / ALLOWED_ORIGINS de Superset para que acepte el embebido — es
la parte que suele morder

Y una más: /api/v1/version devuelve commit: 'dev', así que nadie sabe
qué imagen corre en producción. El fix del GIT_SHA lo hiciste
local-first sin deploy.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Manuel, Marina, Andrés y Christian (la página que vas a
     contenerizar)

  ── Dependen de ti ──
     TODO lo que se ve desde fuera. Eres el último eslabón.

  Puedes adelantar el Dockerfile y el servicio con el shell como está
  — no esperes a que la página esté completa.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/luis-tellez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Luis Tellez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Edgar Ulises Jiménez López  ·  @EJ-by-Me  ·  ALTO

```
Edgar, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Cerrar las dos que ya tienes en vuelo. Vas en 20%.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/edgar-jimenez
    git fetch origin
    git merge origin/main

Tu rama es dev/edgar-jimenez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/edgar-jimenez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/edgar-jimenez
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Avanzar US-521b.

  ── VIE 4 ──
     Cerrar US-521b y US-522b. Code freeze.

  ── SÁB 5 ──
     Apoyar las pruebas integrales.

  ── DOM 6 ──
     Apoyar el despliegue con Luis.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

  ── SE CORTA ──
     US-523b, US-524b y US-525b
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

Vas en 20% con 5 historias asignadas y ninguna cerrada. Te corto tres
para que las dos que ya empezaste queden bien.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Nadie

  ── Dependen de ti ──
     Nada crítico

  Cierra tus dos historias en vuelo.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/edgar-jimenez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Edgar Jimenez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Alejandro Velázquez Mendoza  ·  @avmxk01  ·  ALTO

```
Alejandro, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Cerrar lo tuyo y ser las manos de Luis en el despliegue.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/alejandro-velazquez
    git fetch origin
    git merge origin/main

Tu rama es dev/alejandro-velazquez y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/alejandro-velazquez-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/alejandro-velazquez
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Cerrar US-522a. Ofrecerle apoyo a Luis en US-526 desde hoy.

  ── VIE 4 ──
     Cerrar US-524a. Code freeze.

  ── SÁB 5 ──
     Pruebas integrales del stack.

  ── DOM 6 ──
     Apoyar el despliegue de FARO Web y el redeploy de la API.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

  ── SE CORTA ──
     US-525a
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

El despliegue del frontend es lo más crítico de Célula 5. Si Luis
necesita manos, eres tú.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Nadie

  ── Dependen de ti ──
     Luis Téllez, si necesita manos en US-526

  Ofrécele apoyo el jueves, no esperes a que te lo pida.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/alejandro-velazquez

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Alejandro Velazquez] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```

## Edward Ulysses Ruiz Bustillos  ·  @Dr4wde064  ·  ALTO

```
Edward, este es tu plan de aquí a la demo. Léelo completo una vez.

TU MISIÓN DE LA SEMANA: Cerrar limpio lo que está en revisión.

══════════ 1. ACTUALIZA TU REPO (hoy, antes que nada) ══════════

    git checkout main
    git pull origin main
    git checkout dev/edward-ruiz
    git fetch origin
    git merge origin/main

Tu rama es dev/edward-ruiz y es la ÚNICA que vas a usar. Ya está creada,
es tuya todo el proyecto y NO se borra al mergear.

══════════ 2. ABRE UN CHAT NUEVO CON TU AGENTE (obligatorio) ══════════

No sigas en la conversación que ya tenías abierta. Ese chat recuerda las
reglas viejas —rutas que ya no existen, la forma anterior de crear ramas,
permisos que cambiaron— y te va a tumbar los PRs insistiendo en hacerlo
como antes.

Ciérralo. Abre uno nuevo. Arráncalo pegando esto:

    Lee AGENTS.md, CLAUDE.md, vault/_Meta/Vault_Rules.md,
    vault/_Meta/ownership.yml y
    vault/09_AI_Governance/Agent_Contexts/edward-ruiz-agent-context.md
    antes de proponerme nada. Trabajo en la rama dev/edward-ruiz
    y solo toco los archivos de mi alcance.

══════════ 3. TU PLAN, DÍA POR DÍA ══════════

  ── JUE 3 ──
     Avanzar US-521c.

  ── VIE 4 ──
     Cerrar US-521c y US-522c. Code freeze.

  ── SÁB 5 ──
     Apoyar las pruebas integrales.

  ── DOM 6 ──
     Apoyar el despliegue.

  ── LUN 7 ──
     Correcciones.

  ── MAR 8 ──
     Ensayo general.

  ── MIÉ 9 ──
     Demo.

  ── SE CORTA ──
     US-524c y US-525c
     Cortar no es fracasar: es decidir bien con el tiempo que queda.
     Queda documentado como fuera de alcance, que es lo que la rúbrica premia.

══════════ 4. CONTEXTO QUE NECESITAS ══════════

No abras nada nuevo; cierra lo que ya está en revisión.


══════════ TU LUGAR EN LA CADENA ══════════

  ── Dependes de ──
     Nadie

  ── Dependen de ti ──
     Nada crítico

  Cierra lo que ya está en revisión.
══════════ EL RITUAL, CADA VEZ ══════════

Antes de escribir código:       git fetch origin && git merge origin/main
Antes de abrir el PR (otra vez): git fetch origin && git merge origin/main
Subir:                          git push origin dev/edward-ruiz

Ese segundo merge es el que más se olvida y el que más problemas evita.
main se mueve varias veces al día. El CI RECHAZA el PR si tu rama está
atrasada, así que te va a tocar de todos modos: mejor antes que el rebote.

Nunca 'rebase' ni 'push --force' en tu rama: es permanente.

Título del PR (el CI valida el formato y que la firma sea tuya):
    [Edward Ruiz] - Lo que hiciste (US-###) - [sync|CI|DoF|DevLog]

══════════ CALENDARIO COMÚN ══════════

  Jue 3 · Vie 4 ... cerrar código. El VIERNES es code freeze.
  Sáb 5 .......... pruebas integrales en local. Sin código nuevo.
  Dom 6 .......... despliegue y pruebas en la URL pública.
  Lun 7 .......... corregir lo que salga del domingo.
  Mar 8 .......... ensayo general. Congelado definitivo.
  Mié 9 .......... DEMO EN VIVO.

Si algo te atora más de dos horas, escríbeme el mismo día. Prefiero
recortar alcance a tiempo que enterarme el viernes. — Edgar
```
