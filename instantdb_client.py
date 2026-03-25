"""
InstantDB Integration for Lottery Intelligence System
Real-time database client with cloud sync capabilities
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import time


class InstantDBClient:
    """Client for InstantDB cloud database integration"""
    
    def __init__(self, app_id: str, token: str = None):
        """
        Initialize InstantDB client
        
        Args:
            app_id: Your InstantDB public app ID
            token: Optional authentication token
        """
        self.app_id = app_id
        self.token = token
        self.base_url = f"https://api.instant.dev"
        self.api_url = f"{self.base_url}/apps/{app_id}"
        
        # Headers for API requests
        self.headers = {
            'Content-Type': 'application/json',
        }
        
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
        
        print(f"[INSTANTDB] Initialized with App ID: {app_id}")
    
    
    def insert_winning_number(self, number: int, draw_time: str, draw_date: str = None) -> Dict:
        """Insert a winning lottery number into InstantDB"""
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
            # InstantDB uses transactions for writes
            response = requests.post(
                f"{self.api_url}/transaction",
                headers=self.headers,
                json={
                    "tx": [
                        {
                            "op": "set",
                            "id": ["winning_numbers", f"{number}_{draw_date}_{draw_time}"],
                            "value": data
                        }
                    ]
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"[INSTANTDB] Inserted winning number: {number}")
                return data
            else:
                print(f"[INSTANTDB] Error inserting number: {response.text}")
                return None
                
        except Exception as e:
            print(f"[INSTANTDB] Connection error: {str(e)}")
            return None
    
    
    def save_analysis_results(self, analysis_type: str, results: Dict) -> bool:
        """Save analysis results to InstantDB"""
        try:
            data = {
                "type": analysis_type,
                "results": json.dumps(results, default=str),
                "created_at": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.api_url}/transaction",
                headers=self.headers,
                json={
                    "tx": [
                        {
                            "op": "set",
                            "id": ["analysis_results", f"{analysis_type}_{int(time.time())}"],
                            "value": data
                        }
                    ]
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"[INSTANTDB] Saved analysis: {analysis_type}")
                return True
            else:
                print(f"[INSTANTDB] Error saving analysis: {response.text}")
                return False
                
        except Exception as e:
            print(f"[INSTANTDB] Connection error: {str(e)}")
            return False
    
    
    def save_predictions(self, draw_time: str, predicted_numbers: List[int], confidence_score: float = None) -> bool:
        """Save predictions to InstantDB"""
        try:
            data = {
                "draw_time": draw_time,
                "predicted_numbers": predicted_numbers,
                "confidence_score": confidence_score,
                "created_at": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.api_url}/transaction",
                headers=self.headers,
                json={
                    "tx": [
                        {
                            "op": "set",
                            "id": ["predictions", f"{draw_time}_{int(time.time())}"],
                            "value": data
                        }
                    ]
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"[INSTANTDB] Saved predictions for {draw_time}")
                return True
            else:
                print(f"[INSTANTDB] Error saving predictions: {response.text}")
                return False
                
        except Exception as e:
            print(f"[INSTANTDB] Connection error: {str(e)}")
            return False
    
    
    def get_winning_numbers(self, limit: int = None, draw_time: str = None) -> List[int]:
        """Get winning numbers from InstantDB"""
        try:
            response = requests.get(
                f"{self.api_url}/query",
                headers=self.headers,
                json={
                    "q": {
                        "winning_numbers": {}
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                numbers = []
                
                if "winning_numbers" in data:
                    for record in data["winning_numbers"].values():
                        if draw_time is None or record.get("draw_time") == draw_time:
                            numbers.append(record.get("number"))
                
                if limit:
                    numbers = numbers[-limit:]
                
                print(f"[INSTANTDB] Retrieved {len(numbers)} winning numbers")
                return numbers
            else:
                print(f"[INSTANTDB] Error querying: {response.text}")
                return []
                
        except Exception as e:
            print(f"[INSTANTDB] Connection error: {str(e)}")
            return []
    
    
    def get_recent_predictions(self, limit: int = 5) -> List[Dict]:
        """Get recent predictions from InstantDB"""
        try:
            response = requests.get(
                f"{self.api_url}/query",
                headers=self.headers,
                json={
                    "q": {
                        "predictions": {}
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                predictions = []
                
                if "predictions" in data:
                    for record in list(data["predictions"].values())[-limit:]:
                        predictions.append({
                            "draw_time": record.get("draw_time"),
                            "predicted_numbers": record.get("predicted_numbers"),
                            "confidence_score": record.get("confidence_score"),
                            "created_at": record.get("created_at")
                        })
                
                print(f"[INSTANTDB] Retrieved {len(predictions)} recent predictions")
                return predictions
            else:
                print(f"[INSTANTDB] Error querying: {response.text}")
                return []
                
        except Exception as e:
            print(f"[INSTANTDB] Connection error: {str(e)}")
            return []
    
    
    def log_notification(self, notification_type: str, message: str, recipient: str = None) -> bool:
        """Log notification to InstantDB"""
        try:
            data = {
                "type": notification_type,
                "message": message,
                "recipient": recipient,
                "sent_at": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.api_url}/transaction",
                headers=self.headers,
                json={
                    "tx": [
                        {
                            "op": "set",
                            "id": ["notifications", f"{notification_type}_{int(time.time())}"],
                            "value": data
                        }
                    ]
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"[INSTANTDB] Logged notification: {notification_type}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"[INSTANTDB] Connection error: {str(e)}")
            return False
    
    
    def get_statistics(self) -> Dict:
        """Get database statistics from InstantDB"""
        try:
            response = requests.get(
                f"{self.api_url}/query",
                headers=self.headers,
                json={
                    "q": {
                        "winning_numbers": {},
                        "predictions": {},
                        "analysis_results": {}
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                stats = {
                    'total_numbers': len(data.get('winning_numbers', {})),
                    'total_predictions': len(data.get('predictions', {})),
                    'total_analyses': len(data.get('analysis_results', {})),
                    'last_update': datetime.now().isoformat(),
                    'database_type': 'InstantDB Cloud',
                    'app_id': self.app_id
                }
                
                print(f"[INSTANTDB] Stats: {stats['total_numbers']} numbers, {stats['total_predictions']} predictions")
                return stats
            else:
                return {
                    'error': 'Failed to retrieve statistics',
                    'app_id': self.app_id
                }
                
        except Exception as e:
            print(f"[INSTANTDB] Error getting statistics: {str(e)}")
            return {'error': str(e)}


# Example usage and initialization
if __name__ == "__main__":
    # Initialize with your app ID
    APP_ID = "c3ea4e7d-54d0-41a3-b54c-6fc837fc9573"
    
    client = InstantDBClient(app_id=APP_ID)
    
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
