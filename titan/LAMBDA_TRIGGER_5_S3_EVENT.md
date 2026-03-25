
# S3 EVENT TRIGGER

Invoke Lambda when files are uploaded to S3.
Useful if data arrives via S3 bucket.

STEP 1: Create S3 Bucket
────────────────────────
AWS Console → S3 → Create Bucket

  Bucket name: project-titan-data

STEP 2: Add Notification
─────────────────────────
S3 → Bucket → Properties → Event Notifications → Create

  Event name: ProjectTitanMLTrigger
  Events: s3:ObjectCreated:*
  Destination: Lambda function
  Function: ProjectTitanML

STEP 3: Upload File to Trigger
───────────────────────────────
aws s3 cp lottery_data.csv s3://project-titan-data/

Lambda automatically processes!

PAYOFF:
  ✓ File-based data integration
  ✓ Batch processing
  ✓ Data warehouse integration
