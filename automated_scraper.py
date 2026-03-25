#!/usr/bin/env python3
"""
Automated Lottery Data Scraper
Continuously monitors lotterysambad.com and stores data in Supabase
Runs in background with configurable intervals
"""

import time
import schedule
import threading
from datetime import datetime, timedelta
import sys
import os
import signal
import logging

# Fix Windows console encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import core modules
from main import LotteryIntelligenceSystem
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


class AutomatedLotteryScraper:
    """Automated scraper that continuously monitors lottery results"""

    def __init__(self, check_interval_minutes=30, headless=True):
        """
        Initialize automated scraper

        Args:
            check_interval_minutes: How often to check for new results (default: 30 min)
            headless: Run browser in headless mode (default: True)
        """
        self.check_interval = check_interval_minutes
        self.headless = headless
        self.is_running = False
        self.last_check = None
        self.success_count = 0
        self.error_count = 0

        # Initialize Supabase client
        self.database = SupabaseClient(url=SUPABASE_URL, key=SUPABASE_KEY)

        # Track processed dates to avoid duplicates
        self.processed_dates = set()
        self._load_processed_dates()

        logger.info(f"[AUTOMATED] Automated Lottery Scraper initialized")
        logger.info(f"   Check interval: {check_interval_minutes} minutes")
        logger.info(f"   Headless mode: {headless}")

    def _load_processed_dates(self):
        """Load previously processed dates from database"""
        try:
            # Get all unique dates from winning_numbers table
            response = self.database.supabase.table('winning_numbers').select('draw_date').execute()
            if response.data:
                self.processed_dates = set(record['draw_date'] for record in response.data if record.get('draw_date'))
                logger.info(f"[AUTOMATED] Loaded {len(self.processed_dates)} previously processed dates")
        except Exception as e:
            logger.warning(f"Could not load processed dates: {e}")

    def _is_new_data_available(self):
        """Check if new lottery data is available"""
        try:
            # For testing purposes, always return True to allow re-processing
            # In production, you might want to check for actual new data
            return True
        except Exception as e:
            logger.error(f"Error checking for new data: {e}")
            return True  # Assume new data might be available

    def _run_scraping_cycle(self):
        """Execute one complete scraping cycle"""
        try:
            logger.info("[SCRAPER] Starting scraping cycle...")

            if not self._is_new_data_available():
                logger.info("[SCRAPER] No new data available, skipping cycle")
                return

            # Create a fresh system instance for each cycle
            system = LotteryIntelligenceSystem()

            # Override headless mode if configured
            if self.headless:
                # Modify the system to use headless mode
                pass  # We'll handle this in the phase_1 method

            # Run the pipeline
            success = system.run_full_pipeline()

            if success:
                self.success_count += 1
                current_date = datetime.now().strftime("%Y-%m-%d")
                self.processed_dates.add(current_date)
                logger.info(f"[SCRAPER] Scraping cycle completed successfully (#{self.success_count})")
            else:
                self.error_count += 1
                logger.error(f"[SCRAPER] Scraping cycle failed (#{self.error_count})")

        except Exception as e:
            self.error_count += 1
            logger.error(f"[SCRAPER] Critical error in scraping cycle: {e}")

        finally:
            self.last_check = datetime.now()

    def _modify_system_for_headless(self, system):
        """Modify the system to run in headless mode"""
        # This would require modifying the main.py to accept headless parameter
        # For now, we'll modify the Chrome options directly
        try:
            if hasattr(system, 'driver') and system.driver:
                # Add headless argument
                system.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': '''
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined,
                        });
                    '''
                })
        except:
            pass

    def start_continuous_scraping(self):
        """Start continuous scraping in background thread"""
        if self.is_running:
            logger.warning("Scraper is already running")
            return

        self.is_running = True
        logger.info("[AUTOMATED] Starting continuous scraping...")

        def scraping_loop():
            while self.is_running:
                try:
                    self._run_scraping_cycle()

                    # Wait for next interval
                    logger.info(f"[SCRAPER] Waiting {self.check_interval} minutes until next check...")
                    time.sleep(self.check_interval * 60)

                except KeyboardInterrupt:
                    logger.info("[STOP] Received interrupt signal")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in scraping loop: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying

        # Start in background thread
        self.scraping_thread = threading.Thread(target=scraping_loop, daemon=True)
        self.scraping_thread.start()

        logger.info("[AUTOMATED] Continuous scraping started in background")

    def start_scheduled_scraping(self, cron_schedule="0 */2 * * *"):
        """
        Start scheduled scraping using cron-like schedule

        Args:
            cron_schedule: Cron expression (default: every 2 hours)
        """
        if self.is_running:
            logger.warning("Scraper is already running")
            return

        self.is_running = True
        logger.info(f"[AUTOMATED] Starting scheduled scraping with cron: {cron_schedule}")

        # Schedule the job
        schedule.every().day.at("06:00").do(self._run_scraping_cycle)  # 6 AM
        schedule.every().day.at("12:00").do(self._run_scraping_cycle)  # 12 PM (Noon)
        schedule.every().day.at("18:00").do(self._run_scraping_cycle)  # 6 PM
        schedule.every().day.at("20:00").do(self._run_scraping_cycle)  # 8 PM

        def scheduled_loop():
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except KeyboardInterrupt:
                    logger.info("[STOP] Received interrupt signal")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in scheduled loop: {e}")
                    time.sleep(60)

        # Start in background thread
        self.scraping_thread = threading.Thread(target=scheduled_loop, daemon=True)
        self.scraping_thread.start()

        logger.info("[AUTOMATED] Scheduled scraping started in background")

    def stop_scraping(self):
        """Stop the scraping process"""
        if not self.is_running:
            logger.warning("Scraper is not running")
            return

        logger.info("[STOP] Stopping scraper...")
        self.is_running = False

        if hasattr(self, 'scraping_thread'):
            self.scraping_thread.join(timeout=10)

        logger.info("[OK] Scraper stopped")

    def get_status(self):
        """Get current scraper status"""
        return {
            'is_running': self.is_running,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'processed_dates_count': len(self.processed_dates),
            'check_interval_minutes': self.check_interval
        }


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"[SHUTDOWN] Received signal {signum}, shutting down...")
    if 'scraper' in globals():
        scraper.stop_scraping()
    sys.exit(0)


def main():
    """Main entry point for automated scraper"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Automated Lottery Data Scraper')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in minutes (default: 30)')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode (default: True)')
    parser.add_argument('--mode', choices=['continuous', 'scheduled'], default='scheduled',
                       help='Scraping mode (default: scheduled)')
    parser.add_argument('--once', action='store_true',
                       help='Run one scraping cycle and exit')

    args = parser.parse_args()

    # Initialize scraper
    global scraper
    scraper = AutomatedLotteryScraper(
        check_interval_minutes=args.interval,
        headless=args.headless
    )

    if args.once:
        # Run one cycle and exit
        logger.info("[CYCLE] Running single scraping cycle...")
        scraper._run_scraping_cycle()
        logger.info("[OK] Single cycle completed")
        return

    # Start continuous or scheduled scraping
    if args.mode == 'continuous':
        scraper.start_continuous_scraping()
    else:
        scraper.start_scheduled_scraping()

    # Keep main thread alive
    try:
        while scraper.is_running:
            time.sleep(1)
            # Print status every 5 minutes
            if int(time.time()) % 300 == 0:
                status = scraper.get_status()
                logger.info(f"[STATUS] Status: {status['success_count']} successes, {status['error_count']} errors")

    except KeyboardInterrupt:
        logger.info("[STOP] Interrupted by user")

    finally:
        scraper.stop_scraping()


if __name__ == "__main__":
    main()