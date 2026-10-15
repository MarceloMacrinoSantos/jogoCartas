"""
Versão visual do jogo usando pygame.

Instale:   pip install pygame-ce   (ou use instalar.bat / jogar.bat)
Execute:   python visual.py   (cartas.py precisa estar na mesma pasta)

Tela 1 - Montagem do baralho: clique nas cartas da sua coleção para escolher
         10 cartas sem passar do orçamento de energia. Depois clique em JOGAR.
Tela 2 - Batalha: clique numa carta da mão para lutar (precisa ter energia),
         ou em "Passar a vez" para guardar energia. O duelo é animado:
         clique durante a animação para pular.

SONS: ficam na pasta "sons" (abertura.wav, selecionar.wav, impacto_fogo.wav...).
Para trocar um som, coloque outro .wav/.ogg com o mesmo nome. Tecla M (ou o
ícone de alto-falante no canto) liga/desliga o som.

IMAGENS: as ilustrações ficam na pasta "imagens" ao lado deste arquivo,
uma por espécie (dragao.png, elfo.png, golem.png...) mais verso.png.
Para trocar uma arte, basta colocar outro PNG/JPG com o mesmo nome
(qualquer tamanho; o jogo recorta e redimensiona). Se a pasta não existir,
o jogo desenha um monstrinho simples no lugar.
"""

import math
import os
import random

import pygame
from cartas import (
    Partida, criar_colecao, montar_baralho_automatico, pode_adicionar,
    validar_baralho, custo_total, multiplicador_elemento, HABILIDADES,
    TAMANHO_BARALHO, ORCAMENTO_BARALHO, ENERGIA_MAX,
)

PASTA_IMAGENS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagens")
PASTA_SONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sons")
VOLUME_GERAL = 0.8
# volume relativo de cada som (o que não está aqui usa 0.8)
VOLUMES = {"selecionar": 0.45, "desmarcar": 0.4, "botao": 0.45, "bloqueado": 0.45, "energia": 0.4,
           "disparo": 0.5, "esquiva": 0.6, "cura": 0.55, "passar": 0.5, "pontos": 0.7, "abertura": 0.9,
           "entrada": 0.6, "carta": 0.55}
ELEMENTO_SOM = {"Fogo": "fogo", "Água": "agua", "Planta": "planta",
                "Elétrico": "eletrico", "Terra": "terra", "Sombra": "sombra"}


class Sons:
    """Carrega os efeitos da pasta 'sons' e toca pelo nome. Se não houver
    placa de som ou a pasta não existir, o jogo continua funcionando em silêncio."""

    def __init__(self):
        self.ativo = False
        self.mudo = False
        self.sons = {}

    def iniciar(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(24)
        except pygame.error:
            return
        self.ativo = True
        if not os.path.isdir(PASTA_SONS):
            return
        for arq in os.listdir(PASTA_SONS):
            nome, ext = os.path.splitext(arq)
            if ext.lower() in (".wav", ".ogg"):
                try:
                    self.sons[nome] = pygame.mixer.Sound(os.path.join(PASTA_SONS, arq))
                except pygame.error:
                    pass

    def tocar(self, nome, volume=None):
        if not self.ativo or self.mudo or nome not in self.sons:
            return
        canal = self.sons[nome].play()
        if canal:
            canal.set_volume((VOLUMES.get(nome, 0.8) if volume is None else volume) * VOLUME_GERAL)

    def alternar(self):
        self.mudo = not self.mudo
        if self.mudo and self.ativo:
            pygame.mixer.stop()


SONS = Sons()
ICONE_SOM = pygame.Rect(1100 - 46, 8, 36, 30)   # canto superior direito


def desenhar_icone_som(tela, mouse):
    r = ICONE_SOM
    cor = BRANCO if r.collidepoint(mouse) else CINZA
    x, y = r.x + 4, r.centery
    pygame.draw.polygon(tela, cor, [(x, y - 5), (x + 7, y - 5), (x + 15, y - 12), (x + 15, y + 12), (x + 7, y + 5), (x, y + 5)])
    if SONS.mudo:
        pygame.draw.line(tela, (240, 90, 80), (x + 20, y - 7), (x + 30, y + 7), 3)
        pygame.draw.line(tela, (240, 90, 80), (x + 30, y - 7), (x + 20, y + 7), 3)
    else:
        for raio in (7, 13):
            pygame.draw.arc(tela, cor, (x + 12 - raio, y - raio, raio * 2, raio * 2), -0.9, 0.9, 2)

LARGURA, ALTURA = 1100, 720
CARTA_W, CARTA_H = 160, 248
MINI_W, MINI_H = 196, 118

CORES_ELEMENTO = {
    "Fogo": (230, 90, 60), "Água": (70, 140, 230), "Planta": (80, 180, 90),
    "Elétrico": (225, 185, 40), "Terra": (160, 115, 70), "Sombra": (110, 80, 150),
}
CORES_RARIDADE = {
    "Comum": (200, 200, 200), "Incomum": (90, 200, 120),
    "Rara": (80, 150, 255), "Lendária": (255, 190, 40),
}
FUNDO = (24, 28, 40)
PAINEL = (36, 42, 58)
BRANCO = (245, 245, 245)
CINZA = (150, 155, 170)
OURO = (255, 190, 40)
ENERGIA = (255, 214, 60)


# ---------------------------------------------------------------------------
# Peças de desenho reutilizáveis
# ---------------------------------------------------------------------------
class Fontes:
    def __init__(self):
        self.p = pygame.font.SysFont("arial", 14)
        self.m = pygame.font.SysFont("arial", 17, bold=True)
        self.mp = pygame.font.SysFont("arial", 15, bold=True)
        self.pp = pygame.font.SysFont("arial", 12)
        self.g = pygame.font.SysFont("arial", 28, bold=True)
        self.titulo = pygame.font.SysFont("arial", 68, bold=True)


def texto(tela, fonte, s, cor, pos, centro=False):
    img = fonte.render(s, True, cor)
    r = img.get_rect(center=pos) if centro else img.get_rect(topleft=pos)
    tela.blit(img, r)
    return r


def desenhar_barra(tela, x, y, w, valor, maximo, cor):
    pygame.draw.rect(tela, (50, 50, 50), (x, y, w, 8), border_radius=4)
    proporcao = max(0, min(1, valor / maximo))
    pygame.draw.rect(tela, cor, (x, y, int(w * proporcao), 8), border_radius=4)


def desenhar_gema(tela, f, centro, valor, apagada=False):
    """Bolinha de energia com o custo dentro."""
    cor = (90, 90, 100) if apagada else ENERGIA
    pygame.draw.circle(tela, (20, 20, 30), centro, 15)
    pygame.draw.circle(tela, cor, centro, 13)
    texto(tela, f.m, str(valor), (30, 30, 30), centro, centro=True)


def desenhar_barra_energia(tela, f, x, y, energia, rotulo):
    """Fileira de 10 losangos: os acesos são a energia disponível."""
    texto(tela, f.p, rotulo, CINZA, (x, y - 2))
    x0 = x + 90
    for i in range(ENERGIA_MAX):
        cx = x0 + i * 20
        pts = [(cx, y), (cx + 7, y + 8), (cx, y + 16), (cx - 7, y + 8)]
        pygame.draw.polygon(tela, ENERGIA if i < energia else (60, 62, 75), pts)
    texto(tela, f.m, f"{energia}", ENERGIA, (x0 + ENERGIA_MAX * 20, y - 2))


class Arte:
    """Carrega as imagens da pasta 'imagens' e guarda versões já recortadas
    e redimensionadas (para não refazer isso a cada quadro)."""

    def __init__(self):
        self.originais = {}
        self.cache = {}

    def original(self, nome):
        if nome not in self.originais:
            img = None
            for ext in (".png", ".jpg", ".jpeg"):
                caminho = os.path.join(PASTA_IMAGENS, nome + ext)
                if os.path.exists(caminho):
                    img = pygame.image.load(caminho).convert_alpha()
                    break
            self.originais[nome] = img
        return self.originais[nome]

    def get(self, nome, w, h, raio=8, cantos="todos"):
        """Imagem recortada para preencher w x h (sem distorcer), com cantos arredondados."""
        chave = (nome, w, h, raio, cantos)
        if chave not in self.cache:
            img = self.original(nome)
            if img is None:
                self.cache[chave] = None
                return None
            escala = max(w / img.get_width(), h / img.get_height())
            nova = pygame.transform.smoothscale(
                img, (max(w, round(img.get_width() * escala)), max(h, round(img.get_height() * escala))))
            x = (nova.get_width() - w) // 2
            y = (nova.get_height() - h) // 2
            final = pygame.Surface((w, h), pygame.SRCALPHA)
            final.blit(nova, (0, 0), pygame.Rect(x, y, w, h))
            mascara = pygame.Surface((w, h), pygame.SRCALPHA)
            if cantos == "esquerda":
                pygame.draw.rect(mascara, (255, 255, 255, 255), (0, 0, w, h),
                                 border_top_left_radius=raio, border_bottom_left_radius=raio)
            else:
                pygame.draw.rect(mascara, (255, 255, 255, 255), (0, 0, w, h), border_radius=raio)
            final.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            self.cache[chave] = final
        return self.cache[chave]


ARTE = Arte()


def desenhar_arte(tela, carta, rect, raio=8, cantos="todos"):
    """Desenha a ilustração da espécie; sem imagem, usa o monstrinho geométrico."""
    img = ARTE.get(carta.especie, rect.w, rect.h, raio, cantos)
    if img:
        tela.blit(img, rect.topleft)
    else:
        pygame.draw.rect(tela, (250, 250, 250), rect, border_radius=raio)
        desenhar_monstro(tela, CORES_ELEMENTO[carta.elemento], rect.center, min(rect.w, rect.h) // 3)


def desenhar_selo_elemento(tela, f, carta, x, y):
    img = f.p.render(carta.elemento, True, BRANCO)
    r = pygame.Rect(x, y, img.get_width() + 12, 18)
    pygame.draw.rect(tela, CORES_ELEMENTO[carta.elemento], r, border_radius=9)
    pygame.draw.rect(tela, (20, 20, 30), r, 1, border_radius=9)
    tela.blit(img, (r.x + 6, r.y + 1))


def escuro(cor, q=0.45):
    return tuple(int(c * q) for c in cor)


def desenhar_monstro(tela, cor, centro, raio):
    cx, cy = centro
    escuro = tuple(max(0, c - 70) for c in cor)
    pygame.draw.circle(tela, escuro, (cx, cy + 4), raio)
    olho = max(3, raio // 4)
    pygame.draw.circle(tela, BRANCO, (cx - raio // 3, cy), olho)
    pygame.draw.circle(tela, BRANCO, (cx + raio // 3, cy), olho)
    pygame.draw.circle(tela, (0, 0, 0), (cx - raio // 3, cy), olho // 2)
    pygame.draw.circle(tela, (0, 0, 0), (cx + raio // 3, cy), olho // 2)


def escurecer(tela, rect, alfa=150):
    sombra = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sombra, (10, 10, 20, alfa), sombra.get_rect(), border_radius=12)
    tela.blit(sombra, rect.topleft)


def desenhar_carta(tela, f, carta, x, y, destaque=False, bloqueada=False, vida=None):
    """Carta grande (mão na batalha). 'vida' permite mostrar outro HP (animação)."""
    vida = carta.vida if vida is None else vida
    rect = pygame.Rect(x, y, CARTA_W, CARTA_H)
    if destaque and not bloqueada:
        rect.y -= 15
    cor = CORES_ELEMENTO[carta.elemento]
    borda = CORES_RARIDADE[carta.raridade]
    pygame.draw.rect(tela, escuro(cor, 0.55), rect, border_radius=12)
    faixa = pygame.Rect(rect.x, rect.y, rect.w, 48)
    pygame.draw.rect(tela, escuro(cor, 0.8), faixa, border_top_left_radius=12, border_top_right_radius=12)
    pygame.draw.rect(tela, borda, rect, 5 if carta.raridade != "Comum" else 3, border_radius=12)

    texto(tela, f.m, carta.nome, BRANCO, (rect.x + 10, rect.y + 7))
    texto(tela, f.p, f"{carta.especie_nome} · {carta.raridade}", borda, (rect.x + 10, rect.y + 28))

    arte = pygame.Rect(rect.x + 9, rect.y + 48, CARTA_W - 18, 104)
    desenhar_arte(tela, carta, arte)
    pygame.draw.rect(tela, (20, 20, 30), arte, 2, border_radius=8)
    desenhar_selo_elemento(tela, f, carta, arte.x + 4, arte.bottom - 22)

    yy = rect.y + 158
    texto(tela, f.p, f"ATK {carta.ataque}", (255, 170, 150), (rect.x + 12, yy))
    texto(tela, f.p, f"DEF {carta.defesa}", (170, 210, 255), (rect.x + 84, yy))
    texto(tela, f.p, f"VEL {carta.velocidade}", (255, 235, 150), (rect.x + 12, yy + 18))
    texto(tela, f.p, f"HP {vida}", (170, 255, 180), (rect.x + 84, yy + 18))
    cor_hp = (90, 230, 110) if vida > carta.vida_max * 0.5 else (240, 200, 60) if vida > carta.vida_max * 0.25 else (240, 80, 70)
    desenhar_barra(tela, rect.x + 12, yy + 40, CARTA_W - 24, vida, carta.vida_max, cor_hp)
    if carta.habilidade != "Nenhuma":
        texto(tela, f.p, f"+ {carta.habilidade}", OURO, (rect.x + 12, rect.bottom - 26))

    desenhar_gema(tela, f, (rect.right - 4, rect.y + 4), carta.custo, apagada=bloqueada)
    if bloqueada:
        escurecer(tela, rect)
        texto(tela, f.m, "sem energia", BRANCO, rect.center, centro=True)
    return rect


def desenhar_verso(tela, x, y, w=CARTA_W, h=140):
    rect = pygame.Rect(x, y, w, h)
    img = ARTE.get("verso", w, h, 12)
    if img:
        tela.blit(img, rect.topleft)
    else:
        pygame.draw.rect(tela, (60, 40, 90), rect, border_radius=12)
        pygame.draw.circle(tela, (200, 170, 255), rect.center, min(w, h) // 5, 3)
    pygame.draw.rect(tela, (200, 170, 255), rect, 3, border_radius=12)
    return rect


def desenhar_mini(tela, f, carta, rect, selecionada=False, bloqueada=False, hover=False):
    """Carta deitada, usada na tela de montagem do baralho."""
    pygame.draw.rect(tela, PAINEL, rect, border_radius=12)
    arte = pygame.Rect(rect.x, rect.y, 78, rect.h)
    desenhar_arte(tela, carta, arte, raio=12, cantos="esquerda")
    pygame.draw.rect(tela, CORES_ELEMENTO[carta.elemento], (arte.right - 4, rect.y, 4, rect.h))

    x = rect.x + 86
    texto(tela, f.mp, carta.nome, BRANCO, (x, rect.y + 7))
    texto(tela, f.pp, f"{carta.especie_nome} · {carta.raridade}", CORES_RARIDADE[carta.raridade], (x, rect.y + 28))
    texto(tela, f.p, f"ATK {carta.ataque}  DEF {carta.defesa}", BRANCO, (x, rect.y + 48))
    texto(tela, f.p, f"HP {carta.vida_max}  VEL {carta.velocidade}", BRANCO, (x, rect.y + 66))
    if carta.habilidade != "Nenhuma":
        texto(tela, f.p, f"+ {carta.habilidade}", OURO, (x, rect.y + 90))

    desenhar_gema(tela, f, (rect.x + 16, rect.y + 16), carta.custo)
    pygame.draw.rect(tela, CORES_RARIDADE[carta.raridade] if carta.raridade != "Comum" else (70, 76, 95),
                     rect, 2, border_radius=12)
    if selecionada:
        pygame.draw.rect(tela, BRANCO, rect, 4, border_radius=12)
        pygame.draw.circle(tela, (70, 200, 110), (rect.right - 16, rect.bottom - 16), 11)
        pygame.draw.lines(tela, BRANCO, False, [(rect.right - 21, rect.bottom - 16),
                                                (rect.right - 17, rect.bottom - 12),
                                                (rect.right - 10, rect.bottom - 21)], 3)
    elif hover and not bloqueada:
        pygame.draw.rect(tela, (200, 200, 220), rect, 2, border_radius=12)
    if bloqueada and not selecionada:
        escurecer(tela, rect, 150)


class Botao:
    def __init__(self, rect, rotulo, cor=(70, 110, 220)):
        self.rect = pygame.Rect(rect)
        self.rotulo = rotulo
        self.cor = cor

    def desenhar(self, tela, f, mouse, ativo=True):
        cor = self.cor if ativo else (70, 72, 85)
        if ativo and self.rect.collidepoint(mouse):
            cor = tuple(min(255, c + 30) for c in cor)
        pygame.draw.rect(tela, cor, self.rect, border_radius=10)
        texto(tela, f.m, self.rotulo, BRANCO if ativo else CINZA, self.rect.center, centro=True)

    def clicou(self, pos, ativo=True):
        return ativo and self.rect.collidepoint(pos)


def posicoes_mao(qtd, y, largura_area=LARGURA):
    total = qtd * (CARTA_W + 15) - 15
    x0 = (largura_area - total) // 2
    return [(x0 + i * (CARTA_W + 15), y) for i in range(qtd)]


# ---------------------------------------------------------------------------
# Tela 0: abertura
# ---------------------------------------------------------------------------
class TelaAbertura:
    ESPECIES = ["dragao", "elfo", "mago", "kraken", "golem", "vampiro", "fenix", "sereia",
                "ent", "lobo", "anao", "espectro"]

    def __init__(self):
        self.t = 0.0
        self.tocou = False
        self.b_jogar = Botao((LARGURA // 2 - 120, 560, 240, 60), "JOGAR", (60, 170, 90))
        # cartas flutuando ao fundo
        self.flutuantes = [[random.uniform(0, LARGURA), random.uniform(0, ALTURA + 200),
                            random.uniform(18, 40), random.choice(self.ESPECIES), random.uniform(-15, 15)]
                           for _ in range(14)]

    def update(self, dt):
        if not self.tocou:          # toca a fanfarra no primeiro quadro
            self.tocou = True
            SONS.tocar("abertura")
        self.t += dt
        for fl in self.flutuantes:
            fl[1] -= fl[2] * dt
            if fl[1] < -160:
                fl[0], fl[1] = random.uniform(0, LARGURA), ALTURA + 120
                fl[3] = random.choice(self.ESPECIES)

    def clique(self, pos):
        if self.b_jogar.clicou(pos) and self.t > 0.3:
            SONS.tocar("botao")
            return ("montar",)
        return None

    def desenhar(self, tela, f, mouse):
        t = self.t
        # fundo: cartas viradas para cima, flutuando devagar
        for x, y, vel, esp, ang in self.flutuantes:
            img = ARTE.get(esp, 120, 88, 10)
            if img is None:
                continue
            img = pygame.transform.rotate(img, ang)
            img.set_alpha(70)
            tela.blit(img, img.get_rect(center=(x, y)))
        escurecer(tela, tela.get_rect(), 90)

        # três cartas em leque no centro
        k = suave(t / 1.2)
        for i, (esp, ang) in enumerate((("elfo", 14), ("dragao", 0), ("mago", -14))):
            w, h = 190, 140
            img = ARTE.get(esp, w, h, 14)
            if img is None:
                continue
            moldura = pygame.Surface((w + 12, h + 12), pygame.SRCALPHA)
            pygame.draw.rect(moldura, OURO, moldura.get_rect(), border_radius=18)
            moldura.blit(img, (6, 6))
            moldura = pygame.transform.rotozoom(moldura, ang * k, 0.6 + 0.4 * k)
            cx = LARGURA // 2 + (i - 1) * 170 * k
            cy = 400 - (14 if i == 1 else 0) + 6 * math.sin(t * 2 + i)
            tela.blit(moldura, moldura.get_rect(center=(cx, cy)))

        # título com brilho, entrando junto com a fanfarra
        kt = suave((t - 0.4) / 0.7)
        if kt > 0:
            tela.blit(sprite_brilho((255, 170, 40), 260), (LARGURA // 2 - 260, 150 - 260))
            for d, cor in ((5, (40, 20, 10)), (0, OURO)):
                img = f.titulo.render("BATALHA DE CARTAS", True, cor)
                img = pygame.transform.rotozoom(img, 0, 0.5 + 0.5 * kt)
                img.set_alpha(int(255 * kt))
                tela.blit(img, img.get_rect(center=(LARGURA // 2 + d, 150 + d)))
            sub = f.g.render("Dragões, elfos, golens e magia", True, BRANCO)
            sub.set_alpha(int(255 * suave((t - 1.0) / 0.6)))
            tela.blit(sub, sub.get_rect(center=(LARGURA // 2, 222)))

        if t > 1.2:
            pulso = 1 + 0.04 * math.sin(t * 5)
            r = self.b_jogar.rect
            base = r.copy()
            self.b_jogar.rect = r.inflate(int(r.w * (pulso - 1)), int(r.h * (pulso - 1)))
            self.b_jogar.desenhar(tela, f, mouse)
            self.b_jogar.rect = base
            texto(tela, f.p, "M ou o ícone no canto: liga/desliga o som", CINZA, (LARGURA // 2, 640), centro=True)


# ---------------------------------------------------------------------------
# Tela 1: montagem do baralho
# ---------------------------------------------------------------------------
class TelaMontagem:
    COLUNAS = 5

    def __init__(self, colecao=None, dificil=False):
        self.colecao = colecao or criar_colecao()
        self.selecionadas = []
        self.dificil = dificil
        self.b_auto = Botao((40, 655, 150, 46), "Automático", (120, 90, 200))
        self.b_limpar = Botao((205, 655, 120, 46), "Limpar", (90, 95, 115))
        self.b_nova = Botao((340, 655, 170, 46), "Nova coleção", (90, 95, 115))
        self.b_dif = Botao((560, 655, 230, 46), "", (160, 90, 70))
        self.b_jogar = Botao((870, 655, 190, 46), "JOGAR", (60, 170, 90))

    def rect_mini(self, i):
        col, lin = i % self.COLUNAS, i // self.COLUNAS
        return pygame.Rect(40 + col * (MINI_W + 9), 110 + lin * (MINI_H + 15), MINI_W, MINI_H)

    def clique(self, pos):
        """Retorna ('jogar', baralho, dificil) quando o jogador inicia a partida."""
        for i, carta in enumerate(self.colecao):
            if self.rect_mini(i).collidepoint(pos):
                if carta in self.selecionadas:
                    self.selecionadas.remove(carta)
                    SONS.tocar("desmarcar")
                elif pode_adicionar(self.selecionadas, carta, self.colecao):
                    self.selecionadas.append(carta)
                    SONS.tocar("selecionar")
                else:
                    SONS.tocar("bloqueado")
                return None
        ok, _ = validar_baralho(self.selecionadas)
        if self.b_auto.clicou(pos):
            self.selecionadas = montar_baralho_automatico(self.colecao)
            SONS.tocar("carta")
        elif self.b_limpar.clicou(pos):
            self.selecionadas = []
            SONS.tocar("desmarcar")
        elif self.b_nova.clicou(pos):
            self.colecao, self.selecionadas = criar_colecao(), []
            SONS.tocar("carta")
        elif self.b_dif.clicou(pos):
            self.dificil = not self.dificil
            SONS.tocar("botao")
        elif self.b_jogar.clicou(pos, ok):
            SONS.tocar("botao")
            return ("jogar", list(self.selecionadas), self.dificil)
        elif self.b_jogar.clicou(pos):
            SONS.tocar("bloqueado")
        return None

    def desenhar(self, tela, f, mouse):
        texto(tela, f.g, "Monte seu baralho", BRANCO, (40, 20))
        texto(tela, f.p, f"Escolha {TAMANHO_BARALHO} cartas. A soma dos custos de energia "
                         f"não pode passar de {ORCAMENTO_BARALHO}. Cartas escurecidas não cabem mais.",
              CINZA, (40, 58))

        qtd, custo = len(self.selecionadas), custo_total(self.selecionadas)
        cor_qtd = (110, 220, 130) if qtd == TAMANHO_BARALHO else BRANCO
        texto(tela, f.m, f"Cartas: {qtd}/{TAMANHO_BARALHO}", cor_qtd, (40, 80))
        texto(tela, f.m, f"Energia usada: {custo}/{ORCAMENTO_BARALHO}", ENERGIA, (200, 80))
        desenhar_barra(tela, 420, 87, 300, custo, ORCAMENTO_BARALHO, ENERGIA)

        dica = ""
        for i, carta in enumerate(self.colecao):
            r = self.rect_mini(i)
            hover = r.collidepoint(mouse)
            sel = carta in self.selecionadas
            bloq = not sel and not pode_adicionar(self.selecionadas, carta, self.colecao)
            desenhar_mini(tela, f, carta, r, sel, bloq, hover)
            if hover and carta.habilidade != "Nenhuma":
                dica = f"{carta.habilidade}: {HABILIDADES[carta.habilidade]}"
        if dica:
            texto(tela, f.p, dica, OURO, (40, 632))

        ok, _ = validar_baralho(self.selecionadas)
        self.b_auto.desenhar(tela, f, mouse)
        self.b_limpar.desenhar(tela, f, mouse)
        self.b_nova.desenhar(tela, f, mouse)
        self.b_dif.rotulo = "Dificuldade: " + ("Difícil" if self.dificil else "Normal")
        self.b_dif.desenhar(tela, f, mouse)
        self.b_jogar.desenhar(tela, f, mouse, ativo=ok)


# ---------------------------------------------------------------------------
# Animação do duelo
# ---------------------------------------------------------------------------
def suave(x):
    """Ease-out: começa rápido e desacelera."""
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def entre(a, b, k):
    return a + (b - a) * k


def clarear(cor, q=0.5):
    return tuple(int(c + (255 - c) * q) for c in cor)


_brilhos = {}


def sprite_brilho(cor, raio):
    """Bola luminosa com borda transparente (energia, partículas)."""
    chave = (cor, raio)
    if chave not in _brilhos:
        s = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        for i in range(raio, 0, -1):
            a = int(230 * (1 - i / raio) ** 1.6)
            pygame.draw.circle(s, (*cor, a), (raio, raio), i)
        _brilhos[chave] = s
    return _brilhos[chave]


class Particula:
    def __init__(self, x, y, vx, vy, vida, cor, raio, gravidade=0):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.vida = self.vida_total = vida
        self.cor, self.raio, self.gravidade = cor, raio, gravidade

    def atualizar(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravidade * dt
        self.vx *= 0.96
        self.vida -= dt

    def desenhar(self, tela):
        r = max(1, int(self.raio * (self.vida / self.vida_total)))
        tela.blit(sprite_brilho(self.cor, r), (self.x - r, self.y - r))


class TextoFlutuante:
    """Texto que aparece com um 'pop', sobe e some (dano, CRÍTICO, +pontos...)."""

    def __init__(self, s, x, y, cor, fonte, dur=1.1, vy=-45, atraso=0.0):
        self.img = fonte.render(s, True, cor)
        self.sombra = fonte.render(s, True, (15, 10, 20))
        self.x, self.y, self.vy = x, y, vy
        self.dur, self.idade = dur, -atraso

    @property
    def vivo(self):
        return self.idade < self.dur

    def atualizar(self, dt):
        self.idade += dt
        if self.idade > 0:
            self.y += self.vy * dt

    def desenhar(self, tela):
        if self.idade < 0:
            return
        k = self.idade / self.dur
        escala = 1.0 + 0.6 * max(0.0, 1 - self.idade / 0.15)   # "pop" no começo
        alfa = int(255 * (1 - max(0.0, k - 0.6) / 0.4))
        for img, d in ((self.sombra, 3), (self.img, 0)):
            im = pygame.transform.rotozoom(img, 0, escala) if escala != 1 else img.copy()
            im.set_alpha(alfa)
            tela.blit(im, im.get_rect(center=(self.x + d, self.y + d)))


class Duelo:
    """Anima uma rodada usando o resumo que o motor guardou em partida.ultimo.
    A rodada já foi calculada; aqui só mostramos o que aconteceu, golpe a golpe."""
    ESCALA = 1.25
    CENTRO = {1: (380, 380), 2: (720, 380)}   # 1 = você, 2 = CPU

    def __init__(self, resumo, tela_batalha):
        self.r = resumo
        self.tb = tela_batalha
        self.t = 0.0
        self.particulas = []
        self.textos = []        # desenhados sobre as cartas
        self.textos_topo = []   # desenhados por cima de tudo (placar, energia)
        self.cache = {}
        self.f_dano = pygame.font.SysFont("arial", 40, bold=True)
        self.f_info = pygame.font.SysFont("arial", 22, bold=True)
        self.f_titulo = pygame.font.SysFont("arial", 46, bold=True)
        self.placar = resumo["placar_antes"]
        self.pulso_placar = {1: 0.0, 2: 0.0}

        c1, c2 = resumo["c1"], resumo["c2"]
        self.cartas = {1: c1, 2: c2}
        self.eventos = resumo["eventos"]
        n = len(self.eventos)
        self.D = max(0.42, min(0.8, 5.5 / max(1, n)))    # duração de cada golpe
        self.T0 = 0.75                                     # depois das cartas entrarem
        tipo = resumo["tipo"]
        if tipo == "batalha":
            self.TF = self.T0 + n * self.D + 0.25
        elif tipo == "direto":
            self.TF = self.T0 + 0.9
        else:
            self.TF = 0.3
        self.duracao = self.TF + (2.1 if tipo != "ninguem" else 1.4)

        # vida antes/depois de cada golpe, para animar as barras
        vida = {id(c1): resumo["vida_inicial"][0], id(c2): resumo["vida_inicial"][1]} if tipo == "batalha" else {}
        self.vida_inicial = dict(vida)
        self.passos_vida = []
        for ev in self.eventos:
            a, b = ev["alvo"], ev["atacante"]
            passo = (vida[id(a)], ev["vida_alvo"], vida[id(b)], ev["vida_atacante"])
            vida[id(a)], vida[id(b)] = ev["vida_alvo"], ev["vida_atacante"]
            self.passos_vida.append(passo)

        # quem venceu e quantos pontos cada lado ganhou
        antes, depois = resumo["placar_antes"], resumo["placar_depois"]
        self.ganho = {1: depois[0] - antes[0], 2: depois[1] - antes[1]}
        venc = resumo["vencedora"]
        self.lado_vencedor = 1 if (venc is not None and venc is c1) else 2 if venc is not None else None
        if tipo == "direto":
            self.lado_vencedor = 1 if c1 else 2
        self.pontos_entregues = False
        if tipo != "ninguem":
            SONS.tocar("entrada")

    # ---------------- tempo ----------------
    @property
    def acabou(self):
        return self.t >= self.duracao

    def pular(self):
        self.t = self.duracao

    def inicio(self, i):
        return self.T0 + i * self.D

    def impacto(self, i):
        return self.inicio(i) + 0.55 * self.D

    def lado_de(self, carta):
        return 1 if carta is self.cartas[1] else 2

    # ---------------- estado mostrado ----------------
    def energia_mostrada(self):
        e0 = self.r["energia_antes"]
        if self.t < 0.55:
            return e0
        custos = [c.custo if c else 0 for c in (self.r["c1"], self.r["c2"])]
        return (e0[0] - custos[0], e0[1] - custos[1])

    def vida_em(self, carta):
        v = self.vida_inicial.get(id(carta), carta.vida)
        for i, ev in enumerate(self.eventos):
            imp = self.impacto(i)
            if self.t < imp:
                break
            k = suave((self.t - imp) / (0.3 * self.D))
            a0, a1, b0, b1 = self.passos_vida[i]
            if ev["alvo"] is carta:
                v = entre(a0, a1, k)
            elif ev["atacante"] is carta:
                v = entre(b0, b1, k)
        return int(round(v))

    def centro(self, lado):
        """Posição da carta (com entrada, investida, tremida, esquiva e queda)."""
        cx, cy = self.CENTRO[lado]
        t = self.t
        # entrada: sua carta vem de baixo, a da CPU de cima
        k = suave(t / 0.6)
        cy = entre(ALTURA + 220 if lado == 1 else -220, cy, k)
        frente = 1 if lado == 1 else -1
        carta = self.cartas[lado]
        ang = 0.0
        for i, ev in enumerate(self.eventos):
            s = self.inicio(i)
            if t < s:
                break
            if ev["atacante"] is carta:                       # investida
                u = (t - s) / (0.3 * self.D)
                if 0 <= u <= 1:
                    cx += frente * 45 * math.sin(math.pi * u)
            imp = self.impacto(i)
            if ev["alvo"] is carta and t >= imp:
                u = (t - imp) / (0.32 * self.D)
                if 0 <= u <= 1:
                    if ev["esquiva"]:                         # pulo para o lado
                        cy -= 55 * math.sin(math.pi * u)
                        cx -= frente * 35 * math.sin(math.pi * u)
                    else:                                     # tremida
                        forca = 14 if ev["critico"] else 9
                        cx += math.sin(u * 45) * forca * (1 - u)
                        ang += math.sin(u * 30) * 4 * (1 - u)
        # fim: a perdedora cai
        if self.r["tipo"] == "batalha" and self.lado_vencedor and lado != self.lado_vencedor and t > self.TF:
            k = suave((t - self.TF) / 0.7)
            cy += 90 * k
            ang += -14 * k * frente
        return cx, cy, ang

    # ---------------- atualização ----------------
    def update(self, dt):
        t0, self.t = self.t, self.t + dt
        t = self.t
        cruzou = lambda momento: t0 < momento <= t

        # energia gasta
        if cruzou(0.55) and self.r["tipo"] != "ninguem":
            SONS.tocar("energia")
        if cruzou(0.55):
            for lado, (x, y) in ((1, (330, ALTURA - 40)), (2, (930, 36))):
                c = self.cartas[lado]
                if c:
                    self.textos_topo.append(TextoFlutuante(f"-{c.custo} energia", x, y, ENERGIA, self.f_info, dur=1.3, vy=-20))

        # faíscas de energia saindo das cartas durante o duelo
        if self.T0 * 0.6 < t < self.TF + 0.3:
            for lado in (1, 2):
                c = self.cartas[lado]
                if c and random.random() < 0.5:
                    cx, cy, _ = self.centro(lado)
                    cor = clarear(CORES_ELEMENTO[c.elemento], 0.3)
                    x = cx + random.uniform(-105, 105)
                    y = cy + random.uniform(-150, 150)
                    self.particulas.append(Particula(x, y, random.uniform(-10, 10), random.uniform(-70, -30),
                                                     random.uniform(0.5, 0.9), cor, random.randint(4, 7)))

        for i, ev in enumerate(self.eventos):
            atac, alvo = ev["atacante"], ev["alvo"]
            la, lb = self.lado_de(atac), self.lado_de(alvo)
            s, imp = self.inicio(i), self.impacto(i)
            ax, ay, _ = self.centro(la)
            bx, by, _ = self.centro(lb)
            cor = CORES_ELEMENTO[atac.elemento]
            if cruzou(s + 0.12 * self.D):
                SONS.tocar("disparo")
            if cruzou(s) and ev["furia"]:
                SONS.tocar("furia")
                self.textos.append(TextoFlutuante("FÚRIA!", ax, ay - 190, (255, 90, 70), self.f_info))
            # rastro da bola de energia
            p0 = s + 0.12 * self.D
            if p0 <= t <= imp:
                x, y = self.pos_projetil(i)
                for _ in range(3):
                    self.particulas.append(Particula(x, y, random.uniform(-60, 60), random.uniform(-60, 60),
                                                     0.35, clarear(cor, 0.35), random.randint(6, 10)))
            if cruzou(imp):
                if ev["esquiva"]:
                    SONS.tocar("esquiva")
                else:
                    SONS.tocar("impacto_" + ELEMENTO_SOM[atac.elemento])
                    if ev["critico"]:
                        SONS.tocar("critico", 0.7)
                    if ev["cura"]:
                        SONS.tocar("cura")
                if ev["esquiva"]:
                    self.textos.append(TextoFlutuante("ESQUIVOU!", bx, by - 60, (190, 240, 255), self.f_info))
                    for _ in range(12):
                        self.particulas.append(Particula(bx, by, random.uniform(-150, 150), random.uniform(-150, 150),
                                                         0.4, (220, 230, 255), 6))
                    continue
                for _ in range(34 if ev["critico"] else 22):           # explosão no alvo
                    ang = random.uniform(0, math.tau)
                    vel = random.uniform(120, 380)
                    self.particulas.append(Particula(bx + random.uniform(-20, 20), by + random.uniform(-30, 30),
                                                     math.cos(ang) * vel, math.sin(ang) * vel,
                                                     random.uniform(0.35, 0.7), random.choice([cor, clarear(cor, 0.6), (255, 255, 255)]),
                                                     random.randint(6, 12), gravidade=300))
                cor_txt = (255, 225, 60) if ev["critico"] else (255, 80, 70)
                self.textos.append(TextoFlutuante(f"-{ev['dano']}", bx + random.uniform(-20, 20), by - 40, cor_txt, self.f_dano))
                if ev["critico"]:
                    self.textos.append(TextoFlutuante("CRÍTICO!", bx, by - 95, (255, 225, 60), self.f_info))
                if ev["mult"] > 1:
                    self.textos.append(TextoFlutuante("Super efetivo!", bx, by + 20, (255, 170, 60), self.f_info, atraso=0.05))
                elif ev["mult"] < 1:
                    self.textos.append(TextoFlutuante("Pouco efetivo...", bx, by + 20, (170, 190, 220), self.f_info, atraso=0.05))
                if ev["cura"]:
                    self.textos.append(TextoFlutuante(f"+{ev['cura']}", ax, ay - 40, (110, 255, 140), self.f_dano, atraso=0.1))

        # desfecho
        tipo = self.r["tipo"]
        if tipo == "direto" and cruzou(self.T0):
            SONS.tocar("disparo")
        if tipo == "direto" and cruzou(self.T0 + 0.5):
            SONS.tocar("impacto_" + ELEMENTO_SOM[self.cartas[self.lado_vencedor].elemento])
        if tipo == "ninguem" and cruzou(0.2):
            self.textos.append(TextoFlutuante("Os dois passaram a vez", LARGURA // 2, ALTURA // 2,
                                              BRANCO, self.f_titulo, dur=1.2, vy=-10))
        if tipo == "batalha" and cruzou(self.TF):
            SONS.tocar({1: "vitoria", 2: "derrota", None: "empate"}[self.lado_vencedor])
            if self.lado_vencedor:
                vx, vy, _ = self.centro(self.lado_vencedor)
                perd = 3 - self.lado_vencedor
                px, py, _ = self.centro(perd)
                self.textos.append(TextoFlutuante("VENCEU!", vx, vy - 215, OURO, self.f_titulo, dur=1.9, vy=-8))
                self.textos.append(TextoFlutuante("DERROTADO", px, py, (255, 90, 80), self.f_titulo, dur=1.9, vy=10))
                self.textos.append(TextoFlutuante("-1 carta", px, py + 190, (255, 140, 130), self.f_info, dur=1.5, vy=-10, atraso=0.4))
            else:
                self.textos.append(TextoFlutuante("EMPATE!", LARGURA // 2, 380, BRANCO, self.f_titulo, dur=1.9, vy=-8))
        if self.lado_vencedor and self.ganho[self.lado_vencedor] and not self.pontos_entregues:
            if t >= self.TF + 1.2:
                self.entregar_pontos()

        for p in self.particulas:
            p.atualizar(dt)
        self.particulas = [p for p in self.particulas if p.vida > 0]
        for lista in (self.textos, self.textos_topo):
            for tx in lista:
                tx.atualizar(dt)
        self.textos = [tx for tx in self.textos if tx.vivo]
        self.textos_topo = [tx for tx in self.textos_topo if tx.vivo]
        for lado in (1, 2):
            self.pulso_placar[lado] = max(0.0, self.pulso_placar[lado] - dt)

    def entregar_pontos(self):
        self.pontos_entregues = True
        SONS.tocar("pontos", 0.7 if self.lado_vencedor == 1 else 0.4)
        self.placar = self.r["placar_depois"]
        lado = self.lado_vencedor
        x, y = self.tb.pos_placar[lado]
        self.pulso_placar[lado] = 0.5
        for _ in range(30):
            ang = random.uniform(0, math.tau)
            vel = random.uniform(80, 260)
            self.particulas.append(Particula(x, y, math.cos(ang) * vel, math.sin(ang) * vel,
                                             random.uniform(0.4, 0.8), random.choice([OURO, (255, 240, 160)]), 8))

    def pos_projetil(self, i):
        ev = self.eventos[i]
        la, lb = self.lado_de(ev["atacante"]), self.lado_de(ev["alvo"])
        ax, ay, _ = self.centro(la)
        bx, by, _ = self.centro(lb)
        k = (self.t - (self.inicio(i) + 0.12 * self.D)) / (0.43 * self.D)
        k = max(0.0, min(1.0, k))
        return entre(ax, bx, k), entre(ay, by, k) - 70 * math.sin(math.pi * k)

    def pos_voo_pontos(self):
        """Posição do '+N pontos' voando da carta vencedora até o placar."""
        k = (self.t - (self.TF + 0.4)) / 0.8
        if not (0 <= k <= 1) or not self.lado_vencedor:
            return None
        x0, y0, _ = self.centro(self.lado_vencedor)
        x1, y1 = self.tb.pos_placar[self.lado_vencedor]
        k = k * k * (3 - 2 * k)
        return entre(x0, x1, k), entre(y0 - 120, y1, k) - 90 * math.sin(math.pi * k)

    # ---------------- desenho ----------------
    def superficie_carta(self, f, carta, vida):
        chave = (id(carta), vida)
        if chave not in self.cache:
            s = pygame.Surface((CARTA_W + 24, CARTA_H + 24), pygame.SRCALPHA)
            desenhar_carta(s, f, carta, 6, 18, vida=vida)
            w, h = s.get_size()
            self.cache[chave] = pygame.transform.smoothscale(s, (int(w * self.ESCALA), int(h * self.ESCALA)))
        return self.cache[chave]

    def desenhar(self, tela, f):
        # fundo do duelo: degradê radial com a cor dos elementos em jogo
        for lado in (1, 2):
            c = self.cartas[lado]
            if c:
                cx, cy = self.CENTRO[lado]
                tela.blit(sprite_brilho(escuro(CORES_ELEMENTO[c.elemento], 0.7), 300), (cx - 300, cy - 300))
        t = self.t
        # "VS" pulsando entre as cartas
        if self.r["tipo"] == "batalha" and t > 0.3:
            k = 1 + 0.08 * math.sin(t * 6)
            img = pygame.transform.rotozoom(self.f_titulo.render("VS", True, OURO), 0, k)
            tela.blit(img, img.get_rect(center=(LARGURA // 2, 380)))

        for lado in (1, 2):
            carta = self.cartas[lado]
            cx, cy, ang = self.centro(lado)
            rotulo = "VOCÊ" if lado == 1 else "CPU"
            if carta is None:
                if self.r["tipo"] == "direto":                 # lugar vazio de quem passou
                    r = pygame.Rect(0, 0, 200, 300)
                    r.center = self.CENTRO[lado]
                    pygame.draw.rect(tela, (90, 90, 110), r, 3, border_radius=14)
                    texto(tela, f.m, f"{rotulo}: passou a vez", CINZA, r.center, centro=True)
                continue
            # brilho do vencedor
            if self.lado_vencedor == lado and t > self.TF and self.r["tipo"] == "batalha":
                raio = int(235 + 15 * math.sin(t * 8))
                tela.blit(sprite_brilho(OURO, raio), (cx - raio, cy - raio))
            surf = self.superficie_carta(f, carta, self.vida_em(carta))
            perdeu = (self.r["tipo"] == "batalha" and self.lado_vencedor and lado != self.lado_vencedor and t > self.TF)
            if perdeu:
                k = suave((t - self.TF) / 0.7)
                surf = surf.copy()
                q = int(255 - 140 * k)
                surf.fill((q, q, q, 255), special_flags=pygame.BLEND_RGBA_MULT)
            if abs(ang) > 0.3:
                surf = pygame.transform.rotate(surf, ang)
            tela.blit(surf, surf.get_rect(center=(cx, cy)))
            texto(tela, f.m, rotulo, BRANCO, (cx, cy - 190), centro=True)

        # ataque direto: a carta dispara contra o lugar vazio
        if self.r["tipo"] == "direto":
            lado = self.lado_vencedor
            k = (t - self.T0) / 0.5
            if 0 <= k <= 1:
                ax, ay, _ = self.centro(lado)
                bx, by = self.CENTRO[3 - lado]
                x, y = entre(ax, bx, k), entre(ay, by, k) - 60 * math.sin(math.pi * k)
                cor = CORES_ELEMENTO[self.cartas[lado].elemento]
                tela.blit(sprite_brilho(cor, 34), (x - 34, y - 34))
                pygame.draw.circle(tela, (255, 255, 255), (int(x), int(y)), 9)
                if random.random() < 0.9:
                    self.particulas.append(Particula(x, y, random.uniform(-50, 50), random.uniform(-50, 50), 0.35, clarear(cor, 0.4), 8))
            if (t - self.T0) >= 0.5 and not getattr(self, "_explodiu", False):
                self._explodiu = True
                bx, by = self.CENTRO[3 - lado]
                cor = CORES_ELEMENTO[self.cartas[lado].elemento]
                for _ in range(26):
                    a = random.uniform(0, math.tau); vel = random.uniform(120, 360)
                    self.particulas.append(Particula(bx, by, math.cos(a) * vel, math.sin(a) * vel, 0.6, random.choice([cor, (255, 255, 255)]), 10, 300))
                self.textos.append(TextoFlutuante("Ataque direto!", bx, by - 60, (255, 200, 90), self.f_info))

        # bolas de energia em voo
        for i, ev in enumerate(self.eventos):
            s, imp = self.inicio(i), self.impacto(i)
            if s + 0.12 * self.D <= t <= imp:
                x, y = self.pos_projetil(i)
                cor = CORES_ELEMENTO[ev["atacante"].elemento]
                tam = 40 if ev["critico"] else 30
                tela.blit(sprite_brilho(cor, tam), (x - tam, y - tam))
                tela.blit(sprite_brilho((255, 255, 255), 14), (x - 14, y - 14))

        for p in self.particulas:
            p.desenhar(tela)
        for tx in self.textos:
            tx.desenhar(tela)
        texto(tela, f.p, "clique para pular", CINZA, (LARGURA // 2, ALTURA - 18), centro=True)

    def desenhar_topo(self, tela, f):
        """Coisas desenhadas por cima do placar: pontos voando e energia gasta."""
        pos = self.pos_voo_pontos()
        if pos and self.lado_vencedor:
            g = self.ganho[self.lado_vencedor]
            if g:
                s = f"+{g} ponto" + ("s" if g > 1 else "")
                img = self.f_info.render(s, True, OURO)
                tela.blit(sprite_brilho(OURO, 46), (pos[0] - 46, pos[1] - 46))
                tela.blit(img, img.get_rect(center=pos))
        for tx in self.textos_topo:
            tx.desenhar(tela)


# ---------------------------------------------------------------------------
# Tela 2: batalha
# ---------------------------------------------------------------------------
class TelaBatalha:
    Y_MAO = ALTURA - CARTA_H - 22

    def __init__(self, baralho, dificil):
        self.baralho = baralho
        self.dificil = dificil
        self.partida = Partida(["Você", "CPU"], humanos=[True, False], baralhos=[baralho, None])
        self.log = []
        self.ultima = None
        self.duelo = None
        self.som_fim_tocado = False
        self.pos_placar = {1: (100, 34), 2: (200, 34)}   # atualizado ao desenhar o cabeçalho
        self.b_passar = Botao((900, 380, 170, 46), "Passar a vez", (160, 120, 40))
        self.b_revanche = Botao((LARGURA // 2 - 200, ALTURA // 2 + 20, 190, 44), "Revanche", (60, 170, 90))
        self.b_novo = Botao((LARGURA // 2 + 10, ALTURA // 2 + 20, 190, 44), "Novo baralho", (120, 90, 200))

    def jogar(self, c1):
        humano, cpu = self.partida.jogadores
        c2 = cpu.escolher_carta_ia(oponente=c1, ve_carta=self.dificil)
        self.log = self.partida.jogar_rodada(c1, c2, humano, cpu)
        mult = multiplicador_elemento(c1.elemento, c2.elemento) if c1 and c2 else 1
        self.ultima = (c1, c2, mult)
        self.duelo = Duelo(self.partida.ultimo, self)

    def update(self, dt):
        if self.duelo:
            self.duelo.update(dt)
            if self.duelo.acabou:
                self.duelo = None
        if not self.duelo and self.partida.acabou and not self.som_fim_tocado:
            self.som_fim_tocado = True
            humano = self.partida.jogadores[0]
            SONS.tocar("vitoria_final" if self.partida.vencedor() is humano else "derrota_final")

    def clique(self, pos):
        if self.duelo:              # clique durante a animação: pula para o fim
            self.duelo.pular()
            return None
        p = self.partida
        humano, _ = p.jogadores
        if p.acabou:
            if self.b_revanche.clicou(pos):
                SONS.tocar("botao")
                return ("revanche",)
            if self.b_novo.clicou(pos):
                SONS.tocar("botao")
                return ("montar",)
            return None
        for (x, y), carta in zip(posicoes_mao(len(humano.mao), self.Y_MAO, 880), humano.mao):
            if pygame.Rect(x, y, CARTA_W, CARTA_H).collidepoint(pos):
                if humano.pode_jogar(carta):
                    self.jogar(carta)
                else:
                    SONS.tocar("bloqueado")
                return None
        if self.b_passar.clicou(pos):
            SONS.tocar("passar")
            self.jogar(None)
        return None

    def desenhar_cabecalho(self, tela, f, placar, energias, y_energia=405):
        """Placar e barras de energia (redesenhados por cima da animação)."""
        p = self.partida
        _, cpu = p.jogadores
        pulso = self.duelo.pulso_placar if self.duelo else {1: 0, 2: 0}
        r = texto(tela, f.g, "Você", BRANCO, (30, 16))
        x = r.right + 18
        for lado, sep in ((1, "x"), (2, "CPU")):
            img = f.g.render(str(placar[lado - 1]), True, OURO if pulso[lado] > 0 else BRANCO)
            esc = 1 + 0.8 * pulso[lado]
            if esc != 1:
                img = pygame.transform.rotozoom(img, 0, esc)
            centro = (x + 10, 33)
            tela.blit(img, img.get_rect(center=centro))
            self.pos_placar[lado] = centro
            r = texto(tela, f.g, sep, BRANCO, (x + 34, 16))
            x = r.right + 18
        modo = "Difícil" if self.dificil else "Normal"
        texto(tela, f.p, f"Rodada {p.rodada + (0 if self.duelo else 1)} · Modo {modo}", CINZA, (30, 52))
        desenhar_barra_energia(tela, f, 690, 22, energias[1], "Energia CPU")
        texto(tela, f.p, f"Baralho CPU: {len(cpu.pilha)} cartas", CINZA, (690, 48))
        desenhar_barra_energia(tela, f, 30, y_energia, energias[0], "Sua energia")

    def desenhar(self, tela, f, mouse):
        p = self.partida
        humano, cpu = p.jogadores
        if self.duelo:
            placar, energias = self.duelo.placar, self.duelo.energia_mostrada()
        else:
            placar, energias = (humano.pontos, cpu.pontos), (humano.energia, cpu.energia)

        if self.duelo:
            self.duelo.desenhar(tela, f)
            self.desenhar_cabecalho(tela, f, placar, energias, y_energia=ALTURA - 32)
            self.duelo.desenhar_topo(tela, f)
            return

        self.desenhar_cabecalho(tela, f, placar, energias)

        # mão da CPU (viradas)
        for (x, y) in posicoes_mao(len(cpu.mao), 80):
            desenhar_verso(tela, x, y, h=120)

        # log da última rodada
        for i, linha in enumerate(self.log[-10:]):
            texto(tela, f.p, linha, (220, 220, 230), (30, 215 + i * 18))

        # miniatura das duas cartas da última rodada
        if self.ultima:
            c1, c2, mult = self.ultima
            for x, rotulo, c in ((560, "Você", c1), (760, "CPU", c2)):
                texto(tela, f.m, rotulo, BRANCO, (x, 212))
                r = pygame.Rect(x, 234, 150, 56)
                if c is None:
                    pygame.draw.rect(tela, PAINEL, r, border_radius=10)
                    texto(tela, f.m, "passou", CINZA, r.center, centro=True)
                else:
                    pygame.draw.rect(tela, escuro(CORES_ELEMENTO[c.elemento], 0.6), r, border_radius=10)
                    desenhar_arte(tela, c, pygame.Rect(r.x, r.y, 56, r.h), raio=10, cantos="esquerda")
                    pygame.draw.rect(tela, CORES_RARIDADE[c.raridade], r, 3, border_radius=10)
                    texto(tela, f.p, c.nome, BRANCO, (r.x + 62, r.y + 8))
                    texto(tela, f.p, c.especie_nome, BRANCO, (r.x + 62, r.y + 30))
            texto(tela, f.g, "VS", OURO, (722, 245))
            if mult != 1:
                texto(tela, f.p, "Vantagem de elemento sua!" if mult > 1 else "Desvantagem de elemento...",
                      (255, 220, 120), (560, 298))

        # sua energia, baralho e botão de passar
        texto(tela, f.p, f"Seu baralho: {len(humano.pilha)} cartas", CINZA, (360, 405))
        self.b_passar.desenhar(tela, f, mouse, ativo=not p.acabou and not self.duelo)
        texto(tela, f.p, "guarda energia, mas a", CINZA, (906, 430))
        texto(tela, f.p, "carta da CPU pontua", CINZA, (906, 447))

        # sua mão
        for (x, y), carta in zip(posicoes_mao(len(humano.mao), self.Y_MAO, 880), humano.mao):
            hover = pygame.Rect(x, y, CARTA_W, CARTA_H).collidepoint(mouse)
            desenhar_carta(tela, f, carta, x, y, destaque=hover, bloqueada=not humano.pode_jogar(carta))

        if p.acabou:
            v = p.vencedor()
            escurecer(tela, tela.get_rect(), 120)
            caixa = pygame.Rect(LARGURA // 2 - 240, ALTURA // 2 - 90, 480, 180)
            pygame.draw.rect(tela, (15, 15, 25), caixa, border_radius=16)
            pygame.draw.rect(tela, OURO, caixa, 3, border_radius=16)
            titulo = "Você venceu!" if v is humano else "A CPU venceu!"
            texto(tela, f.g, titulo, BRANCO, (caixa.centerx, caixa.y + 38), centro=True)
            texto(tela, f.p, f"Placar final: {humano.pontos} x {cpu.pontos}", CINZA,
                  (caixa.centerx, caixa.y + 72), centro=True)
            self.b_revanche.desenhar(tela, f, mouse)
            self.b_novo.desenhar(tela, f, mouse)


# ---------------------------------------------------------------------------
# Loop principal
# ---------------------------------------------------------------------------
def main():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Batalha de Cartas")
    relogio = pygame.time.Clock()
    f = Fontes()
    SONS.iniciar()

    atual = TelaAbertura()

    rodando = True
    while rodando:
        dt = min(relogio.tick(60) / 1000, 0.05)
        mouse = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_m:
                SONS.alternar()
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and ICONE_SOM.collidepoint(ev.pos):
                SONS.alternar()
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                acao = atual.clique(ev.pos)
                if not acao:
                    continue
                if acao[0] == "jogar":
                    atual = TelaBatalha(acao[1], acao[2])
                elif acao[0] == "revanche":
                    atual = TelaBatalha(atual.baralho, atual.dificil)
                elif acao[0] == "montar":
                    atual = TelaMontagem(dificil=getattr(atual, "dificil", False))

        if hasattr(atual, "update"):
            atual.update(dt)
        tela.fill(FUNDO)
        atual.desenhar(tela, f, mouse)
        desenhar_icone_som(tela, mouse)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
