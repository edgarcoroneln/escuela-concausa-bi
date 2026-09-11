---
project: "FARO"
date: "2026-09-10"
author_human: "Marina García del Buey"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1 sesión — sincronización con main, lectura de las resoluciones del PO y alineación del paquete de UX/UI a ADR-011. Sin código productivo."
touches: ["US-621", "REQ-002", "ADR-011", "DEC-023", "DEC-024", "DEC-019", "BUG-063", "BUG-058", "US-611"]
tags: [devlog, equipo-3, ux, storytelling, s7, us-621, adr-011]
---

# DevLog — 2026-09-10 — Alineación del paquete de UX/UI a `ADR-011` (`US-621`)

→ [[vault/_DevLog/_index|Volver al índice]] ·
[[vault/03_Architecture/ADRs/ADR-011-rediseno-ux-graficas-nativas]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]]

## Contexto

El PR #297 se mergeó y el PO cerró **las seis peticiones** que abría el plan, con `ADR-011`,
`DEC-023` y `DEC-024`. Esta sesión sincroniza `main` y alinea los cuatro documentos del frente a esas
resoluciones. No hay código productivo.

Nota de gobierno: el primer intento del PO (`d8375bf`) editaba los cuatro archivos de este frente y
regeneraba `graphify-out` en local. Se revirtió íntegro (`e5bd4e6`) y se rehízo en `ee086ca` sin
tocar nada de `FARO_Storytelling_UX/`. Verificado: los documentos llegaron intactos.

## Qué resolvió el PO, y qué cambió aquí

| Petición | Resolución | Efecto en el paquete |
|---|---|---|
| `P-01` | No se expone `prioridad` y **se prohíbe consumirla**; el front deriva un **nivel de atención** desde `indice_riesgo` | Nueva §3.quater; se retira `prioridad` de las Pantallas 4, 5 y 6, del glosario y del criterio 8 |
| `P-02` | alta `>= 0.50` · media `>= 0.30 y < 0.50` · baja `< 0.30` | Se fusiona con `P-01`: una sola etiqueta en vez de dos |
| `P-03` | Nombre de producto **Asistente FARO** | Sale "Watson" de todo el paquete; queda sólo como prohibición explícita |
| `P-04` | Concedido. Superset deja de ser navegación principal y **permanece como evidencia y respaldo** | Se corrige la §12: `Manual_Usuario_Dashboards` **sigue vigente**, no pasa a histórico como yo había escrito |
| `P-05` | Resuelto en contrato; la comprobación por despliegue pasa al smoke continuo de QA | Se conserva la regla de escribir `N` y nunca un literal (ver abajo) |
| `P-06` | `FARO_Storytelling_UX` gobierna el diseño de S7; `UX_Guidelines.md` pasa a `superseded` | `PLAN_TRABAJO` y `00_Storytelling_Scope` pasan a `approved`; se reescribe la §12 y la nota de `03_Visual_Identity` |

Se añaden además los no negociables de `ADR-011` §4, que el plan no tenía escritos —**WCAG 2.1 AA**
entre ellos—, y el régimen de trabajo en paralelo de `DEC-024`, que convierte el viernes en un hito y
no en una compuerta secuencial.

## El hallazgo de la sesión: los dos umbrales discrepan justo en las escuelas de la historia

`src/modelos/publicar_gold.py:197` asigna `prioridad` con `ALTA >= ANCLA_SIGMOIDE` (0.60) y
`MEDIA >= RIESGO_ESTABLE` (0.30). El nivel de atención de `ADR-011` §5 usa **0.50** y **0.30**.

Es decir: **coinciden en el corte de media y baja, y difieren sólo entre 0.50 y 0.60** — que es
exactamente donde viven las escuelas en riesgo, porque el máximo observado sobre el Gold publicado es
`0.5717`.

Consecuencia concreta: el front dirá *atención alta* para esas escuelas y `gold.recomendaciones.prioridad`
dirá `MEDIA` para las mismas. Las dos son correctas según su definición, pero Superset permanece como
evidencia por `DEC-023` y DB-09 expone esa columna, así que quien cruce las dos superficies ve una
contradicción sin explicación. Queda escrito en la §3.quater del plan y el glosario tiene que
distinguirlos. No es una excepción a `ADR-011`: es implementar su §5 con honestidad.

**Segundo hallazgo, mismo patrón.** Las dos constantes viven en capas distintas:
`LINEA_DE_ALERTA = 0.50` en `src/api/repositorio_gold.py:55` y `RIESGO_ESTABLE = 0.30` en
`src/modelos/riesgo.py:76`, que es crítico de Estefany Hernández. El Equipo 5 necesita ambas. Si el
`0.30` se teclea en el frontend, es `BUG-058` otra vez: un umbral hardcodeado sin dueño único. Queda
como regla en la §13.

## Lo que se defendió sin cambiar

**La regla de que el número nunca va escrito a mano.** `ADR-011` resolvió `P-05` en contrato y mandó
la comprobación por despliegue al smoke continuo de QA. Eso no la contradice, la hace necesaria: si
el chequeo vive en el smoke, un `7` tecleado en la copy es justo lo único que ese smoke no detecta.

También se conservan la revelación en la Pantalla 2, la matrícula como señal y no como serie, y la
comparación territorial acotada a pobreza y rezago. El PO no tocó ninguna de las tres, y las dos
últimas se sostienen en el dato, no en preferencia.

## Lo que trae el Equipo 2 y entra al diseño

El diagnóstico del chat ([[vault/15_ML_Models/Diagnostico_Chat_Agente_2026-09-09]], Andrés González)
cambia lo que ve el usuario: llega **streaming**, los errores se distinguen en **tres** (fuera de
alcance, sin datos, timeout) y el asistente ya responde preguntas conceptuales sin tocar la base.
Lo último se solapa con el glosario y conviene aprovecharlo: cada término puede ofrecer
preguntárselo al Asistente. Nueva §4.bis.

## Criterio de cierre de `US-621`

Se escribe por fin en la §14 del plan, porque `US-621` está `in_progress` con pendientes nombrados
por el PO y el cierre no debería depender de interpretación: los cuatro entregables finales, los 7
mockups y el PDF, el handoff aceptado por el Equipo 5 y la ejecución de QA sobre la candidata.

## Pruebas ejecutadas

```
git merge origin/main                        → fast-forward a 6cd7c50, sin conflictos
python vault/_Meta/scripts/vault_lint.py .   → Vault limpio
```

## Siguiente acción recomendada

Avisar al Equipo 3 antes de las 18:00: Juan tiene que quitar "Watson" de sus rutas visuales, Monserrat
cambia la etiqueta a nivel de atención, y Oscar añade el estado de streaming y los tres errores del
Asistente. Y pasarle al Equipo 5 las dos notas de la §3.quater y la §13 antes de que implementen.

---

## Addendum — misma sesión, revisión de Monserrat Miranda

Monserrat revisó el paquete antes de cerrar su documento y levantó cuatro puntos. Tres eran
correctos y se aplican aquí; el primero tenía la premisa invertida pero destapó un defecto real.

### El nombre: la premisa estaba al revés, el hallazgo no

Preguntó si el nombre visible es *Agente FARO* «aunque el `ADR` diga otra cosa», y si había que
pedirle a Edgar corregir el `ADR`. **No hay nada que corregir:** este paquete dice **Asistente FARO**
en sus 13 apariciones, exactamente como `ADR-011` §6. Documentos y fuente de verdad coinciden.

De dónde salió *Agente FARO*: del producto vivo. `src/frontend/pages/3_Chat.py:33` imprime
`st.title("Agente FARO")`. Lo vio en pantalla, no en el documento.

Su distinción técnico/producto sí es correcta y se adopta tal cual: `src/agente/**` y
`/api/v1/agente/consulta` son nombres técnicos y **no se tocan**; sólo cambia la cadena visible.

**El hallazgo que ella no alcanzó a ver y que hace la diferencia:** además de esa línea,
`tests/test_frontend_chat_streamlit.py` **afirma el literal viejo** en las líneas **77** y **114**.
Quien cambie el título sin tocar las pruebas rompe CI. Queda escrito en la nueva §10.ter del plan,
para el Equipo 5 (dueño de `src/frontend/**`) o el Equipo 2. Hay además 8 documentos del vault con el
nombre viejo; son técnicos o históricos y no corren prisa.

### Defecto del plan que ella encontró, y es mío

El §8 ponía sus ejemplos de visualización y los 7 mockups de Juan en el **mismo corte** del viernes
15:00, y a la vez decía que ella le entrega a él para que los integre. Las dos cosas no caben.
Corregido: entrega intermedia **hoy tras el gate**, con el formato que defina Juan, que es quien
integra.

### Carpeta nueva

`ejemplos_graficas/` dentro del paquete: sus ejemplos no tenían ubicación en la estructura original.
Dada de alta en el `_index` por la regla 4, para que ella no tuviera que tocar el índice.

### Su aviso sobre el contrato, con un matiz que abarata la implementación

Verificó que `/api/v1/escuelas` **no tiene filtro por `indice_riesgo`** y que **no existe endpoint de
Top 3 agregado**. Las dos son ciertas y quedan en la nueva §10.bis.

El matiz: no hace falta recorrer las 45 276 escuelas. El endpoint acepta `order_by=indice_riesgo` con
`order=desc`, así que **una sola llamada con `size=100`** trae las de mayor riesgo y se corta al bajar
de `0.50`. El Top 3 se calcula sobre ese conjunto. Es bastante más barato de implementar que la
lectura que ella traía.

### Confirmaciones que pidió

Ratificado el nivel de atención con alta `>= 0.50`, media `>= 0.30 y < 0.50`, baja `< 0.30`, y que
**no** es el campo `prioridad` de la API. Su lectura es correcta: `P-01` y `P-02` se cierran sin que
nadie exponga un campo nuevo, y **la petición al Equipo 5 para mañana 12:00 queda cancelada**.

---

## Addendum 2 — entra al plan la sección "Cómo funciona" del Equipo 1 (`US-601`)

El profesor señaló que **faltó explicar cómo funciona el backend**. Esa brecha es de `US-601` y el
Equipo 1 ya la construyó: una sección pública **Cómo funciona** con siete apartados
(`arquitectura`, `modelo-datos`, `capas`, `cubos`, `stack`, `decisiones`, `modelos-ml`). Dueño
formal Héctor Rafael Morales Marbán; redactada e implementada por Manuel Alejandro Serranía Reinada.

Entra al plan como **§5.bis**. Este frente no la rediseña: le da identidad y la coloca.

### La decisión de fondo: superficie hermana, no octava pantalla

Se resolvió **no** convertirla en una pantalla más del recorrido. El motivo es narrativo, no de
esfuerzo: la historia va de qué le pasa a las escuelas, no de cómo está hecho el sistema. Quien
quiera auditar entra desde la Pantalla 1 o el glosario; quien siga la investigación no tropieza con
un diagrama E-R a media historia.

Efecto práctico: los entregables siguen siendo **7 mockups** y el trabajo de Juan no se dispara a
cuatro días del cierre. Si sobra tiempo, se agrega como octavo.

### Contrato, y por qué está bien diseñado

Dos rutas: `GET /api/v1/about/secciones` (manifest) y `GET /api/v1/about/secciones/{id_seccion}`
(sobre genérico `{id, titulo, fuente, advertencias, bloques}`). `bloques` admite **siete tipos** —
`markdown`, `mermaid`, `tabla`, `metricas`, `mapa`, `barras`, `diagrama_flujo`— y los tres últimos
son **D3**, justo lo que pidió el profesor.

Lo que hace que valga la pena adoptarlo tal cual: **un tipo de bloque desconocido se pinta con una
advertencia en su propio espacio y no tumba la página**. Es el mismo espíritu de `SIN_DATO` aplicado
a la estructura, y permite que el Equipo 1 siga agregando apartados sin romper nada nuestro.

### El aviso que le toca a Juan, y es concreto

Cada bloque D3 vive en **su propio iframe**. El Equipo 1 ya se topó con el defecto: heredaban
`prefers-color-scheme: dark` y quedaban letras negras sobre fondo negro. Lo resolvieron forzando
`color-scheme: light` y fondo blanco explícito en los tres bloques D3 y en mermaid.

**Si la identidad nueva es oscura, esos bloques van a pelear con ella.** Es una decisión que Juan
tiene que tomar a propósito hoy, no descubrir el sábado.

### Dependencia declarada

Las dos rutas, la página y sus 54 pruebas viven en `dev/manuel-serrania` y **no están en `main`**.
Quedan registradas en la §10 y en la tabla de coordinación de la §11 como pendientes de merge. Si no
aterrizan, la §5.bis se cae del alcance y se declara el recorte, como cualquier otra pieza.

Por la misma razón el documento de referencia se cita **sin wikilink**: enlazar a un archivo que no
está en `main` reprueba `vault_lint`. Se convierte en enlace cuando aterrice.

### Fuera de alcance por decisión de la líder

`ADR-012` (retiro de Streamlit, frontend nativo en React, sesión por cookie `httpOnly`) está
`proposed` en `dev/diana-alvarez` y **no se incorpora a este paquete**: no se va a mergear, y el
diseño no se ata a una decisión que el PO no ha ratificado.
