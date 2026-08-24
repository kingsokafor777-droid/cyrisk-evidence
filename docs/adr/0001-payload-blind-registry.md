# ADR 0001: Use payload-blind expectation records

**Status:** Accepted

The first release stores only IDs, hashes, source class, dates, metadata, and supplied review
observations. It does not store raw evidence payloads. This permits deterministic integrity and
expiry checks without creating a sensitive-evidence store, while keeping the open-source release
honest about its non-access to customer data.

Payload acquisition, encrypted retention, access control, legal hold, and evidence interpretation
remain deployer responsibilities outside this package.
