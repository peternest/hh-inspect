from typing import Final

import pytest

from hh_inspect.data_collector import DataCollector
from hh_inspect.settings import GeneralSettings, QuerySettings, Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        query=QuerySettings(
            text="QueryText",
            excluded_text="no_senior",
            search_field="name",
            area=["1", "2"],
            professional_role=["96", "165"],
            salary=100000,
            only_with_salary=True,
            experience=["between1And3", "between3And6"],
            per_page=50,
            order_by="publication_time",
            label="not_from_agency",
        ),
        general=GeneralSettings(
            num_workers=3,
            save_results_to_json=False,
            save_results_to_csv=False,
        ),
    )


def test_data_collector_constuctor(settings: Settings) -> None:
    dc: Final = DataCollector(settings)
    # QuerySettings checks
    assert dc.settings.query.text == "QueryText"
    assert dc.settings.query.excluded_text == "no_senior"
    assert dc.settings.query.search_field == "name"
    assert dc.settings.query.area == ["1", "2"]
    assert dc.settings.query.professional_role == ["96", "165"]
    assert dc.settings.query.salary == 100000
    assert dc.settings.query.only_with_salary is True
    assert dc.settings.query.experience == ["between1And3", "between3And6"]
    assert dc.settings.query.per_page == 50
    assert dc.settings.query.order_by == "publication_time"
    assert dc.settings.query.label == "not_from_agency"
    # GeneralSettings checks
    assert dc.settings.general.num_workers == 3
    assert dc.settings.general.save_results_to_json is False
    assert dc.settings.general.save_results_to_csv is False


@pytest.mark.skip
def test_collect_vacancies(settings: Settings) -> None:
    dc: Final = DataCollector(settings)

    vacancies = dc.collect_vacancies()
    assert len(vacancies) > 0
