import json
import re
import requests

URL_ORIGEN="https://mundodeportes.online/pandatv/playpre/canales.json"
ARCHIVO_DESTINO="novaplay.json"
DEBUG=True

CATEGORIAS_IGNORADAS={"PLUTO","PLUTO TV","PLUTOTV"}

EQUIVALENCIAS={
    "PARAGUAY🇵🇾":{
        "GEN_TV":["GEN TV","GEN PY - MUNDIAL"],
        "PARAVISION  ": ["PARAVISION"],
        "RPC":["TRECE PY","TRECE PY - MUNDIAL"],
        "UNICANAL":["UNICANAL PY","UNICANAL PY - MUNDIAL"],
        "POPU TV": ["POPUTV PY", "POPUTV PY - MUNDIAL"],
        "PY | SNT  ": ["SNT"],
    "TELEFUTURO HD": ["TELEFUTURO"],
    "C9N  ": ["C9N"],
    "HEI NEW": ["HEI NOW"],
    "MEGA TV  PY": ["MEGA TV PY"],
    "SUR TV": ["SUR TV"],
    "ABC TV": ["ABC TV"],
    "NOTICIAS_PY  ": ["NPY"],
    "A24 PY": ["A24 PY"],
    "CANALPRO PY": ["CANAL PRO"],
    "AMERICA PY": ["AMERICA PY"],
    "LA TELE": ["LA TELE"],
    },
    "ARGENTINA🇦🇷":{
        "TELEFE":["TELEFE","TELEFE - MUNDIAL"],
        "TV PUBLICA":["TV PUBLICA","TV PUBLICA AR - MUNDIAL"],
         "AMERICA TV ": ["AMERICA TV"],
    "EL TRECE": ["EL TRECE"],
    "CANAL 9 ": ["CANAL 9"],
    "TN NOTICIAS": ["TN NOTICIAS"],
    "C5N": ["C5N"],
    "LN+ - LA NACION": ["LN+"],
    "CRONICA TV": ["CRONICA"],
    "A24": ["A24 ARGENTINA"],
    "CANAL 26": ["CANAL 26"],
    },
    "INFANTILES 👦":{
        "Cartoonito":["CARTOONITO"],
        "Nickelodeon":["NICKELODEON"],
        "Discovery Kids":["DISCOVERY KIDS"],
        "Disney Channel":["DISNEY CHANNEL"],
        "Tooncast":["TOONCAST"],
        "Nick Jr":["NICK JR"],
        "CARTOON NETWORK":["CARTOON NETWORK"],
        "PLIM PLIM":["PLIM PLIM"],
    },
    "CULTURA Y COCINA 🐢":{
        "HGTV":["HGTV"],
    },
"⚽EVENTOS FLOW ⚽":{
        "EVENTOS FLOW 1":["EVENTOS FLOW 1"],
        "EVENTOS FLOW 2":["EVENTOS FLOW 2"], 
    }
}

def debug(m):
    if DEBUG: print(m)

def normalizar(t):
    if not t: return ""
    t=t.upper().encode("ascii","ignore").decode()
    return re.sub(r"[^A-Z0-9]","",t)

debug("Descargando origen...")
origen=requests.get(URL_ORIGEN,timeout=30).json()

with open(ARCHIVO_DESTINO,"r",encoding="utf8") as f:
    destino=json.load(f)

indice={}
for cat in origen:
    nc=normalizar(cat.get("name",""))
    indice[nc]={}
    for c in cat.get("samples",[]):
        indice[nc][normalizar(c.get("name",""))]=c

mapa={}
for categoria,canales in EQUIVALENCIAS.items():
    ck=normalizar(categoria)
    if ck not in indice:
        debug(f"Categoria no encontrada: {categoria}")
        continue
    for origen_nombre,destinos in canales.items():
        ok=normalizar(origen_nombre)
        if ok not in indice[ck]:
            debug(f"No encontrado {origen_nombre} en {categoria}")
            continue
        origen_canal=indice[ck][ok]
        for d in destinos:
            mapa[normalizar(d)]=origen_canal

cambios=0
for categoria in destino:
    if normalizar(categoria.get("title","")) in {normalizar(x) for x in CATEGORIAS_IGNORADAS}:
        continue
    for canal in categoria.get("items",[]):
        k=normalizar(canal.get("name",""))
        if k not in mapa:
            continue
        nueva=mapa[k].get("url","")
        if nueva and canal.get("url","")!=nueva:
            canal["url"]=nueva
            cambios+=1

if cambios:
    with open(ARCHIVO_DESTINO,"w",encoding="utf8") as f:
        json.dump(destino,f,indent=2,ensure_ascii=False)
    print(f"Actualizados {cambios} canales")
else:
    print("No hubo cambios")
