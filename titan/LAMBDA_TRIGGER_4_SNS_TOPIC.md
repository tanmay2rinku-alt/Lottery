
# SNS TOPIC TRIGGER

Invoke Lambda via SNS notifications.
Useful for chaining with other services.

STEP 1: Create SNS Topic
─────────────────────────
AWS Console → Simple Notification Service → Create Topic

  Topic name: ProjectTitanMLTopic
  
Copy Topic ARN: arn:aws:sns:REGION:ACCOUNT:ProjectTitanMLTopic

STEP 2: Add Lambda as Subscriber
──────────────────────────────────
SNS → ProjectTitanMLTopic → Create Subscription

  Protocol: Lambda function
  Lambda function: ProjectTitanML

STEP 3: Publish Message to Trigger
────────────────────────────────────
aws sns publish \
    --topic-arn arn:aws:sns:us-east-1:ACCOUNT:ProjectTitanMLTopic \
    --message "{}"

Lambda automatically invokes!

PAYOFF:
  ✓ Decoupled architecture
  ✓ Can trigger multiple Lambdas
  ✓ Good for async processing
