import logging
from typing import Any, Final, LiteralString
from urllib.parse import urlencode

import requests

from hh_inspect.options import Options
from hh_inspect.vacancy import BasicVacancy, parse_vacancy_data


REQUEST_TIMEOUT: Final = 5
RESPONSE_OK: Final = 200

_API_BASE_URL: Final[LiteralString] = "https://api.hh.ru/vacancies/"

logger = logging.getLogger(__name__)

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


class DataCollector:
    def __init__(self, options: Options) -> None:
        self.query_params = options.query_params

        self.num_workers = 1
        if options.num_workers is not None and options.num_workers > 1:
            self.num_workers = options.num_workers

    def collect_vacancies(self) -> list[BasicVacancy]:
        url_params: Final = self._encode_query_for_url(self.query_params)
        url: Final = f"{_API_BASE_URL}?{url_params}"

        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code != RESPONSE_OK:
            logger.error(f"Code: {response.status_code}, url: {url_params}")
            return []

        num_pages = response.json()["pages"]
        # build vacancy ids
        ids: list[str] = []
        for idx in range(num_pages + 1):
            response = requests.get(url, {"page": idx}, timeout=REQUEST_TIMEOUT)
            data = response.json()
            if "items" not in data:
                break
            ids.extend(x["id"] for x in data["items"])

        vacancy_list: list[BasicVacancy] = []
        for vacancy_id in ids:
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
            print(f"{full_vac}\n")
            # print(f"{vacancy}\n")  # noqa: ERA001
            return vacancy
        return None

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
        logger.debug(f"Encoded query: {encoded_query}")
        return encoded_query


if __name__ == "__main__":
    start = 120596730
    for n in range(10):
        DataCollector.get_vacancy_or_404(str(start + n))
