#!/usr/bin/env python3
"""Asistente para conectar tu cuenta de Meta (Facebook/Instagram) y, si quieres, ElevenLabs y HeyGen.

Ejecútalo en una sesión aparte de Termux (desliza desde la izquierda → NEW SESSION):
    marketing-configurar
Las claves se guardan solo en este móvil: ~/.config/marketing/config.json
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

CONFIG = os.environ.get("MARKETING_CONFIG", os.path.expanduser("~/.config/marketing/config.json"))
GRAPH = "https://graph.facebook.com/v21.0/"
VOCES = ["es-ES-AlvaroNeural", "es-ES-ElviraNeural", "es-CO-GonzaloNeural", "es-CO-SalomeNeural",
         "es-MX-JorgeNeural", "es-MX-DaliaNeural", "es-AR-TomasNeural", "es-AR-ElenaNeural"]


def g(path, token, **p):
    p["access_token"] = token
    try:
        with urllib.request.urlopen(GRAPH + path + "?" + urllib.parse.urlencode(p), timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        err = json.load(e).get("error", {})
        raise SystemExit(f"Meta dice: {err.get('message')}")


def pregunta(texto, defecto=""):
    r = input(f"{texto}" + (f" [{defecto}]" if defecto else "") + ": ").strip()
    return r or defecto


def elegir(titulo, opciones):
    print(f"\n{titulo}")
    for i, (_, etiqueta) in enumerate(opciones, 1):
        print(f"  {i}. {etiqueta}")
    while True:
        r = pregunta("Número", "1")
        if r.isdigit() and 1 <= int(r) <= len(opciones):
            return opciones[int(r) - 1][0]


def heygen_avatares(clave):
    """Tus avatares de HeyGen; None si la clave no vale."""
    req = urllib.request.Request("https://api.heygen.com/v3/avatars/looks?ownership=private&limit=50",
                                 headers={"x-api-key": clave, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r).get("data", [])
    except urllib.error.HTTPError as e:
        return None if e.code in (401, 403) else []
    except OSError:
        print("No hay conexión con HeyGen; guardo la clave y lo intentas luego.")
        return []


def main():
    try:
        c = json.load(open(CONFIG))
    except OSError:
        c = {}
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    print(__doc__)

    print("== 1. Meta (Facebook e Instagram) ==")
    print("Guía para sacar el token: https://github.com/josemegia/ubuntu-android/blob/main/docs/META.md")
    tok = pregunta("Pega tu token de Meta (Enter para dejar el actual)" if c.get("meta_token") else "Pega tu token de Meta (Enter para saltar)")
    if tok:
        c["meta_token"] = tok
    if c.get("meta_token"):
        t = c["meta_token"]
        yo = g("me", t, fields="name")
        print("Conectado como:", yo["name"])
        cuentas = g("me/adaccounts", t, fields="name,account_id,currency,account_status", limit=50).get("data", [])
        if not cuentas:
            sys.exit("Este token no ve ninguna cuenta publicitaria. Revisa los permisos (ads_management).")
        c["cuenta"] = elegir("¿Qué cuenta publicitaria uso?",
                             [(x["id"], f"{x['name']} · {x['currency']}" + ("" if x["account_status"] == 1 else " (NO activa)")) for x in cuentas])
        paginas = g("me/accounts", t, fields="name,id,instagram_business_account", limit=50).get("data", [])
        if not paginas:
            sys.exit("Este token no ve ninguna página. Necesitas una página de Facebook y el permiso pages_show_list.")
        pid = elegir("¿Con qué página de Facebook se publican los anuncios?", [(x["id"], x["name"]) for x in paginas])
        c["pagina"] = pid
        ig = next((x.get("instagram_business_account", {}).get("id") for x in paginas if x["id"] == pid), None)
        c["instagram"] = ig or ""
        print("Instagram vinculado a la página:", "sí" if ig else "no (los anuncios irán solo a Facebook)")
        w = pregunta("\nWhatsApp que recibirá los mensajes, con prefijo y sin '+' (ej. 34600111222)", c.get("whatsapp", ""))
        c["whatsapp"] = "".join(ch for ch in w if ch.isdigit())
        c["pais"] = pregunta("País donde anuncias, código de 2 letras (ES, CO, MX...)", c.get("pais", "ES")).upper()
        c["nombre_legal"] = pregunta("Nombre de la persona o empresa que paga los anuncios (obligatorio en la UE)", c.get("nombre_legal", yo["name"]))

    print("\n== 2. Voz ==")
    for i, v in enumerate(VOCES, 1):
        print(f"  {i}. {v}")
    r = pregunta("Voz gratuita por defecto (número)", str(VOCES.index(c.get("voz_gratis", VOCES[0])) + 1))
    if r.isdigit() and 1 <= int(r) <= len(VOCES):
        c["voz_gratis"] = VOCES[int(r) - 1]
    k = pregunta("Clave de ElevenLabs para usar TU voz (opcional, Enter para saltar)")
    if k:
        c["elevenlabs_key"] = k
        v = pregunta("ID de tu voz en ElevenLabs si ya la tienes (si no, Enter y luego usa voz-clonar)", c.get("elevenlabs_voz", ""))
        if v:
            c["elevenlabs_voz"] = v

    print("\n== 3. HeyGen: vídeos con tu avatar (opcional) ==")
    print("Clave en https://platform.heygen.com/api-keys · tu avatar se crea en https://app.heygen.com")
    k = pregunta("Clave de HeyGen (Enter para " + ("dejar la actual" if c.get("heygen_key") else "saltar") + ")")
    if k:
        c["heygen_key"] = k
    if c.get("heygen_key"):
        looks = heygen_avatares(c["heygen_key"])
        if looks is None:
            print("HeyGen no acepta esa clave. Revísala y vuelve a ejecutar marketing-configurar.")
            if k:
                c.pop("heygen_key", None)
        elif not looks:
            print("Clave correcta, pero aún no tienes avatar propio. Créalo en https://app.heygen.com y vuelve aquí.")
        else:
            elegido = elegir("¿Qué avatar uso en tus vídeos?", [(x["id"], x.get("name") or x["id"]) for x in looks])
            c["heygen_avatar"] = elegido
            c["heygen_avatar_nombre"] = next((x.get("name") for x in looks if x["id"] == elegido), "")
            print("Avatar elegido:", c["heygen_avatar_nombre"] or elegido)

    with open(CONFIG, "w") as f:
        json.dump(c, f, indent=1)
    os.chmod(CONFIG, 0o600)
    print("\nGuardado en", CONFIG)
    if c.get("meta_token"):
        subprocess.run(["meta", "comprobar"])
    print("\nListo. Vuelve a Claude y dile: «quiero una campaña para mi negocio».")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelado. No se ha guardado nada nuevo.")
