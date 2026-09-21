# Account / browser map (SB-005)

**Compiled:** 2026-09-20 by Claude Code. **Metadata only — no secrets.**
Follows `ACCOUNT_AND_BROWSER_SETUP.md`. Every "verified access" below is **none —
not verified from this session** because this cloud session has no credential
facility and performs no login. This is an inventory + exact-next-step map, not a
claim of live accounts. Reuse existing owner accounts before creating any new one.

## Runtime → persona → platform assignment

| Runtime | Primary persona | Cultural workspace (gated) | Primary platforms |
|---|---|---|---|
| social-a | The Ledger (general) | Sadhana Notes (cultural) | X, Reddit |
| social-b | Tidepool (general) | Utsava Calendar (cultural) | Instagram, TikTok |
| social-c | Switchboard (general) | — | TikTok, X |

Public persona profiles are separate from runtime identity. A runtime hosts a
cultural workspace but does not auto-publish it (publication gated).

## Platform capability + setup map

Legend for **Automation route**: reflects platform policy, not a live grant.

| Platform | Supported publish route | Reply/DM | Analytics | Automation route (policy) | Exact human gate before any use |
|---|---|---|---|---|---|
| Reddit | Official Reddit API (script/OAuth app) | Yes (API) | Per-post + account API | API allowed within rate limits & content policy | Owner creates/authorizes an OAuth app on an existing account; approve subreddit rules; no automation of voting. |
| X | X API v2 (tier-dependent) or manual | Limited by tier | API + native analytics | API allowed; write access is paid-tier gated | Owner confirms which existing X account + API tier; if free tier, publishing is manual-assisted. **Cost gate — no new spend authorized.** |
| Instagram | Instagram Graph API (Business/Creator + linked FB Page) | Comments via API; DMs restricted | Graph API insights | API allowed only for Business/Creator via a FB Page + Meta app review | Owner links an existing IG Business/Creator account to a FB Page and a Meta app; complete Meta app review/permissions. |
| TikTok | TikTok Content Posting API (approved dev app) | Limited | Display/analytics API | API allowed for approved apps; otherwise manual | Owner registers/authorizes a TikTok developer app on an existing account; await content-posting approval. |
| Facebook | Facebook Graph API (Page) | Comments via API | Page insights | API allowed for a Page + reviewed app | Owner selects an existing FB Page + Meta app; complete permissions review. |

## Per-account record template (populated only with real, safe metadata)

For each real account, maintain one registry entry (never in Git as secrets):

```
platform:            <e.g. reddit>
account_alias:       <handle or owner-chosen alias, not a private identity>
persona_mapping:     <persona id(s)>
login_method:        <e.g. owner SSO / password+TOTP — method only>
intended_workspace:  <profile/page/subreddit>
automation_route:    <api-app | browser-assisted | manual>
publish_capability:  <yes/no + tier>
reply_capability:    <yes/no>
analytics_capability:<yes/no + route>
last_verified:       none — not verified from this session
current_blocker:     <exact gate below>
credential_ref:      <keychain/1Password item alias — NEVER the secret>
```

## Browser-first setup procedure (per platform)

1. Automation opens the platform's developer/settings page for the **existing**
   owner account and advances to the exact configuration step.
2. It stops only at the exact human step: password / passkey / MFA / CAPTCHA /
   explicit provider consent (e.g. Meta app-review submission).
3. It records: exact destination reached, exact account/profile being configured,
   exact action needed — then resumes from that destination after the owner acts
   (no restart of the whole flow).

## Standing blockers (exact human steps, deduplicated)

1. **No credential facility in this session** → owner runs the recurring worker on
   an authorized host that injects narrowly-scoped credentials locally.
2. **Account confirmation** → owner names which existing accounts/handles/Pages map
   to each persona (reuse before create).
3. **API app authorization** per platform (Reddit OAuth app; Meta app + review for
   IG/FB; TikTok dev app; X API tier). **X write tier is a cost gate — not
   authorized.**
4. **Public-posting authorization** → not granted; see `LAUNCH_GATE_PACKET.md`.
5. **Named cultural reviewer** → required before either cultural persona posts.

No account was created, no login was performed, and no secret was recorded.
