# Future artifact — Social platform route research

Artifact ID: SB-ACC-008
Owner: ChatGPT lead
Status: ACCEPTED as lead research/preparation artifact
Scope date: 2026-09-20
Purpose: reduce V0.8 implementation discovery and identify zero-additional-spend bootstrap routes. This is research, not live account verification.

## Lead conclusion

For the first three general-persona canaries, a **Buffer-first publishing adapter is the strongest zero-additional-spend bootstrap candidate**, subject to fresh verification of the owner's current Buffer account, exact connected channels, account ownership and API-key availability.

Why:
- Buffer's current GraphQL API is available on every plan, including Free.
- Free currently permits one API key and 3,000 requests per 30 days.
- Buffer's Free plan allows up to three connected channels at once.
- Buffer API supports creating/scheduling posts for Instagram, X/Twitter, Facebook and TikTok among other networks.
- Buffer supports drafts, giving us a safe non-public artifact path before scheduling/publishing.
- The historical Wait How Big handoff records an existing free Buffer workspace with X/Instagram/TikTok channels, although that handoff is dated 2026-08-31 and must be freshly verified before any current claim.

This does NOT mean we should silently reuse Wait How Big's public identity for the new personas. Reuse the infrastructure/accounts only where the identity/product mapping is explicitly appropriate.

## Route A — Buffer API: preferred bootstrap candidate

Current official evidence:
- Buffer API is GraphQL at https://api.buffer.com.
- API can create/schedule posts and retrieve connected channels.
- Buffer documents API access on the Free plan.
- Current Free API allowance: 1 API key, 3,000 requests / 30 days.
- Current Free plan: up to 3 connected channels at one time.
- Supported publishing channels include Facebook Pages, Instagram professional accounts, X/Twitter profiles and TikTok accounts.
- Draft posts can be created with saveToDraft=true and do not publish until explicitly scheduled.

Practical Social Bots implication:
1. Freshly verify the existing Buffer organization/workspace and current plan.
2. Verify exact connected channel identities; do not trust the August handoff as current.
3. Prefer a narrowly scoped owner API key created in Buffer's supported settings if the current Free plan permits it.
4. Use account/channel READ first.
5. Create **draft-only** canary artifacts first.
6. Only after owner posting authorization should a draft be scheduled or sent.
7. Treat Buffer post ID/state + destination public permalink/readback as separate verification layers.
8. Do not rely on Buffer API for production-grade analytics: Buffer itself says full/reliable analytics are not currently exposed through the API; experimental post-metrics queries should not be production reporting authority.

Potential limitation:
- Three connected channels on Free means Buffer alone cannot simultaneously represent all five target platforms/personas. It is, however, an excellent fit for the first V0.9 plan of one platform per each of three general personas.
- Historical account identities must not be forced into new persona roles.
- Reddit is not listed as a Buffer publishing channel.

Official sources:
- https://developers.buffer.com/guides/introduction.html
- https://developers.buffer.com/guides/getting-started.html
- https://developers.buffer.com/examples/create-draft-post.html
- https://support.buffer.com/en-us/articles/what-is-buffers-api-GtIYIQilz5
- https://support.buffer.com/en-us/articles/supported-channels-LM3P7Y4zsp
- https://support.buffer.com/en-us/articles/connecting-your-channels-to-buffer-HvWLgAJvL9
- https://support.buffer.com/en-us/articles/connecting-your-instagram-account-to-buffer-n9Ad6veXsu

## Route B — X direct API: not zero-spend

Current official evidence:
- Create Post endpoint is POST https://api.x.com/2/tweets using OAuth authorization.
- X currently documents pay-per-usage pricing.
- Current documented price for Post: Create is $0.015/request and Post: Create (with URL) is $0.200/request.
- X exposes a made_with_ai field for AI-generated media disclosure.
- Quote-post API capability is documented as Enterprise-only, not self-serve pay-per-use.

Project implication:
- Direct X API write automation is blocked under the owner's no-additional-spend rule unless existing prepaid credits already exist and their use is separately authorized.
- Prefer Buffer or manual-assisted X posting for zero-spend bootstrap.
- Do not buy X credits.

Official sources:
- https://docs.x.com/x-api/posts/create-post
- https://docs.x.com/x-api/getting-started/pricing

## Route C — TikTok direct Content Posting API: later/fallback

Current official evidence:
- Direct Post requires a registered TikTok developer app and Content Posting API.
- video.publish scope must be approved and authorized by the target TikTok user.
- TikTok requires explicit user consent for the post metadata/action.
- Unaudited API clients are restricted to private viewing; public direct-post capability requires audit.
- Current TikTok guidelines describe unaudited limits including private SELF_ONLY viewership and user caps; posting caps also apply.

Project implication:
- Direct TikTok API is not the fastest route to a public zero-spend canary unless an audited/approved app already exists.
- If the existing TikTok account is currently connected to Buffer, Buffer is likely the simpler bootstrap route.
- Keep a direct TikTok adapter as a later independence/fallback artifact, not a V0.9 prerequisite unless Buffer fails.

Official sources:
- https://developers.tiktok.com/docs/en/content-posting-api-get-started
- https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post
- https://developers.tiktok.com/docs/en/content-sharing-guidelines

## Route D — Reddit: separate architecture, no engagement manipulation

Current official evidence from Reddit Devvit:
- User Actions can submit posts and comments on behalf of the logged-in user when configured with the proper permissions.
- Apps cannot upvote/downvote posts/comments or follow users through these actions.
- Approved app version is required for user actions to be enabled broadly.

Project implication:
- Reddit should remain a separate route rather than being forced through Buffer.
- Devvit is promising for compliant posting/comment functionality but is installation/context-oriented; the exact route for the Social Bots public-persona use case must be designed and verified before implementation.
- Voting/karma manipulation is explicitly outside both platform capabilities and project authority.
- Do not rely on unverified community workarounds or scraping as the production route.

Official source:
- https://developers.reddit.com/docs/capabilities/server/userActions

## Instagram/Facebook direct Meta route

Direct official Meta documentation could not be reliably retrieved by the lead's current web tooling during this research pass, so no new direct-Meta API claim is accepted here.

Current **Buffer** documentation is sufficient to establish a safe bootstrap candidate:
- Instagram Professional (Business/Creator) via Instagram login can use automatic publishing on all Buffer plans.
- A linked Facebook Page is optional for Instagram publishing via Buffer but needed for advanced analytics/locations in Buffer.
- Facebook personal profiles cannot be connected for automated Buffer posting; Facebook Pages are supported.

A separate direct-Meta official-doc verification artifact should be groomed before implementing a direct Graph API fallback.

## Recommended future artifact sequence

1. SB-ACC-009 — Fresh Buffer account/workspace/channel readback artifact.
2. SB-ACC-010 — Buffer draft-only adapter + deterministic destination validator.
3. SB-ACC-011 — Three-channel zero-spend bootstrap allocation decision (which persona -> which initial platform), based on identity/account fit, not convenience.
4. SB-ACC-012 — Direct Meta fallback research/adapter contract.
5. SB-ACC-013 — Reddit compliant route design.
6. SB-ACC-014 — TikTok direct fallback contract.
7. SB-ACC-015 — X direct API route remains BLOCKED_NO_SPEND unless existing authorized credits are evidenced.

## Authority

This artifact authorizes no:
- account login;
- API key creation;
- credential use;
- channel connection/reconnection;
- public posting;
- spending;
- upgrade/trial.

Those remain separate artifacts/gates.
