import argparse
import logging
import sys
from pathlib import Path
from typing import Final

import yaml
from pydantic import BaseModel, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


type QueryValue = str | int | bool
type QueryDict = dict[str, QueryValue | list[QueryValue]]

# fmt: off
EXCHANGE_RATES: Final[dict[str, float]] = {
    "RUR": 1.0,
    "USD": 80.0,
    "EUR": 90.0,
    "BYN": 26.0,
    "KZT": 0.15,
    "CNY": 12.0
}
# fmt: on

logger = logging.getLogger(__name__)


# Fields with None will not be included in query string.
class QuerySettings(BaseModel):
    text: str = "Python"
    excluded_text: str = ""
    search_field: list[str] = ["name"]
    area: list[str] = ["113"]
    professional_role: list[str] | None = None
    salary: int | None = None
    only_with_salary: bool = False
    experience: list[str] | None = None
    per_page: int = 25
    order_by: str = "publication_time"
    label: str | None = None

    def to_dict(self) -> QueryDict:
        return self.model_dump(exclude_none=True)


class FilterAfterSettings(BaseModel):
    excluded_companies: list[str] = []


class GeneralSettings(BaseModel):
    num_workers: int = 1
    print_output_to_console: bool = True
    save_results_to_csv: bool = True
    save_results_to_json: bool = True
    draw_salary_plots: bool = True
    print_salary_stats: bool = True
    print_key_skills: bool = True
    print_top_words: bool = True


class Settings(BaseSettings):
    # https://docs.pydantic.dev/latest/concepts/pydantic_settings/#the-basics

    query: QuerySettings = QuerySettings()
    filter_after: FilterAfterSettings = FilterAfterSettings()
    general: GeneralSettings = GeneralSettings()

    def convert_query_to_dict(self) -> QueryDict:
        return self.query.to_dict()

    def __str__(self) -> str:
        return str(self.model_dump())


class DefaultSettings(Settings):
    """Return default setting, completely ignoring CLI."""

    model_config = SettingsConfigDict(cli_parse_args=False)


class FileOnlySettings(Settings):
    model_config = SettingsConfigDict(cli_parse_args=False)

    @classmethod
    def load_from_config(cls, config_file: Path) -> "Settings":
        if config_file and not config_file.exists():
            logger.error(f"Cannot find config file: '{config_file}'")
            return DefaultSettings()

        with config_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)


def load_settings(config_file: Path) -> Settings:
    try:
        settings = FileOnlySettings.load_from_config(config_file)
    except ValidationError:
        logger.exception("Failed to load settings, maybe incorrect YAML. Using default values.")
        print("Failed to load settings, maybe incorrect YAML. Using default values.")  # noqa: T201
        return DefaultSettings()
    else:
        _parse_args(settings, sys.argv[1:])
        return settings


def _parse_args(settings: Settings, argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description="HeadHunter vacancies inspector")
    parser.add_argument(
        "-t",
        "--text",
        action="store",
        type=str,
        default=None,
        help="Text to search (e.g. 'Python developer')",
    )
    parser.add_argument(
        "-n",
        "--num_workers",
        action="store",
        type=int,
        default=None,
        help="Number of parallel workers for multithreading.",
    )

    args: Final = parser.parse_args(argv)

    if args.text is not None:
        settings.query.text = args.text

    if args.num_workers is not None and isinstance(args.num_workers, int) and args.num_workers >= 1:
        settings.general.num_workers = args.num_workers
