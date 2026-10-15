"""
Motor do jogo de cartas de batalha (estilo "monstrinhos colecionáveis").

Contém toda a lógica, sem nenhuma parte visual:
  - Carta (atributos, elemento, raridade, habilidade)
  - Tabela de vantagem entre elementos
  - Criação do baralho, embaralhamento e divisão entre jogadores
  - Cálculo de batalha (ataque x defesa, crítico, vantagem de tipo)
  - Energia: cada carta tem um custo; você acumula energia a cada rodada
  - Montagem de baralho: escolha suas cartas de uma coleção, respeitando um orçamento
  - Pontuação e fim de jogo

Rode este arquivo diretamente para jogar no terminal:
    python cartas.py
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# 0. REGRAS (mude estes números para equilibrar o jogo)
# ---------------------------------------------------------------------------
TAMANHO_COLECAO = 20      # cartas que você recebe para escolher
TAMANHO_BARALHO = 10      # cartas que você leva para a partida
ORCAMENTO_BARALHO = 25    # soma máxima dos custos das cartas do baralho
CARTAS_NA_MAO = 4         # cartas compradas no início
ENERGIA_INICIAL = 3
ENERGIA_POR_RODADA = 2    # energia ganha no fim de cada rodada (acumula)
ENERGIA_MAX = 10
LIMITE_RODADAS = 60       # trava de segurança contra partidas infinitas

# ---------------------------------------------------------------------------
# 1. ELEMENTOS E VANTAGENS
# ---------------------------------------------------------------------------
# Cada elemento é forte contra alguns e fraco contra outros (pedra-papel-tesoura).
ELEMENTOS = ["Fogo", "Água", "Planta", "Elétrico", "Terra", "Sombra"]

FORTE_CONTRA = {
    "Fogo": ["Planta"],
    "Água": ["Fogo", "Terra"],
    "Planta": ["Água", "Terra"],
    "Elétrico": ["Água"],
    "Terra": ["Elétrico", "Fogo"],
    "Sombra": ["Sombra"],
}


def multiplicador_elemento(atacante: str, defensor: str) -> float:
    """1.5 = super efetivo, 0.75 = pouco efetivo, 1.0 = normal."""
    if defensor in FORTE_CONTRA.get(atacante, []):
        return 1.5
    if atacante in FORTE_CONTRA.get(defensor, []):
        return 0.75
    return 1.0


# ---------------------------------------------------------------------------
# 2. RARIDADE
# ---------------------------------------------------------------------------
# peso = chance de aparecer no baralho; bonus = soma nos atributos; pontos = quanto vale ao vencer
RARIDADES = {
    "Comum":    {"peso": 60, "bonus": 0,  "pontos": 1},
    "Incomum":  {"peso": 25, "bonus": 8,  "pontos": 2},
    "Rara":     {"peso": 12, "bonus": 16, "pontos": 3},
    "Lendária": {"peso": 3,  "bonus": 28, "pontos": 5},
}

# ---------------------------------------------------------------------------
# 3. HABILIDADES ESPECIAIS
# ---------------------------------------------------------------------------
HABILIDADES = {
    "Nenhuma":       "Sem efeito especial.",
    "Fúria":         "+20% de ataque se tiver menos vida que o oponente.",
    "Escudo":        "Reduz em 10 o dano recebido.",
    "Vampirismo":    "Recupera 30% do dano causado.",
    "Golpe Duplo":   "25% de chance de atacar duas vezes.",
    "Esquiva":       "20% de chance de não receber dano.",
}


# ---------------------------------------------------------------------------
# 3b. ESPÉCIES (cada uma tem uma imagem em imagens/<id>.png)
# ---------------------------------------------------------------------------
# id da imagem: (nome exibido, ajuste de atributos que combina com a criatura)
ESPECIES = {
    "Fogo":     {"dragao":   ("Dragão",   {"ataque": +6, "velocidade": -6}),
                 "fenix":    ("Fênix",    {"velocidade": +8, "defesa": -4})},
    "Água":     {"sereia":   ("Sereia",   {"velocidade": +6, "ataque": -3}),
                 "kraken":   ("Kraken",   {"vida_max": +15, "velocidade": -8})},
    "Planta":   {"elfo":     ("Elfo",     {"velocidade": +8, "vida_max": -10}),
                 "ent":      ("Ent",      {"vida_max": +20, "velocidade": -10})},
    "Elétrico": {"mago":     ("Mago",     {"ataque": +6, "defesa": -4}),
                 "lobo":     ("Lobo",     {"velocidade": +10, "vida_max": -10})},
    "Terra":    {"golem":    ("Golem",    {"defesa": +8, "velocidade": -10}),
                 "anao":     ("Anão",     {"defesa": +4, "ataque": +2, "velocidade": -6})},
    "Sombra":   {"vampiro":  ("Vampiro",  {"ataque": +4, "defesa": -2}),
                 "espectro": ("Espectro", {"velocidade": +6, "vida_max": -8})},
}


# ---------------------------------------------------------------------------
# 4. A CARTA
# ---------------------------------------------------------------------------
@dataclass
class Carta:
    nome: str
    elemento: str
    ataque: int
    defesa: int
    vida_max: int
    velocidade: int
    raridade: str = "Comum"
    habilidade: str = "Nenhuma"
    especie: str = ""          # id da imagem (ex.: "dragao")
    vida: int = field(init=False)

    def __post_init__(self):
        self.vida = self.vida_max

    @property
    def viva(self) -> bool:
        return self.vida > 0

    @property
    def especie_nome(self) -> str:
        for especies in ESPECIES.values():
            if self.especie in especies:
                return especies[self.especie][0]
        return "Criatura"

    @property
    def pontos(self) -> int:
        return RARIDADES[self.raridade]["pontos"]

    @property
    def poder(self) -> int:
        """Número único para comparar cartas (útil para a IA)."""
        return self.ataque + self.defesa + self.vida_max // 2 + self.velocidade

    @property
    def custo(self) -> int:
        """Custo de energia: cartas mais fortes custam mais (de 1 a 6)."""
        return max(1, min(6, round((self.poder - 60) / 30)))

    def curar(self):
        self.vida = self.vida_max

    def __str__(self):
        return (f"({self.custo}⚡) {self.nome:<14} {self.especie_nome:<9}[{self.elemento:<8}] {self.raridade:<8} "
                f"ATK {self.ataque:>3}  DEF {self.defesa:>3}  "
                f"HP {self.vida:>3}/{self.vida_max:<3} VEL {self.velocidade:>3}  "
                f"({self.habilidade})")


# ---------------------------------------------------------------------------
# 5. GERAÇÃO DO BARALHO
# ---------------------------------------------------------------------------
PREFIXOS = {
    "Fogo": ["Brasa", "Chama", "Pira", "Ígneo"],
    "Água": ["Maré", "Aqua", "Onda", "Coral"],
    "Planta": ["Folha", "Musgo", "Raiz", "Broto"],
    "Elétrico": ["Volt", "Faísca", "Raio", "Ampère"],
    "Terra": ["Rocha", "Duna", "Barro", "Cascalho"],
    "Sombra": ["Umbra", "Névoa", "Eclipse", "Vulto"],
}
SUFIXOS = ["mon", "zard", "tito", "lion", "bix", "ruga", "dor", "fante"]


def sortear_raridade(rng: random.Random) -> str:
    nomes = list(RARIDADES)
    pesos = [RARIDADES[r]["peso"] for r in nomes]
    return rng.choices(nomes, weights=pesos, k=1)[0]


def criar_carta_aleatoria(rng: random.Random) -> Carta:
    elemento = rng.choice(ELEMENTOS)
    raridade = sortear_raridade(rng)
    bonus = RARIDADES[raridade]["bonus"]
    nome = rng.choice(PREFIXOS[elemento]) + rng.choice(SUFIXOS)
    # Habilidade: comuns quase nunca têm; lendárias sempre têm
    chance_hab = {"Comum": 0.1, "Incomum": 0.4, "Rara": 0.7, "Lendária": 1.0}[raridade]
    habs = [h for h in HABILIDADES if h != "Nenhuma"]
    habilidade = rng.choice(habs) if rng.random() < chance_hab else "Nenhuma"
    especie = rng.choice(list(ESPECIES[elemento]))
    atributos = {
        "ataque": rng.randint(20, 45) + bonus,
        "defesa": rng.randint(5, 25) + bonus // 2,
        "vida_max": rng.randint(60, 100) + bonus * 2,
        "velocidade": rng.randint(10, 50) + bonus // 2,
    }
    for attr, ajuste in ESPECIES[elemento][especie][1].items():
        atributos[attr] = max(1, atributos[attr] + ajuste)
    return Carta(nome=nome, elemento=elemento, raridade=raridade,
                 habilidade=habilidade, especie=especie, **atributos)


def criar_baralho(qtd: int = 40, semente: int | None = None) -> list[Carta]:
    rng = random.Random(semente)
    return [criar_carta_aleatoria(rng) for _ in range(qtd)]


def soma_menores_custos(cartas: list[Carta], k: int) -> int:
    return sum(sorted(c.custo for c in cartas)[:k])


def criar_colecao(qtd: int = TAMANHO_COLECAO, semente: int | None = None) -> list[Carta]:
    """Coleção de onde o jogador escolhe o baralho. Garante que dá para montar
    um baralho válido (as cartas mais baratas cabem no orçamento)."""
    rng = random.Random(semente)
    while True:
        colecao = [criar_carta_aleatoria(rng) for _ in range(qtd)]
        if soma_menores_custos(colecao, TAMANHO_BARALHO) <= ORCAMENTO_BARALHO:
            return colecao


# ---------------------------------------------------------------------------
# 6. MONTAGEM DO BARALHO
# ---------------------------------------------------------------------------
def custo_total(cartas: list[Carta]) -> int:
    return sum(c.custo for c in cartas)


def validar_baralho(cartas: list[Carta]) -> tuple[bool, str]:
    if len(cartas) != TAMANHO_BARALHO:
        return False, f"O baralho precisa ter {TAMANHO_BARALHO} cartas (tem {len(cartas)})."
    if custo_total(cartas) > ORCAMENTO_BARALHO:
        return False, f"Custo {custo_total(cartas)} passa do orçamento de {ORCAMENTO_BARALHO}."
    return True, "Baralho válido!"


def pode_adicionar(selecionadas: list[Carta], carta: Carta, colecao: list[Carta]) -> bool:
    """A carta cabe no baralho sem impedir que ele seja completado depois?
    (sobra orçamento para preencher as vagas restantes com as cartas mais baratas)"""
    if carta in selecionadas or len(selecionadas) >= TAMANHO_BARALHO:
        return False
    novas = selecionadas + [carta]
    vagas = TAMANHO_BARALHO - len(novas)
    resto = [c for c in colecao if c not in novas]
    return custo_total(novas) + soma_menores_custos(resto, vagas) <= ORCAMENTO_BARALHO


def montar_baralho_automatico(colecao: list[Carta]) -> list[Carta]:
    """Escolhe as cartas com melhor custo-benefício (poder por energia),
    sem estourar o orçamento. Usado pela CPU e pelo botão 'Automático'."""
    escolhidas: list[Carta] = []
    for carta in sorted(colecao, key=lambda c: c.poder / c.custo, reverse=True):
        if pode_adicionar(escolhidas, carta, colecao):
            escolhidas.append(carta)
    # Usa o orçamento que sobrou: troca cartas fracas por outras mais fortes
    melhorou = True
    while melhorou:
        melhorou = False
        for nova in sorted((c for c in colecao if c not in escolhidas), key=lambda c: -c.poder):
            fraca = min(escolhidas, key=lambda c: c.poder)
            if (nova.poder > fraca.poder and
                    custo_total(escolhidas) - fraca.custo + nova.custo <= ORCAMENTO_BARALHO):
                escolhidas[escolhidas.index(fraca)] = nova
                melhorou = True
                break
    return escolhidas


# ---------------------------------------------------------------------------
# 7. JOGADOR
# ---------------------------------------------------------------------------
@dataclass
class Jogador:
    nome: str
    humano: bool = False
    mao: list[Carta] = field(default_factory=list)
    pilha: list[Carta] = field(default_factory=list)       # cartas do baralho ainda não compradas
    energia: int = ENERGIA_INICIAL
    pontos: int = 0
    derrotadas: list[Carta] = field(default_factory=list)  # cartas que perdeu

    def comprar(self, n: int = 1) -> int:
        compradas = 0
        for _ in range(n):
            if self.pilha:
                self.mao.append(self.pilha.pop())
                compradas += 1
        return compradas

    def pode_jogar(self, carta: Carta) -> bool:
        return carta.custo <= self.energia

    def jogaveis(self) -> list[Carta]:
        return [c for c in self.mao if self.pode_jogar(c)]

    def escolher_carta_ia(self, oponente: Carta | None = None, ve_carta: bool = True) -> Carta | None:
        """IA simples (só olha cartas que tem energia para pagar):
        - se o oponente passou, joga a mais barata (ponto fácil, gasta pouco);
        - modo difícil (ve_carta=True): escolhe a melhor contra a carta do oponente;
        - modo normal (ve_carta=False): joga a mais forte que puder pagar;
        - sem energia para nada, passa (retorna None)."""
        opcoes = self.jogaveis()
        if not opcoes:
            return None
        if oponente is None:
            return min(opcoes, key=lambda c: (c.custo, -c.poder))
        if not ve_carta:
            return max(opcoes, key=lambda c: c.poder)
        def nota(c: Carta):
            return c.poder * multiplicador_elemento(c.elemento, oponente.elemento)
        return max(opcoes, key=nota)


# ---------------------------------------------------------------------------
# 8. BATALHA
# ---------------------------------------------------------------------------
def calcular_dano(atac: Carta, defe: Carta, rng: random.Random, log: list[str]) -> dict:
    """Calcula um golpe. Retorna um dicionário com o que aconteceu
    (usado pelo log em texto e pela animação do duelo)."""
    golpe = {"atacante": atac, "alvo": defe, "dano": 0, "critico": False,
             "mult": 1.0, "esquiva": False, "furia": False, "cura": 0}
    ataque = atac.ataque
    if atac.habilidade == "Fúria" and atac.vida < defe.vida:
        ataque = int(ataque * 1.2)
        golpe["furia"] = True
        log.append(f"  {atac.nome} entra em FÚRIA!")

    mult = multiplicador_elemento(atac.elemento, defe.elemento)
    critico = rng.random() < 0.10          # 10% de crítico
    variacao = rng.uniform(0.85, 1.0)      # aleatoriedade leve
    golpe["mult"], golpe["critico"] = mult, critico

    dano = ataque * mult * variacao * (1.5 if critico else 1.0) - defe.defesa * 0.6
    if defe.habilidade == "Escudo":
        dano -= 10
    dano = max(5, int(dano))                # sempre causa pelo menos 5

    if defe.habilidade == "Esquiva" and rng.random() < 0.20:
        log.append(f"  {defe.nome} ESQUIVOU!")
        golpe["esquiva"] = True
        return golpe

    txt = f"  {atac.nome} ataca {defe.nome}: {dano} de dano"
    if mult > 1: txt += " (super efetivo!)"
    if mult < 1: txt += " (pouco efetivo...)"
    if critico: txt += " CRÍTICO!"
    log.append(txt)
    golpe["dano"] = dano
    return golpe


def batalhar(c1: Carta, c2: Carta, semente: int | None = None,
             eventos: list[dict] | None = None) -> tuple[Carta | None, list[str]]:
    """Duelo por turnos até uma carta cair. Quem tem mais velocidade ataca primeiro.
    Retorna (vencedora, log). Empate (limite de turnos) retorna None.
    Se 'eventos' for uma lista, cada golpe é adicionado nela (para animar)."""
    rng = random.Random(semente)
    log = [f">> {c1.nome} ({c1.elemento}) x {c2.nome} ({c2.elemento})"]
    ordem = sorted([c1, c2], key=lambda c: (c.velocidade, rng.random()), reverse=True)

    for turno in range(1, 21):
        for atac in ordem:
            defe = c2 if atac is c1 else c1
            golpes = 2 if (atac.habilidade == "Golpe Duplo" and rng.random() < 0.25) else 1
            for _ in range(golpes):
                golpe = calcular_dano(atac, defe, rng, log)
                defe.vida = max(0, defe.vida - golpe["dano"])
                if atac.habilidade == "Vampirismo" and golpe["dano"]:
                    cura = int(golpe["dano"] * 0.3)
                    atac.vida = min(atac.vida_max, atac.vida + cura)
                    golpe["cura"] = cura
                    log.append(f"  {atac.nome} drena {cura} de vida")
                golpe["vida_alvo"], golpe["vida_atacante"] = defe.vida, atac.vida
                if eventos is not None:
                    eventos.append(golpe)
                if not defe.viva:
                    log.append(f"** {defe.nome} foi derrotado! Vence {atac.nome}.")
                    return atac, log
    log.append("Empate por tempo!")
    return None, log


# ---------------------------------------------------------------------------
# 9. PARTIDA
# ---------------------------------------------------------------------------
class Partida:
    def __init__(self, nomes: list[str], humanos: list[bool] | None = None,
                 baralhos: list[list[Carta] | None] | None = None, semente: int | None = None):
        """baralhos: um baralho (lista de cartas) por jogador. Quem vier com None
        recebe uma coleção aleatória e um baralho montado automaticamente."""
        humanos = humanos or [False] * len(nomes)
        baralhos = baralhos or [None] * len(nomes)
        self.jogadores = [Jogador(n, h) for n, h in zip(nomes, humanos)]
        for i, (j, baralho) in enumerate(zip(self.jogadores, baralhos)):
            if baralho is None:
                s = None if semente is None else semente * 100 + i
                baralho = montar_baralho_automatico(criar_colecao(semente=s))
            for c in baralho:
                c.curar()
            j.pilha = list(baralho)
            random.shuffle(j.pilha)
            j.comprar(CARTAS_NA_MAO)
        self.rodada = 0
        self.ultimo: dict | None = None   # resumo da última rodada (usado na animação)

    @property
    def acabou(self) -> bool:
        return (sum(1 for j in self.jogadores if j.mao) <= 1
                or self.rodada >= LIMITE_RODADAS)

    def jogar_rodada(self, c1: Carta | None, c2: Carta | None,
                     j1: Jogador, j2: Jogador) -> list[str]:
        """Cada jogador joga uma carta (pagando a energia) ou passa (None).
        - As duas jogaram: batalha. A vencedora volta curada para a mão e o dono
          ganha os pontos da derrotada. A derrotada sai do jogo e o dono compra
          uma carta do próprio baralho.
        - Só um jogou: ataque direto, +1 ponto, e a carta volta para a mão.
        - Ninguém jogou: nada acontece.
        No fim da rodada todos ganham energia."""
        self.rodada += 1
        resumo = {"c1": c1, "c2": c2, "j1": j1, "j2": j2, "vencedora": None, "eventos": [],
                  "placar_antes": (j1.pontos, j2.pontos), "energia_antes": (j1.energia, j2.energia),
                  "vida_inicial": (c1.vida if c1 else 0, c2.vida if c2 else 0),
                  "tipo": "batalha" if (c1 and c2) else ("direto" if (c1 or c2) else "ninguem")}
        for j, c in ((j1, c1), (j2, c2)):
            if c is not None:
                if not j.pode_jogar(c):
                    raise ValueError(f"{j.nome} não tem energia para {c.nome}")
                j.energia -= c.custo
                j.mao.remove(c)

        if c1 and c2:
            vencedora, log = batalhar(c1, c2, eventos=resumo["eventos"])
            resumo["vencedora"] = vencedora
            for vencedor, perdedor, cv, cp in ((j1, j2, c1, c2), (j2, j1, c2, c1)):
                if vencedora is cv:
                    vencedor.pontos += cp.pontos
                    cv.curar()
                    vencedor.mao.append(cv)
                    perdedor.derrotadas.append(cp)
                    if perdedor.comprar(1):
                        log.append(f"  {perdedor.nome} compra uma carta do baralho.")
            if vencedora is None:  # empate: as duas voltam
                for j, c in ((j1, c1), (j2, c2)):
                    c.curar(); j.mao.append(c)
        elif c1 or c2:
            j, c, outro = (j1, c1, j2) if c1 else (j2, c2, j1)
            log = [f">> {outro.nome} passou a vez.",
                   f"  {c.nome} faz um ataque direto! +1 ponto para {j.nome}."]
            j.pontos += 1
            j.mao.append(c)
        else:
            log = [">> Os dois passaram a vez e guardaram energia."]

        for j in (j1, j2):
            j.energia = min(ENERGIA_MAX, j.energia + ENERGIA_POR_RODADA)
        resumo["placar_depois"] = (j1.pontos, j2.pontos)
        resumo["energia_depois"] = (j1.energia, j2.energia)
        self.ultimo = resumo
        return log

    def placar(self) -> str:
        linhas = [f"{j.nome}: {j.pontos} pts, {len(j.mao)} na mão, "
                  f"{len(j.pilha)} no baralho, {j.energia}⚡" for j in self.jogadores]
        return " | ".join(linhas)

    def vencedor(self) -> Jogador:
        # Pontos decidem; desempate por cartas restantes
        return max(self.jogadores, key=lambda j: (j.pontos, len(j.mao) + len(j.pilha)))


# ---------------------------------------------------------------------------
# 10. VERSÃO TERMINAL
# ---------------------------------------------------------------------------
def montar_baralho_terminal(colecao: list[Carta]) -> list[Carta]:
    print(f"\n=== MONTE SEU BARALHO ===")
    print(f"Escolha {TAMANHO_BARALHO} cartas com custo total até {ORCAMENTO_BARALHO}⚡.\n")
    for i, c in enumerate(colecao, 1):
        print(f"  {i:>2}. {c}")
    while True:
        txt = input("\nNúmeros separados por espaço (ENTER = automático): ").strip()
        if not txt:
            baralho = montar_baralho_automatico(colecao)
        else:
            try:
                idx = [int(x) - 1 for x in txt.split()]
                if len(set(idx)) != len(idx) or min(idx) < 0:
                    raise IndexError
                baralho = [colecao[i] for i in idx]
            except (ValueError, IndexError):
                print("Entrada inválida."); continue
        ok, msg = validar_baralho(baralho)
        print(msg)
        if ok:
            print(f"Seu baralho (custo {custo_total(baralho)}):")
            for c in baralho:
                print("   ", c)
            return baralho


def jogar_terminal():
    print("=== BATALHA DE CARTAS ===\n")
    nome = input("Seu nome: ").strip() or "Jogador"
    dificil = input("Dificuldade - (N)ormal ou (D)ifícil? ").strip().lower().startswith("d")
    baralho = montar_baralho_terminal(criar_colecao())
    p = Partida([nome, "CPU"], humanos=[True, False], baralhos=[baralho, None])
    humano, cpu = p.jogadores

    while not p.acabou:
        print(f"\n--- Rodada {p.rodada + 1} ---\n{p.placar()}")
        for i, c in enumerate(humano.mao, 1):
            aviso = "" if humano.pode_jogar(c) else "   [sem energia]"
            print(f"  {i}. {c}{aviso}")
        print("  0. Passar a vez (guardar energia)")
        escolha = input("Escolha sua carta: ").strip()
        try:
            n = int(escolha)
            c1 = None if n == 0 else humano.mao[n - 1]
        except (ValueError, IndexError):
            print("Opção inválida."); continue
        if c1 and not humano.pode_jogar(c1):
            print(f"Energia insuficiente: {c1.nome} custa {c1.custo}, você tem {humano.energia}."); continue
        c2 = cpu.escolher_carta_ia(oponente=c1, ve_carta=dificil)  # no difícil a CPU "vê" sua carta
        for linha in p.jogar_rodada(c1, c2, humano, cpu):
            print(linha)

    v = p.vencedor()
    print(f"\n*** FIM! {p.placar()}\nVencedor: {v.nome}")


if __name__ == "__main__":
    jogar_terminal()
