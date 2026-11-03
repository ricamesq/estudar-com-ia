"""
Shared helpers for VOSviewer converter scripts.
Stdlib only. Python 3.9+.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


# ── Stopwords (PT + EN, short list: expand via thesaurus if needed) ────────

STOPWORDS_PT = {
    "a","o","as","os","um","uma","uns","umas","de","do","da","dos","das",
    "e","ou","mas","por","para","com","sem","sobre","entre","ao","aos",
    "no","na","nos","nas","em","é","são","foi","ser","ter","tem","estão",
    "este","esta","isso","aquilo","que","como","qual","quem","onde","quando",
    "não","sim","se","já","mais","menos","muito","pouco","também","só","apenas",
    "um","dois","três","quatro","cinco","seis","sete","oito","nove","dez",
    "pelo","pela","pelos","pelas","dum","duma","num","numa","ante","após",
    "até","desde","perante","segundo","sob","trás","através","durante",
}

STOPWORDS_EN = {
    "the","a","an","and","or","but","of","to","for","in","on","at","by",
    "with","from","as","is","are","was","were","be","been","being","this",
    "that","these","those","it","its","they","their","we","our","you","your",
    "he","she","him","her","his","hers","i","me","my","mine","ours","yours",
    "which","who","whom","whose","what","where","when","why","how",
    "not","no","yes","so","too","very","more","most","less","least","such",
}

STOPWORDS = STOPWORDS_PT | STOPWORDS_EN


# ── Data model ──────────────────────────────────────────────────────────────

@dataclass
class Document:
    """A minimal bibliographic record. All fields optional except title."""
    title: str
    abstract: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    doi: str = ""
    url: str = ""
    keywords: list[str] = field(default_factory=list)


# ── Text processing ─────────────────────────────────────────────────────────

def strip_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def normalize_term(term: str) -> str:
    """Lowercase, strip accents, collapse whitespace, no punctuation."""
    t = strip_accents(term.lower().strip())
    t = re.sub(r"[^\w\s-]", " ", t, flags=re.UNICODE)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def load_thesaurus(path: str | Path) -> dict[str, str]:
    """Read a tab-separated thesaurus: synonym <TAB> canonical (one per line)."""
    mapping: dict[str, str] = {}
    p = Path(path)
    if not p.exists():
        return mapping
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            mapping[normalize_term(parts[0])] = parts[1].strip()
    return mapping


def extract_terms(
    text: str,
    min_len: int = 3,
    max_len: int = 40,
    thesaurus: dict[str, str] | None = None,
) -> list[str]:
    """Extract unigrams + bigrams from text, filtered by stopwords."""
    if not text:
        return []
    norm = normalize_term(text)
    tokens = [t for t in norm.split(" ") if t and t not in STOPWORDS and len(t) >= min_len]
    unigrams = [t for t in tokens if len(t) <= max_len]
    bigrams: list[str] = []
    for i in range(len(tokens) - 1):
        bg = f"{tokens[i]} {tokens[i + 1]}"
        if min_len <= len(bg) <= max_len:
            bigrams.append(bg)
    terms = unigrams + bigrams
    if thesaurus:
        terms = [thesaurus.get(t, t) for t in terms]
    return terms


# ── Co-occurrence builder ───────────────────────────────────────────────────

def build_cooccurrence(
    docs: Iterable[Document],
    min_term_count: int = 3,
    min_link_strength: int = 2,
    thesaurus: dict[str, str] | None = None,
    use_keywords_if_available: bool = True,
) -> dict:
    """Build a VOSviewer-compatible JSON for keyword/term co-occurrence."""
    doc_terms: list[set[str]] = []
    term_count: Counter[str] = Counter()

    for d in docs:
        if use_keywords_if_available and d.keywords:
            terms = [
                thesaurus.get(normalize_term(k), normalize_term(k)) if thesaurus else normalize_term(k)
                for k in d.keywords
                if k
            ]
            terms = [t for t in terms if t]
        else:
            terms = extract_terms(f"{d.title} {d.abstract}", thesaurus=thesaurus)
        unique = set(terms)
        doc_terms.append(unique)
        for t in unique:
            term_count[t] += 1

    keep = {t for t, c in term_count.items() if c >= min_term_count}

    link_count: dict[tuple[str, str], int] = defaultdict(int)
    for terms in doc_terms:
        filtered = sorted(terms & keep)
        for i in range(len(filtered)):
            for j in range(i + 1, len(filtered)):
                link_count[(filtered[i], filtered[j])] += 1

    items = []
    id_map: dict[str, int] = {}
    for i, (term, count) in enumerate(sorted(term_count.items(), key=lambda x: -x[1]), start=1):
        if term not in keep:
            continue
        id_map[term] = i
        items.append(
            {
                "id": i,
                "label": term,
                "x": 0.0,
                "y": 0.0,
                "weights": {"Documents": count},
                "scores": {},
            }
        )

    links = []
    for (a, b), s in link_count.items():
        if s < min_link_strength:
            continue
        links.append({"source_id": id_map[a], "target_id": id_map[b], "strength": s})

    # Total link strength per item
    tls: Counter[int] = Counter()
    for link in links:
        tls[link["source_id"]] += link["strength"]
        tls[link["target_id"]] += link["strength"]
    for item in items:
        item["weights"]["Total link strength"] = tls.get(item["id"], 0)

    return {
        "network": {"items": items, "links": links, "clusters": []},
        "config": {
            "terminology": {
                "item": "termo",
                "items": "termos",
                "link": "coocorrência",
                "links": "coocorrências",
            }
        },
        "info": {},
    }


# ── Co-authorship builder ───────────────────────────────────────────────────

def build_coauthorship(
    docs: Iterable[Document],
    min_author_count: int = 2,
    min_link_strength: int = 1,
) -> dict:
    """Build a VOSviewer-compatible JSON for co-authorship networks."""
    author_docs: Counter[str] = Counter()
    link_count: dict[tuple[str, str], int] = defaultdict(int)

    for d in docs:
        authors = [a.strip() for a in d.authors if a and a.strip()]
        unique = sorted(set(authors))
        for a in unique:
            author_docs[a] += 1
        for i in range(len(unique)):
            for j in range(i + 1, len(unique)):
                link_count[(unique[i], unique[j])] += 1

    keep = {a for a, c in author_docs.items() if c >= min_author_count}

    items = []
    id_map: dict[str, int] = {}
    for i, (author, count) in enumerate(
        sorted(author_docs.items(), key=lambda x: -x[1]), start=1
    ):
        if author not in keep:
            continue
        id_map[author] = i
        items.append(
            {"id": i, "label": author, "x": 0.0, "y": 0.0, "weights": {"Documents": count}, "scores": {}}
        )

    links = []
    for (a, b), s in link_count.items():
        if a not in keep or b not in keep or s < min_link_strength:
            continue
        links.append({"source_id": id_map[a], "target_id": id_map[b], "strength": s})

    tls: Counter[int] = Counter()
    for link in links:
        tls[link["source_id"]] += link["strength"]
        tls[link["target_id"]] += link["strength"]
    for item in items:
        item["weights"]["Total link strength"] = tls.get(item["id"], 0)

    return {
        "network": {"items": items, "links": links, "clusters": []},
        "config": {
            "terminology": {
                "item": "autor",
                "items": "autores",
                "link": "coautoria",
                "links": "coautorias",
            }
        },
        "info": {},
    }


# ── IO ──────────────────────────────────────────────────────────────────────

def save_json(obj: dict, out_path: str | Path) -> Path:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def summarize(obj: dict) -> str:
    n = obj["network"]
    n_items = len(n["items"])
    n_links = len(n["links"])
    return f"{n_items} items · {n_links} links"
