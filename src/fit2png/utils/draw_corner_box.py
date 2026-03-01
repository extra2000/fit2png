def draw_corner_box(draw, x1, y1, x2, y2, color=(255, 0, 0, 255), width=3, corner_len=25):
    """
    Draws a corner-only (HUD-style) bounding box.
    corner_len is in pixels (will be clamped to fit small boxes).
    """
    # Ensure proper ordering
    x1, x2 = sorted((x1, x2))
    y1, y2 = sorted((y1, y2))

    box_w = max(0, x2 - x1)
    box_h = max(0, y2 - y1)
    L = int(min(corner_len, box_w * 0.5, box_h * 0.5))
    if L <= 0:
        return

    border_color = "black"
    border_width = max(1, width + 2)  # thin outline around the line

    # Top-left
    draw.line([(x1, y1), (x1 + L, y1)], fill=border_color, width=border_width)
    draw.line([(x1, y1), (x1 + L, y1)], fill=color,        width=width)
    draw.line([(x1, y1), (x1, y1 + L)], fill=border_color, width=border_width)
    draw.line([(x1, y1), (x1, y1 + L)], fill=color,        width=width)

    # Top-right
    draw.line([(x2 - L, y1), (x2, y1)], fill=border_color, width=border_width)
    draw.line([(x2 - L, y1), (x2, y1)], fill=color,        width=width)
    draw.line([(x2, y1), (x2, y1 + L)], fill=border_color, width=border_width)
    draw.line([(x2, y1), (x2, y1 + L)], fill=color,        width=width)

    # Bottom-left
    draw.line([(x1, y2), (x1 + L, y2)], fill=border_color, width=border_width)
    draw.line([(x1, y2), (x1 + L, y2)], fill=color,        width=width)
    draw.line([(x1, y2 - L), (x1, y2)], fill=border_color, width=border_width)
    draw.line([(x1, y2 - L), (x1, y2)], fill=color,        width=width)

    # Bottom-right
    draw.line([(x2 - L, y2), (x2, y2)], fill=border_color, width=border_width)
    draw.line([(x2 - L, y2), (x2, y2)], fill=color,        width=width)
    draw.line([(x2, y2 - L), (x2, y2)], fill=border_color, width=border_width)
    draw.line([(x2, y2 - L), (x2, y2)], fill=color,        width=width)
