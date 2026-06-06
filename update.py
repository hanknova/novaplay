import json
import re
import requests

PATTERN = r"/ccur-session/([^/]+)/rolling-buffer/"

# Descargar archivos
nova = requests.get(
    "https://raw.githubusercontent.com/ThedarkSoldier996/test/main/novaplay.json"
).json()

prueba = requests.get(
    "https://archive.org/download/prueba7_202606/prueba.7/prueba7.json"
).json()

# Crear mapa nombre -> session id
sessiones = {}

for canal in prueba:
    url = canal.get("url", "")
    m = re.search(PATTERN, url)
    if m:
        sessiones[canal["name"]] = m.group(1)

# Actualizar novaplay
cambios = 0

for canal in nova:
    nombre = canal.get("name")

    if nombre not in sessiones:
        continue

    url = canal.get("url", "")

    nueva = sessiones[nombre]

    url_nueva = re.sub(
        PATTERN,
        f"/ccur-session/{nueva}/rolling-buffer/",
        url
    )

    if url_nueva != url:
        canal["url"] = url_nueva
        cambios += 1

print("Cambios:", cambios)

with open("novaplay.json", "w", encoding="utf-8") as f:
    json.dump(nova, f, indent=2, ensure_ascii=False)
