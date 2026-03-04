from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import torch


def depth_hud(video_paths: list[str], modelname_depth: str, modeldepth_size: str, depth_outdir: str) -> None:
    """Process depth.

    :param video_paths: List of video file paths to process.
    :param modelname_depth: Path to the MiDaS model for depth estimation.
    :param modeldepth_size: Size of MiDaS model to use.
    :return: None
    """
    midas = torch.hub.load(modelname_depth, modeldepth_size)
    midas_transforms = torch.hub.load(modelname_depth, "transforms")
    device = torch.device("cpu")
    midas.to(device)
    midas.eval()
    transform = midas_transforms.dpt_transform

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

            # MiDaS depth estimation
            input_batch = transform(frame_rgb).to(device)
            # Predict and resize to original resolution
            with torch.no_grad():
                prediction = midas(input_batch)
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=frame_rgb.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()
            result = prediction.cpu().numpy()
            plt.imsave(str(Path(depth_outdir) / f"{frame_idx:07d}.jpg"), result)
            plt.close()

            frame_idx += 1
        cap.release()
