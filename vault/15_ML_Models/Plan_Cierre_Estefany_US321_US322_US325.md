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
| `US-322` | `in_review` | EDA reproducible, selección de variables, controles de fuga y pruebas sobre fixture | Ejecutar contra `gold.features_escuela` reconstruida con datos reales, conservar evidencia agregada y actualizar conclusiones |
| `US-325` | `in_review` | Auditoría por driver, entidad y municipio; validación de `cve_mun`; pruebas de consistencia | Ejecutar contra Gold real, cuantificar brechas territoriales y documentar D5 como cobertura parcial sin convertir ausencia en cero |
| `US-321` | `in_progress` | Pipeline `StandardScaler` + KMeans, selección temporal de `k`, perfiles y registro MLflow | Ratificar política de ausencias, añadir una ejecución reproducible desde Gold, iterar sobre la métrica y registrar la corrida final |

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
