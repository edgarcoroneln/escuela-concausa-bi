---
id: SPRINT-ESTEFANY-LUCERO-HERNANDE
title: "Plan de Sprints — Estefany Lucero Hernández Loredo"
owner: "Estefany Lucero Hernández Loredo"
status: approved
version: "1.0"
traces_up: ["vault/01_Product/PRD", "vault/02_Requirements/User_Stories"]
traces_down: ["US-321", "US-322", "US-325"]
last_reviewed: "2026-07-31"
tags: [sprint, plan, celula-3, nivel-bajo]
---

# FARO · Plan de trabajo individual
## Estefany Lucero Hernández Loredo

> **Proyecto:** FARO — Escuela como Sensor Social
> **Célula:** Celula 3 — Machine Learning & AI Agent · **Peso en rúbrica:** 1.5 + 0.5 pts
> **Rol:** Analista ML jr · Clustering y features · **Nivel asignado:** Bajo
> **Tech Lead de tu célula:** Andrés González Habib
> **Demo en vivo:** miércoles 9 de septiembre de 2026

---

## 1. Tu misión en una frase

Tienes historias **acotadas y bien definidas**, pensadas para que aprendas haciendo. Cada una tiene un resultado claro y verificable. **Pedir ayuda temprano no es debilidad: es el comportamiento correcto.** Si a las 2 horas sigues atorado, escribe en el canal de tu célula.

### Misión actualizada al 4-sep-2026

Llevar `US-322` y `US-325` de evidencia sintética a evidencia agregada sobre Gold real, e iterar
`US-321` con un protocolo temporal honesto hasta superar el umbral de Silhouette o presentar a
Andrés y Edgar una decisión explícita sobre el uso de ML-03. El PR #197 de Diana ya resolvió la
reproducción de Bronze para DS-01/DS-02; todavía se debe ejecutar y verificar Bronze → Silver → Gold.

La propuesta ejecutable y el prompt maestro canónico están en
[[vault/15_ML_Models/Plan_Cierre_Estefany_US321_US322_US325]].

---

## 2. Mapa de dependencias

| | |
|---|---|
| **Recibes de (inputs)** | `gold.features_escuela` de la **Célula 1** · MLflow desplegado por la **Célula 5** |
| **Entregas a (outputs)** | **Célula 4** (modelos para inferencia) · **Célula 2** (tabla de predicciones) |
| **Quién revisa tu código** | Edgar Edmundo Coronel Navarrete (PM) — compuerta única (DEC-003). Andrés González Habib (Tech Lead) revisa como apoyo, no bloquea |
| **Formato de entrega** | Rama fija `dev/estefany-hernandez` (sincronizada con `main`) → PR con plantilla y título estándar → 1 aprobación (PM) → merge a `main` |

> **Regla de desbloqueo:** si un input tuyo no llega a tiempo, **no te quedes esperando**. Trabaja contra
> datos mock o fixtures, avísalo en el standup y registra el bloqueo. Un bloqueo silencioso de 3 días
> con esta ventana de 6 semanas es fatal.

---

## 3. Tus historias de usuario

### `US-321` · Entrenar el Modelo 3 - Clustering de escuelas

| | |
|---|---|
| **Sprint** | S4 — Lun 24 - Dom 30 ago |
| **Objetivo** | KMeans sobre el perfil de escuelas; validar con Silhouette y perfilar cada grupo con lenguaje de negocio. |
| **Entregable** | Código en su carpeta + documento en el vault con frontmatter + fila en la matriz |
| **Cómo se entrega** | Rama fija `dev/estefany-hernandez` (sincronizada con `main`) → PR con plantilla → 1 aprobación del PM → merge a `main` |

### `US-322` · Analisis exploratorio y seleccion de variables

| | |
|---|---|
| **Sprint** | S4 — Lun 24 - Dom 30 ago |
| **Objetivo** | EDA sobre features, correlaciones, y deteccion de fuga de informacion y de sesgo por cobertura. |
| **Entregable** | Código en su carpeta + documento en el vault con frontmatter + fila en la matriz |
| **Cómo se entrega** | Rama fija `dev/estefany-hernandez` (sincronizada con `main`) → PR con plantilla → 1 aprobación del PM → merge a `main` |

### `US-325` · Analizar el sesgo por cobertura parcial en las features

| | |
|---|---|
| **Sprint** | S4 — Lun 24 - Dom 30 ago |
| **Objetivo** | Medir cuantas escuelas tienen SIN_DATO por driver, verificar si esa ausencia se concentra geograficamente y documentar el riesgo de que el modelo aprenda un sesgo territorial. Conecta con `indice_completitud_drivers` y el tablero DB-07. |
| **Entregable** | Código en su carpeta + documento en el vault con frontmatter + fila en la matriz |
| **Cómo se entrega** | Rama fija `dev/estefany-hernandez` (sincronizada con `main`) → PR con plantilla → 1 aprobación del PM → merge a `main` |



---

## 4. Ambiente local — hazlo ANTES del primer standup

Todos trabajamos con el mismo ambiente para evitar el clásico "en mi máquina sí corre".

### 4.1 Requisitos previos
- **Python 3.11** (`python3 --version`)
- **Docker Desktop** corriendo
- **Git** configurado con tu nombre real y el correo **verificado en tu cuenta de GitHub** (no necesariamente el institucional); es lo que atribuye tus commits a tu perfil y los cuenta como evidencia de participación. Si prefieres no exponerlo, usa tu `@users.noreply.github.com` (Settings → Emails).
- **VS Code** (o tu editor) con la extensión de Python
- **macOS + xgboost:** `brew install libomp` (OpenMP; sin esto `import xgboost` truena con `libomp.dylib`)

### 4.2 Clonar y crear tu ambiente virtual

```bash
# 1. Clona el repositorio
git clone https://github.com/edgarcoroneln/escuela-concausa-bi.git
cd escuela-concausa-bi

# 2. Crea tu ambiente virtual (NO se sube al repo, está en .gitignore)
python3 -m venv .venv

# 3. Actívalo
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows PowerShell

# 4. Verifica que estás dentro del venv (debe aparecer (.venv) en tu prompt)
which python

# 5. Actualiza pip e instala dependencias base
pip install --upgrade pip
pip install -r requirements.txt

# 6. Dependencias específicas de tu célula
pip install scikit-learn xgboost mlflow shap pandas chromadb sentence-transformers

# 7. Congela lo que instalaste (si agregaste algo nuevo)
pip freeze > requirements/celula-3.txt
```

### 4.3 Variables de entorno

```bash
cp .env.example .env
```

Abre `.env` y llena los valores. **NUNCA subas el `.env` al repositorio** — está en `.gitignore` y
las reglas de `vault/07_Security/Secrets_Policy.md` lo prohíben explícitamente.

### 4.4 Levantar los servicios locales

```bash
docker compose up -d          # levanta Postgres, Airflow, Superset, MLflow
docker compose ps             # verifica que todos estén "healthy"
docker compose logs -f <servicio>   # si algo falla
```

### 4.5 Verificación final (tu ambiente está listo si esto pasa)

```bash
python -c "import sys; print(sys.version)"     # 3.11.x
docker compose ps                               # todos Up
pytest tests/ -q                                # las pruebas base pasan
python vault/_Meta/scripts/vault_lint.py .            # ✅ Vault limpio
```

Si algo falla, escribe en el canal de tu célula **antes** del standup. No pierdas un día atorado en
setup: es el error más caro de la semana 1.

---

## 5. Prompts sugeridos — funcionan en cualquier LLM

> Puedes usar **Claude Code, ChatGPT, Gemini, Copilot o el que prefieras**. Los prompts están escritos para ser agnósticos.

> Adapta los `<PLACEHOLDERS>`. **Todo lo que genere la IA lo revisas tú antes de commitear, y cada sesión genera una entrada de DevLog** (regla 6 del vault).

> **Prompt recomendado para las misiones pendientes:** usa el prompt maestro de
> [[vault/15_ML_Models/Plan_Cierre_Estefany_US321_US322_US325#3. Prompt maestro potenciado]].
> Contiene el corte post-PR #197, los criterios reales de cierre, el límite de Silhouette y las
> condiciones de paro por alcance. Los prompts siguientes quedan como auxiliares para consultas
> pequeñas; no sustituyen el prompt maestro.

**Contexto que debes pegar al inicio de tu sesión, sea cual sea el LLM:**

```
Estoy trabajando en FARO, una plataforma de BI end-to-end sobre datos abiertos de México
(escuelas + pobreza + inseguridad + infraestructura + agua + aire). Arquitectura medallon
(bronze/silver/gold en Postgres), Airflow, dbt, Great Expectations, MLflow, FastAPI,
Superset, Docker y GCP. Python 3.11. Alcance: CDMX, Edomex, Nuevo Leon y Jalisco.
La llave que une todo es el CCT (centro de trabajo) y la clave INEGI de municipio a 5 digitos.
Responde en espanol, con codigo comentado y explicando tus decisiones.
```

**Estrategia de modelado**
```
Actúa como científico de datos senior. Tengo una tabla de features a nivel escuela con estas columnas: <COLUMNAS>. Quiero predecir <OBJETIVO>. Propón: (1) el algoritmo adecuado y por qué, (2) la estrategia de partición temporal para evitar fuga de información, (3) las métricas de evaluación correctas y (4) los riesgos de sesgo. Sé crítico, no complaciente.
```

**Entrenamiento + MLflow**
```
Escribe el script de entrenamiento para <MODELO> usando scikit-learn/XGBoost. Debe: registrar parámetros, métricas y el artefacto en MLflow; hacer validación temporal (no aleatoria); y guardar el reporte de métricas. Incluye SHAP para explicabilidad.
```

**Agente Text-to-SQL**
```
Ayúdame a construir un agente que traduzca preguntas en lenguaje natural a SQL sobre este esquema: <ESQUEMA>. Requisitos: debe rechazar preguntas fuera del alcance, nunca ejecutar DELETE/UPDATE/DROP, limitar resultados a 1000 filas, y devolver la consulta generada junto con la respuesta para que sea auditable.
```

**Si te atoras (úsalo sin pena, es parte del método)**
```
Explícame como si fuera mi primera semana: qué hace este código línea por línea, qué error estoy viendo y cuál es la causa raíz. No me des solo la solución: quiero entender el porqué para no repetir el error.
```


---

## 6. Reglas del repositorio — obligatorias, sin excepción

> Estas reglas vienen de `vault/_Meta/Vault_Rules.md` y `vault/05_Engineering/Branching_Strategy.md`.
> Romperlas cuesta puntos de la rúbrica (0.5 pts de trabajo en equipo se evalúan por commits repartidos).

### 6.1 PROHIBIDO hacer commits directos a `main`
La rama `main` está protegida y es la única fuente de verdad. Todo cambio entra por Pull Request
revisado. Si intentas `git push origin main` te será rechazado.

### 6.2 Tu rama es una sola, y es permanente

Trabajas siempre en **`dev/estefany-hernandez`**. No creas una rama por historia, ni por sprint, ni por tema: esa
rama es tuya durante todo el proyecto, y **no se borra al mergear**. La rama dice quién eres; el
commit dice qué hiciste.

### 6.3 Flujo correcto, paso a paso

```bash
# 1. Sincroniza. SIEMPRE, antes de escribir una sola línea.
git checkout dev/estefany-hernandez
git fetch origin
git merge origin/main
#   Nunca 'rebase' y nunca '--force': tu rama es permanente y su historia ya fue revisada.

# 2. Trabaja y haz commits pequeños con Conventional Commits
git add <archivos-especificos>        # NUNCA uses git add . a ciegas
git commit -m "feat(bronze): extractor de Formato 911 (US-122)"
#   Formato: <tipo>(<scope>): <descripción> (ID-de-la-historia)

# 3. Vuelve a sincronizar JUSTO ANTES de abrir el PR
git fetch origin && git merge origin/main
#   `main` se mueve varias veces al día. El CI reprueba el PR cuya rama esté atrasada.

# 4. Sube
git push origin dev/estefany-hernandez

# 5. Abre el PR en GitHub con la plantilla (se carga sola) y este título:
#    [Estefany Hernandez] - Descripción concisa (US-###) - [sync|CI|DoF|DevLog]

# 6. Tras el merge: NO borres la rama. Vuelve al paso 1.
```

### 6.4 Reglas del Pull Request
- Usa **`.github/PULL_REQUEST_TEMPLATE.md`** — se llena solo al abrir el PR. Complétalo TODO.
- El **título** sigue el estándar de arriba. El CI valida el formato y que la firma sea la tuya.
- El PR debe referenciar el **ID de la historia** (`US-###`) y el requisito (`REQ-###`).
- **No puedes aprobar tu propio PR.** Requiere **1 aprobación del PM** (compuerta única, DEC-003).
- Solicita a **Andrés González Habib** (Tech Lead) como revisor de apoyo si el cambio toca su área; su revisión no bloquea el merge.
- Los checks de CI deben estar **verdes**: plantilla, sincronía con `main`, propiedad de
  archivos, `vault_lint.py`, lint y pruebas.
- Si tu cambio toca seguridad, esquema de datos o CI/CD, requiere aprobación humana explícita del
  dueño del área (regla 7 de `Vault_Rules.md`).

### 6.5 DevLog — obligatorio en cada sesión con IA
Toda sesión con Claude Code, Copilot o cualquier LLM **genera una entrada de DevLog antes del push**
(regla 6 de `Vault_Rules.md`). Usa `vault/_Templates/DevLog_template.md` y guárdala en `vault/_DevLog/` como
`YYYY-MM-DD-estefany-hernandez-descripcion.md`. Debe registrar: qué pediste, qué generó la IA, qué revisaste
tú y qué IDs tocaste.

### 6.6 Gobernanza de IA y alcance
- Tu alcance vive en dos lugares que dicen lo mismo: `vault/_Meta/ownership.yml` (lo que lee el CI) y
  tu `vault/09_AI_Governance/Agent_Contexts/estefany-hernandez-agent-context.md` (la versión legible).
  **No trabajes fuera de él.** El CI reprueba el PR que toca archivos ajenos.
- Para cambiar algo de otra persona, **pídeselo a su dueño** y que lo lleve en su rama.
- **Todo código generado por IA se revisa línea por línea antes de commitear.** Eres responsable de lo
  que subes, lo haya escrito la IA o tú.
- Prohibido pegar datos reales, credenciales o `.env` en un prompt de IA.
- Registra los prompts que funcionaron bien en `vault/09_AI_Governance/Prompt_Library.md` para que el equipo
  los reutilice.

### 6.7 Definition of Filed (antes de decir "ya quedó")
Nada está terminado hasta que: tiene **ID**, está en su **carpeta**, tiene **frontmatter** con `owner`
y `status`, enlaza a su origen (`traces_up`) y a lo que lo resuelve (`traces_down`), aparece en el
**`_index.md`** de su carpeta, y su fila en la **Traceability_Matrix** está actualizada.

---

## 7. Checklist de entrega (por cada historia que cierres)

Marca todo antes de pedir revisión. Si algo queda sin marcar, la historia **no está Done**.

- [ ] El código corre en mi ambiente local sin errores
- [ ] Escribí/actualicé las pruebas y `pytest` pasa en verde
- [ ] Corrí `python vault/_Meta/scripts/vault_lint.py .` → ✅ Vault limpio
- [ ] Documenté el artefacto en su carpeta del vault con frontmatter completo
- [ ] Agregué el documento al `_index.md` de su carpeta
- [ ] Actualicé mi fila en `vault/02_Requirements/Traceability_Matrix.md`
- [ ] Escribí mi entrada de DevLog si usé IA
- [ ] Actualicé el `README.md` si mi cambio afecta cómo se instala o se usa el proyecto
- [ ] Mis commits siguen Conventional Commits e incluyen el ID de la historia
- [ ] Verifiqué la autoría: `git log -1 --format='%an <%ae>'` coincide con mi cuenta de GitHub
- [ ] Abrí el PR con la plantilla completa y el título estándar
- [ ] Sincronicé mi rama con `main` antes de abrir el PR
- [ ] Los checks de CI están verdes
- [ ] NO subí datos reales, `.env`, llaves ni archivos pesados

---

## 8. Datos de prueba — mantén limpio el repositorio

El repositorio **no debe contener datos reales pesados**. Para que CI y las pruebas corran sin
descargar gigabytes:

- Los datos reales viven en `data/raw/` que está **en `.gitignore`** — nunca se suben.
- Las pruebas usan **fixtures**: muestras pequeñas y deterministas en `tests/fixtures/`.
- Si necesitas un dataset de prueba nuevo, genera una muestra de ≤500 filas, **anonimizada y sin datos
  personales**, y documéntala en `vault/06_Quality_Testing/`.
- Regla de oro para la puesta en producción: **si un archivo pesa más de 5 MB, no va al repositorio.**
  Va a Cloud Storage y en el repo queda solo la referencia.

---

## 9. Seguimiento de tu avance

Actualiza esta tabla **antes de cada standup**. El PM la revisa para el tablero de control.

| ID | Historia | Estado | % | Bloqueado por | Fecha compromiso |
|---|---|---|---|---|---|
| `US-321` | Entrenar el Modelo 3 - Clustering de escue | 🔵 En revisión | 70% | Fallback de imputación y ejecución real con ≥4 ciclos Bronze | Dom 30 ago |
| `US-322` | Analisis exploratorio y seleccion de varia | 🔵 En revisión | 90% | Validación CI y aprobación de Andrés/Edgar | Dom 30 ago |
| `US-325` | Sesgo por cobertura parcial en features | 🔵 En revisión | 85% | Merge de `cve_mun` de C1 y ejecución sobre Gold real | Dom 30 ago |

**Estados válidos:** ⬜ Por iniciar · 🟡 En curso · 🔵 En revisión (PR abierto) · ✅ Terminado · 🔴 Bloqueado

### Si tu historia queda a medias
No pasa nada — lo grave es no decirlo. Si al cierre del sprint tu historia va parcial:
1. Marca el % real, no el que te gustaría
2. Abre el PR igual con lo que sí funciona (mejor 3 PRs chicos que 1 gigante al final)
3. Anota en la tabla **qué falta exactamente** y por qué
4. Dilo en el standup

## 10. Calendario y standups

| Sprint | Fechas | Foco |
|---|---|---|
| **S1** | Lun 3 - Dom 9 ago | Cimientos, fuentes y despliegue temprano |
| **S2** | Lun 10 - Dom 16 ago | Ingesta continua y capa Bronze |
| **S3** | Lun 17 - Dom 23 ago | Silver, Gold, Great Expectations y cubos |
| **S4** | Lun 24 - Dom 30 ago | Modelos ML, FastAPI, Auth y Dashboards |
| **S5** | Lun 31 ago - Dom 6 sep | Agente RAG, integracion y CODE FREEZE |
| **S6** | Lun 7 - Mar 8 sep | Pruebas finales, seguridad, GCP y ensayo |

- **Semanas 1-3 (semanal, jueves):** 6, 13 y 20 de agosto - 19:00 hrs, 45 min.
- **Semanas 4-6 (3 por semana, L-Mi-V):** 24, 26, 28 ago · 31 ago, 2, 4 sep · 7 y 8 sep - 19:00 hrs, 30 min.
- **Formato:** cada celula responde 3 preguntas (que cerre, que sigue, que me bloquea). El PO actualiza la
  Traceability_Matrix al cierre de cada standup.

> **CODE FREEZE: domingo 6 de septiembre.** A partir de ahí no entran funcionalidades nuevas, solo
> correcciones. **Demo en vivo: miércoles 9 de septiembre de 2026.**

---

## 11. Si algo sale mal

| Situación | Qué hacer |
|---|---|
| No logro levantar el ambiente | Escribe en el canal de tu célula el mismo día. No pierdas 2 días. |
| Mi input no llegó | Trabaja con fixtures/mock, registra el bloqueo y avísalo en el standup. |
| Rompí algo en `main` | Avisa de inmediato al Tech Lead de Cloud/DevOps; hay runbook de rollback. |
| Mi PR lleva 2 días sin revisión | Etiqueta a tu Tech Lead; si no responde, escala al PO. |
| No entiendo mi historia | Pregunta ANTES de codificar. Una hora de duda cuesta menos que 3 días de trabajo equivocado. |

---

*Documento generado para el proyecto FARO · Maestría MTIIA · Universidad Anáhuac · Dr. José Gustavo Fuentes*
