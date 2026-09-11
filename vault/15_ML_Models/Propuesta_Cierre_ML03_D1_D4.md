---
id: PROP-CIERRE-ML03-D1-D4
title: "Propuesta de cierre ML-03 con evidencia disponible"
owner: "Deni Garrido Fragoso"
status: proposed
version: "1.0"
source_of_truth: false
traces_up: ["US-631", "REQ-003", "RISK-011"]
traces_down: ["ML03_Comparacion_RISK011_20260910"]
last_reviewed: "2026-09-10"
tags: [ml, ml-03, propuesta, storytelling, cobertura, risk-011]
---

# Propuesta de cierre ML-03 con evidencia disponible

> Esta propuesta no constituye aprobación, promoción a producción ni cierre de `RISK-011`.
> Presenta una ruta acotada para revisión de Estefany Hernández, decisión del PO y validación de QA.

## 1. Decisión propuesta

Cerrar la brecha funcional de ML-03 con el vector operativo **D1-D4**, seleccionar `k` mediante la
validación temporal existente y conservar `indice_completitud_drivers` exclusivamente como atributo
de auditoría. D5 y D6 permanecen fuera del clustering hasta que exista una segunda versión del
contrato de datos con cobertura y temporalidad defendibles.

La variante candidata es:

| Elemento | Propuesta |
|---|---|
| Features | D1 pobreza, D2 inseguridad, D3 infraestructura y D4 conectividad |
| Algoritmo | `StandardScaler` + KMeans |
| Selección | `k=2`, elegido entre `k=2..6` |
| Silhouette temporal | `0.4620526551` |
| Estabilidad | ARI mínimo y promedio `1.0` en semillas 7, 21, 42, 84 y 2026 |
| Ausencias | Casos completos sobre D1-D4; sin imputar `SIN_DATO` |
| Completitud | Visible para auditoría, fuera del vector |
| D5/D6 | Fuera del vector y sin reemplazo por cero |
| MLflow | `ML03_ClusteringEscuelas` v1, corrida `d971ab7271df45629c9a50c27514890f` |

La evidencia agregada reproducible está en
[ML03_Comparacion_RISK011_20260910.json](ML03_Comparacion_RISK011_20260910.json).

La corrida candidata quedó registrada para revisión en el MLflow local con estado `FINISHED`; la
versión 1 está `READY` y su artefacto `StandardScaler + KMeans` fue descargado y cargado nuevamente
con `mlflow.pyfunc`. Este registro aporta trazabilidad, pero no constituye promoción a producción ni
aprobación de `RISK-011`.

## 2. Por qué se propone D1-D4

La corrida anterior usó D1-D4 más completitud y obtuvo `k=3`, con Silhouette `0.4644549058`. Sin
embargo, su cluster 2 coincidió exactamente con las 1,648 observaciones elegibles que tenían D6.
Completitud separó disponibilidad de información, no un perfil sustantivo de escuela.

Al retirar completitud:

| Resultado | D1-D4 + completitud | D1-D4 |
|---|---:|---:|
| `k` seleccionado | 3 | 2 |
| Silhouette | 0.4645 | 0.4621 |
| Cluster equivalente a D6 disponible | Sí, 1,648 observaciones | No |
| Estabilidad medida en cinco semillas | No documentada | ARI 1.0 |

La reducción de Silhouette es `0.0024`, mientras se elimina una separación engañosa. El resultado
supera el umbral provisional del proyecto (`>= 0.30`), pero se presenta como segmentación moderada,
no como estructura fuerte ni como evidencia causal.

Los perfiles candidatos son:

| Perfil | Observaciones | Lectura permitida |
|---|---:|---|
| Presión por inseguridad | 83,275 | Mayor presión relativa de D2; infraestructura y conectividad relativamente mejores |
| Presión por conectividad e infraestructura | 30,925 | Mayor brecha relativa en D4 y D3, con pobreza promedio también mayor |

Los números de cluster son etiquetas sin orden. No significan riesgo alto/bajo ni prioridad automática.

## 3. Encaje con el storytelling FARO

La experiencia se plantea como **un caso escolar con siete pistas**:

1. Matrícula como señal que abre la investigación.
2. Pobreza y rezago.
3. Inseguridad.
4. Infraestructura escolar.
5. Conectividad.
6. Estrés hídrico.
7. Calidad del aire.

No se crea un séptimo driver. Matrícula continúa siendo señal, no causa. ML-03 responde únicamente:

> Con las pistas actualmente observables, ¿qué patrón comparte esta escuela con otras escuelas?

La interfaz debe distinguir tres estados de evidencia: `OK`, `PARCIAL` y `SIN_DATO`. Para la entrega
candidata, D5 se muestra sin evidencia utilizable y D6 como evidencia insuficiente/no comparable con
el ciclo escolar. Esto permite responder honestamente "¿qué tan completo está el expediente?" sin
convertir ausencia en cero ni usar completitud para agrupar.

Texto sugerido para ML-03:

> Con cuatro de las seis líneas de investigación disponibles, esta escuela comparte un patrón de
> presión principalmente asociado con [perfil]. Agua y calidad del aire no participan en esta
> segmentación por cobertura insuficiente.

### Presentación para el usuario final

La interfaz no debe mostrar términos técnicos como `ML-03`, `cluster`, `feature`, `observación no
elegible` o `SIN_DATO`. La salida técnica se traduce a la metáfora de investigación de FARO.

Cuando existe evidencia suficiente para reconocer un patrón:

> **Lo que nos dicen las pistas**
>
> Esta escuela comparte características con otros planteles donde destacan principalmente los
> problemas de conectividad e infraestructura.
>
> Contamos con evidencia comparable en **4 de las 6 pistas**: pobreza, inseguridad,
> infraestructura y conectividad.
>
> La investigación sobre estrés hídrico y calidad del aire continúa abierta porque todavía no
> contamos con información suficiente. Esto no significa que no existan problemas, sino que aún
> no tenemos evidencia para evaluarlos.

Resumen visual sugerido:

```text
Evidencia encontrada: 4 de 6 pistas

✓ Pobreza y rezago
✓ Inseguridad
✓ Infraestructura
✓ Conectividad
○ Estrés hídrico: investigación pendiente
○ Calidad del aire: información insuficiente
```

Cuando falta alguna de las cuatro pistas necesarias para comparar escuelas:

> **Aún no tenemos evidencia suficiente**
>
> Todavía no es posible comparar esta escuela de manera responsable con otros planteles.
> Encontramos información en **[X] de las 6 pistas**, pero falta evidencia necesaria sobre
> [pistas faltantes]. Esto no significa que la escuela no tenga dificultades; significa que
> necesitamos reunir más información antes de presentar una conclusión.

Los títulos visibles recomendados son `Lo que nos dicen las pistas`, `Estado de la investigación`,
`Evidencia encontrada` y `Pistas pendientes`. D5 y D6 conservan sus valores y estados originales;
esta presentación sólo explica la cobertura y no modifica los datos ni el agrupamiento.

## 4. Estado real de D5 y D6

### D5: estrés hídrico

El extractor disponible carga 180 presas con capacidades `NAME` y `NAMO`, pero no obtiene el contrato
que necesita D5: medición temporal de disponibilidad/estrés, fecha comparable, región hidrológica y
georreferencia utilizable. `silver.agua_region` espera otro esquema y Gold mantiene D5 explícitamente
en `SIN_DATO`.

D5 no se perdió por una llave accidental. La fuente extraída no permite calcular responsablemente
estrés hídrico por escuela y la integración quedó incompleta.

### D6: calidad del aire

El cruce observación-estación usa `id_estacion`. El cruce estación-escuela es geoespacial mediante
latitud/longitud, distancia Haversine, radio máximo de 15 km e interpolación IDW. La extracción actual
solicita `rango=1` (un día) y no implementa backfill histórico.

En el entorno revisado hay 418 registros del 5-sep-2026, 93 estaciones y 56 estaciones con PM2.5
válido. El Gold canónico asigna D6 a 595 escuelas y 1,774 observaciones escuela-ciclo. Además, el SQL
promedia las fechas disponibles sin agrupar por ciclo, por lo que no debe presentarse como evidencia
histórica comparable para 2022-2023, 2023-2024 y 2024-2025.

## 5. Riesgos de reabrir D5/D6 antes del cierre

| Riesgo | Impacto posible | Mitigación propuesta |
|---|---|---|
| Cambio de contrato Bronze/Silver | Romper loaders, dbt y pruebas de fuentes | Versionar el contrato y trabajar en base aislada |
| Cambio de grano temporal | Duplicados o uniones incorrectas por `cct × id_ciclo` | Aprobar grano y llaves antes de cargar Gold |
| Fuga temporal en D6 | Usar mediciones futuras para explicar ciclos pasados | Agregar por ciclo y limitar fechas antes de entrenar |
| Semántica incorrecta de D5 | Confundir capacidad de presa con estrés hídrico escolar | Definir el indicador y seleccionar una fuente adecuada |
| Cobertura geográfica artificial | Asignar estaciones o presas demasiado lejanas | Conservar radios/regiones defendibles y `SIN_DATO` fuera de cobertura |
| Cambio de `driver_dominante` | Alterar ML-02 y sus recomendaciones | Recalcular distribución, F1, SHAP y reglas de recomendación |
| Deriva en ML-01 | Cambiar riesgo y umbrales visibles en el producto | Reentrenar y comparar contra baseline temporal |
| Deriva en ML-03 | Cambiar `k`, perfiles y pertenencia de escuelas | Repetir `k=2..6`, estabilidad y perfiles |
| Inconsistencia Gold/API/UI | Mostrar modelos de versiones incompatibles | Publicar una versión atómica y ejecutar E2E |
| Retraso de entrega | Abrir un frente de datos sin estimación ni cobertura garantizada | Separar D5/D6 de la ruta crítica de ML-03 |

El impacto potencial completo es:

```text
Fuente externa
→ extractor
→ Bronze
→ Silver
→ gold.features_escuela
→ driver_dominante
→ ML-01 / ML-02 / ML-03
→ publicaciones Gold
→ API
→ frontend y storytelling
→ QA y despliegue
```

## 6. Riesgos de aceptar esta propuesta

La ruta D1-D4 también conserva limitaciones que deben permanecer visibles:

- ML-03 utiliza cuatro de los seis drivers oficiales.
- Se excluyen 21,846 observaciones con ausencia en D1-D4.
- La validación temporal disponible contiene una sola ventana de prueba.
- Silhouette `0.4621` indica una estructura moderada, no fuerte.
- Los perfiles no prueban causalidad ni efectividad de una intervención.
- D5 y D6 continúan como deuda de datos del proyecto.

Estas limitaciones se mitigan mostrando cobertura por pista, evitando lenguaje causal y conservando
`SIN_DATO` para escuelas sin evidencia o sin asignación.

## 7. Alcance para cerrar ML-03

La corrida y el registro técnico ya se completaron. Después de la aprobación formal, la ruta mínima
restante incluye:

1. Ratificar D1-D4 como vector de ML-03 y actualizar su model card.
2. Persistir `cct × id_ciclo × cluster` en un contrato Gold aprobado e idempotente.
3. Hacer que la API consulte la asignación real en lugar de fijar `cluster = None`.
4. Mostrar perfil, cobertura y limitaciones en el panel.
5. Validar el mismo CCT, ciclo, cluster y versión mediante una prueba E2E sobre base real.
6. Conservar `null`/`SIN_DATO` cuando una escuela no tenga asignación elegible.

Quedan fuera de este cierre:

- Rediseñar D5.
- Ejecutar backfill histórico de D6.
- Aumentar artificialmente el radio de estaciones.
- Reentrenar ML-01 y ML-02 por nuevas versiones de D5/D6.
- Declarar que los seis drivers tienen cobertura productiva.

## 8. Criterios de aceptación

La propuesta puede promoverse sólo si se cumplen todos estos puntos:

- Revisión técnica de Estefany sobre vector, métricas, perfiles y limitaciones.
- Decisión explícita del PO sobre la mitigación de `RISK-011`.
- D1-D4 son las únicas features del estimador; completitud queda como auditoría.
- `k=2..6` se evalúa con la misma partición temporal y el resultado final queda registrado.
- MLflow conserva parámetros, métrica, artefacto, perfiles y versión de código.
- Gold publica asignaciones sin duplicados y con `run_id` trazable.
- API devuelve entero para asignación válida y `null` para ausencia.
- Frontend no interpreta cluster como nivel de riesgo.
- QA demuestra Gold → API → panel sin mocks como evidencia E2E.
- El storytelling declara que D5/D6 no participan por cobertura insuficiente.

## 9. Tratamiento posterior de D5/D6

D5 y D6 deben abrirse como una evolución separada de datos/modelos, no como un ajuste silencioso de
la entrega actual. Antes de cambiar Gold se requiere:

1. Diagnóstico de fuente y cobertura esperada.
2. Contrato de datos versionado y grano temporal aprobado.
3. Reconstrucción en una base aislada.
4. Comparación de cobertura y distribución antes/después.
5. Reentrenamiento y evaluación de ML-01, ML-02 y ML-03.
6. Pruebas de regresión de recomendaciones, API, panel y cubos.
7. Plan de migración y rollback.

Para D5 debe definirse primero si el indicador representa disponibilidad por acuífero/cuenca,
sequía, almacenamiento u otra medida oficial. Para D6 debe implementarse backfill y agregación por
ciclo, manteniendo `SIN_DATO` para escuelas fuera de cobertura espacial confiable.

## 10. Decisión pendiente

| Rol | Decisión requerida | Estado |
|---|---|---|
| Deni Garrido | Presentar propuesta y evidencia reproducible | Completado para revisión |
| Estefany Hernández | Revisión técnica de ML-03 | Pendiente |
| PO | Aprobar D1-D4 y tratamiento de `RISK-011` | Pendiente |
| Equipo 5 | Aceptar contrato de integración API/frontend | Pendiente después del gate |
| Equipo 6 | Definir y ejecutar aceptación E2E | Pendiente después del gate |

La corrida candidata está registrada en MLflow únicamente como evidencia técnica para revisión.
Hasta completar esas decisiones, no se promueve el modelo, no se publica Gold y no se afirma que
ML-03 esté aprobado o integrado en el producto.
