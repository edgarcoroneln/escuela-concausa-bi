"""Cliente HTTP de la inferencia de ML para el panel de US-207.

Consume `/api/v1/predicciones/{cct}` (US-412, contrato `PrediccionOut` de US-415) y
devuelve un objeto estable para que la página no sepa de HTTP ni de códigos de estado.

Mismo patrón que `agente_client.py`: el verbo HTTP es un **seam inyectable** (`get`), así
que las pruebas ejercitan el cliente completo sin red y sin API levantada.

**ML-03 (`cluster`) llega `None` a propósito.** El contrato lo documenta: US-321
(clustering, Célula 3) no tiene productor todavía, así que la columna no existe en
`gold.predicciones`. Se propaga como `None` y la página lo pinta como `SIN_DATO` explícito
— **nunca un cero ni un hueco silencioso**, que es la regla del proyecto.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

#: Umbral de negocio de "escuela en riesgo" (DEC-006, ratificado el 2026-09-04).
#: `indice_riesgo >= 0.60` equivale a proyectar una pérdida de >= 5 % de matrícula:
#: la sigmoide de `src/modelos/riesgo.py` está fijada por esas dos anclas.
UMBRAL_RIESGO = 0.60


@dataclass(frozen=True)
class Prediccion:
    """Salida de los tres modelos para una escuela, en el orden en que se presentan."""

    cct: str
    id_ciclo: str
    indice_riesgo: float          # ML-01
    driver_dominante: str         # ML-02
    recomendacion: str            # ML-02 / ML-03 prescriptivo
    cluster: int | None           # ML-03 — `None` mientras US-321 no aterrice
    mlflow_run_id: str

    @property
    def en_riesgo(self) -> bool:
        """`True` si cruza el umbral de DEC-006."""
        return self.indice_riesgo >= UMBRAL_RIESGO

    @property
    def tiene_cluster(self) -> bool:
        """`False` mientras ML-03 no tenga productor: la página muestra SIN_DATO."""
        return self.cluster is not None


class EscuelaNoEncontrada(LookupError):
    """No hay predicción para ese CCT en el ciclo servido."""


def obtener_prediccion(
    api_base_url: str,
    cct: str,
    get: Callable[..., Any] = httpx.get,
    access_token: str | None = None,
) -> Prediccion:
    """Consulta la predicción de un CCT y valida el contrato mínimo.

    Distingue tres situaciones que la página trata distinto: el CCT no existe (404),
    la API no responde, y la API responde algo que no cumple el contrato.
    """
    clave = cct.strip().upper()
    if len(clave) != 10:
        raise ValueError("El CCT debe tener exactamente 10 caracteres.")

    headers = {"Authorization": f"Bearer {access_token}"} if access_token else None

    try:
        response = get(
            f"{api_base_url.rstrip('/')}/api/v1/predicciones/{clave}",
            headers=headers,
            timeout=15.0,
        )
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise EscuelaNoEncontrada(
                f"No hay predicción publicada para el CCT {clave}."
            ) from exc
        if exc.response.status_code == 503:
            raise ConnectionError(
                "La capa Gold no está disponible; vuelve a intentar en un momento."
            ) from exc
        raise ConnectionError("La API rechazó la solicitud de predicción.") from exc
    except httpx.HTTPError as exc:
        raise ConnectionError("La API de inferencia no está disponible.") from exc

    try:
        cluster = payload.get("cluster")
        if cluster is not None and not isinstance(cluster, int):
            raise TypeError
        return Prediccion(
            cct=str(payload["cct"]),
            id_ciclo=str(payload["id_ciclo"]),
            indice_riesgo=float(payload["indice_riesgo"]),
            driver_dominante=str(payload["driver_dominante"]),
            recomendacion=str(payload["recomendacion"]),
            cluster=cluster,
            mlflow_run_id=str(payload["mlflow_run_id"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("La API devolvió una predicción fuera de contrato.") from exc
