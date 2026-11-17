# Conectar Facebook e Instagram (token de Meta)

Esto se hace **una vez** (y el token se renueva cada 60 días). Mejor desde un ordenador o con
Chrome en modo "sitio de escritorio". Tiempo: unos 15 minutos.

## Lo que necesitas antes

- Una **página de Facebook** de tu negocio.
- Una **cuenta publicitaria** con método de pago (en [Meta Business Suite](https://business.facebook.com) →
  Configuración → Cuentas publicitarias). Si ya has promocionado una publicación, ya la tienes.
- Opcional: tu **Instagram** profesional vinculado a la página, y tu **WhatsApp Business** vinculado a la página
  (página de Facebook → Configuración → Cuentas vinculadas → WhatsApp).

## 1. Crear tu app de Meta (solo la primera vez)

1. Entra en <https://developers.facebook.com/apps> con tu cuenta de Facebook y acepta ser desarrollador.
2. **Crear app** → nombre, por ejemplo "Anuncios de mi negocio".
3. Caso de uso: **Crear y gestionar anuncios con la API de Marketing**. Vincúlala a tu portfolio empresarial si te lo pide.
4. En *Configuración de la app → Básica*:
   - **URL de la política de privacidad**: la página `privacidad.html` de tu landing
     (Claude te la publica en el paso de la landing; ej. `https://tuusuario.github.io/minegocio/privacidad.html`).
   - Categoría: *Empresa y páginas*. Guardar.
5. Arriba, cambia la app de **Desarrollo** a **Publicada / En vivo**.
   *Sin esto Meta no deja crear anuncios por API.*

## 2. Sacar el token

1. Abre el [Explorador de la API Graph](https://developers.facebook.com/tools/explorer/).
2. A la derecha: **App de Meta** = tu app. **Usuario o página** = *Token de usuario*.
3. En **Permisos** añade:
   `ads_management`, `ads_read`, `business_management`, `pages_show_list`,
   `pages_read_engagement`, `pages_manage_ads`.
4. **Generate Access Token** → acepta todo en la ventana de Facebook (marca tu página y tu cuenta publicitaria).
5. Ese token dura solo 1-2 horas. Para alargarlo: pulsa el icono **ⓘ** junto al token →
   **Abrir en el Depurador de tokens de acceso** → abajo, **Ampliar identificador de acceso** (*Extend Access Token*).
   Copia el token nuevo: **dura 60 días**.

## 3. Ponerlo en el móvil

En Termux abre otra sesión (desliza desde el borde izquierdo → **NEW SESSION**) y escribe:

```bash
marketing-configurar
```

Pega el token, elige tu cuenta publicitaria y tu página, y pon tu WhatsApp.
Al final verás `Token válido para: …`. Ya puedes decirle a Claude: *"quiero una campaña para mi negocio"*.

## Renovar cada 60 días

Repite el paso 2 y vuelve a ejecutar `marketing-configurar` (Enter en todo lo demás para conservarlo).
Si un día Claude dice *"El token ha caducado"*, es esto.

## Problemas típicos

| Mensaje | Solución |
|---|---|
| La app está en modo desarrollo | Paso 1.5: publicar la app |
| No ve ninguna cuenta publicitaria | Faltó `ads_management` o no marcaste la cuenta al aceptar |
| No ve ninguna página | Faltó `pages_show_list` o no marcaste la página |
| WhatsApp no vinculado | Vincula WhatsApp Business en la configuración de la página |
| Falta información de pago | Añade una tarjeta en Business Suite → Facturación |

*Los menús de Meta cambian de nombre a menudo; si algo no coincide, busca la opción más parecida.*

> El token es como una contraseña de tus anuncios: no lo compartas ni lo pegues en chats.
> Se guarda solo en tu móvil (`~/.config/marketing/config.json`).
