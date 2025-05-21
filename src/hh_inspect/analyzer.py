import pandas as pd
import logging

from typing import Final

from hh_inspect.data_collector import Vacancy


logger = logging.getLogger(__name__)


class Analyzer:
    def __init__(self, vacancies: list[Vacancy]) -> None:
        self.vacancies: Final = vacancies
        self.working_df: Final = pd.DataFrame([vars(v) for v in self.vacancies])
        print(self.working_df.head())

    def save_vacancies_to_csv(self, filename: str) -> None:
        logger.info(f"Saving vacancies to '{filename}'...")
        self.working_df.to_csv("../data/vacancies.csv", index=False)
