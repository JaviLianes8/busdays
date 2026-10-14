"""Every ``expression  # -> value`` line in the README must hold."""

from __future__ import annotations

import re
import shlex
from pathlib import Path

import pytest

from busdays._cli import main

ROOT = Path(__file__).resolve().parent.parent
BLOCK = re.compile(r"```python\n(.*?)```", re.S)


def test_documented_results_are_true() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    namespace: dict[str, object] = {}
    checked = 0
    for block in BLOCK.findall(text):
        lines: list[str] = []
        for line in block.splitlines():
            if "  # -> " in line:
                exec("\n".join(lines), namespace)
                lines = []
                code, expected = line.split("  # -> ", 1)
                got = eval(code, namespace)
                assert got == eval(expected, namespace), line
                if expected.startswith("Roll."):
                    assert got is eval(expected, namespace), line
                checked += 1
            else:
                lines.append(line)
        exec("\n".join(lines), namespace)
    assert checked >= 25


def test_documented_commands_print_what_the_readme_says(
    capsys: pytest.CaptureFixture[str],
) -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    block = text.split("## Command line", 1)[1].split("```", 2)[1]
    checked = 0
    for line in block.splitlines():
        command, _, comment = line.partition("#")
        if not line.startswith("busdays ") or not re.fullmatch(r" [-0-9]+", comment.rstrip()):
            continue
        assert main(shlex.split(command)[1:]) == 0, line
        assert capsys.readouterr().out == comment.strip() + "\n", line
        checked += 1
    assert checked == 3
