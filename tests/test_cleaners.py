import unittest
import sys
import os

# This allows the test file to find your src folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.phase1_scraper import clean_money_string


class TestDataCleaners(unittest.TestCase):

    def test_clean_money_normal_string(self):
        """Tests if it correctly removes spaces from standard Albanian money formats."""
        result = clean_money_string("4 500 000")
        self.assertEqual(result, 4500000.0)

    def test_clean_money_empty_values(self):
        """Tests if it handles missing data safely without crashing."""
        self.assertEqual(clean_money_string(""), 0.0)
        self.assertEqual(clean_money_string(None), 0.0)

    def test_clean_money_corrupted_text(self):
        """Tests if it defaults to 0.0 when it encounters letters instead of numbers."""
        self.assertEqual(clean_money_string("E Pacaktuar"), 0.0)


if __name__ == "__main__":
    unittest.main()
