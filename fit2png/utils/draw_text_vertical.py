from PIL import ImageFont

def draw_text_vertical(draw, text, color, x, y):
    # Define font size and load font
    font_size = 20
    try:
        font = ImageFont.truetype("Roboto-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    # Calculate individual character dimensions to handle vertical stacking
    # We use a representative character for height consistency
    left, top, right, bottom = draw.textbbox((0, 0), "A", font=font)
    char_height = (bottom - top) + 5

    # Calculate total width (width of the widest character)
    max_char_width = 0
    for char in text:
        l, t, r, b = draw.textbbox((0, 0), char, font=font)
        max_char_width = max(max_char_width, r - l)

    total_height = (len(text) * char_height)
    padding = 10

    # Draw background box for vertical text
    box_coords = [
        x - padding,
        y - padding/2,
        x + max_char_width + padding,
        y + 189 #total_height + padding + 35
    ]
    draw.rectangle(box_coords, fill='black')

    # Draw each character vertically
    for i, char in enumerate(text):
        draw.text((x, y + i * char_height), char, fill=color, font=font)
