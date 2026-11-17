#!/usr/bin/env python3
"""Convierte texto en voz (mp3).

  voz "Hola, soy Ana y te invito a un café." salida.mp3
  voz --archivo guion.txt salida.mp3
  voz --edge es-CO-SalomeNeural "texto" salida.mp3     (forzar una voz gratuita)
  voz --lista                                           (voces gratuitas en español)

Si configuraste ElevenLabs con tu voz clonada (voz-clonar), usa tu voz.
Si no, usa una voz gratuita de Microsoft (edge-tts).
"""
import json
import os
import subprocess
import sys
import urllib.request

CONFIG = os.environ.get("MARKETING_CONFIG", os.path.expanduser("~/.config/marketing/config.json"))
VENV_PY = os.environ.get("UA_PYTHON", "/opt/ubuntu-android-venv/bin/python")
GRATIS = {
    "es-ES-AlvaroNeural": "hombre, España", "es-ES-ElviraNeural": "mujer, España",
    "es-CO-GonzaloNeural": "hombre, Colombia", "es-CO-SalomeNeural": "mujer, Colombia",
    "es-MX-JorgeNeural": "hombre, México", "es-MX-DaliaNeural": "mujer, México",
    "es-AR-TomasNeural": "hombre, Argentina", "es-AR-ElenaNeural": "mujer, Argentina",
    "es-US-AlonsoNeural": "hombre, EE. UU.", "es-US-PalomaNeural": "mujer, EE. UU.",
}


def config():
    try:
        return json.load(open(CONFIG))
    except OSError:
        return {}


def eleven(texto, salida, clave, voz):
    cuerpo = json.dumps({"text": texto, "model_id": "eleven_multilingual_v2",
                         "voice_settings": {"stability": 0.5, "similarity_boost": 0.85, "style": 0.2}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voz}", data=cuerpo,
                                 headers={"xi-api-key": clave, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=180) as r, open(salida, "wb") as f:
        f.write(r.read())


def edge(texto, salida, voz):
    subprocess.run([VENV_PY, "-m", "edge_tts", "--voice", voz, "--text", texto, "--write-media", salida], check=True)


def generar(texto, salida, forzar_edge=None):
    c = config()
    if not forzar_edge and c.get("elevenlabs_key") and c.get("elevenlabs_voz"):
        try:
            eleven(texto, salida, c["elevenlabs_key"], c["elevenlabs_voz"])
            return "ElevenLabs (tu voz)"
        except Exception as e:  # sin saldo, clave caducada... → voz gratuita
            print(f"ElevenLabs falló ({e}); uso la voz gratuita.", file=sys.stderr)
    v = forzar_edge or c.get("voz_gratis", "es-ES-AlvaroNeural")
    edge(texto, salida, v)
    return f"edge-tts ({v})"


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        sys.exit(__doc__)
    if a[0] == "--lista":
        for k, v in GRATIS.items():
            print(f"{k:<22} {v}")
        sys.exit()
    forzar = None
    if a[0] == "--edge":
        forzar, a = a[1], a[2:]
    if a[0] == "--archivo":
        texto, a = open(a[1]).read().strip(), a[2:]
    else:
        texto, a = a[0], a[1:]
    salida = a[0] if a else "voz.mp3"
    print("Voz generada con", generar(texto, salida, forzar), "→", salida)
