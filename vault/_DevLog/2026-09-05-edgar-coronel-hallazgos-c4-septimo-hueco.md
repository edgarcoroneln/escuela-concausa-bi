---
project: "FARO"
date: "2026-09-05"
author_human: "Edgar Edmundo Coronel Navarrete"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "cierre de los hallazgos que C4 dejó al PM"
tags: [devlog, pm, ownership, secrets, rbac, dec-017, bug-053]
---

# DevLog — 2026-09-05 — Los tres hallazgos que C4 dejó en mi mesa

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/10_Risk_Governance/Decision_Log]] ·
[[vault/_Meta/Vault_Steward]]

## Qué se pidió

Christian Ruiz cerró su PR #240 dejándome tres cosas: un hueco de propiedad que impedía cumplir
`Secrets_Policy`, una decisión de producto sobre el RBAC de dos rutas, y una fila de matriz que su
PR no traía. Las tres se resuelven aquí.

## 1. El séptimo hueco de propiedad

`guia-ambiente-local/` en la raíz **no estaba en ningún alcance** —ni verde, ni amarillo, ni
comunes—. Dentro vive `configuracion.env`, versionado en git contra `Secrets_Policy`, reportado por
**Monserrat Miranda** el 4-sep y ratificado por **Christian Ruiz** el 5-sep.

El absurdo: **el gate reprobaba a quien intentara cumplir la política.** `.gitignore` ya trae `*.env`
desde el 3-sep —lo agregó Marina mencionando este mismo archivo—, pero ignorar no des-trackea; hace
falta `git rm --cached`, y nadie podía ejecutarlo sin que el gate lo rechazara por "fuera de alcance".

No se puede exigir que se cumpla una política y a la vez impedir que alguien la cumpla.

Revisado antes de tocarlo, como hicieron los dos que lo reportaron: **7 líneas, puertos de Airflow y
MLflow, cero credenciales**. Riesgo bajo, incumplimiento real. Carpeta a `comunes` y archivo
des-trackeado: sigue en disco y ahora sí lo cubre `.gitignore`.

Es la **séptima** aparición del mismo patrón en cuatro días. Ya está anotado en
[[vault/_Meta/Vault_Steward]] como el hallazgo recurrente número uno, y el punto 2 de la lista existe
exactamente por esto.

## 2. `DEC-017` — el RBAC de predicciones se queda como está

Christian encontró que `API_Specification` prometía que `/predicciones/batch` y `/explicacion` eran
**solo analista con 403**, y que nunca lo fueron: el router se monta con `require_lectura`
(`v1/__init__.py:25`). Alineó la documentación al código en vez del código a la documentación, y me
dejó la decisión de si debía ser al revés.

**Verifiqué su argumento y el que dio no se sostiene.** Dijo que restringir rompería a quien las
llame como ciudadano desde C2/C3; busqué en todo el repo y **ningún consumidor fuera de la propia API
llama esas dos rutas** — los únicos hits son `explicar_driver` y su prueba. Restringirlas hoy no
rompería a nadie.

**La decisión igual es no hacerlo**, por tres razones que sí se sostienen:

1. **El RBAC ya está demostrado.** US-403 validó en vivo analista→200 y ciudadano→403 con cuentas
   reales. El punto de rúbrica no depende de estas dos rutas.
2. **`/explicacion` sirve mock** (§3). Poner un rol delante de un mock no demuestra nada.
3. **FARO Web no está desplegado**, y el panel de ML y el chat son exactamente las superficies que
   las consumirían. El riesgo no es hoy: es el lunes.

Cambiar enforcement a un día del freeze por un punto que ya está asegurado es riesgo sin retorno.
Si algún día se restringen, va en `v1/__init__.py` con su propia dependencia, post-demo.

## 3. `BUG-053` — `/explicacion` no devuelve SHAP

Christian lo diagnosticó al ir a conectarlo, y lo verifiqué de forma independiente:
`entrenar_ml02.py:320::explicar_driver` calcula SHAP con la forma exacta de `ExplicacionSHAPOut`,
pero **el único hit de `grep` en todo `src/` es su propia definición** — no lo llama nadie. Y
`publicar_gold.py` sólo escribe `gold.predicciones` y `gold.recomendaciones`.

No es un pendiente de C4: **no existe fuente que leer.** El orden real es C3 persiste en Gold → C4
lee → prueba, y el primer paso no es de su célula. Las 8 pruebas de contrato ya están escritas, así
que cuando exista la fuente el cambio es del cuerpo del endpoint, no de la forma.

**Lo que importa para el 9:** el driver dominante y la recomendación de `/predicciones/{cct}` **sí
son reales**, salen de ML-02. Lo que es mock es el desglose de contribuciones. El diferenciador del
proyecto se sostiene; el detalle fino no, y eso lo decimos nosotros antes de que lo pregunten.

## 4. La fila de matriz que faltaba

El PR #240 no tocaba `Traceability_Matrix.md` aunque la plantilla lo pide y su DevLog la enlaza.
Sospecho que la evitó para no disparar mi revisión de regla 7, lo cual es defendible — pero deja la
ratificación de US-416 sin traza. La agrego yo, que es mi crítico.

De paso queda registrado lo mejor de su PR, que verifiqué revirtiendo el parche: la ventana de
`KeyError` en el cache es real y sus dos pruebas de regresión fallan con `KeyError` desde
`cachetools/__init__.py:105` cuando se vuelve al patrón `in` + `[]`.

## Verificado

`vault_lint.py` limpio · `ruff` limpio · `pytest tests/ -q` en verde · YAML de `ownership.yml`
válido · `git check-ignore` confirma que `.gitignore:7 *.env` ya cubre el archivo des-trackeado ·
consumidores de `/batch` y `/explicacion` buscados con `grep` en `src/`, `superset/`, `dags/`.

## IDs tocados

`DEC-017`, `BUG-053`, `US-416`, `US-412`, `US-422`, `US-403`, `US-302`, `REQ-003`, `REQ-004`,
`REQ-007`, `SEC-007`

## Pendiente ajeno, anotado y no corregido

Christian deja como **el mayor riesgo abierto de su célula** el login e2e real, y depende de Luis
Téllez: dar de alta los usuarios de prueba, dejar `ANALISTA_EMAILS` sólo con mi correo para que él
quede de ciudadano y podamos demostrar el **403 en vivo**, y buscar *"No se pudo preparar el almacén
de códigos"* en los logs (`SEC-007`). Se lo paso hoy.

## Próximos pasos

- Pasar a Luis los tres pendientes de C4 junto con la lista de correos del SSO de Superset.
- `US-006`, el ensayo de la demo, sigue sin arrancar y es mío.
