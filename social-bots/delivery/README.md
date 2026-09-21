# Social Bots delivery package — imported and reconciled by LEAD-047

**Start at FINAL_RUN.md.** ChatGPT is lead; Fable is the released implementation/integration worker. This is the repo-native adoption of the supplied `social_bots_delivery_plan.patch`, not a request to download/apply it again.

The supplied 31 closure cards, 27 version exit records, 10 reconciliation records and offline validator/test code are retained. Duplicated prose is consolidated with the already-committed `../next-round/` contracts. The imported JSON is reformatted; this is a reviewed semantic import, not a byte-for-byte recreation of the patch. See IMPORT.md for provenance.

Use only one execution queue: TASKS.json plus the existing SB-* artifact packets, interpreted by FINAL_RUN.md and ACTIVE_EXECUTION.json. The older NR-* queue is supporting audit/reference material, not a second queue to implement. These closure tasks integrate and verify existing capabilities; they do not replace the feature work required by the milestone manifest.

Read only the active card (`python3 social-bots/delivery/validate_delivery.py --card C04`) and its contract. Contracts in `../next-round/` remain available for details; do not reload the entire roadmap at every checkpoint.

Build-ready, engineering-verified and operationally accepted remain separate. No product version is promoted by this package. Proposed test profiles in GATES.json are not authorizations. Existing account/alias setup scope is not a public/model/spending grant. No additional live product-model calls are authorized by LEAD-047.

Validation:
```
python3 social-bots/delivery/validate_delivery.py
python3 -m unittest discover -s social-bots/delivery/tests -v
python3 social-bots/delivery/validate_delivery.py --repo .
```
The last command checks the actual checkout and must be run by the integrator. Our local package validation was not a complete runtime or repository audit. See VALIDATION.json and reviews/LEAD047_PROBES.json.
