# Kai, Pri 2.0 and Lipi — current focus

Updated 12 September 2026. The owner selected these three for the next focused discussions and documentation. Lipi's destination is fully autonomous business operation. All bots must accept owner course corrections; simple files are sufficient now, with Slack adapters later. This packet does not activate a new runtime, schedule, integration, Jira write or deployment.

**Current priority update:** the owner subsequently put the first-five bot kickoff ahead of further discussion of these three. This packet is saved/parked; it does not dispatch their implementation. Follow the first-five kickoff in the task library.

Latest host direction supersedes older Windows-primary wording: **R730 is the central hub for Kai and local bots; Windows is fallback; the Intel i9 Mac is staging and secondary fallback.** The mobile Mac is an optional client/development machine and may go offline. Migration and failover are not complete. The existing five-bot launch queue is preserved, not silently canceled or duplicated.

## Kai

**Where we are:** local chat and narrow Google API/plugin reads have worked in dated tests. Current source/deployed hashes match, and a Mac service process exists. The real owner Slack-to-Google workflow and exclusive Slack consumer ownership still need acceptance. A running process is not that acceptance. See [evidence](KAI_PRI_EVIDENCE.md).

**Where we are going / why:** a dependable personal assistant and a small operations entry point. It answers authorized personal requests, reports meaningful bot outcomes, accepts owner direction and routes work to an existing executor. Routine job selection, field validation and waiting should use code. Kai does not need to call a paid reasoning model to hand a known ticket to Cursor.

**Next:** finish the single useful Google workflow under existing BOTS-90/BOTS-92; resolve the demonstrated ingress/context issue with the smallest repair. Document the portable source/runtime boundary and stage a disposable copy on the i9 once inventoried. Keep the current working listener until a replacement is proven, then cut over one host deliberately. The owner is open to leaving OpenClaw; select replacement components after comparing this bounded workflow, rather than a framework rewrite before acceptance.

**Success:** one authorized request reaches one consumer, invokes only the needed tool, replies once, records compact evidence and spends no model tokens while idle. R730 operation and mobile-Mac-disconnected recovery are later explicit acceptance checks, not implied by the staged copy.

## Pri 2.0

**Where we are:** the Slack/local-model chat pilot has produced real replies; the wife test is accepted from the owner's report. Current source matches the accepted candidate. Remaining work is engineering acceptance/review reconciliation and durable hosting, not another wife trial. There are no Google tools in the current chat source. See [evidence](KAI_PRI_EVIDENCE.md).

**Where we are going / why:** a useful personal assistant that reduces the wife's effort through conversation, drafting, planning and later chosen integrations. Her context, preferences and connected accounts stay separate. Kai and Pri can reuse transport/model/receipt helpers without sharing private memory or giving the portfolio access to personal mail.

**Next:** reconcile PT-207/208/209 under PT-52 against existing tests and the wife acceptance; run only missing technical checks and obtain a scoped review. Package the source for portable staging and test isolation, restart behavior and one reply without disturbing the current app. Add a small user-approved knowledge collection when wanted. Google is the next integration family if she chooses it and completes her own account connection; do not make it a prerequisite for the current useful chat.

**Success:** reliable bounded replies, no cross-user retrieval, explicit forget/reset behavior, observable failures, no idle inference and a tested host transition. Prefer retaining the simple existing bot over replacing it merely to make every project use the same framework.

## Lipi Standard

**Where we are:** substantial product/storefront/control documentation and local checks exist. Latest retained evidence reports 25 local task contracts satisfied and 56 aggregate checks passing, yet launch readiness remains false. The control service has proposal/read functions and disconnected commerce providers; it does not execute an autonomous business. Older publication/zero-sales evidence is dated, not current store truth. See [Lipi evidence](LIPI_EVIDENCE.md).

**Where we are going / why:** an autonomous store operator responsible for merchandising, customer acquisition, conversion, order/fulfillment monitoring, support and learning toward profitable delivered orders and customer satisfaction. It should originate experiments, document plans/results and improve its approach within its business rules, with the owner steering direction and handling genuine exceptions. “Autonomous” must include execution and outcome verification, not only suggestions.

**Next:** refresh exact variants, provider costs and shipping; resolve the sample packet's missing quote totals and conflicting tote color before any order. Reconcile existing owner decisions rather than repeatedly requesting broad approval. Produce a concrete capsule/sample decision with known total and exact identities; validate physical quality, checkout and fulfillment before expanding acquisition. Then connect the narrow approved action paths, record destination receipts and prove a real observation cycle (existing LIPI-63–87 scope, current Jira status unverified).

**Autonomy progression:** start with reliable observations and actionable experiments; qualify reversible merchandising/acquisition changes within current authority; then qualify order/support routines and bounded exception handling. Explicit budgets and allowed commercial actions must be executable policy. Unknown budget/authority is not unlimited permission, and past specific approvals remain valid. There is no reason to seek approval for every routine action once its category is authorized and verified.

**Indian clothing to America:** preserve this as a supplier/fulfillment experiment. The existing source is Printful-based; it does not prove India-sourced product quality, US delivery, returns or economics. Evaluate one actual supplier/product route before changing the whole catalog or promising delivery. No supplier or profitability is assumed.

**Success:** a customer can buy the correct item, receive the expected quality, get support and generate measured contribution after relevant costs. Track orders, fulfillment exceptions, returns, contribution, qualified conversion, experiment outcomes and owner interventions; visitors and generated posts are supporting measures.

## Simple shared operating pattern

Use [OWNER_DIRECTION.md](OWNER_DIRECTION.md). Existing mission/ops rules describe enduring purpose; a small per-project direction file records current owner priorities. At task boundaries, workers read only relevant changed direction and current state, take an eligible action, verify it, record the outcome and wait for useful evidence. No idle LLM polling, new crew platform or separate Slack apps are required.

For host setup use [HOST_PLAN.md](HOST_PLAN.md). The i9 setup scripts are a preparation package, not proof the machine has been inspected or a remote executor started. Do not attempt to clone private credentials into a code repo. These three plans and the first-five bot task library are documents; their runtime intake hooks remain to be implemented and tested.
