"""Deterministic payload-blind registry sealing and explicit-date verification."""

from __future__ import annotations

from datetime import date

from cyrisk_core.canonical import content_hash

from cyrisk_evidence.models import RegistryManifest, VerificationReport

LIMITATIONS = (
    "Technical metadata, supplied hash, and expiry check only; not proof of source truth, "
    "completeness, authority, calibration, or decision suitability."
)


def seal_manifest(payload: dict[str, object]) -> RegistryManifest:
    """Create a manifest with canonical declared hash from a payload excluding that hash."""
    provisional = RegistryManifest.model_validate(
        {"schema_version": "1.0", **payload, "declared_hash": "0" * 64}
    )
    canonical_payload = provisional.hash_payload()
    sealed = {**canonical_payload, "declared_hash": content_hash(canonical_payload)}
    return RegistryManifest.model_validate(sealed)


def verify(manifest: RegistryManifest, as_of: date) -> VerificationReport:
    """Evaluate supplied integrity and expiry metadata at a caller-provided date."""
    computed_hash = content_hash(manifest.hash_payload())
    valid: list[str] = []
    expired: list[str] = []
    missing: list[str] = []
    mismatch: list[str] = []
    for expectation in manifest.evidence_expectations:
        if expectation.expires_on < as_of:
            expired.append(expectation.evidence_id)
        elif expectation.observed_integrity_hash is None:
            missing.append(expectation.evidence_id)
        elif expectation.observed_integrity_hash != expectation.expected_integrity_hash:
            mismatch.append(expectation.evidence_id)
        else:
            valid.append(expectation.evidence_id)
    expired_assumptions = sorted(
        record.assumption_id for record in manifest.assumptions if record.expires_on < as_of
    )
    return VerificationReport(
        registry_id=manifest.registry_id,
        as_of=as_of,
        computed_hash=computed_hash,
        declared_hash=manifest.declared_hash,
        valid_evidence_ids=tuple(sorted(valid)),
        expired_evidence_ids=tuple(sorted(expired)),
        missing_observed_hash_ids=tuple(sorted(missing)),
        integrity_mismatch_ids=tuple(sorted(mismatch)),
        expired_assumption_ids=tuple(expired_assumptions),
        limitations=LIMITATIONS,
    )
