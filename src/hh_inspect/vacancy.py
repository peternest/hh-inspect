from dataclasses import dataclass, field
from typing import Any, Final, LiteralString

import requests


REQUEST_TIMEOUT: Final = 5
RESPONSE_OK: Final = 200

_API_BASE_URL: Final[LiteralString] = "https://api.hh.ru/vacancies/"

# Optional fields are marked according to specification at
# https://api.hh.ru/openapi/redoc#tag/Vakansii/operation/get-vacancy


# TypedDict would be good to make more precise check!


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
class Salary:
    currency: str | None
    from_: int | None = field(metadata={"name": "from"})
    to: int | None
    gross: bool | None


@dataclass
class SalaryRange:
    currency: str
    frequency: str | None  # original frequency.name
    from_: int | None = field(metadata={"name": "from"})
    to: int | None
    gross: bool
    mode: str  # original mode.name


@dataclass
class Vacancy:
    vacancy_id: str  # original 'id'
    vacancy_name: str  # original 'name'
    area: Area
    description: str
    employer: Employer | None
    employment: str | None  # deprecated
    experience: str
    key_skills: list[str]
    professional_roles: list[ProfessionalRole]
    salary: Salary | None  # deprecated
    salary_range: SalaryRange | None
    schedule: str | None  # deprecated
    type: str
    published_at: str


def get_vacancy_or_404(vacancy_id: str) -> None:
    url: Final = f"{_API_BASE_URL}{vacancy_id}"
    response: Final = requests.get(url, timeout=REQUEST_TIMEOUT)
    vacancy_json: Final = response.json()
    # print(response.status_code, json.dumps(vacancy_json, ensure_ascii=False, indent=2))

    if response.status_code == RESPONSE_OK:
        vac = parse_vacancy(vacancy_json)
        print(vac)


def parse_vacancy(vacancy_json: Any) -> Vacancy:
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

    def parse_salary(data: dict[str, Any] | None) -> Salary | None:
        if not data:
            return None
        return Salary(
            currency=data.get("currency"),
            from_=data.get("from"),
            to=data.get("to"),
            gross=data.get("gross"),
        )

    def parse_salary_range(data: dict[str, Any] | None) -> SalaryRange | None:
        if not data:
            return None
        return SalaryRange(
            currency=data.get("currency", ""),
            frequency=data.get("frequency", {}).get("name"),
            from_=data.get("from"),
            to=data.get("to"),
            gross=data.get("gross", False),
            mode=data.get("mode", {}).get("name", ""),
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

    return Vacancy(
        vacancy_id=vacancy_json.get("id", ""),
        vacancy_name=vacancy_json.get("name", ""),
        area=Area(
            id=vacancy_json["area"]["id"],
            name=vacancy_json["area"]["name"],
            url=vacancy_json["area"]["url"],
        ),
        description=vacancy_json.get("description", ""),
        employer=parse_employer(vacancy_json.get("employer")),
        employment=vacancy_json.get("employment", {}).get("name"),
        experience=vacancy_json.get("experience", {}).get("name", ""),
        key_skills=[skill["name"] for skill in vacancy_json.get("key_skills", [])],
        professional_roles=parse_professional_roles(vacancy_json.get("professional_roles")),
        salary=parse_salary(vacancy_json.get("salary")),
        salary_range=parse_salary_range(vacancy_json.get("salary_range")),
        schedule=vacancy_json.get("schedule", {}).get("name"),
        type=vacancy_json.get("type", {}).get("name", ""),
        published_at=vacancy_json.get("published_at", ""),
    )


if __name__ == "__main__":
    get_vacancy_or_404("120596707")
