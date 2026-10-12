# ⚔️ Batalha de Cartas

Jogo de cartas colecionáveis feito em Python: monte seu baralho de criaturas (dragões, elfos, golens, magos...) e enfrente o computador em duelos animados, com elementos, energia, raridades e habilidades especiais.

![Tela de abertura](docs/tela_abertura.png)

---

## Sumário

1. [Como instalar e abrir](#-como-instalar-e-abrir)
2. [Objetivo](#-objetivo)
3. [Como jogar, passo a passo](#-como-jogar-passo-a-passo)
4. [Regras](#-regras)
5. [Controles](#-controles)
6. [Dicas de estratégia](#-dicas-de-estratégia)
7. [Personalizando o jogo](#-personalizando-o-jogo)
8. [Arquivos do projeto](#-arquivos-do-projeto)
9. [Problemas comuns](#-problemas-comuns)

---

## 🚀 Como instalar e abrir

**Pré-requisito:** Python 3.9 ou mais novo (inclusive 3.14). Baixe em [python.org](https://www.python.org/downloads/). No Windows, marque **"Add Python to PATH"** na instalação.

### Windows (jeito fácil)

1. Extraia o `jogo_cartas.zip`.
2. Dê dois cliques em **`instalar.bat`**. Ele cria um ambiente virtual (`.venv`) e instala o `pygame-ce`. Só precisa fazer isso uma vez.
3. Para jogar, dê dois cliques em **`jogar.bat`**.

### Mac / Linux

```bash
cd jogo_cartas
sh jogar.sh
```

### Manualmente (qualquer sistema)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python visual.py
# Mac/Linux:
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python visual.py
```

> Prefere jogar sem janela gráfica? Rode `python cartas.py` para a **versão em texto** no terminal (mesmas regras).

---

## 🎯 Objetivo

Fazer **mais pontos** que o computador. Você ganha pontos derrotando as cartas dele: cartas mais raras valem mais. A partida termina quando um dos jogadores fica sem cartas na mão.

---

## 🕹️ Como jogar, passo a passo

### 1. Abertura
Clique em **JOGAR**.

### 2. Monte seu baralho

![Montagem do baralho](docs/tela_montagem.png)

- Você recebe uma **coleção de 20 cartas** e precisa escolher **10** para levar à partida.
- A **soma dos custos de energia** (o número na bolinha amarela) não pode passar de **25**.
- Clique numa carta para selecionar ✅ e clique de novo para desmarcar.
- Cartas **escurecidas** não cabem mais no seu baralho (passariam do orçamento).
- Passe o mouse sobre uma carta com habilidade para ver o que ela faz (aparece embaixo da grade).

| Botão | O que faz |
|---|---|
| **Automático** | Monta o melhor baralho possível com a sua coleção |
| **Limpar** | Desmarca tudo |
| **Nova coleção** | Sorteia outras 20 cartas |
| **Dificuldade** | Alterna entre **Normal** e **Difícil** |
| **JOGAR** | Começa a partida (só fica ativo com 10 cartas válidas) |

### 3. Batalha

![Tela de batalha](docs/tela_batalha.png)

- Você começa com **4 cartas na mão**; o resto do baralho fica na pilha de compra.
- A cada rodada, **clique numa carta da mão** para lutar. Cartas com "sem energia" ainda não podem ser jogadas.
- Ou clique em **Passar a vez** para guardar energia (veja as regras abaixo).
- O computador responde com uma carta dele e as duas se enfrentam num **duelo animado**:

![Duelo](docs/duelo_golpe.png)

- No fim de cada duelo, a vencedora volta **curada** para a mão do dono, e a perdedora **sai do jogo**.
- Quando a partida acaba, escolha **Revanche** (mesmo baralho) ou **Novo baralho**.

---

## 📜 Regras

### Atributos de uma carta

| Atributo | Para que serve |
|---|---|
| **ATK** (ataque) | Quanto dano causa |
| **DEF** (defesa) | Reduz o dano recebido |
| **HP** (vida) | Quando chega a 0, a carta é derrotada |
| **VEL** (velocidade) | Quem for mais rápido ataca primeiro |
| **Custo** ⚡ | Energia necessária para jogar a carta (1 a 6, cartas mais fortes custam mais) |

### Energia
- Você começa com **3 de energia**.
- Jogar uma carta **gasta** o custo dela.
- No fim de **toda** rodada, cada jogador ganha **+2 de energia**, acumulando até no máximo **10**.

### Passar a vez
- Se você passar e o adversário jogar uma carta, ela faz um **ataque direto**: o dono dela ganha **+1 ponto** e a carta volta para a mão.
- Se os dois passarem, nada acontece (os dois só guardam energia).
- Passar é útil para juntar energia e jogar uma carta cara (como uma Lendária) na rodada seguinte.

### Raridade

| Raridade | Frequência | Atributos | Pontos ao ser derrotada |
|---|---|---|---|
| Comum | 60% | normais | **1** |
| Incomum | 25% | +8 | **2** |
| Rara | 12% | +16 | **3** |
| Lendária | 3% | +28 | **5** |

A raridade aparece na cor da borda e no subtítulo da carta.

### Elementos

Cada elemento é **forte** contra alguns outros (causa **+50%** de dano) e **fraco** contra quem é forte contra ele (causa **−25%**).

| Elemento | É forte contra |
|---|---|
| 🔥 Fogo | Planta |
| 💧 Água | Fogo, Terra |
| 🌿 Planta | Água, Terra |
| ⚡ Elétrico | Água |
| 🪨 Terra | Elétrico, Fogo |
| 🌑 Sombra | Sombra |

### Espécies

Cada elemento tem duas criaturas, e cada uma tem um pequeno ajuste de atributos:

| Elemento | Criatura | Característica |
|---|---|---|
| Fogo | Dragão | +ataque, −velocidade |
| Fogo | Fênix | +velocidade, −defesa |
| Água | Sereia | +velocidade, −ataque |
| Água | Kraken | +vida, −velocidade |
| Planta | Elfo | +velocidade, −vida |
| Planta | Ent | +vida, −velocidade |
| Elétrico | Mago | +ataque, −defesa |
| Elétrico | Lobo | +velocidade, −vida |
| Terra | Golem | +defesa, −velocidade |
| Terra | Anão | +defesa, +ataque, −velocidade |
| Sombra | Vampiro | +ataque, −defesa |
| Sombra | Espectro | +velocidade, −vida |

### Habilidades especiais

Cartas mais raras têm mais chance de ter uma habilidade (as Lendárias sempre têm).

| Habilidade | Efeito |
|---|---|
| **Fúria** | +20% de ataque quando tem menos vida que o oponente |
| **Escudo** | Reduz em 10 todo dano recebido |
| **Vampirismo** | Recupera 30% do dano que causa |
| **Golpe Duplo** | 25% de chance de atacar duas vezes seguidas |
| **Esquiva** | 20% de chance de não sofrer dano |

### Como o duelo é calculado

1. A carta com mais **velocidade** ataca primeiro; depois elas se alternam.
2. Dano de cada golpe:

   ```
   dano = ATK × elemento × variação (85% a 100%) × crítico − 60% da DEF do alvo
   ```

   - **Crítico:** 10% de chance, dano ×1,5.
   - Todo golpe causa **pelo menos 5** de dano (a não ser que o alvo esquive).
3. O duelo termina quando uma carta chega a 0 de HP. Se ninguém cair em 20 turnos, é **empate** e as duas voltam para a mão.

### Pontuação e fim de jogo
- Vencer um duelo: você ganha os **pontos da carta derrotada** (de 1 a 5, pela raridade).
- Ataque direto (adversário passou): **+1 ponto**.
- Quem perde uma carta **compra uma nova** do próprio baralho (se ainda houver).
- A partida acaba quando um jogador fica **sem cartas na mão** (ou após 60 rodadas).
- **Vence quem tiver mais pontos.** Em caso de empate, ganha quem tiver mais cartas sobrando.

### Dificuldade

| Modo | Como o computador joga |
|---|---|
| **Normal** | Não vê sua carta: joga a mais forte que puder pagar |
| **Difícil** | Vê sua carta antes de escolher e responde com a que tiver vantagem |

Em ambos, se você passar a vez, o computador joga a carta mais barata para garantir o ponto do ataque direto.

---

## 🎮 Controles

| Ação | Como |
|---|---|
| Selecionar carta / botão | Clique com o botão esquerdo |
| Pular a animação do duelo | Clique em qualquer lugar durante o duelo |
| Ligar/desligar o som | Tecla **M** ou ícone 🔊 no canto superior direito |
| Sair | Fechar a janela |

---

## 💡 Dicas de estratégia

- **Não gaste todo o orçamento em Lendárias.** Com 25 de orçamento para 10 cartas, cartas baratas e eficientes garantem que você sempre tenha o que jogar.
- **Varie os elementos** do baralho para ter resposta contra qualquer carta.
- **Observe a energia do computador** (canto superior): se ele está com pouca, uma carta forte sua provavelmente vai enfrentar uma fraca.
- **Passar a vez tem custo** (o adversário pontua), mas juntar energia para uma Lendária pode render 5 pontos depois.
- **Cartas com Escudo** são ótimas contra cartas de ataque baixo; **Vampirismo** é forte em duelos longos.
- No modo Difícil, o computador sempre escolhe o melhor contra-ataque. Jogue primeiro as cartas de elementos que ele tem menos chance de rebater.

---

## 🛠️ Personalizando o jogo

### Regras
Todos os números de equilíbrio estão no início do `cartas.py`, na seção **"0. REGRAS"**:

```python
TAMANHO_COLECAO = 20      # cartas que você recebe para escolher
TAMANHO_BARALHO = 10      # cartas que você leva para a partida
ORCAMENTO_BARALHO = 25    # soma máxima dos custos das cartas do baralho
CARTAS_NA_MAO = 4
ENERGIA_INICIAL = 3
ENERGIA_POR_RODADA = 2
ENERGIA_MAX = 10
```

Elementos (`FORTE_CONTRA`), raridades (`RARIDADES`), habilidades (`HABILIDADES`) e espécies (`ESPECIES`) também ficam no `cartas.py`.

### Imagens
As ilustrações ficam em `imagens/` (`dragao.png`, `elfo.png`, ..., `verso.png`). Para trocar uma arte, coloque outro PNG/JPG **com o mesmo nome**. Qualquer tamanho serve, o jogo recorta e redimensiona sozinho.

### Sons
Os efeitos ficam em `sons/` (`abertura.wav`, `selecionar.wav`, `impacto_fogo.wav`...). Para trocar, coloque outro `.wav` ou `.ogg` **com o mesmo nome**. O volume de cada som pode ser ajustado no dicionário `VOLUMES` do `visual.py`.

### Criar uma criatura nova
1. Adicione a espécie em `ESPECIES` no `cartas.py`, por exemplo:
   ```python
   "Fogo": {..., "salamandra": ("Salamandra", {"velocidade": +6, "vida_max": -6})},
   ```
2. Coloque a imagem `imagens/salamandra.png`.

### Recriar artes e sons
Os arquivos `gerar_arte.py` e `gerar_sons.py` geram todas as imagens e sons do zero. Eles são opcionais, pois os arquivos já vêm prontos. Para usar, instale `cairosvg` (artes) ou `numpy` (sons) e rode o script.

---

## 📁 Arquivos do projeto

```
jogo_cartas/
├── visual.py          # jogo com interface gráfica (pygame-ce)  ← comece por aqui
├── cartas.py          # regras e lógica do jogo + versão em texto
├── imagens/           # ilustrações das criaturas e verso da carta
├── sons/              # efeitos sonoros e música de abertura
├── instalar.bat       # Windows: cria o ambiente e instala dependências
├── jogar.bat          # Windows: abre o jogo
├── jogar.sh           # Mac/Linux: instala (se preciso) e abre o jogo
├── requirements.txt   # dependências (pygame-ce)
├── gerar_arte.py      # (opcional) regenera as imagens
├── gerar_sons.py      # (opcional) regenera os sons
└── docs/              # imagens deste README
```

---

## ❓ Problemas comuns

| Problema | Solução |
|---|---|
| `'python'` ou `'py'` não é reconhecido | Reinstale o Python marcando **"Add Python to PATH"** |
| `No module named pygame` | Rode o `instalar.bat` (ou `pip install pygame-ce` dentro do ambiente) |
| Erro ao compilar o pygame / `CERTIFICATE_VERIFY_FAILED` | Use o **pygame-ce** em vez do pygame (o `requirements.txt` já usa). O pygame original não tem versão pronta para Python 3.14 |
| `No module named cartas` | Extraia o zip antes de rodar e mantenha `visual.py` e `cartas.py` na mesma pasta |
| Cartas sem ilustração | A pasta `imagens/` precisa ficar ao lado do `visual.py` |
| Jogo sem som | Verifique se a pasta `sons/` está ao lado do `visual.py`, se o som não está desligado (tecla **M**) e o volume do computador |
| `jogar.bat` fecha sozinho com erro | Rode o `instalar.bat` de novo: ele apaga o ambiente antigo e recria |

Bom jogo! 🐉
