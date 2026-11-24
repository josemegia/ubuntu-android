#!/usr/bin/env python3
"""Imágenes y clips de apoyo hechos con IA en ArtCraft (gasta créditos de tu cuenta de ArtCraft).

  escena imagen "una panadería al amanecer, luz cálida"          imagen vertical 9:16
  escena imagen "el mismo local de noche" --ref https://.../foto.jpg
  escena video "la cámara entra despacio en la panadería"        clip vertical de 5 segundos
  escena video "el pan sale del horno" --inicio https://.../foto.jpg --dur 8
  escena ... --formato 16:9          también 1:1
  escena ... -o fondo.png            dónde guardarlo (por defecto, en ~/Descargas)
  escena recoger jinf_...            bajar un trabajo que se quedó a medias
  escena comprobar                   comprueba tu clave

Sirve para escenas, fondos y planos de apoyo. NO pone voz ni mueve los labios: para eso están
video-anuncio y video-avatar. Las fotos de referencia tienen que ser direcciones de internet
(https://...), no archivos del móvil. La clave se pone con  marketing-configurar.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

API = os.environ.get("ARTCRAFT_API", "https://api.storyteller.ai")
CONFIG = os.environ.get("MARKETING_CONFIG", os.path.expanduser("~/.config/marketing/config.json"))
# Cloudflare rechaza (403, error 1010) el User-Agent por defecto de Python, también en la descarga.
AGENTE = "ubuntu-android-escena/1.0"
FORMATOS = {"9:16": "tall_nine_by_sixteen", "16:9": "wide_sixteen_by_nine", "1:1": "square"}
SIGUE = ("pending", "started", "attempt_failed")
ESPERA_MAX = 30 * 60


def cfg():
    try:
        return json.load(open(CONFIG))
    except OSError:
        return {}


def llamar(metodo, ruta, clave, cuerpo=None, intentos=4):
    cab = {"Authorization": f"Bearer {clave}", "Accept": "application/json", "User-Agent": AGENTE}
    datos = None
    if cuerpo is not None:
        datos = json.dumps(cuerpo).encode()
        cab["Content-Type"] = "application/json"
    for i in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + ruta, data=datos, headers=cab, method=metodo), timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            texto = e.read().decode(errors="replace")
            try:
                err = json.loads(texto)
            except ValueError:
                err = {}
            if e.code == 401:
                sys.exit("ArtCraft no acepta tu clave. Vuelve a ponerla con  marketing-configurar  (otra sesión de Termux).")
            if e.code == 402:
                sys.exit("No te quedan créditos en ArtCraft. Recarga en https://getartcraft.com/pricing o sigue sin esta escena.")
            if e.code == 404:
                raise LookupError(ruta)
            if e.code in (429, 500, 502, 503, 504) and i < intentos - 1:
                time.sleep(int(e.headers.get("Retry-After") or 10))
                continue
            detalle = err.get("error_message") or err.get("message") or err.get("error_code_str") or texto[:200] or e.reason
            sys.exit(f"ArtCraft dice ({e.code}): {detalle}")
        except (urllib.error.URLError, TimeoutError) as e:
            if i < intentos - 1:
                time.sleep(5)
                continue
            sys.exit(f"No hay conexión con ArtCraft: {e}")


def comprobar(clave):
    """Un trabajo inventado da 404 con clave buena y 401 con clave mala."""
    try:
        llamar("GET", "/v1/omni_api/job_status/job/jinf_test000000000000000000000", clave)
    except LookupError:
        pass
    print("ArtCraft conectado: la clave es correcta.")
    print("Tus créditos se ven en https://app.getartcraft.com")


def referencias(urls):
    for u in urls or []:
        if not u.startswith(("http://", "https://")):
            sys.exit(f"«{u}» no es una dirección de internet. ArtCraft solo acepta fotos publicadas (https://...).\n"
                     "Publica la foto con  landing-publicar  y usa su dirección.")
    return list(urls or [])


def esperar(token, clave):
    print(f"ArtCraft está trabajando ({token}). Una imagen tarda alrededor de un minuto; un vídeo, varios.")
    inicio, ultimo = time.time(), -1
    while True:
        estado = llamar("GET", f"/v1/omni_api/job_status/job/{token}", clave)["state"]
        st = estado["status"]["status"]
        if st == "complete_success":
            return estado["maybe_result"]["media_links"]["cdn_url"]
        if st not in SIGUE:
            motivo = {"dead": "se quedó sin terminar", "cancelled_by_user": "lo cancelaste",
                      "cancelled_by_system": "ArtCraft lo canceló"}.get(st, "falló")
            causa = estado["status"].get("maybe_failure_category")
            sys.exit(f"ArtCraft no pudo hacerlo: {motivo}" + (f" ({causa})" if causa else "") + ". Prueba con otra descripción o sigue sin esta escena.")
        pct = estado["status"].get("progress_percentage") or 0
        if pct != ultimo:
            print(f"  {pct} %", flush=True)
            ultimo = pct
        if time.time() - inicio > ESPERA_MAX:
            sys.exit(f"ArtCraft sigue trabajando. Recógelo luego con:  escena recoger {token}")
        time.sleep(int(os.environ.get("AC_POLL", 6)))


def bajar(url, salida, extension_defecto):
    if not salida:
        ext = os.path.splitext(url.split("?")[0])[1].lower() or extension_defecto
        carpeta = os.path.expanduser("~/Descargas")
        os.makedirs(carpeta, exist_ok=True)
        salida = os.path.join(carpeta, time.strftime("escena-%Y%m%d-%H%M%S") + ext)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": AGENTE}), timeout=600) as r, open(salida, "wb") as f:
        while True:
            trozo = r.read(1 << 20)
            if not trozo:
                break
            f.write(trozo)
    print(f"Listo: {salida}")
    try:   # el archivo ya está guardado: que falte o se cuelgue ver-en-movil no es un error
        subprocess.run(["ver-en-movil", salida], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="que", metavar="imagen | video | recoger | comprobar")

    im = sub.add_parser("imagen", help="crear una imagen")
    im.add_argument("prompt", help="qué se ve, entre comillas")
    im.add_argument("--ref", action="append", metavar="URL", help="foto de referencia publicada (se puede repetir)")
    im.add_argument("--modelo", default="nano_banana", help="nano_banana (por defecto), nano_banana_pro, gpt_image_1p5...")

    vi = sub.add_parser("video", help="crear un clip de vídeo")
    vi.add_argument("prompt", help="qué pasa en el clip, entre comillas")
    vi.add_argument("--inicio", metavar="URL", help="imagen publicada con la que empieza el clip")
    vi.add_argument("--ref", action="append", metavar="URL", help="foto de referencia publicada (se puede repetir)")
    vi.add_argument("--dur", type=int, default=5, help="segundos (por defecto 5)")
    vi.add_argument("--modelo", default="seedance_2p0", help="seedance_2p0 (por defecto), kling_3p0_pro, veo_3...")
    vi.add_argument("--con-sonido", action="store_true", help="que ArtCraft genere sonido ambiente")

    for p in (im, vi):
        p.add_argument("--formato", default="9:16", choices=list(FORMATOS))
        p.add_argument("-o", "--salida", help="archivo de salida (por defecto, en ~/Descargas)")

    re = sub.add_parser("recoger", help="bajar un trabajo ya lanzado")
    re.add_argument("token", help="el código jinf_... que dio ArtCraft")
    re.add_argument("-o", "--salida")

    sub.add_parser("comprobar", help="comprobar la clave")
    a = ap.parse_args()
    if not a.que:
        ap.print_help()
        return

    clave = os.environ.get("ARTCRAFT_API_KEY") or cfg().get("artcraft_key")
    if not clave:
        sys.exit("Falta tu clave de ArtCraft: ejecuta  marketing-configurar  en otra sesión de Termux.")

    if a.que == "comprobar":
        comprobar(clave)
        return
    if a.que == "recoger":
        try:
            bajar(esperar(a.token, clave), a.salida, ".mp4")
        except LookupError:
            sys.exit("ArtCraft no conoce ese código. Revisa que lo has copiado entero (empieza por jinf_).")
        return

    # El mismo identificador en los reintentos: ArtCraft no crea (ni cobra) dos veces lo mismo.
    cuerpo = {"idempotency_token": str(uuid.uuid4()), "model": a.modelo, "prompt": a.prompt.strip(),
              "aspect_ratio": FORMATOS[a.formato]}
    if not cuerpo["prompt"]:
        sys.exit("Falta describir la escena entre comillas.")
    refs = referencias(a.ref)

    if a.que == "imagen":
        cuerpo["image_batch_count"] = 1
        if refs:
            cuerpo["image_urls"] = refs
        ruta, ext = "/v1/omni_api/generate/image", ".png"
    else:
        cuerpo["duration_seconds"] = a.dur
        cuerpo["generate_audio"] = a.con_sonido
        if a.inicio:
            cuerpo["start_frame_image_url"] = referencias([a.inicio])[0]
        if refs:
            cuerpo["reference_image_urls"] = refs
        ruta, ext = "/v1/omni_api/generate/video", ".mp4"

    try:
        token = llamar("POST", ruta, clave, cuerpo)["inference_job_token"]
    except LookupError:
        sys.exit("ArtCraft no reconoce la petición. Actualiza el kit con  kit-actualizar  y vuelve a probar.")
    bajar(esperar(token, clave), a.salida, ext)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelado. Si ArtCraft ya había empezado, el resultado aparecerá en tu cuenta de ArtCraft.")
