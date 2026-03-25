"""
Database Migration System
Move from Google Sheets to SQLite for better performance
"""

import sqlite3
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional
import os


class LotteryDatabase:
    """SQLite database for lottery intelligence data"""
    
    def __init__(self, db_path: str = "lottery_intelligence.db"):
        self.db_path = db_path
        self.init_database()
        
        print(f"[DATABASE] Connected to {db_path}")
    
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Winning numbers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS winning_numbers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number INTEGER NOT NULL,
                    draw_time TEXT,
                    draw_date DATE,
                    series TEXT,
                    digit_sum INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_type TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draw_time TEXT NOT NULL,
                    predicted_numbers TEXT NOT NULL,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Notification log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notification_type TEXT NOT NULL,
                    message TEXT,
                    recipient TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    
    def migrate_from_google_sheets(self, gs_client, sheet_name: str = "Lottery_Intelligence"):
        """Migrate data from Google Sheets to SQLite"""
        try:
            print("[MIGRATION] Starting migration from Google Sheets...")
            
            sheet = gs_client.open(sheet_name)
            
            # Get all worksheets
            worksheets = sheet.worksheets()
            
            total_migrated = 0
            
            for worksheet in worksheets:
                worksheet_name = worksheet.title
                
                # Skip analysis worksheets for now
                if worksheet_name.lower() in ['analysis', 'predictions']:
                    continue
                
                print(f"[MIGRATION] Migrating worksheet: {worksheet_name}")
                
                # Get all values
                data = worksheet.get_all_values()
                
                if not data or len(data) < 2:
                    continue
                
                # Parse draw date from worksheet name
                draw_date = self._parse_draw_date(worksheet_name)
                
                # Process each row
                for row in data[1:]:  # Skip header
                    if len(row) >= 2:
                        number = row[0].strip()
                        draw_time = row[1].strip() if len(row) > 1 else worksheet_name
                        
                        if number.isdigit() and len(number) == 5:
                            self.insert_winning_number(
                                int(number),
                                draw_time,
                                draw_date
                            )
                            total_migrated += 1
            
            print(f"[MIGRATION] Successfully migrated {total_migrated} records")
            return True
            
        except Exception as e:
            print(f"[MIGRATION] Migration failed: {str(e)}")
            return False
    
    
    def _parse_draw_date(self, worksheet_name: str) -> str:
        """Parse draw date from worksheet name"""
        # Try DD-MM-YYYY format
        try:
            date_obj = datetime.strptime(worksheet_name, "%d-%m-%Y")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            # Default to today
            return datetime.now().strftime("%Y-%m-%d")
    
    
    def insert_winning_number(self, number: int, draw_time: str, draw_date: str = None):
        """Insert a winning number into the database"""
        if draw_date is None:
            draw_date = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate additional fields
        series = str(number)[:2]
        digit_sum = sum(int(d) for d in str(number))
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO winning_numbers (number, draw_time, draw_date, series, digit_sum)
                VALUES (?, ?, ?, ?, ?)
            ''', (number, draw_time, draw_date, series, digit_sum))
            
            conn.commit()
    
    
    def save_analysis_results(self, analysis_type: str, results: Dict):
        """Save analysis results to database"""
        results_json = json.dumps(results, default=str)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analysis_results (analysis_type, results_json)
                VALUES (?, ?)
            ''', (analysis_type, results_json))
            
            conn.commit()
    
    
    def save_predictions(self, draw_time: str, predicted_numbers: List[int], confidence_score: float = None):
        """Save predictions to database"""
        numbers_json = json.dumps(predicted_numbers)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO predictions (draw_time, predicted_numbers, confidence_score)
                VALUES (?, ?, ?)
            ''', (draw_time, numbers_json, confidence_score))
            
            conn.commit()
    
    
    def get_winning_numbers(self, limit: int = None, draw_time: str = None) -> List[int]:
        """Get winning numbers from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT number FROM winning_numbers"
            params = []
            
            if draw_time:
                query += " WHERE draw_time = ?"
                params.append(draw_time)
            
            query += " ORDER BY draw_date DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [row[0] for row in results]
    
    
    def get_series_analysis(self) -> Dict:
        """Get series analysis from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT series, COUNT(*) as count,
                       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM winning_numbers) as frequency,
                       AVG(number) as avg_number
                FROM winning_numbers
                GROUP BY series
                ORDER BY count DESC
            ''')
            
            results = cursor.fetchall()
            
            series_data = {}
            for row in results:
                series_data[row[0]] = {
                    'count': row[1],
                    'frequency': row[2],
                    'avg_number': row[3]
                }
            
            return series_data
    
    
    def get_recent_predictions(self, limit: int = 5) -> List[Dict]:
        """Get recent predictions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT draw_time, predicted_numbers, confidence_score, created_at
                FROM predictions
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            
            predictions = []
            for row in results:
                predictions.append({
                    'draw_time': row[0],
                    'predicted_numbers': json.loads(row[1]),
                    'confidence_score': row[2],
                    'created_at': row[3]
                })
            
            return predictions
    
    
    def log_notification(self, notification_type: str, message: str, recipient: str = None):
        """Log notification"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications (notification_type, message, recipient)
                VALUES (?, ?, ?)
            ''', (notification_type, message, recipient))
            
            conn.commit()
    
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total numbers
            cursor.execute("SELECT COUNT(*) FROM winning_numbers")
            total_numbers = cursor.fetchone()[0]
            
            # Total draws
            cursor.execute("SELECT COUNT(DISTINCT draw_date) FROM winning_numbers")
            total_draws = cursor.fetchone()[0]
            
            # Series count
            cursor.execute("SELECT COUNT(DISTINCT series) FROM winning_numbers")
            total_series = cursor.fetchone()[0]
            
            # Recent analysis
            cursor.execute("SELECT COUNT(*) FROM analysis_results")
            total_analyses = cursor.fetchone()[0]
            
            # Last update
            cursor.execute("SELECT MAX(created_at) FROM winning_numbers")
            last_update = cursor.fetchone()[0]
            
            return {
                'total_numbers': total_numbers,
                'total_draws': total_draws,
                'total_series': total_series,
                'total_analyses': total_analyses,
                'last_update': last_update,
                'database_size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
            }


# Migration utility
def migrate_to_sqlite(gs_client=None, sheet_name="Lottery_Intelligence", db_path="lottery_intelligence.db"):
    """Utility function to migrate from Google Sheets to SQLite"""
    db = LotteryDatabase(db_path)
    
    if gs_client:
        success = db.migrate_from_google_sheets(gs_client, sheet_name)
        if success:
            print("✅ Migration completed successfully!")
        else:
            print("❌ Migration failed!")
    
    return db


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = LotteryDatabase()
    
    # Add some sample data
    sample_numbers = [
        (12345, "1PM", "2024-03-20"),
        (67890, "6PM", "2024-03-20"),
        (23456, "8PM", "2024-03-20"),
        (34567, "1PM", "2024-03-21"),
        (45678, "6PM", "2024-03-21"),
    ]
    
    for number, draw_time, draw_date in sample_numbers:
        db.insert_winning_number(number, draw_time, draw_date)
    
    # Get statistics
    stats = db.get_statistics()
    print("\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get series analysis
    series = db.get_series_analysis()
    print(f"\nSeries Analysis: {len(series)} series found")
    for s, data in list(series.items())[:3]:
        print(f"  {s}xx: {data['count']} numbers ({data['frequency']:.1f}%)")