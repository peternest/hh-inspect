from typing import Final

from hh_inspect.data_collector import DataCollector
from hh_inspect.options import Options
from hh_inspect.parsers import parse_args, parse_config_file


class HHInspector:
    """Main controller class to retrieve vacancies from HH and analyze them."""

    def __init__(self, options: Options) -> None:
        self.collector: Final = DataCollector(options)

    def run(self) -> None:
        print("[INFO]: Creating list of vacancies...")
        vacancies: Final = self.collector.collect_vacancies()
        # print(f"[INFO]: Vacancies: {vacancies}")


def main(argv: list[str]) -> None:
    options = Options()

    # Parse config file first, so command line can override.
    parse_config_file(options)
    parse_args(options, argv)

    hh = HHInspector(options)
    hh.run()
