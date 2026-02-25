import unittest
from bs4 import BeautifulSoup


# We copy the exact logic from your phase2_winners.py
def extract_winner_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for td in soup.find_all("td"):
        text = td.text.lower().strip()
        if "operator ekonomik" in text or "fituesi" in text or "kontraktues" in text:
            next_td = td.find_next_sibling("td")
            if next_td:
                return next_td.text.strip()
    return "E Pacaktuar"


class TestWinnerExtractor(unittest.TestCase):

    def test_successful_winner_extraction(self):
        """Tests if the parser can dig through the <td> and <li> tags to find the company."""
        # This is the exact HTML snippet you grabbed for me earlier!
        fake_html = """
        <tr>
            <td>Operator Ekonomik Kontraktues</td>
            <td>
                <li style="list-decoration:none;display:inline;">
                    <a href="http://opencorporates.al/sq/nipt/L64425401K">4 S</a>
                </li>
            </td>
        </tr>
        """
        result = extract_winner_from_html(fake_html)
        self.assertEqual(result, "4 S")

    def test_missing_winner(self):
        """Tests if the parser safely returns 'E Pacaktuar' when the table is empty."""
        fake_html = "<tr><td>Some other data</td><td>Nothing here</td></tr>"
        result = extract_winner_from_html(fake_html)
        self.assertEqual(result, "E Pacaktuar")


if __name__ == "__main__":
    unittest.main()
