---
id: DOC-PLAN-CIERRE-ESTEFANY-US321-US322-US325
title: "Propuesta de cierre — US-321, US-322 y US-325"
owner: "Estefany Lucero Hernández Loredo"
status: draft
traces_up: ["US-321", "US-322", "US-325", "REQ-003"]
traces_down: ["vault/15_ML_Models/ML03_Entrenamiento_US321", "vault/15_ML_Models/EDA_Features_US322", "vault/15_ML_Models/Cobertura_Parcial_US325"]
tags: [ml, ml-03, clustering, eda, cobertura, plan-cierre]
---

# Propuesta de cierre — US-321, US-322 y US-325

> Responsable: Estefany Lucero Hernández Loredo · Rama: `dev/estefany-hernandez`
> Corte de diagnóstico: 4-sep-2026 · Revisión obligatoria: Edgar Coronel (PM)
> Apoyo técnico recomendado: Andrés González Habib (Tech Lead C3)

## 1. Resultado de la revisión

| Historia | Estado verificable | Qué ya existe | Qué falta para cerrarla |
|---|---|---|---|
| `US-322` | `in_review` | EDA reproducible y evidencia agregada sobre el dump Gold final del 5-sep; llaves y target excluidos | Aprobación de Edgar para cerrar la historia, independiente de ML-03 |
| `US-325` | `in_review` | Auditoría real por driver, entidad y municipio; D5/D6 declarados `SIN_DATO` | Aprobación documental de Edgar sin inventar un umbral de sesgo |
| `US-321` | `in_progress` | Pipeline `StandardScaler` + KMeans y vector operativo ratificado D1–D4 + completitud | Ejecutar la corrida temporal real, seleccionar `k`, reportar Silhouette y registrar la versión con `run_id` real |

La disponibilidad de Bronze dejó de ser el bloqueo: el PR #197, mergeado el 3-sep-2026, incorporó
`python -m src.ingesta.reproducir_bronze_real` para DS-01/DS-02 y las suites de Great Expectations.
El comando carga Bronze y termina indicando `dbt run && dbt test`; por tanto, **no equivale por sí
solo a tener Gold actualizado**. Antes de analizar o entrenar se debe reconstruir y verificar
`gold.features_escuela`.

## 2. Misión propuesta

Convertir las tres historias de una entrega validada con fixtures en una evidencia reproducible sobre
Gold real, sin ampliar el alcance de Estefany ni declarar éxito estadístico donde no lo hay.

### Fase A — preflight y linaje

1. Sincronizar `dev/estefany-hernandez` con `origin/main` mediante merge.
2. Verificar que no se expondrán `.env`, credenciales ni extractos de datos reales.
3. Levantar los servicios requeridos y ejecutar el camino documentado:

```bash
python -m src.ingesta.reproducir_bronze_real
cd dbt
dbt run
dbt test
```

4. Consultar únicamente metadatos agregados de `gold.features_escuela`: número de filas, ciclos,
   escuelas, duplicados por `cct × id_ciclo` y cobertura por driver.
5. Si Bronze carga pero Gold no materializa, detener la misión y registrar el error exacto para
   Diana Alvarez; no modificar `src/ingesta/**`, `dbt/**` ni `dags/**` desde la rama de Estefany.

### Fase B — cerrar evidencia de `US-322` y `US-325`

1. Incorporar un punto de entrada reproducible que lea `gold.features_escuela` sin exportar datos
   individuales al repositorio.
2. Generar reportes agregados de EDA, correlaciones, cobertura y dispersión municipal.
3. Confirmar que `cct`, `cve_mun`, `id_ciclo` y `target_variacion_matricula` no entren al vector de
   clustering.
4. Tratar `SIN_DATO` como ausencia explícita. D5 puede permanecer totalmente ausente mientras no
   exista el crosswalk aprobado; eso es un hallazgo, no un cero ni una razón para inventar datos.
5. Actualizar `EDA_Features_US322.md` y `Cobertura_Parcial_US325.md` con cifras agregadas, fecha,
   commit y comandos de reproducción. Proponer `status: done` sólo si toda la evidencia existe.

### Fase C — iterar `US-321` sin sobreajuste narrativo

1. Reproducir el baseline vigente y conservar el resultado de 0.1086 como referencia histórica.
2. Medir filas totales, entrenadas y excluidas por la política `casos_completos` en cada ciclo y
   entidad. Si la exclusión concentra territorios, no interpretar los clusters como nacionales.
3. Comparar `k=2..6` con walk-forward. Ajustar `StandardScaler` y cualquier transformación sólo con
   la ventana de entrenamiento.
4. Probar como máximo alternativas justificadas y comparables, por ejemplo:
   - retirar features sin varianza o con cobertura inutilizable;
   - eliminar una de dos variables altamente redundantes;
   - PCA ajustado dentro de cada ventana, conservando varianza explicada auditable.
5. No iterar hasta “fabricar” un valor. Reportar todas las variantes probadas bajo el mismo protocolo.
6. Si ninguna variante alcanza Silhouette ≥0.30, mantener `US-321` abierta y recomendar formalmente
   una de estas decisiones a Andrés y Edgar: aceptar el modelo como exploratorio con umbral revisado,
   cambiar el algoritmo o retirar ML-03 de uso operativo.
7. Registrar en MLflow sólo una corrida reproducible, con parámetros, features, política de ausencia,
   métrica temporal, filas excluidas y commit. Registrar no significa promover a producción.

## 3. Prompt maestro potenciado

Usar este prompt después de iniciar una sesión desde la raíz del repositorio:

```text
Actúa como ingeniero/a de ML senior y revisor crítico del proyecto FARO. Trabajas conmigo, Estefany
Lucero Hernández Loredo, exclusivamente en US-321, US-322 y US-325, sobre la rama permanente
dev/estefany-hernandez. Responde en español y no asumas que una tarea está cerrada porque exista código.

FUENTES DE VERDAD QUE DEBES LEER ANTES DE ACTUAR
1. AGENTS.md, CLAUDE.md y vault/_Meta/Vault_Rules.md.
2. vault/_Meta/ownership.yml y mi Agent Context.
3. Mi plan de sprint y este plan de cierre.
4. ML03_Entrenamiento_US321.md, EDA_Features_US322.md y Cobertura_Parcial_US325.md.
5. El código y las pruebas existentes antes de proponer cambios.

CONTEXTO ACTUAL VERIFICADO
- El PR #197 ya está mergeado: DS-01 histórico (6 ciclos) y DS-02 se reproducen con
  `python -m src.ingesta.reproducir_bronze_real`; incluye suites Great Expectations.
- Ese comando sólo carga Bronze. Debes verificar `dbt run`, `dbt test` y la existencia real de
  `gold.features_escuela` antes de analizar o entrenar.
- US-322 y US-325 tienen implementación sobre fixtures, pero requieren evidencia sobre Gold real.
- US-321 tiene pipeline KMeans temporal, pero el resultado conocido es Silhouette 0.1086 frente al
  umbral ≥0.30. No declares éxito si no se supera o si se cambia el protocolo para favorecerlo.
- D5 puede estar completamente SIN_DATO. Nunca lo reemplaces por cero.

RESTRICCIONES
- Puedes modificar: src/modelos/**, src/agente/**, vault/15_ML_Models/**, notebooks/**, pruebas
  acotadas, mi plan, mi Agent Context, mi DevLog y mi fila de trazabilidad.
- No modifiques src/ingesta/**, dbt/**, dags/**, src/api/**, superset/**, .github/** ni vault/_Meta/**.
  Si el bloqueo vive allí, entrega diagnóstico, archivo/línea, comando y mensaje para su dueño.
- Nunca uses partición aleatoria para validar. Toda transformación se ajusta sólo en train.
- No subas datos reales, credenciales, `.env` ni artefactos >5 MB. Conserva sólo evidencia agregada.
- No inventes comandos, tablas, columnas, métricas o aprobaciones. Inspecciona el repositorio primero.
- No cambies estados a done sin criterios, evidencia, pruebas y trazabilidad.

MISIÓN
A. Haz un inventario “hecho / desbloqueado / pendiente / bloqueado” de las tres historias.
B. Propón el cambio mínimo que permita ejecutar EDA, cobertura y ML-03 desde Gold real de forma
   reproducible. Antes de editar, muéstrame archivos a tocar y por qué están dentro de mi alcance.
C. Ejecuta pruebas enfocadas y reporta literalmente comandos, resultados y limitaciones del entorno.
D. Para US-322/325, produce sólo agregados auditables por ciclo, driver, entidad y municipio.
E. Para US-321, reproduce el baseline y compara k=2..6 con walk-forward. Puedes evaluar selección
   de features o PCA dentro del pipeline, pero debes conservar una tabla comparable de todas las
   variantes y evitar búsqueda oportunista del umbral.
F. Si Silhouette sigue <0.30, no lo ocultes: explica qué significa y redacta una decisión para Andrés
   González y Edgar Coronel con alternativas, riesgos y recomendación.
G. Registra MLflow sólo después de validar la corrida. No promociones el modelo.
H. Actualiza documentos, _index, mi fila de Traceability Matrix y DevLog cuando corresponda.
I. Antes del PR: merge origin/main, vault_lint, pruebas, revisión del diff y verificación de alcance.

FORMATO DE RESPUESTA EN CADA ETAPA
1. Evidencia observada.
2. Decisión y razón.
3. Archivos/comandos exactos.
4. Resultado medible.
5. Riesgo o bloqueo y dueño.
6. Siguiente acción.

CONDICIÓN DE PARO
Detente antes de alterar un contrato de Gold, una política de imputación no ratificada o un archivo
fuera de mi alcance. Formula una pregunta concreta al dueño correcto. No uses un workaround silencioso.
```

## 4. Evidencia mínima para solicitar cierre

- `US-322`: reporte real fechado, contrato validado, fugas excluidas y selección de variables motivada.
- `US-325`: cobertura real por driver/entidad/municipio, brechas cuantificadas y limitaciones de D5/D6.
- `US-321`: protocolo temporal reproducible, comparación de variantes, métrica honesta, perfiles de
  negocio y corrida MLflow identificable; si no alcanza el umbral, decisión humana documentada.
- Pruebas enfocadas, Ruff y `vault_lint.py` en verde.
- DevLog, `_index` y trazabilidad actualizados.

## 5. Revisiones solicitadas

- **Edgar Coronel:** aprobación de proceso, trazabilidad, criterio de cierre y cualquier cambio de
  umbral o estado.
- **Andrés González Habib:** política de ausencias, protocolo de comparación y recomendación sobre
  ML-03 si no alcanza 0.30.
- **Diana Alvarez:** sólo si la reconstrucción de Gold falla o el contrato real no coincide; el PR
  #197 ya resolvió la disponibilidad reproducible de Bronze y no debe reabrirse sin evidencia nueva.

## 6. Control de cumplimiento del Vault

| Regla | Evidencia en este cambio | Resultado |
|---|---|---|
| Identidad y rama fija | `stephi-coder` · `dev/estefany-hernandez` | Cumple |
| Sincronía antes del PR | `origin/main` incorporado mediante merge; la rama no está detrás de `main` | Cumple |
| Alcance de Estefany | `check_ownership.py`: 10 archivos, todos dentro del alcance | Cumple |
| Definition of Filed | ID, carpeta, frontmatter, trazas, `_index` y matriz presentes | Cumple |
| Sesión con IA | DevLog creado y listado en `vault/_DevLog/_index.md` | Cumple |
| Calidad automatizada | Vault lint, tablero PM, Ruff, Pytest, dbt parse y Quality Gate en verde | Cumple |
| Seguridad | Sin secretos, `.env`, datos reales ni archivos mayores de 5 MB | Cumple |
| Compuerta única | Revisión de Edgar solicitada por tocar la matriz; el PR no se autoaprueba | Pendiente del PM |

La aprobación del PM es una compuerta deliberadamente pendiente, no un incumplimiento del autor. No
se propone cambiar `US-321`, `US-322` o `US-325` a `done`: este PR entrega el plan verificable de
cierre y mantiene visibles la evidencia real aún necesaria y el Silhouette inferior al umbral.

## 7. Inicio de ejecución — 4-sep-2026

Se implementó `python -m src.modelos.ejecutar_cierre_ml03` como punto de entrada único para las
fases B y C. El comando lee `gold.features_escuela` desde `DATABASE_URL`, valida el contrato y emite
JSON exclusivamente agregado: metadatos del grano, EDA, correlaciones sin target, cobertura y
completitud por driver/entidad/municipio, dispersión municipal y resultado temporal de ML-03.

La primera corrida local del 4-sep no tuvo Docker ni Gold materializado. Ese hecho histórico fue
superado el 5-sep al restaurar el dump final en una base aislada; la evidencia resultante está en la
sección 8. El comando permanece cubierto por pruebas con fixture y MLflow es opt-in mediante
`--tracking-uri`; mientras el vector incluya D5/D6, `casos_completos` conserva el estado `bloqueado`
y no registra un modelo.

Comando pendiente en un ambiente conforme al runbook:

```bash
python -m src.modelos.ejecutar_cierre_ml03 --salida /tmp/evidencia-ml03.json
```

El JSON contiene agregados y puede adjuntarse a la revisión, pero no debe commitearse si pudiera
permitir reidentificación por grupos pequeños. Las historias conservan su estado hasta ejecutar y
revisar esa evidencia con Edgar y Andrés.

## 8. Continuación verificada — 5-sep-2026

### Resultado con dump Gold local — 2026-09-05

Se restauró `gold_bug048_final1_2026-09-05 1.sql` en la base aislada
`faro_gold_bug048_final1_review_20260905` y se ejecutó `src.modelos.ejecutar_cierre_ml03` sin exportar
observaciones individuales. El contrato entregó 136,046 filas, 46,547 escuelas, 3 ciclos,
`cve_mun` disponible y cero duplicados por `cct × id_ciclo`.

`final1` es la fuente canónica de evidencia (SHA-256
`07ECF29DEEE250732C38B252CA48794CCE413B5F295197E68804C337AC89D0BE`). `final2` sólo fue una
comparación independiente: produjo los mismos agregados y no se mezcló con el corte canónico.

La evidencia real ya está documentada para US-322 y US-325. La política de ausencia fue ratificada
técnicamente el 6-sep por Andrés: D5 está 100% en `SIN_DATO` y D6 98.70% sin dato, por lo que no
entran al vector ni se imputan; la regla `casos_completos` se conserva sólo para D1–D4 y
`indice_completitud_drivers`. Esa ratificación no cierra US-321: falta la corrida temporal real,
la selección de `k`, Silhouette y el registro MLflow con `run_id` real.

Se integró `origin/main` (25d76e3) mediante merge en la rama permanente. Docker Engine y Compose
responden; se creó `.env` local desde la plantilla con claves aleatorias, excluido de Git. El servicio
`db` arrancó y la conexión SQLAlchemy desde Windows funciona. La consulta de catálogo confirma que
`gold.features_escuela` todavía no existe en esta base. Instalar Docker no materializa Gold.

El PR #231 fue fusionado a `main` el 5-sep-2026. Esta evidencia posterior permanece local hasta que
se revise, se documente la decisión de ausencia y se publique en una nueva PR conforme al vault.

### Secuencia propuesta para completar la evidencia

1. Usar exclusivamente el dump autorizado `gold_bug048_final1_2026-09-05 1.sql` en una base aislada;
   conservar checksum, grano y agregados como evidencia. Los dumps nunca se versionan.
2. Aplicar el vector ya ratificado por Andrés para ML-03: **D1–D4 más
   `indice_completitud_drivers`**, excluyendo D5/D6 por ausencia estructural. D5/D6 se conservan en el
   reporte de cobertura y nunca se imputan, convierten a cero ni se interpretan como señal del cluster.
3. Aplicar la decisión aprobada en el contrato y reproducir `k=2..6` con walk-forward. Reportar filas
   elegibles/excluidas, perfiles, Silhouette y cualquier limitación territorial; no modificar umbrales
   sin una decisión explícita.
4. Registrar en MLflow sólo la corrida que pase la revisión técnica, con versión, `run_id`, vector,
   política de ausencia y métricas. Si la métrica no alcanza el umbral, se reporta; no se fabrica una
   mejora ni se impide registrar el experimento reproducible.
5. Publicar las asignaciones válidas en Gold por un productor específico de ML-03 y permitir que C4
   las exponga mediante la API. El contrato ejecutable y las compuertas están en la sección 9.
6. Actualizar fichas, matriz, índices y DevLog; solicitar aprobación de Edgar con CI verde. Mantener
   la rama permanente y no autoaprobar, promover modelos ni cambiar historias a `done` por anticipado.

### Ejecución desde PowerShell, cuando Gold esté disponible

El ejecutor no carga `.env` automáticamente. Este comando lo carga dentro del proceso sin imprimir
claves ni pasarlas como argumentos. Ejecutarlo desde la raíz del repositorio:

```powershell
& ./.venv/Scripts/python.exe -c "from dotenv import load_dotenv; load_dotenv('.env'); from src.modelos.ejecutar_cierre_ml03 import main; raise SystemExit(main())"
```

`DATABASE_URL` usa `127.0.0.1:5432` desde Windows; las conexiones de Compose conservan `db:5432`.
Para registrar después de revisar resultados, levantar MLflow y utilizar `--tracking-uri
http://127.0.0.1:5001`. MLflow todavía no se levantó ni se registró una corrida en esta verificación.

Validación local tras el merge: **973 passed, 8 skipped**, Ruff limpio y tablero PM válido.
Los skips y las pruebas con fixtures no sustituyen la evidencia sobre Gold real.

## 9. Plan de aterrizaje final — productor ML-03 y exposición C4

### Decisión técnica propuesta

El productor no debe escribir `cluster` dentro de `gold.predicciones`: esa tabla representa la salida
de ML-01 y exige `valor`, `indice_riesgo` y un grano que ML-03 no produce. Rellenar esos campos para
adaptar un cluster sería información inventada. La salida final debe vivir en una tabla Gold propia:
`gold.ml03_asignaciones`.

| Campo | Regla |
|---|---|
| `cct`, `id_ciclo` | llave primaria compuesta; mismo grano escuela × ciclo que las features |
| `cluster` | entero `>= 0`; sólo existe cuando la escuela fue elegible para la corrida aprobada |
| `modelo`, `mlflow_run_id`, `version_modelo` | trazabilidad obligatoria de la versión registrada |
| `politica_ausencia`, `vector_features`, `generado_at` | reproducibilidad de la asignación, sin copiar features individuales |

Una escuela excluida no recibe un cluster de relleno ni una fila artificial. La ausencia se expresa
en C4 como `cluster: null` y `ml03_estado: "SIN_DATO"`; una asignación válida se expone como
`ml03_estado: "OK"` con su `ml03_run_id`. Así se distingue cobertura insuficiente de un supuesto
valor `0`, que es un cluster legítimo.

### Entregables y responsables

| Fase | Entregable verificable | Responsable | Compuerta |
|---|---|---|---|
| A. Política | Decisión escrita: D1–D4 + completitud; D5/D6 fuera del vector operativo | Andrés (ratificada el 6-sep) | Aplicada en C3; Edgar conserva la compuerta de aprobación del PR |
| B. Productor C3 | `src/modelos/publicar_ml03.py`: valida contrato, recibe `ResultadoML03`, hace UPSERT por `cct,id_ciclo` y rechaza un `run_id` vacío | Estefany | Revisión técnica de Andrés y pruebas enfocadas |
| C. Esquema Gold | DDL/migración idempotente de `gold.ml03_asignaciones`, PK, `CHECK cluster >= 0` e índices | Diana (C1) + Edgar | Regla 7: revisión humana explícita por cambio de esquema |
| D. Registro | Corrida temporal real y versión MLflow con `run_id` recuperable | Estefany + C5 si el servicio MLflow lo requiere | E2E MLflow real, sin promover a producción automáticamente |
| E. API C4 | `LEFT JOIN` de la asignación por `cct,id_ciclo`; contrato con `cluster`, `ml03_estado` y `ml03_run_id` | Christian/Juan (C4) | Revisión C4 y pruebas de contrato/API |
| F. UI C2 | Mostrar cluster/perfil cuando `ml03_estado=OK` y `SIN_DATO` con explicación cuando no exista fila | Manuel/Marina (C2) | Prueba de integración visual |
| G. Cierre | Evidencia, matriz, DevLog, CI verde y aprobación del PM | Estefany + Edgar | PRs separados por propietario; Edgar es la aprobación final |

### Secuencia de ejecución y criterios de aceptación

1. C3 usa la política ya ratificada: excluir D5/D6 y no imputarlos. D5 carece de señal observable y
   D6 no tiene cobertura suficiente para inferirla responsablemente.
2. C3 ejecuta la validación temporal real y sólo genera asignaciones para filas
   elegibles. Debe probar: ausencia de D5/D6 en el vector, no fuga temporal, llave única, perfiles
   reproducibles e idempotencia del UPSERT.
3. C1 revisa y aprueba el nuevo objeto Gold antes de cualquier merge de esquema. El productor no
   ejecutará `DELETE`, `TRUNCATE` ni borrará versiones históricas.
4. Después de registrar en MLflow, el productor persiste las asignaciones con el `run_id` real. Un
   registro fallido revierte la publicación: no se expone una asignación sin trazabilidad.
5. C4 consulta Gold, nunca invoca KMeans ni MLflow por request. Para una escuela sin fila válida debe
   devolver `cluster: null`, `ml03_estado: "SIN_DATO"` y `ml03_run_id: null`; para una válida, los tres
   campos deben corresponder a la misma fila Gold.
6. Se ejecuta E2E `Gold → MLflow → Gold ML-03 → API`, incluyendo una escuela elegible, una excluida
   y una inexistente. C2 consume esos tres casos sin sustituir `null` por `0`.

### Impedimentos actuales y salida

| Impedimento | Efecto | Cómo se resuelve |
|---|---|---|
| D5 100% y D6 98.70% `SIN_DATO` | Contaminarían el clustering si se imputan o se usan como señal | Política ratificada: excluirlas del vector y mantenerlas como cobertura; no hay que esperar una nueva decisión técnica |
| Tabla Gold inexistente para ML-03 | No hay contrato persistente para C4 | C1 crea/revisa la tabla idempotente; C3 no modifica `dbt/**` ni el esquema ajeno |
| API no tiene productor | Hoy devuelve `cluster: null` sin distinguir causas | C4 implementa el `LEFT JOIN` y el estado explícito de cobertura |
| E2E MLflow no ejecutado con la corrida final | No hay `run_id` trazable para publicar | C3/C5 levantan MLflow, registran una sola corrida revisada y validan su carga |

No hay impedimento técnico irresoluble. La política ya no bloquea; el trabajo pendiente es ejecutar
la corrida reproducible y coordinar los cambios de Gold/API con sus dueños mediante PRs separados.
Este plan preserva el alcance de Estefany y las compuertas del vault.

## 10. Plan de respuesta a la revisión técnica de Andrés — 6-sep-2026

La revisión técnica confirma el enfoque y añade cinco condiciones de cierre. Se aceptan sin cambiar
prematuramente el estado de las historias:

| Observación | Acción de cierre | Estado |
|---|---|---|
| US-321 no está cerrada | Política ratificada por Andrés; ejecutar sobre Gold canónico `k=2..6`, seleccionar `k`, reportar Silhouette y registrar un `run_id` real | Pendiente de ejecución C3 |
| US-322 está cerca de cierre | Mantenerla independiente de ML-03; solicitar a Edgar aprobar la evidencia agregada ya completa y cambiar sólo entonces a `done` | Pendiente de Edgar |
| US-325 está cerca de cierre | Conservar cobertura y limitación sin crear un umbral de sesgo; solicitar a Edgar decidir el cierre documental | Pendiente de Edgar |
| Ambigüedad de dumps | Declarar `final1` como fuente canónica y `final2` sólo como comparación equivalente con checksum | Corregido en esta actualización |
| Gold/API fuera del alcance C3 | Mantener `gold.ml03_asignaciones` y C4 como plan posterior; C1 y C4 lo implementan en PRs propios bajo regla 7 | Plan, no entregable de esta PR |

### Próximos pasos ordenados

1. Ejecutar la corrida temporal real con el vector ya ratificado D1–D4 +
   `indice_completitud_drivers`; conservar la tabla comparable `k=2..6`, selección y Silhouette.
2. Cerrar US-322 y US-325 por revisión documental independiente, si Edgar lo aprueba; no esperar la
   corrida de ML-03 ni cambiar sus conclusiones de cobertura.
3. Registrar en MLflow la corrida reproducible revisada. Si no hay métrica válida o la interpretación
   no es defendible, US-321 sigue
   abierta con el resultado reportado tal cual.
4. Con una corrida trazable, C1 y C4 reciben el contrato de `gold.ml03_asignaciones` para sus PRs de
   esquema y API. Ninguno de esos cambios se incluye en esta PR documental.
