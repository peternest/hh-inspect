import json
import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


env = Environment(loader=FileSystemLoader("templates"), autoescape=False)  # noqa: S701


logger = logging.getLogger(__name__)


def json_to_pretty_html(json_filename: Path, html_filename: Path) -> None:
    try:
        with open(json_filename, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        logger.exception(f"Error: JSON file not found at {json_filename}")
        return
    except json.JSONDecodeError:
        logger.exception(f"Error: Invalid JSON format in {json_filename}")
        return

    template = env.get_template("template.html")

    # fmt: off
    context = {
        "data": data
    }
    # fmt: on
    html_output = template.render(context)

    logger.info(f"Saving vacancies to '{html_filename}'...")
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_output)
