# Owner gates and preflight — resolve once, do not hide them

Planning itself grants no model, public, spend or deployment authority. A scoped owner decision must remain traceable to its actual request and the matching lead record. Do not infer permission from an optimistic milestone target.

## Preserve the actual owner context

The owner conditionally allowed use of existing accounts, or a new necessary account/email through the existing Unsubscriber Google Cloud alias setup when confident and useful. Record this as a setup scope, not as an account already created or permission to invent an alias endpoint. Reuse first. Verify the service, alias capability, ownership and mailbox route using the connected account or the authorized local worker. Do not guess credentials, open a paid service, bypass consent/MFA, or send unsolicited messages.

This setup permission is not the separately withheld live-model batch grant, not permission to post on social platforms, and not authority to incur new spend. No account or alias was created by this planning pass.

## One compact gate dossier

Maintain each gate as {gate_id, kind, requested_action, why_needed, artifact_ids, exact provider/host/account aliases, allowed namespaces, maximum attempts/calls/effects, spend_ceiling, expiry, approved_by_ref, lead_manifest_ref, current_state, next_command_or_owner_step, last_verified_at}. Never store secrets or signed URL tokens here.

States: NOT_REQUIRED, PREPARED, NEEDS_OWNER, AUTHORIZED, CONSUMED, EXPIRED, REVOKED, BLOCKED_EXTERNAL. Worker reports cannot turn NEEDS_OWNER into AUTHORIZED. Keep model budgets shared across every process and replay attempt.

## Gate inventory

| Gate | Next concrete action | Boundary |
|---|---|---|
| Persistent host | Inspect the actual Mac or other existing owner-controlled persistent host; verify OS, runtime, local filesystem, private-repo read/push, native scheduling and wake/reboot behavior | Browser/Claude app location does not establish where the execution tool runs. A cloud agent can still be ephemeral. No scheduler installation on an unverified host. |
| Developer invocation | Verify installed headless client/version, credentials via approved credential store, restricted tool permissions and autonomous invocation budget | Existing interactive development use does not silently authorize unlimited scheduled model calls. |
| ChatGPT lead execution | Verify an actual authorized scheduled/event review transport and its successful repo read/write | This document does not install an automation or make an idle chat wake. Do not impersonate a lead response. |
| V0.4 adaptive batch | Prepare the fixed five-case input hash manifest and exact maximum five-call request; verify configured provider/model and no API-key/PAYG fallback | Fresh explicit owner authorization plus matching canonical lead manifest before the first call; no retry-until-pass. |
| V0.5/V0.6 reviewers | Inventory exactly which review/generation stages require real models or a human reviewer, and compile a bounded per-stage maximum | The old five-call divergence grant cannot fund unrelated draft/review calls. Missing cultural reviewer is a real gate. |
| V0.8 identity/alias | Reuse an existing account or verified Unsubscriber alias only where a route needs it; verify receipt delivery/readback and account ownership | Secrets remain local. MFA/consent remain exact owner actions. New aliases are not acceptance evidence for unrelated milestones. |
| Platform capability | Read current official route/scopes/review/quota requirements and verify actual account capability | No assumption all five APIs are free, available or permitted; no anti-bot/CAPTCHA evasion. |
| Public canaries | Freeze persona/account/destination/content hash, max one attempt per approved case, reconciliation and observation profile | Separate explicit public grant; unknown/uncertain send never auto-retries. |
| Real analytics | Read authorized measurements from verified accounts over the frozen observation windows | Missing data blocks conclusions; elapsed time and sufficient evidence cannot be fabricated. |
| V2.3 specialists | Compile exact real-role/provider/tools/context/call/time/worker budgets for the integrated mission | Lower-cost model availability is verified, not assumed. No implicit extra accounts, paid fallback or recursive workers. |
| Multi-brand operation | Confirm the approved brand/account map, migration backup, read scopes and any public action policy | Adding local test brand records does not create verified public brands or expand public authority. |

## Prompt/request template, not an authorization

Request approval for `<run-id>` on `<verified-host>` using `<provider-route>` for `<artifact-ids>` with `<exact-input-hashes>`, maximum `<N>` model calls, `<M>` external-effect attempts, no automatic retry and zero additional spend. Restrict namespaces/accounts to `<verified-list>`, expire at `<timestamp-or-bounded-completion>`, preserve failures, and stop on unknown identity/route/cost. The lead writes the canonical grant only after the owner approves this concrete request.

If the gate is unavailable, state the exact missing fact/action once and continue other permitted work. Do not repeatedly ask the owner to reapprove ordinary implementation or disguise authority blockers as coding tasks.
