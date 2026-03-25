# 🎯 Automated Lottery Scraper - AWS Lambda Deployment

Your lottery scraping system is now configured for **fully automated, cloud-based operation** without needing your PC to run 24/7.

## ✅ What's Been Set Up

### 🔧 Lambda Functions
- **LotteryScraper** - Runs your full scraping pipeline every 2 hours
- **ProjectTitanML** - ML predictions (existing)

### ⏰ Automatic Scheduling
- Scrapes lottery data every 2 hours automatically
- Stores results in Supabase cloud database
- No manual intervention required

### 📊 Data Flow
```
CloudWatch Schedule → Lambda → Scrape Website → Store in Supabase → Run Analysis
```

## 🚀 Quick Deployment

### Prerequisites
```bash
# Install AWS CLI and SAM CLI
pip install awscli aws-sam-cli

# Configure AWS credentials
aws configure
```

### Deploy
```bash
cd F:\LotteryAI\titan

# Set your Supabase credentials
$env:SUPABASE_URL = "https://your-project.supabase.co"
$env:SUPABASE_KEY = "your-service-role-key"

# Build and deploy
sam build
sam deploy --guided
```

## 📈 Monitoring & Logs

### View Logs
```bash
# Lambda logs
aws logs tail /aws/lambda/LotteryScraper --follow

# CloudWatch metrics
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Duration --dimensions Name=FunctionName,Value=LotteryScraper
```

### Dashboard
- AWS Console → Lambda → LotteryScraper → Monitoring
- View execution history, errors, and performance

## 💰 Cost Estimate

- **~ $0.50/month** for 2-hour schedule (12 runs/day)
- **~ $1-2/month** if increased to hourly
- Free tier covers ~1 million requests/month

## 🔧 Customization

### Change Schedule
Edit `template.yml`:
```yaml
Schedule: rate(1 hour)  # Every hour
# or
Schedule: cron(0 */4 * * ? *)  # Every 4 hours
```

### Environment Variables
Set in Lambda Console or `template.yml`:
- `SUPABASE_URL`
- `SUPABASE_KEY`

## 🧪 Testing

### Manual Test
```bash
# Test Lambda function
aws lambda invoke --function-name LotteryScraper --payload '{}' response.json
cat response.json
```

### Local Test
```bash
cd F:\LotteryAI\titan
python scraper_lambda.py
```

## 🎯 Result

Your system now:
- ✅ Runs automatically every 2 hours
- ✅ Scrapes lottery data from lotterysambad.com
- ✅ Stores data in Supabase cloud
- ✅ Runs analysis and predictions
- ✅ Sends notifications
- ✅ Works 24/7 without your PC

**No more keeping your computer running!** 🎉