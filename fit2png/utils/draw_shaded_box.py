from PIL import ImageDraw

def draw_shaded_box(
    draw: ImageDraw.ImageDraw,
    x1: float, y1: float, x2: float, y2: float,
    fill=(255, 255, 255, 200),          # semi-transparent white (RGBA)
    outline=(255, 255, 255, 255),       # optional outline color
    outline_width: int = 0,             # 0 disables outline
):
    """Draw a filled (shaded) rectangle for masking/redaction."""
    # Ensure proper ordering
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))

    # PIL likes integer pixel coords for crisp edges
    x1i, y1i, x2i, y2i = map(int, (round(x1), round(y1), round(x2), round(y2)))

    if x2i <= x1i or y2i <= y1i:
        return

    draw.rectangle((x1i, y1i, x2i, y2i), fill=fill)

    if outline_width and outline_width > 0:
        draw.rectangle((x1i, y1i, x2i, y2i), outline=outline, width=int(outline_width))
