# Contributing

Do not add raw customer evidence, credentials, live URLs, cloud account identifiers, real incident
data, wall-clock state, or unsealed source content. Use synthetic fixtures with payload-blind IDs
and declared digests only. Every new rule needs deterministic tests and must preserve the distinction
between a metadata check and validation of real-world truth or authority.

Run `make check` before proposing a change. Do not reduce the coverage gate or replace caller-supplied dates with the current date.
