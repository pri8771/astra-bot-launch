# Social Bots artifact-oriented management contract

Established 2026-09-20 by ChatGPT lead.

## Core rule

The durable unit of project management is an artifact, not a task, chat message, checklist line, or claimed percentage complete.

Tasks are temporary instructions used to create, repair, review, verify, deploy, or supersede artifacts.

A task may close only when its required artifact state is reached and evidenced.

Examples of artifacts:
- source-code module or patch set;
- test/acceptance suite;
- persona contract;
- research-capture receipt bundle;
- decision/reasoning contract;
- account map;
- deployment package;
- host heartbeat/receipt bundle;
- PR;
- independent review;
- operating runbook;
- experiment definition/result;
- milestone acceptance manifest.

## Why artifact-first

This project uses multiple agents and long-running work. Conversation state is replaceable and task prose becomes stale.

Artifacts provide:
- durable source of truth;
- inspectable evidence;
- explicit ownership;
- dependency tracking;
- independent acceptance;
- resumability;
- version/milestone composition;
- clean handoff between ChatGPT lead and Claude worker.

## Artifact registry

Canonical machine-readable registry: ARTIFACT_INDEX.json.

Every material artifact has:
- stable artifact ID;
- name;
- type;
- target version/milestone;
- owner;
- status;
- canonical source/path/ref;
- dependencies;
- story points for the implementation/repair packet when applicable;
- acceptance criteria;
- evidence refs;
- last verified time/ref;
- supersession relationship where relevant.

The registry contains safe metadata only. No credentials, private identity mapping, cookies or sensitive redirect URLs.

## Artifact status lifecycle

Allowed statuses:
- PLANNED
- READY
- IN_PROGRESS
- SUBMITTED
- CHANGES_REQUIRED
- ACCEPTED
- BLOCKED
- SUPERSEDED
- WITHHELD

Do not use DONE as a substitute for ACCEPTED.

## Artifact IDs

Format: SB-<area>-<number>.

Current area prefixes:
- CTL — control/project contracts.
- V03 — V0.3 runtime correctness/foundation.
- V04 — V0.4 autonomous thinking.
- V05 — V0.5 research/review.
- V06 — V0.6 dry-run proof.
- V07 — V0.7 always-on loop.
- ACC — account/browser/platform connectivity.
- PER — personas/cultural workspaces.
- EVD — evidence/review bundles.

IDs remain stable even if paths move.

## Artifact packet

A worker packet should name the artifact(s) it owns and contain:
- Artifact ID.
- Goal.
- Current source/base ref.
- Owned paths.
- Dependencies.
- Story points.
- Required change.
- Acceptance tests.
- Required evidence.
- Explicit non-goals/authority limits.
- Expected artifact status on return.

Claude should not receive vague "work on V0.4" prompts when the work can be expressed as one or more artifact packets.

## Artifact completion record

Every material submitted artifact should carry or reference:
- What changed.
- Why.
- Source/base ref.
- Exact resulting ref/hash.
- Tests run.
- Test results.
- Independent review where required.
- Limits/unknowns.
- External effect status.
- Next dependent artifact(s).

Hidden chain-of-thought is never an artifact requirement. Decision artifacts record concise rationale and alternatives, not private reasoning traces.

## Acceptance

Claude may submit artifacts; Claude does not self-accept milestone artifacts.

ChatGPT lead:
1. inspects source/evidence;
2. reproduces/checks where appropriate;
3. records findings;
4. marks the artifact ACCEPTED, CHANGES_REQUIRED, BLOCKED, or WITHHELD;
5. unlocks dependent artifacts.

Tests passing alone do not imply artifact acceptance.

## Milestone manifests

Canonical milestone composition: MILESTONE_MANIFEST.md.

A version is promoted only when every required artifact in that milestone's manifest is accepted, except artifacts explicitly classified as future/external gates by that milestone contract.

Status of versions is therefore derived from artifacts, not manually declared.

## Lead / worker boundary under artifact-first management

Claude owns implementation artifacts, source changes, tests, routine repair, host setup, supported browser/account preparation within authority, execution receipts, and artifact submission/readback.

ChatGPT lead owns artifact decomposition, product/version manifests, acceptance criteria, source/repo research, independent review, defect discovery, hard-debugging investigations that unblock the worker, artifact status acceptance, and future artifact grooming.

When lead-side current work is exhausted, ChatGPT should create/groom useful future artifacts from the roadmap and prepare their acceptance contracts without implementing Claude-owned source changes.

## Story points and artifacts

Story points apply to worker packets that produce/repair artifacts, not to the artifact's business value.

Track worker performance against artifact packets in WORKER_PERFORMANCE.md.

A large artifact can be produced through several smaller packets. The final artifact remains one stable ID or an explicitly composed artifact bundle.

## Work queue relationship

WORK_QUEUE.md remains an execution view.

It should increasingly reference artifact IDs and current artifact status rather than duplicate all durable artifact metadata.

If WORK_QUEUE.md, chat text and ARTIFACT_INDEX.json disagree, investigate and reconcile; do not silently choose the most convenient status.

## Artifact-oriented heartbeat

At each ChatGPT heartbeat:
1. inspect changed/submitted artifacts;
2. verify evidence;
3. update artifact statuses;
4. update worker performance for reviewed worker packets;
5. unlock/decompose next artifacts;
6. keep Claude's ready artifact queue stocked;
7. if worker activity is absent, work ahead on non-overlapping future artifacts, reviews, research or acceptance design;
8. append a concise lead message referencing artifact IDs.

At each Claude worker checkpoint:
1. acknowledge owned artifact packet;
2. implement only owned paths/effects;
3. produce evidence;
4. update artifact submission metadata;
5. append Claude -> ChatGPT message referencing artifact IDs;
6. do not self-mark ACCEPTED.
