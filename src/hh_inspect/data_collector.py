import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Final

import requests
from tqdm import tqdm

from hh_inspect.console_printer import ConsolePrinter
from hh_inspect.settings import Settings
from hh_inspect.vacancy import FullVacancy, Vacancy, parse_vacancy_data


REQUEST_TIMEOUT: Final = 5
RESPONSE_OK: Final = 200

_API_URL: Final = "https://api.hh.ru/vacancies/"

logger = logging.getLogger(__name__)
printer = ConsolePrinter()


class DataCollector:
    def __init__(self, settings: Settings) -> None:
        self.query_params = settings.convert_query_to_dict()
        self.num_workers = max(settings.general.num_workers, 1)
        self.excluded_companies = settings.filter_after.excluded_companies

    def collect_vacancies(self) -> list[Vacancy]:
        num_pages = self._get_num_pages()
        if num_pages == 0:
            return []
        vacancy_ids = self._build_vacancy_ids(num_pages)
        return self.build_vacancy_list(vacancy_ids)

    def _get_num_pages(self) -> int:
        url: Final = f"{_API_URL}"
        response = requests.get(url, params=self.query_params, timeout=REQUEST_TIMEOUT)
        logger.info(f"Requested '{response.url}'")
        # printer.print(f"Requested '{response.url}'")  # noqa: ERA001

        if response.status_code != RESPONSE_OK:
            logger.error(f"Response code: {response.status_code}")
            logger.error(response.json())
            logger.error(f"Headers: {response.headers}")
            printer.print(f"Response code: {response.status_code}")
            printer.print(response.json())
            return 0

        found: Final[int] = response.json().get("found", 0)
        num_pages: Final[int] = response.json().get("pages", 0)
        logger.info(f"found: {found}, num_pages: {num_pages}")
        printer.print(f"Found: {found}")
        return num_pages

    def _build_vacancy_ids(self, num_pages: int) -> list[str]:
        url = f"{_API_URL}"
        ids: list[str] = []
        for idx in range(num_pages):
            params = self.query_params.copy()
            params["page"] = idx
            try:
                response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                logger.info(f"Requested '{response.url}'")
                data = response.json()
                ids.extend(x["id"] for x in data["items"])
            except requests.exceptions.HTTPError:
                logger.exception(f"Error fetching page {idx}")
        return ids

    def build_vacancy_list(self, vacancy_ids: list[str]) -> list[Vacancy]:
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
                    if vacancy is not None
                ]
            )
        return vacancy_list

    def get_vacancy_or_none(self, vacancy_id: str) -> Vacancy | None:
        def get_employer_name(vac: FullVacancy) -> str:
            if vac.employer is not None and vac.employer.name is not None:
                return vac.employer.name
            return ""

        def is_excluded(vac: FullVacancy) -> bool:
            employer_name = get_employer_name(vac).lower()
            return any(name.lower() in employer_name for name in self.excluded_companies)

        url = f"{_API_URL}{vacancy_id}"
        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.ConnectTimeout:
            logger.exception("Timeout")
        else:
            vacancy_json: dict[str, Any] = response.json()
            # print(response.status_code, json.dumps(vacancy_json, ensure_ascii=False, indent=2))  # noqa: ERA001

            if response.status_code == RESPONSE_OK:
                full_vac = parse_vacancy_data(vacancy_json)
                excluded = is_excluded(full_vac)
                return full_vac.to_basic_vacancy(excluded)
        return None
