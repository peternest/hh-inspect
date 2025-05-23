import pandas as pd
import logging
from typing import Final
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

    def analyze(self) -> None:
        df: Final = self.working_df[["employer_name", "vacancy_name", "salary_from", "salary_to"]]
        print(df)
        # print(df.describe())

        print(f"\nNumber of vacancies: {len(df)}")

        max_value = df["salary_to"].max()
        print(f"\nMax salary: {max_value}")
        rows_with_max = df.loc[df["salary_to"] == max_value]
        print(rows_with_max)

        df_filtered = df[df["salary_from"] > 0]
        min_value = df_filtered["salary_from"].min()
        print(f"\nMin salary: {min_value}")
        rows_with_min = df_filtered.loc[df_filtered["salary_from"] == min_value]
        print(rows_with_min)
