from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FRONTEND = ROOT / "frontend/src"


class ProductShellContractTests(unittest.TestCase):
    def test_product_routes_and_shared_shell_exist(self) -> None:
        required = (
            "app/explore/page.tsx",
            "app/login/page.tsx",
            "app/create/page.tsx",
            "app/works/page.tsx",
            "app/admin/page.tsx",
            "components/page-placeholder.tsx",
            "components/site-header.tsx",
        )

        self.assertEqual(
            [path for path in required if not (FRONTEND / path).is_file()],
            [],
        )

    def test_navigation_exposes_the_accepted_information_architecture(self) -> None:
        header = (FRONTEND / "components/site-header.tsx").read_text()
        layout = (FRONTEND / "app/layout.tsx").read_text()

        self.assertIn('href="/"', header)
        for href in ("/explore", "/login", "/create", "/works", "/admin"):
            self.assertIn(f'href: "{href}"', header)
        self.assertIn("<SiteHeader />", layout)

    def test_each_route_has_a_distinct_server_rendered_purpose(self) -> None:
        expected = {
            "app/page.tsx": "发现灵感，开始创作",
            "app/explore/page.tsx": "探索灵感",
            "app/login/page.tsx": "邀请制登录",
            "app/create/page.tsx": "开始创作",
            "app/works/page.tsx": "我的作品",
            "app/admin/page.tsx": "管理中心",
        }

        for path, heading in expected.items():
            source = (FRONTEND / path).read_text()
            self.assertIn(heading, source)
            self.assertNotIn('"use client"', source)


if __name__ == "__main__":
    unittest.main()
