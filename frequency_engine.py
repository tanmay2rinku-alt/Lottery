"""
Pipeline 3: Frequency Heatmap Engine
Calculates "Gap" for every number and generates "Recency vs. Frequency" matrix.
"""

import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
from typing import List, Dict

class FrequencyEngine:
    def __init__(self, historical_data: pd.DataFrame):
        """
        historical_data: DataFrame with columns ['number', 'draw_date', 'draw_time']
        """
        self.df = historical_data
        self.df['draw_date'] = pd.to_datetime(self.df['draw_date'])
        self.df = self.df.sort_values('draw_date')

    def calculate_gaps(self) -> Dict:
        """
        Calculate actual gap vs average gap for each number.
        Gap is the number of draws between appearances.
        """
        results = {}
        unique_numbers = self.df['number'].unique()
        total_draws = len(self.df['draw_date'].unique())

        for num in unique_numbers:
            # Indices of draws where this number appeared
            num_draws = self.df[self.df['number'] == num]['draw_date'].unique()
            num_draws = sorted(num_draws)
            
            if len(num_draws) < 2:
                results[num] = {
                    "avg_gap": total_draws, # Default to total period if only seen once
                    "current_gap": (datetime.now() - pd.Timestamp(num_draws[0])).days,
                    "status": "Cold"
                }
                continue

            # Calculate gaps in days between appearances
            gaps = []
            for i in range(1, len(num_draws)):
                gap = (pd.Timestamp(num_draws[i]) - pd.Timestamp(num_draws[i-1])).days
                gaps.append(gap)
            
            avg_gap = np.mean(gaps)
            last_appearance = pd.Timestamp(num_draws[-1])
            current_gap = (datetime.now() - last_appearance).days
            
            # Logic: If current gap is 1.5x larger than average, it's Overdue
            is_overdue = current_gap > (avg_gap * 1.5)
            
            results[num] = {
                "avg_gap": round(float(avg_gap), 2),
                "current_gap": int(current_gap),
                "is_overdue": bool(is_overdue),
                "frequency": len(num_draws),
                "status": "Overdue" if is_overdue else "Neutral"
            }

        return results

    def generate_heatmap_data(self) -> List[Dict]:
        """
        Generates data for color-coding:
        Hot (Frequent): Red
        Cold (Overdue): Blue
        """
        gaps = self.calculate_gaps()
        heatmap = []
        
        for num, data in gaps.items():
            # Heat Score: High frequency + Low current gap = High Heat
            # We normalize frequency and recency
            freq = data['frequency']
            recency = 1 / (data['current_gap'] + 1)
            
            heat_score = freq * recency
            
            color = "Red" if heat_score > 0.5 or (not data['is_overdue'] and freq > 5) else "Blue" if data['is_overdue'] else "Gray"
            
            heatmap.append({
                "number": int(num),
                "frequency": freq,
                "avg_gap": data['avg_gap'],
                "current_gap": data['current_gap'],
                "status": data['status'],
                "color_code": color
            })
            
        return sorted(heatmap, key=lambda x: x['frequency'], reverse=True)
