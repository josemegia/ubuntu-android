<!-- ubuntu-android: archivo gestionado por el instalador. Si lo editas, borra esta línea para que no se sobrescriba. -->
# Entorno

- Estás en **Ubuntu dentro de un móvil Android** (Termux + proot-distro, sin root ni systemd). Usuario `android`.
- `~/Descargas` es la carpeta **Download/Ubuntu** del móvil: todo lo que el usuario deba ver, guárdalo ahí y
  ejecuta `ver-en-movil <archivo>` para que aparezca en la galería o en Archivos.
- `/storage/emulated/0` es el almacenamiento del móvil. Para buscar en él usa Python (os.scandir), no `find`:
  es lento y puede colgarse.
- `am` (Termux) está en el PATH: sirve para hablar con Android.
- Herramientas instaladas: git, gh, tmux, python3, ffmpeg, curl, y las del kit de marketing:
  `meta`, `voz`, `voz-clonar`, `video-anuncio`, `landing-publicar`, `marketing-configurar`, `OGG`.

# Cómo trabajar con este usuario

- Responde en español, corto y claro. El usuario puede no ser técnico: explica qué vas a hacer, no cómo funciona por dentro.
- Para campañas, anuncios, vídeos promocionales o landing pages, usa el skill **campana**.
- **Nunca actives nada que gaste dinero sin un "adelante" explícito.** Todo se crea en pausa.
- Las claves viven en `~/.config/marketing/config.json`. No las muestres, no las copies a repos ni a webs.
  Si hace falta una clave nueva, pide al usuario que ejecute `marketing-configurar` en otra sesión de Termux.
- Programas interactivos (`gh auth login`, `marketing-configurar`): pídele que los ejecute él en otra sesión
  de Termux (deslizar desde el borde izquierdo → NEW SESSION). Tú no puedes contestar sus preguntas.
