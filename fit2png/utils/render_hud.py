import datetime
from os import path
from time import sleep

from PIL import Image

from . import get_address, image_draw
from ..common import NO_SIGNAL

def render_hud(data, max_hr, outdir, geopy_call_interval=10, wait_for_geopy=False, enforce_privacy=False):
    leftmargin = 50
    bottommargin = 150
    screen_resolution = (864, bottommargin + 26 + 10)
    yspacing = 34
    prev_timestamp = None
    xprev = None
    frame_counter = 0
    last_geopy_call = None
    address = ''

    for x in data['record_mesgs']:
        current_timestamp = x['timestamp'].astimezone(datetime.timezone(datetime.timedelta(hours=8)))
        if wait_for_geopy:
            sleep(geopy_call_interval)
        pos_lat = x.get('position_lat', None)
        pos_long = x.get('position_long', None)
        if pos_lat is not None and pos_long is not None:
            address, last_geopy_call = get_address(address, pos_lat, pos_long, last_geopy_call, geopy_call_interval, enforce_privacy)
        else:
            address = NO_SIGNAL

        if prev_timestamp is not None:
            diff_time = (current_timestamp - prev_timestamp).total_seconds()
            if diff_time > 1:
                # Pad idle frames for easier Video Editing
                for i in range(1, int(diff_time)):
                    green_image = Image.new('RGB', screen_resolution, color='green')
                    image_draw(green_image, prev_timestamp + datetime.timedelta(seconds=i), xprev, address, max_hr, leftmargin, bottommargin, yspacing, enforce_privacy, is_active=False)
                    green_image.save(path.join(outdir, f'{frame_counter:05d}.png'))
                    frame_counter += 1
        green_image = Image.new('RGB', screen_resolution, color='green')
        image_draw(green_image, current_timestamp, x, address, max_hr, leftmargin, bottommargin, yspacing, enforce_privacy)
        green_image.save(path.join(outdir, f'{frame_counter:05d}.png'))
        frame_counter += 1
        prev_timestamp = current_timestamp
        xprev = x
