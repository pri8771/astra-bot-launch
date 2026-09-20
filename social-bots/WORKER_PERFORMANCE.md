# Claude worker performance

Purpose: measure Claude Code's implementation reliability by story-point size and task type. Story points are complexity/uncertainty, not time.

No task is counted as accepted until ChatGPT lead verifies the stated acceptance evidence.

## Summary

No statistically meaningful conclusions yet. Existing pre-contract work is not retroactively scored unless the task boundary and acceptance evidence are clear enough to do so honestly.

## Task results

| Task | SP | Type | First attempt | Independent evidence | Review findings | Repair cycles | Accepted | Notes |
|---|---:|---|---|---|---|---:|---|---|
| SB-R0A1 | 3 | signal/state correctness | pending | pending | pending | 0 | no | next ready worker task |
| SB-R0A2 | 2 | gating/regression | pending | pending | pending | 0 | no | may be done after or alongside A1 if file ownership is safe |
| SB-R0B1 | 5 | concurrency/fencing | pending | pending | pending | 0 | no | decompose/design readback expected |
| SB-R0B2 | 4 | state/lease architecture | pending | pending | pending | 0 | no | shared-runtime concurrency |
| SB-R0B3 | 3 | adversarial integration test | pending | pending | pending | 0 | no | final V0.3 concurrency acceptance |

## Metrics to accumulate

For each SP level:
- attempts;
- first-pass accepted;
- first-pass partial;
- first-pass failed;
- average repair cycles (descriptive only, not time);
- escaped defects discovered later;
- task-definition ambiguity incidents;
- access/evidence blockers.

Do not infer worker quality from one task. Track patterns over multiple comparable tasks.
