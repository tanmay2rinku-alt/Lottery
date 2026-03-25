"""
Phase 4: Lottery Intelligence Analysis
Advanced analytics to derive probability scores and predict winning numbers
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple
import sqlite3
import os

# Try to import draw time analyzer
try:
    from draw_time_analyzer import DrawTimeAnalyzer
    HAS_TIME_ANALYZER = True
except ImportError:
    HAS_TIME_ANALYZER = False


class LotteryAnalyzer:
    """Advanced lottery number analytics and prediction engine"""
    
    def __init__(self, winning_numbers: List[str]):
        """
        Initialize analyzer with winning numbers
        
        Args:
            winning_numbers: List of winning lottery numbers (as strings)
        """
        self.winning_numbers = [int(num) for num in winning_numbers if num.isdigit()]
        self.analysis_results = {}
        print(f"[ANALYZER] Initialized with {len(self.winning_numbers)} winning numbers")
        
    def analyze_all(self) -> Dict:
        """Run complete intelligence analysis"""
        print("\n" + "="*60)
        print("[ANALYZER] Starting Lottery Intelligence Analysis...")
        print("="*60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_numbers': len(self.winning_numbers),
            'frequency_analysis': self._frequency_analysis(),
            'statistical_metrics': self._statistical_metrics(),
            'digit_patterns': self._digit_patterns(),
            'sum_analysis': self._sum_analysis(),
            'recency_analysis': self._recency_analysis(),
            'series_analysis': self._series_analysis(),
            'predicted_hot_numbers': self._predict_hot_numbers(),
            'probability_scores': self._calculate_probability_scores(),
            'recommendations': self._generate_recommendations(),
        }
        
        self.analysis_results = results
        self._print_results(results)
        
        return results
    
    
    def _frequency_analysis(self) -> Dict:
        """Analyze frequency of each winning number"""
        print("[ANALYZER] Running frequency analysis...")
        
        if not self.winning_numbers:
            return {}
        
        # Count occurrences
        frequency = Counter(self.winning_numbers)
        
        # Find hot and cold numbers
        sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        
        hot_numbers = [num for num, count in sorted_freq[:10]]  # Top 10 most frequent
        cold_numbers = [num for num, count in sorted_freq[-10:] if count > 0]  # Least frequent
        
        results = {
            'most_frequent': sorted_freq[:5],
            'hot_numbers': hot_numbers,
            'cold_numbers': cold_numbers,
            'hot_frequency_pct': len(hot_numbers) / len(set(self.winning_numbers)) * 100,
            'cold_frequency_pct': len(cold_numbers) / len(set(self.winning_numbers)) * 100,
        }
        
        print(f"[ANALYZER] Top 5 most frequent numbers: {sorted_freq[:5]}")
        return results
    
    
    def _statistical_metrics(self) -> Dict:
        """Calculate statistical metrics"""
        print("[ANALYZER] Calculating statistical metrics...")
        
        if not self.winning_numbers:
            return {}
        
        numbers_array = np.array(self.winning_numbers)
        
        results = {
            'mean': float(np.mean(numbers_array)),
            'median': float(np.median(numbers_array)),
            'std_dev': float(np.std(numbers_array)),
            'min': int(np.min(numbers_array)),
            'max': int(np.max(numbers_array)),
            'range': int(np.max(numbers_array) - np.min(numbers_array)),
            'variance': float(np.var(numbers_array)),
        }
        
        print(f"[ANALYZER] Mean: {results['mean']:.2f}, StdDev: {results['std_dev']:.2f}")
        return results
    
    
    def _digit_patterns(self) -> Dict:
        """Analyze digit patterns in numbers"""
        print("[ANALYZER] Analyzing digit patterns...")
        
        # Convert all numbers to strings for digit analysis
        number_strings = [str(num).zfill(5) for num in self.winning_numbers]
        
        # Analyze each digit position
        digit_analysis = {}
        for position in range(5):
            digits = [int(num[position]) for num in number_strings]
            digit_freq = Counter(digits)
            digit_analysis[f'position_{position}'] = dict(digit_freq)
        
        # Find repeating digits
        repeating_digits = []
        for num_str in number_strings:
            for digit in set(num_str):
                if num_str.count(digit) > 1:
                    repeating_digits.append((int(num_str), digit, num_str.count(digit)))
        
        results = {
            'digit_positions': digit_analysis,
            'repeating_digit_numbers': repeating_digits[:10],
            'unique_digits_avg': np.mean([len(set(num)) for num in number_strings]),
        }
        
        print(f"[ANALYZER] Found {len(repeating_digits)} numbers with repeating digits")
        return results
    
    
    def _sum_analysis(self) -> Dict:
        """Analyze sum and digit sum patterns"""
        print("[ANALYZER] Analyzing sum patterns...")
        
        # Calculate sums
        sums = [sum([int(d) for d in str(num).zfill(5)]) for num in self.winning_numbers]
        sum_counter = Counter(sums)
        
        results = {
            'digit_sums': dict(sum_counter),
            'most_common_sum': sum_counter.most_common(1)[0] if sum_counter else None,
            'sum_range': (min(sums), max(sums)) if sums else None,
            'sum_average': np.mean(sums) if sums else None,
        }
        
        print(f"[ANALYZER] Most common digit sum: {results['most_common_sum']}")
        return results
    
    
    def _recency_analysis(self) -> Dict:
        """Analyze recency and gaps between appearances"""
        print("[ANALYZER] Analyzing recency patterns...")
        
        if not self.winning_numbers:
            return {}
        
        # Sort numbers by appearance (assuming chronological order)
        sorted_numbers = sorted(self.winning_numbers)
        
        # Calculate gaps between consecutive appearances
        gaps = {}
        last_seen = {}
        
        for i, num in enumerate(sorted_numbers):
            if num in last_seen:
                gap = i - last_seen[num]
                if num not in gaps:
                    gaps[num] = []
                gaps[num].append(gap)
            last_seen[num] = i
        
        # Calculate average gap and recency score
        recency_scores = {}
        current_position = len(sorted_numbers)
        
        for num in set(self.winning_numbers):
            if num in gaps and gaps[num]:
                avg_gap = np.mean(gaps[num])
                # Recency score: lower gap = higher recency score
                recency_scores[num] = max(0, 100 - avg_gap * 10)
            else:
                # Numbers that appeared only once get moderate score
                recency_scores[num] = 50
        
        # Identify overdue numbers (high gap, low recent appearances)
        overdue_numbers = []
        for num, score in recency_scores.items():
            if score < 30:  # Low recency score = overdue
                overdue_numbers.append((num, score))
        
        overdue_numbers.sort(key=lambda x: x[1])  # Sort by lowest score (most overdue)
        
        results = {
            'recency_scores': recency_scores,
            'overdue_numbers': overdue_numbers[:10],  # Top 10 most overdue
            'average_gap': np.mean([gap for gaps_list in gaps.values() for gap in gaps_list]) if gaps else 0,
            'hot_streak_numbers': [num for num, score in recency_scores.items() if score > 80][:5],
        }
        
        print(f"[ANALYZER] Found {len(overdue_numbers)} overdue numbers")
        print(f"[ANALYZER] Hot streak numbers: {results['hot_streak_numbers']}")
        return results
    
    
    def _series_analysis(self) -> Dict:
        """Analyze patterns by first two digits (series)"""
        print("[ANALYZER] Analyzing series patterns...")
        
        if not self.winning_numbers:
            return {}
        
        # Group by series (first two digits)
        series_groups = defaultdict(list)
        for num in self.winning_numbers:
            series = str(num)[:2]  # First two digits
            series_groups[series].append(num)
        
        # Calculate series statistics
        series_stats = {}
        for series, numbers in series_groups.items():
            series_stats[series] = {
                'count': len(numbers),
                'frequency': len(numbers) / len(self.winning_numbers) * 100,
                'avg_number': np.mean(numbers),
                'numbers': numbers[:5],  # Sample numbers
            }
        
        # Find dominant series
        dominant_series = sorted(series_stats.items(), 
                                key=lambda x: x[1]['count'], reverse=True)[:5]
        
        # Series diversity analysis
        total_series = len(series_stats)
        concentration_ratio = max([stats['count'] for stats in series_stats.values()]) / len(self.winning_numbers)
        
        results = {
            'series_distribution': dict(series_stats),
            'dominant_series': dominant_series,
            'total_series': total_series,
            'concentration_ratio': concentration_ratio,
            'series_recommendations': self._generate_series_recommendations(series_stats),
        }
        
        print(f"[ANALYZER] Found {total_series} different series")
        print(f"[ANALYZER] Top series: {[s[0] for s in dominant_series[:3]]}")
        return results
    
    
    def _generate_series_recommendations(self, series_stats: Dict) -> List[str]:
        """Generate recommendations based on series analysis"""
        recommendations = []
        
        if not series_stats:
            return recommendations
        
        # Recommend dominant series
        dominant = sorted(series_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        if dominant:
            top_series = dominant[0][0]
            top_count = dominant[0][1]['count']
            recommendations.append(
                f"Focus on {top_series}xx series - appeared {top_count} times ({series_stats[top_series]['frequency']:.1f}%)"
            )
        
        # Recommend underrepresented series (potential value)
        underrepresented = [s for s, stats in series_stats.items() 
                          if stats['count'] == min([st['count'] for st in series_stats.values()])]
        if underrepresented:
            recommendations.append(
                f"Consider {underrepresented[0]}xx series - underrepresented but statistically due"
            )
        
        # Diversity recommendation
        total_series = len(series_stats)
        if total_series > 10:
            recommendations.append(
                f"High series diversity ({total_series} series) - mix different series for better coverage"
            )
        
        return recommendations
    
    
    def _predict_hot_numbers(self) -> List[int]:
        """Predict next hot numbers based on patterns"""
        print("[ANALYZER] Predicting hot numbers...")
        
        if not self.winning_numbers:
            return []
        
        # Score based on multiple factors
        number_scores = {}
        
        # Factor 1: Frequency
        freq_counter = Counter(self.winning_numbers)
        max_freq = max(freq_counter.values()) if freq_counter else 1
        for num, freq in freq_counter.items():
            number_scores[num] = (freq / max_freq) * 40  # 40% weight
        
        # Factor 2: Statistical closeness to mean
        mean = np.mean(self.winning_numbers)
        std = np.std(self.winning_numbers) or 1
        for num in set(self.winning_numbers):
            z_score = abs((num - mean) / std)
            closeness_score = max(0, 100 - z_score * 10) / 100 * 30  # 30% weight
            number_scores[num] = number_scores.get(num, 0) + closeness_score
        
        # Factor 3: Recent wins (recency bonus)
        unique_numbers = list(set(self.winning_numbers))[-10:] if self.winning_numbers else []
        for num in unique_numbers:
            number_scores[num] = number_scores.get(num, 0) + 30  # 30% weight
        
        # Sort and return top predictions
        sorted_predictions = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)
        hot_numbers = [int(num) for num, score in sorted_predictions[:10]]
        
        print(f"[ANALYZER] Top 10 predicted hot numbers: {hot_numbers}")
        return hot_numbers
    
    
    def _calculate_probability_scores(self) -> Dict[int, float]:
        """Calculate probability score (0-100) for each number"""
        print("[ANALYZER] Calculating probability scores...")
        
        probability_scores = {}
        
        # Base score from frequency
        freq_counter = Counter(self.winning_numbers)
        max_count = max(freq_counter.values()) if freq_counter else 1
        
        all_possible = range(10000, 100000)  # 5-digit range
        
        for num in all_possible:
            score = 0
            
            # 1. Frequency (40%)
            count = freq_counter.get(num, 0)
            freq_score = (count / max_count * 100) if max_count > 0 else 0
            score += freq_score * 0.40
            
            # 2. Recency (20%) - numbers that appeared recently get bonus
            if num in set(self.winning_numbers[-5:]):
                score += 100 * 0.20
            elif num in set(self.winning_numbers[-10:]):
                score += 80 * 0.20
            else:
                score += max(0, 50 - count * 5) * 0.20
            
            # 3. Statistical position (20%) - numbers near mean are more likely
            mean = np.mean(self.winning_numbers)
            std = np.std(self.winning_numbers) or 1
            z_score = abs((num - mean) / std)
            stat_score = max(0, 100 - z_score * 15)
            score += stat_score * 0.20
            
            # 4. Digit pattern match (10%) - numbers with common digit patterns
            digit_sum = sum([int(d) for d in str(num).zfill(5)])
            common_sums = Counter([sum([int(d) for d in str(n).zfill(5)]) 
                                   for n in self.winning_numbers])
            if common_sums and digit_sum in common_sums:
                digit_score = (common_sums[digit_sum] / len(self.winning_numbers)) * 100
                score += digit_score * 0.10
            
            # 5. Avoided number bonus (10%) - numbers never seen get small bonus (diversity)
            if count == 0:
                score += 15 * 0.10  # Small chance for undiscovered numbers
            
            probability_scores[num] = min(100, score)
        
        # Return only top 50 numbers for display
        sorted_scores = sorted(probability_scores.items(), key=lambda x: x[1], reverse=True)
        top_50 = dict(sorted_scores[:50])
        
        print(f"[ANALYZER] Calculated probability scores for numbers")
        print(f"[ANALYZER] Top 5 scores: {sorted_scores[:5]}")
        
        return top_50
    
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        print("[ANALYZER] Generating recommendations...")
        
        recommendations = []
        
        if not self.winning_numbers:
            return recommendations
        
        # Recommendation 1: Based on frequency
        freq_counter = Counter(self.winning_numbers)
        if freq_counter:
            most_common = freq_counter.most_common(1)[0][0]
            recommendations.append(
                f"Play {most_common} - it's the most frequent winner ({freq_counter[most_common]} times)"
            )
        
        # Recommendation 2: Based on cold numbers
        rank = sorted([(num, count) for num, count in freq_counter.items()], 
                     key=lambda x: x[1])
        if rank:
            coldest = rank[0][0]
            recommendations.append(
                f"Consider {coldest} - cold numbers are statistically 'due' ({rank[0][1]} appearances)"
            )
        
        # Recommendation 3: Based on statistics
        mean = np.mean(self.winning_numbers)
        recommendations.append(
            f"Average winning number is {mean:.0f} - numbers near this value have higher probability"
        )
        
        # Recommendation 4: Diversity strategy
        recommendations.append(
            "Mix hot (frequent) and cold (rare) numbers for balanced odds"
        )
        
        # Recommendation 5: Pattern matching
        unique_nums = len(set(self.winning_numbers))
        total_nums = len(self.winning_numbers)
        diversity_ratio = unique_nums / total_nums if total_nums > 0 else 0
        recommendations.append(
            f"Diversity ratio is {diversity_ratio:.2%} - favor numbers with varied digit patterns"
        )
        
        return recommendations
    
    
    def _print_results(self, results: Dict):
        """Pretty print analysis results"""
        print("\n" + "-"*60)
        print("LOTTERY INTELLIGENCE REPORT")
        print("-"*60)
        
        # Frequency
        if results['frequency_analysis']:
            print("\n[FREQUENCY ANALYSIS]")
            freq = results['frequency_analysis']
            print(f"  Hot Numbers (top 10): {freq.get('hot_numbers', [])}")
            print(f"  Cold Numbers (bottom 10): {freq.get('cold_numbers', [])}")
        
        # Statistics
        if results['statistical_metrics']:
            print("\n[STATISTICAL METRICS]")
            stat = results['statistical_metrics']
            print(f"  Mean: {stat.get('mean', 0):.0f}")
            print(f"  Median: {stat.get('median', 0):.0f}")
            print(f"  Std Dev: {stat.get('std_dev', 0):.0f}")
            print(f"  Range: {stat.get('min', 0)} - {stat.get('max', 0)}")
        
        # Recency Analysis
        if results.get('recency_analysis'):
            print("\n[RECENCY ANALYSIS]")
            recency = results['recency_analysis']
            print(f"  Overdue Numbers (most due): {[num for num, score in recency.get('overdue_numbers', [])[:3]]}")
            print(f"  Hot Streak Numbers: {recency.get('hot_streak_numbers', [])}")
            print(f"  Average Gap: {recency.get('average_gap', 0):.1f}")
        
        # Series Analysis
        if results.get('series_analysis'):
            print("\n[SERIES ANALYSIS (First 2 Digits)]")
            series = results['series_analysis']
            dominant = series.get('dominant_series', [])[:3]
            print(f"  Dominant Series: {[(s[0], s[1]['count']) for s in dominant]}")
            print(f"  Total Series: {series.get('total_series', 0)}")
            print(f"  Concentration Ratio: {series.get('concentration_ratio', 0):.2%}")
        
        # Predictions
        if results['predicted_hot_numbers']:
            print("\n[PREDICTED HOT NUMBERS (Next Likely Winners)]")
            print(f"  {results['predicted_hot_numbers']}")
        
        # Top Probability Scores
        if results['probability_scores']:
            print("\n[TOP 10 PROBABILITY SCORES]")
            top_10 = sorted(results['probability_scores'].items(), 
                           key=lambda x: x[1], reverse=True)[:10]
            for num, score in top_10:
                bar = "[" + "="*int(score/5) + " "*(20-int(score/5)) + "]"
                print(f"  {num:5d}: {bar} {score:.1f}%")
        
        # Recommendations
        if results['recommendations']:
            print("\n[SMART RECOMMENDATIONS]")
            for i, rec in enumerate(results['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "-"*60)
    
    
    def export_to_sheet(self, worksheet) -> bool:
        """Export analysis results to Google Sheet"""
        try:
            print("\n[SHEET] Exporting analysis results...")
            
            # Create analysis summary
            summary_data = [
                ['LOTTERY INTELLIGENCE ANALYSIS', ''],
                ['Generated', self.analysis_results.get('timestamp', '')],
                ['Total Numbers Analyzed', self.analysis_results.get('total_numbers', 0)],
                ['', ''],
                ['PROBABILITY TOP 10', 'SCORE'],
            ]
            
            # Add top 10 probability scores
            if self.analysis_results.get('probability_scores'):
                top_10 = sorted(self.analysis_results['probability_scores'].items(),
                              key=lambda x: x[1], reverse=True)[:10]
                for num, score in top_10:
                    summary_data.append([str(num), f"{score:.1f}%"])
            
            # Add recommendations section
            summary_data.append(['', ''])
            summary_data.append(['SMART RECOMMENDATIONS', ''])
            for rec in self.analysis_results.get('recommendations', []):
                summary_data.append([rec, ''])
            
            # Append to sheet
            worksheet.append_rows(summary_data)
            print("[SHEET] [OK] Analysis exported successfully")
            return True
            
        except Exception as e:
            print(f"[SHEET] [ERROR] Failed to export: {str(e)}")
            return False
    
    
    def create_frequency_heatmap(self, worksheet) -> bool:
        """Create color-coded frequency vs recency heatmap"""
        try:
            print("\n[HEATMAP] Creating Frequency vs Recency Heatmap...")
            
            # Get recency and frequency data
            recency_data = self.analysis_results.get('recency_analysis', {})
            freq_data = self.analysis_results.get('frequency_analysis', {})
            
            if not recency_data or not freq_data:
                print("[HEATMAP] Insufficient data for heatmap")
                return False
            
            # Prepare heatmap data
            heatmap_data = [
                ['FREQUENCY vs RECENCY HEATMAP', '', '', ''],
                ['Number', 'Frequency', 'Recency Score', 'Heat Level'],
                ['', '', '', ''],
            ]
            
            # Get all unique numbers
            all_numbers = set(self.winning_numbers)
            
            # Create frequency counter
            freq_counter = Counter(self.winning_numbers)
            
            # Build heatmap rows
            heatmap_rows = []
            for num in sorted(all_numbers):
                freq = freq_counter.get(num, 0)
                recency = recency_data.get('recency_scores', {}).get(num, 0)
                
                # Calculate heat level (0-100)
                heat_level = (freq * 0.6 + recency * 0.4)
                
                # Determine color category
                if heat_level >= 80:
                    color = "🔴 HOT"
                elif heat_level >= 60:
                    color = "🟠 WARM"
                elif heat_level >= 40:
                    color = "🟡 MODERATE"
                elif heat_level >= 20:
                    color = "🔵 COLD"
                else:
                    color = "🟣 OVERDUE"
                
                heatmap_rows.append([str(num), freq, f"{recency:.1f}", color])
            
            # Sort by heat level descending
            heatmap_rows.sort(key=lambda x: (freq_counter.get(int(x[0]), 0) * 0.6 + 
                                           recency_data.get('recency_scores', {}).get(int(x[0]), 0) * 0.4), 
                            reverse=True)
            
            # Add top 50 to sheet
            heatmap_data.extend(heatmap_rows[:50])
            
            # Add summary
            heatmap_data.extend([
                ['', '', '', ''],
                ['HEATMAP LEGEND', '', '', ''],
                ['🔴 HOT', 'High frequency + high recency', '', ''],
                ['🟠 WARM', 'Good frequency or recency', '', ''],
                ['🟡 MODERATE', 'Average performance', '', ''],
                ['🔵 COLD', 'Low frequency + low recency', '', ''],
                ['🟣 OVERDUE', 'Very low scores - statistically due', '', ''],
            ])
            
            # Clear and update worksheet
            worksheet.clear()
            worksheet.append_rows(heatmap_data)
            
            print("[HEATMAP] [OK] Frequency heatmap created successfully")
            return True
            
        except Exception as e:
            print(f"[HEATMAP] [ERROR] Failed to create heatmap: {str(e)}")
            return False
