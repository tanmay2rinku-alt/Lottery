@echo off
REM Lottery Scraper AWS Lambda Deployment Script
REM Run this from F:\LotteryAI\titan directory

echo 🚀 Deploying Lottery Scraper to AWS Lambda...
echo.

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS CLI not found. Install from: https://aws.amazon.com/cli/
    pause
    exit /b 1
)

REM Check if SAM CLI is installed
sam --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ AWS SAM CLI not found. Install with: pip install aws-sam-cli
    pause
    exit /b 1
)

echo ✅ AWS tools found
echo.

REM Build the Lambda package
echo 🔨 Building Lambda package...
sam build
if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo ✅ Build successful
echo.

REM Deploy to AWS
echo ☁️ Deploying to AWS Lambda...
sam deploy --guided
if %errorlevel% neq 0 (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

echo.
echo 🎉 Deployment successful!
echo.
echo 📊 Your scraper will now run automatically every 2 hours
echo 📋 Monitor at: https://console.aws.amazon.com/lambda/home
echo 📝 View logs at: https://console.aws.amazon.com/cloudwatch/home
echo.
pause