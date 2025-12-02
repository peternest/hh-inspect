from typing import Final

import pytest

from hh_inspect.data_collector import DataCollector
from hh_inspect.settings import FilterAfterSettings, GeneralSettings, QuerySettings, Settings
from hh_inspect.vacancy import Vacancy


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
            print_output_to_console=False,
            save_results_to_json=False,
            save_results_to_csv=False,
        ),
    )


def test_data_collector_constructor(settings: Settings) -> None:
    dc = DataCollector(settings)

    assert dc.query_params == {
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


def test_collect_vacancies_no_pages(monkeypatch: pytest.MonkeyPatch, settings: Settings) -> None:
    dc = DataCollector(settings)

    def patch_num_pages() -> int:
        return 0

    monkeypatch.setattr(dc, "_get_num_pages", patch_num_pages)
    vacancies = dc.collect_vacancies()
    assert vacancies == []


def test_collect_vacancies_flow(monkeypatch: pytest.MonkeyPatch, settings: Settings) -> None:
    dc = DataCollector(settings)

    def patch_num_pages() -> int:
        return 2

    def patch_vacancy_ids(num_pages: int) -> list[str]:
        return ["id1", "id2"]

    def patch_vacancy_list(vacancy_ids: list[str]) -> list[str]:  # Change return type list[Vacancy] -> list[str]
        return ["vac1", "vac2"]

    monkeypatch.setattr(dc, "_get_num_pages", patch_num_pages)
    monkeypatch.setattr(dc, "_build_vacancy_ids", patch_vacancy_ids)
    monkeypatch.setattr(dc, "build_vacancy_list", patch_vacancy_list)
    vacancies = dc.collect_vacancies()
    assert vacancies == ["vac1", "vac2"]


def test_get_vacancy_returns_none(monkeypatch: pytest.MonkeyPatch, settings: Settings) -> None:
    """Check that errors are handled gracefully."""
    dc = DataCollector(settings)

    def patch_num_pages() -> int:
        return 1

    def patch_vacancy_ids(num_pages: int) -> list[str]:
        return ["id1"]

    def patch_get_vacancy(vacancy_id: str) -> None:
        return None

    monkeypatch.setattr(dc, "_get_num_pages", patch_num_pages)
    monkeypatch.setattr(dc, "_build_vacancy_ids", patch_vacancy_ids)
    monkeypatch.setattr(dc, "get_vacancy_or_none", patch_get_vacancy)
    vacancies = dc.collect_vacancies()
    assert vacancies == []


def test_excluded_company_filtering(monkeypatch: pytest.MonkeyPatch, settings: Settings) -> None:
    dc = DataCollector(settings)
    dc.excluded_companies = ["Bad Company"]

    # Create two vacancies, one from an excluded company
    vac1 = Vacancy(
        vacancy_id="id1",
        region="Region1",
        employer_name="Good Company",
        employer_city="City1",
        accredited_it=False,
        vacancy_name="Developer",
        salary_from=100000,
        salary_to=120000,
        experience="between1And3",
        employment="full",
        schedule="remote",
        work_format=[],
        key_skills=["Python", "SQL"],
        description="Some description",
        vacancy_url="http://example.com/id1",
        published_at="2025-01-01",
    )

    vac2 = Vacancy(
        vacancy_id="id2",
        region="Region2",
        employer_name="Bad Company",
        employer_city="City2",
        accredited_it=False,
        vacancy_name="Analyst",
        salary_from=90000,
        salary_to=110000,
        experience="between1And3",
        employment="full",
        schedule="office",
        work_format=[],
        key_skills=["Excel"],
        description="Other description",
        vacancy_url="http://example.com/id2",
        published_at="2025-01-02",
    )

    def patch_num_pages() -> int:
        return 2

    def patch_vacancy_ids(num_pages: int) -> list[str]:
        return ["id1", "id2"]

    def patch_get_vacancy(vacancy_id: str) -> Vacancy | None:
        return vac1 if vacancy_id == "id1" else vac2

    monkeypatch.setattr(dc, "_get_num_pages", patch_num_pages)
    monkeypatch.setattr(dc, "_build_vacancy_ids", patch_vacancy_ids)
    monkeypatch.setattr(dc, "get_vacancy_or_none", patch_get_vacancy)

    vac_list: Final = dc.build_vacancy_list(["id1", "id2"])
    assert all("badcompany" not in vac.employer_name for vac in vac_list)
