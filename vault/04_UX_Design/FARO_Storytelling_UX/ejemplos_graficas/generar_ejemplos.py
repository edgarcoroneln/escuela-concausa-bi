"""Ejemplos de visualización de la especificación de datos de FARO (US-621).

Acompaña a ``02_Data_Visualization_Spec.md`` (Monserrat Xcaret Miranda Olivas, Equipo 3). Los
ejemplos demuestran FORMA Y LECTURA DEL DATO, no identidad visual: la paleta es neutra y
provisional, y la identidad la define ``03_Visual_Identity.md`` (Juan Carlos Macías Mayen).

Dos pasos, separados a propósito:

1. ``descargar`` consulta la API v1 y guarda la evidencia en un JSON **fuera del repositorio**
   (``%TEMP%/faro_evidencia_us621/`` o ``FARO_EVIDENCIA_DIR``). Sólo usa la biblioteca estándar.
   El token de acceso se toma de ``FARO_TOKEN`` o se pide con entrada oculta; **nunca se imprime
   ni se escribe** en disco.
2. ``graficar`` lee ese JSON y dibuja los PNG/SVG de esta carpeta. Requiere ``matplotlib``
   (versión fijada en ``requirements/celula-3.txt``).

Los cortes (``LINEA_DE_ALERTA``, ``RIESGO_ESTABLE``) y ``SCOPE_ENTIDADES`` se **leen del código
fuente** con ``ast``; no se teclean aquí, para no repetir el patrón de ``BUG-058``.

Uso, desde la raíz del repositorio::

    python vault/04_UX_Design/FARO_Storytelling_UX/ejemplos_graficas/generar_ejemplos.py descargar
    python vault/04_UX_Design/FARO_Storytelling_UX/ejemplos_graficas/generar_ejemplos.py graficar
"""

from __future__ import annotations

import argparse
import ast
import getpass
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CARPETA = Path(__file__).resolve().parent
RAIZ_REPO = CARPETA.parents[3]

API_URL_PRODUCCION = "https://faro-api-eanzfglvyq-uc.a.run.app"
TIMEOUT_S = 40
TAM_PAGINA = 100  # máximo que acepta `size` en /escuelas (openapi.v1.json)
TAM_EXPLORACION = 20

CODIGOS = ("D1", "D2", "D3", "D4", "D5", "D6")
#: D3 y D4 miden servicios PRESENTES (suben cuando la escuela está mejor); D1, D2, D5 y D6 suben
#: cuando la situación empeora. Regla 4 de `dbt/models/gold/features_escuela.sql:385-390`.
DRIVERS_INVERTIDOS = frozenset({"D3", "D4"})


# ---------------------------------------------------------------------------------------------
# Constantes leídas del código fuente (no se retetean)
# ---------------------------------------------------------------------------------------------


def leer_constante(ruta_relativa: str, nombre: str) -> tuple[Any, int]:
    """Devuelve ``(valor, línea)`` de una asignación de módulo, leída con ``ast``.

    Se lee el archivo en vez de importarlo para no arrastrar SQLAlchemy ni la configuración de
    la API, y se evita teclear el número aquí: si el dueño lo cambia, este script lo sigue.
    """
    ruta = RAIZ_REPO / ruta_relativa
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign):
            objetivos = [t.id for t in nodo.targets if isinstance(t, ast.Name)]
            valor = nodo.value
        elif isinstance(nodo, ast.AnnAssign) and isinstance(nodo.target, ast.Name):
            objetivos = [nodo.target.id]
            valor = nodo.value
        else:
            continue
        if nombre in objetivos and valor is not None:
            return ast.literal_eval(valor), nodo.lineno
    raise LookupError(f"No encontré `{nombre}` en {ruta_relativa}")


def constantes() -> dict[str, dict[str, Any]]:
    """Los tres valores de corte y alcance que usan los ejemplos, con su fuente citable."""
    fuentes = {
        "LINEA_DE_ALERTA": "src/api/repositorio_gold.py",
        "RIESGO_ESTABLE": "src/modelos/riesgo.py",
        "SCOPE_ENTIDADES": "src/modelos/generar_fixture.py",
    }
    salida = {}
    for nombre, ruta in fuentes.items():
        valor, linea = leer_constante(ruta, nombre)
        salida[nombre] = {"valor": list(valor) if isinstance(valor, tuple) else valor,
                          "fuente": f"{ruta}:{linea}"}
    return salida


# ---------------------------------------------------------------------------------------------
# Paso 1 — descargar (sólo biblioteca estándar)
# ---------------------------------------------------------------------------------------------


def obtener_token() -> str:
    """Toma el token de ``FARO_TOKEN`` o lo pide con entrada oculta. Nunca lo muestra."""
    token = os.environ.get("FARO_TOKEN", "").strip()
    if not token:
        token = getpass.getpass(
            "Pega tu access_token (no se muestra en pantalla ni se guarda) y presiona Enter: "
        ).strip()
    if token.startswith("{"):
        # Se pegó el TokenPair completo que devuelve /auth/callback: se toma sólo el access_token.
        try:
            token = str(json.loads(token).get("access_token", "")).strip()
        except json.JSONDecodeError:
            token = ""
    if token.lower().startswith("bearer "):
        token = token[len("bearer "):].strip()
    if not token:
        raise SystemExit("Sin access_token no hay consulta. Abre /api/v1/auth/login y vuelve a correr.")
    return token


class ClienteApi:
    """GET autenticado contra la API v1. Registra cada llamada SIN la cabecera del token."""

    def __init__(self, base: str, token: str) -> None:
        self._base = base.rstrip("/")
        self._token = token
        self.llamadas: list[dict[str, Any]] = []

    def get(self, ruta: str, params: dict[str, Any] | None = None,
            *, tolerar: tuple[int, ...] = ()) -> Any:
        """Devuelve el JSON de la respuesta. 401 detiene todo; los códigos en ``tolerar`` se
        devuelven como ``{"_error_http": código}`` para que queden en la evidencia."""
        consulta = f"?{urllib.parse.urlencode(params)}" if params else ""
        peticion = urllib.request.Request(
            f"{self._base}{ruta}{consulta}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
                "User-Agent": "faro-us621-evidencia/1.0",
            },
        )
        inicio = time.monotonic()
        estado: int | None = None
        try:
            with urllib.request.urlopen(peticion, timeout=TIMEOUT_S) as respuesta:
                estado = respuesta.status
                return json.loads(respuesta.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            estado = error.code
            if error.code == 401:
                raise SystemExit(
                    "La API respondió 401: el token no es válido o ya venció (dura 15 min). "
                    "Vuelve a abrir /api/v1/auth/login y corre el comando de nuevo."
                ) from None
            if error.code in tolerar:
                return {"_error_http": error.code}
            raise SystemExit(f"GET {ruta}{consulta} respondió {error.code}. Me detengo.") from None
        except urllib.error.URLError as error:
            raise SystemExit(f"No pude contactar la API ({error.reason}). Me detengo.") from None
        finally:
            self.llamadas.append({
                "get": f"{ruta}{consulta}",
                "http": estado,
                "segundos": round(time.monotonic() - inicio, 3),
            })


def presion(codigo: str, valor: float | None) -> float | None:
    """Valor en el eje común "más alto = más presión". ``None`` es SIN_DATO y se conserva."""
    if valor is None:
        return None
    return 1.0 - valor if codigo in DRIVERS_INVERTIDOS else valor


def argmax_orientado(detalle: dict[str, Any]) -> str | None:
    """Driver con más presión, con el desempate D1 > … > D6 de `features_escuela.sql:380`.

    Sólo se usa como CHEQUEO: el `driver_dominante` que se muestra es el de la API (ML-02).
    """
    candidatos = [
        (p, codigo)
        for codigo in CODIGOS
        if (p := presion(codigo, detalle.get(codigo.lower()))) is not None
    ]
    if not candidatos:
        return None
    return min(candidatos, key=lambda par: (-par[0], par[1]))[1]


def conjunto_en_riesgo(cliente: ClienteApi, linea: float) -> tuple[list[dict], list[dict]]:
    """Ordena desc por `indice_riesgo` y corta del lado cliente en la línea de alerta.

    `/escuelas` no filtra por riesgo; ordena con NULLS LAST (`repositorio_gold.py:208-211`), así
    que el primer valor nulo o menor que la línea cierra el conjunto.
    """
    en_riesgo: list[dict] = []
    paginas: list[dict] = []
    pagina = 1
    while True:
        datos = cliente.get("/api/v1/escuelas", {
            "order_by": "indice_riesgo", "order": "desc", "size": TAM_PAGINA, "page": pagina,
        })
        paginas.append(datos)
        for escuela in datos["items"]:
            riesgo = escuela.get("indice_riesgo")
            if riesgo is None or riesgo < linea:
                return en_riesgo, paginas
            en_riesgo.append(escuela)
        if not datos["items"] or pagina * datos["size"] >= datos["total"]:
            return en_riesgo, paginas
        pagina += 1


def chequeos(evidencia: dict[str, Any]) -> dict[str, Any]:
    """Comprobaciones de consistencia que el documento cita. No corrigen nada: sólo reportan."""
    kpis = evidencia["kpis"]
    conjunto = evidencia["conjunto_en_riesgo"]
    por_escuela = []
    for escuela in conjunto:
        cct = escuela["cct"]
        detalle = evidencia["detalle"].get(cct, {})
        prediccion = evidencia["prediccion"].get(cct, {})
        explicacion = evidencia["explicacion"].get(cct, {})
        contribuciones = explicacion.get("contribuciones") or {}
        por_escuela.append({
            "cct": cct,
            "indice_riesgo": escuela.get("indice_riesgo"),
            "dominante_api": escuela.get("driver_dominante"),
            "dominante_prediccion": prediccion.get("driver_dominante"),
            "argmax_orientado": argmax_orientado(detalle) if detalle else None,
            "riesgo_coincide": (prediccion.get("indice_riesgo") is not None
                                and abs(prediccion["indice_riesgo"] - escuela["indice_riesgo"]) < 1e-9),
            "id_ciclo_prediccion": prediccion.get("id_ciclo"),
            "shap_no_nulos": sum(v is not None for v in contribuciones.values()),
            "drivers_sin_dato": [c for c in CODIGOS if detalle.get(c.lower()) is None],
            "indice_completitud_drivers": detalle.get("indice_completitud_drivers"),
            "es_estimado_por_grupo": detalle.get("es_estimado_por_grupo"),
        })
    return {
        "conjunto_igual_a_kpis": len(conjunto) == kpis.get("escuelas_en_riesgo"),
        "tam_conjunto": len(conjunto),
        "kpis_escuelas_en_riesgo": kpis.get("escuelas_en_riesgo"),
        "d5_nulo_en_todas": all("D5" in e["drivers_sin_dato"] for e in por_escuela),
        "shap_nulo_en_todas": all(e["shap_no_nulos"] == 0 for e in por_escuela),
        "por_escuela": por_escuela,
    }


def carpeta_evidencia() -> Path:
    """Fuera del repositorio a propósito: la evidencia es local y no se versiona."""
    ruta = Path(os.environ.get("FARO_EVIDENCIA_DIR")
                or Path(tempfile.gettempdir()) / "faro_evidencia_us621")
    if RAIZ_REPO in ruta.resolve().parents or ruta.resolve() == RAIZ_REPO:
        raise SystemExit("La evidencia no se guarda dentro del repositorio. Usa otra carpeta.")
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta


def descargar(base: str) -> Path:
    """Consulta la API y guarda un JSON de evidencia fuera del repo. Devuelve su ruta."""
    corte = constantes()
    linea = float(corte["LINEA_DE_ALERTA"]["valor"])
    token = obtener_token()
    cliente = ClienteApi(base, token)
    local = datetime.now().astimezone()

    evidencia: dict[str, Any] = {"meta": {
        "consulta_local": local.isoformat(timespec="seconds"),
        "consulta_utc": local.astimezone(UTC).isoformat(timespec="seconds"),
        "api_url": base,
        "script": "vault/04_UX_Design/FARO_Storytelling_UX/ejemplos_graficas/generar_ejemplos.py",
        "constantes": corte,
    }}
    evidencia["meta"]["api_version"] = cliente.get("/api/v1/version")
    evidencia["kpis"] = cliente.get("/api/v1/kpis")
    conjunto, paginas = conjunto_en_riesgo(cliente, linea)
    evidencia["conjunto_en_riesgo"] = conjunto
    evidencia["escuelas_ordenadas_paginas"] = paginas

    evidencia["detalle"], evidencia["prediccion"], evidencia["explicacion"] = {}, {}, {}
    for escuela in conjunto:
        cct = urllib.parse.quote(escuela["cct"], safe="")
        evidencia["detalle"][escuela["cct"]] = cliente.get(f"/api/v1/escuelas/{cct}", tolerar=(404,))
        evidencia["prediccion"][escuela["cct"]] = cliente.get(
            f"/api/v1/predicciones/{cct}", tolerar=(404, 503))
        evidencia["explicacion"][escuela["cct"]] = cliente.get(
            f"/api/v1/predicciones/{cct}/explicacion", tolerar=(404, 503))

    evidencia["municipios"] = {
        cve: cliente.get(f"/api/v1/municipios/{urllib.parse.quote(cve, safe='')}", tolerar=(404,))
        for cve in sorted({e["cve_mun"] for e in conjunto})
    }

    # Pantalla 6: una página corta por entidad, con y sin filtro, para mostrar el nivel de atención
    # fuera del conjunto en riesgo. `/kpis` no acepta `nivel`: sólo entidad, municipio y ciclo.
    evidencia["exploracion"] = {}
    for cve_ent in corte["SCOPE_ENTIDADES"]["valor"]:
        evidencia["exploracion"][cve_ent] = {
            "escuelas": cliente.get("/api/v1/escuelas", {
                "cve_ent": cve_ent, "order_by": "indice_riesgo", "order": "desc",
                "size": TAM_EXPLORACION,
            }),
            "kpis": cliente.get("/api/v1/kpis", {"cve_ent": cve_ent}),
        }

    evidencia["meta"]["llamadas"] = cliente.llamadas
    evidencia["chequeos"] = chequeos(evidencia)

    destino = carpeta_evidencia() / f"evidencia_api_{local:%Y%m%d_%H%M%S}.json"
    destino.write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")
    imprimir_resumen(evidencia, destino)
    return destino


def imprimir_resumen(evidencia: dict[str, Any], destino: Path) -> None:
    """Resumen legible de la consulta (sin el token, que nunca llega aquí)."""
    meta, kpis, chk = evidencia["meta"], evidencia["kpis"], evidencia["chequeos"]
    print(f"\nConsulta: {meta['consulta_local']} (UTC {meta['consulta_utc']})")
    print(f"API: {meta['api_url']} - commit {meta['api_version'].get('commit')}")
    print(f"Llamadas: {len(meta['llamadas'])}, "
          f"codigos HTTP: {sorted({str(c['http']) for c in meta['llamadas']})}")
    print(f"/kpis sin filtros: {kpis}")
    print(f"Conjunto en riesgo por corte cliente: {chk['tam_conjunto']} escuelas; "
          f"/kpis.escuelas_en_riesgo = {chk['kpis_escuelas_en_riesgo']} -> "
          f"{'COINCIDE' if chk['conjunto_igual_a_kpis'] else 'NO COINCIDE'}")
    print(f"D5 nulo en todas: {chk['d5_nulo_en_todas']} - SHAP nulo en todas: {chk['shap_nulo_en_todas']}")
    print("\ncct        riesgo  dom_API dom_pred argmax  riesgo=  ciclo_pred  shap  sin_dato      compl  estimado")
    for e in chk["por_escuela"]:
        print(f"{e['cct']:<10} {e['indice_riesgo']:.4f}  {e['dominante_api']!s:<7} "
              f"{e['dominante_prediccion']!s:<8} {e['argmax_orientado']!s:<7} "
              f"{'si' if e['riesgo_coincide'] else 'NO':<8} {e['id_ciclo_prediccion']!s:<11} "
              f"{e['shap_no_nulos']:<5} {','.join(e['drivers_sin_dato']) or '-':<13} "
              f"{e['indice_completitud_drivers']!s:<6} {e['es_estimado_por_grupo']!s}")
    print(f"\nEvidencia guardada FUERA del repo en:\n  {destino}")


# ---------------------------------------------------------------------------------------------
# Paso 2 — graficar
# ---------------------------------------------------------------------------------------------


def evidencia_mas_reciente() -> Path:
    """El JSON de evidencia más nuevo de la carpeta local."""
    candidatos = sorted(carpeta_evidencia().glob("evidencia_api_*.json"))
    if not candidatos:
        raise SystemExit("No hay evidencia descargada. Corre primero el paso `descargar`.")
    return candidatos[-1]


#: Paleta NEUTRA Y PROVISIONAL: grises más un solo tono para la magnitud. No es identidad visual;
#: la define `03_Visual_Identity.md` (Juan Carlos Macías). `validar_paleta()` mide el contraste.
PALETA = {
    "fondo": "#FFFFFF",
    "tinta": "#1A1A1A",
    "tinta_2": "#4D4C48",
    "regla": "#C9C8C1",
    "panel": "#F6F6F3",
    "sin_dato_fondo": "#F3F3F0",
    "sin_dato_trama": "#6E6D68",
    "presion_0": "#E8EDF2",
    "presion_1": "#1F3A52",
    "barra": "#5A7690",
    "barra_dominante": "#1F3A52",
}
FUENTE = "DejaVu Sans"

NOMBRE_DRIVER = {
    "D1": "Pobreza y rezago", "D2": "Inseguridad del entorno", "D3": "Infraestructura escolar",
    "D4": "Conectividad digital", "D5": "Estrés hídrico", "D6": "Calidad del aire",
}
#: Cómo se rotula cada driver en el eje de presión (D3 y D4 como falta, §4.1 del documento).
ETIQUETA_PRESION = {
    "D1": "Pobreza y rezago", "D2": "Inseguridad", "D3": "Falta de infraestructura",
    "D4": "Falta de conectividad", "D5": "Estrés hídrico", "D6": "Calidad del aire",
}
DRIVERS_MUNICIPALES = frozenset({"D1", "D2"})
MOTIVO_SIN_DATO = {
    "D1": "sin dato de rezago para su municipio",
    "D2": "sin dato de delitos para su municipio",
    "D3": "sin registro de servicios en el censo CEMABE",
    "D4": "sin registro de conectividad en el censo CEMABE",
    "D5": "aún no hay fuente de estrés hídrico integrada",
    "D6": "no hay estación de calidad del aire a 15 km o menos",
}
#: Etiqueta de las cuatro entidades de `SCOPE_ENTIDADES` (clave INEGI → nombre). Sólo rótulo.
NOMBRE_ENTIDAD = {"09": "Ciudad de México", "15": "Estado de México", "19": "Nuevo León",
                  "14": "Jalisco"}
ICONO_NIVEL = {"alta": "▲", "media": "■", "baja": "●"}


def _canal_lineal(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(color: str) -> float:
    """Luminancia relativa WCAG 2.1 de un color `#RRGGBB`."""
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * _canal_lineal(r) + 0.7152 * _canal_lineal(g) + 0.0722 * _canal_lineal(b)


def contraste(a: str, b: str) -> float:
    """Razón de contraste WCAG entre dos colores."""
    alta, baja = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (alta + 0.05) / (baja + 0.05)


def mezcla(a: str, b: str, t: float) -> str:
    """Interpolación lineal en sRGB, `t` en [0, 1]."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb, strict=True))


def color_presion(p: float) -> tuple[str, str]:
    """Relleno de una celda de presión y la tinta de su número, con contraste de texto ≥ 4.5:1.

    Si la interpolación cae en la franja donde ni la tinta oscura ni la blanca llegan a 4.5:1, el
    relleno se aclara u oscurece lo mínimo necesario; el orden de claro a oscuro se conserva.
    """
    relleno = mezcla(PALETA["presion_0"], PALETA["presion_1"], p)
    tinta = max((PALETA["tinta"], "#FFFFFF"), key=lambda t: contraste(relleno, t))
    hacia = "#FFFFFF" if tinta == PALETA["tinta"] else "#000000"
    for _ in range(60):
        if contraste(relleno, tinta) >= 4.5:
            break
        relleno = mezcla(relleno, hacia, 0.04)
    return relleno, tinta


def validar_paleta() -> list[str]:
    """Comprueba WCAG 2.1 AA de la paleta: texto ≥ 4.5:1 y marcas ≥ 3:1. Detiene si falla."""
    fondo = PALETA["fondo"]
    reglas = [
        ("tinta sobre fondo", contraste(PALETA["tinta"], fondo), 4.5),
        ("tinta secundaria sobre fondo", contraste(PALETA["tinta_2"], fondo), 4.5),
        ("tinta secundaria sobre panel", contraste(PALETA["tinta_2"], PALETA["panel"]), 4.5),
        ("barra sobre fondo", contraste(PALETA["barra"], fondo), 3.0),
        ("barra dominante sobre fondo", contraste(PALETA["barra_dominante"], fondo), 3.0),
        ("trama SIN_DATO sobre su fondo",
         contraste(PALETA["sin_dato_trama"], PALETA["sin_dato_fondo"]), 3.0),
        ("número en celda de presión (peor caso)",
         min(contraste(*color_presion(i / 100)) for i in range(101)), 4.5),
    ]
    informe, fallas = [], []
    for nombre, valor, minimo in reglas:
        linea = f"{nombre}: {valor:.2f}:1 (mínimo {minimo}:1)"
        informe.append(linea)
        if valor < minimo:
            fallas.append(linea)
    if fallas:
        raise SystemExit("La paleta no cumple WCAG 2.1 AA:\n  " + "\n  ".join(fallas))
    return informe


def nivel_atencion(riesgo: float, linea: float, estable: float) -> str:
    """Nivel de atención de `PLAN_TRABAJO` §3.quater, con los cortes leídos del código."""
    if riesgo >= linea:
        return "alta"
    if riesgo >= estable:
        return "media"
    return "baja"


def top3(conjunto: list[dict[str, Any]]) -> tuple[list[tuple[int, str, int]], int]:
    """Top 3 de §5.1 del documento, sobre el conjunto COMPLETO de escuelas en riesgo.

    Devuelve `[(lugar, driver, k)]` y cuántas escuelas no tienen driver dominante. Rango con empates
    compartidos (1, 2, 2, 4): entran todos los drivers con lugar ≤ 3 y `k > 0`, así que un empate en
    el tercer lugar muestra más de tres. Dentro de un empate, orden de catálogo D1 → D6.
    """
    conteo = dict.fromkeys(CODIGOS, 0)
    sin_dominante = 0
    for escuela in conjunto:
        codigo = escuela.get("driver_dominante")
        if codigo in conteo:
            conteo[codigo] += 1
        else:
            sin_dominante += 1
    ordenados = sorted(conteo.items(), key=lambda par: (-par[1], par[0]))
    resultado = []
    for codigo, k in ordenados:
        lugar = 1 + sum(1 for _, otro in ordenados if otro > k)
        if k > 0 and lugar <= 3:
            resultado.append((lugar, codigo, k))
    return resultado, sin_dominante


class Caso:
    """Una escuela en riesgo con todo lo que las pantallas necesitan, tal como vino de la API."""

    def __init__(self, escuela: dict, detalle: dict, prediccion: dict, explicacion: dict,
                 municipio: dict) -> None:
        self.cct: str = escuela["cct"]
        self.nombre: str = escuela["nombre"]
        self.nivel: str = escuela["nivel"].capitalize()
        self.cve_mun: str = escuela["cve_mun"]
        self.municipio: str = municipio.get("nombre_municipio") or f"municipio {self.cve_mun}"
        self.matricula: int = escuela["matricula_total"]
        self.riesgo: float = escuela["indice_riesgo"]
        self.dominante: str | None = escuela.get("driver_dominante")
        self.publicados = {c: detalle.get(c.lower()) for c in CODIGOS}
        self.completitud: float = detalle.get("indice_completitud_drivers", 0.0)
        self.sostenimiento: str = str(detalle.get("sostenimiento", "")).capitalize()
        self.estimado_por_grupo = detalle.get("es_estimado_por_grupo")
        self.recomendacion: str | None = prediccion.get("recomendacion")
        self.contribuciones = explicacion.get("contribuciones") or {}
        self.pobreza_pct = municipio.get("pobreza_pct")

    def presion(self, codigo: str) -> float | None:
        return presion(codigo, self.publicados[codigo])

    @property
    def pistas(self) -> int:
        """Pistas con dato, "k de 6" (`indice_completitud_drivers × 6`)."""
        return round(self.completitud * 6)


def _fecha(iso: str) -> str:
    meses = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
    momento = datetime.fromisoformat(iso)
    return f"{momento.day}-{meses[momento.month - 1]}-{momento.year} {momento:%H:%M} (UTC−06:00)"


def _pct(valor: float, decimales: int = 1) -> str:
    return f"{valor * 100:.{decimales}f} %".replace("-", "−")


def _corta(texto: str, largo: int) -> str:
    """Recorta un nombre largo y lo dice con "…"; nunca lo corta en silencio."""
    return texto if len(texto) <= largo else texto[:largo - 1].rstrip() + "…"


def _enumera(elementos: list[str]) -> str:
    """"a", "a y b", "a, b y c"."""
    if len(elementos) <= 1:
        return "".join(elementos)
    return ", ".join(elementos[:-1]) + " y " + elementos[-1]


class Lienzo:
    """Utilidades de dibujo compartidas por los seis ejemplos."""

    def __init__(self, evidencia: dict[str, Any], destino: Path) -> None:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib import patches

        self.plt, self.patches = plt, patches
        plt.rcParams.update({
            "font.family": FUENTE,
            "svg.fonttype": "none",          # el texto queda editable en el SVG
            "svg.hashsalt": "faro-us621",    # ids estables entre corridas
            "hatch.linewidth": 0.9,
        })
        self.evidencia = evidencia
        self.destino = destino
        meta = evidencia["meta"]
        self.fecha = _fecha(meta["consulta_local"])
        self.commit = str(meta["api_version"].get("commit", ""))[:7]
        cortes = meta["constantes"]
        self.linea = float(cortes["LINEA_DE_ALERTA"]["valor"])
        self.estable = float(cortes["RIESGO_ESTABLE"]["valor"])
        self.fuente_linea = cortes["LINEA_DE_ALERTA"]["fuente"]
        self.fuente_estable = cortes["RIESGO_ESTABLE"]["fuente"]

    def figura(self, ancho: float, alto: float):
        return self.plt.figure(figsize=(ancho, alto), facecolor=PALETA["fondo"])

    def ejes(self, fig, rect: list[float], ancho: float, alto: float):
        """Ejes en unidades propias, con `y` hacia abajo, sin marcos."""
        ax = fig.add_axes(rect)
        ax.set_xlim(0, ancho)
        ax.set_ylim(alto, 0)
        ax.axis("off")
        return ax

    def texto(self, destino, x, y, s, *, size=10, color=None, weight="normal", **kw):
        return destino.text(x, y, s, fontsize=size, color=color or PALETA["tinta"],
                            fontweight=weight, **kw)

    def sin_dato(self, ax, x, y, ancho, alto, etiqueta: str | None, size=8.5):
        """Rectángulo rayado de `SIN_DATO`, con su texto sobre una pastilla blanca."""
        ax.add_patch(self.patches.Rectangle(
            (x, y), ancho, alto, facecolor=PALETA["sin_dato_fondo"],
            edgecolor=PALETA["sin_dato_trama"], hatch="////", linewidth=0))
        if etiqueta:
            self.texto(ax, x + ancho / 2, y + alto / 2, etiqueta, size=size,
                       color=PALETA["tinta_2"], ha="center", va="center",
                       bbox={"boxstyle": "round,pad=0.25", "fc": PALETA["fondo"], "ec": "none"})

    def pie(self, fig, fuente: str, campos: str, extra: str = "") -> None:
        """Pie obligatorio: fuente, campos, fecha, entorno y aviso de paleta provisional."""
        import textwrap
        lineas = [
            f"Fuente: {fuente} · campos: {campos}.",
            (f"Consulta del {self.fecha} a la API v1 en producción (commit {self.commit}). "
             f"Cortes leídos del código: LINEA_DE_ALERTA ({self.fuente_linea}) y "
             f"RIESGO_ESTABLE ({self.fuente_estable})."),
            ("Ejemplo de FORMA Y LECTURA DEL DATO, no mockup ni identidad visual: paleta neutra y "
             "provisional; la identidad la define 03_Visual_Identity.md (Juan Carlos Macías)."),
        ]
        if extra:
            lineas.insert(1, extra)
        texto = "\n".join(textwrap.fill(linea, 190) for linea in lineas)
        fig.text(0.03, 0.012, texto, fontsize=7.6, color=PALETA["tinta_2"], va="bottom",
                 linespacing=1.35)

    def guardar(self, fig, nombre: str) -> list[Path]:
        rutas = []
        for extension, meta in (("png", {"Software": None}), ("svg", {"Date": None})):
            ruta = self.destino / f"{nombre}.{extension}"
            fig.savefig(ruta, dpi=150, facecolor=PALETA["fondo"], metadata=meta)
            rutas.append(ruta)
        self.plt.close(fig)
        return rutas


def _casos(evidencia: dict[str, Any]) -> list[Caso]:
    casos = [
        Caso(e, evidencia["detalle"].get(e["cct"], {}), evidencia["prediccion"].get(e["cct"], {}),
             evidencia["explicacion"].get(e["cct"], {}),
             evidencia["municipios"].get(e["cve_mun"], {}))
        for e in evidencia["conjunto_en_riesgo"]
    ]
    # Valores iguales no se ordenan entre sí por azar: después del índice, por nombre y CCT.
    return sorted(casos, key=lambda c: (-c.riesgo, c.nombre, c.cct))


def _frase_situacion(casos: list[Caso]) -> str:
    """Copy dinámica de la P2 (§3.2): nunca contradice a la matriz."""
    dominantes = {c.dominante for c in casos if c.dominante}
    if len(dominantes) >= 2:
        return ("Comparten el riesgo, pero no la situación: el factor que más destaca cambia de una "
                "escuela a otra.")
    if len(dominantes) == 1:
        codigo = dominantes.pop()
        return f"En las N escuelas destaca el mismo factor: {NOMBRE_DRIVER[codigo].lower()}. " \
               "Sus otras pistas sí difieren."
    return "Ninguna escuela tiene todavía un driver dominante: es una pista pendiente."


def ejemplo_p2(lz: Lienzo, casos: list[Caso]) -> list[Path]:
    """P2 — matriz de casos: N escuelas × 6 drivers, con riesgo, matrícula y evidencia."""
    import textwrap
    kpis = lz.evidencia["kpis"]
    universo = lz.evidencia["escuelas_ordenadas_paginas"][0]["total"]
    fig = lz.figura(16, 10.2)
    fig.text(0.03, 0.962, "Pantalla 2 · Panorama de las escuelas en riesgo — visualización "
             "principal (ejemplo con datos reales)", fontsize=10.5, color=PALETA["tinta_2"])
    fig.text(0.03, 0.915, "N escuelas están en riesgo. Tenemos N casos por investigar.",
             fontsize=21, fontweight="bold", color=PALETA["tinta"])
    fig.text(0.03, 0.877, _frase_situacion(casos), fontsize=13.5, color=PALETA["tinta"])

    datos = [
        (f"{kpis['matricula_total']:,}",
         f"alumnos inscritos en las {universo:,} escuelas del alcance (4 entidades)"),
        (_pct(kpis["variacion_matricula"]),
         ("variación de la matrícula del alcance respecto al ciclo anterior "
          "(agregada, no por escuela)")),
        (f"{kpis['indice_completitud_drivers'] * 6:.1f} de 6",
         "pistas con dato, en promedio, por escuela del alcance"),
    ]
    for i, (cifra, rotulo) in enumerate(datos):
        x = 0.03 + i * 0.31
        fig.text(x, 0.822, cifra, fontsize=17, fontweight="bold", color=PALETA["tinta"])
        fig.text(x, 0.812, textwrap.fill(rotulo, 58), fontsize=8.8, color=PALETA["tinta_2"],
                 va="top", linespacing=1.3)

    # Retícula en unidades: 18.6 de ancho; encabezado de 1.35 y filas de 0.86.
    fila, cabeza = 0.86, 1.35
    alto = cabeza + fila * len(casos) + 0.15
    ancho = 18.6
    ax = lz.ejes(fig, [0.03, 0.225, 0.94, 0.52], ancho, alto)
    x_riesgo, x_mat, x_drv, w_drv, x_ev = 4.75, 6.75, 8.3, 1.36, 16.65

    encabezados = (
        (0.05, "Escuela", "left"),
        (x_riesgo + 0.9, "Índice de riesgo\ny nivel de atención", "center"),
        (x_mat + 1.1, "Matrícula", "right"),
        (x_ev + 0.9, "Evidencia\ndisponible", "center"),
    )
    for x, s, ha in encabezados:
        lz.texto(ax, x, cabeza - 0.12, s, size=9.5, weight="bold", ha=ha, va="bottom")
    lz.texto(ax, x_drv + 3 * w_drv, 0.02, "Presión de cada pista · 0 = menor observada · "
             "1 = mayor observada", size=9, color=PALETA["tinta_2"], ha="center", va="top")
    for j, codigo in enumerate(CODIGOS):
        rotulo = f"{codigo}\n{textwrap.fill(ETIQUETA_PRESION[codigo], 12, break_long_words=False)}"
        if codigo in DRIVERS_MUNICIPALES:
            rotulo += "\n(municipal)"
        lz.texto(ax, x_drv + j * w_drv + w_drv / 2, cabeza - 0.12, rotulo, size=8.4,
                 weight="bold", ha="center", va="bottom", linespacing=1.15)
    ax.plot([0, ancho], [cabeza, cabeza], color=PALETA["regla"], linewidth=1)

    for i, caso in enumerate(casos):
        y = cabeza + i * fila
        yc = y + fila / 2
        if i:
            ax.plot([0, x_drv - 0.1], [y, y], color=PALETA["regla"], linewidth=0.5)
        lz.texto(ax, 0.05, yc - 0.13, _corta(caso.nombre, 44), size=10, weight="bold",
                 va="center")
        lz.texto(ax, 0.05, yc + 0.2, f"{caso.municipio} · {caso.nivel} · {caso.cct}", size=8.4,
                 color=PALETA["tinta_2"], va="center")
        nivel = nivel_atencion(caso.riesgo, lz.linea, lz.estable)
        lz.texto(ax, x_riesgo + 0.9, yc - 0.13, f"{caso.riesgo:.3f}", size=12, weight="bold",
                 ha="center", va="center")
        lz.texto(ax, x_riesgo + 0.9, yc + 0.2, f"{ICONO_NIVEL[nivel]} atención {nivel}", size=8.6,
                 ha="center", va="center")
        lz.texto(ax, x_mat + 1.1, yc, f"{caso.matricula:,}", size=11, ha="right", va="center")

        for j, codigo in enumerate(CODIGOS):
            x = x_drv + j * w_drv + 0.04
            w, h, y0 = w_drv - 0.08, fila - 0.08, y + 0.04
            p = caso.presion(codigo)
            if p is None:
                lz.sin_dato(ax, x, y0, w, h, "sin dato", size=8)
                continue
            relleno, tinta = color_presion(p)
            ax.add_patch(lz.patches.Rectangle((x, y0), w, h, facecolor=relleno, linewidth=0))
            dominante = codigo == caso.dominante
            lz.texto(ax, x + w / 2, y0 + h * (0.4 if dominante else 0.5), f"{p:.2f}", size=12.5,
                     weight="bold", color=tinta, ha="center", va="center")
            if dominante:
                ax.add_patch(lz.patches.Rectangle((x, y0), w, h, fill=False,
                                                  edgecolor=PALETA["tinta"], linewidth=2.6))
                lz.texto(ax, x + w / 2, y0 + h * 0.8, "▲ dominante", size=7.8, weight="bold",
                         color=tinta, ha="center", va="center")

        lz.texto(ax, x_ev + 0.9, yc - 0.17, f"{caso.pistas} de 6", size=11, weight="bold",
                 ha="center", va="center")
        for j, codigo in enumerate(CODIGOS):
            xs, ys, lado = x_ev + 0.27 + j * 0.23, yc + 0.08, 0.17
            if caso.publicados[codigo] is None:
                ax.add_patch(lz.patches.Rectangle((xs, ys), lado, lado, facecolor=PALETA["fondo"],
                                                  edgecolor=PALETA["sin_dato_trama"],
                                                  hatch="////", linewidth=0.6))
            else:
                ax.add_patch(lz.patches.Rectangle((xs, ys), lado, lado,
                                                  facecolor=PALETA["tinta_2"], linewidth=0))

    # Leyenda
    ly = 0.185
    fig.text(0.03, ly, "Cómo se lee", fontsize=9.5, fontweight="bold", color=PALETA["tinta"])
    for k in range(11):
        relleno, _ = color_presion(k / 10)
        fig.add_artist(lz.patches.Rectangle((0.105 + k * 0.016, ly - 0.004), 0.016, 0.022,
                                                transform=fig.transFigure, facecolor=relleno,
                                                linewidth=0))
    fig.text(0.105, ly - 0.02, "0", fontsize=8, color=PALETA["tinta_2"])
    fig.text(0.281, ly - 0.02, "1", fontsize=8, color=PALETA["tinta_2"], ha="right")
    fig.text(0.295, ly, "presión relativa (el número va en la celda)", fontsize=8.6,
             color=PALETA["tinta_2"])
    fig.text(0.03, ly - 0.045, "▲ con contorno = driver dominante (ML-02)   ·   rayado = "
             "SIN_DATO, pista que no pudimos verificar   ·   D1 y D2 son valores del municipio   ·"
             "   D3 y D4 = falta (1 − servicios presentes)", fontsize=8.6,
             color=PALETA["tinta_2"])
    lz.pie(fig, "GET /api/v1/kpis (sin filtros) · GET /api/v1/escuelas?order_by=indice_riesgo&"
           "order=desc&size=100 con corte en LINEA_DE_ALERTA · GET /api/v1/escuelas/{cct} por fila "
           "· GET /api/v1/municipios/{cve_mun}",
           "escuelas_en_riesgo, matricula_total, variacion_matricula, indice_completitud_drivers; "
           "cct, nombre, nivel, cve_mun, matricula_total, indice_riesgo, driver_dominante; d1…d6; "
           "nombre_municipio",
           extra="N se resuelve en vivo de /kpis.escuelas_en_riesgo; en la copy de los mockups va "
                 "como N, nunca como número tecleado.")
    return lz.guardar(fig, "P2_matriz_casos")


def _pista_riesgo(lz: Lienzo, ax, x0: float, ancho: float, yc: float, riesgo: float,
                  nivel: str) -> None:
    """Pista 0–1 con los dos cortes marcados y el índice como marca de forma del nivel."""
    ax.plot([x0, x0 + ancho], [yc, yc], color=PALETA["regla"], linewidth=3,
            solid_capstyle="round")
    for corte in (lz.estable, lz.linea):
        ax.plot([x0 + ancho * corte] * 2, [yc - 0.16, yc + 0.16], color=PALETA["tinta_2"],
                linewidth=1)
    marca = {"alta": "^", "media": "s", "baja": "o"}[nivel]
    ax.plot([x0 + ancho * riesgo], [yc], marker=marca, markersize=9, color=PALETA["tinta"],
            markeredgecolor=PALETA["fondo"], markeredgewidth=1.5)


def ejemplo_p3(lz: Lienzo, casos: list[Caso]) -> list[Path]:
    """P3 — lista de casos con el índice en número y en una pista 0–1 con la línea de alerta."""
    fig = lz.figura(14, 8.6)
    fig.text(0.03, 0.955, "Pantalla 3 · Selección de caso (ejemplo con datos reales)",
             fontsize=10.5, color=PALETA["tinta_2"])
    fig.text(0.03, 0.905, "Elige una escuela para abrir su expediente.", fontsize=19,
             fontweight="bold", color=PALETA["tinta"])
    fig.text(0.03, 0.868, "No necesitas revisarlas todas: puedes investigar una y seguir.",
             fontsize=12.5, color=PALETA["tinta"])
    fila, cabeza, ancho = 0.9, 0.9, 16.0
    alto = cabeza + fila * len(casos)
    ax = lz.ejes(fig, [0.03, 0.215, 0.94, 0.615], ancho, alto)
    x_pista, w_pista = 6.0, 5.6
    lz.texto(ax, 0.05, cabeza - 0.15, "Escuela", size=9.5, weight="bold", va="bottom")
    lz.texto(ax, 5.2, cabeza - 0.15, "Índice", size=9.5, weight="bold", va="bottom", ha="center")
    for valor, rotulo in ((0.0, "0"), (lz.estable, f"{lz.estable:.2f}"),
                          (lz.linea, f"{lz.linea:.2f} línea de alerta"), (1.0, "1")):
        lz.texto(ax, x_pista + w_pista * valor, cabeza - 0.15, rotulo, size=8.4,
                 color=PALETA["tinta_2"], ha="center", va="bottom")
    for tramo, (a, b) in (("baja", (0, lz.estable)), ("media", (lz.estable, lz.linea)),
                          ("alta", (lz.linea, 1.0))):
        lz.texto(ax, x_pista + w_pista * (a + b) / 2, cabeza - 0.5, f"atención {tramo}",
                 size=7.8, color=PALETA["tinta_2"], ha="center", va="bottom", style="italic")
    lz.texto(ax, 12.3, cabeza - 0.15, "Nivel de atención", size=9.5, weight="bold", va="bottom")
    ax.plot([0, ancho], [cabeza, cabeza], color=PALETA["regla"], linewidth=1)

    for i, caso in enumerate(casos):
        y = cabeza + i * fila
        yc = y + fila / 2
        if i:
            ax.plot([0, ancho], [y, y], color=PALETA["regla"], linewidth=0.5)
        nivel = nivel_atencion(caso.riesgo, lz.linea, lz.estable)
        lz.texto(ax, 0.05, yc - 0.14, _corta(caso.nombre, 44), size=10.5, weight="bold",
                 va="center")
        lz.texto(ax, 0.05, yc + 0.2, f"{caso.municipio} · {caso.nivel} · {caso.cct}", size=8.6,
                 color=PALETA["tinta_2"], va="center")
        lz.texto(ax, 5.2, yc, f"{caso.riesgo:.3f}", size=12, weight="bold", ha="center",
                 va="center")
        _pista_riesgo(lz, ax, x_pista, w_pista, yc, caso.riesgo, nivel)
        lz.texto(ax, 12.3, yc, f"{ICONO_NIVEL[nivel]} Atención {nivel}", size=10.5, va="center")
        ax.add_patch(lz.patches.FancyBboxPatch((14.25, yc - 0.22), 1.65, 0.44,
                                               boxstyle="round,pad=0.02,rounding_size=0.12",
                                               facecolor=PALETA["fondo"],
                                               edgecolor=PALETA["tinta"], linewidth=1))
        lz.texto(ax, 15.075, yc, "Abrir expediente →", size=8.6, ha="center", va="center")
    repetidos = len(casos) - len({c.riesgo for c in casos})
    nota = ("Las escuelas con el mismo índice van juntas y en orden alfabético: la lista no "
            "inventa un orden entre valores iguales." if repetidos else "")
    fig.text(0.03, 0.175, nota, fontsize=9, color=PALETA["tinta_2"])
    lz.pie(fig, "los mismos datos que la P2 (GET /api/v1/escuelas?order_by=indice_riesgo&order="
           "desc&size=100 y GET /api/v1/municipios/{cve_mun}); ninguna llamada nueva",
           "cct, nombre, nivel, cve_mun, indice_riesgo, nombre_municipio; nivel de atención "
           "derivado en Front (PLAN_TRABAJO §3.quater)")
    return lz.guardar(fig, "P3_seleccion_caso")


def ejemplo_p4(lz: Lienzo, caso: Caso) -> list[Path]:
    """P4 — expediente: barras de presión D1…D6 en orden fijo, dominante por forma y etiqueta."""
    import textwrap
    fig = lz.figura(15, 9.6)
    nivel = nivel_atencion(caso.riesgo, lz.linea, lz.estable)
    fig.text(0.03, 0.958, "Pantalla 4 · Expediente de una escuela (ejemplo con datos reales)",
             fontsize=10.5, color=PALETA["tinta_2"])
    nombre = textwrap.fill(caso.nombre, 30)
    fig.text(0.03, 0.905, nombre, fontsize=18, fontweight="bold", color=PALETA["tinta"],
             va="top")
    fig.text(0.03, 0.905 - 0.042 * (nombre.count("\n") + 1) - 0.02,
             f"{caso.cct} · {caso.municipio} · {caso.nivel} · {caso.sostenimiento}",
             fontsize=10.5, color=PALETA["tinta_2"], va="top")
    fig.text(0.03, 0.745, "Índice de riesgo", fontsize=10, color=PALETA["tinta_2"])
    fig.text(0.03, 0.688, f"{caso.riesgo:.3f}", fontsize=30, fontweight="bold",
             color=PALETA["tinta"])
    fig.text(0.155, 0.700, f"{ICONO_NIVEL[nivel]} Atención {nivel}", fontsize=14,
             fontweight="bold", color=PALETA["tinta"])
    explica = ("Qué calcula: traduce a una escala de 0 a 1 la variación de matrícula que el modelo "
               f"ML-01 proyecta para el próximo ciclo. {lz.estable:.2f} es una escuela que conserva "
               "su matrícula; 0.60, una que perdería 5 %. Nivel de atención: alta desde "
               f"{lz.linea:.2f} (línea de alerta), media desde {lz.estable:.2f}, baja debajo. "
               "Es un corte de presentación, no la columna «prioridad» de Gold.")
    fig.text(0.03, 0.668, textwrap.fill(explica, 58), fontsize=8.8, color=PALETA["tinta_2"],
             va="top", linespacing=1.35)
    estimado = "sin dato" if caso.estimado_por_grupo is None else (
        "sí" if caso.estimado_por_grupo else "no")
    fig.text(0.03, 0.49, f"Estimación por grupo: {estimado}", fontsize=9.5, color=PALETA["tinta"])
    if caso.estimado_por_grupo is None:
        fig.text(0.03, 0.47, "El contrato expone el campo, pero la API aún lo devuelve vacío.",
                 fontsize=8.4, color=PALETA["tinta_2"])

    tarjeta = fig.add_axes([0.03, 0.2, 0.33, 0.235])
    tarjeta.set_xlim(0, 1)
    tarjeta.set_ylim(0, 1)
    tarjeta.axis("off")
    tarjeta.add_patch(lz.patches.FancyBboxPatch((0.01, 0.02), 0.98, 0.96,
                                                boxstyle="round,pad=0,rounding_size=0.04",
                                                facecolor=PALETA["panel"],
                                                edgecolor=PALETA["regla"], linewidth=1))
    tarjeta.text(0.06, 0.84, "Recomendación", fontsize=11, fontweight="bold",
                 color=PALETA["tinta"], va="top")
    dom = caso.dominante or "—"
    tarjeta.text(0.06, 0.68, f"Asociada al driver dominante: {NOMBRE_DRIVER.get(dom, 'sin dato')}",
                 fontsize=8.8, color=PALETA["tinta_2"], va="top")
    tarjeta.text(0.06, 0.52, textwrap.fill(caso.recomendacion or "SIN_DATO", 42), fontsize=11.5,
                 color=PALETA["tinta"], va="top", linespacing=1.3)

    # Panel derecho: barras de presión
    fig.text(0.42, 0.905, "¿Qué pista destaca en esta escuela?", fontsize=15, fontweight="bold",
             color=PALETA["tinta"], va="top")
    fig.text(0.42, 0.855, f"Evidencia disponible: {caso.pistas} de 6 pistas", fontsize=10.5,
             color=PALETA["tinta"])
    for j, codigo in enumerate(CODIGOS):
        con_dato = caso.publicados[codigo] is not None
        fig.add_artist(lz.patches.Rectangle(
            (0.60 + j * 0.019, 0.852), 0.014, 0.02, transform=fig.transFigure,
            facecolor=PALETA["tinta_2"] if con_dato else PALETA["fondo"],
            edgecolor=PALETA["sin_dato_trama"], hatch=None if con_dato else "////",
            linewidth=0 if con_dato else 0.6))

    ax = fig.add_axes([0.42, 0.33, 0.55, 0.5])
    ax.set_xlim(-0.72, 1.16)
    ax.set_ylim(5.6, -0.6)
    ax.axis("off")
    for x, rotulo in ((0, "0"), (0.5, "0.5"), (1, "1")):
        ax.plot([x, x], [-0.45, 5.5], color=PALETA["regla"], linewidth=0.6, zorder=0)
        ax.text(x, 5.58, rotulo, fontsize=8.4, color=PALETA["tinta_2"], ha="center", va="top")
    ax.text(0, -0.52, "0 = menor presión observada", fontsize=8.2, color=PALETA["tinta_2"],
            ha="left", va="bottom")
    ax.text(1, -0.52, "1 = mayor presión observada", fontsize=8.2, color=PALETA["tinta_2"],
            ha="right", va="bottom")
    for i, codigo in enumerate(CODIGOS):
        dominante = codigo == caso.dominante
        prefijo = "▲ " if dominante else ""
        ax.text(-0.7, i - 0.08, f"{prefijo}{codigo} {ETIQUETA_PRESION[codigo]}", fontsize=10,
                fontweight="bold" if dominante else "normal", color=PALETA["tinta"], va="center")
        secundario = ""
        if codigo in DRIVERS_MUNICIPALES:
            secundario = "valor municipal"
        valor = caso.publicados[codigo]
        if codigo in DRIVERS_INVERTIDOS and valor is not None:
            secundario = f"servicios presentes: {valor:.2f}"
        if secundario:
            ax.text(-0.7, i + 0.24, secundario, fontsize=8.2, color=PALETA["tinta_2"],
                    va="center")
        p = caso.presion(codigo)
        if p is None:
            lz.sin_dato(ax, 0, i - 0.3, 1, 0.6,
                        f"SIN DATO — pista que no pudimos verificar\n{MOTIVO_SIN_DATO[codigo]}",
                        size=7.9)
            continue
        color = PALETA["barra_dominante"] if dominante else PALETA["barra"]
        ax.add_patch(lz.patches.Rectangle((0, i - 0.24), max(p, 0.004), 0.48, facecolor=color,
                                          linewidth=0))
        ax.text(p + 0.015, i, f"{p:.2f}", fontsize=10.5, fontweight="bold",
                color=PALETA["tinta"], va="center")
        if dominante and p > 0.62:
            # No cabe a la derecha: va dentro de la barra, en blanco (11.8:1 sobre el tono).
            ax.text(p - 0.02, i, "Driver dominante", fontsize=9, fontweight="bold",
                    color=PALETA["fondo"], ha="right", va="center")
        elif dominante:
            ax.text(p + 0.135, i, "Driver dominante", fontsize=9, fontweight="bold",
                    color=PALETA["tinta"], va="center",
                    bbox={"boxstyle": "round,pad=0.3", "fc": PALETA["fondo"],
                          "ec": PALETA["tinta"], "lw": 1})

    nota_d1 = ""
    if caso.pobreza_pct is not None and caso.publicados["D1"] is not None:
        nota_d1 = (f"Contexto del municipio (CONEVAL): en {caso.municipio}, "
                   f"{caso.pobreza_pct:.1f} % de la población vive en pobreza. La barra de D1 mide "
                   "el rezago social relativo entre municipios, no el porcentaje de pobreza.")
    causal = ("El driver dominante es el factor que más destaca en esta escuela según el modelo "
              "ML-02. Orienta la investigación y la recomendación; no es la causa.")
    fig.text(0.42, 0.305, textwrap.fill(nota_d1, 105), fontsize=8.8, color=PALETA["tinta_2"],
             va="top", linespacing=1.3)
    fig.text(0.42, 0.26, textwrap.fill(causal, 105), fontsize=8.8, color=PALETA["tinta"],
             va="top", linespacing=1.3)

    shap = fig.add_axes([0.42, 0.13, 0.55, 0.085])
    shap.set_xlim(0, 1)
    shap.set_ylim(0, 1)
    shap.axis("off")
    no_nulos = sum(v is not None for v in caso.contribuciones.values())
    shap.text(0, 0.95, "Qué pesó en el modelo (contribuciones SHAP, panel aparte de la presión)",
              fontsize=9.5, fontweight="bold", color=PALETA["tinta"], va="top")
    if no_nulos == 0:
        lz.sin_dato(shap, 0, 0.0, 1, 0.55, "SIN DATO — la explicación del modelo para esta "
                    "escuela aún no está publicada en producción", size=8.4)
    lz.pie(fig, "GET /api/v1/escuelas/{cct} · GET /api/v1/predicciones/{cct} · GET "
           "/api/v1/predicciones/{cct}/explicacion · GET /api/v1/municipios/{cve_mun}",
           "nombre, nivel, sostenimiento, d1…d6, indice_completitud_drivers, es_estimado_por_grupo; "
           "indice_riesgo, driver_dominante, recomendacion; contribuciones; pobreza_pct",
           extra="D3 y D4 se dibujan como falta (1 − servicios presentes), la misma lectura con la "
                 "que el pipeline elige el dominante (dbt/models/gold/features_escuela.sql:385-410).")
    return lz.guardar(fig, f"P4_expediente_{caso.cct}")


def ejemplo_p5(lz: Lienzo, casos: list[Caso]) -> list[Path]:
    """P5 — Top 3 sobre el conjunto completo: conteo, gráfica de unidades y recomendación."""
    import textwrap
    conjunto = lz.evidencia["conjunto_en_riesgo"]
    ranking, sin_dominante = top3(conjunto)
    n = len(conjunto)
    por_cct = {c.cct: c for c in casos}
    fig = lz.figura(15, 9.8)
    fig.text(0.03, 0.958, "Pantalla 5 · Conclusión Top 3 (ejemplo con datos reales)",
             fontsize=10.5, color=PALETA["tinta_2"])
    fig.text(0.03, 0.905, "Lo que más se repite entre las N escuelas en riesgo", fontsize=20,
             fontweight="bold", color=PALETA["tinta"])
    presentes = len(ranking)
    subtitulo = {
        0: "Ninguna escuela en riesgo tiene todavía un driver dominante.",
        1: "Sólo un factor aparece como dominante entre todas las escuelas en riesgo.",
        2: "Sólo dos factores aparecen como dominantes entre todas las escuelas en riesgo.",
        3: "Los tres factores que más aparecen como dominantes.",
    }.get(presentes, f"Los factores que más aparecen como dominantes: hay un empate, por eso son "
                     f"{presentes}.")
    fig.text(0.03, 0.866, subtitulo, fontsize=13, color=PALETA["tinta"])

    ancho_u, alto_u, rect = 18.8, 9.2, [0.03, 0.33, 0.94, 0.52]
    ax = lz.ejes(fig, rect, ancho_u, alto_u)
    # Casillas cuadradas de verdad: la escala vertical de estos ejes no es la horizontal.
    lado_x = 0.78
    lado_y = lado_x * (rect[2] * 15 / ancho_u) / (rect[3] * 9.8 / alto_u)
    y = 0.1
    lugares = [lugar for lugar, _, _ in ranking]
    for lugar, codigo, k in ranking:
        empate = lugares.count(lugar) > 1
        grupo = [e["cct"] for e in conjunto if e.get("driver_dominante") == codigo]
        lz.texto(ax, 0.05, y + 0.45, f"{lugar}.º", size=24, weight="bold", va="center")
        lz.texto(ax, 1.3, y + 0.25, f"{NOMBRE_DRIVER[codigo]} ({codigo})"
                 + ("  · empate" if empate else ""), size=14, weight="bold", va="center")
        lz.texto(ax, 1.3, y + 0.75, f"{k} de {n} escuelas ({round(100 * k / n)} %)", size=11.5,
                 va="center")
        filas = -(-len(grupo) // 5)
        for m, cct in enumerate(grupo):
            xs, ys = 7.0 + (m % 5) * 0.95, y + 0.05 + (m // 5) * (lado_y + 0.45)
            ax.add_patch(lz.patches.Rectangle((xs, ys), lado_x, lado_y,
                                              facecolor=PALETA["barra_dominante"], linewidth=0))
            lz.texto(ax, xs + lado_x / 2, ys + lado_y + 0.2, cct, size=6.4,
                     color=PALETA["tinta_2"], ha="center", va="center")
        recomendacion = next((por_cct[c].recomendacion for c in grupo
                              if por_cct.get(c) and por_cct[c].recomendacion), "SIN_DATO")
        presiones = [por_cct[c].presion(codigo) for c in grupo if por_cct.get(c)]
        presiones = [p for p in presiones if p is not None]
        problema = ""
        if presiones:
            problema = (f"Presión de {ETIQUETA_PRESION[codigo].lower()} entre {min(presiones):.2f} "
                        f"y {max(presiones):.2f} (0 = menor observada, 1 = mayor)")
            if codigo in DRIVERS_MUNICIPALES:
                problema += "; es un valor del municipio"
            if codigo in DRIVERS_INVERTIDOS:
                vals = sorted({por_cct[c].publicados[codigo] for c in grupo if por_cct.get(c)})
                problema += "; servicios presentes: " + ", ".join(f"{v:.2f}" for v in vals)
            problema += "."
        lz.texto(ax, 1.3, y + 1.1, textwrap.fill(problema, 58), size=8.8,
                 color=PALETA["tinta_2"], va="top", linespacing=1.3)
        lz.texto(ax, 12.4, y + 0.05, "Recomendación", size=9, weight="bold",
                 color=PALETA["tinta_2"], va="top")
        lz.texto(ax, 12.4, y + 0.45, textwrap.fill(recomendacion, 50), size=10.5, va="top",
                 linespacing=1.3)
        alto_grupo = max(2.25, 0.3 + filas * (lado_y + 0.45))
        ax.plot([0, ancho_u], [y + alto_grupo, y + alto_grupo], color=PALETA["regla"],
                linewidth=0.6)
        y += alto_grupo + 0.2
    if sin_dominante:
        lz.texto(ax, 0.05, y + 0.3, f"{sin_dominante} escuelas sin driver dominante (SIN_DATO).",
                 size=10, va="center")
        y += 0.7

    municipios: dict[str, int] = {}
    for caso in casos:
        municipios[caso.municipio] = municipios.get(caso.municipio, 0) + 1
    entidades = sorted({NOMBRE_ENTIDAD.get(c.cve_mun[:2], c.cve_mun[:2]) for c in casos})
    donde = " · ".join(f"{nombre} ({k})" for nombre, k in
                       sorted(municipios.items(), key=lambda par: (-par[1], par[0])))
    lz.texto(ax, 0.05, y + 0.3, f"Dónde están: {donde}, en {_enumera(entidades)}.", size=10.5,
             va="center")
    sin_en_todas = [c for c in CODIGOS if all(caso.publicados[c] is None for caso in casos)]
    pistas = sorted({caso.pistas for caso in casos})
    cobertura = (f"Evidencia: las escuelas tienen dato para {' o '.join(map(str, pistas))} de 6 "
                 "pistas. ")
    if sin_en_todas:
        nombres = _enumera([NOMBRE_DRIVER[c].lower() for c in sin_en_todas])
        cobertura += (f"{nombres[0].upper()}{nombres[1:]} no pudieron verificarse en ninguna: "
                      "que no aparezcan aquí no significa que no sean un problema.")
    cobertura = textwrap.fill(cobertura, 150)
    lz.texto(ax, 0.05, y + 0.65, cobertura, size=10, va="top", linespacing=1.3)
    y += 0.75 + 0.42 * (cobertura.count("\n") + 1)
    niveles = {nivel_atencion(c.riesgo, lz.linea, lz.estable) for c in casos}
    if niveles == {"alta"}:
        lz.texto(ax, 0.05, y + 0.15, "Todas tienen atención alta: el conjunto se define con ese "
                 "mismo corte, por eso aquí no se grafica una distribución de niveles.", size=10,
                 color=PALETA["tinta_2"], va="center")

    fig.add_artist(lz.patches.FancyBboxPatch(
        (0.03, 0.195), 0.62, 0.06, boxstyle="round,pad=0.004,rounding_size=0.008",
        transform=fig.transFigure, facecolor=PALETA["panel"], edgecolor=PALETA["tinta"],
        linewidth=1))
    fig.text(0.04, 0.225, textwrap.fill(
        "Esta conclusión se calcula sobre el conjunto completo de escuelas en riesgo, "
        "independientemente de los filtros utilizados durante la exploración.", 100),
        fontsize=10.5, fontweight="bold", color=PALETA["tinta"], va="center")
    fig.add_artist(lz.patches.FancyBboxPatch(
        (0.74, 0.2), 0.2, 0.05, boxstyle="round,pad=0.004,rounding_size=0.012",
        transform=fig.transFigure, facecolor=PALETA["tinta"], linewidth=0))
    fig.text(0.84, 0.225, "Explorar otras escuelas →", fontsize=11.5, fontweight="bold",
             color=PALETA["fondo"], ha="center", va="center")
    lz.pie(fig, "GET /api/v1/kpis (sin filtros) · GET /api/v1/escuelas?order_by=indice_riesgo&"
           "order=desc&size=100 SIN filtros, con corte en LINEA_DE_ALERTA · GET "
           "/api/v1/predicciones/{cct} (recomendacion) · GET /api/v1/municipios/{cve_mun}",
           "escuelas_en_riesgo; driver_dominante, cve_mun, indice_riesgo; recomendacion; d1…d6 e "
           "indice_completitud_drivers de /escuelas/{cct}; nombre_municipio",
           extra="Conteo por driver_dominante de EscuelaOut; rango con empates compartidos "
                 "(generar_ejemplos.py::top3). Cada casilla es una escuela. Los conteos se "
                 "resuelven en vivo; en los mockups van como N y k.")
    return lz.guardar(fig, "P5_conclusion_top3")


def ejemplo_p6(lz: Lienzo, cve_ent: str) -> list[Path]:
    """P6 — lista filtrada con el nivel de atención por forma y texto, y los KPIs del filtro."""
    datos = lz.evidencia["exploracion"][cve_ent]
    escuelas = sorted(datos["escuelas"]["items"], key=lambda e: (-(e["indice_riesgo"] or 0),
                                                                  e["nombre"], e["cct"]))[:12]
    kpis = datos["kpis"]
    fig = lz.figura(15, 9.6)
    fig.text(0.03, 0.958, "Pantalla 6 · Exploración de otras escuelas (ejemplo con datos reales)",
             fontsize=10.5, color=PALETA["tinta_2"])
    for i, chip in enumerate(("Ciclo: 2024-2025", f"Entidad: {NOMBRE_ENTIDAD[cve_ent]}",
                              "Nivel: todos")):
        x = 0.03 + i * 0.16
        fig.add_artist(lz.patches.FancyBboxPatch(
            (x, 0.885), 0.145, 0.04, boxstyle="round,pad=0.003,rounding_size=0.01",
            transform=fig.transFigure, facecolor=PALETA["panel"], edgecolor=PALETA["regla"],
            linewidth=1))
        fig.text(x + 0.0725, 0.905, chip, fontsize=10, ha="center", va="center",
                 color=PALETA["tinta"])
    fig.text(0.03, 0.845, "Las de mayor índice primero. Elige una para abrir su expediente, "
             "igual al de la Pantalla 4.", fontsize=11.5, color=PALETA["tinta"])

    fila, cabeza, ancho = 0.62, 0.8, 12.6
    alto = cabeza + fila * len(escuelas)
    ax = lz.ejes(fig, [0.03, 0.8 - 0.0725 * alto, 0.66, 0.0725 * alto], ancho, alto)
    x_pista, w_pista = 4.9, 3.9
    lz.texto(ax, 0.05, cabeza - 0.12, "Escuela", size=9.5, weight="bold", va="bottom")
    lz.texto(ax, 4.2, cabeza - 0.12, "Índice", size=9.5, weight="bold", va="bottom",
             ha="center")
    for valor, rotulo in ((lz.estable, f"{lz.estable:.2f}"), (lz.linea, f"{lz.linea:.2f}")):
        lz.texto(ax, x_pista + w_pista * valor, cabeza - 0.12, rotulo, size=8.2,
                 color=PALETA["tinta_2"], ha="center", va="bottom")
    lz.texto(ax, 9.1, cabeza - 0.12, "Atención · driver dominante", size=9.5, weight="bold",
             va="bottom")
    ax.plot([0, ancho], [cabeza, cabeza], color=PALETA["regla"], linewidth=1)
    for i, escuela in enumerate(escuelas):
        y = cabeza + i * fila
        yc = y + fila / 2
        if i:
            ax.plot([0, ancho], [y, y], color=PALETA["regla"], linewidth=0.4)
        riesgo = escuela["indice_riesgo"]
        lz.texto(ax, 0.05, yc - 0.1, _corta(escuela["nombre"], 32), size=9, weight="bold",
                 va="center")
        lz.texto(ax, 0.05, yc + 0.15, f"{escuela['nivel'].capitalize()} · {escuela['cct']}",
                 size=7.6, color=PALETA["tinta_2"], va="center")
        if riesgo is None:
            lz.sin_dato(ax, x_pista, yc - 0.15, w_pista, 0.3, "sin predicción", size=7.4)
            continue
        nivel = nivel_atencion(riesgo, lz.linea, lz.estable)
        lz.texto(ax, 4.2, yc, f"{riesgo:.3f}", size=10, weight="bold", ha="center", va="center")
        _pista_riesgo(lz, ax, x_pista, w_pista, yc, riesgo, nivel)
        dominante = NOMBRE_DRIVER.get(escuela.get("driver_dominante") or "", "sin dato")
        lz.texto(ax, 9.1, yc, f"{ICONO_NIVEL[nivel]} {nivel} · {dominante}", size=9,
                 va="center")

    panel = fig.add_axes([0.72, 0.36, 0.25, 0.44])
    panel.set_xlim(0, 1)
    panel.set_ylim(0, 1)
    panel.axis("off")
    panel.add_patch(lz.patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size="
                                              "0.03", facecolor=PALETA["panel"],
                                              edgecolor=PALETA["regla"], linewidth=1))
    panel.text(0.07, 0.92, "Este filtro", fontsize=12, fontweight="bold", va="top",
               color=PALETA["tinta"])
    panel.text(0.07, 0.80, f"{kpis['escuelas_en_riesgo']:,}", fontsize=26, fontweight="bold",
               va="top", color=PALETA["tinta"])
    panel.text(0.07, 0.62, "escuelas con atención alta\n(cruzan la línea de alerta)",
               fontsize=9.2, va="top", color=PALETA["tinta_2"])
    panel.text(0.07, 0.46, f"{kpis['indice_completitud_drivers'] * 6:.1f} de 6", fontsize=18,
               fontweight="bold", va="top", color=PALETA["tinta"])
    panel.text(0.07, 0.33, "pistas con dato, en promedio", fontsize=9.2, va="top",
               color=PALETA["tinta_2"])
    panel.text(0.07, 0.2, "El filtro de nivel no cambia estos\nindicadores: /kpis no acepta "
               "nivel.", fontsize=8.4, va="top", color=PALETA["tinta_2"])
    repetidos = len(escuelas) - len({e["indice_riesgo"] for e in escuelas})
    notas = [(f"Nivel de atención: ▲ alta desde {lz.linea:.2f} · ■ media desde {lz.estable:.2f} · "
              "● baja debajo. Forma y texto, no sólo color.")]
    if repetidos:
        notas.append("Varias escuelas comparten exactamente el mismo índice: la lista las pone "
                     "juntas en orden alfabético y no inventa un orden entre ellas.")
    fig.text(0.03, 0.8 - 0.0725 * alto - 0.03, "\n".join(notas), fontsize=9,
             color=PALETA["tinta_2"], va="top", linespacing=1.4)
    lz.pie(fig, f"GET /api/v1/escuelas?cve_ent={cve_ent}&order_by=indice_riesgo&order=desc&"
           f"size={TAM_EXPLORACION} · GET /api/v1/kpis?cve_ent={cve_ent}",
           "cct, nombre, nivel, indice_riesgo, driver_dominante; escuelas_en_riesgo, "
           "indice_completitud_drivers",
           extra="Filtro de ejemplo. La matrícula no se muestra aquí: dentro de la historia sólo "
                 "aparece en la Pantalla 2.")
    return lz.guardar(fig, "P6_exploracion")


def _pareja_p4(casos: list[Caso]) -> list[Caso]:
    """Dos expedientes que muestran el diferenciador: mismo municipio y nivel, otro dominante."""
    for a in casos:
        for b in casos:
            if (a.cve_mun == b.cve_mun and a.nivel == b.nivel and a.dominante and b.dominante
                    and a.dominante != b.dominante and a.nombre != b.nombre):
                return [a, b]
    distintos = {c.dominante: c for c in casos if c.dominante}
    return list(distintos.values())[:2] or casos[:1]


def _entidad_p6(evidencia: dict[str, Any], casos: list[Caso]) -> str:
    """Filtro de ejemplo para la P6: fuera de la entidad de los casos, la de más índices distintos."""
    en_riesgo = {c.cve_mun[:2] for c in casos}
    candidatas = [e for e in evidencia["exploracion"] if e not in en_riesgo] or \
        list(evidencia["exploracion"])
    return max(candidatas, key=lambda e: (
        len({x["indice_riesgo"] for x in evidencia["exploracion"][e]["escuelas"]["items"]}), e))


def graficar(ruta_evidencia: Path) -> None:
    """Dibuja los ejemplos P2…P6 a partir de la evidencia (PNG y SVG en esta carpeta)."""
    evidencia = json.loads(ruta_evidencia.read_text(encoding="utf-8"))
    informe = validar_paleta()
    lz = Lienzo(evidencia, CARPETA)
    casos = _casos(evidencia)
    if not casos:
        raise SystemExit("La evidencia no trae escuelas en riesgo: no hay nada que dibujar.")
    rutas = ejemplo_p2(lz, casos) + ejemplo_p3(lz, casos)
    for caso in _pareja_p4(casos):
        rutas += ejemplo_p4(lz, caso)
    rutas += ejemplo_p5(lz, casos)
    rutas += ejemplo_p6(lz, _entidad_p6(evidencia, casos))
    print(f"Evidencia: {ruta_evidencia.name}")
    print("Contraste WCAG:\n  " + "\n  ".join(informe))
    print("Generados:\n  " + "\n  ".join(str(r.relative_to(RAIZ_REPO)) for r in rutas))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="paso", required=True)
    p_desc = sub.add_parser("descargar", help="consulta la API y guarda la evidencia fuera del repo")
    p_desc.add_argument("--api", default=os.environ.get("FARO_API_URL", API_URL_PRODUCCION))
    p_graf = sub.add_parser("graficar", help="dibuja los PNG/SVG a partir de la evidencia")
    p_graf.add_argument("--evidencia", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.paso == "descargar":
        descargar(args.api)
    else:
        graficar(args.evidencia or evidencia_mas_reciente())
    return 0


if __name__ == "__main__":
    sys.exit(main())
