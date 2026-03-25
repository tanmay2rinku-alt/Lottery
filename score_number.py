#!/usr/bin/env python3
"""
Quick number scorer for user-provided lottery number
"""

from number_scorer import SpecificNumberAnalyzer
import sys

# Historical winning numbers from our analysis
winning_numbers = [
    1234, 10101, 10111, 11223, 12345, 21222, 22334, 23456, 32333, 33445,
    34567, 43444, 44556, 45678, 54555, 55667, 56789, 65666, 66778, 67890,
    76777, 77889, 78901, 87888, 88990, 89012, 90123, 98999, 99001
]

def score_user_number(number_str: str):
    """Score a user-provided number"""
    try:
        target_number = int(number_str)
        
        if target_number < 10000 or target_number > 99999:
            print(f"\n[ERROR] Number must be between 10000-99999")
            return
        
        print(f"\n[SCORER] Initializing analyzer with {len(winning_numbers)} historical wins...")
        analyzer = SpecificNumberAnalyzer(winning_numbers)
        
        # Full analysis
        analysis = analyzer.analyze_number(target_number)
        analyzer.print_detailed_report(analysis)
        
        # Comparison with top numbers
        comparison = analyzer.compare_with_top_numbers(target_number, top_n=10)
        analyzer.print_comparison_report(comparison)
        
        print("\n[RECOMMENDATION]")
        score = analysis['total_score']
        if score >= 75:
            rec = "HIGHLY RECOMMENDED - Play this number!"
        elif score >= 60:
            rec = "RECOMMENDED - Good odds for this number"
        elif score >= 45:
            rec = "MODERATE - Could be worth playing"
        else:
            rec = "LOW PROBABILITY - Better alternatives available"
        
        print(f"  {rec}")
        print(f"  Probability Score: {score:.1f}%")
        
    except ValueError:
        print(f"[ERROR] Invalid number format: {number_str}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        number = sys.argv[1]
    else:
        number = input("Enter lottery number (5 digits): ").strip()
    
    score_user_number(number)
