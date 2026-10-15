"""Gera as ilustrações das cartas (SVG -> PNG). Saída: ./imagens/<especie>.png"""
import os, sys, cairosvg

SAIDA = sys.argv[1] if len(sys.argv) > 1 else "imagens"
os.makedirs(SAIDA, exist_ok=True)

O = 'stroke="#1b1020" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"'
O2 = 'stroke="#1b1020" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"'


def lg(id_, *stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in
                [(st if len(st) == 3 else (*st, 1)) for st in stops])
    return f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rg(id_, *stops, cx=0.5, cy=0.5, r=0.5):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in
                [(st if len(st) == 3 else (*st, 1)) for st in stops])
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'


def espelho(svg):
    return f'<g transform="translate(300,0) scale(-1,1)">{svg}</g>'


def brilho(cx, cy, r, cor):
    """Halo luminoso (substitui blur, que o cairosvg não suporta)."""
    gid = f"gl{cx}_{cy}_{r}".replace(".", "_")
    return (f'<defs>{rg(gid, (0, cor, 0.9), (0.4, cor, 0.35), (1, cor, 0))}</defs>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"/>')


# ---------------------------------------------------------------------------
# Cenários por elemento
# ---------------------------------------------------------------------------
def fundo(elemento):
    if elemento == "Fogo":
        return (f'<defs>{lg("bg", (0, "#2a0606"), (0.55, "#8a1e0c"), (1, "#f07a26"))}</defs>'
                '<rect width="300" height="220" fill="url(#bg)"/>'
                + brilho(150, 200, 160, "#ffb347") +
                '<path d="M0,190 L40,150 L60,160 L95,120 L120,150 L140,140 L170,175 L200,130 L230,160 L260,120 L300,165 L300,220 L0,220 Z" fill="#3a0c08" opacity="0.85"/>'
                '<path d="M92,124 L98,118 L102,126 Z M197,134 L202,128 L206,136 Z" fill="#ff9a30"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffcf5a" opacity="{o}"/>' for x, y, r, o in
                          [(30, 60, 2, .8), (70, 30, 1.5, .6), (260, 70, 2, .7), (230, 30, 1.5, .6), (120, 20, 1.2, .5),
                           (280, 140, 1.8, .7), (15, 120, 1.4, .6), (190, 50, 1.2, .5)]))
    if elemento == "Água":
        return (f'<defs>{lg("bg", (0, "#04223f"), (0.6, "#0b5c86"), (1, "#18a3b8"))}</defs>'
                '<rect width="300" height="220" fill="url(#bg)"/>'
                '<path d="M60,0 L100,0 L60,220 L20,220 Z M160,0 L185,0 L150,220 L120,220 Z M240,0 L270,0 L260,220 L225,220 Z" fill="#ffffff" opacity="0.06"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#bff3ff" stroke-width="1.2" opacity="{o}"/>'
                          for x, y, r, o in [(30, 80, 4, .6), (40, 60, 2.5, .5), (265, 90, 5, .6), (255, 60, 3, .5),
                                             (275, 40, 2, .4), (20, 150, 3, .5), (285, 160, 2.5, .5)]))
    if elemento == "Planta":
        return (f'<defs>{lg("bg", (0, "#0c3219"), (0.6, "#2f7a3a"), (1, "#86c25a"))}</defs>'
                '<rect width="300" height="220" fill="url(#bg)"/>'
                '<path d="M100,0 L140,0 L230,220 L170,220 Z" fill="#fff6b0" opacity="0.10"/>'
                '<path d="M20,0 L40,0 L110,220 L70,220 Z" fill="#fff6b0" opacity="0.07"/>'
                + "".join(f'<path d="M{x},{y} l-18,40 h12 l-16,34 h12 l-14,30 h48 l-14,-30 h12 l-16,-34 h12 Z" fill="#0a2a14" opacity="0.7"/>'
                          for x, y in [(25, 70), (275, 60), (60, 100), (245, 95)]) +
                '<path d="M0,205 Q30,195 60,205 T120,205 T180,205 T240,205 T300,205 L300,220 L0,220 Z" fill="#1d5c25"/>')
    if elemento == "Elétrico":
        return (f'<defs>{lg("bg", (0, "#120a33"), (0.6, "#3a2c7a"), (1, "#6b5bb8"))}</defs>'
                '<rect width="300" height="220" fill="url(#bg)"/>'
                + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#1c1446" opacity="0.8"/>'
                          for x, y, rx, ry in [(40, 20, 70, 22), (140, 8, 80, 20), (250, 22, 75, 24)]) +
                '<path d="M40,30 L55,62 L44,64 L62,100" fill="none" stroke="#fff27a" stroke-width="3" stroke-linejoin="round"/>'
                '<path d="M258,36 L244,70 L256,72 L238,112" fill="none" stroke="#fff27a" stroke-width="3" stroke-linejoin="round"/>'
                + brilho(60, 98, 22, "#fff27a") + brilho(240, 110, 22, "#fff27a"))
    if elemento == "Terra":
        return (f'<defs>{lg("bg", (0, "#5a3414"), (0.55, "#b9783a"), (1, "#e8b46a"))}</defs>'
                '<rect width="300" height="220" fill="url(#bg)"/>'
                + brilho(230, 50, 50, "#ffe2a0") +
                '<path d="M0,150 L0,110 L30,110 L35,100 L70,100 L75,150 Z M220,150 L225,95 L260,95 L262,85 L300,85 L300,150 Z" fill="#6b3a1a" opacity="0.8"/>'
                '<path d="M0,185 Q75,165 150,180 T300,175 L300,220 L0,220 Z" fill="#7a4a22"/>')
    # Sombra
    return (f'<defs>{lg("bg", (0, "#07040d"), (0.6, "#24123a"), (1, "#4a2a6a"))}</defs>'
            '<rect width="300" height="220" fill="url(#bg)"/>'
            + brilho(245, 48, 55, "#e8dcff") +
            '<circle cx="245" cy="48" r="24" fill="#f1ebff"/><circle cx="236" cy="42" r="5" fill="#d8ccf0"/><circle cx="252" cy="56" r="3.5" fill="#d8ccf0"/>'
            + "".join(f'<path d="M{x},{y} q5,-6 10,0 q5,-6 10,0 q-5,1 -10,7 q-5,-6 -10,-7 Z" fill="#0b0614" transform="scale(1)"/>'
                      for x, y in [(40, 40), (70, 25), (200, 90)]) +
            '<ellipse cx="80" cy="212" rx="120" ry="14" fill="#9b86c8" opacity="0.15"/>'
            '<ellipse cx="230" cy="215" rx="110" ry="12" fill="#9b86c8" opacity="0.15"/>')


def sombra_chao(cx=150, cy=204, rx=70):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="9" fill="#000" opacity="0.35"/>'


# ---------------------------------------------------------------------------
# Criaturas
# ---------------------------------------------------------------------------
def dragao():
    d = "<defs>" + lg("corpo", (0, "#e8432e"), (1, "#8a140f")) + lg("asa", (0, "#b3231a"), (1, "#4e0a0a"), x2=1, y2=1) \
        + lg("barriga", (0, "#ffe08a"), (1, "#f0a03a")) + lg("fogo", (0, "#fff5b0"), (0.4, "#ffb02e"), (1, "#ff4a1a", 0), x2=1, y2=0) + "</defs>"
    asa_fundo = f'<path d="M168,104 L232,22 Q236,50 256,54 Q252,76 272,86 Q256,100 262,116 Q222,110 182,128 Z" fill="#5c0d0d" {O}/>' \
                '<path d="M168,104 L232,22 M175,110 L256,54 M178,116 L272,86" stroke="#2a0606" stroke-width="2.5" fill="none"/>'
    asa_frente = f'<path d="M150,108 L95,28 Q90,58 70,62 Q72,86 50,92 Q66,108 58,126 Q100,118 138,136 Z" fill="url(#asa)" {O}/>' \
                 '<path d="M150,108 L95,28 M146,112 L70,62 M142,118 L50,92 M140,126 L58,126" stroke="#3a0808" stroke-width="2.5" fill="none"/>'
    cauda = f'<path d="M130,150 C105,174 72,192 44,178 C36,174 32,166 36,160 C54,170 78,166 100,150 C110,143 118,138 124,134 Z" fill="url(#corpo)" {O}/>' \
            f'<path d="M38,164 L14,150 L24,170 L10,184 L44,178 Z" fill="#8a140f" {O}/>'
    perna_tras = f'<path d="M128,152 C118,168 116,182 120,194 L106,198 L136,198 L138,188 C140,176 144,166 147,158 Z" fill="#a31a12" {O}/>'
    corpo = f'<path d="M118,150 C110,120 135,97 165,99 C193,102 206,130 192,158 C180,182 130,184 118,150 Z" fill="url(#corpo)" {O}/>'
    barriga = f'<path d="M152,118 C168,118 184,130 184,150 C180,168 162,176 148,170 C154,152 152,136 152,118 Z" fill="url(#barriga)" {O2}/>' \
              '<path d="M154,130 Q168,128 182,136 M153,142 Q168,140 184,148 M152,154 Q166,154 180,162" stroke="#c97a22" stroke-width="1.6" fill="none"/>'
    espinhos = "".join(f'<path d="M{x},{y} L{x+4},{y-11} L{x+9},{y+1} Z" fill="#ffcf5a" {O2}/>' for x, y in
                       [(128, 110), (140, 101), (153, 97), (166, 96)])
    pescoco = f'<path d="M163,110 C168,92 177,79 190,70 L206,80 C194,90 188,104 186,122 Z" fill="url(#corpo)" {O}/>'
    chifres = f'<path d="M196,58 C188,48 186,36 174,26 C192,32 202,44 205,54 Z" fill="#f6e6c0" {O2}/>' \
              f'<path d="M207,54 C205,42 210,32 204,20 C216,30 219,44 216,54 Z" fill="#f6e6c0" {O2}/>'
    cabeca = f'<path d="M186,72 C186,58 198,50 214,52 L246,60 C252,63 251,72 245,74 L222,80 C208,86 190,84 186,72 Z" fill="url(#corpo)" {O}/>' \
             '<path d="M222,73 L246,69" stroke="#3a0808" stroke-width="1.8"/>' \
             '<ellipse cx="211" cy="63" rx="5.5" ry="4" fill="#ffe14a" stroke="#1b1020" stroke-width="1.4"/>' \
             '<rect x="210" y="59.5" width="2" height="7" rx="1" fill="#1b1020"/><circle cx="241" cy="64" r="1.6" fill="#3a0808"/>'
    fogo = '<path d="M248,62 C262,52 282,58 300,44 L300,92 C284,80 266,82 248,72 Z" fill="url(#fogo)"/>' + brilho(256, 68, 16, "#fff3a0")
    pernas = f'<path d="M176,150 C182,166 186,178 184,194 L172,198 L200,198 L198,188 C198,174 196,160 192,148 Z" fill="#b51e14" {O}/>' \
             '<path d="M176,198 l3,-5 M184,198 l3,-5 M192,198 l3,-5" stroke="#f6e6c0" stroke-width="2"/>'
    return d + sombra_chao(150, 200, 80) + asa_fundo + cauda + perna_tras + asa_frente + corpo + barriga + espinhos + pescoco + chifres + cabeca + pernas + fogo


def fenix():
    d = "<defs>" + lg("asaF", (0, "#fff2a0"), (0.45, "#ff9a2a"), (1, "#c81e10"), x1=1, y1=1, x2=0, y2=0) \
        + lg("corpoF", (0, "#ffd45a"), (1, "#e2541a")) + lg("caudaF", (0, "#ffb23a"), (1, "#c81e10", 0.2)) + "</defs>"
    asa = (f'<path d="M140,112 C110,80 70,58 22,46 C40,60 44,68 40,78 C56,80 62,86 56,98 C72,98 78,104 72,116 '
           f'C88,114 96,120 90,132 C108,128 124,130 140,138 Z" fill="url(#asaF)" {O}/>'
           '<path d="M132,116 C110,96 86,84 58,78 M130,124 C112,110 96,104 76,104 M130,132 C116,124 104,120 92,122" '
           'stroke="#c8461b" stroke-width="1.6" fill="none"/>')
    cauda = (f'<path d="M142,150 C132,178 112,196 92,216 C120,208 140,190 148,165 Z" fill="url(#caudaF)" {O2}/>'
             f'<path d="M146,152 C144,182 150,200 146,220 C160,200 158,180 154,152 Z" fill="url(#caudaF)" {O2}/>')
    corpo = f'<ellipse cx="150" cy="122" rx="20" ry="32" fill="url(#corpoF)" {O}/>' \
            '<path d="M140,112 Q150,118 160,112 M138,124 Q150,130 162,124 M140,136 Q150,142 160,136" stroke="#f08a2a" stroke-width="1.6" fill="none"/>'
    crista = (f'<path d="M144,72 C134,54 138,40 128,28 C146,38 152,52 151,68 Z" fill="#ff6a1a" {O2}/>'
              f'<path d="M149,70 C148,52 156,38 151,20 C166,36 162,54 155,70 Z" fill="#ffb02e" {O2}/>'
              f'<path d="M156,72 C166,54 162,40 172,28 C154,38 148,52 149,68 Z" fill="#ff6a1a" {O2}/>')
    cabeca = f'<circle cx="150" cy="84" r="15" fill="url(#corpoF)" {O}/>' \
             f'<path d="M145,88 L150,101 L155,88 Z" fill="#ffe680" {O2}/>' \
             '<ellipse cx="144" cy="82" rx="2.6" ry="3.2" fill="#1b1020"/><ellipse cx="156" cy="82" rx="2.6" ry="3.2" fill="#1b1020"/>' \
             '<circle cx="145" cy="81" r="0.9" fill="#fff"/><circle cx="157" cy="81" r="0.9" fill="#fff"/>'
    return d + brilho(150, 110, 110, "#ffd06a") + asa + espelho(asa) + cauda + espelho(cauda) + corpo + crista + cabeca


def sereia():
    d = "<defs>" + lg("cauda", (0, "#3ad1c4"), (1, "#16608a")) + lg("rocha", (0, "#7d8a99"), (1, "#3a4452")) \
        + lg("cabelo", (0, "#d4569a"), (1, "#7a2a8a")) + lg("pele", (0, "#ffd9bf"), (1, "#f0b590")) + "</defs>"
    rocha = f'<path d="M66,206 C76,174 118,162 160,168 C202,162 236,176 244,206 Z" fill="url(#rocha)" {O}/>'
    cabelo_tras = f'<path d="M136,70 C128,54 142,46 152,46 C170,46 178,60 170,78 C178,104 184,124 178,146 C170,132 166,120 162,110 C164,98 140,98 138,110 C134,124 130,134 124,144 C120,116 126,92 136,70 Z" fill="url(#cabelo)" {O}/>'
    cauda = (f'<path d="M134,146 C128,170 150,186 180,186 C200,186 212,180 222,170 L228,158 C238,168 252,168 260,158 '
             f'C254,176 242,188 226,190 C238,196 252,202 258,214 C238,214 224,206 216,194 C198,202 168,204 146,194 '
             f'C124,184 118,164 124,146 Z" fill="url(#cauda)" {O}/>'
             + "".join(f'<path d="M{x},{y} q5,6 10,0" stroke="#bff3ff" stroke-width="1.3" fill="none" opacity="0.8"/>'
                       for x, y in [(136, 160), (148, 166), (160, 172), (172, 176), (184, 178), (142, 176), (156, 182), (170, 186), (196, 176)]))
    tronco = f'<path d="M136,148 C132,128 136,110 141,100 L161,100 C166,112 168,128 164,148 Z" fill="url(#pele)" {O}/>' \
             f'<path d="M136,112 C144,119 158,119 166,112 L166,123 C158,128 144,128 136,123 Z" fill="#8a3aa8" {O2}/>'
    tridente = '<path d="M116,52 L116,196" stroke="#1b1020" stroke-width="6"/><path d="M116,52 L116,196" stroke="#f2c84a" stroke-width="3.4"/>' \
               f'<path d="M104,40 L104,58 Q116,66 128,58 L128,40 M116,34 L116,58" fill="none" stroke="#1b1020" stroke-width="5.5" stroke-linecap="round"/>' \
               f'<path d="M104,40 L104,58 Q116,66 128,58 L128,40 M116,34 L116,58" fill="none" stroke="#f2c84a" stroke-width="3" stroke-linecap="round"/>' + brilho(116, 44, 20, "#bff3ff")
    braco_e = f'<path d="M140,104 C130,110 124,118 120,126 L127,131 C131,122 137,116 145,112 Z" fill="url(#pele)" {O2}/><circle cx="120" cy="128" r="5" fill="#ffd9bf" {O2}/>'
    braco_d = f'<path d="M161,104 C172,114 176,126 172,142 L165,141 C167,128 164,118 157,111 Z" fill="url(#pele)" {O2}/>'
    pescoco = '<rect x="146" y="88" width="10" height="14" fill="#f5c4a2"/>'
    rosto = f'<ellipse cx="151" cy="78" rx="14" ry="16" fill="url(#pele)" {O}/>' \
            '<ellipse cx="146" cy="78" rx="2" ry="2.6" fill="#1b1020"/><ellipse cx="157" cy="78" rx="2" ry="2.6" fill="#1b1020"/>' \
            '<path d="M147,86 Q151.5,89 156,86" stroke="#a04a4a" stroke-width="1.5" fill="none"/>' \
            '<circle cx="142" cy="84" r="2.5" fill="#ff8aa0" opacity="0.5"/><circle cx="161" cy="84" r="2.5" fill="#ff8aa0" opacity="0.5"/>'
    franja = f'<path d="M137,76 C136,60 146,54 156,56 C164,58 168,66 166,74 C160,66 150,64 144,68 C140,70 139,74 137,76 Z" fill="url(#cabelo)" {O2}/>' \
             '<circle cx="164" cy="64" r="3" fill="#fff" stroke="#1b1020" stroke-width="1"/>'
    ondas = '<path d="M0,204 Q20,196 40,204 T80,204 T120,204 T160,204 T200,204 T240,204 T280,204 T320,204 L300,220 L0,220 Z" fill="#0b5c86" opacity="0.9"/>' \
            '<path d="M0,204 Q20,196 40,204 T80,204 T120,204 T160,204 T200,204 T240,204 T280,204 T320,204" stroke="#bff3ff" stroke-width="2" fill="none"/>'
    return d + rocha + cabelo_tras + cauda + tridente + braco_d + tronco + braco_e + pescoco + rosto + franja + ondas


def kraken():
    d = "<defs>" + lg("pele", (0, "#c2457a"), (1, "#5a1a4a")) + lg("tent", (0, "#b23a70"), (1, "#5a1a4a"), x2=1, y2=1) + "</defs>"
    t1 = (f'<path d="M104,150 C70,140 48,112 58,80 C64,64 84,62 88,76 C80,74 72,80 72,90 C70,112 90,130 114,140 Z" fill="url(#tent)" {O}/>'
          + "".join(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#ffc2d8" {O2}/>' for x, y in [(76, 100), (84, 118), (98, 132), (74, 84)]))
    t2 = (f'<path d="M108,166 C82,176 48,172 32,152 C26,142 34,130 44,136 C42,146 52,154 68,154 C86,154 98,150 110,146 Z" fill="url(#tent)" {O}/>'
          + "".join(f'<circle cx="{x}" cy="{y}" r="2.4" fill="#ffc2d8" {O2}/>' for x, y in [(50, 150), (64, 158), (80, 160), (94, 158)]))
    cabeca = (f'<path d="M96,168 C86,100 116,46 158,46 C200,46 228,100 214,168 Z" fill="url(#pele)" {O}/>'
              + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffb0cc" opacity="0.35"/>' for x, y, r in
                        [(130, 70, 6), (176, 64, 5), (190, 90, 4), (120, 92, 4), (160, 58, 3)]))
    olhos = ""
    for x in (130, 182):
        olhos += f'<ellipse cx="{x}" cy="118" rx="15" ry="12" fill="#ffd84a" {O}/>' \
                 f'<rect x="{x-10}" y="115.5" width="20" height="5" rx="2.5" fill="#1b1020"/>' \
                 f'<path d="M{x-17},104 Q{x},96 {x+17},104" stroke="#3a0a2a" stroke-width="4" fill="none" stroke-linecap="round"/>'
    agua = '<path d="M0,172 Q25,162 50,172 T100,172 T150,172 T200,172 T250,172 T300,172 L300,220 L0,220 Z" fill="#0a4a72"/>' \
           '<path d="M0,172 Q25,162 50,172 T100,172 T150,172 T200,172 T250,172 T300,172" stroke="#bff3ff" stroke-width="2.4" fill="none"/>' \
           '<path d="M40,192 q10,-5 20,0 M120,198 q10,-5 20,0 M200,190 q10,-5 20,0 M250,204 q10,-5 20,0" stroke="#7fd8f0" stroke-width="1.6" fill="none"/>'
    return d + t1 + t2 + espelho(t1 + t2) + cabeca + olhos + agua


def elfo():
    d = "<defs>" + lg("capa", (0, "#2f7a3a"), (1, "#123d1c")) + lg("tunica", (0, "#7cc46a"), (1, "#3f8a3a")) \
        + lg("pele", (0, "#ffe2c8"), (1, "#f2bf98")) + lg("cab", (0, "#fff0a0"), (1, "#e2b84a")) + "</defs>"
    capa = f'<path d="M104,216 C108,160 120,118 150,100 C180,118 192,160 196,216 Z" fill="url(#capa)" {O}/>'
    capuz = f'<path d="M120,88 C116,58 134,40 152,40 C172,40 188,58 182,90 C176,104 126,104 120,88 Z" fill="url(#capa)" {O}/>'
    cabelo = f'<path d="M132,70 C128,90 128,110 122,126 C134,118 138,104 140,88 Z M170,70 C174,90 176,110 182,126 C168,118 164,104 162,88 Z" fill="url(#cab)" {O2}/>'
    orelhas = f'<path d="M137,74 L114,58 L136,84 Z" fill="url(#pele)" {O2}/>' + f'<path d="M165,74 L188,58 L166,84 Z" fill="url(#pele)" {O2}/>'
    rosto = f'<path d="M134,72 C134,60 142,54 151,54 C162,54 168,62 168,72 C168,86 160,96 151,96 C142,96 134,86 134,72 Z" fill="url(#pele)" {O}/>' \
            '<path d="M140,73 Q144,70 148,73 Q144,76 140,73 Z M154,73 Q158,70 162,73 Q158,76 154,73 Z" fill="#2e8a4a" stroke="#1b1020" stroke-width="1"/>' \
            '<path d="M146,87 Q151,89 156,87" stroke="#a05a4a" stroke-width="1.4" fill="none"/>' \
            f'<path d="M135,68 C138,56 150,52 162,56 C166,58 168,64 168,68 C160,60 146,60 135,68 Z" fill="url(#cab)" {O2}/>'
    tunica = f'<path d="M136,104 L150,140 L164,104 C172,112 178,132 180,162 L120,162 C122,132 128,112 136,104 Z" fill="url(#tunica)" {O}/>' \
             f'<rect x="120" y="150" width="60" height="9" fill="#6a3e1e" {O2}/><rect x="146" y="149" width="8" height="11" fill="#f2c84a" {O2}/>'
    braco = f'<path d="M166,110 C182,114 196,118 206,120 L204,130 C192,128 178,126 166,124 Z" fill="url(#tunica)" {O2}/><circle cx="208" cy="125" r="6" fill="url(#pele)" {O2}/>'
    braco2 = f'<path d="M136,112 C150,118 166,122 178,124 L176,132 C162,132 148,128 132,124 Z" fill="url(#tunica)" {O2}/><circle cx="178" cy="128" r="5.5" fill="url(#pele)" {O2}/>'
    arco = '<path d="M206,36 C246,86 246,166 206,214" fill="none" stroke="#1b1020" stroke-width="8" stroke-linecap="round"/>' \
           '<path d="M206,36 C246,86 246,166 206,214" fill="none" stroke="#a8692e" stroke-width="4.5" stroke-linecap="round"/>' \
           '<path d="M206,36 L178,128 L206,214" fill="none" stroke="#f4f0e0" stroke-width="1.2"/>'
    flecha = '<path d="M178,128 L262,128" stroke="#1b1020" stroke-width="4"/><path d="M178,128 L262,128" stroke="#d9c79a" stroke-width="2"/>' \
             f'<path d="M262,122 L276,128 L262,134 Z" fill="#cfd8e0" {O2}/>' \
             f'<path d="M180,128 L172,121 L186,121 Z M180,128 L172,135 L186,135 Z" fill="#7cc46a" {O2}/>' + brilho(272, 128, 14, "#eaffc0")
    folhas = "".join(f'<path d="M{x},{y} q6,-8 12,0 q-6,8 -12,0 Z" fill="#a8e070" opacity="0.8" transform="rotate({r} {x} {y})"/>'
                     for x, y, r in [(40, 60, 20), (70, 150, -30), (250, 40, 40), (30, 120, 10)])
    return d + sombra_chao(150, 210, 60) + folhas + capa + capuz + cabelo + tunica + braco2 + rosto + orelhas + arco + braco + flecha


def ent():
    d = "<defs>" + lg("casca", (0, "#8a5a32"), (1, "#4a2c16"), x2=1, y2=0) + rg("copa", (0, "#9ad860"), (1, "#2e7a2e")) + "</defs>"
    raizes = f'<path d="M112,200 C100,206 86,208 72,212 L120,212 Z M188,200 C200,206 214,208 228,212 L180,212 Z M140,206 L132,214 L168,214 L160,206 Z" fill="#5a3418" {O}/>'
    tronco = (f'<path d="M110,210 C116,172 112,132 118,102 C126,82 174,82 182,102 C188,132 184,172 190,210 Z" fill="url(#casca)" {O}/>'
              '<path d="M126,110 C128,140 124,170 128,200 M172,112 C170,140 176,170 172,200 M150,170 C148,184 152,196 150,206" stroke="#3a2010" stroke-width="2" fill="none"/>')
    braco_e = (f'<path d="M120,122 C96,116 76,100 60,78 L68,72 C80,88 98,102 122,110 Z" fill="url(#casca)" {O}/>'
               f'<path d="M62,76 L48,70 M64,74 L58,58 M72,86 L60,92" stroke="#4a2c16" stroke-width="4" stroke-linecap="round"/>')
    braco_d = (f'<path d="M180,122 C202,130 222,150 232,172 L224,176 C214,156 198,140 178,134 Z" fill="url(#casca)" {O}/>'
               f'<path d="M230,172 L244,180 M228,176 L230,192 M226,168 L240,164" stroke="#4a2c16" stroke-width="4" stroke-linecap="round"/>')
    copa = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#copa)" {O}/>' for x, y, r in
                   [(110, 74, 28), (190, 74, 28), (128, 44, 26), (172, 42, 26), (150, 60, 36)])
    copa += "".join(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#ff6a8a" {O2}/>' for x, y in [(120, 50), (176, 36), (196, 80), (138, 72), (106, 80)])
    rosto = ('<path d="M128,120 Q138,112 148,120 M152,120 Q162,112 172,120" stroke="#2a1608" stroke-width="4" fill="none" stroke-linecap="round"/>'
             '<ellipse cx="138" cy="128" rx="7" ry="5" fill="#1b1020"/><ellipse cx="162" cy="128" rx="7" ry="5" fill="#1b1020"/>'
             '<ellipse cx="138" cy="128" rx="3.5" ry="3" fill="#d8ff6a"/><ellipse cx="162" cy="128" rx="3.5" ry="3" fill="#d8ff6a"/>'
             + brilho(138, 128, 10, "#d8ff6a") + brilho(162, 128, 10, "#d8ff6a") +
             '<path d="M138,150 Q150,160 162,150 Q150,156 138,150 Z" fill="#1b1020" stroke="#1b1020" stroke-width="2"/>')
    musgo = '<path d="M116,104 q8,-6 16,0 q8,-6 16,0 q8,-6 16,0 q8,-6 18,0 L184,110 L116,110 Z" fill="#5aa03a" opacity="0.9"/>'
    cogumelo = f'<path d="M178,102 L178,94" stroke="#f4ead0" stroke-width="3"/><path d="M171,95 Q178,84 185,95 Z" fill="#e2443a" {O2}/>'
    return d + sombra_chao(150, 210, 85) + raizes + braco_e + braco_d + tronco + musgo + copa + rosto + cogumelo


def mago():
    d = "<defs>" + lg("manto", (0, "#4a3ab8"), (1, "#1e1658")) + lg("chapeu", (0, "#5a48d0"), (1, "#2a1e78")) \
        + lg("pele", (0, "#ffd9bf"), (1, "#e8b08a")) + rg("orbe", (0, "#ffffff"), (0.4, "#fff27a"), (1, "#5ad8ff")) + "</defs>"
    manto = (f'<path d="M108,214 C114,170 124,130 134,110 L166,110 C176,130 186,170 192,214 Z" fill="url(#manto)" {O}/>'
             + "".join(f'<path d="M{x},{y} l2,5 l5,0 l-4,3 l2,5 l-5,-3 l-5,3 l2,-5 l-4,-3 l5,0 Z" fill="#fff27a" opacity="0.85"/>'
                       for x, y in [(126, 170), (170, 150), (150, 192), (178, 194), (120, 200)]))
    cajado = '<path d="M204,58 L192,212" stroke="#1b1020" stroke-width="7" stroke-linecap="round"/><path d="M204,58 L192,212" stroke="#8a5a2e" stroke-width="4" stroke-linecap="round"/>' \
             f'<path d="M196,56 C192,44 200,36 204,40 C208,36 216,44 212,56" fill="none" stroke="#8a5a2e" stroke-width="4"/>'
    orbe = brilho(204, 46, 40, "#c8f4ff") + f'<circle cx="204" cy="46" r="11" fill="url(#orbe)" {O2}/>'
    raios = ('<path d="M214,40 L236,30 L232,40 L256,32" fill="none" stroke="#fff27a" stroke-width="2.6" stroke-linejoin="round"/>'
             '<path d="M210,58 L230,72 L222,74 L244,90" fill="none" stroke="#fff27a" stroke-width="2.6" stroke-linejoin="round"/>'
             '<path d="M196,36 L186,16 L194,18 L188,2" fill="none" stroke="#fff27a" stroke-width="2.2" stroke-linejoin="round"/>')
    braco = f'<path d="M164,112 C180,116 190,118 200,122 L196,134 C184,130 172,128 160,126 Z" fill="url(#manto)" {O}/><circle cx="199" cy="128" r="6.5" fill="url(#pele)" {O2}/>'
    braco2 = f'<path d="M136,112 C122,118 110,110 98,96 L90,104 C104,122 120,130 140,128 Z" fill="url(#manto)" {O}/><circle cx="92" cy="98" r="6.5" fill="url(#pele)" {O2}/>' \
             + brilho(88, 88, 18, "#fff27a") + '<path d="M86,90 L80,78 L88,80 L84,68" fill="none" stroke="#fff27a" stroke-width="2.2"/>'
    rosto = f'<ellipse cx="150" cy="92" rx="15" ry="13" fill="url(#pele)" {O}/>' \
            '<ellipse cx="144" cy="90" rx="2.2" ry="2.2" fill="#1b1020"/><ellipse cx="156" cy="90" rx="2.2" ry="2.2" fill="#1b1020"/>' \
            '<ellipse cx="150" cy="96" rx="3" ry="2.4" fill="#e8a080"/>'
    barba = f'<path d="M136,96 C134,120 142,146 150,164 C158,146 166,120 164,96 C158,104 142,104 136,96 Z" fill="#eef0f6" {O}/>' \
            '<path d="M144,108 Q148,126 150,148 M156,108 Q153,126 151,146" stroke="#b8bccb" stroke-width="1.4" fill="none"/>' \
            '<path d="M140,99 Q150,94 160,99" stroke="#c8ccd8" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
    chapeu = f'<path d="M122,82 C134,62 148,34 176,10 C168,36 170,60 178,82 Z" fill="url(#chapeu)" {O}/>' \
             f'<ellipse cx="150" cy="82" rx="40" ry="8" fill="url(#chapeu)" {O}/>' \
             '<path d="M125,77 Q150,72 176,77" stroke="#f2c84a" stroke-width="4.5" fill="none"/>' \
             '<path d="M148,46 l3,6 l6,0 l-5,4 l2,6 l-6,-4 l-5,4 l2,-6 l-5,-4 l6,0 Z" fill="#fff27a"/>'
    return d + sombra_chao(150, 210, 60) + cajado + manto + braco2 + barba + rosto + chapeu + braco + orbe + raios


def lobo():
    d = "<defs>" + lg("pelo", (0, "#9aaed8"), (1, "#3a4a78")) + lg("peito", (0, "#eef2ff"), (1, "#b8c4e8")) + "</defs>"
    cauda = f'<path d="M190,196 C222,198 244,176 240,150 C236,140 228,142 230,152 C230,170 214,180 192,180 Z" fill="url(#pelo)" {O}/>'
    corpo = f'<path d="M118,204 C106,170 116,138 138,124 C150,116 172,116 184,126 C204,142 208,176 202,204 Z" fill="url(#pelo)" {O}/>'
    raio_pelo = '<path d="M168,140 L180,150 L172,156 L188,170" fill="none" stroke="#fff27a" stroke-width="3.2" stroke-linejoin="round"/>' \
                '<path d="M182,182 L192,188 L186,194" fill="none" stroke="#fff27a" stroke-width="3" stroke-linejoin="round"/>'
    pescoco = f'<path d="M130,136 C120,118 114,102 110,86 L154,74 C160,92 166,110 174,128 Z" fill="url(#pelo)" {O}/>'
    peito = f'<path d="M136,128 C130,150 136,172 148,190 C158,172 162,150 158,128 Q148,138 136,128 Z" fill="url(#peito)" {O2}/>'
    patas = (f'<path d="M134,170 L132,204 L146,204 L146,172 Z" fill="url(#pelo)" {O}/>'
             f'<path d="M150,172 L152,204 L166,204 L164,170 Z" fill="url(#pelo)" {O}/>'
             '<path d="M136,204 v-4 M141,204 v-4 M156,204 v-4 M161,204 v-4" stroke="#1b1020" stroke-width="1.4"/>')
    cabeca = ('<path d="M96,33 L119,63 L103,52 Z" fill="#2a1030"/>'
              f'<path d="M156,82 C158,66 148,54 132,54 L102,27 C97,23 92,27 95,32 L119,62 L104,50 '
              f'C100,48 97,52 100,56 L120,80 C130,92 150,94 156,82 Z" fill="url(#pelo)" {O}/>'
              f'<path d="M95,32 C93,27 97,24 101,27 L104,30 Z" fill="#1b1020"/>'
              '<path d="M108,40 L128,58" stroke="#e8f0ff" stroke-width="1.8" opacity="0.7"/>'
              f'<path d="M140,58 L152,34 L158,66 Z" fill="url(#pelo)" {O}/><path d="M145,56 L152,42 L155,62 Z" fill="#e8a0b8"/>'
              '<path d="M128,64 Q134,60 140,65" stroke="#1b1020" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
              '<path d="M150,76 l6,4 M146,82 l6,4" stroke="#e8f0ff" stroke-width="1.4"/>')
    uivo = '<path d="M84,22 Q74,14 80,4 M78,32 Q64,26 66,12 M92,14 Q90,4 96,-2" stroke="#fff27a" stroke-width="2" fill="none" opacity="0.8"/>'
    return d + sombra_chao(160, 206, 70) + brilho(150, 150, 90, "#a8c8ff") + cauda + corpo + raio_pelo + pescoco + peito + patas + cabeca + uivo


def golem():
    d = "<defs>" + lg("pedra", (0, "#a8957a"), (1, "#5a4a38")) + lg("pedra2", (0, "#8a7860"), (1, "#4a3a2a")) + "</defs>"
    P = 'fill="url(#pedra)" ' + O
    P2 = 'fill="url(#pedra2)" ' + O
    pernas = f'<polygon points="114,172 146,172 142,208 108,208" {P2}/><polygon points="154,172 186,172 192,208 158,208" {P2}/>'
    torso = f'<polygon points="104,94 196,94 212,148 186,178 114,178 88,148" {P}/>'
    rachas = '<path d="M120,110 L132,128 L126,146 M178,108 L168,124 L176,150 M140,160 L150,170 L162,162" stroke="#3a2c1e" stroke-width="2" fill="none"/>'
    runa = brilho(150, 132, 30, "#7aff9a") + '<circle cx="150" cy="132" r="13" fill="none" stroke="#7aff9a" stroke-width="3"/>' \
           '<path d="M150,119 L150,145 M139,126 L161,138 M161,126 L139,138" stroke="#7aff9a" stroke-width="2.4"/>'
    ombros = f'<polygon points="70,92 108,86 116,120 76,128" {P}/><polygon points="230,92 192,86 184,120 224,128" {P}/>'
    bracos = (f'<polygon points="74,124 104,122 100,168 70,166" {P2}/><polygon points="60,162 106,160 110,202 56,202" {P}/>'
              f'<polygon points="226,124 196,122 200,168 230,166" {P2}/><polygon points="240,162 194,160 190,202 244,202" {P}/>'
              '<path d="M70,182 L96,182 M204,182 L230,182" stroke="#3a2c1e" stroke-width="2"/>')
    cabeca = f'<polygon points="128,58 172,58 178,94 122,94" {P}/>' \
             '<path d="M126,72 L174,72" stroke="#3a2c1e" stroke-width="3"/>' \
             + brilho(140, 80, 12, "#7aff9a") + brilho(160, 80, 12, "#7aff9a") + \
             '<rect x="134" y="77" width="12" height="6" rx="2" fill="#d8ffe0"/><rect x="154" y="77" width="12" height="6" rx="2" fill="#d8ffe0"/>'
    musgo = '<path d="M104,94 q6,-5 12,0 q6,-5 12,0 q6,-5 12,0 L140,98 L104,98 Z M70,92 q6,-5 12,0 q6,-5 12,0 L94,95 L70,95 Z" fill="#6aa83a"/>'
    pedrinhas = "".join(f'<polygon points="{x},{y} {x+8},{y-3} {x+11},{y+5} {x+3},{y+8}" {P2}/>' for x, y in [(40, 60), (250, 50), (36, 120), (262, 120)])
    return d + sombra_chao(150, 208, 95) + pedrinhas + pernas + ombros + bracos + torso + rachas + runa + cabeca + musgo


def anao():
    d = "<defs>" + lg("malha", (0, "#9aa6b8"), (1, "#4a5468")) + lg("aco", (0, "#e8eef6"), (1, "#7a889c")) \
        + lg("barba", (0, "#e8742a"), (1, "#a83e14")) + lg("pele", (0, "#ffd0b0"), (1, "#e8a080")) + "</defs>"
    machado = ('<path d="M214,52 L196,208" stroke="#1b1020" stroke-width="8" stroke-linecap="round"/>'
               '<path d="M214,52 L196,208" stroke="#8a5a2e" stroke-width="5" stroke-linecap="round"/>'
               f'<path d="M212,60 C232,48 248,56 254,76 C246,90 230,94 208,84 Z" fill="url(#aco)" {O}/>'
               f'<path d="M212,60 C196,46 180,52 176,70 C182,84 196,88 210,82 Z" fill="url(#aco)" {O}/>'
               '<path d="M244,62 C248,68 250,74 250,78" stroke="#fff" stroke-width="2" fill="none"/>' + brilho(250, 66, 10, "#ffffff"))
    corpo = (f'<path d="M104,206 C98,164 106,132 120,118 L180,118 C194,132 202,164 196,206 Z" fill="url(#malha)" {O}/>'
             + "".join(f'<path d="M{x},{y} q4,4 8,0" stroke="#3a4458" stroke-width="1.2" fill="none"/>'
                       for x in range(110, 190, 10) for y in (136, 148, 180, 192)))
    cinto = f'<rect x="102" y="164" width="96" height="11" fill="#6a3e1e" {O2}/><rect x="142" y="162" width="16" height="15" rx="2" fill="#f2c84a" {O2}/>'
    botas = f'<path d="M112,204 L112,214 L144,214 L144,204 Z M156,204 L156,214 L190,214 L190,204 Z" fill="#4a2c16" {O}/>'
    bracos = (f'<path d="M180,124 C196,128 204,132 208,128 L212,146 C200,150 188,146 176,140 Z" fill="url(#malha)" {O}/>'
              f'<circle cx="208" cy="132" r="9" fill="url(#pele)" {O2}/>'
              f'<path d="M120,124 C104,132 98,148 102,164 L114,162 C114,150 118,140 126,136 Z" fill="url(#malha)" {O}/>'
              f'<circle cx="106" cy="166" r="8" fill="url(#pele)" {O2}/>')
    rosto = f'<ellipse cx="150" cy="94" rx="22" ry="20" fill="url(#pele)" {O}/>' \
            '<ellipse cx="141" cy="92" rx="2.4" ry="2.6" fill="#1b1020"/><ellipse cx="159" cy="92" rx="2.4" ry="2.6" fill="#1b1020"/>' \
            '<path d="M134,85 L146,87 M154,87 L166,85" stroke="#a83e14" stroke-width="4" stroke-linecap="round"/>'
    barba = (f'<path d="M128,102 C124,130 136,160 150,176 C164,160 176,130 172,102 C164,114 136,114 128,102 Z" fill="url(#barba)" {O}/>'
             '<path d="M140,112 Q144,140 150,166 M160,112 Q156,140 150,166" stroke="#8a2e0e" stroke-width="1.6" fill="none"/>'
             f'<rect x="144" y="146" width="12" height="6" rx="2" fill="#f2c84a" {O2}/>'
             )
    nariz = f'<ellipse cx="150" cy="99" rx="4.5" ry="4" fill="#f0a080" {O2}/>' \
            '<path d="M136,108 Q143,102 150,106 Q157,102 164,108" stroke="#c85a1e" stroke-width="5" fill="none" stroke-linecap="round"/>'
    elmo = (f'<path d="M126,88 C124,58 176,58 174,88 Z" fill="url(#aco)" {O}/>'
            f'<rect x="124" y="82" width="52" height="8" rx="3" fill="#c8a24a" {O2}/>'
            f'<path d="M147,88 L150,102 L153,88 Z" fill="url(#aco)" {O2}/>'
            f'<path d="M128,74 C114,70 106,58 108,44 C116,54 122,60 132,64 Z" fill="#f6e6c0" {O2}/>'
            f'<path d="M172,74 C186,70 194,58 192,44 C184,54 178,60 168,64 Z" fill="#f6e6c0" {O2}/>')
    return d + sombra_chao(150, 212, 64) + machado + corpo + cinto + botas + bracos + rosto + barba + nariz + elmo


def vampiro():
    d = "<defs>" + lg("capa", (0, "#2a1440"), (1, "#0a0614")) + lg("forro", (0, "#e0243a"), (1, "#6a0a1a")) \
        + lg("pele", (0, "#f2ecf8"), (1, "#c8bcd8")) + "</defs>"
    capa = f'<path d="M56,216 C66,150 98,100 150,94 C202,100 234,150 244,216 Z" fill="url(#capa)" {O}/>'
    forro = f'<path d="M92,216 C102,160 124,120 150,114 C176,120 198,160 208,216 Z" fill="url(#forro)" {O2}/>'
    gola = f'<path d="M122,96 L94,56 L104,58 L140,100 Z" fill="url(#forro)" {O}/>' + f'<path d="M178,96 L206,56 L196,58 L160,100 Z" fill="url(#forro)" {O}/>'
    terno = f'<path d="M128,108 L172,108 L178,216 L122,216 Z" fill="#1a1024" {O}/>' \
            f'<path d="M140,108 L150,142 L160,108 Z" fill="#f4f0f8" {O2}/>' + f'<circle cx="150" cy="116" r="4.5" fill="#e0243a" {O2}/>' + brilho(150, 116, 8, "#ff6a7a")
    rosto = f'<path d="M135,80 C135,60 165,60 165,80 C165,96 158,106 150,108 C142,106 135,96 135,80 Z" fill="url(#pele)" {O}/>' \
            '<path d="M140,80 L147,82 L140,84 Z M160,80 L153,82 L160,84 Z" fill="#ff2a3a"/>' + brilho(144, 82, 7, "#ff2a3a") + brilho(156, 82, 7, "#ff2a3a") + \
            '<path d="M144,96 Q150,99 156,96" stroke="#5a1a2a" stroke-width="1.5" fill="none"/>' \
            '<path d="M145,97 L146.5,101 L148,97.5 Z M152,97.5 L153.5,101 L155,97 Z" fill="#fff"/>' \
            f'<path d="M135,80 L128,74 L135,88 Z M165,80 L172,74 L165,88 Z" fill="url(#pele)" {O2}/>'
    cabelo = f'<path d="M133,80 C129,58 141,48 150,48 C160,48 172,58 167,80 C163,68 157,63 150,72 C143,63 137,68 133,80 Z" fill="#120a1c" {O2}/>'
    return d + capa + forro + terno + gola + rosto + cabelo


def espectro():
    d = "<defs>" + lg("manto", (0, "#4a5a7a"), (0.7, "#1e2438", 0.9), (1, "#1e2438", 0)) + "</defs>"
    foice = ('<path d="M214,24 L188,214" stroke="#1b1020" stroke-width="6" stroke-linecap="round"/>'
             '<path d="M214,24 L188,214" stroke="#5a4a3a" stroke-width="3.5" stroke-linecap="round"/>'
             f'<path d="M212,30 C190,10 150,10 122,30 C150,24 180,28 208,46 Z" fill="#c8d4e0" {O}/>')
    manto = (f'<path d="M100,70 C100,40 124,24 150,24 C176,24 200,40 200,70 C204,110 214,150 226,186 L210,176 L200,198 '
             f'L186,178 L172,202 L160,182 L148,208 L136,184 L122,202 L112,180 L98,194 L84,182 C94,142 98,106 100,70 Z" fill="url(#manto)" {O}/>'
             '<path d="M118,110 C116,140 112,170 108,186 M182,110 C186,140 190,170 196,186 M150,110 C150,150 150,180 148,204" stroke="#141826" stroke-width="2" fill="none" opacity="0.7"/>')
    capuz = '<path d="M122,72 C122,50 135,40 150,40 C165,40 178,50 178,72 C178,92 165,104 150,104 C135,104 122,92 122,72 Z" fill="#05060c"/>'
    olhos = brilho(140, 72, 14, "#5affd8") + brilho(160, 72, 14, "#5affd8") + \
            '<ellipse cx="140" cy="72" rx="4.5" ry="3" fill="#d8fff6"/><ellipse cx="160" cy="72" rx="4.5" ry="3" fill="#d8fff6"/>'
    braco = f'<path d="M108,108 C92,118 82,130 74,142 L86,150 C94,140 104,132 114,124 Z" fill="#3a4662" {O}/>' \
            '<path d="M78,146 L74,154 M82,148 L80,156" stroke="#d8d4c8" stroke-width="2.4" stroke-linecap="round"/>'
    braco2 = f'<path d="M192,108 C200,116 204,120 206,124 L196,132 C192,126 188,120 186,116 Z" fill="#3a4662" {O}/>'
    lanterna = ('<path d="M76,154 L72,166" stroke="#8a8a9a" stroke-width="1.6"/>'
                + brilho(70, 182, 34, "#7aff7a") +
                f'<path d="M60,166 L80,166 L84,174 L82,196 L58,196 L56,174 Z" fill="#3a3020" {O}/>'
                '<rect x="61" y="175" width="18" height="18" rx="2" fill="#c8ffb0"/>'
                '<path d="M70,192 C64,186 66,180 70,176 C72,182 76,184 70,192 Z" fill="#3aff6a"/>')
    nevoa = '<ellipse cx="150" cy="208" rx="100" ry="12" fill="#c8d8f0" opacity="0.18"/><ellipse cx="110" cy="214" rx="60" ry="8" fill="#c8d8f0" opacity="0.15"/>'
    return d + foice + manto + braco2 + capuz + olhos + braco + lanterna + nevoa


ESPECIES = {
    "dragao": ("Fogo", dragao), "fenix": ("Fogo", fenix),
    "sereia": ("Água", sereia), "kraken": ("Água", kraken),
    "elfo": ("Planta", elfo), "ent": ("Planta", ent),
    "mago": ("Elétrico", mago), "lobo": ("Elétrico", lobo),
    "golem": ("Terra", golem), "anao": ("Terra", anao),
    "vampiro": ("Sombra", vampiro), "espectro": ("Sombra", espectro),
}


def verso():
    d = "<defs>" + lg("vb", (0, "#3a2266"), (1, "#160a2c")) + rg("vc", (0, "#ffe7a0"), (1, "#c8902a")) + "</defs>"
    losangos = "".join(f'<path d="M{x},{y} l10,10 l-10,10 l-10,-10 Z" fill="none" stroke="#5a3a9a" stroke-width="1.5"/>'
                       for x in range(10, 300, 20) for y in range(-10, 220, 20))
    return (d + '<rect width="300" height="220" fill="url(#vb)"/>' + losangos +
            '<rect x="10" y="10" width="280" height="200" rx="14" fill="none" stroke="#e8c26a" stroke-width="3"/>'
            '<rect x="18" y="18" width="264" height="184" rx="10" fill="none" stroke="#e8c26a" stroke-width="1.2" opacity="0.7"/>'
            + brilho(150, 110, 70, "#c89aff") +
            '<path d="M150,62 L192,110 L150,158 L108,110 Z" fill="url(#vc)" stroke="#1b1020" stroke-width="3"/>'
            '<path d="M150,80 L176,110 L150,140 L124,110 Z" fill="#3a2266" stroke="#1b1020" stroke-width="2"/>'
            '<circle cx="150" cy="110" r="8" fill="#ffe7a0"/>')


def salvar(nome, corpo, fundo_svg=""):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="440" viewBox="0 0 300 220">'
           f'<clipPath id="clip"><rect width="300" height="220"/></clipPath><g clip-path="url(#clip)">{fundo_svg}{corpo}</g></svg>')
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(SAIDA, nome + ".png"))


if __name__ == "__main__":
    for nome, (elem, func) in ESPECIES.items():
        salvar(nome, func(), fundo(elem))
    salvar("verso", verso())
    print("ok", len(ESPECIES) + 1, "imagens em", SAIDA)
