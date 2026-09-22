# SB-V13-002 metric provenance and compatibility review

State **READY_FOR_LEAD_REVIEW / RECOMMEND_ACCEPT** for bounded engineering only. Draft [PR13](https://github.com/pri8771/astra-bot-launch/pull/13). This packet requests an exact-SHA ChatGPT lead verdict; it is not formal acceptance.

Native `LEAD-058@f822070` released this offline adversarial audit from accepted engineering base `3f10d0f6eb031c00fff679aae18aa8045d8bd025`. Candidate source is `be0262713eec03c2e7e6b411c2754a7538bad9a6`, tree `f572da02fcbc60bfeb4d6f620e96aeea43193501`.

Synthetic accepted-base diagnostics reproduced four trust failures: invalid sources were persisted/traced/aggregated; reversed windows were persisted and influenced delta aggregation; invented legacy kinds were aggregated; and legacy claims promoted TikTok-unsupported reach or X-unmapped likes. An offset regression verifies latest selection by actual aware instant rather than ISO text.

The repair validates attributable nonblank string sources, aware collection time, optional aware window boundaries, and chronological complete windows before fresh persistence, derivation, trace and aggregation. Persisted PRESENT metrics require a declared kind and exact platform raw-name-to-semantic mapping. Invalid legacy rows remain verbatim in `observations_for`, appear as excluded trace evidence, and increment aggregate invalid counts without numeric contribution.

Valid `raw_kinds` overrides remain supported because validation accepts any declared kind without forcing the platform default. Optional/no-window and end-only snapshots remain supported; deltas without complete windows remain excluded. Finite-number behavior is unchanged. Valid content, experiment, persona, account, platform, source and window identity remains retained.

Final focused checks passed **43/43**. The superseding full suite ran **756**, with **754 passed and 2 existing genuine-live skips**, in **3.638s**. The earlier 752-test result predates the legacy kind/mapping closure. Raw diagnostics, root repeats, red logs and final logs are retained here.

All evidence is synthetic/local and supports engineering review only. It does not prove live analytics, accounts, providers, public effects, scheduler/host operation, measurement windows, or V1.3 completion. Requested action: formal exact-SHA engineering verdict for `SB-V13-002` at `be0262713eec03c2e7e6b411c2754a7538bad9a6`; do not promote the live product version.

Root independently repeated both legacy-kind and mapping reproductions on clean accepted3f10d0f after the final repair. The four-case legacy module against that accepted source has four intended failing assertions across three test methods, plus one compatibility error because its positive test references the newly added invalid counter. That counter error is not a product defect; a separate accepted-source probe confirms the valid GAUGE override and numeric value9 remain supported. The earlier partial-candidate diagnostics remain retained with their observed normalization version. Root authored the source repair; bounded agents supplied disjoint regressions and mechanical review, not formal acceptance.
