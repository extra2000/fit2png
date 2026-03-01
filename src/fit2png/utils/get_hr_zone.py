import math

def get_hr_zone(hr: int, max_hr: int) -> int:
    zone1 = int(math.floor(max_hr * 0.6))
    zone2 = int(math.floor(max_hr * 0.7))
    zone3 = int(math.floor(max_hr * 0.8))
    zone4 = int(math.floor(max_hr * 0.9))
    if hr <= zone1:
        return 1
    elif hr <= zone2:
        return 2
    elif hr <= zone3:
        return 3
    elif hr <= zone4:
        return 4
    else:
        return 5
