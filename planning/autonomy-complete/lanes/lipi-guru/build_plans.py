"""Generate the assigned planning artifacts only; no product or external writes."""
from pathlib import Path
import json, hashlib, subprocess, re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
CONTROL = ROOT.parents[1]
NOW = datetime.now(timezone.utc).isoformat()
BASE = '3833a1b'
LREF = '0d896016f2fa113ce07e504bc5d6528717598b5f'
RETAINED = '37c447bbd90b8aac86f768a480b25eb4d8fc6c44'
LREPO = 'pri8771/lipi-standard-store'
GREPO = 'Canonical Guru repository and root selected and receipt-bound in GURU-01; not currently established'
tasks = {'lipi': [], 'guru': []}

def add(m,n,title,goal,paths,deps,inputs,steps,deliverables,tests_,acceptance,rollback,next_,hours,candidates=(),ev=(),status='planned',gates=()):
    prefix='LIPI' if m=='lipi' else 'GURU'
    ident=f'{prefix}-{n:02}'
    tasks[m].append(dict(id=ident,mission=m,title=title,goal=goal,status=status,
      owner_role=('Suggested Lipi executor, admitted by Lipi coordinator' if m=='lipi' else 'Suggested Guru editorial/engineering executor, admitted by Windows four-mission parent'),
      source_repo=LREPO if m=='lipi' else GREPO,owned_paths=paths,
      evidence_refs=list(ev) or [f'{prefix}-E01'], dependencies=deps,prerequisite_inputs=inputs,
      implementation_steps=steps,deliverables=deliverables,tests=tests_,
      review={'identity_requirement':'Independent reviewer other than implementing author; record actual reviewer identity, model/version and host. Cultural reviewer identity is additionally required for Guru claims; no invented reviewer.',
              'exact_source':'Bind source commit, task/spec SHA256, artifact hashes, policy revision and receiving-system receipts; any material change invalidates affected approval.',
              'bounded_repairs':'At most two targeted repair/review attempts per admitted task, or a stricter existing limit. Unresolved failure becomes needs_input/blocked with evidence; never an unbounded loop.'},
      acceptance=acceptance,rollback=rollback,next_eligible_action=next_,
      estimate={'unit':'engineering_hours','low':hours[0],'high':hours[1],
        'assumptions':'New incremental planning range, not original Jira estimate or worklog. Reuse accepted assets; elapsed shipping, review waiting, observation windows and provider verification are excluded.',
        'dependency_risk':hours[2]},
      jira={'key':None,'candidates':list(candidates),'matching_action':'Designated writer compares current scope and retained acceptance, reuses matching issue or adds only genuine residual scope, preserves all original estimates/actuals, and returns native key/readback bound to this specification.',
        'writer':'Lipi writer designation unresolved: LIPI-I09' if m=='lipi' else 'Windows four-mission release parent; planner outbox only'},
      effect_gates=list(gates),requirement_ids=[]))

add('lipi',1,'Bind current source to accepted Lipi residuals','Reuse LIPI-63–87 local work while proving which source and external residuals the next executor actually owns.',
 ['ops/autonomy/reconciliation/','ops/autonomy/admission/lipi-source.json'],[],['LIPI-I01','LIPI-I09'],
 ['Compare clean main '+LREF+' with retained '+RETAINED+' and cloud session4 branch 52954f1f3d07f160a414713250923993a7d5f3f5; request only missing named return/contract artifacts through existing handoff route, without querying the old Mac.',
  'Build a 25-row local-contract/external-acceptance matrix using current Jira metadata and exact source hashes; preserve local satisfied claims separately from owner/provider residuals.',
  'Reuse validated 31-check main and control-plane baseline; qualify a Windows UTF8/Pillow interpreter without installing, and bind incoming release-worker changes through a new source revision before any edit.'],
 ['25-row acceptance reconciliation','source/admission manifest with path reservations'],
 ['Reject a missing retained artifact as unknown, not accepted-current or absent implementation.','Main structural checks reproduce31 passes and no publication flag; no dirty worker checkout is modified.'],
 ['Each LIPI-63–87 row says reused artifact, source availability, external residual and next owner.','Jira key remains null until designated writer returns current readback.'],
 'Discard only unadmitted reconciliation proposal; preserve evidence and accepted prior artifacts.',
 'Run LIPI-02 and separate variant/economics preparation on the admitted source; missing external evidence blocks only its dependent effect.',(2,5,'Retained exact revision not served by remote; writer and targeted return delivery unknown'),range(63,88),['LIPI-E01','LIPI-E02','LIPI-E03','LIPI-E07','LIPI-E08'],'reuse_and_verify')
tasks['lipi'][-1]['jira']['candidates']=[f'LIPI-{i}' for i in range(63,88)]

add('lipi',2,'Resolve capsule membership and design acceptance','Produce one exact coherent capsule proposal using existing production art and approved brand direction.',
 ['ops/autonomy/capsule/'],['LIPI-01'],['LIPI-I02'],
 ['Retain Meridian, Open Current and Threshold Study12×16 as the proposal, with Quiet Route explicitly retain/exclude/conditional; do not promote proposal to owner approval.',
  'Review production files, dimensions, placement, mockup bindings and usage claims against exact product contracts; preserve English-first premium American direction and excluded Hindi/Devanagari assets.',
  'Present owner one concrete membership decision with all remaining cost/sample facts; apply only that signed/versioned decision and identify replacement work for rejected items.'],
 ['capsule membership and design matrix','owner decision packet'],
 ['A conditional or rejected SKU cannot enter publication/sample payloads.','Every visual references exact art hash and variant; legacy glyph assets remain outside public candidate.'],
 ['Membership state is explicit for every candidate.','Owner decision receipt or a single persisted unanswered question exists without blocking independent engineering.'],
 'Restore prior proposal revision; no public catalog mutation belongs to this task.',
 'Proceed to LIPI-03–06 for retained/conditional candidates and LIPI-24 independently.',(2,4,'Owner membership answer missing'),['LIPI-65'],['LIPI-E02','LIPI-E04','LIPI-E07'],'reuse_and_verify')

variant_specs=[
 (3,'Meridian cap','Yupoong6245CM, template106647957, four historical colors Black/Navy/Cranberry/Spruce','meridian','LIPI-64'),
 (4,'Open Current tote','Mantis M196 Denim Blue, template106648374; sample hint natural conflicts and must never be ordered','open-current','LIPI-67'),
 (5,'Quiet Route jogger','Jerzees975MPR, template106648266, historical20 variants across4 colors/5 sizes; membership conditional','quiet-route','LIPI-68'),
 (6,'Threshold Study print','Threshold Study01 12×16, one finish; exact production file and supplier size/finish mapping remain explicit','threshold-study','LIPI-66')]
for n,name,identity,slug,jira in variant_specs:
 add('lipi',n,'Qualify '+name+' provider identity','Reconcile the existing product instead of duplicating supplier templates or drafts.',
  ['ops/autonomy/providers/'+slug+'/'],['LIPI-01'],['LIPI-I03'],
  ['Use retained identity only as the search anchor: '+identity+'. Refresh exact shop/store, product, variant, SKU, size/color, technique, placement, art hash and provider region.',
   'Read current Shopify Draft/channel/media/retail values and Printful sync-variant/fulfillment status through the qualified route; compare both sides and isolate each mismatch.',
   'Prepare an exact before/after repair for only mismatched private mapping or media. Reuse existing grants if sufficient; live changes require the applicable scoped capability and hash-bound receipt.'],
  ['variant-level joined provider mapping','dated cost/availability/media evidence','bounded correction proposal'],
  ['Variant-count, SKU, color/size, production hash and one-to-one mapping comparisons fail on missing/duplicate/mismatched IDs.','Reopen/read both receiving systems after any authorized correction; Draft status and zero channels stay explicit until launch.'],
  ['Each intended variant either has current matching mapping/fulfillment evidence or an exact blocked reason.','No source hint or mockup is treated as current provider truth.'],
  'Restore only the exact private field mapping from captured prior state if reversible and authorized; do not delete provider records or unpublish automatically.',
  'Feed verified identities into LIPI-07/08; withheld variants stay excluded.',(2,5,'Provider access/availability and mapping controls require current verification'),[jira],['LIPI-E03','LIPI-E04','LIPI-E07'],'reuse_and_verify',['LIPI-G01'])

add('lipi',7,'Enforce all-in economics and US cart shipping','Make every permitted selling basket satisfy the binding20% floor with10% reserve before price or shipping action.',
 ['services/lipi-autonomy/src/economics/','services/lipi-autonomy/test/economics/','ops/autonomy/economics/'],['LIPI-03','LIPI-04','LIPI-05','LIPI-06'],['LIPI-I03','LIPI-I04'],
 ['Reuse the standardized integer-cents method: R=P−D; total revenue=R+customer shipping; contribution subtracts supplier product/decoration/shipping, platform allocation, variable/fixed payment/channel fees,10%×R reserve and actual absorbed costs. Do not use retired30% caution as floor or2–5% reserve hypotheses.',
  'Refresh fee rules, exact variant costs and US destination/service quotes; enumerate single-item, mixed-cart, high-cost-size, discounts and $98.99/$99/$99.01 after-discount threshold cases without double counting shipping.',
  'Fail closed for unknown/stale inputs, prohibited discount+merchant-paid-shipping stack or any allowed basket below20%. Compile a signed policy/economics result and exact price proposal; $99 free-US-shipping remains disabled until mixed-cart proof and existing approval. Preserve owner tax record without supplying a legal determination.'],
 ['versioned margin evaluator','shipping matrix and quote freshness policy','price/shipping decision packet'],
 ['Boundary fixtures at19.99/20.00/20.01% and null fee fail/pass correctly with no intermediate rounding.','Mixed supplier/cart shipments cannot be treated as linear single-item shipping; stale or changed cost invalidates queued price action.'],
 ['Every permitted basket clears20% under current evidenced assumptions; failing baskets cannot sell under the proposed configuration.','Reserve remains10% until owner revisits after100 actual orders; economic and tax unknowns stay explicit.'],
 'Revert proposed calculations/config to previous admitted policy; a live price rollback must itself satisfy current margin authority.',
 'Produce exact purchase quote in LIPI-08; price execution only through LIPI-16.',(5,9,'Current quotes, fees and threshold behavior missing'),['LIPI-69','LIPI-71'],['LIPI-E04','LIPI-E05'],'reuse_and_verify',['LIPI-G02','LIPI-G03'])

add('lipi',8,'Prepare and execute only an approved exact sample order','Turn the retained incomplete sample packet into a purchase-ready decision.',
 ['ops/autonomy/samples/order/'],['LIPI-02','LIPI-07'],['LIPI-I05'],
 ['Repair null quote totals and Open Current natural/Denim Blue conflict using verified provider IDs; record each item, quantity, design hash, shipping service, dated quote, landed total, expiry and private delivery-reference.',
  'Reuse any current exact sample grant; otherwise persist one owner purchase decision with maximum total/currency and selected items. No standing sample budget is assumed.',
  'After exact authorization, submit once through the permitted provider route and capture provider order ID, total and line-item readback; timeout enters reconciliation by order/external ID before any retry.'],
 ['purchase-ready sample packet','owner approval or needs-input record','provider sample order receipt'],
 ['Null total, changed color/design, expired quote or cap overrun blocks submission.','Crash after submit resolves the existing provider order rather than placing a second order.'],
 ['Sample purchase matches exact authorized identities and total, or remains clearly awaiting the one required decision.','Receipt is provider-observed; preparing a packet is not purchasing or delivery.'],
 'Cancel only when provider confirms reversibility and owner authorizes; otherwise retain order and monitor delivery.',
 'LIPI-09 tracks delivery and physical inspection; unrelated storefront/runtime work continues.',(2,4,'Owner per-purchase approval and fulfillment lead time'),['LIPI-70'],['LIPI-E02','LIPI-E04'],'reuse_and_verify',['LIPI-G04'])

add('lipi',9,'Inspect delivered samples and narrow quality claims','Verify physical quality before exposing replacement products or expanding acquisition.',
 ['ops/autonomy/samples/inspection/'],['LIPI-08'],['LIPI-I06'],
 ['Track actual shipped/delivered states against the sample receipt without pretending elapsed time has passed.',
  'Have the receiving owner inspect material, size/fit, print/embroidery registration, color, care/packaging, damage and delivered appearance using the exact ordered variants; retain redacted photos and attributable observations.',
  'Record accepted/narrowed/rejected per SKU, reconcile mockup-vs-delivered claims and create targeted rework only for failures. Use a new exact purchase gate for replacements that cost money.'],
 ['delivery receipt','physical QA matrix','accepted capsule revision'],
 ['A tracking label or synthetic photo cannot mark delivered/quality-accepted.','A failed sample removes affected claims from launch candidate and triggers finite repair review.'],
 ['Each launch SKU has attributable physical acceptance or remains withheld.','Inspection result is linked to the same provider order and product configuration.'],
 'Withhold affected candidate and preserve prior draft; no autonomous refund/replacement.',
 'LIPI-10/12 finish sample-bound content and purchase journey; alternate design experiment may be proposed.',(2,5,'Real delivery and owner inspection waiting excluded'),['LIPI-72'],['LIPI-E02','LIPI-E04'],'reuse_and_verify',['LIPI-G04'])

add('lipi',10,'Finish product content and coordinated storefront candidate','Reuse existing art/theme work and make all customer surfaces tell the same verified product story.',
 ['ops/autonomy/storefront/candidate/','services/lipi-autonomy/test/storefront-contract/'],['LIPI-02','LIPI-07'],['LIPI-I03'],
 ['Stage exact capsule copy, care/size information, official media/alt bindings and truthful shipping language; bind final media to LIPI-09 acceptance before publication.',
  'Create a coordinated manifest for product status/channels, collections, Search/Cart, About, metadata, navigation/contact, Forms popup and lifecycle copy; preserve existing theme IDs as historical search anchors, not live truth.',
  'Run private preview responsive and semantic tests, keyboard focus/escape/return, error/empty states, reduced motion and actual NVDA/device checks. Distinguish real assistive-device evidence from automated DOM checks.'],
 ['exact release-candidate surface manifest','content/media and accessibility evidence','targeted remediation list'],
 ['No legacy character-led identities, generic mockup names, inactive discount claims or inaccessible purchase controls leak from the candidate.','Public/shared surfaces are not changed one-at-a-time as private QA.'],
 ['All candidate surfaces agree on approved identity and available variants.','Responsive/accessibility residuals are explicit and owned, not hidden behind passed source checks.'],
 'Restore private candidate files and previous preview; shared public cutover belongs only to LIPI-14.',
 'LIPI-11 policy and LIPI-12 checkout qualify alongside the final physical sample binding.',(4,8,'Live shared surfaces and actual assistive QA remain unverified'),['LIPI-73','LIPI-74','LIPI-76'],['LIPI-E02','LIPI-E04'],'reuse_and_verify',['LIPI-G01'])

add('lipi',11,'Bind policies, consent and support decisions','Give buyers accurate terms and a recoverable support path within existing owner-only remedy authority.',
 ['ops/autonomy/policy/','services/lipi-autonomy/test/consent/'],['LIPI-01'],['LIPI-I07'],
 ['Reuse policy drafts and inspect current shipping/returns/privacy/contact/consent surfaces; identify owner decisions still required without repeating accepted decisions.',
  'Keep customer replies draft-only, refund/replacement autonomous cap$0, chargebacks owner-only, and1-business-day response target; map merchant/provider policy conflicts explicitly.',
  'Prepare exact policy/consent changes for owner review, minimize personal data retention, and test opt-in/withdrawal/unsubscribe and contact route. Record tax posture as dated owner decision with follow-up, not legal advice or inferred authority.'],
 ['policy/consent decision manifest','support route proof','data retention and deletion contract'],
 ['Unapproved marketing consent or missing destination cannot trigger a customer send.','Policy UI does not promise automatic refunds, stock, delivery deadlines or new legal conclusions.'],
 ['Each policy field has current evidence/owner decision or a precise unresolved input.','Contact/support and consent states survive reopen and route to an accountable owner.'],
 'Revert staged policy revision; do not retroactively erase customer consent/complaint records.',
 'LIPI-12 checkout and LIPI-18 support use the accepted version.',(3,6,'Owner policy decisions and live consent route'),['LIPI-77','LIPI-84'],['LIPI-E04','LIPI-E05'],'reuse_and_verify',['LIPI-G05'])

add('lipi',12,'Verify checkout and transactional journey','Prove a buyer can purchase the correct approved item and receive the correct order handoff.',
 ['ops/autonomy/checkout/','services/lipi-autonomy/test/checkout/'],['LIPI-07','LIPI-09','LIPI-10','LIPI-11'],['LIPI-I03','LIPI-I04','LIPI-I05'],
 ['Exercise variant selection, quantity, cart persistence, discount rejection,US address/shipping, mixed cart, threshold, payment failure/cancel, confirmation and support links using private/test routes first.',
  'Verify merchant/payment eligibility and exact charged-test allowance separately; do not use a synthetic checkout as a real payment or charge without authority.',
  'For the authorized purchase canary, reconcile Shopify order/payment status, Printful mapping/hold state and transactional delivery receipt using secret/PII references only.'],
 ['checkout scenario results','charge/test authority record','joined order/payment/provider receipt'],
 ['Wrong variant, stale price, unauthorized discount or below-floor basket blocks completion.','Payment timeout does not create a second charge/order; user sees useful failure and reconciliation status.'],
 ['Relevant edge cases pass on exact candidate and a separately identified real or test order receipt exists.','Real payment/fulfillment acceptance remains open if only a test route was used.'],
 'Restore staged checkout configuration; refunds, voids and cancellations use exact owner authorization and destination readback.',
 'LIPI-13 review/restore and LIPI-14 release; LIPI-17 observes fulfillment.',(4,8,'Payment eligibility, sample acceptance and exact purchase allowance'),['LIPI-75'],['LIPI-E02','LIPI-E04'],'reuse_and_verify',['LIPI-G04','LIPI-G05'])

add('lipi',13,'Review exact release and rehearse rollback','Make launch a reviewable candidate with a tested recovery procedure.',
 ['ops/autonomy/release/review/','ops/autonomy/release/restore/'],['LIPI-10','LIPI-11','LIPI-12'],['LIPI-I08'],
 ['Capture current theme/catalog/channel/policy/discount snapshot without secrets and hash the exact candidate, cost inputs, sample acceptance and checkout evidence.',
  'Rehearse private restore from the snapshot; distinguish technical rollback capability from permission to change public or irreversible orders.',
  'Obtain attributable independent technical/content review and concrete owner launch decision covering exact catalog/shared surfaces. Limit repairs to2 and invalidate approval if payload drifts.'],
 ['review receipt','private restore evidence','exact owner launch packet'],
 ['Restore reproduces snapshot hashes and preserves order/payment receipts.','Unreviewed file or changed price/mapping invalidates candidate admission.'],
 ['Exact-source independent review and private recovery pass or fail explicitly.','Owner can approve one complete current candidate without unspecified future changes.'],
 'Keep existing live state; restore private candidate only; no forced refund or deletion.',
 'LIPI-14 applies only the approved cutover.',(3,6,'Independent reviewer and exact owner launch decision'),['LIPI-78','LIPI-79'],['LIPI-E02','LIPI-E04'],'reuse_and_verify',['LIPI-G06'])

add('lipi',14,'Apply approved capsule cutover and verify public destinations','Release the accepted purchase-ready capsule with real public readback.',
 ['ops/autonomy/release/cutover/'],['LIPI-13'],['LIPI-I08'],
 ['Reserve the one store writer and compare current live preconditions to approved snapshot; apply approved products/channels/collections/shared surfaces in the declared sequence.',
  'Read public product/variant prices, Search/Cart/About/contact/policies/Forms and checkout back from the actual domain; verify the intended shop and theme, not a preview.',
  'Record per-surface success/uncertain/failure; stop dependent acquisition on inconsistency and use the approved rollback decision with readback, leaving irreversible receipts intact.'],
 ['cutover receipt manifest','public destination evidence','accepted live release ID'],
 ['Stale owner/changed live preconditions abort before mutation.','Partial cutover and restart reconcile each surface; no second publication or blind whole-store overwrite.'],
 ['Approved capsule and consistent shared surfaces are publicly verified, or precise partial state is reported.','Release is distinct from autonomous operation or sales validation.'],
 'Execute only approved reversible theme/catalog rollback from captured prior values; escalate irreversible/customer effects.',
 'LIPI-19 authorized organic distribution and LIPI-17/18 operations start when admitted.',(2,5,'Exact launch grant and provider availability'),['LIPI-82','LIPI-83'],['LIPI-E02','LIPI-E04'],'reuse_and_verify',['LIPI-G06'])

add('lipi',15,'Connect durable commerce observations and due events','Replace repository-only business answers with narrowly scoped current evidence feeding shared scheduling.',
 ['services/lipi-autonomy/src/observations/','services/lipi-autonomy/src/events/','services/lipi-autonomy/test/observations/'],['LIPI-01','SH-02','SH-03','SH-04','SH-13'],['LIPI-I03','LIPI-I10'],
 ['Keep services/lipi-control-plane readonly. Add a separate mission integration that normalizes shop/product/variant/cost changes, order/payment/fulfillment transitions, consent/support events and aggregate analytics into shared durable state.',
  'Qualify supported versioned Shopify and Printful read routes and webhook authenticity/delivery IDs from current official contracts; if webhook access is unavailable use finite due-time incremental reads with cursor/watermark and quota caps.',
  'Deduplicate by provider+shop+event ID/version; persist observed_at, provider time, schema/source hash and next_check_at. Schedule held-order escalation before12h and unshipped review at3 business days; unchanged snapshots trigger no model call.'],
 ['commerce event adapters','mission scheduler configuration','redacted observation ledger'],
 ['Duplicate/out-of-order webhook and cursor restart produce one state transition without losing new evidence.','Wrong shop, stale timestamp, invalid authenticity or malformed payload cannot modify authority or leak PII.'],
 ['One current authorized read is persisted with provenance and repeat idle ticks show0 model calls.','Missing providers yield explicit stale/unknown state and one resource question.'],
 'Disable new consumer and retain cursor/state; keep old readonly service intact. Re-enable only one fenced consumer.',
 'LIPI-16 actions and LIPI-17/18 routines consume these events.',(7,12,'Provider access and webhook format qualification; shared persistence'),[],['LIPI-E03','LIPI-E05','LIPI-E09'],gates=['LIPI-G01','LIPI-G08'])

add('lipi',16,'Execute eligible commerce actions with durable approvals','Implement real permitted mutations without widening the existing read-only MCP service.',
 ['services/lipi-autonomy/src/actions/commerce/','services/lipi-autonomy/test/actions/commerce/'],['LIPI-07','LIPI-15','SH-05','SH-06','SH-10','SH-14'],['LIPI-I03','LIPI-I10'],
 ['Reuse ActionEnvelope canonical payload/expected-before/policy binding as a contract; replace process-local consumed-token Set semantics at the adapter boundary with shared transactional durable consumption and fenced claim.',
  'Implement a strict allowlist for current authorized price changes and separately gated product/private mapping/publication/discount/order/refund actions. Verify destination shop, current direction, reviewed exact source, margin result, quota and grant immediately before effect.',
  'Persist intent before submission, then provider operation ID and exact readback. On timeout reconcile provider state/order/payment ID first; never blindly replay a charged order or price mutation. Log before/after margin math and writer-bound Jira/worklog receipt as existing price authority requires.'],
 ['effect eligibility matrix','commerce action adapters','durable mutation/reconciliation ledger'],
 ['Restart after grant validation cannot reuse consumed grant or admit stale fencing token.','Unknown budget, changed variant cost, different shop, missing price logging admission or expired grant prevents effect.'],
 ['Authorized price change can be observed at destination with current≥20% worst-case contribution.','Refund/replacement cap remains$0 and discounts/publication/customer sends stay gated; generic shell/HTTP does not become an effect tool.'],
 'Pause action intake and reconcile pending effect; reversible field rollback itself rechecks current authority/economics.',
 'LIPI-20 may schedule a bounded permitted merchandising experiment; other action classes wait for exact grants.',(8,14,'Action credentials and durable single-use approval integration'),[],['LIPI-E03','LIPI-E04','LIPI-E05'],gates=['LIPI-G01','LIPI-G02','LIPI-G03','LIPI-G04','LIPI-G05','LIPI-G06','LIPI-G08'])

add('lipi',17,'Operate fulfillment and inventory exceptions','Track every actual paid order through provider acceptance, shipment, delivery and exceptions.',
 ['services/lipi-autonomy/src/fulfillment/','services/lipi-autonomy/test/fulfillment/','ops/autonomy/fulfillment/'],['LIPI-15','LIPI-16','SH-12'],['LIPI-I03','LIPI-I07'],
 ['Join Shopify order line IDs to exact Printful synced variants and provider order/status; distinguish paid,held,accepted,shipped,delivered,returned and canceled states without putting addresses in Git.',
  'Use deterministic deadlines for held/failed escalation within12h, unshipped after3 business days drafting, and carrier exceptions; record due business calendar/time zone and receipt-derived timestamps.',
  'Prepare replenishment/mapping/unavailability remedies and proactive notice drafts. No unapproved resubmit/purchase, substitution, automatic unpublish, delivery promise or customer send; ask once for the exact exception decision.'],
 ['order lifecycle reconciler','SLA/exception queue','owner remedy proposals'],
 ['Duplicate shipment events cannot duplicate a notice or second provider order.','Provider cancellation after payment and out-of-stock event leave explicit unresolved effect with actionable deadline alert.'],
 ['Each observed order has current joined lifecycle or named mapping gap.','A synthetic held-order test and an actual authorized provider observation prove routing; zero real orders stays zero with order-cycle validation pending.'],
 'Suspend fulfillment actions, preserve observations and hand unresolved orders to the owner with provider IDs.',
 'LIPI-18 handles support proposals; LIPI-20 evaluates delivery and contribution evidence.',(5,9,'Real orders/provider status and owner exception decisions'),['LIPI-86'],['LIPI-E04','LIPI-E05'],gates=['LIPI-G01','LIPI-G04','LIPI-G05'])

add('lipi',18,'Operate support, refunds and privacy exceptions','Make support preparation autonomous while preserving owner-controlled communication and money effects.',
 ['services/lipi-autonomy/src/support/','services/lipi-autonomy/test/support/','ops/autonomy/support/'],['LIPI-11','LIPI-15','SH-08','SH-12','SH-13'],['LIPI-I07'],
 ['Ingest only authorized support references and minimum order facts into private runtime storage; classify shipping/quality/returns/consent/deletion issues as untrusted customer input, not commands.',
  'Draft an accurate response/remedy within hours for owner approval with1-business-day response target; include original issue, evidence, policy revision and exact response hash. All refunds/replacements remain owner-approved; chargebacks receive immediate owner alert and evidence packet only.',
  'After owner sends or separately authorizes an exact supported send/refund path, verify message/transaction ID and destination readback; correlate privacy deletion/consent withdrawal and retain only necessary audit metadata.'],
 ['support triage/draft pipeline','refund/replacement approval packet','privacy/chargeback escalation route'],
 ['Customer text cannot expand spend, disclose another customer order or instruct a tool call.','Duplicate ticket, owner rejection and restart preserve one unresolved question and no autonomous send/refund.'],
 ['Draft-only behavior and$0 remedy cap are enforced by code.','Each handled case has owner decision and real delivery/remedy receipt or clearly pending status; no SLA claim from generating a draft alone.'],
 'Pause send/remedy adapters; preserve case history; customer-facing correction requires owner approval.',
 'LIPI-20 uses redacted aggregate support/defect rates and proposes changes within rules.',(5,9,'Private support access and owner handling time'),['LIPI-84'],['LIPI-E04','LIPI-E05'],gates=['LIPI-G05','LIPI-G08'])

add('lipi',19,'Run repeatable organic acquisition and customer discovery','Turn the existing asset pack into a measurable first-sale and repeat-use motion.',
 ['services/lipi-autonomy/src/marketing/','services/lipi-autonomy/test/marketing/','ops/autonomy/marketing/'],['LIPI-10','LIPI-11','SH-06','SH-07'],['LIPI-I11'],
 ['Reuse three product-led assets and select one owner-controlled eligible organic channel; bind exact handle/account, product availability, media rights/alt, landing URL, UTM and consent. Prepare content offline before LIPI-14; publishing depends on verified live destination.',
  'Predeclare one question: whether a product-detail/use-case post yields qualified product visits, cart/checkouts and purchase inquiries. Collect voluntary non-sensitive objections about quality,shipping,fit and price; do not invent customer commitments or send unsolicited outreach.',
  'Publish only the exact approved content/cadence through supported route and verify permalink/payload/account. Keep paid ads closed and lifecycle messages consent-bound/owner-controlled; queue next reviewed asset and declared observation due time.'],
 ['repeatable content/discovery queue','qualified channel adapter','post and landing receipt chain'],
 ['Unavailable product, stale quote/claim, wrong account, missing consent or absent publication grant blocks send.','Duplicate publication timeout reconciles existing post; UTM/test traffic exclusion works.'],
 ['One authorized post has exact real destination evidence and attribution, or remains fully prepared offline.','Acquisition is tied to profitable delivered-order objective; impressions do not become revenue.'],
 'Pause future posts; corrections/deletion require exact authority and destination verification; retain published evidence.',
 'LIPI-20 evaluates objections/conversion and queues the next finite product/content experiment.',(5,9,'Current channel identity, permission and live product destination'),['LIPI-81','LIPI-85'],['LIPI-E02','LIPI-E04'],gates=['LIPI-G07'])

add('lipi',20,'Evaluate commerce experiments and choose continuing actions','Close each finite learning cycle with truthful outcomes and a justified executable next decision.',
 ['services/lipi-autonomy/src/experiments/','services/lipi-autonomy/test/experiments/','ops/autonomy/experiments/'],['LIPI-15','LIPI-16','LIPI-17','LIPI-18','LIPI-19','SH-05','SH-07','SH-09'],['LIPI-I04','LIPI-I10'],
 ['Define immutable experiment baseline, hypothesis, target buyer/use case, intervention, allowed action/cost cap, data window, minimum evidence, stop rule and next_check_at before action; first cycle uses real7-day operations only after launch.',
  'Reconcile qualified sessions,product views,cart/checkouts,paid and delivered orders,returns/defects,actual receipts/costs and owner interventions. Separate QA traffic,missing data,zero,refunds/chargebacks and gross/net contribution; do not count elapsed waiting as work.',
  'At due evidence decide supported/unsupported/inconclusive and choose continue/change/stop with bounded next experiment: low qualified visits→new approved useful-content angle; visits/no carts→one product clarity/fit test; carts/no checkout→shipping clarity test; below-floor economics→hold affected action and price proposal; delivery defects→quality task. Queue selected task automatically without a new launch prompt.'],
 ['aggregate scorecard','experiment evaluator and next-task selector','Jira/documentation experiment outbox'],
 ['Unknown analytics cannot become zero; synthetic orders cannot become revenue.','An unchanged evidence fingerprint produces0 inference and no duplicated next experiment.'],
 ['Two consecutive finite decision cycles preserve original hypotheses and generate eligible next actions or timed evidence waits.','Financial and growth outcomes remain measured, including honest inconclusive/negative results.'],
 'Pause experiment intervention and preserve baseline/results; return to prior admitted configuration only if safe and authorized.',
 'Dispatch the selected task through admission/fencing, or persist one missing-input question and wait cheaply.',(6,10,'Real observation windows and customer outcomes excluded from effort'),['LIPI-80','LIPI-87'],['LIPI-E02','LIPI-E04','LIPI-E05'],gates=['LIPI-G02','LIPI-G07','LIPI-G08'])

add('lipi',21,'Consume owner direction and produce reconciled outboxes','Make ordinary owner steering change the next job once, with durable acknowledgement and resume.',
 ['services/lipi-autonomy/src/direction/','services/lipi-autonomy/src/outbox/','services/lipi-autonomy/test/direction/'],['LIPI-15','SH-08','SH-09'],['LIPI-I09','LIPI-I10'],
 ['Bridge existing ops/DIRECTION.md and business rules to shared issuer/mission/version validation. Persist recorded,seen,applied,waiting-for-effect,needs-input,superseded or expired with actual consumed revision.',
  'Test focus on first customers and evaluate Indian clothing suppliers as prioritization changes; neither widens purchases,sends or brand direction. Pause stops new affected effects, while already submitted sample/order actions reconcile before resume.',
  'Persist one question per missing input/revision and consume the validated answer once. Emit immutable task/experiment/result/review proposals to the designated Lipi writer and canonical ops-document owner; queue through writer outage without a second writer.'],
 ['direction adapter and acknowledgement ledger','deduplicated question/resume flow','Lipi Jira/documentation outbox'],
 ['Old or duplicate direction cannot override newer accepted direction; external customer text cannot be owner direction.','Pause immediately before price/order submit blocks it; restart after question does not ask again.'],
 ['A real owner direction receipt names revision actually consumed and next action.','Native writer readback or explicit pending outbox state exists; stored file alone is not worker acknowledgement.'],
 'Pause direction effects and preserve append-only revisions/outbox; never rewrite prior experiment results.',
 'LIPI-22/23 prove recovery and repeated operation with these directions.',(4,7,'Lipi writer identity and valid owner intake route'),[],['LIPI-E06','LIPI-E08'],gates=['LIPI-G08'])

add('lipi',22,'Qualify independent Windows operations and recovery','Run one bounded Lipi operator without a Mac dependency or duplicate consumer.',
 ['services/lipi-autonomy/ops/windows/','services/lipi-autonomy/test/recovery/','ops/autonomy/recovery/'],['LIPI-15','LIPI-16','LIPI-21','SH-10','SH-11','SH-12','SH-13','SH-14'],['LIPI-I10'],
 ['Package pinned dependencies/config with host-local credential references, private data paths and Windows process-tree/job-object timeout cleanup; keep existing readonly service isolation and old watchdog removal evidence distinct from current health.',
  'Register explicit finite due jobs only after admission. Enforce per-run model/tool/token/time/currency caps,0 idle inference,2-repair maximum and actionable alert state transitions; P0 chargeback and12h fulfillment deadlines use cheap timers.',
  'Inject crash before submit,after provider accepts,before readback,after state commit and during owner pause; restore checkpoint/backup,cursor,claims,consumed grants and outbox, fence former owner and reconcile pending effects before takeover. Produce optional R730 migration manifest and rollback; no migration/i9 prerequisite.'],
 ['Windows service/runbook package','fault/restore evidence','alert/budget/isolation qualification','optional R730 manifest'],
 ['Killing the parent terminates its owned process tree only; unrelated release workers survive.','Stale owner cannot execute after restore; idle interval records0 inference and exhausted budget prevents paid fallback.'],
 ['One Windows cycle runs with mobile Mac disconnected and produces correct receipts.','Backup restore preserves one consumer,all pending effect knowledge and no cross-mission secret/customer access.'],
 'Disable only the new Lipi consumer,fence it,reconcile pending effects and restore last verified package/state; never awaken removed Mac watchdog.',
 'LIPI-23 independent exact-source autonomy acceptance; optional SH-16 migration later.',(6,11,'Current Windows runtime and host-local credentials unverified'),[],['LIPI-E03','LIPI-E06'],gates=['LIPI-G08'])

add('lipi',23,'Prove repeated end-to-end autonomous commerce cycles','Demonstrate operation, owner steering and recovery separately from launch and revenue.',
 ['ops/autonomy/acceptance/'],['LIPI-14','LIPI-17','LIPI-18','LIPI-20','LIPI-21','LIPI-22','SH-15'],['LIPI-I03','LIPI-I10'],
 ['Freeze exact source/task/policy hashes and independent reviewer identity; execute an authorized live observation→decision→permitted action→receiving-system readback→evaluation→next-action cycle.',
  'Repeat from the next due/event trigger without a new launch prompt. Exercise actual owner pause/resume/reprioritize plus crash after an accepted effect and restore without duplication; document model/tool/cost attribution.',
  'Retain real7-day operations evidence when that window elapses. If there are no real customers/orders, prove permitted price/content/read observation routes but leave paid-order/delivery/revenue business acceptance open; never buy merely to manufacture sales.'],
 ['exact-source independent review','two-cycle runtime receipts','direction/restart evidence','separate operating/business readiness report'],
 ['Each link uses actual event/action/destination IDs; synthetic fault fixtures are separately labeled.','Independent reviewer reproduces source checks and reconciles every uncertain effect; unresolved repair after2 attempts prevents autonomy acceptance.'],
 ['Autonomous operation is accepted only with repeated real authorized receipts,owner direction,recovery and bounded usage.','Paid/fulfilled demand and profitability stay separate measured criteria; blocked effect does not become success.'],
 'Stop new autonomous effects,retain read-only monitoring if allowed and hand exceptions to owner; restore qualified prior operator.',
 'Continue the accepted finite experiment queue; reopen failed gates with targeted tasks, not a fresh inventory.',(4,8,'Real authorized effects, reviewer and observation windows'),['LIPI-86','LIPI-87'],['LIPI-E02','LIPI-E03','LIPI-E04','LIPI-E06'],gates=['LIPI-G01','LIPI-G02','LIPI-G04','LIPI-G05','LIPI-G06','LIPI-G07','LIPI-G08'])

add('lipi',24,'Evaluate India-to-US apparel as a separate supplier experiment','Test the owner supplier hypothesis without assuming Printful proves India sourcing or replacing the catalog.',
 ['ops/autonomy/supplier-hypothesis/'],['LIPI-01'],['LIPI-I12'],
 ['Create a supplier comparison for an actual specific garment and US delivery route: manufacturer identity,provenance/material/size claims,design rights,MOQ/customization,capacity,packaging,delivery/tracking,returns address and defect terms; mark unavailable facts unknown.',
  'Use dated primary supplier/carrier/customs evidence to estimate full landed economics,FX,freight/duties/fees/returns and cash exposure separately from current Printful formulas. Obtain qualified owner/professional determinations for legal/import declarations; no outreach or purchase without exact authority.',
  'Predeclare one sample/pilot with budget and physical/delivery/20%-floor acceptance; compare with current capsule. After actual approved sample,accept/narrow/reject route and schedule next evidence collection; do not change English-first brand/catalog claims absent new owner decision.'],
 ['supplier hypothesis and evidence matrix','landed-cost sensitivity model','concrete sample/pilot decision and next experiment'],
 ['A Printful mapping cannot populate an India supplier claim.','Unknown duties/return costs or missing provenance prevent profitability/US-delivery promise.'],
 ['Specific supplier/product route has evidence or a precise collection task for each gap.','Offline research/model is useful now; contact,purchase/import and catalog changes remain separate gates with receipts.'],
 'Archive rejected hypothesis while preserving evidence; no existing capsule or provider account change.',
 'Run approved bounded supplier pilot or continue current capsule and recheck a named missing fact only when evidence can change.',(5,10,'Supplier quotes,legal/import review and real sample lead time'),[],['LIPI-E02','LIPI-E04','LIPI-E06'],gates=['LIPI-G04','LIPI-G09'])

# Guru: references are editorial assets; no runtime home or current account is inferred.
add('guru',1,'Choose and bind canonical Guru implementation home','Preserve editorial provenance and establish exact source/path ownership for executable work.',
 ['ops/guru-home-decision/ (in the selected repository after decision)','guru/ops/admission/ (proposed relative root)'],[],['GURU-I01'],
 ['Read the four-mission parent return once for an already-created Guru home; reuse it if current source and ownership are verified.',
  'If still absent, propose reusing pri8771/bots under guru/ as the minimal default or a separately deployable owner repository when justified; record exact repo/root/base and source owners before creating product files. Do not assume guru/sadhana-notes exists.',
  'Hash the10 preserved canonical Git blobs and bind accepted editorial imports with origin revision252d0bf18d11c47484ffcc2ab0a8ea56203a7076. Reconcile BOTS-61/128/129/130/132/133 via the current Windows parent; no competing Jira writer.'],
 ['canonical home decision receipt','source/provenance and ownership manifest','Jira matching proposal'],
 ['All10 Git blob SHA256 values match SOURCE_PROVENANCE; Windows CRLF bytes are not falsely called source corruption.','Unresolved home blocks product writes but not editorial source work in the assigned planning lane.'],
 ['Exact product repository/root/base is recorded before implementation.','Retained drafts remain withheld and historical; no current account/runtime claim is inferred.'],
 'Withdraw only proposed home/admission; preserve imported provenance and source.',
 'GURU-02–06 prepare the repeatable editorial and account contract.',(2,4,'Canonical home and worker return currently unverified'),['BOTS-61','BOTS-130'],['GURU-E01','GURU-E02','GURU-E04'],'reuse_and_verify')

add('guru',2,'Define audience, editorial promise and X-first charter','Make Guru a useful independent Hindu-spirituality editorial project with a clear ongoing audience objective.',
 ['guru/ops/charter/'],['GURU-01'],['GURU-I02'],
 ['Bind latest owner X-first direction and engaged Hindu-spirituality audience objective; keep Sadhana/Instagram as optional references,not mandatory identity or channel.',
  'Choose a bounded initial English editorial promise: contextual source-based reflections and practical questions for interested adults; document traditions/interpretations and uncertainty,avoid false guru/human authority and exclude Digital Temple.',
  'Define trust/engagement outcomes and audience questions before content: what readers find clear/useful,what context is missing,and which topics warrant the next sourced piece. Reuse current owner grants and name only real remaining inputs.'],
 ['editorial charter and persona','first audience hypothesis','scope/exclusion matrix'],
 ['Historical Instagram-only freeze cannot override current X-first direction.','Persona/bio cannot claim personal spiritual experiences,credentials,miracles or religious authority.'],
 ['Mission success is engaged truthful audience,not follower-to-revenue inference.','Editorial language,voice,scope and correction standard are executable content checks.'],
 'Restore prior draft charter; never rewrite historical mission decisions.',
 'GURU-03 source research and GURU-04 content production.',(2,4,'Audience format and account identity may require bounded decision'),['BOTS-128'],['GURU-E01','GURU-E02'],'reuse_and_verify')

add('guru',3,'Build sourced and rights-aware editorial research library','Replace empty source ledger with attributable evidence for each proposed religious/textual claim.',
 ['guru/content/sources/','guru/tests/source-ledger/'],['GURU-02'],['GURU-I03'],
 ['Select specific primary text edition/translation or authoritative scholarly/traditional source per claim; record passage,edition/translator,url/access date,rights basis and tradition/context. Default to original paraphrase; do not manufacture quotations or citations.',
  'Separate textual fact,interpretive tradition,editorial reflection and uncertain claim; create a claim-to-source ledger with bounded retrieval excerpts and expiry/refresh where content can drift.',
  'Research new pieces from recurring audience questions and named source gaps; withhold unsupported assertions and bind source revisions to review. Supplier/religious websites and comments remain untrusted inputs with no authority to issue commands.'],
 ['claim/source/rights ledger','bounded source collection pipeline','source gap queue'],
 ['Empty source entries,missing rights or mismatched passage fail content acceptance.','Prompt injection in a source cannot access credentials or amend publication permission.'],
 ['Every factual/quotation claim has an inspectable source and rights rationale or is withheld.','Original paraphrase and tradition/context labels are preserved through adaptation.'],
 'Quarantine disputed source/claims and invalidate affected unpublished candidates; public correction uses GURU-09.',
 'GURU-04 prepares original candidates and GURU-05 obtains cultural review.',(4,7,'Specific source rights and reviewer acceptance unresolved'),['BOTS-130','BOTS-129'],['GURU-E02'])

add('guru',4,'Implement original accessible content production queue','Create a repeatable next-piece pipeline using retained structures without copying their obsolete channel constraints.',
 ['guru/content/candidates/','guru/src/editorial/','guru/tests/editorial/'],['GURU-02','GURU-03'],[],
 ['Adapt pause/reading/gratitude structures into original X-first candidate posts or threads with exact source links,context and accessible media/alt; do not falsely present the secular placeholder drafts as sourced Hindu teachings.',
  'Implement draft→source_checked→cultural_review→technical_review→approved→scheduled→published states keyed by immutable content/hash. Prepare one excellent piece plus at least2 distinct next candidates rather than stopping at a canary.',
  'Bound generation/revision work to the admitted content brief,2 targeted repair rounds and measured model usage. Maintain a content calendar with due dates and freshness,not an idle generation loop.'],
 ['original first piece and2 next candidates','editorial state machine','accessibility/content checks'],
 ['Wrong source/alt,bad thread order,unsupported assertion or duplicate content blocks scheduling.','A source/wording change after review returns candidate to affected review state.'],
 ['Each candidate is original,inspectable and appropriate for the actual X format.','No publication/schedule success is inferred from draft creation.'],
 'Return candidate to draft and preserve versions; no public deletion.',
 'GURU-05 source/cultural review and GURU-08 publication when grants pass.',(5,9,'Qualified source and reviewer inputs'),['BOTS-129'],['GURU-E02'],'reuse_and_verify')

add('guru',5,'Implement attributable cultural and independent review','Make quality approval a real named decision bound to exact content.',
 ['guru/src/review/','guru/tests/review/','guru/ops/reviews/'],['GURU-03','GURU-04'],['GURU-I04'],
 ['Identify the actual cultural reviewer and scope of expertise; obtain acceptance of claim context,translation/paraphrase and depiction. Retained WITHHELD status remains until this receipt exists.',
  'Request independent source/technical review with reviewer identity/model/host and exact source/content hashes; cultural and technical review are distinct responsibilities.',
  'Persist approve/revise/withhold and reasons,repair at most2 times,then ask one specific unresolved question or stop affected candidate. Never label same-author/model self-check as independent review.'],
 ['review adapter/state transition','cultural and technical receipts','bounded repair packets'],
 ['Null reviewer,old content hash or merely copied historical approval cannot admit publication.','Third review attempt is refused unless a newly admitted scope explicitly grants it.'],
 ['Only exact approved payloads reach publication eligibility.','Cultural concern has a named owner and finite next action while unrelated drafts proceed.'],
 'Invalidate affected approval and withhold candidate; preserve completed review history.',
 'GURU-08 can publish a qualified candidate; source changes return to GURU-03.',(3,5,'Named cultural reviewer and attributable independent review'),['BOTS-130','BOTS-129'],['GURU-E02'],gates=['GURU-G02'])

add('guru',6,'Qualify supported account-bound X access','Establish the real Guru destination and allowed read/publish capabilities without creating duplicate or fictitious identities.',
 ['guru/ops/accounts/','guru/src/adapters/x-capability/','guru/tests/x-capability/'],['GURU-01'],['GURU-I05','GURU-I06'],
 ['Read the owner account registry and four-mission parent receipt; reuse verified Guru brand identity/admin/recovery owner. Routine account organization authority exists; exact handle,verification or paid entitlement gaps remain narrow inputs.',
  'Qualify supported X OAuth user context,account ID,read/publish/media/analytics scopes,API entitlement and quota/budget from current official docs. No paid plan or browser-automation workaround is assumed.',
  'Persist allowed operations and test readback of the authenticated intended account; keys stay in host-local secret storage. AI automated replies remain disabled pending prior written explicit X approval,applicable recipient opt-in/summoning rules and owner scope.'],
 ['account capability receipt','supported adapter contract','exact access/budget input record'],
 ['Wrong user ID,expired grant or exhausted/unknown paid allowance fails closed.','No private owner/other mission account is accepted as Guru destination; fake follower/import routes absent.'],
 ['Current account read receipt and supported capabilities are known,or a precise unavailable gate exists.','Draft/offline editorial work remains executable without publish access.'],
 'Revoke/disable only the new adapter grant as owner directs; preserve account and recovery ownership.',
 'GURU-07 runtime ingestion and GURU-08 approved publication.',(3,6,'Exact X identity,entitlement and allowed budget unverified'),['BOTS-130','BOTS-132'],['GURU-E01','GURU-E03'],gates=['GURU-G01'])

add('guru',7,'Integrate durable editorial state, claims and cheap scheduling','Give Guru one deterministic next-work loop with explicit content/account ownership.',
 ['guru/src/runtime/','guru/tests/runtime/'],['GURU-01','SH-02','SH-03','SH-04'],[],
 ['Map source-changed,review-returned,owner-direction,content-due,post-receipt,engagement-window-due and correction events into durable mission jobs/experiments/actions.',
  'Store content/source/direction hashes,attempt IDs,account/write scope,review state,next_check_at and evidence fingerprint; claim one mission/account effect at a time with fencing.',
  'Wake only on changed event or due time,select eligible content/research/review/observation task by priority,record compact decision and wait cheaply. No unchanged-input model polling or automatic publication from calendar alone.'],
 ['Guru shared-runtime integration','event/due scheduler','single-owner claim records'],
 ['Duplicate events/review deliveries create one eligible task; stale owner fails at action boundary.','Due wait with unchanged evidence incurs0 model calls.'],
 ['A restart-safe next-work selector progresses source→review→eligible action without repeated owner launch prompts.','Missing account/reviewer blocks only related effects and schedules useful offline work.'],
 'Pause Guru consumer and retain all durable records; no effect replay on restart.',
 'GURU-08/10/11 run publication,measurement and subsequent decisions.',(5,9,'Shared state/claims integration'),[],['GURU-E01','GURU-E04'])

add('guru',8,'Publish reviewed content and verify the real destination','Ship one qualified piece and a repeatable receipt-bound publishing pipeline.',
 ['guru/src/adapters/x-publish/','guru/tests/x-publish/','guru/ops/publications/'],['GURU-05','GURU-06','GURU-07','SH-06','SH-10'],['GURU-I06'],
 ['At effect boundary recheck exact account,source/content/review/direction hashes,grant,cadence,quota and fencing; persist intent and expected content before publishing.',
  'Use supported manage-post/media routes,record returned post/media IDs and verify actual author,content/thread order,media,alt,permalink and timestamp via receiving-system readback.',
  'On timeout or partial thread publication mark uncertain,search bounded account/destination evidence by known post ID/time/payload and reconcile before retry. Duplicate detection survives restart; unconfirmed delivery never becomes published.'],
 ['publishing adapter and action ledger','public permalink/readback receipt','partial-thread recovery plan'],
 ['Crash after external acceptance before local commit yields one post after reconciliation.','A superseding owner pause or changed content review stops new post actions.'],
 ['One real authorized correct-account piece has receiving-system evidence.','Next reviewed piece can run from a scheduled/event trigger with the same controls.'],
 'Stop future posts; correction/deletion only within exact grant and after destination reconciliation. Deleted posts are not assumed recoverable.',
 'GURU-10 observes declared metrics; GURU-09 handles concerns.',(5,9,'Exact publication grant and supported route'),['BOTS-132'],['GURU-E02','GURU-E03'],gates=['GURU-G01','GURU-G02','GURU-G03'])

add('guru',9,'Operate moderation, correction and permitted engagement','Respond to real concerns while preserving trust and platform permission boundaries.',
 ['guru/src/moderation/','guru/tests/moderation/','guru/ops/corrections/'],['GURU-06','GURU-07','SH-06','SH-12','SH-13'],['GURU-I07'],
 ['Collect permitted mentions/replies/flags tied to published IDs,store minimum references and classify cultural/source error,identity confusion,abuse and genuine topic requests; do not infer an individual religion.',
  'Draft grounded responses and correction notices,route cultural/source concerns to named reviewer and pause affected claims. Preserve original post/content and corrected version with transparent rationale.',
  'Enable only explicitly authorized correction/delete/moderation actions with receiving-system receipts. AI automated replies require prior written explicit X approval plus current recipient opt-in/summoning and opt-out rules; default to owner-reviewed drafts. No unsolicited DMs,keyword outreach,follow loops or sensitive-faith targeting.'],
 ['moderation and correction queue','account-bound correction receipts','engagement permission checks'],
 ['Malicious comment cannot change policy or obtain private data.','Duplicate interaction,opt-out,unsummoned self-serve reply or missing X AI-reply approval prevents automated reply.'],
 ['Every material concern gets one actionable owner/reviewer route and status.','Corrections are verified at destination; reply drafts are not counted as sent engagement.'],
 'Pause automated interaction and preserve evidence; public restoration/deletion is a separate authorized act.',
 'GURU-11 uses aggregate concerns and useful questions to select next editorial work.',(4,8,'Moderation scope and platform reply permissions'),[],['GURU-E02','GURU-E03'],gates=['GURU-G04'])

add('guru',10,'Collect trustworthy engagement and audience observations','Measure actual audience outcomes without inventing unavailable reach or identity facts.',
 ['guru/src/measurement/','guru/tests/measurement/','guru/ops/metrics/'],['GURU-06','GURU-07','SH-04','SH-13'],['GURU-I06'],
 ['Declare account/post universe,start/end time,baseline and collection route before experiment; collect follower counts,per-post impressions where accessible,replies/bookmarks or other actual supported metrics with definitions and coverage.',
  'Record meaningful engagement as source-relevant questions,voluntary usefulness feedback and repeat interactions using aggregate/minimized references. Separate own tests and unknown/bot/human status; do not claim religious affiliation.',
  'Use due-time collection/cursors and provider rate limits,retain missing values as null and distinguish gross cross-platform follows from unique people if a later channel is added.'],
 ['versioned metric contract','aggregate observations with provenance','data completeness report'],
 ['Missing impressions are null,not zero; sum of per-post unique reach cannot become unique audience.','Replay of an observation does not double count followers or interactions.'],
 ['Baseline and every observation have dates,source and coverage.','No follower-to-revenue or traffic-to-trust claim is fabricated.'],
 'Stop collection and retain approved aggregate records per retention policy; invalidate affected derived metrics.',
 'GURU-11 evaluates at the frozen window boundary.',(4,7,'Current analytics entitlement and elapsed window'),['BOTS-133'],['GURU-E01','GURU-E03'])

add('guru',11,'Evaluate editorial experiments and automatically choose the next','Turn audience evidence into a continuing finite editorial learning loop.',
 ['guru/src/experiments/','guru/tests/experiments/','guru/ops/experiments/'],['GURU-04','GURU-07','GURU-10','SH-05','SH-07','SH-09'],[],
 ['Freeze hypothesis,budget,voice/format intervention,baseline,window,minimum evidence and stop criteria; first proposal compares concise contextual reflection vs source-led question over an owner-admitted14-day window,not a claim that14 days elapsed.',
  'At due time evaluate trust concerns and relevant engagement with data coverage; declare supported/unsupported/inconclusive without inferring causality from tiny samples.',
  'Select next task without a new launch prompt: factual concern→source correction; views/no meaningful response→test clearer question/context; useful repeated question→next sourced piece; access outage→offline reviewed backlog; sustained poor fit→bounded topic/format revision. Persist rationale,version and next due event with outbox.'],
 ['experiment planner/evaluator','next-candidate selector','two-cycle decision ledger'],
 ['Negative/inconclusive experiment retains valid evidence and leads to one bounded next decision.','Same evidence/direction fingerprint creates no duplicate experiment or idle model call.'],
 ['Two completed decision cycles produce reviewed next work or an evidence wait with clear due trigger.','No revenue promise or excluded-product conversion is introduced.'],
 'Pause intervention and preserve original experiment/result; never relabel old outcome after direction changes.',
 'Admit selected research/content/correction task and repeat.',(5,8,'Actual audience evidence and observation time'),['BOTS-133','BOTS-61'],['GURU-E01','GURU-E02'])

add('guru',12,'Consume owner direction, questions and documentation outboxes','Make pause,resume and audience/topic changes durable and acknowledged once.',
 ['guru/src/direction/','guru/src/outbox/','guru/tests/direction/'],['GURU-07','SH-08','SH-09'],['GURU-I08'],
 ['Consume authenticated mission DIRECTION.md version at job start and before effects; persist seen/applied/pending-reconciliation/needs-input/superseded states.',
  'Exercise pause Guru publishing,focus on the Bhagavad Gita with specific source context,and make posts shorter; scope changes affect unstarted work and preserve old experiments. Do not reinterpret shorter tone as permission to remove source context.',
  'Persist one source/reviewer/account question keyed by input revision,validate answer and resume dependent work. Write immutable Jira/content/experiment/review/result proposals to the Windows parent; writer outage queues and later reconciles native readback without another writer.'],
 ['owner-direction acknowledgement','question/answer resume ledger','Jira/documentation outbox'],
 ['Duplicate/older owner direction and untrusted audience comments cannot change current authority.','Pause after post submit reconciles actual post; it does not assert canceled.'],
 ['Actual consumed revision,next action and affected experiment are observable.','Unchanged unresolved input sends no repeated question; writer status is pending until native readback.'],
 'Pause new directional effects while retaining revision and receipt history.',
 'GURU-14/15 prove restart and real direction acceptance.',(4,6,'Current owner intake and writer receipt route'),[],['GURU-E04'])

add('guru',13,'Enforce mission privacy, usage limits and alerts','Keep a small editorial operation bounded,isolated and understandable when intervention is needed.',
 ['guru/src/policy/','guru/tests/policy/','guru/ops/limits/'],['GURU-06','GURU-07','SH-12','SH-13','SH-14'],['GURU-I06','GURU-I08'],
 ['Store only secret references and minimal public post/aggregate data; separate Guru identity,credentials and runtime storage from Kai/Pri/Lipi/other missions. Never export private chat data or infer sensitive-faith profiles.',
  'Enforce approved local/model/tool/time/token/currency and content/review limits at job/tool boundaries. Measure actual model/version/host/usage; deny unknown paid route or implicit fallback and record0 idle inference.',
  'Emit actionable alerts only for meaningful change: cultural/source concern,wrong-account attempt,grant failure,unreconciled effect,quota exhaustion or recovery failure. Deduplicate and clear alerts with evidence; do not alert on every unchanged wait.'],
 ['privacy/usage policy adapter','alert routing and deduplication','sanitized audit records'],
 ['Prompt injection and cross-mission credential lookups are rejected.','Exhausted cap prevents a paid action and repeated unchanged faults produce one alert.'],
 ['Budget and data boundaries are executable and attributable.','Blocked effect leaves source/editorial offline work eligible.'],
 'Disable affected integration and purge only according to retention policy; preserve minimal audit evidence.',
 'GURU-14 qualified deployment and GURU-15 acceptance.',(4,7,'Owner-approved caps and alert destination'),[],['GURU-E01','GURU-E03','GURU-E04'])

add('guru',14,'Package independent Windows runtime and safe restore','Run Guru through Windows interruptions with one account consumer and no Mac dependency.',
 ['guru/ops/windows/','guru/tests/recovery/','guru/ops/migration/'],['GURU-07','GURU-08','GURU-12','GURU-13','SH-10','SH-11'],['GURU-I08'],
 ['Package pinned source/config and durable state paths; qualify Windows startup,working directory,UTF8,log redaction,process-tree timeout cleanup and host-local credentials.',
  'Fault-test before publish,after external accept,before receipt persist,during partial thread and during owner pause; fence old owner,reconcile real destination,restore backup/cursors/consumed grants and resume one eligible job.',
  'Prove operation with mobile Mac disconnected. Prepare optional R730 transfer manifest,stop/fence/source/backup checksum and rollback acceptance,without deploying or making it a launch requirement; i9 remains deferred.'],
 ['Windows deployment/runbook','recovery and stale-owner evidence','optional R730 migration contract'],
 ['Child process tree cleanup affects only owned Guru processes.','Restore never duplicates a post/response or restarts old listeners;0 idle inference persists.'],
 ['One independent Windows job and controlled restart preserve receipts and one consumer.','R730 migration is proposed/qualified separately; host presence is not execution proof.'],
 'Stop and fence only new Guru consumer,reconcile pending effects and restore last known-good state/package.',
 'GURU-15 demonstrates repeated real cycles.',(5,9,'Current Windows integration and storage qualification'),[],['GURU-E01','GURU-E04'])

add('guru',15,'Accept repeated real editorial autonomy with independent review','Prove the complete operation instead of declaring a published post an autonomous bot.',
 ['guru/ops/acceptance/'],['GURU-08','GURU-09','GURU-10','GURU-11','GURU-12','GURU-13','GURU-14','SH-15'],['GURU-I04','GURU-I06','GURU-I08'],
 ['Bind exact source/content/task/policy hashes and independent reviewer identity; perform real authorized source observation→editorial decision→qualified post→receiving-system readback→metric evaluation→next decision.',
  'Repeat automatically from next admitted due/event trigger; demonstrate actual owner pause/shorter-direction/resume and crash after external acceptance without duplicate posts.',
  'Retain measured usage,real permalink/account and current source/cultural reviews. Synthetic fault cases stay labeled; missing publication access means prepared/tested only and missing real audience data means business validation open.'],
 ['independent exact-source review','two real-cycle receipt chains','owner-direction and recovery evidence','separate runtime/audience acceptance report'],
 ['Reviewer checks actual source and destination receipts,not author done-text.','At most2 repairs; absent cultural/real action/readback evidence prevents autonomy acceptance.'],
 ['Repeatable operation,owner steering and restart meet all18 autonomy requirements.','Audience growth is honestly observed,not guaranteed or inferred from generated content.'],
 'Pause external actions and retain permitted readonly observation; route unresolved concerns to named owner.',
 'Continue finite editorial experiments or run GURU-16 only when its hypothesis is admitted.',(4,7,'Real authorized publication,reviewer and observation window'),['BOTS-132','BOTS-133','BOTS-61'],['GURU-E01','GURU-E02','GURU-E03'],gates=['GURU-G01','GURU-G02','GURU-G03','GURU-G04'])

add('guru',16,'Evaluate later format or channel expansion without mission drift','Keep long-term growth executable while preserving current X-first priority and evidence boundaries.',
 ['guru/ops/expansion/'],['GURU-11'],['GURU-I09'],
 ['Only after evaluated demand proposes a specific benefit,compare one adjacent format/channel against current X audience evidence,cost,rights,moderation and supported publishing/measurement route.',
  'Reuse Sadhana carousel structure if culturally reviewed and suited to the selected channel; establish exact brand account/capability and new baseline rather than treating old Instagram selection as authority.',
  'Predeclare bounded experiment,resource/grant needs and continuation/stop decision. Keep monetization an optional separately justified future offer; exclude Digital Temple,unsolicited outreach,fake followers and paid spend without exact new scope.'],
 ['one-channel/format expansion decision','account/capability and metric plan','admitted next experiment or explicit no-go'],
 ['New channel cannot reuse another mission credentials or count its followers as unique people.','No expansion can bypass source/cultural review or known budgets.'],
 ['Expansion has evidence-based rationale,concrete tasks/gates and independent path to stop.','X-first useful operation remains available if expansion is rejected or blocked.'],
 'Stop new channel scheduling and preserve original X experiment baseline/account.',
 'Run the admitted finite channel test through the same claim/action/review/measurement interfaces,then return to GURU-11.',(3,6,'Demand evidence and optional account capability'),[],['GURU-E01','GURU-E02','GURU-E03'],gates=['GURU-G05'])

add('guru',17,'Deliver the useful native Guru release through its existing parent','Allow a reviewed correct-account first publication while later shared-runtime integration proceeds independently.',
 ['guru/ops/native-release/'],['GURU-04','GURU-05','GURU-06'],['GURU-I06'],
 ['Consume the Windows parent existing admission,exclusive account/source ownership and supported native publication route. Reuse any already-released exact candidate and receipt instead of publishing it again.',
  'Prepare a finite original piece with source/cultural/technical hashes,exact account grant,rollback/correction plan and durable native intent record. Submit only after current preconditions; capture post ID and author/content/media/permalink readback.',
  'If response is ambiguous,persist uncertain and reconcile the intended destination before retry. Return exact source,reviewer,commands,post receipt and measurement baseline to the parent. No shared-framework rewrite,scheduler or R730 migration is a prerequisite.'],
 ['native release intent and receipt','first-useful-piece public verification','parent return and measurement baseline'],
 ['Candidate already published or uncertain cannot be submitted a second time.','Wrong account,missing source/cultural review or absent current grant blocks only publication;offline editorial work continues.'],
 ['The exact qualified piece is publicly verified on its intended account or existing verified receipt is reused.','Native useful release is recorded separately from GURU-15 autonomous-operation acceptance.'],
 'Pause subsequent native actions; apply only qualified correction/deletion scope with receiving-system readback and retained original evidence.',
 'GURU-10/11 evaluate this piece; GURU-07/08 integrate repeated autonomous operation separately.',(2,4,'Parent native release return and publication capability'),['BOTS-132'],['GURU-E01','GURU-E02','GURU-E03'],gates=['GURU-G01','GURU-G02','GURU-G03'])

# Effect gates are a union of applicable effect classes, never a conjunction
# requiring unrelated purchase/reply/migration authority for an original post.
GATE_SCOPES={
 'LIPI-G01':'External shop/provider read or private mapping change only: intended account,current scoped supported route and any required existing grant.',
 'LIPI-G02':'Live retail price change only: existing conditional owner authority,current worst-case20% math,exact before/after and required Jira/worklog admission; no new generic price approval.',
 'LIPI-G03':'Discount change or free-shipping activation only: exact action-time owner grant,mixed-cart economics and cadence/expiry rules.',
 'LIPI-G04':'Sample/purchase/charged test/provider order or paid supplier action only: exact identities,total,currency,cap,expiry and owner grant.',
 'LIPI-G05':'Policy publication,customer send,refund,replacement or chargeback handling only: apply the specific owner-controlled operation; refund/replacement autonomous cap0 and chargebacks owner-only.',
 'LIPI-G06':'Public product/theme/catalog/shared-surface cutover only: exact independent review,owner launch grant,preimage and reversible rollback.',
 'LIPI-G07':'Organic publication/lifecycle marketing effect only: actual account,exact content/cadence grant,live destination,consent where applicable; paid ads remain disabled.',
 'LIPI-G08':'New runtime/startup/model/tool/alert route only: admitted source,exclusive owner,private storage,existing route and finite allowed caps; no monetary allowance inferred.',
 'LIPI-G09':'Supplier contact/import/pilot/catalog expansion only: exact outreach/purchase/import declaration authority and owner-approved scope; offline research is independent.',
 'GURU-G01':'X account read/publish capability for the requested operation only: intended account,supported route,scope,quota and existing budget.',
 'GURU-G02':'Religious/source claim publication only: exact source/rights,cultural and independent content review.',
 'GURU-G03':'Original post/media/thread publication only: exact current account/content/cadence grant and reversible correction plan.',
 'GURU-G04':'Reply/moderation/correction/delete effect only: operation-specific grant. Automated AI replies additionally require written explicit X approval and applicable opt-in/summon/opt-out rules; original-post autonomy does not depend on reply approval.',
 'GURU-G05':'Optional additional channel/format effect only: evidence-based experiment,new exact account/route and grant/budget. X-first operation remains independent.'}

for m,items in tasks.items():
 for t in items:
  t['mission']='LIPI' if m=='lipi' else 'GURU'
  t['conditional_dependencies']=[]
  t['effect_gate_applicability']=[{'gate_id':g,'condition':GATE_SCOPES[g]} for g in t['effect_gates']]
  t['conditional_effect_gates']=[{'condition':GATE_SCOPES[g],'gates':[g]} for g in t['effect_gates']]
  t['effect_gate_semantics']='effect_gates is a capability-gate catalogue. Evaluate each conditional_effect_gates entry only for its named actual action class; never require all unrelated gates as a conjunction.'
  t['completion_rule']='A blocked/missing-input/failure record may finish a preparation subunit only. This task is not capability/release complete until its positive checks and relevant real effect acceptance pass. Disabled unrelated effect classes do not block a qualified allowed class; claimed scope is explicit.'

def task(m,n): return tasks[m][n-1]
def conditional(m,n,condition,deps,acceptance):
 task(m,n)['conditional_dependencies'].append({'condition':condition,'dependencies':deps,'acceptance':acceptance})

task('guru',1)['owned_paths']=['guru/ops/home-decision.json','guru/ops/admission/']
task('lipi',7)['dependencies']=['LIPI-01']
conditional('lipi',7,'Actual retained-capsule launch/price/shipping economics; offline scenario modeling is independent.',['LIPI-02'],
 'Bind owner-accepted membership. Require positive exact variant mapping for every included product and exclude explicitly rejected/withheld variants. Conditional Quiet Route never blocks the other accepted capsule products.')
for n,name in [(3,'Meridian'),(4,'Open Current'),(5,'Quiet Route'),(6,'Threshold Study')]:
 conditional('lipi',7,name+' is included in the actual permitted selling/sample basket.',['LIPI-%02d'%n],
  'Current exact mapping/cost/availability evidence for that included product must pass before treating its actual economics as qualified; otherwise its basket remains blocked,while unrelated scenarios continue.')
task('lipi',7)['implementation_steps'][0]+=' Contribution percent=contribution/(R+customer shipping); reject nonpositive denominator. Represent cents and rate arithmetic exactly using integer/rational intermediates and round only the final displayed money; threshold comparisons use unrounded values. Collected/remitted pass-through tax is excluded from revenue; fee bases follow actual provider rules. Preserve dated owner no-collection posture as an assumption and include any actually absorbed/import cost only when evidenced.'
conditional('lipi',16,'Live price change requiring existing Jira/worklog before/after projection.',['SH-09'],
 'Verify current writer admission and required price logging evidence before the price effect. An unrelated refund,purchase,publish,marketing grant is not required for price-only scope.')
conditional('lipi',19,'Actual organic publication linking to the capsule;offline content/discovery preparation proceeds.',['LIPI-14'],
 'The exact current product/landing destination must be publicly verified and sale-eligible before sending traffic.')
conditional('lipi',22,'Optional R730 migration or host transfer only;Windows acceptance is independent.',['SH-16'],
 'Qualify target storage/backup/secret references,fence previous owner,reconcile pending effects and prove new-host receipt/rollback before cutover.')
conditional('guru',14,'Optional R730 migration only;Windows original-post autonomy is independent.',['SH-16'],
 'Qualify target,restore checksum and exclusive ownership with receiving-host receipt before migration.')
task('lipi',19)['acceptance'][0]='One authorized post has exact real destination evidence and attribution. A fully prepared offline candidate is preparation only and does not satisfy publication acceptance.'
task('lipi',14)['acceptance'][0]='Approved capsule and consistent shared surfaces are publicly verified. Any partial cutover keeps release acceptance incomplete until reconciled and repaired or rolled back.'
task('lipi',13)['acceptance'][0]='Exact-source independent review and private recovery must pass;failed/withheld review leaves release acceptance incomplete.'
task('guru',6)['acceptance'][0]='Current intended-account read receipt and supported capabilities must be verified before capability acceptance. A precise unavailable gate completes intake only,not access acceptance.'
task('lipi',23)['acceptance'][0]='Autonomous operation requires TWO completed real allowed observation-decision-action-verified-result-next-decision cycles,plus actual owner direction,recovery and bounded usage. A scheduled wait or second prepared decision is valid operation but cannot substitute for the second completed real cycle.'
task('guru',15)['acceptance'][0]='Original-post autonomous operation requires TWO completed real allowed observation-decision-publication-verified-result-evaluation-next-decision cycles,actual owner steering and restart. A wait or prepared second candidate does not substitute. Reply automation is an optional separately gated class.'

AUTONOMY={
 'A01':('Durable single-owner state,claims and fencing',['SH-02','SH-03']),
 'A02':('Deterministic event/due scheduling and zero unchanged-input inference',['SH-04']),
 'A03':('Persist evidence-based decisions and source fingerprints',['SH-05']),
 'A04':('Execute only eligible effects and verify receiving-system result',['SH-06']),
 'A05':('Evaluate experiments and select the next finite decision',['SH-07']),
 'A06':('Consume owner nudges and acknowledge the actual revision',['SH-08']),
 'A07':('Ask once for missing input,validate answer and resume',['SH-08']),
 'A08':('Automatic immutable Jira/documentation outboxes and native readback',['SH-09']),
 'A09':('Bound retries and attributable review/repair attempts',['SH-10']),
 'A10':('Deduplicate events,actions and outgoing projections',['SH-06']),
 'A11':('Reconcile uncertain external effects before retry or takeover',['SH-06']),
 'A12':('Windows process-tree cleanup and bounded execution',['SH-11']),
 'A13':('Crash/restart/checkpoint/backup restore without lost effects',['SH-11']),
 'A14':('Actionable alerts and quiet unchanged states',['SH-12']),
 'A15':('Privacy,secret references and cross-mission isolation',['SH-13']),
 'A16':('Enforced model/tool/token/time/spend limits and zero idle inference',['SH-14']),
 'A17':('Exact-source independent review and repeated real end-to-end cycles',['SH-15']),
 'A18':('Independent Windows operation and optional fenced R730 migration',['SH-11','SH-16'])}
AMAP={
 'lipi':[[15,16],[15,20],[16,20],[16,17,18,19],[20],[21],[21],[20,21],[16,22,23],[15,16,21],[8,16,17,22],[22],[22,23],[17,18,22],[15,18,22],[16,20,22],[13,23],[22,23]],
 'guru':[[7,8],[7,10],[7,11],[8,9],[11],[12],[12],[11,12],[5,8,14],[7,8,12],[8,9,14],[14],[14,15],[9,13],[3,9,13],[4,7,13],[5,15],[14,15]]}
OUTCOMES={
 'lipi':[
 ('Reuse accepted25 local contracts and reconcile current source/external residuals',[1]),
 ('Approved capsule/design direction and exact membership',[2]),
 ('Accurate variant-level Shopify/Printful product mappings',[3,4,5,6]),
 ('Worst-case20% all-in contribution with10% reserve and evidenced US shipping',[7]),
 ('Purchase-ready sample decision,authorized order and physical delivery/quality acceptance',[8,9]),
 ('Consistent accessible product content,media and coordinated storefront',[10]),
 ('Policies,consent,privacy and accountable customer support',[11,18]),
 ('Correct checkout,payment and transactional journey',[12]),
 ('Reviewed launch,restore and real public cutover/readback',[13,14]),
 ('Actual fulfillment,inventories/exceptions and owner-gated remedies',[15,17,18]),
 ('Organic first-customer acquisition and repeatable content/discovery',[19]),
 ('Measured profitable delivered orders,customer experience and continuing experiments',[20]),
 ('Real bounded autonomous commerce operation with course correction and recovery',[15,16,21,22,23]),
 ('Separate evidence-based India-to-US supplier/product pilot hypothesis',[24])],
 'guru':[
 ('Verified canonical implementation home and preserved editorial provenance',[1]),
 ('X-first independent Hindu-spirituality editorial identity with meaningful audience goal',[2]),
 ('Accurate sourced rights-aware contextual claims',[3]),
 ('Original accessible first piece plus repeatable next-content production',[4]),
 ('Named cultural and independent exact-content review',[5]),
 ('Correct-account supported publishing capability',[6,8,17]),
 ('Real publication,moderation,correction and qualified engagement receipts',[8,9,17]),
 ('Trustworthy follower,exposure,usefulness and trust measurement',[10]),
 ('Finite audience experiments and repeated next decisions',[11]),
 ('Owner-directed bounded independent autonomous Windows operation',[7,12,13,14,15]),
 ('Evidence-led later format/channel growth without excluded mission drift',[16])]}

def dump(path,data):
 path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def write_requirements(m):
 p='LIPI' if m=='lipi' else 'GURU'; rows=[]
 for i,(text_,ns) in enumerate(OUTCOMES[m],1):
  selected=[f'{p}-{n:02}' for n in ns]
  rows.append({'id':f'{p}-O{i:02}','mission':p,'requirement':text_,'task_ids':selected,'evidence_refs':[f'{p}-E01'],
               'acceptance':[a for t in tasks[m] if t['id'] in selected for a in t['acceptance']]})
 for i,(key,(text_,shared)) in enumerate(AUTONOMY.items()):
  selected=[f'{p}-{n:02}' for n in AMAP[m][i]]
  rows.append({'id':f'{p}-{key}','mission':p,'requirement':text_,'task_ids':selected+shared,
    'evidence_refs':[f'{p}-E03' if m=='lipi' else 'GURU-E04'],
    'acceptance':[a for t in tasks[m] if t['id'] in selected for a in t['tests']]})
 for t in tasks[m]: t['requirement_ids']=[r['id'] for r in rows if t['id'] in r['task_ids']]
 return rows

def cards(m):
 out=['# '+('Lipi Standard' if m=='lipi' else 'Guru')+' executable task cards','',
 'All tasks are proposed incremental work. Existing accepted work is reused; runtime/business completion is not claimed. Product paths are proposed future ownership reservations; select exact canonical source and serialize conflicting paths through admission. Estimates are engineering effort only; observation/shipping/owner waiting is excluded.','']
 for t in tasks[m]:
  out += ['## '+t['id']+' — '+t['title'],'',t['goal'],'',
    '- Status: '+t['status'], '- Owner: '+t['owner_role'], '- Source: '+t['source_repo'],
    '- Owned paths: '+ '; '.join('`'+x+'`' for x in t['owned_paths']),
    '- Evidence: '+', '.join(t['evidence_refs']),'- Dependencies: '+(', '.join(t['dependencies']) or 'None'),
    '- Inputs: '+('; '.join(t['prerequisite_inputs']) or 'No additional owner input for offline work'),
    '- Effect gates: '+(', '.join(t['effect_gates']) or 'No external effect authorized by this task preparation'),
    '- Requirements: '+', '.join(t['requirement_ids']), '', 'Implementation steps:','']
  out += [str(i)+'. '+s for i,s in enumerate(t['implementation_steps'],1)]
  if t['conditional_dependencies']:
   out += ['', 'Conditional dependencies (only the named effect branch):','']
   out += ['- '+c['condition']+' Requires '+', '.join(c['dependencies'])+'. '+c['acceptance'] for c in t['conditional_dependencies']]
  if t['effect_gate_applicability']:
   out += ['', 'Effect-specific gate applicability:','']
   out += ['- '+g['gate_id']+': '+g['condition'] for g in t['effect_gate_applicability']]
  for label,key in [('Deliverables','deliverables'),('Pass/fail checks','tests'),('Acceptance','acceptance')]:
   out += ['',label+':','']+['- '+s for s in t[key]]
  out += ['', 'Completion rule: '+t['completion_rule'],'', 'Review: '+ ' '.join(t['review'].values()),'', 'Rollback: '+t['rollback'],'',
   'Next eligible action: '+t['next_eligible_action'],'',
   f"Planning estimate: {t['estimate']['low']}–{t['estimate']['high']} engineering hours. "+t['estimate']['assumptions']+' Dependency risk: '+t['estimate']['dependency_risk']+'.','',
   'Jira: actual key null. Candidates '+(', '.join(t['jira']['candidates']) or 'none established')+'. '+t['jira']['matching_action']+' Writer: '+t['jira']['writer']+'.','']
 return '\n'.join(out)

for mission in tasks:
 folder=ROOT/'missions'/mission
 req=write_requirements(mission)
 dump(folder/'TASKS.json',tasks[mission]); dump(folder/'requirements.json',req)
 (folder/'TASKS.md').write_text(cards(mission),encoding='utf-8')

# Current and retained evidence remain distinct.
def evidence(i,repo,ref,path,classification,finding,limits,time=NOW):
 return dict(id=i,repository=repo,ref=ref,path=path,observed_at=time,classification=classification,finding=finding,proof_limits=limits)

le=[
 evidence('LIPI-E01',LREPO,LREF,'AGENTS.md; MEMORY.md; ops/DECISIONS.md',['cloud_backed','live_observed'],'Fresh private remote main cloned clean; Windows store execution decision and English-first brand/source ownership read. Current remote heads also include4e77ab6 and52954f1.','Repository observation only; old runtime/store claims in MEMORY are historical. No source mutation,worker contact or live store read.'),
 evidence('LIPI-E02','pri8771/astra-bot-launch',BASE,'focus/kai-pri-lipi/LIPI_EVIDENCE.md; directions/lipi.md',['historical','cloud_backed'],'Retained Sept12 04:31:30 return reports25 LIPI-63–87 local contracts satisfied,56 aggregate checks,readiness false,7 records/23 unknowns. Sample packet null totals and natural tote hint conflict remain documented.','Raw retained return and exact37c447b commit unavailable from current remote (not our ref); no proof of current merge,live sales or completed external acceptance.'),
 evidence('LIPI-E03',LREPO,LREF,'services/lipi-control-plane/README.md; src/mcp/tool-registry.ts; src/domain/action-envelope.ts; tools/verify_openclaw_control_plane.py',['cloud_backed','implemented_tested'],'Source inspected and structural verifier executed:28 required files,11 allowlisted tools,readonly/mock only,disconnected providers,no mutation executor. ActionEnvelope approval consumes an in-memory Set and is not durable effect execution.','TypeScript unit suite not executed or dependencies installed; structural pass is not runtime/live provider acceptance.'),
 evidence('LIPI-E04',LREPO,LREF,'ops/BUSINESS_RULES.md; outputs/unit-economics-template.md; ops/STATE.md; ops/DECISIONS.md',['cloud_backed','historical'],'Binding20% all-in floor,10% net item revenue reserve,$99 conditional free-US-shipping,conditional price authority,owner-only discounts/refunds/replacements/purchases/customer sends,no paid ads. Held/failed≤12h,unshipped3 business days,reply target1 business day.','Dated owner rules are retained authority,not current provider costs/legal determination/live store state. Historical tax decision preserved without new advice.'),
 evidence('LIPI-E05',LREPO,LREF,'tools/check_launch_readiness.py; planning/autonomy-complete/missions/lipi/fresh-main-readiness.json',['cloud_backed','implemented_tested'],'Executed fresh main aggregate:31/31 pass,repository_consistent true,launch_candidate_ready false,7 records(6 verification_pending,1 blocked),23 unknowns; control structural check passed.','Initial system Python lacked Pillow and default encoding caused fixture error; bundled Python with PYTHONUTF8=1 resolved without installs/source edits.31 is this revision,not retained56. No live platform checks.'),
 evidence('LIPI-E06','pri8771/astra-bot-launch',BASE,'focus/kai-pri-lipi/OWNER_DIRECTION.md; HOST_PLAN.md; LIPI_EVIDENCE.md',['cloud_backed','historical'],'Owner direction contract is recorded-not-consumed. Sept7 watchdog removal supersedes stale Mac active-watchdog notes; R730 target,Windows temporary independent execution,i9 deferred.','No actual running direction consumer or current host health verified. Kai/Pri only shared capability boundaries,not additional roadmaps.'),
 evidence('LIPI-E07',LREPO,'52954f1f3d07f160a414713250923993a7d5f3f5','quality/session4/capsule-media/retained-candidate-contract.json',['cloud_backed','historical'],'Current cloud branch inspected:Meridian/Open Current/Threshold Study baseline,Quiet Route conditional,final_membership_decided false,sample_approved false,publication_ready false. Main lacks session12h/session24h retained contracts.','Read git blob only; branch36-check hosted claim not rerun. Exact later25-contract state remains a targeted reconciliation gap.'),
 evidence('LIPI-E08','Atlassian read-only snapshot',None,'planning/autonomy-complete/evidence/JIRA_READBACK.json',['live_observed','local_only'],'Root read-only observation2026-09-12T21:13:05.833Z:all25 LIPI-63–87 issues In Review; original estimates preserved,actual time absent.','Metadata is not acceptance,worklog,source admission or permission to write. Exact task bindings remain null and Lipi writer needs designation.', '2026-09-12T21:13:05.833Z'),
 evidence('LIPI-E09','Official provider documentation','observed2026-09-12','https://shopify.dev/docs/api/admin-graphql/latest ; https://developers.printful.com/docs/v2-beta/',['live_observed'],'Shopify official current GraphQL reference and Printful official V2 beta documentation read as adapter qualification sources.','No account entitlement,credentials,paid route or provider availability established. Executor must pin supported API version and exact capability before use; beta docs are not production approval.')]
ge=[
 evidence('GURU-E01','pri8771/astra-bot-launch',BASE,'reference/MISSION_GOALS.md; WINDOWS_RELEASE_EXECUTION.md; BOT_ROADMAPS.md; REPO_CLOUD_AUDIT.md',['cloud_backed','historical'],'Owner current Guru mission is engaged Hindu-spirituality audience,X-first. Editorial candidates are preserved; no runnable canonical Guru home established. Four-mission release parent owns Guru integration and Jira writes.','Release-worker changes after base unobserved; future executor must consume exact return. No live account/publication/audience/runtime claim.'),
 evidence('GURU-E02','pri8771/astra-bot-launch',BASE,'reference/guru-sadhana-candidate/SOURCE_PROVENANCE.json and10 named candidate files',['cloud_backed','historical','implemented_tested'],'All10 canonical Git blob SHA256 values verified against preserved source252d0bf18d11c47484ffcc2ab0a8ea56203a7076. Three4-slide/caption/alt drafts exist;source ledger empty,named reviewer/account null,WITHHELD,publication blocked,no schedule.','SHA verification proves preservation only. Windows checkout CRLF hashes differ;exact Git blobs match. Historical Instagram-only contract superseded by current X-first direction.'),
 evidence('GURU-E03','Official X documentation','observed2026-09-12','https://docs.x.com/x-api/posts/manage-tweets/introduction ; https://help.x.com/en/rules-and-policies/x-automation',['live_observed'],'Official manage-post route exists for authenticated users;current self-serve replies require summon via mention/quote. AI-powered automated reply bots require prior written explicit X approval;opt-in/opt-out and duplication constraints apply.','No Guru entitlement/account or paid allowance verified. Reply drafting remains useful while automated replies are gated. No platform automation invoked.'),
 evidence('GURU-E04','pri8771/astra-bot-launch',BASE,'focus/kai-pri-lipi/OWNER_DIRECTION.md; reference/ACCOUNTS_CHANNELS_AND_HOSTS.md; tasks/guru/queue.json',['cloud_backed','historical'],'Versioned owner directions,account isolation,outboxes and independent Windows/R730 migration are proposed contracts;4 old Guru tasks do not fully decompose autonomy.','Saved records do not prove runtime consumes directions,account capabilities or active writer acknowledgement.'),
 evidence('GURU-E05','Atlassian read-only snapshot',None,'planning/autonomy-complete/evidence/JIRA_MISSION_SEARCH.json',['live_observed','local_only'],'Root observed BOTS-61/128/129/130/132/133 and their existing summaries/status/estimates;129 In Review,others To Do at snapshot.','Metadata is not current acceptance or a source-bound task association;all new task keys remain null pending Windows parent reconciliation.', '2026-09-12T21:13:19.287Z')]
for m,rows in [('lipi',le),('guru',ge)]:
 folder=ROOT/'missions'/m;dump(folder/'evidence.json',rows)
 body=['# Evidence and limits','',f'Planning evidence captured at {NOW}. No current commerce/social effect was executed.','']
 for r in rows: body += ['## '+r['id'],'', '- Repository/ref: '+r['repository']+' / '+str(r['ref']),'- Path/source: '+r['path'],'- Observed: '+r['observed_at'],'- Classification: '+', '.join(r['classification']), '',r['finding'],'', 'Proof limits: '+r['proof_limits'],'']
 (folder/'EVIDENCE.md').write_text('\n'.join(body),encoding='utf-8')

# Preserve native metadata exactly as observed; candidates never become bindings.
jira_root=ROOT/'evidence'
snapshots=[json.loads((jira_root/f).read_text(encoding='utf-8-sig')) for f in ['JIRA_READBACK.json','JIRA_MISSION_SEARCH.json']]
for m in tasks:
 ids=set(c for t in tasks[m] for c in t['jira']['candidates'])
 found={i['key']:i for s in snapshots for i in s.get('issues',[]) if i['key'] in ids}
 dump(ROOT/'missions'/m/'jira-candidate-metadata.json',{'observed_at':[s['observed_at'] for s in snapshots],'bindings':'all null pending designated writer','issues':list(found.values())})
 out=['# Jira reconciliation proposal','', 'Planner performs no Jira writes. Current metadata is evidence for matching only. Existing original estimates,remaining estimates,actuals and historical acceptance are preserved; absent actual time is unknown,not zero. New engineering ranges are separate incremental planning estimates.','',
 ('Lipi writer identity/scope must be designated under LIPI-I09; do not silently route it to the four-mission parent.' if m=='lipi' else 'Guru projections belong to the Windows four-mission release parent. The unavailable historical Mac writer is not a prerequisite.'),'',
 'Old implementation-hold labels are observed metadata. Latest release authority controls authorized worker work; this planner neither edits labels nor pauses workers.','',
 '| Current candidate | Summary | Status | Original seconds | Actual seconds | Proposed task matching |','|---|---|---|---:|---|---|']
 for key,i in sorted(found.items(),key=lambda x:(x[0].split('-')[0],int(x[0].split('-')[-1]))):
  tt=i.get('timetracking',{}); matches=[t['id'] for t in tasks[m] if key in t['jira']['candidates']]
  out.append('| '+key+' | '+i['summary'].replace('|','/')+' | '+i['status']+' | '+str(tt.get('originalEstimateSeconds','unknown'))+' | '+str(tt.get('timeSpentSeconds','unknown'))+' | '+', '.join(matches)+' |')
 out += ['', 'Writer procedure: compare full current descriptions/acceptance with retained artifacts and task hash; reuse accepted implementation; bind only residual work; add linked new scope only when genuinely missing. Preserve estimates/worklogs and record rationale for any changed scope. Return actual key,current field/dependency readback,source/spec hash,operation ID and payload hash before admitting dependent implementation. Ambiguous writes reconcile by operation ID;outage queues immutable proposals.','']
 (ROOT/'missions'/m/'JIRA_RECONCILIATION.md').write_text('\n'.join(out),encoding='utf-8')

INPUTS={
 'lipi':[
 ('LIPI-I01','Exact missing retained37c447b contract/return artifacts and latest worker source admission','Existing Lipi execution coordinator/source owner','Supply only named session12h/session24h and Sept12 return hashes through existing Windows/private handoff;compare to clean main and session4. No old-Mac fetch.','LIPI-01','Use current31-check main and existing source/art as qualified within their scope.'),
 ('LIPI-I02','Final retained capsule membership,including Quiet Route retain/exclude','Business owner','One current signed/versioned decision bound to concrete membership,designs and sample/cost facts;reuse any valid existing exact decision.','LIPI-02;actual branch of LIPI-07','Model separate scenarios and qualify available product mappings.'),
 ('LIPI-I03','Current shop/provider identity,scoped access,variant mappings and observations','Lipi operator/business owner for required account verification','Read actual intended Shopify/Printful account and exact product/variant/cost/availability. Use owner Chrome when browser needed;do not copy sessions/secrets. New provider grants must be scoped.','LIPI-03–06;15–17','Build adapters,redacted fixtures,content and mapping comparison forms.'),
 ('LIPI-I04','Current fees,shipping,mixed-cart behavior,currency and economics inputs','Lipi operator;business owner for changed rules','Dated provider/account receipts with quote expiry and all-in calculations. Keep unknowns null and dated tax owner posture separate.','LIPI-07;12;20','Run assumed sensitivity/boundary fixtures labeled synthetic.'),
 ('LIPI-I05','Exact sample/charged-test purchase grant and current total','Business owner','Concrete provider IDs/variants/art hash/quantity,total including shipping/fees,currency,cap,expiry and delivery-reference. No standing sample budget.','LIPI-08;charged branch of12','Repair quote packet and continue storefront/runtime work.'),
 ('LIPI-I06','Delivered sample and attributable physical inspection','Receiving owner/physical reviewer','Actual order/tracking-delivery match,physical observations/photos and accepted/narrowed/rejected SKU decisions.','LIPI-09;final launch claims','Complete private content,policy,economics and recovery work.'),
 ('LIPI-I07','Remaining policy/consent/support route decisions and per-case remedies','Business owner;Lipi support operator prepares','Exact policy/version receipt,real support destination/consent flow,approved draft/send/refund or replacement for that case. Chargebacks remain owner-only.','LIPI-11;18','Draft accurate policy/case packets and validate privacy without sends.'),
 ('LIPI-I08','Exact current replacement launch/cutover decision','Business owner after independent reviewer','One complete candidate with source/artifact/policy/economics/sample/checkout hashes,shop/public domain,preimage,scope and rollback.','LIPI-13–14','Rehearse private restore and fix candidate.'),
 ('LIPI-I09','Designated Lipi Jira writer identity and scope','Owner/designated execution coordinator','Explicit Lipi writer role and native issue/source/spec readback;never implicitly assign to four-bot parent or unavailable old Mac writer.','LIPI-01;21;new implementation admissions andprice logging','Complete immutable matching/delta proposals and preserve current estimates.'),
 ('LIPI-I10','Admitted Windows runtime/storage/secret references,finite model/tool limits and owner alert route','Lipi runtime operator and existing account/budget owner','Current host independent execution,source/claim receipt,private storage permissions,backup proof,allowed caps and destination acknowledgement.','LIPI-15–16;20–23','Package fixtures and default-denied caps;durable file alerts.'),
 ('LIPI-I11','Current organic account,content/cadence grant and supported route','Lipi marketing operator/business owner','Exact intended handle/account,post/media/landing hashes,granted cadence,consent for lifecycle and receiving-system publication/analytics receipt. Paid ads disabled.','LIPI-19','Prepare source-grounded product assets and voluntary discovery questions.'),
 ('LIPI-I12','Specific India supplier/product/US-route evidence and any contact/pilot authority','Business owner;qualified supplier/reviewer;legal/import professional when needed','Dated primary identity/product/quality/capacity/landed-cost/delivery/return facts;exact supplier outreach/purchase grant and owner/professional legal declarations only if needed.','LIPI-24','Research publicly available primary evidence and compare scenarios with unknowns explicit.')],
 'guru':[
 ('GURU-I01','Canonical Guru repository/root/base and current parent return','Windows four-mission parent','Reuse actual returned home;if absent record exact minimal reuse/new-home decision,source hash and disjoint path ownership before writes.','GURU-01','Research editorial/source requirements in planning without claiming runtime exists.'),
 ('GURU-I02','Exact current public brand/persona decisions beyond X-first mission','Guru editorial owner/business owner','Reuse existing grants;bind actual brand identity and non-fictitious independent editorial description. X-first owner direction already established.','GURU-02','Prepare original source-based content concepts.'),
 ('GURU-I03','Real source editions/passages and rights for specific claims','Editorial researcher/rights owner','Inspectable primary/contextual source,edition/translation,url/access date and rights basis;unsupported claims remain withheld.','GURU-03–04','Draft secular structure and research source gaps without fabricated quotes.'),
 ('GURU-I04','Named cultural reviewer and actual exact-source independent review route','Editorial review coordinator;reviewers themselves','Reviewer identity/scope plus exact source/content/hash-bound approve/revise/withhold receipt;no inferred cultural expertise or self-review-as-independent.','GURU-05;15','Prepare review packet and alternative candidates.'),
 ('GURU-I05','Current exact Guru account ID/handle/admin/recovery ownership','Windows parent/account operator','Read existing registry and actual authenticated account;reuse routine account-organization authority;name any platform verification step.','GURU-06','Build isolated adapter with secret references and test fixtures.'),
 ('GURU-I06','Supported X publishing/analytics entitlement,exact content scope and finite existing budget','Guru account operator/business owner','Current account/scope/user-context receipt,permitted API operations/quota,and exact current publication/cadence grant. No paid purchase implied.','GURU-06;08;10;15;17','Prepare source-reviewed content and native release manifest.'),
 ('GURU-I07','Operation-specific moderation/correction grant and optional automated-reply qualification','Guru operator/business owner;X for AI reply permission','For original post corrections/deletion,exact applicable grant/readback. For AI automated replies additionally prior written explicit X approval,current recipient opt-in/summoning,opt-out and one-response rules.','Effect branch of GURU-09 only','Draft response/correction and continue qualified original posts;reply permission not required for their acceptance.'),
 ('GURU-I08','Current owner-direction/alert route and independent Windows operating envelope','Windows parent/runtime operator','Actual owner issuer/revision acknowledgement,host/storage/secret references,finite caps,one consumer and restore receipt;no Mac dependence.','GURU-12–15','File-backed direction/question/incident fixtures and package review.'),
 ('GURU-I09','Evidence and exact scope for optional additional channel/format','Guru experiment owner/business owner','Evaluated audience demand,bounded hypothesis,new account/capability/rights/budget and baseline if expanding;otherwise explicit no-go.','GURU-16','Continue existing X-first source/content experiments.')]
}
for m,items in INPUTS.items():
 folder=ROOT/'missions'/m
 rows=[dict(id=i,mission='LIPI' if m=='lipi' else 'GURU',required_input=need,respondent=owner,
  verification=verify,resume_action=resume,independent_work=independent,status='unresolved_or_requires_current_receipt') for i,need,owner,verify,resume,independent in items]
 dump(folder/'inputs.json',rows)
 out=['# Exact unresolved inputs and effect gates','',
 'These are future execution prerequisites,not permission requests sent by this planner. Reuse valid existing specific grants;do not ask for generic authority again. Persist one question per input/revision and resume only after validated receipt. Silence is not approval. Missing inputs block only their dependent effect.','',
 '| Input | Exact item | Respondent | Verification and resume | Useful independent work |','|---|---|---|---|---|']
 out += ['| '+r['id']+' | '+r['required_input']+' | '+r['respondent']+' | '+r['verification']+' Resume: '+r['resume_action']+' | '+r['independent_work']+' |' for r in rows]
 out += ['', '## Gate applicability','',
 'The effect_gates array on each task is the union of possible action classes. Apply only the gates whose condition matches the actual action. It is not an all-grants conjunction. Price-only or original-post operation does not need unrelated purchase/refund/discount/reply grants. Disabled classes remain blocked and unclaimed.','',
 'Every applicable receipt includes mission/action/resource,authority source and revision,payload/source/review hashes,expected-before state,allowed amount/currency/cap when relevant,expiry,issuer,verifier,verified time,secret reference and exact resume target. Never place credentials,addresses,payment details or raw customer messages here.','',
 '| Gate | Exact effect/authority | Resume/verification |','|---|---|---|']
 gate_rows=[]
 for gate,condition in GATE_SCOPES.items():
  if not gate.startswith('LIPI' if m=='lipi' else 'GURU'):continue
  ids=[t['id'] for t in tasks[m] if gate in t['effect_gates']]
  gate_rows.append({'id':gate,'mission':'LIPI' if m=='lipi' else 'GURU','condition':condition,'task_ids':ids,'status':'requires_applicable_current_receipt'})
  out += ['| '+gate+' | '+condition+' | '+', '.join(ids)+';require actual destination readback after authorized effect. |']
 out += ['', 'A source/read/proposal test cannot satisfy mutation/publication capability. A blocked/failure record completes only a preparation subunit;positive review,checks and real receipts are required to accept the claimed capability. Optional migration requires SH-16 only when transferring hosts. Windows useful release and operation do not depend on migration.','']
 dump(folder/'effect-gates.json',gate_rows)
 (folder/'UNRESOLVED_INPUTS.md').write_text('\n'.join(out),encoding='utf-8')

reconcile=['# Retained LIPI-63–87 acceptance reconciliation','',
 'Current-source qualification:main0d896016f2fa113ce07e504bc5d6528717598b5f executed31/31 aggregate checks,repository consistent,launch false,7 records and23 unknowns. The control structural check separately verifies11 readonly tools. These are repository checks,not25 task contracts or live commerce acceptance.','',
 'Retained result:focus/kai-pri-lipi/LIPI_EVIDENCE.md reports25 locally satisfied contracts and56 aggregate checks at37c447bbd90b8aac86f768a480b25eb4d8fc6c44. That exact ref is unavailable from current remote. No subtraction between31 and56 identifies missing features. Preserve retained acceptance and request only the exact named contract/return proof under LIPI-01 before source admission.','',
 'Cloud session4 branch52954f1f3d07f160a414713250923993a7d5f3f5 contains retained media,measurement,policy and synthetic restore contracts;these were inspected selectively,not all re-executed. It does not establish later session12h/session24h acceptance.','',
 '| Issue | Current fresh source evidence/reuse boundary | Retained external residual | Proposed task |','|---|---|---|---|']
remap={
 63:('AGENTS/MEMORY/STATE plus7-record current contract','Current shop/provider truth and exact retained source binding','LIPI-01'),
 64:('Existing Meridian template/record/media;current record fail-closed','Current4-color variant/sync/fulfillment readback','LIPI-03'),
 65:('Cloud session4 final_membership_decided=false','Exact owner capsule decision including Quiet Route','LIPI-02'),
 66:('Threshold12×16 production file and record with explicit unknowns','Exact supplier size/finish/cost/shipping configuration','LIPI-06'),
 67:('Existing Mantis M196 Denim Blue mapping anchor','Current tote identity and stale natural sample hint correction','LIPI-04'),
 68:('Existing Jerzees975MPR20-variant anchor','Conditional membership plus current exact variant qualification','LIPI-05'),
 69:('BUSINESS_RULES and standardized method;31-check baseline not all-in live inputs','Current costs/fees/discounts/reserve and worst-case20% calculation','LIPI-07'),
 70:('Retained sample packet is not on main;focus snapshot reports null totals','Exact total/variant/design purchase approval and receipt','LIPI-08'),
 71:('Historical US profile anchors and$99 conditional rule','Current mixed-cart rate and qualifying basket proof','LIPI-07'),
 72:('No actual delivered sample established by inspected source','Delivered physical inspection and accept/narrow receipt','LIPI-09'),
 73:('Existing private theme/cutover source and passing boundary verifiers','Current coordinated surfaces/candidate staging','LIPI-10'),
 74:('Existing production art/copy/media;session4 media contract','Exact sample-bound final content/media acceptance','LIPI-10'),
 75:('Existing private commerce runbook passes local contract','Actual variant/cart/payment/order/transactional route checks','LIPI-12'),
 76:('Source/private-theme semantic/responsive records','Current real NVDA/device/reduced-motion and purchase-flow QA','LIPI-10'),
 77:('Policy draft/source verifier and consent contracts','Exact owner policy/support/consent decisions and live route','LIPI-11'),
 78:('Retained owner-review local contract reported satisfied','Exact owner replacement-launch approval after current candidate review','LIPI-13'),
 79:('Main private rollback runbook;session4 synthetic snapshot','Exact current private restore and review receipt','LIPI-13'),
 80:('Aggregate analytics scorecard verifier;session4 data contract','Real baseline,consent-aware observations and attribution','LIPI-20'),
 81:('Existing organic asset/copy/UTM checks pass on main','Current approved products/claims/channel-ready exact assets','LIPI-19'),
 82:('Retained cutover local contract reported satisfied;publication false','Actual owner-approved catalog/shared-surface mutation/readback','LIPI-14'),
 83:('No current public replacement destination verified','Actual product/checkout/support public destination evidence','LIPI-14'),
 84:('Policy/customer source checks and support planning','Real consent/support/privacy cases with owner-gated send/remedy','LIPI-18'),
 85:('Existing organic candidate assets,not current social receipts','Actual authorized3-post readback or revised admitted scope','LIPI-19'),
 86:('No actual elapsed7-day commerce cycle established','Real order/fulfillment monitoring,exceptions,receipts and honest zero-order state','LIPI-17;LIPI-23'),
 87:('Retained cycle-close contract reported satisfied','Actual experiment evaluation,independent review and next finite decision','LIPI-20;LIPI-23')}
for k,(src,residual,nexttask) in remap.items():reconcile.append('| LIPI-'+str(k)+' | '+src+' | '+residual+' | '+nexttask+' |')
reconcile += ['', 'All25 current Jira rows were observed In Review,not Done. Metadata/old labels do not certify runtime or authorize this planning agent to change anything. Existing estimates and unknown actuals are retained in jira-candidate-metadata.json. No implementation reset is proposed. LIPI-01 may complete its matrix with precise unknowns;actual provider/purchase/release/operation tasks remain incomplete until positive acceptance receipts exist.','']
(ROOT/'missions/lipi/RETAINED_RECONCILIATION.md').write_text('\n'.join(reconcile),encoding='utf-8')

# Readable prose spacing without changing identifiers, URLs, code paths or raw
# provider/Jira evidence. Data keys and exact owned-path/source/ref fields stay fixed.
def prose(s):
 s=re.sub(r'([,;])(?=[A-Za-z0-9$])',r'\1 ',s)
 s=re.sub(r'\b(The|the|all|with|actual|current|retained|proposed|only|within|after|before|against|at|of|for|on|and|or|its|their|these|those|requires|require|passed|has)(?=[0-9$])',r'\1 ',s)
 s=re.sub(r'(?<=[A-Za-z])(?=20%|10%|31/31|25\s+local|56\s+aggregate)',r' ',s)
 s=re.sub(r'\b([0-9]+)(?=(?:checks|check|tools|tool|tasks|task|records|record|colors|color|variants|variant|attempts|repairs|repair)\b)',r'\1 ',s)
 s=re.sub(r'(?<=[,;])(?=\[)',r' ',s)
 return s
def clean(value,key=None):
 if key in {'id','mission','source_repo','repository','ref','path','owned_paths','evidence_refs','dependencies','task_ids','requirement_ids','next_check_at'}:return value
 if isinstance(value,str):return prose(value)
 if isinstance(value,list):return [clean(x) for x in value]
 if isinstance(value,dict):return {k:clean(v,k) for k,v in value.items()}
 return value
for m in tasks:
 folder=ROOT/'missions'/m
 for filename in ['TASKS.json','requirements.json','inputs.json','effect-gates.json','evidence.json']:
  path=folder/filename
  dump(path,clean(json.loads(path.read_text(encoding='utf-8'))))
 for path in folder.glob('*.md'):
  text_=path.read_text(encoding='utf-8')
  # Inline code spans are exact references and are kept byte-for-byte.
  spans=re.split(r'(`[^`]*`)',text_)
  path.write_text(''.join(x if x.startswith('`') else prose(x) for x in spans),encoding='utf-8')

print(json.dumps({'generated_at':NOW,'task_counts':{m:len(v) for m,v in tasks.items()},'requirement_counts':{m:len(write_requirements(m)) for m in tasks}},indent=2))
