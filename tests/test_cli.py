from __future__ import annotations

import json
from pathlib import Path

import pytest

from cyrisk_evidence.cli import main

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_evidence_registry.json"


def test_cli_emits_verification_report(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["verify", str(FIXTURE), "--as-of", "2099-01-01"]) == 0
    assert json.loads(capsys.readouterr().out)["valid_evidence_ids"] == [
        "evidence-synthetic-control-gap"
    ]


def test_cli_rejects_invalid_registry(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("not-json", encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["verify", str(invalid), "--as-of", "2099-01-01"])
