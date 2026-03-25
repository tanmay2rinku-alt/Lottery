"""
PROJECT TITAN - Pipeline 5: Monte Carlo Simulation Engine

Runs 10,000 randomized simulated draws weighted by historical frequencies.
Returns top 5 most likely full numbers for next draw.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Counter
from collections import Counter as CounterLib
import logging

from database import LotteryDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TITAN] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MonteCarloSimulationEngine:
    """
    Monte Carlo simulation for lottery predictions.
    Runs 10,000 simulations with weighted random number generation.
    """

    def __init__(self, database: LotteryDatabase = None):
        """
        Initialize Monte Carlo engine.

        Args:
            database: LotteryDatabase instance
        """
        self.database = database or LotteryDatabase()
        self.simulation_results = None
        logger.info("[MONTE_CARLO] Monte Carlo Simulation Engine initialized")

    def run_simulations(self, draws_df: pd.DataFrame, 
                       ml_predicted_series: List[str],
                       num_simulations: int = 10000) -> Dict:
        """
        Run 10,000 weighted Monte Carlo simulations.

        Algorithm:
            1. Calculate frequency distribution of all 5-digit numbers in history
            2. Calculate frequency distribution of series in history
            3. For each simulation run:
               a. Sample 5 times from weighted number distribution
               b. Weight sampling by ML model predictions
               c. Track which numbers appear most
            4. Return top 5 numbers with highest frequency across all sims

        Mathematical Model:
            P(number) = (frequency_in_history * ml_confidence) / normalization
            
            This creates a weighted distribution where:
            - Numbers that won before are more likely
            - Numbers from predicted series are boosted
            - Low-probability combinations suppress noise

        Args:
            draws_df: Historical draws DataFrame
            ml_predicted_series: Top 3 series from ML model
            num_simulations: Number of simulation runs (default: 10,000)

        Returns:
            Dictionary with simulation results
        """
        try:
            logger.info(f"[MONTE_CARLO] Starting {num_simulations:,} simulations...")

            # Extract all numbers and series from history
            all_numbers = draws_df['full_number'].values
            all_series = [str(n)[:2] for n in all_numbers]

            unique_numbers = np.unique(all_numbers)
            unique_series = np.unique(all_series)

            # Calculate frequency weights
            number_freq = CounterLib(all_numbers)
            series_freq = CounterLib(all_series)

            # Normalize frequencies to probabilities
            number_probs = np.array([number_freq[num] / len(all_numbers) for num in unique_numbers])
            series_probs = np.array([series_freq[s] / len(all_series) for s in unique_series])

            # Boost probabilities for ML-predicted series
            boosted_series_probs = series_probs.copy()
            for i, series in enumerate(unique_series):
                if series in ml_predicted_series:
                    boost_factor = ml_predicted_series.index(series) + 1
                    boosted_series_probs[i] *= (1.0 + 0.3 * (1 / boost_factor))

            # Normalize boosted probabilities
            boosted_series_probs /= boosted_series_probs.sum()

            # Track results from all simulations
            simulated_numbers = []

            # Run simulations
            for sim_run in range(num_simulations):
                # In each simulation, generate 5 random numbers
                # Weight them by historical frequency and ML predictions
                
                for _ in range(5):
                    # Select series
                    selected_series = np.random.choice(
                        unique_series,
                        p=boosted_series_probs
                    )

                    # Get all numbers with this series
                    series_numbers = [n for n in unique_numbers if str(n)[:2] == selected_series]

                    if series_numbers:
                        # Select number from series
                        series_number_freqs = np.array([number_freq[n] for n in series_numbers])
                        series_number_probs = series_number_freqs / series_number_freqs.sum()

                        selected_number = np.random.choice(
                            series_numbers,
                            p=series_number_probs
                        )

                        simulated_numbers.append(selected_number)

                if (sim_run + 1) % 1000 == 0:
                    logger.info(f"[MONTE_CARLO] Completed {sim_run + 1:,} simulations...")

            # Count frequencies
            number_simulations = CounterLib(simulated_numbers)

            # Sort by frequency
            top_numbers = number_simulations.most_common(5)

            # Convert to percentage
            results = {
                'simulation_count': num_simulations,
                'total_samples': len(simulated_numbers),
                'top_5_numbers': [],
                'simulation_data': top_numbers
            }

            for number, count in top_numbers:
                percentage = (count / len(simulated_numbers)) * 100
                results['top_5_numbers'].append({
                    'number': int(number),
                    'frequency': int(count),
                    'percentage': round(percentage, 2),
                    'series': str(number)[:2]
                })

            logger.info(f"[MONTE_CARLO] Simulation complete")
            logger.info(f"[MONTE_CARLO] Top 5 numbers:")
            for item in results['top_5_numbers']:
                logger.info(f"  {item['number']}: {item['frequency']} times ({item['percentage']}%)")

            self.simulation_results = results
            return results

        except Exception as e:
            logger.error(f"[MONTE_CARLO] Simulation error: {e}")
            return {'error': str(e), 'top_5_numbers': []}

    def get_top_predictions(self, top_k: int = 5) -> List[Dict]:
        """
        Get top K predicted numbers from simulations.

        Args:
            top_k: Number of predictions

        Returns:
            List of top predictions with details
        """
        if self.simulation_results is None:
            logger.warning("[MONTE_CARLO] No simulation results available")
            return []

        return self.simulation_results.get('top_5_numbers', [])[:top_k]

    def save_simulation_results(self, filepath: str = "monte_carlo_results.txt") -> bool:
        """
        Save simulation results to file.

        Args:
            filepath: Path to save file

        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w') as f:
                f.write(f"Monte Carlo Simulation Results\n")
                f.write(f"Simulations: {self.simulation_results.get('simulation_count')}\n")
                f.write(f"\nTop 5 Numbers:\n")
                for item in self.simulation_results.get('top_5_numbers', []):
                    f.write(f"  {item['number']}: {item['frequency']} occurrences ({item['percentage']}%)\n")

            logger.info(f"[MONTE_CARLO] Results saved: {filepath}")
            return True

        except Exception as e:
            logger.error(f"[MONTE_CARLO] Save error: {e}")
            return False
