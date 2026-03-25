"""
PROJECT TITAN - Pipeline 3: Markov Chain Transition Matrix

Builds probabilistic transition matrices for lottery series.
Example: After 80xxx wins at 1PM, what's the probability of 40xxx at 6PM?
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from collections import defaultdict
import logging

from database import LotteryDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TITAN] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarkovChainEngine:
    """
    Builds Markov chains to predict state transitions in lottery results.
    Models: Series -> Series transitions across time slots.
    """

    def __init__(self, database: LotteryDatabase = None):
        """
        Initialize Markov engine.

        Args:
            database: LotteryDatabase instance
        """
        self.database = database or LotteryDatabase()
        self.transition_matrix = None
        self.series_list = None
        logger.info("[MARKOV] Markov Chain Engine initialized")

    def build_transition_matrix(self, draws_df: pd.DataFrame) -> np.ndarray:
        """
        Build Markov transition matrix from historical data.

        Mathematical Model:
            M[i,j] = P(next series = j | current series = i)
                   = count(i->j transitions) / count(i in sequence)

        Args:
            draws_df: DataFrame with columns: date, time_slot, series, full_number

        Returns:
            Transition matrix (numpy array)
        """
        try:
            # Sort by date and time slot to establish sequence
            draws_df = draws_df.sort_values(['date', 'time_slot']).reset_index(drop=True)

            # Get unique series
            self.series_list = sorted(draws_df['series'].unique())
            n_states = len(self.series_list)

            logger.info(f"[MARKOV] Building matrix for {n_states} series states")

            # Initialize transition count matrix
            transition_counts = np.zeros((n_states, n_states))

            # Map series to indices
            series_to_idx = {s: i for i, s in enumerate(self.series_list)}

            # Count transitions
            for i in range(len(draws_df) - 1):
                current_series = draws_df.iloc[i]['series']
                next_series = draws_df.iloc[i + 1]['series']

                current_idx = series_to_idx[current_series]
                next_idx = series_to_idx[next_series]

                transition_counts[current_idx, next_idx] += 1

                logger.debug(f"[MARKOV] Transition: {current_series} -> {next_series}")

            # Normalize to get probabilities
            row_sums = transition_counts.sum(axis=1, keepdims=True)
            # Avoid division by zero
            row_sums[row_sums == 0] = 1

            self.transition_matrix = transition_counts / row_sums

            logger.info(f"[MARKOV] Transition matrix built: {self.transition_matrix.shape}")
            return self.transition_matrix

        except Exception as e:
            logger.error(f"[MARKOV] Error building transition matrix: {e}")
            return None

    def predict_next_series(self, current_series: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Predict top K most likely next series.

        Args:
            current_series: Current series code (e.g., '80')
            top_k: Number of predictions to return

        Returns:
            List of (series, probability) tuples, sorted by probability
        """
        try:
            if self.transition_matrix is None:
                logger.warning("[MARKOV] Transition matrix not built")
                return []

            # Get current series index
            if current_series not in self.series_list:
                logger.warning(f"[MARKOV] Series {current_series} not in history")
                return []

            current_idx = self.series_list.index(current_series)

            # Get transition probabilities for this series
            probabilities = self.transition_matrix[current_idx, :]

            # Get top K series
            top_indices = np.argsort(probabilities)[-top_k:][::-1]
            predictions = [
                (self.series_list[idx], float(probabilities[idx]))
                for idx in top_indices
            ]

            logger.info(f"[MARKOV] Predicted next series from {current_series}: {predictions}")
            return predictions

        except Exception as e:
            logger.error(f"[MARKOV] Prediction error: {e}")
            return []

    def predict_time_slot_transitions(self, draws_df: pd.DataFrame) -> Dict:
        """
        Build separate transition matrices for each time slot transition.
        Example: 1PM -> 6PM transitions vs 6PM -> 8PM transitions

        Args:
            draws_df: DataFrame with time_slot information

        Returns:
            Dictionary of transition matrices keyed by (from_slot, to_slot)
        """
        try:
            time_slots = ['1PM', '6PM', '8PM']
            time_slot_transitions = {}

            draws_df = draws_df.sort_values(['date', 'time_slot']).reset_index(drop=True)

            for from_slot in time_slots:
                for to_slot in time_slots:
                    if from_slot == to_slot:
                        continue

                    # Get draws for each slot
                    from_draws = draws_df[draws_df['time_slot'] == from_slot].reset_index(drop=True)
                    to_draws = draws_df[draws_df['time_slot'] == to_slot].reset_index(drop=True)

                    if len(from_draws) == 0 or len(to_draws) == 0:
                        continue

                    # Count transitions between time slots
                    transitions = defaultdict(lambda: defaultdict(int))

                    for _, from_row in from_draws.iterrows():
                        from_date = from_row['date']
                        from_series = from_row['series']

                        # Find next draw of to_slot on same or next day
                        to_row = to_draws[to_draws['date'] >= from_date].iloc[0] if len(to_draws[to_draws['date'] >= from_date]) > 0 else None

                        if to_row is not None:
                            to_series = to_row['series']
                            transitions[from_series][to_series] += 1

                    time_slot_transitions[(from_slot, to_slot)] = dict(transitions)

            logger.info(f"[MARKOV] Built {len(time_slot_transitions)} time-slot transition models")
            return time_slot_transitions

        except Exception as e:
            logger.error(f"[MARKOV] Time slot transition error: {e}")
            return {}

    def get_transition_matrix_summary(self) -> Dict:
        """
        Get summary statistics of the transition matrix.

        Returns:
            Dictionary with matrix properties
        """
        if self.transition_matrix is None:
            return {}

        return {
            'shape': self.transition_matrix.shape,
            'series_count': len(self.series_list),
            'series': self.series_list,
            'mean_probability': float(np.mean(self.transition_matrix)),
            'max_probability': float(np.max(self.transition_matrix)),
            'min_probability': float(np.min(self.transition_matrix)),
            'sparsity': float(np.count_nonzero(self.transition_matrix) / self.transition_matrix.size)
        }

    def display_matrix(self):
        """Pretty-print the transition matrix"""
        if self.transition_matrix is None:
            logger.warning("[MARKOV] No transition matrix to display")
            return

        df_matrix = pd.DataFrame(
            self.transition_matrix,
            index=self.series_list,
            columns=self.series_list
        )

        logger.info("[MARKOV] Transition Matrix:")
        logger.info("\n" + str(df_matrix.round(4)))
