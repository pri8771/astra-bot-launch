# Windows primary development readiness

12 September 2026. Owner asks to make the always-on Windows desktop the main development machine and wants the shortest path to useful work. This is separate from proving a fully autonomous fleet.

## Live preparation

Host: DESKTOP-H5S6H41, operated through the existing TeamViewer session from the Mac. Hardware is in HARDWARE_PLACEMENT_AUDIT.md; it was not reinventoried here.

- Found Git, GitHub CLI, Node, Python, Ollama, Claude, Gemini, Cursor and the WSL command. Codex CLI was not found in this PATH check; this does not prove no desktop app exists.
- Python reports 3.11.9; Node reports v24.19.0; Ollama reports 0.33.2.
- Claude auth status reports loggedIn=true using claude.ai, subscriptionType=max. This is an auth check, not a successful inference or a billing claim. No Claude model invocation was performed.
- GitHub CLI reports no logged-in host, but noninteractive Git could read the BOTS remote HEAD and clone it. Do not confuse missing gh authentication with inability to read this repository; push/PR access remains unverified.
- Created a new checkout at `D:/Astra/repos/bots` from `https://github.com/pri8771/bots.git`. Readback: clean `main...origin/main`, HEAD `d5b3b7f399b8d3e3ba4b926d0d89f30aacac6e11` at host UTC `2026-09-12T18:06:58.5353467Z`.
- Available disk space was approximately 126 GB on C: and 1,798 GB on D:. This is a snapshot, not reserved capacity.
- WSL list returned installer/help output and status yielded no usable distro evidence. No working WSL distribution is established. No WSL installation or reboot was attempted.
- Official Ollama `qwen3.5:4b` downloaded successfully and passed the two bounded synthetic cases below. No unattended worker qualification is implied.

An initial command contained malformed Windows path escapes and failed with illegal-path/invalid-argument errors. It created no reported working tree. The corrected forward-slash path cloned successfully; final revision/status above are the actual result. Use forward-slash paths or correctly encoded transfer payloads for remote PowerShell entry.

## Development and unattended operation are separate milestones

1. **Windows development:** local source, compatible dependencies, authenticated chosen executor, a fully specified task, isolated branch/worktree and saved output/review packet. Current source clone and language versions cover only part of this milestone. Start with BOTS/OPO rather than migrating every project at once.
2. **Local reasoning:** a small bounded model test with actual responses, telemetry and GPU placement. No tools, external messages, account actions or paid fallback in the smoke test. Success does not qualify autonomous business judgment.
3. **Unattended execution:** a supported Windows worker with durable ownership, finite timeouts, process-tree cleanup, restart recovery and verified Mac-disconnected operation. Existing platform-specific code cannot be copied and called ready.
4. **OPO pilot:** revised Jira contracts through the sole writer, confirmed domain/public host, durable message storage, one logged exchange, then a small measured social-channel experiment. Existing historical repo instructions must not override the latest owner changes.

## Existing code findings

The manual SQLite claim/receipt prototype in `tooling/manual_dispatch/manual_dispatch.py` and context helpers are reuse candidates for an isolated synthetic diagnostic, not a proven multi-host ownership service. Its README calls it a one-Mac cooperative ledger with no automatic reclaim.

`tooling/manual_dispatch/run_queue.py` uses POSIX process-group controls; `tooling/dispatch_service/engine.py` and `supervisor.py` import fcntl and use POSIX locks/process groups. A native Windows supervised-runner path needs qualification, or an actually working Linux environment must be established. Preserve a single authoritative Jira writer and reconcile uncertain effects before any takeover.

The old September 6 coordinator archive is historical preparation material. Do not dispatch its old Jira counts, write instructions or frozen work list as current work. The latest mission/account/host plan is in this directory; source-transfer artifacts do not carry live auth or replace task admission.

## Working estimates, not recorded effort

- First bounded Windows development task: roughly 1–2 hours of active setup/qualification if executor and task access remain available.
- Unattended execution/recovery qualification: roughly another half-day of active work, subject to the platform-specific runner gap.
- OPO public pilot: estimate after confirming the actual host/storage route and revised Jira scope; domain/account waits cannot be promised away.

These are provisional elapsed-work estimates for sequencing, not changes to original Jira estimates, completed effort, a scheduled promise or a statement that jobs continue after this chat stops. Paid development IDE sessions need not wait for local-model tuning. Additional workers should be admitted only after one full task/result/review cycle works on Windows.

## Local-model smoke-test receipt

Completed on Windows at 2026-09-12T18:16:40/41Z. Raw requests/responses and `summary.json` persist at `D:/Astra/pilots/local-smoke-20260912-1812/`. Both `missing_url` and `provided_url` passed, returning needs_input=true and false respectively. Both returned model identifiers were separately checked as `qwen3.5:4b`; the script's boolean assertion alone does not enforce model identity.

Observed local Ollama telemetry: 60+62 input tokens, 11+11 generated tokens; total request durations 4.0017146s cold and 0.1839394s warm. `ollama ps` showed 100% GPU, 2048 context and approximately 3.1GB. Exact source at `D:/Astra/control/windows_smoke.ps1` matched SHA-256 `41bd67ed3ec9dee029a2ea2199d0804675b962b885a7dd0a12ce18745349f8b4`. The Mac copy is `windows_smoke.ps1` beside this document.

These are synthetic no-tool tests with a 2048-token context and 48-token output bound. They do not prove autonomous Jira writing, business judgment, different-model product review, process recovery or Mac-disconnected operation. No paid model was invoked by this diagnostic.

## Sources and review

- [Official model package](https://ollama.com/library/qwen3.5:4b), approximately 3.4 GB, Q4_K_M at inspection.
- [Ollama chat API](https://docs.ollama.com/api/chat), local structured response, explicit context/output bounds and telemetry.
- compact_task_packets completed a bounded read-only portability review; root independently confirmed the POSIX calls/imports. This is a same-model source assessment, not distinct-model product approval.

## Revision transcription correction

Windows PowerShell HEAD was re-read at approximately 18:44 UTC as `d5b3b7f399b8d3e3ba4b926d0d89f30aacac6e11`, matching the GitHub/local-origin SHA. The earlier note had a single-character transcription error; it was not evidence of a different Windows checkout. Cursor GUI command exists in Windows PATH; `agent` and `antigravity` did not appear in that same targeted command lookup.
