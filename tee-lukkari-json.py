#!/usr/bin/env python3
"""Hae viikon lukujärjestys wilmai-CLI:llä ja kirjoita lukkari.json
TRMNL-private-pluginin pollattavaksi.

Ajetaan Hermes-VM:llä cronista (wilmai-auth on siellä). Skripti hakee
kuluvan viikon; jos se on tyhjä (loma), kokeillaan enintään 4 seuraavaa
viikkoa, jolloin tuleva lukkari näkyy jo ennen koulun alkua.

Koordinaatisto on sama kuin Lukkarit.svg:ssä (800x480, tuntirivi 51 px,
y = 59 + tunnit_klo_8_jalkeen * 51), jotta markup pysyy yksinkertaisena:
laatikot sijoitetaan suoraan JSONin x/y/w/h-arvoilla.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys

WILMAI_BIN = os.environ.get("WILMAI_BIN", "wilmai")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lukkari.json")

STUDENTS = {"T": "0419516", "S": "0416199"}   # T = Touko, S = Senja
DAYS = ["MA", "TI", "KE", "TO", "PE"]

# geometria (sama kuin Lukkarit.svg)
GRID_L, DAY_W, SUB_T_W = 44, 149, 74
SUB_BOT, HOUR_H = 59, 51

ABBR = [
    ("Suomen kieli", "ÄI"), ("Matematiikka", "MA"), ("Englanti", "EN"),
    ("Ruotsin", "RU"), ("Ympäristöoppi", "YM"), ("Uskonto", "ET"),
    ("Elämänkatsomustieto", "ET"), ("Käsityö", "KÄ"), ("Kuvataide", "KU"),
    ("Musiikki", "MU"), ("Liikunta", "LI"), ("Yhteiskuntaoppi", "YH"),
    ("Historia", "HI"), ("Oppilaanohjaus", "OP"),
]


def abbr(subject: str) -> str:
    for prefix, code in ABBR:
        if subject.startswith(prefix):
            return code
    return subject[:2].upper()


def y_of(hhmm: str) -> float:
    h, m = map(int, hhmm.split(":"))
    return SUB_BOT + ((h - 8) * 60 + m) * HOUR_H / 60


def fetch_day(student: str, date: dt.date) -> list[dict]:
    proc = subprocess.run(
        [WILMAI_BIN, "schedule", "list", "--date", date.isoformat(),
         "--student", student, "--json"],
        capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise SystemExit(f"wilmai epäonnistui: {proc.stderr.strip()[:200]}")
    raw = proc.stdout
    return json.loads(raw[:raw.rfind("}") + 1]).get("lessons", [])


def build_week(monday: dt.date):
    days, total = [], 0
    for i, name in enumerate(DAYS):
        date = monday + dt.timedelta(days=i)
        day = {"n": name, "date": date.isoformat(), "T": [], "S": []}
        for child, number in STUDENTS.items():
            boxes = []
            last_end = None
            for les in sorted(fetch_day(number, date), key=lambda l: l["start"]):
                y0, y1 = y_of(les["start"]), y_of(les["end"])
                boxes.append({
                    "t": f'{les["start"].lstrip("0")} - {les["end"].lstrip("0")}',
                    "a": abbr(les["subject"]),
                    "y": round(y0) + 1, "h": round(y1 - y0) - 2,
                })
                last_end = les["end"]
                total += 1
            # ruokatunti 11:30-12:15, jos paiva yltaa 11:30:een
            if last_end is not None and last_end >= "11:30":
                boxes.append({"t": "", "a": "Ruokatunti",
                              "y": round(y_of("11:30")) + 1,
                              "h": round(45 * HOUR_H / 60) - 2})
                boxes.sort(key=lambda b: b["y"])
            x = GRID_L + i * DAY_W + (3 if child == "T" else SUB_T_W + 4)
            w = (SUB_T_W - 6) if child == "T" else (DAY_W - SUB_T_W - 7)
            for b in boxes:
                b["x"], b["w"] = x, w
            day[child] = boxes
        days.append(day)
    return days, total


def main():
    today = dt.date.today()
    monday = today - dt.timedelta(days=today.weekday())
    for _ in range(5):
        days, total = build_week(monday)
        if total:
            break
        monday += dt.timedelta(days=7)
    friday = monday + dt.timedelta(days=4)
    data = {
        "paivitetty": dt.datetime.now().strftime("%d.%m.%Y %H:%M"),
        "viikko": f"vko {monday.isocalendar()[1]} · "
                  f"{monday.day}.{monday.month}.–{friday.day}.{friday.month}.",
        "tunteja": total,
        "days": days,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"ok: {OUT} ({total} tuntia, viikko {monday.isoformat()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
