# Architecture

The package is a pure local contract and verification boundary. Input is a JSON registry and output
is a typed `VerificationReport`; no database, cloud SDK, network client, scheduler, or background
worker is included.

| Stage | Deterministic operation | Boundary |
|---|---|---|
| Input | Caller supplies a `RegistryManifest` and explicit ISO date. | No evidence collection or wall-clock default. |
| Seal | Canonical hash includes validated defaults. | Hashing does not prove source truth. |
| Verify | Checks declared/observed hash metadata and expiry. | Does not inspect a payload. |
| Report | Emits sorted identifiers and a limitation statement. | Does not approve an assumption or decide risk. |

Malformed records, duplicate identifiers, a false `authority_validated` assertion, invalid digest,
or invalid date are rejected. A manifest mismatch is reported rather than recovered or silently
replaced.
