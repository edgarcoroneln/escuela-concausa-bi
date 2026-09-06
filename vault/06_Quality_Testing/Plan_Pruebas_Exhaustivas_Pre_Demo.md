---
id: TEST-PLAN-PRE-DEMO
title: "Plan de pruebas exhaustivas previo a la demo — 6 al 8 de septiembre"
owner: "Edgar Edmundo Coronel Navarrete"
status: approved
source_of_truth: true
traces_up: ["REQ-002", "REQ-004", "REQ-005", "US-006", "vault/06_Quality_Testing/Test_Strategy"]
traces_down: ["vault/06_Quality_Testing/QA_Logs/_index", "vault/06_Quality_Testing/Bug_Register"]
last_reviewed: "2026-09-06"
tags: [qa, pruebas, e2e, playwright, pre-demo, freeze]
---

# Plan de pruebas exhaustivas previo a la demo

> **Sugeridas, no restringidas.** Lo de abajo es el piso, no el techo: si alguien encuentra un
> camino que no está listado, lo prueba igual y lo reporta. Lo que **no** se vale es no probar algo
> porque "no venía en la lista".
> → [[vault/06_Quality_Testing/Test_Strategy]] · [[vault/01_Product/Guion_Demo_US006]]

## Por qué existe y qué lo hace distinto

El código está en verde: **1050 pruebas unitarias pasando**. Eso no es lo que califica el miércoles.
Lo que califica es **la aplicación funcionando en la URL pública**, y eso nadie lo ha recorrido
completo con un navegador.

**Regla que ordena todo el plan: se prueba contra producción, no contra local.** Si algo sólo
funciona en local, para efectos de la demo no funciona.

## Antes de empezar: dos cosas que hay que saber o se reportan bugs falsos

**1. La API exige sesión.** Desde `DEC-018` (5-sep), `AUTH_LECTURA_PUBLICA=false`. **Sólo
`/api/v1/health` responde sin token; todo lo demás da 401.** Verificado hoy. Un 401 sin sesión
**no es un bug**: es la postura vigente.

**2. El KPI-04 puede decir 0 o 7 según cuándo pruebes.** `DEC-019` bajó la línea de alerta de 0.60 a
0.50 y **la cadena aún no está mergeada completa**. Si los tableros y la API dan números distintos,
eso **sí es un hallazgo** y hay que reportarlo con la hora exacta.

## Reparto

Cinco personas, cinco superficies, sin traslape. **Cada quien prueba lo que no construyó** cuando se
puede: se encuentran más cosas mirando código ajeno.

| Persona | Célula | Superficie | Por qué esta persona |
|---|---|---|---|
| **Eloisa González Rubio** | C4 | **API completa**: todas las rutas, estados de auth, contrato contra Swagger | Su rol es pruebas de API |
| **Karla Monter Benitez** | C4 | **Flujos de sesión**: login Google, refresco de token, logout, RBAC 200/401/403 | Construyó endpoints y RBAC: sabe qué debe romperse |
| **Monserrat Miranda** | C2 | **Los 10 tableros**: carga, datos, tabs, filtros cruzados, enlaces de drill-down | Es la dueña del modelado semántico |
| **Oscar Quiroz** | C2 | **Corrección visual**: gráficos, mapas, tarjetas vacías, valores de KPI, contraste | Su rol es gráficos, mapas y KPIs |
| **Diana Alvarez** | C1 | **Coherencia del dato de punta a punta**: que el mismo número diga lo mismo en API, tablero y panel | Es quien conoce Gold |

## Qué prueba cada quien

### Eloisa — la API, ruta por ruta

- **Todas** las rutas de `/api/v1` contra el Swagger de `/api/v1/docs`: que exista, que el esquema
  de respuesta coincida y que los códigos sean los documentados.
- Los tres estados de cada ruta de datos: **sin token → 401**, **ciudadano → 200 o 403**,
  **analista → 200**.
- Entradas inválidas: `cct` inexistente, `cct` mal formado, ciclo inexistente, parámetros fuera de
  rango, `limit` negativo. **Que no filtre detalles internos en el error** (`CLAUDE.md`).
- `/api/v1/health` y `/api/v1/version`: que `version` diga el commit desplegado y **compararlo con
  `main`**. Si va por detrás, es hallazgo.
- Tiempos de respuesta. Cualquier ruta que tarde más de 3 s en la demo es un riesgo.

### Karla — la sesión, que es lo que más caro sale si falla

- **Login con Google de punta a punta** en producción, con al menos dos cuentas: una en
  `ANALISTA_EMAILS` y una fuera.
- **`BUG-059`, el caso de la demo**: iniciar sesión, **esperar más de 15 minutos**, y volver a usar
  la aplicación. El access token dura 15 min y el refresco es nuevo. **Este es el escenario real del
  miércoles.**
- Cerrar sesión y confirmar que **no queda token vivo**: recargar y ver que pide login.
- **403 en vivo con cuenta de ciudadano** sobre una ruta de analista. Es punto de rúbrica.
- Qué pasa si se abre una página interna **sin haber pasado por el login**.

### Monserrat — los 10 tableros

- Que **los 10 carguen** y que **ninguno salga vacío**. Un tablero vacío en la demo es peor que uno
  ausente.
- **DB-05**, que es el único con tabs: los 6 tabs, que agrupen en horizontal (`US-213`) y que la
  nota de fuente esté arriba.
- **Filtros cruzados y drill-down**: los enlaces `link_db08`, que lleven al destino correcto y con
  el filtro aplicado.
- Que los números del tablero **coincidan con los del bloque de Diana** (ver abajo).
- Los tableros **con la cuenta del evaluador**, no sólo con la propia.

### Oscar — que lo que se ve sea correcto

- Cada gráfico: que **tenga datos**, que los ejes estén etiquetados y que las leyendas no tapen la
  serie.
- **Tarjetas de KPI**: ninguna en "No data" ni en `NaN`. Si una dice 0, confirmar que **es un 0
  verdadero** y no un filtro roto (`BUG-054` fue exactamente eso).
- **Mapas**: que pinten, que no haya municipios sin geometría en blanco sin explicación.
- **Contraste**, en los dos temas: la deuda de `DEC-016` es conocida y no bloquea, pero **cualquier
  elemento que escriba FARO sí debe pasar 4.5:1**.
- Ventana angosta (proyector) y ventana ancha. **Que nada desborde en horizontal.**

### Diana — que el mismo número diga lo mismo en todas partes

Es la prueba más valiosa del plan y la única que nadie más puede hacer.

- **`escuelas_en_riesgo`**: comparar `/api/v1/kpis`, el tablero DB-04 y el panel de ML **en el mismo
  minuto**. Con `DEC-019` a medio mergear, es donde va a aparecer la inconsistencia.
- **`indice_completitud_drivers`**: debe rondar **0.62**. Si dice 0.197, el Gold desplegado es viejo.
- **`SIN_DATO` nunca cuenta como 0**: verificar en al menos un driver con cobertura parcial (D3 o
  D4) y en uno completo (**D5 está 100 % en SIN_DATO**, es el caso extremo).
- **Total de matrícula** por entidad: API contra tablero.
- El **par de demostración** que elija C2: que responda en producción con los valores del guion.

## Cómo probar: Playwright

No está en el repo todavía. Se instala **fuera del árbol** para no tocar `requirements/` el día del
freeze:

```bash
python -m venv .venv-qa && source .venv-qa/bin/activate
pip install playwright pytest-playwright && playwright install chromium
```

### Prompt sugerido para el agente

> Copiar tal cual, cambiando **sólo el bloque de "Mi superficie"**.

```text
Eres mi copiloto de QA en un proyecto de BI llamado FARO. Vamos a probar la aplicación
DESPLEGADA, no el código local. Usa Playwright con Chromium.

URLs:
- API:      https://faro-api-eanzfglvyq-uc.a.run.app   (rutas bajo /api/v1)
- Superset: https://faro-superset-eanzfglvyq-uc.a.run.app

Contexto que debes tener antes de reportar nada:
- La API EXIGE sesión de Google desde DEC-018. Sólo /api/v1/health responde sin token.
  Un 401 sin sesión NO es un bug.
- Superset exige login con Google y tiene lista blanca de correos. Si un correo válido
  es rechazado, ESO SÍ es un hallazgo.
- El KPI "escuelas en riesgo" está migrando de umbral 0.60 a 0.50 (DEC-019). Si la API
  y el tablero dan números distintos, repórtalo CON LA HORA.
- La convención del proyecto: SIN_DATO nunca significa cero.

Mi superficie: <<PEGAR AQUÍ LA SECCIÓN DEL PLAN QUE ME TOCA>>

Cómo quiero que trabajes:
1. Antes de cada prueba, dime qué vas a hacer y qué esperas ver. Luego hazlo.
2. NO inicies sesión por mí ni escribas credenciales: cuando haga falta login,
   detente y pídeme que yo lo haga en la ventana.
3. Toma captura de cada hallazgo y guárdala con nombre descriptivo.
4. Verifica antes de afirmar. Si un selector no aparece, dilo; no supongas.
5. Cuando algo falle, dame: qué hiciste, qué esperabas, qué pasó, y si se reproduce
   al repetirlo. Un fallo que no se reproduce se reporta COMO intermitente, no como
   fallo firme.
6. NO ejecutes DELETE, UPDATE, DROP ni ningún POST que modifique datos.
7. Al final, dame un resumen en tabla: caso, resultado, evidencia.

Empieza recorriendo mi superficie de arriba a abajo y detente en el primer hallazgo
para que lo veamos juntos.
```

**Por qué el punto 2:** nadie escribe credenciales en un prompt ni deja que el agente las teclee. El
login lo hace la persona, en su ventana.

**Por qué el punto 5:** esta semana perdimos tiempo con un fallo intermitente reportado como firme
(`BUG-052`). Un fallo de 1 de cada 3 se reporta así, con el conteo.

## Dónde se registran los resultados

**Un archivo por persona**, en `vault/06_Quality_Testing/QA_Logs/`:

```
vault/06_Quality_Testing/QA_Logs/2026-09-0X-{identidad}-qa-pre-demo.md
```

Con frontmatter (`id`, `owner`, `status`, `traces_up`) y **la tabla de resultados**: caso, esperado,
obtenido, evidencia, veredicto. **Y hay que agregar la fila al `_index.md` de la carpeta**, o no
cuenta como archivado.

`vault/06_Quality_Testing/**` es **carpeta común**: cualquiera puede escribir su propio log sin
tocar el de otro.

## Qué hacer con lo que se encuentre

**1. Se levanta el bug en `vault/06_Quality_Testing/Bug_Register.md`.** `BUG-060` ya está tomado
(el KPI-04 con dos umbrales entre el camino mock y el real), así que **el siguiente libre es `BUG-061`**. Por `DEC-013`, **un ID no está reservado
hasta que está escrito en `main`** — si dos personas registran a la vez, quien llegue segundo
renumera. Anúncialo en el canal antes de escribirlo.

**2. Se le asigna dueño por superficie, no por quien lo encontró:**

| Si el bug está en… | Va con |
|---|---|
| Rutas, contratos, auth, RBAC | **Christian Ruiz** (TL C4) |
| Tableros, cubos, capa semántica | **Manuel Serranía** (TL C2) |
| Gold, dbt, calidad del dato | **Diana Alvarez** (TL C1) |
| Modelos, predicciones, agente | **Andrés González** (TL C3) |
| Despliegue, Cloud Run, Superset, SSO | **Luis Téllez** (TL C5) |
| No está claro | **Edgar Coronel** (PO), y yo lo enrutó |

**3. Se clasifica por lo que significa para el miércoles, no por severidad técnica:**

- **Rojo — rompe la demo.** Se arregla hoy o se saca del guion. Se avisa al PO **de inmediato**.
- **Ámbar — se ve mal pero la demo sobrevive.** Se registra y se decide con el dueño.
- **Verde — deuda.** Se registra con su medición y se declara. `DEC-016` es el precedente:
  **deuda medida y dicha por nosotros vale más que deuda descubierta por el evaluador.**

**Nada se calla.** Un hallazgo que no se registra reaparece el miércoles frente al profesor.

## Fechas

| Cuándo | Qué |
|---|---|
| **Hoy 6-sep** | Cada quien recorre su superficie y levanta lo que encuentre |
| **Domingo 7-sep** | Ensayo del guion con cronómetro · se arregla lo rojo |
| **Lunes 8-sep** | Re-prueba de lo arreglado · **congelamiento real** |
| **Miércoles 9-sep** | Checklist de la mañana del [[vault/01_Product/Guion_Demo_US006]] |
