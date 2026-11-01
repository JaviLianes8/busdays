"""Read the examples from fetched NumPy reference pages, without embedding copies."""

from __future__ import annotations

import ast
import doctest
import html
import re
from datetime import date

import pytest
from conftest import UPSTREAM, needs

from busdays import Calendar


def day(value: object) -> date:
    assert isinstance(value, str)
    return date.fromisoformat(value + {4: "-01-01", 7: "-01", 10: ""}[len(value)])


@pytest.mark.parametrize("name", ["busday_offset", "busday_count"])
def test_fetched_scalar_examples(name: str) -> None:
    path = UPSTREAM / f"numpy-{name}.html"
    if not path.exists():
        pytest.skip("fetch the NumPy reference pages")
    blocks = re.findall(r"<pre>(.*?)</pre>", path.read_text(encoding="utf-8"), re.S)
    checked = 0
    for block in blocks:
        text = html.unescape(re.sub(r"<[^>]+>", "", block))
        for example in doctest.DocTestParser().get_examples(text):
            statements = ast.parse(example.source).body
            if not statements or not isinstance(statements[-1], ast.Expr):
                continue
            call = statements[-1].value
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
                continue
            assert call.func.attr == name
            args = [ast.literal_eval(arg) for arg in call.args]
            kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
            calendar = Calendar.from_weekmask(kwargs.get("weekmask", "1111100"))
            if name == "busday_count":
                expected = ast.literal_eval(example.want.strip())
                assert calendar.business_days_between(day(args[0]), day(args[1])) == expected
            else:
                want = ast.parse(example.want.strip(), mode="eval").body
                assert isinstance(want, ast.Call)
                expected = day(ast.literal_eval(want.args[0]))
                assert (
                    calendar.add_business_days(day(args[0]), args[1], roll=kwargs["roll"])
                    == expected
                )
            checked += 1
    assert checked == (8 if name == "busday_offset" else 3)


@needs("numpy-is_busday.html")
def test_fetched_membership_example() -> None:
    raw = (UPSTREAM / "numpy-is_busday.html").read_text(encoding="utf-8")
    text = html.unescape(re.sub(r"<[^>]+>", "", re.findall(r"<pre>(.*?)</pre>", raw, re.S)[0]))
    example = doctest.DocTestParser().get_examples(text)[1]
    call = ast.parse(example.source).body[-1]
    assert isinstance(call, ast.Expr) and isinstance(call.value, ast.Call)
    dates = [day(value) for value in ast.literal_eval(call.value.args[0])]
    holidays = [day(value) for value in ast.literal_eval(call.value.keywords[0].value)]
    expected = ast.literal_eval(example.want.strip().removeprefix("array(").removesuffix(")"))
    assert [Calendar(holidays=holidays).is_business_day(value) for value in dates] == expected
