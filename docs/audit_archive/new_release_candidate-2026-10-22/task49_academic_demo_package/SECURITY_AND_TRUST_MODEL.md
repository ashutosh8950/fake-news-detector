# Security and Trust Model

## Trust boundaries

### Model artifacts

Inspected `predictor.py` verifies the configured artifact bundle through `artifact_contract.py` before calling `joblib.load`. This is a source-level safeguard. It is not historical authenticity: the required trusted manifest, independently provisioned expected digests, and production trust root remain unresolved in the prior audits. An unsigned or same-source manifest must not be treated as an independent trust anchor.

### Data provenance and licensing

Tasks 35–42 report that the local `Fake.csv` and `True.csv` acquisition chain, upstream identity, and downstream rights remain unresolved. Local hashes can establish consistency with a recorded file, not ownership, origin, or permission. Training, model distribution, public hosting, and raw-data redistribution require separate evidence and owner/legal decisions.

### Input and output handling

`routers/api.py` uses Pydantic request validation and minimum/maximum text constraints. `predictor.py` maps model outputs to Fake/Real labels and calibrated probabilities; those are model signals, not live fact verification. The frontend escapes displayed labels in relevant dynamic rendering paths, but public deployment still requires a broader security and privacy review.

### Fail-closed release controls

The candidate-only preflight and harness work is synthetic and refusal-oriented. Prior reports document checks for evidence binding, path isolation, and approval records, but real trust roots, owner approvals, licensing evidence, complete dependency locking, and a trusted candidate bundle do not exist. Synthetic passing tests do not authorize real-data training or artifact creation.

## Two release tracks

**Academic demonstration:** may present the inspected application as a software demonstration only if it does not imply that the historical bundle is authenticated or that reported metrics prove general factual accuracy. The isolated claim prototype may be shown as synthetic UI/contract work only.

**Public website:** remains blocked pending authenticated artifacts, dataset rights for the intended hosting context, security/privacy/deployment review, reproducible environment evidence, monitoring, owner authorization, and release approval.

## Known limitations

- Historical production artifact provenance is not established.
- Current dataset origin and licensing are not established.
- Dependency and language-model reconstruction is not a complete authenticated lock.
- Browser behavior for the static Track B mockup was not tested; Task 48 recorded a conditional pass for static/synthetic scope.
- Model metrics in README and prior reports are not an independently trusted benchmark for a new release.
- Python-level gates cannot prevent a local owner from editing code or invoking arbitrary internals.
