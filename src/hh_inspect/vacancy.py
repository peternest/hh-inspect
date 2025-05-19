import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Final

from hh_inspect.options import EXCHANGE_RATES
from hh_inspect.utils import remove_html_tags


_TAX_RATE: Final = 0.13

logger = logging.getLogger(__name__)


# Optional fields in models are marked according to specification at
# https://api.hh.ru/openapi/redoc#tag/Vakansii/operation/get-vacancy


@dataclass
class BasicVacancy:
    """Only necessary fields from FullVacancy for further analysis."""

    vacancy_id: str
    vacancy_name: str
    employer_name: str
    region: str
    salary_from: int | None  # salary after taxes paid
    salary_to: int | None
    experience: str
    employment: str
    schedule: str
    key_skills: list[str]
    description: str

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
    id: str | None
    name: str
    trusted: bool
    accredited_it_employer: bool | None
    url: str | None


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
    employment: str | None
    experience: str
    key_skills: list[str]
    professional_roles: list[ProfessionalRole]
    salary_range: SalaryRange | None
    schedule: str | None
    description: str = field(repr=False)
    type: str
    published_at: str

    def to_basic_vacancy(self) -> BasicVacancy:
        salary_from, salary_to = _extract_and_calc_salary(self.salary_range)

        return BasicVacancy(
            vacancy_id=self.vacancy_id,
            vacancy_name=self.vacancy_name,
            employer_name=self.employer.name,
            region=self.area.name,
            salary_from=salary_from,
            salary_to=salary_to,
            experience=self.experience,
            employment=self.employment,
            schedule=self.schedule,
            key_skills=self.key_skills,
            description=remove_html_tags(self.description),
        )


def parse_vacancy_data(vacancy_json: Any) -> FullVacancy:
    def _get_subfield_value(data: dict[str, Any] | None, field1: str, field2: str) -> str:
        """Return value of a dict subobject or "" if missing.

        Example: data.get("frequency", {}).get("name")
        """
        maybe_dict = data.get(field1)
        if maybe_dict is not None:
            return maybe_dict.get(field2, "")
        return ""

    def parse_employer(data: dict[str, Any] | None) -> Employer | None:
        if not data:
            return None
        return Employer(
            id=data.get("id"),
            name=data.get("name", ""),
            trusted=data.get("trusted", False),
            accredited_it_employer=data.get("accredited_it_employer"),
            url=data.get("url"),
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
        vacancy_id=vacancy_json.get("id", ""),
        vacancy_name=vacancy_json.get("name", ""),
        area=Area(
            id=vacancy_json["area"]["id"],
            name=vacancy_json["area"]["name"],
            url=vacancy_json["area"]["url"],
        ),
        description=vacancy_json.get("description", ""),
        employer=parse_employer(vacancy_json.get("employer")),
        employment=_get_subfield_value(vacancy_json, "employment", "name"),
        experience=_get_subfield_value(vacancy_json, "experience", "name"),
        key_skills=[skill["name"] for skill in vacancy_json.get("key_skills", [])],
        professional_roles=parse_professional_roles(vacancy_json.get("professional_roles")),
        salary_range=parse_salary_range(vacancy_json.get("salary_range")),
        schedule=_get_subfield_value(vacancy_json, "schedule", "name"),
        type=_get_subfield_value(vacancy_json, "type", "name"),
        published_at=vacancy_json.get("published_at", ""),
    )


def _extract_and_calc_salary(salary_range: SalaryRange | None) -> tuple[int | None, int | None]:
    if salary_range is None:
        return (None, None)

    salary_dict: Final = asdict(salary_range)
    currency: Final[str] = salary_dict.get("currency", "")
    rate: Final = EXCHANGE_RATES.get(currency, 1.0)
    gross_coef: Final = (1 - _TAX_RATE) if salary_dict.get("gross") else 1

    salary_from: int | None = None
    if salary_dict.get("from_") is not None:
        salary_from = int(salary_dict.get("from_") * rate * gross_coef)

    salary_to: int | None = None
    if salary_dict.get("to") is not None:
        salary_to = int(salary_dict.get("to") * rate * gross_coef)

    return (salary_from, salary_to)
