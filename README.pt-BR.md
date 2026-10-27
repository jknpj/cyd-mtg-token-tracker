# CYD MTG Table Companion

**Português (Brasil)** | [English](README.md)

**Tokens, pontos de vida, dano de comandante e dados para a sua mesa de Magic, tudo em uma tela touch de 2,8 polegadas. Sem celular, Wi-Fi ou conta durante a partida.**

<p align="center">
  <img src="docs/screenshots/home.png" alt="Menu principal com Tokens, Life Counter, Dice / Coin e Settings" width="200">
  <img src="docs/screenshots/layout-classic.png" alt="Carta do token Soldier: cinco em jogo, um virado, com marcadores Shield e Flying" width="200">
  <img src="docs/screenshots/life-counter.png" alt="Contador de vida para quatro jogadores com paineis coloridos virados para cada lugar" width="200">
  <img src="docs/screenshots/dice.png" alt="Tres dados de vinte lados em 3D somando 13" width="200">
</p>

Um companheiro de mesa offline de Magic: The Gathering para a placa barata **CYD ESP32-2432S028R** ("Cheap Yellow Display"), antigo *CYD MTG Token Tracker*. Grave uma vez e deixe na mesa:

- **Painel de tokens**: 455 tokens de todos os precons de Commander, mais o seu token personalizado. Acompanhe quantos estao em jogo, quantos estao virados, marcadores e poder/resistencia.
- **Decks e precons**: importe os tokens de qualquer um dos **198 precons de Commander** com um toque, ou monte ate oito decks seus.
- **Contador de vida**: paineis grandes e coloridos para **1 a 8 jogadores**, cada um virado para o seu lugar, com dano de comandante (parceiros inclusos) e sorteio de "quem comeca?".
- **Dados e moedas em 3D**: d4 a d20 e moedas, ate 20 por vez, com um lancamento 3D girando.
- **Desenhos**: desenhe bigodes (ou o que quiser) nos seus tokens.
- **Tudo fica salvo** entre as sessoes: tokens, marcadores, decks, configuracoes e, se quiser, a partida em andamento.

[Capturas de tela](#capturas-de-tela) · [Primeiros passos](#primeiros-passos) · [Como jogar](#como-jogar) · [Tokens](#controles) · [Vida](#vida-e-dano-de-comandante) · [Dados](#dados-e-moeda) · [Configuracoes](#configuracoes) · [Problemas](#solucao-de-problemas) · [Para desenvolvedores](#catalogo-de-tokens)

## Capturas de tela

*Capturadas de um CYD real com `tools/screenshot.py`. A arte oficial dos tokens nao e distribuida com o projeto, entao as cartas aqui mostram a area lisa no lugar dela; com a [arte](#arte), a ilustracao aparece nesse espaco. A interface da placa e em ingles.*

**Tokens**

| Carta do token | Escolher um token | Busca |
| :---: | :---: | :---: |
| <img src="docs/screenshots/layout-classic.png" alt="Layout Classic: Soldier com cinco em jogo, um virado, marcadores Shield e Flying e barra de controles embaixo" width="200"> | <img src="docs/screenshots/token-list.png" alt="Lista de tokens, pagina 1 de 51, com Soldier selecionado e cinco em jogo" width="200"> | <img src="docs/screenshots/search-results.png" alt="Resultados da busca white flying: Spirit, Angel, Bird, Pegasus e outros" width="200"> |
| Quantidade, copias viradas, marcadores | 455 tokens, pagina por pagina | Digite `white flying` e veja os voadores |

| Marcadores | Menu de tokens | Desenhos |
| :---: | :---: | :---: |
| <img src="docs/screenshots/counters.png" alt="Pagina de marcadores com +1/+1 em 2, Shield 1 e Flying 1" width="200"> | <img src="docs/screenshots/token-menu.png" alt="Menu de tokens: Choose token, Decks / Precons, Card options, Main menu, Close" width="200"> | <img src="docs/screenshots/drawing.png" alt="Token Bird com carinha sorridente, bigode vermelho e coroa amarela desenhados a mao" width="200"> |
| +1/+1, Shield, habilidades e mais | Tudo sobre tokens em um lugar | Desenhe em qualquer token |

**Decks**

| Seus decks | Precons de Commander |
| :---: | :---: |
| <img src="docs/screenshots/decks.png" alt="Tela de decks com o deck importado Calling All Angels ativo" width="200"> | <img src="docs/screenshots/precons.png" alt="Lista de precons, pagina 1 de 22, mais novos primeiro, com codigo da colecao, ano e quantidade de tokens" width="200"> |
| Oito decks mais All tokens | Um toque importa os tokens do precon |

**Vida, dados e moedas**

| Contador de vida | Dano de comandante | Menu da vida |
| :---: | :---: | :---: |
| <img src="docs/screenshots/life-counter.png" alt="Quatro jogadores no meio da partida, com o jogador 2 marcado FIRST" width="200"> | <img src="docs/screenshots/commander-damage.png" alt="Registrando dano de comandante no jogador 3: o jogador 1 causou 7" width="200"> | <img src="docs/screenshots/life-menu.png" alt="Menu da vida: Dice / Coin, Who starts?, New game, Save match, Main menu, Close" width="200"> |
| Metade esquerda -1, direita +1 | Dano de cada comandante | Quem comeca, nova partida e mais |

| Dados | Moedas |
| :---: | :---: |
| <img src="docs/screenshots/dice.png" alt="Tres d20 rolados somando 13" width="200"> | <img src="docs/screenshots/coins.png" alt="Tres moedas: uma cara dourada e duas coroas prateadas" width="200"> |
| d4 a d20, ate 20 de uma vez | Caras e coroas contadas para voce |

**Visual e configuracoes**

| Layout Overlay | Layout Card only | Card options |
| :---: | :---: | :---: |
| <img src="docs/screenshots/layout-overlay.png" alt="Layout Overlay com botoes grandes de menos e mais sobre a arte" width="200"> | <img src="docs/screenshots/layout-card-only.png" alt="Layout Card only com os controles escondidos" width="200"> | <img src="docs/screenshots/card-options.png" alt="Card options pagina 1: miniaturas dos layouts Classic, Overlay e Card only" width="200"> |
| Botoes maiores sobre a arte | So a carta, controles somem | Escolha o layout |

## Primeiros passos

### Do que voce precisa

- Uma placa **CYD ESP32-2432S028R** (a de tela **ILI9341** de 2,8 polegadas com touch **XPT2046**). Outras variantes do CYD podem usar outra tela ou outros pinos.
- Um cabo USB **de dados** (alguns cabos so carregam).
- Um computador com [VS Code e PlatformIO](https://platformio.org/install/ide?install=vscode).
- Opcional: um cartao microSD, para arte mais nitida ou para salvar desenhos.

### Grave o firmware

1. Baixe ou clone este repositorio e abra a pasta no VS Code.
2. Conecte a placa. Se ela nao estiver na **COM7**, troque `upload_port` e `monitor_port` no [platformio.ini](platformio.ini) pela porta da sua placa.
3. Clique em **PlatformIO: Upload** (a seta na barra de status embaixo). A primeira compilacao leva alguns minutos.

Pronto: a placa reinicia no menu principal. Prefere a linha de comando? Na pasta do projeto:

```console
pio run -e esp32dev -t upload
```

No **Prompt de Comando** do Windows, se `pio` nao estiver no PATH:

```bat
"%USERPROFILE%\.platformio\penv\Scripts\pio.exe" run -e esp32dev -t upload
```

> **A arte dos tokens e opcional.** O repositorio nao inclui arte oficial das cartas. Sem ela, os tokens mostram uma area colorida lisa; para ter as ilustracoes, [gere a arte](#regenerar-o-catalogo-e-as-artes) antes de compilar ou [copie-a para um microSD](#arte-em-alta-qualidade-no-microsd).
>
> **Atualizando?** E so gravar de novo: tokens, decks e configuracoes sao mantidos. Nao use `erase_flash`.

## Como jogar

A placa comeca no **MAIN MENU**. Escolha um modo; voce pode trocar a qualquer momento sem perder os tokens nem a partida atual. **BACK** sempre volta um passo, e **MAIN MENU** no menu de cada modo leva de volta ao inicio.

**Tokens**

1. Toque em **TOKENS**. Toque no **nome** da carta para escolher um token (ou na **lupa** para buscar).
2. Use **+** e **-** para mudar quantos estao em jogo. O botao do meio alterna entre quantidade (`QTY`), copias viradas (`TAP`) e bonus de poder/resistencia (`POW`, `TGH`).
3. Toque na **arte** para virar ou desvirar todos.
4. Toque no **texto de regras** para adicionar marcadores como +1/+1, Shield ou Flying.
5. Toque no **icone de menu** para decks, precons, opcoes da carta e o menu principal.

**Jogando com um precon?** Icone de menu → **DECKS / PRECONS** → **NEW** e toque no seu precon. A carta passa a mostrar so os tokens daquele deck.

**Vida**

1. Toque em **LIFE COUNTER**. Coloque todos em volta da placa: cada painel fica virado para o seu jogador.
2. Toque na **metade esquerda** de um painel para **-1** e na **metade direita** para **+1**; segure para ir mais rapido.
3. Toque na **faixa com o nome** de um jogador para registrar dano de comandante causado a ele.
4. O botao redondo no meio abre **WHO STARTS?**, **NEW GAME** (jogadores e vida inicial), dados e mais.

**Dados e moedas**

Toque em **DICE / COIN** no menu principal ou no menu da vida, escolha o dado e quantos, e toque em **ROLL**.

**Tela desbotada?** **SETTINGS** no menu principal tem brilho, desligamento da tela, orientacao e gama. O visual da carta (layout, tom, desenhos) fica em **CARD OPTIONS**, no menu de tokens.

## Hardware

| Componente | Barramento | Pinos configurados |
| --- | --- | --- |
| Tela ILI9341 | HSPI | SCLK 14, MISO 12, MOSI 13, CS 15, DC 2 |
| Backlight | LEDC / PWM | GPIO 21 |
| Touch XPT2046 | VSPI | SCLK 25, MISO 39, MOSI 32, CS 33, IRQ 36 |
| Slot microSD | VSPI, mesmo periferico do touch | SCLK 18, MISO 19, MOSI 23, CS 5 |

O firmware troca os pinos do VSPI ao acessar o SD e depois restaura os do touch. O brilho e controlado diretamente por `BACKLIGHT_PIN` em [src/main.cpp](src/main.cpp); `TFT_BL` fica sem definicao de proposito, para o TFT_eSPI nao controlar esse pino.

## Controles

O token aparece como uma carta em modo retrato. No layout **Classic** (o padrao) ha uma barra inferior com estes botoes:

- **<** / **>**: token anterior / proximo.
- Botao central: alterna o que **-** e **+** editam: `QTY` (quantidade em jogo), `TAP` (quantos estao virados), `POW` e `TGH` (modificadores de poder/resistencia, so em criaturas). Em `QTY`, toque no grupo de icones desvirados ou virados na arte para escolher qual tipo de copia **+ / -** adiciona ou remove; o grupo escolhido fica destacado. O modo atual aparece no botao. Os marcadores (+1/+1 e os demais) ficam na tela de **contadores**, abaixo.
- Tocar na area da arte vira todos os tokens desvirados ou, se ja estiverem todos virados, desvira todos.
- Tocar na barra do nome abre a lista de tokens, em paginas. Toque num nome para seleciona-lo; **<** / **>** trocam de pagina, **FIND** abre a busca, **BACK** volta para a carta e **DECKS** abre os seus [decks de tokens](#decks-de-tokens).
- O icone de menu, na margem superior esquerda ao lado da carta, abre o **menu de tokens** (**CHOOSE TOKEN**, **DECKS / PRECONS**, **CARD OPTIONS**, **MAIN MENU**, **CLOSE**; toque fora dele para fechar) e a lupa, na margem superior direita, abre a **busca**. Nos outros layouts os dois icones ficam entre os botoes sobre a arte.

Os grupos de icones desvirado/virado permanecem visiveis em todos os modos enquanto houver ao menos uma copia em jogo. Com zero copias, **Card Only** oculta os dois grupos; voltar para `QTY`, usar **+ / -** ou escolher um grupo mostra ou mantem os icones por 2 segundos. Assim da para escolher como a primeira copia entra sem deixar icones numa mesa vazia. Classic e Overlay mantem os grupos vazios visiveis em `QTY`. "IN PLAY" e a quantidade aparecem quando ha mais de um token; com 0 ou 1, a quantidade aparece por 2 segundos depois de uma interacao de quantidade e some em seguida, deixando a arte limpa. O grupo escolhido determina se **+ / -** adiciona ou remove copias viradas ou desviradas. O indicador de posicao (por exemplo, `1/76`) aparece brevemente ao trocar de token e depois some. O icone de mana no canto do nome indica a cor: sol (branco), gota (azul), caveira (preto), chama (vermelho), arvore (verde), roda de cinco pontos coloridos (multicolor) e losango (incolor). Os mesmos icones aparecem na lista e no seletor de cor do editor.

O primeiro item da lista, `Custom`, e um token editavel: com ele selecionado, toque na parte de baixo da carta (tipo e texto) para abrir o editor de nome, linha de tipo, texto, cor e P/T. Os campos de texto usam um teclado na tela, e **SAVE** grava o token na flash.

<img src="docs/screenshots/editor.png" alt="Editor do token personalizado com nome, tipo, texto, cor e poder/resistencia" width="200">

O P/T exibido ja soma os marcadores e os modificadores. Tokens sem P/T (artefatos) editam apenas quantidade e tapped.

Tokens com P/T variavel preservam os simbolos impressos (`*/*`, `*/1+*` etc.), em vez de fingir que sao 0/0. Seus modificadores aparecem junto do simbolo; o painel de tokens nao conhece cemiterios e nao le os totais do contador de vida para resolver essas habilidades sozinho. Cragflame e um Equipment: seu texto aparece na carta, mas equipar e aplicar seu bonus a outra criatura continuam sendo acoes manuais.

## Modo de desenho

Bigodes sao bem-vindos. **Segure a arte por cerca de um segundo**, ou abra os **Contadores** e toque em **DRAW**, para decorar o token selecionado. A pagina 3 do **CARD OPTIONS** escolhe [como o desenho comeca, onde a tinta vai e onde ela e salva](#card-options-pagina-3-desenhos).

<img src="docs/screenshots/drawing.png" alt="Modo de desenho com rosto, bigode e coroa desenhados sobre um token Bird e botoes Back, Pen, Undo, Clear e Save" width="240"> <img src="docs/screenshots/drawing-palette.png" alt="Pop-up do PEN sobre o desenho com oito cores, tres pinceis e a borracha" width="240">

A carta inteira cabe acima de uma barra separada, permitindo desenhar sem encostar nos controles do jogo. Com **DOODLE AREA** em `WHOLE CARD` (o padrao) da para desenhar na arte, nome, moldura e texto; com `ART ONLY`, a tinta fica so na arte e o que ja foi desenhado fora dela fica oculto (nao apagado) ate voltar a opcao. Durante o desenho, os indicadores de quantidade e virados ficam ocultos; os valores do jogo nao mudam. Fora desse modo, o desenho continua visivel nos tres layouts e os toques normais continuam funcionando.

| Botao | Acao |
| --- | --- |
| **BACK** | Voltar para a carta, mantendo o desenho desse token durante a sessao |
| **PEN** | Abrir um pop-up sobre o desenho com oito cores, tres tamanhos de pincel e a borracha (**ERASE**). Um toque escolhe e fecha; toque em qualquer outro lugar (ou em **PEN** de novo) para fechar sem mudar nada. O botao mostra **ERASE** enquanto a borracha estiver ativa |
| **UNDO** | Remover o ultimo traco completo; um toque isolado tambem conta como traco |
| **CLEAR** | Confirmar a limpeza do desenho atual desse token |
| **SAVE** | Manter o desenho depois de reiniciar, na flash ou no microSD (veja **SAVE DOODLES TO**) |

**Borracha:** com **ERASE** selecionada, toque num traco para remover o traco inteiro (o de cima, sob o dedo); arraste para apagar varios. Escolher uma cor ou pincel volta para a caneta.

**Ha suporte a desenhos temporarios e salvos.** Cada token, inclusive o `Custom`, tem seu proprio desenho. Trocar de token nao descarta o desenho da sessao. Reiniciar descarta as edicoes nao salvas e restaura a ultima versao salva explicitamente, se houver. Limpar e apagar tambem sao temporarios ate tocar em **SAVE**: salve um desenho vazio para remover a versao armazenada.

Onde o **SAVE** grava depende de **SAVE DOODLES TO**:

| Opcao | Onde | Observacoes |
| --- | --- | --- |
| `RAM` | Em lugar nenhum | Os desenhos duram ate a placa reiniciar; o **SAVE** so explica isso |
| `FLASH` (padrao) | Particao `spiffs` de 768 KiB, LittleFS | Nao precisa de cartao |
| `SD CARD` | Pasta `/doodles` no microSD | O cartao precisa estar no slot quando a placa liga |

Trocar essa opcao rele os desenhos salvos do novo lugar; a tinta nao salva da sessao continua na tela e pode ser salva la.

No primeiro salvamento na flash, se o armazenamento dos desenhos nao estiver montado, o firmware pede confirmacao antes de inicializa-lo. **INIT formata apenas a particao separada de 768 KiB dos desenhos** (chamada `spiffs`, usada aqui com LittleFS), nunca a NVS dos tokens ou o microSD. Cancele para continuar desenhando temporariamente. Se um sistema de arquivos que ja funcionava ficar indisponivel, inicializa-lo apagara os desenhos daquela particao: cancele se precisar recupera-los. Um arquivo de desenho danificado gera um aviso em vez de ser sobrescrito silenciosamente; use **CLEAR** para substitui-lo explicitamente.

Os desenhos usam tracos compactos, nao bitmaps de tela inteira. Cada token aceita ate **1.024 pontos amostrados**, com um **orcamento de 32 KiB para os buffers de pontos** compartilhado pela sessao; desenhos salvos sem alteracoes podem sair da RAM e ser relidos quando necessario, mas desenhos nao salvos nunca sao descartados silenciosamente. Desenho cheio, falta de RAM ou falha ao salvar geram uma mensagem na tela de ferramentas e no serial. Uma falha ao salvar preserva a versao armazenada anteriormente.

O desenho e reprojetado entre os layouts, mantendo os tracos da arte ancorados na arte; as proporcoes do texto e da moldura podem variar um pouco. Expansoes compativeis que apenas acrescentam entradas ao catalogo preservam os desenhos salvos. Prefixos de catalogo alterados ou reordenados nao reutilizam desenhos em outro token. Evite `uploadfs`, que substituiria o sistema de arquivos dos desenhos.

*Dica: o touch resistivo funciona com a unha, mas uma caneta facilita muito os detalhes pequenos.*

## Contadores

Toque na caixa de texto da carta (no `Custom`, na parte de baixo dela, onde ficam os selos) para abrir a tela de contadores. Cada linha tem **-** e **+**; **<** / **>** trocam de pagina e **BACK** volta para a carta.

- `+1/+1` (so em criaturas): abaixo de zero vira `-1/-1`. O total aparece na linha de status, ao lado do P/T, e ja entra no P/T exibido.
- `Custom`: um contador com nome livre, um por token. Toque no nome (o do lapis) para renomea-lo pelo teclado, com ate 10 letras.
- Marcadores comuns: Shield, Stun, Oil, Charge e Finality.
- Marcadores de habilidade (em azul): Flying, First strike, Double strike, Deathtouch, Lifelink, Trample, Vigilance, Menace, Reach, Hexproof e Indestructible.

Na carta, os contadores diferentes de +1/+1 aparecem como selos na parte de baixo da caixa de texto (nas criaturas, logo acima da linha de status). Os de habilidade so mostram o numero quando ha mais de um. Se nao couberem todos, os nomes viram abreviacoes e o que sobrar aparece como `+N`.

### Food de Ygra

Nas criaturas, a ultima linha da tela de contadores e `Food (Ygra)`. **+** ativa e **-** remove a marca (0/1). Ela vale para todas as copias daquele token, inclusive copias adicionadas depois, ate voce remove-la. Nao cria um token Food separado e nao remove os tipos originais.

A criatura marcada ganha `Artifact` e `Food` na linha de tipo e um selo `Food (Ygra)`. Passa a contar uma vez para bonus que contam artefatos/Foods (por exemplo, Construct) e tambem aparece nessas buscas. A marca fica salva depois de reiniciar. Remova-a quando o efeito de Ygra deixar de valer. O custo de Food (`2, T, sacrificar: ganhar 3 de vida`) e as acoes de sacrificar/ganhar vida ainda sao executados manualmente na partida; o painel de tokens nao se liga ao contador de vida, entao ajuste a vida la manualmente.

## Bonus automaticos e limites das regras

Tokens com texto do tipo "gets +1/+1 for each [other] TIPO you control" tem o P/T calculado sozinho, contando os tokens daquele tipo em jogo em todo o rastreador (pela linha de tipo de cada token):

- `Rat (Vren)`: +1/+1 para cada *outro* Rat (os Rats do Vren e os Rats comuns).
- `Construct`: +1/+1 para cada artefato, incluindo ele mesmo (Treasure, Clue, Food etc. contam).

O bonus atual aparece como um selo verde (ex.: `Rats +4/+4`) e ja entra no P/T. Para permanentes que nao sao tokens (o proprio Vren, artefatos de verdade), use a linha `Rat cards` / `Artifact cards` na tela de contadores desse token. Com quantidade 0, o P/T mostrado e o que o token teria ao entrar. Habilidades de Roles e auras nao sao calculadas. O `Custom` tambem e lido, entao uma criatura personalizada com esse texto funciona igual.

> **Um companheiro de mesa, nao um motor completo de regras.** Os tokens Cat/Dog de Rin and Seri e Cragflame de Mabel estao no catalogo, mas habilidades desencadeadas, equipar, sacrificar, mudancas de vida vindas de efeitos de tokens e outras zonas do jogo ainda dependem do jogador. A marca de Ygra e manual: ela nao detecta a entrada ou saida de Ygra do campo.

## Arte

Cada token mostra a ilustracao da sua impressao no Scryfall, com o nome do ilustrador no rodape da carta. A arte e gerada por `tools/fetch_tokens.py` em `src/token_art_generated.h` (ate 2,5 MB) e fica fora do controle de versao, por ser propriedade da Wizards of the Coast. Sem esse arquivo o firmware compila igual, com as cores da moldura no lugar da arte.

Para caber na flash com mais de 450 tokens, cada token guarda uma unica JPEG, no tamanho da arte dos layouts de tela cheia (214x128, cor em 4:2:0). O layout Classic reduz essa imagem na propria placa para 164x96. O gerador baixa a qualidade JPEG de 5 em 5 so ate tudo caber; a qualidade usada fica anotada no topo de `src/token_art_generated.h`. A qualidade original (85) para todos os tokens precisaria de 4 a 8 MB, mais do que a flash de 4 MB da placa.

O script ajusta as imagens para a tela: recorta para a caixa da arte e escurece os tons medios das artes muito claras (`ART_MAX_MEAN`), que estouram no painel TN do CYD. As cores desse painel tambem mudam bastante com o angulo de visao: com a placa deitada na mesa a carta fica lavada, e as cartas brancas estouram. Por isso a moldura branca e um creme (e nao o branco mais claro que o painel mostra) e ha **CARD TONE** (no **CARD OPTIONS** do menu de tokens) e **SCREEN** (na primeira pagina do **SETTINGS**). Se todas as cores (e nao so as claras) parecem estouradas, veja **DISPLAY GAMMA**, na segunda pagina do **SETTINGS**. A aplicacao tem uma particao de 3 MiB em [partitions.csv](partitions.csv); as artes deixam a gravacao maior e mais demorada.

### Arte em alta qualidade no microSD

O gerador tambem grava a arte de todos os tokens em **JPEG qualidade 90, cor 4:4:4** em `sdcard/mtgart`, nos dois tamanhos. O Classic usa uma imagem no tamanho nativo em vez de reduzir a versao de tela cheia.

1. [Gere o catalogo e as artes](#regenerar-o-catalogo-e-as-artes).
2. Formate um microSD em **FAT32**.
3. Copie a **pasta `mtgart` inteira** para a raiz do cartao, mantendo esta estrutura:

   ```text
   /mtgart/
     catalog.txt
     artists.txt
     full/
       0001.jpg      # 214 x 128
       ...
     classic/
       0001.jpg      # 164 x 96
       ...
   ```

4. Insira o cartao no CYD e **reinicie**. A deteccao do cartao e a validacao do catalogo acontecem ao ligar; as imagens sao lidas sob demanda. Nao ha suporte a troca do cartao com a placa ligada.

| Indicador nas configuracoes | Significado / acao |
| --- | --- |
| `SD HD ART` | Arte do SD compativel disponivel; imagens individuais ausentes usam a flash |
| `SD: NO ART` | Cartao montado, mas o arquivo de catalogo das artes esta ausente ou ilegivel; copie a pasta |
| `SD: OLD ART` | ID de catalogo diferente; gere de novo e substitua a pasta inteira |
| Sem indicador | Nenhum cartao montado; usa a arte embutida |

**O cartao nao e obrigatorio.** Se uma imagem do SD nao puder ser aberta, o firmware usa a arte embutida ou, se ela tambem nao existir, um fundo colorido. Os arquivos gerados em `sdcard/` ficam fora do controle de versao. Use `--no-sd-art` para nao gera-los.

*A leitura de arte do microSD so foi testada fora da placa ate agora; abra uma issue se nao funcionar na sua.*

Quantidades, marcadores, modificadores e o token selecionado ficam salvos na flash (NVS) e sao restaurados ao religar a placa.

## Ferramentas de mesa

Decks e precons fazem parte do modo de tokens: abra pelo menu de tokens (**DECKS / PRECONS**) ou com **DECKS** na lista de tokens. O contador de vida e os dados tem entradas proprias no menu principal.

### Decks de tokens

- **DECKS** oferece ate **oito decks com nome**, alem de **ALL TOKENS**. Toque numa linha para ativa-la; **BACK** volta para a carta com esse deck.
- **NEW** abre a [lista de precons](#decks-de-precon) para importar um deck; o botao **EMPTY** dela cria um deck vazio e abre o teclado de nome. **NAME** renomeia o deck ativo.
- **EDIT** abre o catalogo completo. Toque nos tokens para incluir ou remover (`YES` indica incluido); **FIND** pesquisa o catalogo completo durante a edicao. **BACK** volta aos decks.
- **DEL** pede confirmacao e remove somente o filtro daquele deck.
- Fora da edicao, a navegacao, os resultados da busca e o indicador de posicao respeitam o deck ativo. Um deck vazio volta ao gerenciamento em vez de mostrar um token de fora dele.
- Artes, quantidades, copias viradas, marcadores e o token personalizado continuam compartilhados. Um token pode estar em varios decks. Os decks e o filtro ativo sao sempre salvos.

### Decks de precon

- **NEW** em **DECKS** lista os **198 precons de Commander** da snapshot do catalogo, do mais novo ao mais antigo, com codigo do set, ano e quantidade de tokens. **< / >** mudam de pagina; **FIND** pesquisa por nome, codigo do set ou ano (por exemplo `BLC`, `2024 dragons`). **EMPTY** cria um deck vazio em vez disso, e **BACK** volta aos decks.
- Toque num precon para **importa-lo** num slot livre e ativa-lo. Precons que ja estao num slot aparecem destacados; importar de novo atualiza esse slot. O **NEW** precisa de um slot livre: se os oito estiverem ocupados, apague um com **DEL** antes.
- Um precon importado e um deck normal: pode ser renomeado, ajustado com **EDIT** ou apagado. Nomes com mais de 24 caracteres sao encurtados.
- A lista traz os tokens que o Scryfall liga as cartas de cada decklist. Efeitos que apenas copiam permanentes, ou que criam tokens sem carta ligada, podem precisar de **EDIT**.

### Vida e dano de comandante

Abra **LIFE COUNTER** no menu principal. Cada um dos **1 a 8 jogadores** ganha um painel colorido virado para o seu lugar em volta do aparelho: o primeiro embaixo (ou embaixo a esquerda) e os demais em sentido horario, subindo pela esquerda e descendo pela direita; com dois jogadores, o segundo painel fica virado para cima.

- Toque na **metade esquerda** de um painel para **-1** e na **metade direita** para **+1**. Segure para repetir; depois de algumas repeticoes o passo vira **10**. Uma bolha amarela mostra a variacao acumulada (`+3`, `-7`) e some cerca de 2,5 segundos apos o ultimo toque.
- O painel escurece e o numero fica vermelho claro quando o jogador esta com **0 ou menos** ou levou **21** de um mesmo comandante.
- O **botao redondo** no meio abre **DICE / COIN**, **WHO STARTS?** (um destaque gira pela mesa, desacelera e para num jogador aleatorio, marcado com `FIRST`; o proximo toque limpa), **NEW GAME**, **SAVE MATCH: ON / OFF**, **MAIN MENU** e **CLOSE**. Toque fora do menu para fecha-lo.

**NEW GAME** escolhe o numero de jogadores e a vida inicial, com atalhos **20 / 25 / 30 / 40** e ajuste fino de **1 a 9999**. **START** pede confirmacao antes de restaurar a vida inicial e zerar o dano de comandante; nao altera os tokens. O numero de jogadores e a vida inicial escolhidos ficam salvos mesmo com a restauracao da partida desligada.

A faixa na base de cada painel mostra `P1` a `P8` e uma pilula **CMD** com o maior dano que esse jogador levou de um unico comandante. **Toque na faixa** para registrar dano de comandante **recebido** por esse jogador: os outros paineis escurecem e mostram quanto cada um causou (`TO P2`); as metades **+ / -** deles somam ou tiram esse dano, o que tambem ajusta a vida de quem recebe. Toque na faixa de uma origem para alternar entre **C1** e **C2** (parceiros); os danos dos parceiros nunca sao somados para o limite de 21. Toque no painel de quem recebe (`DONE`) ou no botao de confirmacao no meio para voltar. A vida aceita **-9999 a 9999**, e cada registro de dano de comandante aceita **0 a 999**. E um controle manual, nao um motor de regras nem uma eliminacao automatica.

**SAVE MATCH: OFF / ON**, no menu da vida, decide se vida e dano de comandante voltam depois de reiniciar; o menu continua aberto para mostrar o novo estado. O padrao e **OFF**. Ativar **ON** salva a partida atual imediatamente; as proximas alteracoes sao salvas apos 1,5 segundo sem edicoes. Voltar para **OFF** remove a partida salva imediatamente, mas mantem a partida atual na RAM; ao reiniciar, comeca uma partida nova usando os padroes salvos de jogadores e vida inicial. Os decks e os saves existentes dos tokens independem dessa opcao. Aguarde pelo menos 1,5 segundo apos editar antes de desligar; erros de armazenamento aparecem no cabecalho das telas de mesa e no serial.

### Dados e moeda

**DICE / COIN** (no menu principal e no menu da vida) oferece **COIN, d4, d6, d8, d10, d12 e d20**, com **1 a 20** lancamentos por vez. **ROLL** (ou **FLIP** para moedas), ou um toque na area de resultados, lanca os dados em 3D por cerca de um segundo: cada dado entra voando, faz um arco em sua direcao com uma sombra que cresce, quica uma vez e gira ate parar no resultado. Os dados sao poliedros reais com sombreamento (tetraedro no d4, cubo com pontos no d6 e faces opostas somando 7, octaedro no d8, faces em pipa no d10, dodecaedro no d12, icosaedro no d20) iluminados pelo canto superior esquerdo; as moedas giram de ponta a ponta mostrando a borda e caem com cara dourada ou coroa prateada. A soma ou a contagem de caras/coroas aparece acima. Os resultados continuam visiveis durante a sessao, identificados pelo tipo e quantidade efetivamente lancados, mesmo que voce altere as opcoes da proxima rolagem. Nao sao restaurados depois de reiniciar. **BACK** volta para onde os dados foram abertos: o menu principal ou o contador de vida. As rolagens usam o gerador aleatorio do ESP32 com amostragem por rejeicao para evitar vies de modulo.

## Configuracoes

Ha duas telas de configuracao, cada uma com **<** / **>** para trocar de pagina e **BACK** para sair:

- **SETTINGS**, no menu principal, guarda o que vale para o aparelho todo: brilho, tempo para apagar, orientacao e gama (duas paginas). **BACK** volta ao menu principal.
- **CARD OPTIONS**, no menu de tokens, guarda o que so afeta a carta do token: layout, tom da carta e desenhos (tres paginas). **BACK** volta para a carta.

| Settings 1/2 | Settings 2/2 | Card options 2/3 | Card options 3/3 |
| :---: | :---: | :---: | :---: |
| <img src="docs/screenshots/settings.png" alt="Settings pagina 1: barras de brilho, desligamento da tela e orientacao" width="170"> | <img src="docs/screenshots/settings-gamma.png" alt="Settings pagina 2: perfil de gama com escalas de cinza e RGB" width="170"> | <img src="docs/screenshots/card-tone.png" alt="Card options pagina 2: tom da carta com miniatura de previa" width="170"> | <img src="docs/screenshots/card-doodles.png" alt="Card options pagina 3: area do desenho, como comecar a desenhar e onde salvar" width="170"> |

### Pagina 1: brilho, tempo e tela

- **BRIGHTNESS**: 10 niveis de brilho, de 10% a 100%. Use **-** / **+** ou toque nas barras para ir direto a um nivel.
- **SCREEN OFF AFTER**: tempo sem toque ate apagar a tela: 15 s, 30 s, 1, 2, 5 ou 10 min, ou `Never` (o padrao). O toque que acorda a tela so a acende e nao aciona nenhum botao.
- **SCREEN**: `NORMAL` ou `FLIPPED`, que gira a tela 180 graus (o touch acompanha). O painel TN fica bem melhor visto de um lado do que do outro; na mesa, teste as duas posicoes girando a placa.

### Pagina 2: gama da tela

Para quando todas as cores parecem lavadas ou estouradas, nao so as claras:

- **DISPLAY GAMMA**: programa a curva de gama do painel. Esta placa precisa de inversao de cores (`TFT_INVERSION_ON`) e costuma sair da inicializacao com a gama errada, o que deixa tudo mais claro e sem contraste. **-** / **+** trocam entre os perfis; o escolhido vale na hora e a cada vez que a placa liga:
  - `RECOMMENDED` (o padrao): as tabelas de gama do fabricante, com a curva selecionada de novo logo apos a tela ligar, o ajuste que a comunidade do TFT_eSPI (issue 2985) relata para esta placa.
  - `NO INVERSION`: tira a inversao de cores. Se a tela ficar em negativo, volte para o perfil 1/3.
  - `ST7789 GAMMA`: as tabelas de gama do ST7789, que alguns paineis clones usam.
- **TEST RAMPS**: degrades de cinza, vermelho, verde e azul, do preto ao pleno, direto do painel e sem o **CARD TONE**. Num painel bem ajustado cada degrau e diferente do vizinho e os primeiros sao escuros; se os degraus claros se confundem ou os escuros ja saem acinzentados, teste outro perfil. Depois de acertar a gama, ajuste o **CARD TONE** e o **BRIGHTNESS** se ainda for preciso.

### Card options pagina 1: layout

- **LAYOUT**: toque numa das miniaturas.
  - **Classic**: a carta com a barra de botoes embaixo, o icone de menu no canto esquerdo e a lupa no direito (o padrao).
  - **Overlay**: a carta ocupa a tela inteira e os controles ficam sobre a arte: `<`, icone de menu, lupa e `>` no topo, botoes grandes **-** / **+** ao lado do numero e, embaixo dele, o seletor de modo (`QTY`, `TAP`, `POW`, `TGH`).
  - **Card only**: como o Overlay, mas os controles somem depois de 4 s sem toque e sobra so a carta. O primeiro toque traz os controles de volta sem acionar nada.

Nos layouts de tela cheia, tocar na arte ainda vira os tokens e tocar na barra do nome ainda abre a lista.

### Card options pagina 2: tom da carta

Para quando a carta parece clara, lavada ou estourada, como com a placa deitada na mesa:

- **CARD TONE**: escurece a carta inteira (arte, moldura, caixas de texto e o icone de mana) e abaixa o ponto branco, para que o branco nao estoure: `ORIGINAL` (o padrao) e `DARKER 1` a `DARKER 5`. A previa entre **-** e **+** e uma carta em miniatura do token atual com o tom escolhido (no `Custom`, uma escala de cinza). Vale para a carta e para as miniaturas de layout, mas nao para o resto da interface. Se o branco ainda incomodar, diminua tambem o **BRIGHTNESS** ou teste o **SCREEN** em **SETTINGS**.

### Card options pagina 3: desenhos

Veja [Modo de desenho](#modo-de-desenho).

- **DOODLE AREA**: `ART ONLY` deixa a tinta so na arte; `WHOLE CARD` (o padrao) libera tambem nome, moldura e texto. O que foi desenhado fora da arte e mantido enquanto `ART ONLY` o esconde.
- **START DRAWING WITH**: `BUTTON` (o botao **DRAW** da pagina de contadores), `HOLD ART` (segurar a arte por cerca de um segundo) ou `BOTH` (o padrao). Com uma opcao de segurar, tocar na arte vira os tokens quando voce levanta o dedo, e nao quando encosta.
- **SAVE DOODLES TO**: `RAM` (nada e salvo), `FLASH` (o padrao) ou `SD CARD` (`/doodles` no microSD). A dica embaixo avisa quando nenhum cartao foi encontrado ao ligar.

As configuracoes ficam salvas na flash (NVS), separadas dos tokens, e continuam valendo quando o catalogo muda.

## Busca

A lupa ou o botao **FIND** da lista de tokens abre um teclado na tela. Digite e confirme com **OK** para listar so os tokens que combinam:

- Nao diferencia maiusculas de minusculas e basta o trecho aparecer (`gob` acha o Goblin).
- Com varias palavras separadas por espaco, todas precisam combinar, em qualquer ordem (`green 3/3` acha os tokens verdes 3/3).
- Cada palavra e procurada no nome, na linha de tipo, no texto, no nome da cor (`white`, `blue`, `black`, `red`, `green`, `multicolor`, `colorless`) e no P/T (`3/3`).
- **FIND** na lista refina a busca mantendo o texto digitado; **BACK** no teclado cancela. Tocar na barra do nome na carta sempre abre a lista completa, e **<** / **>** na carta continuam passando por todos os tokens.

<img src="docs/screenshots/search.png" alt="Teclado de busca com white flying digitado e 20 resultados" width="200"> <img src="docs/screenshots/search-results.png" alt="Lista de resultados da busca white flying" width="200">

## Solucao de problemas

| Sintoma | O que conferir |
| --- | --- |
| Gravacao nao consegue abrir a porta | Confira o cabo USB de dados, a porta da placa e a configuracao COM7; feche outros monitores seriais |
| Token sem ilustracao | Esperado ao baixar o repositorio; gere as artes antes de compilar ou prepare a pasta do microSD |
| Arte do SD ignorada | Confira FAT32, `/mtgart/catalog.txt`, o indicador nas configuracoes e reinicie depois de inserir o cartao |
| Desenho desaparece ao reiniciar | So **SAVE** persiste o desenho; **BACK** o mantem apenas na sessao atual. Com **SAVE DOODLES TO** em `RAM` nada e mantido |
| Toque na arte parece atrasado | Com uma opcao de segurar em **START DRAWING WITH**, o toque conta quando voce levanta o dedo; escolha `BUTTON` para toques instantaneos |
| Desenhos no microSD nao aparecem | O cartao precisa estar inserido antes de ligar a placa; os desenhos ficam em `/doodles` |
| Falha ao salvar ou ler um desenho | Leia a mensagem nas ferramentas e no serial; nao inicialize armazenamento existente sem aceitar apagar os desenhos salvos |
| Cores lavadas | Teste **DISPLAY GAMMA** primeiro, depois **CARD TONE**, brilho e orientacao da tela |
| Toques fora da posicao | Confira a revisao da placa e a calibracao abaixo |

### Ajuste do touch

Os limites iniciais em `src/main.cpp` sao aproximados. Se os botoes responderem em posicoes erradas, calibre `TOUCH_X_MIN`, `TOUCH_X_MAX`, `TOUCH_Y_MIN` e `TOUCH_Y_MAX`. Se os eixos estiverem trocados, ajuste a conversao de `point.x` e `point.y` em `handleTouch()`.

## Catalogo de tokens

Os tokens vem de `src/tokens_generated.h`, gerado a partir da API do Scryfall. Nao edite esse arquivo a mao. O gerador preserva os staples de `SPECS` em `tools/fetch_tokens.py` no inicio e acrescenta os tokens dos precons:

- Descobre os decks fisicos `Commander Deck` no MTGJSON, incluindo Secret Lair, ate a data escolhida.
- Consulta os sets de tokens correspondentes no Scryfall e os tokens ligados a cada carta das listas dos decks. Isso tambem cobre Commander 2011/2013 e outros produtos sem set de tokens proprio.
- Junta impressoes com o mesmo nome, tipos, cores, P/T e texto de regras; variantes diferentes permanecem separadas. Sets compartilhados podem acrescentar tokens alem dos usados pelos decks.
- Rin and Seri tem `Cat (Rin and Seri)` **verde 1/1** e `Dog (Rin and Seri)` **branco 1/1**. O Cat branco que ja existia continua separado. `Cragflame (Mabel)` e o token lendario de Equipment.
- Emblemas tambem entram quando disponiveis. Nao e uma lista de todas as artes alternativas, nem um motor que executa todas as habilidades de Magic.

A mesma execucao grava `src/precons_generated.h`: nome, codigo do set, ano e tokens do catalogo de cada precon, usados na lista de precons (**DECKS → NEW**). Edicoes de colecionador reaproveitam a lista de tokens do deck normal. O `PRECON_CATALOG_ID` precisa ser igual ao `CATALOG_ID`, entao a compilacao falha se so um dos dois arquivos for atualizado.

### Regenerar o catalogo e as artes

Execute na raiz do projeto. Precisa de internet; as imagens precisam do Pillow. Estes comandos usam o Python do PlatformIO no Prompt de Comando do Windows:

```bat
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" -m pip install pillow
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" tools\fetch_tokens.py --as-of 2026-10-24
```

Em outras plataformas, use `python -m pip install pillow` e `python tools/fetch_tokens.py --as-of 2026-10-24` no seu ambiente Python.

| Opcao | Finalidade |
| --- | --- |
| `--as-of YYYY-MM-DD` | Limitar a data de lancamento dos precons; o padrao e hoje. A snapshot incluida usa `2026-10-24` |
| `--refresh` | Atualizar as respostas de API em cache |
| `--no-art` | Gerar apenas o catalogo e os decks de precon |
| `--no-sd-art` | Gerar catalogo e arte embutida, sem a pasta do microSD |

Os dados de API ficam em `tools/catalog_cache`; as imagens baixadas sao reutilizadas de `tools/art_cache`. Sem Pillow, so o catalogo e gerado. O gerador percorre todas as paginas e falha explicitamente se nao conseguir resolver uma entrada obrigatoria. A qualidade JPEG so e reduzida para a arte embutida caber na flash; no SD continua em 90. As curvas de cor/tom e o gamma do painel nao mudam. Recompile e grave depois de regenerar a arte embutida; se o catalogo mudou, substitua tambem a pasta do SD.

### Adicionar uma entrada

Para adicionar um token, acrescente uma tupla em `SPECS` no formato `(nome, cores, poder, resistencia, texto[, rotulo])` e rode o script de novo:

- `cores`: letras `w`, `u`, `b`, `r`, `g` ou `c` (incolor).
- `poder`: `None` para tokens sem P/T, como artefatos.
- `texto`: `""` exige um token sem texto, uma string exige que ela apareca no texto e `None` aceita qualquer um.
- `rotulo`: nome exibido na lista quando dois tokens teriam o mesmo nome, como `Wurm (Deathtouch)` e `Wurm (Lifelink)`.

### Testes offline

As regras de mesa podem ser testadas no PC com um compilador C++11 nativo (nao o compilador cruzado do ESP32). Por exemplo, com GCC no Prompt de Comando do Windows:

```bat
g++ -std=c++11 -Wall -Wextra -Werror tools\test_table_state.cpp -o "%TEMP%\test_table_state.exe"
"%TEMP%\test_table_state.exe"
```

Os testes cobrem inclusao de tokens e navegacao circular dos decks, os oito jogadores e seus dois comandantes, ajustes e limites de vida, o limite de 21 por comandante, validacao do formato salvo e faixas/rejeicao dos dados.

Testes do gerador do catalogo:

```bat
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" -m unittest tools.test_fetch_tokens
```

### Conferencia de cobertura dos precons

[tools/check_precon_coverage.py](tools/check_precon_coverage.py) confere o catalogo por um caminho independente das listas do MTGJSON. Ele parte da lista de produtos Commander do proprio Scryfall (sets do tipo `commander` e produtos com "Commander" no nome), percorre todas as cartas impressas neles e verifica se cada token que elas criam (e cada token dos sets de tokens desses produtos) esta no catalogo. Tambem lista os decks com cara de Commander fora do tipo `Commander Deck` e os produtos sem decklist. Sai com erro se faltar algum token criado por uma carta de precon. Precisa de internet.

```bat
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" tools\check_precon_coverage.py --as-of 2026-10-24
```

<details>
<summary>Resultado da conferencia: snapshot de 24/10/2026</summary>

Resultado da snapshot de 2026-10-24:

- 198 decklists `Commander Deck` do MTGJSON, todas completas (100 cartas). 47 dos 52 produtos Commander do Scryfall tem decklist. Os 5 sem decklist nao sao precons: Commander's Arsenal, Commander Collection Green/Black, os minigames de Baldur's Gate e Mystery Booster Commander Edition. Fora do tipo `Commander Deck` so ha produtos digitais (MTGO 2009, Historic Brawl do Arena), caixas de colecao e decks Starter antigos.
- 21.807 impressoes em 54 sets, 1.187 tokens ligados e 46 sets de tokens; 460 faces de token distintas.
- **0 tokens faltando entre os criados por cartas de precon.** Os 29 tokens fora do catalogo vem so de cartas que nao estao em nenhum precon: drops de Secret Lair, Mystery Booster Commander e extras de collector booster (Legends Retold do DMC, Realms and Relics do LTC, cartas extras do Marvel/Final Fantasy/TMNT Eternal).
- Designacoes de jogo (Dungeon, Monarch/Initiative, Ring, Boss, Event, contadores de Experience/Poison) nao viram tokens, porque nao sao permanentes.

</details>

### Atualizar as capturas de tela

As imagens em `docs/screenshots` sao capturadas de uma placa real. O build `shots` adiciona comandos seriais que copiam a tela e simulam toques, e deixa de fora a arte embutida:

```bat
"%USERPROFILE%\.platformio\penv\Scripts\pio.exe" run -e shots -t upload
"%USERPROFILE%\.platformio\penv\Scripts\python.exe" tools\screenshot.py COM7 shot home tap 120 102 wait 800 shot token-card
"%USERPROFILE%\.platformio\penv\Scripts\pio.exe" run -e esp32dev -t upload
```

Os passos sao `tap X Y`, `hold X Y MS`, `path X,Y X,Y ... end` (arrastar), `wait MS` e `shot NOME` (salva `docs/screenshots/NOME.png`). As coordenadas sao pixels da tela em retrato (240x320). A captura le a memoria do display, entao os PNGs saem com as cores certas mesmo com a inversao de cores deste painel. Grave o `esp32dev` de novo no final; o build `shots` e so para desenvolvimento.

## Saves e atualizacoes do firmware

O arquivo gerado inclui um `CATALOG_ID` e os CRCs dos prefixos da lista. Se a expansao mantiver todas as entradas antigas na mesma ordem, quantidades, selecao, contadores, nomes e cartas externas sao preservados. Catalogos incompativeis descartam apenas o estado dos tokens, com aviso no serial; `Custom` e configuracoes continuam preservados.

`partitions.csv` mantem os offsets da aplicacao e da NVS antiga e reserva uma NVS `tokenstore` de 128 KiB para o catalogo ampliado. O firmware migra os saves antigos automaticamente, sem apagar a NVS original. Grave normalmente com PlatformIO para atualizar tambem a tabela de particoes; nao use `erase_flash` para esta atualizacao.

As ferramentas de mesa usam um namespace `table` separado na `tokenstore`, sem mudar o formato dos saves de tokens. Os filtros dos decks sobrevivem a expansoes compativeis do catalogo. Se a ordem dos tokens mudar de forma incompativel, os nomes dos decks continuam, mas as listas sao limpas com aviso para nao apontar para tokens errados.

Com **SAVE DOODLES TO** em `FLASH`, os desenhos salvos sao arquivos LittleFS separados na particao `spiffs` ja existente, nao fazem parte da NVS dos tokens. A gravacao normal do firmware preserva essa particao; `uploadfs`, a inicializacao explicita do armazenamento de desenhos ou apagar toda a flash nao preservam. Com `SD CARD`, sao arquivos em `/doodles` no microSD, nomeados pelo ID do prefixo do catalogo e pela posicao (`dXXXXXXXX-NNNN.bin`).

## Creditos

Os dados do catalogo e as referencias das imagens vem do [Scryfall](https://scryfall.com/) e do [MTGJSON](https://mtgjson.com/). O firmware usa [TFT_eSPI](https://github.com/Bodmer/TFT_eSPI), [XPT2046_Touchscreen](https://github.com/PaulStoffregen/XPT2046_Touchscreen) e [JPEGDEC](https://github.com/bitbank2/JPEGDEC).

Magic: The Gathering e as artes das cartas pertencem a Wizards of the Coast e aos respectivos detentores dos direitos. Este e um projeto de fa, nao oficial, sem afiliacao ou endosso da Wizards of the Coast. As artes baixadas nao sao distribuidas neste repositorio.