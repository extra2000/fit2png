import numpy as np
from PIL import Image, ImageChops

def apply_mask(frame_rgb: np.ndarray, canvas_rgba: Image.Image, *, invert: bool = False) -> Image.Image:
    """
    Uses canvas alpha as a cutout mask on the frame's alpha.
    invert=True  -> boxes become transparent (punched out)
    invert=False -> only boxes remain visible
    """
    base = Image.fromarray(frame_rgb.astype(np.uint8), mode="RGB").convert("RGBA")
    overlay = canvas_rgba.convert("RGBA")

    base_r, base_g, base_b, base_a = base.split()
    mask_a = overlay.split()[3]  # L mode

    # Make mask crisp: any drawn pixel becomes 255
    mask_bin = mask_a.point(lambda a: 255 if a > 0 else 0)

    if invert:
        mask_bin = ImageChops.invert(mask_bin)

    out_a = ImageChops.multiply(base_a, mask_bin)
    return Image.merge("RGBA", (base_r, base_g, base_b, out_a))
