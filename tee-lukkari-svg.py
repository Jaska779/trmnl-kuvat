#!/usr/bin/env python3
"""Generoi Lukkarit.svg TRMNL e-ink -naytolle (800x480).

Pikselitarkka versio: kaikki viivat ovat 1 px:n suorakulmioita
kokonaislukukoordinaateilla, jotta 2x-renderointi + kynnystys tuottaa
puhtaan 1-bittisen mustavalkokuvan ilman dither-rakeisuutta.
PNG tehdaan skriptilla muunna-png.py (ohje READMEssa).
"""

import os

W, H = 800, 480
GRID_L, GRID_R = 44, 789
TOP, HDR_BOT, SUB_BOT, GRID_BOT = 7, 38, 59, 467
DAY_W = (GRID_R - GRID_L) // 5         # 149
SUB_T_W = 74                            # T-puolisko; S saa loput 75
HOUR_H = 51

DAYS = ["MA", "TI", "KE", "TO", "PE"]

# slotit: (aikateksti, y-ylareuna kokonaislukuna)
SLOTS = {
    0: ("8:00 - 8:45",   59),
    1: ("8:50 - 9:35",   101),
    2: ("10:00 - 10:45", 161),
    3: ("10:45 - 11:30", 199),
    4: ("RUOKA",         237),
    5: ("12:15 - 13:00", 275),
    6: ("13:15 - 14:00", 327),
    7: ("14:15 - 15:00", 378),
}
SLOT_H = 38

# child: T = Touko, S = Senja; per paiva lista (slot, aine)
DATA = {
    "T": {
        "MA": [(1, "MA"), (2, "ÄI"), (3, "YM"), (4, ""), (5, "ET"), (6, "KÄ"), (7, "KÄ")],
        "TI": [(0, "ET"), (1, "MU"), (2, "ÄI"), (3, "ÄI"), (4, ""), (5, "EN"), (6, "MA")],
        "KE": [(2, "LI"), (3, "ÄI"), (4, ""), (5, "YM")],
        "TO": [(1, "MA"), (2, "ÄI"), (3, "KU"), (4, ""), (5, "KU")],
        "PE": [(0, "LI"), (1, "EN"), (2, "ÄI"), (3, "MA"), (4, "")],
    },
    "S": {
        "MA": [(0, "ET"), (1, "ÄI"), (2, "KU"), (3, "KU"), (4, ""), (5, "YM")],
        "TI": [(0, "KÄ"), (1, "MA"), (2, "LI"), (3, "LI"), (4, ""), (5, "EN"), (6, "YH")],
        "KE": [(0, "KÄ"), (1, "RU"), (2, "MA"), (3, "ÄI"), (4, ""), (5, "ÄI"), (6, "MU")],
        "TO": [(1, "YH"), (2, "MA"), (3, "ÄI"), (4, ""), (5, "YM")],
        "PE": [(2, "YM"), (3, "ÄI"), (4, ""), (5, "EN"), (6, "RU")],
    },
}

FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
out = []
out.append(f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'xmlns="http://www.w3.org/2000/svg" font-family="{FONT}" '
           f'shape-rendering="crispEdges">')
out.append(f'<rect width="{W}" height="{H}" fill="white"/>')


def hline(y, x1=GRID_L, x2=GRID_R, t=1):
    out.append(f'<rect x="{x1}" y="{y}" width="{x2 - x1}" height="{t}" fill="black"/>')


def vline(x, y1, y2, t=1):
    out.append(f'<rect x="{x}" y="{y1}" width="{t}" height="{y2 - y1}" fill="black"/>')


# vaakaviivat: otsikkorivit + tuntiviivat
hline(HDR_BOT)
hline(SUB_BOT)
for i in range(1, 8):
    hline(SUB_BOT + i * HOUR_H)

# pystyviivat: paivarajat
for i in range(1, 5):
    vline(GRID_L + i * DAY_W, TOP, GRID_BOT)

# T/S-raja pistekatkona (2 px pistetta, 3 px valia)
for i in range(5):
    x = GRID_L + i * DAY_W + SUB_T_W
    y = HDR_BOT
    while y < GRID_BOT - 1:
        out.append(f'<rect x="{x}" y="{y}" width="1" height="2" fill="black"/>')
        y += 5

# kehys 2 px
hline(TOP, t=2)
hline(GRID_BOT - 2, t=2)
vline(GRID_L, TOP, GRID_BOT, t=2)
vline(GRID_R - 2, TOP, GRID_BOT, t=2)

# paivaotsikot ja T/S-otsikot
for i, day in enumerate(DAYS):
    cx = GRID_L + i * DAY_W + DAY_W // 2
    out.append(f'<text x="{cx}" y="28" text-anchor="middle" font-size="14" '
               f'font-weight="bold" fill="black">{day}</text>')
    for sub, sx in (("T", GRID_L + i * DAY_W + SUB_T_W // 2),
                    ("S", GRID_L + i * DAY_W + SUB_T_W + (DAY_W - SUB_T_W) // 2)):
        out.append(f'<text x="{sx}" y="53" text-anchor="middle" font-size="10" '
                   f'font-weight="bold" fill="black">{sub}</text>')

# kellonajat vasempaan reunaan tuntiviivojen tasalle
for h in range(8, 17):
    y = SUB_BOT + (h - 8) * HOUR_H
    out.append(f'<text x="38" y="{y + 4}" text-anchor="end" font-size="10" '
               f'fill="black">{h}:00</text>')

# tuntipalkit
for i, day in enumerate(DAYS):
    for child in ("T", "S"):
        if child == "T":
            bx = GRID_L + i * DAY_W + 3
            bw = SUB_T_W - 6
        else:
            bx = GRID_L + i * DAY_W + SUB_T_W + 4
            bw = DAY_W - SUB_T_W - 7
        for slot, subject in DATA[child][day]:
            label, y0 = SLOTS[slot]
            by, bh = y0 + 1, SLOT_H - 2
            cx = bx + bw // 2
            if slot == 4:  # ruokatunti
                out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" '
                           f'fill="white" stroke="black" stroke-width="1"/>')
                out.append(f'<text x="{cx}" y="{by + bh // 2 + 3}" '
                           f'text-anchor="middle" font-size="9" fill="black">'
                           f'Ruokatunti</text>')
            else:
                out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" '
                           f'fill="black"/>')
                out.append(f'<text x="{cx}" y="{by + 12}" text-anchor="middle" '
                           f'font-size="9" font-weight="bold" fill="white">'
                           f'{label}</text>')
                out.append(f'<text x="{cx}" y="{by + 28}" text-anchor="middle" '
                           f'font-size="12" font-weight="bold" fill="white">'
                           f'{subject}</text>')

out.append("</svg>")

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lukkarit.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("ok:", path)
