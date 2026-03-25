# InstantDB Integration for Lottery Intelligence System

## 🌐 Overview

Your lottery intelligence system now uses **InstantDB** - a real-time cloud database - instead of local SQLite. This gives you:

- ☁️ **Cloud Storage**: All data synced automatically
- 🔄 **Real-Time**: Instant updates across all clients
- 🔐 **Secure**: Built-in authentication and encryption
- 📱 **Multi-Device**: Access from anywhere
- ⚡ **Fast**: Optimized for real-time queries
- 🤝 **Collaborative**: Share data with team members

## 🔧 Configuration

### Your App Credentials

```
App ID: c3ea4e7d-54d0-41a3-b54c-6fc837fc9573
Type: Public (read-only without token)
```

These are already configured in:
- `main.py` - INSTANT_DB_APP_ID constant
- `instantdb_client.py` - Default app ID

### Optional: Add Write Token

For full read-write access, add your token to `credentials.json`:

```json
{
  "instant_db_app_id": "c3ea4e7d-54d0-41a3-b54c-6fc837fc9573",
  "instant_db_token": "your_token_here"
}
```

Then update `main.py`:
```python
# Load from credentials
with open('credentials.json') as f:
    creds = json.load(f)
    self.database = InstantDBClient(
        app_id=creds['instant_db_app_id'],
        token=creds['instant_db_token']
    )
```

## 📊 Data Schema

### Winning Numbers Collection
```javascript
winning_numbers: {
  "number": 12345,
  "draw_time": "6PM",
  "draw_date": "2026-03-23",
  "series": "12",
  "digit_sum": 15,
  "created_at": "2026-03-23T10:30:00"
}
```

### Predictions Collection
```javascript
predictions: {
  "draw_time": "6PM",
  "predicted_numbers": [88990, 43444, 45678],
  "confidence_score": 0.85,
  "created_at": "2026-03-23T10:30:00"
}
```

### Analysis Results Collection
```javascript
analysis_results: {
  "type": "full_analysis",
  "results": "{...json_data...}",
  "created_at": "2026-03-23T10:30:00"
}
```

### Notifications Log Collection
```javascript
notifications: {
  "type": "watchlist_match",
  "message": "Watchlist number 88990 found in 6PM draw",
  "recipient": "user@example.com",
  "sent_at": "2026-03-23T10:30:00"
}
```

## 🚀 Usage Examples

### Initialize InstantDB Client

```python
from instantdb_client import InstantDBClient

# With just app ID (public read-only)
client = InstantDBClient(app_id="c3ea4e7d-54d0-41a3-b54c-6fc837fc9573")

# With write token
client = InstantDBClient(
    app_id="c3ea4e7d-54d0-41a3-b54c-6fc837fc9573",
    token="your_token"
)
```

### Insert Winning Numbers

```python
# Insert a single number
client.insert_winning_number(
    number=88990,
    draw_time="6PM",
    draw_date="2026-03-23"
)

# Insert multiple
for num in [88990, 43444, 45678]:
    client.insert_winning_number(num, "6PM")
```

### Save Predictions

```python
# Save top predictions with confidence score
client.save_predictions(
    draw_time="6PM",
    predicted_numbers=[88990, 43444, 45678, 56789, 67890],
    confidence_score=0.85
)
```

### Save Analysis Results

```python
# Save complete analysis
client.save_analysis_results(
    analysis_type="full_analysis",
    results={
        "total_numbers": 100,
        "mean": 55000,
        "top_5_picks": [88990, 43444, 45678, 56789, 67890],
        "sentiment": "bullish"
    }
)
```

### Query Data

```python
# Get all winning numbers
numbers = client.get_winning_numbers()

# Get specific draw time
numbers_6pm = client.get_winning_numbers(draw_time="6PM")

# Get recent predictions
predictions = client.get_recent_predictions(limit=5)

# Get database statistics
stats = client.get_statistics()
```

### Log Events

```python
# Log notifications for tracking
client.log_notification(
    notification_type="watchlist_match",
    message="Number 88990 matched in 6PM draw!",
    recipient="user@example.com"
)
```

## 🔄 Integration with Lottery System

### Phase 3: Cloud Sync (Updated)

The system now automatically:
1. Uploads to Google Sheets (for backup)
2. **Syncs to InstantDB** (primary cloud storage)

```python
# Phase 3 automatically does this:
if self.database:  # InstantDBClient
    for number, draw_time in data_to_upload:
        self.database.insert_winning_number(int(number), draw_time)
```

### Phase 4: Analysis Export (Updated)

Analysis results are automatically saved to InstantDB:

```python
# Analysis is saved as:
if self.database:
    self.database.save_analysis_results("full_analysis", analysis_results)
```

### Phase 5: Enhanced Features (Updated)

All advanced features now use InstantDB:

- **Watchlist Matching**: Logged to cloud
- **Predictions**: Stored for history
- **Notifications**: Tracked in `notifications` collection
- **Statistics**: Retrieved from cloud

```python
# Phase 5 automatically:
# - Syncs watchlist matches
# - Saves predictions
# - Logs notifications
# - Retrieves statistics
```

## 📱 Access Your Data

### Via Dashboard

```bash
# The dashboard.py loads data from InstantDB
streamlit run dashboard.py
```

The dashboard will:
- Connect to your InstantDB instance
- Display real-time statistics
- Show predictions and analysis
- Visualize trends and patterns

### Via InstantDB Console

Visit https://instant.dev and use your credentials to:
- View all collections
- Monitor real-time updates
- Export data
- Set up webhooks
- Create custom queries

## 🔐 Security Notes

### Public App ID
- ✅ Can read data without token
- ✅ No sensitive data exposed
- ✅ Safe to commit to git

### Write Token
- ⚠️ Keep private (use `.env` or `credentials.json`)
- ⚠️ Never commit to git
- ⚠️ Rotate if compromised

### Best Practices

```python
# Load token from environment, not hardcoded
import os
token = os.environ.get('INSTANT_DB_TOKEN')

# Or from secure config file (gitignored)
client = InstantDBClient(
    app_id=APP_ID,
    token=token
)
```

## ⚡ Performance Tips

### Batch Operations
```python
# ✅ Better: Process multiple numbers
for num in numbers:
    client.insert_winning_number(num, "6PM")

# ❌ Avoid: Individual API calls in loops
```

### Query Optimization
```python
# ✅ Better: Query once, filter locally
all_numbers = client.get_winning_numbers()
filtered = [n for n in all_numbers if n > 50000]

# ❌ Avoid: Multiple queries
```

### Error Handling
```python
# Always handle network errors
try:
    client.insert_winning_number(12345, "6PM")
except Exception as e:
    print(f"Connection error: {e}")
    # Fallback to local cache
```

## 🧪 Testing

```bash
# Run InstantDB integration tests
python test_instantdb.py

# This tests:
✅ Client initialization
✅ Data insert operations
✅ Prediction saves
✅ Analysis results
✅ Query operations
✅ Statistics retrieval
✅ Notification logging
✅ Watchlist integration
```

## 📈 Monitoring & Maintenance

### Check Statistics
```python
stats = client.get_statistics()
print(f"Stored numbers: {stats['total_numbers']}")
print(f"Recent predictions: {stats['total_predictions']}")
print(f"Last update: {stats['last_update']}")
```

### View Recent Activity
```python
# Get last 10 predictions
recent = client.get_recent_predictions(limit=10)
for pred in recent:
    print(f"{pred['draw_time']}: {pred['predicted_numbers']}")
```

### Monitor Notifications
```python
# Retrieve all logged notifications
# Via InstantDB dashboard or direct query
```

## 🎯 Advanced Features

### Real-Time Subscriptions (Next Phase)

```python
# Future: Subscribe to real-time updates
client.subscribe("winning_numbers", callback=on_new_number)

def on_new_number(data):
    print(f"New number: {data['number']}")
```

### Webhook Integration (Next Phase)

```
# Set up webhook to get instant updates
POST /webhook/lottery
- Trigger on new winning number
- Send alerts to Telegram
- Log predictions in real-time
```

### Multi-Tenant Support (Future)

```python
# Scale to multiple users/competitions
client = InstantDBClient(app_id=APP_ID, user_id="user@abc.com")
```

## 🆘 Troubleshooting

### Connection Issues
```
Error: "Connection timeout"
Solution: Check internet connection, verify app ID
```

### Authentication Failed
```
Error: "Invalid token"
Solution: Verify token in credentials.json, check expiration
```

### Query Returns Empty
```
Error: "No data found"
Solution: Insert data first, verify collection names
```

### Rate Limiting
```
Error: "Too many requests"
Solution: Reduce query frequency, batch operations
```

## 📚 Resources

- **InstantDB Docs**: https://docs.instant.dev
- **API Reference**: https://api.instant.dev/docs
- **Dashboard**: https://instant.dev
- **Status Page**: https://status.instant.dev

## 🎉 You're Ready!

Your lottery intelligence system is now powered by InstantDB! 

```bash
# Start the enhanced pipeline with cloud storage
python main.py

# All data automatically syncs to the cloud
# 🌐 Available anywhere, anytime
# 📱 Real-time updates
# 🔐 Secure and backed up
```

Happy lottery analyzing! 🍀
