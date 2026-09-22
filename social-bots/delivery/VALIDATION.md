# What was tested in LEAD-047

The owner-supplied patch applied cleanly to an isolated empty repository. Its read-only delivery validator reported 31 tasks, 27 milestone records and 10 reconciliation records, no errors/warnings; its 30 unit tests passed. These were planning-tool tests, not a full Social Bots checkout or operational tests.

Six isolated source-excerpt sentinel probes reproduced the failures listed in reviews/LEAD047_PROBES.json. Contract/authorization/ledger dependencies were test doubles, copied method bodies were the inspected originals. No real model, public effect or network call occurred. These are narrow reproduction evidence, not independent execution of the entire runtime suite.

The imported package normalizes JSON whitespace and consolidates duplicate docs into existing next-round references. Its validator/tests and card semantics are retained. Rerun both commands on the actual integrated checkout, then run --repo . to validate real artifact refs/status pointers. Historical tests of an empty fixture registry do not verify the actual repository.

Commands:
```
python3 social-bots/delivery/validate_delivery.py
python3 -m unittest discover -s social-bots/delivery/tests -v
python3 social-bots/delivery/validate_delivery.py --repo .
python3 social-bots/delivery/reviews/probes/run_probes.py
```
The last command reproduces historical defects and intentionally succeeds when they appear. It is not a current-runtime safety gate. Port its scenarios into regression tests importing the actual repaired modules before closing findings.
