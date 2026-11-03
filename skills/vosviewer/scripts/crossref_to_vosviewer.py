"""
Crossref query → VOSviewer JSON (co-authorship by default, or co-occurrence).

Uses the public Crossref REST API (no key needed).

Usage:
    python crossref_to_vosviewer.py "digital literacy higher education" --max 500
    python crossref_to_vosviewer.py "telemedicine diabetes" --analysis coauthorship
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


def fetch_crossref(query: str, max_results: int = 500) -> list[Document]:
    docs: list[Document] = []
    rows = min(1000, max_results)
    cursor = "*"
    fetched = 0
    while fetched < max_results:
        url = (
            "https://api.crossref.org/works?"
            f"query={urllib.parse.quote(query)}"
            f"&rows={min(rows, max_results - fetched)}"
            f"&cursor={urllib.parse.quote(cursor)}"
            "&select=title,author,abstract,published-print,published-online,DOI,URL,subject"
        )
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        msg = data.get("message", {})
        items = msg.get("items", [])
        if not items:
            break
        for it in items:
            title = " ".join(it.get("title") or []) or ""
            abstract = (it.get("abstract") or "").strip()
            # strip JATS XML crudely
            abstract = abstract.replace("<jats:p>", "").replace("</jats:p>", "")
            authors = []
            for a in it.get("author", []):
                fam = a.get("family") or ""
                giv = a.get("given") or ""
                if fam:
                    authors.append(f"{fam}, {giv[:1]}.".strip())
            year = None
            for k in ("published-print", "published-online", "issued"):
                parts = (it.get(k) or {}).get("date-parts")
                if parts and parts[0]:
                    try:
                        year = int(parts[0][0])
                        break
                    except (ValueError, TypeError):
                        pass
            docs.append(
                Document(
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    year=year,
                    doi=(it.get("DOI") or "").strip(),
                    url=(it.get("URL") or "").strip(),
                    keywords=list(it.get("subject") or []),
                )
            )
        fetched += len(items)
        cursor = msg.get("next-cursor") or ""
        if not cursor:
            break
        time.sleep(0.3)
    return docs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query", help="Crossref search query")
    ap.add_argument("--max", type=int, default=500)
    ap.add_argument("--out", default="vosviewer-out/crossref.json")
    ap.add_argument(
        "--analysis",
        choices=["coauthorship", "cooccurrence"],
        default="coauthorship",
    )
    ap.add_argument("--min-count", type=int, default=2)
    ap.add_argument("--min-link", type=int, default=1)
    ap.add_argument("--thesaurus", default="")
    args = ap.parse_args()

    print(f"🔎 Crossref: {args.query}")
    docs = fetch_crossref(args.query, args.max)
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
