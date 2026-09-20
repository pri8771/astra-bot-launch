# Account and browser setup contract

Use browser-first setup and existing accounts before proposing new accounts.

## Account model

A public persona profile does not need its own bot process or its own infrastructure login.

Preferred:
- shared administrative ownership where supported;
- distinct public persona profiles/handles when practical and free;
- isolated analytics attribution and persona memory.

Acceptable:
- one umbrella public profile with clearly labeled AI-managed characters/series.

Not acceptable:
- one account pretending to be three unrelated human beings;
- fabricated personal histories;
- fake endorsements;
- fake engagement;
- coordinated voting manipulation;
- bypassing platform account limits.

## Record only safe metadata

For each account/profile:
- platform;
- account alias;
- persona(s);
- login method;
- intended profile/workspace;
- supported browser/API route;
- publish/reply/DM capabilities;
- analytics route;
- last actual verification timestamp;
- exact gate;
- private credential reference such as "1Password item alias" or OS keychain label, never the secret.

Never commit:
passwords, passkeys, TOTP seeds, recovery codes, cookies, session state, private identity mappings, sensitive redirect URLs or access tokens.

## Human interruption rule

Claude/browser automation should navigate to the exact required step. The owner is involved only for password/passkey/MFA/CAPTCHA/consent when necessary. After completion, resume at the intended destination and record verification.
