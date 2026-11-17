#!/bin/bash
# Se ejecuta como root DENTRO de Ubuntu (lo lanza instalar.sh desde Termux).
# Uso: configurar.sh <usuario> <nombre-remote-control>
set -euo pipefail
USUARIO="${1:-android}"
NOMBRE_RC="${2:-android}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
export DEBIAN_FRONTEND=noninteractive

paso() { printf '\n\033[1;32m  -> %s\033[0m\n' "$*"; }

paso "Paquetes de Ubuntu"
apt-get update
apt-get -y -o Dpkg::Options::=--force-confnew upgrade
apt-get install -y --no-install-recommends \
  sudo ca-certificates curl wget git tmux python3 python3-venv python3-pip \
  ffmpeg gh nano less unzip zip locales tzdata procps bash-completion fonts-dejavu-core

paso "Idioma español y zona horaria (${ZONA:-Europe/Madrid})"
sed -i 's/^# *\(es_ES.UTF-8 UTF-8\)/\1/' /etc/locale.gen
locale-gen >/dev/null
update-locale LANG=es_ES.UTF-8
if [ -f "/usr/share/zoneinfo/${ZONA:-Europe/Madrid}" ]; then
  ln -sf "/usr/share/zoneinfo/${ZONA:-Europe/Madrid}" /etc/localtime
  echo "${ZONA:-Europe/Madrid}" > /etc/timezone
fi

paso "Usuario $USUARIO (con sudo sin contraseña)"
id "$USUARIO" >/dev/null 2>&1 || useradd -m -s /bin/bash "$USUARIO"
usermod -aG sudo "$USUARIO"
echo "$USUARIO ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/$USUARIO"
chmod 440 "/etc/sudoers.d/$USUARIO"
CASA="$(getent passwd "$USUARIO" | cut -d: -f6)"
mkdir -p "$CASA/Descargas" "$CASA/.config/ubuntu-android"

paso "Utilidades: claude-arrancar, ogg-transcribir (OGG)"
install -m 755 "$AQUI/bin/claude-arrancar" /usr/local/bin/claude-arrancar
install -m 755 "$AQUI/bin/ogg-transcribir" /usr/local/bin/ogg-transcribir
install -m 755 "$AQUI/bin/ver-en-movil" /usr/local/bin/ver-en-movil
echo "NOMBRE_RC=$NOMBRE_RC" > "$CASA/.config/ubuntu-android/config"

paso "Kit de marketing: meta, voz, voz-clonar, video-anuncio, landing-publicar, marketing-configurar"
VENV=/opt/ubuntu-android-venv          # fuera de /opt/ubuntu-android, que se reemplaza en cada instalación
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade edge-tts
M=/opt/ubuntu-android/marketing
for par in meta:meta.py voz:voz.py voz-clonar:voz_clonar.py video-anuncio:video.py marketing-configurar:configurar.py; do
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

paso "Bloque en ~/.bashrc de $USUARIO"
BASHRC="$CASA/.bashrc"
[ -f "$BASHRC" ] || cp /etc/skel/.bashrc "$BASHRC"
sed -i '/# >>> ubuntu-android >>>/,/# <<< ubuntu-android <<</d' "$BASHRC"
cat >> "$BASHRC" <<'EOF'
# >>> ubuntu-android >>>
export LANG=es_ES.UTF-8
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) PATH="$HOME/.local/bin:$PATH" ;; esac
# OGG: copia los últimos audios de WhatsApp a Descargas/Transcribir
alias OGG=ogg-transcribir
# Claude Code con Remote Control: arrancar en tmux si no está activo
command -v claude-arrancar >/dev/null && claude-arrancar
# <<< ubuntu-android <<<
EOF
chown -R "$USUARIO:$USUARIO" "$CASA"

paso "Claude Code (instalador oficial)"
if [ -x "$CASA/.local/bin/claude" ]; then
  echo "Ya instalado; se actualiza solo."
else
  su - "$USUARIO" -c 'curl -fsSL https://claude.ai/install.sh | bash'
fi

echo "Ubuntu configurado."
