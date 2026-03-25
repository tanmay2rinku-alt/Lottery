"""
PROJECT TITAN - Supabase Database Integration

Replaces local SQLite with cloud-based Supabase PostgreSQL.
Data ingestion handled by Supabase triggers (already configured).
This module reads from Supabase for analytics.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️  Install supabase: pip install supabase")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TITAN] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LotteryDatabaseSupabase:
    """
    Supabase PostgreSQL database manager for lottery data.
    Reads from cloud database where scraper/triggers push data.
    No need for local SQLite - data lives in Supabase.
    """

    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Initialize Supabase connection.

        Args:
            supabase_url: Supabase project URL (from environment or config)
            supabase_key: Supabase API key (from environment or config)

        Example:
            db = LotteryDatabaseSupabase(
                supabase_url="https://your-project.supabase.co",
                supabase_key="your-anon-key"
            )
        """
        try:
            self.client: Client = create_client(supabase_url, supabase_key)
            self.supabase_url = supabase_url
            self.supabase_key = supabase_key
            logger.info("[DB] Supabase connection established")
            logger.info(f"[DB] Project URL: {supabase_url}")
            
            # Verify connection
            response = self.client.table("winning_numbers").select("*").limit(1).execute()
            logger.info("[DB] Connection verified - 'winning_numbers' table accessible")
            
        except Exception as e:
            logger.error(f"[DB] Failed to connect to Supabase: {e}")
            raise

    def get_recent_draws(self, days_back: int = 30) -> pd.DataFrame:
        """
        Fetch recent lottery draws from Supabase.

        Args:
            days_back: Number of days to retrieve (default: 30)

        Returns:
            DataFrame with columns: date, time_slot, full_number, etc.
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            response = self.client.table("winning_numbers")\
                .select("*")\
                .gte("created_at", cutoff_date)\
                .order("created_at", desc=False)\
                .execute()
            
            if not response.data:
                logger.warning(f"[DB] No draws found in last {days_back} days")
                return pd.DataFrame()
            
            df = pd.DataFrame(response.data)
            logger.info(f"[DB] Retrieved {len(df)} draws from Supabase")
            return df
            
        except Exception as e:
            logger.error(f"[DB] Error fetching recent draws: {e}")
            return pd.DataFrame()

    def get_all_draws(self) -> pd.DataFrame:
        """
        Fetch all historical lottery draws from Supabase.

        Returns:
            DataFrame with all available draws
        """
        try:
            # Use pagination for large datasets
            all_data = []
            page = 0
            page_size = 1000
            
            while True:
                response = self.client.table("winning_numbers")\
                    .select("*")\
                    .range(page * page_size, (page + 1) * page_size - 1)\
                    .order("created_at", desc=False)\
                    .execute()
                
                if not response.data:
                    break
                
                all_data.extend(response.data)
                page += 1
            
            df = pd.DataFrame(all_data)
            logger.info(f"[DB] Retrieved {len(df)} total draws from Supabase")
            return df
            
        except Exception as e:
            logger.error(f"[DB] Error fetching all draws: {e}")
            return pd.DataFrame()

    def get_draws_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch draws within a specific date range.

        Args:
            start_date: ISO format date string (YYYY-MM-DD)
            end_date: ISO format date string (YYYY-MM-DD)

        Returns:
            DataFrame with draws in specified range
        """
        try:
            response = self.client.table("winning_numbers")\
                .select("*")\
                .gte("date", start_date)\
                .lte("date", end_date)\
                .order("date", desc=False)\
                .execute()
            
            if not response.data:
                logger.info(f"[DB] No draws found between {start_date} and {end_date}")
                return pd.DataFrame()
            
            df = pd.DataFrame(response.data)
            logger.info(f"[DB] Retrieved {len(df)} draws between {start_date} and {end_date}")
            return df
            
        except Exception as e:
            logger.error(f"[DB] Error fetching draws by date range: {e}")
            return pd.DataFrame()

    def save_prediction(self, prediction_data: Dict) -> bool:
        """
        Save TITAN prediction results to Supabase.

        Args:
            prediction_data: Dictionary with prediction results
                {
                    'timestamp': '2026-03-24T20:59:00',
                    'top_5_numbers': [45678, 56789, ...],
                    'series': '45',
                    'accuracy_score': 52.3,
                    'confidence_flag': 'Medium Confidence',
                    'model_version': 'v1_rf_100'
                }

        Returns:
            True if successful, False otherwise
        """
        try:
            # Insert into predictions table
            response = self.client.table("titan_predictions")\
                .insert({
                    "timestamp": prediction_data.get("timestamp"),
                    "top_5_numbers": prediction_data.get("top_5_numbers"),
                    "predicted_series": prediction_data.get("series"),
                    "accuracy_score": prediction_data.get("accuracy_score"),
                    "confidence_flag": prediction_data.get("confidence_flag"),
                    "model_version": prediction_data.get("model_version"),
                    "created_at": datetime.now().isoformat()
                })\
                .execute()
            
            logger.info(f"[DB] Prediction saved to Supabase: {prediction_data['timestamp']}")
            return True
            
        except Exception as e:
            logger.error(f"[DB] Error saving prediction: {e}")
            return False

    def get_series_history(self, series: str, limit: int = 10) -> pd.DataFrame:
        """
        Get historical draws for a specific series.

        Args:
            series: Series code (e.g., '45')
            limit: Maximum number of records to return

        Returns:
            DataFrame with series history
        """
        try:
            response = self.client.table("winning_numbers")\
                .select("*")\
                .ilike("full_number", f"{series}%")\
                .order("date", desc=True)\
                .limit(limit)\
                .execute()
            
            if not response.data:
                logger.info(f"[DB] No previous wins found for series {series}")
                return pd.DataFrame()
            
            df = pd.DataFrame(response.data)
            logger.info(f"[DB] Retrieved {len(df)} historical records for series {series}")
            return df
            
        except Exception as e:
            logger.error(f"[DB] Error fetching series history: {e}")
            return pd.DataFrame()

    def check_duplicate(self, date: str, time_slot: str, number: int) -> bool:
        """
        Check if a draw already exists (avoid duplicates).

        Args:
            date: Draw date
            time_slot: Time slot (1PM, 6PM, 8PM)
            number: 5-digit number

        Returns:
            True if exists, False if new
        """
        try:
            response = self.client.table("winning_numbers")\
                .select("id")\
                .eq("date", date)\
                .eq("time_slot", time_slot)\
                .eq("full_number", number)\
                .execute()
            
            exists = len(response.data) > 0
            if exists:
                logger.info(f"[DB] Duplicate found: {date} {time_slot} {number}")
            return exists
            
        except Exception as e:
            logger.error(f"[DB] Error checking duplicate: {e}")
            return False

    def get_latest_draw(self) -> Dict:
        """
        Get the most recent lottery draw.

        Returns:
            Dictionary with latest draw info
        """
        try:
            response = self.client.table("winning_numbers")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()
            
            if not response.data:
                logger.warning("[DB] No draws found in database")
                return {}
            
            draw = response.data[0]
            logger.info(f"[DB] Latest draw: {draw['date']} {draw['time_slot']} - {draw['full_number']}")
            return draw
            
        except Exception as e:
            logger.error(f"[DB] Error fetching latest draw: {e}")
            return {}

    def get_draw_count(self) -> int:
        """
        Get total number of draws in database.

        Returns:
            Number of draws
        """
        try:
            response = self.client.table("winning_numbers")\
                .select("id", count="exact")\
                .execute()
            
            count = response.count if hasattr(response, 'count') else 0
            logger.info(f"[DB] Total draws in database: {count}")
            return count
            
        except Exception as e:
            logger.error(f"[DB] Error getting draw count: {e}")
            return 0

    def close(self):
        """Close database connection (Supabase doesn't require this, but for compatibility)"""
        logger.info("[DB] Supabase connection still active (no close needed)")
        pass


# ============================================================================
# CLOUD ML INTEGRATION NOTES
# ============================================================================
"""
For running ML pipelines on cloud with Supabase:

OPTION 1: Supabase Edge Functions (Recommended - Easiest)
├── PROS:
│   ├── Free tier available
│   ├── No server management
│   ├── Scales automatically
│   ├── Direct database access
│   └── Fast cold start (~100ms)
│
├── CONS:
│   ├── Edge Functions run Deno (TypeScript/JavaScript)
│   ├── scikit-learn is Python-only
│   ├── Would need TensorFlow.js or similar
│   └── Less powerful ML libraries than Python
│
└── IMPLEMENTATION:
    - Rewrite ML engine in TypeScript (TensorFlow.js for basic ensemble)
    - Deploy as Supabase Edge Function
    - Trigger automatically on new draw via Postgres trigger
    - Returns predictions directly to Supabase

SAMPLE EDGE FUNCTION STRUCTURE:
├── supabase/functions/titan-predict/
│   ├── index.ts (main ML prediction code)
│   └── deno.json (dependencies)
└── Deploy with: supabase functions deploy


OPTION 2: AWS Lambda + Supabase (More Powerful)
├── PROS:
│   ├── Full Python support
│   ├── scikit-learn, XGBoost, all libraries work
│   ├── Can run 15 min / execution
│   └── More control
│
├── CONS:
│   ├── Requires AWS account + setup
│   ├── Cold start ~5-10 seconds
│   ├── Pay per invocation
│   └── More infrastructure complexity
│
└── IMPLEMENTATION:
    - Convert ml_engine.py to Lambda handler
    - Lambda reads from Supabase
    - Stores predictions back in Supabase
    - Trigger via Supabase webhook


OPTION 3: Google Cloud Run (Balanced)
├── PROS & CONS: Between Edge Functions and Lambda
└── IMPLEMENTATION: Similar to Lambda


OPTION 4: Keep ML Local (Simplest for Now)
├── PROS:
│   ├── No refactoring needed
│   ├── Full scikit-learn support
│   ├── Complete control
│   └── Easiest to debug
│
├── CONS:
│   ├── Need to run local script regularly
│   ├── Must keep machine on for scheduler
│   └── No cloud benefits
│
└── IMPLEMENTATION:
    - Use this module to read from Supabase
    - Keep all 8 pipelines running locally
    - Push results back to Supabase


RECOMMENDATION FOR YOUR SETUP:
────────────────────────────────
Since you already have Supabase with automated scraping/triggers:

PHASE 1 (NOW - Simplest):
├── Data: Supabase (✓ already has scraper/triggers)
├── Analytics: Local Python TITAN (read from Supabase)
├── Scheduler: Windows Task Scheduler or cron
└── Results: Push back to Supabase/Google Sheets

PHASE 2 (OPTIONAL - More Cloud-Native):
├── Convert ml_engine.py to Supabase Edge Function
├── Auto-trigger on new draw via Postgres trigger
├── Zero local infrastructure needed
└── Requires TypeScript rewrite (1-2 hours)

PHASE 3 (ADVANCED - Hybrid):
├── Deploy Python ML to AWS Lambda or Cloud Run
├── Supabase triggers Lambda on new draw
├── Full Python + scikit-learn support
├── Serverless = pay only when ML runs
└── Most powerful and scalable option
"""
