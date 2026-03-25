
# CLOUDWATCH SCHEDULED TRIGGER

Runs Lambda automatically on a schedule.

OPTION A: AWS Console (Visual)
───────────────────────────────
1. AWS Console → CloudWatch → Rules → Create rule
2. Fill in:
   - Name: ProjectTitanMLSchedule
   - Pattern: Fixed rate
   - Value: 6 hours
   - Target: Lambda function → ProjectTitanML

3. Click "Create rule"

Now Lambda runs every 6 hours automatically.

OPTION B: AWS CLI (Scriptable)
───────────────────────────────

# Create CloudWatch rule
aws events put-rule \
    --name ProjectTitanMLSchedule \
    --schedule-expression "rate(6 hours)"

# Add Lambda as target
aws events put-targets \
    --rule ProjectTitanMLSchedule \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:ACCOUNT_ID:function:ProjectTitanML"

# Grant permission for CloudWatch to invoke Lambda
aws lambda add-permission \
    --function-name ProjectTitanML \
    --statement-id TitanMLSchedule \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:ACCOUNT_ID:rule/ProjectTitanMLSchedule

SCHEDULE EXPRESSIONS:
  "rate(1 hour)" → Every hour
  "rate(6 hours)" → Every 6 hours
  "rate(1 day)" → Once per day
  "cron(0 9 * * ? *)" → 9 AM UTC every day
  "cron(0 */6 * * ? *)" → Every 6 hours (specific times: 0, 6, 12, 18 UTC)

PAYOFF:
  ✓ Reliable scheduling
  ✓ No PC needed
  ✓ Automatic AWS management
