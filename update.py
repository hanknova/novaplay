import json
import re
from urllib.request import urlopen

CHANNELS = [
    "APP_CHN1",
    "APP_CHN2",
    "APP_CHN3",
    "APP_CHN4",
    "TigoSP4_WM"
]

PATTERN = r"/ccur-session/([^/]+)/rolling-buffer/(" + "|".join(CHANNELS) + r")/"

NOVA_URL = "https://raw.githubusercontent.com/ThedarkSoldier996/test/main/novaplay.json"
PRUEBA_URL = "https://archive.org/download/prueba7_202606/prueba.7/prueba7.json"

def load(url):
    with urlopen(url) as f:
        return json.load(f)

nova = load(NOVA_URL)
prueba = load(PRUEBA_URL)

# MAPA: canal -> session_id nuevo
session_map = {}

for item in prueba:
    url = item.get("url", "")
    match = re.search(r"/ccur-session/([^/]+)/rolling-buffer/(" + "|".join(CHANNELS) + r")/", url)
    if match:
        session_id = match.group(1)
        channel = match.group(2)
        session_map[channel] = session_id

print("Mapa detectado:", session_map)

changes = 0

for item in nova:
    for key in list(item.keys()):
        if not key.startswith("url"):
            continue

        url = item[key]

        match = re.search(PATTERN, url)
        if not match:
            continue

        old_session = match.group(1)
        channel = match.group(2)

        if channel not in session_map:
            continue

        new_session = session_map[channel]

        if old_session == new_session:
            continue

        new_url = re.sub(
            PATTERN,
            f"/ccur-session/{new_session}/rolling-buffer/{channel}/",
            url
        )

        item[key] = new_url
        changes += 1
        print(f"Actualizado {channel}: {old_session} -> {new_session}")

print("Total cambios:", changes)

with open("novaplay.json", "w", encoding="utf-8") as f:
    json.dump(nova, f, indent=2, ensure_ascii=False)
