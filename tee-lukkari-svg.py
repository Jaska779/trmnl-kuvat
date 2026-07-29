#!/usr/bin/env python3
"""Generoi Lukkarit 2026-2027 -SVG samalla geometrialla kuin Lukkarit.svg
(800x480, ruudukko x 44-789, tuntirivi 51 px, paivasarake 149 px, T/S-jako)."""

W, H = 800, 480
GRID_L, GRID_R = 44.0, 789.0
TOP, HDR_BOT, SUB_BOT, GRID_BOT = 7.0, 38.0, 59.0, 467.0
DAY_W = (GRID_R - GRID_L) / 5          # 149
SUB_W = DAY_W / 2                      # 74.5
PX_MIN = 51.0 / 60                     # 0.85 px/min

DAYS = ["MA", "TI", "KE", "TO", "PE"]

# aika -> (tekstirivi, y-ylareuna)
def slot_y(hh, mm):
    return SUB_BOT + ((hh - 8) * 60 + mm) * PX_MIN

SLOTS = {
    0: ("8:00 - 8:45",   slot_y(8, 0)),
    1: ("8:50 - 9:35",   slot_y(8, 50)),
    2: ("10:00 - 10:45", slot_y(10, 0)),
    3: ("10:45 - 11:30", slot_y(10, 45)),
    4: ("RUOKA",         slot_y(11, 30)),
    5: ("12:15 - 13:00", slot_y(12, 15)),
    6: ("13:15 - 14:00", slot_y(13, 15)),
    7: ("14:15 - 15:00", slot_y(14, 15)),
}
SLOT_H = 45 * PX_MIN                   # 38.25

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
           f'xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">')
out.append(f'<rect width="{W}" height="{H}" fill="white"/>')

# vaakaviivat: ylareuna, otsikkorivin ja T/S-rivin alareunat, tuntiviivat
hlines = [TOP, HDR_BOT, SUB_BOT] + [SUB_BOT + i * 51 for i in range(1, 9)]
for y in hlines:
    out.append(f'<line x1="{GRID_L}" y1="{y}" x2="{GRID_R}" y2="{y}" '
               f'stroke="black" stroke-width="1"/>')

# pystyviivat: paivarajat kiinteina, T/S-raja katkoviivana
for i in range(6):
    x = GRID_L + i * DAY_W
    out.append(f'<line x1="{x}" y1="{TOP}" x2="{x}" y2="{GRID_BOT}" '
               f'stroke="black" stroke-width="1"/>')
for i in range(5):
    x = GRID_L + i * DAY_W + SUB_W
    out.append(f'<line x1="{x}" y1="{HDR_BOT}" x2="{x}" y2="{GRID_BOT}" '
               f'stroke="black" stroke-width="0.75" stroke-dasharray="1.5 2.5"/>')

# kehys hieman paksumpana
out.append(f'<rect x="{GRID_L}" y="{TOP}" width="{GRID_R-GRID_L}" '
           f'height="{GRID_BOT-TOP}" fill="none" stroke="black" stroke-width="1.5"/>')

# paivaotsikot ja T/S-otsikot
for i, day in enumerate(DAYS):
    cx = GRID_L + i * DAY_W + DAY_W / 2
    out.append(f'<text x="{cx}" y="27.5" text-anchor="middle" font-size="13" '
               f'font-weight="bold" fill="black">{day}</text>')
    for j, sub in enumerate(("T", "S")):
        sx = GRID_L + i * DAY_W + SUB_W / 2 + j * SUB_W
        out.append(f'<text x="{sx}" y="52.5" text-anchor="middle" font-size="10" '
                   f'font-weight="bold" fill="black">{sub}</text>')

# kellonajat vasempaan reunaan tuntiviivojen tasalle
for h in range(8, 17):
    y = SUB_BOT + (h - 8) * 51
    out.append(f'<text x="38" y="{y + 3.5}" text-anchor="end" font-size="9.5" '
               f'fill="black">{h}:00</text>')

# tuntipalkit
for i, day in enumerate(DAYS):
    for j, child in enumerate(("T", "S")):
        bx = GRID_L + i * DAY_W + j * SUB_W + 3
        bw = SUB_W - 6
        for slot, subject in DATA[child][day]:
            label, y0 = SLOTS[slot]
            by, bh = y0 + 1, SLOT_H - 2
            if slot == 4:  # ruokatunti
                out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" '
                           f'fill="white" stroke="black" stroke-width="0.75"/>')
                out.append(f'<text x="{bx + bw/2}" y="{by + bh/2 + 3}" '
                           f'text-anchor="middle" font-size="8" fill="black">'
                           f'Ruokatunti</text>')
            else:
                out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" '
                           f'fill="black"/>')
                out.append(f'<text x="{bx + bw/2}" y="{by + 12}" '
                           f'text-anchor="middle" font-size="7" fill="white">'
                           f'{label}</text>')
                out.append(f'<text x="{bx + bw/2}" y="{by + 27}" '
                           f'text-anchor="middle" font-size="11" '
                           f'font-weight="bold" fill="white">{subject}</text>')

out.append("</svg>")

import os
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lukkarit.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("ok:", path)
