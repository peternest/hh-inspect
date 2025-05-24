import logging
from pathlib import Path
from typing import Final, LiteralString

import yaml
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings


type QueryValue = str | int | bool
type QueryDict = dict[str, QueryValue | list[QueryValue]]

# fmt: off
EXCHANGE_RATES: Final[dict[LiteralString, float]] = {
    "RUR": 1.0,
    "USD": 80.0,
    "EUR": 90.0,
    "BYN": 26.0,
    "KZT": 0.15,
    "CNY": 12.0
} # fmt: on

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG: Final[LiteralString] = "config.yaml"


class QuerySettings(BaseModel):
    text: str = "Python"
    excluded_text: str = ""
    search_field: str = "name"
    area: list[str] = ["1"]
    professional_role: list[str] = ["96"]
    salary: int = 100000
    only_with_salary: bool = False
    experience: list[str] | None = None
    per_page: int = 20
    order_by: str = "publication_time"
    label: str | None = None

    def to_dict(self) -> QueryDict:
        return self.model_dump(exclude_none=True)


class GeneralSettings(BaseModel):
    num_workers: int = 1
    save_results_to_csv: bool = False
    save_results_to_json: bool = False


class Settings(BaseSettings):
    # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#the-basics

    # model_config = SettingsConfigDict(cli_parse_args=True)

    query: QuerySettings = QuerySettings()
    general: GeneralSettings = GeneralSettings()

    @classmethod
    def load_from_config(cls, config_file: str = _DEFAULT_CONFIG) -> "Settings":
        if config_file and not Path(config_file).exists():
            logger.error(f"Cannot find config file: '{config_file}'")
            return cls()

        with Path(config_file).open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        try:
            settings = cls.model_validate(data)
        except ValidationError:
            logger.exception("Error validating config:")
            return cls()
        return settings

    def convert_query_to_dict(self) -> QueryDict:
        return self.query.to_dict()

    def __str__(self) -> str:
        return yaml.safe_dump(self.model_dump(), allow_unicode=True, sort_keys=False)


def load_settings() -> Settings:
    # Parse config file first, so command line can override.
    settings = Settings().load_from_config()
    # print(settings.model_dump())
    # _parse_args(options, sys.argv[1:])
    return settings
