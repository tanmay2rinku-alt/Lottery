
# SUPABASE WEBHOOK TRIGGER FOR LAMBDA

Triggers Lambda automatically when new lottery draw is inserted.

STEP 1: Create Lambda REST API
────────────────────────────────
AWS Console → Lambda → ProjectTitanML → Add trigger → API Gateway

Create:
  • New API: ProjectTitanMLAPI
  • API type: REST API
  • Security: OPEN (or use API Key)
  
Copy the endpoint URL: https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/ProjectTitanML

STEP 2: Configure Supabase Webhook
────────────────────────────────────
Supabase Console → Database → winning_numbers table → Insert Row → Add webhook

  Webhook name: ProjectTitanMLTrigger
  URL: [Paste Lambda API URL from Step 1]
  Events: INSERT (trigger on new draws)
  Retry period: 5 seconds
  Active: ✓ (checked)

Save webhook

STEP 3: Test
────────────
Insert a test row in winning_numbers table:
  date: 2026-03-24
  time_slot: 6PM
  full_number: 45678

Lambda should automatically execute within seconds.
Check CloudWatch Logs: /aws/lambda/ProjectTitanML

PAYOFF:
  ✓ Fully automated
  ✓ No manual triggers needed
  ✓ Instant predictions after draw
  ✓ Zero infrastructure to maintain
