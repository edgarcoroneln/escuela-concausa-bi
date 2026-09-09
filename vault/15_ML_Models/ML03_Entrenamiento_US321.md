---
id: DOC-ML03-ENTRENAMIENTO-US321
title: "US-321 — Entrenamiento temporal de ML-03"
owner: "Estefany Lucero Hernández Loredo"
status: in_review
traces_up: ["US-321", "REQ-003", "vault/15_ML_Models/ML_Strategy"]
traces_down: ["US-324", "US-412"]
tags: [ml, ml-03, clustering, kmeans, silhouette]
---

# US-321 — Entrenamiento temporal de ML-03

> Implementación: `src/modelos/entrenar_ml03.py`.

> **Corte 8-sep-2026:** corrida local completada con el vector ratificado: `k=3`,
> Silhouette temporal `0.4644549058`. La auditoría identifica un grupo que coincide con la
> cobertura de D6, representada en completitud (`RISK-011`). Evidencia entregada para revisión;
> no equivale a registro MLflow, publicación Gold ni cierre aprobado de US-321.
> Ver «Corrida final de evidencia — 2026-09-08» al final de este documento.

## Entrega

- KMeans con `StandardScaler` dentro del mismo pipeline.
- Selección de `k` por Silhouette en ventanas walk-forward.
- El scaler y KMeans se ajustan sólo con ciclos anteriores a cada evaluación.
- Perfiles por cluster con los drivers promedio y una descripción determinista en lenguaje de
  negocio.
- Integración MLflow mediante el helper compartido de Célula 3, con versión canónica
  `ML03_ClusteringEscuelas` en Model Registry.

## Separación respecto al diagnóstico

US-322/US-325 se revisan en otro PR porque producen evidencia de calidad y cobertura, mientras
US-321 toma decisiones de entrenamiento. Mezclarlos obligaría a revalidar el diagnóstico cada vez
que cambie la política de imputación y ocultaría qué aprobación desbloquea cada historia.

## Política provisional de ausencia

El vector operativo ratificado por C3 para la corrida final es **D1-D4 +
`indice_completitud_drivers`**. D5 (`d5_agua`) y D6 (`d6_aire`) se conservan en el diagnóstico de
cobertura, pero no entran al vector de KMeans: D5 está 100 % `SIN_DATO` en el Gold real post-BUG-048
y D6 tiene cobertura residual, por lo que incluirlos bloquearía `casos_completos` o empujaría una
imputación no aprobada.

La política sigue siendo `casos_completos` sobre el **vector operativo**: las filas con D1-D4 o
completitud ausentes se contabilizan y excluyen; D5/D6 ausentes no excluyen una escuela ni se
rellenan con cero. Esta política permite verificar KMeans, Silhouette, partición temporal y perfiles
sin inventar señal en los drivers de cobertura parcial.

Registrar una versión no autoriza promoverla como modelo productivo ni interpretarla fuera del
alcance de esa cobertura. Cualquier futura reincorporación de D5/D6 al vector requiere nueva
evidencia de cobertura y revisión humana.

## Criterio pendiente para cierre

El PR #197 resolvió la disponibilidad reproducible de Bronze; el dump canónico permitió verificar
Gold en una base aislada. La corrida del 8-sep completa la selección temporal con el vector
ratificado, sin reconstruir Gold. El plan y prompt de ejecución están en
[[vault/15_ML_Models/Plan_Cierre_Estefany_US321_US322_US325]].

- [x] Usar D1-D4 + completitud, ratificado por Andrés; no se necesita imputación municipal.
- [x] Ejecutar sobre Gold canónico: tres ciclos, una ventana temporal y `k=2..6`.
- [x] Reportar métrica, perfiles y exclusiones sin esconder el efecto de cobertura.
- [ ] Andrés revisa la interpretación de `RISK-011` y la suficiencia de una ventana temporal.
- [ ] Registrar una corrida revisada en MLflow con `run_id` recuperable, si se autoriza avanzar.
- [ ] Edgar decide el cierre de US-321 o su deuda explícita; no se cambia el estado automáticamente.

## Ejecución reproducible desde Gold

## Corrida sobre Gold local — 2026-09-05

La fuente canónica es `gold_bug048_final1_2026-09-05 1.sql` (SHA-256
`07ECF29DEEE250732C38B252CA48794CCE413B5F295197E68804C337AC89D0BE`), restaurado en
`faro_gold_bug048_final1_review_20260905`. `final2` se comparó de forma independiente y produjo los
mismos agregados; no se mezclan cortes. El punto de entrada
`src.modelos.ejecutar_cierre_ml03` validó 136,046 filas, 46,547 escuelas, 3 ciclos y cero
duplicados por `cct × id_ciclo`. Esa corrida se hizo antes de ratificar el vector operativo y quedó
`bloqueada`: D5 (`d5_agua`) está en `SIN_DATO` para el 100% de las observaciones y D6 (`d6_aire`)
para el 98.70%.

No se entrenó KMeans, no se seleccionó `k`, no se calculó Silhouette y no se registró MLflow. Esta
salida es evidencia de cobertura y del bloqueo de la política, no una métrica negativa del modelo.
Tras la ratificación de C3, esta evidencia debe repetirse con D1-D4 + completitud; cualquier
imputación futura o reincorporación de D5/D6 al vector requeriría nueva evidencia de cobertura.

El punto de entrada `python -m src.modelos.ejecutar_cierre_ml03` lee la tabla real desde
`DATABASE_URL`, conserva la comparación walk-forward de `k=2..6` y exige dos fases para MLflow:
primero se genera y revisa la evidencia agregada; después, y sólo tras esa revisión, se indica
`--tracking-uri --confirmar-registro`. Si un driver operativo queda totalmente ausente,
`casos_completos` puede dejar cero filas: el comando lo reporta como bloqueo y no sustituye ausencias
ni registra un modelo.

La secuencia segura es:

```powershell
# Fase de evidencia: no registra ni promociona un modelo.
& ./.venv/Scripts/python.exe -c "from dotenv import load_dotenv; load_dotenv('.env'); from src.modelos.ejecutar_cierre_ml03 import main; raise SystemExit(main())" --salida $env:TEMP/ml03-evidencia.json

# Sólo tras revisión técnica: registra una corrida ya validada y devuelve su run_id.
& ./.venv/Scripts/python.exe -c "from dotenv import load_dotenv; load_dotenv('.env'); from src.modelos.ejecutar_cierre_ml03 import main; raise SystemExit(main())" --tracking-uri http://127.0.0.1:5001 --confirmar-registro --salida $env:TEMP/ml03-registro.json
```

Los JSON quedan fuera del repositorio y no contienen CCT individuales; se documentan únicamente sus
agregados, checksum del dump, `run_id`, versión y commit.

La primera ejecución del 4-sep no tuvo Docker ni Gold local; la evidencia de contrato y cobertura se
obtuvo el 5-sep con el dump aislado. El siguiente corte registra el entrenamiento posterior a la
ratificación; se conservan los antecedentes para distinguir el bloqueo histórico del estado actual.

## Corrida final de evidencia — 2026-09-08

**Resultado:** se ejecutó la fase analítica solicitada por Estefany para el PR de revisión de Edgar.
`k=3` obtiene **Silhouette 0.4644549058**, mayor que la referencia 0.30. Se recomienda aceptar esta
evidencia de ejecución y conservar ML-03 sin publicación hasta revisar `RISK-011`: el cluster 2
coincide exactamente con la disponibilidad de D6 entre las filas elegibles. Aprobar la evidencia
no aprueba el uso operativo ni cierra automáticamente la historia.

Fuente numérica reproducible: [ML03_Evidencia_20260908.json](ML03_Evidencia_20260908.json).
Registro de sesión: [[vault/_DevLog/2026-09-08-handoff-estefany-hernandez-corrida-ml03]].
El diagnóstico solicitado por Edgar quedó publicado previamente en
[PR #276, comentario del diagnóstico](https://github.com/edgarcoroneln/escuela-concausa-bi/pull/276#issuecomment-5577737792).
La aprobación anterior del PR #276 cubre su protección del registro, no los nuevos resultados de este corte.

### Fuente, alcance y controles

- Commit de código ejecutado: `7e514b849648ce7f5aa645495118d70d99dc58a6`.
- Dump canónico: `gold_bug048_final1_2026-09-05 1.sql`, 304,702,498 bytes,
  SHA-256 `07ECF29DEEE250732C38B252CA48794CCE413B5F295197E68804C337AC89D0BE`.
- Base: `faro_gold_bug048_final1_review_20260905`, únicamente en `127.0.0.1`.
  PostgreSQL confirmó `transaction_read_only=on`.
- Se compararon todas las líneas COPY de `gold.features_escuela` del dump y de la tabla local,
  ordenadas lexicográficamente y unidas con LF: SHA-256
  `2969de94a7ce88e8e2715756e6654f30770c098a310cc0cea5819a6e6c3c007b` en ambos casos.
  La igualdad prueba el contenido de esta tabla; no pretende auditar las otras tablas del dump.
- 136,046 observaciones, 46,547 escuelas distintas, tres ciclos, cero duplicados `cct × id_ciclo`.
- Orden de entrada fijado en `id_ciclo,cct`; `random_state=42`, `n_init=20`, dos hilos y
  `working_memory=256 MiB`. Silhouette usa todas las filas elegibles de prueba, sin muestreo.
  Ordenar elimina la ambigüedad del orden de filas SQL; limitar hilos/memoria controla recursos,
  sin sustituir el algoritmo ni cambiar los candidatos después de ver la métrica.
- Python 3.12.14, scikit-learn 1.9.0, NumPy 2.5.2, pandas 3.0.5, SQLAlchemy 2.0.52,
  psycopg2-binary 2.9.12, threadpoolctl 3.6.0. El CI usa Python 3.11; esta corrida local no es
  evidencia de equivalencia numérica entre versiones. Duración completa: 112.282 segundos.
- Sin `tracking-uri`, sin `confirmar-registro`, sin MLflow y sin persistencia de asignaciones.
  No se ejecutaron publicación Gold, migraciones, dbt ni sync de Superset. No se consultó producción.
  Las 45,276 predicciones publicadas y las decisiones DEC-019/BUG-063 permanecen fuera de esta operación.

### Decisiones de modelado y justificación

| Decisión | Justificación y límite |
|---|---|
| Conservar StandardScaler + KMeans | Es el algoritmo ya implementado y revisado; permite reproducir la propuesta sin introducir variantes durante el freeze. Escalar evita que una variable domine sólo por su dispersión. No demuestra por sí solo que los grupos tengan utilidad para intervenir escuelas. |
| D1-D4 + completitud, sin D5/D6 directos | Respeta la ratificación de Andrés y evita imputar señal no observada. La auditoría de abajo muestra que completitud todavía transmite cobertura de D6; no se cambió el vector unilateralmente para eliminar ese resultado. |
| Casos completos del vector operativo | Se excluyen y cuentan las filas incompletas; ni una ausencia ni un cluster se sustituyen por cero. La inferencia queda limitada al subconjunto elegible. |
| Entrenar en 2022-2023/2023-2024; validar en 2024-2025 | Scaler y centroides de cada candidato sólo ven el pasado. Tres ciclos permiten una ventana con dos ciclos de entrenamiento; no se inventan ventanas adicionales ni se divide aleatoriamente. |
| Comparar exactamente k=2..6 | Respeta la búsqueda predefinida. La función existente selecciona la mayor media temporal y, ante empate exacto, el k menor. No se probaron semillas ni algoritmos hasta conseguir una cifra favorable. |
| Separar selección y ajuste final | La métrica se obtiene antes del ajuste final. El modelo descriptivo final se reajusta con las 114,200 filas elegibles de los tres ciclos; sus perfiles no son una prueba temporal independiente. |

Estas prácticas de escalado y separación train/validación siguen la documentación primaria de
[StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)
y de [prevención de fuga de información](https://scikit-learn.org/stable/common_pitfalls.html).
Silhouette mide cohesión y separación geométrica, no causalidad ni beneficio de una intervención;
véase [selección de k con Silhouette](https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis).

### Elegibilidad y exclusiones

**114,200 filas elegibles (83.94 %) y 21,846 excluidas (16.06 %)** por ausencia en D1-D4/completitud.
D5/D6 no excluyen directamente. No se interpreta la fila excluida como escuela sana ni como cluster 0.

| Ciclo | Filas | Elegibles | Excluidas |
|---|---:|---:|---:|
| 2022-2023 | 45,317 | 38,407 | 6,910 |
| 2023-2024 | 45,453 | 38,103 | 7,350 |
| 2024-2025 | 45,276 | 37,690 | 7,586 |

| Entidad, tres ciclos | Filas | Excluidas | Exclusión |
|---|---:|---:|---:|
| CDMX | 20,999 | 2,337 | 11.13 % |
| Jalisco | 37,675 | 8,128 | 21.57 % |
| Estado de México | 57,726 | 7,703 | 13.34 % |
| Nuevo León | 19,646 | 3,678 | 18.72 % |

La exclusión no es territorialmente uniforme. No se declara representatividad nacional ni se
extrapolan los perfiles a las filas excluidas. El detalle ciclo × entidad queda en el JSON.

### Selección temporal de k

Todos los candidatos usan **76,510 filas de entrenamiento y 37,690 de validación**.
El escalador se ajusta dentro de cada pipeline con las filas de entrenamiento.

| k | Silhouette en 2024-2025 | Seleccionado |
|---:|---:|---|
| 2 | 0.4588341487 | No |
| 3 | 0.4644549058 | Sí |
| 4 | 0.4139704910 | No |
| 5 | 0.3939472663 | No |
| 6 | 0.4067550465 | No |

La ventaja de k=3 frente a k=2 es **0.0056207571**. No se estimaron intervalos de confianza ni se
demostró significancia de esa diferencia. La misma ventana selecciona k y reporta su resultado:
es validación temporal para selección, **no un test externo independiente**. No se afirma estabilidad
entre ventanas ni entre semillas. El 0.1086 histórico pertenece a otro protocolo/corte y no es una
comparación controlada de mejora frente a 0.4645.

### Perfiles descriptivos del ajuste final

Promedios en la escala original. D3/D4 altos representan mejores servicios, por eso la narrativa
usa `1-D3` y `1-D4` para hablar de carencias. Los identificadores de cluster son etiquetas de esta
corrida, no niveles de riesgo, ni equivalen al driver dominante de ML-02.

| Cluster | Observaciones | Escuelas distintas dentro del grupo | D1 | D2 | D3 | D4 | Completitud |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 29,875 | 10,014 | 0.1489 | 0.1584 | 0.7431 | 0.3851 | 0.6667 |
| 1 | 82,677 | 27,942 | 0.0447 | 0.2870 | 0.9892 | 0.9124 | 0.6667 |
| 2 | 1,648 | 551 | 0.1877 | 0.1356 | 0.8129 | 0.6596 | 0.8333 |

- **Cluster 0 (26.16 % de observaciones):** brecha de conectividad y carencias de infraestructura.
- **Cluster 1 (72.40 %):** mejores servicios medios; la narrativa relativa destaca inseguridad.
  No significa riesgo alto ni recomienda por sí sola una intervención.
- **Cluster 2 (1.44 %):** el texto automático destaca conectividad y pobreza, pero la auditoría
  identifica que este grupo es, exactamente, el de cobertura D6 observada entre los elegibles.
  No se presenta como tercer perfil sustantivo validado.

En 2024-2025 las asignaciones descriptivas son 9,922 / 27,219 / 549 para clusters 0/1/2.
Las escuelas pueden aparecer en varios ciclos y cambiar de grupo; no se suman los conteos de
escuelas distintas por cluster para obtener un total único.

### RISK-011: completitud introduce cobertura de D6 indirectamente

El refit de auditoría usa el **k=3 ya seleccionado**, misma semilla, orden y parámetros; reproduce
los conteos finales. No vuelve a buscar k ni modifica el protocolo. Cruza las asignaciones sólo en
memoria contra la bandera D6 de las mismas llaves, y publica únicamente este agregado:

| Cluster | Completitud | D6 | Observaciones |
|---:|---:|---|---:|
| 0 | 4/6 | SIN_DATO | 29,875 |
| 1 | 4/6 | SIN_DATO | 82,677 |
| 2 | 5/6 | OK | 1,648 |

**Todas las 1,648 observaciones elegibles con D6 observado están en cluster 2 y ninguna con D6
ausente está en él.** D5 está ausente y D1-D4 son completos en este subconjunto: completitud
codifica aquí la disponibilidad de D6. El cluster 2 contiene 348 observaciones de CDMX y 1,300
del Estado de México; cero de Jalisco/Nuevo León. Son 551 escuelas distintas en tres ciclos.
La asociación es exacta en este ajuste; no se afirma causalidad a partir de ella.

El riesgo es que la interfaz narre un grupo de cobertura como una necesidad escolar. Está dado
de alta en [[vault/10_Risk_Governance/Risk_Register]] como `RISK-011`, ligado a US-321/US-325.
No contradice que se hayan excluido los valores directos de D6: demuestra una vía indirecta a
través de una feature autorizada. Tampoco prueba que k=2 lo resuelva, porque usaría la misma feature.

### Decisión propuesta para Andrés y Edgar

1. **Aceptar la ejecución y el diagnóstico como entregable de esta fase.** El bloqueo de entrenamiento
   por ausencia estructural ya fue superado con la política ratificada y hay evidencia cuantitativa.
2. **Mantener ML-03 como SIN_DATO en producción para la demo**, bajo DEC-015, hasta resolver la
   interpretación de RISK-011. Superar 0.30 no autoriza convertir el grupo de cobertura en recomendación.
3. **Evaluación posterior propuesta, no ejecutada:** Andrés decide si comparar D1-D4 sin completitud,
   con las mismas filas/ventana/candidatos y auditando cobertura por separado. No es autorización para
   cambiar el vector ratificado ni promesa de una métrica mejor. Más ciclos permitirían separar
   selección y evaluación externa; con este dump esa evidencia no existe.
4. **MLflow y dos cables quedan pendientes:** primero corrida revisada y productor C3 con esquema
   de C1; después lectura de C4 y comprobación del Panel. No se registra un `run_id` de relleno,
   no se altera Gold y no se cierra US-321 desde esta PR documental.

La comparación Panel/DB-03 del par de demo continúa separada y pendiente de resolver BUG-065;
esta corrida no prueba ni modifica el riesgo 0.4774 ni los drivers D4/D2 del par.

### Reproducir la fase de evidencia sin publicar

Usar el commit y versiones indicados arriba, el dump canónico ya restaurado y el `.env` local
existente. Guardar el siguiente bloque como script **local ignorado** en `_local/` y ejecutarlo
desde la raíz con `.venv/Scripts/python.exe`. No imprime ni incluye la contraseña en argumentos.

```python
import json
import sys
from pathlib import Path

root = Path.cwd()
sys.path.insert(0, str(root))
from dotenv import dotenv_values
from sklearn import config_context
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from threadpoolctl import threadpool_limits
from src.modelos.entrenar_ml01 import cargar_features_desde_gold
from src.modelos.ejecutar_cierre_ml03 import generar_evidencia

url = make_url(dotenv_values(root / '.env')['DATABASE_URL'])
assert url.host in {'127.0.0.1', 'localhost'}
url = url.set(database='faro_gold_bug048_final1_review_20260905')
engine = create_engine(url, connect_args={
    'options': '-c default_transaction_read_only=on', 'connect_timeout': 5,
})
with engine.connect() as conn:
    assert conn.execute(text('SHOW transaction_read_only')).scalar() == 'on'
df = cargar_features_desde_gold(engine)
engine.dispose()
df = df.sort_values(['id_ciclo', 'cct'], kind='stable').reset_index(drop=True)
with threadpool_limits(limits=2), config_context(working_memory=256):
    reporte, resultado = generar_evidencia(df)
assert resultado is not None, reporte['ml03']
detalle = resultado.asignaciones.merge(
    df[['cct', 'id_ciclo', 'd6_cobertura']],
    on=['cct', 'id_ciclo'], validate='one_to_one',
)
cruce = detalle.groupby([
    'cluster', 'indice_completitud_drivers', 'd6_cobertura'
]).size().rename('observaciones').reset_index()
reporte['auditoria_d6'] = json.loads(cruce.to_json(orient='records'))
(root / '_local/ml03-reproduccion.json').write_text(
    json.dumps(reporte, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
)
```

El JSON versionado conserva sólo agregados y proveniencia. El dump, el JSON local completo y las
asignaciones individuales no se versionan. El código productivo de entrenamiento y registro no cambia.
