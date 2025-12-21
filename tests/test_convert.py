import json
from typing import Final

import pytest

from hh_inspect.vacancy import FullVacancy, parse_vacancy_data


@pytest.fixture
def example_vacancy() -> FullVacancy:
    with open("tests/example_vacancy.json", encoding="utf-8") as f:
        vacancy_json: Final = json.load(f)
    return parse_vacancy_data(vacancy_json)


def test_parse_vacancy_data(example_vacancy: FullVacancy) -> None:
    vac = example_vacancy

    assert vac.vacancy_id == "12345"
    assert vac.vacancy_name == "Инженер данных"
    assert vac.area.id == "2"
    assert vac.area.name == "Санкт-Петербург"
    assert vac.area.url == "https://api.hh.ru/areas/2"
    assert vac.salary_range is not None
    assert vac.salary_range.currency == "RUR"
    assert vac.salary_range.frequency == "Раз в месяц"
    assert vac.salary_range.from_ == 100000
    assert vac.salary_range.to == 200000
    assert vac.salary_range.gross is False
    assert vac.salary_range.mode == "За месяц"
    assert vac.type == "Открытая"
    assert vac.description.startswith("<p><em><strong>Приглашаем в команду")
    assert vac.employer is not None
    assert vac.employer.id == "55555"
    assert vac.employer.name == "Рога и копыта"
    assert vac.employer.url == "https://api.hh.ru/employers/55555"
    assert vac.employer.accredited_it_employer is False
    assert vac.employer.trusted is True
    assert vac.experience == "-"
    assert vac.employment == "Полная занятость"
    assert vac.schedule == "Полный день"
    assert vac.key_skills == ["SQL", "Python", "Machine Learning"]
    assert len(vac.professional_roles) == 1
    assert vac.professional_roles[0].id == "96"
    assert vac.professional_roles[0].name == "Программист, разработчик"
    assert vac.work_format == ["ON_SITE", "HYBRID"]
    assert vac.published_at == "2025-05-15T15:15:15+0300"
    assert vac.vacancy_url == "https://hh.ru/vacancy/12345"


def test_convert_to_basic_vacancy(example_vacancy: FullVacancy) -> None:
    vac = example_vacancy.to_basic_vacancy()

    assert vac.vacancy_id == "12345"
    assert vac.vacancy_name == "Инженер данных"
    assert vac.employer_name == "Рога и копыта"
    assert vac.employer_city == "Санкт-Петербург"
    assert vac.accredited_it is False
    assert vac.region == "Санкт-Петербург"
    assert vac.salary_from == 100000
    assert vac.salary_to == 200000
    assert vac.experience == "-"
    assert vac.employment == "Полная занятость"
    assert vac.schedule == "Полный день"
    assert vac.work_format == ["ON_SITE", "HYBRID"]
    assert vac.key_skills == ["SQL", "Python", "Machine Learning"]
    assert vac.description.startswith("<p><em><strong>Приглашаем в команду")
    assert vac.vacancy_url == "https://hh.ru/vacancy/12345"
    assert vac.published_at == "2025-05-15"
