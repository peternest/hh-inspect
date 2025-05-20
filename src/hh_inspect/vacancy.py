import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Final

from hh_inspect.options import EXCHANGE_RATES
from hh_inspect.utils import remove_html_tags


_TAX_RATE: Final = 0.13

logger = logging.getLogger(__name__)


# Some optional fields in models are marked according to specification at
# https://api.hh.ru/openapi/redoc#tag/Vakansii/operation/get-vacancy


@dataclass
class Vacancy:
    """Only necessary fields from FullVacancy for further analysis.

    salary_from, salary_to = values are after taxes (0 means None)
    """

    vacancy_id: str
    vacancy_name: str
    employer_name: str
    accredited_it: bool
    region: str
    salary_from: int
    salary_to: int
    experience: str
    employment: str
    schedule: str
    key_skills: list[str]
    description: str
    vacancy_url: str

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"{self.vacancy_id}, {self.vacancy_name}, {self.employer_name}, "
            f"({self.salary_from}, {self.salary_to})"
            f")"
        )


@dataclass
class Area:
    id: str
    name: str
    url: str


@dataclass
class Employer:
    id: str
    name: str
    trusted: bool
    accredited_it_employer: bool
    url: str


@dataclass
class ProfessionalRole:
    id: str
    name: str


@dataclass
class SalaryRange:
    currency: str
    frequency: str  # original frequency.name
    from_: int | None = field(metadata={"name": "from"})
    to: int | None
    gross: bool
    mode: str  # original mode.name


@dataclass
class FullVacancy:
    """Most important vacancy fields from HH API."""

    vacancy_id: str  # original 'id'
    vacancy_name: str  # original 'name'
    employer: Employer | None
    area: Area
    employment: str
    experience: str
    key_skills: list[str]
    professional_roles: list[ProfessionalRole]
    salary_range: SalaryRange | None
    schedule: str
    description: str = field(repr=False)
    type: str
    premium: bool
    published_at: str
    vacancy_url: str = field(repr=False)  # original 'alternate_url'

    def to_basic_vacancy(self) -> Vacancy:
        salary_from, salary_to = _extract_and_calc_salary(self.salary_range)

        return Vacancy(
            vacancy_id=self.vacancy_id,
            vacancy_name=self.vacancy_name,
            employer_name=(self.employer.name if self.employer is not None else ""),
            accredited_it=(self.employer.accredited_it_employer if self.employer is not None else False),
            region=self.area.name,
            salary_from=salary_from,
            salary_to=salary_to,
            experience=self.experience,
            employment=self.employment,
            schedule=self.schedule,
            key_skills=self.key_skills,
            description=remove_html_tags(self.description),
            vacancy_url=self.vacancy_url,
        )


def parse_vacancy_data(vac_json: Any) -> FullVacancy:
    def _get_subfield_value(vac_json: Any, field1: str, field2: str) -> str:
        """Return value of a dict subobject or "" if missing.

        Example: json = {"frequency": {"name": "zzz"}} or {"frequency": null}
        """
        dict_or_none = vac_json.get(field1)
        if isinstance(dict_or_none, dict):
            return str(dict_or_none.get(field2, ""))
        return ""

    def parse_employer(data: dict[str, Any] | None) -> Employer | None:
        if not data:
            return None
        return Employer(
            id=data.get("id", ""),
            name=data.get("name", ""),
            trusted=data.get("trusted", False),
            accredited_it_employer=data.get("accredited_it_employer", False),
            url=data.get("url", ""),
        )

    def parse_salary_range(data: dict[str, Any] | None) -> SalaryRange | None:
        if not data:
            return None
        return SalaryRange(
            currency=data.get("currency", ""),
            frequency=_get_subfield_value(data, "frequency", "name"),
            from_=data.get("from"),
            to=data.get("to"),
            gross=data.get("gross", False),
            mode=_get_subfield_value(data, "mode", "name"),
        )

    def parse_professional_roles(data: list[dict[str, Any]] | None) -> list[ProfessionalRole]:
        if not data:
            return []
        return [
            ProfessionalRole(
                id=role.get("id", ""),
                name=role.get("name", ""),
            )
            for role in data
        ]

    return FullVacancy(
        vacancy_id=vac_json.get("id", ""),
        vacancy_name=vac_json.get("name", ""),
        area=Area(
            id=vac_json["area"]["id"],
            name=vac_json["area"]["name"],
            url=vac_json["area"]["url"],
        ),
        description=vac_json.get("description", ""),
        employer=parse_employer(vac_json.get("employer")),
        employment=_get_subfield_value(vac_json, "employment", "name"),
        experience=_get_subfield_value(vac_json, "experience", "name"),
        key_skills=[skill["name"] for skill in vac_json.get("key_skills", [])],
        professional_roles=parse_professional_roles(vac_json.get("professional_roles")),
        salary_range=parse_salary_range(vac_json.get("salary_range")),
        schedule=_get_subfield_value(vac_json, "schedule", "name"),
        type=_get_subfield_value(vac_json, "type", "name"),
        premium=vac_json.get("premium", False),
        published_at=vac_json.get("published_at", ""),
        vacancy_url=vac_json.get("alternate_url", ""),
    )


def _extract_and_calc_salary(salary_range: SalaryRange | None) -> tuple[int, int]:
    if salary_range is None:
        return (0, 0)

    salary_dict: Final = asdict(salary_range)
    currency: Final[str] = salary_dict.get("currency", "")
    rate: Final = EXCHANGE_RATES.get(currency, 1.0)
    gross_coef: Final = (1 - _TAX_RATE) if salary_dict.get("gross") else 1

    salary_from: int = 0
    if salary_dict.get("from_") is not None:
        salary_from = int(salary_dict.get("from_") * rate * gross_coef)

    salary_to: int = 0
    if salary_dict.get("to") is not None:
        salary_to = int(salary_dict.get("to") * rate * gross_coef)

    return (salary_from, salary_to)


def save_vacancies_to_json(vacancies: list[Vacancy], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as fp:
        for vacancy in vacancies:
            vac_str = json.dumps(asdict(vacancy), ensure_ascii=False, indent=2)
            fp.write(f"{vac_str}\n")
