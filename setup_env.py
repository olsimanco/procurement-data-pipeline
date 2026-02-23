import sys
import subprocess
import os


def install_dependencies():
    """
    Checks for requirements.txt and installs missing packages via pip.
    """
    req_file = "requirements.txt"

    # Check if the requirements file exists in the directory
    if not os.path.exists(req_file):
        print(f"Error: '{req_file}' not found in the current directory.")
        print("Please ensure it exists before running the setup.")
        sys.exit(1)

    print(f"Reading '{req_file}' and checking local environment...")

    try:
        # This securely executes: python -m pip install -r requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("\nSuccess! All required libraries are installed and ready to go.")

    except subprocess.CalledProcessError as e:
        print(f"\nInstallation failed. Error details: {e}")
        sys.exit(1)


def build_directory_structure():
    """
    Creates necessary folders for the project so the scraper
    doesn't fail when trying to save outputs.
    """
    folders = ["data", "exports", "logs"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print("Project directory structure verified.")


if __name__ == "__main__":
    print("--- Initializing Procurement Scraper Environment ---")
    install_dependencies()
    build_directory_structure()
    print("--- Setup Complete ---")
