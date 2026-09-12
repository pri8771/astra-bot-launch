# Local validation receipt — 2026-09-12

**Prepared, not run on the target i9.** The development host was actual Darwin/ARM64 with Apple Bash 3.2.57 and an existing selected Xcode Git binary. No hardware identity was mocked into a successful result.

The final validation run passed **40 checks** and produced 11 complete, private (`0600`) local reports under `/private/tmp/astra-i9-script-check.fWt3iQ`. The local Git fixture was explicitly artificial and was never claimed as the real cloud task library or a deployment. No network clone, authentication, installation, model call, service start, or other-host action occurred.

Validated behavior:

- All three scripts pass `/bin/bash -n` under stock Apple Bash.
- Actual development-host inventory finishes; workspace paths containing spaces work; repeated local directory preparation succeeds.
- All scripts refuse relative paths, root, dot components, file paths, symlink ancestors, and trailing-slash symlink paths. Refused paths do not create a child workspace.
- Default preparation leaves the repository absent and does not attempt a clone. Verification reports an absent checkout as incomplete.
- An existing clean local fixture is preserved; a missing `OWNER_DIRECTION.md` is reported as incomplete.
- A dirty fixture is refused even with `--clone`; its untracked file remains intact. Verification also reports the changed checkout as incomplete.
- A deliberately configured content filter that would create a sentinel file does not execute during preparation or verification.
- An unexpected origin is refused without printing its URL.
- Every completed report is published without a remaining `report.pending` file and has private file permissions.

Independent static review checked Bash 3.2 compatibility, path handling, overwrite protection, prompt limitations, helper execution, and clone-process cleanup. Findings led to full ancestor checks, required owner-direction checks, disabled content filters, and cleanup on interruption. Later wording changes keep the i9 parked and instruct the owner to stop after any useful inventory.

Not exercised: actual Intel i9 hardware, missing developer tools, a non-macOS machine, a real GitHub clone or auth failure, the clone timeout against an actual credential helper, or any runtime readiness. These remain unverified; the scripts do not report them as completed. Supported credential prompts are suppressed and a watchdog bounds cloning, but arbitrary custom helpers may still show UI.
