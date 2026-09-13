Fixture anonimizado de Gold — chat FARO en local
=================================================

Para: Andrés González (C2, Chat IA) · Coordinación: Luis Téllez, 2026-09-13.

Qué es esto
-----------

Un recorte de `gold.dim_municipio` + `gold.dim_escuela` + `gold.fact_escuela_ciclo`
(las 3 tablas que consulta el Text-to-SQL del agente), anonimizado y acotado a
≤500 filas en el hecho, para que Andrés levante el chat en local
(`AUTH_LECTURA_PUBLICA=true`) sin tocar producción ni un DSN privado.

Cómo se generó
---------------

`python -m tests.fixtures.generate_gold_chat_fixture` (raíz del repo), contra el
Postgres LOCAL de quien lo corra (nunca producción — el script no acepta un DSN
remoto). Ver el docstring de ese archivo para el criterio completo de
anonimización. Resumen:

- `cct` → surrogate secuencial `ESC-{cve_ent}-{n}` (no un hash del cct real).
- `nombre` → genérico `Escuela {n}`.
- `nivel`, `cve_mun`, `cve_ent` → reales (no son sensibles, y el agente necesita
  agrupar bien).
- Latitud/longitud e infraestructura (agua, drenaje, ...) → **no se incluyen**:
  Luis no las pidió y son la forma más fácil de reidentificar el edificio real.
- Matrícula, D1–D6, `indice_completitud_drivers` → reales, sin perturbar: es lo
  que hace visible el diferenciador prescriptivo.
- `SIN_DATO` → mismo mecanismo que ya usa `gold.fact_escuela_ciclo` en producción
  (valor `NULL` + columna `dN_cobertura = 'SIN_DATO'`), no un string dentro de una
  columna numérica. D5 (estrés hídrico) sale `SIN_DATO` en el 100% de las filas
  porque hoy la propia `fact_escuela_ciclo.sql` no tiene fuente para D5 en ningún
  entorno — no es un defecto de este fixture.
- El mapa cct-real → surrogate se guarda **fuera del repo** (por defecto en
  `~/faro_mapa_cct_real_NO_SUBIR.csv`) — nunca se commitea.

El par del diferenciador (`15DPR0920D` / `15DPR2254O` reales — mismo municipio,
mismo índice de riesgo, distinto driver dominante, el mismo que usa "El
diferenciador" en `Conclusion.jsx`) se incluye siempre, para que Andrés pueda
reproducir esa demo con el chat.

Cómo se carga
--------------

```
psql "$DATABASE_URL" -f tests/fixtures/gold/cargar_fixture_gold.sql
```

Crea el esquema `gold` con las 3 tablas (si no existen) y carga los 3 CSV de este
directorio con `\copy`. Pensado para un Postgres local **vacío** de pruebas — el
`TRUNCATE` antes de cada carga es intencional y solo aplica aquí, no es el patrón
de ingesta de producción (que es append-only, ver `src/ingesta/`).

Pendiente de confirmar (criterio final: Diana, dueña de Gold)
----------------------------------------------------------------

- ¿260 escuelas está bien, o Andrés/Edgar prefieren otro número dentro de 200–300?
- ¿Se excluyen infraestructura/lat-long como se hizo aquí, o alguna sí hace falta
  para el chat?
- Falta la aprobación explícita de Edgar sobre alcance y datos incluidos (la pidió
  Andrés en su mensaje original) antes de compartir el fixture fuera de esta rama.
