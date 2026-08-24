from __future__ import annotations

from datetime import date
from pathlib import Path

from cyrisk_evidence.models import RegistryManifest
from cyrisk_evidence.verifier import seal_manifest, verify

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_evidence_registry.json"


def load_manifest() -> RegistryManifest:
    return RegistryManifest.model_validate_json(FIXTURE.read_text(encoding="utf-8"))


def test_sealed_manifest_verifies_valid_reference() -> None:
    report = verify(load_manifest(), date(2099, 1, 1))
    assert report.valid_evidence_ids == ("evidence-synthetic-control-gap",)
    assert report.expired_evidence_ids == ()
    assert report.computed_hash == report.declared_hash


def test_expiry_is_evaluated_at_supplied_date() -> None:
    report = verify(load_manifest(), date(2100, 1, 1))
    assert report.expired_evidence_ids == ("evidence-synthetic-control-gap",)
    assert report.expired_assumption_ids == ("assumption-frequency",)


def test_missing_and_mismatched_hashes_are_explicit() -> None:
    payload = load_manifest().model_dump(mode="json")
    payload["evidence_expectations"][0]["observed_integrity_hash"] = None  # type: ignore[index]
    missing = RegistryManifest.model_validate(payload)
    assert verify(missing, date(2099, 1, 1)).missing_observed_hash_ids == (
        "evidence-synthetic-control-gap",
    )
    payload["evidence_expectations"][0]["observed_integrity_hash"] = "0" * 64  # type: ignore[index]
    mismatch = RegistryManifest.model_validate(payload)
    assert verify(mismatch, date(2099, 1, 1)).integrity_mismatch_ids == (
        "evidence-synthetic-control-gap",
    )


def test_seal_manifest_creates_canonical_hash() -> None:
    manifest = load_manifest()
    payload = manifest.hash_payload()
    sealed = seal_manifest(payload)
    assert sealed.declared_hash == manifest.declared_hash
