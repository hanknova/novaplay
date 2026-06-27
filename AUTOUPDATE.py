import json
import re
import requests

# =====================================================
# CONFIGURACIÓN
# =====================================================

URL_ORIGEN = "https://mundodeportes.online/pandatv/playpre/canales.json"
ARCHIVO_DESTINO = "novaplay.json"

DEBUG = True

# Ignorar categorías
CATEGORIAS_IGNORADAS = {
    "PLUTO",
    "PLUTO TV",
    "PLUTOTV"
}

# =====================================================
# EQUIVALENCIAS (ÚNICA FUENTE DE CAMBIOS)
# SOLO lo que esté aquí se modifica
# =====================================================

EQUIVALENCIAS = {
    "GEN_TV": ["GEN TV", "GEN PY - MUNDIAL"],
    "RPC": ["TRECE PY", "TRECE PY - MUNDIAL"],
    "UNICANAL": ["UNICANAL PY", "UNICANAL PY - MUNDIAL"],
    "POPU TV": ["POPUTV PY", "POPUTV PY - MUNDIAL"],
    "TELEFE ARG": ["TELEFE - MUNDIAL", "TELEFE"],
    "TV PUBLICA  ARG": ["TV PUBLICA AR - MUNDIAL", "TV PUBLICA"],
    "PY | SNT  ": ["SNT"],
    "TELEFUTURO HD": ["TELEFUTURO"],
    "C9N  ": ["C9N"],
    "HEI NEW": ["HEI NOW"],
    "MEGA TV  PY": ["MEGA TV PY"],
    "SUR TV": ["SUR TV"],
    "5 DIAS PY": ["5 DIAS PY"],
    "ABC TV": ["ABC TV"],
    "NOTICIAS_PY  ": ["NPY"],
    "A24 PY": ["A24 PY"],
    "CANALPRO PY": ["CANAL PRO"],
    "AMERICA PY": ["AMERICA PY"],
    "LA TELE": ["LA TELE"],
    "AMERICA TV ": ["AMERICA TV"],
    "EL TRECE": ["EL TRECE"],
    "CANAL 9 ": ["CANAL 9"],
    "TN NOTICIAS": ["TN NOTICIAS"],
    "C5N": ["C5N"],
    "LN+ - LA NACION": ["LN+"],
    "CRONICA TV": ["CRONICA"],
    "A24": ["A24 ARGENTINA"],
    "CANAL 26": ["CANAL 26"],
}

# =====================================================
# DEBUG
# =====================================================

def debug(msg):
    if DEBUG:
        print(msg)

# =====================================================
# NORMALIZAR
# =====================================================

def normalizar(texto):
    if not texto:
        return ""
    texto = texto.upper()
    texto = texto.encode("ascii", "ignore").decode()
    texto = re.sub(r'[^A-Z0-9]', '', texto)
    return texto

# =====================================================
# DESCARGAR ORIGEN
# =====================================================

debug("Descargando origen...")

r = requests.get(URL_ORIGEN, timeout=30)
r.raise_for_status()
origen = r.json()

# =====================================================
# CARGAR DESTINO
# =====================================================

debug("Cargando destino...")

with open(ARCHIVO_DESTINO, "r", encoding="utf8") as f:
    destino = json.load(f)

# =====================================================
# CREAR MAPA SOLO DESDE EQUIVALENCIAS
# =====================================================

debug("\n===== INDEX SOLO EQUIVALENCIAS =====")

mapa = {}

for categoria in origen:
    for canal in categoria.get("samples", []):

        nombre = canal.get("name", "")
        key = normalizar(nombre)

        # SOLO si está en EQUIVALENCIAS
        for origen_nombre, destinos in EQUIVALENCIAS.items():

            if key == normalizar(origen_nombre):

                debug(f"✔ ORIGEN: {nombre}")

                for d in destinos:
                    mapa[normalizar(d)] = canal

# =====================================================
# ACTUALIZAR (SOLO SI ESTÁ EN MAPA)
# =====================================================

debug("\n===== ACTUALIZANDO =====")

cambios = 0
encontrados = 0
no_encontrados = 0

for categoria in destino:

    titulo = categoria.get("title", "")

    if normalizar(titulo) in {normalizar(x) for x in CATEGORIAS_IGNORADAS}:
        debug(f"\n⛔ OMITIDO: {titulo}")
        continue

    debug(f"\n📁 CATEGORÍA: {titulo}")

    for canal in categoria.get("items", []):

        nombre = canal.get("name", "")
        key = normalizar(nombre)

        debug(f"\n🔎 {nombre}")

        # 🔴 REGLA ABSOLUTA: si no está en EQUIVALENCIAS → NO SE TOCA
        if key not in mapa:
            debug("❌ NO ESTÁ EN EQUIVALENCIAS → IGNORADO")
            no_encontrados += 1
            continue

        encontrados += 1

        origen_canal = mapa[key]

        url_actual = canal.get("url", "")
        url_nueva = origen_canal.get("url", "")

        debug(f"URL actual : {url_actual}")
        debug(f"URL nueva  : {url_nueva}")

        if url_actual != url_nueva and url_nueva:

            debug("🔄 ACTUALIZADO")

            canal["url"] = url_nueva
            cambios += 1

        else:
            debug("✔ SIN CAMBIOS")

# =====================================================
# GUARDAR
# =====================================================

if cambios > 0:

    with open(ARCHIVO_DESTINO, "w", encoding="utf8") as f:
        json.dump(destino, f, indent=2, ensure_ascii=False)

    print("\n==============================")
    print("✅ AUTOUPDATE FINALIZADO")
    print("==============================")
    print(f"Cambios: {cambios}")
    print(f"Encontrados: {encontrados}")
    print(f"Ignorados: {no_encontrados}")

else:

    print("\n==============================")
    print("NO HUBO CAMBIOS")
    print("==============================")
