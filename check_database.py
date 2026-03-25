#!/usr/bin/env python3
"""
Quick Supabase Data Viewer
Shows your lottery database contents
"""

from supabase_client import SupabaseClient
from config import SUPABASE_URL, SUPABASE_KEY

def main():
    # Initialize client with Supabase credentials
    client = SupabaseClient(url=SUPABASE_URL, key=SUPABASE_KEY)

    print("🎰 Supabase Lottery Database Viewer")
    print("=" * 50)

    try:
        # Get statistics
        print("\n📊 Database Statistics:")
        stats = client.get_statistics()
        for key, value in stats.items():
            if isinstance(value, int):
                print(f"  {key}: {value:,}")
            else:
                print(f"  {key}: {value}")

        # Sample winning numbers
        print("\n🎫 Sample Winning Numbers:")
        winning = client.get_winning_numbers(limit=5)
        if winning:
            for num in winning[:5]:
                print(f"  {num}")
        else:
            print("  No winning numbers found")

        # Sample predictions
        print("\n🎯 Sample Predictions:")
        predictions = client.get_recent_predictions(limit=3)
        if predictions:
            for pred in predictions[:3]:
                numbers = pred.get('predicted_numbers', [])
                confidence = pred.get('confidence_score', 0)
                print(f"  Numbers: {numbers} - Confidence: {confidence}%")
        else:
            print("  No predictions found")

        print("\n✅ Database check complete!")

    except Exception as e:
        print(f"\n❌ Error accessing database: {e}")
        print("💡 Make sure you have internet connection to access Supabase")

if __name__ == "__main__":
    main()