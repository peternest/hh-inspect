import argparse
import json
from pathlib import Path
from typing import Any, Final, LiteralString

from hh_inspect.options import Options


_DEFAULT_CONFIG: Final[LiteralString] = "config.json"


# Direct changing of Options attributes. This it definitely bad!


def parse_config_file(options: Options, config_file: str = _DEFAULT_CONFIG) -> None:
    """Parse a config file into an Options object."""
    if config_file and not Path(config_file).exists():
        print(f"[CONFIG] Cannot find config file: '{config_file}'")
        return

    config: dict[str, Any] = {}
    with open(config_file) as cfg:
        config = json.load(cfg)

    for key, value in config.items():
        if hasattr(options, key):
            setattr(options, key, value)
        else:
            print(f"[CONFIG] Unknown option: {key} = {value}")


def parse_args(options: Options, argv: list[str]) -> None:
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

    if args.text is not None and options.query_params is not None:
        options.query_params["text"] = args.text

    if args.num_workers is not None:
        options.num_workers = args.num_workers

    if args.save_results_to_csv is not None:
        options.save_results_to_csv = args.save_results_to_csv
