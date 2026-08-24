# Threat Model

| Threat | Example | Mitigation and boundary |
|---|---|---|
| Raw-evidence leakage | A fixture embeds a cloud export. | The contract permits only IDs and SHA-256 metadata. |
| Time ambiguity | A stale estimate looks current. | A caller supplies `as_of`; expiry is explicit. |
| Silent substitution | Digest changes after review. | Expected and observed values are compared deterministically. |
| Authority overstatement | An observation is treated as approval. | `authority_validated=true` is rejected. |
| False sufficiency claim | Metadata status is presented as audit evidence. | Report limitations describe the narrow technical semantics. |
