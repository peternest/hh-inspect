import re
from typing import Final


def remove_html_tags(html_text: str) -> str:
    pattern: Final = re.compile("<.*?>")
    return re.sub(pattern, "", html_text)
