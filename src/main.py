import os
import pandas as pd
import matplotlib.pyplot as plt

# Dynamically find the absolute path to the exports folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")


def scrape_tenders(url):
    """Placeholder function to hold the BeautifulSoup/Selenium logic."""
    print(f"Targeting: {url}")
    print("Fetching data...")

    # Simulated data reflecting Albanian procurement structures
    # (Replace this with actual scraping logic later)
    dummy_data = {
        "Tender Title": [
            "Rikonstruksion Rruge",
            "Blerje Medikamente",
            "Sherbime Konsulence",
        ],
        "Limit Fund": [15000000, 5000000, 1200000],
        "Winning Bid": [14800000, 4100000, 1190000],  # 1st and 3rd are >98%
        "Number of Bidders": [1, 3, 1],  # 1st and 3rd are single bidders
        "Winning Company": ["Kompani A", "Kompani B", "Kompani A"],
    }
    return pd.DataFrame(dummy_data)


def flag_suspicious_tenders(df):
    """Flags single-bidder contracts close to the limit fund."""
    print("Running red flag analysis...")
    condition = (df["Number of Bidders"] == 1) & (
        df["Winning Bid"] > 0.98 * df["Limit Fund"]
    )
    df["Suspicious"] = condition
    return df


def export_results(df):
    """Saves the CSV and generates the Matplotlib chart."""
    # 1. Save to CSV
    csv_path = os.path.join(EXPORTS_DIR, "red_flags.csv")
    df.to_csv(csv_path, index=False)
    print(f"Data exported to: {csv_path}")

    # 2. Generate Chart
    single_bidders = df[df["Number of Bidders"] == 1]
    top_companies = single_bidders["Winning Company"].value_counts().head(5)

    plt.figure(figsize=(8, 5))
    top_companies.plot(kind="bar", color="#d9534f", edgecolor="black")

    plt.title("Top Companies with Single-Bidder Contracts")
    plt.xlabel("Company")
    plt.ylabel("Contract Count")
    plt.xticks(rotation=0)
    plt.tight_layout()

    # Save the chart as an image
    chart_path = os.path.join(EXPORTS_DIR, "red_flags_chart.png")
    plt.savefig(chart_path)
    print(f"Chart exported to: {chart_path}")


if __name__ == "__main__":
    # Main execution flow
    target_url = "https://openprocurement.al/sq/tender/list"

    raw_data = scrape_tenders(target_url)
    analyzed_data = flag_suspicious_tenders(raw_data)
    export_results(analyzed_data)

    print("Process finished successfully!")
