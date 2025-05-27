import logging
from typing import Final, reveal_type
from collections import Counter
import re

import pandas as pd

from hh_inspect.vacancy import Vacancy

logger = logging.getLogger(__name__)

pd.set_option("display.max_colwidth", 35)


class Analyzer:
    def __init__(self, vacancies: list[Vacancy]) -> None:
        self.vacancies: Final = vacancies
        self.working_df: Final = pd.DataFrame([vars(v) for v in self.vacancies])

    def save_vacancies_to_csv(self, filename: str) -> None:
        logger.info(f"Saving vacancies to '{filename}'...")
        self.working_df.to_csv(filename, index=False)

    def analyze_salary(self) -> None:
        df: Final = self.working_df[["employer_name", "vacancy_name", "salary_from", "salary_to"]]
        # print(f"\n{df.describe()}")

        def print_salary_stat(prefix: str, field_name: str) -> None:
            min_salary = df[field_name].min()
            max_salary = df[field_name].max()
            mean_salary = df[field_name].mean()
            median_salary = df[field_name].median()
            print(
                f"{prefix} min: {min_salary}, max: {max_salary}, mean: {mean_salary:.0f}, median: {median_salary:.0f}"
            )

        print("")
        print_salary_stat("SALARY FROM", "salary_from")
        print_salary_stat("SALARY TO", "salary_to")

    def analyze_key_skills(self, print_amount: int = 10) -> None:
        df: Final = self.working_df

        key_skills_list: list[list[str]] = df["key_skills"].to_list()
        skills_list: Final = [x for elem in key_skills_list for x in elem]
        top_skills: Final = Analyzer.find_top_words_in_list(skills_list)

        print(f"\nThe {print_amount} most frequently used words in Key skills:")
        for key, value in top_skills[:print_amount]:
            print(f"{key[:20]:20} {value}")

    def analyze_description(self, print_amount: int = 15) -> None:
        df: Final = self.working_df

        noise_words: Final = set(["API", "IT", "quot", "and", "or", "I", "it"])

        words_list: Final = " ".join(df["description"].to_list())
        eng_words_list: Final = re.findall("[a-zA-Z_]+", words_list)
        filtered: Final = filter(lambda w: w not in noise_words, eng_words_list)
        top_skills: Final = Analyzer.find_top_words_in_list(filtered)

        print(f"\nThe {print_amount} most frequently used words in Description:")
        for key, value in top_skills[:print_amount]:
            print(f"{key[:20]:20} {value}")

    @staticmethod
    def find_top_words_in_list(lst: list[str]) -> list[tuple[str, int]]:
        words_counter: Final = Counter(lst)
        return sorted(words_counter.items(), key=lambda x: x[1], reverse=True)
