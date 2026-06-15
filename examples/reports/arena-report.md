# AgentPatchBench Arena Report

## Summary

- Total cases: 8
- Total runs: 8
- Passed: 8
- Pass rate: 100.0%
- Average latency: <1s

### Provider Summary

| Provider | Runs | Passed | Pass Rate | Avg Latency | Avg Changed Lines | High Risk Runs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| demo | 8 | 8 | 100.0% | <1s | 3.1 | 0 |

## Case Results

### sample-addition-bug

- Recommended provider: demo

| Provider | Adapter | Model | Tests | Risk | Changed Files | Diff | Time | Recommendation |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| demo | native |  | pass | low | 1 | +1/-1 | <1s | best |

#### demo Details

- Status: tests_passed
- Trace: `examples/run-artifacts/trace.json`
- Patch: `examples/run-artifacts/patch.diff`
- Risk reasons: small focused patch

### sample-multiply-bug

- Recommended provider: demo

| Provider | Adapter | Model | Tests | Risk | Changed Files | Diff | Time | Recommendation |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| demo | native |  | pass | low | 1 | +1/-1 | <1s | best |

#### demo Details

- Status: tests_passed
- Trace: `examples/run-artifacts/trace.json`
- Patch: `examples/run-artifacts/patch.diff`
- Risk reasons: small focused patch

### sample-divide-bug

- Recommended provider: demo

| Provider | Adapter | Model | Tests | Risk | Changed Files | Diff | Time | Recommendation |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| demo | native |  | pass | low | 1 | +1/-1 | <1s | best |

#### demo Details

- Status: tests_passed
- Trace: `examples/run-artifacts/trace.json`
- Patch: `examples/run-artifacts/patch.diff`
- Risk reasons: small focused patch

### sample-slugify-bug

- Recommended provider: demo

| Provider | Adapter | Model | Tests | Risk | Changed Files | Diff | Time | Recommendation |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| demo | native |  | pass | low | 1 | +4/-1 | <1s | best |

#### demo Details

- Status: tests_passed
- Trace: `examples/run-artifacts/trace.json`
- Patch: `examples/run-artifacts/patch.diff`
- Risk reasons: small focused patch

### sample-csv-parser-bug

- Recommended provider: demo

| Provider | Adapter | Model | Tests | Risk | Changed Files | Diff | Time | Recommendation |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| demo | native |  | pass | low | 1 | +1/-1 | <1s | best |

#### demo Details

- Status: tests_passed
- Trace: `examples/run-artifacts/trace.json`
- Patch: `examples/run-artifacts/patch.diff`
- Risk reasons: small focused patch

### sample-config-default-bug

- Recommended provider: demo

| Provider | Adapter | Model | Tests | Risk | Changed Files | Diff | Time | Recommendation |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| demo | native |  | pass | low | 1 | +1/-1 | <1s | best |

#### demo Details

- Status: tests_passed
- Trace: `examples/run-artifacts/trace.json`
- Patch: `examples/run-artifacts/patch.diff`
- Risk reasons: small focused patch

### sample-dedupe-order-bug

- Recommended provider: demo

| Provider | Adapter | Model | Tests | Risk | Changed Files | Diff | Time | Recommendation |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| demo | native |  | pass | low | 1 | +7/-1 | <1s | best |

#### demo Details

- Status: tests_passed
- Trace: `examples/run-artifacts/trace.json`
- Patch: `examples/run-artifacts/patch.diff`
- Risk reasons: small focused patch

### sample-temperature-bug

- Recommended provider: demo

| Provider | Adapter | Model | Tests | Risk | Changed Files | Diff | Time | Recommendation |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| demo | native |  | pass | low | 1 | +1/-1 | <1s | best |

#### demo Details

- Status: tests_passed
- Trace: `examples/run-artifacts/trace.json`
- Patch: `examples/run-artifacts/patch.diff`
- Risk reasons: small focused patch
