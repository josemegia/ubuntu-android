#!/bin/bash
# Instala o actualiza utilidades y kit de marketing (root, DENTRO de Ubuntu). Lo usan configurar.sh y kit-actualizar.
# Uso: kit.sh <usuario>     (los archivos deben estar ya en /opt/ubuntu-android)
set -euo pipefail
USUARIO="${1:-android}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
CASA="$(getent passwd "$USUARIO" | cut -d: -f6)"

for b in claude-arrancar ogg-transcribir ver-en-movil kit-actualizar; do
  install -m 755 "$AQUI/bin/$b" "/usr/local/bin/$b"
done

VENV=/opt/ubuntu-android-venv          # fuera de /opt/ubuntu-android, que se reemplaza en cada instalación
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade edge-tts
M=/opt/ubuntu-android/marketing
for par in meta:meta.py voz:voz.py voz-clonar:voz_clonar.py video-anuncio:video.py video-avatar:avatar.py escena:escena.py marketing-configurar:configurar.py; do
  printf '#!/bin/sh\nexec %s %s "$@"\n' "$VENV/bin/python" "$M/${par#*:}" > "/usr/local/bin/${par%%:*}"
  chmod 755 "/usr/local/bin/${par%%:*}"
done
install -m 755 "$M/landing-publicar" /usr/local/bin/landing-publicar

mkdir -p "$CASA/.config/marketing" "$CASA/.claude/skills" "$CASA/Descargas/Campañas"
chmod 700 "$CASA/.config/marketing"
rm -rf "$CASA/.claude/skills/campana"
cp -r "$AQUI/claude/skills/campana" "$CASA/.claude/skills/campana"
# Instrucciones para Claude: solo si no existen o siguen siendo las nuestras (no pisar ediciones del usuario)
if [ ! -f "$CASA/.claude/CLAUDE.md" ] || head -1 "$CASA/.claude/CLAUDE.md" | grep -q 'ubuntu-android: archivo gestionado'; then
  cp "$AQUI/claude/CLAUDE.md" "$CASA/.claude/CLAUDE.md"
fi
chown -R "$USUARIO:$USUARIO" "$CASA/.config/marketing" "$CASA/.claude" "$CASA/Descargas/Campañas" 2>/dev/null || true
