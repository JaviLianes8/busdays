"""Build the real wheel, install it into a throwaway venv and drive the installed script.

Nothing is mocked: this needs network access for pip to fetch the build backend.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import venv
import zipfile
from pathlib import Path

import pytest

import busdays

ROOT = Path(__file__).resolve().parent.parent
MODULES = ("__init__", "__main__", "_calendar", "_cli", "_core", "_kernel", "_roll", "_validate")


def _run(cmd: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        cmd, input=stdin, capture_output=True, text=True, env=env, timeout=600, check=False
    )


@pytest.mark.e2e
def test_wheel_installs_and_the_script_works(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    built = _run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "-q", "-w", str(dist), str(ROOT)]
    )
    assert built.returncode == 0, built.stderr
    wheels = list(dist.glob("busdays-*.whl"))
    assert [w.name for w in wheels] == [f"busdays-{busdays.__version__}-py3-none-any.whl"]
    names = zipfile.ZipFile(wheels[0]).namelist()
    for module in MODULES:
        assert f"busdays/{module}.py" in names
    assert "busdays/py.typed" in names
    assert not [n for n in names if n.startswith(("data/", "tests/", "scripts/"))]
    metadata = next(n for n in names if n.endswith(".dist-info/METADATA"))
    requires = [
        line
        for line in zipfile.ZipFile(wheels[0]).read(metadata).decode().splitlines()
        if line.startswith("Requires-Dist:")
    ]
    # Zero runtime dependencies: every requirement belongs to the dev extra.
    assert requires and all("extra == 'dev'" in line for line in requires), requires

    env_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, clear=True).create(env_dir)
    bindir = env_dir / ("Scripts" if os.name == "nt" else "bin")
    python = bindir / ("python.exe" if os.name == "nt" else "python")
    script = bindir / ("busdays.exe" if os.name == "nt" else "busdays")
    installed = _run([str(python), "-m", "pip", "install", "-q", "--no-index", str(wheels[0])])
    assert installed.returncode == 0, installed.stderr
    assert script.is_file()

    done = _run([str(script), "add", "2026-01-02", "1"])
    assert (done.returncode, done.stdout) == (0, "2026-01-05\n")
    done = _run([str(script), "add", "2026-01-02", "1", "--holidays", "-"], stdin="2026-01-05\n")
    assert (done.returncode, done.stdout) == (0, "2026-01-06\n")
    done = _run([str(python), "-m", "busdays", "roll", "2026-01-31", "modified_following"])
    assert (done.returncode, done.stdout) == (0, "2026-01-30\n")
    done = _run([str(script), "is", "2026-01-03"])
    assert (done.returncode, done.stdout) == (1, "no\n")
    done = _run([str(script), "add", "9999-12-31", "1"])
    assert done.returncode == 2 and "years 1 to 9999" in done.stderr
    version = _run([str(script), "--version"])
    assert version.stdout.strip() == f"busdays {busdays.__version__}"

    probe = (
        "import datetime as d, busdays as b; "
        "c = b.Calendar.from_weekmask('Sun Mon Tue Wed Thu'); "
        "print(c.add_business_days(d.date(2026, 1, 1), 1), b.Roll('forward'), b.__file__)"
    )
    shown = _run([str(python), "-c", probe]).stdout
    assert shown.startswith("2026-01-04 following ") and str(env_dir) in shown


@pytest.mark.e2e
def test_sdist_ships_the_manifest_but_no_upstream_copies(tmp_path: Path) -> None:
    built = _run([sys.executable, "-m", "build", "--sdist", "--outdir", str(tmp_path), str(ROOT)])
    assert built.returncode == 0, built.stderr
    (sdist,) = tmp_path.glob("busdays-*.tar.gz")
    with tarfile.open(sdist) as archive:
        names = [name.split("/", 1)[1] for name in archive.getnames() if "/" in name]
    assert "data/upstream/MANIFEST.json" in names
    assert "scripts/fetch_upstream.py" in names and "tests/conftest.py" in names
    assert [n for n in names if n.startswith("data/")] == ["data/upstream/MANIFEST.json"]
