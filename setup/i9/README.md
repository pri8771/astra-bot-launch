# i9 staging packet — prepared, not run on the i9

The Intel i9 Mac is **optional, low-priority staging and secondary fallback**: use it only if immediately useful. **R730 remains the primary hub for Kai and local bots; Windows is the first fallback.** Leaving the i9 powered on does not start workers or transfer ownership. The mobile Mac being offline for roughly an hour does not authorize a service takeover. Do not install a redundant stack or pull models for this packet.

This packet uses stock macOS `/bin/bash`; it needs no Python, jq, package manager, or new app. It inventories the Mac on which it actually runs, prepares local folders, and checks a document checkout. Its reports are not evidence of runtime availability or a successful deployment.

## Three owner commands

The i9 is currently parked. Keep this packet ready; do not spend time on setup unless it becomes immediately useful. If inventory is useful, copy these four files together using an existing transfer method and open Terminal in that folder. **Stop after the first command for the current direction.** Commands two and three are prepared for optional later staging:

```bash
/bin/bash ./01_inventory.sh
/bin/bash ./02_prepare_workspace.sh
/bin/bash ./03_verify.sh
```

The default local workspace is `~/Astra-i9-staging`. The second command creates `repos/`, `work/`, `state/`, and `reports/`. If this Mac already has access to the private GitHub repository and needs a fresh checkout, use `/bin/bash ./02_prepare_workspace.sh --clone` as the second command instead. That flag is the only network operation: a clone of `https://github.com/pri8771/astra-bot-launch`, bounded to 45 seconds. Existing checkouts are checked locally and never pulled, reset, or overwritten.

For another location, add the same quoted absolute path to all three commands, for example `"$HOME/Astra i9 staging"`. Choose the Mac's local disk, outside iCloud/Dropbox/shared/network folders. Workspace components must not be symlinks. Do not put credentials in paths or command arguments.

## Read the reports and continue

- `01_inventory.sh` records OS, CPU/architecture, memory, free space, GPU chipset names, and known app/CLI presence. It does not include hardware serials, account details, environment dumps, credentials, or app state. Apart from its report directories/files, it only reads.
- `02_prepare_workspace.sh` creates folders and verifies a clean, expected repository if present. Without `--clone`, absence of a checkout is a reported follow-up, and no network connection occurs. Dirty, unexpected, or symlink checkouts are preserved and refused.
- `03_verify.sh` checks local directories, developer Git, a clean checkout and commit, and the portable documents. Exit `0` means local document review is ready **only after the owner confirms this is the intended i9**; exit `2` means follow-ups remain. Exit `1` indicates a refused/failed operation; `64` means invalid arguments. It does not call models, APIs, jobs, services, or other hosts.

Each run writes a private local `reports/<step>-<UTC>-<unique>/report.txt`, published by an atomic rename. Reports never replace a previous run. The report names the next action if Apple developer tools, repository access, or the document packet is missing. The scripts check the selected developer-tools directory before invoking its Git binary, avoiding the macOS Git shim's install prompt. Local Git checks disable hooks, filesystem-monitor helpers, and configured content filters; checkouts with submodules require separate review. Missing tools are not installed automatically. If needed, the owner can run `/usr/bin/xcode-select --install` separately and finish Apple's installer before retrying.

Optional cloning uses only authentication already configured on that Mac. Terminal/askpass and supported credential-manager prompts are disabled; a watchdog terminates a stalled clone and its helper process group. A failed/partial checkout is preserved for inspection. Complete GitHub sign-in through the Mac's existing IDE/account flow, confirm access to `pri8771/astra-bot-launch`, then retry in a fresh workspace if the partial target remains. No raw Git errors, tokens, or credentials are copied into reports.

Once the checkout and portable packet are available, open `~/Astra-i9-staging/repos/astra-bot-launch` using **File → Open Folder** in any existing IDE. Start with `focus/kai-pri-lipi/README.md`, then `WAVE_STATUS.md`, and read `focus/kai-pri-lipi/OWNER_DIRECTION.md` and referenced evidence before assigning work. If those documents are missing, ask the coordinator for the current packet; the scripts do not assume an old checkout includes current direction. An absent optional CLI does not prevent an installed IDE from reading Markdown.

No script changes power settings, OS settings, networking, remote access, services, cron, launch agents, package managers, or deployments. None migrates credentials, claims a queue, starts Kai/OpenClaw/Ollama, or enables failover. Reversal is manual: after inspecting any files you added, remove only this dedicated workspace and copied packet if no longer needed. Reports and checkout are the only lasting effects.

## Validation status

Prepared on the coordinator's ARM64 Mac, not executed on the unknown i9. Forty syntax and sandbox behavior checks passed; see `TEST_RECEIPT.md`. They establish script behavior, not target hardware readiness or bot operation. No actual network clone was attempted.
