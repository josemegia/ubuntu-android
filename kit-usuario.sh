#!/bin/bash
# Kit de vídeos y anuncios para un Ubuntu que YA tienes (instalado a tu manera), sin sudo y sin tocar lo tuyo.
# Se ejecuta DENTRO de Ubuntu, con tu usuario:
#   curl -fsSL https://raw.githubusercontent.com/josemegia/ubuntu-android/main/kit-usuario.sh | bash
# Instala en ~/.local: los comandos meta, voz, voz-clonar, video-anuncio, video-avatar,
# landing-publicar y marketing-configurar, y la habilidad "campana" de Claude. Se puede repetir.
# Después se actualiza solo: kit-actualizar, como mucho una vez al día al abrir Termux.
set -euo pipefail

REPO="josemegia/ubuntu-android"
RAMA="main"
KIT="$HOME/.local/share/ubuntu-android"
VENV="$HOME/.local/share/ubuntu-android-venv"
BIN="$HOME/.local/bin"

paso() { printf '\n\033[1;32m==> %s\033[0m\n' "$*"; }
fallo() { printf '\033[1;31mError: %s\033[0m\n' "$*" >&2; exit 1; }

[ "$(id -u)" != 0 ] || fallo "ejecútalo con tu usuario, no como root."
command -v python3 >/dev/null || fallo "falta python3 (pide a quien instaló tu Ubuntu: apt install python3 python3-venv)."
command -v ffmpeg >/dev/null || echo "Aviso: no encuentro ffmpeg; video-anuncio lo necesita."

paso "Descargando el kit"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
curl -fsSL "https://github.com/$REPO/archive/refs/heads/$RAMA.tar.gz" | tar -xz -C "$TMP"
SRC="$TMP/ubuntu-android-$RAMA/ubuntu"
mkdir -p "$KIT" "$BIN"
rm -rf "$KIT/marketing"; cp -r "$SRC/marketing" "$KIT/marketing"
install -m 755 "$SRC/bin/ver-en-movil" "$KIT/ver-en-movil"
command -v ver-en-movil >/dev/null || ln -sf "$KIT/ver-en-movil" "$BIN/ver-en-movil"
install -m 755 "$SRC/bin/kit-actualizar" "$BIN/kit-actualizar"

paso "Voz gratuita (edge-tts)"
if [ ! -f "$VENV/pyvenv.cfg" ] || ! "$VENV/bin/python" -m pip --version >/dev/null 2>&1; then
  rm -rf "$VENV"
  if ! python3 -m venv "$VENV" >/dev/null 2>&1; then
    # Sin python3-venv (y sin sudo para instalarlo): entorno sin pip y pip descargado aparte.
    rm -rf "$VENV"
    python3 -m venv --without-pip "$VENV" || fallo "python3 no puede crear entornos."
    curl -fsSL https://bootstrap.pypa.io/get-pip.py -o "$TMP/get-pip.py"
    "$VENV/bin/python" "$TMP/get-pip.py" -q || fallo "no se pudo instalar pip."
  fi
fi
"$VENV/bin/python" -m pip install -q --upgrade edge-tts

paso "Comandos"
for par in meta:meta.py voz:voz.py voz-clonar:voz_clonar.py video-anuncio:video.py video-avatar:avatar.py marketing-configurar:configurar.py; do
  printf '#!/bin/sh\nUA_PYTHON=%s exec %s %s "$@"\n' "$VENV/bin/python" "$VENV/bin/python" "$KIT/marketing/${par#*:}" > "$BIN/${par%%:*}"
  chmod 755 "$BIN/${par%%:*}"
done
install -m 755 "$KIT/marketing/landing-publicar" "$BIN/landing-publicar"
mkdir -p "$HOME/.config/marketing" "$HOME/Descargas/Campañas" 2>/dev/null || mkdir -p "$HOME/.config/marketing"
chmod 700 "$HOME/.config/marketing"

paso "Habilidad 'campana' para tu Claude"
mkdir -p "$HOME/.claude/skills"
rm -rf "$HOME/.claude/skills/campana"
cp -r "$SRC/claude/skills/campana" "$HOME/.claude/skills/campana"
sed -i "s#/opt/ubuntu-android/#$KIT/#g" "$HOME/.claude/skills/campana/SKILL.md"
# Instrucciones del kit en un archivo aparte; tu CLAUDE.md solo recibe una línea que lo importa.
sed "s#/opt/ubuntu-android/#$KIT/#g" "$SRC/claude/CLAUDE.md" > "$HOME/.claude/ubuntu-android-kit.md"
touch "$HOME/.claude/CLAUDE.md"
grep -qF '@ubuntu-android-kit.md' "$HOME/.claude/CLAUDE.md" || printf '\n@ubuntu-android-kit.md\n' >> "$HOME/.claude/CLAUDE.md"

paso "Actualización automática (una vez al día, al abrir Termux)"
BASHRC="$HOME/.bashrc"; touch "$BASHRC"
sed -i '/# >>> ubuntu-android-kit >>>/,/# <<< ubuntu-android-kit <<</d' "$BASHRC"
cat >> "$BASHRC" <<'FIN'
# >>> ubuntu-android-kit >>>
[ -x "$HOME/.local/bin/kit-actualizar" ] && ("$HOME/.local/bin/kit-actualizar" --auto &) >/dev/null 2>&1
# <<< ubuntu-android-kit <<<
FIN

case ":$PATH:" in *":$BIN:"*) ;; *) echo "Aviso: añade ~/.local/bin a tu PATH (o cierra y abre Termux).";; esac
paso "Listo"
echo "Ahora, en una sesión nueva de Termux:  marketing-configurar"
