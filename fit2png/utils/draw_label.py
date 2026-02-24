from PIL import ImageDraw, ImageFont

def draw_label(
    draw: ImageDraw.ImageDraw,
    x1: float,
    y1: float,
    text: str,
    *,
    canvas_size: tuple[int, int],   # (W, H) of the image you're drawing onto
    fg=(255, 255, 255, 255),
    bg=(0, 0, 0, 180),
    pad: int = 3,
):
    W, H = canvas_size
    font_size = 24
    font = ImageFont.truetype("RobotoMono-VariableFont_wght.ttf", font_size)

    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    tw, th = right - left, bottom - top

    tx = int(round(x1))
    ty = int(round(y1 - th - 2 * pad - 2))
    if ty < 0:
        ty = int(round(y1 + 2))

    # clamp so the label stays inside the blank image
    tx = max(0, min(tx, W - (tw + 2 * pad)))
    ty = max(0, min(ty, H - (th + 2 * pad)))

    draw.rectangle((tx, ty, tx + tw + 2 * pad, ty + th + 2 * pad), fill=bg)
    draw.text((tx + pad, ty + pad), text, fill=fg, font=font)
