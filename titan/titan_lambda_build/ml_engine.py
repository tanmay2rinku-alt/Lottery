"""
PROJECT TITAN - Pipeline 4: Machine Learning Ensemble (Random Forest)

Random Forest classifier for predicting next-draw lottery series.
Trains on historical data with engineered features.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from typing import List, Dict, Tuple
import logging
import joblib
from datetime import datetime

from database import LotteryDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TITAN] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLEnsembleEngine:
    """
    Machine Learning ensemble using Random Forest.
    Predicts next lottery series (first 2 digits) based on engineered features.
    """

    def __init__(self, database: LotteryDatabase = None):
        """
        Initialize ML engine.

        Args:
            database: LotteryDatabase instance
        """
        self.database = database or LotteryDatabase()
        self.model = None
        self.feature_names = None
        self.label_encoder = LabelEncoder()
        self.model_version = f"v1_{datetime.now().strftime('%Y%m%d')}"
        logger.info("[ML] ML Ensemble Engine initialized")

    def prepare_training_data(self, draws_df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Prepare training data with features and target variable.

        Feature set:
            1. day_of_week (encoded 0-6)
            2. hour_of_draw (1, 6, 8)
            3. previous_series (last draw's series)
            4. prev_sum_of_digits (sum of last draw's digits)
            5. series_overdue_days (days since series last won)
            6. rolling_win_freq_30d (frequency in 30-day window)
            7. is_weekend (boolean 0/1)
            8. mean_digits_in_window (rolling average)

        Target: series (first 2 digits)

        Args:
            draws_df: DataFrame with engineered features

        Returns:
            Tuple of (features_df, target_array)
        """
        try:
            df = draws_df.copy()
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)

            # Feature 1: Day of week
            df['day_of_week_encoded'] = pd.to_datetime(df['date']).dt.dayofweek

            # Feature 2: Time of draw (1PM=1, 6PM=6, 8PM=8)
            df['hour_of_draw'] = df['time_slot'].map({'1PM': 13, '6PM': 18, '8PM': 20})

            # Feature 3: Previous series (with lag)
            df['previous_series'] = df['series'].shift(1).fillna('00')

            # Feature 4: Previous sum of digits
            df['prev_sum_of_digits'] = df['sum_of_digits'].shift(1).fillna(df['sum_of_digits'].mean())

            # Feature 5: Series overdue days
            df['series_overdue_days'] = df['days_since_last_series'].fillna(0)

            # Feature 6: Rolling frequency (already engineered)
            df['rolling_freq'] = df['rolling_win_freq_30d'].fillna(0)

            # Feature 7: Weekend flag
            df['is_weekend_int'] = df['is_weekend'].astype(int)

            # Feature 8: Rolling mean of digits
            df['rolling_mean_digits'] = df['sum_of_digits'].rolling(window=7, min_periods=1).mean()

            # Select features for model
            self.feature_names = [
                'day_of_week_encoded',
                'hour_of_draw',
                'prev_sum_of_digits',
                'series_overdue_days',
                'rolling_freq',
                'is_weekend_int',
                'rolling_mean_digits'
            ]

            X = df[self.feature_names].copy()
            y = df['series'].values

            logger.info(f"[ML] Training data prepared: {X.shape[0]} samples, {X.shape[1]} features")
            return X, y

        except Exception as e:
            logger.error(f"[ML] Error preparing training data: {e}")
            return None, None

    def train_random_forest(self, X: pd.DataFrame, y: np.ndarray) -> bool:
        """
        Train Random Forest classifier with optimized hyperparameters.

        Hyperparameters:
            n_estimators: 100 trees (balances accuracy and training time)
            max_depth: 15 (prevents overfitting on small dataset)
            min_samples_split: 5 (minimum samples to split a node)
            min_samples_leaf: 2 (minimum samples in leaf node)
            max_features: 'sqrt' (random subset of features)
            random_state: 42 (reproducibility)

        Mathematical rationale:
            - Random forests use Bootstrap AGGregation (bagging) to reduce variance
            - Each tree is trained on random subset of features
            - Final prediction = majority vote across all trees
            - Feature importance = average decrease in impurity

        Args:
            X: Features DataFrame
            y: Target array (series labels)

        Returns:
            True if training successful
        """
        try:
            logger.info("[ML] Training Random Forest classifier...")

            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features='sqrt',
                random_state=42,
                n_jobs=-1,
                verbose=1
            )

            self.model.fit(X, y)

            # Calculate training accuracy
            train_accuracy = self.model.score(X, y)
            logger.info(f"[ML] Training accuracy: {train_accuracy:.4f}")

            # Feature importance
            feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
            sorted_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)

            logger.info("[ML] Feature Importance:")
            for feature, importance in sorted_importance:
                logger.info(f"  {feature}: {importance:.4f}")

            return True

        except Exception as e:
            logger.error(f"[ML] Training error: {e}")
            return False

    def predict_next_series(self, X_test: pd.DataFrame, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Predict top K most probable series for next draw.

        Args:
            X_test: Test feature row(s)
            top_k: Number of predictions

        Returns:
            List of (series, probability) tuples
        """
        try:
            if self.model is None:
                logger.warning("[ML] Model not trained")
                return []

            # Get prediction probabilities
            probabilities = self.model.predict_proba(X_test)

            # Get classes
            classes = self.model.classes_

            # Get top K
            top_k_indices = np.argsort(probabilities[0])[-top_k:][::-1]

            predictions = [
                (classes[idx], float(probabilities[0, idx]))
                for idx in top_k_indices
            ]

            logger.info(f"[ML] Predicted top series: {predictions}")
            return predictions

        except Exception as e:
            logger.error(f"[ML] Prediction error: {e}")
            return []

    def save_model(self, filepath: str = "titan_rf_model.pkl") -> bool:
        """
        Save trained model to disk.

        Args:
            filepath: Path to save model

        Returns:
            True if successful
        """
        try:
            joblib.dump(self.model, filepath)
            logger.info(f"[ML] Model saved: {filepath}")
            return True
        except Exception as e:
            logger.error(f"[ML] Model save error: {e}")
            return False

    def load_model(self, filepath: str = "titan_rf_model.pkl") -> bool:
        """
        Load pre-trained model from disk.

        Args:
            filepath: Path to model file

        Returns:
            True if successful
        """
        try:
            self.model = joblib.load(filepath)
            logger.info(f"[ML] Model loaded: {filepath}")
            return True
        except Exception as e:
            logger.error(f"[ML] Model load error: {e}")
            return False

    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return self.feature_names or []
