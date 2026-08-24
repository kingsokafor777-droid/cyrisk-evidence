from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from cyrisk_evidence.models import AssumptionRecord, CalibrationReview, VerificationReport
from cyrisk_evidence.verifier import seal_manifest


def expectation() -> dict[str, object]:
    return {
        "evidence_id": "evidence-one",
        "source_class": "synthetic",
        "expected_integrity_hash": "a" * 64,
        "observed_integrity_hash": "a" * 64,
        "expires_on": "2099-12-31",
        "description": "Synthetic expectation.",
    }


def assumption() -> dict[str, object]:
    return {
        "assumption_id": "assumption-one",
        "factor_id": "factor-one",
        "unit": "synthetic-unit",
        "lower": "1",
        "central": "2",
        "upper": "3",
        "source_class": "synthetic",
        "owner_reference": "synthetic-owner",
        "rationale": "Synthetic rationale.",
        "evidence_ids": ["evidence-one"],
        "review_due_on": "2098-01-01",
        "expires_on": "2099-12-31",
    }


def payload() -> dict[str, object]:
    return {
        "registry_id": "registry-one",
        "assumptions": [assumption()],
        "evidence_expectations": [expectation()],
        "calibration_reviews": [],
    }


def test_assumption_rejects_reversed_bounds() -> None:
    record = assumption()
    record["lower"] = "3"
    with pytest.raises(ValidationError, match="lower <= central <= upper"):
        AssumptionRecord.model_validate(record)


def test_assumption_rejects_duplicate_or_unknown_evidence_links() -> None:
    record = assumption()
    record["evidence_ids"] = ["evidence-one", "evidence-one"]
    with pytest.raises(ValidationError, match="must be unique"):
        AssumptionRecord.model_validate(record)
    registry = payload()
    registry["assumptions"][0]["evidence_ids"] = ["missing-evidence"]  # type: ignore[index]
    with pytest.raises(ValidationError, match="unknown evidence"):
        seal_manifest(registry)


def test_assumption_rejects_review_due_after_expiry() -> None:
    record = assumption()
    record["review_due_on"] = "2100-01-01"
    with pytest.raises(ValidationError, match="cannot be after"):
        AssumptionRecord.model_validate(record)


def test_review_rejects_authority_assertion_and_unknown_assumption() -> None:
    with pytest.raises(ValidationError, match="authority"):
        CalibrationReview(
            review_id="review-one",
            assumption_id="assumption-one",
            reviewer_reference="synthetic-reviewer",
            observed_on=date(2097, 1, 1),
            observation="Synthetic observation.",
            follow_up_required=False,
            authority_validated=True,
        )
    registry = payload()
    registry["calibration_reviews"] = [
        {
            "review_id": "review-one",
            "assumption_id": "missing-assumption",
            "reviewer_reference": "synthetic-reviewer",
            "observed_on": "2097-01-01",
            "observation": "Synthetic observation.",
            "follow_up_required": False,
        }
    ]
    with pytest.raises(ValidationError, match="unknown assumption"):
        seal_manifest(registry)


def test_registry_rejects_duplicate_ids() -> None:
    registry = payload()
    registry["evidence_expectations"].append(expectation())  # type: ignore[index]
    with pytest.raises(ValidationError, match="evidence_ids must be unique"):
        seal_manifest(registry)


def test_registry_rejects_duplicate_assumption_and_review_ids() -> None:
    registry = payload()
    registry["assumptions"].append(assumption())  # type: ignore[index]
    with pytest.raises(ValidationError, match="assumption_ids must be unique"):
        seal_manifest(registry)
    registry = payload()
    review = {
        "review_id": "review-one",
        "assumption_id": "assumption-one",
        "reviewer_reference": "synthetic-reviewer",
        "observed_on": "2097-01-01",
        "observation": "Synthetic observation.",
        "follow_up_required": False,
    }
    registry["calibration_reviews"] = [review, review]
    with pytest.raises(ValidationError, match="review_ids must be unique"):
        seal_manifest(registry)


def test_report_accepts_ordered_lists_and_limitations() -> None:
    report = VerificationReport(
        registry_id="registry-one",
        as_of=date(2099, 1, 1),
        computed_hash="a" * 64,
        declared_hash="b" * 64,
        valid_evidence_ids=(),
        expired_evidence_ids=(),
        missing_observed_hash_ids=(),
        integrity_mismatch_ids=(),
        expired_assumption_ids=(),
        limitations="Synthetic technical report only.",
    )
    assert report.registry_id == "registry-one"
