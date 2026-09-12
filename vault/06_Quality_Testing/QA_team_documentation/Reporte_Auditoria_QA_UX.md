---
id: QA-STRATEGY-FARO
title: "Estrategia Operativa de Aseguramiento de Calidad (QA) — Proyecto FARO"
owner: "Edward Ulysses Ruiz Bustillos"
status: approved
source_of_truth: true
tags: [qa, estrategia, e2e, ml, release]
---

# Estrategia de Calidad y Evaluación E2E — FARO

> Orquestación de pruebas descentralizadas para el rediseño y despliegue del proyecto FARO. 
> **Alcance estricto del universo:** El análisis y las pruebas aplican única y exclusivamente para escuelas de nivel **preescolar (kínder), primaria y secundaria**.

## 1. Introducción a la Evaluación de Machine Learning (ML)
Para que QA pueda auditar correctamente los modelos (específicamente la reciente integración de **ML-03** validada en el PR #317), es vital entender su función. Un modelo de ML en FARO no "adivina" causas; encuentra patrones matemáticos en los datos para clasificar o predecir escenarios. 

**¿Qué hace y cómo lo evaluamos?**
*   **Clustering (ML-03):** Agrupa las escuelas en perfiles basados en características comunes. QA debe validar que el modelo utilice estrictamente los drivers autorizados (D1-D4) para crear los 2 grupos definidos, sin forzar datos inexistentes de estrés hídrico (D5) o calidad del aire (D6).
*   **Manejo del Vacío:** La evaluación de QA debe asegurar que la ausencia de datos predictivos arroje un estado de `SIN_DATO` ("pista no verificada"), jamás un error técnico como "No data" ni una serie artificial en las gráficas.

## 2. Modelo de Trabajo: "Owner Checks" y Verificación QA
El equipo de QA (3 personas) no será un cuello de botella depurando código. Actuaremos como **orquestadores de calidad**: QA define qué debe comprobarse → el Tech Owner comprueba y entrega evidencia → QA valida el resultado en la interfaz.

### Matriz de Perspectivas QA
El equipo atacará la plataforma simultáneamente desde tres frentes:

| Rol | Foco de Auditoría | Criterio de Falla (Fail) |
|---|---|---|
| **QA 1: Data & Lógica** | Universo (kínder, primaria, secundaria), KPIs, reglas de `SIN_DATO`, RLS. | Números masivos expuestos; cálculos erróneos vs API. |
| **QA 2: Funcional E2E** | Navegación, filtros, *loading states*, integración del Chat IA, expedientes. | Pantallas rotas; errores 400/500; filtros que colapsan la UI. |
| **QA 3: UX & Storytelling** | Narrativa ("7 casos"), uso de copy dinámico, ausencia de IDs o código expuesto. | Lenguaje de causalidad absoluta; texto técnico expuesto (ej. `RLS`). |

## 3. Criterios de Liberación (Go / No-Go)
- **🟢 GO:** Cero defectos P0/P1. Flujos críticos limpios. *Owner checks* entregados. Universo y KPIs correctos. Narrativa intacta.
- **🟡 GO WITH RISKS:** Defectos P2/P3 abiertos con dueño y fecha de resolución, siempre que no afecten la interpretación de datos ni la narrativa.
- **🔴 NO-GO:** Universo incorrecto, métricas/textos *hardcodeados*, lenguaje de causalidad no soportado, recomendación/predicción técnica rota o errores P0/P1 sin resolver.

## 4. Resumen del Flujo de Trabajo (Los 6 Pasos)

1. **Definimos qué se debe cumplir:** QA arma primero los criterios de aceptación por equipo (Backend, Chat, UX, ML, Deploy) y el Data Contract: qué dato sale de qué endpoint y con qué regla. Esto es lo que ya armamos hoy, antes de tocar el producto.
2. **Cada equipo entrega evidencia, no promesas:** Backend, Chat, UX, ML y Deploy no dicen 'ya quedó' — entregan query, captura, resultado o log que demuestre que cumplieron su Owner Check. Sin evidencia, QA no empieza a probar (*Not Ready for QA*).
3. **QA verifica en el producto real:** Con la evidencia en mano, las tres personas de QA revisan cada una su ángulo: datos y números correctos, flujo funcional de punta a punta, y que el storytelling no diga nada que los datos no soporten.
4. **Priorizamos por lo que más pesa:** Viernes atacamos primero lo que rompe todo si está mal: universo de escuelas, KPIs y drivers. Si eso falla, no seguimos probando lo demás encima de una base incorrecta.
5. **Recorremos el producto completo:** Sábado los tres QA hacemos el mismo journey (Login → Entrada → Panorama → Selección → Expediente → Conclusión → Exploración), cada uno buscando algo distinto, y cruzamos hallazgos en una sesión conjunta.
6. **Cerramos con regresión y un veredicto claro:** Domingo confirmamos que las correcciones no rompieron nada más, y damos un GO, GO WITH RISKS o NO-GO según reglas fijas.