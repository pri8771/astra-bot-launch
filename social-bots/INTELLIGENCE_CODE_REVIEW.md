# Intelligence-side lead code review — pre-lane findings

Reviewed implementation head: 2a53046f10ed284f6e4164a78c47bbf750aad73d.

## Finding A — analytics aggregation semantics are unsafe for snapshots

Current `analytics.aggregate()` simply sums numeric values across matching events.

If platform observations are cumulative snapshots (for example 100 views, later 150 views), summing to 250 is wrong.

Required direction for SB-V13-001:
- metric record declares semantic kind: cumulative_snapshot / delta / gauge / rate;
- aggregation is semantic-aware;
- missing != zero;
- retain raw platform metric name/value;
- derived metrics include formula/version.

This is a lead finding, not a worker defect yet because V1.3 has not been implemented.

## Finding B — fact review remains URL-presence only

Current `pipeline.fact_check()` passes if a source ref exists.

SB-V05-002 must replace this with claim-to-evidence support classification.

## Finding C — platform formatting silently truncates text

`format_for_platform()` returns truncated text but `within_limit=false` based on original text.

The V0.3 decision gate now withholds the candidate, so current safety is fail-closed. V1.6 content intelligence should repair/regenerate platform-native copy instead of treating truncation as a valid final candidate.

## Finding D — experiment baseline is not a usable measured baseline

Current experiment creation stores a string-like unknown baseline. That is honest for pre-publication scaffolding, but V1.5 must use typed baseline semantics and INCONCLUSIVE closeout if required observations do not arrive.

## Finding E — audience hypotheses currently live in bot state, not persona scope

Current BotState hypotheses are bot-scoped. This intersects SB-V03-005 persona isolation and V1.4 audience memory. The final model must prevent a cultural persona and general persona on one runtime from silently learning into the same private audience hypothesis namespace.

## Finding F — duplicate detection is persona-aware in key, storage is bot-shared

Current content_key includes persona, which helps, but bot-shared history still requires persona-aware readers/filters for future community/content learning. V1.6 should make scoping explicit.
