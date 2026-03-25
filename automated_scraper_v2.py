#!/usr/bin/env python3
"""
IMPROVISED Automated Lottery Data Scraper
Integrated with 6-Pipeline Intelligence (University-Grade Math)
"""

import time
import schedule
import threading
from datetime import datetime
import sys
import os
import signal
import logging

# Fix Windows console encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import core modules
from orchestrator import IntelligenceOrchestrator
from config import SUPABASE_URL, SUPABASE_KEY
from supabase_client import SupabaseClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImprovisedScraper:
    def __init__(self, interval=30):
        self.interval = interval
        self.orchestrator = IntelligenceOrchestrator()
        self.is_running = False

    def _run_cycle(self):
        logger.info("[CYCLE] Starting 6-Pipeline Execution Cycle...")
        try:
            self.orchestrator.run_all_pipelines()
            logger.info("[SUCCESS] Intelligence Cycle completed.")
        except Exception as e:
            logger.error(f"[CRITICAL] Cycle failed: {e}")

    def start(self, mode='scheduled'):
        self.is_running = True
        logger.info(f"[START] Improvised Scraper active. Mode: {mode}")
        
        if mode == 'scheduled':
            # Nagaland Dear Lottery Draw Times
            schedule.every().day.at("13:15").do(self._run_cycle) # 1 PM Draw (check at 1:15)
            schedule.every().day.at("18:15").do(self._run_cycle) # 6 PM Draw
            schedule.every().day.at("20:15").do(self._run_cycle) # 8 PM Draw
            
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)
        else:
            # Continuous mode
            while self.is_running:
                self._run_cycle()
                logger.info(f"[WAIT] Sleeping for {self.interval} minutes...")
                time.sleep(self.interval * 60)

if __name__ == "__main__":
    scraper = ImprovisedScraper(interval=30)
    # Check if run with --once
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        scraper._run_cycle()
    else:
        scraper.start(mode='scheduled')
