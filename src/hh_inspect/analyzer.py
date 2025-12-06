# pyright: reportUnknownMemberType = false
# pyright: reportUnknownVariableType = false

import logging
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Final

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from hh_inspect.console_printer import ConsolePrinter
from hh_inspect.utils import find_top_words_in_list
from hh_inspect.vacancy import Vacancy


logger = logging.getLogger(__name__)
printer = ConsolePrinter()

pd.set_option("display.max_colwidth", 35)


class Analyzer:
    def __init__(self, vacancies: list[Vacancy], show_excluded: bool) -> None:
        self.vacancies = vacancies
        self.working_df = pd.DataFrame([vars(v) for v in self.vacancies if show_excluded or not v.excluded])
        # print(self.working_df.dtypes)  # noqa: ERA001

    def save_vacancies_to_csv(self, filename: Path) -> None:
        logger.info(f"Saving vacancies to '{filename}'...")
        self.working_df.to_csv(filename, index=False)

    def print_salary_stats(self) -> None:
        printer.print("")
        self.print_salary_stats_for_field("SALARY FROM", "salary_from")
        self.print_salary_stats_for_field("SALARY   TO", "salary_to")

    def print_salary_stats_for_field(self, prefix: str, field_name: str) -> None:
        """Print salary statistics for a given field."""
        if field_name not in self.working_df:
            logger.warning(f"Field '{field_name}' not found in working_df.")
            return

        stats = self.get_salary_stats_for_field(field_name)
        printer.print(
            f"{prefix} min: {stats['min']}, max: {stats['max']}, "
            f"mean: {stats['mean']:.0f}, median: {stats['median']:.0f}"
        )

    def get_salary_stats_for_field(self, field_name: str) -> dict[str, float]:
        series = self.working_df[field_name][self.working_df[field_name] > 0]
        return {
            "min": series.min(),
            "max": series.max(),
            "mean": series.mean(),
            "median": series.median(),
        }

    def print_top_key_skills(self, print_amount: int = 10) -> None:
        top_skills = self.get_top_key_skills()
        printer.print(f"\nThe {print_amount} most frequently used words in Key skills:")
        for key, value in top_skills[:print_amount]:
            printer.print(f"{key[:20]:20} {value}")

    def print_top_words_in_description(self, print_amount: int = 10) -> None:
        top_words = self.get_top_description_words()
        printer.print(f"\nThe {print_amount} most frequently used words in Description:")
        for key, value in top_words[:print_amount]:
            printer.print(f"{key[:20]:20} {value}")

    def get_top_key_skills(self) -> list[tuple[str, int]]:
        df_column = self.working_df["key_skills"]
        key_skills_list: list[list[str]] = df_column.to_list()
        skills_list = [x for elem in key_skills_list for x in elem]
        return find_top_words_in_list(skills_list)

    def get_top_description_words(self) -> list[tuple[str, int]]:
        df_column: pd.Series[str] = self.working_df["description"]
        words_list = " ".join(df_column.to_list())
        eng_words_list: Final[list[str]] = re.findall("[a-zA-Z_]+", words_list)
        filtered_list = Analyzer.filter_noise_words(eng_words_list)
        return find_top_words_in_list(filtered_list)

    @staticmethod
    def filter_noise_words(string_list: list[str]) -> Iterable[str]:
        noise_words = {"API", "IT", "quot", "and", "or", "I", "it"}
        return filter(lambda w: w not in noise_words, string_list)

    def draw_plots(self) -> None:
        printer.print("\nClose an image window to exit...")
        fig = plt.figure("Salary Charts", figsize=(12, 6))

        fig.add_subplot(2, 2, 1)
        plt.title("Amount of salaries")
        plt.ylabel("Salary (rub)")
        sns.swarmplot(data=self.working_df[["salary_from", "salary_to"]], size=5)

        fig.add_subplot(2, 2, 3)
        plt.title("Min, max and quantiles")
        plt.ylabel("Salary (rub)")
        sns.boxplot(data=self.working_df[["salary_from", "salary_to"]], width=0.2, native_scale=True)

        fig.add_subplot(2, 2, 2)
        plt.title("Distribution of salary_to")
        plt.xlabel("Salary (rub)")
        plt.grid(True)
        sns.histplot(data=self.working_df["salary_to"], bins=12, color="C1", kde=True)  # type: ignore

        fig.add_subplot(2, 2, 4)
        plt.title("Distribution of salary_from")
        plt.xlabel("Salary (rub)")
        plt.grid(True)
        sns.histplot(data=self.working_df["salary_from"], bins=12, color="C0", kde=True)  # type: ignore

        plt.tight_layout()
        plt.show()
