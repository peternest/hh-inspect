import logging
import sys
from typing import Final, LiteralString

from hh_inspect.data_collector import DataCollector
from hh_inspect.options import Options, prepare_options


_LOG_FILENAME: Final[LiteralString] = "output.log"

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
        self.collector: Final = DataCollector(options)

    def run(self) -> None:
        logger.info("Creating a list of vacancies...")
        vacancies: Final = self.collector.collect_vacancies()


def main() -> None:
    logger.info("HH Inspector started")
    options = prepare_options(sys.argv[1:])

    hh = HHInspector(options)
    hh.run()
