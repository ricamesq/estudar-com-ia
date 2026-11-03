"""
RIS / BibTeX / MEDLINE file → VOSviewer JSON.

Supports the main RIS tags: TI, AB, AU, PY, DO, KW, UR, N1, N2.
For BibTeX, a minimal parser is used (title, author, year, abstract, keywords, doi).

Usage:
    python ris_to_vosviewer.py refs.ris --out out.json
    python ris_to_vosviewer.py refs.bib --analysis coauthorship
"""

from __future__ import annotations

import argparse
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 fix
except Exception:
    pass
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from vosviewer_common import (  # noqa: E402
    Document,
    build_coauthorship,
    build_cooccurrence,
    load_thesaurus,
    save_json,
    summarize,
)


def parse_ris(text: str) -> list[Document]:
    docs: list[Document] = []
    current: dict = {}
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        m = re.match(r"^([A-Z][A-Z0-9])  - (.*)$", line)
        if not m:
            continue
        tag, value = m.group(1), m.group(2).strip()
        if tag == "TY":
            if current:
                docs.append(_ris_to_doc(current))
            current = {"TY": value, "AU": [], "KW": []}
        elif tag in ("AU", "A1", "A2", "A3"):
            current.setdefault("AU", []).append(value)
        elif tag == "KW":
            current.setdefault("KW", []).append(value)
        elif tag == "ER":
            if current:
                docs.append(_ris_to_doc(current))
                current = {}
        else:
            current[tag] = (current.get(tag, "") + " " + value).strip()
    if current:
        docs.append(_ris_to_doc(current))
    return docs


def _ris_to_doc(r: dict) -> Document:
    year = None
    for k in ("PY", "Y1", "DA"):
        v = r.get(k, "")
        m = re.search(r"\d{4}", v or "")
        if m:
            year = int(m.group(0))
            break
    return Document(
        title=r.get("TI") or r.get("T1") or "",
        abstract=r.get("AB") or r.get("N2") or "",
        authors=r.get("AU", []),
        year=year,
        doi=r.get("DO", ""),
        url=r.get("UR", ""),
        keywords=r.get("KW", []),
    )


def parse_bibtex(text: str) -> list[Document]:
    docs: list[Document] = []
    # Split on @type{key, ... }
    for entry in re.finditer(
        r"@(\w+)\s*\{\s*([^,]+),(.*?)\n\s*\}\s*(?=@|\Z)",
        text,
        flags=re.DOTALL,
    ):
        body = entry.group(3)
        fields: dict[str, str] = {}
        for f in re.finditer(r"(\w+)\s*=\s*[\{\"]([^\{\}]*(?:\{[^\}]*\})*)[\}\"]", body):
            fields[f.group(1).lower()] = f.group(2).strip().replace("\n", " ")
        authors = [a.strip() for a in re.split(r"\s+and\s+", fields.get("author", "")) if a.strip()]
        keywords = [k.strip() for k in re.split(r"[;,]", fields.get("keywords", "")) if k.strip()]
        year = None
        if fields.get("year"):
            m = re.search(r"\d{4}", fields["year"])
            if m:
                year = int(m.group(0))
        docs.append(
            Document(
                title=fields.get("title", ""),
                abstract=fields.get("abstract", ""),
                authors=authors,
                year=year,
                doi=fields.get("doi", ""),
                url=fields.get("url", ""),
                keywords=keywords,
            )
        )
    return docs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", help="Path to .ris or .bib file")
    ap.add_argument("--out", default="vosviewer-out/ris.json")
    ap.add_argument(
        "--analysis",
        choices=["coauthorship", "cooccurrence"],
        default="cooccurrence",
    )
    ap.add_argument("--min-count", type=int, default=2)
    ap.add_argument("--min-link", type=int, default=1)
    ap.add_argument("--thesaurus", default="")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        sys.exit(f"Arquivo não encontrado: {p}")
    text = p.read_text(encoding="utf-8", errors="replace")
    ext = p.suffix.lower()
    if ext == ".ris" or text.lstrip().startswith("TY  -"):
        docs = parse_ris(text)
    elif ext == ".bib" or text.lstrip().startswith("@"):
        docs = parse_bibtex(text)
    else:
        sys.exit("Formato não reconhecido (esperado .ris ou .bib).")

    print(f"📥 {p.name}: {len(docs)} documentos")
    if not docs:
        sys.exit("Nenhum documento.")

    if args.analysis == "coauthorship":
        obj = build_coauthorship(
            docs,
            min_author_count=args.min_count,
            min_link_strength=args.min_link,
        )
    else:
        thesaurus = load_thesaurus(args.thesaurus) if args.thesaurus else None
        obj = build_cooccurrence(
            docs,
            min_term_count=args.min_count,
            min_link_strength=args.min_link,
            thesaurus=thesaurus,
        )
    out = save_json(obj, args.out)
    print(f"✅ {out}: {summarize(obj)}")


if __name__ == "__main__":
    main()
