# Ubuntu en Android (sin root)

Ubuntu completo en el móvil Android, dentro de Termux, con **Claude Code** listo para usar
desde el propio móvil o en remoto desde [claude.ai/code](https://claude.ai/code) y la app de Claude.

**Tu móvil crea tu web, tus vídeos y tus anuncios.** Dile a Claude *"quiero una campaña para mi negocio"*,
responde a sus preguntas y te prepara guion, vídeo con voz, landing page publicada y campaña de
Facebook e Instagram, lista para que digas "adelante".

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
| `OGG` | copia los últimos audios de WhatsApp a *Download/Ubuntu/Transcribir* y los pasa a texto. `OGG hoy`, `OGG 1h`, `OGG resumen` (Claude te dice qué responder), `OGG enviados` |
| Herramientas | git, gh (GitHub), tmux, python3, ffmpeg, curl, nano |
| Kit de marketing | ver abajo |

## Kit de marketing: campañas de Facebook e Instagram

Escribe `claude` y pide, con tus palabras: *"quiero una campaña para mi cafetería en Majadahonda"*.
Claude te hace unas preguntas (qué ofreces, dónde, a quién, cuánto quieres gastar) y prepara:

1. **Guion y textos** del anuncio, siguiendo las normas de Meta.
2. **Vídeo vertical** para Reels y Stories con tus fotos, voz y subtítulos.
3. **Landing page** con botón de WhatsApp, con dirección fija y visible con el móvil apagado: en tu página de Conexpix (`tu-nombre.conexpix.com/c/...`) o, si no usas Conexpix, gratis en GitHub Pages.
4. **Campaña en Meta Ads**, creada **en pausa**. No se gasta nada hasta que tú digas "adelante".
5. **Resultados**: *"¿cómo va mi campaña?"*.

| Comando | Qué hace |
|---|---|
| `marketing-configurar` | conectar tu Facebook/Instagram y, si quieres, ElevenLabs y HeyGen (una vez) |
| `video-anuncio` | vídeo 1080×1920 con fotos, voz y subtítulos |
| `video-avatar` | vídeo con tu avatar de HeyGen hablando (opcional, de pago en HeyGen) |
| `voz` / `voz-clonar` | texto a voz (gratis o con tu voz clonada) / clonar tu voz |
| `landing-publicar` | publicar una carpeta web (en Conexpix si lo tienes; si no, en GitHub Pages) |
| `meta` | crear, activar, pausar y ver resultados de campañas |
| `ver-en-movil` | hacer visible un archivo en la galería del móvil |

**Configuración, una sola vez:**
- Facebook e Instagram → [docs/META.md](docs/META.md) (crear tu app de Meta y sacar el token, ~15 min).
- GitHub para publicar webs → `gh auth login` (gratis). No hace falta si usas Conexpix.
- Tu propia voz (opcional, ~5 USD/mes) → [docs/VOZ.md](docs/VOZ.md): cómo grabarla bien con el móvil y clonarla.
- Tu avatar (opcional, de pago en HeyGen) → crea tu avatar en app.heygen.com, saca la clave en platform.heygen.com/api-keys y ejecuta `marketing-configurar`.

Sin ElevenLabs los vídeos usan una voz gratuita de Microsoft (natural, de locutor).

## Uso diario

- `ubuntu` (en Termux): entrar en Ubuntu. `exit` para volver a Termux.
- Abrir Termux sin entrar en Ubuntu: `SIN_UBUNTU=1 bash`.
- Cambiar el nombre de Remote Control: edita `~/.config/ubuntu-android/config`.
- Volver a pasar el instalador es seguro: lo que ya está hecho se salta.

## Privacidad

El instalador no lleva claves ni datos de nadie. Cada persona inicia su propia sesión en
Claude (`claude`) y, si quiere, en GitHub (`gh auth login`). Las claves de Meta y ElevenLabs
se guardan solo en tu móvil (`~/.config/marketing/config.json`).
