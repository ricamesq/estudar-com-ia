# Estudar com IA

Skills, agentes e modelos para estudar com o Claude Code ou o Codex, da disciplina Estudar com IA (Medicina, CEUNSP).

## Como instalar

Com o Claude Code aberto na sua pasta de estudo, cole:

    Instale as skills e os agentes do repositório github.com/ricamesq/estudar-com-ia no meu Claude Code e copie o modelos/CLAUDE.md para esta pasta. Antes, mostre o que vai copiar e para onde, e espere o meu OK.

No Codex, peça o mesmo e troque CLAUDE.md por AGENTS.md.

## O que tem aqui

| Pasta | Para quê |
|---|---|
| skills/regras-de-estudo | regras para todo texto de estudo (ABNT, sem dado de paciente, citar a nota) |
| skills/resumo-de-aula | transforma uma anotação em resumo com perguntas de revisão |
| skills/bibliometria | busca na literatura sem erro de contagem |
| skills/vosviewer | mapas de coautoria e de palavras-chave no VOSviewer |
| agents/tutor | tutor que pergunta o que você já sabe antes de explicar |
| agents/conferidor-de-referencias | confere DOI e PMID e formata pela NBR 6023 |
| skills/apresentacao-de-aula | slides no padrão: título que descreve, marcadores curtos, ilustração |
| agents/gerador-de-apresentacao | apresentação completa: marcadores, ilustração 3D, diagramas animados, PDF |
| agents/questoes | questões de múltipla escolha com comentário, a partir das notas |
| agents/caso-ficticio | caso clínico fictício para treinar raciocínio |
| agents/leitor-de-artigo | leitura crítica de artigo científico |
| agents/plano-de-estudo | cronograma até a prova com revisão espaçada |
| modelos/CLAUDE.md | regras da pasta de estudo |

## Ferramentas de terceiros (instalar pela origem)

- graphify, mapa das notas: https://github.com/Graphify-Labs/graphify (pacote graphifyy)
- watch, resumo de vídeos: https://github.com/bradautomates/claude-video
- anatomy, figuras explicativas em SVG: https://github.com/wheresryan22/anatomy
- Zotero no Claude: https://github.com/54yyyu/zotero-mcp
- NotebookLM no Claude (não oficial, uso pessoal): https://github.com/jacob-bd/notebooklm-mcp-cli

## Imagem e vídeo

Nano Banana Pro (imagem) e Veo (vídeo) estão no aplicativo Gemini com plano pago do Google AI, ou pela API do Gemini com a sua chave do Google AI Studio guardada num arquivo .env (nunca no chat nem no GitHub). A API cobra por imagem e por segundo de vídeo.

## Cuidado

Nada de dado de paciente nem dado pessoal de colega, professor ou outra pessoa em nota, pedido ou arquivo: o que a IA lê vai para o modelo.
