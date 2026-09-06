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

Las **tres** rutas leen `gold.predicciones` + `gold.recomendaciones` a través de
`RepositorioModelos` (`src/api/repositorio_modelos.py`, US-412) -- cierra BUG-010, que detectó que
seguían leyendo `src/api/mock_data.py` (un valor fabricado, no la salida de ningún modelo), y
BUG-053, que era lo mismo para `explicacion`: desde que ML-02 persiste `shap_d1..shap_d6`
(`publicar_gold.py`, C3) ya hay fuente real que leer. **Este router ya no consume `mock_data`
salvo para el ciclo por defecto.**

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
def explicacion(
    cct: str,
    ciclo: str = Query(mock_data.CICLO_DEFAULT),
    repo: RepositorioModelos = Depends(get_repositorio_modelos),
) -> ExplicacionSHAPOut:
    """Contribucion de cada driver al riesgo (acceso: `require_lectura`, ver el modulo).

    Lee `gold.recomendaciones` (columnas `shap_d1..shap_d6`, que persiste `publicar_gold.py` desde
    ML-02) a traves de `obtener_prediccion` -- la misma fila que sirve `/predicciones/{cct}`.
    Reutilizarla en vez de hacer una consulta propia no es casualidad: hereda el cache TTL y la
    traduccion a 503 de US-416, y hace **imposible** que la explicacion se desincronice del
    `driver_dominante` que dice explicar. Cierra BUG-053; antes devolvia `mock_data`.

    **`null` significa SIN_DATO, no cero.** Un driver sin contribucion calculable viaja como
    `null`; colapsarlo a `0.0` afirmaria que ese driver no contribuyo al riesgo, que es una
    afirmacion falsa sobre la causa (BUG-055). Las seis claves estan siempre presentes: el hueco
    se declara, no se omite.

    404 si el CCT no tiene fila para ese ciclo -- nunca una explicacion inventada.
    """
    try:
        fila = repo.obtener_prediccion(cct, ciclo)
    except RepositorioModelosNoDisponible as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="Servicio de predicciones no disponible."
        ) from exc
    if fila is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="CCT sin prediccion o fuera de alcance."
        )
    return ExplicacionSHAPOut(
        cct=fila["cct"],
        driver_dominante=fila["driver_dominante"],
        contribuciones={
            f"D{i}": fila.get(f"shap_d{i}") for i in range(1, 7)
        },
    )
