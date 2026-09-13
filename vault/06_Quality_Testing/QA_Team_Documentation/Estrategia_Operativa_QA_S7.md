---
id: DOC-QA-ESTRATEGIA-FARO
title: "Estrategia Operativa de Aseguramiento de Calidad (QA) — Sprint 7"
owner: "Edward Ulysses Ruiz Bustillos"
status: in_review
source_of_truth: false
traces_up: ["REQ-004", "REQ-005", "US-621", "US-651"]
traces_down: ["vault/06_Quality_Testing/Plan_QA_Exhaustivo_S7"]
tags: [qa, estrategia, e2e, rbac, release]
---

# Estrategia Operativa de Calidad y Evaluación E2E — FARO (Sprint 7)

> **División de Alcance:** Este documento define la **operativa de trabajo del equipo de QA** (cómo opera el equipo de 3 personas). El detalle específico de casos de prueba y superficies se encuentra en el [[vault/06_Quality_Testing/Plan_QA_Exhaustivo_S7|Plan de QA Exhaustivo S7]].
>
> **Alcance estricto del universo:** El análisis y las pruebas aplican única y exclusivamente para escuelas de nivel **preescolar (kínder), primaria y secundaria** (conforme a las reglas de dbt).

## 1. Alineación con Decisiones de Arquitectura (DEC-027 y RBAC)

*   **Machine Learning (ML-03 / DEC-027):** Conforme a DEC-027, el modelo ML-03 **NO está integrado ni operativo** en esta entrega (sin capa Gold, API ni panel activo). QA verificará y auditará exclusivamente que el sistema declare formalmente este componente como no operativo/no disponible, en lugar de intentar auditar clusters o métricas inexistentes en la UI.
*   **Control de Acceso (RBAC):** FARO utiliza **RBAC** (Role-Based Access Control) para la gestión de permisos y roles de usuario. Se elimina cualquier referencia a RLS (Row Level Security), ya que no aplica en la arquitectura del proyecto.

## 2. Modelo de Trabajo: "Owner Checks" y Verificación QA
El equipo de QA (3 personas) actuará como **orquestadores de calidad**: QA define los criterios de aceptación → el Tech Owner ejecuta y entrega evidencia → QA valida el resultado en la interfaz.

### Matriz de Perspectivas QA

| Rol | Foco de Auditoría | Criterio de Falla (Fail) |
|---|---|---|
| **QA 1: Data & Lógica** | Universo escolar (kínder, primaria, secundaria), KPIs, reglas de `SIN_DATO`, validación de endpoints y permisos **RBAC**. | Números masivos expuestos; cálculos erróneos vs API; datos inconsistentes. |
| **QA 2: Funcional E2E** | Navegación, rutas de 7 pantallas, estados de carga/error, interacción del Chat IA y expedientes. | Pantallas rotas; errores 400/500; filtros que colapsan la UI. |
| **QA 3: UX & Storytelling** | Narrativa ("7 casos"), uso de copy dinámico, ausencia de IDs o código expuesto. | Lenguaje de causalidad absoluta; texto técnico expuesto (ej. `RBAC`, código JS). |

## 3. Criterios de Liberación (Go / No-Go)
- **🟢 GO:** Cero defectos P0/P1. Flujos críticos limpios. *Owner checks* entregados con evidencia. Universo y KPIs correctos. Narrativa intacta.
- **🟡 GO WITH RISKS:** Defectos P2/P3 abiertos con dueño asignado y fecha de resolución, sin afectación a la interpretación de datos ni a la narrativa.
- **🔴 NO-GO:** Universo incorrecto, métricas/textos *hardcodeados*, lenguaje de causalidad no soportado, estado degradado no controlado o errores P0/P1 sin resolver.

## 4. Resumen del Flujo de Trabajo (Los 6 Pasos)

1. **Definimos qué se debe cumplir:** QA establece los criterios de aceptación y Data Contracts por equipo.
2. **Cada equipo entrega evidencia:** Backend, Chat, UX, Data y Deploy entregan evidencia de sus *Owner Checks* antes de habilitar QA.
3. **QA verifica en el producto real:** Las tres personas de QA ejecutan la auditoría desde sus tres perspectivas (Datos, Funcional, UX).
4. **Priorización por impacto:** Validación prioritaria de universos escolares, KPIs y drivers.
5. **Recorrido E2E guiado:** Ejecución conjunta del journey completo de usuario (Login → Panorama → Expedientes).
6. **Veredicto y Regresión:** Emisión del dictamen formal de liberación (Go / No-Go).