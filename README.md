# Ubuntu en Android (sin root)

Ubuntu completo en el móvil Android, dentro de Termux, con **Claude Code** listo para usar
desde el propio móvil o en remoto desde [claude.ai/code](https://claude.ai/code) y la app de Claude.

## Instalación

1. Instala **Termux** desde [F-Droid](https://f-droid.org/packages/com.termux/) o
   [GitHub](https://github.com/termux/termux-app/releases).
   *No uses la versión de Google Play, está anticuada.*
2. Abre Termux y pega:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/josemegia/ubuntu-android/main/instalar.sh | bash
   ```

3. Cuando Android lo pida, pulsa **Permitir** (acceso a archivos).
4. Al terminar, cierra Termux del todo y vuelve a abrirlo: entrarás en Ubuntu.
5. Escribe `claude` e inicia sesión (necesitas una cuenta de Claude Pro o superior).

A partir de ahí, cada vez que abras Termux, Claude arranca solo en segundo plano y
aparece en claude.ai/code con el nombre que elegiste durante la instalación.

**Recomendado:** Ajustes de Android → Apps → Termux → Batería → *Sin restricciones*,
para que Android no cierre Termux.

## Qué incluye

| | |
|---|---|
| Ubuntu (último LTS) | usuario `android` con `sudo` sin contraseña, en español |
| `~/Descargas` | es la carpeta *Download/Ubuntu* del móvil: lo que guardes ahí lo ves en Android y al revés |
| Claude Code | arranca solo en tmux con Remote Control (`tmux attach -t <nombre>` para verlo; salir con `Ctrl+b` y `d`) |
| `OGG` | copia los últimos audios de WhatsApp y WhatsApp Business a *Download/Ubuntu/Transcribir*. `OGG 10` copia 10 |
| Herramientas | git, gh (GitHub), tmux, python3, ffmpeg, curl, nano |

## Uso diario

- `ubuntu` (en Termux): entrar en Ubuntu. `exit` para volver a Termux.
- Abrir Termux sin entrar en Ubuntu: `SIN_UBUNTU=1 bash`.
- Cambiar el nombre de Remote Control: edita `~/.config/ubuntu-android/config`.
- Volver a pasar el instalador es seguro: lo que ya está hecho se salta.

## Privacidad

El instalador no lleva claves ni datos de nadie. Cada persona inicia su propia sesión en
Claude (`claude`) y, si quiere, en GitHub (`gh auth login`).
