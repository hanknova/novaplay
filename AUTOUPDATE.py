import json
import re
import requests

URL_ORIGEN = "https://mundodeportes.online/pandatv/playpre/canales.json"
ARCHIVO_DESTINO = "novaplay.json"
DEBUG = True

CATEGORIAS_IGNORADAS = {"PLUTO", "PLUTO TV", "PLUTOTV"}

EQUIVALENCIAS = {
    "INFANTILES 👦": {
        "Cartoonito": ["CARTOONITO"],
        "Nickelodeon": ["NICKELODEON"],
        "Discovery Kids": ["DISCOVERY KIDS"],
        "Disney Channel": ["DISNEY CHANNEL"],
        "Tooncast": ["TOONCAST"],
        "Nick Jr": ["NICK JR"],
        "CARTOON NETWORK": ["CARTOON NETWORK"],
        "PLIM PLIM": ["PLIM PLIM"],
    },
    "CULTURA Y COCINA 🐢": {
        "HGTV": ["HGTV"],
        "DISCOVERY THEATER": ["DISCOVERY THEATER"],
        "DISCOVERY SCIENCE": ["DISCOVERY SCIENCE"],
        "DISCOVERY ID": ["DISCOVERY ID"],
        "DISCOVERY TURBO": ["DISCOVERY TURBO"],
        "DISCOVERY WORLD": ["DISCOVERY WORLD"],
        "National Geographic": ["NATGEO"],
        "Lifetime": ["Lifetime"],
    },
    "CINE Y SERIES": {
        "TCM": ["TCM"],
        "WARNER CHANNEL": ["Warner TV"],
        "GOLDEN 1": ["GOLDEN SD"],
        "Europa Europa": ["EUROPA EUROPA"],
    },
    "PACK HBO Y UNIVERSAL 🎥": {
        "HBO FAMILY": ["HBO Family"],
        "HBO MUNDI": ["HBO Mundi"],
        "HBO Plus": ["HBO+"],
        "HBO SIGNATURE": ["HBO Signature"],
        "HBO XTREME": ["HBO Xtreme"],
    },
}

def debug(m):
    if DEBUG:
        print(m)

def normalizar(t):
    if not t:
        return ""
    t = t.upper().encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z0-9]", "", t)

debug("Descargando origen...")
r = requests.get(URL_ORIGEN, timeout=30)
r.raise_for_status()
origen = r.json()

with open(ARCHIVO_DESTINO, "r", encoding="utf-8") as f:
    destino = json.load(f)

indice = {}
for cat in origen:
    nc = normalizar(cat.get("name", ""))
    indice[nc] = {}
    for c in cat.get("samples", []):
        indice[nc][normalizar(c.get("name", ""))] = c

mapa = {}

for categoria, canales in EQUIVALENCIAS.items():
    ck = normalizar(categoria)

    if ck not in indice:
        debug(f"Categoria no encontrada: {categoria}")
        continue

    for origen_nombre, destinos in canales.items():
        ok = normalizar(origen_nombre)

        if ok not in indice[ck]:
            debug(f"No encontrado {origen_nombre} en {categoria}")
            continue

        origen_canal = indice[ck][ok]

        for d in destinos:
            mapa[normalizar(d)] = origen_canal

ignoradas = {normalizar(x) for x in CATEGORIAS_IGNORADAS}

cambios = 0

for categoria in destino:
    if normalizar(categoria.get("title", "")) in ignoradas:
        continue

    for canal in categoria.get("items", []):
        k = normalizar(canal.get("name", ""))

        if k not in mapa:
            continue

        nueva = mapa[k].get("url", "")

        if nueva and canal.get("url", "") != nueva:
            canal["url"] = nueva
            cambios += 1

if cambios:
    with open(ARCHIVO_DESTINO, "w", encoding="utf-8") as f:
        json.dump(destino, f, indent=2, ensure_ascii=False)

    print(f"Actualizados {cambios} canales")
else:
    print("No hubo cambios")
