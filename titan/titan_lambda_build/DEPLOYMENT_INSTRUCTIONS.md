# AWS Lambda Deployment Instructions

## Method 1: AWS Console (Easiest)

1. Go to AWS Lambda Console: https://console.aws.amazon.com/lambda
2. Click "Create function"
3. Choose "Author from scratch"
4. Function name: ProjectTitanML
5. Runtime: Python 3.11
6. Advanced settings:
   - Memory: 3008 MB
   - Timeout: 900 seconds (15 min)
   - Architecture: x86_64

7. Upload code:
   - Click "Upload from"
   - Choose ".zip file"
   - Upload: titan_lambda_deployment.zip

8. Configure environment variables:
   - SUPABASE_URL: https://your-project.supabase.co
   - SUPABASE_KEY: your-anon-key
   - PYTHONPATH: /var/task/site-packages

9. Click "Deploy"

## Method 2: AWS CLI (Faster for updates)

```bash
# Create function (first time)
aws lambda create-function \
    --function-name ProjectTitanML \
    --runtime python3.11 \
    --role arn:aws:iam::123456789012:role/lambda-role \
    --handler index.lambda_handler \
    --zip-file fileb://titan_lambda_deployment.zip \
    --timeout 900 \
    --memory-size 3008 \
    --environment Variables={SUPABASE_URL=https://your-project.supabase.co,SUPABASE_KEY=your-key}

# Update function (subsequent deployments)
aws lambda update-function-code \
    --function-name ProjectTitanML \
    --zip-file fileb://titan_lambda_deployment.zip
```

## Requirements

### AWS IAM Role
Your Lambda execution role needs:
- CloudWatch Logs (for logging)
- Optional: SNS (if sending notifications)
- Optional: S3 (if storing results)

### Dependencies Layer (Recommended)

Large packages (pandas, scikit-learn) should be in a Layer:

```bash
# Create layer
mkdir -p python
cd python
pip install -r requirements_lambda.txt -t .
cd ..
zip -r ProjectTitanDeps-layer.zip python/

# Upload layer
aws lambda publish-layer-version \
    --layer-name ProjectTitanDeps \
    --zip-file fileb://ProjectTitanDeps-layer.zip \
    --compatible-runtimes python3.11
```

## Triggers

### Option 1: Supabase Webhook (Recommended)
Auto-triggers on new draw:

1. Go to Supabase → Database → winning_numbers
2. Click "Insert Row" → Add webhook
3. Webhook URL: [Get from Lambda → Function URL]
4. Event: INSERT
5. Mapping: Auto-detect

### Option 2: CloudWatch Schedule
Every 6 hours:

```bash
aws events put-rule \
    --name TitanMLSchedule \
    --schedule-expression "rate(6 hours)"

aws events put-targets \
    --rule TitanMLSchedule \
    --targets "Id"="1","Arn"="arn:aws:lambda:region:account:function:ProjectTitanML"
```

### Option 3: API Gateway
Manual trigger:

1. AWS Lambda Console → Add trigger
2. Create "API Gateway"
3. New API (REST API)
4. Security: OPEN (or use API Key)

## Testing

Execute Lambda:
```bash
aws lambda invoke \
    --function-name ProjectTitanML \
    --payload '{}' \
    response.json && cat response.json
```

View logs:
```bash
aws logs tail /aws/lambda/ProjectTitanML --follow
```

## Monitoring

CloudWatch Metrics:
- Invocations
- Errors
- Duration
- Concurrent Executions

Set up alarms:
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name TitanMLErrors \
    --alarm-actions arn:aws:sns:region:account:topic-name
```

## Cost Estimation

Typical usage:
- Executions: 240/month (10/day, 6-hourly schedule)
- Duration: ~25 seconds per execution
- Memory: 3008 MB
- Monthly cost: ~$1-2 (free tier: 1M requests)

## Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"
Solution: Use Lambda Layers for dependencies

### "Task timed out"
Solution: Increase timeout (currently 900 seconds = 15 min)

### "Connection refused" to Supabase
Solution: Check SUPABASE_URL and SUPABASE_KEY environment variables

### Large package size
Solution: https://github.com/aws-samples/aws-lambda-layer-aws-cli

## Next Steps

1. Upload titan_lambda_deployment.zip
2. Create Lambda function (see Method 1 above)
3. Test with AWS Lambda test event
4. Set up trigger (Supabase webhook or schedule)
5. Monitor in CloudWatch

Ready to deploy! 🚀
