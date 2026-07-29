# trmnl-kuvat

Kuvat TRMNL e-ink -näytölle (800x480, mustavalko).

## Lukkarit.png

Lasten lukujärjestys 2026–2027 (T = Touko, S = Senja). TRMNL:n
Image URL -plugariin laitetaan tämä osoite:

```
https://raw.githubusercontent.com/Jaska779/trmnl-kuvat/main/Lukkarit.png
```

Osoite pysyy samana, kun tiedosto korvataan uudella samalla nimellä.
Muutokset näkyvät raw-osoitteessa noin 5 minuutin välimuistiviiveellä.

## Päivitys

1. Muokkaa lukkaridataa tiedostossa `tee-lukkari-svg.py` (DATA-sanakirja).
2. Generoi SVG ja PNG:

```
python3 tee-lukkari-svg.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --disable-gpu --screenshot=Lukkarit.png --window-size=800,480 \
  "file://$(pwd)/Lukkarit.svg"
```

3. Committaa ja pushaa.
