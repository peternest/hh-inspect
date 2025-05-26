from typing import Final

import pytest

from hh_inspect.data_collector import DataCollector
from hh_inspect.settings import FilterAfterSettings, GeneralSettings, QuerySettings, Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        query=QuerySettings(
            text="QueryText",
            excluded_text="no_senior",
            search_field=["name"],
            area=["1", "2"],
            professional_role=["96", "165"],
            salary=100000,
            only_with_salary=True,
            experience=["between1And3", "between3And6"],
            per_page=50,
            order_by="publication_time",
            label="not_from_agency",
        ),
        filter_after=FilterAfterSettings(excluded_companies=["Альфа", "Бета"]),
        general=GeneralSettings(
            num_workers=3,
            save_results_to_json=False,
            save_results_to_csv=False,
        ),
    )


def test_data_collector_constructor(settings: Settings) -> None:
    dc: Final = DataCollector(settings)

    assert dc.query_params == {
        "page": 0,
        "text": "QueryText",
        "excluded_text": "no_senior",
        "search_field": ["name"],
        "area": ["1", "2"],
        "professional_role": ["96", "165"],
        "salary": 100000,
        "only_with_salary": True,
        "experience": ["between1And3", "between3And6"],
        "per_page": 50,
        "order_by": "publication_time",
        "label": "not_from_agency",
    }
    assert dc.excluded_companies == ["Альфа", "Бета"]
    assert dc.num_workers == 3


@pytest.mark.skip
def test_collect_vacancies(settings: Settings) -> None:
    dc: Final = DataCollector(settings)

    vacancies = dc.collect_vacancies()
    assert len(vacancies) > 0
