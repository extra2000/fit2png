from os import path

import numpy as np
from PIL import Image, ImageDraw
import cv2
from ultralytics import YOLO

from .apply_mask import apply_mask
from .color_for_class_id import color_for_class_id
from .draw_corner_box import draw_corner_box
from .draw_label import draw_label
from .draw_shaded_box import draw_shaded_box

def computer_vision_hud(video_paths, modelname_bbox, modelname_seg, bbox_outdir, seg_outdir, label_outdir):
    """
    Process video frames using YOLO models for bounding box detection and segmentation, and save results as PNG images.

    :param video_paths: List of video file paths to process.
    :param modelname_bbox: Path to the YOLO model for bounding box detection.
    :param modelname_seg: Path to the YOLO model for segmentation.
    :param bbox_outdir: Output directory for bounding box images.
    :param seg_outdir: Output directory for segmentation mask images.
    :param label_outdir: Output directory for label images.
    :return: None
    """
    model_bbox = YOLO(modelname_bbox)
    model_seg = YOLO(modelname_seg)

    frame_idx = 0
    names = None  # keep across all videos (optional)

    for video_path in video_paths:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open video: {video_path}")

        while True:
            ok, frame_bgr = cap.read()
            if not ok:
                break

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            res = model_bbox.predict(frame_rgb, verbose=False)[0]

            if names is None:
                names = res.names

            h, w = frame_rgb.shape[:2]

            # Render bounding boxes
            canvas_bbox = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(canvas_bbox)
            for box in res.boxes:
                x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                cls_id = int(box.cls[0].item())
                color = color_for_class_id(cls_id, alpha=255)
                draw_corner_box(draw, x1, y1, x2, y2, color=color, width=3, corner_len=30)
            canvas_bbox.save(path.join(bbox_outdir, f"{frame_idx:07d}.png"))

            # Render bounding box mask for segmentation
            canvas_bbox_mask = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(canvas_bbox_mask)
            for box in res.boxes:
                x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                draw_shaded_box(draw, x1, y1, x2, y2, fill=(255, 255, 255, 220), outline_width=0)
            masked_frame = apply_mask(frame_rgb, canvas_bbox_mask)

            # Render segmentation mask
            bg = Image.new("RGBA", masked_frame.size, (255, 255, 255, 255))  # white background
            composited = Image.alpha_composite(bg, masked_frame).convert("RGB")
            img_rgb = np.array(composited)
            seg_res = model_seg.predict(img_rgb, retina_masks=True, verbose=False)[0]
            if seg_res.masks is not None and seg_res.masks.data is not None and len(seg_res.masks.data):
                m = seg_res.masks.data  # (N, H, W) torch tensor
                union = m.any(dim=0).to(dtype=m.dtype)  # (H, W) values 0/1
                mask_u8 = (union.cpu().numpy() * 255).astype(np.uint8)
                Image.fromarray(mask_u8, mode="L").save(path.join(seg_outdir, f"{frame_idx:07d}.png"))
            else:
                blank = np.zeros((h, w), dtype=np.uint8)  # (H, W) all zeros
                Image.fromarray(blank, mode="L").save(path.join(seg_outdir, f"{frame_idx:07d}.png"))

            # Render labels
            label_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            label_draw = ImageDraw.Draw(label_layer)
            for box in res.boxes:
                x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item()) if box.conf is not None else 1.0
                cls_name = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else str(cls_id)
                text = f"{cls_name} {conf:.2f}"
                draw_label(label_draw, x1, y1, text, canvas_size=(w, h))
            label_layer.save(path.join(label_outdir, f"{frame_idx:07d}.png"))

            frame_idx += 1
        cap.release()
