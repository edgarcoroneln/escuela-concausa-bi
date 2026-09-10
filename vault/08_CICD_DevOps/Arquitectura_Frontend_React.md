---
id: DOC-FRONTEND-ARCH
title: "Arquitectura del Frontend React (rediseño post-feedback del Dr.)"
owner: "Diana Álvarez / Luis Téllez (Equipo x: Front + Deploy en Prod)"
status: draft
traces_up: ["REQ-005"]
tags: [frontend, react, arquitectura, deploy, equipo-x]
date: "2026-09-10"
---

# Arquitectura del Frontend React

> Contexto: el Dr. pidió tirar Superset/Streamlit visibles y rehacer el
> frontend 100% custom, con estética propia. Equipo x (Diana + Luis) es
> responsable de programarlo y dejarlo en producción para el sábado en la
> mañana. Este doc deja por escrito las decisiones de herramienta y
> estructura antes de construir el contenido de las 12 pantallas, para no
> improvisar sobre la marcha y que Luis pueda tomar el deploy sin
> reconstruir el razonamiento.

## 1. Stack

| Pieza | Elección | Por qué |
|---|---|---|
| Framework | **React 18 + Vite** | Angular quedaba descartado por curva de aprendizaje (TS obligatorio, DI, RxJS, Zone.js) contra 2.5 días y JS nivel medio sin experiencia previa en React/Angular. |
| Estilos | **Tailwind CSS v4** (`@tailwindcss/vite`) | Cero CSS a mano, tokens de color centralizados en `src/index.css`, ya alineados con el mockup de storytelling que mandó UX/UI. |
| Gráficas estándar | **Recharts** | Barras, donas — cubren la mayoría de los ~103 charts sin reinventar cada una. |
| Gráfica flagship + mapa | **D3.js** (targeted) | El Dr. pidió D3 explícitamente. Se usa donde de verdad aporta: el gauge radial de riesgo (`RiskGauge.jsx`) y el mapa de México (`MapaRiesgo.jsx`, `d3-geo` + geojson real de estados). |
| Ruteo | **React Router v6** | Necesario en cuanto pasamos de un dashboard único al storytelling de "7 casos" con pantallas propias. |
| Datos | `fetch` nativo envuelto en `src/lib/api.js` | Sin librería de data-fetching (React Query, SWR) para no sumar curva de aprendizaje; con el volumen de datos de esta demo no hace falta cache/reintentos sofisticados. |

## 1.1 Por qué #1 y no las otras 4 — evidencia de una prueba real, no solo research

Antes de comprometernos con este stack armamos y corrimos las 5 combinaciones candidatas de verdad
(no solo comparamos en el papel): la misma gráfica de matrícula construida 3 veces (Recharts / D3 a
mano / Observable Plot) y el mismo mapa de México construido 2 veces (D3-geo a mano / react-simple-maps),
más un quinto candidato completo (Angular + ngx-charts + D3) montado desde cero como proyecto aparte.

| # | Combo | Líneas (pieza equivalente) | Fricción real encontrada hoy |
|---|---|---|---|
| **1** | **React + Recharts + D3 (gauge/mapa)** ← elegido | 37 (gráfica) / 90 (mapa) | Ninguna nueva — ya en producción. |
| 2 | React + D3 100% a mano | 74 (gráfica) | El doble de código que Recharts para un resultado visualmente equivalente; viable pero replicarlo en las ~8 piezas del catálogo cuesta días que no tenemos. |
| 3 | React + Observable Plot + D3 | 29 (gráfica) | Es otra librería de charts encima de D3, no D3 "puro" — el Dr. la vería igual que Recharts en ese sentido. |
| 5 | React + react-simple-maps + D3 | 48 (mapa) | Trajo 4 dependencias nuevas (`react-simple-maps`, `topojson-client`, y de rebote `prop-types` + `react-is`) que nos rompieron el build 3 veces distintas hoy mismo (`Failed to resolve import`, página en blanco sin error en consola, `require` no soportado en el navegador). Señal real de inestabilidad, no mala suerte. |
| 4 | Angular + ngx-charts + D3 | — | Proyecto aparte completo: `ng new` interactivo (~6 prompts), CLI no queda en el PATH (`command not found: ng`), la versión actual de ngx-charts todavía no es standalone (hay que importar `NgModule`, patrón viejo), y dos dependencias (`@angular/animations`, `@angular/cdk`) no se instalan solas con `--legacy-peer-deps`. Duplica el proyecto (segundo `node_modules`, segundo pipeline de build/deploy) sin ninguna ganancia visual sobre el combo 1. |

**Conclusión:** el combo 1 es el que ya está en producción, el que menos fricción mostró en la prueba
de hoy, y el único que no obliga a elegir entre "menos código" y "estabilidad". El D3 "de verdad" que
pidió el Dr. sigue presente y visible (gauge de riesgo + mapa) — no desaparece, solo no está en cada
gráfica del proyecto.

## 2. Estrategia: componentes reutilizables, no 103 piezas a mano

En vez de construir cada gráfica del catálogo original como pieza única,
se armó una librería chica de componentes genéricos, guiados por props
(`KpiCard`, `Card`, `BarChartCard`, `DonutChartCard`, `RankingList`,
`DataTable`, `RiskGauge`, `MapaRiesgo`, `DriverMatrix`) que se combinan
para armar cada pantalla. Esto es lo que hace viable el timeline:
construir ~9 piezas una vez, no 100+ piezas bespoke.

## 3. Estructura de carpetas

```
frontend/
  src/
    components/   -> piezas reutilizables (una gráfica/bloque = un componente)
    pages/        -> una pantalla del storytelling = un archivo (rutas del router)
    lib/api.js    -> único punto de contacto con el API real (api/openapi.v1.json)
    data/mock.js  -> datos de ejemplo (reales donde ya están verificados) mientras
                     se conecta cada pantalla al API
    data/geo/     -> geojson de México para el mapa
  Dockerfile no vive aquí -> ver docker/frontend-react.Dockerfile (mismo patrón que
  docker/api.Dockerfile, contexto = raíz del repo)
```

## 4. Rutas (storytelling "7 casos", del mockup de UX/UI)

`/` Home · `/casos` Los 7 casos · `/casos/:cct` Expediente de la escuela ·
`/vista-general` · `/comparativa` · `/mapa` · `/drivers` (matriz) ·
`/comparacion-territorial` · `/hallazgos`.

Estado actual: el layout, el router, la navegación y la identidad visual
del mockup (top nav oscuro, paleta, matriz de drivers con escala
divergente) ya están aplicados. Home, Los 7 casos, Vista general, Mapa,
Drivers y Expediente tienen datos reales/mock conectados; Predicción y
Recomendación dentro del expediente son la siguiente fase de contenido.

## 5. El mapa (D3 + geojson real)

`MapaRiesgo.jsx` usa `d3-geo` (proyección Mercator ajustada al bbox) sobre
un geojson real de los 32 estados de México (fuente:
`github.com/angelnmara/geojson`, ~180KB, guardado en
`src/data/geo/mexico-states.json`). Los 7 casos se ubican por
`latitud`/`longitud`, que el API real ya expone en `EscuelaDetalleOut`
— hoy son datos mock (2 de los 7 son reales y verificados: el par
diferenciador en Ecatepec; los otros 5 son coordenadas de placeholder
dentro de municipios reales, marcadas así en el código). Pendiente:
sustituir por `getEscuelas({ indice_riesgo_min: 0.5 })` en cuanto ese
filtro exista en el API.

## 6. Ventaja de este stack sobre el backend actual

El punto de comparación no es solo "React vs Angular vs las otras opciones" — es también qué tanto le
pide este frontend al backend, comparado con lo que le pedía Streamlit:

- **Streamlit corría del lado del servidor** (proceso Python con `st.session_state`) y hacía sus
  llamadas al API desde ahí — el frontend mismo era un servicio con estado que dependía de mantenerse
  vivo y sincronizado con la sesión del usuario.
- **React es 100% estático del lado del cliente.** `frontend-react.Dockerfile` compila con Vite y nginx solo
  sirve archivos — el backend ya no tiene que saber nada de "sesión de Streamlit", solo responder JSON
  a peticiones REST normales desde el navegador (`src/lib/api.js`, que ya habla el contrato real de
  `api/openapi.v1.json`: `getKpis`, `getEscuelas`, `getPrediccion`, etc.). **Auth, decisión 10-sep
  (Luis + Christian):** el frontend no maneja tokens — `nginx` hace `proxy_pass` de `/api/*` a la API
  (un solo origen), `/auth/exchange` deja una cookie `httpOnly` host-only, y `api.js` solo necesita
  `credentials: "same-origin"`. Detalle completo en
  [[vault/03_Architecture/ADRs/ADR-012-retiro-streamlit-frontend-nativo|ADR-012]]. Pendiente: cambiar
  `credentials: "include"` → `"same-origin"` en `api.js` una vez que Luis tenga el `proxy_pass` listo.
- **Consecuencia práctica:** el ciclo de release del frontend queda desacoplado del backend — se puede
  redesplegar el frontend sin tocar el API, y viceversa. El servicio de Cloud Run del frontend pesa
  menos (256Mi / 1 CPU, sin Secret Manager ni VPC connector) que un servicio con estado.
- **Ya hay diseño de fallback:** cada función de `api.js` devuelve `{ data, error }` en vez de lanzar
  excepción, así que si C3 (agente) o C4 (auth) todavía no terminan su parte, la pantalla cae a
  `mock.js` sin romper la demo — no bloquea al resto del equipo.

## 7. Deploy (Cloud Run) — mismo patrón que el API

- `docker/frontend-react.Dockerfile`: build multi-stage (Node 22 compila con
  Vite → nginx alpine sirve `dist/` como estático). Fallback SPA
  (`try_files ... /index.html`) para que rutas como `/casos/15DPR0920D`
  no den 404 al recargar.
- `vault/08_CICD_DevOps/scripts/build-and-push-frontend.sh` +
  `deploy-cloud-run-frontend.sh`: mismos PROJECT_ID/REGION/Artifact
  Registry (`faro-images`) que usa Luis para el API, mismo estilo de
  script. Servicio Cloud Run: `faro-frontend` (reemplaza al Streamlit
  actual en esa misma URL una vez que se apunte el deploy ahí).
- Sin Secret Manager ni VPC connector: es estático, no toca la DB
  directo — llama al API real desde el navegador vía
  `frontend/.env.production` (`VITE_API_BASE_URL`).

**Qué tan complicado es, en concreto:** bajo, comparado con el deploy del API real. No es un servicio
nuevo desde cero — reutiliza el mismo proyecto GCP, la misma Artifact Registry y el mismo patrón de
script que Luis ya corrió y documentó en `Cloud_Run_Deploy.md`.

1. **`docker build` validado el 10-sep** — corre limpio (17/17) y el contenedor sirve el `index.html`
   (`200 OK` probado con `docker run` local). Fix aplicado: `npm ci` necesitaba `--legacy-peer-deps`
   (mismo choque de peers que en local, `react-simple-maps` vs. React 19). Pendiente: rehacer el
   Dockerfile para correr non-root (`nginx-unprivileged` o `USER` explícito) — lo pidió Christian en
   la revisión de seguridad del gate del jueves.
2. **CORS ya no es un bloqueante.** Se descartó por diseño: `/api/*` se sirve por el mismo origen vía
   `proxy_pass` de nginx (Luis), así que el navegador nunca cruza orígenes. Lo que sí falta: Luis
   agrega el `proxy_pass` + headers `CSP`/`X-Frame-Options` en `docker/nginx-frontend.conf.template`,
   y Christian agrega `HSTS`/`X-Content-Type-Options`/`Referrer-Policy` en la API.

Nada de esto requiere aprender herramienta nueva ni tocar infraestructura nueva — es ejecutar el mismo
procedimiento que ya está probado para el API, una vez por cada punto de la lista de arriba.

## 8. Qué necesitamos de otros equipos

- **Christian (C4, backend/seguridad) — cerrado 10-sep, ya no es CORS.** Decisión final: cookie
  `httpOnly` host-only vía `proxy_pass`, sin BFF. De su lado: `Set-Cookie` en `/auth/exchange` y
  `/refresh`, fallback de cookie en `deps.py`, y headers `HSTS`/`X-Content-Type-Options`/
  `Referrer-Policy` en la API (~1h de trabajo, según él mismo). Detalle en `ADR-012`.
- **Christian/C4 (segundo punto, no bloqueante para hoy):** confirmar que `EscuelaDetalleOut` ya trae
  `latitud`/`longitud` reales para los 7 casos — hoy 5 de 7 son coordenadas placeholder documentadas
  como tal en el código.
- **Equipo 6 (UX/UI — Marina, Oscar, Juan Macias, Monse):** el mockup de storytelling de 12 pantallas
  ya se está siguiendo al pie de la letra (paleta, tipografía Inter, semáforo de riesgo). Falta que
  confirmen si los tokens de color que se sacaron del mockup (`src/index.css`) son los definitivos o
  si hay una guía de marca más formal que debamos usar en su lugar.
- **Edgar (PM):** este documento pivotea de lo que dice `ADR-002` (Streamlit sobre Superset + API,
  `accepted`) hacia un frontend 100% custom — es un cambio de arquitectura, no un ajuste menor.
  Recomendación: que Edgar lo revise y decidamos juntos si esto se formaliza como un ADR nuevo que
  supersede a ADR-002 (documentando que el cambio viene de una instrucción directa del Dr.
  post-demo), siguiendo el mismo proceso que ya usamos para ADR-010. Evita que alguien del equipo se
  sorprenda viendo Streamlit reemplazado sin que quede registrado por qué.
- **Luis (mismo Equipo 5):** `proxy_pass` de `/api/*` en nginx (habilita la cookie de un solo
  origen), headers `CSP`/`X-Frame-Options` en `docker/nginx-frontend.conf.template`, y correr el
  deploy real (`build-and-push-frontend.sh` + `deploy-cloud-run-frontend.sh`) — el `docker build` ya
  quedó validado, así que esto ya no espera nada de Docker Desktop.

## 9. Qué falta (siguiente fase, contenido pantalla por pantalla)

- Tarjetas de "Pistas"/drivers con íconos (parcialmente hecho en Los 7 casos).
- Gráfica de predicción con tramo punteado (forecast) y tab de Recomendación dentro del expediente.
- Conectar cada pantalla a `src/lib/api.js` en vez de `mock.js`.
- Confirmar con Equipo 6 la paleta/tipografía final (ver §8).
- Code-splitting por ruta (`React.lazy`) si sobra tiempo — el bundle pesa ~940KB, no bloqueante para
  la demo pero señalado por Vite en el build.
