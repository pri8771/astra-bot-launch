# Evidence and reference index

## Current source review

- Canonical: pri8771/astra-bot-launch@2cda05b4d0144687ca842ac4fe104aa3824e6039.
- Fable: fable/social-bots-v23-fasttrack-20260921@72a55319cf41f9910c5d3b9623129de3ac0eea31.
- Cursor: cursor/social-bots-recovery-v07-20260921@74a515b7f3e30c94979e0f66dc6daae66daed571.
- Independent QA branch observed: claude/social-bots-mac-qa-control@d57a10459dc441e94015168801254771d8e96b1a.
- Inspected paths: runtime/reasoning.py, runtime/specialist_budget.py, runtime/specialist_integrator.py, runtime/specialist_lifecycle.py, runtime/strategy.py; current lead/worker reports, heartbeat and milestone contracts.
- Full source SHA/blob evidence and review scope: reviews/LEAD047_AUDIT.md, reviews/LEAD047_PROBES.json.

## Patch provenance

Original attachment SHA-256 a200dcb3f1129fae6a4e8ded0f3472ab8a8979847a0d45eca19e06a6030e121c. See IMPORT.md. Historical baseline eeb4a39a9bcd813d8ca691db142851206129bf50 is preserved only as provenance, not current runtime truth.

## Primary technical references

Python 3.11 concurrent.futures documentation: https://docs.python.org/3.11/library/concurrent.futures.html . A running future is not stopped by ordinary cancellation. Use a tested supervision boundary for hard deadlines.

Python os.replace documentation: https://docs.python.org/3/library/os.html#os.replace . File replacement behavior is not a multi-file transaction or no-overwrite guarantee.

SQLite WAL constraints: https://www.sqlite.org/wal.html . Any storage change must be justified and tested on supported local deployment; no speculative multi-host database migration.

At implementation/deployment, verify the installed coding-client version and its supported headless/sandbox/authentication behavior from current official provider documentation. Do not derive model identifiers, effort labels or free entitlements from old prose.
