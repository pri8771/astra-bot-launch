"""LEAD-063: every worker unit fails closed on unsafe reconciliation."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime import decision, leasing, paths, worker
from runtime.heartbeat import read_heartbeat
from runtime.jsonstore import append_jsonl


class ReconciliationGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.home = tempfile.TemporaryDirectory()
        self.addCleanup(self.home.cleanup)
        self.env = patch.dict(os.environ, {"SBOTS_HOME": self.home.name})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.bot = "social-a"
        self.task = worker.runtime_task_id(self.bot)

    def _seed_unsafe_queue(self) -> Path:
        queue = paths.content_dir(self.bot) / "publish_queue.jsonl"
        append_jsonl(
            queue,
            {
                "content_id": "historical-violation",
                "persona": self.bot,
                "bot": self.bot,
                "published": True,
                "publish_authorized": False,
            },
        )
        return queue

    def _failure_detail(self) -> dict:
        failures = sorted(paths.receipts_dir(self.bot).glob("*failure*.json"))
        self.assertEqual(len(failures), 1)
        return json.loads(failures[0].read_text())["detail"]

    @staticmethod
    def _cycle_record() -> dict:
        return {
            "cycle": 1,
            "chosen": {"action": "NO_ACTION"},
            "policy": {},
            "outcome": "no_action",
            "verify": {"verified": True, "withheld": False},
        }

    def _assert_blocked(self, result: dict, run_cycle) -> None:
        self.assertEqual(result["outcome"], "blocked_reconciliation_unsafe")
        self.assertFalse(result["verified"])
        self.assertFalse(result["committed"])
        self.assertTrue(result["lease_released"])
        self.assertNotIn("finish_receipt", result)
        run_cycle.assert_not_called()
        detail = self._failure_detail()
        self.assertEqual(detail["outcome"], "blocked_reconciliation_unsafe")
        self.assertFalse(detail["candidate_succeeded"])
        self.assertFalse(detail["cycle_committed"])
        self.assertFalse(detail["verified"])
        self.assertEqual(
            detail["reconciled"],
            {"queue_items": 1, "unauthorized_published": 1, "safe": False},
        )
        heartbeat = read_heartbeat(result["worker_id"])
        self.assertIn(heartbeat["status"], {"blocked", "failed"})

    def test_unsafe_stale_then_fresh_remain_blocked_without_product_mutation(self) -> None:
        queue = self._seed_unsafe_queue()
        before = queue.read_bytes()
        stale = leasing.acquire(self.task, "dead-worker", ttl_seconds=0)

        with patch.object(decision, "run_cycle", return_value=self._cycle_record()) as run_cycle:
            first = worker.run_one_unit(self.task, self.bot, self.bot, worker_id="takeover")
        self.assertEqual(first["took_over_from"], stale.lease_id)
        self._assert_blocked(first, run_cycle)
        self.assertEqual(queue.read_bytes(), before)

        # Receipt files are lifecycle evidence, while product-owned stores remain
        # absent and the unresolved queue evidence stays byte-for-byte unchanged.
        for product_dir in ("state", "memory", "experiments", "analytics"):
            self.assertFalse((Path(self.home.name) / product_dir / self.bot).exists())

        # A deleted old lease and fresh generation cannot clear the violation.
        with patch.object(decision, "run_cycle", return_value=self._cycle_record()) as run_cycle:
            second = worker.run_one_unit(self.task, self.bot, self.bot, worker_id="fresh")
        self.assertIsNone(second["took_over_from"])
        self.assertEqual(second["outcome"], "blocked_reconciliation_unsafe")
        self.assertFalse(second["verified"])
        self.assertFalse(second["committed"])
        run_cycle.assert_not_called()
        self.assertEqual(queue.read_bytes(), before)
        self.assertIsNone(leasing.inspect(self.task))

    def test_only_literal_true_is_safe_and_safe_unit_proceeds(self) -> None:
        record = self._cycle_record()
        unsafe_values = [False, None, 1, "true", [], {}]
        for index, safe in enumerate(unsafe_values):
            with self.subTest(safe=safe), \
                    patch.object(worker, "_reconcile", return_value={
                        "queue_items": 1, "unauthorized_published": 1, "safe": safe,
                    }), patch.object(decision, "run_cycle", return_value=record) as run_cycle:
                result = worker.run_one_unit(
                    self.task, self.bot, self.bot, worker_id=f"unsafe-{index}"
                )
                self.assertEqual(result["outcome"], "blocked_reconciliation_unsafe")
                run_cycle.assert_not_called()

        with patch.object(worker, "_reconcile", return_value={
            "queue_items": 0, "unauthorized_published": 0, "safe": True,
        }), patch.object(decision, "run_cycle", return_value=record) as run_cycle:
            result = worker.run_one_unit(self.task, self.bot, self.bot, worker_id="safe")
        run_cycle.assert_called_once()
        self.assertEqual(result["outcome"], "no_action")
        self.assertTrue(result["verified"])
        self.assertTrue(result["lease_released"])
        self.assertIn("finish_receipt", result)

    def test_unsafe_release_does_not_delete_takeover_workers_lease(self) -> None:
        self._seed_unsafe_queue()
        original_write = worker.receipts.write_receipt
        replacement = {}

        def write_then_take_over(namespace, kind, task_id, worker_id, lease_id, detail):
            receipt = original_write(namespace, kind, task_id, worker_id, lease_id, detail)
            if kind == "failure" and "lease" not in replacement:
                lease_path = paths.leases_dir() / f"{task_id}.lease.json"
                current = json.loads(lease_path.read_text())
                current["renewed_at"] = "1970-01-01T00:00:00+00:00"
                lease_path.write_text(json.dumps(current))
                replacement["lease"] = leasing.acquire(task_id, "new-owner", ttl_seconds=300)
            return receipt

        with patch.object(worker.receipts, "write_receipt", side_effect=write_then_take_over), \
                patch.object(
                    decision, "run_cycle", return_value=self._cycle_record()
                ) as run_cycle:
            result = worker.run_one_unit(
                self.task, self.bot, self.bot, worker_id="old-owner", ttl_seconds=300
            )

        run_cycle.assert_not_called()
        self.assertEqual(result["outcome"], "blocked_reconciliation_unsafe")
        self.assertFalse(result["lease_released"])
        current = leasing.inspect(self.task)
        self.assertEqual(current["lease_id"], replacement["lease"].lease_id)
        self.assertEqual(current["worker_id"], "new-owner")


if __name__ == "__main__":
    unittest.main()
