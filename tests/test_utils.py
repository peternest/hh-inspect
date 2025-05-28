from collections.abc import Iterable
from typing import Any

import pytest

from hh_inspect.utils import find_top_words_in_list, get_field_value, remove_html_tags


@pytest.mark.parametrize(
    ("iterable", "result"),
    [
        ([], []),
        (["str"], [("str", 1)]),
        (["a", "a", "a"], [("a", 3)]),
        (["a", "b", "b", "b"], [("b", 3), ("a", 1)]),
        (["a", "b", "b", "a", "a", "b"], [("a", 3), ("b", 3)]),
    ],
)
def test_find_top_words_in_list(iterable: Iterable[str], result: list[tuple[str, int]]) -> None:
    assert find_top_words_in_list(iterable) == result


@pytest.mark.parametrize(
    ("obj", "field1", "field2", "result"),
    [
        ({"id": 123}, "main", "subname", ""),
        ({"id": 123, "main": None}, "main", "subname", ""),
        ({"id": 123, "main": {"abc": "def"}}, "main", "subname", ""),
        ({"id": 123, "main": {"subname": None}}, "main", "subname", ""),
        ({"id": 123, "main": {"subname": "normal_string"}}, "main", "subname", "normal_string"),
    ],
)
def test_get_field_value(obj: dict[str, Any], field1: str, field2: str, result: str) -> None:
    assert get_field_value(obj, field1, field2) == result


@pytest.mark.parametrize(
    ("html_text", "result"),
    [
        ("", ""),
        ("str", "str"),
        ("no tags", "no tags"),
        ("<p>ParaGraPh</p>", "ParaGraPh"),
        ("<body>unclosed tags", "unclosed tags"),
        ("<br><br><br>", ""),
        ("<p><strong>Text <b>bold <i>italic</i></b> end.</p>", "Text bold italic end."),
    ],
)
def test_remove_html_tags(html_text: str, result: str) -> None:
    assert remove_html_tags(html_text) == result
