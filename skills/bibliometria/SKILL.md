---
name: bibliometria
description: "Use ao construir, medir ou revisar corpus bibliográfico , busca em bases (PubMed, OpenAlex, Crossref, DOAJ, ERIC, SciELO), contagem, interseção, lacuna, triagem, cocitação, coautoria, thesaurus, Zotero. Contém as armadilhas que já produziram conclusão errada neste projeto: número certo pelo motivo errado. Consulte ANTES de afirmar que algo não existe na literatura. Para desenhar o mapa depois de ter os dados, veja a skill vosviewer."
---

# Bibliometria , o que já deu errado, e por quê

Esta skill não ensina bibliometria. Ensina os **erros específicos** que este projeto já
cometeu, todos com a mesma assinatura: **um número que parece certo e está errado**.
Nenhum foi pego por leitura , todos foram pegos por medição.

A regra que organiza o resto:

> **Nunca afirme ausência sem ter medido a presença.** Zero é afirmação forte ,
> significa "procurei no lugar certo, do jeito certo, e não há". Quase sempre significa
> outra coisa.

---

## 1. Zero tem seis causas. Só uma é ausência.

E elas se dividem em dois grupos que **não se verificam do mesmo jeito** , distinção que
o `codex-auditor` apontou como faltando, ao auditar esta própria regra.

### Quatro se eliminam por consulta

Cada uma tem teste concreto. Custam uma chamada, e o resultado é objetivo.

| causa | teste | caso real |
|---|---|---|
| **base errada** | repetir em base de cobertura diferente (OpenAlex, Crossref, DOAJ) | "maçonaria": 0 no PubMed, 1.529 no OpenAlex |
| **campo errado** | repetir o termo em outro campo indexado: `[Author]`, `[Journal]`, `topics.id` | `"amilton iatecola"[tw]` = 0; `"iatecola amilton"[Author]` = 11 |
| **consulta falhou** | ler o tratamento de erro: há caminho que devolve `0` num `except`? | 429 do OpenAlex virando zero |
| **aritmética** | conferir se os fatores da interseção são todos > 0 | interseção 0 porque uma frente já era 0 |

**Nome de autor:** o PubMed indexa `SOBRENOME NOME`; as pessoas escrevem `NOME
SOBRENOME`. Teste as duas ordens antes de concluir que o autor não publicou.

### Duas não se eliminam , declaram-se

Não há teste universal para elas, e fingir que há é pior do que admitir.

- **idioma errado** , provar exigiria buscar em todas as línguas. O que se declara: em
  que idioma a busca rodou, e se o vocabulário controlado da base é de outro. (O MeSH é
  em inglês; termo em português cai para texto livre e perde os sinônimos indexados.)
- **estratégia incompleta** , provar completude exigiria conhecer a estratégia completa,
  que é justamente o desconhecido. O que se declara: qual estratégia foi usada, por
  extenso, para que outro possa refutá-la.

### A consequência é sobre a força da frase permitida

Com as quatro primeiras eliminadas e as duas últimas declaradas, pode-se escrever:

> "Não há registro **nesta base**, com **esta estratégia**, **neste recorte**."

Nunca:

> ~~"Não existe literatura sobre isso."~~

A primeira é sustentável **e refutável** , alguém pode mudar a estratégia e mostrar o
contrário, que é como deve ser. A segunda é indefensável, porque afirma sobre tudo que
não foi consultado.

### Nota sobre o OpenAlex

Ele **cobra por requisição** (US$ 0,001) com orçamento diário que zera à meia-noite UTC.
Esgotado, devolve 429 com `Insufficient budget (...) Resets at midnight UTC` e um
`Retry-After` de horas. Então 429 ali tem duas causas que pedem respostas opostas:
rápido demais (esperar resolve) e cota do dia (não resolve). Ler o corpo antes de
reagir; uma sessão intensa esgota a cota.

## 2. Casamento superficial acerta a maioria e erra o suficiente

Todo casamento por string precisa de **contenção inteira**, nunca de palavra
compartilhada. Casos reais:

- MeSH devolveu `Hypoglycemia, Neonatal, Simulating Foetopathia Diabetica` para
  "retinopatia diabética" , descritor legítimo, doença errada, casou por "diabética".
- Wikipedia devolveu `Escala de Equilíbrio de Berg` como tradução de "teleconsulta",
  porque aquele artigo *menciona* teleconsulta. A frente virou `"teleconsulta" OR "Berg
  Balance Scale"`: 2.456 registros de uma escala de equilíbrio numa busca sobre consulta
  a distância.
- Um artigo entrou numa busca de voz por ter `SHIMMER` no título , acrônimo de índice de
  prontuário, não o parâmetro acústico.

**Regra:** busca por relevância ≠ identidade de conceito. O primeiro resultado de uma
busca fuzzy não é tradução, nem sinônimo, nem a mesma entidade.

## 3. Fusão de variantes: o erro é fundir, não deixar separado

Sugerir fusão por semelhança produziu, na primeira rodada real, onze propostas , quase
todas erradas:

- `Type 1 diabetes` → `Type 2 diabetes` (doenças diferentes; o algarismo era a diferença
  inteira, e o filtro descartava tokens de ≤2 caracteres)
- `Diabetes mellitus` → `Type 2 Diabetes Mellitus` (gênero virando espécie)
- `University of Baltimore` → `University of Maryland, Baltimore` (duas casas)

**Regras:** dígito nunca é token curto; `contido` vale para autor e instituição, jamais
para conceito (onde substring é hierarquia); exija **igualdade** de palavras
distintivas, não subconjunto. Errar para menos custa um clique; errar para mais põe no
mapa uma fusão falsa com cara de acerto. **A decisão final é sempre humana.**

## 4. Confira a soma por dois caminhos

O ingestor truncava o identificador em 24 caracteres para gerar chave. DOIs da mesma
editora compartilham prefixo, colidiam, um sobrescrevia o outro , e a saída dizia **"54
novos"** com o corpus em **49**. Cinco artigos sumiram em silêncio.

O bug existiu porque nada conferia. Sempre: `antes + novos == depois` e `novos +
já_existiam == lidos`. Se não fecha, **diga que não fecha**.

## 5. Teto do script ≠ tamanho do campo

Um script de busca dirigida que usava `per_page=25` + `rows=20`. Nenhuma das 13 queries
passou de 45 no relatório , porque 45 era o teto. A cobertura real varia em três ordens
de grandeza: 0,2% em `data literacy teacher education`, 83% em `DigCompEdu validation`.

Isso **não invalida** busca dirigida , ela existe para achar obras-chave. Mas o número
não sustenta afirmação sobre tamanho ou cobertura. Havendo corte, **diga quanto ficou de
fora**.

## 6. Escopo declarado, sempre

Métricas de "corpus inteiro" e de "incluídos" não são comparáveis. Um tema com 53
coletados e 0 triados respondeu "nenhum registro com DOI" , verdadeiro pela contagem,
enganoso pelo sentido. Diga o escopo em toda saída.

## 7. Texto completo e suplemento: a rota depende do tipo de artigo

Medido em 13/10/2026, ao buscar as sequências de oligos de Benke et al. (2025): o Claude Science tentou
o serviço OA do PMC e o FTP, recebeu 404 nos três caminhos e ficou girando. O suplemento existia; a rota
é que estava errada. 404 aqui é **rota errada**, não ausência (é o "consulta falhou" da seção 1).

**Ordem que funciona:**

1. **PMCID:** `elink.fcgi?dbfrom=pubmed&db=pmc&id=<PMID>`. Sem PMCID, não há texto completo aberto no
   PMC; vá ao DOI e veja se a editora oferece acesso aberto.
2. **Texto completo:** `efetch.fcgi?db=pmc&id=<número do PMCID>&retmode=xml`. Funciona para artigo de
   acesso aberto **e** para manuscrito de autor do NIH. É dali que saem métodos, tabelas e números.
3. **Lista dos suplementos:** no mesmo XML, as tags `<supplementary-material>` com `xlink:href` dão o
   nome de cada arquivo. Antes de baixar, saiba o que procura.
4. **Tipo do artigo:** se o XML tem `<article-id pub-id-type="manuscript-id">NIHMS...`, é **manuscrito de
   autor**, e a rota do passo 5 não serve para o suplemento.
5. **Suplemento de artigo de acesso aberto de editora:** Europe PMC,
   `https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/supplementaryFiles`, devolve um zip
   (PMC12904924: zip de 4,5 MB).
6. **Suplemento de manuscrito NIHMS:** o Europe PMC devolve resposta vazia (297 bytes, PMC11700762), o
   serviço OA do PMC (`/utils/oa/oa.fcgi`) e o FTP dão 404, e o link
   `pmc.ncbi.nlm.nih.gov/articles/instance/<id>/bin/<arquivo>` abre uma página "Preparing to download..."
   que exige navegador. **É barreira contra robô: não contornar.** Pare, diga qual arquivo é preciso e
   peça ao usuário que baixe no navegador e grave na pasta do pacote, com o nome que você indicar.
7. **Antes de pedir ao usuário, tente a editora.** Manuscrito NIHMS também tem versão na editora. Na
   Elsevier, o Crossref dá o PII (`alternative-id`), e o suplemento costuma estar no CDN público
   `https://ars.els-cdn.com/content/image/1-s2.0-<PII>-mmc1.pdf` (troque a extensão se der 404). Benke
   2025 (PII S0956566324010595) veio por aí em 13/10/2026: 200, PDF de 1,5 MB, sem barreira.

**O que nunca fazer:** reconstruir sequência, número de catálogo, volume ou temperatura de memória
porque o suplemento não abriu. O que não veio do arquivo fica "a definir", com o nome do arquivo que falta.

**Antes de girar em rotas:** se duas rotas diferentes deram 404 para o mesmo arquivo, pare e confira o
tipo do artigo (passo 4) em vez de tentar a terceira.

---

## Limites que não se contornam

- **Portaria CAPES 275/2023, art. 50** veda robô ou agente inteligente para acessar ou
  baixar conteúdo contratado , e o veto alcança o usuário autorizado. Scopus, Web of
  Science, Portal CAPES, Google Scholar: monte a string, abra a base ao lado, receba o
  export. Nunca automatize a interface.
- **Nunca escrever em `zotero.sqlite`.** Leitura só com `mode=ro&immutable=1`.
- **Nunca sobrescrever decisão de triagem.** Metadado se refaz; julgamento humano não.
- **Nunca citar identificador sem verificar na API.** DOI fabricado é indistinguível do
  real pela leitura.

## Antes de entregar

1. Todo zero foi explicado por uma das seis causas?
2. Toda soma fecha por dois caminhos?
3. Todo corte diz quanto ficou de fora?
4. Todo escopo está declarado?
5. Toda fusão de variantes foi decidida por humano?
