"""
Fast Historical Ingest (No Scipy)
"""
from main import LotteryIntelligenceSystem
import time

def ingest():
    system = LotteryIntelligenceSystem(headless=True)
    # Get last 20 PDFs
    for i in range(20):
        print(f"Ingesting PDF index {i}")
        try:
            if system.phase_1_stealth_scraper(pdf_index=i):
                if system.phase_2_intelligence_parser():
                    system.phase_3_cloud_sync()
            time.sleep(2)
        except Exception as e:
            print(f"Error on {i}: {e}")
            continue

if __name__ == "__main__":
    ingest()
