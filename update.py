import json
import re
from collections import defaultdict, Counter
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

PRUEBA7_URL = "https://archive.org/download/prueba7_202606/prueba.7/prueba7.json"
PRUEBA8_URL = "https://archive.org/download/prueba8_202606/prueba.8/prueba8.json"


def load(url):
    print(f"Cargando: {url}")

    with urlopen(url) as f:
        data = json.load(f)

    print("OK")
    return data


def extract_sessions(obj):
    """
    Busca URLs recursivamente y guarda todas
    las sesiones encontradas.
    """

    if isinstance(obj, dict):

        for key, value in obj.items():

            if key.startswith("url") and isinstance(value, str):

                match = re.search(PATTERN, value)

                if match:
                    session_id = match.group(1)
                    channel = match.group(2)

                    session_candidates[channel].append(session_id)

                    print(
                        f"Detectado: {channel} -> {session_id}"
                    )

            extract_sessions(value)

    elif isinstance(obj, list):

        for item in obj:
            extract_sessions(item)


def update_urls(obj, session_map):
    """
    Actualiza todas las URLs encontradas
    dentro de novaplay.json
    """

    changes = 0

    if isinstance(obj, dict):

        for key, value in obj.items():

            if key.startswith("url") and isinstance(value, str):

                match = re.search(PATTERN, value)

                if match:

                    old_session = match.group(1)
                    channel = match.group(2)

                    if channel in session_map:

                        new_session = session_map[channel]

                        if old_session != new_session:

                            new_url = re.sub(
                                PATTERN,
                                f"/ccur-session/{new_session}/rolling-buffer/{channel}/",
                                value
                            )

                            obj[key] = new_url

                            changes += 1

                            print(
                                f"[{channel}] "
                                f"{old_session} -> {new_session}"
                            )

            changes += update_urls(value, session_map)

    elif isinstance(obj, list):

        for item in obj:
            changes += update_urls(item, session_map)

    return changes


print("\n========================")
print("CARGANDO ARCHIVOS")
print("========================")

nova = load(NOVA_URL)
prueba7 = load(PRUEBA7_URL)
prueba8 = load(PRUEBA8_URL)

print("\n========================")
print("EXTRAYENDO SESIONES")
print("========================")

session_candidates = defaultdict(list)

extract_sessions(prueba7)
extract_sessions(prueba8)

print("\n========================")
print("SELECCIONANDO SESIONES")
print("========================")

session_map = {}

for channel, sessions in session_candidates.items():

    most_common = Counter(sessions).most_common(1)[0][0]

    session_map[channel] = most_common

    print(
        f"{channel} -> {most_common}"
    )

print("\nSESSION MAP FINAL:")
print(json.dumps(session_map, indent=2))

print("\n========================")
print("ACTUALIZANDO NOVAPLAY")
print("========================")

changes = update_urls(nova, session_map)

print("\n========================")
print(f"TOTAL CAMBIOS: {changes}")
print("========================")

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

print("novaplay.json actualizado correctamente")
