# Task 25 — Dependency Lock Gap

**Status:** Incomplete lock; exact installed-environment snapshot only.

The candidate workspace contains `venv_freeze_all.txt`, an exact `pip freeze --all` snapshot of the existing `.venv` at inspection time. It is not a secure lockfile because it does not provide verified hashes for every package artifact, an offline wheelhouse, a complete platform marker policy, or a separately authenticated source for the packages.

The installed `en_core_web_sm` distribution exposes a direct URL and a SHA-256 value in its local `direct_url.json`, and the freeze output preserves that reference. The hash was not independently recomputed from the installed model package or verified against a retained wheel, so it is recorded as metadata-only rather than as an artifact-integrity proof.

The local pip cache contains HTTP cache files but no locally built wheels. The cache was not treated as an offline package source or as authenticated package artifacts.

## Missing evidence before a defensible lock

- Exact package wheel or source artifact for every pinned distribution.
- Verified SHA-256 hashes for every retained artifact.
- A controlled offline wheelhouse or trusted package index snapshot.
- Python/platform markers and compatibility decisions for all distributions.
- A separately retained and verified `en_core_web_sm` wheel, with its source and hash.
- A reproducible installation procedure tested without network access.
- Organization-controlled authentication of the lock and retained artifacts.

## Proposed later method

From the approved `.venv`, create a clean candidate environment using a reviewed lock-generation tool, resolve all direct and transitive dependencies for the target Python/platform, retain the exact package artifacts in a controlled wheelhouse, compute hashes from those artifacts, and test installation with network access disabled. Record the spaCy model wheel separately if the selected lock format cannot represent it. Review and authenticate the resulting lock, wheelhouse index, and model package record as part of the new-release trust process.

No lock was generated here, and no package or model was installed or downloaded.
