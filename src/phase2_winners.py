import os
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
INPUT_CSV = os.path.join(EXPORTS_DIR, "complete_red_flags.csv")
OUTPUT_CSV = os.path.join(EXPORTS_DIR, "red_flags_with_winners.csv")

# --- PASTE YOUR VIP PASS HERE ---
RAW_COOKIES = (
    "cf_clearance=DOddKPciMDsipUt8XdpBY7lSiMELkZgY8HuzJFLgwLY-1772023617-1.2.1.1-R8Af_vS9gHJXAxYpWwhF4TLf6wxHAE076pIrZh9eZNFAT3rfqVFniaBC9vrP2D69ybVGrjjONdgw2vk1.uLSuSHeE8aTa5hQjOlxeG34ONGitcuSWER1MCXp80kt.brwvakiEI7R4ImYXK0KxDZGLbAJU2ZDe9tFjj5RaYz8r4V7_IMOdY49K.Ff00HAvHVgdwAn0Exidsbu..gvB.GiP3lXv8d9H1CZsd.R9l_GfqI; "
    "_ga=GA1.2.281829140.1771886313; "
    "_ga_X4EV9LSCJD=GS2.2.s1772023617$o3$g1$t1772023648$j29$l0$h0; "
    "_gat=1; "
    "_gid=GA1.2.1978119440.1772023617"
)

MY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
    "Cookie": RAW_COOKIES,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}
# --------------------------------


def get_winner(tender_id):
    """Visits a tender's detail page and extracts the winning company."""
    url = f"https://openprocurement.al/sq/tender/view/id/{tender_id}"
    try:
        response = requests.get(url, headers=MY_HEADERS)

        if "cf-browser-verification" in response.text or response.status_code != 200:
            return "Blocked/Error"

        soup = BeautifulSoup(response.text, "html.parser")

        winner = "E Pacaktuar"  # Default if no winner is listed

        # Search the page for the table header indicating the winner
        for th in soup.find_all("th"):
            text = th.text.lower()
            if (
                "operator ekonomik" in text
                or "fituesi" in text
                or "kontraktues" in text
            ):
                # The actual company name is usually in the table cell (td) right next to it
                td = th.find_next_sibling("td")
                if td:
                    winner = td.text.strip()
                    break

        return winner
    except Exception:
        return "Error"


def main():
    print("--- Starting Phase 2: Winner Extraction ---")

    if not os.path.exists(INPUT_CSV):
        print(f"Error: Cannot find {INPUT_CSV}. Please run main.py first.")
        return

    # Load the data we scraped in Phase 1
    df = pd.read_csv(INPUT_CSV)
    total_rows = len(df)
    print(f"Loaded {total_rows} red-flagged tenders.")

    winners_list = []

    # Loop through every tender ID
    for index, row in df.iterrows():
        tender_id = row["ID"]
        print(
            f"[{index + 1}/{total_rows}] Hunting winner for Tender ID: {tender_id}..."
        )

        winner = get_winner(tender_id)
        winners_list.append(winner)

        # IMPORTANT: Pause for 1.5 seconds between clicks so Cloudflare doesn't ban us
        time.sleep(1.5)

    # Add the new column to our database
    df["Fituesi (Winner)"] = winners_list

    # Save the upgraded database
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\nSuccess! Saved updated database to: {OUTPUT_CSV}")

    # --- Generate the Repeat Offenders Chart ---
    # Filter out tenders that don't have a specific winner listed
    valid_winners = df[
        ~df["Fituesi (Winner)"].isin(["E Pacaktuar", "Blocked/Error", "Error", ""])
    ]

    if not valid_winners.empty:
        plt.figure(figsize=(12, 7))
        top_winners = valid_winners["Fituesi (Winner)"].value_counts().head(10)

        # Plotting
        top_winners.plot(kind="bar", color="#d9534f", edgecolor="black")
        plt.title(
            "Top 10 Kompanitë me Më Shumë Tenderë me Flamur të Kuq",
            fontsize=14,
            fontweight="bold",
        )
        plt.ylabel("Numri i Tenderëve", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        chart_path = os.path.join(EXPORTS_DIR, "top_winning_companies.png")
        plt.savefig(chart_path)
        print(f"Chart saved to: {chart_path}")
    else:
        print("Could not generate chart: No valid winning companies found.")


if __name__ == "__main__":
    run_phase2()
