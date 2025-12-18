from PIL import ImageFont

def draw_text(draw, text, color, x, y, mono=True):
    # Define font size and load font
    font_size = 20
    try:
        if mono:
            font = ImageFont.truetype("RobotoMono-VariableFont_wght.ttf", font_size)
        else:
            font = ImageFont.truetype("Roboto-Regular.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    # Calculate text size and bounding box
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = right - left
    text_height = 6 #bottom - top

    # Draw background box centered around the text's actual bounding box
    padding = 10
    box_coords = [
        x - padding/2,
        y - padding/4,
        x + text_width + padding/2,
        y + text_height + padding*2
    ]

    draw.rectangle(box_coords, fill='black')
    draw.text((x, y), text, fill=color, font=font)
