"""
PROJECT TITAN - Pipeline 2: Advanced Feature Engineering

Transforms raw lottery numbers into 11+ engineered features.
Calculates Days_Since_Last_Appearance, Rolling_Win_Frequency_30D, etc.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import logging

from database import LotteryDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TITAN] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Advanced feature engineering pipeline.
    Transforms raw lottery draws into machine learning features.
    """

    def __init__(self, database: LotteryDatabase = None):
        """
        Initialize feature engineer with database.

        Args:
            database: LotteryDatabase instance
        """
        self.database = database or LotteryDatabase()
        logger.info("[FEATURES] Feature Engineer initialized")

    def engineer_all_features(self, draws_dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering transformations.

        Args:
            draws_dataframe: DataFrame with columns: date, time_slot, full_number

        Returns:
            DataFrame with engineered features
        """
        df = draws_dataframe.copy()

        # Feature 1-6: Basic number decomposition
        df = self._decompose_number(df)

        # Feature 7: Sum of digits
        df['sum_of_digits'] = df['full_number'].astype(str).apply(
            lambda x: sum(int(d) for d in x)
        )

        # Feature 8: Odd/Even ratio
        df['odd_even_ratio'] = df['full_number'].astype(str).apply(
            self._calculate_odd_even_ratio
        )

        # Feature 9-10: Days since last appearance
        df = self._add_days_since_last(df)

        # Feature 11: Rolling win frequency (30 days)
        df = self._add_rolling_frequency(df)

        # Feature 12: Day of week
        df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name()

        # Feature 13: Is weekend
        df['is_weekend'] = pd.to_datetime(df['date']).dt.dayofweek >= 5

        # Feature 14: Draw position in week
        df['week_position'] = pd.to_datetime(df['date']).dt.isocalendar().week

        logger.info(f"[FEATURES] Engineered {len(df.columns)} features for {len(df)} draws")
        return df

    def _decompose_number(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Break 5-digit number into Series, Middle, Ending.

        Mathematical breakdown:
            Number: ABCDE
            - Series: AB (first 2 digits) - most predictive
            - Middle: C (3rd digit)
            - Ending: DE (last 2 digits)

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with decomposed features
        """
        df['full_number_str'] = df['full_number'].astype(str).str.zfill(5)

        df['series'] = df['full_number_str'].str[:2]
        df['middle'] = df['full_number_str'].str[2].astype(int)
        df['ending'] = df['full_number_str'].str[3:].astype(int)

        logger.info("[FEATURES] Number decomposition complete")
        return df

    def _calculate_odd_even_ratio(self, number_str: str) -> float:
        """
        Calculate ratio of odd to even digits.

        Mathematical formula:
            Odd_Even_Ratio = count(odd digits) / count(even digits)
            Special cases: all odd or all even return 1.0 or 0.0

        Args:
            number_str: 5-digit number as string

        Returns:
            Float ratio
        """
        odd_count = sum(1 for d in number_str if int(d) % 2 == 1)
        even_count = 5 - odd_count

        if even_count == 0:
            return 1.0
        return odd_count / even_count

    def _add_days_since_last(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate days since last appearance for Series and Ending.

        Algorithm:
            For each draw, find the most recent previous occurrence of:
            1. Same Series (first 2 digits)
            2. Same Ending (last 2 digits)

        Uses cumulative approach for efficiency.

        Args:
            df: DataFrame with dates and decomposed numbers

        Returns:
            DataFrame with days_since columns
        """
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        df['days_since_last_series'] = 0
        df['days_since_last_ending'] = 0

        last_series_date = {}
        last_ending_date = {}

        for idx, row in df.iterrows():
            current_date = row['date']
            current_series = row['series']
            current_ending = row['ending']

            # Days since last series appearance
            if current_series in last_series_date:
                days_diff = (current_date - last_series_date[current_series]).days
                df.at[idx, 'days_since_last_series'] = days_diff
            else:
                df.at[idx, 'days_since_last_series'] = -1  # Never appeared

            # Days since last ending appearance
            if current_ending in last_ending_date:
                days_diff = (current_date - last_ending_date[current_ending]).days
                df.at[idx, 'days_since_last_ending'] = days_diff
            else:
                df.at[idx, 'days_since_last_ending'] = -1  # Never appeared

            # Update last seen dates
            last_series_date[current_series] = current_date
            last_ending_date[current_ending] = current_date

        logger.info("[FEATURES] Days since last appearance calculated")
        return df

    def _add_rolling_frequency(self, df: pd.DataFrame, days_window: int = 30) -> pd.DataFrame:
        """
        Calculate rolling win frequency for each number over 30 days.

        Algorithm:
            For each draw, count how many times that exact 5-digit number won
            in the past 30 days (including today).

            Rolling_Win_Frequency_30D = (count in 30d window) / (days_in_window)
            This gives a normalized frequency score.

        Args:
            df: Input DataFrame
            days_window: Window size in days (default: 30)

        Returns:
            DataFrame with rolling frequency feature
        """
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        df['rolling_win_freq_30d'] = 0.0

        for idx, row in df.iterrows():
            current_date = row['date']
            current_number = row['full_number']

            # Find all draws of this number in the past 30 days
            window_start = current_date - timedelta(days=days_window)
            mask = (df['date'] >= window_start) & (df['date'] <= current_date) & (df['full_number'] == current_number)

            count = mask.sum()
            frequency = count / days_window  # Normalize by window size

            df.at[idx, 'rolling_win_freq_30d'] = frequency

        logger.info("[FEATURES] Rolling 30-day frequency calculated")
        return df

    def get_feature_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for all engineered features.

        Args:
            df: Feature-engineered DataFrame

        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_records': len(df),
            'date_range': f"{df['date'].min()} to {df['date'].max()}",
            'unique_numbers': df['full_number'].nunique(),
            'unique_series': df['series'].nunique(),
            'avg_days_since_series': df['days_since_last_series'].mean(),
            'avg_rolling_frequency': df['rolling_win_freq_30d'].mean(),
            'sum_digits_stats': {
                'min': df['sum_of_digits'].min(),
                'max': df['sum_of_digits'].max(),
                'mean': df['sum_of_digits'].mean()
            }
        }

        logger.info(f"[FEATURES] Statistics: {stats['total_records']} records, {stats['unique_numbers']} unique numbers")
        return stats
