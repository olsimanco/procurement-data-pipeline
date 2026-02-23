import os
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Set up paths dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

# Map the URL IDs to the actual Red Flag reasons.
RED_FLAG_MAPPING = {
    1: "Mungese konkurrence",
    2: "Procedure me negocim",
    3: "Me negocim, pa njoftim",
    4: "Pamundesi kohore per pergatitje te nje oferte (oferte teknike plus dokumentacion)",
    5: "Shtese kontrate (shtese vlere) pa perfunduar ende faza e pare e kontrates",
    6: " Skualifikim i te gjithe operatoreve konkurrues pervec fituesit/ Skualifikim i ofertes vlere me e ulet",
    7: "Anullimi i Tenderit dy ose me shume here",
}


def fetch_paginated_flag_data(flag_id, flag_name):
    """
    Scrapes all pages for a specific red flag ID using a while loop.
    """
    print(f"\n--- Starting Extraction for: {flag_name} ---")
    all_pages_data = []
    page = 1
    previous_df = None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    while True:
        # IMPORTANT: The "?page=" parameter might be different on the live site.
        # Sometimes it is "?faqe=" or just "/page/2".
        url = f"https://openprocurement.al/sq/index/redflag/flag_options/{flag_id}?page={page}"
        print(f"  -> Scraping Page {page}...")

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # Extract all HTML tables from the page
            tables = pd.read_html(response.text)

            if not tables:
                print("     No tables found. End of pages reached.")
                break

            df = tables[0]  # The main data is almost always the first table (index 0)

            # Protection against infinite loops: Some websites just reload Page 1
            # if you request a page number that doesn't exist.
            if previous_df is not None and df.equals(previous_df):
                print("     Duplicate data detected. End of pages reached.")
                break

            # If the table is empty (just headers), stop the loop
            if df.empty or len(df) == 0:
                print("     Empty table. End of pages reached.")
                break

            # Tag the data with the reason so we can sort it later
            df["Red Flag Reason"] = flag_name
            all_pages_data.append(df)

            previous_df = df.copy()
            page += 1

            # Be polite to the server
            time.sleep(1)

        except ValueError:
            # Pandas throws a ValueError if it literally finds no <table> tags
            print("     No HTML tables exist on this page. Stopping.")
            break
        except Exception as e:
            print(f"     Error on page {page}: {e}")
            break

    # Combine all pages for this specific flag into one DataFrame
    if all_pages_data:
        return pd.concat(all_pages_data, ignore_index=True)
    return pd.DataFrame()


def export_results(master_df):
    """Saves the combined data to CSV and generates a summary chart."""
    if master_df.empty:
        print("\nNo data to export. Exiting.")
        return

    # 1. Save to CSV
    csv_path = os.path.join(EXPORTS_DIR, "complete_red_flags.csv")
    master_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"\nData successfully exported to: {csv_path}")

    # 2. Generate a visual summary of the findings
    plt.figure(figsize=(10, 6))

    # Count how many times each company appears across ALL red flags
    # Note: Update 'Operator Ekonomik Kontraktues' if the column name is slightly different
    company_col = "Operator Ekonomik Kontraktues"

    if company_col in master_df.columns:
        top_companies = master_df[company_col].value_counts().head(10)

        top_companies.plot(kind="bar", color="darkred", edgecolor="black")
        plt.title(
            "Top 10 Companies by Number of Red-Flagged Tenders",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Company Name", fontsize=12)
        plt.ylabel("Total Flags", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        chart_path = os.path.join(EXPORTS_DIR, "top_offenders_chart.png")
        plt.savefig(chart_path)
        print(f"Chart exported to: {chart_path}")
    else:
        print(
            f"Could not generate chart: Column '{company_col}' not found in the table."
        )


def main():
    print("Initializing Multi-Page Extraction...")
    os.makedirs(EXPORTS_DIR, exist_ok=True)

    all_flags_data = []

    for flag_id, flag_name in RED_FLAG_MAPPING.items():
        df_flag = fetch_paginated_flag_data(flag_id, flag_name)
        if not df_flag.empty:
            all_flags_data.append(df_flag)

    if all_flags_data:
        master_df = pd.concat(all_flags_data, ignore_index=True)
        print(
            f"\nExtraction complete! Total flagged tenders downloaded: {len(master_df)}"
        )
        export_results(master_df)
    else:
        print("\nFailed to extract any data.")


if __name__ == "__main__":
    main()
