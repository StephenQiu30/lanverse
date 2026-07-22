from __future__ import annotations

import ast
from pathlib import Path


MODULES = (
    "identity",
    "ingestion",
    "catalog",
    "search",
    "creation",
    "generation",
    "asset",
    "governance",
)
FORBIDDEN_IMPORTS = {"boto3", "celery", "fastapi", "minio", "sqlalchemy"}
PRIVATE_SEGMENTS = {"application", "domain", "orm", "repository"}
BUSINESS_SYMBOLS = {
    "Asset",
    "GenerationJob",
    "Source",
    "Template",
    "User",
    "Work",
}


def required_layout_errors(root: Path) -> list[str]:
    required = [
        ".node-version",
        ".python-version",
        "Makefile",
        "package.json",
        "pnpm-lock.yaml",
        "pnpm-workspace.yaml",
        "pyproject.toml",
        "turbo.json",
        "uv.lock",
        "apps/web/package.json",
        "apps/web/src/app/page.tsx",
        "apps/web/src/app/health/route.ts",
        "apps/api/src/thief_api/main.py",
        "apps/worker/src/thief_worker/app.py",
        "apps/scheduler/src/thief_scheduler/main.py",
        "packages/contracts/src/thief_contracts/__init__.py",
        "packages/adapters/src/thief_adapters/__init__.py",
    ]
    for module in MODULES:
        base = f"packages/core/src/thief_core/{module}"
        required.extend(
            f"{base}/{part}/__init__.py"
            for part in ("domain", "application", "ports")
        )
        required.append(f"{base}/__init__.py")

    return [f"missing:{path}" for path in required if not (root / path).is_file()]


def find_violations(core: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(core.rglob("*.py")):
        relative = path.relative_to(core)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as error:
            violations.append(f"invalid-python:{relative}:{error.lineno}")
            continue
        violations.extend(_import_violations(relative, tree))
        violations.extend(_shared_violations(relative, tree))
    return violations


def _import_violations(relative: Path, tree: ast.AST) -> list[str]:
    current_module = relative.parts[0] if relative.parts else ""
    violations: list[str] = []
    for node in ast.walk(tree):
        imported = _imported_module(node)
        if imported is None:
            continue
        root = imported.split(".", 1)[0]
        if root in FORBIDDEN_IMPORTS:
            violations.append(f"core-framework:{relative}:{imported}")
        parts = imported.split(".")
        if len(parts) < 3 or parts[0] != "thief_core":
            continue
        target_module = parts[1]
        if target_module != current_module and parts[2] in PRIVATE_SEGMENTS:
            violations.append(f"cross-module-internal:{relative}:{imported}")
    return violations


def _imported_module(node: ast.AST) -> str | None:
    if isinstance(node, ast.Import) and node.names:
        return node.names[0].name
    if isinstance(node, ast.ImportFrom):
        return node.module
    return None


def _shared_violations(relative: Path, tree: ast.AST) -> list[str]:
    if not relative.parts or relative.parts[0] != "shared":
        return []
    return [
        f"shared-business-symbol:{relative}:{node.name}"
        for node in ast.walk(tree)
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in BUSINESS_SYMBOLS
    ]
