from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

from tools.architecture import MODULES, find_violations


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"


class PersistenceArchitectureTests(unittest.TestCase):
    def test_each_module_has_an_independent_schema_migration(self) -> None:
        config = (BACKEND / "alembic.ini").read_text()

        for module in MODULES:
            version_directory = BACKEND / f"migrations/{module}/versions"
            revisions = list(version_directory.glob("*.py"))
            self.assertEqual(len(revisions), 1, module)
            source = revisions[0].read_text()
            self.assertIn(f'revision = "{module}_0001"', source)
            self.assertIn(f'CREATE SCHEMA "{module}"', source)
            self.assertIn(f'DROP SCHEMA "{module}"', source)
            self.assertIn(f"migrations/{module}/versions", config)

    def test_unit_of_work_port_stays_framework_independent(self) -> None:
        port = (
            BACKEND
            / "packages/core/src/thief_core/shared/unit_of_work.py"
        )
        adapter = (
            BACKEND
            / "packages/adapters/src/thief_adapters/infrastructure/unit_of_work.py"
        )

        self.assertTrue(port.is_file())
        self.assertTrue(adapter.is_file())
        self.assertEqual(
            find_violations(BACKEND / "packages/core/src/thief_core"),
            [],
        )

    def test_make_exposes_migration_command(self) -> None:
        result = subprocess.run(
            ["make", "--dry-run", "migrate"],
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("THIEF_DATABASE_URL=", result.stdout)
        self.assertIn("alembic -c alembic.ini upgrade heads", result.stdout)

    def test_make_preserves_an_external_database_url(self) -> None:
        ci_url = "postgresql+psycopg://thief:thief_ci@localhost:5432/thief"
        result = subprocess.run(
            ["make", "--dry-run", "migrate"],
            cwd=ROOT,
            env={**os.environ, "THIEF_DATABASE_URL": ci_url},
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"THIEF_DATABASE_URL={ci_url}", result.stdout)

    def test_ci_runs_migrations_and_integration_tests_on_postgres_18(self) -> None:
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()

        for expected in (
            "image: postgres:18.4-bookworm",
            "make migrate",
            "make test-integration",
        ):
            self.assertIn(expected, workflow)

        result = subprocess.run(
            ["make", "--dry-run", "test-integration"],
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("tests/integration", result.stdout)


if __name__ == "__main__":
    unittest.main()
