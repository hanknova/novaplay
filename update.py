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
    print(f"Cargando: {url}")
    with urlopen(url) as f:
        data = json.load(f)
    print(f"Items cargados: {len(data)}")
    return data


nova = load(NOVA_URL)
prueba = load(PRUEBA_URL)

print("\n==============================")
print("CONSTRUYENDO SESSION_MAP")
print("==============================")

session_map = {}

for item in prueba:
    for key, url in item.items():

        if not key.startswith("url"):
            continue

        if not isinstance(url, str):
            continue

        match = re.search(PATTERN, url)

        if not match:
            continue

        session_id = match.group(1)
        channel = match.group(2)

        session_map[channel] = session_id

        print(
            f"Detectado -> Canal: {channel} | Session: {session_id}"
        )

print("\nSESSION_MAP FINAL:")
print(json.dumps(session_map, indent=2))

print("\n==============================")
print("BUSCANDO CAMBIOS EN NOVA")
print("==============================")

changes = 0

for item in nova:

    for key, url in item.items():

        if not key.startswith("url"):
            continue

        if not isinstance(url, str):
            continue

        match = re.search(PATTERN, url)

        if not match:
            continue

        old_session = match.group(1)
        channel = match.group(2)

        print(f"\nCanal: {channel}")
        print(f"Session actual : {old_session}")

        if channel not in session_map:
            print("No existe en session_map")
            continue

        new_session = session_map[channel]

        print(f"Session nueva  : {new_session}")

        if old_session == new_session:
            print("SIN CAMBIOS")
            continue

        print("ACTUALIZANDO")

        new_url = re.sub(
            PATTERN,
            f"/ccur-session/{new_session}/rolling-buffer/{channel}/",
            url
        )

        item[key] = new_url

        changes += 1

print("\n==============================")
print(f"TOTAL CAMBIOS: {changes}")
print("==============================")

if changes == 0:
    print("NO HUBO CAMBIOS REALES")
    exit(0)

with open("novaplay.json", "w", encoding="utf-8") as f:
    json.dump(
        nova,
        f,
        indent=2,
        ensure_ascii=False
    )

print("Archivo novaplay.json actualizado")
