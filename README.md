# Cyrisk Evidence

> **Payload-blind provenance and assumption governance for Cyrisk inputs—not evidence collection, validation, or authorization.**

`cyrisk-evidence` records bounded input assumptions, content-addressed payload-blind evidence
references, integrity expectations, supplied-time expiry status, and calibration-review observations.
It builds on [`cyrisk-core` v0.1.0](https://github.com/kingsokafor777-droid/cyrisk-core/releases/tag/v0.1.0)
and is deliberately local-first.

## Scope boundary

The library does not retrieve cloud data, retain raw evidence, authenticate a reviewer, validate a
source, establish legal/regulatory sufficiency, calibrate a factor, approve an assumption, or
accept risk. It deterministically evaluates caller-provided records at an explicit `as_of` date.
`valid` means only that required metadata and the declared integrity value were present and not
expired by that supplied date.

> An integrity match is not proof that a source is true, complete, authorized, or suitable for a decision.

| Record | Purpose | Explicit non-claim |
|---|---|---|
| `AssumptionRecord` | Binds an input range to source class, owner reference, dates, and evidence IDs. | Does not establish estimate correctness. |
| `EvidenceExpectation` | Binds an ID to expected and observed SHA-256 values. | Does not retain or inspect a payload. |
| `CalibrationReview` | Records a supplied reviewer observation. | Does not validate authority or approve calibration. |
| `RegistryManifest` | Seals an inventory with canonical hashing. | Does not constitute an audit opinion. |
| `VerificationReport` | Reports valid, expired, missing, or mismatched metadata at supplied time. | Does not make a risk, financial, or compliance decision. |

```bash
make bootstrap
make check
cyrisk-evidence verify fixtures/synthetic_evidence_registry.json --as-of 2099-01-01
```

NIST positions cybersecurity risk information and risk registers as inputs to broader enterprise
risk-management processes, rather than replacements for leadership decisions. [1] [2]

## References

[1]: https://csrc.nist.gov/pubs/ir/8286/r1/final "NISTIR 8286 Rev. 1"
[2]: https://csrc.nist.gov/pubs/ir/8286/a/r1/final "NISTIR 8286A Rev. 1"
