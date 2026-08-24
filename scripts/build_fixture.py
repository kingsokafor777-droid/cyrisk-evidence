"""Generate a sealed synthetic payload-blind Cyrisk Evidence registry."""

from __future__ import annotations

from pathlib import Path

from cyrisk_evidence.verifier import seal_manifest

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "fixtures" / "synthetic_evidence_registry.json"
SYNTHETIC_HASH = "7f9b8c2b4b452be484fe4ecf7f8d08ed6a9ca2f80d29c1238ccce47f4e2343a4"

PAYLOAD = {
    "registry_id": "registry-ransomware-baseline",
    "assumptions": [
        {
            "assumption_id": "assumption-frequency",
            "factor_id": "frequency-range",
            "unit": "events-per-year",
            "lower": "0.1",
            "central": "0.3",
            "upper": "0.8",
            "source_class": "synthetic",
            "owner_reference": "synthetic-risk-owner",
            "rationale": "Sealed synthetic scenario assumption only.",
            "evidence_ids": ["evidence-synthetic-control-gap"],
            "review_due_on": "2098-01-01",
            "expires_on": "2099-12-31",
        }
    ],
    "evidence_expectations": [
        {
            "evidence_id": "evidence-synthetic-control-gap",
            "source_class": "synthetic",
            "expected_integrity_hash": SYNTHETIC_HASH,
            "observed_integrity_hash": SYNTHETIC_HASH,
            "expires_on": "2099-12-31",
            "description": "Synthetic payload-blind integrity expectation.",
        }
    ],
    "calibration_reviews": [
        {
            "review_id": "review-frequency-synthetic",
            "assumption_id": "assumption-frequency",
            "reviewer_reference": "synthetic-reviewer",
            "observed_on": "2097-01-01",
            "observation": "Synthetic observation; no authority assertion or approval.",
            "follow_up_required": True,
        }
    ],
}


def main() -> None:
    registry = seal_manifest(PAYLOAD)
    TARGET.parent.mkdir(exist_ok=True)
    TARGET.write_text(registry.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
