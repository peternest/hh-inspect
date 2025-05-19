import logging
from typing import Final, LiteralString

import requests

from hh_inspect.options import Options
from hh_inspect.vacancy import BasicVacancy, parse_vacancy_data


REQUEST_TIMEOUT: Final = 5
RESPONSE_OK: Final = 200

_API_BASE_URL: Final[LiteralString] = "https://api.hh.ru/vacancies/"

logger = logging.getLogger(__name__)


# Query params in Enum or class (per_page, text)!

PER_PAGE: Final[LiteralString] = "per_page"
TEXT: Final[LiteralString] = "text"


class DataCollector:
    def __init__(self, options: Options) -> None:
        self.base_query_string = options.base_query_string

        self.num_workers = 1
        if options.num_workers is not None and options.num_workers > 1:
            self.num_workers = options.num_workers

    def collect_vacancies(self) -> list[BasicVacancy]:
        num_pages: Final = self._get_num_pages()
        if num_pages == 0:
            return []
        vacancy_ids: Final = self._build_vacancy_ids(num_pages)
        return self._build_vacancy_list(vacancy_ids)

    def _build_url(self, per_page: int = 50) -> str:
        additional_params: Final = f"&text=Python&per_page={per_page}"
        final_url: Final = f"{_API_BASE_URL}?{self.base_query_string}{additional_params}"
        logger.info(f"Requesting '{final_url}'")
        return final_url

    def _get_num_pages(self) -> int:
        url: Final = self._build_url()

        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code != RESPONSE_OK:
            logger.error(f"Code: {response.status_code}")
            return 0

        found: Final[int] = response.json().get("found", 0)
        num_pages: Final[int] = response.json().get("pages", 0)
        logger.info(f"found: {found}, num_pages: {num_pages}")
        print(f"Found: {found}")
        return num_pages

    def _build_vacancy_ids(self, num_pages: int) -> list[str]:
        url: Final = self._build_url()

        ids: list[str] = []
        for idx in range(num_pages + 1):
            response = requests.get(url, {"page": idx}, timeout=REQUEST_TIMEOUT)
            data = response.json()
            if response.status_code != RESPONSE_OK:
                logger.error(f"Code: {response.status_code}")
            if "items" not in data:
                break
            ids.extend(x["id"] for x in data["items"])
        return ids

    def _build_vacancy_list(self, vacancy_ids: list[str], max_limit: int = 10) -> list[BasicVacancy]:
        vacancy_list: list[BasicVacancy] = []
        for vacancy_id in vacancy_ids[:max_limit]:
            vacancy = self.get_vacancy_or_404(vacancy_id)
            if vacancy is not None:
                vacancy_list.append(vacancy)
        return vacancy_list

    @staticmethod
    def get_vacancy_or_404(vacancy_id: str) -> BasicVacancy | None:
        url: Final = f"{_API_BASE_URL}{vacancy_id}"
        response: Final = requests.get(url, timeout=REQUEST_TIMEOUT)
        vacancy_json: Final = response.json()
        # print(response.status_code, json.dumps(vacancy_json, ensure_ascii=False, indent=2))  # noqa: ERA001

        if response.status_code == RESPONSE_OK:
            full_vac = parse_vacancy_data(vacancy_json)
            vacancy = full_vac.to_basic_vacancy()
            print(f"{vacancy}")
            return vacancy
        return None


if __name__ == "__main__":
    start = 120596730
    for n in range(10):
        DataCollector.get_vacancy_or_404(str(start + n))
