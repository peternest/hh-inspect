import logging
from pathlib import Path
from typing import Final

from hh_inspect.analyzer import Analyzer
from hh_inspect.console_printer import ConsolePrinter
from hh_inspect.data_collector import DataCollector
from hh_inspect.settings import Settings, load_settings
from hh_inspect.vacancy import Vacancy, save_vacancies_to_json


_ROOT_DIR: Final = Path.resolve(Path(__file__).parent.parent.parent)

_CONFIG_FILENAME: Final = _ROOT_DIR / "config.yaml"

_LOG_FILENAME: Final = _ROOT_DIR / "output/hh_inspect.log"
_JSON_FILENAME: Final = _ROOT_DIR / "output/vacancies.json"
_CSV_FILENAME: Final = _ROOT_DIR / "output/vacancies.csv"

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

        if self.settings.general.draw_salary_plots:
            self.analyzer.draw_plots()

    def print_vacancies(self, vacancies: list[Vacancy]) -> None:
        num_found = len(vacancies)
        num_displaying = min(num_found, 20)
        printer.print(f"Displaying {num_displaying} of {num_found}")
        for vac in vacancies[:num_displaying]:
            printer.print(vac)


def main() -> None:
    logger.info("HH Inspector started")

    settings = load_settings(_CONFIG_FILENAME)
    ConsolePrinter(settings.general.print_output_to_console)

    hh = HHInspector(settings)
    vacancies = hh.collect_vacancies()
    if len(vacancies):
        hh.print_vacancies(vacancies)
        hh.analyze_vacancies(vacancies)
