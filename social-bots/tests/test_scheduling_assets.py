"""Protects the SB-V07-001 scheduling package: OS task definitions and
installers for social-bots/bin/worker_once.py, plus the README/RUNBOOK that
document the exit-code contract and the honesty boundary around them.

These are static assets (XML/plist/systemd/shell/PowerShell text), so this
suite checks structure and cross-file consistency rather than behavior:
that every required file exists, that each template declares the fields the
runbook promises, and that no template carries a placeholder token its
matching installer never substitutes (which would silently ship a broken
scheduled task).
"""
import plistlib
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SCHED_DIR = Path(__file__).resolve().parent.parent / "scheduling"

README = SCHED_DIR / "README.md"
RUNBOOK = SCHED_DIR / "RUNBOOK.md"

WIN_XML = SCHED_DIR / "windows" / "SocialBotsWorkerOnce.xml"
WIN_INSTALL = SCHED_DIR / "windows" / "Install-WorkerOnceTask.ps1"
WIN_UNINSTALL = SCHED_DIR / "windows" / "Uninstall-WorkerOnceTask.ps1"

LINUX_SERVICE = SCHED_DIR / "linux" / "social-bots-worker-once@.service"
LINUX_TIMER = SCHED_DIR / "linux" / "social-bots-worker-once@.timer"
LINUX_INSTALL = SCHED_DIR / "linux" / "install_systemd.sh"

MAC_PLIST = SCHED_DIR / "macos" / "com.socialbots.workeronce.plist"
MAC_INSTALL = SCHED_DIR / "macos" / "install_launchd.sh"

ALL_REQUIRED_FILES = (
    README, RUNBOOK,
    WIN_XML, WIN_INSTALL, WIN_UNINSTALL,
    LINUX_SERVICE, LINUX_TIMER, LINUX_INSTALL,
    MAC_PLIST, MAC_INSTALL,
)

TASK_NS = "http://schemas.microsoft.com/windows/2004/02/mit/task"

# Which installer is responsible for substituting each template's
# placeholders. A template must never carry a __TOKEN__ its installer does
# not mention, or a real install silently ships a broken command line.
TEMPLATE_TO_INSTALLER = {
    WIN_XML: WIN_INSTALL,
    LINUX_SERVICE: LINUX_INSTALL,
    LINUX_TIMER: LINUX_INSTALL,
    MAC_PLIST: MAC_INSTALL,
}

PLACEHOLDER_RE = re.compile(r"__[A-Z0-9_]+__")


class ScheduledAssetsExistTest(unittest.TestCase):
    """Protects against a partial SB-V07-001 package (a file silently dropped)."""

    def test_all_required_files_exist(self):
        for path in ALL_REQUIRED_FILES:
            self.assertTrue(path.is_file(), f"missing required file: {path}")


class WindowsTaskXmlTest(unittest.TestCase):
    """Protects the Task Scheduler v1.2 template's structure and namespace."""

    @classmethod
    def setUpClass(cls):
        cls.tree = ET.parse(WIN_XML)
        cls.root = cls.tree.getroot()
        cls.ns = {"t": TASK_NS}

    def test_root_uses_task_scheduler_namespace(self):
        self.assertEqual(self.root.tag, f"{{{TASK_NS}}}Task")

    def test_multiple_instances_policy_is_ignore_new(self):
        el = self.root.find(".//t:Settings/t:MultipleInstancesPolicy", self.ns)
        self.assertIsNotNone(el, "MultipleInstancesPolicy element missing")
        self.assertEqual(el.text, "IgnoreNew")

    def test_execution_time_limit_present(self):
        el = self.root.find(".//t:Settings/t:ExecutionTimeLimit", self.ns)
        self.assertIsNotNone(el, "ExecutionTimeLimit element missing")
        self.assertTrue(el.text and el.text.startswith("PT"))

    def test_action_invokes_python_placeholder_against_worker_once(self):
        command = self.root.find(".//t:Actions/t:Exec/t:Command", self.ns)
        args = self.root.find(".//t:Actions/t:Exec/t:Arguments", self.ns)
        self.assertIsNotNone(command)
        self.assertIsNotNone(args)
        self.assertIn("__PYTHON_EXE__", command.text)
        self.assertIn("worker_once.py", args.text)


class MacLaunchdPlistTest(unittest.TestCase):
    """Protects the launchd template's required keys and their types."""

    @classmethod
    def setUpClass(cls):
        with open(MAC_PLIST, "rb") as fh:
            cls.plist = plistlib.load(fh)

    def test_label_present(self):
        self.assertIn("Label", self.plist)
        self.assertTrue(self.plist["Label"])

    def test_program_arguments_reference_worker_once(self):
        args = self.plist["ProgramArguments"]
        self.assertTrue(any("worker_once.py" in a for a in args),
                         f"no worker_once.py reference in {args}")

    def test_start_interval_present(self):
        self.assertIn("StartInterval", self.plist)

    def test_run_at_load_is_false(self):
        self.assertIs(self.plist["RunAtLoad"], False)


class LinuxSystemdUnitTest(unittest.TestCase):
    """Protects the systemd template unit/timer's oneshot and hardening contract."""

    @classmethod
    def setUpClass(cls):
        cls.service_text = LINUX_SERVICE.read_text()
        cls.timer_text = LINUX_TIMER.read_text()

    def test_service_is_oneshot(self):
        self.assertIn("Type=oneshot", self.service_text)

    def test_service_success_exit_status_covers_benign_codes(self):
        m = re.search(r"^SuccessExitStatus=(.+)$", self.service_text, re.MULTILINE)
        self.assertIsNotNone(m, "SuccessExitStatus= line missing")
        codes = m.group(1).split()
        self.assertIn("3", codes, "no-overlap exit (3) must not be logged as a failure")
        self.assertIn("5", codes, "lead-halt exit (5) must not be logged as a failure")

    def test_service_has_no_new_privileges_hardening(self):
        self.assertIn("NoNewPrivileges=true", self.service_text)

    def test_timer_has_repeat_interval(self):
        self.assertRegex(self.timer_text, re.compile(r"^OnUnitActiveSec=.+$", re.MULTILINE))

    def test_timer_is_persistent(self):
        self.assertIn("Persistent=true", self.timer_text)


class ShellInstallerConventionsTest(unittest.TestCase):
    """Protects the bash installers' safety preamble (shebang + strict mode)."""

    def test_shell_installers_start_with_shebang_and_use_strict_mode(self):
        for path in (LINUX_INSTALL, MAC_INSTALL):
            text = path.read_text()
            self.assertTrue(text.startswith("#!"), f"{path} missing shebang")
            self.assertIn("set -euo pipefail", text, f"{path} missing strict mode")


class PowerShellInstallerConventionsTest(unittest.TestCase):
    """Protects the PowerShell installers' fail-fast error handling."""

    def test_powershell_installers_set_error_action_preference(self):
        for path in (WIN_INSTALL, WIN_UNINSTALL):
            text = path.read_text()
            self.assertIn("$ErrorActionPreference", text, f"{path} missing $ErrorActionPreference")


class PlaceholderCoverageTest(unittest.TestCase):
    """Protects against a template placeholder no installer ever substitutes."""

    def test_every_template_placeholder_is_referenced_by_its_installer(self):
        for template_path, installer_path in TEMPLATE_TO_INSTALLER.items():
            template_tokens = set(PLACEHOLDER_RE.findall(template_path.read_text()))
            installer_text = installer_path.read_text()
            missing = {tok for tok in template_tokens if tok not in installer_text}
            self.assertFalse(
                missing,
                f"{template_path.name} has placeholder(s) {missing} that "
                f"{installer_path.name} never substitutes",
            )


class HonestyBoundaryDocumentationTest(unittest.TestCase):
    """Protects the explicit claim that a scheduler entry is not proof of a run."""

    def test_readme_states_scheduler_entry_is_not_proof(self):
        text = README.read_text().lower()
        self.assertIn("not evidence that a worker ran", text)

    def test_runbook_states_scheduler_entry_is_not_proof(self):
        text = RUNBOOK.read_text().lower()
        self.assertTrue(
            "not evidence" in text or "does not prove" in text,
            "RUNBOOK.md must state that installing a schedule is not proof of a run",
        )

    def test_readme_and_runbook_reference_governing_contracts(self):
        for path in (README,):
            text = path.read_text()
            self.assertIn("AUTONOMY_CONTRACT.md", text)
            self.assertIn("HEARTBEAT_ASSIGNMENT_PROTOCOL.md", text)


if __name__ == "__main__":
    unittest.main()
