# Artifact packets

Each file in this directory is a bounded execution/acceptance contract for one durable artifact.

Claude should implement the artifact, not merely "complete the task."

Packet contents:
- stable Artifact ID;
- target milestone;
- story points;
- dependencies;
- owned/expected paths;
- required behavior;
- acceptance tests;
- evidence required on return;
- authority/non-goals;
- expected return status.

Artifact status is canonical in ../ARTIFACT_INDEX.json.

Claude may submit an artifact as SUBMITTED. ChatGPT lead determines ACCEPTED / CHANGES_REQUIRED / BLOCKED / WITHHELD.
