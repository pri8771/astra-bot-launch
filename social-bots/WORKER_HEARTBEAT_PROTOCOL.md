# Worker heartbeat protocol

This document is superseded by:

`HEARTBEAT_ASSIGNMENT_PROTOCOL.md`

Current active policy:
- worker bootstrap cadence: 15 minutes;
- require 3 consecutive worker heartbeat records;
- ChatGPT lead reviews/acknowledges them on the platform-supported hourly lead automation;
- worker remains at 15-minute cadence until LEAD_ACK.json authorizes hourly;
- steady cadence after acknowledgement: hourly;
- submissions/blockers push immediately;
- lead updates SESSION_INSTRUCTIONS.md and LEAD_ACK.json to keep work continuously assigned;
- meaningful updates trigger parent-thread notification from the hourly lead review.

Do not use the older state-transition-only cadence rules.
