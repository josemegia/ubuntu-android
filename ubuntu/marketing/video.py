#!/usr/bin/env python3
"""Vídeo vertical para anuncios (1080x1920, Reels/Stories) con fotos, voz y subtítulos.

  video-anuncio --guion guion.txt --fotos ~/Descargas/Campañas/cafe/fotos --salida anuncio.mp4
  video-anuncio --guion guion.txt --fotos a.jpg b.jpg c.jpg --musica fondo.mp3 --final "Escríbeme por WhatsApp"
  video-anuncio --guion guion.txt --audio mi-grabacion.m4a ...   (usar tu propia grabación como voz)

Sin --audio, la voz se genera con  voz  (tu voz de ElevenLabs o una gratuita).
Las fotos se reparten a partes iguales durante la locución, con un zoom suave.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import voz  # noqa: E402

import movil

W, H, FPS = 1080, 1920, 30
IMG = (".jpg", ".jpeg", ".png", ".webp", ".heic")


def duracion(ruta):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def ass_tiempo(s):
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def subtitulos(texto, dur, ruta, final=None):
    """Trozos de 3-6 palabras, con tiempo proporcional a su longitud."""
    palabras = texto.split()
    trozos, actual = [], []
    for p in palabras:
        actual.append(p)
        if len(actual) >= 6 or (len(actual) >= 3 and re.search(r"[.,;:!?…]$", p)):
            trozos.append(" ".join(actual)); actual = []
    if actual:
        trozos.append(" ".join(actual))
    total = sum(len(t) for t in trozos) or 1
    lineas, t = [], 0.15
    for tr in trozos:
        d = (dur - 0.3) * len(tr) / total
        lineas.append(f"Dialogue: 0,{ass_tiempo(t)},{ass_tiempo(t + d)},Sub,,0,0,0,,{tr.upper()}")
        t += d
    if final:
        lineas.append(f"Dialogue: 0,{ass_tiempo(dur)},{ass_tiempo(dur + 2.5)},Final,,0,0,0,,{final}")
    with open(ruta, "w") as f:
        f.write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,DejaVu Sans,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,70,70,520,1
Style: Final,DejaVu Sans,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,3,20,0,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(lineas) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--guion", required=True, help="archivo .txt con la locución (o el texto entre comillas)")
    ap.add_argument("--fotos", nargs="+", required=True, help="carpeta o lista de imágenes")
    ap.add_argument("--salida", default="anuncio.mp4")
    ap.add_argument("--audio", help="usar esta grabación en vez de generar la voz")
    ap.add_argument("--musica", help="música de fondo (suena bajita)")
    ap.add_argument("--final", help="texto del cierre, p. ej. 'Escríbeme por WhatsApp'")
    ap.add_argument("--sin-subtitulos", action="store_true")
    a = ap.parse_args()

    texto = open(a.guion).read().strip() if os.path.isfile(a.guion) else a.guion
    fotos = []
    for x in a.fotos:
        if os.path.isdir(x):
            fotos += sorted(os.path.join(x, n) for n in os.listdir(x) if n.lower().endswith(IMG))
        elif x.lower().endswith(IMG):
            fotos.append(x)
    if not fotos:
        sys.exit("No encuentro fotos. Ponlas en una carpeta de Download/Ubuntu y pásala con --fotos.")

    tmp = tempfile.mkdtemp(prefix="video-")
    if a.audio:
        locucion = a.audio
    else:
        locucion = os.path.join(tmp, "voz.mp3")
        print("Voz:", voz.generar(texto, locucion))
    dur = duracion(locucion)
    extra = 2.5 if a.final else 0.6
    total = dur + extra
    cada = total / len(fotos)
    print(f"Locución de {dur:.1f} s · {len(fotos)} foto(s) · {cada:.1f} s cada una")

    ass = os.path.join(tmp, "subs.ass")
    subtitulos(texto, dur, ass, a.final)

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-stats"]
    for f in fotos:
        cmd += ["-loop", "1", "-t", f"{cada:.3f}", "-i", f]
    cmd += ["-i", locucion]
    if a.musica:
        cmd += ["-stream_loop", "-1", "-i", a.musica]
    fr = int(cada * FPS) + 1
    filtros = []
    for i in range(len(fotos)):
        zoom = "zoom+0.0007" if i % 2 == 0 else "if(eq(on,0),1.12,zoom-0.0007)"
        filtros.append(f"[{i}:v]scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
                       f"zoompan=z='min(max({zoom},1),1.12)':d={fr}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
                       f"trim=duration={cada:.3f},setsar=1[v{i}]")
    filtros.append("".join(f"[v{i}]" for i in range(len(fotos))) + f"concat=n={len(fotos)}:v=1:a=0[base]")
    vfin = "[base]"
    if not a.sin_subtitulos or a.final:
        filtros.append(f"[base]subtitles={ass}[vid]")
        vfin = "[vid]"
    na = len(fotos)
    if a.musica:
        filtros.append(f"[{na}:a]apad=pad_dur={extra}[voz];[{na + 1}:a]volume=0.12[mus];[voz][mus]amix=inputs=2:duration=first:dropout_transition=0[aud]")
    else:
        filtros.append(f"[{na}:a]apad=pad_dur={extra}[aud]")
    if a.sin_subtitulos and a.final:  # solo el cierre
        subtitulos("", dur, ass, a.final)
    cmd += ["-filter_complex", ";".join(filtros), "-map", vfin, "-map", "[aud]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", a.salida]
    print("Montando el vídeo (en el móvil tarda 1-3 minutos)...")
    subprocess.run(cmd, check=True)
    print("Vídeo listo:", a.salida)
    movil.entregar(a.salida, "Tu vídeo está listo")


if __name__ == "__main__":
    main()
