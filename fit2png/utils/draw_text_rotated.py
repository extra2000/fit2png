from PIL import Image, ImageDraw, ImageFont

def draw_text_rotated(image, text, color, x, y, angle=90):
    # Define font
    font_size = 24
    try:
        font = ImageFont.truetype("Roboto-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    # Determine text size
    left, top, right, bottom = font.getbbox(text)
    w, h = right - left, 22 #bottom - top + 5

    # Create a temporary image for the text with an alpha channel
    # Add some padding to avoid clipping during rotation
    txt_img = Image.new('RGBA', (w + 4, h + 4), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((3, 0), text, font=font, fill=color)

    # Rotate the text image
    rotated_txt = txt_img.rotate(angle, expand=True)

    # Draw black background box on the main image
    # The size of the background matches the rotated image's size
    rw, rh = rotated_txt.size
    padding = 5
    draw = ImageDraw.Draw(image)
    draw.rectangle([
        x - padding,
        y - padding,
        x + rw + padding/3,
        976], #y + rh + padding],
        fill='black'
    )

    # Paste onto the main image (using the rotated image as its own mask for transparency)
    image.paste(rotated_txt, (int(x), int(y)), rotated_txt)
