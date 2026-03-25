"""
PROJECT TITAN - Pipeline 7: Automated Backtesting System

Tests ML model on historical data.
Generates Accuracy_Confidence_Score (0-100%).
Flags low confidence predictions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
import logging

from database import LotteryDatabase
from ml_engine import MLEnsembleEngine
from feature_engineering import FeatureEngineer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TITAN] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BacktestingSystem:
    """
    Automated backtesting and validation system.
    Evaluates model performance on historical data.
    """

    def __init__(self, database: LotteryDatabase = None, ml_engine: MLEnsembleEngine = None):
        """
        Initialize backtesting system.

        Args:
            database: LotteryDatabase instance
            ml_engine: MLEnsembleEngine instance
        """
        self.database = database or LotteryDatabase()
        self.ml_engine = ml_engine or MLEnsembleEngine(database)
        logger.info("[BACKTEST] Backtesting System initialized")

    def backtest_model_on_date(self, test_date: str, training_end_date: str) -> Dict:
        """
        Backtest model: train on data up to yesterday, predict today's actual.

        Algorithm:
            1. Get all historical data up to training_end_date
            2. Engineer features and train ML model
            3. Take draws from test_date
            4. Predict what ML model would have predicted for test_date
            5. Compare predictions vs actual results
            6. Calculate accuracy metrics

        Args:
            test_date: Date to test on (YYYY-MM-DD)
            training_end_date: Date to train up to

        Returns:
            Dictionary with accuracy metrics
        """
        try:
            logger.info(f"[BACKTEST] Backtesting for {test_date} (trained on data up to {training_end_date})")

            # Get historical data for training
            training_draws = self.database.get_draws_by_date_range("2024-01-01", training_end_date)

            if len(training_draws) < 50:
                logger.warning(f"[BACKTEST] Insufficient training data: {len(training_draws)} records")
                return {'error': 'Insufficient training data'}

            # Convert to DataFrame
            train_df = pd.DataFrame(training_draws)
            train_df['date'] = pd.to_datetime(train_df['date'])
            train_df['full_number'] = train_df['full_number'].astype(int)

            # Engineer features
            feature_engineer = FeatureEngineer(self.database)
            train_df = feature_engineer.engineer_all_features(train_df)

            # Train model
            logger.info("[BACKTEST] Training model on historical data...")
            X_train, y_train = self.ml_engine.prepare_training_data(train_df)

            if X_train is None:
                return {'error': 'Failed to prepare training data'}

            self.ml_engine.train_random_forest(X_train, y_train)

            # Get actual results from test_date
            test_draws = self.database.get_draws_by_date_range(test_date, test_date)

            if not test_draws:
                logger.warning(f"[BACKTEST] No draws found for {test_date}")
                return {'error': 'No draws on test date'}

            # Backtest calculations
            accuracy_results = {
                'test_date': test_date,
                'training_end_date': training_end_date,
                'actual_results': [],
                'predictions': [],
                'series_matches': 0,
                'exact_matches': 0,
                'accuracy_score': 0.0,
                'confidence_flag': 'Unknown'
            }

            for draw in test_draws:
                actual_series = str(draw['full_number'])[:2]
                actual_number = draw['full_number']

                # Create feature row for this draw
                # Use previous draw's features if available
                last_draws = [d for d in training_draws if d['date'] < test_date]
                
                if last_draws:
                    prev_draw = last_draws[-1]
                    prev_series = str(prev_draw['full_number'])[:2]
                    prev_sum = sum(int(d) for d in str(prev_draw['full_number']))
                else:
                    prev_series = '00'
                    prev_sum = 25

                # Build feature row (must match training features)
                hour_map = {'1PM': 13, '6PM': 18, '8PM': 20}
                test_row = pd.DataFrame([{
                    'day_of_week_encoded': pd.to_datetime(test_date).dayofweek,
                    'hour_of_draw': hour_map.get(draw.get('time_slot', '1PM'), 13),
                    'prev_sum_of_digits': prev_sum,
                    'series_overdue_days': 5,
                    'rolling_freq': 0.01,
                    'is_weekend_int': 1 if pd.to_datetime(test_date).dayofweek >= 5 else 0,
                    'rolling_mean_digits': 25
                }])

                # Predict
                predictions = self.ml_engine.predict_next_series(test_row, top_k=3)

                # Check if series matches
                if predictions and predictions[0][0] == actual_series:
                    accuracy_results['series_matches'] += 1

                accuracy_results['actual_results'].append({
                    'number': actual_number,
                    'series': actual_series
                })

                accuracy_results['predictions'].append({
                    'predicted_series': [p[0] for p in predictions],
                    'confidences': [p[1] for p in predictions]
                })

            # Calculate accuracy score
            if len(test_draws) > 0:
                series_accuracy = (accuracy_results['series_matches'] / len(test_draws)) * 100
                accuracy_results['accuracy_score'] = round(series_accuracy, 2)

                # Set confidence flag
                if accuracy_results['accuracy_score'] < 15:
                    accuracy_results['confidence_flag'] = 'Low Confidence - High Variance'
                elif accuracy_results['accuracy_score'] < 40:
                    accuracy_results['confidence_flag'] = 'Medium Confidence'
                else:
                    accuracy_results['confidence_flag'] = 'High Confidence'

            logger.info(f"[BACKTEST] Accuracy Score: {accuracy_results['accuracy_score']}%")
            logger.info(f"[BACKTEST] Confidence: {accuracy_results['confidence_flag']}")

            return accuracy_results

        except Exception as e:
            logger.error(f"[BACKTEST] Error: {e}")
            return {'error': str(e)}

    def backtest_multiple_dates(self, num_dates: int = 7) -> List[Dict]:
        """
        Backtest on multiple recent dates.

        Args:
            num_dates: Number of recent days to backtest

        Returns:
            List of backtest results
        """
        results = []

        try:
            # Get all dates with draws
            all_draws = self.database.get_all_draws()

            if not all_draws:
                logger.warning("[BACKTEST] No draws in database")
                return results

            # Get unique dates, sorted
            dates = sorted(set(draw['date'] for draw in all_draws))

            # Test on last N dates
            test_dates = dates[-num_dates:] if len(dates) > num_dates else dates[-1:]

            for test_date in test_dates:
                # Find training end date (30 days before test date)
                test_datetime = pd.to_datetime(test_date)
                training_end = (test_datetime - timedelta(days=30)).strftime("%Y-%m-%d")

                backtest_result = self.backtest_model_on_date(test_date, training_end)
                results.append(backtest_result)

            return results

        except Exception as e:
            logger.error(f"[BACKTEST] Multiple dates error: {e}")
            return results

    def get_average_accuracy(self, backtest_results: List[Dict]) -> float:
        """
        Calculate average accuracy across multiple backtests.

        Args:
            backtest_results: List of backtest result dictionaries

        Returns:
            Average accuracy percentage
        """
        scores = [r.get('accuracy_score', 0) for r in backtest_results if 'accuracy_score' in r]

        if not scores:
            return 0.0

        return round(np.mean(scores), 2)
