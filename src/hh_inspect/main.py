import logging
from typing import Final, LiteralString

from hh_inspect.analyzer import Analyzer
from hh_inspect.data_collector import DataCollector
from hh_inspect.options import Options, prepare_options
from hh_inspect.vacancy import save_vacancies_to_json


_LOG_FILENAME: Final[LiteralString] = "../data/output.log"
_JSON_FILENAME: Final[LiteralString] = "../data/vacancies.json"
_CSV_FILENAME: Final[LiteralString] = "../data/vacancies.csv"

logging.basicConfig(
    format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
    datefmt="%d.%m %H:%M:%S",
    filename=_LOG_FILENAME,
    encoding="utf-8",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class HHInspector:
    """Main controller class to retrieve vacancies from HH and analyze them."""

    def __init__(self, options: Options) -> None:
        self.options = options
        self.collector: Final = DataCollector(options)
        self.analyzer = None

    def run(self) -> None:
        logger.info("Creating the list of vacancies...")
        vacancies: Final = self.collector.collect_vacancies()

        if self.options.save_results_to_json:
            save_vacancies_to_json(vacancies, _JSON_FILENAME)

        self.analyzer = Analyzer(vacancies)
        if self.options.save_results_to_csv:
            self.analyzer.save_vacancies_to_csv(_CSV_FILENAME)


def main() -> None:
    logger.info("HH Inspector started")
    options = prepare_options()

    hh = HHInspector(options)
    hh.run()
