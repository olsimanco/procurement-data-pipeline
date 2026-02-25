import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# Set up paths dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

# --- YOUR VIP PASS (COOKIES & HEADERS) ---
# Combined all your cookies into one perfect string
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
# ----------------------------------------

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
    if not val or val == "":
        return 0.0
    try:
        return float(str(val).replace(" ", "").strip())
    except ValueError:
        return 0.0


def fetch_flag_data(flag_id, flag_name):
    url = f"https://openprocurement.al/sq/index/redflag/flag_options/{flag_id}"
    print(f"Fetching data for: {flag_name}...")

    try:
        # Using the standard requests library with your Firefox headers
        response = requests.get(url, headers=MY_HEADERS)

        # Check if Cloudflare blocked us
        if (
            "cf-browser-verification" in response.text
            or "challenge-platform" in response.text
        ):
            print("  -> Blocked by Cloudflare! Your cookie might have expired.")
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


def main():
    print("--- Starting Procurement Red Flag Scraper ---")
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    all_flags_data = []

    for flag_id, flag_name in RED_FLAG_MAPPING.items():
        df_flag = fetch_flag_data(flag_id, flag_name)
        if not df_flag.empty:
            all_flags_data.append(df_flag)

    if all_flags_data:
        master_df = pd.concat(all_flags_data, ignore_index=True)
        print(f"\n--- Extraction Complete! Total rows: {len(master_df)} ---")

        csv_path = os.path.join(EXPORTS_DIR, "complete_red_flags.csv")
        master_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"File saved to: {csv_path}")

        inst_col = "Institucioni Prokurues"
        if inst_col in master_df.columns:
            plt.figure(figsize=(10, 6))
            master_df[inst_col].value_counts().head(10).plot(
                kind="bar", color="#8b0000", edgecolor="black"
            )
            plt.title(
                "Top 10 Institucionet me Tenderë me Flamur të Kuq",
                fontsize=14,
                fontweight="bold",
            )
            plt.ylabel("Numri i Tenderëve", fontsize=12)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(os.path.join(EXPORTS_DIR, "top_institutions.png"))
            print("Chart saved.")
    else:
        print("\nExtraction failed. No files were saved.")


if __name__ == "__main__":
    main()
