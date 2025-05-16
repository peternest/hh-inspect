import re
from dataclasses import dataclass
from typing import Any, Final, LiteralString
from urllib.parse import urlencode

import requests

from hh_inspect.options import Options


REQUEST_TIMEOUT: Final = 5


@dataclass
class SalaryInfo:
    is_salary: bool = False
    salary_from: int = 0
    salary_to: int = 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.salary_from}, {self.salary_to})"


@dataclass
class Vacancy:
    vacancy_id: str
    vacancy_name: str
    employer_name: str
    salary: SalaryInfo
    experience: str
    schedule: str
    key_skills: list[str]
    description: str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.vacancy_id}, {self.vacancy_name}, {self.employer_name}, {self.salary})"


class DataCollector:
    _API_BASE_URL: Final[LiteralString] = "https://api.hh.ru/vacancies/"
    _DICT_KEYS: Final = (
        "Ids",
        "Employer",
        "Name",
        "Salary",
        "From",
        "To",
        "Experience",
        "Schedule",
        "Keys",
        "Description",
    )
    _TAX_RATE: Final = 0.13

    def __init__(self, options: Options) -> None:
        self.query_params = options.query_params

        self.num_workers = 1
        if options.num_workers is not None and options.num_workers > 1:
            self.num_workers = options.num_workers

        self.exchange_rates = options.exchange_rates

    def collect_vacancies(self) -> list[Vacancy]:
        url_params: Final = self._encode_query_for_url(self.query_params)

        target_url: Final = self._API_BASE_URL + "?" + url_params
        num_pages: Final = requests.get(target_url, timeout=REQUEST_TIMEOUT).json()["pages"]

        ids: list[str] = []
        for idx in range(num_pages + 1):
            response = requests.get(target_url, {"page": idx}, timeout=REQUEST_TIMEOUT)
            data = response.json()
            if "items" not in data:
                break
            ids.extend(x["id"] for x in data["items"])

        vacancy_list: list[Vacancy] = []
        for vacancy_id in ids:
            vacancy = self.get_vacancy(vacancy_id)
            print(vacancy)
            vacancy_list.append(vacancy)

        return vacancy_list

    def get_vacancy(self, vacancy_id: str) -> Vacancy:
        url = f"{self._API_BASE_URL}{vacancy_id}"
        vacancy = requests.get(url, timeout=REQUEST_TIMEOUT).json()
        # print(json.dumps(vacancy, ensure_ascii=False, indent=2))  # noqa: ERA001

        return Vacancy(
            vacancy_id,
            vacancy.get("name", ""),
            vacancy.get("employer", {}).get("name", ""),
            self._calc_salary_info(vacancy),
            vacancy.get("experience", {}).get("name", ""),
            vacancy.get("schedule", {}).get("name", ""),
            [el["name"] for el in vacancy.get("key_skills", [])],
            self.remove_html_tags(vacancy.get("description", "")),
        )

    def _calc_salary_info(self, vacancy: Any) -> SalaryInfo:
        salary: Final = vacancy.get("salary")
        if salary is None:
            return SalaryInfo()

        currency: Final[str] = salary.get("currency", "")
        is_gross: Final = salary.get("gross")
        gross_coef = (1 - self._TAX_RATE) if is_gross else 1

        # print(salary)
        salary_from = salary.get("from") if salary.get("from") is not None else 0
        salary_to = salary.get("to") if salary.get("to") is not None else salary_from
        # print(salary_from, salary_to)

        salary_from = int(gross_coef * salary_from / self.exchange_rates[currency])
        salary_to = int(gross_coef * salary_to / self.exchange_rates[currency])
        return SalaryInfo(True, salary_from, salary_to)

    @staticmethod
    def remove_html_tags(html_text: str) -> str:
        pattern: Final = re.compile("<.*?>")
        return re.sub(pattern, "", html_text)

    @staticmethod
    def _encode_query_for_url(query: dict[str, Any] | None) -> str:
        if query is None:
            return ""

        if False:  # "professional_roles" in query:
            query_copy = query.copy()

            roles = "&".join([f"professional_role={r}" for r in query_copy.pop("professional_roles")])

            x = roles + (f"&{urlencode(query_copy)}" if len(query_copy) > 0 else "")
            print(x)
            return x

        encoded_query: Final = urlencode(query)
        print(f"[DEBUG] {encoded_query}")
        return encoded_query
