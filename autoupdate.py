import json
import re
import requests

# =====================================================
# CONFIGURACIÓN
# =====================================================

# Archivo origen (el que tiene las URLs nuevas)
URL_ORIGEN = "https://mundodeportes.online/pandatv/playpre/canales.json"

# Tu archivo del repositorio
ARCHIVO_DESTINO = "novaplay.json"

# =====================================================
# EQUIVALENCIAS
# IZQUIERDA = nombre en origen
# DERECHA = nombre en tu novaplay.json
# =====================================================

EQUIVALENCIAS = {

    "GEN_TV": "GEN TV",
    "GEN_TV": "GEN PY - MUNDIAL",
    "RPC  ": "TRECE PY - MUNDIAL",
    "RPC  ": "TRECE PY",


    # Agrega aquí todas las equivalencias que quieras.

}


# =====================================================
# NORMALIZA LOS NOMBRES
# Ejemplo:
#
# Gen Tv
# GEN-TV
# GEN TV
# gentv
#
# todos pasan a:
#
# GENTV
#
# =====================================================

def normalizar(nombre):
    return re.sub(r'[^A-Z0-9]', '', nombre.upper())


# =====================================================
# DESCARGAR JSON ORIGEN
# =====================================================

print("Descargando lista origen...")

r = requests.get(URL_ORIGEN, timeout=30)
r.raise_for_status()

origen = r.json()

# =====================================================
# LEER TU JSON
# =====================================================

print("Leyendo novaplay.json...")

with open(ARCHIVO_DESTINO, "r", encoding="utf8") as f:
    destino = json.load(f)


# =====================================================
# CREAR ÍNDICE
#
# Se guarda cada canal por nombre normalizado
#
# Ejemplo:
#
# GENTV -> objeto canal
#
# =====================================================

indice = {}

for categoria in origen:

    canales = categoria.get("channels", [])

    for canal in canales:

        nombre = canal.get("name", "")

        indice[normalizar(nombre)] = canal


# =====================================================
# AGREGAR EQUIVALENCIAS
#
# Si tiene:
#
# GENTV
#
# y tú tienes:
#
# GEN TV
#
# ambos apuntarán al mismo canal.
#
# =====================================================

for nombre_origen, nombre_destino in EQUIVALENCIAS.items():

    key_origen = normalizar(nombre_origen)
    key_destino = normalizar(nombre_destino)

    if key_origen in indice:

        indice[key_destino] = indice[key_origen]


# =====================================================
# ACTUALIZAR URLS
# =====================================================

cambios = 0

for categoria in destino:

    canales = categoria.get("channels", [])

    for canal in canales:

        nombre = canal.get("name", "")

        key = normalizar(nombre)

        if key not in indice:
            continue

        url_nueva = indice[key].get("url", "")
        url_actual = canal.get("url", "")

        if url_nueva and url_actual != url_nueva:

            print(f"Actualizado: {nombre}")

            canal["url"] = url_nueva

            cambios += 1


# =====================================================
# GUARDAR
# =====================================================

if cambios:

    print()

    print(f"Se actualizaron {cambios} canales.")

    with open(ARCHIVO_DESTINO, "w", encoding="utf8") as f:

        json.dump(
            destino,
            f,
            indent=2,
            ensure_ascii=False
        )

else:

    print("No hubo cambios.")
