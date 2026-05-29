import json
import requests

JSON_URL = "https://raw.githubusercontent.com/ThedarkSoldier996/test/refs/heads/main/novaplay.json"
SALIDA = "lista.m3u"

r = requests.get(JSON_URL)
r.raise_for_status()

data = r.text

json_data = json.loads(data)

canales = []

# recorrer categorías
for categoria in json_data:
    items = categoria.get("items", [])
    nombre_cat = categoria.get("title", "SIN CATEGORIA")

    for c in items:
        canales.append({
            "name": c.get("name") or c.get("title") or "Sin nombre",
            "url": c.get("url", ""),
            "logo": c.get("icono", ""),
            "group": nombre_cat
        })

# generar M3U
with open(SALIDA, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")

    for c in canales:
        f.write(
            f'#EXTINF:-1 group-title="{c["group"]}" tvg-logo="{c["logo"]}",{c["name"]}\n'
        )
        f.write(c["url"] + "\n")

print("M3U generado correctamente")
