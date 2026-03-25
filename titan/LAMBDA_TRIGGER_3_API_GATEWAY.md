
# API GATEWAY TRIGGER

Invoke Lambda via HTTP requests.
Perfect for manual triggers or external integrations.

STEP 1: Create REST API
────────────────────────
AWS Console → API Gateway → Create API

  API type: REST API
  API name: ProjectTitanMLAPI
  Endpoint type: Regional

STEP 2: Create Method
──────────────────────
• Resource: Create new: /predict
• Method: POST
• Integration: Lambda Function
• Function: ProjectTitanML

STEP 3: Deploy
───────────────
• Stage: Create new stage "prod"
• Deployment complete

Copy API endpoint: https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/predict

STEP 4: Test via Curl
──────────────────────

curl -X POST https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/predict \
    -H "Content-Type: application/json" \
    -d '{}'

Response:
{
  "statusCode": 200,
  "body": {
    "predictions": {
      "top_5_numbers": [45678, 56789, ...],
      "series": "45"
    }
  }
}

STEP 5: Use from Python
────────────────────────

import requests
import json

url = "https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/predict"

response = requests.post(url, json={})
predictions = response.json()

print(f"Top 5: {predictions['body']['predictions']['top_5_numbers']}")

STEP 6: Add Authentication (Optional)
──────────────────────────────────────

API Gateway → Authorizers → Create

  Type: API Key
  Create API key

Now requests need:
  curl -H "x-api-key: YOUR_API_KEY" ...

PAYOFF:
  ✓ On-demand predictions
  ✓ Easy integration with other services
  ✓ Can be called from anywhere (webhooks, scripts, apps)
  ✓ Optional authentication
