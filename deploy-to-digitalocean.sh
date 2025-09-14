#!/bin/bash

# DigitalOcean App Platform Deployment Script
# For Django Hospital Management System

echo "🏥 Deploying Django Hospital System to DigitalOcean App Platform"
echo "================================================================="

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

# Create app from YAML configuration
echo "🚀 Creating app from configuration..."
doctl apps create --spec digitalocean-app-production.yaml

if [ $? -eq 0 ]; then
    echo "✅ App created successfully!"
    echo "🌐 Your app will be available at: https://your-app-name.ondigitalocean.app/"
    echo ""
    echo "📋 Next steps:"
    echo "1. Wait 3-5 minutes for the deployment to complete"
    echo "2. Check the app logs: doctl apps logs <app-id>"
    echo "3. Access your hospital management system"
    echo "4. Login with admin/admin123"
else
    echo "❌ App creation failed. Check the error messages above."
fi
