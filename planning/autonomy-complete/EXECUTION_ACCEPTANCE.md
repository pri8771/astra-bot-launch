# Shared fault and per-mission acceptance protocol

This defines future runtime acceptance. Current planning tests validate the documents/task graph only. Product checks run during source qualification are separately labeled in mission evidence.

Freeze exact source/spec/config/asset bytes and compatible shared version. Record SHA256, repository commit, actual author/reviewer identities, timestamps and executed commands. Windows CRLF conversion can change worktree hashes: distinguish Git-blob hashes from the bytes actually built/reviewed; never silently compare one to the other. Any meaningful candidate change requires affected checks and review again. An independent same-model review is not distinct-model approval where the task contract calls for the latter.

| Case | Injection or action | Required observation |
| --- | --- | --- |
| Duplicate intake | Same provider event/question/direction delivered twice and after restart | One logical job/application, original revision retained |
| Wrong mission/account | Valid payload using another mission's grant or wrong destination | Rejected before effect; incident with no leaked payload |
| Claim race | Two workers request the same scope at one revision | One epoch/owner; loser has no credential path |
| Lease expiry/partition | Old owner disconnected then reappears during takeover | New owner waits for fence/reconciliation; old epoch cannot send |
| Before-send crash | Persist intent then stop before network dispatch | Qualified absence or safe idempotent replay; no invented effect |
| After-send crash | Destination succeeds, process stops before receipt | Destination reconciliation finds original effect; no duplicate |
| Lag/ambiguous effect | Provider acceptance but no visible public item/order yet | Pending/unknown with bounded readback; no blind retry or budget release |
| Stop/revise | Pause current mission and supersede its direction mid-job | Exact revision acknowledged at safe boundary; pending remote action reconciled |
| Missing input | Ask once, duplicate timer, invalid answer then correct answer | No repeated question/inference; correct job resumes once; unrelated jobs continue |
| Spend race/exhaustion | Concurrent cost reservations, missing ceiling, unknown usage | No over-cap dispatch; unknown cost explicit; no hidden model/provider fallback |
| Process loss | Windows child/grandchild, timeout and supervisor termination | Full owned tree exits; durable attempts survive; unrelated processes untouched |
| Restore gap | Recover backup from before an already successful effect | Reconciliation mode covers gap before new effects; no duplicate |
| Writer outage | Queue experiment/docs then writer unavailable/ambiguous apply | No unrecorded new experiment launch; immutable outbox reconciles once; independent preparation continues |
| Zero idle | Advance fixture clock 24h with no changed evidence/not-due decisions; inspect real deployed idle window separately | Zero unnecessary model calls; window/due events are explicit |
| Low data | Evaluation window ends below predeclared exposure | Inconclusive or justified dated extension within remaining grant; no fabricated improvement |
| Review staleness | Change one reviewed payload/source byte | Previous release approval rejected |

Each mission adds its real effect: OPO durable outside request/service result; WHB sourced correct-account public piece; CommerceLint permitted scan/result and qualified offer event; BidetFit manufacturer-backed checker result/referral with eligible program evidence; Guru reviewed culturally accurate piece and moderation/engagement receipt; Lipi granted provider/catalog/order/support action plus actual required fulfillment observations. Synthetic clients and sandbox charges cannot satisfy real adoption/revenue/delivered-order requirements.

Runtime autonomy requires two successive eligible cycles without a new launch prompt, original baseline and outcome evidence, owner direction application, question/resume, pause, restart/restore and exact-source independent review. Lipi's seven-day operating interval and physical/sample delivery must actually elapse. Failure, zero response or no sales can be an honest valid experiment result; they do not prove business validation. A blocked publication/payment retains an accepted offline candidate but leaves external/runtime acceptance incomplete.

After each accepted cycle, append next decision and due trigger. The endpoint is an operating decision process with controls, not an infinite queue of tasks labeled complete. No external acceptance tests are executed by this planning package.
