#!/usr/bin/env python3
"""Clona TU voz en ElevenLabs a partir de grabaciones hechas con el móvil.

  voz-clonar ~/Descargas/Voz/*.m4a
  voz-clonar --nombre "Ana" grabacion1.m4a grabacion2.m4a

Necesita una clave de ElevenLabs (marketing-configurar) y un plan de pago
(Starter o superior): la clonación no está en el plan gratuito.
Cómo grabar bien: docs/VOZ.md del repo. Clona solo tu propia voz.
"""
import json
import os
import subprocess
import sys

CONFIG = os.environ.get("MARKETING_CONFIG", os.path.expanduser("~/.config/marketing/config.json"))
a = sys.argv[1:]
if not a or a[0] in ("-h", "--help"):
    sys.exit(__doc__)
nombre = "Mi voz"
if a[0] == "--nombre":
    nombre, a = a[1], a[2:]
archivos = [x for x in a if os.path.isfile(x)]
if not archivos:
    sys.exit("No encuentro las grabaciones. Ponlas en Download/Ubuntu/Voz del móvil y usa ~/Descargas/Voz/*")

try:
    c = json.load(open(CONFIG))
except OSError:
    c = {}
if not c.get("elevenlabs_key"):
    sys.exit("Falta la clave de ElevenLabs: ejecuta  marketing-configurar  en otra sesión de Termux.")

# Unir y limpiar: un solo mp3 mono a 44,1 kHz (ElevenLabs acepta hasta varios minutos)
total = 0.0
for x in archivos:
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", x],
                       capture_output=True, text=True).stdout.strip()
    total += float(d or 0)
print(f"{len(archivos)} grabación(es), {total:.0f} segundos en total.")
if total < 45:
    print("Aviso: con menos de 1 minuto el parecido será peor. Lo ideal es 1-3 minutos.")

cmd = ["curl", "-s", "--max-time", "300", "-H", f"xi-api-key: {c['elevenlabs_key']}",
       "--form-string", f"name={nombre}", "--form-string", "remove_background_noise=true",
       "--form-string", "description=Voz clonada desde el móvil (ubuntu-android)"]
for x in archivos:
    cmd += ["-F", f"files=@{x}"]
r = subprocess.run(cmd + ["https://api.elevenlabs.io/v1/voices/add"], capture_output=True, text=True).stdout
try:
    r = json.loads(r)
except ValueError:
    sys.exit("ElevenLabs no respondió bien: " + r[:300])
if "voice_id" not in r:
    det = r.get("detail", r)
    msg = det.get("message", det) if isinstance(det, dict) else det
    sys.exit(f"No se pudo clonar: {msg}\n(¿Tienes plan Starter o superior? ¿La clave tiene permiso de 'Voices: escritura'?)")

c["elevenlabs_voz"] = r["voice_id"]
json.dump(c, open(CONFIG, "w"), indent=1)
os.chmod(CONFIG, 0o600)
print(f"Voz «{nombre}» creada: {r['voice_id']}")
print('Pruébala:  voz "Hola, esta es mi voz clonada. ¿Se parece?" ~/Descargas/prueba-voz.mp3')
