#!/bin/bash

# DigitalOcean App Platform Redeploy Script
# This script helps redeploy your Django Hospital System to DigitalOcean

echo "🏥 DigitalOcean Hospital System Redeploy Script"
echo "=============================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository. Please run this from your project root."
    exit 1
fi

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Uncommitted changes detected. Committing them..."
    git add .
    git commit -m "Fix DigitalOcean deployment: update ALLOWED_HOSTS and add app.yaml"
fi

# Push to main branch
echo "🚀 Pushing changes to main branch..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Code pushed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to your DigitalOcean App Platform dashboard"
    echo "2. Navigate to your 'hospital-system' app"
    echo "3. Go to Settings → App-Level"
    echo "4. Click 'Redeploy' or 'Force Deploy'"
    echo "5. Wait for deployment to complete"
    echo "6. Test your app at: https://hospital-system-u3uy4.ondigitalocean.app/"
    echo ""
    echo "🔍 If you still see DNS issues:"
    echo "- Wait 5-10 minutes for DNS propagation"
    echo "- Clear your DNS cache"
    echo "- Try accessing from a different network"
    echo "- Check the app logs in DigitalOcean dashboard"
else
    echo "❌ Failed to push changes. Please check your git configuration."
    exit 1
fi
