"""
Historical Data Populator
Ingests the last 15-20 days of winning numbers into Supabase.
"""

import time
from main import LotteryIntelligenceSystem
from orchestrator import IntelligenceOrchestrator

def populate_history(limit=10):
    print(f"[POPULATOR] Starting historical ingestion (Limit: {limit} PDFs)...")
    system = LotteryIntelligenceSystem(headless=True)
    orchestrator = IntelligenceOrchestrator()
    
    # We use the system's phase_1 with index to pull older results
    for i in range(limit):
        print(f"\n[POPULATOR] Working on PDF #{i}...")
        try:
            if system.phase_1_stealth_scraper(pdf_index=i):
                if system.phase_2_intelligence_parser():
                    # Sync to Supabase
                    system.phase_3_cloud_sync()
                    print(f"[POPULATOR] Successfully ingested PDF #{i}")
            
            # Small delay to avoid hammering the server
            time.sleep(5)
        except Exception as e:
            print(f"[POPULATOR] Failed on PDF #{i}: {e}")
            continue
    
    # After population, run one full analysis cycle to update P3, P4, P5
    print("\n[POPULATOR] Ingestion complete. Running full analysis cycle...")
    orchestrator.run_all_pipelines()

if __name__ == "__main__":
    populate_history(limit=15)
