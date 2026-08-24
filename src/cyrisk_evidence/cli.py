"""Local CLI for deterministic Cyrisk Evidence verification."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from cyrisk_evidence.models import RegistryManifest
from cyrisk_evidence.verifier import verify


def main(argv: Sequence[str] | None = None) -> int:
    """Verify one local registry at a supplied date and emit stable JSON."""
    parser = argparse.ArgumentParser(prog="cyrisk-evidence")
    parser.add_argument("command", choices=("verify",))
    parser.add_argument("registry", type=Path)
    parser.add_argument("--as-of", required=True, type=date.fromisoformat)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.registry.read_text(encoding="utf-8"))
        manifest = RegistryManifest.model_validate(payload)
        report = verify(manifest, args.as_of)
    except (OSError, ValidationError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    print(report.model_dump_json())
    return 0
