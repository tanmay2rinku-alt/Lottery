"""
Draw Time Recommender
Analyzes which lottery draw time (1PM, 6PM, 8PM) has highest winning probability
"""

import pandas as pd
from collections import Counter
from typing import Dict, Tuple


class DrawTimeAnalyzer:
    """Analyzes draw times to recommend optimal play time"""
    
    def __init__(self, winning_numbers: list, draw_times: list):
        """
        Initialize with winning numbers and their corresponding draw times
        
        Args:
            winning_numbers: List of winning lottery numbers
            draw_times: List of draw times (1PM, 6PM, 8PM) corresponding to numbers
        """
        self.winning_numbers = winning_numbers
        self.draw_times = draw_times
        self.analysis = {}
        
    def analyze(self) -> Dict:
        """Analyze draw times and return recommendations"""
        print("\n[DRAW_TIME] Analyzing draw time patterns...")
        
        # Count frequency by draw time
        time_counter = Counter(self.draw_times)
        total = sum(time_counter.values())
        
        # Calculate probabilities
        time_probs = {}
        for time, count in time_counter.items():
            prob = (count / total * 100) if total > 0 else 0
            time_probs[time] = {
                'count': count,
                'probability': prob,
                'frequency': f"{count}/{total}"
            }
        
        # Rank by probability
        ranked = sorted(time_probs.items(), key=lambda x: x[1]['probability'], reverse=True)
        
        print("[DRAW_TIME] Draw Time Analysis Results:")
        for i, (time, data) in enumerate(ranked, 1):
            print(f"  {i}. {time:4s} - {data['probability']:.1f}% ({data['frequency']})")
        
        # Generate recommendation
        best_time = ranked[0][0] if ranked else "1PM"
        best_prob = ranked[0][1]['probability'] if ranked else 0
        
        self.analysis = {
            'best_time': best_time,
            'probability': best_prob,
            'ranked_times': ranked,
            'all_probabilities': time_probs
        }
        
        return self.analysis
    
    def recommend_for_number(self, number: str) -> str:
        """Get recommendation for a specific number"""
        if not self.analysis:
            self.analyze()
        
        return self.analysis.get('best_time', '1PM')


def get_draw_time_recommendation(current_winning_data: list) -> Dict:
    """
    Quick recommendation based on typical lottery patterns
    
    Args:
        current_winning_data: List of (number, draw_time) tuples
    
    Returns:
        Recommendation with reasoning
    """
    
    numbers = [item[0] if isinstance(item, tuple) else item for item in current_winning_data]
    times = [item[1] if isinstance(item, tuple) else '1PM' for item in current_winning_data]
    
    analyzer = DrawTimeAnalyzer(numbers, times)
    analysis = analyzer.analyze()
    
    best_time = analysis['best_time']
    probability = analysis['probability']
    
    recommendation = {
        'recommended_time': best_time,
        'confidence': probability,
        'reasoning': [
            f"Draw time '{best_time}' has {probability:.1f}% frequency in winning data",
            f"This time slot historically produces more winners",
            f"Statistically {best_time} is most active",
        ]
    }
    
    return recommendation
