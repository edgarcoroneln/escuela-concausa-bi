#!/usr/bin/env python3
"""vault_lint.py — Higiene del vault.

Detecta:
  - Links [[wikilink]] rotos (destino inexistente)
  - Archivos .md sin frontmatter YAML
  - IDs duplicados en frontmatter
  - Documentos huérfanos (no referenciados por ningún _index.md ni ningún otro doc)

Uso:
  python _Meta/scripts/vault_lint.py [ruta_del_vault]   # default: .
Salida: código 0 si limpio, 1 si hay hallazgos.
"""
import os
import re
import sys

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|\\][^\]]*)?\]\]")
ID_RE = re.compile(r"^\s*id:\s*(.+?)\s*$", re.MULTILINE)
FENCED = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]*`")

# Archivos que legítimamente no llevan frontmatter (se copian a otro sitio o son raíz)
FM_EXEMPT = {"README.md", "PULL_REQUEST_TEMPLATE.md"}

# Directorios que NO son artefactos del vault: salida generada (graphify-out/) o ambientes y
# cachés locales (ya en .gitignore). Se excluyen del linter para no reportar, p. ej., cada
# LICENSE.md dentro de .venv/site-packages/ como problema del vault.
# .github/ contiene configuración de GitHub, no artefactos del vault.
EXCLUDED_DIRS = (
    "/.git", "/.obsidian", "/graphify-out", "/.github",
    "/.venv", "/venv", "/node_modules",
    "/.pytest_cache", "/.ruff_cache", "/__pycache__",
)


def _norm(path):
    """Normaliza separadores a / para comparaciones multiplataforma (Windows/Unix)."""
    return path.replace(os.sep, "/")


def find_md(root):
    for dirpath, _, files in os.walk(root):
        # _norm() garantiza que las comparaciones con EXCLUDED_DIRS funcionen en Windows
        if any(d in _norm(dirpath) for d in EXCLUDED_DIRS):
            continue
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)


def strip_code(text):
    """Quita bloques y spans de código para no leer links de ejemplo."""
    return INLINE_CODE.sub("", FENCED.sub("", text))


def stem(path):
    return os.path.splitext(os.path.basename(path))[0]


def main(root="."):
    md_files = list(find_md(root))
    stems = {}
    for p in md_files:
        stems.setdefault(stem(p), []).append(p)

    broken, no_fm, referenced = [], [], set()
    ids = {}

    for p in md_files:
        text = open(p, encoding="utf-8", errors="replace").read()
        if not text.lstrip().startswith("---") and os.path.basename(p) not in FM_EXEMPT:
            no_fm.append(p)
        # IDs: se ignoran las plantillas (_Templates/) porque son ejemplares con IDs placeholder
        if "/_Templates/" not in _norm(p):
            for m in ID_RE.finditer(text.split("---")[1] if "---" in text else ""):
                ids.setdefault(m.group(1), []).append(p)
        for m in WIKILINK.finditer(strip_code(text)):
            target = m.group(1).strip().rstrip("\\").split("/")[-1]
            referenced.add(target)
            if target not in stems:
                broken.append((p, m.group(1).strip()))

    orphans = [p for p in md_files
               if stem(p) not in referenced
               and os.path.basename(p) not in ("_index.md", "README.md", "PROJECT_INDEX.md")]
    dup_ids = {k: v for k, v in ids.items() if len(v) > 1}

    problems = 0
    if broken:
        problems += len(broken)
        print(f"\n❌ Links rotos ({len(broken)}):")
        for src, tgt in broken:
            print(f"   {src} → [[{tgt}]]")
    if no_fm:
        problems += len(no_fm)
        print(f"\n⚠️  Sin frontmatter ({len(no_fm)}):")
        for p in no_fm:
            print(f"   {p}")
    if dup_ids:
        problems += len(dup_ids)
        print(f"\n❌ IDs duplicados ({len(dup_ids)}):")
        for k, v in dup_ids.items():
            print(f"   {k}: {', '.join(v)}")
    if orphans:
        print(f"\nℹ️  Posibles huérfanos ({len(orphans)}) — no referenciados por wikilinks:")
        for p in orphans:
            print(f"   {p}")

    if problems == 0:
        print("✅ Vault limpio.")
        return 0
    print(f"\nTotal de problemas bloqueantes: {problems}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
