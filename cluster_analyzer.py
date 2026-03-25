"""
Pipeline 4: Cluster & Neighbor Analysis
Looks for Series Clusters (first 2 digits) and correlates with Draw Times.
"""

import pandas as pd
from collections import Counter
from typing import List, Dict

class ClusterAnalyzer:
    def __init__(self, historical_data: pd.DataFrame):
        self.df = historical_data

    def analyze_series_clusters(self) -> Dict:
        """
        Groups numbers by their first 2 digits (Series).
        Returns which series are hitting hardest at which times.
        """
        # Extract Series
        self.df['series'] = self.df['number'].apply(lambda x: str(x).zfill(5)[:2])
        
        # Group by Time and Series
        cluster_stats = self.df.groupby(['draw_time', 'series']).size().reset_index(name='count')
        
        results = {}
        for time in self.df['draw_time'].unique():
            time_clusters = cluster_stats[cluster_stats['draw_time'] == time]
            top_series = time_clusters.sort_values('count', reverse=True).head(3)
            
            results[time] = {
                "top_series": top_series['series'].tolist(),
                "counts": top_series['count'].tolist(),
                "summary": f"The {time} draw is hitting the {', '.join(top_series['series'].tolist())}-series hard."
            }
            
        return results

    def get_neighbor_patterns(self) -> List[Dict]:
        """
        Identifies if certain numbers appear 'neighbors' (e.g. 12345 followed by 12346).
        """
        sorted_df = self.df.sort_values(['draw_date', 'draw_time', 'number'])
        neighbors = []
        
        # Simple neighbor check: consecutive numbers in the same draw
        for (date, time), group in sorted_df.groupby(['draw_date', 'draw_time']):
            nums = sorted(group['number'].tolist())
            for i in range(len(nums) - 1):
                if nums[i+1] - nums[i] == 1:
                    neighbors.append({
                        "date": str(date),
                        "time": time,
                        "pair": (nums[i], nums[i+1])
                    })
                    
        return neighbors
