import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, "/Users/pchordia/Downloads/swarm_codex/review/bots-composition-source/social-bots")
from runtime import leasing, paths, pipeline, worker
from runtime.jsonstore import append_jsonl

tmp = tempfile.mkdtemp(prefix="bots-lead062-")
os.environ["SBOTS_HOME"] = tmp
bot = "social-b"
task = worker.runtime_task_id(bot)

# Synthetic durable evidence of a reconciliation violation: published without authority.
append_jsonl(paths.content_dir(bot) / "publish_queue.jsonl", {
    "content_id": "synthetic-unsafe",
    "persona": "social-b",
    "published": True,
    "publish_authorized": False,
})

# Dead prior owner forces the production takeover/reconcile branch.
prior = leasing.acquire(task, "dead-owner", ttl_seconds=0)
called = {"decision": 0}

def fake_cycle(*args, **kwargs):
    called["decision"] += 1
    return {
        "cycle": 1,
        "chosen": {"action": "NO_ACTION"},
        "policy": {},
        "outcome": "no_action",
        "verify": {"verified": True, "withheld": False},
    }

with patch.object(worker.decision, "run_cycle", side_effect=fake_cycle):
    result = worker.run_one_unit(task, bot, "social-b", worker_id="takeover", ttl_seconds=300)

finish = sorted((Path(tmp) / "receipts" / bot).glob("*finish*.json"))[-1]
finish_detail = json.loads(finish.read_text())["detail"]
observed = {
    "source_head": "8c86898d1c6641adbf5c9884e1aa7ab2923b1af3",
    "prior_lease": prior.lease_id,
    "decision_called_after_unsafe_reconcile": called["decision"],
    "finish_reconciled": finish_detail["reconciled"],
    "worker_result": result,
    "temp_runtime": tmp,
}
assert finish_detail["reconciled"] == {
    "queue_items": 1, "unauthorized_published": 1, "safe": False
}
assert called["decision"] == 1
assert result["verified"] is True
print(json.dumps(observed, indent=2, sort_keys=True))
