from hh_inspect.settings import GeneralSettings, QuerySettings, Settings


def test_default_settings() -> None:
    st = Settings()

    assert st.query.text == "Python"
    assert st.query.salary == 100000
    assert st.query.experience is None
    assert st.query.label is None
    assert st.general.num_workers == 1


def test_regular_settings() -> None:
    st = Settings(
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

    assert st.query.text == "QueryText"
    assert st.query.excluded_text == "no_senior"
    assert st.query.search_field == "name"
    assert st.query.area == ["1", "2"]
    assert st.query.professional_role == ["96", "165"]
    assert st.query.salary == 100000
    assert st.query.only_with_salary is True
    assert st.query.experience == ["between1And3", "between3And6"]
    assert st.query.per_page == 50
    assert st.query.order_by == "publication_time"
    assert st.query.label == "not_from_agency"

    assert st.general.num_workers == 3
    assert st.general.save_results_to_json is False
    assert st.general.save_results_to_csv is False
