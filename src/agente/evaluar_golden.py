"""Evalua preguntas golden contra Anthropic, ChromaDB y Postgres reales.

Uso manual desde la raiz del repositorio:

    python -m src.agente.evaluar_golden

Requiere `ANTHROPIC_API_KEY`, `DATABASE_URL_READ_ONLY` y ChromaDB disponible. No se ejecuta en
CI porque consume el LLM y los resultados se guardan solo si se proporciona `--salida`.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from src.agente.llm import generar_sql_con_llm, redactar_respuesta_con_llm
from src.agente.recuperacion import recuperar_contexto
from src.agente.servicio import procesar_consulta_con_rag
from src.api.ejecutor_gold import ejecutar_sql_read_only

FIXTURE_POR_DEFECTO = Path("tests/fixtures/preguntas_evaluacion.json")


@dataclass(frozen=True)
class ResultadoGolden:
    """Resultado observable de una pregunta, sin incluir secretos ni SQL completo."""

    indice: int
    pregunta: str
    categoria: str
    paso: bool
    fuera_de_alcance: bool | None
    tiene_sql: bool
    respuesta_no_vacia: bool
    error: str | None = None


def _cargar_fixture(ruta: Path) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8") as archivo:
        casos = json.load(archivo)
    if not isinstance(casos, list) or not casos:
        raise ValueError("El fixture golden debe contener una lista no vacia.")
    for caso in casos:
        if not isinstance(caso, dict) or not all(
            isinstance(caso.get(campo), str) for campo in ("pregunta", "categoria")
        ):
            raise ValueError("Cada caso golden requiere pregunta y categoria de texto.")
    return casos


def _cumple_expectativa(categoria: str, fuera_de_alcance: bool, tiene_sql: bool) -> bool:
    if categoria == "valida":
        return not fuera_de_alcance and tiene_sql
    if categoria == "fuera_de_alcance":
        return fuera_de_alcance and not tiene_sql
    if categoria == "insegura":
        return not tiene_sql
    raise ValueError(f"Categoria golden desconocida: {categoria}")


def evaluar_caso(indice: int, caso: dict[str, str]) -> ResultadoGolden:
    pregunta = caso["pregunta"]
    categoria = caso["categoria"]
    try:
        resultado = procesar_consulta_con_rag(
            pregunta,
            generar_sql=generar_sql_con_llm,
            ejecutar_sql=ejecutar_sql_read_only,
            redactar_respuesta=redactar_respuesta_con_llm,
        )
        fuera_de_alcance = resultado.fuera_de_alcance
        tiene_sql = bool(resultado.sql_generado)
        respuesta_no_vacia = bool(resultado.respuesta.strip())
        paso = respuesta_no_vacia and _cumple_expectativa(
            categoria, fuera_de_alcance, tiene_sql
        )
        return ResultadoGolden(
            indice=indice,
            pregunta=pregunta,
            categoria=categoria,
            paso=paso,
            fuera_de_alcance=fuera_de_alcance,
            tiene_sql=tiene_sql,
            respuesta_no_vacia=respuesta_no_vacia,
        )
    except Exception as exc:  # noqa: BLE001 - el reporte debe continuar con los demás casos.
        return ResultadoGolden(
            indice=indice,
            pregunta=pregunta,
            categoria=categoria,
            paso=False,
            fuera_de_alcance=None,
            tiene_sql=False,
            respuesta_no_vacia=False,
            error=str(exc),
        )


def evaluar_fixture(ruta: Path) -> list[ResultadoGolden]:
    """Ejecuta todos los casos golden y devuelve resultados individuales."""
    return [evaluar_caso(indice, caso) for indice, caso in enumerate(_cargar_fixture(ruta), 1)]


def _argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        type=Path,
        default=FIXTURE_POR_DEFECTO,
        help="Ruta al fixture JSON de preguntas golden.",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        help="Ruta opcional para guardar el reporte JSON sin respuestas ni SQL sensibles.",
    )
    return parser.parse_args()


def main() -> int:
    args = _argumentos()
    try:
        resultados = evaluar_fixture(args.fixture)
    except (OSError, ValueError) as exc:
        print(f"No se pudo ejecutar la evaluacion golden: {exc}", file=sys.stderr)
        return 2

    total = len(resultados)
    aprobados = sum(resultado.paso for resultado in resultados)
    print(f"Evaluacion golden: {aprobados}/{total} casos aprobados.")
    for resultado in resultados:
        estado = "PASS" if resultado.paso else "FAIL"
        detalle = f" error={resultado.error}" if resultado.error else ""
        print(f"[{estado}] {resultado.indice:02d} [{resultado.categoria}] {resultado.pregunta}{detalle}")

    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(
            json.dumps([asdict(resultado) for resultado in resultados], ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
        print(f"Reporte guardado en {args.salida}")

    return 0 if aprobados == total else 1


if __name__ == "__main__":
    raise SystemExit(main())