#!/usr/bin/env python3
"""
FARO — Sincronizar capa semántica y tableros a Superset.

Lee los archivos YAML y SQL de superset/semantic/ y configura:
  - Conexión a la base de datos gold
  - Datasets virtuales (uno por cada .sql)
  - Métricas y columnas/dimensiones (desde metrics_*.yaml)

Desde US-203 además lee superset/dashboards/*.yaml y configura:
  - Charts (uno por entrada `charts:`), con validación de datos opcional
  - Dashboards con sus charts adjuntados y layout en grilla
  - Filtros nativos globales (mejor esfuerzo; el refinado es US-214a)

Idempotente: crea nuevos, actualiza existentes, reporta cambios.
No modifica archivos fuente (superset/semantic/*, superset/dashboards/*).

Uso:
    source .venv/bin/activate
    python superset/sync_semantic_layer.py            # capa semántica + tableros
    python superset/sync_semantic_layer.py --no-charts  # solo datasets/métricas
    python superset/sync_semantic_layer.py --validar-datos  # consulta cada chart

Requiere que Superset esté corriendo (docker compose up superset) y que
las variables de entorno estén configuradas (copiar de .env.example).
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuración desde variables de entorno
# ---------------------------------------------------------------------------

SUPERSET_URL = os.environ.get("SUPERSET_URL", "http://127.0.0.1:8088")
ADMIN_USER = os.environ.get("SUPERSET_ADMIN_USERNAME", "faro_superset_admin")
ADMIN_PASS = os.environ.get("SUPERSET_ADMIN_PASSWORD", "")

DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DB", "escuela_concausa_db")
DB_USER = os.environ.get("POSTGRES_USER", "postgres")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "")

# Nombre interno que Superset asigna a la conexión
CONNECTION_NAME = "faro_escuela_concausa_db"

SEMANTIC_DIR = Path(__file__).resolve().parent / "semantic"
DASHBOARDS_DIR = Path(__file__).resolve().parent / "dashboards"

# Formatos d3 por convención del proyecto (metrics_*.yaml -> campo `formato`)
FORMATO_D3 = {
    "entero": ",d",
    "decimal_1": ",.1f",
    "decimal_2": ",.2f",
    "porcentaje_0": ",.0%",
    "porcentaje_1": ",.1%",
    # "fecha": sin esta entrada, FORMATO_D3.get("fecha", "") caia a cadena
    # vacia y Superset rechazaba el PUT del dataset completo (d3format exige
    # 1-128 caracteres) -- NINGUNA metrica del dataset se aplicaba, no solo
    # la de fecha (hallado en metrics_db10.yaml -> ultima_ingesta, US-223).
    # "smart_date" (el sentinel de Superset para ejes de serie de tiempo) se
    # probo primero pero en un big_number_total interpreta el timestamp como
    # numero crudo ("​.527ms" en vez de una fecha) -- un d3-time-format
    # explicito si renderiza la fecha real.
    "fecha": "%Y-%m-%d",
}

ALTO_TILE_KPI = 38      # altura de un tile KPI (unidades de grilla Superset)
ALTO_GRAFICO = 60       # altura de un gráfico estándar

# ---------------------------------------------------------------------------
# Utilidades HTTP (stdlib, sin dependencias externas)
# ---------------------------------------------------------------------------

_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE

# Cookie jar compartido para persistir sesión entre requests
_cookie_jar = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(_cookie_jar),
    urllib.request.HTTPSHandler(context=_CTX),
)


def _request(
    method: str,
    path: str,
    token: str | None = None,
    body: dict | None = None,
    csrf_token: str | None = None,
    raw_body: bytes | None = None,
    content_type: str = "application/json",
) -> dict:
    url = f"{SUPERSET_URL}{path}"
    headers: dict[str, str] = {
        "Content-Type": content_type,
        "Accept": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if csrf_token:
        headers["X-CSRFToken"] = csrf_token
        headers["Referer"] = SUPERSET_URL

    data = raw_body if raw_body is not None else (json.dumps(body).encode() if body is not None else None)

    # Esta imagen aplica rate limit (50 req/s): reintenta con espera ante 429.
    import time
    for intento in range(3):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with _opener.open(req) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode() if exc.fp else ""
            if exc.code == 429 and intento < 2:
                time.sleep(0.5 * (intento + 1))
                continue
            print(f"  ✗ HTTP {exc.code} en {method} {path}: {err_body[:300]}")
            raise


# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------

def login() -> tuple[str, str]:
    """Obtiene JWT + CSRF token de Superset."""
    resp = _request("POST", "/api/v1/security/login", body={
        "username": ADMIN_USER,
        "password": ADMIN_PASS,
        "provider": "db",
        "refresh": True,
    })
    access_token = resp.get("access_token", "")
    if not access_token:
        print("✗ No se pudo obtener access_token. Verifica credenciales.")
        sys.exit(1)

    # El endpoint de CSRF token establece una cookie de sesión necesaria
    # para los POST subsiguientes. La cookie se persiste en _cookie_jar.
    csrf_resp = _request("GET", "/api/v1/security/csrf_token/", token=access_token)
    csrf_token = csrf_resp.get("result", "")
    print("✔ Autenticado en Superset")
    return access_token, csrf_token


# ---------------------------------------------------------------------------
# Conexión a base de datos
# ---------------------------------------------------------------------------

def ensure_database(token: str, csrf: str) -> int:
    """Crea o actualiza la conexión a escuela_concausa_db. Retorna el ID."""
    resp = _request("GET", "/api/v1/database/", token=token)
    for db in resp.get("result", []):
        if db.get("database_name") == CONNECTION_NAME:
            print(f"✔ Conexión '{CONNECTION_NAME}' ya existe (id={db['id']})")
            return db["id"]

    # La URI de conexión usa 'db' (nombre del servicio Docker), NO localhost.
    # Superset corre dentro de la red Docker y necesita resolver 'db'.
    superset_db_host = "db"
    body = {
        "database_name": CONNECTION_NAME,
        "engine": "postgresql",
        "sqlalchemy_uri": f"postgresql://{DB_USER}:{DB_PASS}@{superset_db_host}:{DB_PORT}/{DB_NAME}",
        "expose_in_sqllab": True,
        "allow_ctas": False,
        "allow_cvas": False,
        "allow_dml": False,
        "allow_run_async": False,
        "extra": json.dumps({
            "allows_virtual_table_explore": True,
            "disable_sql_lab": False,
        }),
    }
    created = _request("POST", "/api/v1/database/", token=token, csrf_token=csrf, body=body)
    db_id = created.get("id")
    print(f"✔ Conexión '{CONNECTION_NAME}' creada (id={db_id})")
    return db_id


# ---------------------------------------------------------------------------
# Datasets virtuales
# ---------------------------------------------------------------------------

def _read_sql(path: Path) -> str:
    """Lee un archivo .sql y extrae la query (sin comentarios al inicio)."""
    # encoding explícito: en Windows read_text() usa cp1252 y truena con acentos
    # (misma familia que BUG-005 / BUG-011).
    raw = path.read_text(encoding="utf-8")
    # Quitar comentarios SQL al inicio (líneas que empiezan con --)
    lines = []
    in_comment_block = True
    for line in raw.splitlines():
        stripped = line.strip()
        if in_comment_block and (stripped.startswith("--") or stripped == ""):
            continue
        in_comment_block = False
        lines.append(line)
    return "\n".join(lines)


def ensure_datasets(
    token: str, csrf: str, db_id: int
) -> dict[str, int]:
    """Crea datasets virtuales desde cada .sql. Retorna {nombre: dataset_id}."""
    resp = _request("GET", "/api/v1/dataset/", token=token)
    existing = {
        d["table_name"]: d["id"]
        for d in resp.get("result", [])
        if d.get("database", {}).get("id") == db_id or d.get("database") == db_id
    }

    datasets: dict[str, int] = {}
    for sql_file in sorted(SEMANTIC_DIR.glob("*.sql")):
        name = sql_file.stem  # p.ej. db03_cubo_escuela_360
        sql = _read_sql(sql_file)

        # BUG-029: un dataset cuya tabla Gold aun no existe (ambiente sin la
        # cadena Bronze->Gold completa) no debe tumbar la corrida entera --
        # antes, un solo 500 aqui abortaba el sync para TODOS los tableros
        # alfabeticamente posteriores, sanos o no. Se reporta y se continua;
        # el dataset simplemente no entra a `datasets`, y los charts que lo
        # usan ya saben omitirse (ensure_chart devuelve -1 si el nombre no
        # esta en `datasets_by_name`).
        try:
            if name in existing:
                ds_id = existing[name]
                # El SQL del archivo puede haber cambiado desde la última corrida:
                # comparar contra lo guardado y hacer PUT si difiere (si no, los
                # tableros seguirían consultando el SQL viejo para siempre).
                detalle = _request("GET", f"/api/v1/dataset/{ds_id}", token=token).get("result", {})
                sql_actual = (detalle.get("sql") or "").strip()
                if sql_actual != sql.strip():
                    _request(
                        "PUT",
                        f"/api/v1/dataset/{ds_id}",
                        token=token,
                        csrf_token=csrf,
                        body={"sql": sql},
                    )
                    print(f"  ↻ Dataset '{name}' actualizado (el SQL cambió)")
                else:
                    print(f"  ✔ Dataset '{name}' existe y está al día (id={ds_id})")
            else:
                body = {
                    "database": db_id,
                    "sql": sql,
                    "schema": "gold",
                    "table_name": name,
                }
                created = _request(
                    "POST", "/api/v1/dataset/", token=token, csrf_token=csrf, body=body
                )
                ds_id = created.get("id")
                print(f"  ✔ Dataset '{name}' creado (id={ds_id})")
        except Exception as e:  # noqa: BLE001 - un dataset roto no debe abortar el sync (BUG-029)
            print(f"  ✗ Dataset '{name}' omitido (tabla/vista Gold ausente o error): {e}")
            continue

        datasets[name] = ds_id

    return datasets


# ---------------------------------------------------------------------------
# Métricas y dimensiones
# ---------------------------------------------------------------------------

def _read_yaml(path: Path) -> dict:
    """
    Parser YAML mínimo para el formato de metrics_db03_db04.yaml.
    Sin dependencias externas. Maneja estructuras planas y anidadas simples.
    """
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        pass

    # Fallback: parser manual para la estructura conocida
    # Parsea el YAML línea por línea, manejando indentación
    result: dict[str, Any] = {}
    stack: list[tuple[int, dict | list]] = [(0, result)]
    current_key: str | None = None
    list_accumulator: list | None = None
    in_block_scalar = False
    block_lines: list[str] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        if in_block_scalar:
            if indent > stack[-1][0]:
                block_lines.append(line.rstrip())
                continue
            else:
                if list_accumulator is not None and current_key:
                    list_accumulator.append(" ".join(block_lines))
                in_block_scalar = False
                block_lines = []

        if stripped.startswith("- "):
            # Elemento de lista
            val = stripped[2:].strip()
            if ":" in val:
                # Objeto dentro de lista: - nombre: foo
                key_val = val.split(":", 1)
                obj = {key_val[0].strip(): _coerce(key_val[1].strip())}
                if list_accumulator is None:
                    # Buscar la lista padre en el stack
                    for i in range(len(stack) - 1, -1, -1):
                        if isinstance(stack[i][1], list):
                            list_accumulator = stack[i][1]
                            break
                if list_accumulator is not None:
                    list_accumulator.append(obj)
            elif val.endswith(":"):
                # Nuevo dict dentro de lista
                obj: dict[str, Any] = {}
                if list_accumulator is not None:
                    list_accumulator.append(obj)
                stack.append((indent + 2, obj))
            else:
                if list_accumulator is not None:
                    list_accumulator.append(_coerce(val))
            continue

        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if value == "":
                # Puede ser dict o lista; miramos la siguiente línea no-vacía para decidir
                if len(stack) > 1 and indent <= stack[-2][0]:
                    # Backtrack
                    stack.pop()
                    if isinstance(stack[-1][1], dict):
                        stack[-1][1][key] = {}
                    elif isinstance(stack[-1][1], list):
                        stack[-1][1].append({key: {}})
                    current_key = key
                else:
                    parent = stack[-1][1]
                    if isinstance(parent, dict):
                        # Verificar si la siguiente línea es un `-`
                        # Por ahora asumimos que es un dict
                        parent[key] = {}
                        stack.append((indent + 2, parent[key]))
                    current_key = key
            elif value == "|":
                in_block_scalar = True
                block_lines = []
                list_accumulator = None
            else:
                parent = stack[-1][1]
                coerced = _coerce(value)
                if isinstance(parent, dict):
                    parent[key] = coerced
                elif isinstance(parent, list) and parent and isinstance(parent[-1], dict):
                    parent[-1][key] = coerced
                current_key = key

    return result


def _coerce(value: str) -> Any:
    """Convierte string a tipo nativo."""
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    if value in ("null", "None"):
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    # Quitar comillas
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


# Los formatos porcentaje_* son d3 con sufijo %: multiplican el valor por 100
# al renderizar. Por eso las expresiones del YAML guardan la razon pura
# (0.318 -> "31.8%") y NUNCA un "* 100" en SQL, que duplicaria el escalado.
# Un unico mapa para dataset (d3format) y charts (y_axis_format): dos mapas
# divergentes fue la causa de tiles que mostraban "3,181.8%".


def _apply_metrics_and_columns(
    token: str,
    csrf: str,
    ds_id: int,
    dataset_cfg: dict,
    dataset_name: str,
) -> None:
    """Aplica métricas y dimensiones al dataset.

    A diferencia de una version anterior que se saltaba las metricas ya
    existentes ("ya existe" -> continue), aqui SIEMPRE se envia la lista
    completa: si la expresion o el formato d3 cambiaron en el YAML, el PUT
    los actualiza (el importador v1 no toca datasets). Sin esto, los fixes
    de formato nunca llegaban a Superset y los tiles mostraban valores
    viejos.
    """
    # Obtener dataset actual con sus columnas y métricas
    resp = _request("GET", f"/api/v1/dataset/{ds_id}", token=token)
    ds_data = resp.get("result", {})
    current_columns = ds_data.get("columns", [])
    current_metrics = ds_data.get("metrics", [])
    # El PUT distingue update de alta por la presencia de `id` numerico
    # (_validate_metrics en commands/dataset/update.py): sin id, trata la
    # entrada como nueva y rechaza por nombre duplicado.
    existente_por_nombre = {
        m.get("metric_name"): m for m in current_metrics
    }

    # --- Métricas virtuales: lista completa, con id/uuid de las existentes ---
    desired_metrics: list[dict] = []
    for m in dataset_cfg.get("metricas", []):
        mname = m["nombre"]
        # Algunas métricas son solo columnas (ej. contexto_socioeconomico), no expresiones
        if "expresion" not in m:
            print(f"    ⚠ Métrica '{mname}' sin expresión (solo columnas), se omite")
            continue

        desired_metrics.append({
            "metric_name": mname,
            "verbose_name": m.get("etiqueta", mname),
            "expression": m["expresion"],
            "metric_type": "sql",
            # El campo del schema es d3format; NO extra.d3Format (nunca aplicaba).
            "d3format": FORMATO_D3.get(m.get("formato", ""), ""),
            "description": f"{m.get('kpi', '')} — {m.get('nota', '')}".strip(" —"),
        })
        previa = existente_por_nombre.get(mname)
        if previa and previa.get("id") is not None:
            desired_metrics[-1]["id"] = previa["id"]
            if previa.get("uuid"):
                desired_metrics[-1]["uuid"] = previa["uuid"]

    def _metrica_cambio(m: dict) -> bool:
        actual = existente_por_nombre.get(m["metric_name"])
        if actual is None:
            return True  # nueva
        return (
            actual.get("expression") != m["expression"]
            or (actual.get("d3format") or "") != m["d3format"]
            or actual.get("verbose_name") != m["verbose_name"]
        )

    metrics_a_actualizar = [m["metric_name"] for m in desired_metrics if _metrica_cambio(m)]

    # --- Dimensiones (columnas) ---
    # Las columnas existentes ya están detectadas por Superset.
    # Solo necesitamos marcar las jerarquías como dimensiones.
    # Superset usa 'groupby' y 'filterable' para dimensiones.
    new_columns: list[dict] = []
    for col in current_columns:
        col_name = col.get("column_name", "")
        new_columns.append({
            "column_name": col_name,
            "id": col.get("id"),
            "groupby": True,
            "filterable": True,
            "is_dttm": col.get("is_dttm", False),
        })

    if not metrics_a_actualizar and not new_columns:
        print("    ✔ Métricas/dimensiones ya alineadas")
        return

    # Aplicar actualización
    body: dict[str, Any] = {}
    if metrics_a_actualizar:
        body["metrics"] = desired_metrics
        print(f"    ➜ Métricas a actualizar/crear: {', '.join(metrics_a_actualizar)}")

    if new_columns:
        body["columns"] = [
            {
                "column_name": c["column_name"],
                "id": c["id"],
                "groupby": c["groupby"],
                "filterable": c["filterable"],
                "is_dttm": c["is_dttm"],
            }
            for c in new_columns
        ]

    try:
        _request("PUT", f"/api/v1/dataset/{ds_id}", token=token, csrf_token=csrf, body=body)
        print(f"    ✔ Dataset {ds_id} actualizado")
    except Exception as e:  # noqa: BLE001 - un dataset desalineado no debe abortar el sync
        print(f"    ✗ Error actualizando dataset {ds_id}: {e}")


def sync_metrics(
    token: str, csrf: str, datasets: dict[str, int]
) -> None:
    """Lee metrics_*.yaml y aplica métricas/dimensiones a cada dataset."""
    for yaml_file in sorted(SEMANTIC_DIR.glob("metrics_*.yaml")):
        data = _read_yaml(yaml_file)
        for ds_cfg in data.get("datasets", []):
            ds_name_raw = ds_cfg.get("sql", "").replace(".sql", "")
            ds_name = ds_name_raw

            # Buscar nombre real del dataset (puede ser diferente al sql)
            sql_match = ds_cfg.get("sql", "").replace(".sql", "")
            # Intentar con el nombre del dataset primero
            if ds_cfg.get("nombre") in datasets:
                ds_id = datasets[ds_cfg["nombre"]]
                ds_label = ds_cfg["nombre"]
            elif sql_match in datasets:
                ds_id = datasets[sql_match]
                ds_label = sql_match
            else:
                print(f"  ✗ Dataset '{ds_name}' no encontrado para métricas de {yaml_file.name}")
                continue

            print(f"  Aplicando métricas a '{ds_label}'...")
            _apply_metrics_and_columns(token, csrf, ds_id, ds_cfg, ds_label)


# ---------------------------------------------------------------------------
# Charts y dashboards (US-203)
# ---------------------------------------------------------------------------

def _formato_de_metrica(yaml_datasets: list[dict], dataset_name: str, metrica: str) -> str:
    """Busca el formato d3 declarado en metrics_*.yaml para (dataset, metrica)."""
    for ds in yaml_datasets:
        if ds.get("nombre") != dataset_name:
            continue
        for m in ds.get("metricas", []):
            if m.get("nombre") == metrica:
                return FORMATO_D3.get(m.get("formato", ""), ",d")
    return ",d"


def _params_chart(
    chart_cfg: dict,
    ds_id: int,
    formato: str,
) -> dict:
    """Construye el params JSON de un chart según su viz_type.

    El YAML puede sobreescribir/añadir cualquier llave vía `params_extra`,
    así que los ajustes finos de visualización son ediciones de datos y no
    de código.
    """
    viz = chart_cfg["viz"]
    metrica = chart_cfg["metrica"]
    base: dict[str, Any] = {
        "datasource": f"{ds_id}__table",
        "viz_type": viz,
    }

    if viz == "big_number_total":
        base.update({
            "metric": metrica,
            "subheader": chart_cfg.get("subheader", ""),
            "y_axis_format": formato,
            "header_font_size": 0.3,
            "compare_lag": "",
            "time_range": "",
        })
    elif viz in ("echarts_timeseries_bar", "echarts_timeseries_line"):
        # Métrica como string plano: un adhoc sin expressionType rompe el
        # schema de params y el endpoint /dashboard/<slug>/datasets (422).
        base.update({
            "metrics": [metrica],
            "x_axis": chart_cfg.get("eje_x", "ciclo"),
            "groupby": [],
            "timeseries_limit": 0,
            "y_axis_format": formato,
            "rich_tooltip": True,
            "show_value": True,
        })
    elif viz == "table":
        base.update({
            "metrics": [metrica],
            "groupby": chart_cfg.get("dimensiones", []),
            "include_time": False,
            "order_desc": True,
            "row_limit": int(chart_cfg.get("row_limit", 50)),
            "page_length": 0,
        })
    elif viz == "pie":
        base.update({
            "metric": metrica,
            "groupby": chart_cfg.get("dimensiones", []),
            "row_limit": int(chart_cfg.get("row_limit", 20)),
            "sort_by_metric": True,
        })
    elif viz == "deck_polygon":
        # Coroplético: la geometría viaja como texto GeoJSON en `geometria`
        # (columna del dataset), la llave contra el GeoJSON remoto es `llave_geo`.
        base.update({
            "metric": metrica,
            "line_column": chart_cfg.get("columna_geometria", "geometria"),
            "line_type": "json",
            "fill_color_color_scheme": "superset_seq_YlOrRd",
            "reverse_long_lat": False,
            "mapbox_style": chart_cfg.get(
                "basemap", "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            ),
            "raster_layer_name": chart_cfg.get("basemap_nombre", "OpenStreetMap"),
            "js_columns": chart_cfg.get("tooltip_columnas", []),
            "autozoom": True,
            "opacity": 0.85,
            "extruded": False,
        })
    elif viz == "deck_scatter":
        base.update({
            "point_radius_fixed": {"type": "fixed", "value": chart_cfg.get("radio_px", 8)},
            "point_unit": "pixels",
            "dimension_field": chart_cfg.get("categoria", ""),
            "spatial": {
                "type": "latlong",
                "lonCol": chart_cfg.get("longitud", "longitud"),
                "latCol": chart_cfg.get("latitud", "latitud"),
            },
            "color_picker": {"a": 1, "b": 30, "g": 60, "r": 200},
            "mapbox_style": chart_cfg.get(
                "basemap", "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
            ),
            "raster_layer_name": chart_cfg.get("basemap_nombre", "OpenStreetMap"),
            "js_columns": chart_cfg.get("tooltip_columnas", []),
            "autozoom": True,
        })

    base.update(chart_cfg.get("params_extra", {}))
    return base


def ensure_chart(token: str, csrf: str, chart_cfg: dict, datasets_by_name: dict[str, int], yaml_datasets: list[dict]) -> tuple[int, str]:
    """Crea o actualiza un chart. Retorna (id, uuid)."""
    nombre = chart_cfg["nombre"]
    dataset_name = chart_cfg["dataset"]
    if dataset_name not in datasets_by_name:
        print(f"    ✗ Chart '{nombre}': dataset '{dataset_name}' no existe, se omite")
        return -1, ""
    ds_id = datasets_by_name[dataset_name]

    formato = _formato_de_metrica(yaml_datasets, dataset_name, chart_cfg["metrica"])
    params = _params_chart(chart_cfg, ds_id, formato)

    # Los nombres llevan acentos y '·': el filtro va como JSON URL-encoded.
    filtro = urllib.parse.quote(json.dumps({
        "filters": [{"col": "slice_name", "opr": "eq", "value": nombre}],
    }), safe="")
    resp = _request("GET", f"/api/v1/chart/?q={filtro}", token=token)
    homonimos = [c for c in resp.get("result", []) if c.get("slice_name") == nombre]
    # El slice_name NO es identidad global: dos tableros pueden tener charts
    # homónimos sobre datasets distintos (hallazgo de US-212 — DB-01 y DB-03/04
    # compartían nombres y el sync repuntaba el chart ajeno sin avisar). Solo se
    # actualiza el candidato que apunta al MISMO dataset; los demás quedan
    # intactos y aquí se crea un chart nuevo para este tablero.
    existente = None
    for candidato in homonimos:
        ds_candidato = candidato.get("datasource_id")
        if ds_candidato is None:
            detalle_c = _request("GET", f"/api/v1/chart/{candidato['id']}", token=token).get("result", {})
            ds_candidato = detalle_c.get("datasource_id")
        if ds_candidato == ds_id:
            existente = candidato
            break

    body = {
        "slice_name": nombre,
        "datasource_id": ds_id,
        "datasource_type": "table",
        "viz_type": chart_cfg["viz"],
        "params": json.dumps(params),
    }
    if existente:
        chart_id = existente["id"]
        _request("PUT", f"/api/v1/chart/{chart_id}", token=token, csrf_token=csrf, body={
            "slice_name": nombre,
            "viz_type": chart_cfg["viz"],
            "params": json.dumps(params),
        })
        print(f"    ✔ Chart '{nombre}' actualizado (id={chart_id})")
    else:
        if homonimos:
            print(f"    ⚠ '{nombre}': existe con ese nombre en otro dataset; "
                  f"se crea copia para este tablero (el chart ajeno no se toca)")
        creado = _request("POST", "/api/v1/chart/", token=token, csrf_token=csrf, body=body)
        chart_id = creado.get("id")
        print(f"    ✔ Chart '{nombre}' creado (id={chart_id})")

    detalle = _request("GET", f"/api/v1/chart/{chart_id}", token=token).get("result", {})
    return chart_id, str(detalle.get("uuid", ""))


def validar_chart(token: str, ds_id: int, chart_cfg: dict) -> bool:
    """Valida que la consulta del chart corre, vía el endpoint bulk /chart/data."""
    metrica = chart_cfg["metrica"]
    columnas = list(chart_cfg.get("dimensiones", []))
    if (viz := chart_cfg.get("eje_x")) and viz not in columnas:
        columnas.append(viz)
    query: dict[str, Any] = {"row_limit": 10}
    if chart_cfg["viz"] == "deck_polygon":
        # el coroplético trae geometrías pesadas: basta validar las métricas
        query.update({"metrics": [metrica], "columns": []})
    else:
        query.update({"metrics": [metrica], "columns": columnas})
    try:
        resp = _request("POST", "/api/v1/chart/data", token=token, body={
            "datasource": {"id": ds_id, "type": "table"},
            "queries": [query],
        })
        result = resp.get("result", [])
        filas = len(result[0].get("data", [])) if result else 0
        print(f"      ✓ datos OK ({filas} fila(s))")
        return True
    except Exception as exc:  # noqa: BLE001 - cualquier fallo de consulta invalida el chart
        print(f"      ✗ {chart_cfg['nombre']}: la consulta falló → {str(exc)[:160]}")
        return False


def _layout_grilla(charts_con_layout: list[tuple[int, str, int, int]]) -> dict:
    """Genera position_json v2 con el árbol exacto que espera el frontend:
    ROOT_ID → GRID_ID → filas → componentes CHART (con parentId en cada nodo)."""
    position: dict[str, Any] = {"DASHBOARD_VERSION_KEY": "v2"}
    rows: list[str] = []
    for i, (cid, nombre, width, height) in enumerate(charts_con_layout):
        row_id = f"ROW-{i}"
        comp_id = f"CHART-{i}"
        rows.append(row_id)
        position[row_id] = {
            "type": "ROW",
            "id": row_id,
            "parentId": "GRID_ID",
            "children": [comp_id],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }
        position[comp_id] = {
            "type": "CHART",
            "id": comp_id,
            "parentId": row_id,
            "children": [],
            "meta": {
                "chartId": cid,
                "sliceName": nombre,
                "width": width,
                "height": height,
            },
        }
    position["ROOT_ID"] = {"type": "GRID", "id": "ROOT_ID", "children": ["GRID_ID"]}
    position["GRID_ID"] = {
        "type": "GRID",
        "id": "GRID_ID",
        "parentId": "ROOT_ID",
        "children": rows,
    }
    return position


def _layout_tabs(
    tabs: list[tuple[str, str, list[tuple[int, str, int, int]], str | None]]
) -> dict:
    """Genera position_json v2 con tabs (US-213), árbol validado por Manuel Serranía:
    ROOT_ID(TABS) → TAB-<id> → GRID-<id> → filas → CHART|MARKDOWN.

    Cambio aditivo: función hermana de `_layout_grilla()`, no la reemplaza — los
    tableros ya sincronizados (camino plano, sin tabs) siguen usando
    `_layout_grilla()` sin ningún cambio.

    `tabs` es una lista de (tab_id, tab_label, charts_con_layout, nota_opcional).
    `charts_con_layout` tiene el mismo formato tupla que ya usa `_layout_grilla()`.
    Si `nota_opcional` no es None, se agrega un nodo MARKDOWN estático (meta.code)
    como la primera fila del GRID del tab — aprobado por Manuel junto con los
    tabs, mismo PR: la nota de fuente/nivel de medición del driver es texto
    estático en el YAML (no una consulta), tal como ya anticipa el contrato
    (`fuente_driver`). Id estable `MD-{tab_id}-0` para que el sync sea idempotente.
    """
    position: dict[str, Any] = {"DASHBOARD_VERSION_KEY": "v2"}
    tab_node_ids: list[str] = []
    contador = 0
    for tab_id, tab_label, charts_con_layout, nota in tabs:
        tab_node_id = f"TAB-{tab_id}"
        grid_node_id = f"GRID-{tab_id}"
        rows: list[str] = []

        if nota:
            md_row_id = f"ROW-MD-{tab_id}"
            md_id = f"MD-{tab_id}-0"
            rows.append(md_row_id)
            position[md_row_id] = {
                "type": "ROW",
                "id": md_row_id,
                "parentId": grid_node_id,
                "children": [md_id],
                "meta": {"background": "BACKGROUND_TRANSPARENT"},
            }
            position[md_id] = {
                "type": "MARKDOWN",
                "id": md_id,
                "parentId": md_row_id,
                "children": [],
                "meta": {"code": nota, "width": 12, "height": 8},
            }

        for cid, nombre, width, height in charts_con_layout:
            row_id = f"ROW-{contador}"
            comp_id = f"CHART-{contador}"
            contador += 1
            rows.append(row_id)
            position[row_id] = {
                "type": "ROW",
                "id": row_id,
                "parentId": grid_node_id,
                "children": [comp_id],
                "meta": {"background": "BACKGROUND_TRANSPARENT"},
            }
            position[comp_id] = {
                "type": "CHART",
                "id": comp_id,
                "parentId": row_id,
                "children": [],
                "meta": {
                    "chartId": cid,
                    "sliceName": nombre,
                    "width": width,
                    "height": height,
                },
            }
        position[grid_node_id] = {
            "type": "GRID",
            "id": grid_node_id,
            "parentId": tab_node_id,
            "children": rows,
        }
        position[tab_node_id] = {
            "type": "TAB",
            "id": tab_node_id,
            "parentId": "ROOT_ID",
            "children": [grid_node_id],
            "meta": {"text": tab_label},
        }
        tab_node_ids.append(tab_node_id)

    position["ROOT_ID"] = {"type": "TABS", "id": "ROOT_ID", "children": tab_node_ids}
    return position


def _uuid_estable(*partes: str) -> str:
    """UUID determinístico por nombre, para que el sync sea reproducible."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"faro-us203:{':'.join(partes)}"))


def _yaml_dump(obj: Any) -> str:
    """Serializa a YAML para el bundle de importación."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError(
            "El bundle de tableros requiere PyYAML (pip install pyyaml)"
        ) from exc
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)


# ---------------------------------------------------------------------------
# Bundle de importación v1 (Superset >= 4: única vía que llena dashboard_slices)
# ---------------------------------------------------------------------------

def _detalle_dataset(token: str, ds_id: int) -> dict:
    """Detalle completo de un dataset (columnas, métricas, base, uuid)."""
    return _request("GET", f"/api/v1/dataset/{ds_id}", token=token).get("result", {})


_db_export_cache: dict[int, dict] = {}


def _export_database(token: str, db_id: int) -> dict:
    """Entrada databases/ del bundle. El importador la casa por uuid y no
    toca nada si ya existe (overwrite=False), así que basta lo mínimo."""
    if db_id in _db_export_cache:
        return _db_export_cache[db_id]
    detalle = _request("GET", f"/api/v1/database/{db_id}", token=token).get("result", {})
    export = {
        "database_name": detalle.get("database_name", "faro"),
        "sqlalchemy_uri": detalle.get("sqlalchemy_uri")
            or f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "uuid": detalle.get("uuid") or _uuid_estable("database"),
        "version": "1.0.0",
        "expose_in_sqllab": False,
        "allow_run_async": False,
        "allow_ctas": False,
        "allow_cvas": False,
        "allow_dml": False,
        "allow_csv_upload": False,
        "impersonate_user": False,
        "extra": {},
    }
    _db_export_cache[db_id] = export
    return export


def _export_dataset(detalle: dict, db_uuid: str) -> dict:
    """Entrada datasets/ del bundle a partir del detalle REST del dataset."""
    columnas = []
    for col in detalle.get("columns", []):
        extra = col.get("extra")
        columnas.append({
            "column_name": col.get("column_name"),
            "verbose_name": col.get("verbose_name"),
            "is_dttm": bool(col.get("is_dttm")),
            "type": col.get("type"),
            "groupby": bool(col.get("groupby")),
            "filterable": bool(col.get("filterable")),
            "expression": col.get("expression"),
            "description": col.get("description"),
            "python_date_format": col.get("python_date_format"),
            "extra": json.loads(extra) if isinstance(extra, str) else extra,
        })
    metricas = []
    for met in detalle.get("metrics", []):
        if not met.get("metric_name"):
            continue
        extra = met.get("extra")
        metricas.append({
            "metric_name": met["metric_name"],
            "verbose_name": met.get("verbose_name"),
            "metric_type": met.get("metric_type"),
            "expression": met.get("expression") or met["metric_name"],
            "description": met.get("description"),
            "d3format": met.get("d3format"),
            "extra": json.loads(extra) if isinstance(extra, str) else extra,
        })
    return {
        "table_name": detalle.get("table_name"),
        "sql": detalle.get("sql"),
        "schema": detalle.get("schema"),
        "description": detalle.get("description"),
        "main_dttm_col": detalle.get("main_dttm_col") or None,
        "offset": 0,
        "cache_timeout": detalle.get("cache_timeout"),
        "params": detalle.get("params") or {},
        "filter_select_enabled": True,
        "extra": {},
        "uuid": str(detalle.get("uuid")),
        "database_uuid": db_uuid,
        "version": "1.0.0",
        "columns": columnas,
        "metrics": metricas,
    }


def _export_chart(chart_cfg: dict, params: dict, chart_uuid: str, dataset_uuid: str) -> dict:
    return {
        "slice_name": chart_cfg["nombre"],
        "viz_type": chart_cfg["viz"],
        "params": params,
        "query_context": None,
        "cache_timeout": None,
        "uuid": chart_uuid,
        "dataset_uuid": dataset_uuid,
        "version": "1.0.0",
    }


def _importar_bundle(token: str, csrf: str, files: dict[str, str]) -> None:
    """POST /dashboard/import/ con un ZIP en memoria (multipart)."""
    import io
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # El importador v1 exige que todo viva bajo una carpeta raíz
        # (remove_root() quita el primer componente de cada ruta) y un
        # metadata.yaml con la versión: sin ambos cae al importador v0.
        raiz = "faro"
        zf.writestr(f"{raiz}/metadata.yaml", _yaml_dump({
            "version": "1.0.0",
            "type": "Dashboard",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }))
        for nombre, contenido in files.items():
            zf.writestr(f"{raiz}/{nombre}", contenido)
    zip_bytes = buffer.getvalue()

    boundary = f"----faro{uuid.uuid4().hex}"
    # El endpoint lee overwrite del FORM, no del query string.
    partes = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n".encode(),
        (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"formData\"; filename=\"bundle.zip\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + zip_bytes + b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    cuerpo = b"".join(partes)

    _request(
        "POST",
        "/api/v1/dashboard/import/",
        token=token,
        csrf_token=csrf,
        raw_body=cuerpo,
        content_type=f"multipart/form-data; boundary={boundary}",
    )


def _position_con_uuid(position: dict, charts_con_uuid: list[tuple[int, str]]) -> dict:
    """Inyecta meta.uuid en cada nodo CHART (el importador v1 remapea por ahí)."""
    por_indice = [u for _, u in sorted(charts_con_uuid)]
    i = 0
    for child in position.values():
        if isinstance(child, dict) and child.get("type") == "CHART":
            if i < len(por_indice) and por_indice[i]:
                child["meta"]["uuid"] = por_indice[i]
            i += 1
    return position


def _resolver_valor_mas_reciente(token: str, ds_id: int, columna: str) -> Any | None:
    """Resuelve el valor mas reciente de una columna contra los datos reales (ORDER BY DESC LIMIT 1).

    Usado para defaults declarativos tipo `default: ultimo_ciclo`: nunca se hardcodea
    el ciclo vigente en el codigo -- si hoy responde "2024-2025" y el proximo ciclo
    carga "2025-2026", el default se mueve solo en la siguiente corrida del sync.
    """
    try:
        resp = _request("POST", "/api/v1/chart/data", token=token, body={
            "datasource": {"id": ds_id, "type": "table"},
            "queries": [{"columns": [columna], "orderby": [[columna, False]], "row_limit": 1}],
        })
        filas = resp.get("result", [{}])[0].get("data", [])
        return filas[0].get(columna) if filas else None
    except Exception as e:  # noqa: BLE001 - sin default dinamico el filtro sigue funcionando, solo sin preseleccion
        print(f"    ⚠ No se pudo resolver el valor por defecto de '{columna}': {e}")
        return None


def _filtros_nativos(
    cfg_dashboard: dict,
    datasets_uuids: dict[str, str],
    token: str | None = None,
    datasets_by_name: dict[str, int] | None = None,
) -> list[dict]:
    """Arma la configuración de filtros nativos globales (AC-002.2).

    Formato Superset 6: `filterType: filter_select` (el viejo
    `native_filters.SelectFilter` ya no está registrado) y los targets van por
    `datasetUuid`; el importador v1 los remapea a datasetId.

    Dos formas de fijar un valor por defecto, ambas OPCIONALES y aditivas —
    un filtro que no declara ninguna se comporta igual que antes:

    - `valor_por_defecto` (US-214a, Marina García): valor(es) explícitos y
      estáticos en el YAML. Simple, pero "al cargar un ciclo nuevo hay que
      actualizar este valor" a mano en cada tablero.
    - `default: ultimo_<algo>` (BUG-047): resuelve el valor dinámicamente
      contra los datos reales (requiere `token`/`datasets_by_name`; sin
      ellos, esta rama simplemente no aplica). Nunca queda desactualizado.

    Si un filtro declara ambas, `default` dinámico gana cuando logra
    resolver un valor; `valor_por_defecto` queda como respaldo si la
    resolución dinámica no está disponible o falla (sin red, sin token).
    """
    filtros = []
    for i, f_cfg in enumerate(cfg_dashboard.get("filtros_globales", [])):
        # targets planos: el importador v1 hace target.get("datasetUuid")
        targets = []
        for ds_name in f_cfg.get("datasets", []):
            if ds_uuid := datasets_uuids.get(ds_name):
                targets.append({"column": {"name": f_cfg["columna"]}, "datasetUuid": ds_uuid})
        if not targets:
            continue
        filtro: dict[str, Any] = {
            "id": f"NATIVE_FILTER-US203-{i}",
            "name": f_cfg.get("etiqueta", f_cfg["columna"]),
            "filterType": "filter_select",
            "type": "NATIVE_FILTER",
            "controlValues": {"enableEmptyFilter": False, "multiSelect": True},
            "targets": targets,
            "scope": {"rootPath": ["ROOT_ID"], "excluded": []},
        }

        # BUG-047: `default: ultimo_<algo>` se documentaba en el contrato semantico
        # pero nunca se traducia en un defaultDataMask real -- el filtro nacia sin
        # preseleccion y, con enableEmptyFilter=False + multiSelect=True, Superset
        # preseleccionaba TODAS las opciones (los 3 ciclos), triplicando cualquier
        # metrica SUM() aguas abajo (ver tests/test_filtros_nativos_default_dinamico.py).
        valores: list[Any] | None = None
        default_cfg = f_cfg.get("default", "")
        if default_cfg.startswith("ultimo_") and token and datasets_by_name:
            ds_name = next((d for d in f_cfg.get("datasets", []) if d in datasets_by_name), None)
            valor = (
                _resolver_valor_mas_reciente(token, datasets_by_name[ds_name], f_cfg["columna"])
                if ds_name else None
            )
            if valor is not None:
                valores = [valor]

        # `valor_por_defecto` (US-214a) — respaldo estático si no hubo resolución
        # dinámica (sin red/token, o el filtro no declara `default: ultimo_*`).
        if valores is None and (valor := f_cfg.get("valor_por_defecto")) is not None:
            valores = valor if isinstance(valor, list) else [valor]

        if valores is not None:
            filtro["defaultDataMask"] = {
                "extraFormData": {"filters": [{"col": f_cfg["columna"], "op": "IN", "val": valores}]},
                "filterState": {
                    "label": ", ".join(str(v) for v in valores),
                    "validateStatus": False,
                    "value": valores,
                },
                "ownState": {},
            }

        filtros.append(filtro)
    return filtros


def ensure_dashboard(token: str, csrf: str, dash_cfg: dict, datasets_by_name: dict[str, int], yaml_datasets: list[dict], db_id: int, validar_datos: bool) -> None:
    """Crea o actualiza un dashboard con sus charts, layout y filtros nativos.

    Superset >= 4 no asocia charts vía REST PUT (solo el flujo de importación
    v1 llena `dashboard_slices`), así que los charts se crean/actualizan por
    REST y luego todo se adjunta al tablero con POST /dashboard/import/.
    """
    titulo = dash_cfg["titulo"]
    slug = dash_cfg["slug"]
    print(f"\n▸ Dashboard '{titulo}'...")

    # US-213: dashboards con un tab por driver (clave `tabs:` en vez de `charts:`
    # en la raíz). Cambio aditivo -- si no hay `tabs`, el camino de abajo es
    # exactamente el de antes, para los tableros ya sincronizados.
    usa_tabs = "tabs" in dash_cfg
    charts_validos: list[tuple[dict, int, str]] = []
    todos_los_charts: list[dict] = []
    layout: list[tuple[int, str, int, int]] = []
    tabs_layout: list[tuple[str, str, list[tuple[int, str, int, int]], str | None]] = []

    if usa_tabs:
        for tab_cfg in dash_cfg["tabs"]:
            layout_tab: list[tuple[int, str, int, int]] = []
            for ch in tab_cfg.get("charts", []):
                todos_los_charts.append(ch)
                cid, ch_uuid = ensure_chart(token, csrf, ch, datasets_by_name, yaml_datasets)
                if cid == -1:
                    continue
                charts_validos.append((ch, cid, ch_uuid))
                if validar_datos:
                    validar_chart(token, datasets_by_name[ch["dataset"]], ch)
                layout_tab.append((cid, ch["nombre"], int(ch.get("ancho", 12)), int(ch.get("alto", ALTO_GRAFICO))))
            tabs_layout.append((
                tab_cfg["id"], tab_cfg.get("etiqueta", tab_cfg["id"]), layout_tab, tab_cfg.get("nota"),
            ))
    else:
        for ch in dash_cfg.get("charts", []):
            todos_los_charts.append(ch)
            cid, ch_uuid = ensure_chart(token, csrf, ch, datasets_by_name, yaml_datasets)
            if cid == -1:
                continue
            charts_validos.append((ch, cid, ch_uuid))
            if validar_datos:
                validar_chart(token, datasets_by_name[ch["dataset"]], ch)
            layout.append((cid, ch["nombre"], int(ch.get("ancho", 12)), int(ch.get("alto", ALTO_GRAFICO))))

    if not charts_validos:
        print("    ✗ Sin charts válidos; dashboard no creado")
        return

    # Datasets involucrados (charts + filtros nativos), con uuid real.
    datasets_invueltos = {ch["dataset"] for ch in todos_los_charts if ch["dataset"] in datasets_by_name}
    for f in dash_cfg.get("filtros_globales", []):
        datasets_invueltos.update(ds for ds in f.get("datasets", []) if ds in datasets_by_name)
    detalles_ds = {ds: _detalle_dataset(token, datasets_by_name[ds]) for ds in sorted(datasets_invueltos)}
    datasets_uuids = {ds: str(det["uuid"]) for ds, det in detalles_ds.items()}

    json_metadata: dict[str, Any] = {
        "refresh_frequency": 0,
        "stagger_refresh": False,
        "expanded_slices": {},
        "default_filters": "{}",
        "timed_refresh_immune_slices": [],
        "chart_configuration": {},
        "cross_filters_enabled": False,
        # OJO: el enum del frontend es 'VERTICAL'/'HORIZONTAL' (mayusculas).
        # Con "vertical" en minusculas el DashboardBuilder no hace match en
        # ninguna comparacion y NO monta la barra de filtros nativos.
        "filter_bar_orientation": "VERTICAL",
        "color_scheme": "",
    }
    nativos = _filtros_nativos(dash_cfg, datasets_uuids, token=token, datasets_by_name=datasets_by_name)
    if nativos:
        json_metadata["native_filter_configuration"] = nativos

    if usa_tabs:
        position = _position_con_uuid(
            _layout_tabs(tabs_layout), [(cid, cu) for _, cid, cu in charts_validos]
        )
    else:
        position = _position_con_uuid(
            _layout_grilla(layout), [(cid, cu) for _, cid, cu in charts_validos]
        )

    db_export = _export_database(token, db_id)
    db_uuid = str(db_export["uuid"])
    files: dict[str, str] = {
        "databases/faro.yaml": _yaml_dump(db_export),
        f"dashboards/{slug}.yaml": _yaml_dump({
            "dashboard_title": titulo,
            "description": None,
            "css": "",
            "slug": slug,
            "uuid": _uuid_estable("dashboard", slug),
            "version": "1.0.0",
            "published": True,
            "certified_by": None,
            "certification_details": None,
            "position": position,
            "metadata": json_metadata,
        }),
    }
    for ch, cid, ch_uuid in charts_validos:
        if not ch_uuid or ch["dataset"] not in datasets_uuids:
            continue
        params = _params_chart(
            ch, datasets_by_name[ch["dataset"]],
            _formato_de_metrica(yaml_datasets, ch["dataset"], ch["metrica"]),
        )
        files[f"charts/chart-{cid}.yaml"] = _yaml_dump(
            _export_chart(ch, params, ch_uuid, datasets_uuids[ch["dataset"]])
        )
    for ds, det in detalles_ds.items():
        files[f"datasets/{ds}.yaml"] = _yaml_dump(_export_dataset(det, db_uuid))

    _importar_bundle(token, csrf, files)
    print(f"    ✔ Dashboard '{titulo}' sincronizado por importación v1")
    print(f"    ➜ {SUPERSET_URL}/superset/dashboard/{slug}/")


def sync_dashboards(token: str, csrf: str, datasets: dict[str, int], db_id: int, validar_datos: bool) -> None:
    """Lee superset/dashboards/*.yaml y crea/actualiza charts + dashboards."""
    yaml_datasets: list[dict] = []
    for yf in sorted(SEMANTIC_DIR.glob("metrics_*.yaml")):
        data = _read_yaml(yf)
        yaml_datasets.extend(data.get("datasets", []))

    for dash_file in sorted(DASHBOARDS_DIR.glob("*.yaml")):
        data = _read_yaml(dash_file)
        for dash_cfg in data.get("dashboards", []):
            ensure_dashboard(token, csrf, dash_cfg, datasets, yaml_datasets, db_id, validar_datos)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-charts", action="store_true",
                        help="Solo capa semántica (datasets/métricas); no crea tableros")
    parser.add_argument("--validar-datos", action="store_true",
                        help="Consulta /chart/<id>/data de cada chart para verificar el SQL")
    args = parser.parse_args()

    print("=" * 60)
    print("FARO — Sync de capa semántica y tableros a Superset")
    print("=" * 60)

    if not ADMIN_PASS:
        print("✗ SUPERSET_ADMIN_PASSWORD no está definido. Exporta las variables de .env")
        sys.exit(1)
    if not DB_PASS:
        print("✗ POSTGRES_PASSWORD no está definido. Exporta las variables de .env")
        sys.exit(1)

    print(f"\nSuperset: {SUPERSET_URL}")
    print(f"Base de datos: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"Directorio semántico: {SEMANTIC_DIR}\n")

    # 1. Login
    token, csrf = login()

    # 2. Conexión a BD
    print("\n▸ Conexión a base de datos...")
    db_id = ensure_database(token, csrf)

    # 3. Datasets virtuales
    print("\n▸ Datasets virtuales...")
    datasets = ensure_datasets(token, csrf, db_id)
    print(f"  Total datasets: {len(datasets)}")

    # 4. Métricas y dimensiones
    print("\n▸ Métricas y dimensiones...")
    sync_metrics(token, csrf, datasets)

    # 5. Charts + dashboards
    if not args.no_charts:
        print("\n▸ Tableros y charts...")
        sync_dashboards(token, csrf, datasets, db_id, args.validar_datos)

    print("\n" + "=" * 60)
    print("✔ Sincronización terminada")
    if not args.no_charts:
        print("⚠ Nota: la preview de datos requiere gold.* materializado en Postgres")
        print("  (dbt run) y, para DB-02, gold.geo_municipio (ver superset/README.md).")
    else:
        print("⚠ Nota: la preview de datos requiere que gold.* exista (Célula 1)")
    print("=" * 60)


if __name__ == "__main__":
    main()
