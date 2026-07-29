#!/usr/bin/env python3
"""Muunna 2x-renderoity kuvakaappaus puhtaaksi 1-bittiseksi 800x480-PNG:ksi.

Kaytto: python3 muunna-png.py <2x-kuvakaappaus.png>
Vaatii Pillow-kirjaston (pip install pillow).
Kynnystys poistaa antialiasoinnin harmaat, jolloin TRMNL:n dither
ei tuota rakeisuutta.
"""

import os
import sys

from PIL import Image

src = sys.argv[1]
img = Image.open(src).convert("L")
img = img.resize((800, 480), Image.LANCZOS)
img = img.point(lambda p: 0 if p < 140 else 255).convert("1")

dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Lukkarit.png")
img.save(dst, optimize=True)
print("ok:", dst, img.size, img.mode)
