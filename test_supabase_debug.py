import json
from supabase_client import SupabaseClient
from config import SUPABASE_URL, SUPABASE_KEY

def test_connection():
    client = SupabaseClient(url=SUPABASE_URL, key=SUPABASE_KEY)
    
    # 1. Test Insert
    print("Testing Insert...")
    res = client.insert_winning_number(99999, "TEST", "2026-03-25")
    print(f"Insert result: {res}")
    
    # 2. Test Select
    print("\nTesting Select...")
    try:
        data = client.supabase.table('winning_numbers').select('*').execute().data
        print(f"Retrieved {len(data)} rows from 'winning_numbers'")
        if data:
            print(f"Sample data: {data[0]}")
    except Exception as e:
        print(f"Select error: {e}")

    # 3. Test Stats
    print("\nTesting Stats...")
    stats = client.get_statistics()
    print(f"Stats: {stats}")

if __name__ == "__main__":
    test_connection()
