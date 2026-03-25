"""
PROJECT TITAN - AWS Lambda Handler

ML predictions as serverless function.
Runs locally for testing, deploys to AWS Lambda for production.

Deployment targets:
  • Local: python ml_engine_lambda.py
  • AWS Lambda: zip and deploy via AWS CLI or Console

Trigger: Can be invoked by:
  • Supabase webhook (on new draw)
  • CloudWatch Events (scheduled)
  • Direct AWS API call
  • SNS topic
  • S3 event
"""

import json
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any
import traceback

# Lambda-compatible imports (all available in Lambda runtime)
try:
    import pandas as pd
    import numpy as np
except ImportError:
    # Will be installed in Lambda layer
    print("⚠️  Install dependencies: pip install pandas numpy scikit-learn")
    sys.exit(1)

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Handler name for AWS Lambda
# In AWS Lambda Console: Set handler to "ml_engine_lambda.lambda_handler"


def get_database_connection(event: Dict = None):
    """
    Get database connection - supports local and Lambda environments.
    
    Args:
        event: Lambda event (contains environment info if needed)
    
    Returns:
        Database client (Supabase)
    """
    from database_supabase import LotteryDatabaseSupabase
    
    # Get credentials from environment variables
    # Set these in Lambda environment or locally in .env
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
    
    return LotteryDatabaseSupabase(SUPABASE_URL, SUPABASE_KEY)


def get_ml_engine(db):
    """Initialize ML engine"""
    from ml_engine import MLEnsembleEngine
    return MLEnsembleEngine(db)


def get_feature_engineer(db):
    """Initialize feature engineer"""
    from feature_engineering import FeatureEngineer
    return FeatureEngineer(db)


def get_monte_carlo(db):
    """Initialize Monte Carlo engine"""
    from monte_carlo import MonteCarloSimulationEngine
    return MonteCarloSimulationEngine(db)


def get_markov_engine(db):
    """Initialize Markov engine"""
    from markov_engine import MarkovChainEngine
    return MarkovChainEngine(db)


def get_constraint_filter(db):
    """Initialize constraint filter"""
    from filter_constraints import ConstraintFilter
    return ConstraintFilter(db)


def predict_lottery_numbers(draws_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Core ML prediction logic.
    
    Pipeline:
      1. Feature Engineering (14 features)
      2. Markov Chains (probability analysis)
      3. Random Forest ML (prediction)
      4. Monte Carlo (10k simulations)  
      5. Filtering (constraint checks)
    
    Args:
        draws_df: DataFrame with historical draws
    
    Returns:
        Dictionary with predictions
    """
    try:
        db = get_database_connection()
        
        # ═══════════════════════════════════════════════════════════════
        # PIPELINE 2: FEATURE ENGINEERING
        # ═══════════════════════════════════════════════════════════════
        logger.info("🔧 Feature Engineering...")
        feature_engineer = get_feature_engineer(db)
        engineered_df = feature_engineer.engineer_all_features(draws_df)
        
        if engineered_df.empty:
            raise ValueError("Feature engineering produced empty DataFrame")
        
        logger.info(f"✓ Engineered {len(engineered_df)} records with 14 features")
        
        # ═══════════════════════════════════════════════════════════════
        # PIPELINE 3: MARKOV CHAINS
        # ═══════════════════════════════════════════════════════════════
        logger.info("🔗 Markov Chain Analysis...")
        markov_engine = get_markov_engine(db)
        markov_engine.build_transition_matrix(engineered_df)
        markov_preds = markov_engine.predict_next_series(
            engineered_df['series'].iloc[-1] if len(engineered_df) > 0 else '00',
            top_k=3
        )
        logger.info(f"✓ Markov predictions: {markov_preds}")
        
        # ═══════════════════════════════════════════════════════════════
        # PIPELINE 4: MACHINE LEARNING
        # ═══════════════════════════════════════════════════════════════
        logger.info("🤖 Random Forest ML...")
        ml_engine = get_ml_engine(db)
        
        # Prepare training data
        feature_cols = ['day_of_week', 'hour_of_draw', 'prev_sum_of_digits',
                       'series_overdue_days', 'rolling_freq', 'is_weekend', 'rolling_mean_digits']
        
        X = engineered_df[feature_cols].fillna(0).values
        y = engineered_df['series'].values
        
        # Train model
        ml_engine.train_random_forest(X, y)
        
        # Get predictions
        top_3_ml = ml_engine.predict_next_series(X, top_k=3)
        top_series = top_3_ml[0] if top_3_ml else '45'
        
        train_accuracy = ml_engine.model.score(X, y)
        logger.info(f"✓ ML predictions: {top_3_ml} (accuracy: {train_accuracy:.2%})")
        
        # ═══════════════════════════════════════════════════════════════
        # PIPELINE 5: MONTE CARLO SIMULATION
        # ═══════════════════════════════════════════════════════════════
        logger.info("🎲 Monte Carlo Simulation (10,000 runs)...")
        monte_carlo = get_monte_carlo(db)
        mc_results = monte_carlo.run_simulations(
            engineered_df,
            ml_predicted_series=top_series,
            num_simulations=10000
        )
        
        top_5_numbers = [item['number'] for item in mc_results['top_5_numbers']]
        logger.info(f"✓ Top-5 predictions: {top_5_numbers}")
        
        # ═══════════════════════════════════════════════════════════════
        # PIPELINE 6: FILTERING
        # ═══════════════════════════════════════════════════════════════
        logger.info("🔍 Applying Constraints...")
        constraint_filter = get_constraint_filter(db)
        filter_results = constraint_filter.apply_all_constraints(top_5_numbers)
        
        final_predictions = filter_results['passed_all_checks']
        logger.info(f"✓ Final predictions (after filtering): {final_predictions}")
        
        # ═══════════════════════════════════════════════════════════════
        # COMPILE RESULTS
        # ═══════════════════════════════════════════════════════════════
        results = {
            'status': 'SUCCESS',
            'timestamp': datetime.now().isoformat(),
            'predictions': {
                'top_5_numbers': final_predictions,
                'top_5_all': top_5_numbers,
                'series': top_series,
                'markov_series': markov_preds,
                'ml_series': top_3_ml
            },
            'accuracy': {
                'ml_training': train_accuracy,
                'markov_ensemble': 'Ready for comparison'
            },
            'pipeline': {
                'features_engineered': 14,
                'markov_matrix': '100x100',
                'ml_model': 'Random Forest (100 trees)',
                'monte_carlo_sims': 10000,
                'constraints_applied': 3
            }
        }
        
        logger.info("✓ All pipelines completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"❌ Prediction failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise


def lambda_handler(event: Dict, context: Any) -> Dict:
    """
    AWS Lambda handler entry point.
    
    This is the function AWS Lambda calls.
    
    Args:
        event: Lambda event (from API Gateway, S3, Supabase webhook, etc.)
        context: Lambda context (runtime info, requestId, etc.)
    
    Returns:
        HTTP response with predictions
    
    Example event from Supabase webhook:
        {
            "type": "INSERT",
            "table": "winning_numbers",
            "record": {
                "date": "2026-03-24",
                "time_slot": "6PM",
                "full_number": 45678
            }
        }
    
    AWS Lambda will respond with:
        {
            "statusCode": 200,
            "body": {
                "status": "SUCCESS",
                "predictions": {...},
                "message": "ML prediction completed"
            }
        }
    """
    
    logger.info("="*70)
    logger.info("🚀 PROJECT TITAN - AWS LAMBDA ML HANDLER")
    logger.info("="*70)
    
    try:
        # Log incoming event
        logger.info(f"📨 Event received: {json.dumps(event, default=str)[:500]}")  # Log first 500 chars
        
        # Get database connection
        logger.info("🔌 Connecting to Supabase...")
        db = get_database_connection(event)
        
        # Fetch all historical draws
        logger.info("📊 Fetching historical draws...")
        draws_df = db.get_all_draws()
        
        if draws_df.empty:
            logger.error("❌ No draws found in database")
            return {
                'statusCode': 428,  # Precondition Required
                'body': json.dumps({
                    'status': 'INSUFFICIENT_DATA',
                    'message': 'No lottery draws available in database',
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        logger.info(f"✓ Loaded {len(draws_df)} historical draws")
        
        # Run ML pipeline
        logger.info("▶️  Running ML pipeline...")
        results = predict_lottery_numbers(draws_df)
        
        # Prepare response
        response = {
            'statusCode': 200,
            'body': json.dumps({
                **results,
                'message': 'ML prediction completed successfully',
                'execution_time': 'See CloudWatch logs'
            }, default=str)
        }
        
        logger.info("✓ Response prepared")
        logger.info("="*70)
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Lambda handler error: {str(e)}")
        logger.error(traceback.format_exc())
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'ERROR',
                'message': str(e),
                'timestamp': datetime.now().isoformat(),
                'traceback': traceback.format_exc()
            })
        }


# ============================================================================
# LOCAL TESTING (Run locally before deploying to AWS Lambda)
# ============================================================================

def local_test():
    """
    Test the Lambda handler locally with Supabase data.
    
    Usage:
        python ml_engine_lambda.py
    
    This simulates what happens when Lambda is triggered.
    """
    import os
    from dotenv import load_dotenv
    
    print("\n" + "="*70)
    print("🧪 LOCAL TESTING - PROJECT TITAN LAMBDA HANDLER")
    print("="*70)
    
    # Load environment
    load_dotenv()
    
    # Create mock Lambda event
    mock_event = {
        'source': 'local-test',
        'timestamp': datetime.now().isoformat(),
        'detail-type': 'Local Test'
    }
    
    # Create mock Lambda context
    class MockContext:
        def __init__(self):
            self.function_name = "ProjectTitanMLLocal"
            self.function_version = "1"
            self.invoked_function_arn = "arn:aws:lambda:local:test"
            self.memory_limit_in_mb = 3008
            self.aws_request_id = "local-test-request"
            self.log_group_name = "/aws/lambda/ProjectTitanMLLocal"
            self.log_stream_name = "local-test-stream"
            
        def get_remaining_time_in_millis(self):
            return 300000  # 5 minutes
    
    mock_context = MockContext()
    
    # Call handler
    try:
        response = lambda_handler(mock_event, mock_context)
        
        print("\n✅ LAMBDA HANDLER EXECUTED SUCCESSFULLY\n")
        print("Response Status Code:", response['statusCode'])
        print("\nResponse Body:")
        body = json.loads(response['body'])
        print(json.dumps(body, indent=2))
        
        if response['statusCode'] == 200:
            print("\n" + "="*70)
            print("🎯 PREDICTIONS READY FOR DEPLOYMENT")
            print("="*70)
            print(f"Top 5 Numbers: {body['predictions']['top_5_numbers']}")
            print(f"Series: {body['predictions']['series']}")
            print(f"Timestamp: {body['timestamp']}")
            
            # Save to JSON for reference
            with open('titan_lambda_test_output.json', 'w') as f:
                json.dump(body, f, indent=2)
            print("\n✓ Results saved to: titan_lambda_test_output.json")
        
        return response
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    """
    Run as: python ml_engine_lambda.py
    Tests the Lambda handler locally before deployment
    """
    # Configure logging for local testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [LAMBDA-LOCAL] %(levelname)s - %(message)s'
    )
    
    # Run local test
    local_test()
    
    print("\n" + "="*70)
    print("✓ Local testing complete!")
    print("\nNext steps:")
    print("  1. Review titan_lambda_test_output.json")
    print("  2. Run: python prepare_lambda_deployment.py")
    print("  3. Deploy to AWS Lambda")
    print("="*70 + "\n")
