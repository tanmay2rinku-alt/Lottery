"""
Specific Number Analyzer
Evaluates probability score for a specific lottery number
"""

import numpy as np
from collections import Counter
from typing import Dict, List


class SpecificNumberAnalyzer:
    """Analyze a specific lottery number against historical winning data"""
    
    def __init__(self, winning_numbers: List[int]):
        """
        Initialize with historical winning numbers
        
        Args:
            winning_numbers: List of all winning lottery numbers
        """
        self.winning_numbers = winning_numbers
        self.freq_counter = Counter(winning_numbers)
        self.stats = self._calculate_stats()
        
    def _calculate_stats(self) -> Dict:
        """Calculate basic statistics"""
        if not self.winning_numbers:
            return {}
        
        numbers_array = np.array(self.winning_numbers)
        return {
            'mean': float(np.mean(numbers_array)),
            'median': float(np.median(numbers_array)),
            'std_dev': float(np.std(numbers_array)),
            'min': int(np.min(numbers_array)),
            'max': int(np.max(numbers_array)),
            'total_draws': len(self.winning_numbers),
            'unique_numbers': len(set(self.winning_numbers)),
        }
    
    def analyze_number(self, target_number: int) -> Dict:
        """
        Comprehensive analysis of a specific number
        
        Args:
            target_number: The lottery number to analyze
            
        Returns:
            Dict with detailed probability score and analysis
        """
        print(f"\n[SCORER] Analyzing number {target_number}...")
        
        score_breakdown = {}
        total_score = 0
        
        # ===== FACTOR 1: Historical Frequency (30%) =====
        freq = self.freq_counter.get(target_number, 0)
        max_freq = max(self.freq_counter.values()) if self.freq_counter else 1
        
        freq_score = (freq / max_freq * 100) if max_freq > 0 else 0
        score_breakdown['frequency'] = {
            'score': freq_score,
            'weight': 0.30,
            'weighted': freq_score * 0.30,
            'reasoning': f"Appeared {freq} times (max: {max_freq})",
        }
        total_score += score_breakdown['frequency']['weighted']
        
        # ===== FACTOR 2: Statistical Position (25%) =====
        mean = self.stats['mean']
        std = self.stats['std_dev'] or 1
        
        # Numbers close to mean get higher scores
        dist_from_mean = abs(target_number - mean)
        z_score = dist_from_mean / std
        stat_score = max(0, 100 - (z_score * 20))
        
        score_breakdown['statistical_position'] = {
            'score': stat_score,
            'weight': 0.25,
            'weighted': stat_score * 0.25,
            'reasoning': f"Distance from mean: {dist_from_mean:.0f} (Z-score: {z_score:.2f})",
        }
        total_score += score_breakdown['statistical_position']['weighted']
        
        # ===== FACTOR 3: Digit Pattern Analysis (20%) =====
        digit_str = str(target_number).zfill(5)
        digits = [int(d) for d in digit_str]
        digit_sum = sum(digits)
        
        # Calculate how common this digit sum is
        all_digit_sums = [sum([int(d) for d in str(n).zfill(5)]) for n in self.winning_numbers]
        digit_sum_freq = Counter(all_digit_sums)
        common_sums = digit_sum_freq.get(digit_sum, 0)
        max_sum_freq = max(digit_sum_freq.values()) if digit_sum_freq else 1
        
        pattern_score = (common_sums / max_sum_freq * 100) if max_sum_freq > 0 else 50
        
        # Unique digits bonus
        unique_digits = len(set(digits))
        diversity_bonus = (unique_digits / 5) * 20  # 0-20 points
        pattern_score = min(100, pattern_score + diversity_bonus)
        
        score_breakdown['digit_pattern'] = {
            'score': pattern_score,
            'weight': 0.20,
            'weighted': pattern_score * 0.20,
            'reasoning': f"Digits: {digit_str} | Sum: {digit_sum} | Unique: {unique_digits}/5",
        }
        total_score += score_breakdown['digit_pattern']['weighted']
        
        # ===== FACTOR 4: Range Position (15%) =====
        min_val = self.stats['min']
        max_val = self.stats['max']
        total_range = max_val - min_val or 1
        
        # Numbers in middle range typically win more
        mid_point = min_val + total_range / 2
        dist_from_midpoint = abs(target_number - mid_point)
        range_score = max(0, 100 - (dist_from_midpoint / total_range * 100))
        
        score_breakdown['range_position'] = {
            'score': range_score,
            'weight': 0.15,
            'weighted': range_score * 0.15,
            'reasoning': f"Position in range: {min_val}-{max_val} (middle favored)",
        }
        total_score += score_breakdown['range_position']['weighted']
        
        # ===== FACTOR 5: Cold/Hot Opportunity (10%) =====
        # If number hasn't appeared, give bonus for "due" status
        if freq == 0:
            opportunity_score = 70  # High opportunity
            reasoning = "This number is COLD - statistically 'due' for a win"
        elif freq < 2:
            opportunity_score = 60
            reasoning = "Rarely won - lower competition"
        elif freq >= max_freq / 2:
            opportunity_score = 40
            reasoning = "Already frequently won - higher competition"
        else:
            opportunity_score = 50
            reasoning = "Moderate win frequency"
        
        score_breakdown['opportunity'] = {
            'score': opportunity_score,
            'weight': 0.10,
            'weighted': opportunity_score * 0.10,
            'reasoning': reasoning,
        }
        total_score += score_breakdown['opportunity']['weighted']
        
        # ===== FINAL PROBABILITY SCORE =====
        final_score = min(100, max(0, total_score))
        
        result = {
            'number': target_number,
            'total_score': final_score,
            'score_breakdown': score_breakdown,
            'appeared_count': freq,
            'digit_sum': digit_sum,
            'unique_digits': unique_digits,
        }
        
        return result
    
    def compare_with_top_numbers(self, target_number: int, top_n: int = 5) -> Dict:
        """Compare target number with top predicted numbers"""
        print(f"[SCORER] Comparing {target_number} with top numbers...")
        
        # Analyze target
        target_analysis = self.analyze_number(target_number)
        target_score = target_analysis['total_score']
        
        # Score all numbers
        all_scores = {}
        for num in set(self.winning_numbers):
            analysis = self.analyze_number(num)
            all_scores[num] = analysis['total_score']
        
        # Get top numbers
        sorted_nums = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        top_numbers = sorted_nums[:top_n]
        
        # Find rank
        rank = next((i+1 for i, (num, score) in enumerate(sorted_nums) if num == target_number), -1)
        percentile = (len(sorted_nums) - rank) / len(sorted_nums) * 100 if rank > 0 else 0
        
        return {
            'target_number': target_number,
            'target_score': target_score,
            'rank': rank,
            'percentile': percentile,
            'top_numbers': top_numbers,
            'target_analysis': target_analysis,
        }
    
    def print_detailed_report(self, analysis: Dict):
        """Print detailed analysis report"""
        print("\n" + "="*60)
        print(f"LOTTERY NUMBER ANALYSIS: {analysis['number']}")
        print("="*60)
        
        score = analysis['total_score']
        bar_length = int(score / 5)
        bar = "[" + "="*bar_length + " "*(20-bar_length) + "]"
        print(f"\nOVERALL PROBABILITY SCORE: {bar} {score:.1f}%\n")
        
        print("FACTOR BREAKDOWN:")
        for factor_name, factor_data in analysis['score_breakdown'].items():
            f_score = factor_data['score']
            f_weight = factor_data['weight'] * 100
            f_weighted = factor_data['weighted']
            f_reasoning = factor_data['reasoning']
            
            factor_bar = "[" + "="*int(f_score/5) + " "*(20-int(f_score/5)) + "]"
            print(f"\n  {factor_name.upper()}")
            print(f"    Raw Score: {factor_bar} {f_score:.1f}%")
            print(f"    Weight: {f_weight:.0f}% (contributes {f_weighted:.1f}%)")
            print(f"    Reason: {f_reasoning}")
        
        print(f"\nNUMBER DETAILS:")
        print(f"  Digits: {str(analysis['number']).zfill(5)}")
        print(f"  Digit Sum: {analysis['digit_sum']}")
        print(f"  Unique Digits: {analysis['unique_digits']}/5")
        print(f"  Historical Appearances: {analysis['appeared_count']}")
        
        print("\n" + "="*60)
    
    def print_comparison_report(self, comparison: Dict):
        """Print comparison report"""
        target_num = comparison['target_number']
        target_score = comparison['target_score']
        rank = comparison['rank']
        percentile = comparison['percentile']
        
        print("\n" + "="*60)
        print(f"RANKING COMPARISON: {target_num}")
        print("="*60)
        
        print(f"\nYour Number: {target_num}")
        print(f"Probability Score: {target_score:.1f}%")
        print(f"Rank: #{rank} out of all winning numbers")
        print(f"Percentile: {percentile:.1f}% (better than this % of numbers)")
        
        if target_score >= 75:
            tier = "EXCELLENT"
            color = "[EXCELLENT]"
        elif target_score >= 60:
            tier = "GOOD"
            color = "[GOOD]"
        elif target_score >= 45:
            tier = "MODERATE"
            color = "[MODERATE]"
        else:
            tier = "LOW"
            color = "[LOW]"
        
        print(f"\nTIER: {color} {tier}")
        
        print(f"\nTOP 5 COMPETING NUMBERS:")
        for i, (num, score) in enumerate(comparison['top_numbers'][:5], 1):
            indicator = "<<< YOUR NUMBER" if num == target_num else ""
            print(f"  {i}. {num}: {score:.1f}% {indicator}")
        
        print("\n" + "="*60)
