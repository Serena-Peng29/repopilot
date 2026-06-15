# AgentPatchBench Arena Report

## Summary

- Total cases: 2
- Total runs: 2
- Passed: 2
- Pass rate: 100.0%
- Average latency: <1s

### Provider Summary

| Provider | Runs | Passed | Pass Rate | Avg Latency | Avg Changed Lines | High Risk Runs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| demo | 2 | 2 | 100.0% | <1s | 2.0 | 0 |

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
