# Session log — 2026-07-23

## Goal

Map the Ingot × CARN competitive field, identify defensible mechanisms, and
implement the smallest measured, live-path capability-cache slices.

## Why

Ingot already governs versioned Agent Skills. CARN already explores
deterministic replay. The missing product boundary is a safe route from fuzzy
capability discovery to exact, validated execution reuse without weakening
Ingot's human evidence gate.

## Decisions

- Ingot remains the activation and governance plane; CARN remains the
  execution record/replay/compiler plane.
- `route_and_load` remains the sole serving-selection contract.
- Body-aware retrieval is the first implementation slice because the strongest
  routing evidence shows full skill bodies materially affect selection.
- Semantic similarity may nominate replay candidates but never authorize
  side effects. Exact compatibility fingerprints and node validators are
  required.
- AGPL-3.0 and unlicensed sources are idea-only. Implementation is clean-room.
- Defensibility comes from permissioned compatibility and outcome evidence,
  not from cache mechanics.

## Artifacts

- `docs/ingot-carn_ATLAS.md` — competitor map, architecture decision, take
  ledger, moat, kill conditions, and follow-through tracker.
- `analysis/ingot-carn_index.jsonl` — normalized discovery index.
- `analysis/ingot-carn_dossiers.jsonl` — deep-read target dossiers.

## Verification

Initial focused test attempt:

```text
python -m pytest -q tests/test_router.py tests/test_routing_eval.py
```

Collection succeeded, but the local interpreter lacks `onnxruntime`; 16 tests
failed and 4 errored before router execution. This is an environment baseline,
not a product regression. Use the repository's container or install the pinned
runtime before claiming deterministic green.
