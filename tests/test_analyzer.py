# pyright: reportUnknownMemberType = false
# pyright: reportUnknownVariableType = false

import pytest

from hh_inspect.analyzer import Analyzer
from hh_inspect.vacancy import Vacancy


@pytest.fixture
def vacancies() -> list[Vacancy]:
    return [
        Vacancy(
            vacancy_id="1",
            region="Region1",
            employer_name="CompanyA",
            employer_city="City1",
            accredited_it=False,
            vacancy_name="Dev",
            salary_from=100_000,
            salary_to=120_000,
            experience="between1And3",
            employment="full",
            schedule="remote",
            key_skills=["Python"],
            description="desc1",
            vacancy_url="url1",
            published_at="2025-01-01",
        ),
        Vacancy(
            vacancy_id="2",
            region="Region2",
            employer_name="CompanyB",
            employer_city="City2",
            accredited_it=False,
            vacancy_name="Dev",
            salary_from=150_000,
            salary_to=180_000,
            experience="between1And3",
            employment="full",
            schedule="remote",
            key_skills=["SQL"],
            description="desc2",
            vacancy_url="url2",
            published_at="2025-01-02",
        ),
        Vacancy(
            vacancy_id="3",
            region="Region3",
            employer_name="CompanyC",
            employer_city="City3",
            accredited_it=False,
            vacancy_name="Dev",
            salary_from=200_000,
            salary_to=210_000,
            experience="between1And3",
            employment="full",
            schedule="remote",
            key_skills=["Pandas"],
            description="desc3",
            vacancy_url="url3",
            published_at="2025-01-03",
        ),
    ]


@pytest.fixture
def vacancies_with_zeroes() -> list[Vacancy]:
    return [
        Vacancy(
            vacancy_id="1",
            region="Region1",
            employer_name="CompanyA",
            employer_city="City1",
            accredited_it=False,
            vacancy_name="Dev",
            salary_from=0,
            salary_to=120_000,
            experience="between1And3",
            employment="full",
            schedule="remote",
            key_skills=["Python"],
            description="desc1",
            vacancy_url="url1",
            published_at="2025-01-01",
        ),
        Vacancy(
            vacancy_id="2",
            region="Region2",
            employer_name="CompanyB",
            employer_city="City2",
            accredited_it=False,
            vacancy_name="Dev",
            salary_from=150_000,
            salary_to=0,
            experience="between1And3",
            employment="full",
            schedule="remote",
            key_skills=["SQL"],
            description="desc2",
            vacancy_url="url2",
            published_at="2025-01-02",
        ),
        Vacancy(
            vacancy_id="3",
            region="Region3",
            employer_name="CompanyC",
            employer_city="City3",
            accredited_it=False,
            vacancy_name="Dev",
            salary_from=200_000,
            salary_to=210_000,
            experience="between1And3",
            employment="full",
            schedule="remote",
            key_skills=["Pandas"],
            description="desc3",
            vacancy_url="url3",
            published_at="2025-01-03",
        ),
    ]


def test_calc_salary_stats_from(vacancies: list[Vacancy]) -> None:
    analyzer = Analyzer(vacancies)
    stats = analyzer.calc_salary_stats("salary_from")
    assert stats["min"] == 100_000
    assert stats["max"] == 200_000
    assert stats["mean"] == pytest.approx((100_000 + 150_000 + 200_000) / 3)
    assert stats["median"] == 150_000


def test_calc_salary_stats_to(vacancies: list[Vacancy]) -> None:
    analyzer = Analyzer(vacancies)
    stats = analyzer.calc_salary_stats("salary_to")
    assert stats["min"] == 120_000
    assert stats["max"] == 210_000
    assert stats["mean"] == pytest.approx((120_000 + 180_000 + 210_000) / 3)
    assert stats["median"] == 180_000


def test_calc_salary_stats_from_ignores_zero(vacancies_with_zeroes: list[Vacancy]) -> None:
    analyzer = Analyzer(vacancies_with_zeroes)
    stats = analyzer.calc_salary_stats("salary_from")
    assert stats["min"] == 150_000
    assert stats["max"] == 200_000
    assert stats["mean"] == pytest.approx((150_000 + 200_000) / 2)
    assert stats["median"] == 175_000


def test_calc_salary_stats_to_ignores_zero(vacancies_with_zeroes: list[Vacancy]) -> None:
    analyzer = Analyzer(vacancies_with_zeroes)
    stats = analyzer.calc_salary_stats("salary_to")
    assert stats["min"] == 120_000
    assert stats["max"] == 210_000
    assert stats["mean"] == pytest.approx((120_000 + 210_000) / 2)
    assert stats["median"] == 165_000
