"""Predicciones / inferencia ML: `/predicciones/*` (§3.4).

`PrediccionOut` combina ML-01 (riesgo), ML-02 (driver + recomendación) y ML-03 (cluster, `None`
hasta que exista -- ver BUG-010).

**Acceso real de las tres rutas: `require_lectura`**, igual que `gold` y `agente` -- se aplica a
nivel de router en `v1/__init__.py`, no aquí. Es decir: públicas cuando `AUTH_LECTURA_PUBLICA` está
encendido y con sesión de **cualquier** rol cuando está apagado. **Ninguna ruta de predicciones
exige `analista`.** Este docstring decía lo contrario ("solo analista, se forzará en US-403") desde
antes de que US-403 cerrara; era documentación que prometía más restricción de la que el código
aplica, que es la clase de desajuste que se descubre en una demo. Si algún día se quiere que la
explicación sea solo de analista, el cambio va en `v1/__init__.py` con su propia dependencia, no en
un comentario.

`prediccion`/`prediccion_batch` leen `gold.predicciones` + `gold.recomendaciones` a través de
`RepositorioModelos` (`src/api/repositorio_modelos.py`, US-412) -- cierra BUG-010, que detectó que
seguían leyendo `src/api/mock_data.py` (un valor fabricado, no la salida de ningún modelo).
`explicacion` sigue sobre `mock_data` (SHAP no tiene fuente en Gold todavía; fuera de alcance de
BUG-010, que cubre solo `/predicciones` y `/predicciones/batch`).

Si Postgres no responde a tiempo (`RepositorioModelosNoDisponible`, US-416), ambas rutas devuelven
503 `service_unavailable` -- nunca dejan la excepción caer al handler genérico de `app.py` (que la
convertiría en un 500 `internal_error` menos específico) ni inventan una predicción.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api import mock_data
from src.api.repositorio_modelos import (
    RepositorioModelos,
    RepositorioModelosNoDisponible,
    get_repositorio_modelos,
)
from src.api.schemas import (
    ExplicacionSHAPOut,
    Page,
    PrediccionBatchIn,
    PrediccionOut,
)
from src.api.v1.common import paginate

router = APIRouter(prefix="/predicciones", tags=["Predicciones"])


def _buscar_escuela(cct: str) -> dict:
    for e in mock_data.ESCUELAS:
        if e["cct"] == cct:
            return e
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="CCT inexistente o fuera de alcance.")


@router.get("/{cct}", response_model=PrediccionOut)
def prediccion(
    cct: str,
    ciclo: str = Query(mock_data.CICLO_DEFAULT),
    repo: RepositorioModelos = Depends(get_repositorio_modelos),
) -> PrediccionOut:
    """Riesgo y driver dominante de una escuela (rol mínimo: ciudadano)."""
    try:
        fila = repo.obtener_prediccion(cct, ciclo)
    except RepositorioModelosNoDisponible as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="Servicio de predicciones no disponible."
        ) from exc
    if fila is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="CCT sin predicción o fuera de alcance."
        )
    return PrediccionOut(**fila)


@router.post("/batch", response_model=Page[PrediccionOut])
def prediccion_batch(
    body: PrediccionBatchIn,
    repo: RepositorioModelos = Depends(get_repositorio_modelos),
) -> Page[PrediccionOut]:
    """Inferencia en lote (acceso: `require_lectura`, ver el docstring del módulo).

    Omite silenciosamente los CCT sin fila en `gold.predicciones` -- nunca inventa una
    predicción para un CCT fuera de alcance o sin modelo corrido.
    """
    try:
        filas = repo.listar_predicciones(body.ccts, body.id_ciclo)
    except RepositorioModelosNoDisponible as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="Servicio de predicciones no disponible."
        ) from exc
    items = [PrediccionOut(**fila) for fila in filas]
    return paginate(items, page=1, size=100)


@router.get("/{cct}/explicacion", response_model=ExplicacionSHAPOut)
def explicacion(cct: str) -> ExplicacionSHAPOut:
    """Contribución de cada driver al riesgo (acceso: `require_lectura`, ver el módulo).

    **Esta ruta todavía NO devuelve valores SHAP.** Las `contribuciones` son los seis drivers de
    `mock_data`, no la salida de ningún modelo. No es un pendiente de C4 solamente: hoy **no existe
    fuente que leer**. `src/modelos/entrenar_ml02.py::explicar_driver` calcula SHAP con la forma
    exacta de `ExplicacionSHAPOut`, pero **no la llama nadie** y `publicar_gold.py` solo escribe
    `gold.predicciones` y `gold.recomendaciones` -- ninguna guarda contribuciones.

    Calcularlo aquí, por petición, no es opción: `shap` vive en `requirements/celula-3.txt` (no en
    la imagen de la API) y `KernelExplainer` tarda segundos por fila, incompatible con el
    `statement_timeout` y la degradación 503 de US-416.

    Orden para cerrarlo: **C3 persiste las contribuciones en Gold → C4 cambia este cuerpo por una
    lectura del repositorio → prueba de contrato**. El primer paso no es de esta célula.
    """
    escuela = _buscar_escuela(cct)
    contribuciones = {
        f"D{i}": (escuela.get(f"d{i}") or 0.0) for i in range(1, 7)
    }
    return ExplicacionSHAPOut(
        cct=escuela["cct"],
        driver_dominante=escuela["driver_dominante"],
        contribuciones=contribuciones,
    )
