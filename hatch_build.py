"""Keep repository-only exclusion files out of source archives."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        if self.target_name == "sdist":
            forced = build_data["force_include"]
            for source in list(forced):
                if Path(source).name in {".gitignore", ".hgignore"}:
                    del forced[source]
