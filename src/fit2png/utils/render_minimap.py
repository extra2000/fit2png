import datetime
import io
from os import makedirs, path

import contextily as cx
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageOps

from src.fit2png.common import SEMICIRCLES_TO_DEGREES


def apply_levels(image: Image.Image, black_point: int, gamma: float, white_point: int)\
    -> Image.Image:
    """Apply GIMP-like levels adjustment to an RGB/RGBA image."""
    # Create a lookup table for the adjustment
    lut = []
    for i in range(256):
        # Clamp and normalize input
        v = min(max(i, black_point), white_point)
        normalized = (v - black_point) / (white_point - black_point)
        # Apply gamma and scale back to 0-255
        res = pow(normalized, 1.0 / gamma) * 255
        lut.append(int(res))

    # Apply to RGB channels only (preserving Alpha if present)
    if image.mode == "RGBA":
        r, g, b, a = image.split()
        r = r.point(lut)
        g = g.point(lut)
        b = b.point(lut)
        return Image.merge("RGBA", (r, g, b, a))
    return image.point(lut)

def render_minimap(data: dict, minimap_outdir: str, max_tails: int = 10) -> None:
    """Render minimap HUD."""
    diff_time = 0
    frame_counter = 0
    fig, ax = plt.subplots(figsize=(5, 5), frameon=False)

    for current_coord_index in range(len(data["record_mesgs"])):
        ax.clear()
        ax.set_axis_off()
        for i in range(max(0, current_coord_index - max_tails), current_coord_index + 1):
            x = data["record_mesgs"][i]

            pos_lat = x.get("position_lat", None)
            pos_long = x.get("position_long", None)
            if pos_lat is not None and pos_long is not None:
                pos_lat = x["position_lat"] * SEMICIRCLES_TO_DEGREES
                pos_long = x["position_long"] * SEMICIRCLES_TO_DEGREES

                # Lower margin, higher the zoom. Also crops the basemap to reduce bandwidth
                margin = 0.001
                ax.set_xlim(pos_long - margin, pos_long + margin)
                ax.set_ylim(pos_lat - margin, pos_lat + margin)

                # Add the basemap but force a LOWER zoom level (e.g., 15 or 16)
                # Standard street level is 18. By forcing 16, the labels will appear 4x larger.
                cx.add_basemap(ax,
                       crs="EPSG:4326",
                       source=cx.providers.OpenStreetMap.Mapnik,
                       zoom=19, # Lower zoom = More detail
                       attribution="")

                cx.add_basemap(ax,
                       crs="EPSG:4326",
                       source=cx.providers.Esri.WorldImagery,
                       zoom=19,
                       alpha=0.1,
                       attribution="")

                # Fix copyright (attribution) text color
                if ax.texts:
                    attribution_text = ax.texts[-1]
                    attribution_text.set_color("black")

                if i < current_coord_index:
                    # Trails
                    ax.plot(pos_long, pos_lat, "bo", markersize=15 - (((current_coord_index+1) - i)*0.5), markeredgecolor="white")
                else:
                    # Head
                    ax.plot(pos_long, pos_lat, "ro", markersize=15, markeredgecolor="white")

        # 1. Convert Figure to PIL Image
        buf = io.BytesIO()
        # Use bbox_inches='tight', pad_inches=0 to avoid extra white space
        fig.savefig(buf, format="png", transparent=True, bbox_inches="tight", pad_inches=0)
        buf.seek(0)
        img = Image.open(buf).convert("RGBA")

        # Apply GIMP Levels: (low, gamma, high)
        img = apply_levels(img, 146, 0.5, 255)

        # 2. Create a circular mask
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        # Draw a white circle (255) on the black background (0)
        # draw.ellipse((0, 0) + img.size, fill=255)
        draw.rectangle((0, 0, img.size[0], img.size[1]), fill=255)

        # 3. Apply the mask
        output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)

        # # 4. Draw a medium thick circle border
        # draw_output = ImageDraw.Draw(output)
        # border_width = 2
        # draw_output.ellipse(
        #         (0, 0, output.size[0], output.size[1]),
        #         outline="black",
        #         width=border_width
        #     )

        # 5. Save the processed image
        output.save(path.join(minimap_outdir, f"{frame_counter:05d}.png"))
        frame_counter += 1

        current_x = data["record_mesgs"][current_coord_index]
        next_x = data["record_mesgs"][current_coord_index+1] if current_coord_index < len(data["record_mesgs"]) - 1 else None
        current_timestamp = current_x["timestamp"].astimezone(datetime.timezone(datetime.timedelta(hours=8)))
        upcoming_time = next_x["timestamp"].astimezone(datetime.timezone(datetime.timedelta(hours=8))) if next_x is not None else None
        diff_time = (upcoming_time - current_timestamp).total_seconds() if upcoming_time is not None else 0
        if diff_time > 1:
            # Pad idle frames for easier Video Editing
            for i in range(1, int(diff_time)):
                output.save(path.join(minimap_outdir, f"{frame_counter:05d}.png"))
                frame_counter += 1

        plt.close(fig)
