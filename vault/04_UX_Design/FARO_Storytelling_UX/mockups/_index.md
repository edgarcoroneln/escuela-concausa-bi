---
id: MOC-04-FARO-UX-MOCKUPS
title: "mockups/ — Los 7 mockups de escritorio de US-621"
owner: "Juan Carlos Macías Mayen"
status: active
tags: [moc, ux, mockups, s7, us-621]
---

# mockups/ — índice

→ [[vault/04_UX_Design/FARO_Storytelling_UX/_index|Volver al paquete]] ·
[[vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity]]

Entregable principal de `US-621` (`03_Visual_Identity.md` §7): los 7 mockups de escritorio, cada
uno con su PNG (captura) y su HTML (markup real, Tailwind autocontenido).

| # | Pantalla | PNG | HTML |
|---|---|---|---|
| 0 | Login | [00_Login.png](00_Login.png) | [00_Login.html](00_Login.html) |
| 1 | Entrada | [01_Entrada.png](01_Entrada.png) | [01_Entrada.html](01_Entrada.html) |
| 2 | Panorama de las escuelas en riesgo | [02_Panorama_Escuelas_Riesgo.png](02_Panorama_Escuelas_Riesgo.png) | [02_Panorama_Escuelas_Riesgo.html](02_Panorama_Escuelas_Riesgo.html) |
| 3 | Selección de caso | [03_Seleccion_Caso.png](03_Seleccion_Caso.png) | [03_Seleccion_Caso.html](03_Seleccion_Caso.html) |
| 4 | Expediente de escuela | [04_Expediente_Escuela.png](04_Expediente_Escuela.png) | [04_Expediente_Escuela.html](04_Expediente_Escuela.html) |
| 5 | Conclusión (Top 2 real; "Top 3" es el máximo de casillas, no una cuenta fija) | [05_Conclusion_Top3.png](05_Conclusion_Top3.png) | [05_Conclusion_Top3.html](05_Conclusion_Top3.html) |
| 6 | Explorador de escuelas | [06_Explorador.png](06_Explorador.png) | [06_Explorador.html](06_Explorador.html) |
| **S** | **Cómo funciona** — superficie hermana, fuera del recorrido (`PLAN_TRABAJO` §5.bis) | [Como_Funciona_Preview.png](Como_Funciona_Preview.png) | [Como_Funciona_Preview.html](Como_Funciona_Preview.html) |

> **Sobre la fila `S`.** *Cómo funciona* **es una superficie del producto** —el usuario la ve, con
> overlay y acceso desde P1 y desde el glosario— pero **no es una pantalla de la historia**: el
> recorrido sigue siendo P0–P6. Lleva identificador propio para que el Equipo 5 la encuentre aquí y
> no entre los anexos.
>
> **Equipo 5:** su comportamiento, acceso y retorno están en `01_UX_Architecture.md` §1; su alcance y
> su dependencia, en `PLAN_TRABAJO.md` §5.bis; las reglas de forma de sus bloques D3, en
> `02_Data_Visualization_Spec.md` §8.4. El contenido es del Equipo 1 (`US-601`) y llega por
> `GET /api/v1/about/secciones*`.
>
> *Movida de la tabla de soporte a la de superficies por Marina García el 2026-09-11, gate de UX/UI,
> avisado a Juan Macías.*

## Material de soporte (no numerado, no es de las 7 pantallas de la historia)

| Archivo | Qué es |
|---|---|
| [Guia_Identidad_Visual.png](Guia_Identidad_Visual.png) / [.html](Guia_Identidad_Visual.html) | Guía de identidad completa (paleta de interfaz, sistema de color de datos, tipografía, componentes) |
| [Design_Tokens_Stitch.md](Design_Tokens_Stitch.md) | Anexo técnico de `03_Visual_Identity.md` — tokens crudos de tipografía, radios, espaciado y elevación. Tiene su propio frontmatter (`DOC-FARO-UX-TOKENS`) |

Todos usan el dataset real de 7 escuelas verificado en producción (10-sep-2026, commit
`457715a`), nunca cifras tecleadas — ver `02_Data_Visualization_Spec.md` de Monserrat Miranda.
