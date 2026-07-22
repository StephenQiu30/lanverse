from __future__ import annotations

import os
import unittest

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from tools.architecture import MODULES


class MigrationIntegrationTests(unittest.TestCase):
    engine: Engine

    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(os.environ["THIEF_DATABASE_URL"])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine.dispose()

    def test_all_module_schemas_and_revisions_exist(self) -> None:
        with self.engine.connect() as connection:
            schemas = set(
                connection.execute(
                    text(
                        "SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name = ANY(:schemas)"
                    ),
                    {"schemas": list(MODULES)},
                ).scalars()
            )
            revisions = set(
                connection.execute(
                    text("SELECT version_num FROM public.alembic_version")
                ).scalars()
            )

        self.assertEqual(schemas, set(MODULES))
        self.assertEqual(revisions, {f"{module}_0001" for module in MODULES})

    def test_initial_migrations_do_not_create_business_tables(self) -> None:
        with self.engine.connect() as connection:
            tables = list(
                connection.execute(
                    text(
                        "SELECT table_schema, table_name "
                        "FROM information_schema.tables "
                        "WHERE table_schema = ANY(:schemas)"
                    ),
                    {"schemas": list(MODULES)},
                )
            )

        self.assertEqual(tables, [])


if __name__ == "__main__":
    unittest.main()
