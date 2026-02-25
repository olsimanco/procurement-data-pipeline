# src/main.py

# Import the specific functions from your other files
from phase1_scraper import run_phase1
from phase2_winners import run_phase2


def main():
    print("==================================================")
    print("  ALBANIAN PROCUREMENT RED FLAG PIPELINE STARTED")
    print("==================================================")

    # Run Phase 1: Download the summary tables
    print("\n>>> [PHASE 1] Extracting Base Red Flag Data...")
    run_phase1()

    # Run Phase 2: Hunt down the winning companies
    print("\n>>> [PHASE 2] Extracting Winning Companies...")
    run_phase2()

    print("\n==================================================")
    print("  PIPELINE COMPLETE! Check the 'exports' folder.")
    print("==================================================")


if __name__ == "__main__":
    main()
