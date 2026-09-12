#!/usr/bin/env python3
"""
FARO — Generar la silueta nacional simplificada para el mapa de "Cómo funciona" (US-601).

Pedido explícito del usuario tras ver el mapa de los 4 estados de `SCOPE_ENTIDADES`: mostrar el
resto de México en gris de fondo. No existe en el mirror comunitario que ya usa el proyecto
(PhantomInsights/mexico-geojson, mismo origen que `generar_geojson_municipios.py`) un archivo
nacional ligero de solo contorno -- únicamente los 32 estados a detalle de municipio. Este script
baja los 32 (no solo los 4 del alcance), **rasteriza** todos los municipios sobre una rejilla
nacional y **traza el contorno** de la máscara resultante: el resultado es una silueta -- un
polígono (o varios, para Baja California y Yucatán) que se parece a México, no una unión
topológica exacta de fronteras administrativas. Es intencional: el pedido fue "muy simplificada",
para dar contexto visual al mapa de los 4 estados resaltados, no para ningún uso analítico.

**No usar `mexico_silueta.geojson` para nada que no sea decorativo.** No tiene fronteras
estatales, no tiene las llaves `cve_mun`/`cve_ent` del asset de municipios y su borde no coincide
pixel a pixel con el real (viene de una rejilla de ~0.05°, no de las geometrías originales).

Uso:
    # 1) descargar los 32 estados a un directorio temporal (puede tardar varios minutos)
    python superset/generar_geojson_silueta_nacional.py --descargar <dir_tmp>
    # 2) rasterizar + trazar contorno + simplificar y escribir el asset
    python superset/generar_geojson_silueta_nacional.py --generar <dir_tmp>

Dependencias: numpy (ya es dependencia del proyecto vía pandas/scikit-learn, no se agrega nada
nuevo). El resto es stdlib, igual que `generar_geojson_municipios.py`.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
ASSET = RAIZ / "superset" / "assets" / "geojson" / "mexico_silueta.geojson"

# Mismo mirror que ya usa el proyecto (generar_geojson_municipios.py) -- aquí se bajan los 32
# estados, no solo los 4 del alcance, porque la silueta es del país completo.
BASE_URL = "https://raw.githubusercontent.com/PhantomInsights/mexico-geojson/main/2023/states"

# Nombres de archivo verificados contra el listado real del repo (GitHub API), no adivinados.
ESTADOS_TODOS = [
    "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas",
    "Chihuahua", "Ciudad de México", "Coahuila de Zaragoza", "Colima", "Durango",
    "Guanajuato", "Guerrero", "Hidalgo", "Jalisco", "México", "Michoacán de Ocampo",
    "Morelos", "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo",
    "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala",
    "Veracruz de Ignacio de la Llave", "Yucatán", "Zacatecas",
]

# Rejilla nacional (grados). 0.05° ≈ 5.5 km -- "muy simplificada" a propósito (US-601): más
# resolución no aporta a un fondo decorativo y encarece la traza de contorno.
PASO_GRADOS = 0.05
BBOX_MX = (-118.5, 14.3, -86.5, 32.8)  # (lon_min, lat_min, lon_max, lat_max), con margen

TOLERANCIA_DP = 0.03  # grados -- mucho más laxa que el asset de municipios: es solo un contorno
DECIMALES = 3


# --------------------------------------------------------------------------- descarga


def descargar(dir_tmp: Path) -> None:
    dir_tmp.mkdir(parents=True, exist_ok=True)
    for i, nombre in enumerate(ESTADOS_TODOS, 1):
        destino = dir_tmp / f"{nombre}.json"
        if destino.exists():
            print(f"↷ {i:2d}/32 {nombre} (ya descargado)")
            continue
        url = f"{BASE_URL}/{urllib.parse.quote(nombre)}.json"
        print(f"↓ {i:2d}/32 {nombre}")
        with urllib.request.urlopen(url, timeout=120) as resp, destino.open("wb") as fh:
            fh.write(resp.read())
    print("✔ Descarga completa (32 estados)")


# --------------------------------------------------------------------------- rasterización


def _poligonos_de_estado(ruta: Path) -> list[list[list[tuple[float, float]]]]:
    """Lista de polígonos del archivo de un estado, cada uno como lista de anillos (lon, lat).
    Aplana Polygon/MultiPolygon a la misma forma."""
    data = json.loads(ruta.read_text(encoding="utf-8"))
    poligonos: list[list[list[tuple[float, float]]]] = []
    for feat in data["features"]:
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            anillos_grupos = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            anillos_grupos = geom["coordinates"]
        else:
            continue
        for anillos in anillos_grupos:
            poligonos.append([[(float(x), float(y)) for x, y in anillo] for anillo in anillos])
    return poligonos


def _rasterizar_poligono(
    anillos: list[list[tuple[float, float]]],
    lons: np.ndarray,
    lats: np.ndarray,
    mascara: np.ndarray,
) -> None:
    """Marca en `mascara` (bool, shape (n_lat, n_lon)) las celdas cuyo centro cae dentro del
    polígono (anillo exterior menos agujeros), restringido a la sub-rejilla de su bounding box.
    Ray casting vectorizado con numpy -- sin matplotlib ni shapely."""
    exterior = anillos[0]
    xs = np.array([p[0] for p in exterior])
    ys = np.array([p[1] for p in exterior])
    lon_min, lon_max = xs.min(), xs.max()
    lat_min, lat_max = ys.min(), ys.max()

    i0 = max(0, np.searchsorted(lats, lat_min) - 1)
    i1 = min(len(lats), np.searchsorted(lats, lat_max) + 1)
    j0 = max(0, np.searchsorted(lons, lon_min) - 1)
    j1 = min(len(lons), np.searchsorted(lons, lon_max) + 1)
    if i0 >= i1 or j0 >= j1:
        return

    sub_lons = lons[j0:j1]
    sub_lats = lats[i0:i1]
    px, py = np.meshgrid(sub_lons, sub_lats)  # shape (i1-i0, j1-j0)

    dentro = _punto_en_poligono(px, py, exterior)
    for agujero in anillos[1:]:
        dentro &= ~_punto_en_poligono(px, py, agujero)

    mascara[i0:i1, j0:j1] |= dentro


def _punto_en_poligono(px: np.ndarray, py: np.ndarray, anillo: list[tuple[float, float]]) -> np.ndarray:
    """Ray casting vectorizado (par de arreglos 2D px, py) contra un anillo cerrado."""
    n = len(anillo)
    dentro = np.zeros(px.shape, dtype=bool)
    x1, y1 = anillo[0]
    for k in range(1, n + 1):
        x2, y2 = anillo[k % n]
        cruza = ((y1 > py) != (y2 > py))
        # Evita división por cero cuando y2 == y1 (segmento horizontal, no puede cruzar un rayo horizontal)
        with np.errstate(divide="ignore", invalid="ignore"):
            x_interseccion = (x2 - x1) * (py - y1) / (y2 - y1 + (y2 == y1)) + x1
        dentro ^= cruza & (px < x_interseccion)
        x1, y1 = x2, y2
    return dentro


def _trazar_contorno(mascara: np.ndarray, lons: np.ndarray, lats: np.ndarray) -> list[list[list[float]]]:
    """Marching squares binario sobre `mascara` (muestras en los CENTROS de celda `(lats[i],
    lons[j])`, tratadas como el campo escalar de la rejilla). Cada segmento se genera ya
    orientado (regla fija por caso, incluidos los 2 casos "silla de montar" ambiguos) para que el
    encadenado por punto compartido nunca dependa de resolver una bifurcación a mano -- un punto
    de una arista siempre tiene grado ≤ 2, a diferencia de trazar por aristas de celda (lo que
    fallaba: la región continental se perdía por completo al no poder cerrar el anillo grande).
    Verificado con 3 casos sintéticos (cuadrado, forma en L, componentes separadas) antes de
    aplicarlo a México real -- ver DevLog de esta sesión.
    """
    n_lat, n_lon = mascara.shape
    segmentos: list[tuple[tuple[float, float], tuple[float, float]]] = []

    def _n(i, j):
        return ((lons[j] + lons[j + 1]) / 2, lats[i + 1])

    def _s(i, j):
        return ((lons[j] + lons[j + 1]) / 2, lats[i])

    def _o(i, j):
        return (lons[j], (lats[i] + lats[i + 1]) / 2)

    def _e(i, j):
        return (lons[j + 1], (lats[i] + lats[i + 1]) / 2)

    for i in range(n_lat - 1):
        for j in range(n_lon - 1):
            tl = bool(mascara[i + 1, j])
            tr = bool(mascara[i + 1, j + 1])
            br = bool(mascara[i, j + 1])
            bl = bool(mascara[i, j])
            caso = (tl << 3) | (tr << 2) | (br << 1) | bl
            if caso in (0, 15):
                continue
            N, E, S, O = _n(i, j), _e(i, j), _s(i, j), _o(i, j)
            if caso == 1:
                segmentos.append((O, S))
            elif caso == 2:
                segmentos.append((S, E))
            elif caso == 3:
                segmentos.append((O, E))
            elif caso == 4:
                segmentos.append((E, N))
            elif caso == 5:
                # Silla de montar (BL+TR rellenos, TL/BR vacíos): cada esquina se aísla por
                # separado, igual que los casos 1 (O,S) y 4 (E,N) por separado -- NO (O,N)+(S,E),
                # que cruza mal las diagonales y rompe la cadena en cualquier anillo grande que
                # pase por aquí (bug real, encontrado al fallar el trazo del continente completo;
                # los 3 casos sintéticos de prueba no lo detectaron porque ninguno tenía un punto
                # de silla).
                segmentos += [(O, S), (E, N)]
            elif caso == 6:
                segmentos.append((S, N))
            elif caso == 7:
                segmentos.append((O, N))
            elif caso == 8:
                segmentos.append((N, O))
            elif caso == 9:
                segmentos.append((N, S))
            elif caso == 10:
                # Silla de montar (TL+BR rellenos, TR/BL vacíos): mismo criterio que el caso 5,
                # cada esquina aislada por separado -- igual que los casos 8 (N,O) y 2 (S,E).
                segmentos += [(N, O), (S, E)]
            elif caso == 11:
                segmentos.append((N, E))
            elif caso == 12:
                segmentos.append((E, O))
            elif caso == 13:
                segmentos.append((E, S))
            elif caso == 14:
                segmentos.append((S, O))

    salida: dict[tuple[float, float], list[tuple[float, float]]] = {}
    for a, b in segmentos:
        salida.setdefault(a, []).append(b)

    usados: set[tuple[tuple[float, float], tuple[float, float]]] = set()
    anillos: list[list[list[float]]] = []
    for a, b in segmentos:
        if (a, b) in usados:
            continue
        anillo = [a, b]
        usados.add((a, b))
        actual = b
        while actual != a:
            siguientes = [x for x in salida.get(actual, []) if (actual, x) not in usados]
            if not siguientes:
                break
            siguiente = siguientes[0]
            usados.add((actual, siguiente))
            anillo.append(siguiente)
            actual = siguiente
        if anillo[0] == anillo[-1] and len(anillo) >= 4:
            anillos.append([list(p) for p in anillo])
    return anillos


# --------------------------------------------------------------------------- simplificación
# (mismo Douglas-Peucker que generar_geojson_municipios.py, sin duplicar lógica distinta)


def _perp_dist(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return ((px - (ax + t * dx)) ** 2 + (py - (ay + t * dy)) ** 2) ** 0.5


def _douglas_peucker(puntos, tol):
    if len(puntos) < 3:
        return puntos
    a, b = puntos[0], puntos[-1]
    dist_max, idx = 0.0, 0
    for i in range(1, len(puntos) - 1):
        d = _perp_dist(puntos[i], a, b)
        if d > dist_max:
            dist_max, idx = d, i
    if dist_max > tol:
        izq = _douglas_peucker(puntos[: idx + 1], tol)
        der = _douglas_peucker(puntos[idx:], tol)
        return izq[:-1] + der
    return [a, b]


def _simplificar_anillo(anillo: list[list[float]]) -> list[list[float]]:
    pts = [(x, y) for x, y in anillo]
    simplificado = _douglas_peucker(pts, TOLERANCIA_DP)
    if len(simplificado) < 4:
        simplificado = pts
    if simplificado[0] != simplificado[-1]:
        simplificado.append(simplificado[0])
    return [[round(x, DECIMALES), round(y, DECIMALES)] for x, y in simplificado]


# --------------------------------------------------------------------------- generación


def generar(dir_tmp: Path) -> None:
    lon_min, lat_min, lon_max, lat_max = BBOX_MX
    lons = np.arange(lon_min, lon_max, PASO_GRADOS)
    lats = np.arange(lat_min, lat_max, PASO_GRADOS)
    mascara = np.zeros((len(lats), len(lons)), dtype=bool)

    for i, nombre in enumerate(ESTADOS_TODOS, 1):
        ruta = dir_tmp / f"{nombre}.json"
        if not ruta.exists():
            print(f"✗ Falta {ruta.name}; corre --descargar primero", file=sys.stderr)
            sys.exit(1)
        poligonos = _poligonos_de_estado(ruta)
        for anillos in poligonos:
            _rasterizar_poligono(anillos, lons, lats, mascara)
        print(f"✔ {i:2d}/32 {nombre}: {len(poligonos)} polígonos rasterizados")

    print(f"Celdas cubiertas: {int(mascara.sum())} de {mascara.size} ({mascara.mean():.1%})")

    anillos_crudos = _trazar_contorno(mascara, lons, lats)
    # Descarta ruido de rejilla (huecos de 1 celda, artefactos): un anillo real de México a este
    # paso de rejilla cubre miles de celdas de perímetro; un umbral de 12 vértices es generoso.
    anillos_crudos = [a for a in anillos_crudos if len(a) >= 12]
    if not anillos_crudos:
        print("✗ No se trazó ningún anillo -- revisa la rasterización", file=sys.stderr)
        sys.exit(1)

    anillos_simplificados = [_simplificar_anillo(a) for a in anillos_crudos]
    multipoligono = [[anillo] for anillo in anillos_simplificados]  # cada anillo, su propio polígono

    asset = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "nombre": "México (silueta simplificada)",
                    "fuente": "PhantomInsights/mexico-geojson (CONABIO 2023, MIT), rasterizado y trazado",
                    "uso": "decorativo -- no usar para análisis ni como fuente de fronteras",
                },
                "geometry": {"type": "MultiPolygon", "coordinates": multipoligono},
            }
        ],
    }
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    ASSET.write_text(json.dumps(asset, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    peso_kb = ASSET.stat().st_size / 1024
    total_vertices = sum(len(a) for a in anillos_simplificados)
    print(
        f"✔ Asset escrito: {ASSET} ({len(anillos_simplificados)} anillo(s), "
        f"{total_vertices} vértices, {peso_kb:.0f} KB)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--descargar", metavar="DIR", help="Descarga los 32 estados a DIR")
    parser.add_argument("--generar", metavar="DIR", help="Genera el asset desde los archivos en DIR")
    args = parser.parse_args()

    if args.descargar:
        descargar(Path(args.descargar))
    if args.generar:
        generar(Path(args.generar))
    if not args.descargar and not args.generar:
        parser.print_help()


if __name__ == "__main__":
    main()
