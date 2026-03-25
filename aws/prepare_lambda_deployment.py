"""
PROJECT TITAN - AWS Lambda Deployment Package Generator

Prepares code and dependencies for AWS Lambda deployment.

Creates:
  • lambda_deployment.zip (ready for AWS Console or CLI)
  • requirements_lambda.txt (Lambda-compatible)
  • Dockerfile (optional, for custom runtime)

Usage:
  python prepare_lambda_deployment.py
  
Output:
  titan_lambda_deployment.zip → Upload to AWS Lambda
"""

import os
import sys
import shutil
import zipfile
import json
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def create_requirements_lambda():
    """Create Lambda-specific requirements file"""
    
    # Core dependencies for Lambda
    requirements = """# PROJECT TITAN - AWS Lambda Dependencies
# These packages are optimized for AWS Lambda runtime
# Total size must be < 50MB for direct upload, < 250MB for S3 layer

pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
python-dotenv==1.0.0
requests==2.31.0

# Note: supabase requires additional version pinning for Lambda
# Using specific version known to work in Lambda environment
supabase>=2.0.2,<3.0.0
"""
    
    output_path = 'requirements_lambda.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print_success(f"Created {output_path}")
    return output_path


def create_lambda_deployment_package():
    """Create deployment ZIP for AWS Lambda"""
    
    print("\n" + "="*70)
    print("📦 CREATING AWS LAMBDA DEPLOYMENT PACKAGE")
    print("="*70 + "\n")
    
    titandir = Path('.')  # Current directory (F:\LotteryAI\titan\)
    deploy_dir = Path('titan_lambda_build')
    
    # Clean previous build
    if deploy_dir.exists():
        print_info("Removing previous build directory...")
        shutil.rmtree(deploy_dir)
    
    deploy_dir.mkdir()
    print_success("Created build directory")
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 1: Copy Handler
    # ════════════════════════════════════════════════════════════════════════
    print_info("Copying Lambda handler...")
    shutil.copy('ml_engine_lambda.py', deploy_dir / 'index.py')
    print_success("Copied ml_engine_lambda.py → index.py (Lambda entrypoint)")
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 2: Copy ML Pipeline Modules
    # ════════════════════════════════════════════════════════════════════════
    print_info("Copying ML pipeline modules...")
    
    ml_files = [
        'database_supabase.py',
        'feature_engineering.py',
        'ml_engine.py',
        'monte_carlo.py',
        'markov_engine.py',
        'filter_constraints.py',
        'backtester.py'
    ]
    
    for file in ml_files:
        if (titandir / file).exists():
            shutil.copy(file, deploy_dir / file)
            print_success(f"  ✓ {file}")
        else:
            print_warning(f"  ⚠️  Missing {file}")
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 3: Create Lambda Configuration File
    # ════════════════════════════════════════════════════════════════════════
    print_info("Creating Lambda configuration...")
    
    lambda_config = {
        "name": "ProjectTitanML",
        "description": "PROJECT TITAN - ML Prediction as AWS Lambda",
        "handler": "index.lambda_handler",
        "runtime": "python3.11",
        "timeout": 900,  # 15 minutes (max for Lambda)
        "memory_size": 3008,  # Max for standard Lambda
        "layers": [
            "arn:aws:lambda:{region}:123456789012:layer:ProjectTitanDeps:1"
        ],
        "environment_variables": {
            "SUPABASE_URL": "https://your-project.supabase.co",
            "SUPABASE_KEY": "your-anon-key"
        },
        "triggers": [
            {
                "type": "API Gateway",
                "description": "HTTP trigger for manual invocation"
            },
            {
                "type": "Supabase Webhook",
                "description": "Auto-trigger on new lottery draw (winning_numbers table)"
            },
            {
                "type": "CloudWatch Events",
                "description": "Scheduled trigger (e.g., every 6 hours)"
            }
        ]
    }
    
    config_path = deploy_dir / 'lambda_config.json'
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(lambda_config, f, indent=2)
    
    print_success(f"Created lambda_config.json")
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 4: Create Deployment Instructions
    # ════════════════════════════════════════════════════════════════════════
    print_info("Creating deployment instructions...")
    
    instructions = """# AWS Lambda Deployment Instructions

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
aws lambda create-function \\
    --function-name ProjectTitanML \\
    --runtime python3.11 \\
    --role arn:aws:iam::123456789012:role/lambda-role \\
    --handler index.lambda_handler \\
    --zip-file fileb://titan_lambda_deployment.zip \\
    --timeout 900 \\
    --memory-size 3008 \\
    --environment Variables={SUPABASE_URL=https://your-project.supabase.co,SUPABASE_KEY=your-key}

# Update function (subsequent deployments)
aws lambda update-function-code \\
    --function-name ProjectTitanML \\
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
aws lambda publish-layer-version \\
    --layer-name ProjectTitanDeps \\
    --zip-file fileb://ProjectTitanDeps-layer.zip \\
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
aws events put-rule \\
    --name TitanMLSchedule \\
    --schedule-expression "rate(6 hours)"

aws events put-targets \\
    --rule TitanMLSchedule \\
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
aws lambda invoke \\
    --function-name ProjectTitanML \\
    --payload '{}' \\
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
aws cloudwatch put-metric-alarm \\
    --alarm-name TitanMLErrors \\
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
"""
    
    instructions_path = deploy_dir / 'DEPLOYMENT_INSTRUCTIONS.md'
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print_success("Created DEPLOYMENT_INSTRUCTIONS.md")
    
    # ════════════════════════════════════════════════════════════════════════
    # STEP 5: Create ZIP Archive
    # ════════════════════════════════════════════════════════════════════════
    print_info("Creating deployment ZIP file...")
    
    zip_path = 'titan_lambda_deployment.zip'
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from build dir
        for file_path in deploy_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(deploy_dir)
                zipf.write(file_path, arcname)
                
        # Also add requirements
        if os.path.exists('requirements_lambda.txt'):
            zipf.write('requirements_lambda.txt', 'requirements_lambda.txt')
    
    # Get ZIP size
    zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print_success(f"Created {zip_path} ({zip_size_mb:.2f} MB)")
    
    return zip_path


def create_docker_support():
    """Create Dockerfile for custom Lambda runtime (optional)"""
    
    dockerfile_content = """# Dockerfile for AWS Lambda Custom Runtime
# Use if deployment ZIP exceeds 50MB limit

FROM public.ecr.aws/lambda/python:3.11

# Copy requirements
COPY requirements_lambda.txt ${LAMBDA_TASK_ROOT}/

# Install dependencies
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements_lambda.txt

# Copy handler
COPY ml_engine_lambda.py ${LAMBDA_TASK_ROOT}/index.py
COPY *.py ${LAMBDA_TASK_ROOT}/

# Set handler
CMD ["index.lambda_handler"]
"""
    
    dockerfile_path = 'Dockerfile.lambda'
    with open(dockerfile_path, 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    print_success(f"Created {dockerfile_path} (optional, for large deployments)")
    
    # Create build script
    build_script = """# Build and push custom Lambda image to ECR

#!/bin/bash

AWS_ACCOUNT_ID=123456789012
AWS_REGION=us-east-1
ECR_REPO=project-titan-ml

# Build image
docker build -f Dockerfile.lambda -t ${ECR_REPO}:latest .

# Create ECR repo if not exists
aws ecr create-repository --repository-name ${ECR_REPO} --region ${AWS_REGION} || true

# Get login token
aws ecr get-login-password --region ${AWS_REGION} | \\
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Tag image
docker tag ${ECR_REPO}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest

# Push to ECR
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest

echo "✓ Image pushed to ECR"
echo "Update Lambda function:"
echo "  Runtime: Custom image"
echo "  URI: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest"
"""
    
    build_script_path = 'lambda_build_and_push.sh'
    with open(build_script_path, 'w', encoding='utf-8') as f:
        f.write(build_script)
    
    os.chmod(build_script_path, 0o755)
    print_success(f"Created {build_script_path} (optional ECR deployment)")


def print_summary(zip_path):
    """Print deployment summary"""
    
    print("\n" + "="*70)
    print("✅ AWS LAMBDA DEPLOYMENT PACKAGE READY")
    print("="*70)
    
    print(f"""
📦 Deployment Package: {zip_path}
   Size: {os.path.getsize(zip_path) / (1024*1024):.2f} MB
   
📋 Next Steps:

   1. UPLOAD TO AWS LAMBDA
      • AWS Console: Lambda → Create function → Upload .zip file
      • AWS CLI: aws lambda update-function-code --function-name ProjectTitanML --zip-file fileb://{zip_path}
   
   2. SET ENVIRONMENT VARIABLES
      • SUPABASE_URL: https://your-project.supabase.co
      • SUPABASE_KEY: your-anon-key-here
   
   3. CONFIGURE TRIGGER (Pick one)
      • Supabase webhook (auto-trigger on new draw)
      • CloudWatch Events (every 6 hours)
      • API Gateway (manual HTTP call)
   
   4. TEST
      • AWS Lambda Console → Test
      • CloudWatch Logs → View execution

📚 Documentation:
   • titan_lambda_build/DEPLOYMENT_INSTRUCTIONS.md
   • ml_engine_lambda.py (handler code)
   • requirements_lambda.txt (dependencies)
   
💡 Pro Tips:
   • Use Lambda Layers for dependencies (> 50MB)
   • Set timeout to 900s (15 minutes)
   • Memory: 3008 MB recommended for ML
   • Monitor with CloudWatch
   • Cost: ~$1-2/month for typical usage

🚀 Ready to deploy!
""")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🏗️  PROJECT TITAN - AWS LAMBDA DEPLOYMENT BUILDER")
    print("="*70 + "\n")
    
    try:
        # Create requirements file
        reqs_file = create_requirements_lambda()
        print()
        
        # Create deployment package
        zip_path = create_lambda_deployment_package()
        print()
        
        # Create Docker support (optional)
        create_docker_support()
        print()
        
        # Print summary
        print_summary(zip_path)
        
        print_success("✓ Deployment package ready!")
        print(f"\nUpload this file to AWS Lambda: {zip_path}\n")
        
    except Exception as e:
        print_error(f"Error creating deployment: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
