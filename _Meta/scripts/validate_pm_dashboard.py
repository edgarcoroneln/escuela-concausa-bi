#!/usr/bin/env python3
"""Valida contrato, cobertura y vínculos del snapshot PM (TEST-002)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


VALID_STATES = {"planned", "in_progress", "in_review", "blocked", "done"}


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def main(root_value: str = ".") -> int:
    root = Path(root_value).resolve()
    data_path = root / "13_Reports/data/pm-dashboard.json"
    html_path = root / "13_Reports/TABLERO_CONTROL_PM.html"
    failures: list[str] = []
    if not data_path.exists() or not html_path.exists():
        print("❌ Ejecuta primero generate_pm_dashboard.py")
        return 1
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if data.get("meta", {}).get("schema_version") != "2.2":
        fail("Se esperaba schema 2.2 con contador de entrega", failures)
    if not re.fullmatch(r"[0-9a-f]{12}", data.get("meta", {}).get("source_fingerprint", "")):
        fail("Fingerprint de fuentes ausente o inválido", failures)
    delivery = data.get("delivery", {})
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", delivery.get("date", "")):
        fail("Fecha canónica de entrega ausente o inválida", failures)
    if delivery.get("source") != "12_Roadmap_Sprints/PLAN_MAESTRO.md":
        fail("La entrega no traza al Plan Maestro", failures)
    stories = data.get("stories", [])
    ids = [story.get("id") for story in stories]
    if len(ids) != 91:
        fail(f"Se esperaban 91 US y hay {len(ids)}", failures)
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
        fail("Las US del equipo no cubren exactamente las 87 historias", failures)
    if len(data.get("sources", [])) != 8:
        fail(f"Se esperaban 8 fuentes y hay {len(data.get('sources', []))}", failures)
    if round(sum(item.get("points", 0) for item in data.get("rubric", [])), 2) != 10.0:
        fail("Los puntos de rúbrica no suman 10", failures)
    html = html_path.read_text(encoding="utf-8")
    if "__PM_DASHBOARD_DATA__" in html:
        fail("El HTML conserva el marcador sin reemplazar", failures)
    for countdown_id in ["delivery-days", "delivery-label"]:
        if f'id="{countdown_id}"' not in html:
            fail(f"Falta elemento del contador: {countdown_id}", failures)
    for countdown_marker in ["updateDeliveryCountdown", "D.delivery.timezone", "setInterval"]:
        if countdown_marker not in html:
            fail(f"El contador no es dinámico: falta {countdown_marker}", failures)
    for tab in ["summary", "flow", "cells", "team", "plans", "dependencies", "rubric", "sources", "risks", "governance", "explorer"]:
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
