"""Entry-point for fit2png executable."""
import argparse
import logging
import logging.handlers
from functools import partial
from pathlib import Path
from pprint import PrettyPrinter

import argcomplete

from src.fit2png import __version__
from src.fit2png.utils import computer_vision_hud, parse_cfg, read_fit, render_hud, render_minimap, render_audiometer, depth_hud

log = logging.getLogger(__name__)
pp = PrettyPrinter(indent=2, width=80, compact=True)


def main() -> None:
    """Entry-point for fit2png executable."""
    try:
        _app()
    except KeyboardInterrupt:
        log.info("Received keyboard interrupt. Exiting.")

def _app() -> None:
    args, parser = _parse_args()

    _init_log(args.loglevel)

    log.info("fit2png version %s", __version__)

    command = {
        "fit": partial(_fit, args),
        "minimap": partial(_minimap, args),
        "cv": partial(_cv, args),
        "audiometer": partial(_audiometer, args),
        "depth": partial(_depth, args)
    }

    choice = command.get(args.command, parser.print_help())
    result = choice()

    if result is not None:
        if isinstance(result, dict):
            print(result if args.no_pprint else pp.pformat(result)) # noqa: T201
        else:
            print(result) # noqa: T201


def _init_log(loglevel:str="INFO") -> None:
    """Initialize log.

    Parameters
    ----------
    loglevel : str
        Log level for ``logging`` module. Default is ``'INFO'``.

    """
    formatter = logging.Formatter('{"timestamp": "%(asctime)s", "process_id": "%(process)d", "thread_id": "%(thread)d", "severity": "%(levelname)s", "module": "%(name)s", "line": "%(lineno)d", "message": "%(message)s"}')  # noqa: E501

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(loglevel)

    mainlog = logging.getLogger("src")
    mainlog.addHandler(stream_handler)
    mainlog.setLevel(loglevel)


def _parse_args() -> tuple[argparse.Namespace, argparse.ArgumentParser]:
    parser = argparse.ArgumentParser(
        description=f"fit2png {__version__}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--loglevel", help="Log level", default="INFO")
    parser.add_argument("--config", help="Path to config file", default="config.yaml")

    subparser = parser.add_subparsers(help="Command", dest="command")

    fit = subparser.add_parser("fit", help="Render FIT HUD")
    fit_opt_args = fit.add_argument_group("optional arguments")
    fit_opt_args.add_argument("--redacted", type=bool, default=False,
                              help="Exclude privacy info.")

    minimap = subparser.add_parser("minimap", help="Render Minimap HUD")

    cv = subparser.add_parser("cv", help="Render Detection HUD")

    depth = subparser.add_parser("depth", help="Render Depth HUD")

    audiometer = subparser.add_parser("audiometer", help="Render Audio Meter HUD")

    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    return args, parser

def _fit(args: argparse.Namespace) -> None:
    cfg = parse_cfg(args.config)
    data = read_fit(cfg["fit"]["filename"])
    log.info(data["file_id_mesgs"][0])

    if not args.redacted:
        Path(cfg["computed"]["hud_outdir"]).mkdir(parents=True, exist_ok=True)
        render_hud(data, cfg["fit"]["max_hr"], cfg["computed"]["hud_outdir"],
                   geopy_call_interval=cfg["geopy"]["call_interval"],
                   wait_for_geopy=cfg["geopy"]["wait"], enforce_privacy=args.redacted)
    else:
        Path(cfg["computed"]["hud_redacted_outdir"]).mkdir(parents=True, exist_ok=True)
        render_hud(data, cfg["fit"]["max_hr"], cfg["computed"]["hud_redacted_outdir"],
                   geopy_call_interval=cfg["geopy"]["call_interval"],
                   wait_for_geopy=cfg["geopy"]["wait"], enforce_privacy=args.redacted)

def _minimap(args: argparse.Namespace) -> None:
    cfg = parse_cfg(args.config)
    data = read_fit(cfg["fit"]["filename"])
    log.info(data["file_id_mesgs"][0])

    Path(cfg["computed"]["minimap_outdir"]).mkdir(parents=True, exist_ok=True)

    render_minimap(data, cfg["computed"]["minimap_outdir"], cfg["geopy"]["call_interval"])

def _cv(args: argparse.Namespace) -> None:
    cfg = parse_cfg(args.config)

    Path(cfg["computed"]["bbox_outdir"]).mkdir(parents=True, exist_ok=True)
    Path(cfg["computed"]["seg_outdir"]).mkdir(parents=True, exist_ok=True)
    Path(cfg["computed"]["label_outdir"]).mkdir(parents=True, exist_ok=True)

    computer_vision_hud(cfg["video"]["paths"], cfg["cv"]["model"]["bbox"],
                        cfg["cv"]["model"]["seg"], cfg["computed"]["bbox_outdir"],
                        cfg["computed"]["seg_outdir"], cfg["computed"]["label_outdir"])

def _depth(args: argparse.Namespace) -> None:
    cfg = parse_cfg(args.config)
    Path(cfg["computed"]["depth_outdir"]).mkdir(parents=True, exist_ok=True)
    depth_hud(cfg["video"]["paths"], cfg["cv"]["model"]["depth"]["name"], cfg["cv"]["model"]["depth"]["size"], cfg["computed"]["depth_outdir"])

def _audiometer(args: argparse.Namespace) -> None:
    cfg = parse_cfg(args.config)

    Path(cfg["computed"]["audiometer_outdir"]).mkdir(parents=True, exist_ok=True)

    render_audiometer(cfg["video"]["paths"], cfg["computed"]["audiometer_outdir"],
                      cfg["audiometer"]["floor_db"], cfg["audiometer"]["ceiling_db"])
