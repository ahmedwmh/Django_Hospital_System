#!/bin/bash

# DigitalOcean App Platform Redeployment Script
# This script helps redeploy your Django Hospital System with correct configuration

echo "🏥 DigitalOcean Hospital System Redeployment Script"
echo "=================================================="

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl CLI not found. Please install it first:"
    echo "   https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if user is logged in
if ! doctl account get &> /dev/null; then
    echo "❌ Please login to DigitalOcean first:"
    echo "   doctl auth init"
    exit 1
fi

echo "✅ DigitalOcean CLI is ready"

# Get app ID
APP_ID=$(doctl apps list --format ID,Name --no-header | grep "hospital-system" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo "❌ App 'hospital-system' not found. Please check your app name."
    exit 1
fi

echo "✅ Found app ID: $APP_ID"

# Create deployment
echo "🚀 Creating new deployment..."
doctl apps create-deployment $APP_ID --wait

if [ $? -eq 0 ]; then
    echo "✅ Deployment created successfully!"
    echo "🌐 Your app should be available at: https://urchin-app-j2low.ondigitalocean.app/"
    echo ""
    echo "📋 Next steps:"
    echo "1. Wait 2-3 minutes for the deployment to complete"
    echo "2. Check the app logs: doctl apps logs $APP_ID"
    echo "3. If still having issues, try accessing from mobile data"
else
    echo "❌ Deployment failed. Check the logs:"
    echo "   doctl apps logs $APP_ID"
fi
