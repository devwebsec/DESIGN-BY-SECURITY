# Semantic Security Design Evaluation

This harness validates the **relationships between security-design artifacts**, not merely the presence of keywords.

## Model

`THREAT → REQUIREMENT → CONTROL → VALIDATION`

and

`ATTACK PATH → DETECTION → RESPONSE → OPERATIONAL HANDOFF`

The evaluator also enforces the pipeline hard-fail conditions declared in `pipeline-manifest.yml`.

## Scope

- Deterministic, offline, CI-safe validation.
- JSON fixtures represent a normalized Security Design artifact set.
- No LLM call and no production security action is performed.
- Negative fixtures intentionally violate one invariant each and must fail.

## Run

```bash
python3 tests/security-design-pipeline/semantic/evaluate.py \
  tests/security-design-pipeline/semantic/fixtures/valid-web-api.json \
  tests/security-design-pipeline/semantic/fixtures/negative
```

The command exits non-zero if the valid fixture fails or if any negative fixture does not fail.
