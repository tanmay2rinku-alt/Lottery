"""
Supabase Integration for Lottery Intelligence System
Cloud database client with real-time capabilities
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from supabase import create_client, Client


class SupabaseClient:
    """Client for Supabase cloud database integration"""

    def __init__(self, url: str, key: str):
        """
        Initialize Supabase client

        Args:
            url: Supabase project URL
            key: Supabase publishable key
        """
        self.supabase: Client = create_client(url, key)
        print(f"[SUPABASE] Initialized with URL: {url}")

    def insert_winning_number(self, number: int, draw_time: str, draw_date: str = None) -> Dict:
        """Insert a winning lottery number into Supabase"""
        if draw_date is None:
            draw_date = datetime.now().strftime("%Y-%m-%d")

        series = str(number)[:2]
        digit_sum = sum(int(d) for d in str(number))

        data = {
            "number": number,
            "draw_time": draw_time,
            "draw_date": draw_date,
            "series": series,
            "digit_sum": digit_sum,
            "created_at": datetime.now().isoformat()
        }

        try:
            response = self.supabase.table('winning_numbers').insert(data).execute()
            if response.data:
                print(f"[SUPABASE] Inserted winning number: {number}")
                return data
            else:
                err_msg = getattr(response, 'error', response)
                print(f"[SUPABASE] Error inserting number: {err_msg}")
                return None

        except Exception as e:
            print(f"[SUPABASE] Connection error: {str(e)}")
            return None

    def save_analysis_results(self, analysis_type: str, results: Dict) -> bool:
        """Save analysis results to Supabase"""
        try:
            data = {
                "analysis_type": analysis_type,
                "results_json": json.dumps(results, default=str),
                "created_at": datetime.now().isoformat()
            }

            response = self.supabase.table('analysis_results').insert(data).execute()

            if response.data:
                print(f"[SUPABASE] Saved analysis: {analysis_type}")
                return True
            else:
                err_msg = getattr(response, 'error', response)
                print(f"[SUPABASE] Error saving analysis: {err_msg}")
                return False

        except Exception as e:
            print(f"[SUPABASE] Connection error: {str(e)}")
            return False

    def save_predictions(self, draw_time: str, predicted_numbers: List[int], confidence_score: float = None) -> bool:
        """Save predictions to Supabase"""
        try:
            data = {
                "draw_time": draw_time,
                "predicted_numbers": json.dumps(predicted_numbers),
                "confidence_score": confidence_score,
                "created_at": datetime.now().isoformat()
            }

            response = self.supabase.table('predictions').insert(data).execute()

            if response.data:
                print(f"[SUPABASE] Saved predictions for {draw_time}")
                return True
            else:
                err_msg = getattr(response, 'error', response)
                print(f"[SUPABASE] Error saving predictions: {err_msg}")
                return False

        except Exception as e:
            print(f"[SUPABASE] Connection error: {str(e)}")
            return False

    def get_winning_numbers(self, limit: int = None, draw_time: str = None) -> List[int]:
        """Get winning numbers from Supabase"""
        try:
            query = self.supabase.table('winning_numbers').select('number')

            if draw_time:
                query = query.eq('draw_time', draw_time)

            query = query.order('draw_date', desc=True)

            if limit:
                query = query.limit(limit)

            response = query.execute()

            if response.data:
                numbers = [record['number'] for record in response.data]
                print(f"[SUPABASE] Retrieved {len(numbers)} winning numbers")
                return numbers
            else:
                print(f"[SUPABASE] Error querying: {response}")
                return []

        except Exception as e:
            print(f"[SUPABASE] Connection error: {str(e)}")
            return []

    def get_recent_predictions(self, limit: int = 5) -> List[Dict]:
        """Get recent predictions from Supabase"""
        try:
            response = self.supabase.table('predictions') \
                .select('*') \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()

            if response.data:
                predictions = []
                for record in response.data:
                    predictions.append({
                        "draw_time": record.get("draw_time"),
                        "predicted_numbers": json.loads(record.get("predicted_numbers", "[]")),
                        "confidence_score": record.get("confidence_score"),
                        "created_at": record.get("created_at")
                    })

                print(f"[SUPABASE] Retrieved {len(predictions)} recent predictions")
                return predictions
            else:
                print(f"[SUPABASE] Error querying: {response}")
                return []

        except Exception as e:
            print(f"[SUPABASE] Connection error: {str(e)}")
            return []

    def log_notification(self, notification_type: str, message: str, recipient: str = None) -> bool:
        """Log notification to Supabase"""
        try:
            data = {
                "notification_type": notification_type,
                "message": message,
                "recipient": recipient,
                "sent_at": datetime.now().isoformat()
            }

            response = self.supabase.table('notifications').insert(data).execute()

            if response.data:
                print(f"[SUPABASE] Logged notification: {notification_type}")
                return True
            else:
                return False

        except Exception as e:
            print(f"[SUPABASE] Connection error: {str(e)}")
            return False

    def get_statistics(self) -> Dict:
        """Get database statistics from Supabase"""
        try:
            # Get counts for each table
            winning_response = self.supabase.table('winning_numbers').select('*').execute()
            predictions_response = self.supabase.table('predictions').select('*').execute()
            analysis_response = self.supabase.table('analysis_results').select('*').execute()

            # Get distinct draw dates
            draw_dates = self.supabase.table('winning_numbers').select('draw_date').execute()
            unique_dates = len(set(record['draw_date'] for record in draw_dates.data if record.get('draw_date'))) if draw_dates.data else 0

            # Get distinct series
            series_data = self.supabase.table('winning_numbers').select('series').execute()
            unique_series = len(set(record['series'] for record in series_data.data if record.get('series'))) if series_data.data else 0

            stats = {
                'total_numbers': len(winning_response.data),
                'total_draws': unique_dates,
                'total_series': unique_series,
                'total_analyses': len(analysis_response.data),
                'total_predictions': len(predictions_response.data),
                'last_update': datetime.now().isoformat(),
                'database_type': 'Supabase Cloud'
            }

            print(f"[SUPABASE] Stats: {stats['total_numbers']} numbers, {stats['total_predictions']} predictions")
            return stats

        except Exception as e:
            print(f"[SUPABASE] Error getting statistics: {str(e)}")
            return {'error': str(e)}

    def get_series_analysis(self) -> Dict:
        """Get series analysis from Supabase"""
        try:
            # This would require more complex aggregation, for now return basic stats
            response = self.supabase.table('winning_numbers').select('series, number').execute()

            if response.data:
                series_data = {}
                for record in response.data:
                    series = record['series']
                    if series not in series_data:
                        series_data[series] = {'count': 0, 'numbers': []}
                    series_data[series]['count'] += 1
                    series_data[series]['numbers'].append(record['number'])

                # Calculate averages
                for series, data in series_data.items():
                    data['avg_number'] = sum(data['numbers']) / len(data['numbers']) if data['numbers'] else 0
                    data['frequency'] = data['count'] / len(response.data) * 100
                    del data['numbers']  # Remove the list to keep it clean

                return series_data
            else:
                return {}

        except Exception as e:
            print(f"[SUPABASE] Error getting series analysis: {str(e)}")
            return {}


# Example usage and initialization
if __name__ == "__main__":
    # Initialize with your Supabase credentials
    SUPABASE_URL = "https://ivduqfljmbmpnjafpqgn.supabase.co"
    SUPABASE_KEY = "sb_publishable_s4UyCW0CYXjXBSTtA_uPkA_eXdtlOPD"

    client = SupabaseClient(url=SUPABASE_URL, key=SUPABASE_KEY)

    # Example: Insert winning numbers
    sample_numbers = [12345, 67890, 23456, 34567]
    for num in sample_numbers:
        client.insert_winning_number(num, "6PM", "2026-03-23")

    # Example: Save predictions
    client.save_predictions("6PM", [88990, 43444, 45678], 0.85)

    # Example: Get statistics
    stats = client.get_statistics()
    print(f"\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")