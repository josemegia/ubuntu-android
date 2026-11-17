# Tu propia voz en los vídeos (ElevenLabs)

Sin hacer nada, los vídeos usan una voz gratuita que suena natural pero es de locutor.
Con ElevenLabs, el vídeo habla **con tu voz**: la grabas una vez y luego escribes lo que quieras que diga.

**Clona solo tu propia voz** (o la de alguien que te dé permiso por escrito).

## 1. Cuenta y clave

1. Crea una cuenta en <https://elevenlabs.io>.
2. Contrata el plan **Starter** (unos 5 USD al mes). La clonación no está en el plan gratuito.
   Con Starter tienes minutos de sobra para varios anuncios al mes.
3. Clave de API: icono de tu perfil → **API Keys** → **Create API Key**. Dale permiso a
   *Text to Speech* y a *Voices* (lectura y escritura). Copia la clave.
4. En Termux, otra sesión (deslizar desde la izquierda → **NEW SESSION**):
   ```bash
   marketing-configurar
   ```
   Enter hasta llegar a *Clave de ElevenLabs*, pégala, y Enter en el ID de voz (aún no lo tienes).

## 2. Grabar tu voz con el móvil

Necesitas **entre 1 y 3 minutos** de tu voz. Más no mejora el resultado; peor calidad sí lo empeora.

**Dónde**
- Una habitación pequeña con cortinas, sofá o ropa: absorben el eco.
- **No** en el baño, la cocina, un pasillo vacío ni la calle.
- Sin tele, música, ventilador ni nadie hablando.

**Cómo**
- App **Grabadora** del móvil (no notas de voz de WhatsApp: comprimen demasiado).
- Móvil a **un palmo** de la boca (15-20 cm), un poco de lado para que no "sople" en las p y las b.
- De pie o sentado recto, a tu volumen normal. No susurres ni grites.
- **Habla como hablarías en tu anuncio**: la copia imita también el tono. Si grabas leyendo aburrido, tu voz
  clonada sonará aburrida.
- Si te equivocas, haz una pausa y repite la frase: no hace falta empezar de cero.

**Qué leer** (unos 90 segundos; léelo como si se lo contaras a un cliente):

> Hola, ¿qué tal? Te cuento un poco a qué me dedico.
> Llevo años trabajando con gente como tú, y lo que más me gusta es ver la cara que ponen cuando algo por fin funciona.
> ¿Sabes lo que me dicen muchos al principio? "No tengo tiempo." Y lo entiendo, de verdad. Yo también lo pensaba.
> Por eso lo hago fácil: quedamos, te explico en diez minutos cómo funciona, y decides tú. Sin compromiso.
> El martes pasado, por ejemplo, vino una clienta a las nueve y media, con prisa, y a las diez ya tenía todo resuelto.
> Me escribió por la tarde: "¡Gracias! No pensé que fuera tan sencillo."
> Si te apetece, escríbeme por WhatsApp. Te contesto yo, no un robot. ¿Cuándo te viene mejor: mañana o el jueves?
> Estoy en el centro, a dos minutos de la plaza. Hay sitio para aparcar y el café corre de mi cuenta.
> Uno, dos, tres, cuatro, cinco. Lunes, miércoles, viernes. Doce euros, cincuenta por ciento, dos mil veintiséis.
> Venga, te espero. ¡Un abrazo y hasta pronto!

Puedes hacer 2 o 3 grabaciones cortas en vez de una larga.

## 3. Pasar la grabación a Ubuntu y clonar

1. Con la app **Archivos** del móvil, mueve la grabación a la carpeta **Download/Ubuntu/Voz**
   (créala si no existe).
2. En Ubuntu:
   ```bash
   voz-clonar --nombre "Mi voz" ~/Descargas/Voz/*
   ```
3. Pruébala:
   ```bash
   voz "Hola, esta es mi voz clonada. ¿Se parece a mí?" ~/Descargas/prueba-voz.mp3
   ver-en-movil ~/Descargas/prueba-voz.mp3
   ```

Desde ese momento los vídeos de `video-anuncio` usan tu voz automáticamente.
Si no te convence, graba otra vez en un sitio más silencioso y repite el paso 3.

## Si no quieres clonar

- Puedes grabar tú cada locución con la grabadora y pasársela a Claude: el vídeo usará esa grabación tal cual.
- O elegir otra voz gratuita: `voz --lista` y cambiarla con `marketing-configurar`.
