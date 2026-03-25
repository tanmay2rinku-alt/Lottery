"""
Quick InstantDB Data Population with Progress Tracking
Optimized for filling 1GB storage efficiently
"""

import json
import random
from datetime import datetime, timedelta

# Configuration
APP_ID = "c3ea4e7d-54d0-41a3-b54c-6fc837fc9573"
TARGET_SIZE_MB = 1024  # 1GB

def estimate_record_size():
    """Estimate average record size across all collections"""
    
    # Sample winning number record
    winning_record = {
        "number": 12345,
        "draw_time": "6PM",
        "draw_date": "2026-03-23",
        "series": "12",
        "digit_sum": 15,
        "created_at": "2026-03-23T10:30:00",
        "frequency_rank": 100,
        "hot_score": 75.50,
        "cold_score": 25.50,
        "recency_score": 85.00
    }
    winning_size = len(json.dumps(winning_record))
    
    # Sample prediction record (larger)
    pred_record = {
        "draw_time": "6PM",
        "draw_date": "2026-03-23",
        "predicted_numbers": [88990, 43444, 45678, 56789, 67890],
        "top_50_numbers": list(range(10000, 10050)),
        "confidence_score": 0.85,
        "algorithm_version": "v2.0",
        "factors": {
            "frequency": 0.3,
            "recency": 0.25,
            "series": 0.2,
            "digit_pattern": 0.15,
            "cold": 0.1
        },
        "created_at": "2026-03-23T10:30:00"
    }
    pred_size = len(json.dumps(pred_record))
    
    # Average size estimate
    avg_size = (winning_size + pred_size) // 2
    return avg_size


def calculate_distribution():
    """Calculate record distribution for 1GB"""
    avg_size = estimate_record_size()
    total_records = (TARGET_SIZE_MB * 1024 * 1024) // avg_size
    
    print(f"📊 Storage Calculation:")
    print(f"  Average record size: {avg_size:,} bytes")
    print(f"  Total target size: {TARGET_SIZE_MB} MB")
    print(f"  Estimated records: {total_records:,}")
    print()
    
    # Distribution across collections
    winning = total_records // 3
    predictions = total_records // 3
    analyses = total_records // 6
    notifications = (total_records - winning - predictions - analyses)
    
    return {
        "winning_numbers": winning,
        "predictions": predictions,
        "analysis_results": analyses,
        "notifications": notifications,
        "total": winning + predictions + analyses + notifications
    }


def generate_bulk_data_sql():
    """Generate SQL-like format for bulk insert"""
    
    distribution = calculate_distribution()
    
    print("📈 Data Generation Plan:")
    print("="*60)
    for collection, count in distribution.items():
        if collection != "total":
            percentage = (count / distribution["total"]) * 100
            print(f"{collection:20s}: {count:>10,} records ({percentage:>5.1f}%)")
    print("="*60)
    print(f"{'TOTAL':20s}: {distribution['total']:>10,} records (100.0%)")
    
    return distribution


def simulate_population():
    """Simulate population with estimated time"""
    
    distribution = calculate_distribution()
    
    # Estimate performance
    records_per_second = 500  # Conservative estimate
    total_records = distribution["total"]
    estimated_hours = (total_records / records_per_second) / 3600
    
    print(f"\n⏱️  Estimated Population Time:")
    print(f"  At {records_per_second:,} records/second:")
    print(f"  Total time: ~{estimated_hours:.1f} hours")
    print(f"  Or: ~{estimated_hours * 60:.0f} minutes")
    
    return distribution


def main():
    print("🎯 InstantDB 1GB Population Planning")
    print("="*60)
    
    # Calculate distribution
    distribution = generate_bulk_data_sql()
    
    # Simulate population
    simulate_population()
    
    print(f"\n✅ Ready to populate!")
    print(f"\nRun: python populate_instantdb.py")
    print(f"     (Will populate {distribution['total']:,} records into InstantDB)")


if __name__ == "__main__":
    main()
