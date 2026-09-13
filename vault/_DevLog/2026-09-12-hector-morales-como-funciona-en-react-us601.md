---
project: "FARO"
date: "2026-09-12"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "2h"
touches: ["US-601", "US-621", "REQ-002", "REQ-007", "DEC-026", "BUG-063", "BUG-077"]
tags: [devlog, us-601, componentes, frontend, react, equipo-1]
---

# DevLog — 2026-09-12 — «Cómo funciona» en la UI nativa y validación de las notas del equipo (US-601)

→ [[vault/_DevLog/_index|Volver al índice]]

## Qué se hizo

1. **La sección «Cómo funciona» ahora existe también en el frontend de React** (`/como-funciona`),
   consumiendo el mismo contrato de bloques que ya consumía el shell de Streamlit.
2. **Se eliminó una página duplicada** que Streamlit estaba mostrando dos veces.
3. **Se validaron contra este ambiente las notas que dejó el equipo** el 11 y 12 de septiembre;
   dos de ellas cambian de lectura con la evidencia de aquí.

## 1. La sección en React

`frontend/src/pages/ComoFunciona.jsx` pide el manifest y pinta lo que venga: **agregar, quitar o
reordenar una sección del lado de la API no obliga a tocar la pantalla**, que es justo lo que el
contrato de bloques buscaba cuando se diseñó para Streamlit. Cinco de los ocho tipos de bloque
están portados (`markdown`, `tabla`, `metricas`, `svg`, `barras`); los otros tres **se declaran en
pantalla** con un recuadro de «pendiente de portar» en vez de omitirse — misma política que
`SIN_DATO` aplica a los datos.

### `mermaid`: se probó, se midió y se revirtió

La primera versión instalaba `mermaid` para dibujar los cuatro E-R. **Se deshizo tras auditarla**:

| | |
|---|---|
| `mermaid@^12` | `chevrotain` → `lodash-es`, **2 avisos de severidad alta** (inyección de código, contaminación de prototipo) |
| `mermaid@^11` | la misma cadena vulnerable — no hay línea limpia hoy |
| Costo | **69 paquetes transitivos, 123 MB** para cuatro diagramas |
| Tras quitarlo | `package.json` y `package-lock.json` **idénticos a `HEAD`**, `npm audit` → **0 vulnerabilidades** |

Meter una dependencia con avisos altos en el `package.json` de otra persona es un cambio de
seguridad, y la **regla 7** del vault pide revisión humana explícita. **La salida de fondo no es
otra librería**: es servir esos cuatro diagramas como bloques `svg` desde la API —igual que ya se
hace con el de arquitectura—, que los dibuja una vez, sin dependencia, y sirve a las dos interfaces
a la vez. Queda propuesto, no hecho.

### Markdown sin librería, por medición

Se midió el contenido real que sirve la API en las 6 secciones: código en línea (53), negritas
(26), encabezados `###` (5) y una lista numerada. Nada de enlaces, imágenes ni HTML. Se escribió un
renderer de ~40 líneas para ese subconjunto en vez de traer un parser completo y su superficie de
HTML arbitrario. **Modo de falla declarado:** Markdown fuera del subconjunto se ve literal, no roto.

### Costo real en el bundle, medido

Se construyó con y sin la pantalla, en el mismo árbol:

| | JS | gzip |
|---|---|---|
| Sin la pantalla | 959.57 kB | 293.78 kB |
| Con la pantalla | 968.67 kB | 296.29 kB |
| **Aporte** | **+9.1 kB** | **+2.5 kB** |

El aviso de «chunk mayor a 500 kB» **ya existía** (d3 + recharts); no lo introduce este cambio.

## 2. La página duplicada de Streamlit

El menú mostraba «Cómo funciona» **dos veces**. Causa: `src/frontend/pages/4_Como_Funciona 2.py`,
una copia de sincronización de iCloud (el repositorio vive en un Desktop sincronizado). Streamlit
descubre páginas leyendo el directorio, así que cualquier archivo ahí se vuelve una entrada del
menú. Se diffeó antes de tocarla —era el archivo vivo **menos** las 24 líneas del bloque `svg`, sin
nada propio— y se **movió fuera** del repositorio, no se borró.

**No es un defecto del proyecto y va a volver** mientras el repositorio viva en la carpeta
sincronizada: hay **46** archivos así hoy, incluido un `frontend/src 2` completo. Ninguno está
rastreado; el riesgo real es un `git add .` a ciegas.

## 3. Validación de las notas del equipo

| Nota | Estado tras validarla aquí |
|---|---|
| **Edgar** — «faltan `shap_d1..d6`; confirmar contra un ambiente que no sea el mío antes de escalarlo» | **Confirmado y diagnosticado.** Reproduce aquí (`/predicciones/{cct}` → 503), así que no es el volumen del PO. **No es defecto de código**: `publicar_gold.py:592-606` ya migra idempotente. Causa: ambas bases salieron de un dump anterior al `ALTER` del 7-sep y nadie ha corrido `publicar_gold` en local. Lo arregla la republicación de `DEC-026` |
| **Edgar** — `BUG-077` crítico, `/municipios` 500 por `nombre_entidad` nulo | **No reproduce aquí.** `gold.dim_municipio`: 317 filas, **0 nulos** en `nombre_entidad`; `/municipios` y `/municipios/14113` → **200**. Sí coincide lo disperso de `poblacion` (10 de 317). **Su hallazgo de fondo sigue en pie y es el importante**: ningún workflow corre `dbt test`, así que la guarda `not_null_dim_municipio_nombre_entidad` nunca se ejecuta |
| **Plan de QA §4** — verificación local de ML | **Hecha.** 66/66 en las cuatro suites; `/api/v1/version` responde con `cortes_atencion`. MLflow local vacío, igual que reportó Deni |
| **Manuel** — confirmar el bosquejo de `US-601` | **Confirmado** en el DevLog del 11-sep |
| **Manuel** — reportar a Edgar la inconsistencia de `ownership.yml` en E1 | **Documentado, no escalado.** Está en el DevLog y en el mensaje del commit; falta pedírselo a Edgar de forma directa |
| **`DEC-026`** — bajar el corte de `prioridad` a 0.50, republicar Gold, prueba guarda | **No hecho, con tres dependencias** (§4) |

## 4. `DEC-026`: por qué no se hizo todavía

**Tres dependencias, ninguna de código propio:**

1. **La constante no existe en esta capa.** `LINEA_DE_ALERTA` vive en `src/api/repositorio_gold.py`
   (C4) y en `src/frontend/prediccion_client.py` (C2). Importarla desde el API invertiría la
   dependencia; definir una tercera copia agrava `RISK-010`. **Propuesta:** definirla en
   `src/modelos/riesgo.py` como fuente canónica más una prueba que ate la copia del API — que es
   exactamente lo que `RISK-010` pide y no toca el archivo de nadie más.
2. **El número de la decisión no coincide con este Gold.** `DEC-026` se apoya en un máximo de
   `indice_riesgo` de **0.5717**; aquí el máximo real es **0.3744**, así que con el corte en 0.50
   **seguiría habiendo cero filas `alta`** y `BUG-063` no cerraría. La procedencia lo explica: este
   Gold trae `mlflow_run_id = local-sin-mlflow` —una corrida personal— y no
   `bug048-20260905-temporal-robusto`. **Republicar contra la base equivocada sobrescribiría
   producción con una corrida personal.**
3. **La prueba guarda no puede ser absoluta.** Con corte 0.50 y máximo 0.3744 saldría **roja aquí**.
   Tiene que correr sobre fixture o parametrizarse por el Gold publicado, no consultar la base que
   esté conectada.

**Contradicción ya viva en `main`, sin relación con esta rama:** `/api/v1/version` declara
`alta: 0.50` (C4 mergeó su mitad) mientras la columna `prioridad` se escribió con 0.60. Dos
superficies del mismo sistema dicen cosas distintas hoy; falta la mitad de C3.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Archivos creados:** `frontend/src/pages/ComoFunciona.jsx`,
  `frontend/src/components/BloqueAbout.jsx`, `frontend/src/components/MarkdownLite.jsx`,
  `frontend/src/lib/about.js`
- **Modificados:** `frontend/src/main.jsx` (ruta), `frontend/src/components/Topbar.jsx` (menú)
- **Decisiones autónomas del agente:** portar solo 5 tipos y declarar los 3 restantes en pantalla;
  escribir el renderer de Markdown en vez de traer un parser; **revertir `mermaid` tras auditarlo**;
  derivar el estado de carga en vez de guardarlo (quitó un aviso de `oxlint`).
- **Correcciones manuales:** ninguna al código. La auditoría de dependencias **revirtió** una
  decisión del propio agente (instalar `mermaid`), que es el punto de haberla corrido.
- **Prompt inicial:** ver la sección con la UI nueva y quitar la duplicada.

## Seguridad / calidad

- [x] Sin secretos hardcodeados
- [x] `npm audit --omit=dev` → **0 vulnerabilidades**; `package.json`/`package-lock.json` idénticos a `HEAD`
- [x] `npx oxlint` limpio en los 6 archivos
- [x] `npm run build` correcto
- [x] `pytest tests/ -q` → **1285 passed, 4 skipped** (sin cambios de Python en esta sesión)
- [x] DevLog enlaza a los IDs afectados

`vault_lint` reporta 10 bloqueantes, **todos preexistentes y ninguno de estos archivos**: 6 IDs
duplicados por copias de iCloud sin rastrear y 4 `.md` sueltos en la raíz heredados de
`componentes-back`.

## Bloqueantes

- **El gate de propiedad reprueba.** `frontend/**` es verde de **Diana Alvarez** (`DEC-022/023`, ella
  lidera el frontend nativo en S7) y `src/api/**` no está en el alcance de ningún integrante de E1.
  Esta pantalla la tendría que llevar ella, o Edgar tiene que ampliar el alcance de E1. Se sube a la
  rama propia para revisión, **no para mergear así**.
- `DEC-026` bloqueado por las tres dependencias de §4.

## Próximos pasos

- Preguntar a Edgar: **cuál Gold es el autoritativo**, y si el cambio de `DEC-026` lo hace Estefany
  o Héctor (la decisión nombra a los dos).
- Escalarle también la inconsistencia de `ownership.yml` en E1 y el destino de esta pantalla.
- Proponer a C2/C5 servir los cuatro E-R como bloques `svg` desde la API, para quitar del camino la
  dependencia de `mermaid` en cualquier frontend futuro.
