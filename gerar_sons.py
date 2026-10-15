"""
Gera todos os efeitos sonoros do jogo por síntese (nenhum arquivo externo).
Saída: pasta "sons/" com arquivos .wav.

Uso (opcional - os .wav já vêm prontos):  pip install numpy  e  python gerar_sons.py
Para trocar um som, basta colocar outro .wav (ou .ogg) com o mesmo nome em sons/.
"""
import os
import sys
import wave

import numpy as np

SR = 44100
SAIDA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "sons")
rng = np.random.default_rng(7)


# ---------------------------------------------------------------------------
# Blocos básicos
# ---------------------------------------------------------------------------
def tempo(dur):
    return np.arange(int(SR * dur)) / SR


def env(n, a=0.005, d=0.1, s=0.6, r=0.1, dur=None):
    """Envelope ADSR com n amostras."""
    t = np.arange(n) / SR
    total = n / SR
    r = min(r, total * 0.9)
    e = np.ones(n) * s
    e[t < a] = t[t < a] / max(a, 1e-6)
    m = (t >= a) & (t < a + d)
    e[m] = 1 - (1 - s) * (t[m] - a) / max(d, 1e-6)
    m = t >= total - r
    e[m] *= np.linspace(1, 0, m.sum())
    return e


def decai(n, tau):
    return np.exp(-np.arange(n) / SR / tau)


def oscilador(freq, dur, forma="sine"):
    """freq pode ser número ou array (varredura de frequência)."""
    n = int(SR * dur)
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,)) if np.ndim(freq) else np.full(n, float(freq))
    fase = 2 * np.pi * np.cumsum(f) / SR
    if forma == "sine":
        return np.sin(fase)
    if forma == "tri":
        return 2 / np.pi * np.arcsin(np.sin(fase))
    if forma == "square":
        return np.tanh(4 * np.sin(fase))
    if forma == "saw":
        return 2 * ((fase / (2 * np.pi)) % 1) - 1
    raise ValueError(forma)


def metal(freq, dur, brilho):
    """Timbre de metal (trompete): harmônicos que 'abrem' com o envelope de brilho."""
    t = tempo(dur)
    out = np.zeros_like(t)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.25, 0, 1)
    for k in range(1, 14):
        amp = (1 / k) * np.power(np.clip(brilho, 1e-4, 1), k / 3.5)
        out += amp * np.sin(2 * np.pi * freq * k * np.cumsum(vib) / SR)
    return out


def ruido(dur):
    return rng.uniform(-1, 1, int(SR * dur))


def filtro(sinal, baixo=0, alto=SR / 2):
    """Passa-faixa simples por FFT (suave nas bordas)."""
    n = len(sinal)
    esp = np.fft.rfft(sinal)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if baixo > 0:
        m *= 1 / (1 + (baixo / np.maximum(f, 1)) ** 4)
    if alto < SR / 2:
        m *= 1 / (1 + (f / alto) ** 4)
    return np.fft.irfft(esp * m, n)


def filtro_variavel(sinal, centros, largura=0.6, blocos=64):
    """Passa-faixa cujo centro muda com o tempo (whoosh)."""
    n = len(sinal)
    out = np.zeros(n)
    tam = n // blocos + 1
    janela = np.hanning(tam * 2)
    for i in range(blocos):
        ini = max(0, i * tam - tam // 2)
        fim = min(n, ini + tam * 2)
        c = centros[min(n - 1, (ini + fim) // 2)]
        trecho = filtro(sinal[ini:fim] * janela[:fim - ini], c * (1 - largura), c * (1 + largura))
        out[ini:fim] += trecho
    return out


def reverb(sinal, tamanho=1.2, mistura=0.25):
    ir = ruido(tamanho) * decai(int(SR * tamanho), tamanho / 5)
    ir = filtro(ir, 200, 6000)
    tam = len(sinal) + len(ir) - 1                      # convolução rápida via FFT
    molhado = np.fft.irfft(np.fft.rfft(sinal, tam) * np.fft.rfft(ir, tam), tam)
    molhado = molhado[:len(sinal) + int(SR * tamanho * 0.6)]
    molhado /= max(1e-9, np.abs(molhado).max())
    seco = np.concatenate([sinal, np.zeros(len(molhado) - len(sinal))])
    return seco * (1 - mistura) + molhado * mistura * np.abs(sinal).max()


def junta(*partes):
    """Mistura (inicio_em_segundos, sinal) num só sinal."""
    fim = max(int(SR * ini) + len(s) for ini, s in partes)
    out = np.zeros(fim)
    for ini, s in partes:
        i = int(SR * ini)
        out[i:i + len(s)] += s
    return out


def nota(nome):
    notas = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    base, oit = nome[:-1], int(nome[-1])
    semi = notas[base[0]] + (1 if "#" in base else -1 if "b" in base[1:] else 0)
    return 440 * 2 ** ((semi + (oit - 4) * 12) / 12)


def salvar(nome, sinal, volume=0.85):
    sinal = np.asarray(sinal, dtype=float)
    pico = np.abs(sinal).max()
    if pico > 0:
        sinal = sinal / pico * volume
    n = len(sinal)
    borda = min(200, n // 4)                   # evita estalos no começo/fim
    sinal[:borda] *= np.linspace(0, 1, borda)
    sinal[-borda:] *= np.linspace(1, 0, borda)
    dados = (np.clip(sinal, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(os.path.join(SAIDA, nome + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(dados)


# ---------------------------------------------------------------------------
# Instrumentos
# ---------------------------------------------------------------------------
def trompete(freq, dur, forte=1.0):
    n = int(SR * dur)
    e = env(n, a=0.03, d=0.15, s=0.75, r=min(0.2, dur * 0.4))
    brilho = 0.35 + 0.65 * e
    s = metal(freq, dur, brilho * forte) + 0.6 * metal(freq * 1.003, dur, brilho * forte)
    return s * e


def sino(freq, dur, tau=0.4):
    n = int(SR * dur)
    s = (np.sin(2 * np.pi * freq * tempo(dur)) + 0.4 * np.sin(2 * np.pi * freq * 2.01 * tempo(dur))
         + 0.15 * np.sin(2 * np.pi * freq * 3.98 * tempo(dur)))
    return s * decai(n, tau) * env(n, a=0.002, d=0.01, s=1, r=0.02)


def tambor(freq=70, dur=0.6, forca=1.0):
    n = int(SR * dur)
    f = freq * (1 + 1.5 * decai(n, 0.03))
    corpo = oscilador(f, dur) * decai(n, dur / 3.5)
    ataque = filtro(ruido(dur), 100, 2500) * decai(n, 0.02)
    return (corpo + 0.5 * ataque) * forca


def prato(dur=2.0):
    n = int(SR * dur)
    return filtro(ruido(dur), 4000, 16000) * decai(n, dur / 4)


# ---------------------------------------------------------------------------
# Sons do jogo
# ---------------------------------------------------------------------------
def abertura():
    """Fanfarra de abertura (~4 s): rufar, motivo de metais e acorde final."""
    partes = []
    # rufar de tímpano crescendo
    for i in range(14):
        t = i * 0.045
        partes.append((t, tambor(65, 0.35, 0.25 + 0.6 * i / 14)))
    partes.append((0.62, tambor(55, 1.0, 1.4)))
    # motivo: G3 C4 E4 | G4 ... | F4+A4 | G4+B4+D5 | C5 acorde
    motivo = [(0.65, "G3", 0.16), (0.82, "C4", 0.16), (0.99, "E4", 0.16), (1.16, "G4", 0.55),
              (1.75, "E4", 0.14), (1.9, "G4", 0.5)]
    for ini, n_, d in motivo:
        partes.append((ini, trompete(nota(n_), d) * 0.7))
        partes.append((ini, trompete(nota(n_) / 2, d) * 0.35))
    for ini, acorde, d in [(2.45, ["F3", "A3", "C4", "F4", "A4"], 0.42),
                           (2.9, ["G3", "B3", "D4", "G4", "B4"], 0.42)]:
        for n_ in acorde:
            partes.append((ini, trompete(nota(n_), d) * 0.32))
        partes.append((ini, tambor(60, 0.4, 0.8)))
    final = ["C3", "G3", "C4", "E4", "G4", "C5"]
    for n_ in final:
        partes.append((3.35, trompete(nota(n_), 1.9, 1.0) * 0.3))
    partes.append((3.35, tambor(50, 1.4, 1.6)))
    partes.append((3.35, prato(2.4) * 0.5))
    # brilhos subindo no acorde final
    for i, n_ in enumerate(["C6", "E6", "G6", "C7"]):
        partes.append((3.4 + i * 0.08, sino(nota(n_), 1.2, 0.35) * 0.25))
    return reverb(junta(*partes), 1.8, 0.3)


def selecionar():
    a = sino(nota("E6"), 0.12, 0.05)
    b = sino(nota("B6"), 0.18, 0.08)
    return junta((0, a), (0.055, b))


def desmarcar():
    a = sino(nota("B5"), 0.12, 0.05)
    b = sino(nota("E5"), 0.16, 0.07)
    return junta((0, a), (0.055, b))


def bloqueado():
    s = oscilador(140, 0.16, "square") * env(int(SR * 0.16), a=0.005, d=0.05, s=0.6, r=0.05)
    s2 = oscilador(148, 0.16, "square") * env(int(SR * 0.16), a=0.005, d=0.05, s=0.6, r=0.05)
    return filtro(s + s2, 0, 1500)


def botao():
    n = int(SR * 0.07)
    return oscilador(1200 * (0.6 + 0.4 * decai(n, 0.01)), 0.07, "tri") * decai(n, 0.018)


def whoosh(dur=0.4, f0=300, f1=2500, f2=500):
    n = int(SR * dur)
    t = np.linspace(0, 1, n)
    centros = np.where(t < 0.5, f0 + (f1 - f0) * (t / 0.5), f1 + (f2 - f1) * ((t - 0.5) / 0.5))
    s = filtro_variavel(ruido(dur), centros, 0.5)
    return s * np.sin(np.pi * t) ** 1.5


def carta():
    return junta((0, whoosh(0.38, 400, 3000, 800)), (0.02, sino(nota("A5"), 0.3, 0.1) * 0.15))


def entrada():
    return junta((0, whoosh(0.55, 200, 1800, 300)), (0.42, tambor(80, 0.4, 0.7)))


def disparo():
    n = int(SR * 0.3)
    f = np.linspace(260, 1400, n) ** 1
    zum = oscilador(f, 0.3, "saw") * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return filtro(zum, 200, 4000) * 0.5 + whoosh(0.3, 600, 4000, 2000) * 0.8


def impacto_fogo():
    d = 0.7
    n = int(SR * d)
    boom = tambor(75, d, 1.0)
    chiado = filtro(ruido(d), 300, 5000) * decai(n, 0.18)
    estalos = np.zeros(n)
    for _ in range(40):                                   # crepitar
        i = rng.integers(0, int(n * 0.85))
        k = rng.integers(40, 160)
        estalos[i:i + k] += rng.uniform(-1, 1, k) * rng.uniform(0.3, 1) * decai(k, 0.001)
    return boom + 0.8 * chiado + 0.6 * filtro(estalos, 1000, 9000) * decai(n, 0.4)


def impacto_agua():
    d = 0.7
    n = int(SR * d)
    respingo = filtro(ruido(d), 800, 6000) * decai(n, 0.12)
    bolhas = []
    for _ in range(9):
        f0 = rng.uniform(500, 1100)
        dd = rng.uniform(0.04, 0.09)
        nn = int(SR * dd)
        bolhas.append((rng.uniform(0.05, 0.5), oscilador(np.linspace(f0, f0 * 1.8, nn), dd) * decai(nn, dd / 2) * 0.18))
    return junta((0, respingo), (0, tambor(90, 0.4, 0.6)), *bolhas)


def impacto_planta():
    d = 0.6
    n = int(SR * d)
    baque = tambor(110, d, 0.9)
    farfalhar = filtro(ruido(d), 2500, 9000) * decai(n, 0.2) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * tempo(d)))
    graveto = filtro(ruido(0.03), 1500, 6000) * decai(int(SR * 0.03), 0.006)
    return junta((0, baque), (0, farfalhar * 0.7), (0.0, graveto * 1.5))


def impacto_eletrico():
    d = 0.6
    n = int(SR * d)
    f = 110 * (1 + 0.5 * rng.standard_normal(n).cumsum() / np.sqrt(np.arange(1, n + 1)) * 0.3)
    zap = oscilador(np.abs(f) + 60, d, "saw")
    tremor = (rng.uniform(size=n // 400 + 1) > 0.3).repeat(400)[:n]
    estalo = filtro(ruido(d), 3000, 12000) * tremor
    return (filtro(zap, 80, 6000) * 0.7 + estalo * 0.5) * decai(n, 0.16) + tambor(90, d, 0.5)


def impacto_terra():
    d = 0.9
    n = int(SR * d)
    boom = tambor(48, d, 1.4)
    ronco = filtro(ruido(d), 30, 300) * decai(n, 0.35)
    pedras = []
    for _ in range(10):
        dd = 0.02
        pedras.append((rng.uniform(0.05, 0.5), filtro(ruido(dd), 800, 4000) * decai(int(SR * dd), 0.005) * rng.uniform(0.08, 0.25)))
    return junta((0, boom), (0, ronco * 1.2), *pedras)


def impacto_sombra():
    d = 0.8
    n = int(SR * d)
    t = tempo(d)
    grave = sum(np.sin(2 * np.pi * f * t) for f in (73, 77.8, 110.5))
    grave *= np.minimum(1, t / 0.05) * decai(n, 0.25)
    sopro = filtro(ruido(d), 200, 1200) * np.sin(np.pi * np.linspace(0, 1, n)) * 0.8
    return reverb(grave * 0.6 + sopro + tambor(60, d, 0.6), 1.0, 0.35)


def critico():
    d = 0.9
    n = int(SR * d)
    t = tempo(d)
    anel = sum(a * np.sin(2 * np.pi * 620 * r * t) for r, a in ((1, 1), (2.76, 0.6), (5.4, 0.35), (8.93, 0.2)))
    return anel * decai(n, 0.22) * 0.6 + tambor(55, d, 1.2)


def esquiva():
    return whoosh(0.25, 1500, 6000, 3000)


def cura():
    return junta(*[(i * 0.07, sino(nota(n_), 0.6, 0.25) * 0.6) for i, n_ in enumerate(["C6", "E6", "G6", "C7"])])


def furia():
    d = 0.5
    n = int(SR * d)
    s = oscilador(np.linspace(95, 70, n), d, "saw") * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * tempo(d)))
    return np.tanh(3 * filtro(s, 40, 1200)) * env(n, a=0.04, d=0.1, s=0.8, r=0.15)


def energia():
    return junta(*[(i * 0.05, sino(nota(n_), 0.3, 0.08) * 0.5) for i, n_ in enumerate(["A6", "E6", "C6"])])


def passar():
    n = int(SR * 0.3)
    return oscilador(np.linspace(600, 260, n), 0.3, "tri") * env(n, a=0.01, d=0.1, s=0.5, r=0.12) * 0.6


def vitoria():
    partes = [(0, trompete(nota("C5"), 0.13)), (0.13, trompete(nota("E5"), 0.13)),
              (0.26, trompete(nota("G5"), 0.13))]
    for n_ in ("C5", "E5", "G5", "C6"):
        partes.append((0.4, trompete(nota(n_), 0.7) * 0.5))
    return reverb(junta(*partes), 1.0, 0.25)


def derrota():
    partes = [(i * 0.22, oscilador(nota(n_), 0.32, "tri") * env(int(SR * 0.32), 0.01, 0.1, 0.6, 0.12))
              for i, n_ in enumerate(["G4", "E4", "C4"])]
    partes.append((0.66, oscilador(nota("B3") * np.ones(int(SR * 0.7)), 0.7, "tri") * decai(int(SR * 0.7), 0.3)))
    return reverb(junta(*partes), 0.8, 0.2)


def empate():
    return junta((0, sino(nota("G5"), 0.4, 0.15)), (0.15, sino(nota("G5"), 0.5, 0.2)))


def pontos():
    return junta((0, sino(nota("B5"), 0.25, 0.08)), (0.08, sino(nota("E6"), 0.7, 0.3)),
                 (0.08, sino(nota("B6"), 0.5, 0.2) * 0.3))


def vitoria_final():
    partes = []
    seq = [(0.0, "G4", 0.15), (0.16, "C5", 0.15), (0.32, "E5", 0.15), (0.48, "G5", 0.35),
           (0.86, "E5", 0.13), (1.0, "G5", 0.6)]
    for ini, n_, d in seq:
        partes.append((ini, trompete(nota(n_), d) * 0.7))
    for n_ in ("C4", "G4", "C5", "E5", "G5", "C6"):
        partes.append((1.62, trompete(nota(n_), 1.6) * 0.35))
    partes += [(1.62, tambor(55, 1.2, 1.4)), (1.62, prato(2.2) * 0.45)]
    partes += [(1.7 + i * 0.07, sino(nota(n_), 1.0, 0.3) * 0.25) for i, n_ in enumerate(["E6", "G6", "C7", "E7"])]
    return reverb(junta(*partes), 1.6, 0.3)


def derrota_final():
    partes = []
    for i, (acorde, d) in enumerate([(["A3", "C4", "E4"], 0.6), (["F3", "A3", "C4"], 0.6),
                                     (["D3", "F3", "A3"], 0.6), (["E3", "G#3", "B3"], 1.3)]):
        for n_ in acorde:
            nn = int(SR * d)
            partes.append((i * 0.55, oscilador(nota(n_), d, "tri") * env(nn, 0.05, 0.2, 0.6, 0.25) * 0.4))
    partes.append((1.65, tambor(45, 1.0, 0.8)))
    return reverb(junta(*partes), 1.6, 0.35)


SONS = {
    "abertura": abertura, "selecionar": selecionar, "desmarcar": desmarcar, "bloqueado": bloqueado,
    "botao": botao, "carta": carta, "entrada": entrada, "disparo": disparo,
    "impacto_fogo": impacto_fogo, "impacto_agua": impacto_agua, "impacto_planta": impacto_planta,
    "impacto_eletrico": impacto_eletrico, "impacto_terra": impacto_terra, "impacto_sombra": impacto_sombra,
    "critico": critico, "esquiva": esquiva, "cura": cura, "furia": furia, "energia": energia,
    "passar": passar, "vitoria": vitoria, "derrota": derrota, "empate": empate, "pontos": pontos,
    "vitoria_final": vitoria_final, "derrota_final": derrota_final,
}

if __name__ == "__main__":
    os.makedirs(SAIDA, exist_ok=True)
    for nome, func in SONS.items():
        salvar(nome, func())
    print(f"{len(SONS)} sons gerados em {SAIDA}")
