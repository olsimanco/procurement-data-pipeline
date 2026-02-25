import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from curl_cffi import requests

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
INPUT_CSV = os.path.join(EXPORTS_DIR, "complete_red_flags.csv")
OUTPUT_CSV = os.path.join(EXPORTS_DIR, "red_flags_with_winners.csv")


# --- SETTINGS ---
# Set this to False when you are ready to run all 10,000+ rows!
TEST_MODE = True
TEST_LIMIT = 15  # Only process this many rows if TEST_MODE is True
# ----------------


def get_winner(tender_id):
    """Visits a tender's detail page and extracts the winning company."""
    url = f"https://openprocurement.al/sq/tender/view/id/{tender_id}"
    try:
        response = requests.get(url, impersonate="chrome", timeout=10)

        if response.status_code != 200:
            return "Error/Blocked"

        soup = BeautifulSoup(response.text, "html.parser")
        winner = "E Pacaktuar"

        # We loop through all 'td' elements because that's how the site is actually built
        for td in soup.find_all("td"):
            text = td.text.lower().strip()

            # Look for the exact label preceding the winner's name
            if (
                "operator ekonomik" in text
                or "fituesi" in text
                or "kontraktues" in text
            ):
                # Grab the next <td> right beside it
                next_td = td.find_next_sibling("td")
                if next_td:
                    # .text automatically strips away the <li> and <a> tags you found
                    winner = next_td.text.strip()
                    break

        return winner
    except Exception:
        return "Error"


def run_phase2():
    print("\n--- Starting Phase 2: Winner Extraction ---")

    if not os.path.exists(INPUT_CSV):
        print(f"Error: Cannot find {INPUT_CSV}. Please run Phase 1 first.")
        return

    # Load the data we scraped in Phase 1
    df = pd.read_csv(INPUT_CSV)

    if TEST_MODE:
        print(f"\n[!] RUNNING IN TEST MODE: Only processing first {TEST_LIMIT} rows!")
        df = df.head(TEST_LIMIT).copy()

    total_rows = len(df)
    winners_list = []

    # Loop through every tender ID
    for index, row in df.iterrows():
        tender_id = row["ID"]
        print(
            f"[{index + 1}/{total_rows}] Hunting winner for ID: {tender_id}...", end=" "
        )

        winner = get_winner(tender_id)
        winners_list.append(winner)
        print(f"Result: {winner}")

        time.sleep(1.0)  # Be nice to the server to avoid bans!

    # Add the new column to our database
    df["Fituesi (Winner)"] = winners_list

    # Save the upgraded database
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\nSuccess! Saved updated database to: {OUTPUT_CSV}")

    json_path = os.path.join(EXPORTS_DIR, "red_flags_with_winners.json")
    df.to_json(json_path, orient="records", force_ascii=False, indent=4)

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

        title = "Kompanitë me Më Shumë Tenderë me Flamur të Kuq"
        if TEST_MODE:
            title += " (TEST MODE)"

        plt.title(title, fontsize=14, fontweight="bold")
        plt.ylabel("Numri i Tenderëve", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        chart_path = os.path.join(EXPORTS_DIR, "top_winning_companies.png")
        plt.savefig(chart_path)
        print(f"Chart saved to: {chart_path}")
    else:
        print("Could not generate chart: No valid winners found.")


if __name__ == "__main__":
    run_phase2()
