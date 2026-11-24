"""Lo que se hace al terminar un archivo: enseñarlo en el móvil y avisar al usuario."""
import subprocess


def entregar(archivo, aviso=None):
    # El archivo ya está guardado: que falte o se cuelgue un comando del móvil no es un error.
    for cmd in (["ver-en-movil", archivo], ["avisar", aviso] if aviso else None):
        if not cmd:
            continue
        try:
            subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            pass
