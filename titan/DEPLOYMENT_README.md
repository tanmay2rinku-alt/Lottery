# Deploy Lottery Scraper to AWS Lambda

## Prerequisites
- AWS CLI installed and configured
- AWS SAM CLI installed
- Supabase project URL and service key

## Step 1: Configure Environment
```bash
cd F:\LotteryAI\titan

# Set your Supabase credentials
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-service-role-key"
```

## Step 2: Build and Deploy with SAM
```bash
# Build the Lambda functions
sam build

# Deploy to AWS (first time)
sam deploy --guided

# For subsequent deploys
sam deploy
```

## Step 3: Verify Deployment
```bash
# Check Lambda functions
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `Lottery`)].FunctionName'

# Check CloudWatch rules
aws events list-rules --query 'Rules[?starts_with(Name, `Lottery`)].Name'
```

## What Gets Deployed
- **LotteryScraper** - Runs every 2 hours automatically
- **ProjectTitanML** - ML predictions (existing)

## Monitoring
- Logs: AWS CloudWatch → Log Groups
- Metrics: AWS Lambda → Monitoring
- Alerts: Set up CloudWatch alarms for failures

## Cost Estimate
- ~$0.50/month for 2-hour schedule
- ~$1-2/month with higher frequency

## Manual Testing
```bash
# Test scraper manually
aws lambda invoke --function-name LotteryScraper output.json

# Check results
cat output.json
```