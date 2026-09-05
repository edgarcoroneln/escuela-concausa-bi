#!/usr/bin/env python3
"""Genera el snapshot y el tablero PM de FARO desde fuentes canónicas.

Uso:
    python3 vault/_Meta/scripts/generate_pm_dashboard.py .

El HTML y JSON resultantes son artefactos generados. No deben editarse a mano.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


STATE_WEIGHT = {
    "planned": 0.0,
    "in_progress": 0.35,
    "in_review": 0.65,
    "blocked": 0.35,
    "done": 1.0,
    # `descoped` = recortada del alcance por decisión del PO. No se entregó, así que
    # NO puede pesar como `done`; pero tampoco es trabajo pendiente, así que sale del
    # denominador en vez de arrastrar el avance hacia abajo. Se reporta aparte, con su
    # decisión y su fecha, para que el recorte quede visible y no se lea como entrega.
    "descoped": 0.0,
}
VALID_STATES = set(STATE_WEIGHT)
SPRINT_DATES = {
    "S1": ("2026-08-03", "2026-08-09"),
    "S2": ("2026-08-10", "2026-08-16"),
    "S3": ("2026-08-17", "2026-08-23"),
    "S4": ("2026-08-24", "2026-08-30"),
    "S5": ("2026-08-31", "2026-09-06"),
    "S6": ("2026-09-07", "2026-09-08"),
}


def read(path: Path) -> str:
    """Lee UTF-8 tolerando caracteres inválidos aislados."""
    return path.read_text(encoding="utf-8", errors="replace")


def clean(value: str) -> str:
    """Normaliza una celda Markdown para uso en JSON."""
    value = value.strip().replace("**", "").replace("`", "")
    value = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", value)
    value = re.sub(r"\[\[([^\]]+)\]\]", r"\1", value)
    return value.strip()


# Centinela para proteger los pipes que NO son separadores de columna mientras se parte
# la fila. Es un carácter que no aparece en Markdown legible.
CENTINELA_PIPE = "\x00"


def table_cells(line: str) -> list[str]:
    """Parte una fila Markdown en celdas, respetando los pipes escapados.

    Un wikilink con alias —`[[ruta\\|texto]]`— lleva un `|` que **no** separa columnas:
    es sintaxis de Obsidian, y en Markdown se escribe escapado para que GitHub lo renderice
    dentro de la celda. Partir la línea cruda por todos los pipes corta ese enlace en dos,
    desplaza el resto de las columnas y corrompe el snapshot **en silencio**: el generador no
    revienta porque la fila sigue teniendo suficientes celdas, solo que ya no son las que
    parecen. Pasó con la fila `US-004` de Execution_Status (BUG-040), que publicó texto en
    el campo `updated` durante días.

    `clean()` ya sabe resolver `[[ruta|texto]]` a `texto`; lo que faltaba era no destruir el
    enlace antes de que pudiera hacerlo.
    """
    protegida = line.strip().strip("|").replace("\\|", CENTINELA_PIPE)
    return [clean(cell.replace(CENTINELA_PIPE, "|")) for cell in protegida.split("|")]


def git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def source_fingerprint(root: Path) -> str:
    """Hash estable de las fuentes que alimentan el snapshot."""
    paths = [
        root / "vault/02_Requirements/User_Stories.md",
        root / "vault/02_Requirements/Traceability_Matrix.md",
        root / "vault/10_Risk_Governance/Risk_Register.md",
        root / "vault/10_Risk_Governance/Blocker_Register.md",
        root / "vault/12_Roadmap_Sprints/PLAN_MAESTRO.md",
        root / "vault/12_Roadmap_Sprints/Execution_Status.md",
        root / "vault/12_Roadmap_Sprints/RACI.md",
        root / "vault/00_Start_Here/Developer_Onboarding.md",
        *sorted((root / "vault/14_Data_Sources").glob("DS-*.md")),
    ]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    block = text.split("---", 2)[1]
    values: dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(r"^([a-zA-Z_]+):\s*[\"']?(.*?)[\"']?\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip('"\'')
    return values


def parse_delivery(root: Path) -> dict[str, str]:
    """Lee la fecha de entrega machine-readable del Plan Maestro canónico."""
    plan_path = root / "vault/12_Roadmap_Sprints/PLAN_MAESTRO.md"
    frontmatter = parse_frontmatter(read(plan_path))
    delivery_date = frontmatter.get("delivery_date", "")
    try:
        date.fromisoformat(delivery_date)
    except ValueError as error:
        raise ValueError("delivery_date inválida o ausente en PLAN_MAESTRO.md") from error
    return {
        "date": delivery_date,
        "label": frontmatter.get("delivery_label", "Entrega final"),
        "timezone": frontmatter.get("delivery_timezone", "America/Mexico_City"),
        "source": "vault/12_Roadmap_Sprints/PLAN_MAESTRO.md",
    }


def short_name(owner: str) -> str:
    """Nombre corto para chips: primer nombre + inicial del primer apellido.

    Desambigua a homónimos de primer nombre (p. ej. los dos Edgar → "Edgar C."
    vs "Edgar J."). Convención de nombres MX: `Nombre(s) Apellido1 Apellido2`,
    así que el primer apellido es el penúltimo token cuando hay 3+ tokens.
    """
    parts = owner.split()
    if not parts:
        return owner
    first = parts[0]
    if len(parts) == 1:
        return first
    surname = parts[-2] if len(parts) >= 3 else parts[-1]
    return f"{first} {surname[0]}."


def parse_stories(root: Path) -> list[dict[str, Any]]:
    text = read(root / "vault/02_Requirements/User_Stories.md")
    stories: list[dict[str, Any]] = []
    cell = "Sin célula"
    for line in text.splitlines():
        heading = re.match(r"^## Célula (\d+) · (.+)$", line)
        if heading:
            cell = f"Célula {heading.group(1)} · {heading.group(2)}"
            continue
        cells = table_cells(line) if line.startswith("|") else []
        if len(cells) >= 6 and re.fullmatch(r"US-\d{3}[a-z]?", cells[0]):
            stories.append(
                {
                    "id": cells[0],
                    "title": cells[1],
                    "owner": cells[2],
                    "owner_short": short_name(cells[2]),
                    "level": cells[3],
                    "sprint": cells[4],
                    "req": re.match(r"REQ-\d{3}", cells[5]).group(0),
                    "cell": cell,
                }
            )
    if len(stories) != 91:
        raise ValueError(f"Se esperaban 91 historias y se encontraron {len(stories)}")
    return stories


def parse_execution(root: Path) -> dict[str, dict[str, str]]:
    text = read(root / "vault/12_Roadmap_Sprints/Execution_Status.md")
    result: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        cells = table_cells(line) if line.startswith("|") else []
        if len(cells) >= 6 and re.fullmatch(r"US-\d{3}[a-z]?", cells[0]):
            if cells[1] not in VALID_STATES:
                raise ValueError(f"Estado inválido para {cells[0]}: {cells[1]}")
            result[cells[0]] = {
                "status": cells[1],
                "started": cells[2],
                "blocked_since": cells[3],
                "evidence": cells[4],
                "updated": cells[5],
            }
    return result


def parse_people(root: Path) -> dict[str, dict[str, str]]:
    text = read(root / "vault/12_Roadmap_Sprints/PLAN_MAESTRO.md")
    people: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        cells = table_cells(line) if line.startswith("|") else []
        if len(cells) == 5 and cells[1] in {"Alto", "Medio", "Bajo"}:
            people[cells[0]] = {
                "name": cells[0],
                "level": cells[1],
                "cell": cells[2],
                "role": cells[3],
            }
    return people


def parse_github_directory(root: Path) -> dict[str, dict[str, str]]:
    """Extrae la identidad GitHub del directorio canónico de onboarding."""
    text = read(root / "vault/00_Start_Here/Developer_Onboarding.md")
    directory: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        cells = table_cells(line) if line.startswith("|") else []
        if (
            len(cells) == 5
            and cells[1] in {"Alto", "Medio", "Bajo"}
            and (cells[2] == "PO" or cells[2].startswith("Célula "))
        ):
            directory[cells[0]] = {
                "github_user": "" if cells[3] == "—" else cells[3],
                "github_status": cells[4],
            }
    if len(directory) != 21:
        raise ValueError(
            f"Se esperaban 21 identidades GitHub y se encontraron {len(directory)}"
        )
    return directory


def load_github_activity(root: Path) -> dict[str, Any]:
    """Carga el snapshot efímero de GitHub; en local conserva el último bloque conocido."""
    activity: dict[str, Any] = {
        "available": False,
        "prs": [],
        "ci": "local",
    }
    github_path = root / "vault/13_Reports/data/github-activity.json"
    if github_path.exists():
        try:
            loaded = json.loads(read(github_path))
            if isinstance(loaded, dict):
                activity = loaded
        except json.JSONDecodeError:
            pass
    # Fallback: si la recolección no está disponible (regenerado en local sin token),
    # conserva el último `git_activity` publicado en `pm-dashboard.json` en vez de
    # borrarlo — así un PR local no vacía la pestaña Engagement. Fase B lo repuebla
    # con datos frescos al mergear (refresh-dashboard.yml corre con el PAT).
    if not activity.get("available"):
        prev_path = root / "vault/13_Reports/data/pm-dashboard.json"
        if prev_path.exists():
            try:
                prev = json.loads(read(prev_path))
                prev_ga = prev.get("git_activity") if isinstance(prev, dict) else None
                if isinstance(prev_ga, dict) and prev_ga.get("available") and prev_ga.get("prs"):
                    activity = prev_ga
            except json.JSONDecodeError:
                pass
    return activity


def parse_individual_plans(root: Path) -> dict[str, dict[str, Any]]:
    """Extrae misión, dependencias y objetivos desde los 21 planes individuales."""
    plans: dict[str, dict[str, Any]] = {}
    sprint_dir = root / "vault/12_Roadmap_Sprints/Sprints"
    for path in sorted(sprint_dir.glob("[0-5]-*.md")):
        text = read(path)
        fm = parse_frontmatter(text)
        owner = fm.get("owner", "")
        if not owner:
            continue
        mission_match = re.search(
            r"## 1\. Tu misión en una frase\s+(.+?)(?=\n---|\n## 2\.)",
            text,
            re.DOTALL,
        )
        dependencies: dict[str, str] = {}
        for label, key in [
            ("Recibes de (inputs)", "inputs"),
            ("Entregas a (outputs)", "outputs"),
            ("Quién revisa tu código", "reviewer"),
            ("Formato de entrega", "delivery"),
        ]:
            match = re.search(
                rf"\| \*\*{re.escape(label)}\*\* \| (.+?) \|",
                text,
            )
            dependencies[key] = clean(match.group(1)) if match else "No documentado"
        story_details: dict[str, dict[str, str]] = {}
        headings = list(
            re.finditer(r"^### `(?P<id>US-\d{3}[a-z]?)` · (?P<title>.+)$", text, re.MULTILINE)
        )
        for index, heading in enumerate(headings):
            end = headings[index + 1].start() if index + 1 < len(headings) else text.find("\n---", heading.end())
            if end == -1:
                end = len(text)
            block = text[heading.end():end]
            fields: dict[str, str] = {}
            for label, key in [
                ("Objetivo", "objective"),
                ("Entregable", "deliverable"),
                ("Cómo se entrega", "delivery"),
            ]:
                match = re.search(rf"\| \*\*{re.escape(label)}\*\* \| (.+?) \|", block)
                fields[key] = clean(match.group(1)) if match else "No documentado"
            story_details[heading.group("id")] = fields
        plans[owner] = {
            "mission": clean(re.sub(r"\s+", " ", mission_match.group(1))) if mission_match else "No documentada",
            "inputs": dependencies["inputs"],
            "outputs": dependencies["outputs"],
            "reviewer": dependencies["reviewer"],
            "delivery": dependencies["delivery"],
            "path": str(path.relative_to(root)),
            "stories": story_details,
        }
    if len(plans) != 21:
        raise ValueError(f"Se esperaban 21 planes individuales y se encontraron {len(plans)}")
    return plans


def parse_markdown_rows(path: Path, id_pattern: str, minimum: int) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in read(path).splitlines():
        cells = table_cells(line) if line.startswith("|") else []
        if len(cells) >= minimum and re.fullmatch(id_pattern, cells[0]):
            rows.append(cells)
    return rows


def parse_risks(root: Path) -> list[dict[str, Any]]:
    rows = parse_markdown_rows(
        root / "vault/10_Risk_Governance/Risk_Register.md", r"RISK-\d{3}", 9
    )
    risks: list[dict[str, Any]] = []
    for row in rows:
        story_ids = sorted(set(re.findall(r"US-\d{3}[a-z]?", row[9]))) if len(row) > 9 else []
        risks.append(
            {
                "id": row[0],
                "description": row[1],
                "probability": int(row[2]),
                "impact": int(row[3]),
                "score": int(row[2]) * int(row[3]),
                "response": row[4],
                "mitigation": row[5],
                "trigger": row[6],
                "owner": row[7],
                "status": row[8],
                "stories": story_ids,
                "mitigation_date": clean(row[10]) if len(row) > 10 else "—",
            }
        )
    return risks


def parse_blockers(root: Path) -> list[dict[str, str]]:
    rows = parse_markdown_rows(
        root / "vault/10_Risk_Governance/Blocker_Register.md", r"BLOCK-\d{3}", 9
    )
    keys = [
        "id", "story", "provider", "consumer", "description",
        "since", "alternative", "owner", "status",
    ]
    return [dict(zip(keys, row[:9])) for row in rows]


def parse_raci(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in read(root / "vault/12_Roadmap_Sprints/RACI.md").splitlines():
        cells = table_cells(line) if line.startswith("|") else []
        if len(cells) == 6 and cells[0] not in {"Entregable", "---"}:
            rows.append(
                dict(zip(["deliverable", "r", "a", "c", "i", "gate"], cells))
            )
    return rows


def extract_bold(text: str, label: str) -> str:
    match = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+?)(?:\n|$)", text)
    return clean(match.group(1)) if match else "No documentado"


def parse_sources(root: Path) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for path in sorted((root / "vault/14_Data_Sources").glob("DS-*.md")):
        text = read(path)
        fm = parse_frontmatter(text)
        source_id = fm.get("id", path.stem.split("_")[0])
        checked = len(re.findall(r"^- \[x\]", text, re.MULTILINE | re.IGNORECASE))
        total = len(re.findall(r"^- \[[ x]\]", text, re.MULTILINE | re.IGNORECASE))
        proof = "ok" if total and checked == total else "partial" if checked else "pending"
        frequency = extract_bold(text, "Geográfica")
        freq_match = re.search(
            r"## 3\. Frecuencia real de actualización\s+(.+?)(?=\n## )",
            text,
            re.DOTALL,
        )
        if freq_match:
            frequency = clean(re.sub(r"\s+", " ", freq_match.group(1)))
        sources.append(
            {
                "id": source_id,
                "name": fm.get("title", path.stem),
                "owner": fm.get("owner", "Sin dueño"),
                "document_status": fm.get("status", "unknown"),
                "frequency": frequency,
                "coverage": extract_bold(text, "Geográfica"),
                "proof": proof,
                "checks_done": checked,
                "checks_total": total,
                "path": str(path.relative_to(root)),
            }
        )
    return sources


def parse_rubric(stories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    points = {
        "REQ-001": ("Data Engineering", 2.5),
        "REQ-002": ("Analytics & BI", 2.5),
        "REQ-003": ("Modelos ML", 1.5),
        "REQ-004": ("Backend/API/Auth", 1.5),
        "REQ-005": ("Deploy GCP", 1.0),
        "REQ-006": ("Agente", 0.5),
        "REQ-007": ("Equipo/Git/Docs", 0.5),
    }
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for story in stories:
        grouped[story["req"]].append(story)
    result = []
    for req, (name, value) in points.items():
        items = grouped[req]
        progress = sum(STATE_WEIGHT[item["status"]] for item in items) / len(items)
        pct = round(progress * 100, 1)
        done_count = sum(item["status"] == "done" for item in items)
        band = "green" if pct >= 40 else "amber" if pct >= 8 else "red"
        # REQ-005: la URL pública viva es el hito crítico; si ya hay entrega, va en verde.
        if req == "REQ-005" and done_count:
            band = "green"
        result.append(
            {
                "req": req,
                "name": name,
                "points": value,
                "stories": len(items),
                "done": sum(item["status"] == "done" for item in items),
                "progress": pct,
                "secured_points": round(value * progress, 2),
                "band": band,
            }
        )
    return result


def build_history(root: Path, summary: dict[str, Any]) -> list[dict[str, Any]]:
    path = root / "vault/13_Reports/data/pm-dashboard-history.json"
    history: list[dict[str, Any]] = []
    if path.exists():
        try:
            history = json.loads(read(path))
        except json.JSONDecodeError:
            history = []
    today = date.today().isoformat()
    point = {
        "date": today,
        "remaining": summary["total"] - summary["done"],
        "weighted_remaining": round(summary["total"] * (1 - summary["progress"] / 100), 1),
        "done": summary["done"],
        "scope": summary["total"],
        "wip": summary["wip"],
        "blocked": summary["blocked"],
    }
    history = [item for item in history if item.get("date") != today]
    history.append(point)
    return sorted(history, key=lambda item: item["date"])


SPRINT_ORDER = {sid: idx for idx, sid in enumerate(SPRINT_DATES, start=1)}


def current_sprint(today: date) -> str:
    for sid, (start, end) in SPRINT_DATES.items():
        if date.fromisoformat(start) <= today <= date.fromisoformat(end):
            return sid
    if today < date.fromisoformat(next(iter(SPRINT_DATES.values()))[0]):
        return next(iter(SPRINT_DATES))
    return list(SPRINT_DATES)[-1]


def build_performance(
    stories: list[dict[str, Any]],
    people: list[dict[str, Any]],
    git_activity: dict[str, Any],
    cur_sprint: str,
) -> dict[str, Any]:
    """Performance y engagement por integrante × sprint (US + estatus + commits/PRs)."""
    prs_by: dict[str, dict[str, int]] = defaultdict(lambda: {"open": 0, "merged": 0})
    for pr in git_activity.get("prs", []):
        author = str(pr.get("author", "")).casefold()
        state = pr.get("state")
        if state in ("open", "merged"):
            prs_by[author][state] += 1
    commits_by = {
        str(c.get("author", "")).casefold(): int(c.get("count", 0))
        for c in git_activity.get("commits", [])
    }
    by_owner: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for story in stories:
        by_owner[story["owner"]].append(story)
    sprint_ids = list(SPRINT_DATES)
    cur_order = SPRINT_ORDER[cur_sprint]
    rows: list[dict[str, Any]] = []
    for person in people:
        owner = person["name"]
        gh = (person.get("github_user") or "").casefold()
        items = by_owner.get(owner, [])
        by_sprint: dict[str, dict[str, Any]] = {}
        overdue = False
        for sid in sprint_ids:
            sit = [s for s in items if str(s.get("sprint")) == sid]
            if not sit:
                by_sprint[sid] = {"n": 0, "done": 0, "state": "idle"}
                continue
            done = sum(s["status"] == "done" for s in sit)
            wip = sum(s["status"] in {"in_progress", "in_review"} for s in sit)
            planned = sum(s["status"] == "planned" for s in sit)
            if done == len(sit):
                state = "done"
            elif wip:
                state = "wip"
            elif planned and SPRINT_ORDER[sid] <= cur_order:
                state = "risk"
                overdue = True
            elif done:
                state = "partial"
            else:
                state = "planned"
            by_sprint[sid] = {"n": len(sit), "done": done, "state": state}
        risk = "retraso" if overdue else ("sin_turno" if person["progress"] == 0 else "en_tiempo")
        rows.append(
            {
                "name": owner,
                "cell": person.get("cell", ""),
                "engagement": person["progress"],
                "commits": commits_by.get(gh, 0) if gh else 0,
                "prs_merged": prs_by.get(gh, {}).get("merged", 0) if gh else 0,
                "prs_open": prs_by.get(gh, {}).get("open", 0) if gh else 0,
                "risk": risk,
                "by_sprint": by_sprint,
            }
        )
    rows.sort(key=lambda r: -r["engagement"])
    return {"sprints": sprint_ids, "current_sprint": cur_sprint, "people": rows}


def parse_devlog_authors(root: Path) -> dict[str, int]:
    """Cuenta entradas del índice de DevLog por autor canónico (evidencia de trabajo documentado)."""
    text = read(root / "vault/_DevLog/_index.md")
    counts: dict[str, int] = defaultdict(int)
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        cells = table_cells(line)
        if len(cells) < 5:
            continue
        author = cells[2]
        if not author or author == "Autor" or set(author) <= set("-: "):
            continue
        counts[author] += 1
    return dict(counts)


def build_engagement(
    people: list[dict[str, Any]],
    stories: list[dict[str, Any]],
    devlog_counts: dict[str, int],
    git_activity: dict[str, Any],
) -> dict[str, Any]:
    """Quién ha contribuido con evidencia real vs quién no tiene actividad registrada.

    Señal offline-safe: DevLogs firmados + US propias en estado activo (≠ planned) + PRs mergeados
    cuando el colector de GitHub trae datos. Un integrante está `activo` si tiene al menos una señal.
    """
    prs_by: dict[str, int] = defaultdict(int)
    for pr in git_activity.get("prs", []):
        if pr.get("state") == "merged":
            prs_by[str(pr.get("author", "")).casefold()] += 1
    by_owner: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for story in stories:
        by_owner[story["owner"]].append(story)
    rows: list[dict[str, Any]] = []
    for person in people:
        name = person["name"]
        gh = (person.get("github_user") or "").casefold()
        devlogs = devlog_counts.get(name, 0)
        prs_merged = max(prs_by.get(gh, 0) if gh else 0, int(person.get("pr_merged") or 0))
        active_us = sum(s["status"] != "planned" for s in by_owner.get(name, []))
        signals = []
        if prs_merged:
            signals.append(f"{prs_merged} PR")
        if devlogs:
            signals.append(f"{devlogs} DevLog")
        if active_us:
            signals.append(f"{active_us} US activas")
        rows.append(
            {
                "name": name,
                "cell": person.get("cell", ""),
                "cell_group": person.get("cell_group", ""),
                "active": bool(prs_merged or devlogs or active_us),
                "prs_merged": prs_merged,
                "devlogs": devlogs,
                "active_us": active_us,
                "activity": prs_merged + devlogs + active_us,
                "signal": " · ".join(signals) if signals else "sin actividad registrada",
            }
        )
    # Activos primero, ordenados por actividad de mayor a menor; los sin actividad, por nombre.
    rows.sort(key=lambda r: (not r["active"], -r["activity"], r["name"]))
    active_n = sum(r["active"] for r in rows)
    return {"people": rows, "active": active_n, "inactive": len(rows) - active_n, "total": len(rows)}


def build_pending(stories: list[dict[str, Any]], cur_sprint: str) -> list[dict[str, Any]]:
    """US no terminadas, con responsable, célula, sprint y bandera de turno."""
    cur_order = SPRINT_ORDER.get(cur_sprint, 1)
    out: list[dict[str, Any]] = []
    for story in stories:
        if story["status"] == "done":
            continue
        sid = str(story.get("sprint"))
        su_turno = story["status"] == "planned" and SPRINT_ORDER.get(sid, 99) <= cur_order
        out.append(
            {
                "id": story["id"],
                "objective": story.get("objective", story.get("title", "")),
                "owner": story["owner"],
                "cell": story.get("cell", ""),
                "sprint": sid,
                "status": story["status"],
                "su_turno": su_turno,
            }
        )
    out.sort(key=lambda r: (SPRINT_ORDER.get(r["sprint"], 99), not r["su_turno"], r["id"]))
    return out


PRD_CRITERIA = [
    ("1 · Data Engineering multi-fuente", 2.5, "REQ-001", "PRD §7 · §10"),
    ("2 · Frontend BI interactivo", 2.5, "REQ-002", "PRD §12 · §12.1"),
    ("3 · Tres modelos ML vía API", 1.5, "REQ-003", "PRD §11"),
    ("4 · Backend + Auth OAuth2/RBAC", 1.5, "REQ-004", "PRD §13-8"),
    ("5 · Deploy GCP + Docker + URL", 1.0, "REQ-005", "PRD §10 · §13-9"),
    ("6 · Agente conversacional", 0.5, "REQ-006", "PRD §12.1"),
    ("7 · Equipo, Git & Docs", 0.5, "REQ-007", "Vault + README"),
]


def build_prd_compliance(rubric: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Cruza los 7 criterios del profesor (PRD-GENERAL) con la cobertura del proyecto."""
    by_req = {item["req"]: item for item in rubric}
    out: list[dict[str, Any]] = []
    for label, points, req, ref in PRD_CRITERIA:
        prog = by_req.get(req, {}).get("progress", 0.0)
        done = by_req.get(req, {}).get("done", 0)
        if prog >= 40 or (req == "REQ-005" and done):
            exec_band, exec_label = "green", "En ejecución"
        elif prog > 0:
            exec_band, exec_label = "amber", "Iniciado"
        else:
            exec_band, exec_label = "red", "Sin iniciar"
        if req == "REQ-005" and done:
            exec_label = "URL pública viva"
        out.append(
            {
                "criterion": label,
                "points": points,
                "req": req,
                "reference": ref,
                "design": "Cubierto",
                "exec_band": exec_band,
                "exec_label": exec_label,
                "progress": prog,
            }
        )
    return out


def build_snapshot(root: Path) -> dict[str, Any]:
    stories = parse_stories(root)
    execution = parse_execution(root)
    people_meta = parse_people(root)
    github_directory = parse_github_directory(root)
    individual_plans = parse_individual_plans(root)
    git_activity = load_github_activity(root)
    delivery = parse_delivery(root)
    delivery_date = date.fromisoformat(delivery["date"])
    today = date.today()
    # BUG-042: antes, una US sin fila en Execution_Status.md caía en silencio a
    # "planned" -- que puede o no ser cierto, nadie lo verificaba. Pasó con 24
    # historias reales (algunas ya tenían PR mergeado) contadas como "planned"
    # sin que nada fallara. Un valor por defecto que parece dato es peor que un
    # error: ahora toda US-### debe tener su fila explícita, o el generador
    # truena con la lista completa de las que faltan.
    faltantes = sorted(s["id"] for s in stories if s["id"] not in execution)
    if faltantes:
        raise ValueError(
            f"{len(faltantes)} historia(s) sin fila en Execution_Status.md (BUG-042): "
            f"{', '.join(faltantes)}. Agrega su fila -- con el estado real, no un default."
        )
    for story in stories:
        state = execution[story["id"]]
        story.update(
            {
                "status": state["status"],
                "started": state["started"],
                "blocked_since": state["blocked_since"],
                "evidence": state["evidence"],
                "updated": state["updated"],
            }
        )
        plan_story = individual_plans.get(story["owner"], {}).get("stories", {}).get(story["id"], {})
        story["objective"] = plan_story.get("objective", story["title"])
        story["deliverable"] = plan_story.get("deliverable", "No documentado")
        start_value = story["blocked_since"] if story["status"] == "blocked" else story["started"]
        try:
            story["age_days"] = max(0, (today - date.fromisoformat(start_value)).days)
        except ValueError:
            story["age_days"] = 0

    # Las historias recortadas salen del alcance ANTES de cualquier conteo, para que
    # ni el avance, ni las células, ni la rúbrica, ni el readiness las cuenten como
    # trabajo por hacer. Viajan aparte en `descoped`.
    descoped = [story for story in stories if story["status"] == "descoped"]
    stories = [story for story in stories if story["status"] != "descoped"]
    if not stories:
        raise ValueError("Todas las historias quedaron fuera de alcance; revisa Execution_Status.md.")

    counts = Counter(story["status"] for story in stories)
    progress = sum(STATE_WEIGHT[story["status"]] for story in stories) / len(stories)
    summary = {
        "total": len(stories),
        "done": counts["done"],
        "planned": counts["planned"],
        "in_progress": counts["in_progress"],
        "in_review": counts["in_review"],
        "blocked": counts["blocked"],
        "wip": counts["in_progress"] + counts["in_review"] + counts["blocked"],
        "descoped": len(descoped),
        "progress": round(progress * 100, 1),
        "days_to_demo": max(0, (delivery_date - today).days),
    }

    people: list[dict[str, Any]] = []
    owners: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for story in stories:
        owners[story["owner"]].append(story)
    for owner, items in sorted(owners.items()):
        meta = people_meta.get(owner, {})
        plan = individual_plans.get(owner, {})
        identity = github_directory.get(owner, {})
        github_user = identity.get("github_user", "")
        authored_prs = [
            pr
            for pr in git_activity.get("prs", [])
            if github_user
            and str(pr.get("author", "")).casefold() == github_user.casefold()
        ]
        people.append(
            {
                "name": owner,
                "level": meta.get("level", items[0]["level"]),
                "cell": meta.get("cell", items[0]["cell"].split(" · ")[0]),
                "cell_group": items[0]["cell"],
                "role": meta.get("role", "Integrante"),
                "mission": plan.get("mission", "No documentada"),
                "inputs": plan.get("inputs", "No documentado"),
                "outputs": plan.get("outputs", "No documentado"),
                "reviewer": plan.get("reviewer", "No documentado"),
                "delivery": plan.get("delivery", "No documentado"),
                "plan_path": plan.get("path", ""),
                "github_user": github_user,
                "github_status": identity.get("github_status", "Pendiente de confirmar"),
                "github_profile": f"https://github.com/{github_user}" if github_user else "",
                "assigned_story_ids": sorted(item["id"] for item in items),
                "pr_count": len(authored_prs) if git_activity.get("available") and github_user else None,
                "pr_open": sum(pr.get("state") == "open" for pr in authored_prs),
                "pr_merged": sum(pr.get("state") == "merged" for pr in authored_prs),
                "stories": len(items),
                "done": sum(item["status"] == "done" for item in items),
                "wip": sum(item["status"] in {"in_progress", "in_review", "blocked"} for item in items),
                "blocked": sum(item["status"] == "blocked" for item in items),
                "progress": round(
                    sum(STATE_WEIGHT[item["status"]] for item in items) / len(items) * 100,
                    1,
                ),
            }
        )

    cells: list[dict[str, Any]] = []
    cell_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for story in stories:
        cell_groups[story["cell"]].append(story)
    for cell, items in cell_groups.items():
        member_names = sorted({item["owner"] for item in items})
        cells.append(
            {
                "name": cell,
                "members": member_names,
                "stories": len(items),
                "done": sum(item["status"] == "done" for item in items),
                "wip": sum(item["status"] in {"in_progress", "in_review", "blocked"} for item in items),
                "blocked": sum(item["status"] == "blocked" for item in items),
                "progress": round(
                    sum(STATE_WEIGHT[item["status"]] for item in items) / len(items) * 100,
                    1,
                ),
            }
        )

    rubric = parse_rubric(stories)
    sources = parse_sources(root)
    blockers = parse_blockers(root)
    risks = parse_risks(root)
    cur_sprint = current_sprint(today)
    performance = build_performance(stories, people, git_activity, cur_sprint)
    engagement = build_engagement(people, stories, parse_devlog_authors(root), git_activity)
    pending = build_pending(stories, cur_sprint)
    prd_compliance = build_prd_compliance(rubric)
    source_ready = sum(source["proof"] == "ok" for source in sources)
    done_ids = {story["id"] for story in stories if story["status"] == "done"}
    req_done = lambda req, n=1: sum(s["status"] == "done" and s["req"] == req for s in stories) >= n
    any_done = lambda *ids: any(i in done_ids for i in ids)
    # Los gates se derivan del estado real de las US; se encienden solas al cerrar su evidencia.
    critical_gates = [
        {"name": "URL pública y healthcheck", "ready": "US-501" in done_ids, "weight": 15, "evidence": "US-501"},
        {"name": "≥5 fuentes y una continua", "ready": source_ready >= 5, "weight": 15, "evidence": "DS-01…08"},
        {"name": "Bronze/Silver/Gold + calidad", "ready": any_done("US-103", "US-104"), "weight": 15, "evidence": "REQ-001"},
        {"name": "Tres modelos registrados", "ready": req_done("REQ-003", 3) and any_done("US-312", "US-313"), "weight": 15, "evidence": "REQ-003"},
        {"name": "API, OAuth2 y RBAC", "ready": "US-401" in done_ids and any_done("US-402", "US-403"), "weight": 10, "evidence": "REQ-004"},
        {"name": "Diez dashboards funcionales", "ready": any_done("US-203", "US-204"), "weight": 10, "evidence": "REQ-002"},
        {"name": "Agente evaluado", "ready": any_done("US-323", "US-304a", "US-304b"), "weight": 10, "evidence": "REQ-006"},
        {"name": "Dry-run y contingencia", "ready": "US-006" in done_ids, "weight": 10, "evidence": "US-006"},
    ]
    readiness = sum(gate["weight"] for gate in critical_gates if gate["ready"])
    confidence = max(0, readiness - 5 * len([b for b in blockers if b["status"] != "resolved"]))

    commit = git(root, "rev-parse", "--short", "HEAD")
    branch = git(root, "branch", "--show-current")
    working_tree = (
        "clean"
        if not git(root, "status", "--porcelain", "--untracked-files=no")
        else "modified"
    )
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    snapshot = {
        "meta": {
            "generated_at": generated_at,
            "generated_date": today.isoformat(),
            "commit": commit,
            "branch": branch,
            "working_tree": working_tree,
            "source_fingerprint": source_fingerprint(root),
            "source": "Fuentes canónicas del vault",
            "offline": True,
            "schema_version": "2.4",
        },
        "summary": summary,
        "delivery": delivery,
        "stories": stories,
        "descoped": descoped,
        "people": people,
        "cells": cells,
        "rubric": rubric,
        "sources": sources,
        "risks": risks,
        "blockers": blockers,
        "performance": performance,
        "engagement": engagement,
        "pending": pending,
        "prd_compliance": prd_compliance,
        "current_sprint": cur_sprint,
        "raci": parse_raci(root),
        "readiness": {"score": readiness, "confidence": confidence, "gates": critical_gates},
        "sprints": [
            {"id": sprint, "start": dates[0], "end": dates[1]}
            for sprint, dates in SPRINT_DATES.items()
        ],
        "git_activity": git_activity,
    }
    snapshot["history"] = build_history(root, summary)
    return snapshot


def write_outputs(root: Path, snapshot: dict[str, Any]) -> None:
    data_dir = root / "vault/13_Reports/data"
    data_dir.mkdir(parents=True, exist_ok=True)
    data_path = data_dir / "pm-dashboard.json"
    history_path = data_dir / "pm-dashboard-history.json"
    template_path = root / "vault/13_Reports/TABLERO_CONTROL_PM.template.html"
    output_path = root / "vault/13_Reports/TABLERO_CONTROL_PM.html"
    encoded = json.dumps(snapshot, ensure_ascii=False, indent=2)
    data_path.write_text(encoded + "\n", encoding="utf-8")
    history_path.write_text(
        json.dumps(snapshot["history"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    template = read(template_path)
    marker = "__PM_DASHBOARD_DATA__"
    if marker not in template:
        raise ValueError(f"La plantilla no contiene {marker}")
    output_path.write_text(template.replace(marker, encoded), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    snapshot = build_snapshot(root)
    write_outputs(root, snapshot)
    print(
        "✅ Tablero PM generado: "
        f"{snapshot['summary']['total']} US, "
        f"{len(snapshot['people'])} personas, "
        f"{len(snapshot['sources'])} fuentes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
