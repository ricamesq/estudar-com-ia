---
name: gerador-de-apresentacao
description: Gera uma apresentação completa no padrão da casa (texto em marcadores, ilustração 3D por slide, diagramas animados, notas do apresentador, PDF 16:9). Usar quando pedirem slides de aula, seminário ou palestra.
---

Você monta apresentações seguindo a skill apresentacao-de-aula.

1. Pergunte o tema, o público, a duração e as fontes que devem ser usadas.
2. Separe o conteúdo do layout: escreva primeiro um arquivo de conteúdo (um item por slide com título, de três a cinco marcadores e as notas do apresentador) e mostre a sequência para aprovação antes de gerar qualquer imagem.
3. Para cada slide de tema, gere uma ilustração 3D (Nano Banana Pro, se a chave da API do Gemini estiver no .env), sem texto dentro da imagem, e ponha o crédito "Ilustração gerada por IA (Nano Banana)".
4. Diagramas, gráficos e passos em sequência saem animados por código (Manim ou ManimGX), com o quadro final no PDF. Vídeo realista (Veo) só em uma ou duas tomadas, porque cobra por segundo.
5. Layout fixo: fundo escuro, uma cor de destaque, título que descreve o assunto, imagem à direita e texto à esquerda, a mesma cor para a mesma função em todos os slides.
6. Último slide com as referências pela NBR 6023, conferidas no PubMed ou no Crossref.
7. Entregue em PDF 16:9 com nome de capa ("Sobrenome Ano - Título.pdf") e guarde o arquivo de conteúdo, para que a próxima versão mude só o texto.
Sem travessão, sem emoji, sem linguagem de venda, sem dado de paciente.
