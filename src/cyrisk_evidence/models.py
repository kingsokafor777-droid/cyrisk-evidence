"""Strict payload-blind provenance, assumption, and review contracts."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from cyrisk_core.models import SourceClass
from pydantic import BaseModel, ConfigDict, Field, model_validator

ID_PATTERN = r"^[a-z][a-z0-9_-]{2,63}$"
HASH_PATTERN = r"^[a-f0-9]{64}$"


class EvidenceRecord(BaseModel):
    """Immutable strict payload-blind record."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class EvidenceExpectation(EvidenceRecord):
    """Caller-supplied expected and observed hashes; no payload is retained."""

    evidence_id: str = Field(pattern=ID_PATTERN)
    source_class: SourceClass
    expected_integrity_hash: str = Field(pattern=HASH_PATTERN)
    observed_integrity_hash: str | None = Field(default=None, pattern=HASH_PATTERN)
    expires_on: date
    description: str = Field(min_length=1, max_length=500)


class AssumptionRecord(EvidenceRecord):
    """An explicit bounded input assumption with a payload-blind evidence link."""

    assumption_id: str = Field(pattern=ID_PATTERN)
    factor_id: str = Field(pattern=ID_PATTERN)
    unit: str = Field(min_length=1, max_length=64)
    lower: Decimal = Field(ge=0)
    central: Decimal = Field(ge=0)
    upper: Decimal = Field(ge=0)
    source_class: SourceClass
    owner_reference: str = Field(min_length=1, max_length=120)
    rationale: str = Field(min_length=1, max_length=500)
    evidence_ids: tuple[str, ...] = Field(min_length=1)
    review_due_on: date
    expires_on: date

    @model_validator(mode="after")
    def validate_bounds_and_links(self) -> AssumptionRecord:
        if not self.lower <= self.central <= self.upper:
            raise ValueError("assumption bounds must satisfy lower <= central <= upper")
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("assumption evidence_ids must be unique")
        if self.review_due_on > self.expires_on:
            raise ValueError("review_due_on cannot be after expires_on")
        return self


class CalibrationReview(EvidenceRecord):
    """A recorded observation, explicitly not an authorization or approval decision."""

    review_id: str = Field(pattern=ID_PATTERN)
    assumption_id: str = Field(pattern=ID_PATTERN)
    reviewer_reference: str = Field(min_length=1, max_length=120)
    observed_on: date
    observation: str = Field(min_length=1, max_length=500)
    follow_up_required: bool
    authority_validated: bool = False

    @model_validator(mode="after")
    def forbid_authority_assertion(self) -> CalibrationReview:
        if self.authority_validated:
            raise ValueError("authority validation belongs to an authenticated downstream workflow")
        return self


class RegistryManifest(EvidenceRecord):
    """Sealed registry inventory; hash mismatch is reported by verifier, not hidden."""

    schema_version: str = Field(default="1.0", pattern=r"^\d+\.\d+$")
    registry_id: str = Field(pattern=ID_PATTERN)
    assumptions: tuple[AssumptionRecord, ...] = Field(min_length=1)
    evidence_expectations: tuple[EvidenceExpectation, ...] = Field(min_length=1)
    calibration_reviews: tuple[CalibrationReview, ...] = Field(default=())
    declared_hash: str = Field(pattern=HASH_PATTERN)

    @model_validator(mode="after")
    def validate_unique_references(self) -> RegistryManifest:
        assumption_ids = [record.assumption_id for record in self.assumptions]
        evidence_ids = [record.evidence_id for record in self.evidence_expectations]
        review_ids = [record.review_id for record in self.calibration_reviews]
        if len(assumption_ids) != len(set(assumption_ids)):
            raise ValueError("assumption_ids must be unique")
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("evidence_ids must be unique")
        if len(review_ids) != len(set(review_ids)):
            raise ValueError("review_ids must be unique")
        known_assumptions = set(assumption_ids)
        known_evidence = set(evidence_ids)
        unknown_review_assumption = any(
            record.assumption_id not in known_assumptions for record in self.calibration_reviews
        )
        if unknown_review_assumption:
            raise ValueError("review references unknown assumption_id")
        if any(
            evidence_id not in known_evidence
            for record in self.assumptions
            for evidence_id in record.evidence_ids
        ):
            raise ValueError("assumption references unknown evidence_id")
        return self

    def hash_payload(self) -> dict[str, object]:
        return self.model_dump(mode="json", exclude={"declared_hash"})


class VerificationReport(EvidenceRecord):
    """Deterministic technical verification result with no sufficiency or decision claim."""

    registry_id: str = Field(pattern=ID_PATTERN)
    as_of: date
    computed_hash: str = Field(pattern=HASH_PATTERN)
    declared_hash: str = Field(pattern=HASH_PATTERN)
    valid_evidence_ids: tuple[str, ...]
    expired_evidence_ids: tuple[str, ...]
    missing_observed_hash_ids: tuple[str, ...]
    integrity_mismatch_ids: tuple[str, ...]
    expired_assumption_ids: tuple[str, ...]
    limitations: str = Field(min_length=1, max_length=500)
