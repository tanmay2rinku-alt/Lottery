"""
PROJECT TITAN - Pipeline 6: The "Common Sense" Constraint Filter

Eliminates numbers with:
- 4+ repeating digits (e.g., 77772)
- Perfect sequences (12345, 98765)
- Recent 1st prize winners (last 30 days)
"""

import pandas as pd
from typing import List, Dict
import logging

from database import LotteryDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [TITAN] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConstraintFilter:
    """
    Final filter for predictions.
    Removes numbers that violate common sense constraints.
    """

    def __init__(self, database: LotteryDatabase = None):
        """
        Initialize constraint filter.

        Args:
            database: LotteryDatabase instance
        """
        self.database = database or LotteryDatabase()
        logger.info("[FILTER] Constraint Filter initialized")

    def apply_all_constraints(self, candidates: List[int], 
                             recent_winners: List[int] = None,
                             days_back: int = 30) -> Dict:
        """
        Apply all constraints to candidate numbers.

        Constraints:
            1. Repeating digits: Drop if 4+ same digits (88880, 11111)
            2. Perfect sequences: Drop if sequential (12345, 98765, etc)
            3. Recent winners: Drop if won in last 30 days

        Args:
            candidates: List of candidate numbers
            recent_winners: List of recent winning numbers
            days_back: Look-back window in days

        Returns:
            Dictionary with filtered results and elimination reasons
        """
        try:
            results = {
                'original_count': len(candidates),
                'passed_all_checks': [],
                'eliminated_repeating': [],
                'eliminated_sequence': [],
                'eliminated_recent': [],
                'final_count': 0
            }

            if recent_winners is None:
                recent_winners = self._get_recent_winners(days_back)

            for num in candidates:
                reasons = []

                # Check 1: Repeating digits
                if self._has_excessive_repeating_digits(num):
                    results['eliminated_repeating'].append(num)
                    reasons.append("4+ repeating digits")
                    continue

                # Check 2: Perfect sequences
                if self._is_perfect_sequence(num):
                    results['eliminated_sequence'].append(num)
                    reasons.append("Perfect sequence")
                    continue

                # Check 3: Recent winner
                if num in recent_winners:
                    results['eliminated_recent'].append(num)
                    reasons.append(f"Won in last {days_back} days")
                    continue

                # Passed all checks
                results['passed_all_checks'].append(num)

                if reasons:
                    logger.info(f"[FILTER] Eliminated {num}: {', '.join(reasons)}")
                else:
                    logger.info(f"[FILTER] Passed {num}")

            results['final_count'] = len(results['passed_all_checks'])

            logger.info(f"[FILTER] Filter summary:")
            logger.info(f"  Original: {results['original_count']}")
            logger.info(f"  Repeating digits: {len(results['eliminated_repeating'])}")
            logger.info(f"  Perfect sequences: {len(results['eliminated_sequence'])}")
            logger.info(f"  Recent winners: {len(results['eliminated_recent'])}")
            logger.info(f"  Final: {results['final_count']}")

            return results

        except Exception as e:
            logger.error(f"[FILTER] Constraint application error: {e}")
            return {'error': str(e), 'passed_all_checks': candidates}

    def _has_excessive_repeating_digits(self, number: int, threshold: int = 4) -> bool:
        """
        Check if number has 4+ repeating digits.

        Examples:
            77772: True (four 7s)
            77771: True (four 7s)
            77677: False (only three 7s)
            11111: True (five 1s)

        Args:
            number: 5-digit lottery number
            threshold: Minimum count for elimination (default: 4)

        Returns:
            True if should be eliminated
        """
        num_str = str(number).zfill(5)
        digit_counts = {}

        for digit in num_str:
            digit_counts[digit] = digit_counts.get(digit, 0) + 1

        max_count = max(digit_counts.values())
        return max_count >= threshold

    def _is_perfect_sequence(self, number: int) -> bool:
        """
        Check if number is a perfect sequence (ascending or descending).

        Examples:
            12345: True (ascending)
            54321: True (descending)
            98765: True (descending)
            12346: False (not perfect)
            13579: False (skip sequence)

        Args:
            number: 5-digit lottery number

        Returns:
            True if should be eliminated
        """
        num_str = str(number).zfill(5)
        digits = [int(d) for d in num_str]

        # Check ascending sequence
        if digits == sorted(digits) and digits[0] != digits[-1]:
            return True

        # Check descending sequence
        if digits == sorted(digits, reverse=True) and digits[0] != digits[-1]:
            return True

        return False

    def _get_recent_winners(self, days_back: int = 30) -> List[int]:
        """
        Get all numbers that won in the last N days.

        Args:
            days_back: Number of days to look back

        Returns:
            List of winning numbers
        """
        try:
            from datetime import datetime, timedelta

            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")

            draws = self.database.get_draws_by_date_range(start_date, end_date)
            recent = [draw['full_number'] for draw in draws]

            logger.info(f"[FILTER] Found {len(recent)} winners in last {days_back} days")
            return recent

        except Exception as e:
            logger.error(f"[FILTER] Error getting recent winners: {e}")
            return []

    def validate_candidates(self, candidates: List[int]) -> Dict:
        """
        Quick validation of candidate list.

        Args:
            candidates: List of numbers to validate

        Returns:
            Validation report
        """
        report = {
            'total': len(candidates),
            'valid_5_digit': 0,
            'invalid': [],
            'duplicates': len(candidates) - len(set(candidates))
        }

        for num in candidates:
            if isinstance(num, int) and 10000 <= num <= 99999:
                report['valid_5_digit'] += 1
            else:
                report['invalid'].append(num)

        return report
