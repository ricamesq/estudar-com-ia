---
name: vosviewer
description: Build and open bibliometric network visualizations in VOSviewer (desktop or VOSviewer Online) from bibliographic data. Use this skill whenever the user wants to visualize co-authorship, co-citation, keyword co-occurrence, bibliographic coupling, or term maps from PubMed, Crossref, Scopus, Web of Science, RIS exports, NotebookLM sources, or any list of papers. Also trigger on phrases like "mapa bibliométrico", "rede de coautoria", "análise bibliométrica", "VOSviewer", "co-citation", "term map", "keyword map".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebFetch
---

# VOSviewer Integration

Purpose: turn any bibliographic dataset into a working VOSviewer network — either as a JSON file that loads directly in **VOSviewer Online** (no install), or as a .map + .net pair for the desktop version.

## When to use this skill

Trigger this skill when the user asks for any of:

- Mapa bibliométrico / bibliometric map
- Rede de coautoria / co-authorship network
- Rede de citação / co-citation network / bibliographic coupling
- Mapa de termos / keyword map / term co-occurrence
- "Visualizar artigos do PubMed/Crossref/Scopus/RIS no VOSviewer"
- "Quero ver a rede de autores/termos/keywords de …"
- Explicit: "VOSviewer", "app.vosviewer.com", ".map", ".net", ".json VOSviewer"

Also consider this skill when the user has a dataset of academic references (NotebookLM sources, acervo, bibliografia_parsed.json) and wants to explore it visually.

## Core concepts

VOSviewer works with **items** (nodes) connected by **links** (edges), organized into **clusters**. Items can be authors, documents, terms, keywords, journals, organizations, countries, etc.

Four analysis types:

1. **Co-authorship** — items = authors/organizations/countries, link strength = number of co-authored papers
2. **Co-citation** — items = cited references/authors/sources, link strength = number of documents citing both
3. **Bibliographic coupling** — items = documents/authors/sources, link strength = number of shared cited references
4. **Co-occurrence** — items = keywords/terms, link strength = number of documents where both appear

## File formats VOSviewer accepts

| Format | Extension | Use case |
|---|---|---|
| **VOSviewer JSON** | `.json` | Best for sharing. Single file loads in VOSviewer Online via URL. Contains items + links + config. |
| **Map + Network** | `.map` + `.net` | Classic desktop format. Tab-separated. `.map` = items, `.net` = links. |
| **Bibliographic DB** | Various | Raw exports from Web of Science, Scopus, Dimensions, Lens, PubMed (MEDLINE), Crossref JSON, RIS. VOSviewer parses these directly. |

**Rule of thumb:** Produce the **JSON file** when possible — it's the most flexible, shareable, and works in VOSviewer Online (no desktop install required).

## VOSviewer JSON schema (essentials)

```jsonc
{
  "network": {
    "items": [
      {
        "id": 1,                          // unique integer
        "label": "cultura digital",       // display name
        "description": "optional HTML",   // shown in popover
        "url": "https://...",             // optional click-through
        "x": 0.42,                        // optional; VOSviewer computes if omitted
        "y": -0.17,                       // optional
        "cluster": 1,                     // integer cluster id
        "weights": {                      // arbitrary numeric weights
          "Documents": 12,
          "Citations": 58,
          "Total link strength": 23
        },
        "scores": {                       // optional numeric scores for coloring
          "Avg. pub. year": 2022.4
        }
      }
    ],
    "links": [
      {"source_id": 1, "target_id": 2, "strength": 3}
    ]
  },
  "config": {
    "terminology": {                      // optional: customize labels
      "item": "termo", "items": "termos",
      "link": "coocorrência", "links": "coocorrências",
      "cluster": "cluster", "clusters": "clusters"
    },
    "templates": [                        // optional: label/color visualization
      { "label_size": {"min": 0.5, "max": 2.0} }
    ]
  }
}
```

## Canonical workflow

Follow these steps when the user asks for a VOSviewer visualization:

### 1. Identify the data source

Ask (or infer) from:

- **PubMed query** — use `mcp__7899fadf-...__search_articles` + `get_article_metadata` (this project has the PubMed MCP)
- **Crossref** — `WebFetch` `https://api.crossref.org/works?query=...&rows=100` (free, no key)
- **OpenAlex** — `WebFetch` `https://api.openalex.org/works?search=...&per_page=100`
- **NotebookLM sources** — `mcp__notebooklm-mcp__source_get_content` per source
- **Local file** — RIS, BibTeX, CSV, JSON in the project (use Read/Glob)
- **Manual list** — user pastes DOIs or titles

### 2. Pick the analysis type

| User says | Analysis type | Items | Links by |
|---|---|---|---|
| "rede de autores" / "co-authorship" | co-authorship | authors | co-authored papers |
| "mapa de termos" / "keyword map" | co-occurrence | keywords/terms | co-occurrence in abstracts/titles |
| "co-citação" / "co-citation" | co-citation | cited refs | co-cited by a common paper |
| "artigos similares" / "coupling" | bibliographic coupling | documents | shared references |
| "mapa de temas" / "themes" | co-occurrence | terms | co-occurrence |

Default when ambiguous: **keyword/term co-occurrence** — it's the most forgiving analysis and works with just titles + abstracts.

### 3. Build the network

Use the appropriate converter script in `scripts/` (see below). All scripts emit a VOSviewer JSON file in the current project.

### 4. Open the result

Two options — present both to the user:

**Option A — VOSviewer Online (zero install):**

1. Host the JSON file anywhere publicly reachable (GitHub raw, S3, Netlify, Cloudflare R2, a gist, etc.)
2. Build the URL:
   ```
   https://app.vosviewer.com/?json=<URL-encoded-URL-to-json>
   ```
3. Share this URL with the user. Clicking it loads the network directly in the browser.

**Option B — VOSviewer Desktop:**

1. Save the JSON file locally
2. Instruct the user: open VOSviewer → File → Open → select the JSON file
3. Alternatively provide `.map` + `.net` tab-separated files

### 5. Offer tuning

After producing the first version, offer to:

- Filter items by minimum weight (e.g., keywords that appear ≥ 5 times)
- Change cluster count via resolution parameter
- Add year scores to show temporal trends (oldest = blue, newest = red)
- Merge synonyms via a thesaurus (e.g., "ia" ↔ "inteligência artificial")

## Scripts

This skill ships with ready converter scripts in `scripts/`:

- `scripts/pubmed_to_vosviewer.py` — PubMed query → keyword co-occurrence JSON
- `scripts/crossref_to_vosviewer.py` — Crossref query → co-authorship JSON
- `scripts/openalex_to_vosviewer.py` — OpenAlex query → concepts co-occurrence JSON
- `scripts/ris_to_vosviewer.py` — RIS file → keyword co-occurrence JSON
- `scripts/json_to_map_net.py` — Convert VOSviewer JSON → `.map` + `.net` for desktop
- `scripts/open_in_vosviewer.py` — Build the VOSviewer Online URL (or open desktop)

All scripts are stdlib-only Python (no pip dependencies) unless noted.

## Thesaurus (Portuguese-friendly)

`reference/thesaurus-pt.txt` contains common Brazilian-Portuguese synonym normalizations (e.g., `ia → inteligência artificial`, `chatgpt → modelos de linguagem`, `aps → atenção primária`). Load this when building term co-occurrence maps for Saci Digital or Portuguese health/education datasets.

## Saci Digital integration

For this project specifically, useful starting datasets:

- `acervo-saci/data/processed/bibliografia_parsed.json` — pre-parsed bibliography
- `acervo-saci/output/notebooklm/03_livros_referencias_links/livros_referencias.md` — book/reference list
- NotebookLM notebook `32897aac` (Portal Saci Digital, 13 docs) — source titles via `mcp__notebooklm-mcp__notebook_get`
- NotebookLM notebook `9f860ed7` (Saci Mentor, 5 pedagogical docs)

Example end-to-end request: "Gera um mapa de termos dos textos do acervo Saci sobre cultura digital" → load `bibliografia_parsed.json`, filter by tag, extract titles+abstracts, build keyword co-occurrence via `scripts/ris_to_vosviewer.py` (after converting to RIS or directly via a small adapter), emit JSON, host on GitHub raw, return the `app.vosviewer.com?json=…` URL.

## Output location convention

Save all produced files in `vosviewer-out/` in the current project root (create if missing):

```
vosviewer-out/
├── YYYY-MM-DD_topic.json        # VOSviewer JSON
├── YYYY-MM-DD_topic.map         # desktop map file (if requested)
├── YYYY-MM-DD_topic.net         # desktop network file (if requested)
└── README.md                     # What was generated, how, and the Online URL
```

## Response format

When delivering a VOSviewer result to the user, ALWAYS include:

1. **Dataset summary** — source, number of items, number of links, date range (if available)
2. **File path(s)** — where the JSON/map/net files were saved
3. **VOSviewer Online URL** — if the JSON was hosted somewhere reachable
4. **Desktop instructions** — one line on how to open the JSON locally
5. **Next actions** — what to tune next (filter, cluster count, thesaurus, etc.)

Keep the response concise. Do not paste the full JSON in the chat — only the summary and the URL/path.

## Reference links

- VOSviewer homepage: https://www.vosviewer.com/
- VOSviewer Online: https://app.vosviewer.com/
- Manual (JSON format): https://app.vosviewer.com/docs/file-types/json-file-type/
- Desktop manual: https://www.vosviewer.com/documentation/Manual_VOSviewer_1.6.20.pdf
