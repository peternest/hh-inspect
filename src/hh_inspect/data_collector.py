import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Final, LiteralString

import requests
from tqdm import tqdm

from hh_inspect.console_printer import ConsolePrinter
from hh_inspect.settings import Settings
from hh_inspect.vacancy import Vacancy, parse_vacancy_data


REQUEST_TIMEOUT: Final = 5
RESPONSE_OK: Final = 200

_API_URL: Final[LiteralString] = "https://api.hh.ru/vacancies/"

logger = logging.getLogger(__name__)
printer = ConsolePrinter()


class DataCollector:
    def __init__(self, settings: Settings) -> None:
        self.query_params = settings.convert_query_to_dict()
        self.query_params["page"] = 0  # to be used later
        self.num_workers = max(settings.general.num_workers, 1)
        self.excluded_companies = settings.filter_after.excluded_companies

    def collect_vacancies(self) -> list[Vacancy]:
        num_pages: Final = self._get_num_pages()
        if num_pages == 0:
            return []
        vacancy_ids: Final = self._build_vacancy_ids(num_pages)
        return self._build_vacancy_list(vacancy_ids)

    def _get_num_pages(self) -> int:
        url: Final = f"{_API_URL}"
        response = requests.get(url, params=self.query_params, timeout=REQUEST_TIMEOUT)
        logger.info(f"Requested '{response.url}'")
        printer.print(f"Requested '{response.url}'")

        if response.status_code != RESPONSE_OK:
            logger.error(f"Code: {response.status_code}")
            logger.error(response.json())
            logger.error(f"Headers: {response.headers}")
            return 0

        found: Final[int] = response.json().get("found", 0)
        num_pages: Final[int] = response.json().get("pages", 0)
        logger.info(f"found: {found}, num_pages: {num_pages}")
        printer.print(f"Found: {found}")
        return num_pages

    def _build_vacancy_ids(self, num_pages: int) -> list[str]:
        url: Final = f"{_API_URL}"
        ids: list[str] = []
        for idx in range(num_pages):
            self.query_params["page"] = idx
            response = requests.get(url, params=self.query_params, timeout=REQUEST_TIMEOUT)
            logger.info(f"Requested '{response.url}'")
            data = response.json()
            if response.status_code != RESPONSE_OK:
                logger.error(f"Code: {response.status_code}")
            ids.extend(x["id"] for x in data["items"])
        return ids

    def _build_vacancy_list(self, vacancy_ids: list[str]) -> list[Vacancy]:
        def company_is_ok(vacancy: Vacancy) -> bool:
            employer_name: Final = vacancy.employer_name.lower()
            return not any(name.lower() in employer_name for name in self.excluded_companies)

        vacancy_list: list[Vacancy] = []
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            vacancy_list.extend(
                [
                    vacancy
                    for vacancy in tqdm(
                        executor.map(self.get_vacancy_or_none, vacancy_ids),
                        desc="Getting data from api.hh.ru",
                        ncols=100,
                        total=len(vacancy_ids),
                    )
                    if vacancy is not None and company_is_ok(vacancy)
                ]
            )
        return vacancy_list

    def get_vacancy_or_none(self, vacancy_id: str) -> Vacancy | None:
        url: Final = f"{_API_URL}{vacancy_id}"
        try:
            response: Final = requests.get(url, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.ConnectTimeout:
            logger.exception("Timeout")
        else:
            vacancy_json: Final[dict[str, Any]] = response.json()
            # print(response.status_code, json.dumps(vacancy_json, ensure_ascii=False, indent=2))  # noqa: ERA001

            if response.status_code == RESPONSE_OK:
                full_vac = parse_vacancy_data(vacancy_json)
                return full_vac.to_basic_vacancy()
        return None
