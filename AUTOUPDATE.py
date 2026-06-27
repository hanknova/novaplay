import json
import re
import requests

# =====================================================
# CONFIGURACIÓN
# =====================================================

URL_ORIGEN = "https://mundodeportes.online/pandatv/playpre/canales.json"
ARCHIVO_DESTINO = "novaplay.json"

# =====================================================
# EQUIVALENCIAS DE NOMBRES
# IZQUIERDA = Mundo Deportes
# DERECHA = Tu novaplay.json
# =====================================================

EQUIVALENCIAS = {
    "GEN_TV": "GEN TV",
    "GEN_TV": "GEN PY - MUNDIAL",
    "RPC  ": "TRECE PY - MUNDIAL",
    "RPC  ": "TRECE PY",
}

# =====================================================
# NORMALIZAR TEXTO
# =====================================================

def normalizar(texto):
    if not texto:
        return ""

    texto = texto.upper()

    # Elimina banderas y cualquier carácter raro
    texto = texto.encode("ascii", "ignore").decode()

    # Elimina todo menos letras y números
    texto = re.sub(r'[^A-Z0-9]', '', texto)

    return texto

# =====================================================
# DESCARGAR ORIGEN
# =====================================================

print("Descargando lista origen...")

r = requests.get(URL_ORIGEN, timeout=30)
r.raise_for_status()

origen = r.json()

print("Leyendo novaplay.json...")

with open(ARCHIVO_DESTINO, "r", encoding="utf8") as f:
    destino = json.load(f)

# =====================================================
# CREAR ÍNDICE
# categoria -> canal
# =====================================================

indice = {}

for categoria in origen:

    nombre_categoria = normalizar(categoria.get("name", ""))

    indice[nombre_categoria] = {}

    for canal in categoria.get("samples", []):

        indice[nombre_categoria][normalizar(canal.get("name", ""))] = canal

# =====================================================
# APLICAR EQUIVALENCIAS
# =====================================================

for categoria in indice.values():

    for origen_nombre, destino_nombre in EQUIVALENCIAS.items():

        ko = normalizar(origen_nombre)
        kd = normalizar(destino_nombre)

        if ko in categoria:
            categoria[kd] = categoria[ko]

# =====================================================
# ACTUALIZAR
# =====================================================

cambios = 0

for categoria in destino:

    nombre_categoria = normalizar(categoria.get("title", ""))

    if nombre_categoria not in indice:
        print(f"Categoría no encontrada: {categoria.get('title')}")
        continue

    canales_origen = indice[nombre_categoria]

    for canal in categoria.get("items", []):

        nombre = canal.get("name", "")
        key = normalizar(nombre)

        if key not in canales_origen:
            print(f"No encontrado: {categoria.get('title')} -> {nombre}")
            continue

        origen_canal = canales_origen[key]

        url_nueva = origen_canal.get("url", "")
        url_actual = canal.get("url", "")

        if url_nueva and url_actual != url_nueva:

            print(f"Actualizando {categoria.get('title')} -> {nombre}")

            canal["url"] = url_nueva

            cambios += 1

# =====================================================
# GUARDAR
# =====================================================

if cambios:

    with open(ARCHIVO_DESTINO, "w", encoding="utf8") as f:
        json.dump(destino, f, indent=2, ensure_ascii=False)

    print()
    print(f"✅ AUTOUPDATE finalizado.")
    print(f"✅ Se actualizaron {cambios} canales.")

else:

    print()
    print("No hubo cambios.")
