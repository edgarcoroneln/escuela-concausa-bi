---
project: "FARO"
date: "2026-09-13"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "2h"
touches: ["US-601", "US-641", "REQ-002", "REQ-004", "ADR-012"]
tags: [devlog, us-601, componentes, frontend, react, equipo-1]
---

# DevLog — 2026-09-13 — Componentes al día con ADR-012, y «Cómo funciona» deja de pedir login (US-601)

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

1. **La sección describía la arquitectura de la demo del 9-sep**, ya derogada por `ADR-012`. Se
   actualizaron la lista de componentes, la memoria técnica y el diagrama.
2. **Se reconciliaron dos refactors de `main`** que rompían la pantalla nueva.
3. **Se corrigió que la sección exigiera sesión**, contra lo que el propio API declara.

## 1. La documentación decía algo que ya no era cierto

`ADR-012` retiró Streamlit y el embebido de Superset como interfaz del producto, a petición del
profesor tras la demo. La sección seguía describiendo el sistema anterior — y es lo primero que lee
alguien que llega al proyecto.

| Fila | Antes | Ahora |
|---|---|---|
| **React 19 + Vite** | no existía | la interfaz real del producto (E5 · Diana Alvarez) |
| **nginx** | no existía | sirve la SPA y proxea el API en el mismo origen (E5 · Luis Téllez) |
| Streamlit | «Shell único de FARO Web» | «shell histórico», **retirado como interfaz** |
| Superset | «Los 10 dashboards del proyecto» | motor de cubos **interno**; lo retirado es su embebido |

La memoria técnica pasó de 10 a 12 filas: entran *Frontend* (React 19 + Vite + Tailwind · d3 y
Recharts) y *Servidor web* (nginx); *BI* pasa a **BI interno**.

**En el diagrama:** la caja de FARO Web dice React/nginx, **desapareció la flecha «embebido»** de
Superset hacia ella —esa ruta ya no existe—, Superset queda con borde punteado (fuera de la ruta
del usuario final) y la flecha del API dice «REST · mismo origen».

Se añadió una nota fechada: la tabla de células describe **cómo se construyó** el sistema, y las dos
filas nuevas citan su equipo actual (`E5`) porque no existían cuando el reparto era por células.

**Guarda nueva** (`test_about_arquitectura_refleja_adr012`): reprueba si la sección vuelve a
describir Streamlit como la interfaz vigente, si desaparecen React o nginx, o si Superset deja de
declararse interno. Es el mismo desfase que ya costó caro con la ficha de ML-01: documentación que
afirma algo que dejó de ser verdad.

## 2. Reconciliación con dos refactors de `main`

- **Se retiraron 6 vistas heredadas** (decisión de Marina García, `38a16fd`) y cambió el router. Se
  adoptó **su estructura completa** —las 7 pantallas— y se sumó `/como-funciona` al final, marcada
  como pantalla de referencia fuera del relato. También el renombre `casos/:cct` → `escuela/:cct`.
- **Se eliminó `Topbar.jsx`**, reemplazado por `Sidebar` + `Header`. Se aceptó el borrado y la
  entrada de menú se movió al `Sidebar`, en una sección **«Referencia»** nueva y **sin número de
  fase**: no es una de las 7 pantallas del relato. Registrada en `navFases.js` para el breadcrumb.

## 3. La pantalla en blanco: dos causas, no una

**Caché de Vite apuntando a `mermaid`.** Ésta era la del blanco. Al desinstalar la librería, la
caché de dependencias pre-optimizadas siguió referenciando sus módulos (`erDiagram-*.js`,
`pieDiagram-*.js` seguían en `node_modules/.vite`), así que
`ENOENT: ... mermaid/dist/mermaid.core.mjs` hacía fallar la carga de `BloqueAbout.jsx` y React no
pintaba nada. Se borró la caché. **Es un efecto de instalar y desinstalar en la misma sesión; no
reproduce en una instalación desde cero.**

**La compuerta de sesión que entró hoy en `App.jsx`.** Aunque hubiera cargado, no se vería: sin
sesión toda la app manda a `Login`. Eso **contradice una decisión explícita del proyecto** —
`src/api/v1/__init__.py` declara `about` *«público siempre, independiente de
`AUTH_LECTURA_PUBLICA`: es metadata del sistema, no dato de escuela»*. El API la servía a
cualquiera y la interfaz pedía login para verla.

Se añadió `RUTAS_PUBLICAS` en `App.jsx`: una lista explícita, con una sola entrada, que deja pasar
la sección conservando el chrome. Se verificó que `Sidebar` y `Header` ya manejan
`status === "anonimo"` sin reventar.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Modificados:** `src/api/v1/about.py`, `frontend/src/App.jsx`, `frontend/src/main.jsx`,
  `frontend/src/components/Sidebar.jsx`, `frontend/src/lib/navFases.js`,
  `tests/test_api_contract.py`, `api/openapi.v1.json` (regenerado con su script)
- **Eliminado:** `frontend/src/components/Topbar.jsx` (se adopta el borrado de `main`)
- **Decisiones autónomas del agente:** conservar la atribución por células para la narrativa de
  construcción y citar `E5` solo en las filas nuevas; poner «Cómo funciona» como sección de
  referencia **sin número de fase**; resolver la ruta pública con una lista explícita en vez de un
  flag por pantalla.
- **Correcciones manuales:** ninguna al código. **La suite de geometría reprobó un error propio**:
  la etiqueta «REST · mismo origen» se colocó centrada entre FastAPI y FARO Web, pero ese hueco
  mide 60 px y el texto ~97 — se encimaba con las dos cajas. Se bajó. Es la tercera vez que esa
  prueba caza algo que la revisión a ojo no vio.
- **Prompt inicial:** actualizar componentes, memoria técnica y diagrama; después, «la página se
  muestra en blanco».

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] **Sin dependencias nuevas**: `package.json` y `package-lock.json` intactos;
      `npm audit --omit=dev` → **0 vulnerabilidades**
- [x] `pytest tests/ -q` → **1303 passed, 10 skipped**
- [x] `ruff` y `oxlint` limpios · `npm run build` correcto (673.42 kB, bajó de 982 porque `main`
      retiró las 6 vistas heredadas)
- [x] DevLog enlaza a los IDs afectados

**Verificación que sustituye a la captura de pantalla.** Sin herramienta de navegador, se contrastó
por programa **los 36 bloques que sirve la API contra los campos que lee cada renderer de React** —
incluyendo que ninguna fila de tabla tenga menos celdas que columnas y que ningún enlace del
diagrama de flujo apunte a un nodo inexistente. **Cero problemas.** Es la otra clase de defecto que
deja la página en blanco, y era lo verificable sin ver la pantalla.

## Bloqueantes y dependencias

- **`frontend/src/App.jsx` es el layout raíz de todas las pantallas y su compuerta de
  autenticación.** El cambio son tres líneas y sólo alinea la UI con lo que el API ya declara, pero
  cae en la **regla 7** (seguridad → revisión humana explícita) y el archivo es verde de **Diana
  Alvarez**. Se pide su revisión de forma expresa en el PR.
- **El gate de propiedad reprueba**: `frontend/**` es de Diana y `src/api/**` no está en el alcance
  de ningún integrante de E1 — `ownership.yml` conserva para los tres los alcances de sus células
  anteriores. Pendiente de Edgar desde el 11-sep.
- **`DEC-026` sigue sin hacerse**, con las tres dependencias ya registradas: `LINEA_DE_ALERTA` no
  existe en `src/modelos/**`, el máximo real de este Gold es 0.3744 y no 0.5717 (corrida personal,
  `mlflow_run_id = local-sin-mlflow`), y la prueba guarda saldría roja aquí.

## Próximos pasos

- Revisión de Diana Alvarez sobre `App.jsx` y la pantalla; de Manuel Serranía y Carlos Mayorga
  sobre el contenido.
- **Decisión de Manuel:** retirar o no `BloqueMermaid` del contrato, que ya nada emite.
- Con los ocho tipos portados, **retirar el shell de Streamlit ya no pierde funcionalidad** de esta
  sección; la decisión es de E5.

## Adenda — CI del PR #350

Tres checks reprobaron al abrir el PR. Los tres eran míos de resolver:

**1 · Tres `.md` sueltos en la raíz reprobaban `vault_lint`** (los dos jobs de vault, misma causa):
`PLAN_US206_EMBEBIDO.md`, `avisosequipo.md` y `plan7diasporpersona.md`. **No están en `main`**:
entraron a mi rama el 11-sep, cuando mergeé `dev/manuel-serrania` para construir sobre US-601, y
vienen del merge de `componentes-back` — el propio bosquejo de Manuel ya los señalaba como ajenos a
la historia. Son notas de trabajo suyas (su plan de US-206, mensajes al equipo, planes de 7 días) y
la raíz del repositorio les está prohibida por `Definition_of_Filed`.

**Se retiran de mi rama, no se pierden**: siguen en `origin/dev/manuel-serrania` y en su historia.
Lo que se evita es arrastrarlos a `main` a través de este PR. Dónde deben vivir es decisión de
Manuel.

**2 · El check de plantilla marcaba una casilla sin marcar.** La línea
*«(Alternativa) No usé IA en este cambio»* lleva `<!-- opcional -->` en la plantilla oficial y yo lo
omití al redactar el cuerpo. Como sí usé IA, la alternativa no aplica: se borra, que es lo que el
propio mensaje del check indica.

**Error de método, vale registrarlo:** verifiqué la plantilla en local y me dio verde **falso**. El
script lee el cuerpo de la variable de entorno `PR_BODY` y yo se lo pasé como argumento, así que
evaluó una cadena vacía. La invocación correcta es
`PR_BODY="$(cat cuerpo.md)" bash .github/scripts/verificar_plantilla_pr.sh`. Es el mismo modo de
falla que el PM ya registró dos veces —dar por verificado lo que se comprobó mal— y por eso queda
escrito aquí en vez de corregirse en silencio.

## Adenda 2 — ajustes pedidos por Edgar Coronel en la revisión del PR #350

Aprobó el contenido y pidió ajustes antes de mergear. Aplicados:

**1 · Fuera `.claude/settings.json` y los 4 archivos de `gx/**`.** Mismo caso que los tres `.md`:
no están en `main`, entraron por el merge de `dev/manuel-serrania` y sobreviven ahí. Se retiran del
control de versiones; **siguen en disco**, que es lo correcto porque son locales.

**Hallazgo al verificarlo, más fuerte que «están fuera de alcance»: los cinco estaban rastreados
pese a estar en `.gitignore`.** `gx/` está ignorado en la línea 50 —con el comentario de que es *«el
contexto por defecto que crea Great Expectations 0.18+ al llamar `get_context()` sin dir»*— y
`/.claude/` en la 104. Además **ningún código los usa**: las ocho validaciones de `src/ingesta/`
apuntan a `context_root_dir="great_expectations"`, la carpeta real, no a `gx/`. O sea que `gx/` es
andamiaje autogenerado que el repositorio ya declaraba que nunca debía versionarse, y se coló de
todas formas. Vale la pena que alguien revise cómo, porque el mecanismo puede repetirse.

**2 · `superset/**` declarado como transversal.** El geojson de la silueta nacional y su generador
son alcance de **Equipo 3** (`superset/**` es verde de Marina García del Buey, con Monserrat
Miranda y Oscar Quiroz). Se declara en la descripción del PR y se pide su revisión.

**Nota devuelta a Edgar:** dijo «tres ajustes» y enumeró dos. Se aplicaron los dos; queda pendiente
que confirme cuál era el tercero.
