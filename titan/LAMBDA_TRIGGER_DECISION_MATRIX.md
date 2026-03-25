
┌──────────────────────────────────────────────────────────────────────────┐
│                    AWS LAMBDA TRIGGER COMPARISON                         │
├──────────────────┬──────────┬──────────┬──────────┬──────────┬───────────┤
│ Trigger Type     │ Auto?    │ Setup    │ Cost     │ Use Case │ Recommend │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼───────────┤
│ Supabase Hook    │ ✓ YES    │ Easy     │ $0       │ Real-time│ ⭐⭐⭐⭐⭐ │
│ CloudWatch       │ ✓ YES    │ Easy     │ $0       │ Scheduled│ ⭐⭐⭐⭐   │
│ API Gateway      │ ✗ Manual │ Medium   │ $3.50/mo │ On-demand│ ⭐⭐⭐⭐   │
│ SNS Topic        │ ✓ YES    │ Medium   │ $0       │ Chaining │ ⭐⭐⭐    │
│ S3 Event         │ ✓ YES    │ Easy     │ $0       │ File-based│ ⭐⭐⭐   │
│ Step Functions   │ ✓ YES    │ Hard     │ $0.000025│ Complex  │ ⭐⭐⭐⭐   │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴───────────┘

RECOMMENDATION:
  For simplicity → Supabase Webhook (auto on new draw)
  For scheduling → CloudWatch (every 6 hours)
  For flexibility → API Gateway (call whenever)
  For complex → Step Functions
