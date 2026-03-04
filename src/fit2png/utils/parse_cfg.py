"""Provides parsing YAML config file."""
import logging
from pathlib import Path

import yaml

log = logging.getLogger(__name__)


def parse_cfg(config_fname: str) -> dict:
    """Parse YAML config file.

    :param config_fname: Path to the config file.
    :return: A dictionary resulting from the parsing process. The specifics of
        the returned dictionary are undefined within this code.
    :rtype: dict
    """
    with Path(config_fname).open("r") as f:
        log.info("Using config file: %s", str(Path(config_fname).resolve()))
        cfg = yaml.safe_load(f)
        fit_id = Path(cfg["fit"]["filename"]).stem
        cfg["computed"] = {
            "fit_id": fit_id,
            "hud_outdir": str(Path(cfg["outdir"]) / fit_id / "hud"),
            "hud_redacted_outdir": str(Path(cfg["outdir"]) / fit_id / "hud_redacted"),
            "minimap_outdir": str(Path(cfg["outdir"]) / fit_id / "minimap"),
            "bbox_outdir": str(Path(cfg["outdir"]) / fit_id / "bbox"),
            "seg_outdir": str(Path(cfg["outdir"]) / fit_id / "seg"),
            "label_outdir": str(Path(cfg["outdir"]) / fit_id / "label"),
            "audiometer_outdir": str(Path(cfg["outdir"]) / fit_id / "audiometer"),
            "depth_outdir": str(Path(cfg["outdir"]) / fit_id / "depth"),
        }
        return cfg
