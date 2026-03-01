def color_for_class_id(cls_id: int, alpha: int = 255) -> tuple[int, int, int, int]:
    """Return a white color with optional alpha transparency for a given class ID.

    Args:
        cls_id (int): Class ID for which to generate color.
        alpha (int, optional): Alpha transparency value (0-255). Defaults to 255 (fully opaque).

    Returns:
        tuple[int, int, int, int]: RGBA color tuple.
    """
    return (255, 255, 255, alpha)
