# AWS Lambda Trigger Examples

Ready-to-use configurations for PROJECT TITAN ML Lambda function.

## Examples

1. [SUPABASE_WEBHOOK](LAMBDA_TRIGGER_1_SUPABASE_WEBHOOK.md)
   - Auto-trigger when new draw inserted
   - **RECOMMENDED** for fully automated setup
   - Zero manual work

2. [CLOUDWATCH_SCHEDULE](LAMBDA_TRIGGER_2_CLOUDWATCH_SCHEDULE.md)
   - Run every 6 hours automatically
   - Reliable scheduling
   - Good fallback if webhook fails

3. [API_GATEWAY](LAMBDA_TRIGGER_3_API_GATEWAY.md)
   - Manual HTTP trigger
   - Call from apps/webhooks
   - Optional authentication

4. [SNS_TOPIC](LAMBDA_TRIGGER_4_SNS_TOPIC.md)
   - Event-based chaining
   - Integration with other services
   - Pub/sub pattern

5. [S3_EVENT](LAMBDA_TRIGGER_5_S3_EVENT.md)
   - Trigger on file upload
   - File-based data integration
   - Batch processing

6. [STEP_FUNCTIONS](LAMBDA_TRIGGER_6_STEP_FUNCTIONS.md)
   - Complex multi-stage workflows
   - Visual execution monitoring
   - Advanced orchestration

## Quick Pick

| Goal | Trigger |
|------|---------|
| Fully automated, no manual work | ⭐ Supabase Webhook |
| Scheduled runs every N hours | ⭐ CloudWatch Schedule |
| Manual on-demand predictions | ⭐ API Gateway |
| Complex multi-step pipeline | ⭐ Step Functions |

## Setup Time

- Supabase Webhook: 5 minutes
- CloudWatch: 5 minutes
- API Gateway: 10 minutes
- Others: 10-20 minutes

Choose one and go! 🚀
