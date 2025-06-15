import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final

from hh_inspect.settings import EXCHANGE_RATES
from hh_inspect.utils import get_field_value, remove_html_tags


logger = logging.getLogger(__name__)

_TAX_RATE: Final = 0.13

_FIX_SALARY_TO: Final = True  # If salary_to is not set, make it = salary_from * _FIX_SALARY_TO_COEF
_FIX_SALARY_TO_COEF: Final = 1.1

# Some optional fields in models are marked according to specification at
# https://api.hh.ru/openapi/redoc#tag/Vakansii/operation/get-vacancy


@dataclass
class Vacancy:
    """Only necessary fields from FullVacancy for further analysis.

    salary_from, salary_to = values are after taxes (0 means None)

    salary_to = salary_from * _FIX_SALARY_TO_COEF if absent!
    """

    vacancy_id: str
    region: str
    employer_name: str
    employer_city: str
    accredited_it: bool
    vacancy_name: str
    salary_from: int
    salary_to: int
    experience: str
    employment: str
    schedule: str
    key_skills: list[str]
    description: str
    vacancy_url: str
    published_at: str

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"{self.vacancy_id}, "
            f"{self.employer_name[:35]:35}, {self.employer_city[:15]:15}, {self.vacancy_name[:35]:35}, "
            f"({self.salary_from:6}, {self.salary_to:6}), {self.published_at}"
            f")"
        )


@dataclass
class Area:
    id: str
    name: str
    url: str


@dataclass
class Address:
    city: str | None
    street: str
    building: str
    description: str
    raw: str


@dataclass
class Employer:
    id: str
    name: str | None
    trusted: bool
    accredited_it_employer: bool | None
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
    address: Address | None
    employment: str
    experience: str
    key_skills: list[str]
    professional_roles: list[ProfessionalRole]
    salary_range: SalaryRange | None
    schedule: str
    description: str = field(repr=False)
    type: str
    published_at: str
    vacancy_url: str = field(repr=False)  # original 'alternate_url'

    def to_basic_vacancy(self) -> Vacancy:
        salary_from, salary_to = _extract_and_calc_salary(self.salary_range)

        def get_employer_name() -> str:
            if self.employer is not None and self.employer.name is not None:
                return self.employer.name
            return ""

        def get_employer_city() -> str:
            if self.address is not None and self.address.city is not None:
                return self.address.city
            return ""

        def get_employer_accreditation() -> bool:
            if self.employer is not None and self.employer.accredited_it_employer is not None:
                return self.employer.accredited_it_employer
            return False

        def get_published_date() -> str:
            return self.published_at[:10]

        return Vacancy(
            vacancy_id=self.vacancy_id,
            vacancy_name=self.vacancy_name,
            employer_name=get_employer_name(),
            employer_city=get_employer_city(),
            accredited_it=get_employer_accreditation(),
            region=self.area.name,
            salary_from=salary_from,
            salary_to=salary_to,
            experience=self.experience,
            employment=self.employment,
            schedule=self.schedule,
            key_skills=self.key_skills,
            description=remove_html_tags(self.description),
            vacancy_url=self.vacancy_url,
            published_at=get_published_date(),
        )


def parse_vacancy_data(vac_json: dict[str, Any]) -> FullVacancy:
    def parse_address(data: dict[str, Any] | None) -> Address | None:
        if not data:
            return None
        return Address(
            city=data.get("city", ""),
            street=data.get("street", ""),
            building=data.get("building", ""),
            description=data.get("description", ""),
            raw=data.get("raw", ""),
        )

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
            frequency=get_field_value(data, "frequency", "name"),
            from_=data.get("from"),
            to=data.get("to"),
            gross=data.get("gross", False),
            mode=get_field_value(data, "mode", "name"),
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
        address=parse_address(vac_json.get("address")),
        description=vac_json.get("description", ""),
        employer=parse_employer(vac_json.get("employer")),
        employment=get_field_value(vac_json, "employment", "name"),
        experience=get_field_value(vac_json, "experience", "name"),
        key_skills=[skill["name"] for skill in vac_json.get("key_skills", [])],
        professional_roles=parse_professional_roles(vac_json.get("professional_roles")),
        salary_range=parse_salary_range(vac_json.get("salary_range")),
        schedule=get_field_value(vac_json, "schedule", "name"),
        type=get_field_value(vac_json, "type", "name"),
        published_at=vac_json.get("published_at", ""),
        vacancy_url=vac_json.get("alternate_url", ""),
    )


def _extract_and_calc_salary(salary_range: SalaryRange | None) -> tuple[int, int]:
    if salary_range is None:
        return (0, 0)

    salary_dict = asdict(salary_range)
    currency: Final[str] = salary_dict.get("currency", "")
    rate = EXCHANGE_RATES.get(currency, 1.0)
    gross_coef = (1 - _TAX_RATE) if salary_dict.get("gross") else 1

    raw_value = salary_dict.get("from_")
    salary_from_val = raw_value if raw_value is not None else 0.0
    salary_from = int(salary_from_val * rate * gross_coef)

    raw_value = salary_dict.get("to")
    salary_to_val = raw_value if raw_value is not None else 0.0
    salary_to = int(salary_to_val * rate * gross_coef)

    if salary_to == 0 and _FIX_SALARY_TO:
        salary_to = int(salary_from * _FIX_SALARY_TO_COEF)

    return (salary_from, salary_to)


def save_vacancies_to_json(vacancies: list[Vacancy], filename: Path) -> None:
    logger.info(f"Saving vacancies to '{filename}'...")
    with open(filename, "w", encoding="utf-8") as fp:
        json_str = json.dumps([vac.__dict__ for vac in vacancies], ensure_ascii=False, indent=2)
        fp.write(f"{json_str}\n")
