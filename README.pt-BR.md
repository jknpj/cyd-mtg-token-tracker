# Tokens de MTG no CYD 2,8"

**Português (Brasil)** | [English](README.md)

Firmware offline para navegar por 455 entradas de tokens/emblemas de MTG (mais `Custom`) e ajustar a quantidade em jogo usando o touch. O catalogo cobre os 198 precons de Commander listados nas fontes ate 24/10/2026, incluindo os staples, Cat/Dog de Rin and Seri e Cragflame de Mabel. Tem tres layouts de tela, brilho e desligamento automatico da tela ajustaveis e busca de tokens.

## Placa assumida

Este projeto assume o CYD ESP32-2432S028R, com tela ILI9341 e touch resistivo XPT2046. A pinagem configurada e a comum nessa variante:

- Tela (HSPI): SCLK 14, MISO 12, MOSI 13, CS 15, DC 2, backlight 21 (PWM)
- Touch (VSPI, barramento proprio): SCLK 25, MISO 39, MOSI 32, CS 33, IRQ 36

Outras revisoes do CYD podem usar outro controlador ou pinagem. Confirme a identificacao impressa na placa antes de gravar.

O brilho e ajustado por PWM (LEDC) direto no pino do backlight, `BACKLIGHT_PIN` em `src/main.cpp`. Por isso `platformio.ini` nao define `TFT_BL`: a biblioteca TFT_eSPI nao deve controlar esse pino.

## Compilar e gravar

1. Abra esta pasta no VS Code com a extensao PlatformIO instalada.
2. Use **PlatformIO: Build** para compilar.
3. Conecte a placa por USB e use **PlatformIO: Upload** para gravar.
4. Abra o monitor serial em 115200 baud se quiser acompanhar a inicializacao.

O token aparece como uma carta em modo retrato. No layout **Classic** (o padrao) ha uma barra inferior com estes botoes:

- **<** / **>**: token anterior / proximo.
- Botao central: alterna o que **-** e **+** editam: `QTY` (quantidade em jogo), `TAP` (quantos estao virados), `POW` e `TGH` (modificadores de poder/resistencia, so em criaturas). O item em edicao fica destacado em amarelo na carta (P/T ou icone de virados); a quantidade nao tem destaque, para nao emoldurar a arte, e o modo atual aparece escrito no botao. Os marcadores (+1/+1 e os demais) ficam na tela de **contadores**, abaixo.
- Tocar na area da arte vira todos os tokens desvirados ou, se ja estiverem todos virados, desvira todos.
- Tocar na barra do nome abre a lista de tokens, em paginas. Toque num nome para seleciona-lo; **<** / **>** trocam de pagina, **FIND** abre a busca, **BACK** volta para a carta e **SET** abre as configuracoes.
- A engrenagem, na margem superior esquerda ao lado da carta, abre as **configuracoes** e a lupa, na margem superior direita, abre a **busca**. Nos outros layouts os dois icones ficam entre os botoes sobre a arte.

Na arte, "IN PLAY", a quantidade e os icones de desvirado e virado so aparecem quando ha mais de um token daquele tipo em jogo; com 0 ou 1, a quantidade aparece por 2 segundos depois de ser ajustada e some em seguida, deixando a arte limpa. Ao remover tokens, os desvirados saem primeiro. O indicador de posicao (por exemplo, `1/76`) aparece brevemente ao trocar de token e depois some. O icone de mana no canto do nome indica a cor: sol (branco), gota (azul), caveira (preto), chama (vermelho), arvore (verde), roda de cinco pontos coloridos (multicolor) e losango (incolor). Os mesmos icones aparecem na lista e no seletor de cor do editor.

O primeiro item da lista, `Custom`, e um token editavel: com ele selecionado, toque na parte de baixo da carta (tipo e texto) para abrir o editor de nome, linha de tipo, texto, cor e P/T. Os campos de texto usam um teclado na tela, e **SAVE** grava o token na flash.

O P/T exibido ja soma os marcadores e os modificadores. Tokens sem P/T (artefatos) editam apenas quantidade e tapped.

Tokens com P/T variavel preservam os simbolos impressos (`*/*`, `*/1+*` etc.), em vez de fingir que sao 0/0. Seus modificadores aparecem junto do simbolo; o rastreador nao conhece zonas como cemiterios ou a vida dos jogadores para resolver essas habilidades sozinho. Cragflame e um Equipment: seu texto aparece na carta, mas equipar e aplicar seu bonus a outra criatura continuam sendo acoes manuais.

## Contadores

Toque na caixa de texto da carta (no `Custom`, na parte de baixo dela, onde ficam os selos) para abrir a tela de contadores. Cada linha tem **-** e **+**; **<** / **>** trocam de pagina e **BACK** volta para a carta.

- `+1/+1` (so em criaturas): abaixo de zero vira `-1/-1`. O total aparece na linha de status, ao lado do P/T, e ja entra no P/T exibido.
- `Custom`: um contador com nome livre, um por token. Toque no nome (o do lapis) para renomea-lo pelo teclado, com ate 10 letras.
- Marcadores comuns: Shield, Stun, Oil, Charge e Finality.
- Marcadores de habilidade (em azul): Flying, First strike, Double strike, Deathtouch, Lifelink, Trample, Vigilance, Menace, Reach, Hexproof e Indestructible.

Na carta, os contadores diferentes de +1/+1 aparecem como selos na parte de baixo da caixa de texto (nas criaturas, logo acima da linha de status). Os de habilidade so mostram o numero quando ha mais de um. Se nao couberem todos, os nomes viram abreviacoes e o que sobrar aparece como `+N`.

### Food de Ygra

Nas criaturas, a ultima linha da tela de contadores e `Food (Ygra)`. **+** ativa e **-** remove a marca (0/1). Ela vale para todas as copias daquele token, inclusive copias adicionadas depois, ate voce remove-la. Nao cria um token Food separado e nao remove os tipos originais.

A criatura marcada ganha `Artifact` e `Food` na linha de tipo e um selo `Food (Ygra)`. Passa a contar uma vez para bonus que contam artefatos/Foods (por exemplo, Construct) e tambem aparece nessas buscas. A marca fica salva depois de reiniciar. Remova-a quando o efeito de Ygra deixar de valer. O custo de Food (`2, T, sacrificar: ganhar 3 de vida`) e as acoes de sacrificar/ganhar vida ainda sao executados manualmente na partida; o rastreador nao controla a vida.

## Habilidades "para cada"

Tokens com texto do tipo "gets +1/+1 for each [other] TIPO you control" tem o P/T calculado sozinho, contando os tokens daquele tipo em jogo em todo o rastreador (pela linha de tipo de cada token):

- `Rat (Vren)`: +1/+1 para cada *outro* Rat (os Rats do Vren e os Rats comuns).
- `Construct`: +1/+1 para cada artefato, incluindo ele mesmo (Treasure, Clue, Food etc. contam).

O bonus atual aparece como um selo verde (ex.: `Rats +4/+4`) e ja entra no P/T. Para permanentes que nao sao tokens (o proprio Vren, artefatos de verdade), use a linha `Rat cards` / `Artifact cards` na tela de contadores desse token. Com quantidade 0, o P/T mostrado e o que o token teria ao entrar. Habilidades de Roles e auras nao sao calculadas. O `Custom` tambem e lido, entao uma criatura personalizada com esse texto funciona igual.

## Arte

Cada token mostra a ilustracao da sua impressao no Scryfall, com o nome do ilustrador no rodape da carta. A arte e gerada por `tools/fetch_tokens.py` em `src/token_art_generated.h` (ate 2,5 MB) e fica fora do controle de versao, por ser propriedade da Wizards of the Coast. Sem esse arquivo o firmware compila igual, com as cores da moldura no lugar da arte.

Para caber na flash com mais de 450 tokens, cada token guarda uma unica JPEG, no tamanho da arte dos layouts de tela cheia (214x128, cor em 4:2:0). O layout Classic reduz essa imagem na propria placa para 164x96. O gerador baixa a qualidade JPEG de 5 em 5 so ate tudo caber; a qualidade usada fica anotada no topo de `src/token_art_generated.h`. A qualidade original (85) para todos os tokens precisaria de 4 a 8 MB, mais do que a flash de 4 MB da placa.

O script ajusta as imagens para a tela: recorta para a caixa da arte e escurece os tons medios das artes muito claras (`ART_MAX_MEAN`), que estouram no painel TN do CYD. As cores desse painel tambem mudam bastante com o angulo de visao: com a placa deitada na mesa a carta fica lavada, e as cartas brancas estouram. Por isso a moldura branca e um creme (e nao o branco mais claro que o painel mostra) e ha **CARD TONE** e **SCREEN** na segunda pagina das configuracoes. Se todas as cores (e nao so as claras) parecem estouradas, o culpado costuma ser a gama do proprio painel: veja **DISPLAY GAMMA**, na terceira pagina. Por causa do tamanho da arte, `platformio.ini` usa a tabela de particoes `huge_app.csv`, e a gravacao demora mais.

Quantidades, marcadores, modificadores e o token selecionado ficam salvos na flash (NVS) e sao restaurados ao religar a placa.

## Configuracoes

A engrenagem (ou o botao **SET** da lista de tokens) abre a tela de configuracoes. Ela tem tres paginas; **<** / **>** trocam de pagina e **BACK** volta.

Pagina 1:

- **BRIGHTNESS**: 10 niveis de brilho, de 10% a 100%. Use **-** / **+** ou toque nas barras para ir direto a um nivel.
- **SCREEN OFF AFTER**: tempo sem toque ate apagar a tela: 15 s, 30 s, 1, 2, 5 ou 10 min, ou `Never` (o padrao). O toque que acorda a tela so a acende e nao aciona nenhum botao.
- **LAYOUT**: toque numa das miniaturas.
  - **Classic**: a carta com a barra de botoes embaixo e a engrenagem e a lupa nos cantos (o padrao).
  - **Overlay**: a carta ocupa a tela inteira e os controles ficam sobre a arte: `<`, engrenagem, lupa e `>` no topo, botoes grandes **-** / **+** ao lado do numero e, embaixo dele, o seletor de modo (`QTY`, `TAP`, `POW`, `TGH`).
  - **Card only**: como o Overlay, mas os controles somem depois de 4 s sem toque e sobra so a carta. O primeiro toque traz os controles de volta sem acionar nada.

Nos layouts de tela cheia, tocar na arte ainda vira os tokens e tocar na barra do nome ainda abre a lista. **BACK** volta para a carta.

Pagina 2, para quando a carta parece clara, lavada ou estourada, como com a placa deitada na mesa:

- **CARD TONE**: escurece a carta inteira (arte, moldura, caixas de texto e o icone de mana) e abaixa o ponto branco, para que o branco nao estoure: `ORIGINAL` (o padrao) e `DARKER 1` a `DARKER 5`. A previa entre **-** e **+** e uma carta em miniatura do token atual com o tom escolhido (no `Custom`, uma escala de cinza). Vale para a carta e para as miniaturas de layout, mas nao para o resto da interface. Se o branco ainda incomodar, diminua tambem o **BRIGHTNESS** da pagina 1.
- **SCREEN**: `NORMAL` ou `FLIPPED`, que gira a tela 180 graus (o touch acompanha). O painel TN fica bem melhor visto de um lado do que do outro; na mesa, teste as duas posicoes girando a placa.

Pagina 3, para quando todas as cores parecem lavadas ou estouradas, nao so as claras:

- **DISPLAY GAMMA**: programa a curva de gama do painel. Esta placa precisa de inversao de cores (`TFT_INVERSION_ON`) e costuma sair da inicializacao com a gama errada, o que deixa tudo mais claro e sem contraste. **-** / **+** trocam entre os perfis; o escolhido vale na hora e a cada vez que a placa liga:
  - `RECOMMENDED` (o padrao): as tabelas de gama do fabricante, com a curva selecionada de novo logo apos a tela ligar, o ajuste que a comunidade do TFT_eSPI (issue 2985) relata para esta placa.
  - `NO INVERSION`: tira a inversao de cores. Se a tela ficar em negativo, volte para o perfil 1/3.
  - `ST7789 GAMMA`: as tabelas de gama do ST7789, que alguns paineis clones usam.
- **TEST RAMPS**: degrades de cinza, vermelho, verde e azul, do preto ao pleno, direto do painel e sem o **CARD TONE**. Num painel bem ajustado cada degrau e diferente do vizinho e os primeiros sao escuros; se os degraus claros se confundem ou os escuros ja saem acinzentados, teste outro perfil. Depois de acertar a gama, ajuste o **CARD TONE** e o **BRIGHTNESS** se ainda for preciso.

As configuracoes ficam salvas na flash (NVS), separadas dos tokens, e continuam valendo quando o catalogo muda.

## Busca

A lupa ou o botao **FIND** da lista de tokens abre um teclado na tela. Digite e confirme com **OK** para listar so os tokens que combinam:

- Nao diferencia maiusculas de minusculas e basta o trecho aparecer (`gob` acha o Goblin).
- Com varias palavras separadas por espaco, todas precisam combinar, em qualquer ordem (`green 3/3` acha os tokens verdes 3/3).
- Cada palavra e procurada no nome, na linha de tipo, no texto, no nome da cor (`white`, `blue`, `black`, `red`, `green`, `multicolor`, `colorless`) e no P/T (`3/3`).
- **FIND** na lista refina a busca mantendo o texto digitado; **BACK** no teclado cancela. Tocar na barra do nome na carta sempre abre a lista completa, e **<** / **>** na carta continuam passando por todos os tokens.

## Ajuste do touch

Os limites iniciais em `src/main.cpp` sao aproximados. Se os botoes responderem em posicoes erradas, calibre `TOUCH_X_MIN`, `TOUCH_X_MAX`, `TOUCH_Y_MIN` e `TOUCH_Y_MAX`. Se os eixos estiverem trocados, ajuste a conversao de `point.x` e `point.y` em `handleTouch()`.

## Catalogo de tokens

Os tokens vem de `src/tokens_generated.h`, gerado a partir da API do Scryfall. Nao edite esse arquivo a mao. O gerador preserva os staples de `SPECS` em `tools/fetch_tokens.py` no inicio e acrescenta os tokens dos precons:

- Descobre os decks fisicos `Commander Deck` no MTGJSON, incluindo Secret Lair, ate a data escolhida.
- Consulta os sets de tokens correspondentes no Scryfall e os tokens ligados a cada carta das listas dos decks. Isso tambem cobre Commander 2011/2013 e outros produtos sem set de tokens proprio.
- Junta impressoes com o mesmo nome, tipos, cores, P/T e texto de regras; variantes diferentes permanecem separadas. Sets compartilhados podem acrescentar tokens alem dos usados pelos decks.
- Rin and Seri tem `Cat (Rin and Seri)` **verde 1/1** e `Dog (Rin and Seri)` **branco 1/1**. O Cat branco que ja existia continua separado. `Cragflame (Mabel)` e o token lendario de Equipment.
- Emblemas tambem entram quando disponiveis. Nao e uma lista de todas as artes alternativas, nem um motor que executa todas as habilidades de Magic.

Para regenerar o catalogo e a arte (precisa de internet; a arte precisa do Pillow, `python -m pip install pillow`, e sem ele ou com `--no-art` so o catalogo e gerado; as imagens baixadas ficam em `tools/art_cache` e nao sao baixadas de novo):

```
%USERPROFILE%\.platformio\penv\Scripts\python.exe tools\fetch_tokens.py
```

Os dados de API ficam em `tools/catalog_cache`. Para atualizar as fontes, use `--refresh`; para limitar a data de lancamento dos precons, use `--as-of YYYY-MM-DD` (o padrao e hoje). A snapshot incluida foi gerada com `--as-of 2026-10-24`. O gerador percorre todas as paginas e falha explicitamente se nao conseguir resolver uma entrada obrigatoria. A qualidade JPEG e reduzida automaticamente ate a arte de todos os tokens caber no orcamento de flash; as curvas de cor/tom e o gamma do painel nao mudam.

Para adicionar um token, acrescente uma tupla em `SPECS` no formato `(nome, cores, poder, resistencia, texto[, rotulo])` e rode o script de novo:

- `cores`: letras `w`, `u`, `b`, `r`, `g` ou `c` (incolor).
- `poder`: `None` para tokens sem P/T, como artefatos.
- `texto`: `""` exige um token sem texto, uma string exige que ela apareca no texto e `None` aceita qualquer um.
- `rotulo`: nome exibido na lista quando dois tokens teriam o mesmo nome, como `Wurm (Deathtouch)` e `Wurm (Lifelink)`.

Para testar o gerador sem internet: `%USERPROFILE%\.platformio\penv\Scripts\python.exe -m unittest tools.test_fetch_tokens`.

### Conferencia de cobertura dos precons

`tools/check_precon_coverage.py` confere o catalogo por um caminho independente das listas do MTGJSON. Ele parte da lista de produtos Commander do proprio Scryfall (sets do tipo `commander` e produtos com "Commander" no nome), percorre todas as cartas impressas neles e verifica se cada token que elas criam (e cada token dos sets de tokens desses produtos) esta no catalogo. Tambem lista os decks com cara de Commander fora do tipo `Commander Deck` e os produtos sem decklist. Sai com erro se faltar algum token criado por uma carta de precon:

```
cd tools
%USERPROFILE%\.platformio\penv\Scripts\python.exe check_precon_coverage.py --as-of 2026-10-24
```

Resultado da snapshot de 2026-10-24:

- 198 decklists `Commander Deck` do MTGJSON, todas completas (100 cartas). 47 dos 52 produtos Commander do Scryfall tem decklist. Os 5 sem decklist nao sao precons: Commander's Arsenal, Commander Collection Green/Black, os minigames de Baldur's Gate e Mystery Booster Commander Edition. Fora do tipo `Commander Deck` so ha produtos digitais (MTGO 2009, Historic Brawl do Arena), caixas de colecao e decks Starter antigos.
- 21.807 impressoes em 54 sets, 1.187 tokens ligados e 46 sets de tokens; 460 faces de token distintas.
- **0 tokens faltando entre os criados por cartas de precon.** Os 29 tokens fora do catalogo vem so de cartas que nao estao em nenhum precon: drops de Secret Lair, Mystery Booster Commander e extras de collector booster (Legends Retold do DMC, Realms and Relics do LTC, cartas extras do Marvel/Final Fantasy/TMNT Eternal).
- Designacoes de jogo (Dungeon, Monarch/Initiative, Ring, Boss, Event, contadores de Experience/Poison) nao viram tokens, porque nao sao permanentes.

O arquivo gerado inclui um `CATALOG_ID` e os CRCs dos prefixos da lista. Se a expansao mantiver todas as entradas antigas na mesma ordem, quantidades, selecao, contadores, nomes e cartas externas sao preservados. Catalogos incompativeis descartam apenas o estado dos tokens, com aviso no serial; `Custom` e configuracoes continuam preservados.

`partitions.csv` mantem os offsets da aplicacao e da NVS antiga e reserva uma NVS `tokenstore` de 128 KiB para o catalogo ampliado. O firmware migra os saves antigos automaticamente, sem apagar a NVS original. Grave normalmente com PlatformIO para atualizar tambem a tabela de particoes; nao use `erase_flash` para esta atualizacao.