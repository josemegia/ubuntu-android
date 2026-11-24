---
name: campana
description: Crea una campaña completa de Facebook e Instagram para el negocio del usuario a partir de preguntas sencillas — guion, textos del anuncio, vídeo vertical con voz y subtítulos (o con su avatar de HeyGen, y planos de apoyo de ArtCraft si lo tiene), landing page publicada en su web de Conexpix (o GitHub Pages) y campaña en Meta Ads EN PAUSA. Úsalo cuando el usuario hable de anuncios, campaña, Facebook, Instagram, conseguir clientes, promocionar su negocio, landing, web para su negocio, vídeo para anuncio o reel promocional, o pida resultados de una campaña.
---

# Campaña de Facebook e Instagram desde el móvil

El usuario no es técnico. Habla claro, en frases cortas, sin jerga ("conjunto de anuncios" → "a quién y dónde se muestra").
Tú haces el trabajo; él solo responde preguntas, manda fotos y dice "adelante".

## Regla de oro

**Nunca gastes dinero sin un "adelante" explícito del usuario en este mismo momento.**
Todo se crea EN PAUSA. Antes de `meta activar` enseña: qué se anuncia, a quién, dónde, cuánto al día,
cuántos días y el coste máximo total. Activar es lo último y solo con su sí.

## Paso 0 — Comprobar herramientas

```bash
meta comprobar
```
- Si falla por configuración: dile que abra **otra sesión de Termux** (deslizar desde el borde izquierdo
  → NEW SESSION), escriba `marketing-configurar` y siga las preguntas. La guía del token está en
  https://github.com/josemegia/ubuntu-android/blob/main/docs/META.md. **No le pidas que pegue claves en el chat.**
- Para la landing: si tiene Conexpix (`~/.conexpix/token`) no hace falta nada. Si no, GitHub: `gh auth status`; si falla, que ejecute `gh auth login` (en otra sesión).
- Puedes preparar guion, vídeo y landing aunque Meta aún no esté configurado.

## Paso 1 — Entrevista (máximo 2 tandas de preguntas)

Antes de preguntar, lee `~/Descargas/Mi negocio/negocio.md` si existe: ya trae el negocio, la oferta, el cliente
ideal, el contacto y fotos reales en `~/Descargas/Mi negocio/fotos/`. Confírmalo en una frase («Veo que vendes…»)
y pregunta solo lo que falte (sobre todo zona, presupuesto y qué quiere anunciar esta vez). Puedes copiar sus fotos
a la carpeta de la campaña (`ffmpeg -i foto.webp foto.jpg` si hace falta JPG).

Pregunta en un solo mensaje, numerado, lo que falte de esto:
1. ¿Cómo se llama tu negocio y qué ofreces? (producto o servicio estrella)
2. ¿Dónde están tus clientes? (ciudad o barrio y cuántos km alrededor)
3. ¿Quién es tu cliente ideal? (edad aproximada, a qué se dedica, qué problema tiene)
4. ¿Qué le ofreces para que te escriba hoy? (oferta, prueba, café, presupuesto gratis…)
5. ¿Quieres que te escriban por WhatsApp o que visiten una web? (por defecto: WhatsApp + landing con botón de WhatsApp)
6. ¿Cuánto quieres gastar al día y cuántos días? (sugiere 5-6 al día, 7 días, para probar)
7. Fotos: que ponga 3-6 fotos reales (del local, del producto, de él/ella) en la carpeta del móvil
   **Download/Ubuntu/Campañas/<nombre>/fotos** (créala tú antes con `mkdir -p` y díselo).

Crea la carpeta de trabajo `~/Descargas/Campañas/<nombre-corto>/` y guarda allí todo.

## Paso 2 — Guion y textos → `ficha.md`

Escribe y enséñale:
- **Guion del vídeo** (20-30 s, 55-80 palabras): gancho en la primera frase (una pregunta al cliente ideal
  o una escena), qué ofreces, prueba concreta, llamada a la acción ("Escríbeme por WhatsApp").
- **Texto del anuncio** (2-3 frases, una pregunta + oferta + llamada), **titular** (máx. 40 caracteres),
  **mensaje prellenado** de WhatsApp en primera persona del cliente ("Hola, vi tu anuncio y quiero…"),
  **texto final del vídeo** ("Escríbeme por WhatsApp").
- Ofrece 2 variantes de gancho. Ajusta hasta que diga que le gusta.

### Normas de Meta y de buena publicidad (cúmplelas siempre)
- Nada de promesas de ingresos, dinero fácil, "hazte rico", resultados garantizados ni estilo de vida.
- Nada de "multinivel", antes/después de salud o peso, ni afirmaciones médicas.
- No señalar atributos personales: ❌ "¿Estás gordo?", ❌ "¿Tienes deudas?" → ✅ "Si quieres sentirte con más energía…".
- No inventar opiniones, cifras de clientes ni premios. Si no hay datos reales, no se ponen.
- Empleo, vivienda, crédito o política son categorías especiales: avisa y no lo lances sin revisarlo con él.

## Paso 3 — Voz y vídeo

El vídeo normal (fotos o clips + voz + subtítulos) es SIEMPRE el camino por defecto y no necesita
ninguna clave de pago. El avatar de HeyGen y las escenas de ArtCraft son solo extras: si no están disponibles,
la campaña sigue igual.

```bash
cd ~/Descargas/Campañas/<nombre>
echo "<guion>" > guion.txt
video-anuncio --guion guion.txt --fotos fotos --final "Escríbeme por WhatsApp" --salida anuncio.mp4
```
- Usa su voz clonada si la tiene (ElevenLabs configurado); si no, una voz gratuita (`voz --lista`).
- Si quiere grabar él la locución: que la grabe con la grabadora del móvil, la deje en la carpeta y usa `--audio`.
- Si quiere su propia voz clonada: guía docs/VOZ.md y `voz-clonar`.
- `video-anuncio` deja el vídeo visible en el móvil. Pídele que lo vea y te diga qué cambiar.

### Con su avatar de HeyGen (si lo tiene)
Si `video-avatar --comprobar` funciona, ofrécele la opción: «¿Lo hago con tu avatar hablando? Gasta créditos de tu HeyGen».
Solo con su sí:
```bash
video-avatar --guion guion.txt --formato 9:16 --salida avatar.mp4
```
- Usa su voz de ElevenLabs si la tiene; si no, la de su avatar. `--audio` para su propia grabación.
- Tarda de 2 a 10 minutos: avísale y sigue con la landing mientras tanto.
- Solo con **su propio** avatar (su cara). Nunca el de otra persona ni famosos.
- En el texto del anuncio o en el vídeo, indica que está hecho con IA (p. ej. «Vídeo creado con IA»).
- Si `video-avatar --comprobar` falla (sin clave, clave mala) no ofrezcas el avatar: haz el vídeo normal
  y sigue. Como mucho, al final, una línea: «Si un día quieres tu avatar hablando, mira Mi asistente en tu panel».
- Si `video-avatar` falla al crear el vídeo (sin créditos, saldo insuficiente, HeyGen no responde):
  díselo en una frase, haz el vídeo normal con `video-anuncio` con el mismo guion y continúa con la campaña.
  No te quedes parado ni insistas con HeyGen.
- Nunca le pidas la clave en el chat: se pone con `marketing-configurar` en otra sesión.

### Planos de apoyo con ArtCraft (si lo tiene)
ArtCraft crea imágenes y clips cortos con IA: una escena, un fondo, un plano de ambiente. Sirve para vestir el
anuncio cuando faltan fotos o para abrir con algo llamativo. **No pone voz ni mueve los labios**: la voz sigue
siendo `video-anuncio` (o `video-avatar`).

Si `escena comprobar` funciona y le vendría bien, ofréceselo diciendo qué harías: «Te faltan fotos del local.
¿Genero dos imágenes de apoyo con ArtCraft? Gasta créditos de tu cuenta». Solo con su sí:
```bash
escena imagen "interior de una panadería artesanal al amanecer, luz cálida, sin texto" -o fotos/apoyo1.png
escena video "la cámara avanza despacio hacia el mostrador" --inicio https://su-web/c/campana/foto.jpg --dur 5 -o clip.mp4
```
- Sale en vertical (9:16). Las imágenes van a la carpeta `fotos` y entran en `video-anuncio` como una foto más.
- Empieza por imágenes (baratas y rápidas). Un clip de vídeo cuesta bastante más: uno o dos como mucho, y avísale.
- `--ref` y `--inicio` necesitan una dirección de internet: publica antes la foto con `landing-publicar`.
- Pide en la descripción que no haya texto ni logotipos: la IA los escribe mal.
- No inventes lo que vende: nada de productos, locales, personas o resultados que no sean reales. Es ambiente, no prueba.
  Nunca caras de personas reales ni famosos. Indica que hay imágenes creadas con IA.
- Si `escena comprobar` falla (sin clave, clave mala) no lo ofrezcas. Si `escena` falla al generar (sin créditos,
  ArtCraft no responde, lo rechaza): díselo en una frase y sigue con sus fotos. No insistas.
- Si tarda demasiado, `escena` da un código `jinf_...`: recógelo después con `escena recoger <código>`.

## Paso 4 — Landing page

```bash
cp -r /opt/ubuntu-android/marketing/plantilla-landing ~/Descargas/Campañas/<nombre>/web
```
- Rellena todos los `{{…}}` de `index.html` y `privacidad.html` con lo que te ha contado. Borra los comentarios
  y la sección de opinión si no hay una real. Copia sus fotos como foto1.jpg, foto2.jpg, foto3.jpg
  (redúcelas: `ffmpeg -i in.jpg -vf scale=1200:-2 -q:v 4 foto1.jpg`).
- Mensaje prellenado en la URL de WhatsApp codificado (python3 urllib.parse.quote).
- Elige `COLOR_MARCA` acorde al negocio. Textos con la misma voz que el anuncio.
- Publica: `landing-publicar ~/Descargas/Campañas/<nombre>/web <nombre-corto>`.
  - Con Conexpix (existe `~/.conexpix/token`): queda en `https://<su-nombre>.conexpix.com/c/<nombre-corto>/`. No hace falta GitHub.
  - Sin Conexpix: GitHub Pages, `https://<usuario>.github.io/<nombre-corto>/` (necesita `gh auth login`).
- La página de privacidad sirve también como "URL de política de privacidad" de su app de Meta.

## Paso 5 — Campaña en Meta (EN PAUSA)

1. Lugar: `meta buscar-lugar "<ciudad>"` → usa el `key` de la ciudad con su radio.
2. Escribe `ficha.json` (todos los campos en el docstring de `campana()` en /opt/ubuntu-android/marketing/meta.py):
   ```json
   {"nombre": "Café Majadahonda", "destino": "whatsapp", "pais": "ES",
    "lugar": {"key": "776688", "radio_km": 10}, "edad": [30, 60],
    "presupuesto_diario": 6, "dias": 7, "video": "anuncio.mp4",
    "texto": "...", "titulo": "...", "mensaje_prellenado": "...", "bienvenida": "..."}
   ```
   Con `"destino": "web"` añade `"web": "https://…github.io/…/"`.
3. `meta campana ficha.json` → crea todo en pausa y da el enlace al Administrador de anuncios.
4. Resume en 4 líneas (qué, a quién, dónde, coste máximo) y pregunta: **"¿Le doy al adelante?"**
5. Solo con su sí: `meta activar <campaign_id>`.

Errores habituales:
- "app en modo desarrollo" / no deja crear el anuncio → su app de Meta debe estar en **modo público** (docs/META.md).
- Token caducado (cada 60 días) → renovarlo (docs/META.md) y `marketing-configurar`.
- WhatsApp no vinculado → en la página de Facebook: Configuración → Cuentas vinculadas → WhatsApp.
- Falta método de pago en la cuenta publicitaria → que lo añada en Meta Business Suite.

Cuando la campaña quede creada en pausa (y cada vez que termines algo que tardó varios minutos), avísale:
```bash
avisar "Tu campaña está lista para revisar. No se gasta nada hasta que digas adelante."
```
Le llega una notificación al móvil. Los vídeos y las escenas ya avisan solos. Si no llega, no pasa nada: sigue.

## Paso 6 — Seguimiento

`meta resultados` (activas) o `meta resultados <id>`. Explica en cristiano: cuánta gente lo vio,
cuántos hicieron clic, cuántos escribieron y cuánto ha costado cada conversación.
A los 2-3 días, si hay clics pero no mensajes, propón cambiar el gancho o el mensaje prellenado;
si no hay clics, cambiar el vídeo. `meta pausar <id>` si lo pide.
