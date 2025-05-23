import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, LiteralString


# fmt: off
EXCHANGE_RATES: Final[dict[LiteralString, float]] = {
    "RUR": 1.0,
    "USD": 80.0,
    "EUR": 90.0,
    "BYN": 26.0,
    "KZT": 0.15,
    "CNY": 12.0
} # fmt: on

_DEFAULT_CONFIG: Final[LiteralString] = "config.json"

logger = logging.getLogger(__name__)


@dataclass
class Options:
    """Options collected from a config file and command line flags.

    Options
    ----------
    *_query : str
        Common search params to retrieve vacancies
    num_workers : int
        Number of parallel workers for threading
    save_results_to_json : bool
        Save vacancy list to JSON file
    save_results_to_csv : bool
        Save vacancy list to CSV file
    """

    base_query: str = ""
    expr_query: str = ""
    text_query: str = ""
    page_query: str = ""

    num_workers: int = 1
    save_results_to_json: bool = False
    save_results_to_csv: bool = False

    def __repr__(self) -> str:
        opts: Final = ", ".join([f"{k}: {v}" for k, v in self.__dict__.items()])
        return f"{self.__class__.__name__}({opts})"


def prepare_options() -> Options:
    options = Options()

    # Parse config file first, so command line can override.
    _parse_config_file(options)
    _parse_args(options, sys.argv[1:])
    return options


def _parse_config_file(options: Options, config_file: str = _DEFAULT_CONFIG) -> None:
    """Parse a config file into an Options object."""
    if config_file and not Path(config_file).exists():
        logger.error(f"Cannot find config file: '{config_file}'")
        return

    config: dict[str, Any] = {}
    with open(config_file) as cfg:
        config = json.load(cfg)

    for key, value in config.items():
        if hasattr(options, key):
            setattr(options, key, value)
        else:
            logger.error(f"Unknown option in config: {key} = {value}")


def _parse_args(options: Options, argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description="HeadHunter vacancies inspector")
    parser.add_argument(
        "-t",
        "--text",
        action="store",
        type=str,
        default=None,
        help="Text to search (e.g. 'Python developer')",
    )
    parser.add_argument(
        "-n",
        "--num_workers",
        action="store",
        type=int,
        default=None,
        help="Number of parallel workers for multithreading.",
    )
    parser.add_argument(
        "-s",
        "--save_results_to_csv",
        action="store_true",
        default=None,
        help="Save parsed results to CSV file.",
    )

    args: Final = parser.parse_args(argv)

    if args.text is not None:
        pass  # don't used now

    if args.num_workers is not None:
        options.num_workers = args.num_workers

    if args.save_results_to_csv is not None:
        options.save_results_to_csv = args.save_results_to_csv
