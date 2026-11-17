#!/data/data/com.termux/files/usr/bin/bash
# Ubuntu para Android (Termux + proot-distro), con Claude Code y utilidades.
# Uso, en Termux:
#   curl -fsSL https://raw.githubusercontent.com/josemegia/ubuntu-android/main/instalar.sh | bash
# Se puede repetir: lo que ya está hecho se salta.
set -euo pipefail

REPO="josemegia/ubuntu-android"
RAMA="main"
DISTRO="ubuntu"
USUARIO="android"
CARPETA_MOVIL="/storage/emulated/0/Download/Ubuntu"   # se ve como ~/Descargas dentro de Ubuntu

paso() { printf '\n\033[1;32m==> %s\033[0m\n' "$*"; }
aviso() { printf '\033[1;33m%s\033[0m\n' "$*"; }
fallo() { printf '\033[1;31mError: %s\033[0m\n' "$*" >&2; exit 1; }

# Preguntas: leer del teclado aunque el script llegue por "curl | bash".
preguntar() {  # preguntar "texto" "valor por defecto"
  local r=""
  if [ -r /dev/tty ]; then read -r -p "$1 [$2]: " r </dev/tty || true; fi
  printf '%s' "${r:-$2}"
}

[ -d /data/data/com.termux ] && [ -n "${PREFIX:-}" ] || fallo "esto se ejecuta en Termux, no dentro de Ubuntu."

# 1. Permiso de almacenamiento (Android muestra un aviso: pulsa "Permitir")
paso "Acceso al almacenamiento del móvil"
if ! ls /storage/emulated/0 >/dev/null 2>&1; then
  aviso "Android va a pedir permiso de archivos: pulsa PERMITIR."
  termux-setup-storage || true
  for _ in $(seq 1 60); do ls /storage/emulated/0 >/dev/null 2>&1 && break; sleep 1; done
fi
if ls /storage/emulated/0 >/dev/null 2>&1; then
  mkdir -p "$CARPETA_MOVIL"
else
  aviso "Sin permiso de almacenamiento: ~/Descargas no se enlazará con el móvil (puedes repetir luego)."
fi

# 2. Termux al día + proot-distro
paso "Actualizando Termux"
pkg update -y
pkg upgrade -y -o Dpkg::Options::=--force-confnew
pkg install -y proot-distro curl tar

# 3. Ubuntu
RAIZ="$PREFIX/var/lib/proot-distro/installed-rootfs/$DISTRO"
if [ -d "$RAIZ/usr" ]; then
  paso "Ubuntu ya estaba instalado: se reutiliza"
else
  paso "Instalando Ubuntu (descarga de unos 30-60 MB)"
  proot-distro install "$DISTRO"
fi

# 4. Archivos del proyecto dentro de Ubuntu (/opt/ubuntu-android)
paso "Copiando los archivos de configuración"
DESTINO="$RAIZ/opt/ubuntu-android"
rm -rf "$DESTINO"; mkdir -p "$DESTINO"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -n "$AQUI" ] && [ -f "$AQUI/ubuntu/configurar.sh" ]; then
  cp -r "$AQUI/ubuntu/." "$DESTINO/"            # ejecutado desde una copia local del repo
else
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/$RAMA.tar.gz" \
    | tar -xz -C "$DESTINO" --strip-components=2 "ubuntu-android-$RAMA/ubuntu"
fi

# 5. Configurar Ubuntu (paquetes, usuario, Claude Code, utilidades)
NOMBRE_RC="$(preguntar "Nombre con el que verás este móvil en Claude (Remote Control)" "Android")"
NOMBRE_RC="$(printf '%s' "$NOMBRE_RC" | tr -cd 'A-Za-z0-9_-')"; NOMBRE_RC="${NOMBRE_RC:-Android}"
ZONA="$(getprop persist.sys.timezone 2>/dev/null || true)"
paso "Configurando Ubuntu (puede tardar varios minutos)"
proot-distro login "$DISTRO" -- env ZONA="${ZONA:-Europe/Madrid}" \
  bash /opt/ubuntu-android/configurar.sh "$USUARIO" "$NOMBRE_RC"

# 6. Comando "ubuntu" y entrada automática al abrir Termux
paso "Creando el comando 'ubuntu' y el arranque automático"
cat > "$PREFIX/bin/ubuntu" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
# Entra en Ubuntu como $USUARIO, con la carpeta Download/Ubuntu del móvil en ~/Descargas.
ENLACE=()
[ -d "$CARPETA_MOVIL" ] && ENLACE=(--bind "$CARPETA_MOVIL:/home/$USUARIO/Descargas")
exec proot-distro login $DISTRO --user $USUARIO "\${ENLACE[@]}" "\$@"
EOF
chmod +x "$PREFIX/bin/ubuntu"

BASHRC="$HOME/.bashrc"; touch "$BASHRC"
if grep -q '>>> ubuntu-android >>>' "$BASHRC"; then
  :
elif grep -q 'proot-distro login' "$BASHRC"; then
  aviso "Tu ~/.bashrc de Termux ya entra en un proot-distro: no lo toco. Usa el comando 'ubuntu'."
else
  cat >> "$BASHRC" <<'EOF'

# >>> ubuntu-android >>>
# Al abrir Termux, entrar en Ubuntu. Al salir (exit) vuelves a Termux.
# Para abrir Termux sin entrar: SIN_UBUNTU=1 bash
[ -z "${SIN_UBUNTU:-}" ] && [ -z "${PROOT_DISTRO_ACTIVA:-}" ] && PROOT_DISTRO_ACTIVA=1 ubuntu
# <<< ubuntu-android <<<
EOF
fi

paso "¡Listo!"
cat <<EOF
Cierra Termux del todo y vuelve a abrirlo: entrarás directamente en Ubuntu.
(O escribe ahora:  ubuntu)

La primera vez, dentro de Ubuntu:
  1. Escribe  claude   e inicia sesión con tu cuenta (Pro o superior).
     Después Claude arranca solo en segundo plano al abrir Termux,
     con el nombre "$NOMBRE_RC" en claude.ai/code y en la app de Claude.
  2. Opcional:  gh auth login   para usar GitHub.

Recomendado: Ajustes de Android > Apps > Termux > Batería > Sin restricciones.
EOF
