import json
import re
import requests

# =====================================================
# CONFIGURACIÓN
# =====================================================

URL_ORIGEN = "https://mundodeportes.online/pandatv/playpre/canales.json"
ARCHIVO_DESTINO = "novaplay.json"

DEBUG = True

# Categorías que NO quieres tocar
CATEGORIAS_IGNORADAS = {
    "PLUTO",
    "PLUTO TV",
    "PLUTOTV"
}

# =====================================================
# EQUIVALENCIAS (ORIGEN -> DESTINOS MÚLTIPLES)
# =====================================================

EQUIVALENCIAS = {
    "GEN_TV": ["GEN TV", "GEN PY - MUNDIAL"],
    "RPC": ["TRECE PY", "TRECE PY - MUNDIAL"],
    "UNICANAL": ["UNICANAL PY", "UNICANAL PY - MUNDIAL"],
    "POPU TV": ["POPUTV PY", "POPUTV PY - MUNDIAL"],
    "TELEFE ARG": ["TELEFE - MUNDIAL"],
    "TV PUBLICA ARG": ["TV PUBLICA AR - MUNDIAL", "TV PUBLICA"],
}

# =====================================================
# DEBUG
# =====================================================

def debug(msg):
    if DEBUG:
        print(msg)

# =====================================================
# NORMALIZAR NOMBRES
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

debug("Cargando novaplay.json...")

with open(ARCHIVO_DESTINO, "r", encoding="utf8") as f:
    destino = json.load(f)

# =====================================================
# CREAR ÍNDICE GLOBAL (TODOS LOS CANALES)
# =====================================================

indice = {}

debug("\n===== INDEXANDO ORIGEN =====")

for categoria in origen:

    nombre_cat = categoria.get("name", "")

    debug(f"\nCategoría origen: {nombre_cat}")

    for canal in categoria.get("samples", []):

        nombre = canal.get("name", "")
        key = normalizar(nombre)

        indice[key] = canal

        debug(f"  + {nombre}")

debug(f"\nTotal canales indexados: {len(indice)}")

# =====================================================
# APLICAR EQUIVALENCIAS
# =====================================================

debug("\n===== EQUIVALENCIAS =====")

for origen_nombre, destinos in EQUIVALENCIAS.items():

    origen_key = normalizar(origen_nombre)

    if origen_key not in indice:
        debug(f"❌ No existe origen: {origen_nombre}")
        continue

    for destino_nombre in destinos:

        destino_key = normalizar(destino_nombre)

        indice[destino_key] = indice[origen_key]

        debug(f"✔ {origen_nombre} -> {destino_nombre}")

# =====================================================
# ACTUALIZACIÓN
# =====================================================

debug("\n===== ACTUALIZANDO =====")

cambios = 0
encontrados = 0
no_encontrados = 0

for categoria in destino:

    titulo = categoria.get("title", "")

    if normalizar(titulo) in {normalizar(x) for x in CATEGORIAS_IGNORADAS}:
        debug(f"\n⛔ Omitiendo categoría: {titulo}")
        continue

    debug(f"\n📁 Categoría: {titulo}")

    for canal in categoria.get("items", []):

        nombre = canal.get("name", "")
        key = normalizar(nombre)

        debug(f"\n🔎 Buscando: {nombre}")

        if key not in indice:
            debug("❌ No encontrado")
            no_encontrados += 1
            continue

        encontrados += 1

        origen_canal = indice[key]

        url_actual = canal.get("url", "")
        url_nueva = origen_canal.get("url", "")

        debug(f"URL actual : {url_actual}")
        debug(f"URL origen : {url_nueva}")

        if url_nueva and url_actual != url_nueva:

            debug("🔄 ACTUALIZADO")

            canal["url"] = url_nueva
            cambios += 1

        else:
            debug("✔ Sin cambios")

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
    print(f"No encontrados: {no_encontrados}")

else:

    print("\n==============================")
    print("NO HUBO CAMBIOS")
    print("==============================")
