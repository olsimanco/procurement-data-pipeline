import os
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from curl_cffi import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

RED_FLAG_MAPPING = {
    1: "Mungese konkurrence",
    2: "Procedure me negocim",
    3: "Me negocim, pa njoftim",
    4: "Pamundesi kohore per pergatitje te nje oferte (oferte teknike plus dokumentacion)",
    5: "Shtese kontrate (shtese vlere) pa perfunduar ende faza e pare e kontrates",
    6: "Skualifikim i te gjithe operatoreve konkurrues pervec fituesit/ Skualifikim i ofertes vlere me e ulet",
    7: "Anullimi i Tenderit dy ose me shume here",
}


def clean_money_string(val):
    if pd.isna(val) or str(val).strip() == "":
        return 0.0
    try:
        return float(str(val).replace(" ", "").strip())
    except ValueError:
        return 0.0


def fetch_flag_data(flag_id, flag_name):
    url = f"https://openprocurement.al/sq/index/redflag/flag_options/{flag_id}"
    print(f"Fetching data for: {flag_name}...")

    try:
        # Impersonate Chrome to bypass Cloudflare automatically
        response = requests.get(url, impersonate="chrome")

        if response.status_code != 200:
            print("  -> Server error or blocked.")
            return pd.DataFrame()

        soup = BeautifulSoup(response.text, "html.parser")
        tbody = soup.find("tbody")

        if not tbody:
            print("  -> Warning: No data table found.")
            return pd.DataFrame()

        tenders = []
        for row in tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 8:
                tenders.append(
                    {
                        "ID": cols[1].text.strip(),
                        "Titulli": cols[2].text.strip(),
                        "Autoriteti Prokurues": cols[3].text.strip(),
                        "Institucioni Prokurues": cols[4].text.strip(),
                        "Vlera / Fondi Limit": clean_money_string(cols[5].text.strip()),
                        "Data e Shpalljes": cols[6].text.strip(),
                        "Nr Reference": cols[7].text.strip(),
                        "Red Flag Reason": flag_name,
                    }
                )

        df = pd.DataFrame(tenders)
        print(f"  -> Success! Extracted {len(df)} rows.")
        return df

    except Exception as e:
        print(f"  -> Error: {str(e)[:100]}")
        return pd.DataFrame()


def run_phase1():
    print("\n--- Starting Phase 1: Base Data Scraper ---")
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    all_flags_data = []

    for flag_id, flag_name in RED_FLAG_MAPPING.items():
        df_flag = fetch_flag_data(flag_id, flag_name)
        if not df_flag.empty:
            all_flags_data.append(df_flag)

    if all_flags_data:
        master_df = pd.concat(all_flags_data, ignore_index=True)
        print(f"\n--- Phase 1 Complete! Total rows: {len(master_df)} ---")
        csv_path = os.path.join(EXPORTS_DIR, "complete_red_flags.csv")
        master_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"File saved to: {csv_path}")
    else:
        print("\nExtraction failed. No files were saved.")


if __name__ == "__main__":
    run_phase1()
