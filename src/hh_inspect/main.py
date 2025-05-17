import logging
from typing import Final, LiteralString

from hh_inspect.data_collector import DataCollector
from hh_inspect.options import Options
from hh_inspect.parsers import parse_args, parse_config_file


_LOG_FILENAME: Final[LiteralString] = "output.log"

logging.basicConfig(
    format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=_LOG_FILENAME,
    encoding="utf-8",
    level=logging.INFO,
)

log = logging.getLogger(__name__)


class HHInspector:
    """Main controller class to retrieve vacancies from HH and analyze them."""

    def __init__(self, options: Options) -> None:
        self.collector: Final = DataCollector(options)
        # self.analyzer: Final = Analyzer(options.save_results_to_csv)

    def run(self) -> None:
        log.info("Creating a list of vacancies...")
        vacancies: Final = self.collector.collect_vacancies()
        # df = self.analyzer.prepare_df(vacancies)
        # print(f"[INFO]: Dataframe: {df}")


def main(argv: list[str]) -> None:
    log.info("HH Inspector started")
    options = Options()

    # Parse config file first, so command line can override.
    parse_config_file(options)
    parse_args(options, argv)

    hh = HHInspector(options)
    hh.run()
