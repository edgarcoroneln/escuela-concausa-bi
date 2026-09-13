---
title: "Fixture anonimizado de Gold para el chat local de Andres (coordinacion de Luis, US-2xx Chat IA)"
fecha: 2026-09-13
autor: Diana Aracely Alvarez Varela
herramienta: Claude Code / claude-sonnet-5
relacionado: [US-621, REQ-002]
---

## Contexto

Andres Gonzalez (C2, Chat IA) pidio un fixture/dump anonimizado de Gold (<=500 filas) para
probar el Text-to-SQL del chat en local, sin acceso a produccion. Luis Tellez coordino el
alcance exacto por mensaje: `gold.dim_municipio`, `gold.dim_escuela`, `gold.fact_escuela_ciclo`
(las 3 que consulta el agente), 200-300 escuelas de las 4 entidades del alcance, incluyendo
siempre el par real del diferenciador (mismo municipio/riesgo, distinto driver dominante) para
que la demo del chat lo pueda mostrar. Como duena de Gold, me toca definir el criterio final de
anonimizacion.

## Que se entrega (script, no el fixture todavia)

`tests/fixtures/generate_gold_chat_fixture.py`: se conecta al Postgres LOCAL (nunca produccion,
no acepta DSN remoto), extrae las 3 tablas, y anonimiza:

- `cct` -> surrogate secuencial `ESC-{cve_ent}-{n}` (no un hash: los CCT reales de todo el pais
  son publicos, un hash es reversible por diccionario).
- `nombre` -> generico `Escuela {n}`.
- `nivel`/`cve_mun`/`cve_ent` -> reales (no sensibles, el agente necesita agrupar bien).
- Latitud/longitud e infraestructura -> se excluyen (Luis no las pidio, y son la forma mas facil
  de reidentificar el edificio real aunque el nombre ya sea generico).
- Matricula, D1-D6, `indice_completitud_drivers` -> reales sin perturbar (es lo que hace visible
  el diferenciador).
- `SIN_DATO` -> mismo mecanismo que ya usa `fact_escuela_ciclo` en produccion (NULL +
  `dN_cobertura='SIN_DATO'`), no un string en una columna numerica.
- El par real del diferenciador (15DPR0920D/15DPR2254O) se incluye siempre.
- El mapa cct-real->surrogate se escribe FUERA del repo (`~/faro_mapa_cct_real_NO_SUBIR.csv`),
  nunca se commitea.

`tests/fixtures/gold/cargar_fixture_gold.sql`: crea el esquema `gold` (3 tablas) en un Postgres
local de pruebas vacio y carga los 3 CSV con `\copy`. `tests/fixtures/gold/README.md` documenta
todo lo anterior para Andres.

## Aprobacion de Edgar (revision de PR #358, 2026-09-13)

Edgar aprobo el alcance y los datos: 260 escuelas anonimizadas, sin coordenadas ni
infraestructura -- el criterio de anonimizacion descrito arriba (surrogate secuencial de CCT,
exclusion de lat/long e infraestructura, resto de columnas reales sin perturbar) queda
confirmado, sin ajustes pendientes.

## Pendiente

- Correr el script contra mi Postgres local (requiere psql, no disponible en este entorno de
  ejecucion) y revisar los CSV resultantes antes de subir nada.

## Verificacion

Sintaxis del script verificada con `python3 -m py_compile` (limpio). Sin Postgres/psql en este
entorno de ejecucion -- no se genero ningun CSV todavia, ni se toco produccion en ningun momento.
