from PIL import ImageDraw

from ..common import SEMICIRCLES_TO_DEGREES, NO_SIGNAL
from . import get_hr_zone, draw_text, draw_text_rotated

def image_draw(green_image, current_time, x, address, max_hr, leftmargin, bottommargin, yspacing, enforce_privacy=False, is_active=True):
    draw = ImageDraw.Draw(green_image)
    speed_kmh = x['speed'] * 3.6
    distance_km = x['distance'] / 1000
    hr = x['heart_rate']
    temp = x['temperature']

    pos_lat = x.get('position_lat', None)
    pos_long = x.get('position_long', None)
    if pos_lat is not None and pos_long is not None:
        pos_lat = '[REDACTED]' if enforce_privacy else x['position_lat'] * SEMICIRCLES_TO_DEGREES
        pos_long = '[REDACTED]' if enforce_privacy else x['position_long'] * SEMICIRCLES_TO_DEGREES
    else:
        pos_lat = NO_SIGNAL
        pos_long = NO_SIGNAL

    altitude = x['altitude']
    day_name = current_time.strftime("%A").upper()
    color = "white" if is_active else "yellow"

    draw_text(draw, address, color, leftmargin, bottommargin - yspacing*4, mono=False)
    draw_text(draw, str(f"LAT {pos_lat}, LONG {pos_long}"), color, leftmargin, bottommargin - yspacing*3)
    draw_text(draw, str(f"{day_name} {temp}\u00b0C {current_time} (MYT)"), 'white', leftmargin, bottommargin - yspacing*2)
    draw_text(draw, str(f"{speed_kmh:.2f} KM/H, {distance_km:.4f} KM, ALT {altitude:.1f} M"), color, leftmargin, bottommargin - yspacing)
    draw_text(draw, str(f"{hr}/{max_hr} BPM Z{get_hr_zone(hr, max_hr)} ({(hr/max_hr)*100:.2f}%)"), color, leftmargin, bottommargin)
    draw_text_rotated(green_image, f"CYCPLUS M1", 'white', leftmargin - 37, bottommargin - yspacing*4+2, bottommargin, 270)
