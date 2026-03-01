from os import path
from pathlib import Path

import av
import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm


def rms_dbfs(samples: np.ndarray, eps: float = 1e-12) -> float:
    """RMS level in dBFS (NOT RMS)."""
    samples = np.asarray(samples, dtype=np.float32)
    if samples.size == 0:
        return float("-inf")
    rms = np.sqrt(np.mean(samples * samples) + eps)
    return 20.0 * np.log10(rms + eps)

def frame_loudness_lr(audio_lr: np.ndarray, i0: int, i1: int) -> tuple[float, float] | tuple[float, None]:
    """audio_lr shape: (channels, samples).

    Returns (L_dBFS, R_dBFS) when 2+ channels, else (mono_dBFS, None)
    """
    chunk = audio_lr[:, i0:i1]
    if chunk.shape[1] == 0:
        return float("-inf"), (float("-inf") if audio_lr.shape[0] >= 2 else None)

    if audio_lr.shape[0] >= 2:
        l = rms_dbfs(chunk[0])
        r = rms_dbfs(chunk[1])
        return l, r
    else:
        mono = rms_dbfs(chunk[0])
        return mono, None

def peak_dbfs(samples: np.ndarray, eps: float = 1e-12) -> float:
    """Sample-peak level in dBFS (NOT RMS).

    0 dBFS == full scale (abs(sample) == 1.0 for float PCM).
    """
    samples = np.asarray(samples, dtype=np.float32)
    if samples.size == 0:
        return float("-inf")
    peak = float(np.max(np.abs(samples)))
    return 20.0 * np.log10(max(peak, eps))

def frame_volume_lr_peak(audio_lr: np.ndarray, i0: int, i1: int) -> tuple[float, float] | tuple[float, None]:
    """audio_lr shape: (channels, samples).

    Returns (L_peak_dBFS, R_peak_dBFS) when 2+ channels, else (mono_peak_dBFS, None)
    """
    chunk = audio_lr[:, i0:i1]
    if chunk.shape[1] == 0:
        return float("-inf"), (float("-inf") if audio_lr.shape[0] >= 2 else None)

    if audio_lr.shape[0] >= 2:
        l = peak_dbfs(chunk[0])
        r = peak_dbfs(chunk[1])
        return l, r
    else:
        mono = peak_dbfs(chunk[0])
        return mono, None

def render_audiometer(video_paths: str, audiometer_outdir: str, floor_db: float, ceil_db: float) -> None:
    """Render audiometer HUD."""
    frame_idx = 0
    for video_path in video_paths:
        # Video via OpenCV (frames)
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:
            raise RuntimeError(f"Could not read FPS from video: {video_path}")
        frame_duration = 1.0 / fps

        # Audio via PyAV (demux/decode)
        container = av.open(video_path)

        audio_stream = next((s for s in container.streams if s.type == "audio"), None)
        if audio_stream is None:
            raise RuntimeError("No audio stream found in container")

        # Define sample rate ONCE, from the stream (robust + simple)
        if getattr(audio_stream, "rate", None) is None:
            raise RuntimeError("Audio stream has no sample rate (audio_stream.rate is None)")
        sr = int(audio_stream.rate)

        audio_frames_lr: list[np.ndarray] = []

        for audio_frame in container.decode(audio_stream):
            arr = audio_frame.to_ndarray()

            # Normalize to shape (channels, samples)
            if arr.ndim == 1:
                # mono interleaved -> (1, samples)
                arr = arr[np.newaxis, :]
            elif arr.ndim == 2:
                # could already be (channels, samples) (planar)
                # if it's (samples, channels) swap it
                if arr.shape[0] > arr.shape[1]:
                    # heuristic: more samples than channels -> (samples, channels)
                    # so transpose to (channels, samples)
                    arr = arr.T
            else:
                raise RuntimeError(f"Unexpected audio ndarray shape: {arr.shape}")

            audio_frames_lr.append(arr.astype(np.float32, copy=False))

        audio_lr = np.concatenate(audio_frames_lr, axis=1) if audio_frames_lr else np.zeros((1, 0), dtype=np.float32)
        channels = audio_lr.shape[0]


        # Initialize plot
        font_size = 10
        font_path = Path("~/.local/share/fonts/google/roboto_mono/RobotoMono-VariableFont_wght.ttf").expanduser()
        mono_fp = fm.FontProperties(fname=font_path, size=font_size)

        xmin = 10 ** (floor_db / 20.0)  # amplitude at -60 dBFS
        xmax = 10 ** (ceil_db / 20.0)   # amplitude at 0 dBFS = 1.0

        plt.style.use("dark_background")

        fig, ax = plt.subplots(figsize=(2.7, 0.8), dpi=150)

        bars = ax.barh(
            ["CH2", "CH1"],
            [0.0, 0.0],
            left=xmin,
            color="white",
            edgecolor="white",
            alpha=1.0,
            height=0.6,
        )

        ax.set_xscale("log")
        ax.set_xlim(xmin, xmax)
        # ax.set_xlabel("Amplitude", fontproperties=mono_fp)
        # ax.set_title("Loudness", fontproperties=mono_fp)

        # dB tick labels on the X axis
        # [-60, -56, -52, -48, -44, -40, -36, -32, -28, -24, -20, -16, -12, -8, -4, 0]
        # [-60, -48, -36, -24, -12, -6, 0]
        ticks_db = np.array([-36, -12, 0], dtype=float)
        ax.set_xticks(10 ** (ticks_db / 20.0))
        ax.set_xticklabels([f"{int(t)} dB" for t in ticks_db])

        ax.grid(True, which="both", axis="x", alpha=0.3)

        txt = fig.text(
            0.2, 0.98, "",
            ha="left", va="top",
            color="white",
            fontproperties=mono_fp,
        )

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(mono_fp)

        fig.subplots_adjust(top=1.20)   # leaves room for the text above the axes
        fig.tight_layout()


        while True:
            ok, frame_bgr = cap.read()
            if not ok:
                break

            t0 = frame_idx * frame_duration
            t1 = (frame_idx + 1) * frame_duration

            i0 = int(t0 * sr)
            i1 = int(t1 * sr)

            # l_dbfs, r_dbfs = frame_loudness_lr(audio_lr, i0, i1)
            l_dbfs, r_dbfs = frame_volume_lr_peak(audio_lr, i0, i1)


            # Plot loudness meter
            l_val = float(l_dbfs) if (l_dbfs is not None and np.isfinite(l_dbfs)) else floor_db
            r_val = float(r_dbfs) if (r_dbfs is not None and np.isfinite(r_dbfs)) else np.nan

            l_plot_db = float(np.clip(l_val, floor_db, ceil_db))
            r_plot_db = floor_db if not np.isfinite(r_val) else float(np.clip(r_val, floor_db, ceil_db))

            l_amp = 10 ** (l_plot_db / 20.0)
            r_amp = 10 ** (r_plot_db / 20.0)

            # Baseline stays at xmin (=-60 dBFS in amplitude)
            bars[0].set_x(xmin)
            bars[1].set_x(xmin)

            # Width is offset from baseline (amplitude units)
            bars[0].set_width(r_amp - xmin)
            bars[1].set_width(l_amp - xmin)

            # bars[1].set_alpha(0.25 if not np.isfinite(r_val) else 1.0)

            txt.set_text(f"{l_plot_db:5.1f} dB       {'—' if not np.isfinite(r_val) else f'{r_plot_db:5.1f} dB'}")
            # txt.set_text(f"{r_plot_db:5.1f} dB       {r_plot_db:5.1f} dB")

            out_png = path.join(audiometer_outdir, f"{frame_idx:07d}.png")
            fig.savefig(out_png, format="png", transparent=True)


            frame_idx += 1
            plt.close(fig)

        cap.release()
        container.close()
