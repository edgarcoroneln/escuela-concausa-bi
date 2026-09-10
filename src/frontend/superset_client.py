"""Cliente del guest token de Superset para el embebido de dashboards (US-206).

El front habla directo con Superset: autentica con el usuario admin (login provider "db"),
resuelve el id de cada dashboard por slug, **habilita el embedding** de cada uno (idempotente)
para obtener su ``embedded_uuid`` y solicita **un** guest token que cubre todos los uuids.
Devuelve el dominio de Superset + el guest token + los uuids para que el navegador los monte
con el Embedded SDK de Superset (``@superset-ui/embedded-sdk``).

IMPORTANTE (por qué NO se pone el guest token en la URL del iframe): Superset NO autentica
por ``?guest_token=`` en la URL. El guest token viaja al iframe ``/embedded/{uuid}`` por el
canal ``postMessage`` que abre el SDK (``fetchGuestToken``). Por eso el recurso del token debe
ser el ``embedded_uuid`` (no el uuid regular del dashboard) y el render se hace con el SDK.

Requiere del lado de despliegue (C5): ``SUPERSET_EMBEDDED=true`` en el contenedor de Superset
(activa ``FEATURE_FLAGS[EMBEDDED_SUPERSET]`` + ``GUEST_TOKEN_JWT_SECRET``). Ver
docker/superset_config.py §7 y vault/03_Architecture/Frontend_Architecture.md §4.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx

# URL con la que el SERVIDOR (este contenedor) habla con Superset (login, guest token).
SUPERSET_URL = os.environ.get("SUPERSET_URL", "http://127.0.0.1:8088").rstrip("/")
# URL con la que el NAVEGADOR carga el SDK y el iframe /embedded/{uuid}. En Cloud Run
# coincide con SUPERSET_URL (ambos son la URL pública); en local difiere (el servidor
# usa http://superset:8088 pero el navegador necesita http://localhost:8088).
SUPERSET_PUBLIC_URL = os.environ.get("SUPERSET_PUBLIC_URL", SUPERSET_URL).rstrip("/")
ADMIN_USER = os.environ.get("SUPERSET_ADMIN_USERNAME", "faro_superset_admin")
ADMIN_PASS = os.environ.get("SUPERSET_ADMIN_PASSWORD", "")

# Origen (scheme://host[:port]) del shell, para el allowed_domains del embed. Si no se
# puede derivar, se deja vacío ⇒ Superset permite embeber desde cualquier dominio (el
# guest token de vida corta y acotado por recurso sigue siendo la frontera de seguridad).
_FRONTEND_URL = os.environ.get("FARO_FRONTEND_URL", "").strip()


def _origen(url: str) -> str:
    """Devuelve scheme://host[:port] de una URL, o '' si no es derivable."""
    if not url:
        return ""
    partes = urlsplit(url)
    if not partes.scheme or not partes.netloc:
        return ""
    return f"{partes.scheme}://{partes.netloc}"


_ALLOWED_DOMAINS = [d for d in (_origen(_FRONTEND_URL), _origen(SUPERSET_PUBLIC_URL)) if d]

# Catálogo de los 10 dashboards por slug (DB-01…DB-10 declarados en superset/dashboards/*.yaml).
DASHBOARDS: tuple[dict[str, str], ...] = (
    {"id": "db01", "titulo": "Panel Ejecutivo", "slug": "db01-ejecutivo"},
    {"id": "db02", "titulo": "Mapa de Riesgo", "slug": "db02-mapa-riesgo"},
    {"id": "db03", "titulo": "Ficha de Escuela", "slug": "db03-ficha-escuela"},
    {"id": "db04", "titulo": "Comparador de Municipio", "slug": "db04-comparador-municipio"},
    {"id": "db05", "titulo": "Análisis de Driver", "slug": "db05-analisis-driver"},
    {"id": "db06", "titulo": "Predicciones", "slug": "db06-predicciones"},
    {"id": "db07", "titulo": "Calidad de Cobertura", "slug": "db07-calidad-cobertura"},
    {"id": "db08", "titulo": "Explorador de Cubo", "slug": "db08-explorador-cubo"},
    {"id": "db09", "titulo": "Recomendaciones", "slug": "db09-recomendaciones"},
    {"id": "db10", "titulo": "Monitor de Pipeline", "slug": "db10-monitor-pipeline"},
)

# RLS por rol. ciudadano ve solo su alcance público; analista ve todo. (Sin cláusulas hoy:
# el acotado por rol se afina en Superset; se conserva el gancho para no cambiar la firma.)
RLS_CLAUSES: dict[str, list[dict[str, str]]] = {
    "ciudadano": [],
    "analista": [],
}


class SupersetDeshabilitado(Exception):
    """Superset no expone guest token (falta ``SUPERSET_EMBEDDED=true`` del lado C5)."""


class SupersetError(Exception):
    """Fallo de autenticación o de solicitud del guest token a Superset."""


def _login(cliente: httpx.Client) -> tuple[str, str]:
    """Autentica (provider "db") y devuelve (access_token, csrf_token).

    El ``cliente`` conserva la cookie de sesión entre llamadas (jar de httpx), necesaria
    para que el CSRF del POST del guest token valide.
    """
    if not ADMIN_PASS:
        raise SupersetError(
            "SUPERSET_ADMIN_PASSWORD no está definido. Exporta las variables de .env."
        )
    resp = cliente.post(
        "/api/v1/security/login",
        json={
            "username": ADMIN_USER,
            "password": ADMIN_PASS,
            "provider": "db",
            "refresh": True,
        },
    )
    if resp.status_code != 200:
        raise SupersetError(
            f"No se pudo autenticar en Superset (HTTP {resp.status_code})."
        )
    token = resp.json().get("access_token", "")
    if not token:
        raise SupersetError("Superset no devolvió access_token.")

    # CSRF: necesario para los POST (guest token, habilitar embed) con WTF_CSRF_ENABLED.
    csrf = ""
    resp_csrf = cliente.get(
        "/api/v1/security/csrf_token/",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp_csrf.status_code == 200:
        csrf = resp_csrf.json().get("result", "")
    return token, csrf


def _cabeceras(token: str, csrf: str) -> dict[str, str]:
    """Cabeceras de escritura: Bearer + CSRF + Referer (que el CSRF de Superset exige)."""
    cab = {"Authorization": f"Bearer {token}"}
    if csrf:
        cab["X-CSRFToken"] = csrf
        cab["Referer"] = SUPERSET_URL
    return cab


def _id_por_slug(cliente: httpx.Client, token: str, slug: str) -> int | None:
    """Resuelve el id numérico del dashboard consultando la API por slug."""
    resp = cliente.get(
        "/api/v1/dashboard/",
        params={"q": f"(filters:!((col:slug,opr:eq,value:{slug})))"},
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code != 200:
        return None
    items = resp.json().get("result", [])
    if not items:
        return None
    try:
        return int(items[0]["id"])
    except (KeyError, ValueError, TypeError):
        return None


def _embedded_uuid(
    cliente: httpx.Client, token: str, csrf: str, dash_id: int
) -> str | None:
    """Habilita (idempotente) el embedding del dashboard y devuelve su ``embedded_uuid``.

    ``POST /dashboard/{id}/embedded`` hace *upsert*: si ya estaba habilitado, actualiza
    allowed_domains y devuelve el mismo uuid. Si no, lo crea.
    """
    resp = cliente.post(
        f"/api/v1/dashboard/{dash_id}/embedded",
        json={"allowed_domains": _ALLOWED_DOMAINS},
        headers={**_cabeceras(token, csrf), "Content-Type": "application/json"},
    )
    if resp.status_code in (401, 403):
        raise SupersetDeshabilitado(
            "Superset rechazó habilitar el embedding (¿falta SUPERSET_EMBEDDED=true en el "
            "contenedor de Superset?). Actívalo del lado de despliegue (C5)."
        )
    if resp.status_code not in (200, 201):
        return None
    return resp.json().get("result", {}).get("uuid")


def _guest_token(
    cliente: httpx.Client,
    token: str,
    csrf: str,
    uuids: list[str],
    rol: str,
) -> str:
    """POST ``/api/v1/security/guest_token/`` para un token que cubre todos los uuids."""
    recursos = [{"type": "dashboard", "id": u} for u in uuids]
    resp = cliente.post(
        "/api/v1/security/guest_token/",
        json={
            "user": {"username": "faro_guest", "first_name": "FARO", "last_name": "Invitado"},
            "resources": recursos,
            "rls": RLS_CLAUSES.get(rol, []),
        },
        headers={**_cabeceras(token, csrf), "Content-Type": "application/json"},
    )
    if resp.status_code in (401, 403):
        raise SupersetDeshabilitado(
            "Superset rechazó el guest token (¿falta SUPERSET_EMBEDDED=true / "
            "GUEST_TOKEN_JWT_SECRET en la config del contenedor?). Habilítalo (C5)."
        )
    if resp.status_code != 200:
        raise SupersetError(
            f"Superset devolvió HTTP {resp.status_code} al pedir el guest token."
        )
    guest = resp.json().get("token", "")
    if not guest:
        raise SupersetDeshabilitado("Superset no devolvió token en el guest token.")
    return guest


@dataclass(frozen=True)
class TableroEmbebido:
    """Un dashboard listo para montar con el Embedded SDK."""

    id: str
    titulo: str
    slug: str
    uuid: str  # embedded_uuid (el recurso del guest token)


@dataclass(frozen=True)
class PanelSuperset:
    """Todo lo que el navegador necesita para montar los dashboards con el SDK."""

    superset_domain: str  # dominio que usa el navegador (SUPERSET_PUBLIC_URL)
    guest_token: str  # token compartido que cubre todos los uuids
    tableros: list[TableroEmbebido]


def tableros_embebidos(
    rol: str = "ciudadano", cliente: httpx.Client | None = None
) -> PanelSuperset:
    """Devuelve el panel de dashboards embebibles para el rol, o lanza SupersetDeshabilitado.

    Sin token válido NO devuelve tableros: el llamador no monta ningún iframe (AC-002.1).
    ``cliente`` se inyecta para pruebas (mismo patrón DI del frontend); si viene None, se crea
    un httpx.Client contra SUPERSET_URL.
    """
    propio = cliente is None
    if cliente is None:
        cliente = httpx.Client(base_url=SUPERSET_URL, timeout=30.0)
    try:
        token, csrf = _login(cliente)
        tableros: list[TableroEmbebido] = []
        for d in DASHBOARDS:
            slug = d["slug"]
            if not slug:
                continue
            dash_id = _id_por_slug(cliente, token, slug)
            if dash_id is None:
                continue
            uuid = _embedded_uuid(cliente, token, csrf, dash_id)
            if not uuid:
                continue
            tableros.append(
                TableroEmbebido(id=d["id"], titulo=d["titulo"], slug=slug, uuid=uuid)
            )
        if not tableros:
            raise SupersetError(
                "No se resolvieron dashboards embebibles en Superset "
                "(¿están publicados los slugs DB-01…DB-10?)."
            )
        guest = _guest_token(cliente, token, csrf, [t.uuid for t in tableros], rol)
        return PanelSuperset(
            superset_domain=SUPERSET_PUBLIC_URL,
            guest_token=guest,
            tableros=tableros,
        )
    finally:
        if propio:
            cliente.close()
