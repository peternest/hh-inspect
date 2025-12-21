import json
import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from hh_inspect.vacancy import Vacancy


env = Environment(loader=FileSystemLoader("templates"), autoescape=False)  # noqa: S701


logger = logging.getLogger(__name__)


def convert_vacancies_to_json(vacancies: list[Vacancy], show_excluded: bool) -> str:
    return json.dumps(
        [vac.__dict__ for vac in vacancies if show_excluded or not vac.excluded], ensure_ascii=False, indent=2
    )


def save_vacancies_to_json(json_str: str, json_filename: Path) -> None:
    logger.info(f"Saving vacancies to '{json_filename}'...")
    with open(json_filename, "w", encoding="utf-8") as fp:
        fp.write(f"{json_str}\n")


def save_vacancies_to_html(json_str: str, html_filename: Path) -> None:
    template = env.get_template("template.html")

    # fmt: off
    context = {
        "data": json.loads(json_str)
    }
    # fmt: on
    html_output = template.render(context)

    logger.info(f"Saving vacancies to '{html_filename}'...")
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_output)
