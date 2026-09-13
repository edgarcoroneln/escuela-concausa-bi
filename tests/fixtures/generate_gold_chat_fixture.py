"""Genera el fixture anonimizado de Gold para que Andrés pruebe el chat FARO en local
(coordinación de Luis, 2026-09-13, a petición de Andrés González -- C2, Chat IA).

Extrae de Gold real (Postgres LOCAL, nunca producción -- este script no acepta un DSN
remoto) las 3 tablas que consulta el Text-to-SQL del agente:

    - gold.dim_municipio      (clave, nombre_municipio, nombre_entidad)
    - gold.dim_escuela        (cct, nombre, nivel, municipio)
    - gold.fact_escuela_ciclo (matrícula + los 6 drivers + indice_completitud_drivers)

y escribe 3 CSV anonimizados en tests/fixtures/gold/, <=500 filas en el hecho (regla del
repo), listos para cargarse a un Postgres local con cargar_fixture_gold.sql (mismo
directorio).

Anonimización aplicada (criterio de Diana Alvarez, dueña de Gold -- ajustar aquí si cambia):
    - cct          -> surrogate secuencial "ESC-{cve_ent}-{n:04d}" (nunca un hash del cct
                      real: un hash es reversible por diccionario porque los ~200k CCT
                      reales de todo el país son públicos y buscables).
    - nombre       -> genérico "Escuela {n:04d}".
    - nivel, cve_mun, cve_ent -> se conservan tal cual (no son sensibles, y el Text-to-SQL
                      necesita agrupar por ellos correctamente -- pedido explícito de Luis).
    - latitud/longitud, sostenimiento, infraestructura (agua/drenaje/...) -> NO se exportan:
                      Luis no las pidió para este fixture (el agente no las consulta) y
                      lat/long de un edificio real es la forma más fácil de reidentificar
                      la escuela aunque el nombre ya sea genérico.
    - matrícula, drivers D1-D6, indice_completitud_drivers -> reales, sin perturbar: son
                      justo lo que hace visible el diferenciador prescriptivo que pidió
                      Andrés, y no son datos personales de nadie.
    - SIN_DATO     -> se conserva el mismo mecanismo que ya usa gold.fact_escuela_ciclo
                      (valor NULL + columna `dN_cobertura` = 'SIN_DATO'), en vez de escribir
                      el string "SIN_DATO" en una columna numérica -- así el fixture se
                      comporta IGUAL que producción, que es el punto de un fixture. D5
                      (estrés hídrico) va a salir SIN_DATO en el 100% de las filas porque
                      hoy fact_escuela_ciclo.sql todavía no tiene fuente para D5 en ningún
                      entorno -- no es un error de este script.
    - mapa real->surrogate -> se guarda APARTE, fuera de tests/fixtures/, en un CSV que
                      nunca se commitea (ver --mapa-salida) -- por si hay que auditar o
                      corregir algo después. Bórralo cuando ya no lo necesites.

El par del diferenciador (15DPR0920D / 15DPR2254O -- mismo municipio, mismo índice de
riesgo, distinto driver dominante, el que ya usa "El diferenciador" en Conclusion.jsx) se
incluye siempre, sin importar el muestreo aleatorio, para que Andrés pueda reproducir la
demo con el chat.

Requiere Postgres LOCAL con Gold ya poblado (dbt run del proyecto) -- no corre nada de dbt
ni toca producción. Usa las mismas variables de entorno que ya lee el resto del proyecto
(POSTGRES_HOST/PORT/DB/USER/PASSWORD, ver src/ingesta/cargar_bronze_fixture.py).

Uso:
    python -m tests.fixtures.generate_gold_chat_fixture
    python -m tests.fixtures.generate_gold_chat_fixture --n-escuelas 260 --seed 0.42
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

import psycopg2
import psycopg2.extras

SCOPE_ENTIDADES = ("09", "15", "19", "14")  # CDMX, Edomex, Nuevo León, Jalisco -- Data_Model.md §7
DIFERENCIADOR_CCTS = ("15DPR0920D", "15DPR2254O")  # par real de "El diferenciador", Conclusion.jsx

DRIVERS = ["d1", "d2", "d3", "d4", "d5", "d6"]

SALIDA_DIR = Path(__file__).resolve().parent / "gold"


def conectar():
    return psycopg2.connect(
        f"host={os.environ.get('POSTGRES_HOST', 'localhost')} "
        f"port={os.environ.get('POSTGRES_PORT', '5432')} "
        f"dbname={os.environ.get('POSTGRES_DB', 'escuela_concausa_db')} "
        f"user={os.environ.get('POSTGRES_USER', 'postgres')} "
        f"password={os.environ.get('POSTGRES_PASSWORD', '')}"
    )


def elegir_ccts(cur, n_escuelas: int, seed: float) -> list[str]:
    """CCTs a incluir: el par del diferenciador siempre + muestra aleatoria reproducible
    del resto del alcance, hasta completar n_escuelas."""
    cur.execute("select setseed(%s)", (seed,))
    cur.execute(
        """
        select e.cct
        from gold.dim_escuela e
        where e.cve_ent in %s
          and e.cct not in %s
        order by random()
        limit %s
        """,
        (SCOPE_ENTIDADES, DIFERENCIADOR_CCTS, max(n_escuelas - len(DIFERENCIADOR_CCTS), 0)),
    )
    resto = [r[0] for r in cur.fetchall()]
    return list(DIFERENCIADOR_CCTS) + resto


def construir_mapa_surrogate(cur, ccts: list[str]) -> dict[str, dict]:
    """cct real -> {surrogate, nombre_generico, cve_ent}, secuencial y determinista
    (orden por cve_ent y luego por cct real) para que el fixture sea reproducible."""
    cur.execute(
        "select cct, cve_ent from gold.dim_escuela where cct = any(%s)",
        (ccts,),
    )
    fila_por_cct = dict(cur.fetchall())
    ordenados = sorted(ccts, key=lambda c: (fila_por_cct.get(c, "99"), c))

    mapa: dict[str, dict] = {}
    contador_por_entidad: dict[str, int] = {}
    for cct in ordenados:
        cve_ent = fila_por_cct.get(cct, "00")
        contador_por_entidad[cve_ent] = contador_por_entidad.get(cve_ent, 0) + 1
        n = contador_por_entidad[cve_ent]
        n_global = len(mapa) + 1
        mapa[cct] = {
            "surrogate": f"ESC-{cve_ent}-{n:04d}",
            "nombre_generico": f"Escuela {n_global:04d}",
            "cve_ent": cve_ent,
        }
    return mapa


def exportar_dim_municipio(cur, ruta: Path) -> int:
    cur.execute(
        """
        select cve_mun, cve_ent, nombre_municipio, coalesce(nombre_entidad, 'SIN_DATO') as nombre_entidad
        from gold.dim_municipio
        where cve_ent in %s
        order by cve_mun
        """,
        (SCOPE_ENTIDADES,),
    )
    filas = cur.fetchall()
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cve_mun", "cve_ent", "nombre_municipio", "nombre_entidad"])
        w.writerows(filas)
    return len(filas)


def exportar_dim_escuela_y_fact(cur, mapa: dict[str, dict], ccts: list[str], dir_salida: Path) -> tuple[int, int]:
    """Une dim_escuela + fact_escuela_ciclo en una sola consulta (evita repetirla) y
    escribe los dos CSV ya anonimizados."""
    cur.execute(
        """
        select
            e.cct, e.nombre, e.nivel, e.cve_mun,
            f.id_ciclo, f.matricula_total, f.matricula_ciclo_anterior, f.variacion_matricula,
            f.indice_completitud_drivers,
            f.d1, f.d2, f.d3, f.d4, f.d5, f.d6,
            f.d1_cobertura, f.d2_cobertura, f.d3_cobertura, f.d4_cobertura, f.d5_cobertura, f.d6_cobertura
        from gold.dim_escuela e
        join gold.fact_escuela_ciclo f on f.cct = e.cct
        where e.cct = any(%s)
          and f.id_ciclo = (select max(id_ciclo) from gold.fact_escuela_ciclo)
        order by e.cct
        """,
        (ccts,),
    )
    cols = [d.name for d in cur.description]
    filas = cur.fetchall()

    dim_rows = []
    fact_rows = []
    for fila in filas:
        r = dict(zip(cols, fila))
        info = mapa[r["cct"]]
        surrogate = info["surrogate"]
        dim_rows.append([surrogate, info["nombre_generico"], r["nivel"], r["cve_mun"]])
        fact_rows.append(
            [surrogate, r["id_ciclo"], r["matricula_total"], r["matricula_ciclo_anterior"], r["variacion_matricula"],
             r["indice_completitud_drivers"]]
            + [r[d] for d in DRIVERS]
            + [r[f"{d}_cobertura"] for d in DRIVERS]
        )

    with (dir_salida / "dim_escuela_fixture.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cct", "nombre", "nivel", "cve_mun"])
        w.writerows(dim_rows)

    with (dir_salida / "fact_escuela_ciclo_fixture.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["cct", "id_ciclo", "matricula_total", "matricula_ciclo_anterior", "variacion_matricula",
             "indice_completitud_drivers"]
            + DRIVERS
            + [f"{d}_cobertura" for d in DRIVERS]
        )
        w.writerows(fact_rows)

    return len(dim_rows), len(fact_rows)


def escribir_mapa_auditoria(mapa: dict[str, dict], ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cct_real", "surrogate", "nombre_generico", "cve_ent"])
        for cct_real, info in mapa.items():
            w.writerow([cct_real, info["surrogate"], info["nombre_generico"], info["cve_ent"]])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-escuelas", type=int, default=260, help="Escuelas a incluir (default 260, entre 200-300 pedidas)")
    ap.add_argument("--seed", type=float, default=0.42, help="Semilla de Postgres para el muestreo reproducible")
    ap.add_argument(
        "--mapa-salida",
        default=str(Path.home() / "faro_mapa_cct_real_NO_SUBIR.csv"),
        help="Ruta FUERA del repo para el mapa cct_real->surrogate (nunca se commitea)",
    )
    args = ap.parse_args()

    if not (200 <= args.n_escuelas <= 300):
        print(f"[aviso] --n-escuelas={args.n_escuelas} fuera del rango 200-300 que pidió Luis, pero se continúa.")

    SALIDA_DIR.mkdir(parents=True, exist_ok=True)

    conn = conectar()
    try:
        with conn.cursor() as cur:
            n_municipios = exportar_dim_municipio(cur, SALIDA_DIR / "dim_municipio_fixture.csv")

            ccts = elegir_ccts(cur, args.n_escuelas, args.seed)
            mapa = construir_mapa_surrogate(cur, ccts)
            n_escuelas, n_fact = exportar_dim_escuela_y_fact(cur, mapa, ccts, SALIDA_DIR)

        escribir_mapa_auditoria(mapa, Path(args.mapa_salida))
    finally:
        conn.close()

    print(f"dim_municipio_fixture.csv:      {n_municipios} filas")
    print(f"dim_escuela_fixture.csv:        {n_escuelas} filas")
    print(f"fact_escuela_ciclo_fixture.csv: {n_fact} filas (límite del repo: 500)")
    print(f"Mapa real->surrogate (NO subir a git): {args.mapa_salida}")
    if n_fact > 500:
        raise SystemExit(f"[error] {n_fact} filas en el hecho supera el límite de 500 -- baja --n-escuelas")


if __name__ == "__main__":
    main()
