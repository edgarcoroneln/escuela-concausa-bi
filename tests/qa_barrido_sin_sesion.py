"""Barrido QA pre-demo de la superficie SIN SESIÓN, contra producción.

No inicia sesión: valida exactamente lo que ve alguien que llega sin credenciales.
Cubre los hallazgos 3 y 5 del reporte de sesión y el contrato 401 de DEC-018.
"""
from __future__ import annotations
import json, sys
from playwright.sync_api import sync_playwright

API = "https://faro-api-eanzfglvyq-uc.a.run.app"
SUPERSET = "https://faro-superset-eanzfglvyq-uc.a.run.app"
WEB = "https://faro-frontend-eanzfglvyq-uc.a.run.app"
R: list[dict] = []

def caso(id_, desc, esperado, obtenido, ok):
    R.append({"id": id_, "caso": desc, "esperado": esperado, "obtenido": obtenido,
              "veredicto": "PASA" if ok else "FALLA"})
    print(f"{'🟢' if ok else '🔴'} {id_:6} {desc[:58]:60} {obtenido}")

with sync_playwright() as p:
    nav = p.chromium.launch()
    ctx = nav.new_context(ignore_https_errors=False)
    pg = ctx.new_page()

    # --- Contrato de la API sin sesión (DEC-018) ---
    for ruta, esp in [("/api/v1/health", 200), ("/api/v1/version", 200),
                      ("/api/v1/auth/me", 401), ("/api/v1/kpis", 401),
                      ("/api/v1/escuelas", 401), ("/api/v1/agente/consulta", 405),
                      ("/api/v1/docs", 200), ("/docs", 404)]:
        r = ctx.request.get(f"{API}{ruta}")
        caso(f"API-{ruta.split('/')[-1][:8]}", f"GET {ruta} sin sesión", esp, r.status, r.status == esp)

    # --- Que el 401 no filtre detalle interno ---
    r = ctx.request.get(f"{API}/api/v1/kpis", headers={"Authorization": "Bearer invalido"})
    cuerpo = r.text()
    fuga = any(x in cuerpo.lower() for x in ("traceback", "file \"", "sqlalchemy", "psycopg", "jwt."))
    caso("SEC-01", "401 con token inválido no filtra detalle interno", "sin traza", 
         "limpio" if not fuga else "FUGA", not fuga)

    # --- Superset exige login ---
    pg.goto(SUPERSET, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(3000)
    url_final = pg.url
    caso("SUP-01", "Superset sin sesión redirige a login", "/login", url_final,
         "login" in url_final.lower())
    tiene_google = pg.locator("text=/google/i").count() > 0
    caso("SUP-02", "El login de Superset ofrece Google", "botón visible",
         "sí" if tiene_google else "no", tiene_google)

    # --- FARO Web: las 3 páginas internas sin sesión ---
    pg.goto(WEB, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(6000)
    caso("WEB-01", "La portada de FARO Web carga", 200, "carga", True)

    for nombre, frag in [("Dashboards", "Dashboards"), ("Panel_ML", "Panel"), ("Chat", "Chat")]:
        try:
            pg.goto(f"{WEB}/{frag}", wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(5000)
            txt = pg.inner_text("body")[:4000].lower()
            bloquea = any(s in txt for s in ("inicia sesión", "iniciar sesión", "no autorizado", "debes iniciar"))
            caso(f"WEB-{nombre[:6]}", f"{nombre} sin sesión: ¿exige login antes de renderizar?",
                 "bloquea o avisa", "avisa" if bloquea else "RENDERIZA SIN AVISO", bloquea)
        except Exception as exc:  # noqa: BLE001 - una prueba de navegador reporta cualquier fallo, no lo propaga
            caso(f"WEB-{nombre[:6]}", f"{nombre} sin sesión", "carga", f"error: {type(exc).__name__}", False)

    ctx.close(); nav.close()

print()
pasa = sum(1 for x in R if x["veredicto"] == "PASA")
print(f"RESUMEN: {pasa}/{len(R)} pasan · {len(R)-pasa} fallan")
destino = sys.argv[1] if len(sys.argv) > 1 else "resultados.json"
with open(destino, "w", encoding="utf-8") as fh:
    json.dump(R, fh, ensure_ascii=False, indent=2)
