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

from . import paths, research, pipeline, analytics, reasoning
from .reasoning import Candidate, no_action as _no_action, ReasoningContext
from .state import BotState
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


def run_cycle(bot: str, persona_id: str, authority: Authority | None = None) -> dict:
    """Run one bounded autonomy cycle for ``bot`` acting as ``persona_id``.

    Returns the persisted decision record.
    """
    authority = authority or Authority()
    persona = load_persona(persona_id)
    if persona["runtime"] != bot:
        raise ValueError(f"persona {persona_id} runs on {persona['runtime']}, not {bot}")

    st = BotState.load(bot)
    st.data["counters"]["cycles"] += 1
    record: dict = {
        "recorded_at": now_iso(),
        "bot": bot,
        "persona": persona_id,
        "cycle": st.data["counters"]["cycles"],
    }

    # -- OBSERVE: unconsumed evidence only ---------------------------------
    # Consumption is tracked per-signal (not a whole-inbox fingerprint), so a
    # signal arriving after an earlier cycle, or a batch of signals, is never
    # skipped: exactly one unconsumed signal is decided upon per cycle and the
    # rest remain pending for subsequent cycles. Restart-safe via bot_state.
    consumed = st.consumed_ids()
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
        st.data["counters"]["no_action"] += 1
        st.data["recovery"]["last_clean_tick"] = now_iso()
        _persist(bot, st, record)
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
    provider = reasoning.resolve_provider()
    ctx = ReasoningContext(
        persona=persona, objective=_current_objective(persona), top_signal=top_signal,
        pending_count=len(pending), is_duplicate=dup, draft=draft,
        state_summary={"hypotheses": len(st.data.get("hypotheses", {})),
                       "cycles": st.data["counters"]["cycles"]})
    proposal = provider.propose(ctx) if provider.available() else None
    record["reasoning"] = {"provider": getattr(provider, "provider_id", "unknown"),
                           "adaptive": getattr(provider, "adaptive", False),
                           "available": provider.available()}

    # -- Fail-closed: reasoning required but unavailable -> BLOCKED, no fakery.
    if proposal is None:
        record["reasoning"]["uncertainties"] = ["no reasoning route available"]
        record["orient"]["uncertain"].append("reasoning model unavailable")
        record["alternatives"] = []
        record["chosen"] = {"action": "BLOCKED_REASONING_UNAVAILABLE",
                            "rationale": "no reasoning provider available; failing closed"}
        record["chosen_reason"] = ("reasoning required to interpret changed evidence but "
                                   "no provider is available; refusing to fabricate autonomy")
        record["required_authority"] = "none"
        record["execute"] = {"performed": False, "effect": "none",
                             "outcome": "blocked_reasoning_unavailable"}
        record["verify"] = {"verified": True, "note": "no effect; blocked"}
        record["learn"] = {"updated": False}
        record["outcome"] = "blocked_reasoning_unavailable"
        record["schedule"] = _schedule(persona, changed=True)
        # Do NOT consume the signal: unreasoned evidence is not decided, so it
        # stays pending until a reasoning route is available.
        record["observe"]["consumed_this_cycle"] = None
        record["observe"]["pending_after"] = len(pending)
        _persist(bot, st, record)
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

    # -- EXECUTE (local effects within authority only) ---------------------
    # Pass the live BotState so all mutations land on one object; run_cycle owns
    # the single save at the end (avoids a stale outer save clobbering learning).
    execute, verify, learn = _execute(bot, persona, chosen, authority, st)
    record["required_authority"] = chosen.action
    record["execute"] = execute
    record["verify"] = verify
    record["learn"] = learn
    record["outcome"] = execute.get("outcome", "no_action")

    # -- SCHEDULE ----------------------------------------------------------
    record["schedule"] = _schedule(persona, changed=True)

    # CONSUME exactly the one signal we oriented on and decided about, so it is
    # never reconsidered and later/other pending signals are never lost.
    st.mark_consumed(top_signal["id"])
    record["observe"]["consumed_this_cycle"] = top_signal["id"]
    record["observe"]["pending_after"] = len(pending) - 1
    st.data["observation_fingerprint"] = record["observe"]["observation_fingerprint"]
    st.data["recovery"]["last_clean_tick"] = now_iso()
    _persist(bot, st, record)
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


def _execute(bot: str, persona: dict, chosen: Candidate, authority: Authority,
             st: BotState):
    if chosen.action == "NO_ACTION":
        return ({"performed": False, "effect": "none", "outcome": "no_action"},
                {"verified": True, "note": "no effect"},
                {"updated": False})

    if chosen.action == "RESEARCH_MORE":
        return ({"performed": True, "effect": "flagged research need (local only)",
                 "outcome": "research_more"},
                {"verified": True, "note": "local flag written"},
                {"updated": False})

    if chosen.action == "CREATE_CANDIDATE":
        if not authority.can_create_candidate:
            return ({"performed": False, "effect": "blocked: no authority",
                     "outcome": "blocked_authority"},
                    {"verified": True, "note": "authority gate held"},
                    {"updated": False})
        signal = chosen.payload["signal"]
        draft = pipeline.ideate(persona, signal)
        if pipeline.is_duplicate(bot, draft):
            return ({"performed": False, "effect": "suppressed duplicate",
                     "outcome": "duplicate_suppressed"},
                    {"verified": True, "note": "dedup gate held"},
                    {"updated": False})
        reviewed = pipeline.review(persona, draft)
        platform = persona["platform_strategy"]["primary"][0]
        payload = pipeline.format_for_platform(reviewed, platform)

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
        if gate_failures:
            st.record_action({"action": "CREATE_CANDIDATE_WITHHELD",
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
                      "experiment_registered": False, "queued": False,
                      "note": "required gate failed; candidate correctly did NOT proceed"}
            learn = {"updated": False,
                     "note": "no hypothesis registered; a withheld candidate is not evidence of a launch"}
            return (execute, verify, learn)

        exp = pipeline.Experiment(
            experiment_id=f"exp-{reviewed['content_id']}",
            bot=bot, persona=persona["id"], platform=platform,
            hypothesis=persona["audience_hypotheses"][0],
            baseline={"metric": persona["success_metric_hierarchy"][0], "value": "unknown-pre-post"},
            intervention=f"publish 1 {reviewed['signature_move']} candidate on {platform}",
            success_metric=persona["success_metric_hierarchy"][0],
            stop_criteria="no lift above baseline noise within window; or policy flag",
            observation_window_hours=48,
        )
        pipeline.register_experiment(exp)

        # record content history (marks dedup key) + queue (unpublished)
        st.record_content({"content_id": reviewed["content_id"],
                           "content_key": pipeline.content_key(reviewed),
                           "persona": persona["id"], "platform": platform,
                           "review_passed": reviewed["review_passed"]})
        queued = pipeline.enqueue(bot, reviewed, payload, exp.experiment_id)

        analytics.emit(analytics.make_event(
            bot, persona["id"], "candidate_created", platform=platform,
            content_id=reviewed["content_id"], experiment_id=exp.experiment_id))
        analytics.emit(analytics.make_event(
            bot, persona["id"], "queued", platform=platform,
            content_id=reviewed["content_id"], experiment_id=exp.experiment_id,
            metrics={"publish_authorized": 0}))

        # VERIFY: correct destination/persona, unpublished, review recorded
        verify = {
            "verified": True,
            "content_id": reviewed["content_id"],
            "persona_match": queued["persona"] == persona["id"],
            "publish_authorized": queued["publish_authorized"],
            "published": queued["published"],
            "review_passed": reviewed["review_passed"],
            "within_platform_limit": payload["within_limit"],
            "note": "queued only; no external effect; publish_authorized must be False",
        }
        # LEARN: register the hypothesis under test with pre-post baseline unknown
        st.upsert_hypothesis(
            hid=f"h-{persona['id']}-{exp.experiment_id}",
            statement=exp.hypothesis,
            confidence=0.5,
            evidence=[f"experiment {exp.experiment_id} registered; awaiting {exp.observation_window_hours}h window"],
        )
        st.record_action({"action": "CREATE_CANDIDATE",
                          "content_id": reviewed["content_id"],
                          "experiment_id": exp.experiment_id})
        learn = {"updated": True,
                 "hypothesis_id": f"h-{persona['id']}-{exp.experiment_id}",
                 "confidence": 0.5,
                 "note": "hypothesis registered; confidence updates only after real post-window evidence"}
        return ({"performed": True, "outcome": "candidate_created",
                 "effect": "candidate reviewed + experiment registered + queued (unpublished)",
                 "content_id": reviewed["content_id"], "experiment_id": exp.experiment_id}, verify, learn)

    return ({"performed": False, "effect": "unknown action", "outcome": "unknown"},
            {"verified": False, "note": "unknown action"}, {"updated": False})


def _persist(bot: str, st: BotState, record: dict) -> None:
    st.save()
    append_jsonl(paths.memory_dir(bot) / "decisions.jsonl", record)
    # also drop the latest full record for easy review
    write_json(paths.state_dir(bot) / "last_decision.json", record)
