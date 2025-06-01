import logging
from typing import Final, LiteralString

from hh_inspect.analyzer import Analyzer
from hh_inspect.console_printer import ConsolePrinter
from hh_inspect.data_collector import DataCollector
from hh_inspect.settings import Settings, load_settings
from hh_inspect.vacancy import Vacancy, save_vacancies_to_json


_LOG_FILENAME: Final[LiteralString] = "../../output/hh_inspect.log"
_JSON_FILENAME: Final[LiteralString] = "../../output/vacancies.json"
_CSV_FILENAME: Final[LiteralString] = "../../output/vacancies.csv"

logging.basicConfig(
    format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
    datefmt="%d.%m %H:%M:%S",
    filename=_LOG_FILENAME,
    encoding="utf-8",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
printer = ConsolePrinter()


class HHInspector:
    """Main controller class to retrieve vacancies from HH and analyze them."""

    analyzer: Analyzer
    collector: DataCollector
    settings: Settings

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.collector = DataCollector(settings)

    def collect_vacancies(self) -> list[Vacancy]:
        logger.info("Creating the list of vacancies...")
        vacancies = self.collector.collect_vacancies()

        if len(vacancies) == 0:
            return []

        if self.settings.general.save_results_to_json:
            save_vacancies_to_json(vacancies, _JSON_FILENAME)
        return vacancies

    def analyze_vacancies(self, vacancies: list[Vacancy]) -> None:
        self.analyzer = Analyzer(vacancies)
        if self.settings.general.save_results_to_csv:
            self.analyzer.save_vacancies_to_csv(_CSV_FILENAME)

        self.analyzer.print_salary_stats()
        self.analyzer.print_top_key_skills()
        self.analyzer.print_top_words_in_description()

    def print_vacancies(self, vacancies: list[Vacancy]) -> None:
        printer.print(f"Displaying: {len(vacancies)}")
        for vac in vacancies:
            printer.print(vac)


def main() -> None:
    logger.info("HH Inspector started")

    settings = load_settings()
    ConsolePrinter(settings.general.print_output_to_console)

    hh = HHInspector(settings)
    vacancies = hh.collect_vacancies()
    hh.print_vacancies(vacancies)
    hh.analyze_vacancies(vacancies)
