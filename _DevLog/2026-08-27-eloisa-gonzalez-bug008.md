---
id: DEVLOG-2026-08-27-ELOISA-US422-BUG008
fecha: 2026-08-27
owner: "Eloisa Gonzalez Rubio"
status: done
historia: US-422
bug: BUG-008
herramienta_ia: Claude (Copilot)
traces_up: ["US-422"]
traces_down: ["BUG-008"]
---

# DevLog — US-422: guarda de regresion para BUG-008

## 1. Contexto

Edgar Coronel (PM) reasigno a Eloisa a US-422 y pidio arrancar por BUG-008: hoy
ninguna prueba verifica que aplicacion arranca el contenedor de la API. El
Dockerfile (`docker/api.Dockerfile`) levantaba `src.api.main:app` (el
"hola-mundo" de 3 rutas de US-501) en vez de `src.api.app:app` (el contrato
real con 18 rutas bajo `/api/v1`). Severidad `high`; bloqueaba el ensayo E2E
del 28-29 de agosto.

Tras compartir el diagnostico con Edgar y Christian, Edgar confirmo dos cosas
importantes que reencuadran esta entrega:

1. Luis Tellez ya habia corregido el bug en `main` (rama
   `fix/luis-tellez-bug008-api-dockerfile`, 27 de agosto) antes de que esta
   sesion terminara.
2. El unico test de regresion que existia para BUG-008 era un `curl` manual
   contra produccion. **No existia ninguna prueba automatizada del entrypoint
   del contenedor.** Por lo tanto, el entregable real de esta sesion no es
   "detectar BUG-008" (ya resuelto por Luis), sino **US-422**: dejar la
   primera prueba automatizada de esa guarda para que el bug no pueda
   regresar sin que el CI lo note.

## 2. Que se le pidio a la IA

- Disenar, paso a paso y sin escribir codigo hasta entender el problema, una
  prueba que:
  1. lea el `CMD` de `docker/api.Dockerfile`,
  2. identifique/importe la app que ese `CMD` nombra,
  3. verifique que esa app expone las rutas del contrato v1.
- Usar `tests/test_frontend_chat_streamlit.py` (Andres Gonzalez Habib, US-305)
  como modelo de estilo: cargar un recurso real del repo y validar
  comportamiento real, no solo texto estatico.
- Ayudar a preparar el entorno local (venv con Python 3.11) para poder
  ejecutar `pytest` dentro de WSL.
- Tras la revision de Edgar: ajustar la prueba para que las rutas esperadas
  del contrato v1 salgan del esquema OpenAPI en vivo, no de una lista escrita
  a mano (para que no genere falsos positivos cuando el contrato crezca).
- Ayudar a resolver un desfase de `git status` (415 archivos marcados como
  modificados por un problema de finales de linea CRLF/LF, no por cambios
  reales) y a traer el fix de Luis a la rama de trabajo con `git pull origin
  main --no-rebase`.

## 3. Que genero la IA

- Analisis guiado del repositorio (sin modificarlo) para localizar:
  - el `CMD` real del Dockerfile,
  - las dos apps FastAPI existentes (`src/api/main.py` y `src/api/app.py`),
  - la ausencia de una prueba automatizada del entrypoint (solo existia el
    `curl` manual mencionado por Edgar).
- Archivo `tests/test_docker_api_entrypoint.py` con 3 pruebas:
  1. `test_dockerfile_declara_un_cmd_uvicorn` — el Dockerfile declara `CMD
     uvicorn`.
  2. `test_referencia_del_cmd_es_extraible` — se puede extraer la referencia
     `modulo:atributo` del `CMD` con una expresion regular.
  3. `test_app_que_arranca_el_contenedor_expone_el_contrato_v1` — importa
     dinamicamente la app que el Dockerfile declara y compara sus rutas
     OpenAPI contra las rutas oficiales del contrato v1, obtenidas en vivo
     desde el esquema OpenAPI de `src.api.app` (funcion
     `_rutas_del_contrato_v1()`), sin ninguna ruta escrita a mano.
- Ayuda para crear un entorno virtual (`~/venvs/concausa-bi`, Python 3.11)
  fuera de OneDrive, porque el `.venv` dentro del repo (sincronizado por
  OneDrive) no creaba correctamente los symlinks de `bin/`.
- Diagnostico y solucion del problema de `git status` (415 archivos con
  finales de linea distintos, 0 cambios de contenido real) mediante `git
  checkout -- .`, antes de traer el fix de Luis con `git pull`.

## 4. Que revise yo (Eloisa)

- Confirme que el `CMD` real del Dockerfile apuntaba a `src.api.main:app`
  antes del fix de Luis, y a `src.api.app:app` despues del `git pull`.
- Confirme que `src/api/main.py` solo expone `/`, `/health`, `/info` (sin
  `/api/v1`).
- Confirme que `src/api/app.py` monta `api_v1_router` bajo `API_PREFIX =
  "/api/v1"` y expone 18 rutas reales (verificado ejecutando
  `app.openapi()["paths"]` directamente, no solo confiando en el conteo de
  Edgar).
- Revise linea por linea ambas versiones del archivo de prueba antes de
  ejecutarlas.
- En la primera version, decidi explicitamente usar las 12 rutas oficiales de
  `test_api_contract.py` en vez de una seleccion propia de 6 rutas.
- Tras la observacion de Edgar (12 rutas hardcodeadas vs. 18 reales), ajuste
  la prueba para eliminar por completo cualquier lista de rutas escrita a
  mano y leerlas dinamicamente del esquema OpenAPI de `src.api.app`.
- Verifique con `git diff --stat` que el desfase de 415 archivos en
  `git status` era unicamente un problema de finales de linea (mismas
  inserciones que eliminaciones), antes de descartar esos cambios.
- Ejecute la prueba en ambas versiones:
  - Antes del fix de Luis: `1 failed, 2 passed` (confirma el bug).
  - Despues del fix de Luis y del ajuste de rutas dinamicas: `3 passed`
    (confirma que la guarda funciona y no genera falsos positivos).
- No modifique `docker/api.Dockerfile`, `src/api/main.py` ni `src/api/app.py`
  (correccion realizada por Luis Tellez, fuera de mi alcance).

## 5. IDs tocados

- Historia: US-422
- Bug: BUG-008 (ya corregido por Luis Tellez; esta entrega deja su guarda de
  regresion automatizada)

## 6. Archivos nuevos/modificados

- `tests/test_docker_api_entrypoint.py` (nuevo)

## 7. Commits en la rama feat/eloisa-actividades

- `9803e16` — `test(api): valida que el Dockerfile arranque el contrato v1
  (BUG-008, US-422)` — primera version, con 12 rutas oficiales copiadas de
  `test_api_contract.py`.
- `69c5798` — `test(api): compara rutas del CMD contra el esquema OpenAPI en
  vivo (BUG-008, US-422)` — ajuste pedido por Edgar: rutas leidas
  dinamicamente, sin hardcodear ninguna.

## 8. Estado y siguiente paso

- Prueba lista, revisada y en verde (`3 passed`) contra el estado actual de
  `main` (con el fix de Luis ya integrado via `git pull origin main
  --no-rebase`).
- Avisado por Teams a Edgar y Christian con el diagnostico original; Edgar
  confirmo el fix de Luis y pidio el ajuste de rutas dinamicas, ya aplicado.
- Pendiente: push de la rama y solicitud formal de revision de codigo a
  Christian (Tech Lead de Celula 4) antes de abrir el PR.
- Pendiente (US-422, fuera de esta entrega): `dependency_override` en
  `tests/test_api_contract.py::test_municipio_ok_y_404` (linea 101,
  actualmente hardcodea `/municipios/09010`) y recuperar las 5 pruebas
  omitidas en CI por falta de `pyyaml`/`streamlit` en requirements.
