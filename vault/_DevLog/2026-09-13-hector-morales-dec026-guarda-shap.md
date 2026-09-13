---
project: "FARO"
date: "2026-09-13"
author_human: "Héctor Rafael Morales Marbán"
agent: "Claude Code"
model: "claude-opus-5"
session_duration: "1h"
touches: ["DEC-026", "BUG-063", "BUG-058", "DEC-019", "DEC-006", "RISK-010", "US-313"]
tags: [devlog, ml, celula-3, gold, dec-026]
---

# DevLog — 2026-09-13 — `DEC-026` completo salvo la republicación

→ [[vault/_DevLog/_index|Volver al índice]]

Segunda parte de `DEC-026`, ya con `US-601` mergeado (PR #350). Recoge lo que pidieron Edgar
Coronel y Christian Imanol Ruiz Hurtado sobre el trabajo que quedó anclado el 12-sep.

## 1. El cambio de corte, sin novedad

`prioridad_de_riesgo()` marca `ALTA` desde `LINEA_DE_ALERTA` (0.50) y no desde `ANCLA_SIGMOIDE`
(0.60), que era **inalcanzable por construcción**: el máximo real sobre el Gold de producción es
0.5717, así que ninguna de las 45,276 escuelas calificaba y la tarjeta de DB-09 leía 0
(`BUG-063`). El ancla no se mueve: sigue calibrando la sigmoide.

`LINEA_DE_ALERTA` pasa a ser canónica en `src/modelos/riesgo.py`, invirtiendo una decisión propia
del 6-sep — el argumento de entonces (no agravar `RISK-010` con una tercera copia) era correcto
**mientras la capa de modelos no necesitara el número**.

## 2. La guarda de `BUG-063`, con el diseño de Christian Imanol

Él la ofreció escrita y su versión es **mejor que la mía en una cosa**: localiza el corte por
**bisección** sobre `prioridad_de_riesgo`, así que verifica el **comportamiento** de la función y
sigue valiendo sin importar cómo se llame la constante. La mía afirmaba contra el nombre.

Se adopta tal cual, con un solo cambio: importa `LINEA_DE_ALERTA` de `src/modelos/riesgo.py` y no
de `src/api/repositorio_gold.py`. Su versión hacía que una prueba de la capa de modelos dependiera
de la capa que los expone; `test_linea_de_alerta_unica.py` ata las dos copias a la canónica, así
que la garantía es la misma sin invertir la dependencia. Queda anotada su autoría en el archivo.

## 3. La guarda de `--con-shap`: del runbook al script

**El hallazgo es de Christian Imanol y es el más peligroso de todo esto.** `escribir()` hace
`on_conflict_do_update` con `set_` sobre **todas** las columnas menos las llaves. Sin `--con-shap`,
`construir_recomendaciones_ml02` deja `shap_d1..d6` en `None`, así que republicar
**sobrescribe con NULL el SHAP ya publicado** en las 45,276 filas — y `/predicciones/{cct}/explicacion`
se queda sin datos sin que nada falle.

Yo lo iba a anotar en el runbook. **Edgar tiene razón en que eso no basta**: el modo de falla es
silencioso y destructivo, así que ahora lo rechaza el propio script. `_verificar_shap_antes_de_publicar()`
corre **antes de entrenar** y:

- rechaza `--desde-gold` sin `--con-shap`, nombrando las columnas que se perderían;
- ofrece `--sin-shap-a-proposito` para el caso legítimo —un ambiente donde el SHAP nunca se
  pobló—, que obliga a declararlo en vez de que ocurra por omisión;
- comprueba que `shap` esté instalado **antes** de entrenar: descubrirlo al final costaría la
  corrida completa de ML-01 y ML-02;
- no estorba cuando no hay nada que perder: sin `--desde-gold` se publica contra el fixture, y
  `--solo-predicciones` ni siquiera toca `gold.recomendaciones`.

Verificado contra el CLI real, no sólo la función: `python -m src.modelos.publicar_gold --desde-gold`
sale con el mensaje y sin tocar la base.

## 4. Lo que NO se hizo: republicar

Diana Alvarez confirmó que el Gold autoritativo es **producción** y que este ambiente local es
**otra base** —probablemente un target de dbt desalineado, `faro_gold` en vez de `faro`—, no una
variación de la misma. Republicar exige credenciales de producción que no tengo: es de C5 o de
quien administre Cloud SQL.

**Su criterio de cierre, que sustituye al que yo había escrito** y es más fuerte:

1. Comprobar contra producción que exista **al menos una fila `alta`** en `gold.recomendaciones`.
2. Que ese conteo **coincida con `escuelas_en_riesgo` de `/kpis`**.

Ata las dos superficies que hoy cuentan cosas distintas con el mismo nombre. Christian Imanol
añade una tercera comprobación razonable: que el máximo siga en ≈0.5717, reproducible por
`random_state: 0` **sólo si la versión de sklearn es la misma**.

## 🤖 Sesión de IA

- **Agente / modelo:** Claude Code · claude-opus-5
- **Modificados:** `src/modelos/riesgo.py`, `src/modelos/publicar_gold.py`,
  `tests/test_publicar_gold.py`
- **Creados:** `tests/test_prioridad_alcanzable.py`, `tests/test_linea_de_alerta_unica.py`
- **Decisiones autónomas del agente:** añadir `--sin-shap-a-proposito` en vez de sólo rechazar,
  para que el caso legítimo tenga salida declarada; comprobar `shap` antes de entrenar.
- **Correcciones manuales:** ninguna. **El diseño de la guarda principal no es mío**, es de
  Christian Imanol; y el hallazgo del SHAP también.

## Seguridad / calidad

- [x] `pytest tests/ -q` → **1321 passed, 10 skipped**
- [x] `ruff` limpio · **ninguna base de datos tocada**
- [x] Guarda verificada **contra el CLI real**, no sólo la función
- [x] Las guardas se falsificaron el 12-sep: revertir el corte reprueba `test_prioridad_alcanzable`;
      desincronizar la canónica reprueba `test_linea_de_alerta_unica`

## Bloqueantes

- **Republicar Gold**: necesita credenciales de producción. Hasta entonces `prioridad` conserva el
  corte viejo en las filas ya escritas y la tarjeta de DB-09 **sigue en 0** aunque el código ya
  esté bien.
- **`RISK-010` no cierra con esto**: las copias de C4 y C2 siguen existiendo. Lo que sí hay ahora
  es el lugar al que deben apuntar y **la prueba que las ata**, que era lo que el riesgo pedía.

## Próximos pasos

- Quien tenga acceso a producción corre `publicar_gold --desde-gold --con-shap` y entrega la
  verificación de Diana.
- C4 y C2 deciden si retiran sus copias de `LINEA_DE_ALERTA`. La prueba ya las ata, así que
  retirarlas es seguro.
