# pyright: reportUnknownMemberType = false
# pyright: reportUnknownVariableType = false

import pytest

from hh_inspect.analyzer import Analyzer
from hh_inspect.vacancy import Vacancy


def create_vacancy(  # noqa: PLR0913
    vacancy_id: str,
    region: str = "TestRegion",
    employer_name: str = "TestCompany",
    employer_city: str = "City1",
    accredited_it: bool = False,
    vacancy_name: str = "TestVacancy",
    salary_from: int = 0,
    salary_to: int = 0,
    experience: str = "from1to3",
    employment: str = "full",
    schedule: str = "remote",
    key_skills: list[str] = [],  # noqa: B006
    description: str = "",
    vacancy_url: str = "http://example.com/url",
    published_at: str = "2025-01-01",
) -> Vacancy:
    return Vacancy(
        vacancy_id=vacancy_id,
        region=region,
        employer_name=employer_name,
        employer_city=employer_city,
        accredited_it=accredited_it,
        vacancy_name=vacancy_name,
        salary_from=salary_from,
        salary_to=salary_to,
        experience=experience,
        employment=employment,
        schedule=schedule,
        key_skills=key_skills,
        description=description,
        vacancy_url=vacancy_url,
        published_at=published_at,
    )


def test_calc_salary_stats_from() -> None:
    vacancies = [
        create_vacancy("1", salary_from=100_000),
        create_vacancy("2", salary_from=150_000),
        create_vacancy("3", salary_from=200_000),
    ]
    analyzer = Analyzer(vacancies)
    stats = analyzer.get_salary_stats_for_field("salary_from")
    assert stats["min"] == 100_000
    assert stats["max"] == 200_000
    assert stats["mean"] == pytest.approx((100_000 + 150_000 + 200_000) / 3)
    assert stats["median"] == 150_000


def test_calc_salary_stats_to() -> None:
    vacancies = [
        create_vacancy("1", salary_to=120_000),
        create_vacancy("2", salary_to=180_000),
        create_vacancy("3", salary_to=210_000),
    ]
    analyzer = Analyzer(vacancies)
    stats = analyzer.get_salary_stats_for_field("salary_to")
    assert stats["min"] == 120_000
    assert stats["max"] == 210_000
    assert stats["mean"] == pytest.approx((120_000 + 180_000 + 210_000) / 3)
    assert stats["median"] == 180_000


def test_calc_salary_stats_from_ignores_zero() -> None:
    vacancies = [
        create_vacancy("1", salary_from=0),
        create_vacancy("2", salary_from=150_000),
        create_vacancy("3", salary_from=200_000),
    ]
    analyzer = Analyzer(vacancies)
    stats = analyzer.get_salary_stats_for_field("salary_from")
    assert stats["min"] == 150_000
    assert stats["max"] == 200_000
    assert stats["mean"] == pytest.approx((150_000 + 200_000) / 2)
    assert stats["median"] == 175_000


def test_calc_salary_stats_to_ignores_zero() -> None:
    vacancies = [
        create_vacancy("1", salary_to=120_000),
        create_vacancy("2", salary_to=0),
        create_vacancy("3", salary_to=210_000),
    ]
    analyzer = Analyzer(vacancies)
    stats = analyzer.get_salary_stats_for_field("salary_to")
    assert stats["min"] == 120_000
    assert stats["max"] == 210_000
    assert stats["mean"] == pytest.approx((120_000 + 210_000) / 2)
    assert stats["median"] == 165_000


def test_get_top_key_skills_single_skill() -> None:
    vacancies = [
        create_vacancy("1", key_skills=["Python"]),
        create_vacancy("2", key_skills=["Python"]),
        create_vacancy("3", key_skills=["Python"]),
    ]
    analyzer = Analyzer(vacancies)
    top_skills = analyzer.get_top_key_skills()
    assert top_skills == [("Python", 3)]


def test_get_top_key_skills_multiple_skills() -> None:
    vacancies = [
        create_vacancy("1", key_skills=["Python", "SQL"]),
        create_vacancy("2", key_skills=["Python", "Pandas"]),
        create_vacancy("3", key_skills=["SQL", "Pandas"]),
    ]
    analyzer = Analyzer(vacancies)
    top_skills = analyzer.get_top_key_skills()
    assert ("Python", 2) in top_skills
    assert ("SQL", 2) in top_skills
    assert ("Pandas", 2) in top_skills
    assert len(top_skills) == 3


def test_get_top_key_skills_with_empty_lists() -> None:
    vacancies = [
        create_vacancy("1", key_skills=[]),
        create_vacancy("2", key_skills=["Python"]),
        create_vacancy("3", key_skills=[]),
    ]
    analyzer = Analyzer(vacancies)
    top_skills = analyzer.get_top_key_skills()
    assert top_skills == [("Python", 1)]


def test_get_top_key_skills_no_skills() -> None:
    vacancies = [
        create_vacancy("1", key_skills=[]),
        create_vacancy("2", key_skills=[]),
    ]
    analyzer = Analyzer(vacancies)
    top_skills = analyzer.get_top_key_skills()
    assert top_skills == []


def test_get_top_key_skills_ordering() -> None:
    vacancies = [
        create_vacancy("1", key_skills=["Python", "SQL"]),
        create_vacancy("2", key_skills=["Python"]),
        create_vacancy("3", key_skills=["SQL", "Python"]),
        create_vacancy("4", key_skills=["Pandas", "Django"]),
        create_vacancy("5", key_skills=["Django"]),
    ]
    analyzer = Analyzer(vacancies)
    top_skills = analyzer.get_top_key_skills()
    assert top_skills[0] == ("Python", 3)
    assert top_skills[1][1] == 2
    assert top_skills[2][1] == 2
    assert top_skills[3] == ("Pandas", 1)


def test_get_top_description_words_basic() -> None:
    vacancies = [
        create_vacancy("1", description="Python SQL Python"),
        create_vacancy("2", description="SQL Pandas"),
        create_vacancy("3", description="Python Pandas"),
    ]
    analyzer = Analyzer(vacancies)
    top_words = analyzer.get_top_description_words()
    assert ("Python", 3) in top_words
    assert ("SQL", 2) in top_words
    assert ("Pandas", 2) in top_words


def test_get_top_description_words_filters_noise() -> None:
    vacancies = [
        create_vacancy("1", description="Python API IT and or"),
        create_vacancy("2", description="API Python"),
    ]
    analyzer = Analyzer(vacancies)
    top_words = analyzer.get_top_description_words()
    # Only Python should remain, API, IT, and, or are noise
    assert top_words == [("Python", 2)]


def test_get_top_description_words_empty() -> None:
    vacancies = [
        create_vacancy("1", description=""),
        create_vacancy("2", description=""),
    ]
    analyzer = Analyzer(vacancies)
    top_words = analyzer.get_top_description_words()
    assert top_words == []


def test_get_top_description_words_case_sensitive() -> None:
    vacancies = [
        create_vacancy("1", description="python Python PYTHON"),
        create_vacancy("2", description="PyThOn"),
    ]
    analyzer = Analyzer(vacancies)
    top_words = analyzer.get_top_description_words()
    assert ("python", 1) in top_words
    assert ("Python", 1) in top_words
    assert ("PYTHON", 1) in top_words
    assert ("PyThOn", 1) in top_words


def test_get_top_description_words_with_punctuation() -> None:
    vacancies = [
        create_vacancy("1", description="Python, SQL! Pandas?"),
        create_vacancy("2", description="Python; Pandas."),
    ]
    analyzer = Analyzer(vacancies)
    top_words = analyzer.get_top_description_words()
    assert ("Python", 2) in top_words
    assert ("SQL", 1) in top_words
    assert ("Pandas", 2) in top_words
