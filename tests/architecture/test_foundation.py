from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.architecture import find_violations, required_layout_errors


ROOT = Path(__file__).resolve().parents[2]


class FoundationLayoutTests(unittest.TestCase):
    def test_required_foundation_layout_exists(self) -> None:
        self.assertEqual(required_layout_errors(ROOT), [])


class ArchitectureBoundaryTests(unittest.TestCase):
    def test_core_rejects_framework_imports(self) -> None:
        violations = self._scan(
            "catalog/domain/model.py",
            "from fastapi import FastAPI\n",
        )

        self.assert_rule(violations, "core-framework")

    def test_module_rejects_other_module_internals(self) -> None:
        violations = self._scan(
            "identity/application/use_case.py",
            "from thief_core.catalog.domain.model import Template\n",
        )

        self.assert_rule(violations, "cross-module-internal")

    def test_shared_rejects_business_symbols(self) -> None:
        violations = self._scan(
            "shared/job.py",
            "class GenerationJob:\n    pass\n",
        )

        self.assert_rule(violations, "shared-business-symbol")

    def test_public_contract_import_is_allowed(self) -> None:
        violations = self._scan(
            "identity/application/use_case.py",
            "from thief_core.catalog import PublishTemplate\n",
        )

        self.assertEqual(violations, [])

    def _scan(self, relative_path: str, source: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            core = Path(directory) / "packages/core/src/thief_core"
            target = core / relative_path
            target.parent.mkdir(parents=True)
            target.write_text(source, encoding="utf-8")
            return find_violations(core)

    def assert_rule(self, violations: list[str], rule: str) -> None:
        self.assertTrue(
            any(item.startswith(f"{rule}:") for item in violations),
            violations,
        )


if __name__ == "__main__":
    unittest.main()
