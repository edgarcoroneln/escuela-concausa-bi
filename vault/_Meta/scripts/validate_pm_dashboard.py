#!/usr/bin/env python3
"""Valida contrato, cobertura y vínculos del snapshot PM (TEST-002)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


VALID_STATES = {"planned", "in_progress", "in_review", "blocked", "done", "descoped"}
# Historias del catálogo (vault/02_Requirements/User_Stories.md), en alcance o recortadas.
CATALOGO_US = 91


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main(root_value: str = ".") -> int:
    root = Path(root_value).resolve()
    data_path = root / "vault/13_Reports/data/pm-dashboard.json"
    html_path = root / "vault/13_Reports/TABLERO_CONTROL_PM.html"
    failures: list[str] = []
    if not data_path.exists() or not html_path.exists():
        print("❌ Ejecuta primero generate_pm_dashboard.py")
        return 1
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if data.get("meta", {}).get("schema_version") != "2.4":
        fail("Se esperaba schema 2.4 con bloques ejecutivos", failures)
    if not re.fullmatch(r"[0-9a-f]{12}", data.get("meta", {}).get("source_fingerprint", "")):
        fail("Fingerprint de fuentes ausente o inválido", failures)
    delivery = data.get("delivery", {})
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", delivery.get("date", "")):
        fail("Fecha canónica de entrega ausente o inválida", failures)
    if delivery.get("source") != "vault/12_Roadmap_Sprints/PLAN_MAESTRO.md":
        fail("La entrega no traza al Plan Maestro", failures)
    stories = data.get("stories", [])
    ids = [story.get("id") for story in stories]
    # El catálogo son 91 historias y sigue siéndolo: recortar no borra la historia, la
    # saca del alcance (DEC-014). La guarda vigila el TOTAL -- alcance + recortadas --
    # para que una US no pueda desaparecer del tablero en silencio, que es lo que esta
    # comprobación existe para impedir.
    catalogo = len(ids) + len(data.get("descoped", []))
    if catalogo != CATALOGO_US:
        fail(f"Se esperaban {CATALOGO_US} US en el catálogo y hay {catalogo} "
             f"({len(ids)} en alcance + {len(data.get('descoped', []))} recortadas)", failures)
    if len(ids) != len(set(ids)):
        fail("Hay US duplicadas en el snapshot", failures)
    for story in stories:
        if not re.fullmatch(r"US-\d{3}[a-z]?", story.get("id", "")):
            fail(f"ID inválido: {story.get('id')}", failures)
        if story.get("status") not in VALID_STATES:
            fail(f"Estado inválido: {story.get('id')}", failures)
        if story.get("status") == "blocked" and story.get("blocked_since") in {"", "—"}:
            fail(f"{story['id']} bloqueada sin fecha", failures)
        if story.get("status") == "done" and story.get("evidence") in {"", "—"}:
            fail(f"{story['id']} done sin evidencia", failures)
        if not story.get("owner_short"):
            fail(f"{story.get('id')} sin owner_short (nombre corto del responsable)", failures)
        # BUG-040: una fila mal formada en Execution_Status desplaza las columnas y mete
        # texto donde va la fecha. El snapshot seguía siendo "válido" porque nadie miraba
        # este campo, y el tablero publicó basura durante días. Ahora falla al generarlo.
        actualizado = story.get("updated", "")
        if actualizado not in {"", "—"} and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", actualizado):
            fail(
                f"{story.get('id')}: 'updated' no es una fecha ({actualizado[:48]!r}). "
                "Suele ser una fila de Execution_Status con columnas desalineadas.",
                failures,
            )
    people = data.get("people", [])
    if len(people) != 21:
        fail(f"Se esperaban 21 personas y hay {len(people)}", failures)
    github_users = [person.get("github_user", "").casefold() for person in people if person.get("github_user")]
    if len(github_users) != len(set(github_users)):
        fail("Hay usuarios de GitHub duplicados en el directorio", failures)
    assigned_ids: list[str] = []
    activity = data.get("git_activity", {})
    prs_by_author: dict[str, int] = {}
    if activity.get("available"):
        for pr in activity.get("prs", []):
            author = str(pr.get("author", "")).casefold()
            prs_by_author[author] = prs_by_author.get(author, 0) + 1
    for person in people:
        if "github_user" not in person or "assigned_story_ids" not in person:
            fail(f"Identidad o US asignadas ausentes para {person.get('name')}", failures)
        if len(person.get("assigned_story_ids", [])) != person.get("stories"):
            fail(f"Conteo de US inconsistente para {person.get('name')}", failures)
        assigned_ids.extend(person.get("assigned_story_ids", []))
        pr_count = person.get("pr_count")
        if pr_count is not None and (not isinstance(pr_count, int) or pr_count < 0):
            fail(f"Conteo de PR inválido para {person.get('name')}", failures)
        github_user = person.get("github_user", "").casefold()
        expected_prs = prs_by_author.get(github_user, 0) if github_user else None
        if activity.get("available") and pr_count != expected_prs:
            fail(f"Conteo de PR no coincide para {person.get('name')}", failures)
        if not activity.get("available") and pr_count is not None:
            fail(f"{person.get('name')} muestra PR sin snapshot de GitHub", failures)
    if sorted(assigned_ids) != sorted(ids):
        fail(f"Las US del equipo no cubren exactamente las {len(ids)} historias en alcance", failures)
    if len(data.get("sources", [])) != 8:
        fail(f"Se esperaban 8 fuentes y hay {len(data.get('sources', []))}", failures)
    if round(sum(item.get("points", 0) for item in data.get("rubric", [])), 2) != 10.0:
        fail("Los puntos de rúbrica no suman 10", failures)
    for item in data.get("rubric", []):
        if item.get("band") not in {"green", "amber", "red"}:
            fail(f"Rúbrica {item.get('req')} sin banda de semáforo válida", failures)
    # Bloques ejecutivos (schema 2.3)
    performance = data.get("performance", {})
    if len(performance.get("people", [])) != 21 or len(performance.get("sprints", [])) != 6:
        fail("Bloque performance incompleto (21 personas × 6 sprints)", failures)
    if performance.get("current_sprint") not in {f"S{i}" for i in range(1, 7)}:
        fail("performance.current_sprint inválido", failures)
    engagement = data.get("engagement", {})
    eng_people = engagement.get("people", [])
    if len(eng_people) != 21:
        fail(f"Bloque engagement incompleto ({len(eng_people)} personas, se esperaban 21)", failures)
    if not all("active" in p and "signal" in p for p in eng_people):
        fail("engagement.people sin 'active'/'signal'", failures)
    if engagement.get("active", 0) + engagement.get("inactive", 0) != len(eng_people):
        fail("engagement: activos + inactivos no suman el total", failures)
    # Una historia recortada no puede colarse al alcance ni quedar sin justificación:
    # el recorte es una decisión del PO y tiene que poder leerse en el tablero.
    for story in data.get("descoped", []):
        if story.get("status") != "descoped":
            fail(f"{story.get('id')} está en 'descoped' con estado {story.get('status')}", failures)
        if story.get("evidence") in {"", "—", None}:
            fail(f"{story.get('id')} recortada sin decisión registrada en la evidencia", failures)
    ids_alcance = {story.get("id") for story in stories}
    for story in data.get("descoped", []):
        if story.get("id") in ids_alcance:
            fail(f"{story.get('id')} aparece a la vez en alcance y en recortadas", failures)
    if data.get("summary", {}).get("descoped") != len(data.get("descoped", [])):
        fail("summary.descoped no coincide con el número de historias recortadas", failures)

    pending = data.get("pending", [])
    expected_pending = sum(story.get("status") != "done" for story in stories)
    if len(pending) != expected_pending:
        fail(f"Pendientes ({len(pending)}) no coinciden con US no-done ({expected_pending})", failures)
    prd = data.get("prd_compliance", [])
    if len(prd) != 7:
        fail(f"Se esperaban 7 criterios de PRD y hay {len(prd)}", failures)
    for crit in prd:
        if crit.get("exec_band") not in {"green", "amber", "red"}:
            fail(f"Criterio PRD {crit.get('req')} sin banda de ejecución", failures)
    for risk in data.get("risks", []):
        if "stories" not in risk or "mitigation_date" not in risk:
            fail(f"{risk.get('id')} sin US relacionada o fecha de mitigación", failures)
    if not all("weighted_remaining" in point for point in data.get("history", [])[-1:]):
        fail("El historial no trae weighted_remaining para el burndown", failures)
    html = html_path.read_text(encoding="utf-8")
    if "__PM_DASHBOARD_DATA__" in html:
        fail("El HTML conserva el marcador sin reemplazar", failures)
    for countdown_id in ["delivery-days", "delivery-label"]:
        if f'id="{countdown_id}"' not in html:
            fail(f"Falta elemento del contador: {countdown_id}", failures)
    for countdown_marker in ["updateDeliveryCountdown", "D.delivery.timezone", "setInterval"]:
        if countdown_marker not in html:
            fail(f"El contador no es dinámico: falta {countdown_marker}", failures)
    for tab in ["exec", "roadmaplight", "performance", "engagement", "prd", "summary", "flow", "cells", "team", "plans", "dependencies", "rubric", "sources", "risks", "governance", "explorer"]:
        if f'id="panel-{tab}"' not in html:
            fail(f"Falta panel {tab}", failures)
    if failures:
        print("❌ Tablero PM inválido:")
        for item in failures:
            print(f"   - {item}")
        return 1
    print("✅ TEST-002: snapshot y tablero PM válidos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
