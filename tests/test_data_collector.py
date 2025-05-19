from typing import Final

import pytest

from hh_inspect.data_collector import DataCollector
from hh_inspect.options import Options


@pytest.fixture
def options() -> Options:
    return Options(
        base_query_string="QueryString", num_workers=3, save_results_to_json=False, save_results_to_csv=False
    )


def test_data_collector_constuctor(options: Options) -> None:
    dc: Final = DataCollector(options)
    assert dc.base_query_string == "QueryString"
    assert dc.num_workers == 3


@pytest.mark.skip
def test_collect_vacancies(options: Options) -> None:
    dc: Final = DataCollector(options)

    vacancies = dc.collect_vacancies()
    assert len(vacancies) > 0
