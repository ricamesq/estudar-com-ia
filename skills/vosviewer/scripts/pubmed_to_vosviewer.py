"""
PubMed query → VOSviewer JSON (keyword co-occurrence).

Uses the public NCBI E-utilities API (no key required, but rate-limited).

Usage:
    python pubmed_to_vosviewer.py "letramento digital docente" --max 200 --out out.json
    python pubmed_to_vosviewer.py "covid vaccine AND brazil" --max 500 --min-count 5

Or import and call fetch_pubmed() + build_cooccurrence() directly.
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
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from vosviewer_common import (  # noqa: E402
    Document,
    build_cooccurrence,
    load_thesaurus,
    save_json,
    summarize,
)

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
HEADERS = {"User-Agent": "Saci-Digital-VOSviewer/1.0 (research)"}


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def esearch(query: str, max_results: int = 200) -> list[str]:
    """Return a list of PMIDs matching the query."""
    url = (
        f"{EUTILS}/esearch.fcgi?db=pubmed"
        f"&term={urllib.parse.quote(query)}"
        f"&retmax={max_results}&retmode=json"
    )
    data = json.loads(_get(url))
    return data.get("esearchresult", {}).get("idlist", [])


def efetch(pmids: Iterable[str]) -> list[Document]:
    """Fetch full records for PMIDs in batches of 200."""
    pmids = list(pmids)
    docs: list[Document] = []
    for i in range(0, len(pmids), 200):
        chunk = pmids[i : i + 200]
        url = (
            f"{EUTILS}/efetch.fcgi?db=pubmed"
            f"&id={','.join(chunk)}&retmode=xml"
        )
        xml_bytes = _get(url)
        root = ET.fromstring(xml_bytes)
        for art in root.findall(".//PubmedArticle"):
            docs.append(_parse_article(art))
        time.sleep(0.4)  # NCBI etiquette
    return docs


def _parse_article(art: ET.Element) -> Document:
    title = "".join(art.itertext()) if False else (art.findtext(".//ArticleTitle") or "")
    abstract_parts = [t.text or "" for t in art.findall(".//Abstract/AbstractText")]
    abstract = " ".join(abstract_parts)
    authors = []
    for a in art.findall(".//AuthorList/Author"):
        last = a.findtext("LastName") or ""
        fore = a.findtext("ForeName") or ""
        coll = a.findtext("CollectiveName")
        if coll:
            authors.append(coll)
        elif last:
            authors.append(f"{last}, {fore[:1]}.".strip())
    year_text = (
        art.findtext(".//ArticleDate/Year")
        or art.findtext(".//PubDate/Year")
        or art.findtext(".//JournalIssue/PubDate/Year")
    )
    try:
        year = int(year_text) if year_text else None
    except ValueError:
        year = None
    doi = ""
    for aid in art.findall(".//ArticleId"):
        if (aid.get("IdType") or "").lower() == "doi":
            doi = (aid.text or "").strip()
            break
    keywords = [
        (k.text or "").strip()
        for k in art.findall(".//KeywordList/Keyword")
        if k.text
    ]
    # MeSH descriptors
    mesh = [
        (d.text or "").strip()
        for d in art.findall(".//MeshHeadingList/MeshHeading/DescriptorName")
        if d.text
    ]
    return Document(
        title=title,
        abstract=abstract,
        authors=authors,
        year=year,
        doi=doi,
        url=f"https://pubmed.ncbi.nlm.nih.gov/{art.findtext('.//PMID') or ''}/",
        keywords=keywords + mesh,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query", help="PubMed search query")
    ap.add_argument("--max", type=int, default=200, help="Max articles")
    ap.add_argument("--out", default="vosviewer-out/pubmed.json")
    ap.add_argument("--min-count", type=int, default=3, help="Min term count")
    ap.add_argument("--min-link", type=int, default=2, help="Min link strength")
    ap.add_argument("--thesaurus", default="", help="Path to thesaurus .txt")
    args = ap.parse_args()

    print(f"🔎 esearch: {args.query}")
    pmids = esearch(args.query, args.max)
    print(f"  ↪ {len(pmids)} PMIDs")
    if not pmids:
        sys.exit("Nenhum resultado.")

    print(f"📥 efetch: {len(pmids)} articles")
    docs = efetch(pmids)
    print(f"  ↪ {len(docs)} parsed")

    thesaurus = load_thesaurus(args.thesaurus) if args.thesaurus else None
    obj = build_cooccurrence(
        docs,
        min_term_count=args.min_count,
        min_link_strength=args.min_link,
        thesaurus=thesaurus,
    )
    out = save_json(obj, args.out)
    print(f"✅ {out} — {summarize(obj)}")


if __name__ == "__main__":
    main()
