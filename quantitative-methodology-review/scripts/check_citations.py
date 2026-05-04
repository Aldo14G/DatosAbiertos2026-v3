#!/usr/bin/env python3
"""
check_citations.py
Scans all .tex files under a root directory, extracts every \\cite{},
\\parencite{}, and \\textcite{} key, then compares against the entries
declared in referencias.bib. Prints a JSON report of missing keys.

Usage:
    python check_citations.py <root_directory>

Example:
    python check_citations.py Documentacion/
"""

import re
import sys
import json
import pathlib


def load_bib_keys(bib_path: pathlib.Path) -> set[str]:
    """Extract all citation keys from a .bib file."""
    text = bib_path.read_text(encoding="utf-8")
    return {m.group(1) for m in re.finditer(r"@\w+\{([^,]+),", text)}


def find_cite_keys(tex_path: pathlib.Path) -> set[str]:
    """Extract all cited keys from a .tex file (cite, parencite, textcite)."""
    text = tex_path.read_text(encoding="utf-8")
    raw_keys: set[str] = set()
    for m in re.finditer(r"\\(?:par(?:en)?cite|textcite|cite)\{([^}]+)\}", text):
        for key in m.group(1).split(","):
            key = key.strip()
            if key:
                raw_keys.add(key)
    return raw_keys


def main(root: str) -> None:
    root_path = pathlib.Path(root)

    # Locate the bibliography file
    bib_candidates = list(root_path.rglob("referencias.bib"))
    if not bib_candidates:
        print("ERROR: referencias.bib not found under", root, file=sys.stderr)
        sys.exit(1)

    bib_keys = set()
    for bib in bib_candidates:
        bib_keys |= load_bib_keys(bib)

    # Scan all .tex files
    report: dict[str, list[str]] = {}
    all_cited: set[str] = set()
    for tex in sorted(root_path.rglob("*.tex")):
        cited = find_cite_keys(tex)
        all_cited |= cited
        missing = cited - bib_keys
        if missing:
            report[str(tex.relative_to(root_path))] = sorted(missing)

    # Summary
    summary = {
        "bib_entries": sorted(bib_keys),
        "total_cited": len(all_cited),
        "total_bib_entries": len(bib_keys),
        "missing_by_file": report,
        "unused_bib_entries": sorted(bib_keys - all_cited),
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if report:
        print(
            f"\nWARNING: {sum(len(v) for v in report.values())} missing citation(s) found.",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print("\nOK: All citations resolved.", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <root_directory>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
