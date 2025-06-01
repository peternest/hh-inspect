import pytest
from pydantic import ValidationError

from hh_inspect.settings import FilterAfterSettings, GeneralSettings, QuerySettings, Settings


def test_default_settings() -> None:
    st = Settings()

    assert st.query.text == "Python"
    assert st.query.salary is None
    assert st.query.experience is None
    assert st.query.label is None
    assert st.query.search_field == ["name", "company_name", "description"]
    assert st.query.area == ["113"]
    assert st.filter_after.excluded_companies == []
    assert st.general.num_workers == 1
    assert st.general.save_results_to_csv is True
    assert st.general.save_results_to_json is True


def test_partial_query_settings() -> None:
    st = Settings(query=QuerySettings(text="Go"))
    assert st.query.text == "Go"
    assert st.general.num_workers == 1  # default


def test_partial_general_settings() -> None:
    st = Settings(general=GeneralSettings(num_workers=5))
    assert st.query.text == "Python"  # default
    assert st.general.num_workers == 5


def test_invalid_salary_type() -> None:
    with pytest.raises(ValidationError):
        QuerySettings(salary="not_a_number")  # type: ignore  # noqa: PGH003


def test_list_fields() -> None:
    st = QuerySettings(area=["1", "2", "3"], professional_role=["96", "165"])
    assert st.area == ["1", "2", "3"]
    assert st.professional_role == ["96", "165"]


def test_to_dict_method() -> None:
    st = QuerySettings(text="Test", area=["1"])
    d = st.to_dict()
    assert d["text"] == "Test"
    assert d["area"] == ["1"]


def test_regular_settings() -> None:
    st = Settings(
        query=QuerySettings(
            text="QueryText",
            excluded_text="no_senior",
            search_field=["name", "company"],
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
            save_results_to_csv=True,
        ),
    )

    assert st.query.text == "QueryText"
    assert st.query.excluded_text == "no_senior"
    assert st.query.search_field == ["name", "company"]
    assert st.query.area == ["1", "2"]
    assert st.query.professional_role == ["96", "165"]
    assert st.query.salary == 100000
    assert st.query.only_with_salary is True
    assert st.query.experience == ["between1And3", "between3And6"]
    assert st.query.per_page == 50
    assert st.query.order_by == "publication_time"
    assert st.query.label == "not_from_agency"

    assert st.filter_after.excluded_companies == ["Альфа", "Бета"]

    assert st.general.num_workers == 3
    assert st.general.print_output_to_console is False
    assert st.general.save_results_to_json is False
    assert st.general.save_results_to_csv is True
