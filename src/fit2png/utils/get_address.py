import datetime
from time import sleep
from geopy.geocoders import Nominatim

from ..common import SEMICIRCLES_TO_DEGREES

def get_address(address: str, pos_lat: float, pos_long: float, last_geopy_call: datetime.datetime, geopy_call_interval: int = 10, enforce_privacy: bool = False) -> tuple[str, datetime.datetime]:
    pos_lat = pos_lat * SEMICIRCLES_TO_DEGREES
    pos_long = pos_long * SEMICIRCLES_TO_DEGREES
    max_tries = 3

    geolocator = Nominatim(user_agent="fit2png")
    times_tried = 0

    if last_geopy_call is not None and ((datetime.datetime.now() - last_geopy_call).total_seconds() < geopy_call_interval):
        return address, last_geopy_call

    while True:
        location = geolocator.reverse(f"{pos_lat}, {pos_long}")
        road = location.raw['address'].get('road', '')
        neigh = location.raw['address'].get('neighbourhood', '')
        city = location.raw['address'].get('city', '')
        state = location.raw['address'].get('state', '')

        if enforce_privacy:
            if len(state) > 0 or times_tried > max_tries:
                break
        else:
            if (len(road) > 0 and len(neigh) > 0 and len(city) > 0 and len(state) > 0) or times_tried > max_tries:
                break

        times_tried += 1
        sleep(geopy_call_interval)

    if len(road) > 0:
        road = f"{road}, "
    if len(neigh) > 0:
        neigh = f"{neigh}, "
    if len(city) > 0:
        city = f"{city}, "

    if enforce_privacy:
        address = f"[REDACTED], {state}"
    else:
        address = f"{road}{neigh}{city}{state}"

    if len(address) > 44:
        return f"{address[:41]}...", datetime.datetime.now()
    else:
        return address, datetime.datetime.now()
