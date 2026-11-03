"""
OpenAlex query → VOSviewer JSON (concepts co-occurrence by default).

Uses the public OpenAlex API (no key required).

Usage:
    python openalex_to_vosviewer.py "digital literacy higher education" --max 500
    python openalex_to_vosviewer.py "telemedicine brazil" --analysis coauthorship
"""

from __future__ import annotations

import argparse
import json
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 fix
except Exception:
    pass
import time
import urllib.parse
import urllib.request
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

HEADERS = {"User-Agent": "vosviewer-skill/1.0 (research)"}


def fetch_openalex(query: str, max_results: int = 500) -> list[Document]:
    docs: list[Document] = []
    per_page = 200
    cursor = "*"
    while len(docs) < max_results:
        url = (
            "https://api.openalex.org/works?"
            f"search={urllib.parse.quote(query)}"
            f"&per_page={per_page}&cursor={cursor}"
            "&select=title,authorships,abstract_inverted_index,publication_year,doi,id,concepts"
        )
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        results = data.get("results", [])
        if not results:
            break
        for it in results:
            title = it.get("title") or ""
            abstract = _invert_abstract(it.get("abstract_inverted_index") or {})
            authors = [
                (a.get("author") or {}).get("display_name") or ""
                for a in it.get("authorships") or []
            ]
            authors = [a for a in authors if a]
            year = it.get("publication_year")
            doi = (it.get("doi") or "").replace("https://doi.org/", "")
            concepts = [
                (c.get("display_name") or "").strip()
                for c in it.get("concepts") or []
                if (c.get("level") or 0) >= 1  # skip top-level mega-domains
            ]
            docs.append(
                Document(
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    year=year,
                    doi=doi,
                    url=it.get("id") or "",
                    keywords=concepts,
                )
            )
            if len(docs) >= max_results:
                break
        cursor = (data.get("meta") or {}).get("next_cursor")
        if not cursor:
            break
        time.sleep(0.2)
    return docs


def _invert_abstract(inv: dict) -> str:
    if not inv:
        return ""
    positions: list[tuple[int, str]] = []
    for word, poses in inv.items():
        for p in poses:
            positions.append((p, word))
    positions.sort()
    return " ".join(w for _, w in positions)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query")
    ap.add_argument("--max", type=int, default=500)
    ap.add_argument("--out", default="vosviewer-out/openalex.json")
    ap.add_argument(
        "--analysis",
        choices=["coauthorship", "cooccurrence"],
        default="cooccurrence",
    )
    ap.add_argument("--min-count", type=int, default=3)
    ap.add_argument("--min-link", type=int, default=2)
    ap.add_argument("--thesaurus", default="")
    args = ap.parse_args()

    print(f"🔎 OpenAlex: {args.query}")
    docs = fetch_openalex(args.query, args.max)
    print(f"  ↪ {len(docs)} documents")
    if not docs:
        sys.exit("Nenhum resultado.")

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
