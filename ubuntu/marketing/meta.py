#!/usr/bin/env python3
"""Meta Ads (Facebook + Instagram) desde la terminal. Todo se crea EN PAUSA.

  meta comprobar                     ¿funciona el token? ¿qué cuenta y página uso?
  meta buscar-lugar "Majadahonda"    claves de ciudades/regiones para segmentar
  meta subir-video video.mp4         sube el vídeo a la cuenta y devuelve su id
  meta campana ficha.json            crea campaña + conjunto + anuncio (EN PAUSA)
  meta activar <campaign_id>         activa campaña, conjuntos y anuncios
  meta pausar <campaign_id>
  meta resultados [<campaign_id>]    alcance, clics, gasto, conversaciones
  meta campanas                      lista las campañas de la cuenta

Configuración: ~/.config/marketing/config.json (la crea marketing-configurar).
"""
import datetime
import json
import os
import subprocess
import sys
import time

GRAPH = "https://graph.facebook.com/v21.0/"
CONFIG = os.environ.get("MARKETING_CONFIG", os.path.expanduser("~/.config/marketing/config.json"))
REGISTRO = os.path.expanduser("~/.config/marketing/campanas.json")
UE = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV",
      "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"}


def cfg():
    try:
        c = json.load(open(CONFIG))
    except OSError:
        sys.exit("Falta configurar Meta: abre otra sesión de Termux y ejecuta  marketing-configurar")
    if not c.get("meta_token"):
        sys.exit("No hay token de Meta. Ejecuta  marketing-configurar  (guía: docs/META.md del repo).")
    return c


C = None


def call(path, data=None, get=False, fatal=True, files=None):
    cmd = ["curl", "-s", "--max-time", "600"] + (["-G"] if get else [])
    for k, v in (data or {}).items():
        val = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        cmd += ["--data-urlencode", f"{k}={val}"] if not files else ["--form-string", f"{k}={val}"]
    for k, ruta in (files or {}).items():
        cmd += ["-F", f"{k}=@{ruta}"]
    tok = ["--form-string" if files else "--data-urlencode", f"access_token={C['meta_token']}"]
    out = subprocess.run(cmd + tok + [GRAPH + path], capture_output=True, text=True).stdout
    try:
        r = json.loads(out)
    except ValueError:
        r = {"error": {"message": out[:300] or "sin respuesta (¿hay conexión?)"}}
    if "error" in r:
        e = r["error"]
        msg = f"ERROR en {path}: {e.get('error_user_msg') or e.get('message')}"
        if e.get("code") == 190:
            msg += "\n→ El token ha caducado o no vale. Renuévalo (docs/META.md) y ejecuta marketing-configurar."
        if fatal:
            sys.exit(msg)
        print(msg)
        return None
    return r


def guardar(nombre, datos):
    d = {}
    if os.path.exists(REGISTRO):
        d = json.load(open(REGISTRO))
    d[nombre] = datos
    json.dump(d, open(REGISTRO, "w"), indent=1, ensure_ascii=False)


def comprobar(_):
    yo = call("me", {"fields": "id,name"}, get=True)
    print("Token válido para:", yo["name"])
    act = call(C["cuenta"], {"fields": "name,currency,account_status,timezone_name"}, get=True)
    estado = {1: "activa", 2: "DESACTIVADA", 3: "con pagos pendientes"}.get(act.get("account_status"), act.get("account_status"))
    print(f"Cuenta publicitaria: {act['name']} ({C['cuenta']}) · {act['currency']} · {estado}")
    pag = call(C["pagina"], {"fields": "name,instagram_business_account"}, get=True)
    print("Página:", pag["name"], "· Instagram:", "sí" if C.get("instagram") else "no vinculado")
    print("WhatsApp:", "+" + C["whatsapp"] if C.get("whatsapp") else "no configurado")


def buscar_lugar(args):
    q = " ".join(args) or sys.exit("Uso: meta buscar-lugar <ciudad>")
    r = call("search", {"type": "adgeolocation", "q": q, "location_types": ["city", "region", "zip"], "limit": "8"}, get=True)
    for x in r.get("data", []):
        print(f"{x['key']:>10}  {x['type']:<7} {x['name']}, {x.get('region', '')}, {x.get('country_code', '')}")
    if not r.get("data"):
        print("Nada encontrado. Prueba con otro nombre.")


def subir_video(args):
    ruta = args[0] if args else sys.exit("Uso: meta subir-video <video.mp4>")
    print("Subiendo vídeo a Meta...")
    v = call(f"{C['cuenta']}/advideos", {"name": os.path.basename(ruta)}, files={"source": ruta})["id"]
    for _ in range(60):  # esperar a que Meta lo procese
        st = call(v, {"fields": "status"}, get=True).get("status", {}).get("video_status")
        if st == "ready":
            break
        time.sleep(5)
    print("video_id:", v)
    return v


def miniatura(video_id):
    th = call(video_id, {"fields": "thumbnails{uri,is_preferred}"}, get=True)["thumbnails"]["data"]
    return next((x["uri"] for x in th if x.get("is_preferred")), th[0]["uri"])


def campana(args):
    """ficha.json:
    {"nombre": "Café Majadahonda", "destino": "whatsapp" | "web", "web": "https://...",
     "pais": "ES", "lugar": {"key": "1234", "radio_km": 10}  o  {"lat": 40.47, "lon": -3.87, "radio_km": 10},
     "edad": [30, 60], "presupuesto_diario": 6, "dias": 7,
     "video": "/home/android/Descargas/Campañas/x/anuncio.mp4"  o  "video_id": "...",
     "texto": "texto principal del anuncio", "titulo": "titular corto",
     "mensaje_prellenado": "Hola, vi tu anuncio y...", "bienvenida": "¡Hola! ¿En qué te ayudo?"}
    """
    f = json.load(open(args[0])) if args else sys.exit("Uso: meta campana ficha.json")
    destino = f.get("destino", "whatsapp")
    if destino == "whatsapp" and not C.get("whatsapp"):
        sys.exit("No hay número de WhatsApp configurado (marketing-configurar).")
    if destino == "web" and not f.get("web"):
        sys.exit("Falta la dirección de la web en la ficha (\"web\").")
    vid = f.get("video_id") or subir_video([f["video"]])
    thumb = miniatura(vid)
    fin = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=int(f.get("dias", 7)))).strftime("%Y-%m-%dT%H:%M:%S+0000")

    lugar = f["lugar"]
    radio = {"radius": int(lugar.get("radio_km", 10)), "distance_unit": "kilometer"}
    if "key" in lugar:
        geo = {"cities": [{"key": str(lugar["key"]), **radio}]}
    else:
        geo = {"custom_locations": [{"latitude": lugar["lat"], "longitude": lugar["lon"], **radio}]}
    geo["location_types"] = ["home", "recent"]
    edad = f.get("edad", [25, 65])
    segm = {"age_min": edad[0], "age_max": edad[1], "geo_locations": geo,
            "publisher_platforms": ["facebook", "instagram"], "facebook_positions": ["facebook_reels", "story"],
            "instagram_positions": ["reels", "story"], "targeting_automation": {"advantage_audience": 0}}
    if not C.get("instagram"):
        segm.update(publisher_platforms=["facebook"]); segm.pop("instagram_positions")

    # presupuesto en céntimos de la moneda de la cuenta
    diario = str(int(round(float(f["presupuesto_diario"]) * 100)))
    objetivo = "OUTCOME_ENGAGEMENT" if destino == "whatsapp" else "OUTCOME_TRAFFIC"
    camp = call(f"{C['cuenta']}/campaigns", {"name": f["nombre"], "objective": objetivo, "special_ad_categories": [],
                                             "status": "PAUSED", "is_adset_budget_sharing_enabled": "false"})["id"]
    conj = {"name": f"{f['nombre']} · {edad[0]}-{edad[1]}", "campaign_id": camp, "status": "PAUSED",
            "daily_budget": diario, "billing_event": "IMPRESSIONS", "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
            "end_time": fin, "targeting": segm}
    if f.get("pais", C.get("pais", "")).upper() in UE:  # Ley de Servicios Digitales: obligatorio en la UE
        conj.update(dsa_beneficiary=C.get("nombre_legal", ""), dsa_payor=C.get("nombre_legal", ""))
    if destino == "whatsapp":
        conj.update(optimization_goal="CONVERSATIONS", destination_type="WHATSAPP",
                    promoted_object={"page_id": C["pagina"], "whatsapp_phone_number": C["whatsapp"]})
    else:
        conj.update(optimization_goal="LANDING_PAGE_VIEWS", destination_type="WEBSITE")
    adset = call(f"{C['cuenta']}/adsets", conj)["id"]

    vd = {"video_id": vid, "image_url": thumb, "title": f.get("titulo", ""), "message": f["texto"]}
    if destino == "whatsapp":
        vd["call_to_action"] = {"type": "WHATSAPP_MESSAGE", "value": {"app_destination": "WHATSAPP"}}
        if f.get("mensaje_prellenado"):
            vd["page_welcome_message"] = json.dumps({
                "type": "VISUAL_EDITOR", "version": 2, "landing_screen_type": "welcome_message", "media_type": "text",
                "text_format": {"customer_action_type": "autofill_message", "message": {
                    "autofill_message": {"content": f["mensaje_prellenado"]},
                    "text": f.get("bienvenida", "¡Hola! Gracias por escribir. ¿En qué te puedo ayudar?")}}}, ensure_ascii=False)
    else:
        vd["call_to_action"] = {"type": "LEARN_MORE", "value": {"link": f["web"]}}
    spec = {"page_id": C["pagina"], "video_data": vd}
    if C.get("instagram"):
        spec["instagram_user_id"] = C["instagram"]
    cr = call(f"{C['cuenta']}/adcreatives", {"name": f["nombre"], "object_story_spec": spec})["id"]
    ad = call(f"{C['cuenta']}/ads", {"name": f["nombre"], "adset_id": adset, "creative": {"creative_id": cr}, "status": "PAUSED"})["id"]

    ids = {"campaign": camp, "adset": adset, "ad": ad, "video": vid, "creado": datetime.date.today().isoformat()}
    guardar(f["nombre"], ids)
    total = float(f["presupuesto_diario"]) * int(f.get("dias", 7))
    print(json.dumps(ids, indent=1))
    print(f"\nCampaña creada EN PAUSA. Coste máximo si la activas: {f['presupuesto_diario']}/día × {f.get('dias', 7)} días = {total:g} (moneda de la cuenta).")
    print(f"Revisar en: https://adsmanager.facebook.com/adsmanager/manage/campaigns?act={C['cuenta'][4:]}")
    print(f"Para activarla:  meta activar {camp}")


def cambiar(args, estado):
    camp = args[0] if args else sys.exit("Falta el id de la campaña")
    for hijo in ("adsets", "ads"):
        for x in call(f"{camp}/{hijo}", {"fields": "id"}, get=True).get("data", []):
            call(x["id"], {"status": estado})
    call(camp, {"status": estado})
    print("Campaña", camp, "→", "ACTIVA" if estado == "ACTIVE" else "EN PAUSA")


def resultados(args):
    camps = [args[0]] if args else [x["id"] for x in call(f"{C['cuenta']}/campaigns", {"fields": "id", "effective_status": ["ACTIVE"], "limit": "20"}, get=True)["data"]]
    if not camps:
        print("No hay campañas activas. Usa  meta campanas  para ver todas.")
    for c in camps:
        info = call(c, {"fields": "name,effective_status"}, get=True)
        ins = call(f"{c}/insights", {"fields": "impressions,reach,clicks,spend,actions", "date_preset": "maximum"}, get=True).get("data", [])
        print(f"\n{info['name']} ({info['effective_status']})")
        if not ins:
            print("  Sin datos todavía.")
            continue
        i = ins[0]
        acc = {a["action_type"]: a["value"] for a in i.get("actions", [])}
        conv = acc.get("onsite_conversion.messaging_conversation_started_7d", "0")
        print(f"  Alcance {i.get('reach')} · Impresiones {i.get('impressions')} · Clics {i.get('clicks')} · Gasto {i.get('spend')}")
        print(f"  Conversaciones de WhatsApp iniciadas: {conv} · Visitas a la web: {acc.get('landing_page_view', '0')}")


def campanas(_):
    for x in call(f"{C['cuenta']}/campaigns", {"fields": "id,name,effective_status,created_time", "limit": "25"}, get=True)["data"]:
        print(f"{x['id']}  {x['effective_status']:<10} {x['created_time'][:10]}  {x['name']}")


ORDENES = {"comprobar": comprobar, "buscar-lugar": buscar_lugar, "subir-video": subir_video, "campana": campana,
           "activar": lambda a: cambiar(a, "ACTIVE"), "pausar": lambda a: cambiar(a, "PAUSED"),
           "resultados": resultados, "campanas": campanas}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ORDENES:
        sys.exit(__doc__)
    C = cfg()
    ORDENES[sys.argv[1]](sys.argv[2:])
