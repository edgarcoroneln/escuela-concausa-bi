#!/usr/bin/env python3
"""vault_lint.py — Higiene del vault.

Detecta:
  - Links [[wikilink]] rotos (destino inexistente)
  - Archivos .md sin frontmatter YAML
  - IDs duplicados en frontmatter
  - Texto con la codificación rota (mojibake) por editores en locale no-UTF-8
  - Documentos huérfanos (no referenciados por ningún _index.md ni ningún otro doc)

Uso:
  python vault/_Meta/scripts/vault_lint.py [ruta_del_vault]   # default: .
Salida: código 0 si limpio, 1 si hay hallazgos.
"""
import os
import re
import sys

# Windows-safe: las consolas cp1252 lanzan UnicodeEncodeError al imprimir los
# emoji del reporte (❌ ⚠️ ℹ️ ✅). Forzar UTF-8 con reemplazo evita el crash de
# impresión sin cambiar el resultado del lint (reportado por Marina, 14-ago).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|\\][^\]]*)?\]\]")
ID_RE = re.compile(r"^\s*id:\s*(.+?)\s*$", re.MULTILINE)
FENCED = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]*`")

# Archivos que legítimamente no llevan frontmatter (se copian a otro sitio o son raíz)
FM_EXEMPT = {"README.md", "PULL_REQUEST_TEMPLATE.md"}

# Escotilla para documentar el defecto sin dispararlo. Los bloques de código ``` ya se
# omiten, así que esto solo hace falta en prosa que deba mostrar el texto roto en línea.
PERMITIR_MOJIBAKE = "vault-lint: permitir-mojibake"

# Directorios que NO son artefactos del vault: salida generada (graphify-out/) o ambientes y
# cachés locales (ya en .gitignore). Se excluyen del linter para no reportar, p. ej., cada
# LICENSE.md dentro de .venv/site-packages/ como problema del vault.
# .github/ contiene configuración de GitHub, no artefactos del vault.
# _local/ son notas de trabajo/handoff personales por sprint (ya en .gitignore), no del vault.
EXCLUDED_DIRS = (
    "/.git", "/.obsidian", "/graphify-out", "/.github",
    "/.venv", "/venv", "/node_modules",
    "/.pytest_cache", "/.ruff_cache", "/__pycache__",
    "/_local",
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


def es_mojibake(linea):
    """¿Esta línea es texto UTF-8 que un editor guardó como si fuera cp1252?

    Prueba de ida y vuelta: si la línea puede codificarse en cp1252 y ese resultado
    decodifica como UTF-8 válido **dando algo distinto**, entonces los bytes originales
    ya eran UTF-8 y se escribieron dos veces. Es lo que convierte `Descripción` en
    `DescripciÃ³n`.

    Un acento correcto no dispara la prueba: `é` sí codifica a cp1252 (0xE9), pero ese
    byte suelto no es UTF-8 válido, así que decodificar falla y la línea pasa. Tampoco
    disparan los emoji, las flechas ni las comillas angulares: no existen en cp1252 y la
    codificación falla antes.

    Origen: el PR #102 reescribió las 227 líneas de `vault/_DevLog/_index.md` así. Es la misma
    familia de BUG-005 (CRLF de Windows) y BUG-011 (`read_text()` sin `encoding`): el
    locale del sistema filtrándose a un archivo del vault.

    **Alcance conocido.** Cubre la familia de letras acentuadas, que es la que nos ha
    pegado. No cubre el mojibake de comillas tipográficas cuando arrastra bytes que cp1252
    deja sin definir (0x81, 0x8D, 0x8F, 0x90, 0x9D): ahí la codificación falla y la línea
    pasa. Ampliarlo exigiría una tabla de traducción propia; no se hizo porque ese caso no
    se ha presentado y el costo de un falso positivo en un check requerido es alto.
    """
    try:
        reparada = linea.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False
    return reparada != linea


def stem(path):
    return os.path.splitext(os.path.basename(path))[0]


def main(root="."):
    md_files = list(find_md(root))
    stems = {}
    for p in md_files:
        stems.setdefault(stem(p), []).append(p)

    broken, no_fm, referenced = [], [], set()
    mojibake = []
    conflictos = []
    ids = {}

    for p in md_files:
        text = open(p, encoding="utf-8", errors="replace").read()
        if not text.lstrip().startswith("---") and os.path.basename(p) not in FM_EXEMPT:
            no_fm.append(p)
        # Codificación rota: se omiten los bloques ``` para poder documentar el defecto.
        en_bloque = False
        for n, linea in enumerate(text.splitlines(), start=1):
            if linea.lstrip().startswith("```"):
                en_bloque = not en_bloque
                continue
            if en_bloque or PERMITIR_MOJIBAKE in linea:
                continue
            if es_mojibake(linea):
                mojibake.append((p, n, linea.strip()[:70]))
            # Marcadores de conflicto commiteados. Pasó el 2026-09-05: un `git add -A`
            # sobre un merge a medias metió `<<<<<<<` en la matriz y llegó a `main` sin
            # que nada lo detuviera -- ni el linter, ni las pruebas, ni el gate. El
            # `git status | grep UU` tampoco lo ve, porque el add ya los había marcado
            # como resueltos. Un marcador en `main` es corrupción visible del vault.
            if linea.startswith(("<<<<<<< ", ">>>>>>> ")) or linea.rstrip() == "=======":
                conflictos.append((p, n, linea.strip()[:70]))
        # IDs: se ignoran las plantillas (vault/_Templates/) porque son ejemplares con IDs placeholder
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
    if mojibake:
        problems += len(mojibake)
        archivos = sorted({p for p, _, _ in mojibake})
        print(f"\n❌ Codificación rota ({len(mojibake)} líneas en {len(archivos)} archivo(s)):")
        for p, n, muestra in mojibake[:10]:
            print(f"   {p}:{n} → {muestra}")
        if len(mojibake) > 10:
            print(f"   … y {len(mojibake) - 10} líneas más")
        print("   Tu editor guardó texto UTF-8 como si fuera cp1252 (Windows).")
        print("   Recupera el archivo con `git checkout origin/main -- <ruta>` y vuelve a")
        print("   editarlo con el editor en UTF-8. Ver vault/_Meta/Vault_Rules.md.")
    if conflictos:
        problems += len(conflictos)
        archivos = sorted({p for p, _, _ in conflictos})
        print(f"\n❌ Marcadores de conflicto sin resolver ({len(conflictos)} en {len(archivos)} archivo(s)):")
        for p, n, muestra in conflictos[:10]:
            print(f"   {p}:{n} → {muestra}")
        print("   Un merge quedó a medias y se commiteó. Resuelve el bloque a mano;")
        print("   `git status` no los ve si ya pasaron por `git add`.")
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
