"""Exercise the published release and the built wheel as isolated external consumers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import venv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROBE = """
import json, pickle, random
from datetime import date, timedelta
from pathlib import Path
import busdays as b
rng = random.Random(7319)
results = []
for _ in range(1000):
    start = date(2000, 1, 1) + timedelta(days=rng.randrange(9000))
    stop = start + timedelta(days=rng.randrange(-100, 100))
    weekend = tuple(rng.sample(range(7), rng.randrange(7)))
    holidays = [start + timedelta(days=rng.randrange(-20, 20)) for _ in range(8)]
    c = b.Calendar(weekend, holidays)
    n = rng.randrange(-20, 20)
    results.append([c.weekend, [str(x) for x in c.holidays], c.weekmask])
    for name, args in [
        ('is_business_day', (start,)), ('add_business_days', (start, n)),
        ('business_days_between', (start, stop)), ('next_business_day', (start,)),
        ('prev_business_day', (start,)), ('first_business_day', (start.year, start.month)),
        ('last_business_day', (start.year, start.month))]:
        result = getattr(c, name)(*args)
        assert result == getattr(b, name)(*args, weekend=weekend, holidays=holidays)
        results.append(str(result))
    results.append([str(x) for x in c.business_days(start, stop)])
    for mode in b.Roll:
        try:
            results.append(str(c.roll(start, mode)))
        except ValueError:
            results.append('ValueError')
saved = Path('calendar.pickle')
if saved.exists():
    old = pickle.loads(saved.read_bytes())
    assert old == b.Calendar(holidays=[date(2026, 1, 1)])
    assert old.next_business_day(date(2025, 12, 31)) == date(2026, 1, 2)
saved.write_bytes(pickle.dumps(b.Calendar(holidays=[date(2026, 1, 1)])))
print(json.dumps(results))
"""


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, timeout=240)
    assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.mark.e2e
def test_upgrade_from_pypi_preserves_valid_results(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    run([sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", str(dist), str(ROOT)], tmp_path)
    (wheel,) = dist.glob("busdays-1.0.0-*.whl")
    environment = tmp_path / "consumer"
    venv.EnvBuilder(with_pip=True).create(environment)
    bindir = environment / ("Scripts" if os.name == "nt" else "bin")
    python = str(bindir / ("python.exe" if os.name == "nt" else "python"))
    cli = str(bindir / ("busdays.exe" if os.name == "nt" else "busdays"))
    run([python, "-m", "pip", "install", "busdays==0.2.0"], tmp_path)
    assert run([cli, "--version"], tmp_path).stdout.strip() == "busdays 0.2.0"
    before = run([python, "-I", "-c", PROBE], tmp_path).stdout
    run([python, "-m", "pip", "install", "--upgrade", "--no-index", str(wheel)], tmp_path)
    after = run([python, "-I", "-c", PROBE], tmp_path).stdout
    assert json.loads(before) == json.loads(after)
    assert run([cli, "--version"], tmp_path).stdout.strip() == "busdays 1.0.0"
    for args, expected in [
        (["count", "2026-01-05", "2026-01-12"], "5\n"),
        (["list", "2026-01-02", "2026-01-06"], "2026-01-02\n2026-01-05\n"),
        (["is", "2026-01-05"], "yes\n"),
        (["add", "2026-01-02", "1"], "2026-01-05\n"),
        (["roll", "2026-01-31", "preceding"], "2026-01-30\n"),
    ]:
        assert run([cli, *args], tmp_path).stdout == expected
        assert run([python, "-I", "-m", "busdays", *args], tmp_path).stdout == expected
    assert "Business-day arithmetic" in run([cli, "--help"], tmp_path).stdout
