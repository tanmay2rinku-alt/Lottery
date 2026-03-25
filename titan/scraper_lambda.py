#!/usr/bin/env python3
"""
AWS Lambda Handler for Automated Lottery Scraper
Runs the full scraping pipeline in serverless environment
"""

import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core modules
try:
    from main import LotteryIntelligenceSystem
    from config import SUPABASE_URL, SUPABASE_KEY
    from supabase_client import SupabaseClient
    logger.info("✓ Core modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for automated lottery scraping.

    Args:
        event: Lambda event (can be from CloudWatch, API Gateway, etc.)
        context: Lambda context

    Returns:
        HTTP response with scraping results
    """

    logger.info("="*70)
    logger.info("🎯 LOTTERY SCRAPER - AWS LAMBDA HANDLER")
    logger.info("="*70)

    start_time = datetime.now()

    try:
        # Log event details
        logger.info(f"📨 Event: {json.dumps(event, default=str)[:500]}")

        # Initialize Supabase client
        logger.info("🔌 Connecting to Supabase...")
        database = SupabaseClient(
            url=os.environ.get('SUPABASE_URL', SUPABASE_URL),
            key=os.environ.get('SUPABASE_KEY', SUPABASE_KEY)
        )

        # Create system instance with headless mode for Lambda
        logger.info("🏗️ Initializing Lottery Intelligence System...")
        system = LotteryIntelligenceSystem(headless=True)

        # Override database client
        system.database = database

        # Run full pipeline
        logger.info("🚀 Starting full scraping pipeline...")
        success = system.run_full_pipeline()

        if success:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Pipeline completed successfully in {execution_time:.1f}s")

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'status': 'SUCCESS',
                    'message': 'Lottery scraping pipeline completed',
                    'execution_time_seconds': execution_time,
                    'timestamp': start_time.isoformat()
                })
            }
        else:
            logger.error("❌ Pipeline failed")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'status': 'FAILED',
                    'message': 'Lottery scraping pipeline failed',
                    'timestamp': start_time.isoformat()
                })
            }

    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"💥 Critical error: {str(e)}")
        logger.error("Full traceback:", exc_info=True)

        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'ERROR',
                'message': f'Critical error: {str(e)}',
                'execution_time_seconds': execution_time,
                'timestamp': start_time.isoformat()
            })
        }


# For local testing
if __name__ == "__main__":
    # Mock event and context for testing
    mock_event = {
        "source": "aws.events",
        "detail-type": "Scheduled Event",
        "detail": {}
    }

    mock_context = type('MockContext', (), {
        'aws_request_id': 'test-request-id',
        'function_name': 'lottery-scraper-lambda',
        'memory_limit_in_mb': '3008'
    })()

    result = lambda_handler(mock_event, mock_context)
    print("Lambda result:", json.dumps(result, indent=2))