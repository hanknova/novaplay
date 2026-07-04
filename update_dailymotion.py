import json
import re
import requests

JSON_FILE = "novaplay.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

PATRON = re.compile(
    r"https://cdndirector\.dailymotion\.com/cdn/live/video/([A-Za-z0-9]+)\.m3u8"
)

hubo_cambios = False


def obtener_url(video_id):
    url = f"https://www.dailymotion.com/player/metadata/video/{video_id}"

    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()

    data = r.json()

    auto = data.get("qualities", {}).get("auto")

    if not auto:
        return None

    return auto[0]["url"]


def recorrer(obj):
    global hubo_cambios

    if isinstance(obj, dict):

        if "url" in obj and isinstance(obj["url"], str):

            m = PATRON.search(obj["url"])

            if m:
                video_id = m.group(1)

                print(f"Verificando {obj.get('name','')} ({video_id})")

                try:
                    nueva = obtener_url(video_id)

                    if nueva and nueva != obj["url"]:
                        obj["url"] = nueva
                        hubo_cambios = True
                        print("Actualizado")
                    else:
                        print("Sin cambios")

                except Exception as e:
                    print("ERROR:", e)

        for value in obj.values():
            recorrer(value)

    elif isinstance(obj, list):

        for item in obj:
            recorrer(item)


with open(JSON_FILE, encoding="utf8") as f:
    data = json.load(f)

recorrer(data)

if hubo_cambios:
    with open(JSON_FILE, "w", encoding="utf8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("Se guardaron cambios.")
else:
    print("No hubo cambios. No se modificó el archivo.")
