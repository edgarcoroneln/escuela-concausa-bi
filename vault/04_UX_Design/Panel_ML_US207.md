---
id: DOC-PANEL-ML-US207
title: "Panel de ML interactivo — especificación y alcance entregado (US-207)"
owner: "Marina García del Buey"
status: approved
version: "1.0"
traces_up: ["US-207", "REQ-002", "DOC-FRONTEND-ARCH", "ADR-002"]
traces_down: ["US-321", "US-412", "US-415", "DEC-006", "DEC-015", "BUG-048"]
last_reviewed: "2026-09-05"
tags: [ux, frontend, streamlit, ml, celula-2]
---

# Panel de ML interactivo — US-207

> Especificación de la página `pages/2_Panel_ML.py` de FARO Web: qué muestra, de dónde lo
> toma y **qué no muestra y por qué**.
> → [[vault/04_UX_Design/_index]] · Arquitectura: [[vault/03_Architecture/Frontend_Architecture]] §5
> · Decisión de stack: [[vault/03_Architecture/ADRs/ADR-002-frontend-streamlit]]

## 1. Frontera de este documento

[[vault/03_Architecture/Frontend_Architecture]] (Manuel Serranía) es el documento canónico
de **la capa web completa**: el shell, el router, la sesión y las cuatro páginas. Este
documento **no lo duplica**: especifica una sola página —el panel de ML— al nivel de detalle
que la arquitectura no baja, igual que los `Cube_Specs_*` especifican cubos que
`Data_Model.md` solo enuncia.

Regla 1 del vault: si algo se dice en los dos, manda `Frontend_Architecture`.

> **Discrepancia detectada al implementar, para su dueño.** `Frontend_Architecture` §5 dice
> que el front hace **`POST`** a los endpoints de inferencia. El contrato real es
> **`GET /api/v1/predicciones/{cct}`** (US-412), verificado en local y en producción al
> construir el cliente. Es corrección de Manuel Serranía, no de esta historia.

## 2. Qué entrega la página

Un formulario de CCT que consulta la inferencia y presenta la salida de los modelos en tres
bloques, en el orden en que se leen.

| Bloque | Modelo | Qué muestra | Fuente |
|---|---|---|---|
| §ML-01 | Índice de riesgo | El valor contra el umbral **0.60** de DEC-006, con la lectura de negocio: "proyecta perder ≥ 5 % de su matrícula" | `indice_riesgo` |
| §ML-02 | Driver dominante | El driver que explica el riesgo, con su nombre legible, y la recomendación prescriptiva que se deriva de él | `driver_dominante`, `recomendacion` |
| §ML-03 | Segmento (clustering) | **`SIN_DATO` explícito** — ver §4 | `cluster` |

### 2.1 Por qué el orden importa

No es cosmético. La página está ordenada para que se lea como el argumento del proyecto:
primero **cuánto** riesgo hay, después **por qué**, y de ahí **qué hacer**. Un panel que
solo diera el índice sería descriptivo; el driver y la recomendación son lo que lo vuelve
prescriptivo.

Verificado con dos escuelas de riesgo parecido y driver distinto — **medición local**,
sobre el Gold reconstruido tras BUG-045:

| CCT | `indice_riesgo` | Driver | Recomendación |
|---|---|---|---|
| `15DJN0049A` | 0.7423 | D1 · Pobreza | Priorizar programas de becas y apoyo alimentario |
| `09DSN0042A` | 0.6692 | D2 · Inseguridad | Coordinar rutas escolares seguras y entornos protegidos |

**Mismo nivel de urgencia, intervención distinta.** Es el diferenciador que el PRD promete,
y es lo que esta página hace visible en una sola pantalla.

> **Este par no se puede citar en la demo mientras BUG-048 siga abierto.** La URL pública
> sirve un Gold anterior al fix de BUG-045 y devuelve otra cosa para los mismos CCT:
> `15DJN0049A` da **0.129 / D3** —infraestructura, no pobreza— y `09DSN0042A` da **0.0976 / D2**,
> con `escuelas_en_riesgo = 0` en `/kpis` (reverificado 2026-09-05). El **contraste de drivers**
> se sostiene en local; lo que no se sostiene en producción son los valores.
> Así quedó asentado en **DEC-015**: se ratifica el alcance de la historia, no que este par
> sea citable el 9-sep.

## 3. Contrato y frontera con la API

La página **no habla HTTP**. Todo pasa por `src/frontend/prediccion_client.py`, que expone
un `Prediccion` estable y traduce los errores de transporte a tres situaciones que la
interfaz presenta distinto:

| Situación | Qué ve el usuario |
|---|---|
| CCT sin predicción publicada (404) | Aviso, no error: *"solo se publican las escuelas cuyo ciclo tiene features completas"* |
| Gold inalcanzable (503, US-416) | Error de disponibilidad, con invitación a reintentar |
| Respuesta fuera de contrato | Error explícito — antes que pintar una recomendación huérfana |

El verbo HTTP es un **seam inyectable**, así que las pruebas ejercitan el cliente completo
sin red ni API levantada (mismo patrón que `agente_client.py`).

### 3.1 Lectura pública

`/api/v1/predicciones/{cct}` responde **sin token** mientras `AUTH_LECTURA_PUBLICA=true`. La
página lo aprovecha: se puede consultar una predicción sin iniciar sesión, y se dice en
pantalla. Si C5 pone esa bandera en `false`, el cliente ya acepta un `access_token` y la
página lo pasa desde la sesión — no hay cambio de código pendiente.

## 4. ML-03: el hueco declarado, no escondido

**La historia pide "los 3 modelos". Se entregan 2, y el tercero se declara.**

`gold.predicciones` **no tiene columna `cluster`**: US-321 (clustering, Estefany Hernández,
Célula 3) sigue en curso, y el contrato de la API lo documenta explícitamente —
`schemas.py::PrediccionOut` marca `cluster: StrictInt | None = None` con la nota de que al
aterrizar ML-03 vuelve a obligatorio.

Verificado el 2026-09-05: `cluster` viene `null` **en local y en producción**.

La página muestra un aviso `SIN_DATO` que dice qué falta y por qué, con la historia que lo
cierra. **No se inventa un segmento ni se deja el espacio en blanco**, que es la regla del
proyecto y el modo de falla que ya costó BUG-017 y BUG-031: un número creíble que significa
otra cosa.

> Cuando US-321 publique, **no hay que tocar esta página**: el cliente ya propaga el valor y
> hay una prueba que lo verifica (`test_cuando_ml03_aterrice_el_cluster_se_respeta`).

## 5. Decisiones de presentación

- **El umbral se explica, no solo se aplica.** La tarjeta de ML-01 dice qué significa 0.60
  en términos de negocio. Un KPI con un umbral sin explicar invita a la pregunta *"¿y por
  qué ese número?"* justo en la demo.
- **Los drivers se muestran con nombre legible** (`D1 · Pobreza y rezago social`), no solo
  con su id. El mapeo vive en la página porque es presentación; el id canónico viaja en la
  respuesta.
- **Se ofrecen dos CCT de ejemplo con driver distinto.** Sin ellos, el panel exige conocer
  una clave de memoria; con ellos, el diferenciador se demuestra en dos clics.

## 6. Alcance entregado y qué queda fuera

| Entregado | Pendiente |
|---|---|
| Formulario de CCT → inferencia real | Formulario de **parámetros libres** (simular una escuela hipotética): no está en la API, requiere un endpoint de inferencia sobre features arbitrarias |
| ML-01 y ML-02 con datos reales | ML-03, bloqueado por **US-321** |
| Verificado contra local y producción, **reportados por separado** (§7) | Verificación visual en el despliegue público: FARO Web aún no está desplegado (coordinación de C5) |

**Alcance ratificado por el PM en DEC-015** (2026-09-05, Edgar Coronel): la historia enuncia
tres modelos y cierra con dos servidos y el tercero declarado. Edgar verificó el argumento
antes de ratificarlo —`schemas.py` declara `cluster: StrictInt | None` nombrando US-321,
`repositorio_modelos.py` lo fija en `None`, y producción devuelve `"cluster": null`— y dejó
asentado en la misma decisión que **el par de §2.1 no es citable en la demo** mientras
BUG-048 siga abierto.

## 7. Cómo se probó

- `tests/test_prediccion_client.py` — 16 casos sobre el cliente, sin red.
- `tests/test_frontend_panel_ml_streamlit.py` — 6 casos sobre la página con `AppTest`.

Cada guarda se validó **reintroduciendo su defecto**: convertir el `cluster` nulo en `0`,
mover el umbral a 0.50, tratar el 404 como error genérico, que la página hable `httpx`
directo, y borrar el aviso de `SIN_DATO`. Las cinco fallan cuando deben.

Verificación contra la API real, no solo con dobles. **Los dos ambientes se reportan por
separado a propósito**: juntarlos en un solo renglón ya indujo una lectura equivocada.

| Ambiente | Gold que sirve | Medición |
|---|---|---|
| Local | reconstruido tras BUG-045 | `15DJN0049A` → 0.7423 / D1 · `09DSN0042A` → 0.6692 / D2 |
| Producción | anterior a BUG-045 (**BUG-048 abierto**) | `09DBN0007I` → 0.1060 / D1 · `15DJN0049A` → **0.129 / D3** |

El mismo CCT da driver distinto en cada ambiente. No es discrepancia del código —`/version`
es correcto— sino del dato: es BUG-048. `cluster` viene `null` en **los dos**, que es lo que
sostiene el aviso de ML-03 (§4).

## 8. Trazabilidad

- **Implementa:** US-207 (REQ-002)
- **Consume:** US-412 / US-415 (contrato de inferencia, Célula 4) · DEC-006 (umbral)
- **Ratificado por:** DEC-015 (alcance de 2 de 3 modelos, con ML-03 declarado)
- **Bloqueado parcialmente por:** US-321 (ML-03, Célula 3)
- **Limitado en producción por:** BUG-048 (Gold viejo en Cloud SQL) — ver §2.1 y §7
- **Complementa:** [[vault/03_Architecture/Frontend_Architecture]] §5 (canónico de la capa web)
