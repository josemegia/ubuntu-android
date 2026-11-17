# Ubuntu en Android (sin root)

Ubuntu completo en el móvil Android, dentro de Termux, con **Claude Code** listo para usar
desde el propio móvil o en remoto desde [claude.ai/code](https://claude.ai/code) y la app de Claude.

> **Solo Android.** En iPhone no es posible: iOS no permite instalar Linux en el teléfono.
> Desde un iPhone sí puedes usar Claude Code en remoto con la app de Claude o en
> [claude.ai/code](https://claude.ai/code).

## Paso 0: instalar Termux

Termux es la app que hace de terminal y donde vivirá Ubuntu.
**No la instales desde Google Play**: esa versión está abandonada y falla.

1. En el móvil, abre esta página con Chrome:
   <https://github.com/termux/termux-app/releases/latest>
2. Baja hasta *Assets* y pulsa el archivo que termina en **`universal.apk`**.
   Vale para cualquier móvil Android.
3. Cuando termine la descarga, ábrelo. Android avisará de que Chrome no puede instalar apps:
   pulsa **Ajustes**, activa **Permitir de esta fuente**, vuelve atrás y pulsa **Instalar**.
4. Si Play Protect avisa de una app desconocida, pulsa **Más detalles → Instalar de todas formas**.
5. Abre Termux y espera unos segundos a que termine de prepararse.

> Si ya tenías Termux de Google Play, desinstálalo antes.
> *(También existe en F-Droid; si lo instalas de ahí, sus complementos deben venir de F-Droid.
> No hace falta: el método de arriba es el recomendado.)*

## Instalación

1. Ya con Termux instalado (paso 0).
2. Abre Termux y pega:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/josemegia/ubuntu-android/main/instalar.sh | bash
   ```

3. Cuando Android lo pida, pulsa **Permitir** (acceso a archivos).
4. Al terminar, cierra Termux del todo y vuelve a abrirlo: entrarás en Ubuntu.
5. Escribe `claude` e inicia sesión (necesitas una cuenta de Claude Pro o superior).

A partir de ahí, cada vez que abras Termux, Claude arranca solo en segundo plano y
aparece en claude.ai/code con el nombre `android`.

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
