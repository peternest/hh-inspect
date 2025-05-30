# pyright: reportUnknownMemberType = false
# pyright: reportUnknownVariableType = false

import logging
from typing import Final, Iterable
import re

import pandas as pd

from hh_inspect.console_printer import ConsolePrinter
from hh_inspect.vacancy import Vacancy
from hh_inspect.utils import find_top_words_in_list

logger = logging.getLogger(__name__)
printer = ConsolePrinter()

pd.set_option("display.max_colwidth", 35)


class Analyzer:
    def __init__(self, vacancies: list[Vacancy]) -> None:
        self.vacancies: Final = vacancies
        self.working_df: Final = pd.DataFrame([vars(v) for v in self.vacancies])
        # print(self.working_df.dtypes)

    def save_vacancies_to_csv(self, filename: str) -> None:
        logger.info(f"Saving vacancies to '{filename}'...")
        self.working_df.to_csv(filename, index=False)

    def analyze_salary(self) -> None:
        printer.print("")
        self.calc_and_print_salary_stat("SALARY FROM", "salary_from")
        self.calc_and_print_salary_stat("SALARY TO", "salary_to")

    def calc_and_print_salary_stat(self, prefix: str, field_name: str) -> None:
        """Print salary statistics for a given field."""

        if field_name not in self.working_df:
            logger.warning(f"Field '{field_name}' not found in working_df.")
            return

        stats: Final = self.calc_salary_stats(field_name)
        printer.print(
            f"{prefix} min: {stats['min']}, max: {stats['max']}, mean: {stats['mean']:.0f}, median: {stats['median']:.0f}"
        )

    def calc_salary_stats(self, field_name: str) -> dict[str, float]:
        series: Final = self.working_df[field_name][self.working_df[field_name] > 0]
        return {
            "min": series.min(),
            "max": series.max(),
            "mean": series.mean(),
            "median": series.median(),
        }

    def analyze_key_skills(self, print_amount: int = 10) -> None:
        df_column: Final = self.working_df["key_skills"]

        key_skills_list: list[list[str]] = df_column.to_list()
        skills_list: Final = [x for elem in key_skills_list for x in elem]
        top_skills: Final = find_top_words_in_list(skills_list)

        printer.print(f"\nThe {print_amount} most frequently used words in Key skills:")
        for key, value in top_skills[:print_amount]:
            printer.print(f"{key[:20]:20} {value}")

    def analyze_description(self, print_amount: int = 15) -> None:
        df_column: Final = self.working_df["description"]

        words_list: Final = " ".join(df_column.to_list())  # type: ignore
        eng_words_list: Final[list[str]] = re.findall("[a-zA-Z_]+", words_list)
        filtered_list: Final = Analyzer.filter_noise_words(eng_words_list)
        top_skills: Final = find_top_words_in_list(filtered_list)

        printer.print(f"\nThe {print_amount} most frequently used words in Description:")
        for key, value in top_skills[:print_amount]:
            printer.print(f"{key[:20]:20} {value}")

    @staticmethod
    def filter_noise_words(string_list: list[str]) -> Iterable[str]:
        noise_words: Final = set(["API", "IT", "quot", "and", "or", "I", "it"])
        return filter(lambda w: w not in noise_words, string_list)
