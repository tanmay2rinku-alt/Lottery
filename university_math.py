"""
Pipeline 5: University Math Intelligence Engine
Implements MIT/Stanford grade statistical models for lottery analysis.
"""

import numpy as np
from scipy import stats
from typing import List, Dict

class UniversityMathEngine:
    def __init__(self, historical_numbers: List[int]):
        self.numbers = np.array(historical_numbers)

    def monte_carlo_simulation(self, iterations: int = 10000) -> Dict:
        """
        Runs Monte Carlo iterations to find most likely winners.
        """
        if len(self.numbers) == 0: return {}
        
        # Calculate prob distribution from history
        unique, counts = np.unique(self.numbers, return_counts=True)
        probs = counts / counts.sum()
        
        # Simulate next 10 draws 10,000 times
        sim_results = np.random.choice(unique, size=(iterations, 10), p=probs)
        
        # Flatten and count the most frequent top performers in sims
        all_sim_nums = sim_results.flatten()
        sim_counts = Counter(all_sim_nums)
        
        top_picks = sorted(sim_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "top_simulated_picks": [int(n[0]) for n in top_picks],
            "confidence_interval": [float(np.percentile(all_sim_nums, 2.5)), float(np.percentile(all_sim_nums, 97.5))]
        }

    def poisson_arrival_analysis(self, num_draws: int = 100) -> Dict:
        """
        Uses Poisson Distribution to predict frequency of occurrences per time unit.
        """
        if len(self.numbers) == 0: return {}
        
        # Avg occurrences (lambda)
        lam = len(self.numbers) / num_draws
        
        # Prob of num appearing k times
        def poisson_pmf(k, lam):
            return (np.exp(-lam) * (lam**k)) / np.math.factorial(k)
        
        return {
            "expected_lambda": float(lam),
            "prob_of_repeat": float(poisson_pmf(2, lam)),
            "is_hot": lam > 1.2
        }

    def chi_squared_test(self) -> Dict:
        """
        Test for statistical significance (Deviation from expected distribution).
        """
        if len(self.numbers) < 10: return {"status": "insufficient_data"}
        
        # Group by first digit (0-9)
        first_digits = [int(str(n).zfill(5)[0]) for n in self.numbers]
        observed = np.bincount(first_digits, minlength=10)
        expected = np.full(10, len(first_digits) / 10)
        
        chi2, p_value = stats.chisquare(observed, expected)
        
        return {
            "chi_squared_stat": float(chi2),
            "p_value": float(p_value),
            "bias_detected": p_value < 0.05,
            "interpretation": "Draw is biased/hot" if p_value < 0.05 else "Draw is statistically random"
        }

from collections import Counter
