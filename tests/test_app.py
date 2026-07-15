import io
import unittest

import pandas as pd

from app import build_store_summary, load_data


class LoadDataTests(unittest.TestCase):
    def test_load_data_uses_local_csv_when_provided(self) -> None:
        csv_content = "shop,brand\nA,BrandA\nB,BrandB\n"
        local_file = io.StringIO(csv_content)

        df = load_data("dummy-sheet", "0", use_private=False, local_file=local_file)

        self.assertEqual(df.iloc[0]["shop"], "A")
        self.assertEqual(df.iloc[1]["brand"], "BrandB")


class BuildStoreSummaryTests(unittest.TestCase):
    def test_build_store_summary_includes_ce_ict_warnings(self) -> None:
        data = pd.DataFrame(
            [
                {"store_id": "S1", "store_name": "Shop 1", "brand": "BrandA", "category": "CE", "active": "ACTIVE"},
                {"store_id": "S1", "store_name": "Shop 1", "brand": "BrandB", "category": "PHONE", "active": "ACTIVE"},
                {"store_id": "S2", "store_name": "Shop 2", "brand": "BrandA", "category": "CE", "active": "ACTIVE"},
            ]
        )
        cols = {
            "store_id": "store_id",
            "store_name": "store_name",
            "brand": "brand",
            "category": "category",
            "active": "active",
            "name_verification": None,
            "nik_verification": None,
        }

        summary = build_store_summary(data, cols)

        store1 = summary[summary["store_id"] == "S1"].iloc[0]
        store2 = summary[summary["store_id"] == "S2"].iloc[0]

        self.assertEqual(store1["total_promotor"], 2)
        self.assertEqual(store1["ce_count"], 1)
        self.assertEqual(store1["ict_count"], 1)
        self.assertIn("CE < 2 người", store1["warnings"])
        self.assertIn("ICT < 2 người", store1["warnings"])

        self.assertEqual(store2["total_promotor"], 1)
        self.assertEqual(store2["ce_count"], 1)
        self.assertEqual(store2["ict_count"], 0)
        self.assertIn("Thiếu ICT", store2["warnings"])


if __name__ == "__main__":
    unittest.main()
