# VOSviewer — Workflows comuns (Saci Digital)

Guia rápido dos fluxos mais frequentes. Cada workflow presume que você já tem a `vosviewer` skill carregada.

---

## 1. Mapa de termos a partir de um tema (via PubMed)

**Use quando:** o usuário pede "mapa bibliométrico sobre X" ou "quais são os principais temas na literatura de X".

```bash
python ~/.claude/skills/vosviewer/scripts/pubmed_to_vosviewer.py \
  "digital literacy higher education" \
  --max 300 \
  --min-count 5 \
  --min-link 3 \
  --out vosviewer-out/digital-literacy-pubmed.json
```

**Saída:** JSON em `vosviewer-out/`. Para abrir:

- **Online:** publique o JSON (Cloudflare R2 / GitHub raw / Netlify), construa `https://app.vosviewer.com/?json=<URL>` e envie ao usuário
- **Desktop:** File → Open → selecione o JSON

---

## 2. Rede de coautoria (via Crossref)

**Use quando:** "quem colabora com quem no tema X", "rede de autores", "pesquisadores do Brasil em X".

```bash
python ~/.claude/skills/vosviewer/scripts/crossref_to_vosviewer.py \
  "telemedicine brazil primary care" \
  --analysis coauthorship \
  --max 1000 \
  --min-count 3 \
  --out vosviewer-out/telemedicine-br-coauthors.json
```

Ajuste `--min-count` para filtrar autores com poucas publicações (normalmente 3+).

---

## 3. Mapa de conceitos a partir do OpenAlex

**Use quando:** o usuário quer um overview conceitual do campo, com hierarquia OpenAlex.

```bash
python ~/.claude/skills/vosviewer/scripts/openalex_to_vosviewer.py \
  "continuing medical education AI" \
  --analysis cooccurrence \
  --max 500 \
  --min-count 4 \
  --out vosviewer-out/cme-ai-concepts.json
```

OpenAlex retorna "concepts" pré-classificados, o que reduz ruído comparado ao PubMed.

---

## 4. A partir de um arquivo RIS/BibTeX local

**Use quando:** o usuário já tem um export de biblioteca (EndNote, Zotero, Mendeley).

```bash
# RIS
python ~/.claude/skills/vosviewer/scripts/ris_to_vosviewer.py \
  refs.ris --analysis cooccurrence --out vosviewer-out/refs.json

# BibTeX
python ~/.claude/skills/vosviewer/scripts/ris_to_vosviewer.py \
  refs.bib --analysis coauthorship --min-count 2
```

---

## 5. Com thesaurus (unificando sinônimos)

**Use quando:** há variações do mesmo termo ("ia" vs "inteligência artificial", "chatgpt" vs "modelos de linguagem").

1. Crie/edite `vosviewer-out/thesaurus-saci.txt` (um sinônimo por linha, tab-separado):

```
ia	inteligência artificial
chatgpt	inteligência artificial
llm	inteligência artificial
aps	atenção primária à saúde
atencao primaria	atenção primária à saúde
educacao	educação
```

2. Passe para o script:

```bash
python ~/.claude/skills/vosviewer/scripts/pubmed_to_vosviewer.py \
  "artificial intelligence primary care" \
  --thesaurus vosviewer-out/thesaurus-saci.txt \
  --min-count 5 \
  --out vosviewer-out/ai-aps.json
```

---

## 6. Converter JSON para .map + .net (desktop clássico)

```bash
python ~/.claude/skills/vosviewer/scripts/json_to_map_net.py \
  vosviewer-out/ai-aps.json \
  --out-prefix vosviewer-out/ai-aps
```

Gera `ai-aps.map` + `ai-aps.net`. No VOSviewer desktop: **File → Open → Map + Network files**.

---

## 7. Abrir em VOSviewer Online

**Pré-requisito:** o JSON precisa estar hospedado em URL pública HTTPS.

Opções de hospedagem (todas grátis):

- **GitHub raw** — commit no repo do projeto, use `https://raw.githubusercontent.com/user/repo/main/path.json`
- **Cloudflare R2** — use o MCP Cloudflare desta sessão
- **Netlify** — drag&drop de uma pasta com o JSON, publica em segundos
- **Gist** — `gh gist create file.json -p` e use a URL raw

Depois:

```bash
python ~/.claude/skills/vosviewer/scripts/open_in_vosviewer.py \
  --json-url "https://raw.githubusercontent.com/user/repo/main/ai-aps.json"
```

Copia/abre `https://app.vosviewer.com/?json=<URL-encoded>`.

---

## 8. Dataset do projeto Saci Digital

Para gerar um mapa dos textos do acervo:

1. Leia `acervo-saci/data/processed/bibliografia_parsed.json` com `Read`
2. Normalize para `Document` (title, abstract, authors, year, keywords)
3. Salve temporariamente como RIS ou passe direto via um script Python custom que importa `vosviewer_common` e chama `build_cooccurrence()`
4. Salve o JSON em `vosviewer-out/saci-acervo-<tema>.json`

Exemplo inline (em um script Python novo):

```python
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / ".claude/skills/vosviewer/scripts"))
from vosviewer_common import Document, build_cooccurrence, save_json, load_thesaurus

raw = json.loads(Path("acervo-saci/data/processed/bibliografia_parsed.json").read_text(encoding="utf-8"))
docs = [
    Document(
        title=r.get("titulo", ""),
        abstract=r.get("resumo", "") or r.get("abstract", ""),
        authors=r.get("autores") or [],
        year=r.get("ano"),
        keywords=r.get("palavras_chave") or r.get("keywords") or [],
    )
    for r in raw
]
thesaurus = load_thesaurus("vosviewer-out/thesaurus-saci.txt")
obj = build_cooccurrence(docs, min_term_count=3, min_link_strength=2, thesaurus=thesaurus)
save_json(obj, "vosviewer-out/saci-acervo.json")
```

---

## Dicas de ajuste final

| Problema | Ajuste |
|---|---|
| Grafo muito denso, ilegível | `--min-count` maior, `--min-link` maior |
| Poucos termos aparecem | `--min-count` menor (tente 2) |
| Termos duplicados/variantes | Use `--thesaurus` |
| Clusters pouco definidos | No desktop, ajuste "Resolution" na aba Analysis |
| Labels sobrepostos | No desktop/online, ajuste "Scale" no painel Visualization |
| Colorir por ano | Adicione `scores: {"Avg. pub. year": <year>}` nos items |
