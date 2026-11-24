#!/usr/bin/env python3
"""Vídeo con TU avatar de HeyGen hablando (gasta créditos de tu cuenta de HeyGen).

  video-avatar --guion guion.txt --salida avatar.mp4            vertical 9:16 para Reels/Stories
  video-avatar --guion guion.txt --formato 1:1 --salida a.mp4    cuadrado (también 16:9, 4:5)
  video-avatar --guion guion.txt --audio mi-grabacion.m4a ...    tu propia grabación como voz
  video-avatar --guion guion.txt --voz-heygen ...                la voz de tu avatar en HeyGen
  video-avatar --subtitulos ...                                  con subtítulos incrustados
  video-avatar --avatares                                        lista tus avatares
  video-avatar --comprobar                                       clave y saldo

Voz: si configuraste ElevenLabs con tu voz, se usa esa (sale igual que en tus otros vídeos);
si no, la voz de tu avatar en HeyGen. La clave y el avatar se eligen con  marketing-configurar.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import movil  # noqa: E402
import voz  # noqa: E402

API = os.environ.get("HEYGEN_API", "https://api.heygen.com")
CONFIG = os.environ.get("MARKETING_CONFIG", os.path.expanduser("~/.config/marketing/config.json"))
ESPERA_MAX = 40 * 60   # HeyGen suele tardar 2-10 minutos


def cfg():
    try:
        return json.load(open(CONFIG))
    except OSError:
        return {}


def llamar(metodo, ruta, clave, cuerpo=None, archivo=None, intentos=4):
    # Misma clave de idempotencia en los reintentos: HeyGen no crea (ni cobra) dos veces el mismo vídeo.
    cab = {"x-api-key": clave, "Accept": "application/json", "Idempotency-Key": uuid.uuid4().hex}
    datos = None
    if archivo:
        frontera = uuid.uuid4().hex
        nombre = os.path.basename(archivo)
        tipo = {"mp3": "audio/mpeg", "wav": "audio/wav", "m4a": "audio/mp4"}.get(nombre.rsplit(".", 1)[-1].lower(), "application/octet-stream")
        datos = (f"--{frontera}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{nombre}\"\r\n"
                 f"Content-Type: {tipo}\r\n\r\n").encode() + open(archivo, "rb").read() + f"\r\n--{frontera}--\r\n".encode()
        cab["Content-Type"] = f"multipart/form-data; boundary={frontera}"
    elif cuerpo is not None:
        datos = json.dumps(cuerpo).encode()
        cab["Content-Type"] = "application/json"
    if metodo == "GET":
        del cab["Idempotency-Key"]
    for i in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + ruta, data=datos, headers=cab, method=metodo), timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            try:
                err = json.load(e).get("error", {})
            except Exception:
                err = {}
            if e.code in (409, 429) and i < intentos - 1:
                time.sleep(int(e.headers.get("Retry-After") or 10))
                continue
            if e.code == 401:
                sys.exit("HeyGen no acepta tu clave. Vuelve a ponerla con  marketing-configurar  (otra sesión de Termux).")
            sys.exit(f"HeyGen dice ({e.code}): {err.get('message') or e.reason}")
        except (urllib.error.URLError, TimeoutError) as e:
            if i < intentos - 1:
                time.sleep(5)
                continue
            sys.exit(f"No hay conexión con HeyGen: {e}")


def avatares(clave):
    vistos, token = [], None
    while True:
        q = "/v3/avatars/looks?ownership=private&limit=50" + (f"&token={token}" if token else "")
        r = llamar("GET", q, clave)
        vistos += r.get("data", [])
        token = r.get("next_token")
        if not r.get("has_more") or not token:
            return vistos


def bajar(url, salida):
    with urllib.request.urlopen(url, timeout=600) as r, open(salida, "wb") as f:
        while True:
            trozo = r.read(1 << 20)
            if not trozo:
                break
            f.write(trozo)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--guion", help="archivo .txt con lo que dice el avatar (o el texto entre comillas)")
    ap.add_argument("--salida", default="avatar.mp4")
    ap.add_argument("--formato", default="9:16", choices=["9:16", "1:1", "4:5", "16:9"])
    ap.add_argument("--audio", help="usar esta grabación (mp3, wav o m4a) como voz")
    ap.add_argument("--voz-heygen", action="store_true", help="usar la voz del avatar en HeyGen aunque tengas ElevenLabs")
    ap.add_argument("--subtitulos", action="store_true", help="subtítulos incrustados por HeyGen")
    ap.add_argument("--avatar", help="ID de otro avatar (por defecto, el elegido en marketing-configurar)")
    ap.add_argument("--avatares", action="store_true")
    ap.add_argument("--comprobar", action="store_true")
    a = ap.parse_args()

    c = cfg()
    clave = c.get("heygen_key")
    if not clave:
        sys.exit("Falta tu clave de HeyGen: ejecuta  marketing-configurar  en otra sesión de Termux.")

    if a.comprobar:
        yo = llamar("GET", "/v3/users/me", clave).get("data", {})
        print("HeyGen conectado:", yo.get("email") or yo.get("username") or "sí")
        if yo.get("billing"):
            print("Saldo/plan:", json.dumps(yo["billing"], ensure_ascii=False))
        print("Avatar elegido:", c.get("heygen_avatar_nombre") or c.get("heygen_avatar") or "ninguno")
        return
    if a.avatares:
        lista = avatares(clave)
        if not lista:
            print("No tienes avatares propios. Crea el tuyo en https://app.heygen.com (Avatars → Create).")
        for x in lista:
            print(f"{x['id']}  {x.get('name', '')}  ({x.get('avatar_type', '')}, {x.get('preferred_orientation', '')})")
        return
    if not a.guion:
        sys.exit("Falta --guion (el texto que dice el avatar).")

    avatar = a.avatar or c.get("heygen_avatar")
    if not avatar:
        sys.exit("Aún no has elegido avatar: ejecuta  marketing-configurar  (o pasa --avatar <ID>; míralos con --avatares).")
    texto = open(a.guion).read().strip() if os.path.isfile(a.guion) else a.guion.strip()
    if not texto:
        sys.exit("El guion está vacío.")

    cuerpo = {"type": "avatar", "avatar_id": avatar, "aspect_ratio": a.formato, "resolution": "1080p",
              "output_format": "mp4", "title": os.path.splitext(os.path.basename(a.salida))[0][:80]}
    if a.subtitulos:
        cuerpo["caption"] = {"file_format": "srt", "style": "default"}

    audio = a.audio
    if not audio and not a.voz_heygen and c.get("elevenlabs_key") and c.get("elevenlabs_voz"):
        audio = os.path.join(tempfile.mkdtemp(prefix="avatar-"), "voz.mp3")
        print("Voz:", voz.generar(texto, audio))
    if audio:
        print("Subiendo la voz a HeyGen...")
        cuerpo["audio_asset_id"] = llamar("POST", "/v3/assets", clave, archivo=audio)["data"]["asset_id"]
    else:
        cuerpo["script"] = texto
        if c.get("heygen_voz"):
            cuerpo["voice_id"] = c["heygen_voz"]

    vid = llamar("POST", "/v3/videos", clave, cuerpo)["data"]["video_id"]
    print(f"HeyGen está creando el vídeo ({vid}). Suele tardar de 2 a 10 minutos...")
    inicio = time.time()
    while True:
        time.sleep(int(os.environ.get("HG_POLL", 15)))
        d = llamar("GET", f"/v3/videos/{vid}", clave)["data"]
        if d["status"] == "completed":
            break
        if d["status"] == "failed":
            sys.exit(f"HeyGen no pudo hacer el vídeo: {d.get('failure_message') or d.get('failure_code')}")
        if time.time() - inicio > ESPERA_MAX:
            sys.exit(f"HeyGen sigue trabajando. Míralo luego en {d.get('video_page_url') or 'https://app.heygen.com'}")
    url = (d.get("captioned_video_url") if a.subtitulos else None) or d["video_url"]
    bajar(url, a.salida)
    print(f"Vídeo listo: {a.salida} ({d.get('duration') or '?'} s)")
    movil.entregar(a.salida, "Tu vídeo con avatar está listo")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelado. Si HeyGen ya había empezado, el vídeo aparecerá en tu cuenta de HeyGen.")
