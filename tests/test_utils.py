import pytest

from hh_inspect.utils import remove_html_tags


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
