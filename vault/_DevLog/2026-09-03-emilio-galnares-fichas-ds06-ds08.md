---
id: DEVLOG-2026-09-03-EMILIO-GALNARES
project: "FARO"
date: "2026-09-03"
title: "DevLog — 2026-09-03 — Emilio Galnares — Fichas DS-06 y DS-08"
owner: "Emilio Galnares Ruiz"
author_human: "Emilio Galnares Ruiz"
agent: "Claude (chat)"
status: done
tags: [devlog, data-sources]
---

# DevLog — 2026-09-03 — Fichas DS-06 y DS-08

→ [[vault/_DevLog/_index|Volver al índice]] · [[vault/14_Data_Sources/DS-06_CONAGUA_SINA]] ·
[[vault/14_Data_Sources/DS-08_CONAPO_Proyecciones]]

- **Objetivo:** actualizar `DS-06_CONAGUA_SINA.md` y `DS-08_CONAPO_Proyecciones.md`, que seguían
  marcadas `PENDIENTE-CONFIRMAR` en el banner y en §2 pese a que §9 ya documentaba la prueba de
  descarga resuelta desde el 24/08/2026.
- **Rama:** `dev/emilio-galnares`
- **Cambios:** banner y §2 (Acceso) de ambas fichas, reflejando el endpoint real de CONAGUA
  (POST a `mapa.php`) y la limitación de descarga manual de CONAPO (sin URL fija).
- **IDs tocados:** `DS-06`, `DS-08`
- **Decisiones:** ninguna nueva; solo se documenta lo ya resuelto.
- **Preguntas abiertas:** ninguna de mi parte; D5 sigue `SIN_DATO` por un hueco de fuente ajeno,
  confirmado por Edgar.
- **Riesgos:** ninguno.
- **Próxima acción recomendada:** push a `dev/emilio-galnares` y abrir/actualizar PR.
