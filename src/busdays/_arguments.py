"""Command line diagnostics that do not echo arbitrary arguments."""

from __future__ import annotations

import argparse
from typing import NoReturn


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        if "invalid choice:" in message:
            message = "invalid command; use --help for the command list"
        elif message.startswith("unrecognized arguments:"):
            message = "unrecognized arguments; use --help for usage"
        elif len(message) > 300:
            message = "invalid arguments; use --help for usage"
        super().error(message)
