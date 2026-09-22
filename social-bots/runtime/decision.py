"""Autonomous decision loop: OBSERVE -> ORIENT -> GENERATE -> SCORE -> CHOOSE
-> EXECUTE -> VERIFY -> LEARN -> SCHEDULE.

Design commitments (AUTONOMY_CONTRACT.md):
- NO_ACTION is a valid decision. A heartbeat firing is not a reason to act.
- The deterministic no-change path produces NO_ACTION WITHOUT any model call.
- Every non-trivial decision writes a decision record with the alternatives
  considered and why the chosen one won.
- EXECUTE performs only effects within the given ``Authority``. Public posting is
  never in local authority here; it stays a queued, unauthorized item.
- LEARN persists an evidence-tied hypothesis update, not a model's "I learned X".
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

from . import paths, research, pipeline, analytics, reasoning, model_dispatch
from . import account_routes, audience, experiment_engine, metrics, platform_selection
from . import content_intelligence as ci
from .reasoning import Candidate, no_action as _no_action, ReasoningContext
from .state import RuntimeState, PersonaState
from .personas import load as load_persona
from .jsonstore import append_jsonl, write_json, now_iso


@dataclass
class Authority:
    can_create_candidate: bool = True
    can_register_experiment: bool = True
    can_update_state: bool = True
    can_public_post: bool = False      # never granted by the loop itself
    can_spend: bool = False
    can_message_users: bool = False


ACTIONS = ("NO_ACTION", "RESEARCH_MORE", "CREATE_CANDIDATE", "CONTINUE_EXPERIMENT")


def run_cycle(bot: str, persona_id: str, authority: Authority | None = None,
              fence=None, require_adaptive: bool | None = None) -> dict:
    """Run one bounded autonomy cycle for ``bot`` acting as ``persona_id``.

    Returns the persisted decision record.

    ``require_adaptive`` sets the V0.4 reasoning posture for this cycle: None
    (default) follows the env-driven ``reasoning.adaptive_required()``; True
    forces the adaptive-required posture so a non-adaptive provider fails closed
    (the production worker passes True). Baseline/contextual deterministic
    providers stay available for tests/diagnostics but cannot satisfy an
    adaptive-required cycle.

    ``fence`` (a ``leasing.Fence``) gates every durable worker-owned write of the
    cycle — shared runtime state, persona-private state, content, experiment
    registration, publish-queue entry, success analytics AND the decision
    log/last-decision records — behind a single ownership check: they are all
    written inside one ``leasing.Fence.fenced_commit`` under the per-task lock. If
    the lease expired and another worker took over mid-cycle, the commit is
    refused with ``leasing.FenceLost`` and NOTHING durable is written by this
    (obsolete) owner — including the decision log and last-decision file, which
    previously slipped out after the fenced region (SB-V03-004 repair). When
    ``fence`` is None (unit tests, dry runs) the same writes run unguarded.

    Guarantee scope: this is an OWNERSHIP guarantee, not a database transaction.
    The commit performs several independent single-file atomic writes; a crash
    *between* them can leave some written and others not. What is guaranteed is
    (a) each individual file write is crash-atomic (temp+fsync+rename), and
    (b) an obsolete fence owner commits none of them. Crash-time idempotent
    recovery across the multi-file set is deferred reliability work.
    """
    authority = authority or Authority()
    persona = load_persona(persona_id)
    if persona["runtime"] != bot:
        raise ValueError(f"persona {persona_id} runs on {persona['runtime']}, not {bot}")

    # Shared runtime state (counters/recovery/fingerprint) and this persona's
    # PRIVATE state (consumed ledger, hypotheses, working set). Consumption and
    # hypotheses are persona-scoped, so two personas on one runtime never
    # contaminate each other's learning or evidence consumption (SB-V03-005).
    rt = RuntimeState.load(bot)
    # Pass the shared runtime so a first-time legacy migration sets its marker on
    # the SAME instance this cycle commits (SB-V03-005 migration-consistency).
    ps = PersonaState.load(bot, persona_id, runtime=rt)
    rt.data["counters"]["cycles"] += 1
    record: dict = {
        "recorded_at": now_iso(),
        "bot": bot,
        "persona": persona_id,
        "cycle": rt.data["counters"]["cycles"],
        "fence": fence.token() if fence is not None else None,
    }

    # -- MEASURE / CLOSEOUT (V1.5 / D2): elapsed engine experiments of THIS
    # persona close honestly (INCONCLUSIVE without a measurement); their durable
    # writes join the cycle's fenced commit below, whatever path the cycle takes.
    closeout = _closeout_experiments(bot, persona_id)
    record["closeout"] = closeout["summary"]

    # -- OBSERVE: this persona's unconsumed evidence only ------------------
    # Consumption is tracked per-signal, per-PERSONA (not a whole-inbox
    # fingerprint, not runtime-wide): a signal arriving after an earlier cycle,
    # or a batch of signals, is never skipped, and the same shared signal remains
    # independently available to every other persona on the runtime. Exactly one
    # unconsumed signal is decided upon per cycle. Restart-safe via persona state.
    consumed = ps.consumed_ids()
    pending = research.unconsumed_signals(bot, consumed)
    all_count = len(research.load_signals(bot))
    record["observe"] = {
        "total_signals": all_count,
        "consumed_count": len(consumed),
        "pending_count": len(pending),
        "changed": bool(pending),
        "observation_fingerprint": research.evidence_fingerprint(research.load_signals(bot)),
    }

    # -- Deterministic NO-CHANGE path: no model, no action -----------------
    if not pending:
        chosen = _no_action("no unconsumed evidence since last observation")
        record["orient"] = {"summary": "no new signals; nothing to reconsider",
                            "known": [], "inferred": [], "uncertain": [],
                            "objective": _current_objective(persona)}
        record["alternatives"] = [_summ(chosen)]
        record["chosen"] = _summ(chosen)
        record["chosen_reason"] = chosen.rationale
        record["required_authority"] = "none"
        record["execute"] = {"performed": False, "effect": "none", "outcome": "no_action"}
        record["verify"] = {"verified": True, "note": "no effect to verify"}
        record["learn"] = {"updated": False}
        record["outcome"] = "no_action"
        record["schedule"] = _schedule(persona, changed=False)
        rt.data["counters"]["no_action"] += 1
        rt.data["recovery"]["last_clean_tick"] = now_iso()
        _commit(fence, bot, rt, ps, record, closeout["effects"])
        return record

    # -- ORIENT ------------------------------------------------------------
    record["orient"] = {
        "summary": f"{len(pending)} unconsumed signal(s); deciding on the oldest this cycle",
        "known": [f"signal {s['id']} from {s['source']} ({s['provenance']})" for s in pending],
        "inferred": [f"topic tags: {sorted({t for s in pending for t in s.get('tags', [])})}"],
        "uncertain": ["external audience reaction (no post yet)"],
        "objective": _current_objective(persona),
    }

    # -- GENERATE (via reasoning provider; policy still decides eligibility) --
    top_signal = pending[0]
    draft = pipeline.ideate(persona, top_signal)
    dup = pipeline.is_duplicate(bot, draft)
    provider = reasoning.resolve_provider(require_adaptive=require_adaptive)
    effective_require = (reasoning.adaptive_required() if require_adaptive is None
                         else bool(require_adaptive))
    # V1.4 / D2: this persona's OWN learned audience evidence reaches reasoning
    # (and the model prompt / context digest) — never another persona's.
    audience_summary = _audience_summary(bot, persona_id)
    record["orient"]["known"].append(
        f"audience (persona-scoped): {audience_summary['learned_count']} learned, "
        f"{audience_summary['unlearned_count']} unlearned hypothesis(es)")
    ctx = ReasoningContext(
        persona=persona, objective=_current_objective(persona), top_signal=top_signal,
        pending_count=len(pending), is_duplicate=dup, draft=draft,
        state_summary={"hypotheses": ps.hypothesis_count(),
                       "cycles": rt.data["counters"]["cycles"],
                       "audience": audience_summary})
    record["reasoning"] = {"provider": getattr(provider, "provider_id", "unknown"),
                           "adaptive": getattr(provider, "adaptive", False),
                           "adaptive_required": effective_require,
                           "available": provider.available(),
                           # SB-R07-041 / C04: what the shared pre-dispatch gate
                           # actually did for this cycle (class, slot, outcome),
                           # so LIVE_MODEL and offline evidence never blur.
                           "dispatch": None,
                           "live_model_call": False}

    # Resolve a proposal, then VALIDATE it before scoring/execution. Any of:
    # provider unavailable, no proposal, or a proposal that fails the schema
    # (unsupported action, out-of-bounds numbers, empty/inconsistent
    # alternatives, authority-smuggling payload) fails closed — never scored.
    block_reason = None
    proposal = None
    if not provider.available():
        block_reason = getattr(provider, "reason", None) or "no reasoning provider available"
    else:
        model_dispatch.clear_last()
        proposal = provider.propose(ctx)
        dispatched = model_dispatch.last_record()
        record["reasoning"]["dispatch"] = dispatched.as_dict() if dispatched else None
        record["reasoning"]["live_model_call"] = bool(
            dispatched is not None and dispatched.invoked
            and dispatched.dispatch_class == model_dispatch.LIVE_MODEL)
        if proposal is None:
            block_reason = getattr(provider, "reason", None) or \
                "provider returned no usable proposal"
        else:
            contract_errors = reasoning.validate_proposal(proposal, ctx)
            if contract_errors:
                proposal = None
                block_reason = "provider output failed schema validation: " + \
                    "; ".join(contract_errors)[:240]

    # -- Fail-closed: reasoning required but unavailable/invalid -> BLOCKED.
    if proposal is None:
        record["reasoning"]["uncertainties"] = [block_reason]
        record["orient"]["uncertain"].append("reasoning unavailable/invalid")
        record["alternatives"] = []
        record["chosen"] = {"action": "BLOCKED_REASONING_UNAVAILABLE",
                            "rationale": block_reason}
        record["chosen_reason"] = ("reasoning required to interpret changed evidence but "
                                   f"failed closed: {block_reason}")
        record["required_authority"] = "none"
        record["execute"] = {"performed": False, "effect": "none",
                             "outcome": "blocked_reasoning_unavailable",
                             "block_reason": block_reason}
        record["verify"] = {"verified": True, "note": "no effect; blocked"}
        record["learn"] = {"updated": False}
        record["outcome"] = "blocked_reasoning_unavailable"
        record["schedule"] = _schedule(persona, changed=True)
        # Do NOT consume the signal: unreasoned evidence is not decided, so it
        # stays pending until a valid reasoning route is available.
        record["observe"]["consumed_this_cycle"] = None
        record["observe"]["pending_after"] = len(pending)
        _commit(fence, bot, rt, ps, record, closeout["effects"])
        return record

    # -- SCORE + CHOOSE (policy chooses among the provider's alternatives) ---
    record["reasoning"]["uncertainties"] = proposal.uncertainties
    scored = sorted(proposal.alternatives, key=lambda c: c.score(), reverse=True)
    chosen = scored[0]
    record["alternatives"] = [{**_summ(c), "score": c.score()} for c in scored]
    record["chosen"] = {**_summ(chosen), "score": chosen.score()}
    record["chosen_reason"] = (
        f"highest net score {chosen.score()} from {proposal.provider_id} "
        f"({'adaptive' if proposal.adaptive else 'baseline'}); "
        + ("duplicate suppressed" if dup and chosen.action != "CREATE_CANDIDATE"
           else "clears authority and reversibility bar")
    )

    # -- POLICY BOUNDARY (SB-V04-003) --------------------------------------
    # The policy selects strictly by its own deterministic ranking of the
    # validated alternatives. A provider's ``recommended_action`` is ADVISORY
    # ONLY: it never selects, and it can never override the ranked/allowed
    # alternatives. The record makes the proposal-vs-allowed distinction explicit;
    # authority/spend/messaging/review/dedup/platform/leases/scheduling/verify
    # remain owned by deterministic code downstream, not by the proposal.
    record["policy"] = {
        "provider_recommended": proposal.recommended_action,
        "policy_selected": chosen.action,
        "recommended_followed": proposal.recommended_action == chosen.action,
        "selection_basis": "deterministic policy ranking; recommended_action is advisory only",
        "authority_owned_by_policy": ["public_post", "spend", "messaging", "review_gate",
                                      "dedup", "platform_limit", "lease_fence",
                                      "scheduling", "effect_verification"],
    }

    # -- EXECUTE (local effects within authority only) ---------------------
    # ``_execute`` PREPARES the outcome and returns a ``effects`` closure holding
    # every durable side effect (experiment registration, publish-queue entry,
    # analytics, hypothesis/action/content records). Nothing durable is written
    # yet: run_cycle commits ``effects`` + the state save together under the
    # fence, so a fenced-out worker writes none of it.
    execute, verify, learn, effects = _execute(bot, persona, chosen, authority, rt, ps)
    record["required_authority"] = chosen.action
    record["execute"] = execute
    record["verify"] = verify
    record["learn"] = learn
    record["outcome"] = execute.get("outcome", "no_action")

    # -- SCHEDULE ----------------------------------------------------------
    record["schedule"] = _schedule(persona, changed=True)

    # CONSUME exactly the one signal we oriented on and decided about, so it is
    # never reconsidered and later/other pending signals are never lost. This is
    # an in-memory mutation; it is only persisted by the fenced commit below, so
    # a fenced-out worker never advances the consumed ledger either.
    ps.mark_consumed(top_signal["id"])
    record["observe"]["consumed_this_cycle"] = top_signal["id"]
    record["observe"]["pending_after"] = len(pending) - 1
    rt.data["observation_fingerprint"] = record["observe"]["observation_fingerprint"]
    rt.data["recovery"]["last_clean_tick"] = now_iso()
    _commit(fence, bot, rt, ps, record, _chain(closeout["effects"], effects))
    return record


def _current_objective(persona: dict) -> str:
    metrics = persona.get("success_metric_hierarchy", [])
    top = metrics[0] if metrics else "audience"
    return f"grow {top} for {persona['display_name']} via evidence-based experiments"


def _summ(c: Candidate) -> dict:
    return {"action": c.action, "rationale": c.rationale,
            "expected_value": c.expected_value, "expected_learning": c.expected_learning,
            "risk": c.risk, "reversibility": c.reversibility,
            "duplication_risk": c.duplication_risk}


def _schedule(persona: dict, changed: bool) -> dict:
    hours = 6 if changed else 24
    return {"next_check_in_hours": hours,
            "trigger": "deterministic timer + new-signal event",
            "note": "wait on events/timers, not constant polling"}


# --------------------------------------------------------------------------- #
# V1.7 D2 — the V1.2–V1.6 producers wired into the ordinary cycle
# --------------------------------------------------------------------------- #
def _chain(*effects):
    """Compose optional zero-arg effect closures into one (or None)."""
    fns = [f for f in effects if f is not None]
    if not fns:
        return None

    def run():
        for f in fns:
            f()
    return run


def _strategy_weights(persona: dict) -> dict:
    strat = persona.get("platform_strategy") or {}
    weights = {p: 0.5 for p in strat.get("secondary") or []}
    weights.update({p: 1.0 for p in strat.get("primary") or []})
    return weights


def _content_format(candidate: dict) -> str:
    """What the candidate can actually carry. Text-only unless an asset exists."""
    if candidate.get("content_format"):
        return str(candidate["content_format"])
    if candidate.get("video_asset"):
        return "video"
    if candidate.get("image_asset"):
        return "image"
    return "text"


def _platform_history(bot: str, persona_id: str) -> dict:
    """Per-platform performance from REAL normalized observations of this persona.

    Only PRESENT derived rates count (V1.3: missing is never zero); a platform
    with no present measurement has no history entry and stays EXPLORATORY.
    """
    acc: dict[str, list] = {}
    for row in metrics.observations_for(bot):
        if row.get("persona") != persona_id:
            continue
        try:
            obs = metrics.NormalizedObservation(**row)
        except TypeError:
            continue
        rates = [d["value"] for d in metrics.derive_all(obs).values()
                 if d.get("availability") == metrics.PRESENT
                 and isinstance(d.get("value"), (int, float))]
        if not rates:
            continue
        acc.setdefault(obs.platform, []).append(sum(rates) / len(rates))
    return {p: {"performance": max(0.0, min(1.0, sum(v) / len(v))), "samples": len(v)}
            for p, v in acc.items()}


def _select_platform(bot: str, persona: dict, candidate: dict) -> dict:
    """V1.2 platform selection with a truthful NO_PLATFORM outcome.

    Availability comes only from the credential-free account route registry.
    With no registry the loop may still draft for the persona's primary platform
    in an explicitly EXPLORATORY, unverified mode (nothing is publishable); with
    a registry and no eligible platform the result is NO_PLATFORM.
    """
    weights = _strategy_weights(persona)
    platforms = list(weights)
    avail = account_routes.availability_for(bot, persona["id"], platforms)
    fmt = _content_format(candidate)
    sel = platform_selection.select_platforms(
        persona_strategy=weights, content_format=fmt,
        availability=avail["availability"], history=_platform_history(bot, persona["id"]))
    out = {
        "content_format": fmt,
        "registry_present": avail["registry_present"],
        "registry_error": avail["registry_error"],
        "ranked": sel["ranked"], "selectable": sel["selectable"],
        "blocked": sel["blocked"], "unsuitable": sel["unsuitable"],
        "any_historical_basis": sel["any_historical_basis"],
    }
    if sel["selectable"]:
        platform = sel["selectable"][0]
        out.update(platform=platform, mode="registry_route",
                   route_id=avail["availability"][platform].get("route_id"),
                   publishable=bool(avail["availability"][platform].get("publishable")))
    elif not avail["registry_present"]:
        primary = (persona.get("platform_strategy") or {}).get("primary") or platforms[:1]
        out.update(platform=primary[0] if primary else None, mode="exploratory_unverified",
                   route_id=None, publishable=False,
                   note="no account route registry: drafting for the persona's primary "
                        "platform without any verified route; not publishable")
    else:
        out.update(platform=None, mode="no_platform", route_id=None, publishable=False)
    return out


def _audience_summary(bot: str, persona_id: str) -> dict:
    """V1.4: this persona's OWN audience hypotheses, learned ones first.

    Confidence is derived from decayed real observations (``audience.confidence``);
    unlearned hypotheses are counted, never given a number.
    """
    learned, unlearned = [], 0
    for hyp in audience.list_hypotheses(bot, persona_id):
        conf = audience.confidence(hyp)
        if conf["status"] == "learned":
            learned.append({"hypothesis_id": hyp.id, "statement": hyp.statement,
                            "segment": hyp.segment, "confidence": conf["confidence"],
                            "freshness_days": conf["freshness_days"],
                            "evidence_count": len(conf["evidence_refs"])})
        else:
            unlearned += 1
    learned.sort(key=lambda h: h["confidence"], reverse=True)
    return {"scope": {"bot": bot, "persona": persona_id}, "learned": learned[:3],
            "learned_count": len(learned), "unlearned_count": unlearned}


def _treatment_observation(bot: str, persona_id: str, exp) -> "metrics.NormalizedObservation | None":
    rows = [r for r in metrics.observations_for(bot)
            if r.get("persona") == persona_id and r.get("experiment_id") == exp.id
            and (r.get("window_end") or r.get("collected_at") or "") >= (exp.started_at or "")]
    if not rows:
        return None
    rows.sort(key=lambda r: r.get("window_end") or r.get("collected_at") or "")
    try:
        return metrics.NormalizedObservation(**rows[-1])
    except TypeError:
        return None


def _closeout_experiments(bot: str, persona_id: str) -> dict:
    """V1.5: close this persona's RUNNING engine experiments whose window elapsed.

    A treatment observation is read from the normalized metric store by
    experiment id; when none exists the outcome is INCONCLUSIVE (never success,
    never zero effect). Durable writes are returned as an effect closure so they
    run under the cycle's fence.
    """
    now = datetime.now(timezone.utc)
    closed, summary = [], []
    for row in experiment_engine.list_experiments(bot, persona_id):
        if row.get("status") != experiment_engine.RUNNING:
            continue
        try:
            exp = experiment_engine.Experiment(**row)
        except TypeError:
            continue
        if not experiment_engine.window_elapsed(exp, now=now):
            continue
        treatment = _treatment_observation(bot, persona_id, exp)
        if treatment is None:
            experiment_engine.close_without_observation(exp, now=now)
        else:
            experiment_engine.close(exp, treatment, now=now)
        ref = experiment_engine.to_learning_ref(exp)
        closed.append(exp)
        summary.append({"experiment_id": exp.id, "outcome": exp.outcome,
                        "reason": (exp.result or {}).get("reason"),
                        "treatment_observation_id": (exp.result or {}).get(
                            "treatment_observation_id"),
                        "learning_ref": ref})

    def effects():
        for exp in closed:
            experiment_engine.save_experiment(bot, persona_id, exp)

    return {"summary": summary, "effects": effects if closed else None}


def _execute(bot: str, persona: dict, chosen: Candidate, authority: Authority,
             rt: RuntimeState, ps: PersonaState):
    """Prepare the outcome and return ``(execute, verify, learn, effects)``.

    ``effects`` is a zero-arg closure holding EVERY durable side effect (shared
    action/content records, persona-private hypothesis updates, experiment
    registration, publish-queue entry, analytics). It is executed by
    ``run_cycle`` inside the fenced commit, never here — so a worker that has
    lost its fence performs none of these writes. ``effects`` is None when there
    is nothing durable beyond the base state saves.
    """
    if chosen.action == "NO_ACTION":
        return ({"performed": False, "effect": "none", "outcome": "no_action"},
                {"verified": True, "note": "no effect"},
                {"updated": False}, None)

    if chosen.action == "RESEARCH_MORE":
        return ({"performed": True, "effect": "flagged research need (local only)",
                 "outcome": "research_more"},
                {"verified": True, "note": "local flag written"},
                {"updated": False}, None)

    if chosen.action == "CREATE_CANDIDATE":
        if not authority.can_create_candidate:
            return ({"performed": False, "effect": "blocked: no authority",
                     "outcome": "blocked_authority"},
                    {"verified": True, "note": "authority gate held"},
                    {"updated": False}, None)
        signal = chosen.payload["signal"]
        draft = pipeline.ideate(persona, signal)
        if pipeline.is_duplicate(bot, draft):
            return ({"performed": False, "effect": "suppressed duplicate",
                     "outcome": "duplicate_suppressed"},
                    {"verified": True, "note": "dedup gate held"},
                    {"updated": False}, None)
        reviewed = pipeline.review(persona, draft)

        # ---- PLATFORM SELECTION (V1.2 / D2): real routes decide ------------
        selection = _select_platform(bot, persona, reviewed)
        if selection["platform"] is None:
            def no_platform_effects():
                rt.record_action({"action": "CREATE_CANDIDATE_NO_PLATFORM",
                                  "persona": persona["id"],
                                  "content_id": reviewed["content_id"],
                                  "blocked": selection["blocked"],
                                  "unsuitable": selection["unsuitable"],
                                  "registry_error": selection["registry_error"]})
                analytics.emit(analytics.make_event(
                    bot, persona["id"], "correction", content_id=reviewed["content_id"],
                    metrics={"no_platform": 1}))
            execute = {"performed": False, "outcome": "no_platform",
                       "effect": "NO_PLATFORM: no available, authorized platform route can "
                                 "carry this content; no experiment, no queue entry",
                       "content_id": reviewed["content_id"],
                       "platform_selection": selection}
            verify = {"verified": True, "withheld": True,
                      "published": False, "publish_authorized": False,
                      "review_passed": reviewed["review_passed"],
                      "within_platform_limit": None,
                      "final_review_bound": False, "final_text_sha256": None,
                      "experiment_registered": False, "queued": False,
                      "platform_selection": selection,
                      "note": "no platform; candidate correctly did NOT proceed"}
            learn = {"updated": False, "note": "no platform; nothing registered"}
            return (execute, verify, learn, no_platform_effects)
        platform = selection["platform"]
        payload = pipeline.format_for_platform(reviewed, platform)
        # ---- FINAL-CONTENT REVIEW BINDING (V1.7 C05/C06) -------------------
        # Every check is re-run over the exact rendered text and bound to its
        # hash; enqueue refuses anything unbound or mismatched.
        final = pipeline.final_review(persona, reviewed, payload)
        # ---- LINEAGE + NOVELTY (V1.6 / D2): persona-scoped, never cross-persona
        variant = pipeline.variant_from_payload(payload)
        novelty = ci.check_novelty(bot, variant)

        # ---- REQUIRED-REVIEW GATE (deterministic publication gate) --------
        # A failed factual/voice/cultural review or a platform-limit failure
        # STOPS here: no experiment registration, no publish-queue entry, no
        # success result. Only a truthful WITHHELD/BLOCKED receipt is produced.
        gate_failures = []
        if not reviewed["review_passed"]:
            failed = [c for c in reviewed["review"].values() if not c["passed"]]
            gate_failures.append({"gate": "review", "checks": failed})
        if not payload["within_limit"]:
            gate_failures.append({"gate": "platform_limit",
                                  "platform": platform,
                                  "char_limit": payload["char_limit"]})
        if not final["passed"]:
            gate_failures.append({"gate": "final_review",
                                  "checks": [c for c in final["checks"].values()
                                             if not c["passed"]],
                                  "reasons": final["reasons"],
                                  "final_text_sha256": final["final_text_sha256"]})
        if not novelty.get("novel", True):
            gate_failures.append({"gate": "novelty", "novelty": novelty,
                                  "platform": platform})
        if gate_failures:
            def withheld_effects():
                rt.record_action({"action": "CREATE_CANDIDATE_WITHHELD",
                                  "persona": persona["id"],
                                  "content_id": reviewed["content_id"],
                                  "reasons": gate_failures})
                analytics.emit(analytics.make_event(
                    bot, persona["id"], "correction", platform=platform,
                    content_id=reviewed["content_id"],
                    metrics={"withheld": 1}))
            execute = {"performed": False,
                       "outcome": "withheld",
                       "effect": "withheld: failed required review/platform gate; "
                                 "no experiment, no queue entry",
                       "content_id": reviewed["content_id"],
                       "gate_failures": gate_failures}
            verify = {"verified": True, "withheld": True,
                      "published": False, "publish_authorized": False,
                      "review_passed": reviewed["review_passed"],
                      "within_platform_limit": payload["within_limit"],
                      "final_review_bound": final["passed"],
                      "final_text_sha256": final["final_text_sha256"],
                      "platform_selection": selection, "novelty": novelty,
                      "lineage": payload.get("lineage"),
                      "experiment_registered": False, "queued": False,
                      "note": "required gate failed; candidate correctly did NOT proceed"}
            learn = {"updated": False,
                     "note": "no hypothesis registered; a withheld candidate is not evidence of a launch"}
            return (execute, verify, learn, withheld_effects)

        # PROSPECTIVE registration (V1.7 C07): the metric is predeclared, the
        # baseline is explicitly NOT measured, and there is no outcome, decision
        # or confidence until real post-window evidence exists.
        metric = persona["success_metric_hierarchy"][0]
        exp = pipeline.Experiment(
            experiment_id=f"exp-{reviewed['content_id']}",
            bot=bot, persona=persona["id"], platform=platform,
            hypothesis=persona["audience_hypotheses"][0],
            baseline=pipeline.prospective_baseline(metric),
            intervention=f"publish 1 {reviewed['signature_move']} candidate on {platform}",
            success_metric=metric,
            stop_criteria="no lift above baseline noise within window; or policy flag",
            observation_window_hours=48,
        )
        hid = f"h-{persona['id']}-{exp.experiment_id}"

        def success_effects():
            # ALL durable success artifacts, committed under the fence in one
            # ownership-checked region (not a cross-file transaction).
            pipeline.register_experiment(exp)
            rt.record_content({"content_id": reviewed["content_id"],
                               "content_key": pipeline.content_key(reviewed),
                               "persona": persona["id"], "platform": platform,
                               "review_passed": reviewed["review_passed"],
                               "final_text_sha256": final["final_text_sha256"],
                               "concept_id": payload.get("concept_id"),
                               "lineage": payload.get("lineage")})
            ci.record_variant(bot, variant)          # persona-scoped lineage history
            pipeline.enqueue(bot, reviewed, payload, exp.experiment_id)
            analytics.emit(analytics.make_event(
                bot, persona["id"], "candidate_created", platform=platform,
                content_id=reviewed["content_id"], experiment_id=exp.experiment_id))
            analytics.emit(analytics.make_event(
                bot, persona["id"], "queued", platform=platform,
                content_id=reviewed["content_id"], experiment_id=exp.experiment_id,
                metrics={"publish_authorized": 0}))
            ps.upsert_hypothesis(
                hid=hid, statement=exp.hypothesis, confidence=None,
                evidence=[f"experiment {exp.experiment_id} registered PROSPECTIVE; "
                          f"awaiting {exp.observation_window_hours}h window after "
                          f"an actual publication"])
            rt.record_action({"action": "CREATE_CANDIDATE",
                              "persona": persona["id"],
                              "content_id": reviewed["content_id"],
                              "experiment_id": exp.experiment_id})

        # VERIFY: correct destination/persona, unpublished, review recorded.
        # Values are deterministic by construction (enqueue always sets
        # publish_authorized/published False and stamps this persona).
        verify = {
            "verified": True,
            "content_id": reviewed["content_id"],
            "persona_match": True,
            "publish_authorized": False,
            "published": False,
            "review_passed": reviewed["review_passed"],
            "within_platform_limit": payload["within_limit"],
            "final_review_bound": True,
            "final_text_sha256": final["final_text_sha256"],
            "platform_selection": selection, "novelty": novelty,
            "lineage": payload.get("lineage"),
            "note": "queued only; no external effect; publish_authorized must be False",
        }
        learn = {"updated": True,
                 "hypothesis_id": hid,
                 "confidence": None,
                 "status": pipeline.PROSPECTIVE,
                 "note": "prospective registration: no baseline measured, no outcome, "
                         "no confidence until real post-window evidence"}
        return ({"performed": True, "outcome": "candidate_created",
                 "effect": "candidate reviewed + experiment registered + queued (unpublished)",
                 "content_id": reviewed["content_id"], "experiment_id": exp.experiment_id},
                verify, learn, success_effects)

    # A validated but not-yet-executable vocabulary action (CONTINUE_EXPERIMENT or
    # CLOSE_EXPERIMENT — in the schema vocabulary but with NO effect executor yet)
    # produces NO effect. The policy never invents an effect for an action it
    # cannot safely perform, and we deliberately do not add future effect
    # executors just because an action is in the schema (SB-V04-001).
    # Unsupported/unknown actions never reach here: validate_proposal rejects them.
    return ({"performed": False, "outcome": "blocked_unsupported_action",
             "effect": f"no executor for action {chosen.action!r}; no effect performed"},
            {"verified": True, "note": "no effect; action not executable by policy"},
            {"updated": False}, None)


def _commit(fence, bot: str, rt: RuntimeState, ps: PersonaState, record: dict,
            effects=None) -> None:
    """Persist EVERY durable worker-owned write of the cycle behind one fence.

    All of it — shared runtime state, persona-private state, the experiment/
    queue/analytics/content/action side effects AND the decision log +
    last-decision records — runs inside a single ``leasing.Fence.fenced_commit``.
    On fence loss ``leasing.FenceLost`` propagates before any write runs, so an
    obsolete owner writes NOTHING, not even the decision log.

    SB-V03-004 repair: the decision-log/last-decision writes used to run AFTER
    the fenced region (outside the ownership lock). A worker that stalled past
    its lease could then resume and write those stale, later-cycle-owned durable
    records after another worker had already taken over. They are now part of the
    fenced closure, so a fenced-out worker can no longer emit them.

    This is an ownership gate, NOT a cross-file transaction: each file write is
    individually crash-atomic, but the multi-file set is not all-or-nothing on a
    crash. Without a fence (unit tests / dry runs) the same writes run unguarded.
    """
    def do_commit():
        if effects is not None:
            effects()
        rt.save()
        ps.save()
        # Durable, worker-owned cycle records — must be inside the fence so a
        # fenced-out owner cannot write them post-takeover (SB-V03-004).
        append_jsonl(paths.memory_dir(bot) / "decisions.jsonl", record)
        write_json(paths.state_dir(bot) / "last_decision.json", record)

    if fence is not None:
        fence.fenced_commit(do_commit)   # raises FenceLost -> caller stands down
    else:
        do_commit()
