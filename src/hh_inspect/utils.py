import re
from collections import Counter
from collections.abc import Iterable
from typing import Any


def find_top_words_in_list(iterable: Iterable[str]) -> list[tuple[str, int]]:
    words_counter = Counter(iterable)
    return sorted(words_counter.items(), key=lambda x: x[1], reverse=True)


def get_field_value(obj: dict[str, Any], field1: str, field2: str) -> str:
    """Return the value of obj.field1.field2 if it exists and "" otherwise.

    Obj can be:
        {"id": 123}
        {"id": 123, "main": None}
        {"id": 123, "main": {"abc": "def"}}
        {"id": 123, "main": {"subname": None}}
        {"id": 123, "main": {"subname": "normal_string"}}
    """
    dict_or_none = obj.get(field1)
    if dict_or_none is None:
        return ""
    value_or_none = dict_or_none.get(field2, "")
    if value_or_none is None:
        return ""
    return str(value_or_none)


def remove_html_tags(html_text: str) -> str:
    pattern = re.compile("<.*?>")
    return re.sub(pattern, "", html_text)
