# Build and push custom Lambda image to ECR

#!/bin/bash

AWS_ACCOUNT_ID=123456789012
AWS_REGION=us-east-1
ECR_REPO=project-titan-ml

# Build image
docker build -f Dockerfile.lambda -t ${ECR_REPO}:latest .

# Create ECR repo if not exists
aws ecr create-repository --repository-name ${ECR_REPO} --region ${AWS_REGION} || true

# Get login token
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Tag image
docker tag ${ECR_REPO}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest

# Push to ECR
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest

echo "✓ Image pushed to ECR"
echo "Update Lambda function:"
echo "  Runtime: Custom image"
echo "  URI: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}:latest"
