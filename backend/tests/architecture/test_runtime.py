from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CI_WORKFLOW = ROOT / ".github/workflows/ci.yml"


class RuntimeContractTests(unittest.TestCase):
    def test_runtime_entrypoints_and_smoke_test_exist(self) -> None:
        for path in (
            "backend/apps/scheduler/src/thief_scheduler/app.py",
            "backend/apps/scheduler/src/thief_scheduler/settings.py",
            "backend/tools/runtime_smoke.py",
        ):
            self.assertTrue((ROOT / path).is_file(), path)

        for target, expected in (
            ("run-web", "pnpm --dir frontend start"),
            ("run-api", "uvicorn thief_api.main:app"),
            ("run-worker", "celery"),
            ("run-scheduler", "beat"),
            ("test-runtime", "tools/runtime_smoke.py"),
        ):
            result = subprocess.run(
                ["make", "--dry-run", target],
                cwd=ROOT,
                capture_output=True,
                check=False,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(expected, result.stdout)

    def test_ci_runs_runtime_smoke_with_rabbitmq(self) -> None:
        workflow = CI_WORKFLOW.read_text()

        for expected in (
            "image: rabbitmq:4.3.3-management",
            "THIEF_RABBITMQ_URL: amqp://thief:thief_ci@localhost:5672//",
            "make test-runtime",
        ):
            self.assertIn(expected, workflow)


if __name__ == "__main__":
    unittest.main()
