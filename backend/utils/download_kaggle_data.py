import os
import kaggle
import pandas as pd

def download_mining_datasets():
    """
    Download mining datasets from Kaggle and save locally
    """
    # ✅ Make sure Kaggle credentials exist in environment
    if not os.getenv('KAGGLE_USERNAME') or not os.getenv('KAGGLE_KEY'):
        print("❌ Kaggle credentials missing! Please set them first.")
        print("Run this in your terminal:")
        print('setx KAGGLE_USERNAME "your_kaggle_username"')
        print('setx KAGGLE_KEY "your_kaggle_api_key"')
        return
    
    # ✅ Choose realistic mining-related datasets
    datasets = [
        "samithsachidanandan/gold-production",
    "tunguz/gold-prices",
    "niravnaik/safety-helmet-and-reflective-jacket"
    ]

    output_dir = os.path.join(os.path.dirname(__file__), "../data/kaggle_data")
    os.makedirs(output_dir, exist_ok=True)
    
    for dataset in datasets:
        try:
            print(f"📥 Downloading {dataset} ...")
            kaggle.api.dataset_download_files(dataset, path=output_dir, unzip=True)
            print(f"✅ Downloaded and unzipped: {dataset}")
        except Exception as e:
            print(f"⚠️ Failed to download {dataset}: {e}")

if __name__ == "__main__":
    download_mining_datasets()
