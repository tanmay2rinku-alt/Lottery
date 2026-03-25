"""
Full-Stack Lottery Intelligence: Orchestrator
Production-ready 6-pipeline system for Nagaland Dear Lottery.
"""

import os
import sys
import time
from datetime import datetime
import pandas as pd
from typing import List

# Import Pipelines
from main import LotteryIntelligenceSystem # Phase 1, 2, 3 logic
from frequency_engine import FrequencyEngine # Pipeline 3
from cluster_analyzer import ClusterAnalyzer # Pipeline 4
from university_math import UniversityMathEngine # Pipeline 5
from sentiment_scraper import SentimentScraper # Pipeline 6
from smart_notifications import SmartNotifier   
from supabase_client import SupabaseClient      
from config import SUPABASE_URL, SUPABASE_KEY

class IntelligenceOrchestrator:
    def __init__(self):
        print("[ORCHESTRATOR] Initializing 6-Pipeline System...")
        self.core = LotteryIntelligenceSystem(headless=True)
        self.db = SupabaseClient(url=SUPABASE_URL, key=SUPABASE_KEY)
        self.notifier = SmartNotifier()
        self.scraper = SentimentScraper()

    def run_all_pipelines(self):
        print("\n" + "#"*60)
        print("# EXECUTING 6-PIPELINE LOTTERY INTELLIGENCE")
        print("# Started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("#"*60)

        # PIPE 1 & 2: Ingestion & Storage
        print("\n[P1/P2] Ingesting Data and Syncing to Cloud...")
        if not self.core.phase_1_stealth_scraper(): 
            print("[ERROR] Pipe 1 failed (Scraper)")
            return
        if not self.core.phase_2_intelligence_parser():
            print("[ERROR] Pipe 2 failed (Parser)")
            return
        
        current_numbers = self.core.winning_numbers
        draw_time = self.core._extract_draw_time()
        self.core.phase_3_cloud_sync() 

        # Get historical data for analysis
        try:
            history = self.db.supabase.table('winning_numbers').select('*').execute().data
            df_history = pd.DataFrame(history)
        except Exception as e:
            print(f"[ERROR] Database access failed: {e}")
            df_history = pd.DataFrame()

        if df_history.empty:
            print("[WARN] No historical data. Skipping advanced analytic pipes.")
        else:
            # PIPE 3: Frequency Engine
            print("\n[P3] Running Frequency Heatmap Engine...")
            freq_eng = FrequencyEngine(df_history)
            heatmap = freq_eng.generate_heatmap_data()
            self.db.save_analysis_results("frequency_heatmap", {"heatmap": heatmap})

            # PIPE 4: Cluster Analysis
            print("\n[P4] Running Cluster & Neighbor Analysis...")
            cluster_eng = ClusterAnalyzer(df_history)
            clusters = cluster_eng.analyze_series_clusters()
            neighbors = cluster_eng.get_neighbor_patterns()
            self.db.save_analysis_results("cluster_analysis", {"clusters": clusters, "neighbors": neighbors})

            # PIPE 5: University Math Intelligence
            print("\n[P5] Running University-Grade Math Engine (MIT/Stanford standards)...")
            univ_math = UniversityMathEngine(df_history['number'].tolist())
            monte_carlo = univ_math.monte_carlo_simulation()
            poisson = univ_math.poisson_arrival_analysis()
            chi_squared = univ_math.chi_squared_test()
            
            self.db.save_analysis_results("university_math", {
                "monte_carlo": monte_carlo,
                "poisson": poisson,
                "chi_squared": chi_squared
            })

            # PIPE 6: Consensus Engine (Sentiment vs Math)
            print("\n[P6] Comparing Guru Sentiment vs University Math...")
            sentiment = self.scraper.scrape_youtube_predictions()
            
            # Add consensus logic
            math_picks = set(monte_carlo.get('top_simulated_picks', []))
            guru_picks = set()
            for nums in sentiment.get('guru_predictions', {}).values():
                guru_picks.update([int(n) for n in nums])
            
            consensus = list(math_picks.intersection(guru_picks))
            sentiment['math_consensus'] = consensus
            
            self.db.save_analysis_results("sentiment_trends", sentiment)

        # DELIVERY & NOTIFICATIONS
        print("\n[FINAL] Executing Notifications...")
        watchlist_data = self.db.supabase.table('watchlist').select('number').execute().data
        watchlist_numbers = [str(n['number']) for n in watchlist_data]
        self.notifier.add_to_watchlist(watchlist_numbers)
        self.notifier.check_results_and_notify(current_numbers, draw_time)
        
        print("\n" + "#"*60)
        print("# [SUCCESS] 6-PIPELINE EXECUTION COMPLETE")
        print("#"*60 + "\n")

if __name__ == "__main__":
    orchestrator = IntelligenceOrchestrator()
    orchestrator.run_all_pipelines()
