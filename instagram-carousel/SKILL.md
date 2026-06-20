---
name: instagram-carousel
description: Generate Instagram carousels from emails, podcasts, or tweets with professional design and automatic formatting. Supports design customization, content validation, and publication via Upload Post API.
license: MIT
---

# Instagram Carousel Generator

Genera carruseles de Instagram automáticamente desde emails, transcripciones de podcasts o tweets con diseño profesional y validación de contenido.

## Flujo de trabajo

1. **Ingesta de contenido**: El usuario proporciona un email, transcripción de podcast o tweet
2. **Generación**: Crea slides en formato JSON + PNG con `generate_carousel.py`
3. **Revisión**: Muestra las slides al usuario antes de publicar
4. **Publicación**: Publica vía Upload Post API o descarga manual

## Requisitos

```bash
pip install Pillow upload-post
```

## Reglas de diseño

- **Fuente**: Courier New Bold (variantes: Regular, Italic, Bold Italic)
- **Tamaño uniforme**: Máximo 120px en todas las slides
- **Dimensiones**: 1080x1080px (Instagram estándar)
- **Paleta oscura**: `["#0a0a12", "#0d1a40", "#1a0a0d", "#081820", "#0d0d08"]`
- **Contraste**: Texto blanco sobre fondo oscuro
- **Límite slides**: Máximo 10 slides (límite de Instagram)
- **Sin navegación**: Instagram añade sus propios puntos
- **Efectos disponibles**: `*acento*`, `_subrayado_`, `~cursiva~`
- **Estilos**: classic, contrast, minimal, warm

## Reglas de contenido (AIDA)

- **Atención**: Primera slide = hook que pare el scroll (nunca datos ni contexto)
- **Interés**: Desarrolla temas en slides individuales
- **Deseo**: Genera demanda o curiosidad
- **Acción**: CTA clara al final

## Restricciones importantes

✗ Sin hashtags en caption
✗ Sin consejos, órdenes, condescendencia
✗ Caption NUNCA vacío, siempre relacionado con el contenido
✓ SIEMPRE mostrar slides + caption ANTES de publicar
✓ Alto contraste y legibilidad

## Para podcasts

- Slide 1: Hook provocador + subtítulo discreto `"subtitle": "(ep. #X con Invitado)"`
- Extrae las ideas más potentes como slides individuales
- Última slide: CTA al episodio completo

## Uso del script

```bash
python3 generate_carousel.py slides.json --output-dir ./carruseles/YYYY-MM-DD_slug
```

## Publicación con Upload Post API

### Configuración

Credenciales en `~/.carruseles_app/config.json`:

```json
{
  "api_key": "tu_api_key_aqui",
  "user": "tu_usuario_instagram"
}
```

### Ejemplos de código

```python
from upload_post import UploadPostClient

client = UploadPostClient(api_key="...")

# Publicar inmediatamente
client.upload_photos(
  photos=[...],
  title="caption",
  user="TU_USUARIO",
  platforms=["instagram"],
  instagram_title="caption"
)

# Programar publicación
client.upload_photos(
  photos=[...],
  title="caption",
  user="TU_USUARIO",
  platforms=["instagram"],
  scheduled_date="2026-04-05T08:00:00",
  timezone="Europe/Madrid"
)

# Consultar estado
client.get_status("request_id")
client.get_history()
client.list_scheduled()
client.list_users()
```

## Estructura de JSON de slides

```json
{
  "slides": [
    {
      "text": "Texto principal",
      "subtitle": "Subtítulo opcional",
      "style": "classic",
      "bg_color": "#0a0a12",
      "text_color": "#ffffff"
    }
  ],
  "caption": "Caption para Instagram"
}
```

## Próximos pasos

1. Proporciona el contenido (email, podcast, tweet)
2. Especifica el estilo deseado (classic/contrast/minimal/warm)
3. Revisa las slides generadas
4. Aprueba y publica o descarga los PNGs
