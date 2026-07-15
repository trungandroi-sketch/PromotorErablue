import unittest

from app import parse_sheet_reference


class ParseSheetReferenceTests(unittest.TestCase):
    def test_extracts_id_from_full_url(self):
        url = "https://docs.google.com/spreadsheets/d/15Hpk_d8G2UFtiOzNcd-CqtidzIZPoRwLXt5dXU1jjas/edit?usp=sharing"
        sheet_id, gid = parse_sheet_reference(url, "0")

        self.assertEqual(sheet_id, "15Hpk_d8G2UFtiOzNcd-CqtidzIZPoRwLXt5dXU1jjas")
        self.assertEqual(gid, "0")

    def test_extracts_gid_from_url_query(self):
        url = "https://docs.google.com/spreadsheets/d/ID/edit#gid=123"
        sheet_id, gid = parse_sheet_reference(url, "0")

        self.assertEqual(sheet_id, "ID")
        self.assertEqual(gid, "123")

    def test_returns_raw_value_for_sheet_id(self):
        sheet_id, gid = parse_sheet_reference("ID_ONLY", "0")
        self.assertEqual(sheet_id, "ID_ONLY")
        self.assertEqual(gid, "0")


if __name__ == "__main__":
    unittest.main()
