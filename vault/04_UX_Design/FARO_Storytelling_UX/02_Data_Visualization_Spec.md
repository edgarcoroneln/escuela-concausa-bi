---
id: DOC-FARO-UX-DATAVIZ
title: "Data Visualization Spec — qué dato demuestra la historia"
owner: "Monserrat Xcaret Miranda Olivas"
status: approved
traces_up: ["US-621", "REQ-002", "ADR-011", "DEC-023", "DEC-024", "vault/04_UX_Design/FARO_Storytelling_UX/00_Storytelling_Scope"]
traces_down: ["US-641", "vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity"]
last_reviewed: "2026-09-11"
tags: [ux, dataviz, storytelling, s7, us-621]
---

# Data Visualization Spec — qué dato demuestra la historia

> Documento de Monserrat Xcaret Miranda Olivas. Fija **qué datos y gráficas demuestran** la historia.
> Libertad creativa para reorganizar las visualizaciones, dentro de los datos y endpoints existentes.
> → [[vault/04_UX_Design/FARO_Storytelling_UX/PLAN_TRABAJO]] ·
> [[vault/04_UX_Design/FARO_Storytelling_UX/00_Storytelling_Scope]] ·
> [[vault/03_Architecture/ADRs/ADR-011-rediseno-ux-graficas-nativas]]

**Estado: aprobado** el 2026-09-11 por Marina García del Buey, gate final de UX/UI (plan §7), contra la versión mergeada a `main`. Los cambios posteriores pasan por ella.

> **Evidencia de datos.** Los números y los ejemplos de este documento salen de una consulta a la API
> v1 en **producción** (`https://faro-api-eanzfglvyq-uc.a.run.app`, commit desplegado `457715a`) el
> **10 de septiembre de 2026 a las 18:24 (UTC−06:00)**, con sesión de lectura (`ciudadano`): 34
> llamadas, todas con respuesta 200. La consulta la repite
> [`generar_ejemplos.py`](ejemplos_graficas/generar_ejemplos.py) paso `descargar`; la evidencia cruda
> se guarda **fuera** del repositorio y no se versiona. Donde este documento da un número, dice de qué
> endpoint salió. En la copy del producto ningún conteo va escrito: va `N` y se resuelve en vivo.

---

## 1. Regla de sustento

Cada gráfica de este documento declara el endpoint y los campos que la sostienen. **Si no hay
endpoint, no hay gráfica.** El mapeo verificado está en la §10 del plan y aquí se vuelve a comprobar
campo por campo contra `api/openapi.v1.json`.

Cuando algo falta hay tres salidas y sólo tres (`DEC-024`, `ADR-011` §7):

1. se sostiene con un endpoint actual;
2. se representa con **fixture contractual rotulado como tal** en el propio gráfico;
3. se marca **`SIN_DATO`** explícito.

Nunca se dibuja como si existiera. Las seis peticiones P-01…P-06 del plan están cerradas; lo que
queda fuera se registra en la §8 con su "si se aprueba" y su "mientras tanto".

### 1.1 Lo único que se deriva en Front

Front no inventa métricas. Estas cinco derivaciones son las únicas permitidas, cada una con su dato de
origen, su fórmula y quién la construye:

| Derivación | Dato de origen | Fórmula | Construye |
|---|---|---|---|
| **Nivel de atención** | `indice_riesgo` (`EscuelaOut`, `PrediccionOut`) | alta `>= LINEA_DE_ALERTA` · media `>= RIESGO_ESTABLE` y `< LINEA_DE_ALERTA` · baja `< RIESGO_ESTABLE` | Equipo 5 |
| **Presión de D3 y D4** | `d3`, `d4` (`EscuelaDetalleOut`) | `1 − valor publicado` (ver §4.1) | Equipo 5, en **una sola** función nombrada |
| **Conjunto en riesgo** | `indice_riesgo` de `/escuelas` ordenado desc | corte del lado cliente en `LINEA_DE_ALERTA` (ver §3.4) | Equipo 5 |
| **Top 3** | `driver_dominante` (`EscuelaOut`) del conjunto completo | conteo por driver (ver §5) | Equipo 5 |
| **Evidencia disponible** | `indice_completitud_drivers` | `k = round(indice × 6)` → "k de 6 pistas" | Equipo 5 |

Las dos constantes **se importan, no se teclean**: `LINEA_DE_ALERTA = 0.50` vive en
`src/api/repositorio_gold.py:55` y `RIESGO_ESTABLE = 0.30` en `src/modelos/riesgo.py:76` (crítico de
Estefany Hernández). Un `0.30` o un `0.50` escrito a mano en el frontend es `BUG-058` otra vez. Los
ejemplos de la §7 cumplen la misma regla: el script lee las dos constantes del código fuente.

### 1.2 Definiciones de datos para el glosario

Texto de datos que las gráficas necesitan que el glosario diga (§6 del plan). Es contenido, no
diseño: Oscar y Juan deciden dónde y cómo se muestra.

| Término | Qué debe decir, en lenguaje sencillo |
|---|---|
| **Índice de riesgo** | Un número entre 0 y 1 que traduce la variación de matrícula que el modelo ML-01 proyecta para la escuela en el próximo ciclo. 0.30 corresponde a una escuela que conserva su matrícula y 0.60 a una que perdería 5 % (`src/modelos/riesgo.py`, anclas de la sigmoide). FARO pone la línea de alerta en 0.50, que equivale a perder alrededor de 3.4 % (`src/api/repositorio_gold.py:42-47`). No dice cuántos alumnos perdió la escuela. |
| **Driver** | Cada una de las seis pistas del entorno que FARO revisa: pobreza y rezago, inseguridad, infraestructura escolar, conectividad, estrés hídrico y calidad del aire. |
| **Driver dominante** | El factor que más destaca en esa escuela según el modelo ML-02. Orienta la investigación y la recomendación; **no es la causa** de nada. |
| **Recomendación** | La acción asociada al driver dominante. Hay una por driver; dos escuelas con el mismo riesgo pueden recibir recomendaciones distintas. |
| **Nivel de atención** | Una etiqueta —alta, media o baja— que FARO calcula a partir del índice de riesgo: alta desde 0.50, media desde 0.30, baja por debajo de 0.30. Es un **corte de presentación**. |
| **Nivel de atención ≠ `prioridad`** | Los tableros de respaldo en Superset (DB-09) muestran una columna llamada `prioridad` que viene de Gold y usa otro corte: sólo llama *alta* a partir de 0.60 (`src/modelos/publicar_gold.py:197`). Como ninguna escuela llega a 0.60, **ahí las escuelas de esta historia aparecen como `media`**. Las dos lecturas son correctas según su propia definición; la historia usa el nivel de atención y nunca le dice "prioridad". |
| **`SIN_DATO`** | Una pista que no pudimos verificar para esa escuela. No significa cero ni que el problema no exista. |
| **Evidencia disponible** | Cuántas de las seis pistas tienen dato para esa escuela, por ejemplo "3 de 6". |

Los números 0.30, 0.50 y 0.60 del glosario son **definiciones**, no conteos, y por eso sí pueden ir
escritos; aun así Front los debe tomar de las constantes para que el texto no se desincronice del
cálculo. Cada término puede ofrecer "pregúntale al Asistente FARO" (§4.bis del plan).

---

## 2. Pregunta → dato → gráfica

Una fila por pantalla. La pregunta es la del usuario, no la del analista. La matrícula aparece sólo
en la P2.

| Pantalla | Pregunta que responde | Dato | Endpoint | Gráfica propuesta |
|---|---|---|---|---|
| **P2 — Panorama** | ¿Cuántas escuelas están en riesgo y viven todas la misma situación? | `escuelas_en_riesgo`, `matricula_total`, `variacion_matricula`, `indice_completitud_drivers` (`KpisOut`) · por escuela `cct`, `nombre`, `nivel`, `cve_mun`, `matricula_total`, `indice_riesgo`, `driver_dominante` (`EscuelaOut`) · `d1`…`d6`, `indice_completitud_drivers` (`EscuelaDetalleOut`) · `nombre_municipio` (`MunicipioOut`) | `GET /api/v1/kpis` sin filtros · `GET /api/v1/escuelas?order_by=indice_riesgo&order=desc&size=100` con corte cliente · `GET /api/v1/escuelas/{cct}` × N · `GET /api/v1/municipios/{cve_mun}` | Cifra de revelación `N` + **matriz de casos** N escuelas × 6 drivers (§3) |
| **P3 — Selección** | ¿Qué caso quiero investigar? | `cct`, `nombre`, `nivel`, `indice_riesgo` (`EscuelaOut`) · `nombre_municipio` · nivel de atención (derivado, §1.1) | Los mismos datos ya cargados en la P2; **ninguna llamada nueva** | **Lista de casos** con el índice en número y en una pista 0–1 con la línea de alerta marcada, más la etiqueta de nivel de atención con icono y texto |
| **P4 — Expediente** | ¿Qué factor destaca en esta escuela y qué recomienda FARO? | `nombre`, `nivel`, `sostenimiento`, `d1`…`d6`, `indice_completitud_drivers`, `es_estimado_por_grupo` (`EscuelaDetalleOut`) · `indice_riesgo`, `driver_dominante`, `recomendacion` (`PrediccionOut`) · `contribuciones` (`ExplicacionSHAPOut`) · `nombre_municipio`, `pobreza_pct`, `indice_rezago_social` (`MunicipioOut`, sólo como contexto de D1) | `GET /api/v1/escuelas/{cct}` · `GET /api/v1/predicciones/{cct}` · `GET /api/v1/predicciones/{cct}/explicacion` · `GET /api/v1/municipios/{cve_mun}` | **Barras de presión** D1–D6 en orden fijo, dominante destacado por forma y etiqueta, medidor de evidencia y tarjeta de recomendación; panel SHAP aparte (§4) |
| **P5 — Conclusión** | ¿Qué factores se repiten más entre todas las escuelas en riesgo y qué se recomienda para cada uno? | `driver_dominante` y `cve_mun` (`EscuelaOut`) del **conjunto completo** · `recomendacion` (`PrediccionOut`) · `indice_completitud_drivers` · `escuelas_en_riesgo` (`KpisOut` sin filtros) | Los mismos de la P2, pedidos **sin filtros** aunque el usuario haya filtrado antes | **Top 3** en "k de N escuelas" con **gráfica de unidades** (una casilla por escuela), recomendación por driver, concentración por municipio y cobertura (§5) |
| **P6 — Exploración** | ¿Y las demás escuelas, con mis filtros? | `EscuelaOut` filtrado por `ciclo`, `cve_ent`, `cve_mun`, `nivel` · `KpisOut` filtrado por `ciclo`, `cve_ent`, `cve_mun` (**no acepta `nivel`**) · el expediente de la P4 para la escuela elegida | `GET /api/v1/escuelas?…` · `GET /api/v1/kpis?…` · los de la P4 | **Lista filtrada** con la misma pista de riesgo de la P3, ahora con niveles alta/media/baja por forma y texto; al elegir, el expediente de la P4 sin cambios |

**Lo que dijo la consulta del 10-sep** (producción, 18:24):

| Dato | Valor | De dónde |
|---|---|---|
| Escuelas en riesgo | 7 | `GET /api/v1/kpis` → `escuelas_en_riesgo` |
| Conjunto por corte cliente | 7, en **una** página; coincide con `/kpis` | `GET /api/v1/escuelas?order_by=indice_riesgo&order=desc&size=100` |
| Escuela siguiente, ya fuera | `indice_riesgo` 0.498, justo debajo de la línea | misma página, posición 8 |
| Universo del alcance | 44,114 escuelas · matrícula 6,704,229 · variación −2.9 % · evidencia promedio 3.7 de 6 | `Page.total` de `/escuelas` · `/kpis` |
| Dónde están las 7 | Toluca (5) y Naucalpan de Juárez (2), Estado de México | `cve_mun` + `/municipios/{cve_mun}` |
| Driver dominante | D2 inseguridad en 5 · D4 conectividad en 2 | `driver_dominante` de `EscuelaOut` |
| Evidencia por escuela | **3 de 6** en las 7: hay dato de D1, D2 y D4; **D3, D5 y D6 son `SIN_DATO` en las 7** | `/escuelas/{cct}` |
| Explicación SHAP | 0 de 42 contribuciones con valor (7 escuelas × 6) | `/predicciones/{cct}/explicacion` |
| `es_estimado_por_grupo` | `null` en las 7 | `/escuelas/{cct}` |
| Otras entidades | 0 escuelas en riesgo en Ciudad de México, Nuevo León y Jalisco | `/kpis?cve_ent=…` |

Los valores concretos sirven para **citar la evidencia** en este documento. En la copy del producto
siguen siendo `N` y `k`, porque si cambian el ciclo o el umbral tienen que cambiar solos.

---

## 3. Visualización principal de la Pantalla 2

### 3.1 Qué tiene que hacer evidente

El mensaje central de `00_Storytelling_Scope` §3.5: **todas las escuelas están en riesgo, pero no
todas viven la misma situación.** La gráfica tiene que mostrar las dos mitades a la vez: lo que
comparten (el riesgo) y lo que las distingue (qué pista destaca en cada una).

### 3.2 La forma: matriz de casos

Una retícula con **una fila por escuela en riesgo** y **una columna por driver**, en el orden fijo
D1 → D6, flanqueada por los atributos del caso.

| Zona | Contenido | Dato |
|---|---|---|
| Izquierda | Nombre de la escuela; debajo, municipio, nivel y CCT | `nombre`, `nombre_municipio`, `nivel`, `cct` |
| Izquierda | Índice de riesgo en número (3 decimales) y nivel de atención con icono + texto | `indice_riesgo`; nivel derivado |
| Izquierda | Matrícula del ciclo — **única pantalla de la historia donde aparece** | `matricula_total` (`EscuelaOut`) |
| Centro | Seis celdas D1…D6 con la **presión** del driver: tono de un solo color, más oscuro con más presión, y el valor con dos decimales dentro de la celda | `d1`…`d6` orientados (§4.1) |
| Centro | La celda del **driver dominante** lleva contorno grueso, el marcador ▲ y la palabra "dominante" | `driver_dominante` (`EscuelaOut`) |
| Centro | Una celda `SIN_DATO` va rayada, con el texto "sin dato"; nunca en blanco ni en cero | `d_i = null` |
| Derecha | Evidencia disponible, "k de 6", en texto y seis casillas llenas o rayadas | `indice_completitud_drivers`, `d_i` |

Las zonas describen **contenido, no posición**: dónde va cada bloque, su tamaño y su orden en la
página los decide Juan (§7.5). Lo que no cambia es qué dato aparece y cómo se lee.

**Orden de filas:** `indice_riesgo` descendente y, entre valores iguales, por nombre y CCT. La API no
garantiza un orden estable entre empates, y los empates son frecuentes: en la consulta, dos escuelas
comparten 0.572 y tres comparten 0.515. Encima de la matriz, la frase de revelación de
`00_Storytelling_Scope` §3.4 con `N` resuelto en vivo y los tres datos del alcance (matrícula,
variación agregada y evidencia promedio).

**Cómo se lee.** La columna de riesgo dice "todas están del mismo lado de la línea"; los ▲, que caen
en columnas distintas, dicen "no les pasa lo mismo". Ese contraste es el mensaje.

**Lo que muestra con el dato real** ([ejemplo P2](ejemplos_graficas/P2_matriz_casos.png)): las siete
escuelas están entre 0.515 y 0.572; en cinco destaca la inseguridad (D2) y en dos la falta de
conectividad (D4). El caso más claro está en Toluca: sus cinco escuelas comparten la presión de
pobreza (0.06) y de inseguridad (0.47) porque son valores del municipio, y **lo único que las separa
es la conectividad que registra cada escuela** — con conectividad completa destaca D2; con
conectividad nula o a medias destaca D4. Es el diferenciador del proyecto visto en una sola retícula: mismo
municipio, mismo riesgo, distinta situación, distinta recomendación.

> **Dato para QA y el Equipo 5.** Dos parejas comparten nombre y coordenadas pero son CCT distintos, y
> tienen conectividad registrada distinta: `15EJN4151O` (0.00 → D4) y `15EJN0104C` (1.00 → D2), ambas
> "LIC. AGUSTIN GONZALEZ"; `15EES1468A` (0.50 → D4) y `15EPR0628Y` (1.00 → D2), ambas "SOR JUANA INES
> DE LA CRUZ". El dato no dice por qué. La matriz lo deja visible con la CCT en cada fila y el
> expediente muestra el valor publicado de D4, para que nadie lo lea como una fila duplicada.

**Copy dinámica, no fija.** La segunda frase se construye con el dato. Si los dominantes se reparten
en dos o más drivers: *"Comparten el riesgo, pero no la situación: el factor que más destaca cambia de
una escuela a otra."* Si todas tuvieran el mismo dominante, esa frase sería falsa y se sustituye por
*"En las N escuelas destaca el mismo factor: {driver}. Sus otras pistas sí difieren."* El texto nunca
contradice a la matriz que tiene debajo.

### 3.3 Por qué ésta y no otra

1. **Es la única forma que muestra las dos mitades del mensaje en una sola vista.** Una gráfica de
   riesgo muestra la igualdad; una de drivers, la diferencia. La matriz pone ambas en la misma fila.
2. **N es pequeño, así que cada caso cabe completo.** No hace falta agregar ni promediar: el usuario
   ve cada escuela, y la agregación honesta se deja para la P5.
3. **Cada fila es un caso que se puede abrir.** La P3 y la P4 salen de la misma fila: la matriz es a
   la vez panorama y puerta.
4. **Conserva los números.** La retícula es una tabla con una capa visual encima, no un sustituto de
   la tabla: el valor se lee en la celda, y la tabla gemela accesible tiene la misma estructura.

**Alternativas descartadas:**

| Alternativa | Por qué no |
|---|---|
| Mapa de puntos o coroplético | Ningún endpoint expone geometría y `latitud`/`longitud` sin base cartográfica no se leen. Además, *dónde* no responde *qué situación*: las siete están en dos municipios. La línea base lo confirma: el coroplético de DB-02 sale vacío (§7.3) |
| Barras del índice de riesgo por escuela | Muestra sólo la mitad "todas en riesgo", y un eje recortado exageraría diferencias mínimas (de 0.515 a 0.572) |
| Un radar por escuela | N radares no se comparan entre sí, el área exagera y un `SIN_DATO` rompe el polígono: con D3, D5 y D6 vacíos, la mitad de cada radar estaría rota |
| Barras apiladas con las contribuciones SHAP | `contribuciones` está en `SIN_DATO` en producción (§4.4), y SHAP explica al modelo, no la situación de la escuela |
| Sankey riesgo → driver | Con N pequeño esconde los casos individuales detrás de flujos, y no hay etapas intermedias reales que mostrar |
| Tabla de números sola | Es exacta, pero el patrón no salta; es lo que hacían DB-03 y DB-08 (§7.3) |
| Seis gráficas, una por driver | Obliga a comparar entre gráficas separadas; es lo que hace DB-04 (§7.3). La matriz pone las seis en una retícula |

### 3.4 De dónde sale el conjunto, y lo que cuesta

`/escuelas` **no filtra por `indice_riesgo`**, pero sí ordena por él, así que **no hace falta
recorrer el universo**: una sola llamada trae a las de mayor riesgo y se corta ahí.

1. **Una llamada:** `GET /api/v1/escuelas?order_by=indice_riesgo&order=desc&size=100` (`size`
   máximo 100).
2. Se toman escuelas mientras `indice_riesgo >= LINEA_DE_ALERTA` y se corta en la primera que queda
   por debajo. La API ordena con `NULLS LAST` (`src/api/repositorio_gold.py:208-211`), así que un
   valor nulo tampoco se cuela antes del corte. **Guarda:** sólo si las 100 de la página estuvieran
   en riesgo se pide `page=2`; con los datos de hoy no ocurre (7 de 100).
3. El tamaño del conjunto se compara con `GET /api/v1/kpis` → `escuelas_en_riesgo`. **Deben
   coincidir** (los dos usan el ciclo más reciente y el mismo corte), y en la consulta del 10-sep
   coincidieron: 7 y 7. Si no coinciden, la P2 no inventa cuál tiene razón: muestra el conteo de
   `/kpis`, marca la discrepancia y QA la registra.

**Costo.** El conjunto y el Top 3 cuestan **dos llamadas** (`/kpis` y una página de `/escuelas`).
Lo caro es la matriz: `EscuelaOut` no trae `d1`…`d6` ni `indice_completitud_drivers`, así que hace
falta **una llamada a `/escuelas/{cct}` por fila**, más una a `/municipios/{cve_mun}` por municipio
distinto. Total de la P2: `2 + N (/escuelas/{cct}) + M (/municipios)`; hoy, 2 + 7 + 2 = 11 llamadas.
Consecuencias de diseño para el Equipo 5:

- La columna de riesgo, la de matrícula y los ▲ salen de la primera llamada: se pintan de inmediato.
- Las celdas D1…D6 y la evidencia llegan fila por fila; mientras cargan, la fila muestra su propio
  estado de carga, **nunca** celdas vacías que parezcan `SIN_DATO` ni ceros.
- Si N creciera (otro ciclo u otro corte) más allá de unas 25 filas, la matriz se pagina de 10 en 10
  y las filas se piden al hacerse visibles. El Top 3 de la P5 no depende de estas llamadas.

**Filtros de la P2.** Son "limitados" (plan §5). Dos restricciones que Oscar necesita: `/kpis`
acepta `cve_ent`, `cve_mun` y `ciclo`, **pero no `nivel`**; y hoy las siete escuelas están en una sola
entidad, así que un filtro por cualquier otra deja la matriz vacía. Recomendación: la revelación es
siempre el total sin filtros, y los filtros de la P2 sólo atenúan filas de la matriz.

---

## 4. Gráfica comparativa de los 6 drivers (Pantalla 4)

### 4.1 Qué es cada driver, verificado contra el pipeline

Antes de dibujar hay que saber qué mide cada columna. Esto está verificado en el modelo que lee la API
(`dbt/models/gold/fact_escuela_ciclo.sql`), y cambia la forma de la gráfica:

| Driver | Campo | Grano | Qué mide | Dirección publicada | En la gráfica |
|---|---|---|---|---|---|
| D1 Pobreza y rezago | `d1` | **municipio** | Índice de rezago social de CONEVAL, normalizado min-max entre los municipios observados (`:146-160`) | sube con más rezago | tal cual |
| D2 Inseguridad | `d2` | **municipio** | Delitos por 100 000 habitantes por mes (SESNSP ÷ CONAPO), min-max (`:205-237`) | sube con más delitos | tal cual |
| D3 Infraestructura | `d3` | escuela | Proporción de servicios **presentes**: drenaje, electricidad, sanitarios (CEMABE 2013). Es un promedio de hasta tres indicadores sí/no, así que toma pocos valores | **sube cuando la escuela está mejor** | **falta de infraestructura** = `1 − d3` |
| D4 Conectividad | `d4` | escuela | Proporción de servicios **presentes**: internet y computadoras (CEMABE 2013). Promedio de dos indicadores sí/no: 0, 0.5 o 1 | **sube cuando la escuela está mejor** | **falta de conectividad** = `1 − d4` |
| D5 Estrés hídrico | `d5` | — | **Sin fuente integrada: `null` para todas las escuelas** (`:359-360`) | — | `SIN_DATO` |
| D6 Calidad del aire | `d6` | escuela | PM2.5 interpolado desde estaciones SINAICA a 15 km o menos, min-max (`:249-337`) | sube con peor aire | tal cual; `SIN_DATO` sin estación cercana |

Tres consecuencias:

1. **D3 y D4 se orientan.** Dibujados tal cual, un dominante de conectividad —escuela *sin*
   internet— sería la barra **más corta** de la gráfica y el resaltado contradiría a la vista. El
   pipeline ya resuelve esto: para elegir el dominante usa `1 − d3` y `1 − d4` (regla 4 de
   `dbt/models/gold/features_escuela.sql:385-410`). La gráfica usa **la misma transformación**, así
   que no es una métrica nueva: es leer el dato como lo lee el modelo. El valor publicado se conserva
   como etiqueta secundaria ("servicios presentes: 1.00"). En la consulta, el dominante de ML-02
   **coincidió con la barra más larga en las siete escuelas**.
2. **Los valores son posiciones relativas, no porcentajes.** `0.47` en D2 significa "a media altura
   del rango de delitos por habitante entre los municipios observados", no "47 % de inseguridad". El
   eje se rotula "0 = menor presión observada · 1 = mayor presión observada" y la copy nunca escribe
   `%` junto a un driver.
3. **D1 y D2 son del municipio.** Todas las escuelas de un municipio comparten esos dos valores; la
   gráfica lo dice con la nota "valor municipal" para que nadie lea que una escuela es más pobre que su
   vecina.

### 4.2 La forma: barras de presión en orden fijo

- **Seis barras horizontales** sobre un eje común 0–1, siempre en el orden D1 → D6. **No se
  reordenan por valor**: el ojo aprende dónde está cada pista y la P2 usa el mismo orden en sus
  columnas, así que pasar de la matriz al expediente no obliga a releer.
- El valor va al final de cada barra con dos decimales. Rejilla mínima: marcas en 0, 0.5 y 1.
- **Todas las barras llevan el mismo tono.** El color no codifica identidad de driver: la identidad la
  da la etiqueta de la fila. Así el único acento de la gráfica es el dominante.
- Un **cero real** se dibuja como una línea mínima con su "0.00" (en la consulta: la falta de
  conectividad de MIXCOAC, cuyo registro de conectividad está completo, `d4 = 1.00`). No se parece en
  nada al rayado de `SIN_DATO`.

**El driver dominante** (`driver_dominante` de `PrediccionOut`) se destaca con **cuatro señales, no
sólo color**: barra en el color de **acento** —nunca un paso de la rampa, que ya codifica magnitud;
en los ejemplos es tinta neutra y el acento definitivo lo elige Juan—, marcador ▲ junto a la
etiqueta, etiqueta en negritas y la leyenda "Driver dominante" junto a la barra (dentro de ella, en
blanco, cuando la barra llega al borde). Debajo va una frase fija: *"El driver dominante es el factor que más destaca en esta escuela
según el modelo ML-02. Orienta la investigación y la recomendación; no es la causa."*

**Contexto territorial, sólo para D1.** `MunicipioOut` expone `pobreza_pct` e `indice_rezago_social`.
Es la **única** comparación contra el territorio que se sostiene hoy (`00_Storytelling_Scope` §4.2):
bajo la gráfica va una línea de contexto, *"En {municipio}, {pobreza_pct} % de la población vive en
pobreza (CONEVAL)."* Hace falta además aclarar qué mide la barra, porque el dato real lo exige: en
Toluca la presión de D1 es **0.06** y la pobreza es **51.8 %**. No se contradicen —la barra es el
rezago social relativo entre municipios, no el porcentaje de pobreza—, y la línea de contexto lo dice
así. No existe un promedio municipal de D2…D6, así que para esas cinco pistas no se escribe ninguna
comparación escuela contra municipio.

### 4.3 Cómo se dibuja un driver `SIN_DATO`

- **La fila no desaparece.** Las seis pistas siempre están, en su lugar (criterio 6 del plan).
- **Sin barra y sin `0.00`.** La pista se rellena de punta a punta con rayado a 45° y lleva el texto
  "SIN DATO — pista que no pudimos verificar" y, debajo, el motivo. Un cero es una línea mínima con su
  número; el rayado a todo lo ancho no se puede confundir con eso.
- **Motivo corto, del dato:** D5 → "aún no hay fuente de estrés hídrico integrada"; D6 → "no hay
  estación de calidad del aire a 15 km o menos"; D3 y D4 → "sin registro en el censo CEMABE"; D1 y D2
  → "sin dato para su municipio".
- **Nunca puede ser el dominante**: el pipeline excluye `SIN_DATO` al elegirlo
  (`features_escuela.sql:379`).
- Encima de la gráfica, el **medidor de evidencia**: *"Evidencia disponible: 3 de 6 pistas"* en texto
  y seis casillas, llenas o rayadas en el mismo orden D1…D6.

**No es un caso de borde: es el caso normal.** En las siete escuelas en riesgo hay **tres filas
rayadas** —D3, D5 y D6—, así que el diseño se valida con la mitad de la gráfica en `SIN_DATO`.

### 4.4 La explicación del modelo va aparte

`GET /api/v1/predicciones/{cct}/explicacion` devuelve `contribuciones` `{"D1": número|null, …}`.
Dos reglas:

1. **Nunca se mezcla con las barras de presión.** La presión describe la situación de la escuela;
   la contribución SHAP describe cuánto pesó cada driver en el cálculo del modelo. Son preguntas
   distintas y van en paneles distintos.
2. **`null` es `SIN_DATO`, no cero**, igual que en la §4.3.

**Estado en producción: 0 de 42 contribuciones con valor.** Las columnas `shap_d1…shap_d6` no están
pobladas (`vault/13_Reports/Cierre_Proyecto_2026-09-08.md:117`; Equipo 4, `US-631`). Mientras tanto
el panel muestra un solo estado: *"La explicación del modelo para esta escuela aún no está disponible
(SIN_DATO)."* Cuando haya datos, la forma es una barra divergente por driver alrededor de cero, en el
mismo orden D1…D6, con los `null` rayados.

### 4.5 Accesibilidad

WCAG 2.1 AA (`ADR-011` §4) y [[vault/04_UX_Design/Accessibility]]: texto con contraste ≥ 4.5:1 y
marcas ≥ 3:1 contra el fondo; ninguna información sólo por color (dominante: forma + etiqueta;
`SIN_DATO`: rayado + texto; nivel de atención: icono ▲ ■ ● + texto); cada gráfica tiene una **tabla
gemela** accesible con los mismos valores; el foco de teclado muestra lo mismo que el *hover*; sin
animación que no respete `prefers-reduced-motion`. El script de la §7 mide el contraste de su paleta
y se detiene si alguna regla falla.

---

## 5. Cómo se obtiene y comunica el Top 3

Se calcula en Front, **sobre el conjunto completo de escuelas en riesgo**, sin importar los filtros
que el usuario haya usado antes. No existe ningún endpoint que devuelva el Top 3 agregado. La función
`top3()` de [`generar_ejemplos.py`](ejemplos_graficas/generar_ejemplos.py) es la versión ejecutable de
esta mecánica.

### 5.1 La mecánica, paso a paso

1. `GET /api/v1/kpis` **sin parámetros** → `N = escuelas_en_riesgo`.
2. `GET /api/v1/escuelas?order_by=indice_riesgo&order=desc&size=100`, **sin `cve_ent`, `cve_mun` ni
   `nivel`**, con el corte de la §3.4. Si la P2 ya lo cargó sin filtros, se reutiliza.
3. Si el tamaño del conjunto no es `N`, el Top 3 **no se publica**: se muestra "no pudimos confirmar
   el conjunto completo" y QA lo registra. No se elige uno de los dos números.
4. Para cada escuela del conjunto se toma `driver_dominante` de `EscuelaOut`: **no hace falta ninguna
   llamada por escuela**. Un `driver_dominante` nulo se cuenta aparte como "sin driver dominante" y no
   se reparte entre los demás.
5. Se cuenta `k_d` = número de escuelas con dominante `d`, para D1…D6, incluidos los ceros.
6. Se ordena por `k_d` descendente y se asigna **rango con empates compartidos** (1, 2, 2, 4):
   - entran al Top 3 todos los drivers con rango ≤ 3 y `k_d > 0`, así que un empate en el tercer lugar
     muestra **cuatro** drivers en vez de elegir uno a ciegas;
   - los empatados llevan el mismo número de lugar y la palabra "empate";
   - dentro de un empate el orden visual es D1 → D6 y se dice que es el orden del catálogo, no de
     importancia;
   - un driver con `k_d = 0` nunca entra; si menos de tres tienen `k_d > 0`, se muestran los que hay y
     la copy lo dice.
7. Para cada driver del Top 3, `recomendacion` sale de `GET /api/v1/predicciones/{cct}` de cualquier
   escuela del grupo: es un texto fijo por driver (`src/modelos/recomendaciones.py:5-12`), así que
   Front **no lo teclea**.

**Resultado con la consulta del 10-sep:** 1.º D2 inseguridad del entorno, 5 de 7 escuelas; 2.º D4
conectividad digital, 2 de 7. Sin empates y sin escuelas sin dominante. **Sólo dos drivers aparecen
como dominantes**, y hay que decir por qué sin maquillarlo: en las siete escuelas sólo hay dato de D1,
D2 y D4, y D1 nunca destaca (su presión es 0.04 o 0.06). El Top 3 de hoy es un Top 2 elegido entre
tres pistas verificables; la pantalla lo dice con la copy del paso 6 y la nota de cobertura de la
§5.2. Ver [ejemplo P5](ejemplos_graficas/P5_conclusion_top3.png).

### 5.2 Cómo se expresa

- **Conteo primero, proporción después:** *"{k} de N escuelas (p %)"*, con `p` redondeado a entero.
  Con N pequeño la proporción exagera —hoy una escuela vale 14 puntos—, por eso no va sola.
- **Gráfica de unidades:** N casillas, una por escuela, agrupadas por driver dominante y separadas por
  posición, no por color. Cada casilla es una escuela real, con su CCT, y se puede señalar para ver su
  nombre. Las escuelas sin driver dominante van en su propio grupo, rayadas.
- Junto a cada grupo, la recomendación y la problemática **sólo con datos**, por ejemplo *"Presión de
  inseguridad entre 0.45 y 0.47 (0 = menor observada, 1 = mayor); es un valor del municipio."* Nunca
  *"pierden matrícula por…"*.
- **Concentración por municipio** (`00_Storytelling_Scope` §6): conteo de `cve_mun` en el conjunto,
  con nombre de `/municipios`. Hoy: *"Toluca (5) · Naucalpan de Juárez (2), en Estado de México."*
- **Cobertura**, con la lista de pistas que no se pudieron verificar en ninguna escuela, calculada del
  dato: *"Las escuelas tienen dato para 3 de 6 pistas. Infraestructura escolar, estrés hídrico y
  calidad del aire no pudieron verificarse en ninguna: que no aparezcan aquí no significa que no sean
  un problema."*
- La leyenda obligatoria (plan §5), visible y sin tooltip: **"Esta conclusión se calcula sobre el
  conjunto completo de escuelas en riesgo, independientemente de los filtros utilizados durante la
  exploración."**
- **No se grafica la distribución de niveles de atención.** El conjunto en riesgo se define con el
  mismo corte que "atención alta" (`LINEA_DE_ALERTA`), así que el 100 % es *alta* por construcción: la
  gráfica no aportaría nada. Se dice en una línea en vez de dibujarlo.
- Un solo CTA principal y sin drill-down (criterio 13 del plan).

---

## 6. Tratamiento de SIN_DATO y cobertura parcial

- **`indice_completitud_drivers`** es la fracción de drivers con cobertura `OK` de la escuela
  (`fact_escuela_ciclo.sql:378-385`, suma de seis banderas ÷ 6). Se muestra como "k de 6 pistas"
  con `k = round(indice × 6)`, en texto y seis casillas, en P2, P4 y P6. Agregado, `/kpis` devuelve
  el promedio: hoy 0.619, que se muestra como "en promedio, 3.7 de 6 pistas".
- **D5 es `SIN_DATO` para todas las escuelas**, no parcial: la columna existe y viene `null`
  (`fact_escuela_ciclo.sql:359-360`). Por eso **la evidencia máxima posible hoy es 5 de 6**. Se dice
  así, no se esconde.
- **D6** es `SIN_DATO` donde no hay estación SINAICA a 15 km o menos. **D3** lo es donde el censo
  CEMABE no registra servicios. En las siete escuelas en riesgo faltan los tres, y cada una llega a
  **3 de 6**: es la cobertura con la que se construyó la conclusión, y la P5 lo dice.
- **`es_estimado_por_grupo`** existe en el contrato (`EscuelaDetalleOut`) pero **la API siempre lo
  devuelve `null`**: la columna todavía no existe en Gold (`src/api/v1/gold.py:78-80`, pendiente de
  Diana Alvarez y Héctor Morales). Confirmado en producción: `null` en las siete. Se muestra, porque
  existe, como *"Estimación por grupo: sin dato"* junto al índice. **No** se muestra como "no", que
  sería afirmar algo que el dato no dice. Importa más de lo que parece: el índice **se repite
  exactamente** entre escuelas con el mismo perfil observado (en Toluca, las tres con conectividad
  completa tienen 0.5153; en Ciudad de México, las 20 de mayor índice comparten 0.4702), y ese campo
  es el que diría si el valor es propio o de grupo.
- **`variacion_matricula`** de `/kpis` cae a `0.0` cuando no hay ciclo anterior para el filtro
  (`src/api/repositorio_gold.py:381`): un cero ahí no distingue "no cambió" de "no hay dato". La P2
  la usa sólo sin filtros; con filtros no se muestra un `0.0` exacto sin la nota "puede ser falta de
  ciclo anterior". Aviso a Christian Ruiz, dueño de `src/api/**`.
- **Lenguaje:** la falta de dato es *"una pista que no pudimos verificar"*, nunca *"no hay problema"*
  ni *"0"*. `SIN_DATO` no se excluye en silencio de ningún denominador: si una cuenta lo deja fuera, lo
  dice.

---

## 7. Ejemplos de visualizaciones

### 7.1 Los archivos

En [`ejemplos_graficas/`](ejemplos_graficas/generar_ejemplos.py), en PNG (150 dpi) y SVG con el
texto editable. Demuestran **forma y lectura del dato, no identidad visual**: paleta neutra y
provisional (grises y un solo tono para la magnitud), declarada en el pie de cada imagen. La identidad
la define [[vault/04_UX_Design/FARO_Storytelling_UX/03_Visual_Identity]] y el formato de entrega lo
decide Juan, que es quien integra: si pide otro, el script lo regenera. `mockups/` es de Juan y no se
toca.

| Pantalla | Archivo | Qué demuestra |
|---|---|---|
| P2 | [P2_matriz_casos.png](ejemplos_graficas/P2_matriz_casos.png) · [SVG](ejemplos_graficas/P2_matriz_casos.svg) | La matriz de casos: riesgo compartido, ▲ en columnas distintas, D3/D5/D6 rayados, evidencia "3 de 6" |
| P3 | [P3_seleccion_caso.png](ejemplos_graficas/P3_seleccion_caso.png) · [SVG](ejemplos_graficas/P3_seleccion_caso.svg) | Lista con índice en número y pista 0–1 con la línea de alerta; empates juntos y en orden alfabético |
| P4 | [P4_expediente_15EJN4151O.png](ejemplos_graficas/P4_expediente_15EJN4151O.png) · [SVG](ejemplos_graficas/P4_expediente_15EJN4151O.svg) | Expediente con dominante D4 (falta de conectividad 1.00, dentro de la barra) |
| P4 | [P4_expediente_15DJN1794N.png](ejemplos_graficas/P4_expediente_15DJN1794N.png) · [SVG](ejemplos_graficas/P4_expediente_15DJN1794N.svg) | Misma ciudad, mismo nivel y mismo rango de riesgo, otro dominante (D2) y otra recomendación; un cero real de D4 junto a tres `SIN_DATO` |
| P5 | [P5_conclusion_top3.png](ejemplos_graficas/P5_conclusion_top3.png) · [SVG](ejemplos_graficas/P5_conclusion_top3.svg) | Top con "k de N", gráfica de unidades con CCT, recomendación, concentración, cobertura y la leyenda obligatoria |
| P6 | [P6_exploracion.png](ejemplos_graficas/P6_exploracion.png) · [SVG](ejemplos_graficas/P6_exploracion.svg) | Lista filtrada (Nuevo León, filtro de ejemplo) con niveles por forma y texto, y los indicadores del filtro |

Los dos expedientes P4 los elige el script con una regla fija —mismo municipio y nivel, dominante
distinto—, no a mano. La entidad de la P6 también: la de más índices distintos fuera de la entidad de
los casos.

Todas las imágenes llevan en el pie la fuente (endpoints y campos), la fecha y el commit de la
consulta, los cortes con su archivo y la advertencia de paleta provisional. En la copy de los ejemplos
los conteos van como `N`; los valores dibujados son los que devolvió la API.

**Contraste medido por el script** (WCAG 2.1 AA): tinta 17.4:1 · tinta secundaria 8.6:1 · barra
4.7:1 · barra dominante 11.8:1 · rayado de `SIN_DATO` 4.7:1 · número en celda, peor caso 4.5:1.

La carpeta tiene su propio índice,
[[vault/04_UX_Design/FARO_Storytelling_UX/ejemplos_graficas/_index]], y en `referencias/` están las
cinco referencias de forma de Monserrat, evaluadas en la §7.4.

### 7.2 Cómo se regeneran

```bash
python vault/04_UX_Design/FARO_Storytelling_UX/ejemplos_graficas/generar_ejemplos.py descargar
python vault/04_UX_Design/FARO_Storytelling_UX/ejemplos_graficas/generar_ejemplos.py graficar
```

`descargar` usa sólo la biblioteca estándar y pide el `access_token` con entrada oculta (se obtiene
en `/api/v1/auth/login`); nunca lo imprime ni lo escribe. La evidencia queda en
`%TEMP%/faro_evidencia_us621/`, fuera del repositorio. `graficar` necesita `matplotlib==3.11.1`
(`requirements/celula-3.txt`).

### 7.3 Qué mejora respecto a los tableros actuales

Contra las capturas versionadas de Superset en `vault/04_UX_Design/capturas/` (db01…db10), que son
la línea base de la revisión del 9-sep. Las capturas muestran un corte de 4,263 escuelas, no el
universo de producción; lo que se compara es la **forma**, no las cifras.

| Pantalla | Qué había (captura) | Qué cambia |
|---|---|---|
| P2 | DB-01 y DB-02: tarjetas apiladas sin historia; KPI-04 en "No data" con el subtítulo viejo "Índice ≥ 0.6"; coroplético vacío; mapa de puntos sin lectura de riesgo; "Driver dominante" como una sola barra "Sin recomendación" | Una revelación con `N` en vivo y una matriz que muestra en la misma vista el riesgo compartido y la situación distinta; los huecos se ven rayados en lugar de vaciar la gráfica |
| P3 | DB-09 "Escuelas a intervenir" y el ranking de DB-02, con el índice en `N/A` | Cada caso con su índice en número, su posición contra la línea de alerta y su nivel de atención con forma y texto |
| P4 | DB-03: drivers en tabla cruda con decimales largos (`0.0392001632…`) y recomendación en `N/A`; DB-04: seis gráficas separadas, una por driver, varias vacías | Una sola gráfica con las seis pistas en un eje común y orientado, el dominante con cuatro señales, cada `SIN_DATO` con su motivo y la recomendación como tarjeta |
| P5 | DB-01 y DB-09: una barra "SIN_DATO" o "Sin recomendación" y un pastel de prioridad `<NULL>` | Un Top contado sobre el conjunto completo, con cada escuela visible, su recomendación, su cobertura y la leyenda obligatoria; sin la columna `prioridad` |
| P6 | DB-08: pivote de números sin lectura, pastel OK/SIN_DATO y detalle escuela × driver en `N/A` | La misma lista y el mismo expediente de la historia, con los filtros obligatorios y el nivel de atención por fila |
| Todas | DB-07 contaba `SIN_DATO` sólo agregado (barras de 100 % por driver) y su mapa de vacíos salía como mapamundi | `SIN_DATO` visible en cada escuela y en cada pista, con el motivo, y la evidencia "k de 6" junto al dato |

### 7.4 Referencias de forma de Monserrat

Cinco pantallas de referencia en `ejemplos_graficas/referencias/`, con su nota de autora
[[vault/04_UX_Design/FARO_Storytelling_UX/ejemplos_graficas/referencias/LEER_PRIMERO]]. Fijan la
forma de lectura de cada pantalla y están construidas con **valores de fixture**
(`tests/fixtures/features_escuela_mock.csv`): no son hallazgos, y los números que muestran no son los
de producción. Se revisaron contra el contrato con la regla de la §1: lo que se sostiene se adopta; lo
que no, se dice y se propone la forma más cercana que sí se sostiene.

| Referencia | Qué fija y se adopta | Qué no se sostiene tal cual, y la forma más cercana |
|---|---|---|
| [02_Panorama](ejemplos_graficas/referencias/02_Panorama.png) | Revelación con `N`; tarjetas de matrícula, variación agregada con flecha y signo del dato, y evidencia promedio en barra continua; matriz escuelas × 6 drivers con dominante por contorno y `s/d` rayado; filtros limitados al universo de los N casos; "ver los mismos datos como tabla"; un CTA hacia la selección | **D3 y D4 van en valor publicado**, así que las celdas más oscuras son las escuelas *mejor* servidas: se leen como falta (`1 − valor`, §4.1). **La tarjeta de evidencia dice que D5 y D6 tienen "cobertura parcial por diseño"**: en producción D5 es `SIN_DATO` en todas las escuelas, y en las siete en riesgo faltan además D3 y D6; la copy correcta es la de la §6. **D5 aparece con valores**: vienen del fixture; en producción esa columna va rayada completa |
| [03_Seleccion_de_caso](ejemplos_graficas/referencias/03_Seleccion_de_caso.png) | Coincide con la §2: índice en número, pista con 0.30 y la línea de alerta, nivel con icono y texto, empates juntos en orden alfabético | Se sostiene completa, con los datos ya cargados en la P2 |
| [04_Expediente](ejemplos_graficas/referencias/04_Expediente.png) | Seis pistas en barras sobre un eje común, dominante con acento, `SIN_DATO` rayado, medidor de muescas "k de 6", recomendación con la aclaración de no causalidad, regreso a los casos y avance a la conclusión | **La frase "la pista dominante es la que más pesa en la predicción, no la de valor más alto" es incorrecta**: el dominante es la salida de ML-02, que aprende a señalar la pista con más presión orientada (`features_escuela.sql:371-418`), y en producción coincidió con la barra más larga en las siete. Lo que pesa en la predicción es SHAP, hoy `SIN_DATO`. La diferencia que la frase intenta explicar desaparece al orientar D3/D4 (§4.1). **D3 y D4 en valor publicado**: igual que en la 02. **Ubicación:** el mapa usa `superset/assets/geojson/municipios_scope.geojson`, que la API no expone; queda como recorte de la §8.1 y, mientras tanto, municipio y entidad en texto. **Rezago del municipio contra un "promedio estatal":** el índice de CONEVAL es estandarizado y aquí es negativo (Naucalpan −1.22, Toluca −1.06), así que una barra rellena desde cero lo dibuja al revés; y el promedio estatal no existe en la API, habría que calcularlo en Front desde `GET /api/v1/municipios?cve_ent=…` (dos llamadas para el Estado de México). La forma más cercana que se sostiene es una franja con todos los municipios de la entidad sobre el eje del índice, el de la escuela marcado y el promedio simple como marca declarada. Entra a las derivaciones de la §1.1 sólo con visto bueno de Marina; mientras tanto, la línea de contexto con `pobreza_pct` de la §4.2 |
| [05_Conclusion](ejemplos_graficas/referencias/05_Conclusion.png) | Banner "cómo se calcula" con el conjunto completo; tarjetas de casos, pistas evaluadas, evidencia en muescas (x de 42) y municipios; Top con tarjeta de empate "sin tercer lugar único" —la misma regla de la §5.1—; tabla de las seis pistas con "domina en" y "verificada en", incluidos los ceros; "lo que no podemos afirmar"; un solo CTA | **La copy lleva conteos tecleados** ("3 de las 7", "36 de 42", "6" municipios, "7 de 7"): en los mockups van como `N` y `k`. **El resultado es del fixture** (D1 primero, D5 y D6 empatados): en producción son D2 (5) y D4 (2), y D5 no puede ser dominante. **"Verificada en" es un conteo entero x de y**: por la regla 6 de la propia nota va en muescas, no en barra; y necesita `d1…d6` de cada escuela, o sea las N llamadas que ya hace la P2 |
| [06_Explorador](ejemplos_graficas/referencias/06_Explorador.png) | Filtros de ciclo, entidad, municipio y nivel; pop-up único de primera vez; "N escuelas encontradas" (`Page.total`); orden por índice; niveles alta, media y baja con icono y texto; paginación de 50 | Se sostiene completa. El filtro de nivel no llega a `/kpis` (§8.1) |

Las cinco imágenes no llevan el rótulo de fixture dentro del dibujo; lo llevan la carpeta, la nota y
esta tabla. Si alguna se reutiliza fuera de este paquete, tiene que llevarlo en la propia imagen
(`DEC-024`).

### 7.5 Qué decide Juan y qué no se mueve

**Juan Carlos Macías tiene libertad total sobre la maquetación y la identidad.** Los ejemplos de la
§7.1 y las referencias de la §7.4 son bocetos de lectura, no maquetas: puede reacomodar la posición
de tarjetas, gráficas y textos; cambiar la jerarquía, el tamaño y el orden de los bloques en la
página; y decidir colores, tipografías, tamaños de letra, iconografía, componentes, espaciado y
acabado. Nada de este documento fija una posición en pantalla.

Lo que **no** se mueve es la lectura del dato:

1. **Qué dato va en cada pantalla** (§2) y de qué endpoint sale. Un bloque se puede reubicar dentro
   de su pantalla, no quitar ni pasar a otra; la matrícula sólo aparece en la P2.
2. **Un solo tono para la magnitud**, en pasos discretos; el dominante con contorno o acento, **nunca
   un paso de la rampa**; nada codificado sólo por color. WCAG 2.1 AA: texto ≥ 4.5:1 y marcas ≥ 3:1.
3. **`SIN_DATO` con tratamiento propio**, idéntico en todas las pantallas, distinto de cualquier paso
   de la rampa y de un cero.
4. **D1…D6 siempre en el mismo orden**; D3 y D4 leídos como falta; el eje de presión rotulado
   "0 = menor observada · 1 = mayor observada", sin `%`.
5. **Las barras terminan en el valor** y parten de un cero con sentido; los conteos enteros "x de y"
   van en muescas.
6. **Los conteos de la copy son `N` y `k`**, resueltos en vivo; los cortes se importan (§1.1).
7. En la P5, la leyenda del conjunto completo visible y **un solo CTA**.
8. **Sin causalidad**; "nivel de atención", nunca "prioridad"; **Asistente FARO**.

Lo que Juan tiene que definir para que la lectura funcione (de la nota de las referencias): una rampa
de un solo tono en cinco pasos, un color de acento para el dominante y el Top, un gris de contexto,
una textura para `SIN_DATO` y tres etiquetas de nivel de atención con texto e icono.

---

## 7.bis Leyenda de las gráficas

Responde a la §7.bis del plan y al criterio de aceptación **28**. Va aquí, en el documento canónico
de visualizaciones, y no en un archivo aparte (regla 1 del vault).

**Ninguna gráfica se entrega sin su leyenda.** No es la leyenda de colores que trae cualquier
librería: es el bloque que permite leer la gráfica sin que nadie la explique en voz alta. Va directo
contra el hallazgo del profesor del 9-sep — una gráfica que hay que explicar en vivo no comunica sola.

### 7.bis.1 Qué declara toda leyenda

Cuatro cosas, en este orden y en lenguaje de negocio:

| # | Declara | Regla |
|---|---|---|
| 1 | **Qué se está viendo** | Qué representa cada eje, fila, columna, serie o marca, con el nombre que usa el usuario y no el del campo: `indice_riesgo` es "índice de riesgo"; `d2` es "inseguridad del entorno"; `cve_mun` no aparece |
| 2 | **En qué unidad está el valor** | Si es índice, proporción, conteo o posición relativa, con su rango. Un driver **nunca** se rotula con `%` (§4.1): son posiciones relativas, no porcentajes |
| 3 | **Cómo se ve aquí un `SIN_DATO`** | La marca concreta *de esa gráfica* —celda rayada, pista rayada, fila sin marca— y la frase de que no es un cero (§6) |
| 4 | **De qué ciclo y qué recorte habla** | El ciclo, resuelto del dato (`id_ciclo`, nunca tecleado), y si el conjunto son las `N` escuelas en riesgo, el universo del alcance o una lista filtrada |

**Forma: bloque fijo y visible, nunca sólo tooltip.** La §4.5 ya prohíbe que un valor viva únicamente
en el *hover*; la leyenda cae en la misma regla. El tooltip puede repetirla, no sustituirla, y la
tabla gemela accesible incluye el mismo texto. Juan le da tratamiento visual; el texto es de este
documento y no se reescribe al maquetar (§7.5).

### 7.bis.2 Leyenda resuelta, gráfica por gráfica

**El alcance es por gráfica, no por pantalla:** son cinco gráficas más el panel de explicación del
modelo. Texto listo para implementar; los conteos van como `N` y `k` y se resuelven en vivo (§1.1).

| Gráfica | Qué se está viendo | Unidad | `SIN_DATO` aquí | Ciclo y recorte |
|---|---|---|---|---|
| **P2 · Matriz de casos** (§3) | Una fila por escuela en riesgo y una columna por pista del entorno. El tono de la celda dice cuánta presión ejerce esa pista sobre esa escuela; el recuadro con ▲ marca la que más destaca | Posición relativa de 0 a 1 frente al resto de escuelas observadas, **no porcentaje**: 0 es la menor presión observada y 1 la mayor | Celda rayada con "sin dato": esa pista no se pudo verificar para esa escuela. No es un cero ni quiere decir que no haya problema | Ciclo `{id_ciclo}`. Las `N` escuelas que cruzan la línea de alerta, de las `M` del alcance (CDMX, Estado de México, Nuevo León y Jalisco) |
| **P3 · Pista del índice de riesgo** (§2) | Una fila por escuela. El número es su índice de riesgo y la pista muestra dónde cae ese índice, con dos marcas fijas: `RIESGO_ESTABLE` y la línea de alerta | Índice de 0 a 1 que traduce la variación de matrícula que el modelo proyecta. No es probabilidad ni porcentaje | Una escuela sin predicción lo dice en su fila y no recibe marca en la pista; no se coloca en 0 | Ciclo `{id_ciclo}`. Las `N` escuelas en riesgo, de mayor a menor índice |
| **P4 · Comparativa de los 6 drivers** (§4) | Las seis pistas del entorno de esta escuela, siempre en el mismo orden. La barra mide cuánta presión ejerce cada una; la marcada con ▲ es la que más destaca según el modelo | Posición relativa de 0 a 1 entre las escuelas observadas. Infraestructura y conectividad se leen como **falta**: 1 es carencia total del servicio (§4.1) | Pista rayada de punta a punta, con el motivo por el que falta. Un cero real se dibuja como una línea mínima con su "0.00": no se parecen | Ciclo `{id_ciclo}`, una sola escuela. Pobreza y rezago e inseguridad son **valores de su municipio**, compartidos con las demás escuelas de ahí |
| **P4 · Panel de explicación del modelo** (§4.4) | Cuánto pesó cada pista en el cálculo del modelo. Es una pregunta distinta a la presión: describe al modelo, no a la escuela | Contribución con signo alrededor de cero | Hoy el panel completo está en `SIN_DATO`: la explicación aún no se publica en producción | Ciclo `{id_ciclo}`, una sola escuela |
| **P5 · Gráfica de unidades del Top** (§5) | Cada casilla es una escuela en riesgo, agrupada bajo la pista que más destaca en ella. Cuantas más casillas, más se repite esa pista | Conteo de escuelas, `k de N`. La proporción es secundaria: con `N` pequeño una escuela mueve muchos puntos | Las pistas que no pudieron verificarse en ninguna escuela no aparecen en el Top, y la nota de cobertura dice cuáles son. Una pista con 0 no deja de existir | Ciclo `{id_ciclo}`. El **conjunto completo** de escuelas en riesgo, sin filtros, sin importar lo que el usuario haya filtrado antes |
| **P6 · Las reutilizadas del expediente** (§2) | La pista del índice y la comparativa de los 6 drivers, idénticas a la P3 y la P4. No cambian de forma al reutilizarse | La misma de cada gráfica original | El mismo de cada gráfica original | **Lo único que cambia es esta línea:** ciclo `{id_ciclo}` y el filtro activo de entidad, municipio y nivel, en vez del conjunto en riesgo. El filtro de nivel **no** cambia los indicadores de arriba (§8.1) |

Que la leyenda de la P6 sólo cambie en el recorte es deliberado: es lo que hace que el usuario
reconozca la gráfica que ya aprendió a leer en la historia, y que la única diferencia —de qué
escuelas habla ahora— quede dicha en lugar de suponerse.

---

## 8. Lo que NO se puede graficar hoy

### 8.1 Recortes explícitos

| Qué | Por qué no | Si se aprueba | Mientras tanto |
|---|---|---|---|
| **`prioridad` de Gold** (era P-01) | No aparece en `EscuelaOut`, `EscuelaDetalleOut`, `PrediccionOut` ni `ExplicacionSHAPOut`, y `ADR-011` §5 prohíbe consumir `gold.recomendaciones.prioridad` mientras use el ancla histórica 0.60 (`src/modelos/publicar_gold.py:197`, `BUG-063`) | Si el PO y el Equipo 4 realinean `prioridad` a `LINEA_DE_ALERTA` y el contrato la expone, coincidiría con el nivel de atención: Front podría consumirla y retirar su derivación | **Nivel de atención** derivado (§1.1). Ninguna gráfica, filtro ni texto la llama "prioridad". El glosario explica por qué DB-09 muestra `media` para las mismas escuelas (§1.2) |
| **Bandas "oficiales" alto/medio/bajo** (era P-02) | Resuelto por `ADR-011` §5: son el nivel de atención | — | Una sola etiqueta; no existe una segunda |
| **Distribución de niveles de atención en la P5** | Tautológica: el conjunto en riesgo se define con el mismo corte que "alta" | — | Una línea de texto (§5.2) |
| **Distribución de niveles en la P6 para todo un filtro** | Contarla exige paginar todas las escuelas del filtro (`size ≤ 100`), y `/kpis` sólo cuenta las de riesgo alto | Un conteo por nivel de atención en `/kpis` (cambio de contrato, Equipo 5) | El nivel va por fila en la página visible, y `escuelas_en_riesgo` del filtro desde `/kpis` |
| **Mapa de ubicación** | La API no expone geometría y `latitud`/`longitud` sin base no se leen | Exponer la geometría municipal de Gold o aprobar como base cartográfica versionada `superset/assets/geojson/municipios_scope.geojson`, que es lo que usa la referencia 04 (§7.4): municipio resaltado y punto de la escuela en el expediente | Municipio y entidad como texto |
| **Rezago del municipio contra el promedio estatal** | El promedio estatal no está en la API y el índice de CONEVAL es negativo en estos municipios | Derivación declarada en §1.1 desde `GET /api/v1/municipios?cve_ent=…`, dibujada como franja de municipios con el promedio marcado (§7.4) | Línea de contexto con `pobreza_pct` (§4.2) |
| **Evolución histórica de matrícula por escuela** | `/escuelas/{cct}` no acepta `ciclo`, y el plan la excluye del expediente | Cambio de plan más petición de endpoint | No se dibuja |
| **Caída de matrícula de una escuela concreta** | `variacion_matricula` sólo existe agregada (`KpisOut`) | Un campo por escuela en el contrato | Sólo la variación agregada, en la P2 |
| **Escuela contra su municipio en D2…D6** | No hay promedio municipal de esos drivers; además D1 y D2 ya son valores del municipio | Un agregado territorial por driver en el contrato | Sólo el contexto de D1 con `pobreza_pct` (§4.2) |
| **Explicación SHAP con valores** | Las columnas `shap_d1…shap_d6` no están pobladas en producción (0 de 42 en la consulta) | Cuando el Equipo 4 las pueble: barras divergentes (§4.4) | Panel `SIN_DATO` |
| **Perfil de ML-03 (`cluster`)** | `cluster` es `None` sin productor (`vault/03_Architecture/API_Specification.md:208-209`) | Si ML-03 llega a Gold y API (`US-631`): etiqueta de perfil en el expediente | No se muestra |
| **Indicadores filtrados por nivel educativo** | `/kpis` no acepta `nivel` | Añadir `nivel` a `/kpis` | El filtro de nivel sólo actúa sobre la lista |
| **D5 estrés hídrico** | Sin fuente integrada (DS-06): `null` en todas las escuelas | Cuando DS-06 llegue a Gold, la fila se llena sola | Rayado `SIN_DATO` en todas |
| **`es_estimado_por_grupo` con valor** | La columna no existe en Gold; la API siempre devuelve `null` | Cuando se materialice | "Estimación por grupo: sin dato" |

Ninguno de estos recortes detiene la construcción (`DEC-024`): cada uno tiene su "mientras tanto"
dibujable hoy.

### 8.2 Avisos para el Equipo 5 que no son gráficas

- **El nombre del asistente.** De cara al usuario es **Asistente FARO** (`ADR-011` §6), y así lo
  escribe todo este paquete. `src/agente/**` y `/api/v1/agente/consulta` son nombres técnicos y **no
  se tocan**: es producto contra implementación, no contradicción. Lo único que cambia es la cadena que
  ve el usuario, y hoy el producto vivo todavía imprime el nombre viejo: `src/frontend/pages/3_Chat.py:33`
  → `st.title("Agente FARO")`. Además, **dos pruebas exigen ese literal**:
  `tests/test_frontend_chat_streamlit.py:77` y `:114`. Quien cambie el título sin tocarlas rompe CI.
  Es del Equipo 5, dueño de `src/frontend/**`; Marina García se los pasa hoy.
- **Las constantes se importan** (§1.1) y la orientación de D3/D4 vive en una sola función (§4.1).
- **Ciclo explícito.** `/escuelas`, `/escuelas/{cct}` y `/kpis` usan el ciclo más reciente
  materializado (`src/api/repositorio_gold.py:213-241`); `/predicciones/{cct}` tiene `ciclo` por
  defecto `2024-2025`. En la consulta coincidieron: `id_ciclo = 2024-2025` e `indice_riesgo` idéntico
  en las siete. Cuando Gold avance de ciclo dejarán de coincidir, así que Front debe pasar el mismo
  `ciclo` a `/escuelas`, `/kpis` y `/predicciones`. `/escuelas/{cct}` no acepta `ciclo`: si el ciclo
  elegido no es el más reciente, sus `d1…d6` son de otro ciclo y el expediente lo tiene que decir.

### 8.3 Revisión de Marina García (PR #308, 2026-09-10) — visto bueno con dos correcciones a su plan

Marina revisó y dio **visto bueno**. Registro aquí sus dos hallazgos, porque corrigen `PLAN_TRABAJO`
y ella los aplica ahí, no en este documento:

1. **§10 del plan prometía `/predicciones/{cct}/explicacion` como evidencia disponible del driver
   dominante.** Con `shap_d1…shap_d6` sin poblar (§4.4 de aquí), esa evidencia no existe hoy. Marina
   corrige el mapeo del plan.
2. **El Top 3 que hoy son dos drivers.** Confirmado: la pantalla muestra los que realmente dominan,
   sin rellenar hasta tres, con la copy explicando que sólo hay dato de D1, D2 y D4 en las siete y que
   D1 no destaca. El paso 6 de la §5.1 ya lo resuelve tal cual; no cambia.

También resolvió a mi favor un choque con Oscar: `/kpis` no acepta `nivel` (verificado en la §3.4),
y adoptó mi recomendación de que la revelación de la P2 es siempre el total sin filtros, con los
filtros atenuando filas de la matriz — así la leyenda obligatoria de la P5 (§5.2) se sostiene con
cualquier filtro que el usuario haya usado antes.

**Las tres piezas nuevas del plan ya están en `main`** (PR #312, mergeado el 2026-09-11). Efecto en
este documento:

- **§7.bis, leyenda de las gráficas** → resuelta en la **§7.bis de aquí**, como sección propia y con
  alcance por gráfica: cinco gráficas más el panel de explicación del modelo.
- **§4.ter, el SQL del Asistente FARO no se muestra por defecto** → no toca ninguna gráfica de este
  documento. Queda anotado por si una pieza futura lo asumiera.
- **§5.bis, "Cómo funciona" del Equipo 1** → revisada contra las reglas de forma de aquí en la §8.4.

### 8.4 "Cómo funciona" (§5.bis) contra las reglas de forma de este documento

Revisión pedida por Marina. La sección es del Equipo 1 y **este frente no la rediseña**; lo que sigue
son los puntos donde sus tres bloques D3 —`mapa`, `barras` y `diagrama_flujo`— se cruzan con las
reglas de aquí. Ninguno es un defecto suyo: son decisiones que hay que tomar a propósito.

1. **El criterio 28 no distingue superficies.** Dice "toda gráfica explica qué se está viendo". Leído
   literal, los tres bloques D3 también necesitan su leyenda (§7.bis.1). Tiene sentido que la lleven
   —son justo las piezas que el profesor pidió ver—, pero el texto es del Equipo 1, que es quien sabe
   qué mide cada una. **Decisión para Marina:** o el criterio 28 se acota explícitamente a las
   gráficas de la historia, o el Equipo 1 escribe las cuatro declaraciones de sus tres bloques. Lo que
   no se sostiene es dejarlo ambiguo y que QA lo descubra el domingo.
2. **Contenido fijo con cifras dentro.** La §5.bis dice que el único dato vivo son los conteos de
   filas por capa y que el resto es contenido fijo. Si alguno de esos bloques lleva una cifra escrita
   —cuántas escuelas, cuántos municipios—, es el mismo patrón contra el que existe la regla de `N`
   (§1.1): el día que cambie el ciclo, esa cifra miente y nada la detecta. **Recomendación:** que las
   cifras de esos bloques salgan del conteo vivo o no aparezcan.
3. **`SIN_DATO` de estructura.** Que un tipo de bloque desconocido se pinte con advertencia y no tumbe
   la página es la misma regla de aquí, bien aplicada. Para que se lea igual en las dos superficies,
   esa advertencia debe verse como se ve un `SIN_DATO` en la historia —textura y texto, no un hueco
   en blanco (§6).
4. **El fondo blanco forzado de los iframes.** El Equipo 1 fijó `color-scheme: light` para no quedar
   con letras negras sobre fondo negro. Si la identidad de Juan resulta oscura, esos tres bloques van
   a quedar en una isla clara. Desde la lectura del dato eso importa menos que dos cosas que sí son
   innegociables: que **no usen semáforo rojo/ámbar/verde** ni rampa multicolor para magnitud (§7.5),
   porque entonces la misma idea se leería de dos formas distintas según la superficie.
5. **Una oportunidad, no un pendiente.** Su bloque `mapa` demuestra que el front ya puede pintar una
   base cartográfica. Eso **no** habilita por sí solo el mapa de la historia —el suyo ilustra la
   arquitectura, no dibuja escuelas de Gold, y sigue sin haber geometría en la API v1—, pero sí
   responde la mitad de la condición que la §8.1 pone en "si se aprueba". Si el PO quiere el mapa en
   la P2 o en el expediente, el camino más corto pasa por ahí y no por un endpoint nuevo.

Las dos rutas (`/api/v1/about/secciones` y `/api/v1/about/secciones/{id_seccion}`) siguen sin llegar
a `main`: mientras eso no ocurra, esta revisión es sobre la especificación del Equipo 1, no sobre algo
que se pueda mirar funcionando.
