from typing import Final

import pytest

from hh_inspect.data_collector import DataCollector
from hh_inspect.options import Options


@pytest.fixture
def options() -> Options:
    return Options(
        query_params={"text": "TestQuery"},
        num_workers=3,
    )


def test_data_collector_constuctor(options: Options) -> None:
    dc: Final = DataCollector(options)
    assert dc.query_params.get("text") == "TestQuery"
    assert dc.num_workers == 3


@pytest.mark.skip
def test_collect_vacancies(options: Options) -> None:
    dc: Final = DataCollector(options)

    vacancies = dc.collect_vacancies(
        query_params={"text": "Rust", "area": 2, "per_page": 10},
    )
    assert len(vacancies) > 0
