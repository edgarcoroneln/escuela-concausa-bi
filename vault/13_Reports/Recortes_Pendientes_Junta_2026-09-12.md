---
title: "Recortes de datos pendientes — lo que Equipo 3 diseñó y hoy no tiene dato para mostrarse"
fecha: 2026-09-12
autor: Diana Aracely Alvarez Varela
herramienta: Claude Code / claude-sonnet-5
relacionado: [US-621, ADR-011, DEC-024, REQ-002]
---

# Recortes de datos pendientes — junta de freeze

→ Fuente canónica de este documento: `vault/04_UX_Design/FARO_Storytelling_UX/02_Data_Visualization_Spec.md` §8.1 ("Recortes explícitos"), depurada y con estatus actualizado al 12-sep.

Ninguno de estos recortes detiene la construcción (`DEC-024`): cada uno ya tiene su versión "mientras tanto" dibujable hoy, sin esperar al dato real. Esta lista es para decidir **qué se aprueba, quién lo resuelve y cuándo** — no para bloquear el freeze de hoy.

## 1. Requieren una decisión en esta junta

| Qué diseñó Equipo 3 | Por qué no hay dato hoy | Decisión que se necesita | Encargado(s) | Mientras tanto (ya construido) |
|---|---|---|---|---|
| **Evolución histórica de matrícula por escuela** (línea de tiempo, Comparativa/Expediente) | `GET /escuelas/{cct}` no acepta `ciclo`; el plan excluyó esto del expediente desde el inicio (§8.1 original) | ¿Se aprueba abrir `GET /escuelas/{cct}/series` (serie real de 3 ciclos)? Es alcance nuevo, no un fix | **Decide: Edgar Coronel (PO)** · Si se aprueba, implementa: **Christian Ruiz** | No se dibuja como línea de tiempo. Ya cubierto parcialmente por el punto 2 de abajo (actual vs. ciclo anterior) |
| **Explicación SHAP con valores** (panel aparte en P4, §4.4) | `shap_d1…shap_d6`: 0 de 42 contribuciones pobladas en producción | ¿Se prioriza poblar SHAP antes del freeze, o queda como deuda declarada post-freeze? | **Datos: Estefany Hernández Loredo** (ML-03 y explicación ML) · **UI: Diana Alvarez** (agregando el panel `SIN_DATO` ahora mismo, no depende de nadie) | Panel con el mensaje fijo: *"La explicación del modelo para esta escuela aún no está disponible (SIN_DATO)"* |
| **Perfil de ML-03 (`cluster`)** en el expediente | `cluster` es `None`, sin productor en Gold ni en la API (`US-631`) | ¿Se promueve ML-03 a producción (Gold → API → panel) antes o después del freeze? Ligado a `RISK-011`/`DEC-027`, ya evaluado como "post-freeze, sin fecha" | **Estefany Hernández Loredo** | No se muestra nada — ninguna etiqueta de perfil |
| **Escuela contra su municipio en D2…D6** | No hay promedio municipal de esos drivers en el contrato (D1/D2 ya son valores del municipio) | ¿Se agrega un agregado territorial por driver al contrato de la API? | **Decide/implementa: Christian Ruiz** | Solo el contexto de D1 con `pobreza_pct` |
| **Rezago del municipio contra el promedio estatal** | El promedio estatal no está en la API; el índice de CONEVAL es negativo en estos municipios (una barra desde cero lo invertiría) | ¿Se agrega la derivación al contrato, o se calcula en Front con llamadas adicionales (`GET /municipios?cve_ent=`)? Entra a la especificación solo con visto bueno de Marina | **Christian Ruiz** (contrato) o **Diana Alvarez** (cálculo en Front, con aprobación de **Marina García del Buey**) | Línea de contexto con `pobreza_pct` |
| **Indicadores filtrados por nivel educativo** (`/kpis`) | `/kpis` no acepta el parámetro `nivel` | ¿Se agrega `nivel` al contrato de `/kpis`? | **Christian Ruiz** | El filtro de nivel solo actúa sobre la lista visible, no sobre los KPIs agregados |
| **Distribución de niveles de atención en P6 para todo el filtro** | Contarlo exige paginar todo el universo del filtro (`size ≤ 100`); `/kpis` solo cuenta riesgo alto | ¿Se agrega un conteo por nivel de atención a `/kpis`? | **Christian Ruiz** | El nivel va por fila en la página visible; `escuelas_en_riesgo` del filtro sale de `/kpis` |
| **D5 estrés hídrico** | Sin fuente de datos integrada (`DS-06`) | ¿Quién y cuándo integra `DS-06` a Gold? | **Sin dueño confirmado todavía** — hay que asignarlo en esta junta | Rayado `SIN_DATO` en todas las escuelas |
| **`es_estimado_por_grupo` con valor** | La columna no existe en Gold; la API siempre da `null` | ¿Quién materializa esta columna y cuándo? | **Sin dueño confirmado todavía** — hay que asignarlo en esta junta | Texto: "Estimación por grupo: sin dato" |

## 2. Buenas noticias — se resuelven con el PR de hoy de Christian (pendiente de aprobar/mergear)

| Qué | Qué cambió | Falta |
|---|---|---|
| **Caída de matrícula de una escuela concreta** | Antes solo existía `variacion_matricula` agregada (`KpisOut`); Christian ya expuso `matricula_ciclo_anterior`/`variacion_matricula` **por escuela** | Que se apruebe y mergee su PR — **Edgar Coronel** |
| **6 drivers + completitud en batch** (matriz de Panorama) | Antes una llamada por escuela; ahora viajan en una sola llamada a `/escuelas` | Mismo PR — **Edgar Coronel** aprueba; **Diana Alvarez** actualiza el frontend para consumirlo (no urgente, no bloquea hoy) |

## 3. Ya resueltos — no deberían salir como pendientes en la junta

- **Prioridad de Gold / bandas oficiales alto-medio-bajo** → resuelto, es el nivel de atención (`ADR-011` §5).
- **Mapa de ubicación** → dejó de ser recorte el 12-sep; construido como contexto de ubicación, no como ranking (decisión de Diana Alvarez, documentada).
- **BUG-077 (`/municipios` 500)** → frente de dato (Diana) y frente de código (Christian) resueltos en código; pendiente de merge + despliegue en producción (ver seguimiento aparte con Luis Téllez).

---

*Documento de apoyo para la junta de freeze del 12-sep. No sustituye la especificación oficial (`02_Data_Visualization_Spec.md` §8.1), que sigue siendo la fuente de verdad.*
